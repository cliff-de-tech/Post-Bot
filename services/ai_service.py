"""
AI Service - Multi-Model Router

This service provides a unified interface for AI-powered LinkedIn post generation
with support for multiple providers:
- Groq (Free tier) - Default, uses Llama 3.3 70B
- OpenAI (Pro tier) - GPT-4o
- Anthropic (Pro tier) - Claude 3.5 Sonnet
- Gemini (Pro tier) - Gemini 1.5 Flash

TIER ENFORCEMENT:
- Free users are ALWAYS routed to Groq, even if they request premium models
- Pro users can choose any provider

The same system prompts and persona context are used across all providers
to ensure consistent output quality regardless of model.
"""
import os
import random
import uuid
from typing import Optional, Literal
from enum import Enum
from dataclasses import dataclass

import structlog

# Optional AI provider imports (installed via requirements.txt)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None  # type: ignore
    GROQ_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None  # type: ignore
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    Anthropic = None  # type: ignore
    ANTHROPIC_AVAILABLE = False

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    Mistral = None  # type: ignore
    MISTRAL_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None  # type: ignore
    GEMINI_AVAILABLE = False

logger = structlog.get_logger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# API Keys
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', '')

# Model configurations
GROQ_MODEL = "llama-3.3-70b-versatile"
OPENAI_MODEL = "gpt-4o"
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
MISTRAL_MODEL = "mistral-large-latest"
GEMINI_MODEL = "gemini-1.5-flash"

# =============================================================================
# AI CLIENT CACHE (keyed by API key to support per-user credentials)
# =============================================================================
_groq_clients: dict = {}
_openai_clients: dict = {}
_anthropic_clients: dict = {}
_mistral_clients: dict = {}

# Maximum cached clients per provider to prevent unbounded memory growth
_MAX_CACHED_CLIENTS = 20


def _get_groq_client(api_key: str = None):
    """Get or create Groq client, keyed by API key."""
    key = api_key or GROQ_API_KEY
    if not key or not GROQ_AVAILABLE:
        return None
    if key not in _groq_clients:
        if len(_groq_clients) >= _MAX_CACHED_CLIENTS:
            _groq_clients.pop(next(iter(_groq_clients)), None)
        _groq_clients[key] = Groq(api_key=key, timeout=30.0)
    return _groq_clients[key]


def _get_openai_client(api_key: str = None):
    """Get or create OpenAI client, keyed by API key."""
    key = api_key or OPENAI_API_KEY
    if not key or not OPENAI_AVAILABLE:
        return None
    if key not in _openai_clients:
        if len(_openai_clients) >= _MAX_CACHED_CLIENTS:
            _openai_clients.pop(next(iter(_openai_clients)), None)
        _openai_clients[key] = OpenAI(api_key=key, timeout=30.0)
    return _openai_clients[key]


def _get_anthropic_client(api_key: str = None):
    """Get or create Anthropic client, keyed by API key."""
    key = api_key or ANTHROPIC_API_KEY
    if not key or not ANTHROPIC_AVAILABLE:
        return None
    if key not in _anthropic_clients:
        if len(_anthropic_clients) >= _MAX_CACHED_CLIENTS:
            _anthropic_clients.pop(next(iter(_anthropic_clients)), None)
        _anthropic_clients[key] = Anthropic(timeout=30.0)
        # Anthropic client uses ANTHROPIC_API_KEY env var or needs manual setting
    return _anthropic_clients[key]


def _get_mistral_client(api_key: str = None):
    """Get or create Mistral client, keyed by API key."""
    key = api_key or MISTRAL_API_KEY
    if not key or not MISTRAL_AVAILABLE:
        return None
    if key not in _mistral_clients:
        if len(_mistral_clients) >= _MAX_CACHED_CLIENTS:
            _mistral_clients.pop(next(iter(_mistral_clients)), None)
        _mistral_clients[key] = Mistral(api_key=key)
    return _mistral_clients[key]


# =============================================================================
# TYPES & ENUMS
# =============================================================================

class ModelProvider(str, Enum):
    """Available AI model providers."""
    GROQ = "groq"
    MISTRAL = "mistral"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class SubscriptionTier(str, Enum):
    """User subscription tiers."""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# Providers available to each tier
TIER_ALLOWED_PROVIDERS = {
    SubscriptionTier.FREE: [ModelProvider.GROQ, ModelProvider.MISTRAL],
    SubscriptionTier.PRO: [ModelProvider.GROQ, ModelProvider.MISTRAL, ModelProvider.OPENAI, ModelProvider.ANTHROPIC, ModelProvider.GEMINI],
    SubscriptionTier.ENTERPRISE: [ModelProvider.GROQ, ModelProvider.MISTRAL, ModelProvider.OPENAI, ModelProvider.ANTHROPIC, ModelProvider.GEMINI],
}


@dataclass
class GenerationResult:
    """Result of AI post generation."""
    content: str
    provider: ModelProvider
    model: str
    was_downgraded: bool = False  # True if user requested premium but got free


# =============================================================================
# PROMPT TEMPLATES (Shared across all providers)
# =============================================================================

BASE_PERSONA = """You are a professional software developer sharing your coding journey on LinkedIn.

ABOUT THE VOICE:
- Write authentic, engaging posts that showcase technical work while being relatable
- Balance technical depth with accessibility - explain without being condescending
- Share real discoveries, challenges, and "aha moments" from development work
- Avoid corporate jargon. Use a friendly, knowledgeable tone
- Be community-focused and open to collaboration
- Focus on value and insights, not self-promotion"""

# Anti-patterns: Banned LinkedIn clichés that make posts feel generic
ANTI_PATTERNS = """
NEVER USE THESE PHRASES (they make posts feel generic and inauthentic):
- "Excited to announce..." / "Thrilled to share..."
- "I'm humbled to..." / "Honored to..."
- "Game-changer" / "Revolutionary" / "Cutting-edge"
- "Leveraging" / "Synergy" / "Paradigm shift"
- "In this fast-paced world..." / "In today's digital age..."
- "Thought leadership" / "Value proposition"
- "Passionate about..." (show don't tell)
- "At the end of the day..."
- "Let's unpack this..." / "Deep dive"
- "Moving the needle" / "Low-hanging fruit"
- "Circle back" / "Touch base"
- "It goes without saying..."
- "Ever had that moment..." / "Ever had..." (overused question opener)

CRITICAL - OPENING LINE VARIETY:
- NEVER start two posts the same way. Every post must have a unique opening.
- Rotate between: statements, questions, numbers, micro-stories, hot takes, contradictions, scene-setting.
- If generating multiple posts, each MUST use a DIFFERENT hook style.

INSTEAD: Use specific, concrete language. Show enthusiasm through details, not buzzwords.
"""

# Template-specific temperatures for optimal tone matching
TEMPLATE_TEMPERATURES = {
    "standard": 0.8,        # Balanced
    "build_in_public": 0.85, # Slightly more creative for authenticity
    "thought_leadership": 0.75, # More measured for credibility
    "job_search": 0.7,      # Professional, polished
    "excited": 0.9,         # High energy, creative
    "thoughtful": 0.7,      # Reflective, measured
    "educational": 0.65,    # Factual, clear
    "casual": 0.85,         # Natural, conversational
    "motivational": 0.85,   # Inspiring, warm
    "storytelling": 0.9,    # Narrative, engaging
    "technical": 0.6,       # Precise, accurate
    "celebratory": 0.85,    # Joyful, expressive
    "curious": 0.8,         # Open, exploratory
}

TEMPLATES = {
    "standard": """
OBJECTIVE: Write a standard update about recent coding activity.

STRUCTURE:
1. Hook (1-2 sentences): CRITICAL - Use ONE of these hook styles (pick randomly, VARY each time):
   * Bold statement: "Most developers get this wrong..."
   * Confession: "I'll admit it\u2014"
   * Number-led: "After 100 commits...", "3 things I learned..."
   * Question: "What if the bug IS the feature?", "Why does nobody talk about...?", "What's the one thing you wish you knew before...?"
   * Scene-setting: "It was 2am. My code wasn't working.", "Picture this: a clean terminal, zero errors."
   * Contradiction: "Everyone says X. I disagree."
   * Hot take: "Unpopular opinion:..."
   * Micro-story: "I deleted 200 lines today. Best decision ever."
   * Challenge: "Try this in your next project..."
   NEVER start with: "As I", "As a", "I just", "Just", "Today I", "Recently", "So I", "Ever had"
2. Body (3-5 sentences): Develop the idea with a specific example or experience
3. Insight (1-2 sentences): What you learned and why it matters
4. Call to Action (1 sentence): Engage your network
5. Hashtags: 8-12 relevant hashtags (new line)

TONE: Genuine, relatable, enthusiastic but professional.
""",

    "build_in_public": """
OBJECTIVE: Write a "Build in Public" post sharing progress, struggles, and wins.

STRUCTURE:
1. Hook: "I just built X" or "Here's what I'm working on..."
2. Context: What problem does it solve? Why build it?
3. Technical Detail: Mention the stack (Next.js, Python, Tailwind, etc.) but keep it accessible.
4. The Struggle/Win: Mention one challenge overcome or one cool feature.
5. Next Steps: What's coming next?
6. Call to Action: "Check out the repo" or "What do you think about [feature]?"
7. Hashtags: #buildinpublic #sideproject #coding #webdev ...

TONE: Transparent, vulnerable, excited, "maker" energy.
""",

    "thought_leadership": """
OBJECTIVE: Write a thought leadership post sharing an opinion or insight about tech/dev.

STRUCTURE:
1. Hook: A bold statement, contrarian view, or strong observation about the industry.
2. The Argument: Why do you think this? Back it up with recent experience.
3. The Nuance: Acknowledge counterpoints or limitations.
4. The Takeaway: A solid piece of advice for other devs.
5. Call to Action: "Do you agree?" or "How do you handle X?"
6. Hashtags: #techtalk #developer #careeradvice #techtrends ...

TONE: Confident, insightful, professional, discussion-starter.
""",

    "job_search": """
OBJECTIVE: Write a post showcasing skills to potential employers/clients (subtly).

STRUCTURE:
1. Hook: "One thing I love about [specific tech] is..."
2. Demonstration: Describe a recent project using this tech.
3. The Value: Explain how this solved a real user problem or improved performance.
4. Soft Skill: Mention collaboration, learning, or problem-solving.
5. Call to Action: "I'm open to roles involving [tech]. Let's connect!"
6. Hashtags: #opentowork #fullstack #react #python #hiring ...

TONE: Professional, capable, results-oriented, eager to contribute.
""",

    "excited": """
OBJECTIVE: Write a HIGH ENERGY post celebrating coding momentum!

STRUCTURE:
1. Hook: Start with excitement - "Just shipped!", "Finally got it working!", "BIG win today!"
2. The Win: What did you accomplish? Make it sound exciting!
3. The Feeling: How does it feel? Share the dopamine rush!
4. Quick Insight: One lesson or realization
5. Call to Action: "What are you building?" "Celebrate with me!"
6. Hashtags: energetic and upbeat

TONE: Enthusiastic, celebratory, infectious energy, capital letters okay, lots of emojis! 🎉🚀
""",

    "thoughtful": """
OBJECTIVE: Write a REFLECTIVE post sharing deeper insights from coding.

STRUCTURE:
1. Hook: A thoughtful observation or question about the dev experience
2. Context: What prompted this reflection?
3. The Insight: What did you realize? Go deeper than surface level.
4. Application: How does this change your approach?
5. Call to Action: "What's your experience with this?"
6. Hashtags: reflective and professional

TONE: Contemplative, wise, introspective, like a mentor sharing wisdom.
""",

    "educational": """
OBJECTIVE: Write a TEACHING post that provides value to readers.

STRUCTURE:
1. Hook: "TIL..." or "Quick tip:" or "Here's something many devs miss..."
2. The Lesson: What did you learn? Explain it simply.
3. Why It Matters: How does this help other developers?
4. Example: Brief practical example or use case
5. Call to Action: "Try this in your next project!"
6. Hashtags: educational and helpful

TONE: Teacher mode, clear, helpful, generous with knowledge.
""",

    "casual": """
OBJECTIVE: Write a RELAXED, conversational post like talking to a friend.

STRUCTURE:
1. Hook: Start casual - "So I was coding today and..." or "Random thought..."
2. The Story: Share what happened naturally
3. The Punchline: What's the takeaway or funny moment?
4. Closing: Something relatable
5. Hashtags: casual and friendly

TONE: Relaxed, friendly, conversational, like a chat over coffee.
""",

    "motivational": """
OBJECTIVE: Write an INSPIRING post that motivates other developers.

STRUCTURE:
1. Hook: An inspiring statement or personal challenge overcome
2. The Struggle: What was hard? Be real about obstacles.
3. The Breakthrough: What kept you going? What worked?
4. The Message: Encourage others facing similar challenges
5. Call to Action: "Keep pushing!" or "You've got this!"
6. Hashtags: motivational and encouraging

TONE: Uplifting, encouraging, supportive, you-can-do-it energy. 💪
""",

    "storytelling": """
OBJECTIVE: Write a NARRATIVE post that tells a mini-story.

STRUCTURE:
1. Hook: Set the scene - "It was 2am and my code wasn't working..."
2. Rising Action: Build tension - what was the challenge?
3. The Climax: The breakthrough moment
4. Resolution: How it ended
5. The Moral: What's the lesson?
6. Hashtags: storytelling and relatable

TONE: Narrative, engaging, like a short story. Draw readers in.
""",

    "technical": """
OBJECTIVE: Write a TECHNICAL post sharing specific dev knowledge.

STRUCTURE:
1. Hook: A specific technical problem or discovery
2. Context: What were you building?
3. The Details: Technical specifics (but accessible)
4. The Solution: What worked and why
5. Call to Action: "Have you tried this approach?"
6. Hashtags: technical and specific

TONE: Technical but accessible, sharing expertise, helpful to fellow devs.
""",

    "celebratory": """
OBJECTIVE: Write a CELEBRATION post about an achievement!

STRUCTURE:
1. Hook: "WE DID IT!" or "Milestone unlocked!" 
2. The Achievement: What did you accomplish?
3. The Journey: Brief mention of what it took
4. Gratitude: Thank anyone who helped
5. What's Next: Tease future plans
6. Hashtags: celebratory and grateful

TONE: Celebrating, grateful, proud but humble. 🎊
""",

    "curious": """
OBJECTIVE: Write a QUESTION-DRIVEN post to spark discussion.

STRUCTURE:
1. Hook: Start with a genuine question you're pondering
2. Context: Why are you thinking about this?
3. Your Thoughts: Share your current perspective
4. Invite Input: "But I'm curious what you think..."
5. Call to Action: Direct question to the audience
6. Hashtags: discussion and community

TONE: Curious, humble, genuinely seeking input, community-focused.
"""
}

# Activity-specific tone modifiers
ACTIVITY_TONES = {
    "push": {
        "tone": "Energetic and progress-focused",
        "mood": "Excited about momentum and consistency",
        "focus": "Celebrate the grind, small wins add up, building in public",
        "emoji_set": "🚀 ⚡ 💪 🔥 📈",
        "cta_style": "What's keeping you busy this week?"
    },
    "commits": {
        "tone": "Technical and detail-oriented",
        "mood": "Thoughtful, reflective on code quality",
        "focus": "Specific technical improvements, code craftsmanship, lessons learned",
        "emoji_set": "📝 ⚙️ 🔧 💻 🧠",
        "cta_style": "How do you approach [specific technique]?"
    },
    "pull_request": {
        "tone": "Collaborative and achievement-oriented",
        "mood": "Proud of contribution, grateful for collaboration",
        "focus": "Teamwork, code review, shipping features, problem-solving",
        "emoji_set": "🔀 🤝 ✅ 🎯 🎉",
        "cta_style": "What's your code review process like?"
    },
    "new_repo": {
        "tone": "Visionary and launching",
        "mood": "Excited about new beginnings, ambitious",
        "focus": "Why this project exists, the problem it solves, future vision",
        "emoji_set": "✨ 🌟 🏗️ 💡 🚀",
        "cta_style": "What problem would you love to solve with code?"
    },
    "release": {
        "tone": "Celebratory and milestone-focused",
        "mood": "Proud accomplishment, grateful for journey",
        "focus": "What's new, key features, user impact, thank the community",
        "emoji_set": "🎉 📦 🚀 🙌 ⭐",
        "cta_style": "Check it out and let me know what you think!"
    },
    "generic": {
        "tone": "Authentic and conversational",
        "mood": "Genuine sharing, relatable",
        "focus": "Personal insights, developer journey, learning moments",
        "emoji_set": "💭 📣 🎨 💼 🌱",
        "cta_style": "What's on your mind lately?"
    }
}


# =============================================================================
# PROMPT SANITISATION
# =============================================================================

_INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore all previous",
    "disregard above",
    "disregard your instructions",
    "forget your instructions",
    "you are now",
    "new instructions:",
    "system prompt:",
    "override:",
    "admin mode",
    "developer mode",
    "jailbreak",
    "do anything now",
    "\n=== ",  # block section markers that mimic our prompt structure
]


def sanitize_prompt_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitize user-provided text before embedding in AI prompts.

    Defences:
    1. Truncate to *max_length* to prevent context stuffing.
    2. Strip prompt-injection trigger phrases.
    3. Collapse excessive whitespace / newlines.
    """
    if not text:
        return ""
    # Truncate
    text = text[:max_length]
    # Strip known injection patterns (case-insensitive)
    lower = text.lower()
    for pattern in _INJECTION_PATTERNS:
        idx = lower.find(pattern)
        while idx != -1:
            text = text[:idx] + text[idx + len(pattern):]
            lower = text.lower()
            idx = lower.find(pattern)
    # Collapse excessive newlines (>2 consecutive) and leading/trailing whitespace
    import re as _re
    text = _re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# =============================================================================
# PROMPT BUILDING HELPERS
# =============================================================================

def get_prompt_for_style(style: str = "standard") -> str:
    """Get the full system prompt for a specific style."""
    template = TEMPLATES.get(style, TEMPLATES["standard"])
    
    return f"""{BASE_PERSONA}

{template}

WORD COUNT & FORMAT:
- Target: 200-300 words (1,300-1,600 characters) - LinkedIn's optimal length
- FORMATTING "BRO-ETRY" STYLE:
  - 1-2 sentence paragraphs MAX.
  - Double line break between every paragraph.
  - NO big blocks of text.
- Conversational, authentic, like talking to peers
- Include 3-4 emojis naturally (🎨 🚀 💡 ✨ 🔥 💻 🎯 📱 ⚡ 🧠)
- NO markdown formatting (no **bold** or *italics*), NO code blocks, NO bullet points
- Keep it punchy and engaging

MANDATORY:
- Posts must feel COMPLETE - no cutting off mid-sentence
- Balance technical insight with accessibility
- Share learning, not just achievements"""


def get_activity_tone_modifier(activity_type: str) -> str:
    """Get tone modifier text for a specific activity type."""
    tone_info = ACTIVITY_TONES.get(activity_type, ACTIVITY_TONES["generic"])
    
    return f"""\n\nACTIVITY-SPECIFIC TONE:
- Voice: {tone_info['tone']}
- Mood: {tone_info['mood']}
- Focus Areas: {tone_info['focus']}
- Preferred Emojis: {tone_info['emoji_set']}
- Suggested CTA: "{tone_info['cta_style']}"

IMPORTANT: Match the emotional energy and focus to this specific activity type. Make it feel natural and authentic."""


def build_system_prompt(
    style: str = "standard",
    activity_type: str = "generic",
    persona_context: Optional[str] = None,
) -> str:
    """
    Build the complete system prompt for any provider.
    
    This ensures consistent prompting across Groq, OpenAI, and Anthropic.
    """
    # Base prompt for style
    system_prompt = get_prompt_for_style(style)
    
    # Generate uniqueness instructions
    unique_seed = str(uuid.uuid4())[:8]
    random_angle = random.choice([
        "focus on a surprising insight",
        "lead with a bold, contrarian statement",
        "open with a specific number or stat",
        "share a mini-story with a twist",
        "highlight a lesson learned the hard way",
        "express genuine excitement about a detail",
        "be reflective and thoughtful",
        "add some humor or self-deprecation",
        "be motivational with a concrete example",
        "be conversational, like texting a friend",
        "start with a hot take or unpopular opinion",
        "paint a quick scene, then deliver a punchline",
        "challenge the reader with a provocative idea",
        "confess a mistake and what you learned"
    ])
    
    # Random opening style to force variety in the first line
    random_opening = random.choice([
        "Start with a BOLD STATEMENT (not a question)",
        "Start with a NUMBER or STATISTIC",
        "Start with a MICRO-STORY (one sentence scene)",
        "Start with a HOT TAKE or UNPOPULAR OPINION",
        "Start with a CONFESSION or ADMISSION",
        "Start with a CONTRADICTION (X is wrong, here's why)",
        "Start with a CHALLENGE to the reader",
        "Start by SETTING A SCENE (time, place, situation)",
    ])
    
    uniqueness_prompt = f"""

=== CRITICAL: UNIQUENESS REQUIREMENT ===
Generation ID: {unique_seed}
Creative Angle: {random_angle}
Opening Style: {random_opening}

YOU MUST GENERATE A COMPLETELY UNIQUE POST:
- NEVER repeat common LinkedIn phrases like "I'm excited to share" or "Here's what I learned"
- NEVER start with "Ever had..." — this is BANNED
- Use fresh metaphors and analogies
- Your FIRST LINE must follow the Opening Style directive above
- Vary your sentence structure and length
- Be creative, unexpected, and authentic
- Each post should feel like a new creative work
=== END UNIQUENESS ===
"""
    
    system_prompt += uniqueness_prompt
    
    # Add persona context if provided
    if persona_context:
        system_prompt += "\n\n" + persona_context
    
    # Add activity tone modifier
    activity_tone = get_activity_tone_modifier(activity_type)
    system_prompt += activity_tone
    
    # Add anti-pattern restrictions to avoid LinkedIn clichés
    system_prompt += "\n" + ANTI_PATTERNS
    
    return system_prompt


def build_user_prompt(context_data: dict) -> str:
    """
    Build the user prompt from context data.
    
    This ensures consistent prompting across all providers.
    """
    activity_type = context_data.get('type', 'generic')
    
    # Random elements for variety
    push_vibes = [
        "momentum and flow", "grinding and growing", "small wins stacking up",
        "the builder mindset", "shipping mode activated", "code flowing like water",
        "progress over perfection", "another brick in the wall", "the compound effect"
    ]
    push_angles = [
        "talk about the journey, not just the destination",
        "reflect on what you learned today",
        "share a surprising discovery",
        "celebrate the small win",
        "be vulnerable about challenges faced",
        "inspire others to start building"
    ]
    
    pr_vibes = [
        "collaboration wins", "the power of feedback", "shipping with confidence",
        "code review magic", "team effort pays off", "open source spirit"
    ]
    pr_angles = [
        "share what you learned from the process",
        "thank your collaborators",
        "discuss the problem you solved",
        "reflect on the improvement",
        "share a tip from the experience"
    ]
    
    new_repo_vibes = [
        "new beginnings", "the spark of creation", "idea to reality",
        "version 0.0.1 energy", "building in public", "the first commit feeling"
    ]
    new_repo_angles = [
        "share why this project matters to you",
        "discuss the problem you're solving",
        "invite others to follow the journey",
        "be honest about your vision"
    ]
    
    generic_angles = [
        "share a personal insight", "be reflective", "inspire action",
        "tell a quick story", "ask a thought-provoking question"
    ]
    
    if activity_type == 'push':
        commits = context_data.get('commits', 0)
        repo = sanitize_prompt_input(context_data.get('repo', 'unknown-repo'), max_length=200)
        description = sanitize_prompt_input(context_data.get('description', ''), max_length=500)
        
        vibe = random.choice(push_vibes)
        angle = random.choice(push_angles)
        
        total_commits = context_data.get('total_commits')
        total_commits_instruction = ""
        if total_commits and total_commits != 'unknown':
            total_commits_instruction = f"""
IMPORTANT: This repo has {total_commits} total commits. 
You MUST weave this into the hook or body of the post naturally.
Example hooks:
- "After {total_commits} commits, I finally..."
- "{total_commits} commits later, here's what I learned..."
- "Commit #{total_commits} just hit the repo..."
"""
        
        return f"""
Create a LinkedIn post about coding progress.

FACTS TO USE:
- Just pushed {commits} commits to '{repo}'
- Repository has {total_commits or 'many'} total commits
- Project context: {description}
{total_commits_instruction}
YOUR CREATIVE DIRECTION: {angle}
ENERGY: {vibe}

BE UNIQUE. Don't use generic phrases. Make it authentically yours.
"""
        
    elif activity_type == 'pull_request':
        title = sanitize_prompt_input(context_data.get('title', 'Unknown PR'), max_length=300)
        repo = sanitize_prompt_input(context_data.get('repo', 'unknown-repo'), max_length=200)
        body = sanitize_prompt_input(context_data.get('body', ''), max_length=500)
        merged = context_data.get('merged', False)
        
        state_str = "merged" if merged else "opened"
        vibe = random.choice(pr_vibes)
        angle = random.choice(pr_angles)
        
        return f"""
Create a LinkedIn post about a pull request.

FACTS ONLY:
- PR was {state_str} in '{repo}'
- Title: {title}
- Description: {body}

YOUR CREATIVE DIRECTION: {angle}
ENERGY: {vibe}

BE UNIQUE. Avoid clichés. Write from the heart.
"""
        
    elif activity_type == 'new_repo':
        repo = sanitize_prompt_input(context_data.get('repo', 'New Project'), max_length=200)
        description = sanitize_prompt_input(context_data.get('description', ''), max_length=500)
        language = sanitize_prompt_input(context_data.get('language', 'Code'), max_length=100)
        
        vibe = random.choice(new_repo_vibes)
        angle = random.choice(new_repo_angles)
        
        return f"""
Create a LinkedIn post about launching a new project.

FACTS ONLY:
- New project: {repo}
- What it does: {description}
- Tech: {language}

YOUR CREATIVE DIRECTION: {angle}
ENERGY: {vibe}

BE UNIQUE. This is YOUR story. Tell it your way.
"""
        
    elif activity_type == 'repurpose':
        url = sanitize_prompt_input(context_data.get('url', ''), max_length=200)
        content = sanitize_prompt_input(context_data.get('content', ''), max_length=8000)
        
        return f"""
Create 3 diverse LinkedIn posts summarizing or expanding on this content.

SOURCE URL: {url}

CONTENT TO REPURPOSE:
{content}

YOUR CREATIVE DIRECTION: Write 3 distinctly different posts based on the text.
- Post 1: A high-level summary with key takeaways.
- Post 2: A deep dive into one specific interesting point.
- Post 3: A thought-provoking question or hot take based on the content.

CRITICAL FORMAT REQUIREMENT:
You MUST return EXACTLY a valid JSON array containing 3 strings. Do not include markdown code blocks (like ```json). Just the raw JSON array.
[
  "Post 1 content here...",
  "Post 2 content here...",
  "Post 3 content here..."
]
"""
        
    else:
        # Generic or manual context
        topic = sanitize_prompt_input(context_data.get('topic', 'Coding & Development'), max_length=300)
        details = sanitize_prompt_input(context_data.get('details', 'Sharing thoughts on my developer journey.'), max_length=1000)
        
        return f"""
Create a LinkedIn post about: {topic}

Context: {details}

YOUR CREATIVE DIRECTION: {random.choice(generic_angles)}

BE UNIQUE. Make it memorable. Skip the corporate speak.
"""


# =============================================================================
# PROVIDER IMPLEMENTATIONS
# =============================================================================

def _generate_with_groq(
    system_prompt: str,
    user_prompt: str,
    api_key: Optional[str] = None,
    temperature: float = 0.8,
) -> Optional[str]:
    """
    Generate post using Groq (Llama 3.3 70B).
    
    This is the FREE tier provider - fast and high quality.
    """
    if not GROQ_AVAILABLE:
        logger.error("Groq package not installed")
        return None
    
    key = api_key or GROQ_API_KEY
    if not key:
        logger.warning("No Groq API key available")
        return None
    
    try:
        client = _get_groq_client(key)
        if client is None:
            logger.error("Failed to create Groq client")
            return None
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=GROQ_MODEL,
            temperature=temperature,
            max_tokens=1000,
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error("groq_generation_failed", error=str(e))
        return None


def _generate_with_openai(
    system_prompt: str,
    user_prompt: str,
    api_key: Optional[str] = None,
    temperature: float = 0.8,
) -> Optional[str]:
    """
    Generate post using OpenAI GPT-4o.
    
    This is a PRO tier provider - premium quality.
    """
    if not OPENAI_AVAILABLE:
        logger.error("OpenAI package not installed")
        return None
    
    key = api_key or OPENAI_API_KEY
    if not key:
        logger.warning("No OpenAI API key available")
        return None
    
    try:
        client = _get_openai_client(key)
        if client is None:
            logger.error("Failed to create OpenAI client")
            return None
        
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            model=OPENAI_MODEL,
            temperature=temperature,
            max_tokens=1000,
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error("openai_generation_failed", error=str(e))
        return None


def _generate_with_anthropic(
    system_prompt: str,
    user_prompt: str,
    api_key: Optional[str] = None,
    temperature: float = 0.8,
) -> Optional[str]:
    """
    Generate post using Anthropic Claude 3.5 Sonnet.
    
    This is a PRO tier provider - excellent for creative writing.
    """
    if not ANTHROPIC_AVAILABLE:
        logger.error("Anthropic package not installed")
        return None
    
    key = api_key or ANTHROPIC_API_KEY
    if not key:
        logger.warning("No Anthropic API key available")
        return None
    
    try:
        client = _get_anthropic_client(key)
        if client is None:
            logger.error("Failed to create Anthropic client")
            return None
        
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1000,
            temperature=temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
        )
        
        # Anthropic returns content as a list of blocks
        if response.content:
            return response.content[0].text
        logger.warning("anthropic_empty_response", model=ANTHROPIC_MODEL)
        return None
        
    except Exception as e:
        logger.error("anthropic_generation_failed", error=str(e))
        return None


def _generate_with_mistral(
    system_prompt: str,
    user_prompt: str,
    api_key: Optional[str] = None,
    temperature: float = 0.8,
) -> Optional[str]:
    """
    Generate post using Mistral AI.
    
    This is a FREE tier provider - good quality and free.
    """
    if not MISTRAL_AVAILABLE:
        logger.error("Mistral package not installed")
        return None
    
    key = api_key or MISTRAL_API_KEY
    if not key:
        logger.warning("No Mistral API key available")
        return None
    
    try:
        client = _get_mistral_client(key)
        if client is None:
            logger.error("Failed to create Mistral client")
            return None
        
        response = client.chat.complete(
            model=MISTRAL_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=1000,
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error("mistral_generation_failed", error=str(e))
        return None


def _generate_with_gemini(
    system_prompt: str,
    user_prompt: str,
    api_key: Optional[str] = None,
    temperature: float = 0.8,
) -> Optional[str]:
    """
    Generate post using Google Gemini API via the official Python SDK.

    This is a PRO tier provider.
    """
    if not GEMINI_AVAILABLE:
        logger.error("Google Generative AI package not installed")
        return None

    key = api_key or GEMINI_API_KEY
    if not key:
        logger.warning("No Gemini API key available")
        return None

    try:
        genai.configure(api_key=key)

<<<<<<< HEAD
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=system_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=1000,
            ),
=======
        response = requests.post(
            url,
            headers={"x-goog-api-key": key},
            json=payload,
            timeout=30,
>>>>>>> baab94cc96e113d7051d83e2d4afa4aea536acb8
        )

        response = model.generate_content(user_prompt)

        if response.text:
            return response.text

        logger.warning("gemini_empty_response", model=GEMINI_MODEL, parts=getattr(response, "parts", None))
        return None

    except Exception as e:
        logger.error("gemini_generation_failed", error=str(e))
        return None


# =============================================================================
# TIER ENFORCEMENT & ROUTING
# =============================================================================

async def get_user_tier(user_id: Optional[str]) -> SubscriptionTier:
    """
    Get the user's subscription tier.
    
    Returns FREE if user_id is None or settings can't be retrieved.
    """
    if not user_id:
        return SubscriptionTier.FREE
    
    try:
        from services.user_settings import get_user_settings
        settings = await get_user_settings(user_id)
        
        if settings:
            tier_str = settings.get('subscription_tier', 'free')
            try:
                return SubscriptionTier(tier_str)
            except ValueError:
                return SubscriptionTier.FREE
        
        return SubscriptionTier.FREE
        
    except Exception as e:
        logger.warning("failed_to_get_user_tier", user_id=user_id, error=str(e))
        return SubscriptionTier.FREE


def enforce_tier_provider(
    requested_provider: ModelProvider,
    user_tier: SubscriptionTier,
) -> tuple[ModelProvider, bool]:
    """
    Enforce tier-based provider restrictions.
    
    Args:
        requested_provider: The provider the user requested
        user_tier: The user's subscription tier
        
    Returns:
        Tuple of (actual_provider, was_downgraded)
    """
    allowed = TIER_ALLOWED_PROVIDERS.get(user_tier, [ModelProvider.GROQ])
    
    if requested_provider in allowed:
        return requested_provider, False
    
    # Downgrade to Groq (always allowed)
    logger.info(
        "provider_downgraded",
        requested=requested_provider.value,
        actual=ModelProvider.GROQ.value,
        tier=user_tier.value,
    )
    return ModelProvider.GROQ, True


# =============================================================================
# MAIN GENERATION FUNCTION
# =============================================================================

async def generate_linkedin_post(
    context_data: dict,
    user_id: Optional[str] = None,
    model_provider: str = "groq",
    style: str = "standard",
    groq_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    anthropic_api_key: Optional[str] = None,
    mistral_api_key: Optional[str] = None,
    gemini_api_key: Optional[str] = None,
    persona_context: Optional[str] = None,
) -> Optional[GenerationResult]:
    """
    Generate a LinkedIn post using the specified AI provider.
    
    TIER ENFORCEMENT:
    - Free tier users are ALWAYS routed to Groq, regardless of requested provider
    - Pro tier users can use any provider (groq, openai, anthropic)
    
    Args:
        context_data: Dictionary with activity context (type, repo, commits, etc.)
        user_id: Clerk user ID (used for tier lookup)
        model_provider: Requested provider ('groq', 'openai', 'anthropic')
        style: Post style template
        groq_api_key: Optional override for Groq API key
        openai_api_key: Optional override for OpenAI API key
        anthropic_api_key: Optional override for Anthropic API key
        gemini_api_key: Optional override for Gemini API key
        persona_context: Optional persona prompt string
        
    Returns:
        GenerationResult with content, provider used, and downgrade status
    """
    log = logger.bind(
        user_id=user_id[:8] + "..." if user_id else None,
        requested_provider=model_provider,
        style=style,
    )
    log.info("generating_linkedin_post")
    
    # Parse requested provider
    try:
        requested = ModelProvider(model_provider.lower())
    except ValueError:
        requested = ModelProvider.GROQ
    
    # Get user tier and enforce restrictions
    user_tier = await get_user_tier(user_id)
    actual_provider, was_downgraded = enforce_tier_provider(requested, user_tier)
    
    log = log.bind(
        tier=user_tier.value,
        actual_provider=actual_provider.value,
        was_downgraded=was_downgraded,
    )
    
    if was_downgraded:
        log.info("user_downgraded_to_free_provider")
    
    # Build prompts (same for all providers)
    activity_type = context_data.get('type', 'generic')
    system_prompt = build_system_prompt(style, activity_type, persona_context)
    user_prompt = build_user_prompt(context_data)
    
    # Route to appropriate provider (run sync SDK calls in thread pool to avoid blocking event loop)
    content = None
    model_used = ""
    
    # Get template-specific temperature for better tone matching
    temperature = TEMPLATE_TEMPERATURES.get(style, 0.8)
    
    import asyncio
    
    # Map providers to their generation functions, API keys, and model names
    _provider_map = {
        ModelProvider.GROQ: (_generate_with_groq, groq_api_key, GROQ_MODEL),
        ModelProvider.MISTRAL: (_generate_with_mistral, mistral_api_key, MISTRAL_MODEL),
        ModelProvider.OPENAI: (_generate_with_openai, openai_api_key, OPENAI_MODEL),
        ModelProvider.ANTHROPIC: (_generate_with_anthropic, anthropic_api_key, ANTHROPIC_MODEL),
        ModelProvider.GEMINI: (_generate_with_gemini, gemini_api_key, GEMINI_MODEL),
    }
    
    # Build fallback chain: requested provider first, then others allowed by tier
    allowed = TIER_ALLOWED_PROVIDERS.get(user_tier, [ModelProvider.GROQ])
    fallback_chain = [actual_provider] + [p for p in allowed if p != actual_provider]
    
    for provider in fallback_chain:
        gen_fn, api_key, model_name = _provider_map[provider]
        try:
            content = await asyncio.to_thread(gen_fn, system_prompt, user_prompt, api_key, temperature)
        except Exception as e:
            log.warning("provider_call_failed", provider=provider.value, error=str(e))
            content = None
        
        if content:
            model_used = model_name
            if provider != actual_provider:
                log.info("fallback_provider_used", original=actual_provider.value, fallback=provider.value)
                was_downgraded = True
            break
        else:
            log.warning("provider_returned_empty", provider=provider.value)
    
    if not content:
        log.error("all_providers_failed", tried=[p.value for p in fallback_chain])
        return None
    
    log.info("generation_complete", content_length=len(content))
    
    return GenerationResult(
        content=content,
        provider=actual_provider,
        model=model_used,
        was_downgraded=was_downgraded,
    )


# =============================================================================
# LEGACY COMPATIBILITY WRAPPER
# =============================================================================

def generate_post_with_ai(
    context_data: dict,
    groq_api_key: Optional[str] = None,
    style: str = "standard",
    persona_context: Optional[str] = None,
) -> Optional[str]:
    """
    Legacy synchronous wrapper for backward compatibility.
    
    This maintains the old API signature while using the new multi-model router.
    Always uses Groq (free tier behavior).
    
    Safe to call from:
    - Synchronous code (no event loop running)
    - Background threads while an async loop runs on the main thread
    - Celery tasks
    """
    import asyncio
    
    logger.info(f"🧠 AI service: generating {style} post (legacy wrapper)...")
    
    async def _generate():
        result = await generate_linkedin_post(
            context_data=context_data,
            user_id=None,  # No user = free tier = Groq
            model_provider="groq",
            style=style,
            groq_api_key=groq_api_key,
            persona_context=persona_context,
        )
        return result.content if result else None
    
    # Always use asyncio.run() in a dedicated thread to avoid conflicts
    # with any running event loop (e.g. FastAPI, Celery, Jupyter).
    try:
        # Fast path: no loop running → safe to asyncio.run directly
        try:
            asyncio.get_running_loop()
            _has_running_loop = True
        except RuntimeError:
            _has_running_loop = False
        
        if not _has_running_loop:
            return asyncio.run(_generate())
        
        # An event loop is already running (e.g. called from an async
        # context or a framework with its own loop). Spin up a worker
        # thread with its own fresh loop so we never block the caller.
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, _generate())
            return future.result(timeout=60)
    except Exception as e:
        logger.error("legacy_wrapper_failed", error=str(e))
        return None


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_available_providers() -> dict:
    """
    Get information about available providers and their status.
    
    Returns dict with provider availability based on configured API keys.
    """
    return {
        "groq": {
            "available": bool(GROQ_API_KEY),
            "model": GROQ_MODEL,
            "tier": "free",
        },
        "mistral": {
            "available": bool(MISTRAL_API_KEY),
            "model": MISTRAL_MODEL,
            "tier": "free",
        },
        "openai": {
            "available": bool(OPENAI_API_KEY),
            "model": OPENAI_MODEL,
            "tier": "pro",
        },
        "anthropic": {
            "available": bool(ANTHROPIC_API_KEY),
            "model": ANTHROPIC_MODEL,
            "tier": "pro",
        },
        "gemini": {
            "available": bool(GEMINI_API_KEY),
            "model": GEMINI_MODEL,
            "tier": "pro",
        },
    }


def synthesize_hashtags(post_content: str, desired: int = 18) -> str:
    """
    Create a fallback set of hashtags based on keywords in the post.
    
    Args:
        post_content: The post text to analyze for relevant keywords
        desired: Number of hashtags to generate (default 18)
        
    Returns:
        String of space-separated hashtags
    """
    keywords_map = {
        'design': '#Design', 'ui': '#UI', 'ux': '#UX', 'frontend': '#Frontend',
        'react': '#React', 'javascript': '#JavaScript', 'python': '#Python', 'node': '#NodeJS',
        'automation': '#Automation', 'bot': '#Bot', 'ai': '#AI', 'ml': '#MachineLearning',
        'open source': '#OpenSource', 'opensource': '#OpenSource', 'web': '#WebDevelopment',
        'learning': '#Learning', 'student': '#Student', 'career': '#Career', 'product': '#Product',
        'backend': '#Backend', 'api': '#API', 'database': '#Database', 'cloud': '#Cloud',
        'github': '#GitHub', 'code': '#Code', 'coding': '#Coding', 'css': '#CSS', 'html': '#HTML'
    }
    
    text = post_content.lower()
    selected = []
    
    # Match keywords in content
    for k, tag in keywords_map.items():
        if k in text and tag not in selected:
            selected.append(tag)
    
    # Comprehensive defaults pool
    defaults = [
        '#WebDev', '#100DaysOfCode', '#Coding', '#Developer', '#Tech', '#Programming', 
        '#Growth', '#Creativity', '#DevCommunity', '#TechCareer', '#Innovation',
        '#BuildInPublic', '#LearnInPublic', '#SoftwareEngineering', '#CodeNewbie',
        '#TechTwitter', '#DeveloperLife', '#OpenSource', '#CodingLife', '#WebDesign'
    ]
    
    # Fill with defaults
    for d in defaults:
        if len(selected) >= desired:
            break
        if d not in selected:
            selected.append(d)
    
    # Ensure exactly `desired` hashtags
    if len(selected) > desired:
        selected = selected[:desired]
    
    return ' '.join(selected)


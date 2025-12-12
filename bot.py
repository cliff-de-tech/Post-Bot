import requests
import json
import random
import datetime
from dateutil import parser

# --- CONFIGURATION ---
LINKEDIN_ACCESS_TOKEN = "your_access_token_here"
LINKEDIN_USER_URN = "your_user_urn_here"
GITHUB_USERNAME = "cliff-de-tech" # e.g., 'torvalds'

# --- THE STATIC BRAIN (Fallback Content) ---
# Keep your list here! (I'm truncating it for space, but keep your 60 items)
STATIC_POST_IDEAS = [
    # --- WEEK 1: THE FOUNDATION (AUTOMATION & PYTHON) ---
    """I used to think automation was about "being lazy." I was DEAD wrong. 🤦‍♂️
    
    I just built a custom LinkedIn bot in Python, and it changed everything. Automation isn't laziness—it's LEVERAGE.
    
    Every minute spent copy-pasting or clicking the same buttons is a minute stolen from strategic work. But give 2 hours to automation? You're buying back thousands of hours.
    
    The 3-Click Rule: If you do something 3+ times, script it. Period. Your future self will bow down to you. 🚀
    
    #Python #Automation #Efficiency #Productivity #CodingLife #TechHacks #DeveloperTips""",

    """ "It works on my machine." — The most famous LAST WORDS in programming 💀
    
    Built my latest Python project and spent 3 HOURS debugging only to realize I was running the WRONG library version. Facepalm emoji wasn't enough.
    
    Here's the brutal truth: Coding is 50% logic, 50% managing the absolute CHAOS of dependencies and versions.
    
    Junior devs: Learn Docker or Virtual Environments NOW. Your future sanity is worth it. Trust me on this one.
    
    #DevOps #Python #CodingStruggles #TechTips #DeveloperLife #EnvironmentManagement #ProTips""",

    """Why Python? The REAL Reason 🐍
    
    Everyone asks me why Python for automation. "Because it's popular?" Nope.
    
    Python is the closest language to HUMAN SPEECH. It reads like you're telling someone what to do, not writing an algorithm.
    
    Readable = Maintainable. Maintainable = Survives. 
    
    I write a script, ghost it for 6 months, come back—and I STILL know what I was thinking. That's a superpower in tech.
    
    #PythonDeveloper #SoftwareEngineering #CleanCode #Readability #BestPractices #TechTips""",

    """The "Hello World" Phase is a LIE 🚨
    
    Those first print statements? TOO EASY. That's where the tutorial writers lie to you.
    
    Real growth? It happens in the VALLEY OF DESPAIR—when YouTube stops helping and you're face-to-face with raw, brutal documentation.
    
    Right now, I'm DEEP in LinkedIn API docs. Dense. Complex. Sometimes infuriating.
    
    But cracking it myself? 10x better than following a guide. This is where senior engineers are FORGED.
    
    #GrowthMindset #LearningToCode #DevJourney #StruggleIsGrowth #TechMastery #SelfTaught""",

    """APIs Are the HIDDEN SUPERPOWERS of the Web 🌐⚡
    
    Billions of data packets flowing between servers every second—silently. Invisibly. BEAUTIFULLY.
    
    My current project? "Talking" to LinkedIn's servers with JSON. It's like having a secret conversation the internet doesn't even see.
    
    Once you understand REST APIs, you stop seeing Instagram/Twitter/LinkedIn as apps. You see them as DATA SOURCES. The entire internet becomes programmable.
    
    What API are YOU experimenting with? Drop it in the comments—I'm curious!
    
    #API #Backend #WebDev #RestAPI #TechTalk #Integration #DataFlow""",

    """PERFECT Code is the Enemy of SHIPPED Code 🚢
    
    I used to get STUCK on elegance. Overthinking. Rewriting. Refactoring before I even shipped.
    
    Here's the truth: A MESSY 10-line script that works TODAY beats a PERFECT system that launches next month.
    
    Iterative. Rapid. Ship it. Break it. Fix it. Ship it again.
    
    That's the winner's playbook.
    
    #Agile #Productivity #ShipIt #Startup #Execution #SpeedMatters""",

    """Sunday Reflection: The JOY of Building 🛠️✨
    
    There's a RUSH you get when you type a command and watch your machine execute it PERFECTLY.
    
    You told it what to do. And it LISTENED. Every single time.
    
    Whether it's a calculator or a bot that posts for you—creation is what separates us from users. We're builders.
    
    Here's to another week of solving problems nobody else is crazy enough to try.
    
    #SundayReset #CreatorEconomy #BuilderMindset #TechLife #MakerMovement""",

    # --- WEEK 2: CODING BEST PRACTICES ---
    """ "Always code as if the person maintaining it is a violent psychopath who knows where you live." — John Woods
    
    I've been forcing myself to write better docs. It's EASY to write quick, messy scripts on personal projects.
    
    But here's the trap: "Future Me" is the one reading this disaster 6 months later.
    
    Meaningful variable names. Clear comments. Modular functions. These aren't just for TEAMS. They're SELF-CARE for developers.
    
    Treat your code like you're writing a love letter to your future self. 💌
    
    #CleanCode #BestPractices #SelfCare #Python #Maintainability""",

    """Unpopular Opinion: Comments Are NOT Explanations 🔥
    
    BAD:
    # Adds 1 to i
    i = i + 1
    
    GOOD:
    # Retry connection 3 times before timeout failure
    i = i + 1
    
    CODE shows WHAT. Comments must show WHY.
    
    The "why" is the story. The decision. The context. THAT'S what separates junior code from professional code.
    
    #CodingTips #SoftwareEngineering #Mentorship #ProTips #CodeQuality""",

    """Refactoring is INVISIBLE POWER 🧙💪
    
    You don't HAVE to do it. You can live in the MESS. 
    
    But eventually? You'll trip over your own code. It breaks. Users suffer. You cry.
    
    Spent this morning refactoring bot.py. Zero new features. But the logic is CLEANER and the whole system is MORE ROBUST.
    
    There's power in deleting code. In removing the CHAOS.
    
    Code you delete is code you don't have to maintain forever.
    
    #Refactoring #TechnicalDebt #Minimalism #CodeQuality #CleanCode""",

    """Global Variables: The Forbidden Fruit 🍎
    
    It's SO EASY to slap a variable at the top and access it EVERYWHERE. Fast. Works. Life is good.
    
    And then 2 weeks later? Your bug tracking becomes a NIGHTMARE. Who changed this value? When? WHY?
    
    Learning to pass arguments properly and use classes was my BIGGEST level-up in Python.
    
    Constraints force you to be better. Embrace them.
    
    #PythonTips #JuniorDev #Architecture #BestPractices #SoftwareDesign""",

    """Don't Optimize Prematurely ⚡️ (Yet)
    
    Caught myself trying to make my code run 0.01 seconds faster. For a script that runs ONCE a DAY. 🐢
    
    Here's the brutal reality: Readability beats raw speed 99% of the time.
    
    Unless you're building high-frequency trading bots, premature optimization is shooting yourself in the foot.
    
    The Formula: Make it work → Make it right → THEN make it fast.
    
    #EngineeringWisdom #Optimization #KISS #Performance""",

    """The Art of the Error Message 🛑📢
    
    A GOOD error message doesn't just say "Something went wrong." It's a CONVERSATION:
    1. What happened?
    2. Why did it happen?
    3. How do I fix it?
    
    I'm obsessed with making my tools fail GRACEFULLY. Instead of crashing silently, they log, alert, and guide.
    
    Resilient software > Perfect software. Every time.
    
    #ErrorHandling #DevOps #Reliability #UserExperience #Logging""",

    """Documentation is a Love Letter 💌
    
    I used to HATE writing README files. Total waste of time, I thought.
    
    Now? I won't START a project without one.
    
    If you can't explain how to run your project in 3 bullet points, it's OVER-ENGINEERED.
    
    Good documentation separates "interesting project" from "actually usable by humans."
    
    #OpenSource #Documentation #DevCommunity #WritingMatters""",

    # --- WEEK 3: MINDSET & CAREER ---
    """STOP Calling Yourself "Aspiring." 🚫
    
    If you write code → You ARE a Developer.
    If you solve problems with tech → You ARE an Engineer.
    
    The "Aspiring" label is PERMISSION to quit when things get hard. Delete it from your bio TODAY.
    
    Innovative companies hire DOERS, not "aspiring doers."
    
    Own it. You're already in the game.
    
    #CareerAdvice #TechJobs #Confidence #Mindset #SelfBelief""",

    """Imposter Syndrome Never Really Leaves 🕵️‍♂️
    
    I was talking to a Senior Engineer with 15+ YEARS of experience. Know what he told me?
    
    "I still Google basic syntax almost every day."
    
    The goal ISN'T to memorize every Python function. The goal is to know how to FIND IT when you need it.
    
    Resourcefulness > Memorization. Always.
    
    #ImposterSyndrome #TechReality #Motivation #SeniorDev #RealTalk""",

    """The MOST Important Skill Isn't Coding ❤️
    
    It's EMPATHY.
    
    You can write the most BRILLIANT algorithm on earth. But if it solves the WRONG problem for your user, it's useless.
    
    Understanding USER PAIN POINTS separates Code Monkeys from Product Engineers.
    
    Build for humans. Code is just the tool.
    
    #UserExperience #ProductDesign #SoftSkills #Empathy #HumanCentered""",

    """Networking is Idea Collecting, Not Contact Hunting 🧠💡
    
    I'm building this bot not just to post—but to ENGAGE with the incredible tech community here.
    
    Networking isn't about collecting 10,000 connections. It's about collecting GAME-CHANGING IDEAS.
    
    If you're working on something COOL—AI, Web3, automation scripts—DROP A COMMENT. I want to see what you're building.
    
    Let's elevate each other.
    
    #Networking #Community #TechTrends #Ideas #Collaboration""",

    """ "Jack of all trades, master of none" is a MISQUOTE 🎯
    
    Full quote: "...master of none, but OFTENTIMES BETTER THAN A MASTER OF ONE."
    
    In 2025, specialist knowledge is VALUABLE. But a generalist who connects Backend + Frontend + AI dots? That person SCALES COMPANIES.
    
    Don't be afraid to explore new tech. Curiosity is a superpower.
    
    #Generalist #FullStack #CareerGrowth #TechStack #Learning""",

    """Burnout is REAL. And It's NOT Hustle 🕯️
    
    I LOVE coding. But staring at a screen for 12 hours? That's not "grind culture." That's SELF-SABOTAGE.
    
    My biggest breakthroughs NEVER happen at the keyboard. They happen WALKING, COOKING, SLEEPING.
    
    Rest isn't the opposite of work. Rest IS PART of the work.
    
    Your brain needs recovery to perform. Respect that.
    
    #MentalHealth #WorkLifeBalance #SelfCare #DeveloperLife #Sustainability""",

    """Consistency > Intensity 🎯
    
    Coding 30 MINUTES EVERY SINGLE DAY destroys 10 hours once a month.
    
    Consistency keeps the syntax FRESH in your brain. It builds the HABIT of problem-solving.
    
    Small daily wins compound into massive yearly gains.
    
    #Habits #AtomicHabits #LearningStrategy #Consistency #Growth""",

    # --- WEEK 4: TOOLS OF THE TRADE ---
    """VS Code or PyCharm? The Eternal Showdown 🥊
    
    I'm team VS Code—the sheer number of extensions make it POWERFUL without the bloat.
    
    But honestly? The best IDE is the one where you KNOW THE KEYBOARD SHORTCUTS by heart.
    
    Don't get caught in the tool wars. Pick your weapon and MASTER it.
    
    What's YOUR tool of choice? Let me know!
    
    #IDE #VSCode #PyCharm #DeveloperTools #Productivity""",

    """Git is a TIME MACHINE ⏳
    
    Remember saving files like `final_v1.py`, `final_v2_REAL.py`, `FINAL_ACTUALLY.py`?
    
    Yeah. Git killed that nightmare.
    
    Learning Git was scary (merge conflicts haunted my dreams), but now I can't live without it. You can BREAK EVERYTHING and `git checkout` back to safety instantly.
    
    That confidence to take risks? That's Git's gift.
    
    #Git #VersionControl #DevTools #Workflow #Collaboration""",

    """The Terminal Isn't Scary—It's POWER 🖥️⚡
    
    To non-coders, that black screen with green text looks like "hacking."
    
    To us? It's the MOST DIRECT way to tell the computer what to do.
    
    GUIs are pretty. CLI is where the real MAGIC lives.
    
    Master `ls`, `cd`, and `grep`—suddenly you feel like a WIZARD.
    
    #Linux #Terminal #PowerUser #CommandLine #Hacker""",

    """JSON: The Language of the Web 💬
    
    It's simple. It's human-readable. And it powers EVERYTHING.
    
    Learning to parse nested JSON dictionaries? It sounds boring. But it's the SKILL that pays the bills.
    
    JSON is the bridge between systems. Master it.
    
    #Data #JSON #WebDevelopment #Backend #APIs""",

    """Regex is Straight-Up MAGIC 🪄✨
    
    Spent 20 minutes writing a string parser. Then learned a SINGLE LINE of Regex could handle it INSTANTLY.
    
    (I still use a Regex checker to write it. Nobody actually memorizes Regex syntax... right? 😅)
    
    Once you understand patterns, text becomes PROGRAMMABLE.
    
    #Regex #ProgrammingHumor #DataScience #TextProcessing #Hacks""",

    """Cloud Computing: Someone ELSE's Computer ☁️
    
    Exploring AWS and Render deployment. The ability to have code running 24/7 without my laptop staying on? GAME CHANGER.
    
    Serverless architecture is MIND-BENDING: Upload a function, get billed in MILLISECONDS.
    
    The future of software is distributed, scalable, and serverless.
    
    #Cloud #AWS #Serverless #Deployment #CloudComputing""",

    """StackOverflow is the Real MVP 🏆
    
    Be real: Modern dev is 90% knowing how to ASK THE RIGHT QUESTION on Google.
    
    There's NO SHAME in copy-pasting solutions. Just take 5 minutes to UNDERSTAND WHY it works before you ship it.
    
    Knowledge is knowing the answer. Wisdom is knowing why.
    
    #StackOverflow #RealTalk #DevLife #Learning #GoogleFu""",

    # --- WEEK 5: CREATIVITY & INNOVATION ---
    """Code is Modern Poetry 📜✨
    
    It has structure. Rhythm. Syntax. When written well, it SINGS.
    
    But unlike poetry, one misplaced comma and EVERYTHING CRASHES. 😅
    
    I see myself as a "Creative Technologist"—using code to EXPRESS IDEAS, not just process data.
    
    Code can be art. Let it be.
    
    #CreativeCoding #ArtAndTech #Philosophy #Expression #Design""",

    """AI Isn't Taking Jobs—It's AUTOMATING Boring Stuff 🤖
    
    Using ChatGPT to generate boilerplate code and test cases. It doesn't REPLACE engineers; it makes them FASTER.
    
    We're evolving from "Code Writers" → "Code Editors."
    
    The future belongs to people who can COLLABORATE with AI, not compete against it.
    
    #AI #FutureOfWork #Copilot #TechTrends #Augmentation""",

    """Innovation Looks Like a Stupid Idea at First 💡
    
    Friends asked me: "Why build a bot when you can just use a scheduling tool?"
    
    Because building it MYSELF gives me CONTROL. Integration. Customization. Learning.
    
    Don't be afraid to REINVENT THE WHEEL if your goal is learning how wheels are made.
    
    The journey IS the destination.
    
    #Innovation #Learning #DIY #Experimentation #Curiosity""",

    """Data Visualization is CRIMINALLY Underrated 📊✨
    
    You can have PERFECT data but if you can't VISUALIZE it, nobody cares.
    
    Playing with `matplotlib` in Python turns CSV files into GOLD. That moment when a boring dataset becomes a beautiful graph? *Chef's kiss* 💋
    
    Learn to tell stories with data.
    
    #DataScience #Python #Visualization #DataDriven #Analytics""",

    """The "Creative Technologist" Persona 🎨⚙️
    
    We live at the intersection of Art & Engineering.
    
    We care about the UI AND the Database.
    We care about User Journey AND Latency.
    We care about Beauty AND Performance.
    
    It's CHAOTIC. But this is where INTERESTING PRODUCTS are born.
    
    #ProductManagement #Design #Engineering #Holistic #Innovation""",

    """What If We Used Tech to DISCONNECT? 🔌
    
    Beautiful irony: I'm using a bot to post so I DON'T have to be on social media all day.
    
    Automation gives us a DIGITAL PRESENCE while reclaiming our PHYSICAL LIVES.
    
    The goal isn't to be everywhere—it's to be strategic about where we show up.
    
    #DigitalMinimalism #Automation #LifeHacks #Intentional #Balance""",

    """Building in Public 📢💯
    
    I'm sharing my code. My wins. My FAILURES.
    
    It's VULNERABLE to show your work before it's "perfect." But perfection is the ENEMY of progress.
    
    If you're working on a side project, SHARE IT. You never know who's watching.
    
    The community rewards courage.
    
    #BuildInPublic #IndieDev #OpenSource #Transparency #Growth""",

    # --- WEEK 6: PROBLEM SOLVING ---
    """The Rubber Duck Method Works 🦆💡
    
    Stuck on a logic bug for an HOUR. Finally, I turned to my empty coffee mug and explained the code line-by-line OUT LOUD.
    
    Found the bug in 30 SECONDS. 
    
    Explaining your logic forces you to SLOW DOWN and verify your assumptions. Rubber ducks save careers.
    
    #Debugging #CodingHacks #Psychology #ProTips #MentalModel""",

    """Think Twice, Code Once ✍️
    
    I USED to jump straight to the keyboard. Now? I spend 20 minutes with pen and paper first.
    
    Drawing your app's architecture BEFORE coding saves HOURS of rewriting later.
    
    Planning isn't boring—it's the difference between 2 days and 2 weeks.
    
    #SystemDesign #Planning #SoftwareArchitecture #Efficiency #Strategy""",

    """Recursion: See 'Recursion' 🔄
    
    One of those concepts that breaks your brain until it SUDDENLY CLICKS.
    
    Solving a problem by breaking it into smaller versions of itself? ELEGANT.
    
    But INFINITE LOOPS are ALWAYS lurking in the shadows... 👻
    
    Master recursion and you'll see problems differently.
    
    #CSConcepts #Algorithms #Math #MindBender #Elegant""",

    """Big O Notation MATTERS 📈
    
    Sounds like academic theory, but knowing the difference between O(n) and O(n²) is the difference between BLAZING FAST and BROWSER CRASH.
    
    Efficiency is a HABIT you develop, not a skill you fake.
    
    Learn Big O. Love Big O. Live Big O.
    
    #ComputerScience #Algorithms #Performance #Efficiency #Scalability""",

    """Simplicity is the Soul of Efficiency 🎯
    
    Can't explain your code to a junior dev in 5 minutes? It's OVER-ENGINEERED.
    
    Smart code is good. SIMPLE code is better.
    
    The best engineer isn't the one who writes the most clever solution—it's the one who solves it with elegance and clarity.
    
    #KISS #Programming #Mentorship #Clarity #Design""",

    """The Hardest Bug I Ever Solved 🐛
    
    ...turned out to be a TYPO.
    
    It's HUMBLING. No matter how senior you get, a missing semicolon or a misspelled variable can WRECK your day.
    
    We've ALL been there. You're not alone.
    
    #DevHorrorStories #Humor #TechLife #Relatable #Reality""",

    """Constraints Breed GENIUS 💎
    
    Working with STRICT API limits or SLOW servers forces you to be CLEVER.
    
    Don't complain about your tools' limitations. USE them to become a BETTER engineer.
    
    The best solutions come from fighting against the hardest problems.
    
    #Engineering #Creativity #ProblemSolving #Resilience #Innovation""",

    # --- WEEK 7: PERSONAL GROWTH ---
    """ "Expert" is RELATIVE 🎓
    
    To a complete beginner, you ARE an expert.
    To a senior dev, you're STILL a beginner.
    
    Don't wait until you're "the best" to start TEACHING. Share what you learned YESTERDAY—it's INVALUABLE to someone learning it TODAY.
    
    Mentorship is a privilege. Use it.
    
    #Teaching #ContentCreation #Growth #Mentorship #GivingBack""",

    """Open to Work 💼🚀
    
    Looking for opportunities where I can apply Python, Automation, and Creative Tech at scale.
    
    I love building SYSTEMS that solve REAL PROBLEMS. If you're hiring or want to collaborate, LET'S CHAT.
    
    Remote? Full-time? Contract? I'm flexible.
    
    #OpenToWork #JobSearch #Hiring #Opportunity #Connection""",

    """The Value of Deep Work 🧠⚡
    
    In a world of CONSTANT NOTIFICATIONS, the ability to FOCUS on one complex task for 4 hours is a SUPERPOWER.
    
    I TURN OFF MY PHONE when I code. The flow state is SACRED.
    
    Deep work is where REAL progress happens.
    
    #Productivity #DeepWork #Focus #FlowState #Mastery""",

    """Hobbies Outside of Tech 🎸🌲
    
    CRITICAL: Developers need non-screen hobbies.
    
    Cooking. Hiking. Music. Gaming. Whatever RESETS your brain.
    
    Step away from the keyboard. Your creativity NEEDS rest.
    
    What do YOU do when you're NOT coding? Drop it below!
    
    #LifeStyle #MentalHealth #HumanConnection #Balance #Wellbeing""",

    """Mentorship Changed My Career 🎯
    
    I'm GRATEFUL for the people who reviewed my TERRIBLE code and pointed me in the right direction.
    
    If you're senior: MENTOR a junior. If you're junior: FIND a mentor.
    
    It's the FASTEST way to grow. Period.
    
    #GivingBack #Community #TechLeadership #Mentorship #Paying ItForward""",

    """Fail Fast, Fail Often 💪
    
    BROKE my production build today. It happens.
    
    The goal ISN'T to never fail. The goal is to RECOVER QUICKLY and never make the SAME mistake twice.
    
    Resilience beats perfection. Always.
    
    #Resilience #Agile #StartupLife #Iteration #Growth""",

    """Reading Code is Harder Than Writing Code 📚
    
    Spending more time reading open-source GitHub projects. It's an EYE-OPENER.
    
    Seeing how OTHER engineers structure their projects teaches you MORE than tutorials.
    
    Want to write better novels? Read more books. Want better code? READ MORE CODE.
    
    #OpenSource #Learning #GitHub #CommunityCode #Inspiration""",

    # --- WEEK 8: THE FUTURE ---
    """Web3, VR, AI... The Tech Tsunami 🌊
    
    The landscape changes so FAST your head spins.
    
    But FUNDAMENTALS never change. Logic is logic. Data is data.
    
    Don't chase EVERY trend. MASTER the fundamentals and you can learn ANY framework in a week.
    
    Be a student of principles, not a slave to trends.
    
    #TechIndustry #Future #Advice #Fundamentals #WisdomOverTrends""",

    """The "No-Code" Movement 🔌
    
    Some devs FEAR no-code tools. I EMBRACE them.
    
    If a drag-and-drop tool builds the UI FASTER, awesome! That means I spend TIME on complex backend logic that NO-CODE can't touch.
    
    Tools are tools. Use them strategically.
    
    #NoCode #LowCode #Development #Pragmatism #Evolution""",

    """Ethics in Engineering ⚖️🤔
    
    Just because we CAN build it doesn't mean we SHOULD.
    
    As engineers, we have a RESPONSIBILITY to think about the IMPACT of our algorithms.
    
    Power + Responsibility = Ethical engineering.
    
    #TechEthics #Responsibility #Society #Morality #Leadership""",

    """Remote Work is Here to STAY 🏠
    
    Realized I don't need an OFFICE to be productive. I just need:
    
    ✅ Good internet
    ✅ Clear goals
    ✅ Focused time
    
    The world is now our job market. Location is no longer a limitation.
    
    #RemoteWork #DigitalNomad #FutureOfWork #Freedom #Opportunity""",

    # --- WEEK 9: WRAP UP & REFLECTION ---
    """60 Days of Automation 🤖✨
    
    If you've been following my posts, some are AUTOMATED.
    
    It's been a fascinating experiment in CONSISTENCY. Proved that tools maintain RELATIONSHIPS, but content must come from a HUMAN HEART.
    
    Thank you for keeping up.
    
    #Experiment #ProjectUpdate #Conclusion #Journey #Impact""",

    """What's Next? 🚀
    
    MASTERED the LinkedIn API basics. Now INTEGRATING OpenAI to brainstorm with me (not write FOR me).
    
    The journey NEVER ends. There's always another mountain to climb.
    
    #NextSteps #AI #Integration #Evolution #Growth""",

    """Thank You 💌
    
    To everyone who LIKED, COMMENTED, or CONNECTED—thank you.
    
    Technology is cool, but the COMMUNITY is what makes it worth it.
    
    Keep building. Keep learning. Keep SHIPPING.
    
    #Gratitude #Community #Together #TheEnd #NewBeginnings"""
]

# --- SENSOR 1: GITHUB ACTIVITY CHECKER ---
def get_latest_github_activity():
    print(f"🕵️ Checking GitHub activity for {GITHUB_USERNAME}...")
    url = f"https://api.github.com/users/{GITHUB_USERNAME}/events"
    response = requests.get(url)
    
    if response.status_code != 200:
        return None
        
    events = response.json()
    
    # Get today's date (UTC)
    today = datetime.datetime.now(datetime.timezone.utc).date()
    
    for event in events:
        # Check if it's a PushEvent (Code upload)
        if event['type'] == 'PushEvent':
            event_date = parser.isoparse(event['created_at']).date()
            
            # If the code was pushed TODAY (or yesterday)
            if event_date == today:
                repo_name = event['repo']['name']
                # Clean up the repo name (remove username/)
                clean_repo_name = repo_name.split('/')[-1]
                
                # Create a dynamic post
                post_text = (
                    f"🚀 Update: I just pushed some new code to my project '{clean_repo_name}' on GitHub!\n\n"
                    f"Building in public keeps me accountable. You can check out my progress here:\n"
                    f"https://github.com/{repo_name}\n\n"
                    f"#BuildInPublic #Python #Coding #DevLog"
                )
                return post_text
    
    print("No coding activity found for today. Switching to fallback mode.")
    return None

# --- THE POSTING FUNCTION ---
def post_to_linkedin(message_text):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    post_data = {
        "author": f"urn:li:person:{LINKEDIN_USER_URN}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": message_text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    
    print(f"🤖 Posting: '{message_text[:30]}...'")
    response = requests.post(url, headers=headers, json=post_data)
    if response.status_code == 201:
        print("\n✅ SUCCESS! Post is live.")
    else:
        print(f"\n❌ FAILED. {response.status_code}")

# --- MAIN BRAIN ---
if __name__ == "__main__":
    # 1. Try to get a dynamic update from GitHub
    post_content = get_latest_github_activity()
    
    # 2. If no GitHub update, pick a random static thought
    if post_content is None:
        post_content = random.choice(STATIC_POST_IDEAS)
        
    # 3. Post it
    post_to_linkedin(post_content)
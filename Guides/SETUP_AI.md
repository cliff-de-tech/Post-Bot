# AI Integration Setup Guide

PostBot supports **5 AI providers** for LinkedIn post generation. Groq is the default (free tier). Users can switch providers from the dashboard settings.

## Supported Providers

| Provider | Model | Tier | API Key Env Var |
|----------|-------|------|-----------------|
| **Groq** | llama-3.3-70b-versatile | Free | `GROQ_API_KEY` |
| **OpenAI** | gpt-4o | Pro | `OPENAI_API_KEY` |
| **Anthropic** | claude-3-5-sonnet-20241022 | Pro | `ANTHROPIC_API_KEY` |
| **Mistral** | mistral-large-latest | Pro | `MISTRAL_API_KEY` |
| **Gemini** | gemini-1.5-flash | Pro | `GEMINI_API_KEY` |

## Quick Setup

### 1. Get an API Key

| Provider | Where to get a key |
|----------|-------------------|
| Groq | [console.groq.com](https://console.groq.com) |
| OpenAI | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| Anthropic | [console.anthropic.com](https://console.anthropic.com) |
| Mistral | [console.mistral.ai](https://console.mistral.ai) |
| Gemini | [aistudio.google.com](https://aistudio.google.com) |

### 2. Set Environment Variables

Add one or more keys to your `.env` file:

```env
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...          # optional
ANTHROPIC_API_KEY=sk-ant-...   # optional
MISTRAL_API_KEY=...            # optional
GEMINI_API_KEY=...             # optional
```

At least one provider key is required. Groq is recommended for development (free tier).

### 3. Configure via Dashboard

Users select their preferred AI provider from **Settings > AI Provider** in the dashboard. The backend validates the key and uses the selected provider for all post generation.

## How It Works

### Generation Flow

```
1. User requests post generation (manual or scheduled)
   ↓
2. Backend loads user's selected AI provider
   ↓
3. Persona context + GitHub activity assembled into prompt
   ↓
4. AI provider generates post draft
   ↓
5. Post saved to database (editable before publishing)
```

### AI Service Architecture

All providers are managed by `services/ai_service.py` with lazy-loaded singleton clients. Each provider implements the same interface — only the API call differs.

### Persona System

Each user has a persona profile (built via `services/persona_service.py`) that shapes the AI's writing style:

- Writing tone (professional, casual, technical)
- Topics of interest
- Post length preferences
- Hashtag strategy
- Industry context

## Troubleshooting

| Error | Solution |
|---|---|
| `AI provider not configured` | Ensure at least one API key is set in `.env` |
| `Invalid API key` | Regenerate key from the provider's console |
| `Rate limit exceeded` | Wait and retry, or switch to a different provider |
| Post quality issues | Adjust persona settings in the dashboard |

## Security Notes

- API keys are stored encrypted (Fernet) in the database
- Keys are never returned to the frontend — only masked previews
- Provider clients are lazy-loaded (no initialization cost at startup)
- All AI calls include structured logging (no secrets in logs)

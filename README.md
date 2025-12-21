# LinkedIn Post Bot 🤖

An AI-powered LinkedIn content automation platform that transforms your GitHub activity into engaging LinkedIn posts. Available as both a **command-line bot** and a **full-featured web application**.

![LinkedIn Post Bot](https://img.shields.io/badge/LinkedIn-Post%20Bot-0A66C2?style=for-the-badge&logo=linkedin)
![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)
![Python](https://img.shields.io/badge/Python-3.14-blue?style=for-the-badge&logo=python)
![Groq](https://img.shields.io/badge/Groq-AI-orange?style=for-the-badge)

## ✨ Features

### Web Application
- 🎨 **Modern Dashboard** - Beautiful dark/light mode UI with real-time stats
- 🤖 **Bot Mode Panel** - Scan GitHub activity, generate AI posts, and publish in one flow
- � **Custom Day Filters** - Scan GitHub activity from 1-30 days
- 🎯 **Activity Type Filters** - Filter by Push, PR, Commits, New Repo, or Generic posts
- 💡 **Smart Suggestions** - Get alternative activities when your preferred type isn't found
- 🖼️ **Unsplash Integration** - Add beautiful images to your posts
- 📊 **Analytics** - Track your posting history and engagement
- � **Multi-tenant Auth** - Per-user credentials with Clerk authentication

### CLI Bot
- ⚡ **Automated Posting** - Schedule daily posts with cron/Task Scheduler
- 🧠 **AI Generation** - Groq LLM creates engaging, natural posts
- 📚 **60-Day Content Library** - Pre-written fallback posts
- 🔄 **GitHub Activity Sync** - Auto-fetch your coding activity

---

## 🚀 Quick Start

### Option 1: Web Application (Recommended)

#### Prerequisites
- Node.js 18+
- Python 3.10+
- Clerk account (free tier available)

#### 1. Clone & Install

```bash
git clone https://github.com/cliff-de-tech/linkedin-post-bot.git
cd linkedin-post-bot

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd web
npm install
```

#### 2. Configure Environment Variables

**Backend `.env`:**
```bash
cp .env.example .env
```

Edit `.env`:
```env
# LinkedIn OAuth (get from LinkedIn Developers Portal)
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret

# AI Generation (get from console.groq.com)
GROQ_API_KEY=your_groq_api_key

# GitHub (your username)
GITHUB_USERNAME=your_github_username

# Optional: Images
UNSPLASH_ACCESS_KEY=your_unsplash_key

# Clerk Auth (for multi-user support)
CLERK_ISSUER=https://your-clerk-instance.clerk.accounts.dev
```

**Frontend `web/.env.local`:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key
CLERK_SECRET_KEY=sk_test_your_key
```

#### 3. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
py app.py
# or: python app.py
```

**Terminal 2 - Frontend:**
```bash
cd web
npm run dev
```

#### 4. Open in Browser
Visit `http://localhost:3000` and complete the onboarding flow!

---

### Option 2: CLI Bot (Standalone)

For automated daily posting without the web UI:

```bash
# 1. Configure credentials in bot.py or .env
# 2. Run authentication
python auth.py

# 3. Run the bot
python bot.py

# 4. Schedule (optional)
# Windows: schtasks /create /tn "LinkedInBot" /tr "python bot.py" /sc daily /st 09:00
# Linux/Mac: crontab -e → 0 9 * * * /usr/bin/python3 /path/to/bot.py
```

---

## 🔑 Getting API Keys

### LinkedIn Developer App
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers)
2. Create new app → Set redirect URL: `http://localhost:8000/auth/linkedin/callback`
3. Request these OAuth scopes: `openid`, `profile`, `email`, `w_member_social`
4. Copy **Client ID** and **Client Secret**

### Groq AI Key
1. Visit [console.groq.com](https://console.groq.com)
2. Create account → API Keys → Generate new key
3. Free tier includes generous rate limits

### Unsplash (Optional)
1. Visit [unsplash.com/developers](https://unsplash.com/developers)
2. Create app → Copy **Access Key**

### Clerk Authentication
1. Visit [clerk.com](https://clerk.com)
2. Create application → Copy **Publishable Key** and **Secret Key**
3. Set Frontend API URL in Clerk dashboard

---

## 📁 Project Structure

```
linkedin-post-bot/
├── web/                    # Next.js Frontend
│   ├── src/
│   │   ├── pages/          # Routes (dashboard, settings, onboarding)
│   │   ├── components/     # UI Components
│   │   └── lib/            # Utilities & API clients
│   └── public/             # Static assets
├── backend/                # FastAPI Backend
│   ├── app.py              # Main API server
│   └── middleware/         # Auth middleware
├── services/               # Core Services
│   ├── ai_service.py       # Groq AI integration
│   ├── github_activity.py  # GitHub API
│   ├── linkedin_service.py # LinkedIn posting
│   ├── image_service.py    # Unsplash images
│   ├── user_settings.py    # Settings storage
│   └── token_store.py      # OAuth token management
├── bot.py                  # Standalone CLI bot
├── auth.py                 # OAuth helper
└── .env.example            # Environment template
```

---

## 🖥️ Using the Web App

### Dashboard Overview
- **Stats Overview** - Posts generated, published, drafts count
- **Bot Mode Panel** - Main workflow for generating posts
- **GitHub Activity Feed** - See your recent coding activity
- **Post Editor** - Manually create posts with custom context

### Bot Mode Workflow
1. **Select Time Range** - Choose 1, 3, 7, 14, or 30 days
2. **Filter Activity Type** - All, Push, PR, Commits, New Repo, Generic
3. **Scan GitHub** - Fetches your recent activity
4. **Generate Posts** - AI creates LinkedIn-optimized content
5. **Review & Edit** - Modify posts before publishing
6. **Add Images** - Optional Unsplash image selection
7. **Publish** - Post to LinkedIn (supports test mode)

### Settings Page
- Save credentials individually with dedicated Save buttons
- Connect LinkedIn via OAuth
- View saved credentials (masked for security)
- Buttons show "✓ Saved" when credentials are stored

---

## 🛠️ Development

### Run in Development Mode
```bash
# Backend with auto-reload
cd backend && uvicorn app:app --reload --port 8000

# Frontend with hot-reload
cd web && npm run dev
```

### Build for Production
```bash
cd web
npm run build
npm run start
```

### Lint & Type Check
```bash
cd web
npm run lint
npm run build  # TypeScript check
```

---

## 🔒 Security Features

- **Per-user credentials** - Each user stores their own API keys
- **Masked secrets** - API keys shown as `gsk_xxxx...xxxx` in UI
- **Clerk JWT verification** - Secure API endpoints
- **CORS protection** - API only accepts authorized origins
- **Environment variables** - Never commit secrets to git

---

## 🌐 Deployment

### Vercel (Frontend)
```bash
cd web
npx vercel --prod
```

### Railway/Render (Backend)
Deploy `backend/` with Python runtime, set environment variables.

### Docker (Coming Soon)
```bash
docker-compose up -d
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No GitHub activity found" | Check GITHUB_USERNAME, extend day range |
| LinkedIn auth fails | Verify Client ID/Secret, check redirect URL |
| AI posts are empty | Check GROQ_API_KEY is valid |
| Credentials not saving | Restart backend, check console for errors |
| "Invalid token" error | Re-authenticate with LinkedIn |

---

## 🗺️ Roadmap

- [ ] Scheduled posting (queue posts for specific times)
- [ ] Multi-account support
- [ ] Analytics dashboard with engagement metrics
- [ ] AI persona customization
- [ ] Docker deployment package
- [ ] Mobile app (React Native)

---

## 📄 License

MIT License - Use freely for personal and commercial projects.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

**Made with ❤️ by [cliff-de-tech](https://github.com/cliff-de-tech)**

Happy posting! 🚀

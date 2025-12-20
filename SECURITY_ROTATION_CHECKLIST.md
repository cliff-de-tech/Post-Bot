# Security Incident Response - Credential Rotation Checklist

**Incident:** Public leak detected on December 20, 2025  
**Affected Secrets:**
1. Google API Key (bot.py:14) - `AIzaSyCJE68mgN7XdYh5rNSPHui...`
2. LinkedIn Client Secret (auth.py:8) - `WPL_AP1.zZAW2G8BlWjm8HeX.AS...`

---

## ⚠️ CRITICAL - DO IMMEDIATELY (Priority 1)

### 1. Revoke Google API Key

**Steps:**
1. Open [Google Cloud Console - Credentials](https://console.cloud.google.com/apis/credentials)
2. Find the API key starting with `AIzaSyCJE68mgN7XdYh5rNSPHui...`
3. Click **⋮** (three dots) → **Delete** or **Restrict immediately**
4. **Create new API key:**
   - Click **+ CREATE CREDENTIALS** → **API key**
   - **Immediately restrict the new key:**
     - Application restrictions: Set HTTP referrers or IP addresses
     - API restrictions: Select only the APIs your bot needs
5. **Copy the new key** (you'll only see it once)

**Test new key locally:**
```powershell
$env:GROQ_API_KEY = "YOUR_NEW_GOOGLE_KEY_HERE"
python -c "import os; print('Key length:', len(os.getenv('GROQ_API_KEY')))"
```

---

### 2. Revoke LinkedIn Client Secret & Regenerate Access Token

**Steps:**
1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Select your app → **Auth** tab
3. Under **Client Secret**, click **Regenerate**
4. **Copy the new Client Secret** (shown only once)
5. **Re-authorize to get new access token:**
   ```powershell
   # Set new client secret
   $env:LINKEDIN_CLIENT_ID = "77hpfpf5cv4m4t"
   $env:LINKEDIN_CLIENT_SECRET = "YOUR_NEW_CLIENT_SECRET_HERE"
   
   # Run auth flow
   python auth.py
   ```
6. Follow the OAuth flow and copy the new `ACCESS_TOKEN` and `USER_URN`

**Test new credentials:**
```powershell
$env:LINKEDIN_ACCESS_TOKEN = "YOUR_NEW_ACCESS_TOKEN_HERE"
$env:LINKEDIN_USER_URN = "YOUR_USER_URN_HERE"
python -c "import os; print('Token set:', bool(os.getenv('LINKEDIN_ACCESS_TOKEN')))"
```

---

### 3. Rotate GitHub Personal Access Token (if exposed)

**Steps:**
1. Go to [GitHub Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Find token starting with `github_pat_11BAYGHYI0...`
3. Click **Delete** or **Revoke**
4. Create new token:
   - Click **Generate new token (classic)**
   - Scopes: Select only `repo` (read access) if bot only reads activity
   - Set expiration (recommended: 90 days)
5. Copy new token

**Test:**
```powershell
$env:MY_GITHUB_TOKEN = "YOUR_NEW_GITHUB_TOKEN_HERE"
python -c "import os; print('Token set:', bool(os.getenv('MY_GITHUB_TOKEN')))"
```

---

### 4. Rotate Unsplash Access Key (if exposed)

**Steps:**
1. Go to [Unsplash Applications](https://unsplash.com/oauth/applications)
2. Select your app → scroll to **Keys**
3. Click **Regenerate Access Key** or **Roll Keys**
4. Copy new access key

---

## 🔒 SECURE - Update Repository Secrets (Priority 2)

### Add NEW secrets to GitHub Actions

**Option A: Using GitHub CLI (`gh`)**
```bash
# Install gh CLI if needed: https://cli.github.com/

gh secret set LINKEDIN_CLIENT_SECRET
# Paste new secret when prompted

gh secret set LINKEDIN_ACCESS_TOKEN
# Paste new token

gh secret set LINKEDIN_USER_URN
# Paste URN

gh secret set GROQ_API_KEY
# Paste new Google/Groq key

gh secret set UNSPLASH_ACCESS_KEY
# Paste new Unsplash key

gh secret set MY_GITHUB_TOKEN
# Paste new GitHub token

gh secret set MY_GITHUB_USERNAME --body "cliff-de-tech"
```

**Option B: Using GitHub Web UI**
1. Go to repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** for each:
   - `LINKEDIN_CLIENT_SECRET` = new client secret
   - `LINKEDIN_ACCESS_TOKEN` = new access token
   - `LINKEDIN_USER_URN` = your URN
   - `GROQ_API_KEY` = new Google/Groq key
   - `UNSPLASH_ACCESS_KEY` = new Unsplash key
   - `MY_GITHUB_TOKEN` = new GitHub token
   - `MY_GITHUB_USERNAME` = cliff-de-tech

**Verify secrets are set:**
```bash
gh secret list
```

---

## 🧹 CLEANUP - Purge Secrets from Git History (Priority 3)

**WARNING:** This rewrites history and requires force-push. Coordinate with collaborators.

### Method 1: Using git-filter-repo (Recommended)

**Install git-filter-repo:**
```powershell
pip install git-filter-repo
```

**Backup your repo first:**
```powershell
cd "C:\Users\Lois Adu Yeboah\Desktop"
cp -r Linkedin-Post-Bot Linkedin-Post-Bot-BACKUP
cd Linkedin-Post-Bot
```

**Create patterns file:**
```powershell
# Create file: secrets-to-remove.txt
@"
AIzaSyCJE68mgN7XdYh5rNSPHui
WPL_AP1.zZAW2G8BlWjm8HeX
github_pat_11BAYGHYI0
gsk_gx3rK7pp3iTDJ4
AQXro0Ks4o2c2vYxGua55s
cJLnxL4gVZlRpG-VOVunp3l
"@ | Out-File -FilePath secrets-to-remove.txt -Encoding UTF8
```

**Run filter-repo:**
```powershell
git filter-repo --replace-text secrets-to-remove.txt --force
```

**Force push cleaned history:**
```powershell
git remote add origin https://github.com/cliff-de-tech/Linkedin-Post-Bot.git
git push origin --force --all
git push origin --force --tags
```

**Notify collaborators to re-clone:**
```bash
# They must delete their local copy and re-clone
git clone https://github.com/cliff-de-tech/Linkedin-Post-Bot.git
```

---

### Method 2: Using BFG Repo-Cleaner (Alternative)

**Download BFG:**
```powershell
# Download from: https://rtyley.github.io/bfg-repo-cleaner/
# Save as bfg.jar
```

**Run BFG:**
```powershell
java -jar bfg.jar --replace-text secrets-to-remove.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin --force --all
```

---

## 🛡️ PREVENTION - Add Secret Scanning (Priority 4)

### Enable GitHub Secret Scanning
1. Repo → **Settings** → **Security** → **Code security and analysis**
2. Enable **Secret scanning**
3. Enable **Push protection** (prevents future commits with secrets)

### Add pre-commit hook (local protection)
```powershell
pip install pre-commit
```

**Create `.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

**Install hook:**
```powershell
pre-commit install
pre-commit run --all-files
```

---

## ✅ VERIFICATION CHECKLIST

- [ ] Google API key revoked and new key created
- [ ] LinkedIn client secret regenerated
- [ ] LinkedIn access token refreshed via OAuth
- [ ] GitHub token revoked and new token created
- [ ] Unsplash key rotated
- [ ] All new secrets added to GitHub Actions secrets
- [ ] Verified workflow runs with new secrets (test run)
- [ ] Git history purged using git-filter-repo or BFG
- [ ] Force-pushed cleaned history to remote
- [ ] Collaborators notified to re-clone
- [ ] Secret scanning enabled on repository
- [ ] Pre-commit hooks installed locally

---

## 📋 POST-INCIDENT ACTIONS

1. **Monitor for unauthorized usage:**
   - Check Google Cloud billing for unexpected API calls
   - Review LinkedIn app analytics for unusual activity
   - Check GitHub audit log for suspicious access

2. **Document lessons learned:**
   - Never commit `.env` files (already in `.gitignore`)
   - Use secret scanning tools before pushing
   - Rotate credentials every 90 days

3. **Set expiration reminders:**
   - Google API key: Review restrictions quarterly
   - LinkedIn tokens: Expire and refresh every 60 days
   - GitHub tokens: Set 90-day expiration

---

## 🆘 SUPPORT

- **Google Cloud Support:** https://cloud.google.com/support
- **LinkedIn Developer Support:** https://www.linkedin.com/help/linkedin
- **GitHub Security:** https://docs.github.com/en/code-security

---

**Last Updated:** December 20, 2025  
**Incident Status:** Active - Awaiting credential rotation

# Claudeflare Slack Bridge - Project Index

Your complete Cloudflare Workers API for bridging Slack and GitHub Actions.

## 📚 Documentation Files (Start Here!)

| File | Purpose | For Whom |
|------|---------|----------|
| **[QUICK_START.md](QUICK_START.md)** | 5-minute setup guide with examples | Everyone - start here! |
| **[DEPLOY_SCRIPTS.md](DEPLOY_SCRIPTS.md)** | Automated deployment scripts guide | Users who want one-command deploy |
| **[README.md](README.md)** | Comprehensive user guide and usage | Users and integrators |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Detailed deployment & troubleshooting | DevOps, manual deployment |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System design, API specs, internals | Developers, extenders |
| **[This file](INDEX.md)** | Project overview and file guide | Navigation |

## 🚀 Getting Started

### For First-Time Users
1. Read **[QUICK_START.md](QUICK_START.md)** (5 min)
2. Follow the 5-minute setup
3. Test in Slack: `@Panchang Bot 2026-06-15`

### For Deployments
1. Read **[DEPLOYMENT.md](DEPLOYMENT.md)**
2. Follow checklist step-by-step
3. Monitor with `wrangler tail`

### For Development/Extension
1. Read **[ARCHITECTURE.md](ARCHITECTURE.md)**
2. Review API specifications
3. Modify `src/` files as needed

### For Troubleshooting
1. Check **[README.md](README.md)** → Troubleshooting section
2. Run `wrangler tail` to view logs
3. Use `python test_events.py` to test locally

## 📁 Project Structure

```
claudeflare-api/
│
├── 📖 DOCUMENTATION
│   ├── README.md                    ⭐ Main documentation
│   ├── QUICK_START.md              ⭐ 5-minute setup
│   ├── DEPLOY_SCRIPTS.md           ⭐ One-command deployment
│   ├── DEPLOYMENT.md               📋 Deployment guide
│   ├── ARCHITECTURE.md             🔧 System design & API
│   └── INDEX.md                    📑 This file
│
├── 🔧 SOURCE CODE
│   ├── src/
│   │   ├── index.ts                🎯 Main Worker entry point
│   │   └── utils/
│   │       ├── slack-verify.ts     ✓ Signature verification
│   │       ├── slack-parse.ts      📅 Date extraction
│   │       ├── slack-respond.ts    💬 Slack responses
│   │       └── github-dispatch.ts  🔄 GitHub trigger
│   │
│   └── tsconfig.json               TypeScript configuration
│
├── ⚙️ CONFIGURATION
│   ├── wrangler.toml               🎛️ Cloudflare config
│   ├── package.json                📦 NPM dependencies
│   ├── .env.example                🔐 Environment template
│   └── .gitignore                  🚫 Git ignore rules
│
├── 🧪 TESTING
│   └── test_events.py              📝 Local event simulator
│
├── 🌐 GITHUB INTEGRATION
│   └── example-github-workflow.yml 📋 GitHub Actions workflow
│
└── 🚀 DEPLOYMENT AUTOMATION
    ├── deploy.ps1                  ⭐ PowerShell script (Windows)
    ├── deploy.sh                   ⭐ Bash script (Unix/Linux)
    ├── deploy.js                   ⭐ Node.js wrapper (cross-platform)
    ├── DEPLOY_SCRIPTS.md           📋 Deployment scripts guide
    └── setup.sh                    ⚡ Legacy setup script
```

## 📄 File Descriptions

### Documentation

#### QUICK_START.md
- **What:** 5-minute setup guide
- **Length:** ~200 lines
- **Contains:** Step-by-step instructions, supported formats, troubleshooting
- **For:** New users who want to get running fast

#### README.md
- **What:** Complete reference documentation
- **Length:** ~500 lines
- **Contains:** Overview, setup, configuration, API endpoints, security, FAQ
- **For:** Users, maintainers, anyone building on this

#### DEPLOYMENT.md
- **What:** Detailed deployment & configuration guide
- **Length:** ~400 lines
- **Contains:** Pre-deployment checklist, step-by-step, environment vars, verification
- **For:** DevOps, production deployments

#### ARCHITECTURE.md
- **What:** System architecture & API reference
- **Length:** ~600 lines
- **Contains:** Data flows, event specs, security model, extension guide
- **For:** Developers extending the system

### Source Code

#### src/index.ts
- **What:** Main Worker entry point
- **Lines:** ~150
- **Does:**
  - Handles POST /slack/events
  - Handles GET /health
  - Verifies Slack signatures
  - Orchestrates event processing
  - Error handling & logging

#### src/utils/slack-verify.ts
- **What:** Slack signature verification
- **Lines:** ~70
- **Does:**
  - HMAC-SHA256 signature validation
  - Timestamp verification (prevents replay attacks)
  - Constant-time comparison (prevents timing attacks)

#### src/utils/slack-parse.ts
- **What:** Slack event parsing & date extraction
- **Lines:** ~180
- **Does:**
  - Parse different event types (app_mention, message, etc.)
  - Extract dates in multiple formats
  - Support natural language dates (e.g., "June 15, 2026")
  - Filter irrelevant messages

#### src/utils/github-dispatch.ts
- **What:** GitHub workflow dispatch trigger
- **Lines:** ~80
- **Does:**
  - Call GitHub API to dispatch workflow
  - Handle authentication
  - Return success/failure status

#### src/utils/slack-respond.ts
- **What:** Slack response handling
- **Lines:** ~90
- **Does:**
  - Send confirmation messages to Slack
  - Use response URLs from events
  - Error handling for response failures

#### tsconfig.json
- **What:** TypeScript configuration
- **Sets:** Compilation target, strict mode, lib versions

### Configuration Files

#### wrangler.toml
- **What:** Cloudflare Workers configuration
- **Contains:**
  - Worker name & entry point
  - Build configuration
  - Environment-specific routes
  - Runtime variables (GITHUB_OWNER, GITHUB_REPO)

#### package.json
- **What:** Node.js project metadata
- **Contains:**
  - Project name & version
  - Build/deploy/dev scripts
  - Dependencies (minimal, optimized for Workers)
  - Dev dependencies (TypeScript, Wrangler)

#### .env.example
- **What:** Template for environment variables
- **Use:** Copy to .env.local and fill in your values

#### .gitignore
- **What:** Git ignore rules
- **Ignores:** node_modules, dist, .env, secrets, logs

### Testing & Examples

#### test_events.py
- **What:** Local testing harness for Slack events
- **Language:** Python 3
- **Tests:**
  - Health check endpoint
  - URL verification challenge
  - App mention with date
  - Message with date
  - Natural language dates
  - Invalid signatures
  - Invalid date formats
- **Usage:** `python test_events.py <test_name>`

#### example-github-workflow.yml
- **What:** GitHub Actions workflow that receives dispatches
- **Use:** Copy to `.github/workflows/panchang-webhook.yml` in your repo
- **Triggers:** On repository_dispatch with type "panchang-webhook"
- **Jobs:** Calculate panchangam, notify on failure

#### setup.sh
- **What:** Automated setup script
- **Language:** Bash
- **Does:**
  - Check Node.js & npm installed
  - Install Wrangler CLI
  - Install npm dependencies
  - Compile TypeScript
  - Create .env.local template

## 🔄 Data Flow Summary

```
Slack Message (with date)
    ↓
Worker receives /slack/events POST
    ↓
Verify Slack signature
    ↓
Parse event & extract date
    ↓
Validate date format (YYYY-MM-DD)
    ↓
Trigger GitHub workflow dispatch
    ↓
Send confirmation back to Slack
    ↓
GitHub Actions runs Panchang calculation
    ↓
Results posted to Slack webhook
    ↓
User sees results in Slack channel ✓
```

## 🎯 Key Features

✅ **Slack Integration** - Receives events via webhook  
✅ **Date Extraction** - Multiple format support (ISO, natural language)  
✅ **GitHub Trigger** - Dispatches workflows with date payload  
✅ **Security** - HMAC signature verification, timestamp validation  
✅ **Error Handling** - Clear error messages back to Slack  
✅ **Logging** - Full request/response logging via `wrangler tail`  
✅ **Serverless** - Zero infrastructure to manage  
✅ **Global Edge** - Deployed to 300+ Cloudflare edge locations  

## 🔐 Security Features

- ✓ HMAC-SHA256 signature verification on all Slack requests
- ✓ Timestamp validation to prevent replay attacks (5-min window)
- ✓ Constant-time string comparison to prevent timing attacks
- ✓ All secrets stored in Cloudflare encrypted secrets (not in code)
- ✓ GitHub token with minimum required scopes
- ✓ No logging of sensitive data

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Total lines of code | ~600 |
| Total documentation | ~2000 |
| Number of modules | 5 |
| Test scenarios | 8 |
| GitHub Actions workflows | 1 |
| Dependencies | 0 (production) |
| Dev dependencies | 4 |

## 🚀 Deployment Architecture

```
Your Computer
    ↓ (git push or npm run deploy)
Cloudflare API
    ↓ (compile & deploy)
Cloudflare Global Network (300+ locations)
    ↓ (auto-route to nearest)
Receives Slack webhooks → Process → Trigger GitHub → Respond
    ↓ (billions of requests/day capacity)
Fast, reliable, zero cold-start
```

## 🎓 Learning Path

### Beginner
1. QUICK_START.md
2. Test in Slack
3. Monitor logs with `wrangler tail`

### Intermediate
1. README.md (full guide)
2. DEPLOYMENT.md (production setup)
3. Run test_events.py locally

### Advanced
1. ARCHITECTURE.md (system design)
2. Read source code (src/ directory)
3. Modify for your needs
4. Deploy custom version

## 🔗 Related Resources

### External Documentation
- **Cloudflare Workers Docs:** https://developers.cloudflare.com/workers/
- **Slack API Docs:** https://api.slack.com/
- **GitHub Actions Docs:** https://docs.github.com/en/actions/

### Parent Project
- **My-Panchang-Agent:** https://github.com/{GITHUB_OWNER}/My-Panchang-Agent
- **Panchang Calculations:** Astronomical calculations for Hindu calendar

### Configuration Files in Parent Repo
- `.github/workflows/panchang-webhook.yml` - GitHub workflow
- `main.py` - Panchang calculation entry point
- `config.py` - Configuration (location, timezone, etc.)

## 📞 Support & Troubleshooting

### Quick Checks
```bash
# 1. Is the worker running?
curl https://your-worker.workers.dev/health

# 2. Are secrets configured?
wrangler secret list

# 3. What are the recent logs?
wrangler tail

# 4. Can you test locally?
npm run dev
python test_events.py health
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Unauthorized" from Slack | Check SLACK_SIGNING_SECRET secret |
| "Failed to trigger workflow" | Check GITHUB_TOKEN secret and repo exists |
| "No date extracted" | Verify date format (try 2026-06-15) |
| Slack app not receiving | Check Event Subscription URL is correct |
| Worker not deployed | Run `wrangler login` then `npm run deploy` |

### Getting Help
1. **Logs:** `wrangler tail`
2. **Docs:** This README and related files
3. **Tests:** `python test_events.py`
4. **Issues:** Check GitHub repo issues

## 📝 Quick Commands

```bash
# Setup
npm install
wrangler login

# Development
npm run dev                    # Local server
npm run build                  # Compile TS
npm run build -- --watch     # Watch mode

# Deployment
npm run deploy                 # Production
npm run deploy:staging         # Staging
wrangler delete               # Remove worker

# Secrets
wrangler secret put NAME      # Set secret
wrangler secret list          # View secrets
wrangler secret delete NAME   # Delete secret

# Monitoring
wrangler tail                 # View logs
wrangler deployments list     # View history
wrangler rollback             # Rollback

# Testing
python test_events.py health
python test_events.py mention
python test_events.py message
```

## 📋 Checklist: From Zero to Production

- [ ] Read QUICK_START.md
- [ ] Create Cloudflare account
- [ ] Create Slack app
- [ ] Generate GitHub token
- [ ] Run `npm install`
- [ ] Run `wrangler login`
- [ ] Run `npm run deploy`
- [ ] Set 3 Cloudflare secrets
- [ ] Configure Slack Event Subscription URL
- [ ] Test: `@Panchang Bot 2026-06-15`
- [ ] Set up GitHub workflow
- [ ] Verify results in Slack ✓

---

**Next Step:** Read [QUICK_START.md](QUICK_START.md) or [DEPLOYMENT.md](DEPLOYMENT.md)

**Version:** 1.0.0  
**Last Updated:** 2026-05-22  
**Status:** Production Ready ✓

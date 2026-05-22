# Quick Start Guide

## What is Claudeflare?

A **Cloudflare Workers API** that bridges your Slack workspace with your Panchang Agent GitHub Actions workflow.

```
Your Slack Channel → "Calculate for 2026-06-15" → Trigger GitHub Workflow → Results posted to Slack
```

## In 5 Minutes (Complete Automation)

### 1. One Command Deployment

Navigate to the project:
```bash
cd claudeflare-api
```

Run the unified deployment script:
```bash
npm run deploy
```

That's it! The script handles:
- ✅ Environment checks
- ✅ Dependencies installation
- ✅ TypeScript compilation  
- ✅ Cloudflare authentication
- ✅ **Interactive secret configuration** (you'll be prompted)
- ✅ Deployment to Cloudflare
- ✅ Post-deployment instructions

**Alternative commands:**
```bash
npm run deploy:prod          # Explicit production
npm run deploy:staging       # Deploy to staging
npm run deploy:skip-secrets  # Skip re-entering secrets
npm run deploy:dry-run       # Preview without deploying
```

### What Happens During Deploy

When you run `npm run deploy`, you'll see:

```
✅ Node.js: v18.x.x
✅ npm: 9.x.x
✅ Dependencies installed
✅ TypeScript compiled successfully
ℹ️  Checking Cloudflare authentication...
✅ Already authenticated with Cloudflare

[Prompts you for secrets]
Enter GITHUB_TOKEN: ghp_xxxxx...
Enter SLACK_SIGNING_SECRET: xxxxx...
Enter SLACK_WEBHOOK_URL: (optional)

ℹ️  Starting deployment...
✅ Deployment completed successfully!

🎉 Your Claudeflare Worker is live!
```

**Your Worker URL** will be shown: `https://panchang-slack-bridge.<subdomain>.workers.dev`

### 2. Configure Slack App (Final Step)

1. Go to https://api.slack.com/apps
2. Select your Panchang Bot app
3. **Event Subscriptions** → Enable Events
4. Request URL: `https://panchang-slack-bridge.<subdomain>.workers.dev/slack/events`
5. Wait for green checkmark ✅
6. Subscribe to bot events (if not done):
   - `app_mention`
   - `message.channels`
   - `message.groups`
7. Save changes

### 3. Test It!

In Slack, mention your bot:
```
@Panchang Bot 2026-06-15
```

You should see:
- ✅ Confirmation in Slack
- 🔄 Workflow triggered in GitHub Actions
- 📊 Results posted to Slack

**Done!** 🎉

---

## Manual Step-by-Step (If Needed)

If you prefer manual control or the automated script doesn't work:

```bash
# 1. Install dependencies
npm install

# 2. Build TypeScript
npm run build

# 3. Authenticate with Cloudflare
npm install -g wrangler
wrangler login

# 4. Set secrets manually
wrangler secret put GITHUB_TOKEN
wrangler secret put SLACK_SIGNING_SECRET
wrangler secret put SLACK_WEBHOOK_URL

# 5. Deploy
wrangler deploy
```

## Supported Date Formats

Your message can contain dates in any of these formats:

```
2026-06-15           ← ISO standard (YYYY-MM-DD) ✅
June 15, 2026        ← Natural language ✅
15/06/2026           ← DD/MM/YYYY ✅
06/15/2026           ← MM/DD/YYYY ✅
```

## Example Slack Messages

```
@Panchang Bot 2026-06-15
→ Extracts: 2026-06-15 ✅

Calculate panchangam for June 15, 2026
→ Extracts: 2026-06-15 ✅

@Panchang please calculate for 2026-06-15
→ Extracts: 2026-06-15 ✅
```

## File Structure

```
claudeflare-api/
├── README.md                    ← Comprehensive guide
├── DEPLOYMENT.md               ← Step-by-step deployment
├── QUICK_START.md              ← This file
├── src/
│   ├── index.ts                ← Main Worker code
│   └── utils/                  ← Helper modules
├── test_events.py              ← Local testing script
├── wrangler.toml               ← Cloudflare config
├── package.json                ← Dependencies
└── tsconfig.json               ← TypeScript config
```

## Troubleshooting

### "Event not received"
1. Check Slack app is installed: Workspace in menu → Your Workspace → Panchang Bot
2. Verify Event Subscription URL is correct
3. Check Cloudflare logs: `wrangler tail`

### "GitHub not triggered"
1. Verify `GITHUB_TOKEN` secret is set: `wrangler secret list`
2. Check token has `repo` scope
3. Check `.github/workflows/panchang-webhook.yml` exists

### "Signature verification failed"
1. Verify `SLACK_SIGNING_SECRET` matches exactly
2. Check system time is synced

## Local Development

Test locally before deploying:

```bash
# Start local server
npm run dev

# In another terminal, test with
python test_events.py health
python test_events.py verify
python test_events.py mention
```

## Key Features

✅ **Slack Signature Verification** - Only Slack requests are processed  
✅ **Automatic Date Extraction** - Multiple date formats supported  
✅ **GitHub Workflow Trigger** - Dispatches with date payload  
✅ **Error Handling** - Clear feedback on failures  
✅ **Logging** - View all events via `wrangler tail`  
✅ **No Cold Starts** - Cloudflare edge workers are instant  

## Environment Variables Needed

**In Cloudflare Secrets (via `wrangler secret put`):**
- `GITHUB_TOKEN` - GitHub PAT for workflow dispatch
- `SLACK_SIGNING_SECRET` - Slack app signing secret
- `SLACK_WEBHOOK_URL` - (Optional) Slack incoming webhook

**In GitHub Actions Secrets:**
- `SLACK_WEBHOOK_URL` - For posting results back to Slack

**In Slack App:**
- Signing Secret - For request verification

## Next Steps

1. **Read full docs:** See [README.md](README.md)
2. **Deployment details:** See [DEPLOYMENT.md](DEPLOYMENT.md)
3. **Test locally:** Run `python test_events.py`
4. **Set up GitHub workflow:** Copy `example-github-workflow.yml`
5. **Monitor logs:** Use `wrangler tail`

## Common Commands

```bash
# Development
npm run dev          # Start local server
npm run build        # Compile TypeScript

# Deployment
npm run deploy       # Deploy to production
npm run deploy:staging  # Deploy to staging

# Maintenance
wrangler tail        # View logs
wrangler secret put NAME  # Set secret
wrangler secret list # List secrets
wrangler delete      # Delete worker

# Testing
python test_events.py health
python test_events.py mention
```

## Need Help?

1. **Check logs:** `wrangler tail`
2. **Read README:** Full documentation in [README.md](README.md)
3. **View workflows:** GitHub repo → Actions tab
4. **Test events:** Use `test_events.py` script
5. **Parent project:** https://github.com/{GITHUB_OWNER}/My-Panchang-Agent

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                  SLACK WORKSPACE                         │
│   User: "@Panchang Bot 2026-06-15"                      │
│   Slack App forwards to webhook                          │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTPS POST
                     │ (with HMAC signature)
                     ▼
┌──────────────────────────────────────────────────────────┐
│        CLOUDFLARE WORKER (This API)                      │
│   1. Verify signature  ✓                                 │
│   2. Parse event & extract date                          │
│   3. Validate YYYY-MM-DD format                          │
│   4. Build GitHub dispatch payload                       │
└────────────────────┬─────────────────────────────────────┘
                     │ REST API call
                     │ (GitHub token auth)
                     ▼
┌──────────────────────────────────────────────────────────┐
│              GITHUB ACTIONS                              │
│   Repository dispatch triggers workflow                  │
│   Workflow runs Panchang calculation                     │
│   Posts results to Slack webhook                         │
└────────────────────┬─────────────────────────────────────┘
                     │ Slack webhook POST
                     ▼
┌──────────────────────────────────────────────────────────┐
│            SLACK CHANNEL                                 │
│   Results displayed to user ✓                            │
└──────────────────────────────────────────────────────────┘
```

---

**Ready?** Start with step 1 above, or see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed setup.

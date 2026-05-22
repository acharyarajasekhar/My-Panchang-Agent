# Complete Deployment Checklist

Use this checklist to track your deployment progress from zero to production.

---

## 📋 Pre-Deployment Setup

### Accounts & Credentials (Do These First)

- [ ] Create [Cloudflare account](https://dash.cloudflare.com/sign-up) (free tier OK)
- [ ] Create [GitHub Personal Access Token](https://github.com/settings/tokens)
  - [ ] Scope: `repo` (full control of private repositories)
  - [ ] Copy token (starts with `ghp_`)
- [ ] Create/have Slack workspace with admin access
- [ ] Create [Slack app](https://api.slack.com/apps) (or use existing)

### Environment Setup

- [ ] Install [Node.js](https://nodejs.org/) v14+ (`node --version`)
- [ ] Install npm (comes with Node.js, `npm --version`)
- [ ] Install [Git](https://git-scm.com/) (`git --version`)
- [ ] Navigate to `claudeflare-api` folder
  ```bash
  cd claudeflare-api
  ```

---

## 🚀 Deployment

### Automatic Deployment (One Command!)

- [ ] Run unified deployment script
  ```bash
  npm run deploy
  ```

- [ ] When prompted, enter your secrets:
  - [ ] **GITHUB_TOKEN** - Your GitHub PAT from above
  - [ ] **SLACK_SIGNING_SECRET** - From Slack app Basic Information
  - [ ] **SLACK_WEBHOOK_URL** - (Optional) From Slack incoming webhooks

- [ ] Confirm deployment when asked
  ```
  Configure these secrets? (y/n): y
  ```

- [ ] Watch deployment complete
  ```
  ✅ Deployment completed successfully!
  ```

- [ ] Note your Worker URL from output
  ```
  https://panchang-slack-bridge.<your-subdomain>.workers.dev
  ```

**That's the main deployment done!** ✅

---

## ⚙️ Slack App Configuration

### Event Subscription Setup

1. [ ] Go to [Slack Apps](https://api.slack.com/apps)
2. [ ] Select your Panchang Bot app
3. [ ] Navigate to **Event Subscriptions**
4. [ ] Toggle **Enable Events** to ON
5. [ ] Enter Request URL:
   ```
   https://panchang-slack-bridge.<your-subdomain>.workers.dev/slack/events
   ```
6. [ ] Wait for green checkmark ✅
   - If red X appears, check URL is exactly correct
   - Allow 30 seconds for verification
7. [ ] Under **Subscribe to bot events**, add:
   - [ ] `app_mention`
   - [ ] `message.channels`
   - [ ] `message.groups`
8. [ ] Scroll down and click **Save Changes**

### OAuth & Permissions

1. [ ] Go to **OAuth & Permissions** in Slack app
2. [ ] Verify **Bot Token Scopes** include:
   - [ ] `app_mentions:read`
   - [ ] `chat:write`
   - [ ] `channels:history`
3. [ ] Ensure app is installed to your workspace
   - If not, click **Install to Workspace**

---

## 🔧 GitHub Workflow Setup

### Create Workflow File

1. [ ] In your Panchang Agent repository
2. [ ] Create file: `.github/workflows/panchang-webhook.yml`
3. [ ] Copy content from: `example-github-workflow.yml`
4. [ ] Commit and push to GitHub

### GitHub Secrets

1. [ ] Go to your Panchang Agent repo
2. [ ] Settings → Secrets and variables → Actions
3. [ ] Add repository secret:
   - [ ] Name: `SLACK_WEBHOOK_URL`
   - [ ] Value: Your Slack incoming webhook URL
4. [ ] Save

---

## ✅ Testing

### Test 1: Health Check

```bash
curl https://panchang-slack-bridge.<subdomain>.workers.dev/health
```

Expected response:
```json
{ "status": "ok" }
```

- [ ] Returns 200 OK

### Test 2: Slack Test (Main Test!)

1. [ ] Open your Slack workspace
2. [ ] Find or create a test channel
3. [ ] Type and send:
   ```
   @Panchang Bot 2026-06-15
   ```
4. [ ] Watch for:
   - [ ] ✅ Confirmation message from bot
   - [ ] ✅ "Panchangam calculation triggered" message
   - [ ] ✅ Link to GitHub Actions

### Test 3: GitHub Workflow

1. [ ] Go to your repository
2. [ ] Click **Actions** tab
3. [ ] Look for run with event type **panchang-webhook**
4. [ ] Verify it:
   - [ ] Shows event type "panchang-webhook"
   - [ ] Contains your date (2026-06-15)
   - [ ] Workflow completed successfully

### Test 4: Results in Slack

1. [ ] Check your Slack channel for results
2. [ ] Look for Panchangam data posted
3. [ ] Verify date matches what you sent (2026-06-15)

**All tests passing?** 🎉 You're done!

---

## 📊 Monitoring & Verification

### View Logs

```bash
wrangler tail
```

You should see:
```
Processing app_mention event for date: 2026-06-15
✅ Workflow triggered successfully for 2026-06-15
```

- [ ] Check logs for errors
- [ ] Verify requests are being received

### Verify Secrets

```bash
wrangler secret list
```

Should show:
- [ ] GITHUB_TOKEN (set)
- [ ] SLACK_SIGNING_SECRET (set)
- [ ] SLACK_WEBHOOK_URL (set or not)

### Worker Status

```bash
wrangler deployments list
```

- [ ] Latest deployment shows successful
- [ ] Timestamp is recent
- [ ] Status is green/active

---

## 🔄 Redeploy for Changes

When you make code changes:

```bash
npm run deploy:skip-secrets
```

- [ ] Skips secret re-entry
- [ ] Rebuilds and redeployes
- [ ] About 30 seconds

---

## 🚨 Troubleshooting

### Slack Event Not Received

- [ ] Check Event Subscription URL is EXACTLY correct
  - Format: `https://panchang-slack-bridge.<subdomain>.workers.dev/slack/events`
  - No trailing slash
  - HTTPS (not HTTP)
- [ ] Verify app is installed to workspace
- [ ] Check green checkmark on Event Subscriptions
- [ ] Wait 30 seconds, try again

### "Invalid request signature" Error

- [ ] Verify SLACK_SIGNING_SECRET is set correctly
  ```bash
  wrangler secret list
  ```
- [ ] Make sure secret matches Slack app signing secret EXACTLY
- [ ] Check system time is synced
- [ ] Slack only allows 5-minute old timestamps

### GitHub Workflow Not Triggering

- [ ] Check `.github/workflows/panchang-webhook.yml` exists
- [ ] Verify workflow contains:
  ```yaml
  on:
    repository_dispatch:
      types: [panchang-webhook]
  ```
- [ ] Check GITHUB_TOKEN secret in Cloudflare:
  ```bash
  wrangler secret list
  ```
- [ ] Verify GitHub token has `repo` scope
- [ ] Check GitHub Actions are enabled in repo settings

### No Results Posted to Slack

- [ ] Check GitHub Actions workflow completed
- [ ] Verify SLACK_WEBHOOK_URL secret in GitHub Actions
- [ ] Check workflow environment variables
- [ ] Review workflow logs for errors

---

## 📚 Documentation Reference

- **Quick Start:** [QUICK_START.md](QUICK_START.md)
- **Deploy Scripts:** [DEPLOY_SCRIPTS.md](DEPLOY_SCRIPTS.md)
- **Full Guide:** [README.md](README.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Commands:** [COMMANDS.md](COMMANDS.md)
- **Deployment Details:** [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🎉 Success Criteria

Your deployment is **complete & working** when:

✅ Worker deployed to Cloudflare  
✅ Slack app event subscriptions configured  
✅ GitHub workflow file created  
✅ Test message sent in Slack: `@Panchang Bot 2026-06-15`  
✅ Confirmation message received from bot  
✅ GitHub Actions workflow triggered  
✅ Results posted back to Slack  
✅ Logs show no errors in `wrangler tail`  

---

## 📝 Notes

Use this section to record your setup details:

```
Worker URL: https://panchang-slack-bridge.___.workers.dev
Slack App: [Your App Name]
Slack Channel: #[channel]
GitHub Repo: [owner/repo]
Deployment Date: 2026-05-22
Issues Encountered: [List any issues and how you fixed them]
```

---

## 🔄 After Deployment

### Regular Maintenance

- [ ] Periodically check logs: `wrangler tail`
- [ ] Monitor GitHub Actions runs
- [ ] Keep GitHub token fresh (regenerate if needed)
- [ ] Test monthly: `@Panchang Bot YYYY-MM-DD`

### If Something Breaks

1. [ ] Check `wrangler tail` for errors
2. [ ] Verify secrets with `wrangler secret list`
3. [ ] Test locally: `npm run dev`
4. [ ] Check GitHub Actions logs
5. [ ] Rollback if needed: `wrangler rollback`

---

## ✨ What's Next?

- [ ] Monitor with `npm run dev` or `wrangler tail`
- [ ] Customize Slack messages in `src/utils/slack-respond.ts`
- [ ] Add more event types
- [ ] Set up GitHub Actions notifications
- [ ] Create dashboard to track calculations

---

**Completed!** 🎉 Your Claudeflare Slack Bridge is now live and operational.

For issues, check the docs or review logs with `wrangler tail`.

# Deployment & Configuration Guide

## Quick Deployment Checklist

### ✅ Pre-Deployment

- [ ] Node.js 18+ installed
- [ ] Cloudflare account (free tier OK)
- [ ] GitHub personal access token generated
- [ ] Slack app created
- [ ] Slack signing secret copied
- [ ] Slack app installed to workspace

### ✅ Cloudflare Setup

1. **Install Wrangler CLI**
   ```bash
   npm install -g wrangler@latest
   ```

2. **Authenticate with Cloudflare**
   ```bash
   wrangler login
   ```
   - Opens browser for OAuth
   - Confirm permission grant

3. **Install Dependencies**
   ```bash
   npm install
   ```

4. **Deploy Worker**
   ```bash
   npm run deploy
   ```
   
   Output will show:
   ```
   ✨ Built successfully, deployed with status 200
   📝 To monitor Cloudflare service status, visit https://www.cloudflarestatus.com
   Your worker is live at: https://panchang-slack-bridge.<subdomain>.workers.dev
   ```

### ✅ Secrets Configuration

After deployment, set secrets:

```bash
# GitHub Token (for workflow dispatch)
wrangler secret put GITHUB_TOKEN
# Paste your GitHub Personal Access Token

# Slack Signing Secret (for request verification)
wrangler secret put SLACK_SIGNING_SECRET
# Paste your Slack app signing secret

# Slack Webhook (optional, for fallback)
wrangler secret put SLACK_WEBHOOK_URL
# Paste your Slack incoming webhook URL
```

Verify secrets:
```bash
wrangler secret list
```

You should see all three secrets listed.

### ✅ Slack Configuration

1. Go to https://api.slack.com/apps
2. Select your "Panchang Bot" app
3. Navigate to **Event Subscriptions**
4. Enable Events (toggle on)
5. In "Request URL", paste:
   ```
   https://panchang-slack-bridge.<subdomain>.workers.dev/slack/events
   ```
6. Wait for green checkmark ✅
7. Subscribe to bot events:
   - [ ] app_mention
   - [ ] message.channels
   - [ ] message.groups
8. Save changes
9. In **OAuth & Permissions**, ensure scopes:
   - [ ] app_mentions:read
   - [ ] chat:write
   - [ ] channels:history

### ✅ GitHub Workflow

1. Create `.github/workflows/panchang-webhook.yml` in your repo
2. Copy content from `example-github-workflow.yml`
3. Make sure it listens for `repository_dispatch` with type `panchang-webhook`
4. Add GitHub secret:
   ```
   Settings → Secrets and variables → New repository secret
   Name: SLACK_WEBHOOK_URL
   Value: Your Slack incoming webhook URL
   ```

## Environment Variables Summary

**In Cloudflare Secrets:**
```
GITHUB_TOKEN              = ghp_xxxxxxxxxxxxx
SLACK_SIGNING_SECRET      = xxxxxxxxxxxxxxxx  
SLACK_WEBHOOK_URL         = https://hooks.slack.com/services/...
SLACK_BOT_TOKEN           = xoxb-xxxxxxxxxxxxx (optional)
```

**In GitHub Actions Secrets:**
```
SLACK_WEBHOOK_URL         = https://hooks.slack.com/services/...
```

**In Slack App Config:**
```
Signing Secret            = xxxxxxxxxxxxxxxx (from Basic Information)
Bot Token                 = xoxb-xxxxxxxxxxxxx (from Install App)
```

## Verifying Deployment

### Test 1: Health Check
```bash
curl https://panchang-slack-bridge.<subdomain>.workers.dev/health
```

Expected response:
```json
{ "status": "ok" }
```

### Test 2: Slack Event Verification
Check Cloudflare logs:
```bash
wrangler tail
```

When Slack sends an event, you should see logs like:
```
Processing app_mention event for date: 2026-06-15
✅ Workflow triggered successfully for 2026-06-15
```

### Test 3: GitHub Workflow
1. Go to your repo → Actions tab
2. You should see workflow runs triggered
3. Each run will show event type: `panchang-webhook`

## Troubleshooting Deployment

### Error: "Cannot find module '@cloudflare/workers-types'"
```bash
npm install --save-dev @cloudflare/workers-types
npm run build
```

### Error: "Unauthorized" when running `wrangler deploy`
```bash
# Clear cached credentials and re-login
wrangler logout
wrangler login
```

### Slack: "Invalid request URL"
- Verify URL format is exactly: `https://panchang-slack-bridge.<subdomain>.workers.dev/slack/events`
- No trailing slash
- Must be HTTPS
- Worker must be deployed

### GitHub: "Failed to trigger webhook"
- Verify `GITHUB_TOKEN` has `repo` scope
- Token must be valid (not expired)
- Repository must exist at specified path
- Workflow file must exist and be valid YAML

## Production Deployment

For production, use environment-specific configs:

```bash
# Deploy to production
npm run deploy:prod

# Deploy to staging
npm run deploy:staging
```

In `wrangler.toml`, modify routes as needed:
```toml
[env.production]
route = "https://panchang-api.*.workers.dev/*"

[env.staging]  
route = "https://panchang-staging-*.workers.dev/*"
```

## Monitoring

### Real-time Logs
```bash
wrangler tail
```

### Error Tracking
- Check Cloudflare Dashboard → Workers
- View error rates and response times
- Review exception logs

### Metrics to Monitor
- Request count per minute
- Error rate (should be <1%)
- Average response time (should be <500ms)

## Updating Worker

Make code changes, then:

```bash
# Rebuild
npm run build

# Deploy
npm run deploy

# Or update specific environment
npm run deploy:staging
```

## Rolling Back

To revert to previous version:

```bash
# List recent deployments
wrangler deployments list

# Rollback automatically reverts to last deployment
# Or manually specify:
wrangler rollback --version <version-id>
```

## Cleanup

To remove worker:

```bash
wrangler delete
```

This will:
- Remove deployed worker
- Retain secrets (must delete manually)
- Keep wrangler.toml config

## Support Resources

- **Cloudflare Workers Docs:** https://developers.cloudflare.com/workers/
- **Wrangler CLI Docs:** https://developers.cloudflare.com/workers/cli-wrangler/
- **Slack API Docs:** https://api.slack.com/
- **GitHub REST API:** https://docs.github.com/en/rest/

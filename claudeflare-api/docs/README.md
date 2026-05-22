# Claudeflare Slack Bridge API

**A Cloudflare Workers wrapper that mediates between your Slack channel and GitHub Actions for Panchang calculations.**

```
Slack Input (date) → Verify Signature → Parse Date → Trigger GitHub Workflow → Response to Slack
```

## Overview

This Cloudflare Worker acts as a webhook receiver for Slack events. When you mention the bot or post a message with a date in `YYYY-MM-DD` format, it:

1. ✅ Verifies the request is genuinely from Slack
2. 📅 Extracts the date from your message
3. 🔄 Triggers your Panchang Agent GitHub workflow via repository dispatch
4. 💬 Sends confirmation back to your Slack channel

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Slack Workspace                          │
│  User mentions bot or posts date → Webhook event           │
└────────────────────┬────────────────────────────────────────┘
                     │ (HTTPS POST)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Cloudflare Worker (This API)                      │
│  ├─ Verify Slack signature                                 │
│  ├─ Parse event + extract date                             │
│  ├─ Validate date format (YYYY-MM-DD)                      │
│  └─ Trigger GitHub workflow dispatch                       │
└────────────────────┬────────────────────────────────────────┘
                     │ (REST API call)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              GitHub Actions (Panchang Agent)                │
│  Receives event_type: "panchang-webhook"                   │
│  Extracts date from client_payload                         │
│  Runs calculation and posts result to Slack                │
└─────────────────────────────────────────────────────────────┘
```

## Setup Guide

### Complete Automated Deployment (Recommended)

**One command deploys everything:**

```bash
cd claudeflare-api
npm run deploy
```

This script automatically:
- ✅ Checks your environment (Node.js, npm, Wrangler)
- ✅ Installs dependencies
- ✅ Compiles TypeScript
- ✅ Authenticates with Cloudflare
- ✅ **Prompts for secrets interactively**
- ✅ Deploys to Cloudflare Workers
- ✅ Shows next steps

**Deployment options:**
```bash
npm run deploy              # Production deployment
npm run deploy:staging      # Deploy to staging environment
npm run deploy:skip-secrets # Redeploy without reconfiguring secrets
npm run deploy:dry-run      # Preview deployment without changes
```

See [DEPLOY_SCRIPTS.md](DEPLOY_SCRIPTS.md) for complete deployment script documentation.

---

## Manual Setup (Alternative)

1. Go to https://api.slack.com/apps
2. Create New App → From scratch
3. Name: `Panchang Bot`
4. Choose your workspace
5. Under **Socket Mode** → Enable Socket Mode (optional for events)
6. Under **Event Subscriptions** → Enable Events
   - Subscribe to these bot events:
     - `app_mention`
     - `message.channels`
     - `message.groups`
7. Under **OAuth & Permissions** → Add these scopes:
   - `app_mentions:read`
   - `chat:write`
   - `channels:history`
8. Install app to workspace
9. Copy:
   - **Signing Secret** (Basic Information tab)
   - **Bot Token** (xoxb-...)

### 3. Deploy Cloudflare Worker

```bash
cd claudeflare-api

# Install dependencies
npm install

# Build TypeScript
npm run build

# Login to Cloudflare (first time only)
wrangler login

# Deploy to Cloudflare
npm run deploy
```

**Note:** Your worker will be deployed at: `https://panchang-slack-bridge.<your-subdomain>.workers.dev`

### 4. Configure Secrets in Cloudflare

```bash
# Set GitHub token
wrangler secret put GITHUB_TOKEN
# Paste your GitHub token when prompted

# Set Slack signing secret
wrangler secret put SLACK_SIGNING_SECRET
# Paste your Slack app signing secret when prompted

# Optional: Set Slack webhook for fallback responses
wrangler secret put SLACK_WEBHOOK_URL
# Paste your Slack incoming webhook URL
```

Verify secrets were set:
```bash
wrangler secret list
```

### 5. Configure Slack Event Subscription

1. Go to your Slack App settings
2. **Event Subscriptions** → Edit Request URL
3. Paste: `https://panchang-slack-bridge.<your-subdomain>.workers.dev/slack/events`
4. Slack will send a URL verification challenge
5. If successful, green checkmark appears ✅

### 6. Verify GitHub Workflow Trigger

Your Panchang Agent repository needs a workflow that listens for `panchang-webhook` events.

**Example workflow** (`.github/workflows/panchang-webhook.yml`):

```yaml
name: Panchang Webhook Trigger

on:
  repository_dispatch:
    types: [panchang-webhook]

jobs:
  calculate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run Panchang for date
        env:
          TARGET_DATE: ${{ github.event.client_payload.date }}
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        run: python main.py --date $TARGET_DATE
```

## Usage

### Via Slack App Mention

```
@Panchang Bot 2026-06-15
```

The bot will extract the date and trigger the workflow.

### Via Direct Message (with date)

```
@Panchang please calculate panchangam for 2026-06-15
```

### Manual Date Formats Supported

- `2026-06-15` (ISO standard)
- `June 15, 2026`
- `15/06/2026` (DD/MM/YYYY)
- `06/15/2026` (MM/DD/YYYY)

## API Endpoints

### POST `/slack/events`
Receives Slack events (app_mention, message, url_verification).

**Headers:**
```
X-Slack-Request-Timestamp: <timestamp>
X-Slack-Signature: v0=<hmac_signature>
Content-Type: application/json
```

**Response:**
- `200 OK` - Event received (always, even if ignored)
- `401 Unauthorized` - Invalid signature
- `500 Internal Server Error` - Processing error

### GET `/health`
Simple health check endpoint.

**Response:**
```json
{ "status": "ok" }
```

## Environment Variables

Set these in Cloudflare Workers secrets:

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | GitHub PAT for workflow dispatch | ✅ Yes |
| `SLACK_SIGNING_SECRET` | Slack app signing secret | ✅ Yes |
| `SLACK_WEBHOOK_URL` | Slack incoming webhook (fallback) | ❌ Optional |
| `SLACK_BOT_TOKEN` | Slack bot token (for future use) | ❌ Optional |

Set via:
```bash
wrangler secret put GITHUB_TOKEN
```

## Configuration (wrangler.toml)

These can be modified in `wrangler.toml`:

```toml
[vars]
GITHUB_OWNER = "your_github_username"
GITHUB_REPO = "My-Panchang-Agent"
GITHUB_EVENT_TYPE = "panchang-webhook"
```

## Troubleshooting

### "Slack signature verification failed"

1. Verify `SLACK_SIGNING_SECRET` is correct in Cloudflare secrets
2. Check that secret matches your Slack app signing secret exactly
3. Ensure your system time is synchronized (Slack rejects timestamps >5 min old)

### "Failed to trigger GitHub workflow"

1. Verify `GITHUB_TOKEN` is set correctly
2. Check token has `repo` scope
3. Ensure workflow file exists in your repository
4. Check GitHub Actions tab for error logs

### "Could not extract date"

1. Make sure date is in `YYYY-MM-DD` format or recognizable English format
2. Message must contain date or keyword like "panchang", "calculate", "panchangam"
3. Dates are case-insensitive for natural language parsing

### Worker not receiving events

1. Verify Event Subscription URL in Slack app is correct
2. Check Cloudflare worker logs: `wrangler tail`
3. Ensure Slack app is installed to your workspace
4. Try re-saving Event Subscriptions URL in Slack

## Development

### Local Development

```bash
# Watch mode with hot reload
npm run dev

# This starts a local server at http://localhost:8787
```

### Testing Locally

Use `curl` to simulate Slack events:

```bash
curl -X POST http://localhost:8787/slack/events \
  -H "Content-Type: application/json" \
  -H "X-Slack-Request-Timestamp: $(date +%s)" \
  -d '{
    "type": "url_verification",
    "challenge": "test_challenge_string"
  }'
```

### Building

```bash
npm run build
```

Outputs compiled Worker to `dist/` directory.

## Logging & Monitoring

View real-time logs from your deployed worker:

```bash
wrangler tail
```

This shows:
- Incoming requests
- Date extraction
- GitHub dispatch calls
- Slack responses
- Any errors or warnings

## Files Structure

```
claudeflare-api/
├── src/
│   ├── index.ts                    # Main Worker entry point
│   └── utils/
│       ├── slack-verify.ts         # Slack signature verification
│       ├── slack-parse.ts          # Event parsing & date extraction
│       ├── slack-respond.ts        # Response handling
│       └── github-dispatch.ts      # GitHub workflow trigger
├── wrangler.toml                   # Cloudflare Worker config
├── package.json                    # Dependencies & scripts
├── tsconfig.json                   # TypeScript config
├── .env.example                    # Environment variable template
└── README.md                        # This file
```

## Security

✅ **HMAC-SHA256 Signature Verification** - All Slack requests are verified  
✅ **Constant-Time Comparison** - Protection against timing attacks  
✅ **Timestamp Validation** - Prevents replay attacks (5-min window)  
✅ **Token Rotation Ready** - Easy secret updates in Cloudflare Dashboard  
✅ **No Credentials in Code** - All secrets via environment variables  

## API Rate Limits

- Slack Events API: Unlimited for verified apps
- GitHub Dispatch: 256 requests per hour (per repository)
- Cloudflare Workers: Free tier = 100,000 requests/day

## Future Enhancements

- [ ] Support for slash commands (`/panchang 2026-06-15`)
- [ ] Interactive message buttons (date picker)
- [ ] Caching of calculated Panchangams
- [ ] Multiple language support in responses
- [ ] Scheduled Panchangam delivery
- [ ] Database to track request history
- [ ] Webhook templates for customization

## Support & Debugging

1. **Check logs:** `wrangler tail`
2. **View Slack app logs:** Slack App settings → Activity
3. **Verify GitHub workflow:** Go to your repo → Actions tab
4. **Test endpoint:** Use `/health` endpoint for quick status check

## License

Part of My-Panchang-Agent project. See parent repository for license.

## Questions?

Check the parent Panchang Agent repository for more context:
https://github.com/{GITHUB_OWNER}/My-Panchang-Agent

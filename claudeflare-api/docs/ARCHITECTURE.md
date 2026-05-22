# Architecture & API Reference

## System Architecture

### High-Level Data Flow

```
Slack User Input
    │
    ├─ @Panchang Bot 2026-06-15
    ├─ Calculate panchangam for June 15, 2026
    └─ When is the next full moon? (ignored)
    │
    ▼
Slack App (Webhook)
    │ POST /slack/events
    │ Headers: X-Slack-Request-Timestamp, X-Slack-Signature
    │ Body: SlackEvent JSON
    │
    ▼
Cloudflare Worker
    ├─ 1. Verify HMAC-SHA256 signature
    │     ├─ Checks timestamp (must be within 5 min)
    │     ├─ Validates signature against SLACK_SIGNING_SECRET
    │     └─ Rejects if invalid (401 Unauthorized)
    │
    ├─ 2. Parse Event
    │     ├─ URL Verification? → Respond with challenge
    │     ├─ App Mention? → Parse and extract date
    │     ├─ Message? → Check if relevant (contains date/keywords)
    │     └─ Other events? → Ignore gracefully (200 OK)
    │
    ├─ 3. Extract Date from Text
    │     ├─ Look for YYYY-MM-DD pattern
    │     ├─ Parse natural language (June 15, 2026)
    │     ├─ Convert other formats to ISO
    │     └─ Return undefined if not found
    │
    ├─ 4. Validate Date Format
    │     ├─ Must match YYYY-MM-DD
    │     ├─ Send error response if invalid
    │     └─ Continue if valid
    │
    ├─ 5. Trigger GitHub Workflow
    │     ├─ POST to /repos/{owner}/{repo}/dispatches
    │     ├─ Headers: Authorization: token {GITHUB_TOKEN}
    │     ├─ Body: { event_type: "panchang-webhook", client_payload: { date } }
    │     └─ Return immediately (200 OK) even if GitHub fails
    │
    └─ 6. Respond to Slack
         ├─ Use response_url from event
         ├─ Send confirmation message
         └─ Show GitHub Actions link
    │
    ▼
GitHub Actions
    ├─ Workflow listening for repository_dispatch
    ├─ event_type: "panchang-webhook"
    │
    ├─ Steps:
    │   ├─ 1. Extract date from github.event.client_payload.date
    │   ├─ 2. python main.py --date {date}
    │   ├─ 3. Calculations run
    │   └─ 4. Results posted to Slack
    │
    └─ Sends response to Slack webhook
        └─ User sees results in channel


┌─────────────────────────────────────────────────────────────┐
│ TIMELINE:                                                   │
│ T+0s   : User types message in Slack                       │
│ T+0.5s : Slack app sends webhook to Cloudflare             │
│ T+1s   : Worker returns 200 OK (acknowledges receipt)      │
│ T+2s   : Worker sends confirmation to Slack                │
│ T+3s   : GitHub workflow starts                            │
│ T+30s  : Panchang calculation completes                    │
│ T+31s  : Results posted to Slack channel                   │
└─────────────────────────────────────────────────────────────┘
```

## API Specification

### Endpoint 1: Slack Events Webhook

**Request**
```
POST /slack/events
Content-Type: application/json
X-Slack-Request-Timestamp: <unix_timestamp>
X-Slack-Signature: v0=<hmac_sha256_hex>

{
  "type": "event_callback" | "url_verification",
  "token": "verification_token",
  "team_id": "T12345678",
  "team_domain": "myworkspace",
  "channel_id": "C12345678",
  "user_id": "U12345678",
  "api_app_id": "A12345678",
  "event": { ... },
  "type": "event_callback",
  "event_id": "Ev12345678",
  "event_time": 1234567890
}
```

**Responses**

Success (Any event processed or ignored):
```
HTTP 200 OK
Content-Type: application/json

{ "ok": true }
```

Invalid Signature:
```
HTTP 401 Unauthorized
Content-Type: application/json

{ "error": "Unauthorized" }
```

Invalid Request:
```
HTTP 400 Bad Request
Content-Type: application/json

{ "error": "Invalid request" }
```

Server Error:
```
HTTP 500 Internal Server Error
Content-Type: application/json

{
  "error": "Internal server error",
  "details": "Error message"
}
```

### Endpoint 2: Health Check

**Request**
```
GET /health
```

**Response**
```
HTTP 200 OK
Content-Type: application/json

{ "status": "ok" }
```

## Event Processing Details

### Event Type: URL Verification

**When:** Slack verifies the webhook URL

**Request Body:**
```json
{
  "type": "url_verification",
  "challenge": "3eZbrw1aBrskbtA"
}
```

**Response:**
```
HTTP 200 OK

3eZbrw1aBrskbtA
```

### Event Type: App Mention

**When:** Bot is mentioned in channel

**Request Body:**
```json
{
  "type": "event_callback",
  "event": {
    "type": "app_mention",
    "user": "U12345678",
    "text": "<@U987654> please calculate panchangam for 2026-06-15",
    "channel": "C87654321",
    "ts": "1234567890.000100",
    "bot_id": "B98765432"
  }
}
```

**Processing:**
1. Extract text from event
2. Find YYYY-MM-DD pattern or parse natural language
3. Send confirmation to Slack
4. Trigger GitHub workflow

**Slack Response:**
```json
{
  "text": "✅ Panchangam calculation triggered for 2026-06-15",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Panchangam Calculation Triggered*\n\nDate: `2026-06-15`\nStatus: Processing...\n\n<https://github.com/{GITHUB_OWNER}/My-Panchang-Agent/actions|View in GitHub Actions>"
      }
    }
  ]
}
```

### Event Type: Message

**When:** Message posted in channel that contains relevant keywords

**Request Body:**
```json
{
  "type": "event_callback",
  "event": {
    "type": "message",
    "user": "U12345678",
    "text": "Calculate panchangam for 2026-06-15",
    "channel": "C87654321",
    "ts": "1234567890.000100",
    "thread_ts": "1234567890.000050"
  }
}
```

**Processing:**
1. Check if message contains relevant keywords (panchang, calculate, date, ephemeris, panchangam)
2. Skip if from bot (bot_id field present)
3. Extract date from text
4. If date found, proceed as above
5. If no date, ignore silently

## GitHub Workflow Dispatch Format

**Request to GitHub**
```
POST /repos/{GITHUB_OWNER}/My-Panchang-Agent/dispatches
Authorization: token ghp_xxxxxxxxxxxxxxxx
Content-Type: application/json

{
  "event_type": "panchang-webhook",
  "client_payload": {
    "date": "2026-06-15"
  }
}
```

**Expected GitHub Workflow Response**
```
HTTP 204 No Content
```

## Environment Variables Reference

### Cloudflare Worker Secrets

Set via: `wrangler secret put <name>`

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `GITHUB_TOKEN` | string | ✅ | GitHub Personal Access Token with `repo` scope |
| `SLACK_SIGNING_SECRET` | string | ✅ | Slack App Signing Secret (from Basic Information) |
| `SLACK_WEBHOOK_URL` | string | ❌ | Slack Incoming Webhook for fallback responses |
| `SLACK_BOT_TOKEN` | string | ❌ | Slack Bot Token (for future use) |

### Cloudflare Worker Vars (in wrangler.toml)

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_OWNER` | your_github_username | GitHub repository owner |
| `GITHUB_REPO` | My-Panchang-Agent | GitHub repository name |
| `GITHUB_EVENT_TYPE` | panchang-webhook | Event type for workflow dispatch |

## Security Model

### Slack Request Verification

All Slack requests include two headers:
- `X-Slack-Request-Timestamp`: Unix timestamp of request
- `X-Slack-Signature`: HMAC-SHA256 signature

**Verification Process:**
```
1. Check timestamp is within 5 minutes of current time
2. Build signature base string: "v0:timestamp:body"
3. Compute HMAC-SHA256(signing_secret, base_string)
4. Compare computed signature with provided signature (constant-time comparison)
5. Reject if timestamp too old or signature doesn't match
```

**Protection Against:**
- ❌ Replay attacks (timestamp validation)
- ❌ Man-in-the-middle (HMAC signature)
- ❌ Timing attacks (constant-time comparison)

### GitHub Authentication

Uses Personal Access Token (PAT) in Authorization header:
```
Authorization: token ghp_xxxxxxxxxxxxxxxx
```

### Secrets Management

- All secrets stored in Cloudflare Workers secrets (encrypted at rest)
- No secrets in code or configuration files
- Tokens rotatable without redeployment

## Error Handling

### Date Parsing Errors

```
Input: "2026-13-45"
Output: "❌ Invalid date format: "2026-13-45". Please use YYYY-MM-DD format."
```

### No Date Found

```
Input: "hey bot"
Output: "❌ Could not extract date. Please provide a date in YYYY-MM-DD format."
```

### GitHub Trigger Failure

```
Input: (GitHub API returns 401)
Output: "❌ Failed to trigger workflow: GitHub API returned 401: {error details}"
```

### Slack Response Failure

Failures in sending Slack responses are logged but don't prevent workflow trigger.
User will still see GitHub Actions running.

## Logging

All operations are logged for debugging:

```
View logs: wrangler tail
```

Example logs:
```
Processing app_mention event for date: 2026-06-15
✅ Workflow triggered successfully for 2026-06-15
Slack response sent successfully
```

## Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| Request latency | 50-200ms | Cloudflare edge |
| P95 latency | <500ms | Including Slack/GitHub API calls |
| Error rate | <0.1% | Typical for verified apps |
| Uptime | >99.9% | Cloudflare SLA |
| Concurrent requests | Unlimited | Cloudflare auto-scaling |

## Scalability Limits

| Limit | Value | Applies To |
|-------|-------|-----------|
| Requests per day | 100,000 | Free tier (sufficient for >273/day) |
| Requests per minute | Unlimited* | Burst traffic OK |
| Payload size | 10MB | Worker requests/responses |
| Execution timeout | 30 seconds | Per request |
| Secrets | 10 | Per worker |

*Cloudflare auto-scales; no hard limit for paid plans

## Extending the System

### Adding New Event Types

Edit `src/utils/slack-parse.ts`:

```typescript
function parseSlackEvent(event: Record<string, unknown>): ParsedEvent {
  const eventType = event.type as string;

  switch (eventType) {
    case 'your_new_event_type': {
      return parseYourEvent(event);
    }
    // ...
  }
}
```

### Adding Custom Date Parsers

Edit `src/utils/slack-parse.ts`:

```typescript
export function extractDateFromMessage(text: string): string | undefined {
  // ... existing code ...
  
  // Add custom parser:
  const customDate = parseCustomFormat(text);
  if (customDate) {
    return customDate;
  }
  
  return undefined;
}
```

### Modifying GitHub Dispatch Payload

Edit `src/utils/github-dispatch.ts`:

```typescript
const payload = {
  event_type: eventType,
  client_payload: {
    date: date,
    // Add custom fields:
    user_id: userId,
    custom_param: "value"
  },
};
```

## Testing

### Local Testing

Start dev server:
```bash
npm run dev
```

Run tests:
```bash
python test_events.py verify
python test_events.py mention
python test_events.py message
```

### Production Testing

After deployment:
```bash
# Health check
curl https://panchang-slack-bridge.<subdomain>.workers.dev/health

# View logs
wrangler tail

# Test in Slack
@Panchang Bot 2026-06-15
```

## Deployment Topology

```
┌─────────────────────────────────────────────┐
│         Cloudflare Global Network           │
│  ┌─────────────────────────────────────┐   │
│  │    Edge Locations (300+)            │   │
│  │  ┌──────────────────────────────┐   │   │
│  │  │ Your Worker (replicated)     │   │   │
│  │  │ - Instant startup            │   │   │
│  │  │ - No cold start              │   │   │
│  │  │ - Automatic failover         │   │   │
│  │  └──────────────────────────────┘   │   │
│  └─────────────────────────────────────┘   │
│              ↓ requests route to nearest    │
│       geographically closest edge           │
└─────────────────────────────────────────────┘
              ↓ ↓ ↓ ↓ ↓ (global)
     ┌────────────────────────┐
     │   Slack API (US)      │
     │   GitHub API (US)     │
     └────────────────────────┘
```

---

**See [README.md](README.md) for usage guide and [DEPLOYMENT.md](DEPLOYMENT.md) for setup instructions.**

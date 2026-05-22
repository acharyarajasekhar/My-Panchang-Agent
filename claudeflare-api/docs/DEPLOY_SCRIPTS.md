# Deployment Scripts Guide

Complete automated build and deployment scripts for Claudeflare Slack Bridge.

## Overview

Three deployment options available:

1. **`deploy.ps1`** - PowerShell script for Windows
2. **`deploy.sh`** - Bash script for macOS/Linux
3. **`deploy.js`** - Unified Node.js wrapper (auto-selects appropriate script)

All three options run the **same complete workflow**:
- ✅ Environment checks
- ✅ Dependency installation
- ✅ TypeScript compilation
- ✅ Cloudflare authentication
- ✅ Secret configuration (interactive)
- ✅ Pre-deployment verification
- ✅ Deployment to Cloudflare
- ✅ Post-deployment instructions

## Quick Start

### Option 1: Using npm (Recommended)

```bash
npm run deploy                # Deploy to production
npm run deploy:staging        # Deploy to staging
npm run deploy:skip-secrets   # Skip secret configuration
npm run deploy:dry-run        # Simulate without deploying
```

### Option 2: Direct Script Execution

#### On Windows (PowerShell)
```powershell
.\deploy.ps1                    # Production
.\deploy.ps1 staging            # Staging
.\deploy.ps1 -SkipSecrets       # Skip secrets
.\deploy.ps1 -DryRun            # Dry run
```

#### On macOS/Linux
```bash
bash deploy.sh                  # Production
bash deploy.sh staging          # Staging
bash deploy.sh --skip-secrets   # Skip secrets
bash deploy.sh --dry-run        # Dry run
```

#### Cross-Platform (Node.js)
```bash
node deploy.js                  # Production
node deploy.js staging          # Staging
node deploy.js --skip-secrets   # Skip secrets
node deploy.js --dry-run        # Dry run
```

## Available Commands

### npm run deploy
**Default deployment to production**

```bash
npm run deploy
```

- Checks environment
- Installs dependencies
- Builds TypeScript
- Authenticates with Cloudflare (if needed)
- Prompts for secrets interactively
- Deploys worker
- Shows post-deployment instructions

### npm run deploy:prod
**Explicit production deployment**

```bash
npm run deploy:prod
```

Same as `npm run deploy`

### npm run deploy:staging
**Deploy to staging environment**

```bash
npm run deploy:staging
```

- Same workflow as production
- Deploys to staging subdomain
- Easier for testing before production

### npm run deploy:skip-secrets
**Deploy without reconfiguring secrets**

```bash
npm run deploy:skip-secrets
```

- Skips the secret configuration step
- Uses existing Cloudflare secrets
- Useful for redeployments

### npm run deploy:dry-run
**Simulate deployment without making changes**

```bash
npm run deploy:dry-run
```

- Runs all checks
- Shows what would be deployed
- Does NOT:
  - Install packages
  - Build TypeScript
  - Call Cloudflare API
  - Configure secrets
  - Deploy worker

### npm run deploy:wrangler
**Direct Wrangler deployment (no automation)**

```bash
npm run deploy:wrangler
```

- Assumes environment is ready
- Skips all checks and setup
- Direct deployment only
- For advanced users

## PowerShell Script Details

**File:** `deploy.ps1`

**Parameters:**

```powershell
.\deploy.ps1 [-Environment <production|staging>] [-SkipSecrets] [-DryRun]
```

| Parameter | Default | Description |
|-----------|---------|-------------|
| `Environment` | `production` | Target environment (production or staging) |
| `SkipSecrets` | `$false` | Skip interactive secret configuration |
| `DryRun` | `$false` | Simulate without making changes |

**Examples:**

```powershell
# Production deployment
.\deploy.ps1

# Staging with secrets
.\deploy.ps1 staging

# Redeployment (skip secrets)
.\deploy.ps1 -SkipSecrets

# Preview before deploying
.\deploy.ps1 -DryRun
```

**Features:**
- Colored output for easy reading
- Progress indicators (✅, ❌, ⚠️, ℹ️)
- Interactive secret input (hidden passwords)
- Parameter validation
- Detailed error messages

## Bash Script Details

**File:** `deploy.sh`

**Usage:**

```bash
./deploy.sh [production|staging] [--skip-secrets] [--dry-run]
```

| Argument | Default | Description |
|----------|---------|-------------|
| Environment | `production` | Target environment (production or staging) |
| `--skip-secrets` | `false` | Skip secret configuration |
| `--dry-run` | `false` | Simulate without changes |

**Examples:**

```bash
# Production deployment
./deploy.sh

# Staging
./deploy.sh staging

# Redeployment
./deploy.sh --skip-secrets

# Preview
./deploy.sh --dry-run

# Staging without secrets
./deploy.sh staging --skip-secrets
```

**Features:**
- Cross-platform compatible
- ANSI color output
- Interactive secret input
- Progress indicators
- Clear error messages

## Step-by-Step Workflow

### Step 1: Environment Check
Verifies required tools are installed:
- Node.js (v14+)
- npm
- Git
- Wrangler (global or local)

**Output:**
```
✅ Node.js: v18.x.x
✅ npm: 9.x.x
✅ Git: 2.x.x
```

### Step 2: Dependencies Installation
Installs npm packages defined in `package.json`

**Output:**
```
ℹ️  Running: npm install
✅ Dependencies installed
```

### Step 3: TypeScript Build
Compiles TypeScript source to JavaScript

**Output:**
```
ℹ️  Running: npm run build
✅ TypeScript compiled successfully
```

### Step 4: Cloudflare Authentication
Checks if authenticated with Cloudflare, prompts login if needed

**Output:**
```
✅ Already authenticated with Cloudflare
ℹ️  user@example.com
```

Or:
```
⚠️  Not authenticated with Cloudflare
ℹ️  Opening browser for authentication...
✅ Authenticated with Cloudflare
```

### Step 5: Secret Configuration
Interactive prompts for Cloudflare secrets (if not `--skip-secrets`)

**Prompts:**
```
1. Enter GITHUB_TOKEN (or press Enter to skip): ghp_xxxxx
2. Enter SLACK_SIGNING_SECRET (or press Enter to skip): xxxx
3. Enter SLACK_WEBHOOK_URL (optional, press Enter to skip): 
```

**Shows summary:**
```
ℹ️  Secrets to configure:
  • GITHUB_TOKEN: ****xxxxx
  • SLACK_SIGNING_SECRET: ****xxxx
  
Configure these secrets? (y/n): y
✅ Secret configured: GITHUB_TOKEN
✅ Secret configured: SLACK_SIGNING_SECRET
```

### Step 6: Pre-Deployment Verification
Checks that everything is ready:
- Cloudflare secrets exist
- `wrangler.toml` exists
- Build output directory exists

**Output:**
```
ℹ️  Checking secrets...
✅ Secrets found: 3
ℹ️  Checking wrangler.toml...
✅ wrangler.toml found
```

### Step 7: Deployment
Actually deploys the worker to Cloudflare

**Output:**
```
ℹ️  Deploying to: production
ℹ️  Starting deployment...
✅ Deployment completed successfully!
```

**Or (dry-run):**
```
⚠️  DRY RUN: Would deploy to production
```

### Step 8: Post-Deployment
Shows next steps and useful commands

**Output:**
```
ℹ️  Next steps to complete setup:

1. UPDATE SLACK APP EVENT SUBSCRIPTION
   ├─ Go to: https://api.slack.com/apps
   ├─ Select your Panchang Bot app
   ...

2. TEST IN SLACK
   └─ Type: @Panchang Bot 2026-06-15
```

### Summary
Final summary of deployment

**Output:**
```
╔════════════════════════════════════════════════════════════╗
║ Deployment Summary                                         ║
╚════════════════════════════════════════════════════════════╝

✅ COMPLETED

Environment:        production
Build Status:       Built
Deploy Status:      Deployed
Secrets Configured: Yes

Worker URL:
  https://panchang-slack-bridge.<your-subdomain>.workers.dev

🎉 Your Claudeflare Worker is live!
```

## Secrets Configuration

The script prompts for three secrets:

### 1. GITHUB_TOKEN (Required)
**Purpose:** Trigger GitHub workflows

**How to get:**
1. Go to https://github.com/settings/tokens
2. Generate new personal access token
3. Check only `repo` scope
4. Copy token (starts with `ghp_`)

**Validation:** Script checks token starts with `ghp_` or `github_pat_`

### 2. SLACK_SIGNING_SECRET (Required)
**Purpose:** Verify Slack webhook requests

**How to get:**
1. Go to https://api.slack.com/apps
2. Select your Panchang Bot app
3. Go to "Basic Information"
4. Find "Signing Secret"
5. Copy it

**Note:** Do NOT share this secret. Keep it safe.

### 3. SLACK_WEBHOOK_URL (Optional)
**Purpose:** Fallback webhook for responses

**How to get:**
1. Go to https://api.slack.com/messaging/webhooks
2. Create new Incoming Webhook
3. Select your workspace and channel
4. Copy webhook URL

**Note:** Usually not needed if using response_url from events

## Dry Run Mode

Test deployment without making changes:

```bash
npm run deploy:dry-run
```

**What it simulates:**
- Environment checks ✅ (actual)
- Dependency installation ❌ (simulated)
- TypeScript build ❌ (simulated)
- Cloudflare auth ✅ (actual)
- Secret verification ❌ (simulated)
- Deployment ❌ (simulated)
- Post-deployment steps ✅ (shown)

**Useful for:**
- Testing configuration before deploying
- Verifying environment setup
- Understanding deployment flow
- Checking what would be deployed

## Skip Secrets Mode

Redeploy without reconfiguring secrets:

```bash
npm run deploy:skip-secrets
```

**Useful for:**
- Redeploying after code changes
- Minor updates without secret changes
- Faster redeployments
- CI/CD pipelines (secrets pre-configured)

## Environment Variables

### Production Environment
- Worker deployed to standard subdomain
- Standard rate limits
- Suitable for live Slack app

### Staging Environment
- Separate worker subdomain
- For testing before production
- Different Slack app configuration possible
- Rollback to production if issues

**To deploy to staging:**
```bash
npm run deploy:staging
```

## Troubleshooting

### "Node.js is not installed"
Install Node.js from https://nodejs.org/ (v14+)

### "npm is not installed"
Usually installed with Node.js. Reinstall Node.js

### "Wrangler not installed globally"
This is okay. Script will use local version installed by `npm install`

### "Authentication failed"
1. Ensure Cloudflare account exists
2. Run `npm run deploy` again to retry login
3. Check Cloudflare account access

### "Deployment failed"
1. Check `wrangler.toml` is valid
2. Verify Cloudflare account is active
3. Check terminal output for specific error
4. Run `npm run deploy:dry-run` to check configuration

### "Secrets not configured"
1. Run `npm run deploy:skip-secrets` on next deployment
2. Manually set secrets: `wrangler secret put NAME`
3. Verify with: `wrangler secret list`

### Script won't execute (Windows)
If PowerShell script won't run:

```powershell
# Set execution policy temporarily
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
.\deploy.ps1
```

Or use the Node.js wrapper:
```bash
node deploy.js
```

### Script won't execute (macOS/Linux)
Make script executable:

```bash
chmod +x deploy.sh
./deploy.sh
```

Or use npm:
```bash
npm run deploy
```

## Advanced Usage

### Custom Wrangler Deploy
For advanced configurations:

```bash
npm run deploy:wrangler
```

This skips all automation and runs `wrangler deploy` directly.

### Manual Deployment (No Script)
If scripts don't work:

```bash
# 1. Install dependencies
npm install

# 2. Build TypeScript
npm run build

# 3. Authenticate
wrangler login

# 4. Set secrets manually
wrangler secret put GITHUB_TOKEN
wrangler secret put SLACK_SIGNING_SECRET
wrangler secret put SLACK_WEBHOOK_URL

# 5. Deploy
wrangler deploy
```

### Environment-Specific Secrets
For multiple environments, set secrets per environment:

```bash
# Production secrets
wrangler secret put GITHUB_TOKEN
wrangler secret put SLACK_SIGNING_SECRET

# Staging secrets (if different)
wrangler secret put GITHUB_TOKEN --env staging
wrangler secret put SLACK_SIGNING_SECRET --env staging
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Claudeflare

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Deploy with script
        run: npm run deploy:skip-secrets
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
```

### GitLab CI Example

```yaml
deploy:
  stage: deploy
  script:
    - npm install
    - npm run deploy:skip-secrets
  environment:
    name: production
  only:
    - main
```

## Performance

### Typical Deployment Time

| Step | Time |
|------|------|
| Environment check | <1s |
| npm install | 10-30s |
| TypeScript build | 5-10s |
| Cloudflare auth check | 1-2s |
| Secret configuration | 30-60s (interactive) |
| Deployment | 10-20s |
| **Total** | **~1-2 minutes** |

### Subsequent Deployments (skip-secrets)

| Step | Time |
|------|------|
| Environment check | <1s |
| npm install (cached) | 2-5s |
| TypeScript build | 5-10s |
| Deployment | 10-20s |
| **Total** | **~30-40 seconds** |

## See Also

- [QUICK_START.md](QUICK_START.md) - 5-minute setup
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
- [README.md](README.md) - Complete documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design

---

**Version:** 1.0.0  
**Last Updated:** 2026-05-22

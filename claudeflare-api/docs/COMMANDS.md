# Commands Quick Reference

## One-Command Deploy (Recommended)

```bash
npm run deploy
```

**That's it!** The script handles everything automatically.

---

## All Deploy Commands

| Command | What It Does |
|---------|--------------|
| `npm run deploy` | Full deployment to production (interactive) |
| `npm run deploy:prod` | Same as above, explicit production |
| `npm run deploy:staging` | Deploy to staging environment |
| `npm run deploy:skip-secrets` | Redeploy without reconfiguring secrets |
| `npm run deploy:dry-run` | Preview deployment without making changes |
| `npm run deploy:wrangler` | Direct Wrangler deployment (skips automation) |

---

## Development

```bash
npm run dev           # Start local dev server (http://localhost:8787)
npm run build         # Compile TypeScript
npm run build -- --watch  # Watch mode
```

---

## Monitoring

```bash
wrangler tail         # View real-time logs from deployed worker
```

---

## Secrets Management

```bash
wrangler secret put <name>      # Set a secret
wrangler secret list            # List all secrets
wrangler secret delete <name>   # Delete a secret
```

**Common secrets:**
```bash
wrangler secret put GITHUB_TOKEN
wrangler secret put SLACK_SIGNING_SECRET
wrangler secret put SLACK_WEBHOOK_URL
```

---

## Testing Locally

```bash
# Terminal 1: Start local server
npm run dev

# Terminal 2: Run tests
python test_events.py health          # Health check
python test_events.py verify          # URL verification
python test_events.py mention         # App mention with date
python test_events.py message         # Message with date
python test_events.py invalid_sig     # Test invalid signature
python test_events.py natural         # Natural language date
```

---

## Deployment Variants

### Windows (PowerShell)
```powershell
.\deploy.ps1                  # Production
.\deploy.ps1 staging          # Staging
.\deploy.ps1 -SkipSecrets     # Skip secrets
.\deploy.ps1 -DryRun          # Preview
```

### macOS/Linux (Bash)
```bash
bash deploy.sh                # Production
bash deploy.sh staging        # Staging
bash deploy.sh --skip-secrets # Skip secrets
bash deploy.sh --dry-run      # Preview
```

### Node.js (Cross-Platform)
```bash
node deploy.js                # Production
node deploy.js staging        # Staging
node deploy.js --skip-secrets # Skip secrets
node deploy.js --dry-run      # Preview
```

---

## Cloudflare Management

```bash
wrangler login               # Authenticate with Cloudflare
wrangler logout              # Log out
wrangler whoami              # Show current user
wrangler tail                # View worker logs
wrangler deployments list    # Show deployment history
wrangler rollback            # Rollback to previous version
wrangler delete              # Delete the worker
```

---

## Environment Switching

```bash
# Deploy to production (default)
npm run deploy

# Deploy to staging
npm run deploy:staging

# Switch between environments using wrangler
wrangler deploy --env staging
wrangler deploy --env production
```

---

## CI/CD Deployment (GitHub Actions)

```bash
# In CI pipeline with pre-configured secrets
npm run deploy:skip-secrets
```

---

## Troubleshooting Commands

```bash
# Check environment
node --version
npm --version
npm list -g wrangler

# View deployment logs
wrangler tail

# Check configured secrets
wrangler secret list

# Run local tests
python test_events.py health

# Test TypeScript syntax
npm run build
```

---

## Quick Reference Table

| Task | Command |
|------|---------|
| **Deploy** | `npm run deploy` |
| **Deploy staging** | `npm run deploy:staging` |
| **Preview deploy** | `npm run deploy:dry-run` |
| **View logs** | `wrangler tail` |
| **Set secret** | `wrangler secret put NAME` |
| **List secrets** | `wrangler secret list` |
| **Local dev** | `npm run dev` |
| **Run tests** | `python test_events.py <test>` |
| **Build TypeScript** | `npm run build` |
| **Authenticate** | `wrangler login` |
| **Rollback** | `wrangler rollback` |
| **Delete worker** | `wrangler delete` |

---

## Common Workflows

### Initial Setup
```bash
npm install
npm run deploy
# Prompts for secrets
# Done!
```

### Code Update & Redeploy
```bash
# Make code changes...
npm run deploy:skip-secrets
```

### Test Before Deploying
```bash
npm run dev            # Terminal 1: Start local
python test_events.py health  # Terminal 2: Test
```

### Staging Test
```bash
npm run deploy:staging
# Test in staging environment
npm run deploy          # When ready for production
```

### Emergency Rollback
```bash
wrangler deployments list    # See previous versions
wrangler rollback             # Rollback to previous
```

---

## See Also

- [QUICK_START.md](QUICK_START.md) - 5-minute setup
- [DEPLOY_SCRIPTS.md](DEPLOY_SCRIPTS.md) - Detailed deployment info
- [README.md](README.md) - Full documentation
- [INDEX.md](INDEX.md) - File index

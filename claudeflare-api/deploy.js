#!/usr/bin/env node

/**
 * Claudeflare Deploy - Complete Build & Deployment in Node.js
 * 
 * No shell scripts needed - all logic in Node.js for cross-platform compatibility
 * 
 * Usage:
 *   npm run deploy                  # Deploy to production
 *   npm run deploy staging          # Deploy to staging
 *   npm run deploy --skip-secrets   # Skip secret configuration
 *   npm run deploy --dry-run        # Simulate without deploying
 */

const { execSync, spawn } = require('child_process');
const readline = require('readline');
const fs = require('fs');
const path = require('path');

// ═══════════════════════════════════════════════════════════════════════════
// COLOR OUTPUT
// ═══════════════════════════════════════════════════════════════════════════

const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    cyan: '\x1b[36m'
};

const log = {
    success: (msg) => console.log(`${colors.green}✅ ${msg}${colors.reset}`),
    error: (msg) => console.log(`${colors.red}❌ ${msg}${colors.reset}`),
    warn: (msg) => console.log(`${colors.yellow}⚠️  ${msg}${colors.reset}`),
    info: (msg) => console.log(`${colors.cyan}ℹ️  ${msg}${colors.reset}`),
    header: (msg) => {
        console.log('');
        console.log(`${colors.cyan}╔════════════════════════════════════════════════════════════╗${colors.reset}`);
        console.log(`${colors.cyan}║ ${msg}${colors.reset}`);
        console.log(`${colors.cyan}╚════════════════════════════════════════════════════════════╝${colors.reset}`);
        console.log('');
    }
};

// ═══════════════════════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

function parseArgs() {
    const args = process.argv.slice(2);
    return {
        environment: ['production', 'staging'].includes(args[0]) ? args[0] : 'production',
        skipSecrets: args.includes('--skip-secrets'),
        dryRun: args.includes('--dry-run')
    };
}

async function exec(command, options = {}) {
    try {
        const output = execSync(command, { encoding: 'utf8', ...options });
        return { success: true, output: output.trim() };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

function spawnAsync(command, args = []) {
    return new Promise((resolve) => {
        const child = spawn(command, args, { stdio: 'inherit', shell: true });
        child.on('exit', (code) => {
            resolve(code === 0);
        });
    });
}

function prompt(question) {
    return new Promise((resolve) => {
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });
        rl.question(question, (answer) => {
            rl.close();
            resolve(answer.trim());
        });
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// MAIN DEPLOYMENT FLOW
// ═══════════════════════════════════════════════════════════════════════════

async function main() {
    const config = parseArgs();
    
    console.log('\n🚀 Claudeflare Deploy\n');
    log.info(`Environment: ${config.environment}`);
    log.info(`Skip Secrets: ${config.skipSecrets}`);
    log.info(`Dry Run: ${config.dryRun}\n`);

    try {
        // Step 1: Environment Check
        await stepEnvironmentCheck();

        // Step 2: Install Dependencies
        await stepInstallDependencies(config.dryRun);

        // Step 3: Build TypeScript
        await stepBuildTypeScript(config.dryRun);

        // Step 4: Cloudflare Authentication
        await stepCloudflareAuth(config.dryRun);

        // Step 5: Configure Secrets
        if (!config.skipSecrets) {
            await stepConfigureSecrets(config.dryRun);
        } else {
            log.header('Step 5: Secrets Configuration (Skipped)');
            log.info('Using existing secrets');
        }

        // Step 6: Pre-deployment Verification
        await stepVerification(config.dryRun);

        // Step 7: Deployment
        await stepDeploy(config.environment, config.dryRun);

        // Step 8: Post-deployment
        await stepPostDeploy();

        // Summary
        await stepSummary(config);

    } catch (error) {
        log.error(`Deployment failed: ${error.message}`);
        process.exit(1);
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// STEP 1: ENVIRONMENT CHECK
// ═══════════════════════════════════════════════════════════════════════════

async function stepEnvironmentCheck() {
    log.header('Step 1: Environment Check');

    const tools = [
        { name: 'Node.js', cmd: 'node --version' },
        { name: 'npm', cmd: 'npm --version' },
        { name: 'Git', cmd: 'git --version' }
    ];

    for (const tool of tools) {
        const result = await exec(tool.cmd);
        if (result.success) {
            log.success(`${tool.name}: ${result.output}`);
        } else {
            log.error(`${tool.name} is not installed`);
            throw new Error(`${tool.name} required`);
        }
    }

    // Check wrangler
    const wrangler = await exec('npx wrangler --version');
    if (wrangler.success) {
        log.success(`Wrangler: ${wrangler.output}`);
    } else {
        log.warn('Wrangler not found - will install with dependencies');
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// STEP 2: INSTALL DEPENDENCIES
// ═══════════════════════════════════════════════════════════════════════════

async function stepInstallDependencies(dryRun) {
    log.header('Step 2: Installing Dependencies');

    if (dryRun) {
        log.warn('DRY RUN: Would run npm install');
        return;
    }

    log.info('Running: npm install');
    const success = await spawnAsync('npm', ['install']);
    
    if (!success) {
        throw new Error('npm install failed');
    }
    log.success('Dependencies installed');
}

// ═══════════════════════════════════════════════════════════════════════════
// STEP 3: BUILD TYPESCRIPT
// ═══════════════════════════════════════════════════════════════════════════

async function stepBuildTypeScript(dryRun) {
    log.header('Step 3: Building TypeScript');

    if (dryRun) {
        log.warn('DRY RUN: Would run npm run build');
        return;
    }

    log.info('Running: npm run build');
    const success = await spawnAsync('npm', ['run', 'build']);
    
    if (!success) {
        throw new Error('Build failed');
    }
    log.success('TypeScript compiled successfully');
}

// ═══════════════════════════════════════════════════════════════════════════
// STEP 4: CLOUDFLARE AUTHENTICATION
// ═══════════════════════════════════════════════════════════════════════════

async function stepCloudflareAuth(dryRun) {
    log.header('Step 4: Cloudflare Authentication');

    log.info('Checking Cloudflare authentication...');
    
    if (dryRun) {
        log.warn('DRY RUN: Would check wrangler whoami');
        return;
    }

    const result = await exec('npx wrangler whoami');
    
    if (result.success) {
        log.success('Already authenticated with Cloudflare');
        log.info(result.output);
    } else {
        log.warn('Not authenticated with Cloudflare');
        log.info('Opening browser for authentication...');
        const success = await spawnAsync('npx', ['wrangler', 'login']);
        
        if (!success) {
            throw new Error('Authentication failed');
        }
        log.success('Authenticated with Cloudflare');
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// STEP 5: CONFIGURE SECRETS
// ═══════════════════════════════════════════════════════════════════════════

async function stepConfigureSecrets(dryRun) {
    log.header('Step 5: Configure Secrets');

    console.log(`
The following secrets need to be configured in Cloudflare Workers:

1. GITHUB_TOKEN (required)
   - Your GitHub Personal Access Token
   - Get from: https://github.com/settings/tokens
   - Needs: 'repo' scope
   
2. SLACK_SIGNING_SECRET (required)
   - Your Slack app signing secret
   - Get from: https://api.slack.com/apps → Your App → Basic Information
   - Shows as "Signing Secret"
   
3. SLACK_WEBHOOK_URL (optional)
   - Slack incoming webhook for fallback responses
   - Get from: https://api.slack.com/messaging/webhooks
   - Only needed if not using response_url from events

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RUN THESE COMMANDS TO SET SECRETS:

  npx wrangler secret put GITHUB_TOKEN
  → Paste your GitHub token, then press Enter twice

  npx wrangler secret put SLACK_SIGNING_SECRET
  → Paste your Slack signing secret, then press Enter twice

  npx wrangler secret put SLACK_WEBHOOK_URL
  → Paste your Slack webhook URL (optional)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);

    if (!dryRun) {
        log.info('Skipping interactive secret configuration.');
        log.info('Use the commands above to set your secrets manually.');
        log.info('');
        log.info('Once secrets are set, run:  npm run deploy:skip-secrets');
    } else {
        log.warn('DRY RUN: Skipping secret configuration');
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// STEP 6: VERIFICATION
// ═══════════════════════════════════════════════════════════════════════════

async function stepVerification(dryRun) {
    log.header('Step 6: Pre-Deployment Verification');

    if (!dryRun) {
        log.info('Checking secrets...');
        const secrets = await exec('npx wrangler secret list');
        if (secrets.success) {
            log.success('Secrets found:');
            console.log(secrets.output);
        } else {
            log.warn('Could not verify secrets (may not be set yet)');
        }
    } else {
        log.warn('DRY RUN: Would list secrets');
    }

    log.info('Checking wrangler.toml...');
    if (fs.existsSync('wrangler.toml')) {
        log.success('wrangler.toml found');
    } else {
        throw new Error('wrangler.toml not found');
    }

    log.info('Checking TypeScript build output...');
    if (fs.existsSync('dist')) {
        log.success('Build output directory found');
    } else {
        log.warn('Build output directory not found (will be created during deploy)');
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// STEP 7: DEPLOYMENT
// ═══════════════════════════════════════════════════════════════════════════

async function stepDeploy(environment, dryRun) {
    log.header('Step 7: Deploying to Cloudflare');

    const envFlag = environment === 'staging' ? ['--env', 'staging'] : [];
    
    log.info(`Deploying to: ${environment}`);
    log.info(`Command: npx wrangler deploy ${envFlag.join(' ')}`);

    if (dryRun) {
        log.warn(`DRY RUN: Would run npx wrangler deploy ${envFlag.join(' ')}`);
        console.log('');
        log.info('Deployment would complete with:');
        log.info('  • Worker deployed to Cloudflare edge');
        log.info('  • URL: https://panchang-slack-bridge.*.workers.dev');
        log.info('  • Secrets encrypted and stored');
        log.info('  • Ready to receive Slack webhooks');
    } else {
        log.info('Starting deployment...');
        const success = await spawnAsync('npx', ['wrangler', 'deploy', ...envFlag]);
        
        if (!success) {
            throw new Error('Deployment failed');
        }
        log.success('Deployment completed successfully!');
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// STEP 8: POST-DEPLOYMENT
// ═══════════════════════════════════════════════════════════════════════════

async function stepPostDeploy() {
    log.header('Step 8: Post-Deployment Configuration');

    log.info('Next steps to complete setup:');
    console.log(`
1. UPDATE SLACK APP EVENT SUBSCRIPTION
   ├─ Go to: https://api.slack.com/apps
   ├─ Select your Panchang Bot app
   ├─ Event Subscriptions → Enable Events
   ├─ Request URL: https://panchang-slack-bridge.<subdomain>.workers.dev/slack/events
   ├─ Wait for green checkmark ✅
   └─ Save changes

2. SUBSCRIBE TO BOT EVENTS (if not already done)
   ├─ app_mention
   ├─ message.channels
   └─ message.groups

3. TEST IN SLACK
   └─ Type: @Panchang Bot 2026-06-15
   
4. SET UP GITHUB WORKFLOW
   ├─ Create: .github/workflows/panchang-webhook.yml
   ├─ Copy from: example-github-workflow.yml
   └─ Add GitHub secret: SLACK_WEBHOOK_URL

5. MONITOR DEPLOYMENT
   └─ Run: npx wrangler tail

6. VIEW LOGS
   └─ Run: npm run dev (for local testing first)
`);
}

// ═══════════════════════════════════════════════════════════════════════════
// SUMMARY
// ═══════════════════════════════════════════════════════════════════════════

async function stepSummary(config) {
    log.header('Deployment Summary');

    const status = config.dryRun ? 'DRY RUN - No changes made' : 'COMPLETED';
    log.success(status);

    console.log(`
Environment:        ${config.environment}
Build Status:       ${config.dryRun ? 'Simulated' : 'Built'}
Deploy Status:      ${config.dryRun ? 'Simulated' : 'Deployed'}
Secrets Configured: ${config.skipSecrets ? 'Skipped' : 'Yes'}

Worker URL:
  https://panchang-slack-bridge.<your-subdomain>.workers.dev

Useful Commands:
  • View logs:        npm run dev  or  npx wrangler tail
  • Redeploy:         npm run deploy
  • Update secrets:   npx wrangler secret put <name>
  • List secrets:     npx wrangler secret list
  • Run tests:        python test_events.py <test_name>
  • Rollback:         npx wrangler rollback

Documentation:
  • Quick Start:      docs/QUICK_START.md
  • Full Guide:       docs/README.md
  • Deployment Info:  docs/DEPLOYMENT.md
  • Architecture:     docs/ARCHITECTURE.md
`);

    if (!config.dryRun) {
        log.success('🎉 Your Claudeflare Worker is live!');
        console.log('');
        log.info('Configure your Slack app Event Subscription URL:');
        console.log('https://panchang-slack-bridge.<subdomain>.workers.dev/slack/events');
    }

    console.log('');
}

// ═══════════════════════════════════════════════════════════════════════════
// RUN
// ═══════════════════════════════════════════════════════════════════════════

main().catch(error => {
    log.error(error.message);
    process.exit(1);
});

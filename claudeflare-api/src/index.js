"use strict";
/**
 * Panchang Slack Bridge - Cloudflare Worker
 * ──────────────────────────────────────────
 * Acts as a mediator between Slack and GitHub Actions.
 *
 * Slack → Extract Date (YYYY-MM-DD) → Trigger GitHub Workflow → Response
 */
Object.defineProperty(exports, "__esModule", { value: true });
const slack_verify_1 = require("./utils/slack-verify");
const github_dispatch_1 = require("./utils/github-dispatch");
const slack_parse_1 = require("./utils/slack-parse");
const slack_respond_1 = require("./utils/slack-respond");
exports.default = {
    async fetch(request, env, ctx) {
        const url = new URL(request.url);
        // Route: Health check (GET)
        if (url.pathname === '/health') {
            return new Response(JSON.stringify({ status: 'ok' }), {
                headers: { 'Content-Type': 'application/json' },
            });
        }
        // Only accept POST requests for other routes
        if (request.method !== 'POST') {
            return new Response('Method not allowed', { status: 405 });
        }
        // Route: Slack Events
        if (url.pathname === '/slack/events') {
            return handleSlackEvents(request, env, ctx);
        }
        return new Response(JSON.stringify({ error: 'Not found' }), {
            status: 404,
            headers: { 'Content-Type': 'application/json' },
        });
    },
};
async function handleSlackEvents(request, env, ctx) {
    try {
        // Read the request body
        const rawBody = await request.text();
        const timestamp = request.headers.get('X-Slack-Request-Timestamp');
        const signature = request.headers.get('X-Slack-Signature');
        // Verify Slack signature
        if (!timestamp || !signature) {
            console.error('Missing Slack verification headers');
            return new Response(JSON.stringify({ error: 'Invalid request' }), {
                status: 401,
                headers: { 'Content-Type': 'application/json' },
            });
        }
        const isValid = await (0, slack_verify_1.verifySlackSignature)(env.SLACK_SIGNING_SECRET, timestamp, rawBody, signature);
        if (!isValid) {
            console.error('Slack signature verification failed');
            return new Response(JSON.stringify({ error: 'Unauthorized' }), {
                status: 401,
                headers: { 'Content-Type': 'application/json' },
            });
        }
        // Parse the event
        const body = JSON.parse(rawBody);
        // Respond to URL verification challenge
        if (body.type === 'url_verification' && body.challenge) {
            return new Response(body.challenge);
        }
        // Process event
        if (body.type === 'event_callback' && body.event) {
            ctx.waitUntil(processEvent(body.event, env));
        }
        // Always return 200 OK to acknowledge receipt
        return new Response(JSON.stringify({ ok: true }), {
            headers: { 'Content-Type': 'application/json' },
        });
    }
    catch (error) {
        console.error('Error handling Slack event:', error);
        return new Response(JSON.stringify({
            error: 'Internal server error',
            details: error instanceof Error ? error.message : String(error),
        }), { status: 500, headers: { 'Content-Type': 'application/json' } });
    }
}
async function processEvent(event, env) {
    try {
        const { eventType, date, responseUrl } = (0, slack_parse_1.parseSlackEvent)(event);
        if (!eventType) {
            console.log('Event does not require processing:', event.type);
            return;
        }
        console.log(`Processing ${eventType} event for date: ${date}`);
        if (!date) {
            await (0, slack_respond_1.respondToSlack)(responseUrl, {
                text: '❌ Could not extract date. Please provide a date in YYYY-MM-DD format.',
            });
            return;
        }
        // Validate date format
        if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
            await (0, slack_respond_1.respondToSlack)(responseUrl, {
                text: `❌ Invalid date format: "${date}". Please use YYYY-MM-DD format.`,
            });
            return;
        }
        // Trigger GitHub workflow
        const workflowResult = await (0, github_dispatch_1.triggerGitHubWorkflow)(date, env);
        if (workflowResult.success) {
            const confirmation = {
                text: `✅ Panchangam calculation triggered for ${date}`,
                blocks: [
                    {
                        type: 'section',
                        text: {
                            type: 'mrkdwn',
                            text: `*Panchangam Calculation Triggered*\n\nDate: \`${date}\`\nStatus: Processing...\n\n<https://github.com/achar24/panchang-engine/actions|View in GitHub Actions>`,
                        },
                    },
                ],
            };
            await (0, slack_respond_1.respondToSlack)(responseUrl, confirmation);
            console.log(`✅ Workflow triggered successfully for ${date}`);
        }
        else {
            await (0, slack_respond_1.respondToSlack)(responseUrl, {
                text: `❌ Failed to trigger workflow: ${workflowResult.error}`,
            });
            console.error(`Failed to trigger workflow: ${workflowResult.error}`);
        }
    }
    catch (error) {
        console.error('Error processing event:', error);
    }
}
//# sourceMappingURL=index.js.map
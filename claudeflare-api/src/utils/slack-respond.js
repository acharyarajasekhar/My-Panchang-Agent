"use strict";
/**
 * Slack Response Handler
 * ─────────────────────
 * Sends responses back to Slack via webhook or API
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.respondToSlack = respondToSlack;
exports.postToSlackWebhook = postToSlackWebhook;
async function respondToSlack(responseUrl, message) {
    if (!responseUrl) {
        console.warn('No response URL available for Slack response');
        return;
    }
    try {
        const response = await fetch(responseUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(message),
        });
        if (!response.ok) {
            console.error(`Failed to send Slack response: ${response.status} ${response.statusText}`);
        }
        else {
            console.log('✅ Slack response sent successfully');
        }
    }
    catch (error) {
        console.error('Error sending Slack response:', error);
    }
}
/**
 * Send a message to Slack via Incoming Webhook
 * (fallback if response_url is not available)
 */
async function postToSlackWebhook(message, env) {
    if (!env.SLACK_WEBHOOK_URL) {
        console.warn('SLACK_WEBHOOK_URL not configured');
        return;
    }
    try {
        const response = await fetch(env.SLACK_WEBHOOK_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(message),
        });
        if (!response.ok) {
            console.error(`Failed to post to Slack webhook: ${response.status} ${response.statusText}`);
        }
        else {
            console.log('✅ Message posted to Slack webhook');
        }
    }
    catch (error) {
        console.error('Error posting to Slack webhook:', error);
    }
}
//# sourceMappingURL=slack-respond.js.map
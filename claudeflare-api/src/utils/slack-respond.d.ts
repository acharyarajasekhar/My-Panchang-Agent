/**
 * Slack Response Handler
 * ─────────────────────
 * Sends responses back to Slack via webhook or API
 */
interface Env {
    SLACK_WEBHOOK_URL?: string;
}
interface SlackMessage {
    text?: string;
    blocks?: unknown[];
    thread_ts?: string;
    reply_broadcast?: boolean;
}
export declare function respondToSlack(responseUrl: string | undefined, message: SlackMessage): Promise<void>;
/**
 * Send a message to Slack via Incoming Webhook
 * (fallback if response_url is not available)
 */
export declare function postToSlackWebhook(message: SlackMessage, env: Env): Promise<void>;
export {};
//# sourceMappingURL=slack-respond.d.ts.map
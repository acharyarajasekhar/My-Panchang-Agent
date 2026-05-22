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

export async function respondToSlack(
  responseUrl: string | undefined,
  message: SlackMessage
): Promise<void> {
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
      console.error(
        `Failed to send Slack response: ${response.status} ${response.statusText}`
      );
    } else {
      console.log('✅ Slack response sent successfully');
    }
  } catch (error) {
    console.error('Error sending Slack response:', error);
  }
}

/**
 * Send a message to Slack via Incoming Webhook
 * (fallback if response_url is not available)
 */
export async function postToSlackWebhook(
  message: SlackMessage,
  env: Env
): Promise<void> {
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
      console.error(
        `Failed to post to Slack webhook: ${response.status} ${response.statusText}`
      );
    } else {
      console.log('✅ Message posted to Slack webhook');
    }
  } catch (error) {
    console.error('Error posting to Slack webhook:', error);
  }
}

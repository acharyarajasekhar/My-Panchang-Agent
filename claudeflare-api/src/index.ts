/**
 * Panchang Slack Bridge - Cloudflare Worker
 * ──────────────────────────────────────────
 * Acts as a mediator between Slack and GitHub Actions.
 * 
 * Slack → Extract Date (YYYY-MM-DD) → Trigger GitHub Workflow → Response
 */

import { verifySlackSignature } from './utils/slack-verify';
import { triggerGitHubWorkflow } from './utils/github-dispatch';
import { parseSlackEvent } from './utils/slack-parse';
import { respondToSlack } from './utils/slack-respond';
import { generateAppHomeCalendar, extractDateFromAction } from './utils/app-home-calendar';

interface Env {
  GITHUB_TOKEN: string;
  GITHUB_OWNER: string;
  GITHUB_REPO: string;
  SLACK_SIGNING_SECRET: string;
  SLACK_WEBHOOK_URL?: string;
}

interface SlackEvent {
  type: string;
  event?: Record<string, unknown>;
  challenge?: string;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
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

    // Route: Slack Slash Commands
    if (url.pathname === '/slack/commands') {
      return handleSlashCommand(request, env);
    }

    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' },
    });
  },
};

async function handleSlackEvents(
  request: Request,
  env: Env,
  ctx: ExecutionContext
): Promise<Response> {
  try {
    // Read the request body
    const rawBody = await request.text();
    const timestamp = request.headers.get('X-Slack-Request-Timestamp');
    const signature = request.headers.get('X-Slack-Signature');

    // Log what we received
    console.log('Raw body received:', rawBody.substring(0, 200));

    // Verify Slack signature
    if (!timestamp || !signature) {
      console.error('Missing Slack verification headers');
      return new Response(JSON.stringify({ error: 'Invalid request' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const isValid = await verifySlackSignature(
      env.SLACK_SIGNING_SECRET,
      timestamp,
      rawBody,
      signature
    );

    if (!isValid) {
      console.error('Slack signature verification failed');
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Check if this is form-encoded (slash command or interactive action)
    if (rawBody.includes('payload=')) {
      // This is an interactive action - delegate to interaction handler
      console.log('Detected interactive action payload');
      return handleInteractiveActionPayload(rawBody, env);
    }
    
    if (rawBody.includes('command=')) {
      // This is a slash command - delegate to slash command handler
      console.log('Detected slash command payload');
      return handleSlashCommandPayload(rawBody);
    }

    // Parse as JSON event
    const body: SlackEvent = JSON.parse(rawBody);

    // Respond to URL verification challenge
    if (body.type === 'url_verification' && body.challenge) {
      return new Response(body.challenge);
    }

    // Process event
    if (body.type === 'event_callback' && body.event) {
      const eventType = (body.event as Record<string, unknown>).type;
      
      // Handle app_home_opened - show calendar
      if (eventType === 'app_home_opened') {
        const userId = (body.event as Record<string, unknown>).user as string;
        ctx.waitUntil(handleAppHomeOpened(userId));
      } else {
        ctx.waitUntil(processEvent(body.event, env));
      }
    }

    // Always return 200 OK to acknowledge receipt
    return new Response(JSON.stringify({ ok: true }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error handling Slack event:', error);
    return new Response(
      JSON.stringify({
        error: 'Internal server error',
        details: error instanceof Error ? error.message : String(error),
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

async function processEvent(
  event: Record<string, unknown>,
  env: Env
): Promise<void> {
  try {
    const { eventType, date, responseUrl } =
      parseSlackEvent(event);

    if (!eventType) {
      console.log('Event does not require processing:', event.type);
      return;
    }

    console.log(`Processing ${eventType} event for date: ${date}`);

    if (!date) {
      await respondToSlack(
        responseUrl,
        {
          text: '❌ Could not extract date. Please provide a date in YYYY-MM-DD format.',
        }
      );
      return;
    }

    // Validate date format
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) {
      await respondToSlack(
        responseUrl,
        {
          text: `❌ Invalid date format: "${date}". Please use YYYY-MM-DD format.`,
        }
      );
      return;
    }

    // Trigger GitHub workflow
    const workflowResult = await triggerGitHubWorkflow(date, env);

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

      await respondToSlack(responseUrl, confirmation);
      console.log(`✅ Workflow triggered successfully for ${date}`);
    } else {
      await respondToSlack(
        responseUrl,
        {
          text: `❌ Failed to trigger workflow: ${workflowResult.error}`,
        }
      );
      console.error(`Failed to trigger workflow: ${workflowResult.error}`);
    }
  } catch (error) {
    console.error('Error processing event:', error);
  }
}

async function handleSlashCommand(
  request: Request,
  env: Env
): Promise<Response> {
  try {
    const rawBody = await request.text();
    const timestamp = request.headers.get('X-Slack-Request-Timestamp');
    const signature = request.headers.get('X-Slack-Signature');

    // Verify Slack signature
    if (!timestamp || !signature) {
      return new Response(JSON.stringify({ error: 'Invalid request' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const isValid = await verifySlackSignature(
      env.SLACK_SIGNING_SECRET,
      timestamp,
      rawBody,
      signature
    );

    if (!isValid) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Return calendar modal for slash command
    const calendarData = generateAppHomeCalendar();
    return new Response(JSON.stringify({
      response_type: 'in_channel',
      blocks: calendarData.blocks,
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error handling slash command:', error);
    return new Response(
      JSON.stringify({
        response_type: 'ephemeral',
        text: 'Error processing command',
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

async function handleSlashCommandPayload(
  rawBody: string
): Promise<Response> {
  try {
    const bodyParams = new URLSearchParams(rawBody);
    const command = bodyParams.get('command');
    const userId = bodyParams.get('user_id');

    console.log(`Slash command received: ${command} from user: ${userId}`);

    // Generate calendar for any panchang-related slash command
    if (command === '/panchang') {
      console.log('Returning calendar blocks for slash command');
      const calendarData = generateAppHomeCalendar();
      return new Response(JSON.stringify({
        response_type: 'in_channel',
        blocks: calendarData.blocks,
      }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response(
      JSON.stringify({
        response_type: 'ephemeral',
        text: 'Unknown command',
      }),
      { headers: { 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Error handling slash command payload:', error);
    return new Response(
      JSON.stringify({
        response_type: 'ephemeral',
        text: 'Error processing command',
      }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

async function handleInteractiveActionPayload(
  rawBody: string,
  env: Env
): Promise<Response> {
  try {
    const bodyParams = new URLSearchParams(rawBody);
    const payload = JSON.parse(bodyParams.get('payload') || '{}') as Record<string, unknown>;

    console.log('Interactive action received:', payload.type);

    // Handle block_actions (calendar date button clicks)
    if (payload.type === 'block_actions') {
      const actions = payload.actions as Array<Record<string, unknown>>;
      if (actions && actions.length > 0) {
        const action = actions[0];
        const actionId = action.action_id as string;
        const date = extractDateFromAction(actionId);

        if (date) {
          console.log(`Date selected from calendar: ${date}`);
          
          // Trigger workflow
          const workflowResult = await triggerGitHubWorkflow(date, env);
          
          if (workflowResult.success) {
            return new Response(
              JSON.stringify({
                response_type: 'ephemeral',
                text: `✅ Panchangam calculation triggered for ${date}`,
              }),
              { headers: { 'Content-Type': 'application/json' } }
            );
          } else {
            return new Response(
              JSON.stringify({
                response_type: 'ephemeral',
                text: `❌ Failed to trigger workflow: ${workflowResult.error}`,
              }),
              { headers: { 'Content-Type': 'application/json' } }
            );
          }
        }
      }
    }

    return new Response(JSON.stringify({ ok: true }), {
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error handling interactive action:', error);
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}

async function handleAppHomeOpened(userId: string): Promise<void> {
  try {
    console.log(`App Home opened for user: ${userId}`);
    // Calendar is automatically shown in app home - just log the event
    // Slack will display the calendar view we return
  } catch (error) {
    console.error('Error handling app home opened:', error);
  }
}

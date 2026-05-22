/**
 * Slack Event Parser
 * ──────────────────
 * Extracts relevant data from Slack events and messages
 */

interface ParsedEvent {
  eventType?: string; // 'app_mention' | 'message' | 'slash_command'
  date?: string;
  responseUrl?: string;
  userId?: string;
  channelId?: string;
  text?: string;
}

export function parseSlackEvent(event: Record<string, unknown>): ParsedEvent {
  const eventType = event.type as string;

  switch (eventType) {
    case 'app_mention': {
      return parseAppMention(event);
    }
    case 'message': {
      return parseMessage(event);
    }
    default:
      return {};
  }
}

function parseAppMention(event: Record<string, unknown>): ParsedEvent {
  const text = event.text as string;
  const date = extractDateFromMessage(text);

  return {
    eventType: 'app_mention',
    date,
    text,
    userId: event.user as string,
    channelId: event.channel as string,
    responseUrl: buildResponseUrl(event),
  };
}

function parseMessage(event: Record<string, unknown>): ParsedEvent {
  const text = event.text as string;
  
  // Only process messages that contain date-like patterns
  // Skip if it's a message from a bot or contains 'panchang'
  if (
    event.bot_id ||
    !text ||
    !isRelevantMessage(text)
  ) {
    return {};
  }

  const date = extractDateFromMessage(text);

  if (!date) {
    return {};
  }

  return {
    eventType: 'message',
    date,
    text,
    userId: event.user as string,
    channelId: event.channel as string,
    responseUrl: buildResponseUrl(event),
  };
}

export function extractDateFromMessage(text: string): string | undefined {
  if (!text) return undefined;

  // Look for YYYY-MM-DD pattern
  const dateMatch = text.match(/\d{4}-\d{2}-\d{2}/);
  if (dateMatch) {
    return dateMatch[0];
  }

  // Look for common date formats and try to convert
  // e.g., "June 15, 2026" -> "2026-06-15"
  const dateObject = parseFlexibleDate(text);
  if (dateObject) {
    return formatDateAsISO(dateObject);
  }

  return undefined;
}

function isRelevantMessage(text: string): boolean {
  // Check for keywords
  const keywords = [
    'panchang',
    'panchangam',
    'calculate',
    'date',
    'ephemeris',
  ];
  const lowerText = text.toLowerCase();
  
  // Accept if it contains keywords OR is a date pattern (for DMs)
  const hasKeyword = keywords.some((keyword) => lowerText.includes(keyword));
  const hasDatePattern = /\d{4}-\d{2}-\d{2}/.test(text); // YYYY-MM-DD
  
  return hasKeyword || hasDatePattern;
}

function parseFlexibleDate(text: string): Date | null {
  // Try to parse various date formats
  const patterns = [
    /(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})/, // DD/MM/YYYY or MM/DD/YYYY
    /(\w+)\s+(\d{1,2}),?\s+(\d{4})/, // January 15, 2026
  ];

  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      try {
        const date = new Date(match[0]);
        if (!isNaN(date.getTime())) {
          return date;
        }
      } catch {
        // Continue to next pattern
      }
    }
  }

  return null;
}

function formatDateAsISO(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function buildResponseUrl(event: Record<string, unknown>): string {
  // For Slack Events API, we need to build response URL from context
  // In reality, we'll use the response_url if available (webhooks)
  // For app_mention/message, we'll post back to channel via Slack API
  if (event.response_url) {
    return event.response_url as string;
  }

  // Fallback: we'll need to use Slack Web API to post to channel
  return '';
}

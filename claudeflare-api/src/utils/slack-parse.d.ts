/**
 * Slack Event Parser
 * ──────────────────
 * Extracts relevant data from Slack events and messages
 */
interface ParsedEvent {
    eventType?: string;
    date?: string;
    responseUrl?: string;
    userId?: string;
    channelId?: string;
    text?: string;
}
export declare function parseSlackEvent(event: Record<string, unknown>): ParsedEvent;
export declare function extractDateFromMessage(text: string): string | undefined;
export {};
//# sourceMappingURL=slack-parse.d.ts.map
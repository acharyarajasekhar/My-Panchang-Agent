/**
 * Slack Request Signature Verification
 * ────────────────────────────────────
 * Verifies that requests are actually from Slack
 * using HMAC-SHA256 signature validation.
 */
export declare function verifySlackSignature(signingSecret: string, timestamp: string, body: string, signature: string): Promise<boolean>;
//# sourceMappingURL=slack-verify.d.ts.map
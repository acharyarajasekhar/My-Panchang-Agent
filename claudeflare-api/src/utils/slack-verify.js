"use strict";
/**
 * Slack Request Signature Verification
 * ────────────────────────────────────
 * Verifies that requests are actually from Slack
 * using HMAC-SHA256 signature validation.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.verifySlackSignature = verifySlackSignature;
async function verifySlackSignature(signingSecret, timestamp, body, signature) {
    // Prevent replay attacks
    const now = Math.floor(Date.now() / 1000);
    const slackTime = parseInt(timestamp, 10);
    // Allow 5 minute drift
    if (Math.abs(now - slackTime) > 300) {
        console.warn('Slack signature timestamp too old:', timestamp);
        return false;
    }
    // Build signature base string
    const signatureBaseString = `v0:${timestamp}:${body}`;
    // Create HMAC
    const encoder = new TextEncoder();
    const hmacKey = encoder.encode(signingSecret);
    const messageBytes = encoder.encode(signatureBaseString);
    // Use WebCrypto API available in Cloudflare Workers
    try {
        const key = await crypto.subtle.importKey('raw', hmacKey, { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
        const signatureBuffer = await crypto.subtle.sign('HMAC', key, messageBytes);
        const computedSignature = 'v0=' +
            Array.from(new Uint8Array(signatureBuffer))
                .map((b) => b.toString(16).padStart(2, '0'))
                .join('');
        // Use constant-time comparison to prevent timing attacks
        return constantTimeCompare(computedSignature, signature);
    }
    catch (error) {
        console.error('Error verifying signature:', error);
        return false;
    }
}
/**
 * Constant-time string comparison to prevent timing attacks
 */
function constantTimeCompare(a, b) {
    if (a.length !== b.length) {
        return false;
    }
    let result = 0;
    for (let i = 0; i < a.length; i++) {
        result |= a.charCodeAt(i) ^ b.charCodeAt(i);
    }
    return result === 0;
}
//# sourceMappingURL=slack-verify.js.map
/**
 * Panchang Slack Bridge - Cloudflare Worker
 * ──────────────────────────────────────────
 * Acts as a mediator between Slack and GitHub Actions.
 *
 * Slack → Extract Date (YYYY-MM-DD) → Trigger GitHub Workflow → Response
 */
interface Env {
    GITHUB_TOKEN: string;
    GITHUB_OWNER: string;
    GITHUB_REPO: string;
    SLACK_SIGNING_SECRET: string;
    SLACK_WEBHOOK_URL?: string;
}
declare const _default: {
    fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response>;
};
export default _default;
//# sourceMappingURL=index.d.ts.map
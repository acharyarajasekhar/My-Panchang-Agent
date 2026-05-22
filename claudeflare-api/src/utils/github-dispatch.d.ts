/**
 * GitHub Workflow Dispatch Trigger
 * ────────────────────────────────
 * Triggers the Panchang calculation workflow via GitHub API
 */
interface Env {
    GITHUB_TOKEN: string;
    GITHUB_OWNER: string;
    GITHUB_REPO: string;
}
export declare function triggerGitHubWorkflow(date: string, env: Env): Promise<{
    success: boolean;
    error?: string;
}>;
export {};
//# sourceMappingURL=github-dispatch.d.ts.map
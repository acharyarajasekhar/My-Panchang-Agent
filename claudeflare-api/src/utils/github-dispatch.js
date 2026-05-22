/**
 * GitHub Workflow Dispatch Trigger
 * ────────────────────────────────
 * Triggers the Panchang calculation workflow via GitHub API
 */
export async function triggerGitHubWorkflow(date, env) {
    try {
        const githubOwner = env.GITHUB_OWNER;
        const githubRepo = env.GITHUB_REPO;
        const eventType = 'panchang-webhook';
        const url = `https://api.github.com/repos/${githubOwner}/${githubRepo}/dispatches`;
        const payload = {
            event_type: eventType,
            client_payload: {
                date: date,
            },
        };
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                Authorization: `token ${env.GITHUB_TOKEN}`,
                'Content-Type': 'application/json',
                'User-Agent': 'Panchang-Slack-Bridge/1.0',
            },
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`GitHub dispatch failed with status ${response.status}:`, errorText);
            return {
                success: false,
                error: `GitHub API returned ${response.status}: ${errorText}`,
            };
        }
        console.log(`✅ GitHub workflow dispatched for date: ${date}`);
        return { success: true };
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error('Error triggering GitHub workflow:', errorMessage);
        return {
            success: false,
            error: errorMessage,
        };
    }
}
//# sourceMappingURL=github-dispatch.js.map
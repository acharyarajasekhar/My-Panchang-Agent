# Trigger Panchangam Webhook
# Usage: .\trigger-webhook.ps1 -Date "2026-06-15"
# Or:    .\trigger-webhook.ps1 (uses today's date)

param(
    [string]$Date = (Get-Date -Format "yyyy-MM-dd"),
    [string]$GitHubToken = $env:PANCHANG_GITHUB_TOKEN,
    [string]$RepoOwner = $env:GITHUB_OWNER,
    [string]$RepoName = $env:GITHUB_REPO
)

# Validate date format
if ($Date -notmatch '^\d{4}-\d{2}-\d{2}$') {
    Write-Error "Invalid date format: $Date. Use YYYY-MM-DD"
    exit 1
}

# Check if required environment variables are set
if (-not $GitHubToken) {
    Write-Error "GitHub token not found. Set environment variable: `$env:PANCHANG_GITHUB_TOKEN = 'your_token'"
    exit 1
}

if (-not $RepoOwner) {
    Write-Error "Repository owner not found. Set environment variable: `$env:GITHUB_OWNER = 'your_github_username'"
    exit 1
}

if (-not $RepoName) {
    Write-Error "Repository name not found. Set environment variable: `$env:GITHUB_REPO = 'your_repo_name'"
    exit 1
}

# Prepare request
$headers = @{
    "Authorization" = "token $GitHubToken"
    "Content-Type" = "application/json"
}

$body = @{
    event_type = "panchang-webhook"
    client_payload = @{
        date = $Date
    }
} | ConvertTo-Json

$uri = "https://api.github.com/repos/$RepoOwner/$RepoName/dispatches"

Write-Host "Triggering webhook for date: $Date" -ForegroundColor Cyan
Write-Host "Repository: $RepoOwner/$RepoName" -ForegroundColor Cyan

try {
    $response = Invoke-RestMethod -Method Post `
        -Uri $uri `
        -Headers $headers `
        -Body $body
    
    Write-Host "✅ Webhook triggered successfully!" -ForegroundColor Green
    Write-Host "Check GitHub Actions: https://github.com/$RepoOwner/$RepoName/actions" -ForegroundColor Green
}
catch {
    Write-Error "Failed to trigger webhook: $_"
    exit 1
}

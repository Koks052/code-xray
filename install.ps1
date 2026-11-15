$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillSource = Join-Path $repoRoot 'skills\code-xray'
$claudeRoot = Join-Path $HOME '.claude'
$claudeCommandsSource = Join-Path $repoRoot '.claude\commands'
$claudeCommands = Join-Path $claudeRoot 'commands'

$skillTargets = @(
    [pscustomobject]@{ Name = 'Claude Code (user)'; Path = (Join-Path $HOME '.claude\skills\code-xray') }
    [pscustomobject]@{ Name = 'Codex and Agent Skills clients (user)'; Path = (Join-Path $HOME '.agents\skills\code-xray') }
    [pscustomobject]@{ Name = 'Claude Code (project)'; Path = (Join-Path $repoRoot '.claude\skills\code-xray') }
    [pscustomobject]@{ Name = 'GitHub Copilot (project)'; Path = (Join-Path $repoRoot '.github\skills\code-xray') }
    [pscustomobject]@{ Name = 'Cursor (project)'; Path = (Join-Path $repoRoot '.cursor\skills\code-xray') }
    [pscustomobject]@{ Name = 'Codex and Agent Skills clients (project)'; Path = (Join-Path $repoRoot '.agents\skills\code-xray') }
)

foreach ($target in $skillTargets) {
    New-Item -ItemType Directory -Force -Path $target.Path | Out-Null
    Copy-Item -Path (Join-Path $skillSource '*') -Destination $target.Path -Recurse -Force
    Write-Output "Installed code-xray for $($target.Name): $($target.Path)"
}

New-Item -ItemType Directory -Force -Path $claudeCommands | Out-Null

Get-ChildItem -LiteralPath $claudeCommandsSource -Filter '*.md' -File | ForEach-Object {
    $destination = Join-Path $claudeCommands $_.Name
    if (Test-Path -LiteralPath $destination) {
        Write-Warning "Keeping existing Claude command: $destination"
    }
    else {
        Copy-Item -LiteralPath $_.FullName -Destination $destination
    }
}

Write-Output "Installed code-xray commands for Claude Code: $claudeCommands"

$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillSource = Join-Path $repoRoot 'skills\code-xray'
$claudeRoot = Join-Path $HOME '.claude'
$claudeSkill = Join-Path $claudeRoot 'skills\code-xray'
$claudeCommandsSource = Join-Path $repoRoot '.claude\commands'
$claudeCommands = Join-Path $claudeRoot 'commands'
$copilotSkill = Join-Path $repoRoot '.github\skills\code-xray'

New-Item -ItemType Directory -Force -Path $claudeSkill, $claudeCommands, $copilotSkill | Out-Null
Copy-Item -Path (Join-Path $skillSource '*') -Destination $claudeSkill -Recurse -Force
Copy-Item -Path (Join-Path $skillSource '*') -Destination $copilotSkill -Recurse -Force

Get-ChildItem -LiteralPath $claudeCommandsSource -Filter '*.md' -File | ForEach-Object {
    $destination = Join-Path $claudeCommands $_.Name
    if (Test-Path -LiteralPath $destination) {
        Write-Warning "Keeping existing Claude command: $destination"
    }
    else {
        Copy-Item -LiteralPath $_.FullName -Destination $destination
    }
}

Write-Output "Installed code-xray for Claude Code: $claudeSkill"
Write-Output "Installed code-xray commands for Claude Code: $claudeCommands"
Write-Output "Installed code-xray for GitHub Copilot: $copilotSkill"

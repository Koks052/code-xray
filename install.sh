#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$SCRIPT_DIR
SOURCE=$REPO_ROOT/skills/code-xray
CLAUDE_COMMANDS_SOURCE=$REPO_ROOT/.claude/commands
CLAUDE_COMMANDS_DEST=$HOME/.claude/commands

install_skill() {
    destination=$1
    label=$2
    mkdir -p "$destination"
    cp -R "$SOURCE/." "$destination/"
    printf 'Installed code-xray for %s: %s\n' "$label" "$destination"
}

install_skill "$HOME/.claude/skills/code-xray" "Claude Code (user)"
install_skill "$HOME/.agents/skills/code-xray" "Codex and Agent Skills clients (user)"
install_skill "$REPO_ROOT/.claude/skills/code-xray" "Claude Code (project)"
install_skill "$REPO_ROOT/.github/skills/code-xray" "GitHub Copilot (project)"
install_skill "$REPO_ROOT/.cursor/skills/code-xray" "Cursor (project)"
install_skill "$REPO_ROOT/.agents/skills/code-xray" "Codex and Agent Skills clients (project)"

mkdir -p "$CLAUDE_COMMANDS_DEST"

for command_file in "$CLAUDE_COMMANDS_SOURCE"/*.md; do
    [ -f "$command_file" ] || continue
    command_name=${command_file##*/}
    if [ -e "$CLAUDE_COMMANDS_DEST/$command_name" ]; then
        printf 'Keeping existing Claude command: %s\n' "$CLAUDE_COMMANDS_DEST/$command_name" >&2
    else
        cp "$command_file" "$CLAUDE_COMMANDS_DEST/$command_name"
    fi
done

printf 'Installed code-xray commands for Claude Code: %s\n' "$CLAUDE_COMMANDS_DEST"

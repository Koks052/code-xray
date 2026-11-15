#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$SCRIPT_DIR
SOURCE=$REPO_ROOT/skills/code-xray
CLAUDE_DEST=$HOME/.claude/skills/code-xray
CLAUDE_COMMANDS_SOURCE=$REPO_ROOT/.claude/commands
CLAUDE_COMMANDS_DEST=$HOME/.claude/commands
COPILOT_DEST=$REPO_ROOT/.github/skills/code-xray

mkdir -p "$CLAUDE_DEST" "$CLAUDE_COMMANDS_DEST" "$COPILOT_DEST"
cp -R "$SOURCE/." "$CLAUDE_DEST/"
cp -R "$SOURCE/." "$COPILOT_DEST/"

for command_file in "$CLAUDE_COMMANDS_SOURCE"/*.md; do
    [ -f "$command_file" ] || continue
    command_name=${command_file##*/}
    if [ -e "$CLAUDE_COMMANDS_DEST/$command_name" ]; then
        printf 'Keeping existing Claude command: %s\n' "$CLAUDE_COMMANDS_DEST/$command_name" >&2
    else
        cp "$command_file" "$CLAUDE_COMMANDS_DEST/$command_name"
    fi
done

printf 'Installed code-xray for Claude Code: %s\n' "$CLAUDE_DEST"
printf 'Installed code-xray commands for Claude Code: %s\n' "$CLAUDE_COMMANDS_DEST"
printf 'Installed code-xray for GitHub Copilot: %s\n' "$COPILOT_DEST"
printf 'For Cursor, copy skills/code-xray into .cursor/skills/code-xray if your Cursor version uses project skills.\n'

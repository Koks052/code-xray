---
description: List potential unused Python definitions with code-xray.
argument-hint: [--dir <path>]
---

Use the `code-xray` skill's `dead-code` mode with the optional directory provided in
`$ARGUMENTS`. Resolve `xray.py` from the current repository's
`skills/code-xray/scripts/` directory, or from `~/.claude/skills/code-xray/scripts/`
if the skill is installed for the user. Run it with an available Python 3 interpreter.
On Windows, try `py -3` if `python3` is unavailable, and verify that it starts Python.
If both launchers fail, look under `$HOME/.local/bin/` or
`%LOCALAPPDATA%/Programs/Python/` for an installed interpreter and invoke its full path.
Without `--dir`, the command scans the
current working directory. Describe results as candidates, not proof of dead code.

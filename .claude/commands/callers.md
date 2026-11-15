---
description: Find call sites and references for a symbol with code-xray.
argument-hint: <symbol> [--dir <path>]
---

Use the `code-xray` skill's `callers` mode with the symbol and optional directory
provided in `$ARGUMENTS`. Resolve `xray.py` from the current repository's
`skills/code-xray/scripts/` directory, or from `~/.claude/skills/code-xray/scripts/`
if the skill is installed for the user. Run it with an available Python 3 interpreter.
On Windows, try `py -3` if `python3` is unavailable, and verify that it starts Python.
If both launchers fail, look under `$HOME/.local/bin/` or
`%LOCALAPPDATA%/Programs/Python/` for an installed interpreter and invoke its full path.
Without `--dir`, the command searches the
current working directory. If no matches are found, report which directory was
searched and ask the user which additional directories to check.

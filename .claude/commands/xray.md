---
description: Show a compact structural outline of a source file with code-xray.
argument-hint: <file>
---

Use the `code-xray` skill's `skeleton` mode for the file provided in `$ARGUMENTS`.
Resolve `xray.py` from the current repository's `skills/code-xray/scripts/` directory,
or from `~/.claude/skills/code-xray/scripts/` if the skill is installed for the user.
Run it with an available Python 3 interpreter. On Windows, try `py -3` if `python3`
is unavailable; verify the interpreter runs, because Windows app-execution aliases
can exist without Python being installed. If both launchers fail, look for an
installed interpreter under `$HOME/.local/bin/` or
`%LOCALAPPDATA%/Programs/Python/` and invoke its full path.
If the file argument is missing, ask the user which file to inspect.

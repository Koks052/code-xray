---
name: code-xray
description: Use automatically when exploring unfamiliar files longer than 150 lines, finding function or class usages during refactoring, or cleaning up code. Also activate for /xray, /callers, and /dead-code.
---

# Code X-Ray

Navigate project structure before reading large files or changing shared code. Use the standard-library-only script at `skills/code-xray/scripts/xray.py`; when this skill is installed outside the repository, use the equivalent `scripts/xray.py` path inside the installed skill directory. Run it with an available Python 3 interpreter. Prefer `python3` on macOS/Linux and `py -3` on Windows; verify that the command actually starts Python 3, since Windows app-execution aliases can exist without a working interpreter. If neither command works on Windows, look for an installed interpreter (for example under `$HOME/.local/bin/` or `%LOCALAPPDATA%/Programs/Python/`) and invoke its full path. If no Python 3 interpreter is available, tell the user rather than claiming the scan ran.

## Workflow

1. **Apply the X-Ray First rule.** Before using `Read` on a file longer than 150 lines, run `python3 skills/code-xray/scripts/xray.py skeleton <file>`. Inspect the outline, then use `Read` with the exact `offset` and `limit` for only the function or class you need. Do not read the entire file unless the task requires it.
2. **Apply the Call-Graph rule.** Before changing a function signature or removing a function, run `python3 skills/code-xray/scripts/xray.py callers <symbol>` (or use the available Python 3 command for the platform). This searches the current working directory by default; add `--dir <path>` only when you need to search a different directory. Review the results before editing so you preserve relevant callers. If no matching calls are found, tell the user which directory was scanned and ask which additional directories to check before concluding that there are no callers.
3. **Check cleanup candidates deliberately.** For Python cleanup, run `python3 skills/code-xray/scripts/xray.py dead-code` (or use the available Python 3 command and add `--dir <path>` only to scan another directory). Treat the output as candidates, not proof: review dynamic dispatch, framework registration, command-line entry points, and external consumers before deleting anything.
4. **Honor Token HUD.** At the end of your response, briefly report the estimated context saved when you used `skeleton`. Use its `Saved` percentage and make clear that token counts are approximate; do not claim savings when you did not measure them.

## Commands

- `/xray <file>`, `/callers <symbol>`, and `/dead-code` are registered Claude Code commands when the installer copies `.claude/commands/` into `~/.claude/commands/`. They run the corresponding operation below.

The scanner ignores common generated and dependency directories. Python callers are found from parsed call expressions, not comments or strings; other text files use word-boundary matching. Results are best-effort, so verify important findings manually.

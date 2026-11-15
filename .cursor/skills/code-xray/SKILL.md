---
name: code-xray
description: Use automatically when exploring unfamiliar files longer than 150 lines, finding function or class usages during refactoring, or cleaning up code. Also activate for /xray, /callers, and /dead-code.
---

# Code X-Ray

Use this Agent Skills-compatible workflow in any coding agent that can load skills. If the host does not support Agent Skills, load these instructions through its project rules or prompt and run the bundled script directly. Do not claim automatic activation in a host that does not support it.

Find `xray.py` beside this `SKILL.md` at `scripts/xray.py`. In a source checkout, it is `skills/code-xray/scripts/xray.py`. Run it with Python 3: prefer `py -3` on Windows and `python3` on macOS/Linux. Verify the selected command actually starts Python; Windows app-execution aliases can exist without an interpreter. If needed, locate an installed Python 3 executable and invoke its full path. If none is available, tell the user rather than claiming the scan ran. The script uses Python's standard library only.

## Workflow

1. **Apply X-Ray First.** Before opening a file longer than 150 lines, run `<python3> <script> skeleton <file>` (substitute the Python 3 command available on this system). Use the host's range-reading tool to inspect only the reported lines for the relevant function or class.
2. **Apply Call-Graph before refactoring.** Before changing a function signature or removing code, run `<python3> <script> callers <symbol>`. Project scans default to the current directory; use `--dir <path>` only for a different directory. Review matches before editing. If none are found, state which directory was scanned and ask the user which other directories to check.
3. **Review cleanup candidates.** For Python cleanup, run `<python3> <script> dead-code`. Treat results as leads, not proof; check dynamic dispatch, framework registration, entry points, and external consumers before removing anything.
4. **Honor Token HUD.** At the end of the response, if `skeleton` was used, briefly report its approximate context savings. Do not claim savings that were not measured.

## Commands

- In Claude Code, `/xray <file>`, `/callers <symbol>`, and `/dead-code` are command shortcuts installed into `~/.claude/commands/`.
- In other hosts, activate the skill with that host's skill selector or follow the steps above; slash-command aliases are not universal.
- If the skill cannot be auto-loaded, call the script directly:
  - `<python3> <script> skeleton <file>`
  - `<python3> <script> callers <symbol> [--dir <path>]`
  - `<python3> <script> dead-code [--dir <path>]`

The scanner ignores common generated and dependency directories. Python callers are found from parsed call expressions, not comments or strings; other text files use word-boundary matching. Results are best-effort, so verify important findings manually.

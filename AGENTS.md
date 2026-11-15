# Code X-Ray project instructions

Use the Code X-Ray workflow when exploring unfamiliar code, tracing dependencies before refactoring, or reviewing Python cleanup candidates.

- Resolve the script at `skills/code-xray/scripts/xray.py` and use an available Python 3 interpreter.
- Before opening a source file longer than 150 lines, run `python <script> skeleton <file>`, then read only the relevant reported line range with the host's source-reading tool.
- Before changing a function signature or removing a function, run `python <script> callers <symbol>`. The scan defaults to the current working directory; use `--dir <path>` for another directory. If there are no results, report the scanned directory and ask which other directories to check.
- For Python cleanup, run `python <script> dead-code` and treat the output as candidates. Check dynamic dispatch, framework registration, entry points, and external consumers before removing code.
- If `python` is not Python 3, use the platform's Python 3 command (for example, `py -3` on Windows or `python3` on macOS/Linux). Do not claim a scan ran unless it did.
- When `skeleton` reports token estimates, note that they are approximate and include the measured savings in the final response.

The same skill is available to compatible clients under `.agents/skills/code-xray`, `.claude/skills/code-xray`, `.cursor/skills/code-xray`, and `.github/skills/code-xray`. These are copies of the canonical skill in `skills/code-xray`.

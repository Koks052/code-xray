<div align="center">

# Code X-Ray

**See the shape of a codebase before you read every line.**

[![Python 3](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An agent skill and tiny CLI for fast structural navigation, caller discovery, and Python dead-code triage.

</div>

AI coding agents can waste context opening whole files just to find one function. They can also miss callers when a signature changes, or mistake comments for real code references. **Code X-Ray** gives agents a compact structural outline and focused project-wide search before they read or edit.

## What it does

- Builds Python outlines with the built-in `ast` module, including typed signatures and exact source ranges.
- Extracts imports, exports, and class, interface, and function declarations from JavaScript and TypeScript files.
- Finds Python call expressions without matching comments or string literals, then searches other text files by word boundary.
- Flags potentially unreferenced Python functions and classes for human review.
- Runs on Python's standard library alone; no package installation or network access required.

## Works across AI coding agents

Code X-Ray uses the open [Agent Skills](https://agentskills.io/home) folder format: one portable `SKILL.md` plus its local script. Agent Skills-compatible coding clients can load the same skill; the installer places it in the common locations below.

| Agent | Skill location |
|---|---|
| Claude Code | `~/.claude/skills/code-xray` and `.claude/skills/code-xray` |
| GitHub Copilot | `.github/skills/code-xray` |
| Cursor | `.cursor/skills/code-xray` |
| OpenAI Codex and `.agents/skills` clients | `~/.agents/skills/code-xray` and `.agents/skills/code-xray` |

No single skill format can automatically integrate with **every** AI product. If your coding agent does not discover Agent Skills, load `skills/code-xray/SKILL.md` through its custom instructions or skill importer, then run the bundled script directly. The root [`AGENTS.md`](AGENTS.md) provides a generic project-instructions fallback for agents that support it. Claude slash shortcuts are Claude-specific; other agents use their own skill selector or the CLI commands.

## Three modes

### 1. `skeleton` — inspect structure, not the whole file

```console
$ python3 skills/code-xray/scripts/xray.py skeleton src/billing.py
FUNCTION [L1-L102] def calculate_tax(amount: float) -> float
Original: 102 lines (~416 tokens) | X-Ray: 1 lines (~15 tokens) | Saved: 96%
```

This is actual CLI output from a 102-line sample module; its implementation body is omitted here. The outline reports source line ranges so an agent can read just the relevant section. Token figures are estimates based on text size, not tokenizer measurements.

### 2. `callers` — check call sites before refactoring

```console
$ python3 skills/code-xray/scripts/xray.py callers calculate_tax
tests/test_billing.py:3 -> assert calculate_tax(10) == 110
```

Python results come from parsed call expressions. For other readable files, the tool uses word-boundary matches, which may include declarations or non-call references. By default, search the current working directory; add `--dir src` only to search a different directory.

### 3. `dead-code` — shortlist candidates for review

```console
$ python3 skills/code-xray/scripts/xray.py dead-code
src/legacy.py:1 -> legacy_discount
```

This is a heuristic, not a deletion command. Dynamic dispatch, plugin registration, framework hooks, and external callers can make apparently unused code live.

## Command reference

Run commands from the repository root. For project scans, the current working directory is searched by default, so you do not need to provide `--dir`. Use `python3` on macOS/Linux; on Windows, use `py -3` if `python3` is unavailable.

### `skeleton <file>`

```console
python3 skills/code-xray/scripts/xray.py skeleton src/app.py
```

Print a compact outline for one `.py`, `.js`, `.ts`, `.tsx`, or `.jsx` file. For Python, include imports, classes, functions, methods, typed signatures, and their source-line ranges. For JavaScript and TypeScript, include imports, exports, and class, interface, and function declarations with line ranges. Finish with estimated original and outline token counts and the percentage saved; small files can show zero or negative savings.

### `callers <symbol> [--dir <path>]`

```console
python3 skills/code-xray/scripts/xray.py callers parse_config
```

Search for a symbol in the current working directory. In Python files, report actual calls whose target is the named function or method, ignoring comments and strings. In other readable files, report lines matching the symbol at a word boundary; these matches can include declarations, comments, or non-call references. Print each match as `path:line -> source line`. `--dir <path>` is optional; use it only to search a different directory, for example `--dir src`. Skip `.git`, `node_modules`, virtual environments, caches, and common build output directories.

If no matching lines are found, report that the symbol was not found in the directory scanned and ask the user which additional directories should be searched. Do not claim that the symbol is unused across the whole project based on one directory scan.

### `dead-code [--dir <path>]`

```console
python3 skills/code-xray/scripts/xray.py dead-code
```

Scan Python files in the current working directory and list function or class definitions with no matching name reference in the scanned project. `--dir <path>` is optional; use it only to scan a different directory. Omit `__init__`, `test_*`, and decorated definitions. Treat results as candidates to investigate, not proof: dynamic use, framework registration, and references outside the scanned directory can make a reported symbol necessary.

All commands accept `--help` for argument details. Project scans print warnings for files that cannot be read or parsed and continue with the remaining files.

## Context savings

Savings depend on file size and how much of a file is structurally interesting. These measurements use the tool's approximate character-based token counter:

| Workflow | Full input | X-Ray outline | Approx. reduction |
|---|---:|---:|---:|
| 102-line Python module (sample run) | ~416 tokens | ~15 tokens | 96% |
| 8-line Python module (sample run) | ~55 tokens | ~56 tokens | -2% |
| Call-site or dead-code lookup | Project-dependent | Matching lines or candidates | Varies |

Treat these as examples, not a guarantee. Confirm the actual `Saved` value printed for each file; a small or declaration-heavy file may not save context.

## Quick start

Requirements: Python 3.8+. The CLI works on Windows, macOS, and Linux. The installer copies the skill and commands; it does not install Python. On Windows, first try `py -3`. If that is unavailable, use the full path to an installed Python 3 executable. Check that the selected command actually runs Python: the `python`/`python3` entries in WindowsApps may only be app-store aliases.

```console
# Clone and enter the repository
git clone https://github.com/Koks052/code-xray.git
cd code-xray
# Run from the repository root
python3 -m unittest discover tests
python3 skills/code-xray/scripts/xray.py skeleton path/to/file.py
python3 skills/code-xray/scripts/xray.py callers my_function
python3 skills/code-xray/scripts/xray.py dead-code
```

On Windows, replace `python3` with `py -3` (or the full path to your Python 3 executable), for example:

```powershell
py -3 skills\code-xray\scripts\xray.py callers my_function
```

Install for the common agents above with one command:

```console
# Windows PowerShell (Claude and Codex user skills plus project skills)
.\install.ps1

# macOS/Linux (or Git Bash/WSL on Windows)
sh install.sh
```

The installer copies the portable skill to Claude Code and Codex user directories and to the Claude Code, GitHub Copilot, Cursor, and `.agents/skills` project directories. It also installs `/xray`, `/callers`, and `/dead-code` for Claude Code, preserving unrelated commands with the same names. Restart the coding agent if it does not refresh skills automatically. You can also call the skill `/code-xray` in Claude Code or run the CLI directly.

## Agent workflow

The skill instructions live in [`skills/code-xray/SKILL.md`](skills/code-xray/SKILL.md). They direct agents to outline files over 150 lines before reading, inspect callers before changing or removing a function, and treat dead-code output as a review list.

## Promo video

Watch the short English narrated promo (about 23 seconds): [`promo/code-xray-promo.mp4`](promo/code-xray-promo.mp4). It demonstrates one measured self-scan (~3,505 source tokens to ~298 outline tokens, approximately 91% fewer in that example only), the three modes, and supported agents. Savings are estimated and vary by file. To regenerate it locally on Windows, see [`promo/README.md`](promo/README.md) and run `.\promo\render-promo.ps1`.

## Limitations

- Python analysis follows syntax trees; syntax errors are reported and skipped during project scans.
- JavaScript/TypeScript extraction is dependency-free and heuristic, not a complete parser. Complex syntax may not produce perfect ranges.
- Dead-code output is limited to Python definitions and cannot prove that a symbol is unreachable.
- Scans skip `.git`, `node_modules`, virtual environments, caches, and common build output directories.

## License

MIT. See [LICENSE](LICENSE).

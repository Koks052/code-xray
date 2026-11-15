#!/usr/bin/env python3
"""Fast, dependency-free structural code browsing for AI agents."""

import argparse
import ast
import os
import re
import sys
from pathlib import Path


IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
}
JS_EXTENSIONS = {".js", ".ts", ".tsx", ".jsx"}


def _read_text(path):
    return path.read_text(encoding="utf-8")


def _relative(path, root):
    return path.relative_to(root).as_posix()


def _walk_files(root):
    for current, dirs, filenames in os.walk(root):
        dirs[:] = sorted(name for name in dirs if name not in IGNORED_DIRS)
        for filename in sorted(filenames):
            yield Path(current) / filename


def _source_expression(node, source):
    unparse = getattr(ast, "unparse", None)
    if unparse:
        return unparse(node)
    segment = ast.get_source_segment(source, node)
    return segment if segment is not None else "..."


def _format_arguments(arguments, source):
    positional = list(getattr(arguments, "posonlyargs", [])) + list(arguments.args)
    defaults = [None] * (len(positional) - len(arguments.defaults)) + list(arguments.defaults)
    result = []

    def format_arg(arg, prefix="", default=None):
        text = prefix + arg.arg
        if arg.annotation is not None:
            text += ": " + _source_expression(arg.annotation, source)
        if default is not None:
            text += " = " + _source_expression(default, source)
        return text

    posonly_count = len(getattr(arguments, "posonlyargs", []))
    for index, (arg, default) in enumerate(zip(positional, defaults)):
        result.append(format_arg(arg, default=default))
        if posonly_count and index + 1 == posonly_count:
            result.append("/")

    if arguments.vararg is not None:
        result.append(format_arg(arguments.vararg, "*"))
    elif arguments.kwonlyargs:
        result.append("*")

    for arg, default in zip(arguments.kwonlyargs, arguments.kw_defaults):
        result.append(format_arg(arg, default=default))
    if arguments.kwarg is not None:
        result.append(format_arg(arguments.kwarg, "**"))
    return ", ".join(result)


def _python_skeleton(path):
    source = _read_text(path)
    tree = ast.parse(source, filename=str(path))
    entries = []

    def visit(node, in_class=False):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                names = ", ".join(
                    alias.name + ((" as " + alias.asname) if alias.asname else "")
                    for alias in node.names
                )
                text = "import " + names
            else:
                module = "." * node.level + (node.module or "")
                names = ", ".join(
                    alias.name + ((" as " + alias.asname) if alias.asname else "")
                    for alias in node.names
                )
                text = "from " + module + " import " + names
            entries.append((node.lineno, node.end_lineno, "IMPORT", text))
        elif isinstance(node, ast.ClassDef):
            entries.append(
                (node.lineno, node.end_lineno, "CLASS", "class " + node.name)
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
            kind = "METHOD" if in_class else "FUNCTION"
            signature = (
                prefix
                + "def "
                + node.name
                + "("
                + _format_arguments(node.args, source)
                + ")"
            )
            if node.returns is not None:
                signature += " -> " + _source_expression(node.returns, source)
            entries.append((node.lineno, node.end_lineno, kind, signature))

        child_in_class = in_class or isinstance(node, ast.ClassDef)
        for child in ast.iter_child_nodes(node):
            visit(child, child_in_class)

    visit(tree)
    entries.sort(key=lambda entry: (entry[0], entry[1], entry[2]))
    lines = [
        "{} [L{}-L{}] {}".format(kind, start, end, text)
        for start, end, kind, text in entries
    ]
    return source, lines


def _strip_js_line(line, state):
    output = []
    index = 0
    quote = state.get("quote")
    while index < len(line):
        char = line[index]
        next_char = line[index + 1] if index + 1 < len(line) else ""
        if state.get("block_comment"):
            if char == "*" and next_char == "/":
                state["block_comment"] = False
                index += 2
            else:
                index += 1
            continue
        if quote:
            if char == "\\":
                index += 2
                continue
            if char == quote:
                quote = None
            index += 1
            continue
        if char == "/" and next_char == "*":
            state["block_comment"] = True
            index += 2
            continue
        if char == "/" and next_char == "/":
            break
        if char in ("'", '"', "`"):
            quote = char
            index += 1
            continue
        output.append(char)
        index += 1
    state["quote"] = quote if quote == "`" else None
    return "".join(output)


def _js_declaration_end(code_lines, start):
    depth = 0
    opened = False
    for index in range(start, len(code_lines)):
        for char in code_lines[index]:
            if char == "{":
                depth += 1
                opened = True
            elif char == "}" and opened:
                depth -= 1
                if depth == 0:
                    return index + 1
        if not opened and index > start:
            return index
    return start + 1


def _js_skeleton(path):
    source = _read_text(path)
    lines = source.splitlines()
    state = {"block_comment": False, "quote": None}
    code_lines = [_strip_js_line(line, state) for line in lines]
    entries = []
    declaration_patterns = (
        ("CLASS", re.compile(r"^\s*(?:export\s+(?:default\s+)?)?(?:abstract\s+)?class\s+\w+")),
        ("INTERFACE", re.compile(r"^\s*(?:export\s+(?:default\s+)?)?(?:declare\s+)?interface\s+\w+")),
        ("FUNCTION", re.compile(r"^\s*(?:export\s+(?:default\s+)?)?(?:declare\s+)?(?:async\s+)?function\s*\*?\s*[\w$]+")),
        ("FUNCTION", re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+[\w$]+\s*(?::[^=]+)?=\s*(?:async\s*)?(?:\([^)]*\)|[\w$]+)\s*=>")),
    )
    for index, (line, code) in enumerate(zip(lines, code_lines)):
        start_line = index + 1
        if re.match(r"^\s*import\b", code):
            end_index = index
            while end_index + 1 < len(lines):
                statement = "\n".join(code_lines[index : end_index + 1])
                if (
                    ";" in statement
                    or re.search(r"\bfrom\s*['\"]", statement)
                    or re.match(r"^\s*import\s*['\"]", lines[index])
                ):
                    break
                end_index += 1
            text = " ".join(part.strip() for part in lines[index : end_index + 1])
            entries.append((start_line, end_index + 1, "IMPORT", text))
        if re.match(r"^\s*export\b", code):
            entries.append((start_line, start_line, "EXPORT", line.strip()))
        for kind, pattern in declaration_patterns:
            match = pattern.match(code)
            if match:
                end_line = _js_declaration_end(code_lines, index)
                header = " ".join(part.strip() for part in lines[index:end_line])
                header = header.split("{", 1)[0].strip()
                entries.append((start_line, end_line, kind, header))
                break

    entries.sort(key=lambda entry: (entry[0], entry[2], entry[1]))
    return source, [
        "{} [L{}-L{}] {}".format(kind, start, end, text)
        for start, end, kind, text in entries
    ]


def _token_estimate(text):
    return (len(text) + 3) // 4


def skeleton(path_value):
    path = Path(path_value)
    if not path.is_file():
        raise ValueError("File not found: {}".format(path_value))
    if path.suffix.lower() == ".py":
        source, outline = _python_skeleton(path)
    elif path.suffix.lower() in JS_EXTENSIONS:
        source, outline = _js_skeleton(path)
    else:
        raise ValueError("Unsupported file type: {}".format(path.suffix or "(none)"))

    original_lines = len(source.splitlines())
    original_tokens = _token_estimate(source)
    outline_text = "\n".join(outline)
    outline_lines = len(outline)
    outline_tokens = _token_estimate(outline_text)
    saved = round((1 - outline_tokens / original_tokens) * 100) if original_tokens else 0
    for line in outline:
        print(line)
    print(
        "Original: {} lines (~{} tokens) | X-Ray: {} lines (~{} tokens) | Saved: {}%".format(
            original_lines, original_tokens, outline_lines, outline_tokens, saved
        )
    )


def _python_call_matches(path, symbol):
    source = _read_text(path)
    tree = ast.parse(source, filename=str(path))
    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        called_name = function.id if isinstance(function, ast.Name) else (
            function.attr if isinstance(function, ast.Attribute) else None
        )
        if called_name == symbol:
            matches.append(node.lineno)
    return source.splitlines(), matches


def callers(symbol, directory):
    root = Path(directory).resolve()
    if not root.is_dir():
        raise ValueError("Directory not found: {}".format(directory))
    text_pattern = re.compile(r"\b" + re.escape(symbol) + r"\b")
    results = []
    for path in _walk_files(root):
        try:
            if path.suffix.lower() == ".py":
                source_lines, line_numbers = _python_call_matches(path, symbol)
                for line_number in line_numbers:
                    text = source_lines[line_number - 1].strip()
                    results.append((_relative(path, root), line_number, text))
            else:
                source_lines = _read_text(path).splitlines()
                for line_number, line in enumerate(source_lines, 1):
                    if text_pattern.search(line):
                        results.append((_relative(path, root), line_number, line.strip()))
        except (OSError, UnicodeError, SyntaxError) as error:
            print("Warning: could not scan {}: {}".format(_relative(path, root), error), file=sys.stderr)
    for path, line_number, text in sorted(results):
        print("{}:{} -> {}".format(path, line_number, text))


def _python_definitions(tree, relative_path):
    definitions = []

    def visit(node):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "__init__" or node.name.startswith("test_"):
                    pass
                elif not node.decorator_list:
                    definitions.append((node.name, relative_path, node.lineno))
            elif not node.decorator_list:
                definitions.append((node.name, relative_path, node.lineno))
        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)
    return definitions


def _python_references(tree):
    references = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            references.add(node.id)
        elif isinstance(node, ast.Attribute):
            references.add(node.attr)
        elif isinstance(node, ast.alias):
            references.add(node.asname or node.name.split(".")[0])
    return references


def dead_code(directory):
    root = Path(directory).resolve()
    if not root.is_dir():
        raise ValueError("Directory not found: {}".format(directory))
    definitions = []
    references = set()
    for path in _walk_files(root):
        if path.suffix.lower() != ".py":
            continue
        relative = _relative(path, root)
        try:
            source = _read_text(path)
            tree = ast.parse(source, filename=str(path))
            definitions.extend(_python_definitions(tree, relative))
            references.update(_python_references(tree))
        except (OSError, UnicodeError, SyntaxError) as error:
            print("Warning: could not scan {}: {}".format(relative, error), file=sys.stderr)

    for name, path, line in sorted(definitions, key=lambda item: (item[1], item[2], item[0])):
        if name not in references:
            print("{}:{} -> {}".format(path, line, name))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Navigate code structure and references.")
    commands = parser.add_subparsers(dest="command", required=True)

    skeleton_parser = commands.add_parser("skeleton", help="Print a compact file outline.")
    skeleton_parser.add_argument("path", help="Path to a .py, .js, .ts, .tsx, or .jsx file.")

    callers_parser = commands.add_parser("callers", help="Find calls or text references.")
    callers_parser.add_argument("symbol", help="Function, method, or symbol name.")
    callers_parser.add_argument("--dir", default=".", help="Project directory to scan.")

    dead_parser = commands.add_parser("dead-code", help="List possibly unreferenced Python definitions.")
    dead_parser.add_argument("--dir", default=".", help="Project directory to scan.")

    args = parser.parse_args(argv)
    try:
        if args.command == "skeleton":
            skeleton(args.path)
        elif args.command == "callers":
            callers(args.symbol, args.dir)
        else:
            dead_code(args.dir)
    except (OSError, UnicodeError, SyntaxError, ValueError) as error:
        print("Error: {}".format(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

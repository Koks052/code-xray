import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "code-xray" / "scripts" / "xray.py"


class XRayTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write(self, relative_path, content):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def run_xray(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=str(self.root),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_python_skeleton_shows_imports_typed_signatures_and_ranges(self):
        path = self.write(
            "sample.py",
            "from typing import Optional\n\n"
            "class Greeter:\n"
            "    def greet(self, name: str, times: int = 1) -> Optional[str]:\n"
            "        return name * times\n",
        )
        result = self.run_xray("skeleton", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("IMPORT [L1-L1] from typing import Optional", result.stdout)
        self.assertIn("CLASS [L3-L5] class Greeter", result.stdout)
        self.assertIn(
            "METHOD [L4-L5] def greet(self, name: str, times: int = 1) -> Optional[str]",
            result.stdout,
        )
        self.assertRegex(result.stdout, r"Original: 5 lines .* Saved: -?\d+%")

    def test_javascript_skeleton_reports_import_exports_and_declarations(self):
        path = self.write(
            "sample.ts",
            "import { value } from './value';\n"
            "import './polyfill'\n"
            "export interface Item {\n"
            "  id: string;\n"
            "}\n"
            "export function load(id: string): Item {\n"
            "  return { id };\n"
            "}\n",
        )
        result = self.run_xray("skeleton", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("IMPORT [L1-L1]", result.stdout)
        self.assertIn("IMPORT [L2-L2]", result.stdout)
        self.assertIn("EXPORT [L3-L3]", result.stdout)
        self.assertIn("INTERFACE [L3-L5] export interface Item", result.stdout)
        self.assertIn("FUNCTION [L6-L8] export function load(id: string): Item", result.stdout)

    def test_callers_detects_python_calls_but_not_comments_or_strings(self):
        self.write(
            "app.py",
            "def target():\n"
            "    pass\n\n"
            "# target()\n"
            "message = 'target()'\n"
            "target()\n"
            "service.target()\n",
        )
        (self.root / "ui.js").write_text("target(); // target\n", encoding="utf-8")
        self.write("node_modules/ignored.py", "target()\n")
        result = self.run_xray("callers", "target", "--dir", str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("app.py:6 -> target()", result.stdout)
        self.assertIn("app.py:7 -> service.target()", result.stdout)
        self.assertIn("ui.js:1 -> target(); // target", result.stdout)
        self.assertNotIn("app.py:4", result.stdout)
        self.assertNotIn("app.py:5", result.stdout)
        self.assertNotIn("node_modules", result.stdout)

    def test_dead_code_excludes_tests_and_decorated_definitions_and_tracks_references(self):
        self.write(
            "app.py",
            "def unused():\n"
            "    pass\n\n"
            "class Unused:\n"
            "    pass\n\n"
            "def used():\n"
            "    pass\n\n"
            "used()\n\n"
            "def test_something():\n"
            "    pass\n\n"
            "def __init__():\n"
            "    pass\n\n"
            "@app.route('/')\n"
            "def endpoint():\n"
            "    pass\n",
        )
        result = self.run_xray("dead-code", "--dir", str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            "app.py:1 -> unused\napp.py:4 -> Unused",
        )


if __name__ == "__main__":
    unittest.main()

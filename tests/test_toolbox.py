"""The toolbox must survive an error inside a tool instead of crashing the window.
Run:  python -m unittest discover -s tests -v
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent ))

from tidymate import toolbox  # noqa: E402


class ToolboxTests(unittest.TestCase):
    def test_error_in_a_tool_is_reported_not_fatal(self):
        def boom(ui, cfg):
            raise RuntimeError("simulated problem")

        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / "last_error.txt"
            entry = ("Broken tool", "hint", boom)
            out = io.StringIO()
            # keys: 1 = the broken tool, Enter = continue, 0 = exit
            with mock.patch.object(toolbox, "MENU", [entry]), \
                 mock.patch.object(toolbox, "ERROR_FILE", report), \
                 mock.patch("builtins.input", side_effect=["1", "", "0"]), \
                 contextlib.redirect_stdout(out):
                toolbox.main(["--plain"])
            text = out.getvalue()
            self.assertIn("something went wrong: simulated problem", text)
            self.assertIn("Bye!", text)                       # the menu carried on and exited
            self.assertIn("RuntimeError", report.read_text(encoding="utf-8"))

    def test_systemexit_from_a_tool_does_not_close_the_window(self):
        def exits(ui, cfg):
            raise SystemExit(2)

        with tempfile.TemporaryDirectory() as tmp:
            out = io.StringIO()
            with mock.patch.object(toolbox, "MENU", [("Exits", "hint", exits)]), \
                 mock.patch.object(toolbox, "ERROR_FILE", Path(tmp) / "e.txt"), \
                 mock.patch("builtins.input", side_effect=["1", "", "0"]), \
                 contextlib.redirect_stdout(out):
                toolbox.main(["--plain"])
            self.assertIn("Bye!", out.getvalue())


if __name__ == "__main__":
    unittest.main()

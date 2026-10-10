"""Tests for the `tidymate` command and the quote/apostrophe folder-name bug.
Run:  python -m unittest discover -s tests -v
"""
import contextlib
import io
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tidymate import cli, common, rename_files   # noqa: E402
from tidymate import __version__                 # noqa: E402


def tm(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = cli.main(argv)
    return code, out.getvalue()


class FolderNameTests(unittest.TestCase):
    """Regression: a folder named  Advitya 26'  was 'not a folder' because the tool stripped
    the apostrophe from the end of the path."""

    def test_clean_path_keeps_real_names_and_strips_matching_quotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            odd = Path(tmp, "Advitya 26'")
            odd.mkdir()
            self.assertEqual(common.clean_path(str(odd)), odd)
            self.assertEqual(common.clean_path('"{}"'.format(odd)), odd)
            self.assertEqual(common.clean_path("'{}'".format(odd)), odd)
            plain = Path(tmp, "plain")
            plain.mkdir()
            self.assertEqual(common.clean_path('"{}"'.format(plain)), plain)
        self.assertEqual(str(common.clean_path("x'")), "x'")        # lone quote is kept

    def test_rename_works_in_a_folder_with_an_apostrophe(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp, "Advitya 26'")
            folder.mkdir()
            for name in ("a.JPG", "b.jpg", "c.txt"):
                (folder / name).write_text("x")
            with contextlib.redirect_stdout(io.StringIO()):
                code = rename_files.main(["--number=Ad", "--only=jpg", "-y", "--", str(folder)])
            self.assertEqual(code, 0)
            self.assertEqual(sorted(p.name for p in folder.iterdir() if p.is_file()),
                             ["Ad_001.JPG", "Ad_002.jpg", "c.txt"])

    def test_rename_find_replace_and_text_that_starts_with_a_dash(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "IMG_1.jpg").write_text("x")
            with contextlib.redirect_stdout(io.StringIO()):
                rename_files.main(["--find=IMG", "--replace-with=-Trip-", "-y", "--", tmp])
            self.assertTrue((Path(tmp) / "-Trip-_1.jpg").exists())

    def test_pattern_shortcuts(self):
        self.assertEqual(rename_files.normalise_pattern("jpg"), "*.jpg")
        self.assertEqual(rename_files.normalise_pattern(".png"), "*.png")
        self.assertEqual(rename_files.normalise_pattern("IMG_*"), "IMG_*")
        self.assertEqual(rename_files.normalise_pattern(""), "")


class CliTests(unittest.TestCase):
    def test_version_and_help(self):
        self.assertIn(__version__, tm(["--version"])[1])
        self.assertIn("tidymate tidy FOLDER", tm(["--help"])[1])

    def test_unknown_command(self):
        code, out = tm(["frobnicate"])
        self.assertEqual(code, 2)
        self.assertIn("Unknown command", out)

    def test_explain(self):
        code, out = tm(["explain", "svg", "Photo.JPEG"])
        self.assertEqual(code, 0)
        self.assertIn("SVG vector graphic", out)
        self.assertIn("JPEG photo", out)
        self.assertIn("Goes in: Images/", out)

    def test_tidy_dry_run_then_real_then_undo_via_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp, "report.pdf")
            f.write_text("x")
            old = time.time() - 7200
            os.utime(f, (old, old))
            tm(["tidy", "--dry-run", tmp])
            self.assertTrue(f.exists())
            tm(["tidy", "-y", tmp])
            self.assertTrue(Path(tmp, "Documents", "report.pdf").exists())
            code, out = tm(["undo", tmp, "-y"])
            self.assertEqual(code, 0)
            self.assertTrue(f.exists())

    def test_tools_are_reachable(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "a.txt").write_text("hi")
            for cmd in (["disk", tmp], ["tree", tmp], ["empty", "--dry-run", tmp],
                        ["dupes", tmp], ["checksum", "create", tmp], ["checksum", "verify", tmp]):
                with self.subTest(cmd=cmd[0]):
                    self.assertEqual(tm(cmd)[0], 0)

    def test_config_creates_editable_file_that_is_used(self):
        from tidymate import smart_organizer as so
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp, "categories.json")
            with mock.patch.object(so, "USER_CONFIG_PATH", cfg):
                code, out = tm(["config"])
                self.assertEqual(code, 0)
                self.assertTrue(cfg.exists())
                self.assertIn(str(cfg), out)
                import json
                data = json.loads(cfg.read_text(encoding="utf-8"))
                data["categories"]["Documents"].remove(".epub")
                data["categories"]["Ebooks"] = [".epub"]
                cfg.write_text(json.dumps(data), encoding="utf-8")
                self.assertEqual(so.category_for(".epub", so.load_config()), "Ebooks")

    def test_a_folder_argument_opens_the_menu(self):
        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch("builtins.input", side_effect=["0"]), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(cli.main([tmp, "--plain"]), 0)
        self.assertIn("Working in:", out.getvalue())


if __name__ == "__main__":
    unittest.main()

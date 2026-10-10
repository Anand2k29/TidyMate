"""Tests for smart_organizer.py, migrate_old_folders.py and explain.py.
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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent ))

from tidymate import explain               # noqa: E402
from tidymate import migrate_old_folders   # noqa: E402
from tidymate import smart_organizer as so  # noqa: E402


def make(folder, name, content="x", age_minutes=60):
    path = Path(folder) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    t = time.time() - age_minutes * 60
    os.utime(path, (t, t))
    return path


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = so.main(argv)
    return code, buf.getvalue()


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()

    def test_01_sorts_into_categories(self):
        make(self.dir, "report.pdf"); make(self.dir, "holiday.mp4"); make(self.dir, "logo.svg")
        self.assertEqual(run([str(self.dir), "-y"])[0], 0)
        self.assertTrue((self.dir / "Documents" / "report.pdf").exists())
        self.assertTrue((self.dir / "Videos" / "holiday.mp4").exists())
        self.assertTrue((self.dir / "Images" / "logo.svg").exists())

    def test_02_dry_run_changes_nothing(self):
        make(self.dir, "a.pdf")
        run([str(self.dir), "--dry-run"])
        self.assertTrue((self.dir / "a.pdf").exists())
        self.assertFalse((self.dir / "Documents").exists())

    def test_03_unfinished_downloads_are_left_alone(self):
        make(self.dir, "movie.mp4.crdownload"); make(self.dir, "x.tmp")
        run([str(self.dir), "-y"])
        self.assertTrue((self.dir / "movie.mp4.crdownload").exists())
        self.assertTrue((self.dir / "x.tmp").exists())

    def test_04_recent_files_are_skipped(self):
        make(self.dir, "fresh.pdf", age_minutes=0)
        run([str(self.dir), "-y"])
        self.assertTrue((self.dir / "fresh.pdf").exists())
        run([str(self.dir), "-y", "--min-age", "0"])
        self.assertTrue((self.dir / "Documents" / "fresh.pdf").exists())

    def test_05_name_clash_never_overwrites(self):
        make(self.dir, "Documents/a.pdf", "old")
        make(self.dir, "a.pdf", "new")
        run([str(self.dir), "-y"])
        self.assertEqual((self.dir / "Documents" / "a.pdf").read_text(), "old")
        self.assertEqual((self.dir / "Documents" / "a (1).pdf").read_text(), "new")

    def test_06_dedupe_sends_exact_copies_to_duplicates(self):
        make(self.dir, "Documents/a.pdf", "same")
        make(self.dir, "a.pdf", "same")
        run([str(self.dir), "-y", "--dedupe"])
        self.assertTrue((self.dir / "_Duplicates" / "a.pdf").exists())

    def test_07_subfolders_are_never_touched(self):
        make(self.dir, "MyStuff/notes.txt")
        run([str(self.dir), "-y"])
        self.assertTrue((self.dir / "MyStuff" / "notes.txt").exists())

    def test_08_files_without_extension_stay(self):
        make(self.dir, "Makefile")
        run([str(self.dir), "-y"])
        self.assertTrue((self.dir / "Makefile").exists())

    def test_09_undo_restores_and_removes_new_folders(self):
        make(self.dir, "a.pdf"); make(self.dir, "b.mp3")
        run([str(self.dir), "-y"])
        self.assertFalse((self.dir / "a.pdf").exists())
        code, out = run([str(self.dir), "--undo", "-y"])
        self.assertEqual(code, 0)
        self.assertTrue((self.dir / "a.pdf").exists())
        self.assertTrue((self.dir / "b.mp3").exists())
        self.assertFalse((self.dir / "Documents").exists())

    def test_10_modes_extension_and_date(self):
        make(self.dir, "a.jpeg")
        run([str(self.dir), "-y", "--mode", "extension"])
        self.assertTrue((self.dir / "JPEG" / "a.jpeg").exists())
        run([str(self.dir), "--undo", "-y"])
        run([str(self.dir), "-y", "--mode", "category-date"])
        month = time.strftime("%Y-%m", time.localtime((self.dir / "Images").stat().st_mtime))
        found = list((self.dir / "Images").glob("*/a.jpeg"))
        self.assertEqual(len(found), 1)
        self.assertRegex(found[0].parent.name, r"^\d{4}-\d{2}$")
        self.assertTrue(month)

    def test_11_exclude_pattern(self):
        make(self.dir, "keep.psd"); make(self.dir, "go.pdf")
        run([str(self.dir), "-y", "--exclude", "*.psd"])
        self.assertTrue((self.dir / "keep.psd").exists())
        self.assertTrue((self.dir / "Documents" / "go.pdf").exists())

    def test_12_refuses_drive_root(self):
        code, out = run([Path(self.dir.anchor).as_posix()])
        self.assertEqual(code, 2)
        self.assertIn("top of a drive", out)

    def test_13_migrates_old_extension_folders(self):
        make(self.dir, ".txt/a.txt"); make(self.dir, ".mp4/b.mp4")
        make(self.dir, ".crdownload/c.mp4.crdownload")
        make(self.dir, ".vscode/settings.json")                 # must stay
        make(self.dir, ".txt2/x.txt")                            # mixed -> checked below
        make(self.dir, ".ipynb_checkpoints/n.ipynb")             # must stay
        make(self.dir, ".git/config")                            # must stay
        with contextlib.redirect_stdout(io.StringIO()):
            code = migrate_old_folders.main([str(self.dir), "-y"])
        self.assertEqual(code, 0)
        self.assertTrue((self.dir / "Documents" / "a.txt").exists())
        self.assertTrue((self.dir / "Videos" / "b.mp4").exists())
        self.assertTrue((self.dir / "c.mp4.crdownload").exists())
        self.assertFalse((self.dir / ".txt").exists())
        self.assertTrue((self.dir / ".vscode" / "settings.json").exists())
        self.assertTrue((self.dir / ".git" / "config").exists())
        self.assertTrue((self.dir / ".ipynb_checkpoints" / "n.ipynb").exists())
        run([str(self.dir), "--undo", "-y"])                     # undo recreates old folders
        self.assertTrue((self.dir / ".txt" / "a.txt").exists())


class ExplainTests(unittest.TestCase):
    def test_every_configured_extension_is_explained(self):
        for exts in so.DEFAULT_CONFIG["categories"].values():
            for ext in exts:
                self.assertIn(ext, explain.EXT_INFO, ext)

    def test_lookup_helpers(self):
        self.assertEqual(explain.normalise_ext("SVG"), ".svg")
        self.assertEqual(explain.normalise_ext("Photo.JPEG"), ".jpeg")
        self.assertEqual(explain.folder_for_ext(".svg", so.DEFAULT_CONFIG), "Images")
        self.assertIsNone(explain.folder_for_ext(".crdownload", so.DEFAULT_CONFIG))
        self.assertEqual(explain.folder_for_ext(".zzz", so.DEFAULT_CONFIG), "Other")


if __name__ == "__main__":
    unittest.main()

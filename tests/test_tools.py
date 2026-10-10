"""Tests for the extra tools (rename, archive, duplicates, empty folders, backup,
checksums, disk report, tree) and the shared undo.
Run:  python -m unittest discover -s tests -v
"""
import contextlib
import io
import os
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent ))

from tidymate import archive_old_files     # noqa: E402
from tidymate import backup_folder         # noqa: E402
from tidymate import checksum_tool         # noqa: E402
from tidymate import cleanup_empty_folders  # noqa: E402
from tidymate import common                # noqa: E402
from tidymate import disk_report           # noqa: E402
from tidymate import find_duplicates       # noqa: E402
from tidymate import folder_tree           # noqa: E402
from tidymate import rename_files          # noqa: E402
from tidymate import smart_organizer       # noqa: E402


def make(folder, name, content="x", age_days=0):
    path = Path(folder) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    t = time.time() - age_days * 86400 - 3600
    os.utime(path, (t, t))
    return path


def quiet(func, argv):
    with contextlib.redirect_stdout(io.StringIO()):
        return func(argv)


class ToolTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()

    def names(self):
        return sorted(p.name for p in self.dir.iterdir() if p.is_file())

    # ---- rename ----------------------------------------------------------
    def test_rename_lower_spaces_and_undo(self):
        make(self.dir, "My Photo.JPG"); make(self.dir, "Other File.PNG")
        self.assertEqual(quiet(rename_files.main, [str(self.dir), "--lower", "--spaces", "-y"]), 0)
        self.assertEqual(self.names(), ["my_photo.jpg", "other_file.png"])
        quiet(smart_organizer.main, [str(self.dir), "--undo", "-y"])     # shared undo
        self.assertEqual(self.names(), ["My Photo.JPG", "Other File.PNG"])

    def test_rename_number_and_no_overwrite(self):
        make(self.dir, "a.jpg"); make(self.dir, "b.jpg"); make(self.dir, "trip_001.jpg", "keep")
        quiet(rename_files.main, [str(self.dir), "--number", "trip", "--only", "[ab].jpg", "-y"])
        self.assertEqual((self.dir / "trip_001.jpg").read_text(), "keep")      # not overwritten
        self.assertEqual(self.names(), ["trip_001 (1).jpg", "trip_001.jpg", "trip_002.jpg"])

    def test_rename_requires_a_change(self):
        make(self.dir, "a.txt")
        self.assertEqual(quiet(rename_files.main, [str(self.dir)]), 2)

    def test_rename_replace_and_only(self):
        make(self.dir, "IMG_1.jpg"); make(self.dir, "IMG_2.png")
        quiet(rename_files.main, [str(self.dir), "--replace", "IMG", "Holiday",
                                  "--only", "*.jpg", "-y"])
        self.assertEqual(self.names(), ["Holiday_1.jpg", "IMG_2.png"])

    # ---- archive ---------------------------------------------------------
    def test_archive_moves_only_old_files_and_undoes(self):
        make(self.dir, "old.pdf", age_days=500); make(self.dir, "new.pdf", age_days=1)
        quiet(archive_old_files.main, [str(self.dir), "--days", "365", "-y"])
        self.assertTrue(list((self.dir / "_Old").glob("*/old.pdf")))
        self.assertTrue((self.dir / "new.pdf").exists())
        quiet(smart_organizer.main, [str(self.dir), "--undo", "-y"])
        self.assertTrue((self.dir / "old.pdf").exists())
        self.assertFalse((self.dir / "_Old").exists())

    # ---- duplicates ------------------------------------------------------
    def test_duplicates_report_is_read_only(self):
        make(self.dir, "a.txt", "same"); make(self.dir, "sub/b.txt", "same"); make(self.dir, "c.txt", "diff")
        quiet(find_duplicates.main, [str(self.dir)])
        self.assertEqual(len(find_duplicates.find_groups(self.dir)), 1)
        self.assertTrue((self.dir / "sub" / "b.txt").exists())

    def test_duplicates_move_keeps_oldest_and_never_deletes(self):
        make(self.dir, "a.txt", "same", age_days=10); make(self.dir, "b.txt", "same", age_days=1)
        dest = self.dir / "_review"
        quiet(find_duplicates.main, [str(self.dir), "--move-to", str(dest), "-y"])
        self.assertTrue((self.dir / "a.txt").exists())
        self.assertTrue((dest / "b.txt").exists())
        self.assertTrue(list(dest.glob("duplicates_moved_*.json")))
        quiet(smart_organizer.main, [str(self.dir), "--undo", "-y"])
        self.assertTrue((self.dir / "b.txt").exists())

    # ---- empty folders ---------------------------------------------------
    def test_cleanup_removes_nested_empty_but_keeps_full_and_hidden(self):
        (self.dir / "e1" / "e2").mkdir(parents=True)
        (self.dir / ".git").mkdir()
        make(self.dir, "full/file.txt")
        quiet(cleanup_empty_folders.main, [str(self.dir), "-y"])
        self.assertFalse((self.dir / "e1").exists())
        self.assertTrue((self.dir / ".git").exists())
        self.assertTrue((self.dir / "full" / "file.txt").exists())

    # ---- backup ----------------------------------------------------------
    def test_backup_creates_valid_zip_outside_folder(self):
        src = self.dir / "data"
        make(src, "a.txt", "hello"); make(src, "sub/b.txt", "world")
        out = self.dir / "backups"
        quiet(backup_folder.main, [str(src), "--dest", str(out), "-y"])
        zips = list(out.glob("data_backup_*.zip"))
        self.assertEqual(len(zips), 1)
        with zipfile.ZipFile(zips[0]) as zf:
            self.assertEqual(sorted(zf.namelist()), ["a.txt", "sub/b.txt"])
            self.assertIsNone(zf.testzip())

    # ---- checksums -------------------------------------------------------
    def test_checksum_detects_change_missing_and_new(self):
        make(self.dir, "a.txt", "1"); make(self.dir, "b.txt", "2")
        self.assertEqual(quiet(checksum_tool.main, ["create", str(self.dir)]), 0)
        self.assertEqual(quiet(checksum_tool.main, ["verify", str(self.dir)]), 0)
        (self.dir / "a.txt").write_text("changed")
        (self.dir / "b.txt").unlink()
        make(self.dir, "c.txt", "new")
        self.assertEqual(quiet(checksum_tool.main, ["verify", str(self.dir)]), 1)

    # ---- read-only tools -------------------------------------------------
    def test_disk_report_and_tree_run_and_change_nothing(self):
        make(self.dir, "a.mp4", "x" * 2000); make(self.dir, "d/b.pdf", "y" * 10)
        before = sorted(p.name for p in self.dir.rglob("*"))
        self.assertEqual(quiet(disk_report.main, [str(self.dir)]), 0)
        self.assertEqual(quiet(folder_tree.main, [str(self.dir), "--files"]), 0)
        self.assertEqual(before, sorted(p.name for p in self.dir.rglob("*")))

    # ---- shared helpers --------------------------------------------------
    def test_human_size_and_unique_path(self):
        self.assertEqual(common.human_size(1536), "1.5 KB")
        self.assertEqual(common.human_size(5), "5 B")
        make(self.dir, "x.txt")
        self.assertEqual(common.unique_path(self.dir / "x.txt").name, "x (1).txt")

    def test_tools_refuse_drive_root(self):
        root = Path(self.dir.anchor).as_posix()
        self.assertEqual(quiet(rename_files.main, [root, "--lower"]), 2)
        self.assertEqual(quiet(archive_old_files.main, [root]), 2)


if __name__ == "__main__":
    unittest.main()

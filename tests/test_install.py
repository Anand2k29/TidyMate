"""Tests for the launchers (tidymate / start_here), `tidymate setup`, `tidymate doctor` and "This folder".
Run:  python -m unittest discover -s tests -v
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tidymate import setup_command   # noqa: E402


class LauncherTextTests(unittest.TestCase):
    def test_windows_shim_installed_mode(self):
        text = setup_command.windows_shim(r"C:\Py (x86)\python.exe", None)
        self.assertTrue(text.startswith("@echo off"))
        self.assertIn(r'set "TIDYMATE_PYTHON=C:\Py (x86)\python.exe"', text)
        self.assertIn('"%TIDYMATE_PYTHON%" -m tidymate %*', text)
        self.assertIn("Python that TidyMate was installed with is missing", text)
        self.assertNotIn("TIDYMATE_ROOT", text)
        self.assertTrue(all(line.endswith("\r") for line in text.split("\n")[:-1]))   # CRLF

    def test_windows_shim_source_mode_survives_moves(self):
        text = setup_command.windows_shim(r"C:\Python\python.exe", r"D:\Org 100%\proj")
        self.assertIn(r'set "TIDYMATE_ROOT=D:\Org 100%%\proj"', text)          # % escaped
        self.assertIn('set "PYTHONPATH=%TIDYMATE_ROOT%;%PYTHONPATH%"', text)
        self.assertIn("py -3 -m tidymate %*", text)           # fallback Python
        self.assertNotIn("--here", text)                                  # arguments pass straight through
        self.assertIn("moved or deleted", text)

    def test_unix_shim_variants(self):
        installed = setup_command.unix_shim("/venv/bin/python", None)
        self.assertIn('exec /venv/bin/python -m tidymate "$@"', installed)
        source = setup_command.unix_shim("/usr/bin/python3", "/my proj")
        self.assertIn("ROOT='/my proj'", source)
        self.assertIn("moved or deleted", source)
        self.assertNotIn("--here", source)

    def test_windows_prefers_windowsapps_when_already_on_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            apps = Path(tmp, "Microsoft", "WindowsApps")
            apps.mkdir(parents=True)
            folder, needs_path = setup_command.choose_windows_bin_dir(
                tmp, os.pathsep.join(["/x/y", str(apps)]))
            self.assertEqual(folder, apps)
            self.assertFalse(needs_path)

    def test_windows_falls_back_to_own_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder, needs_path = setup_command.choose_windows_bin_dir(tmp, "/x/y")
            self.assertEqual(folder, Path(tmp, "TidyMate", "bin"))
            self.assertTrue(needs_path)

    def test_bad_command_name_is_refused(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup_command.main(["--name", "bad name!"]), 2)


@unittest.skipIf(os.name == "nt", "Unix install path")
class UnixSetupTests(unittest.TestCase):
    def test_setup_creates_working_commands_and_doctor_and_uninstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            home, work = Path(tmp, "home"), Path(tmp, "work")
            home.mkdir(); work.mkdir()
            env = dict(os.environ, HOME=str(home))
            with mock.patch.dict(os.environ, {"HOME": str(home)}), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(setup_command.main(["--name", "sh_test"]), 0)
            bindir = home / ".local" / "bin"
            self.assertTrue(os.access(bindir / "sh_test", os.X_OK))
            self.assertTrue(os.access(bindir / "start_here", os.X_OK))      # alias is created too
            # run `sh_test` INSIDE the work folder: menu 1 (tidy), Enter = "This folder", then cancel
            (work / "a.pdf").write_text("x")
            os.utime(work / "a.pdf", (1, 1))
            result = subprocess.run([str(bindir / "sh_test")], input="1\n\n0\n\n0\n", cwd=str(work),
                                    capture_output=True, text=True, env=env)
            self.assertIn("Working in: " + str(work.resolve()), result.stdout)
            self.assertIn("This folder", result.stdout)
            self.assertIn("Documents/", result.stdout)                  # preview shown
            self.assertTrue((work / "a.pdf").exists())                  # cancelled -> unchanged
            # `--version` through the alias launcher
            version = subprocess.run([str(bindir / "start_here"), "--version"], capture_output=True,
                                     text=True, env=env)
            self.assertIn("tidymate", version.stdout)
            # doctor: ok when the bin dir is on PATH, explains when it is not
            with mock.patch.dict(os.environ, {"HOME": str(home),
                                              "PATH": str(bindir) + os.pathsep + os.environ["PATH"]}), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(setup_command.check("sh_test"), 0)
            with mock.patch.dict(os.environ, {"HOME": str(home), "PATH": "/usr/bin"}), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(setup_command.check("sh_test"), 1)
                self.assertEqual(setup_command.main(["--name", "sh_test", "--uninstall"]), 0)
            self.assertFalse((bindir / "sh_test").exists())
            self.assertFalse((bindir / "start_here").exists())


if __name__ == "__main__":
    unittest.main()

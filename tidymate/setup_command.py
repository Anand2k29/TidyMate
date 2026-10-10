#!/usr/bin/env python3
"""
setup_command.py - make `tidymate` (and its alias `start_here`) work from ANY terminal, right away.

    tidymate setup                 create the launchers   (python -m tidymate setup)
    tidymate doctor                test them and explain any problem
    tidymate setup --uninstall     remove them again

Why this exists: `pip` puts commands in a "Scripts" folder that is often NOT on your PATH,
and terminals opened before an install (or from File Explorer's address bar) keep an old
copy of PATH. This puts two tiny launcher files where your system ALREADY looks for
commands (Windows: %LOCALAPPDATA%\\Microsoft\\WindowsApps; Mac/Linux: ~/.local/bin), so the
commands work immediately. No admin rights needed.
"""
import argparse
import os
import shlex
import shutil
import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
SOURCE_ROOT = PACKAGE_DIR.parent
DEFAULT_NAME = "tidymate"
ALIAS_NAME = "start_here"          # second name for the same command


# --------------------------------------------------------------------------- #
#  Launcher text
# --------------------------------------------------------------------------- #
def running_from_source():
    """True when run from an unzipped/cloned project (not from an installed package)."""
    return (SOURCE_ROOT / "pyproject.toml").exists() and (PACKAGE_DIR / "__main__.py").exists()


def _bat_escape(text):
    return text.replace("%", "%%")


def windows_shim(python, source_root=None):
    """Launcher for Command Prompt / PowerShell. Passes all your arguments straight through."""
    lines = ["@echo off", "setlocal",
             'set "TIDYMATE_PYTHON={}"'.format(_bat_escape(str(python)))]
    if source_root:
        lines += ['set "TIDYMATE_ROOT={}"'.format(_bat_escape(str(source_root))),
                  'if not exist "%TIDYMATE_ROOT%\\tidymate\\__main__.py" goto moved',
                  'set "PYTHONPATH=%TIDYMATE_ROOT%;%PYTHONPATH%"']
    lines += ['if exist "%TIDYMATE_PYTHON%" goto run']
    if source_root:                                   # unzipped project: any Python will do
        lines += ["where py >nul 2>nul", "if %errorlevel%==0 goto runpy",
                  "where python >nul 2>nul", "if %errorlevel%==0 goto runpython"]
    lines += ["goto gone",
              ":run",
              '"%TIDYMATE_PYTHON%" -m tidymate %*',
              "goto :eof"]
    if source_root:
        lines += [":runpy", "py -3 -m tidymate %*", "goto :eof",
                  ":runpython", "python -m tidymate %*", "goto :eof",
                  ":moved",
                  "echo.",
                  "echo  The TidyMate folder was moved or deleted.",
                  "echo  Open its new location and double-click INSTALL_COMMAND.bat again.",
                  "exit /b 1"]
    lines += [":gone",
              "echo.",
              "echo  The Python that TidyMate was installed with is missing.",
              "echo  Reinstall it, or run:  pip install --upgrade tidymate",
              "echo  and then:  tidymate setup",
              "exit /b 1"]
    return "\r\n".join(lines) + "\r\n"


def unix_shim(python, source_root=None):
    lines = ["#!/bin/sh"]
    if source_root:
        root = shlex.quote(str(source_root))
        lines += ['ROOT={}'.format(root),
                  'if [ ! -f "$ROOT/tidymate/__main__.py" ]; then',
                  '  echo "The TidyMate folder was moved or deleted."',
                  '  echo "Open its new location and run:  python3 -m tidymate setup"',
                  "  exit 1", "fi",
                  'export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"']
    py = shlex.quote(str(python))
    lines += ['if [ -x {} ]; then exec {} -m tidymate "$@"; fi'.format(py, py)]
    if source_root:
        lines += ['exec python3 -m tidymate "$@"']
    else:
        lines += ['echo "The Python that TidyMate was installed with is missing."',
                  'echo "Reinstall it with:  pip install --upgrade tidymate"',
                  "exit 1"]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
#  Where launchers go
# --------------------------------------------------------------------------- #
def _local_app_data():
    return Path(os.environ.get("LOCALAPPDATA") or Path.home())


def windows_bin_dir():
    """Our own private folder (fallback)."""
    return _local_app_data() / "TidyMate" / "bin"


def unix_bin_dir():
    return Path.home() / ".local" / "bin"


def _same(a, b):
    return a.rstrip("\\/").lower() == b.rstrip("\\/").lower()


def choose_windows_bin_dir(localappdata=None, path_env=None):
    """Return (folder, needs_path_edit).

    Windows 10/11 already have  %LOCALAPPDATA%\\Microsoft\\WindowsApps  on every user's PATH
    and it is writable. A command placed there works IMMEDIATELY - even in terminals opened
    from File Explorer, which otherwise keep an old copy of PATH until you sign out.
    """
    base = Path(localappdata) if localappdata else _local_app_data()
    path_env = os.environ.get("PATH", "") if path_env is None else path_env
    apps = base / "Microsoft" / "WindowsApps"
    on_path = any(_same(p, str(apps)) for p in path_env.split(os.pathsep) if p)
    if apps.is_dir() and on_path and os.access(str(apps), os.W_OK):
        return apps, False
    return base / "TidyMate" / "bin", True


def find_shims(name):
    if os.name == "nt":
        folders, suffix = [_local_app_data() / "Microsoft" / "WindowsApps", windows_bin_dir()], ".cmd"
    else:
        folders, suffix = [unix_bin_dir()], ""
    return [f / (name + suffix) for f in folders if (f / (name + suffix)).exists()]


# --------------------------------------------------------------------------- #
#  Windows: user PATH (registry), no admin needed
# --------------------------------------------------------------------------- #
def _broadcast_environment_change():
    try:
        import ctypes
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001A, 0, "Environment", 0x0002,
                                                 5000, None)
    except Exception:
        pass


def registry_path_has(directory):
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, "Path")
        return any(_same(p, str(directory)) for p in value.split(";") if p)
    except Exception:
        return False


def edit_user_path(directory, add=True):
    """Add/remove a folder in the user PATH. Returns True if something changed."""
    import winreg
    directory = str(directory)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                        winreg.KEY_READ | winreg.KEY_SET_VALUE) as key:
        try:
            value, kind = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            value, kind = "", winreg.REG_EXPAND_SZ
        parts = [p for p in value.split(";") if p]
        present = any(_same(p, directory) for p in parts)
        if add and not present:
            parts.append(directory)
        elif not add and present:
            parts = [p for p in parts if not _same(p, directory)]
        else:
            return False
        if kind not in (winreg.REG_SZ, winreg.REG_EXPAND_SZ):
            kind = winreg.REG_EXPAND_SZ
        winreg.SetValueEx(key, "Path", 0, kind, ";".join(parts))
    _broadcast_environment_change()
    return True


# --------------------------------------------------------------------------- #
#  Doctor
# --------------------------------------------------------------------------- #
def check(name=DEFAULT_NAME):
    """Test the command and explain, in plain words, what to do if it won't work."""
    print("Checking the '{}' command ...".format(name))
    print("  Python : {} ({})".format(sys.version.split()[0], sys.executable))
    try:
        from tidymate import __version__
        print("  [ok] TidyMate {} ({})".format(__version__, PACKAGE_DIR))
    except ImportError:
        print("  [x] The tidymate package cannot be imported.")
        return 1
    found = shutil.which(name)
    shims = find_shims(name)
    for shim in shims:
        print("  [ok] Launcher file: {}".format(shim))
    if found:
        print("  [ok] This window can run it: {}".format(found))
        print("\nAll good. Type  {}  in any folder.".format(name))
        return 0
    if not shims:
        print("  [x] The command is not set up yet.")
        print("      Fix: run  tidymate setup   (or: python -m tidymate setup)")
        return 1
    folder = shims[0].parent
    print("  [!] This window cannot find '{}' yet.".format(name))
    if os.name == "nt":
        if registry_path_has(folder):
            print("  [ok] The folder is saved in your PATH, so NEW windows will find it.")
        print()
        print("  Why: a window that was open BEFORE the setup - or one opened from File")
        print("  Explorer's address bar - keeps an old copy of PATH.")
        print("  Fix (pick one):")
        print("    1. PowerShell, this window only:  $env:Path += ';{}'".format(folder))
        print("       Command Prompt, this window only:  set \"PATH=%PATH%;{}\"".format(folder))
        print("    2. Open a NEW terminal from the Start menu, then use  cd  to reach a folder")
        print("    3. Sign out of Windows and back in once (fixes it everywhere, for good)")
    else:
        print('  Add this line to ~/.bashrc or ~/.zshrc, then open a new terminal:')
        print('      export PATH="{}:$PATH"'.format(folder))
    return 1


# --------------------------------------------------------------------------- #
#  Install / uninstall
# --------------------------------------------------------------------------- #
def install(name=DEFAULT_NAME):
    source_root = SOURCE_ROOT if running_from_source() else None
    launchers = [name] + ([ALIAS_NAME] if name != ALIAS_NAME else [])
    if os.name == "nt":
        bindir, needs_path = choose_windows_bin_dir()
        bindir.mkdir(parents=True, exist_ok=True)
        for cmd in launchers:
            shim = bindir / (cmd + ".cmd")
            text = windows_shim(sys.executable, source_root)
            try:
                shim.write_bytes(text.encode("oem"))
            except (LookupError, UnicodeEncodeError):
                shim.write_bytes(text.encode("utf-8"))
            print("[ok] Created {}".format(shim))
        if needs_path:
            edit_user_path(bindir, add=True)
            print("[ok] Added {} to your PATH".format(bindir))
    else:
        bindir = unix_bin_dir()
        bindir.mkdir(parents=True, exist_ok=True)
        for cmd in launchers:
            shim = bindir / cmd
            shim.write_text(unix_shim(sys.executable, source_root))
            shim.chmod(0o755)
            print("[ok] Created {}".format(shim))
    print()
    check(name)                                   # verify, and explain if something is stale
    print()
    print("How to use it:")
    if os.name == "nt":
        print("  1. Open any folder in File Explorer")
        print("  2. Click the address bar, type  cmd  (or  powershell)  and press Enter")
        print("  3. Type:  {}".format(name))
        print("Problems? Run  tidymate doctor  - it tells you exactly what to do.")
    else:
        print("  1. Open a terminal in any folder (cd there)")
        print("  2. Type:  {}".format(name))
        print("Problems? Run  tidymate doctor")
    return 0


def uninstall(name=DEFAULT_NAME):
    found = False
    for cmd in {name, ALIAS_NAME}:
        for shim in find_shims(cmd):
            shim.unlink()
            found = True
            print("[ok] Removed {}".format(shim))
    if not found:
        print("The commands '{}' / '{}' were not set up.".format(name, ALIAS_NAME))
    if os.name == "nt":
        own = windows_bin_dir()
        try:
            if own.is_dir() and not any(own.iterdir()):
                own.rmdir()
            if not own.exists() and edit_user_path(own, add=False):
                print("[ok] Removed {} from your PATH".format(own))
        except OSError:
            pass
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Make the 'tidymate' and 'start_here' commands work in any terminal.")
    parser.add_argument("--name", default=DEFAULT_NAME, help="command name (default tidymate)")
    parser.add_argument("--uninstall", action="store_true", help="remove the launchers")
    parser.add_argument("--check", action="store_true", help="test the command and explain problems")
    args = parser.parse_args(argv)
    if not args.name.replace("_", "").replace("-", "").isalnum():
        print("Please use only letters, numbers, - and _ in the command name.")
        return 2
    if args.uninstall:
        return uninstall(args.name)
    if args.check:
        return check(args.name)
    return install(args.name)


if __name__ == "__main__":
    sys.exit(main())

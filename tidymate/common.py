#!/usr/bin/env python3
"""
common.py - small helpers shared by every tool.

Sizes, safe file names, hidden-file checks and - most important - the UNDO LOG.
Every tool that moves or renames files writes a log into  <folder>/.organizer_logs/
and one shared undo can reverse the most recent change, whichever tool made it.
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

LOG_DIR_NAME = ".organizer_logs"
LOG_TOOLS = ("organize", "easy", "rename", "archive", "migrate", "dupes")


# --------------------------------------------------------------------------- #
#  Small helpers
# --------------------------------------------------------------------------- #
def human_size(num_bytes):
    """1536 -> '1.5 KB'"""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return "{:.0f} B".format(value) if unit == "B" else "{:.1f} {}".format(value, unit)
        value /= 1024


def is_hidden(path):
    """Hidden on Linux/Mac (leading dot) or hidden/system on Windows."""
    path = Path(path)
    if path.name.startswith("."):
        return True
    try:
        attrs = getattr(path.stat(), "st_file_attributes", 0)      # Windows only
        return bool(attrs & 0x2 or attrs & 0x4)
    except OSError:
        return False


def is_drive_root(path):
    path = Path(path).resolve()
    return path == Path(path.anchor) or path == path.parent


def clean_path(text):
    """Accept pasted paths: removes ONE matching pair of surrounding quotes, expands ~ and %VARS%.

    A path that already exists is returned untouched, so folders whose real names contain
    quotes, apostrophes, $ or % (for example  D:\\Advitya 26'  ) are never changed.
    """
    text = str(text).strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1].strip()
    if os.path.exists(text):
        return Path(text)
    return Path(os.path.expandvars(os.path.expanduser(text)))


def unique_path(path):
    """name.ext -> name (1).ext -> name (2).ext ... so nothing is ever overwritten."""
    path = Path(path)
    if not path.exists():
        return path
    n = 1
    while True:
        candidate = path.with_name("{} ({}){}".format(path.stem, n, path.suffix))
        if not candidate.exists():
            return candidate
        n += 1


def confirm(question, default=False):
    hint = "[Y/n]" if default else "[y/N]"
    try:
        raw = input("{} {} ".format(question, hint)).strip().lower()
    except EOFError:
        return False
    if raw == "":
        return default
    return raw in ("y", "yes")


def check_folder(folder):
    """Return an error message if the folder is not safe to work on, else None."""
    folder = Path(folder)
    if not folder.is_dir():
        return "'{}' is not a folder.".format(folder)
    if is_drive_root(folder):
        return "For safety I won't work on the top of a drive ({}).".format(folder)
    return None


def tick(ui, i, total, label=""):
    """Progress bar that doesn't flood a log file with thousands of lines."""
    if ui.animate or i == total or i % 25 == 0:
        ui.progress(i, total, label)


# --------------------------------------------------------------------------- #
#  Undo logs
# --------------------------------------------------------------------------- #
def write_log(folder, tool, moves, created_dirs=()):
    """moves = [{'from': old_path, 'to': new_path}, ...]  -> path of the log file."""
    folder = Path(folder)
    log_dir = folder / LOG_DIR_NAME
    log_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    path = log_dir / "{}_{}.json".format(tool, stamp)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"tool": tool, "folder": str(folder),
                   "created_dirs": list(created_dirs), "moves": moves}, fh, indent=2)
    return path


def list_logs(folder):
    """All undo logs for a folder, oldest first (already-undone ones are ignored)."""
    log_dir = Path(folder) / LOG_DIR_NAME
    if not log_dir.is_dir():
        return []
    logs = [p for p in log_dir.glob("*.json")
            if not p.name.endswith(".undone.json") and p.name.split("_", 1)[0] in LOG_TOOLS]
    return sorted(logs, key=lambda p: p.name.split("_", 1)[1])


def latest_log(folder):
    logs = list_logs(folder)
    return logs[-1] if logs else None


def read_log(log_path):
    with open(log_path, encoding="utf-8") as fh:
        return json.load(fh)


def undo_log(log_path, progress=None):
    """Reverse one log. Returns (restored, missing). progress(i, total, label) is optional."""
    log_path = Path(log_path)
    data = read_log(log_path)
    folder = Path(data["folder"])
    moves = data.get("moves", [])
    restored = missing = 0
    for i, item in enumerate(reversed(moves), 1):
        src, dest = Path(item["to"]), Path(item["from"])
        if progress:
            progress(i - 1, len(moves), src.name)
        if not src.exists():
            missing += 1
            continue
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(unique_path(dest)))
            restored += 1
        except OSError:
            missing += 1
    if progress:
        progress(len(moves), len(moves), "done")
    for name in reversed(data.get("created_dirs", [])):      # remove folders we made, if empty
        try:
            (folder / name).rmdir()
        except OSError:
            pass
    log_path.rename(log_path.with_name(log_path.stem + ".undone.json"))
    return restored, missing

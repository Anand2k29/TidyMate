#!/usr/bin/env python3
"""
smart_organizer.py - the power-user command-line organizer.

    tidymate tidy FOLDER --dry-run     preview, nothing moves
    tidymate tidy FOLDER               do it (asks first)
    tidymate undo FOLDER        put everything back

New to this?  Run  start_here  (or  tidymate ) instead - it asks simple questions.
"""
import argparse
import copy
import filecmp
import fnmatch
import json
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

from tidymate import common  # noqa: E402

USER_DIR = Path.home() / ".tidymate"
USER_CONFIG_PATH = USER_DIR / "categories.json"      # created by:  tidymate config

DEFAULT_CONFIG = {
    "other_folder": "Other",
    "categories": {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico",
                   ".heic", ".tif", ".tiff", ".avif"],
        "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".flv", ".m4v"],
        "Audio": [".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".wma"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md", ".epub", ".pkpass"],
        "Spreadsheets": [".xls", ".xlsx", ".xlsm", ".csv", ".tsv", ".ods"],
        "Presentations": [".ppt", ".pptx", ".odp"],
        "Code": [".py", ".ipynb", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".java",
                 ".c", ".cpp", ".h", ".cs", ".go", ".rs", ".php", ".rb", ".sh", ".bat",
                 ".ps1", ".sql", ".vsix"],
        "Data": [".json", ".xml", ".yaml", ".yml", ".pkl", ".parquet", ".db", ".sqlite",
                 ".h5", ".npy", ".npz", ".log", ".winmd"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".whl"],
        "Installers": [".exe", ".msi", ".msix", ".appx", ".dmg", ".pkg", ".apk", ".deb",
                       ".rpm", ".iso"],
        "Design_3D": [".glb", ".gltf", ".stl", ".obj", ".fbx", ".blend", ".psd", ".ai",
                      ".fig", ".xd", ".dwg"],
        "Certificates_Keys": [".pem", ".crt", ".cer", ".pfx", ".p12", ".ppk"],
        "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
        "Shortcuts": [".lnk", ".url"],
    },
    "skip_extensions": [".crdownload", ".part", ".partial", ".download", ".opdownload",
                        ".aria2", ".tmp", ".temp"],
    "skip_names": ["desktop.ini", "thumbs.db", ".ds_store", "ntuser.dat", "ntuser.dat.log",
                   "iconcache.db"],
}

MODES = ("category", "extension", "date", "category-date")


# --------------------------------------------------------------------------- #
#  Config and planning
# --------------------------------------------------------------------------- #
def load_config(path=None):
    """Built-in defaults, overridden by your own file (~/.tidymate/categories.json,
    create it with  tidymate config ) or by --config FILE."""
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    candidate = Path(path) if path else USER_CONFIG_PATH
    if path or candidate.exists():
        with open(candidate, encoding="utf-8") as fh:
            cfg.update(json.load(fh))
    return cfg


def category_for(ext, cfg):
    ext = ext.lower()
    for category, exts in cfg["categories"].items():
        if ext in (e.lower() for e in exts):
            return category
    return cfg.get("other_folder", "Other")


def free_path(path, taken):
    """First name that doesn't exist on disk and isn't already planned this run."""
    candidate, n = Path(path), 1
    while candidate.exists() or candidate in taken:
        candidate = Path(path).with_name("{} ({}){}".format(Path(path).stem, n, Path(path).suffix))
        n += 1
    return candidate


def _same_content(a, b):
    try:
        return filecmp.cmp(str(a), str(b), shallow=False)
    except OSError:
        return False


def target_dir(path, ext, category, mode):
    if mode == "category":
        return category
    if mode == "extension":
        return ext.lstrip(".").upper()
    when = datetime.fromtimestamp(path.stat().st_mtime)
    if mode == "date":
        return "{:%Y}/{:%Y-%m}".format(when, when)
    return "{}/{:%Y-%m}".format(category, when)                     # category-date


def build_plan(folder, cfg, mode="category", min_age=5, excludes=(), include_hidden=False,
               dedupe=False, now=None):
    """Return (plan, skipped). plan = [(source Path, destination Path)]."""
    folder = Path(folder)
    now = time.time() if now is None else now
    skip_ext = {e.lower() for e in cfg.get("skip_extensions", [])}
    skip_names = {n.lower() for n in cfg.get("skip_names", [])}
    me = Path(__file__).resolve()
    plan, skipped, taken = [], Counter(), set()
    for path in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        try:
            if path.is_dir():
                continue                                       # your folders are never touched
            ext = path.suffix.lower()
            if path.resolve() == me:
                skipped["this script"] += 1
            elif path.name.lower() in skip_names:
                skipped["system file"] += 1
            elif not include_hidden and common.is_hidden(path):
                skipped["hidden/system file"] += 1
            elif ext in skip_ext:
                skipped["unfinished download"] += 1
            elif not ext:
                skipped["no extension"] += 1
            elif any(fnmatch.fnmatch(path.name.lower(), pat.lower()) for pat in excludes):
                skipped["excluded by --exclude"] += 1
            elif min_age and now - path.stat().st_mtime < min_age * 60:
                skipped["modified very recently"] += 1
            else:
                rel = target_dir(path, ext, category_for(ext, cfg), mode)
                dest = folder / rel / path.name
                if dest.exists() or dest in taken:
                    if dedupe and dest.exists() and _same_content(path, dest):
                        dest = free_path(folder / "_Duplicates" / path.name, taken)
                    else:
                        dest = free_path(dest, taken)
                taken.add(dest)
                plan.append((path, dest))
        except OSError:
            skipped["unreadable"] += 1
    return plan, skipped


def ensure_dir(folder, directory, created):
    """mkdir -p, remembering which folders WE created (so undo can remove them)."""
    folder, current = Path(folder), Path(folder)
    for part in Path(directory).relative_to(folder).parts:
        current = current / part
        if not current.exists():
            current.mkdir()
            created.append(str(current.relative_to(folder)))


def execute(folder, plan, progress=None, tool="organize"):
    """Move the files and write the undo log. Returns (moves, failed, log_path)."""
    import shutil
    folder = Path(folder)
    moves, failed, created = [], [], []
    for i, (src, dest) in enumerate(plan, 1):
        if progress:
            progress(i - 1, len(plan), src.name)
        try:
            ensure_dir(folder, dest.parent, created)
            shutil.move(str(src), str(dest))
            moves.append({"from": str(src), "to": str(dest)})
        except OSError as err:
            failed.append((src.name, str(err)))
    if progress:
        progress(len(plan), len(plan), "done")
    log = common.write_log(folder, tool, moves, created) if moves else None
    return moves, failed, log


# --------------------------------------------------------------------------- #
#  Command line
# --------------------------------------------------------------------------- #
def summarize(folder, plan, skipped):
    groups = Counter()
    for src, dest in plan:
        groups[dest.relative_to(folder).parts[0]] += 1
    print("Folder: {}".format(folder))
    print("Plan ({} file(s)):".format(len(plan)))
    for name in sorted(groups):
        print("  {:<30}  {} file(s)".format(name + "/", groups[name]))
    if skipped:
        print("Skipped: " + ", ".join("{} x {}".format(n, why) for why, n in skipped.items()))


def run_undo(folder, args):
    log = Path(args.undo_log) if args.undo_log else common.latest_log(folder)
    if not log or not Path(log).exists():
        print("Nothing to undo in {}".format(folder))
        return 0
    count = len(common.read_log(log).get("moves", []))
    print("Undo: {} ({} file(s))".format(Path(log).name, count))
    if not args.yes and not common.confirm("Put these {} file(s) back?".format(count)):
        print("Cancelled.")
        return 0
    restored, missing = common.undo_log(log)
    print("Restored {} file(s).".format(restored))
    if missing:
        print("{} file(s) were missing (moved or deleted since).".format(missing))
    return 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(
        description="Tidy a folder safely: preview, never overwrite, undo. "
                    "New to this? Run easy_organizer.py instead.")
    parser.add_argument("folder", nargs="?", help="the folder to organize")
    parser.add_argument("--dry-run", action="store_true", help="show the plan, change nothing")
    parser.add_argument("-y", "--yes", action="store_true", help="don't ask for confirmation")
    parser.add_argument("--mode", choices=MODES, default="category")
    parser.add_argument("--min-age", type=int, default=5, metavar="MINUTES",
                        help="skip files modified in the last N minutes (default 5, 0 = off)")
    parser.add_argument("--dedupe", action="store_true",
                        help="exact copies go to _Duplicates/ instead of 'name (1).ext'")
    parser.add_argument("--exclude", action="append", default=[], metavar="PATTERN",
                        help='leave matching files alone, e.g. --exclude "*.psd" (repeatable)')
    parser.add_argument("--include-hidden", action="store_true", help="also move hidden files")
    parser.add_argument("--config", metavar="FILE", help="your own categories JSON")
    parser.add_argument("--undo", action="store_true", help="reverse the last run")
    parser.add_argument("--undo-log", metavar="FILE", help="reverse a specific run")
    args = parser.parse_args(argv)

    if not args.folder:
        parser.print_help()
        print("\nTip: for a guided version with menus, run  start_here")
        return 2
    folder = common.clean_path(args.folder)
    problem = common.check_folder(folder)
    if problem:
        print("Error: " + problem)
        return 2
    folder = folder.resolve()

    if args.undo or args.undo_log:
        return run_undo(folder, args)

    try:
        cfg = load_config(args.config)
    except (OSError, ValueError) as err:
        print("Error: could not read the config file: {}".format(err))
        return 2
    plan, skipped = build_plan(folder, cfg, args.mode, args.min_age, args.exclude,
                               args.include_hidden, args.dedupe)
    if not plan:
        print("Folder: {}\nNothing to move.".format(folder))
        if skipped:
            print("Skipped: " + ", ".join("{} x {}".format(n, w) for w, n in skipped.items()))
        return 0
    summarize(folder, plan, skipped)
    if args.dry_run:
        print()
        for src, dest in plan:
            print("  {}  ->  {}".format(src.name, dest.relative_to(folder)))
        print("\nDry run - nothing was moved.")
        return 0
    print()
    if not args.yes and not common.confirm("Move these {} file(s)?".format(len(plan))):
        print("Cancelled. Nothing was moved.")
        return 0
    moves, failed, log = execute(folder, plan)
    print("Moved {} file(s).".format(len(moves)))
    for name, err in failed:
        print("  Could not move {}: {}".format(name, err))
    if log:
        print("Undo anytime with:  tidymate undo \"{}\"".format(folder))
    return 0


if __name__ == "__main__":
    sys.exit(main())

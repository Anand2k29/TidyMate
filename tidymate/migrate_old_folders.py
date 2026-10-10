#!/usr/bin/env python3
"""
migrate_old_folders.py - turn the old ".txt / .mp4 / .ipynb ..." folders into tidy
category folders (Documents/, Videos/, Code/ ...).

Only folders named exactly like an extension AND containing only files of that
extension are converted. ".git", ".vscode", ".ipynb_checkpoints" and your own
folders are left alone. Unfinished downloads (.crdownload) go back to the main folder.

    tidymate migrate FOLDER --dry-run
    tidymate migrate FOLDER
Undo with:  tidymate undo FOLDER
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
from tidymate import common            # noqa: E402
from tidymate import smart_organizer   # noqa: E402

OLD_FOLDER = re.compile(r"^\.[A-Za-z0-9]{1,10}$")


def find_candidates(folder):
    """Old-style folders that are safe to convert: [(folder_path, [files])]."""
    found = []
    for item in sorted(Path(folder).iterdir(), key=lambda p: p.name.lower()):
        if not item.is_dir() or not OLD_FOLDER.match(item.name):
            continue
        try:
            files = list(item.iterdir())
        except OSError:
            continue
        ext = item.name.lower()
        if files and all(f.is_file() and f.suffix.lower() == ext for f in files):
            found.append((item, files))
    return found


def build_plan(folder, cfg):
    skip_ext = {e.lower() for e in cfg.get("skip_extensions", [])}
    plan, taken = [], set()
    for old, files in find_candidates(folder):
        for f in sorted(files, key=lambda p: p.name.lower()):
            ext = f.suffix.lower()
            if ext in skip_ext:
                dest = Path(folder) / f.name                       # back to the main folder
            else:
                dest = Path(folder) / smart_organizer.category_for(ext, cfg) / f.name
            dest = smart_organizer.free_path(dest, taken)
            taken.add(dest)
            plan.append((f, dest))
    return plan


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("folder")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true")
    parser.add_argument("--config", metavar="FILE")
    args = parser.parse_args(argv)

    folder = common.clean_path(args.folder)
    problem = common.check_folder(folder)
    if problem:
        print("Error: " + problem)
        return 2
    folder = folder.resolve()
    cfg = smart_organizer.load_config(args.config)

    candidates = find_candidates(folder)
    if not candidates:
        print("No old-style folders (.txt, .mp4 ...) found in {}".format(folder))
        return 0
    plan = build_plan(folder, cfg)
    print("Old folders found:")
    for old, files in candidates:
        print("  {:<14} {} file(s)".format(old.name + "/", len(files)))
    print("\nPlan:")
    for src, dest in plan:
        print("  {}/{}  ->  {}".format(src.parent.name, src.name, dest.relative_to(folder)))
    if args.dry_run:
        print("\nDry run - nothing was moved.")
        return 0
    if not args.yes and not common.confirm("\nConvert {} file(s)?".format(len(plan))):
        print("Cancelled. Nothing was moved.")
        return 0

    moves, failed, log = smart_organizer.execute(folder, plan, tool="migrate")
    for old, _ in candidates:                                      # remove folders we emptied
        try:
            old.rmdir()
        except OSError:
            pass
    print("Moved {} file(s).".format(len(moves)))
    for name, err in failed:
        print("  Could not move {}: {}".format(name, err))
    if log:
        print("Undo anytime with:  tidymate undo \"{}\"".format(folder))
    return 0


if __name__ == "__main__":
    sys.exit(main())

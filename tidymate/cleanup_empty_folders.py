#!/usr/bin/env python3
"""
cleanup_empty_folders.py - remove folders that contain nothing at all.

    tidymate empty FOLDER --dry-run     just list them
    tidymate empty FOLDER               list them, ask, then remove

A folder that only contains other empty folders counts as empty too. Hidden folders
(.git ...) and the undo history (.organizer_logs) are never touched. Only EMPTY folders
are removed - no file is ever deleted.
"""
import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
from tidymate import common        # noqa: E402
from tidymate.ui import UI    # noqa: E402


def find_empty(folder):
    """Return empty folders, deepest first, so removing them in order works."""
    empty = set()
    ordered = []
    for root, dirs, files in os.walk(folder, topdown=False):
        root_path = Path(root)
        if root_path == Path(folder) or root_path.name.startswith("."):
            continue
        if files:
            continue
        children = [Path(root, d) for d in dirs]
        if all(c in empty for c in children):
            empty.add(root_path)
            ordered.append(root_path)
    return ordered


def main(argv=None):
    parser = argparse.ArgumentParser(description="Remove empty folders.")
    parser.add_argument("folder")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true")
    args = parser.parse_args(argv)

    ui = UI()
    folder = common.clean_path(args.folder)
    problem = common.check_folder(folder)
    if problem:
        ui.error(problem)
        return 2
    folder = folder.resolve()

    with ui.spinner("Looking for empty folders"):
        empty = find_empty(folder)
    if not empty:
        ui.ok("No empty folders. Nice and tidy!")
        return 0
    ui.heading("{} empty folder(s)".format(len(empty)))
    for path in empty[:40]:
        ui.say("  " + str(path.relative_to(folder)))
    if len(empty) > 40:
        ui.say("  ... and {} more".format(len(empty) - 40))
    if args.dry_run:
        ui.info("Dry run - nothing was removed.")
        return 0
    if not args.yes and not common.confirm("\nRemove these {} empty folder(s)?".format(len(empty))):
        ui.ok("Cancelled. Nothing was removed.")
        return 0
    removed = 0
    for i, path in enumerate(empty, 1):
        common.tick(ui, i, len(empty), path.name)
        try:
            path.rmdir()                       # rmdir refuses non-empty folders: extra safety
            removed += 1
        except OSError:
            pass
    ui.end_progress()
    ui.celebrate("Removed {} empty folder(s)".format(removed))
    return 0


if __name__ == "__main__":
    sys.exit(main())

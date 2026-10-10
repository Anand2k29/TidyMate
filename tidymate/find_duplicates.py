#!/usr/bin/env python3
"""
find_duplicates.py - find files that are exact copies of each other.

    tidymate dupes FOLDER                      report only (changes nothing)
    tidymate dupes FOLDER --min-size 100       ignore files smaller than 100 KB
    tidymate dupes FOLDER --move-to DUPES      move the EXTRA copies to DUPES

It NEVER deletes anything. With --move-to the extra copies are moved (the oldest copy
stays where it is) and a JSON file in the destination lists where each file came from.
Undo with:  tidymate undo FOLDER
"""
import argparse
import hashlib
import json
import os
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
from tidymate import common        # noqa: E402
from tidymate.ui import UI    # noqa: E402


def file_hash(path, chunk=1024 * 1024):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def iter_files(folder, min_size=0, skip_dirs=()):
    skip = {Path(d).resolve() for d in skip_dirs}
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs
                   if not d.startswith(".") and Path(root, d).resolve() not in skip]
        for name in files:
            path = Path(root, name)
            try:
                if path.is_symlink():
                    continue
                size = path.stat().st_size
            except OSError:
                continue
            if size >= min_size and size > 0:
                yield path, size


def find_groups(folder, min_size=0, skip_dirs=(), progress=None):
    """Return [[keeper, extra, extra...], ...] - each list is one set of identical files."""
    by_size = defaultdict(list)
    for path, size in iter_files(folder, min_size, skip_dirs):
        by_size[size].append(path)
    candidates = [p for paths in by_size.values() if len(paths) > 1 for p in paths]
    by_hash = defaultdict(list)
    for i, path in enumerate(candidates, 1):
        if progress:
            progress(i, len(candidates), path.name)
        try:
            by_hash[(path.stat().st_size, file_hash(path))].append(path)
        except OSError:
            pass
    groups = []
    for paths in by_hash.values():
        if len(paths) > 1:
            paths.sort(key=lambda p: (p.stat().st_mtime, len(str(p)), str(p)))   # oldest = keeper
            groups.append(paths)
    groups.sort(key=lambda g: -g[0].stat().st_size * (len(g) - 1))
    return groups


def move_extras(folder, groups, dest, progress=None):
    """Move every non-keeper to dest. Returns the list of moves."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    extras = [(g[0], p) for g in groups for p in g[1:]]
    moves = []
    for i, (kept, path) in enumerate(extras, 1):
        if progress:
            progress(i - 1, len(extras), path.name)
        target = common.unique_path(dest / path.name)
        try:
            shutil.move(str(path), str(target))
            moves.append({"from": str(path), "to": str(target), "kept": str(kept)})
        except OSError:
            pass
    if progress:
        progress(len(extras), len(extras), "done")
    if moves:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(dest / "duplicates_moved_{}.json".format(stamp), "w", encoding="utf-8") as fh:
            json.dump(moves, fh, indent=2)
        common.write_log(folder, "dupes", [{"from": m["from"], "to": m["to"]} for m in moves])
    return moves


def main(argv=None):
    parser = argparse.ArgumentParser(description="Find exact duplicate files (never deletes).")
    parser.add_argument("folder")
    parser.add_argument("--min-size", type=int, default=0, metavar="KB",
                        help="ignore files smaller than this many KB")
    parser.add_argument("--move-to", metavar="DIR", help="move the extra copies here")
    parser.add_argument("-y", "--yes", action="store_true")
    args = parser.parse_args(argv)

    ui = UI()
    folder = common.clean_path(args.folder)
    problem = common.check_folder(folder)
    if problem:
        ui.error(problem)
        return 2
    folder = folder.resolve()
    dest = common.clean_path(args.move_to).resolve() if args.move_to else None

    with ui.spinner("Comparing files (this can take a while for big folders)"):
        groups = find_groups(folder, args.min_size * 1024, skip_dirs=[dest] if dest else [])
    if not groups:
        ui.ok("No duplicates found.")
        return 0

    wasted = sum(g[0].stat().st_size * (len(g) - 1) for g in groups)
    ui.heading("{} set(s) of duplicates - {} could be freed".format(
        len(groups), common.human_size(wasted)))
    for n, group in enumerate(groups[:25], 1):
        ui.say("  {}. {} each, {} copies".format(n, common.human_size(group[0].stat().st_size),
                                               len(group)))
        for i, path in enumerate(group):
            tag = ui.c("keep ", "green") if i == 0 else ui.c("extra", "yellow")
            ui.say("       {}  {}".format(tag, path))
    if len(groups) > 25:
        ui.say("  ... and {} more set(s)".format(len(groups) - 25))

    if not dest:
        ui.info("Report only - nothing was changed.")
        ui.info("To move the extras aside, add:  --move-to \"SOME_FOLDER\"")
        return 0
    extras = sum(len(g) - 1 for g in groups)
    if not args.yes and not common.confirm(
            "\nMove {} extra copies to {}?".format(extras, dest)):
        ui.ok("Cancelled. Nothing was moved.")
        return 0
    moves = move_extras(folder, groups, dest, lambda i, t, l: common.tick(ui, i, t, l))
    ui.end_progress()
    ui.celebrate("Moved {} extra file(s) to {}".format(len(moves), dest))
    ui.info("Nothing was deleted - look through them, then delete what you don't need.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

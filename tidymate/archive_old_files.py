#!/usr/bin/env python3
"""
archive_old_files.py - put away files you haven't touched for a long time.

    tidymate archive FOLDER                  files older than 365 days
    tidymate archive FOLDER --days 90        older than 90 days
    tidymate archive FOLDER --dry-run        just show them

Old files are MOVED (never deleted) into  FOLDER/_Old/<year>/  where <year> is the
year the file was last changed. Only loose files are looked at. Undo with:
    tidymate undo FOLDER
"""
import argparse
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
from tidymate import common            # noqa: E402
from tidymate import smart_organizer   # noqa: E402
from tidymate.ui import UI        # noqa: E402

ARCHIVE_DIR = "_Old"


def build_plan(folder, days, cfg=None, now=None):
    """[(source, destination)] for loose files not modified for `days` days."""
    folder = Path(folder)
    cfg = cfg or smart_organizer.load_config()
    now = time.time() if now is None else now
    skip_ext = {e.lower() for e in cfg.get("skip_extensions", [])}
    skip_names = {n.lower() for n in cfg.get("skip_names", [])}
    cutoff = now - days * 86400
    plan, taken = [], set()
    for path in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        try:
            if (not path.is_file() or common.is_hidden(path) or path.suffix.lower() in skip_ext
                    or path.name.lower() in skip_names):
                continue
            mtime = path.stat().st_mtime
            if mtime >= cutoff:
                continue
        except OSError:
            continue
        year = datetime.fromtimestamp(mtime).year
        dest = smart_organizer.free_path(folder / ARCHIVE_DIR / str(year) / path.name, taken)
        taken.add(dest)
        plan.append((path, dest))
    return plan


def main(argv=None):
    parser = argparse.ArgumentParser(description="Move old, untouched files into _Old/<year>/.")
    parser.add_argument("folder")
    parser.add_argument("--days", type=int, default=365, help="age in days (default 365)")
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

    with ui.spinner("Looking for files older than {} days".format(args.days)):
        plan = build_plan(folder, args.days)
    if not plan:
        ui.ok("No files older than {} days. Nothing to archive.".format(args.days))
        return 0
    per_year = Counter(dest.parent.name for _, dest in plan)
    size = sum(src.stat().st_size for src, _ in plan)
    ui.heading("{} old file(s), {} in total".format(len(plan), common.human_size(size)))
    for year in sorted(per_year):
        ui.say("  {}/{}/   {} file(s)".format(ARCHIVE_DIR, year, per_year[year]))
    if args.dry_run:
        for src, dest in plan[:30]:
            ui.say("    {}".format(src.name))
        ui.info("Dry run - nothing was moved.")
        return 0
    if not args.yes and not common.confirm("\nMove these {} file(s) into {}/ ?".format(
            len(plan), ARCHIVE_DIR)):
        ui.ok("Cancelled. Nothing was moved.")
        return 0
    moves, failed, log = smart_organizer.execute(
        folder, plan, lambda i, t, l: common.tick(ui, i, t, l), tool="archive")
    ui.end_progress()
    ui.celebrate("Archived {} file(s)".format(len(moves)))
    for name, err in failed:
        ui.warn("Could not move {}: {}".format(name, err))
    ui.info("Nothing was deleted. Undo anytime from the toolbox.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

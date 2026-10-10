#!/usr/bin/env python3
"""
disk_report.py - "What is using my disk space?"  (read-only, changes nothing)

    tidymate disk FOLDER
    tidymate disk FOLDER --top 15 --stale-days 365

Shows: total size, space per category (with bars), the biggest files, and files you
haven't touched for a long time.
"""
import argparse
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
from tidymate import common            # noqa: E402
from tidymate import smart_organizer   # noqa: E402
from tidymate.ui import UI        # noqa: E402


def scan(folder):
    """[(path, size, mtime)] for every file below folder."""
    out = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d != common.LOG_DIR_NAME]
        for name in files:
            path = os.path.join(root, name)
            try:
                if os.path.islink(path):
                    continue
                st = os.stat(path)
                out.append((path, st.st_size, st.st_mtime))
            except OSError:
                pass
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description="What is using my disk space?")
    parser.add_argument("folder")
    parser.add_argument("--top", type=int, default=10, help="how many big files to list")
    parser.add_argument("--stale-days", type=int, default=365,
                        help="files not changed for this many days count as stale")
    args = parser.parse_args(argv)

    ui = UI()
    folder = common.clean_path(args.folder)
    if not folder.is_dir():
        ui.error("'{}' is not a folder.".format(folder))
        return 2
    folder = folder.resolve()
    cfg = smart_organizer.load_config()

    with ui.spinner("Measuring your files"):
        files = scan(folder)
    if not files:
        ui.info("No files found.")
        return 0

    total = sum(size for _, size, _ in files)
    ui.heading("Disk report: {}".format(folder))
    ui.say("  {} file(s), {} in total".format(len(files), common.human_size(total)))

    sizes, counts = defaultdict(int), defaultdict(int)
    for path, size, _ in files:
        ext = Path(path).suffix.lower()
        key = smart_organizer.category_for(ext, cfg) if ext else "(no extension)"
        sizes[key] += size
        counts[key] += 1
    ui.say()
    ui.say("  " + ui.c("By category", "bold", "cyan"))
    biggest = max(sizes.values()) or 1
    for key in sorted(sizes, key=lambda k: -sizes[k]):
        bar = "#" * max(1, int(28 * sizes[key] / biggest)) if sizes[key] else ""
        ui.say("    {:<18} {:>9}  {:>5} files  {}".format(
            key, common.human_size(sizes[key]), counts[key], ui.c(bar, "green")))

    ui.say()
    ui.say("  " + ui.c("Biggest files", "bold", "cyan"))
    for path, size, _ in sorted(files, key=lambda f: -f[1])[:args.top]:
        ui.say("    {:>9}  {}".format(common.human_size(size), os.path.relpath(path, folder)))

    cutoff = time.time() - args.stale_days * 86400
    stale = [f for f in files if f[2] < cutoff]
    ui.say()
    ui.say("  " + ui.c("Not changed for {}+ days".format(args.stale_days), "bold", "cyan"))
    if stale:
        ui.say("    {} file(s), {} - candidates to archive or delete".format(
            len(stale), common.human_size(sum(f[1] for f in stale))))
        for path, size, _ in sorted(stale, key=lambda f: -f[1])[:5]:
            ui.say("    {:>9}  {}".format(common.human_size(size), os.path.relpath(path, folder)))
        ui.info("Tip: 'tidymate archive' can move them aside safely.")
    else:
        ui.say("    None - everything was used recently.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

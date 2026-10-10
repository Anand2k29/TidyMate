#!/usr/bin/env python3
"""
backup_folder.py - make a dated .zip backup of a folder.

    tidymate backup FOLDER                     zip is saved NEXT TO the folder
    tidymate backup FOLDER --dest D:\\Backups   or choose where it goes

Result:  Downloads_backup_20261009_153000.zip   (the original is not changed)
The zip is checked after it is written, so you know it is not broken.
"""
import argparse
import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
from tidymate import common        # noqa: E402
from tidymate.ui import UI    # noqa: E402


def list_files(folder, skip=None):
    out = []
    for root, dirs, files in os.walk(folder):
        for name in files:
            path = Path(root, name)
            if skip is not None and path.resolve() == skip:
                continue
            if not path.is_symlink():
                out.append(path)
    return out


def make_backup(folder, dest_dir, progress=None):
    """Create the zip. Returns (zip_path, file_count, bad_member_or_None)."""
    folder, dest_dir = Path(folder), Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = dest_dir / "{}_backup_{}.zip".format(folder.name or "drive", stamp)
    files = list_files(folder, skip=zip_path.resolve())
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, path in enumerate(files, 1):
            if progress:
                progress(i, len(files), path.name)
            try:
                zf.write(path, path.relative_to(folder))
            except OSError:
                pass                                   # unreadable file: skip, keep going
    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
    return zip_path, len(files), bad


def main(argv=None):
    parser = argparse.ArgumentParser(description="Make a dated zip backup of a folder.")
    parser.add_argument("folder")
    parser.add_argument("--dest", metavar="DIR", help="where to save the zip (default: next to the folder)")
    parser.add_argument("-y", "--yes", action="store_true")
    args = parser.parse_args(argv)

    ui = UI()
    folder = common.clean_path(args.folder)
    problem = common.check_folder(folder)
    if problem:
        ui.error(problem)
        return 2
    folder = folder.resolve()
    dest = common.clean_path(args.dest).resolve() if args.dest else folder.parent

    with ui.spinner("Measuring the folder"):
        files = list_files(folder)
        total = sum(p.stat().st_size for p in files if p.exists())
    ui.say("  {} file(s), {} to back up".format(len(files), common.human_size(total)))
    ui.say("  The zip will be saved in: {}".format(dest))
    if not args.yes and not common.confirm("\nStart the backup?", default=True):
        ui.ok("Cancelled.")
        return 0

    zip_path, count, bad = make_backup(folder, dest, lambda i, t, l: common.tick(ui, i, t, l))
    ui.end_progress()
    if bad:
        ui.error("The backup may be damaged (problem with {}). Try again.".format(bad))
        return 1
    ui.celebrate("Backup ready: {} ({})".format(zip_path.name,
                                               common.human_size(zip_path.stat().st_size)))
    ui.info("Saved at: {}".format(zip_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())

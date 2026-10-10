#!/usr/bin/env python3
"""
checksum_tool.py - check that files have not changed or been damaged.

A "checksum" is a fingerprint of a file. If even one byte changes, the fingerprint
changes. Take fingerprints now, compare later.

    tidymate checksum create FOLDER      save fingerprints to FOLDER/checksums.sha256
    tidymate checksum verify FOLDER      compare the files with the saved fingerprints

verify tells you which files are OK, CHANGED, MISSING or NEW.
Good for: backups, USB sticks, big downloads, files you send to someone.
"""
import argparse
import hashlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
from tidymate import common        # noqa: E402
from tidymate.ui import UI    # noqa: E402

MANIFEST = "checksums.sha256"


def file_hash(path, chunk=1024 * 1024):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def list_files(folder):
    """Relative paths (with /) of every file except the manifest and undo logs."""
    out = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d != common.LOG_DIR_NAME]
        for name in files:
            if name == MANIFEST and Path(root) == Path(folder):
                continue
            out.append(Path(root, name).relative_to(folder).as_posix())
    return sorted(out)


def read_manifest(folder):
    manifest = {}
    with open(Path(folder) / MANIFEST, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if len(line) > 66 and line[64:66] == "  ":
                manifest[line[66:]] = line[:64]
    return manifest


def cmd_create(ui, folder):
    files = list_files(folder)
    if not files:
        ui.info("No files to fingerprint.")
        return 0
    lines = []
    for i, rel in enumerate(files, 1):
        common.tick(ui, i, len(files), rel)
        try:
            lines.append("{}  {}".format(file_hash(Path(folder) / rel), rel))
        except OSError:
            ui.warn("Could not read {}".format(rel))
    ui.end_progress()
    with open(Path(folder) / MANIFEST, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    ui.celebrate("Saved {} fingerprint(s) to {}".format(len(lines), MANIFEST))
    ui.info("Later, run 'verify' to see if anything changed.")
    return 0


def cmd_verify(ui, folder):
    if not (Path(folder) / MANIFEST).exists():
        ui.error("No {} here yet. Run 'create' first.".format(MANIFEST))
        return 2
    manifest = read_manifest(folder)
    current = set(list_files(folder))
    ok, changed, missing = 0, [], []
    names = sorted(manifest)
    for i, rel in enumerate(names, 1):
        common.tick(ui, i, len(names), rel)
        path = Path(folder) / rel
        if rel not in current:
            missing.append(rel)
            continue
        try:
            if file_hash(path) == manifest[rel]:
                ok += 1
            else:
                changed.append(rel)
        except OSError:
            changed.append(rel)
    ui.end_progress()
    new = sorted(current - set(manifest))
    ui.say()
    ui.ok("{} file(s) are exactly as before (OK)".format(ok))
    for title, items, color in (("CHANGED", changed, "red"), ("MISSING", missing, "red"),
                                ("NEW (not in the saved list)", new, "yellow")):
        if items:
            ui.say("  " + ui.c("{} - {} file(s):".format(title, len(items)), color, "bold"))
            for rel in items[:20]:
                ui.say("      " + rel)
            if len(items) > 20:
                ui.say("      ... and {} more".format(len(items) - 20))
    if not (changed or missing):
        ui.celebrate("Nothing was changed or lost.")
        return 0
    ui.warn("Some files are different from when the fingerprints were saved.")
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="Create or verify file fingerprints (SHA-256).")
    parser.add_argument("action", choices=["create", "verify"])
    parser.add_argument("folder")
    args = parser.parse_args(argv)
    ui = UI()
    folder = common.clean_path(args.folder)
    if not folder.is_dir():
        ui.error("'{}' is not a folder.".format(folder))
        return 2
    folder = folder.resolve()
    return cmd_create(ui, folder) if args.action == "create" else cmd_verify(ui, folder)


if __name__ == "__main__":
    sys.exit(main())

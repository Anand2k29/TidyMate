#!/usr/bin/env python3
"""
folder_tree.py - draw a picture of a folder: what is inside, and how big each part is.
Read-only. Changes nothing.

    tidymate tree FOLDER
    tidymate tree FOLDER --depth 3        go deeper
    tidymate tree FOLDER --files          also list single files
    tidymate tree FOLDER --limit 20       show up to 20 items per folder

Example:
    Downloads/  (1.2 GB)
    |-- Videos/  (800.0 MB)
    |-- Documents/  (300.0 MB)
    `-- Images/  (100.0 MB)
"""
import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
from tidymate import common        # noqa: E402
from tidymate.ui import UI    # noqa: E402


def build(path, show_files):
    """Node = dict(name, dir, size, kids). Sizes always include everything below."""
    node = {"name": path.name or str(path), "dir": True, "size": 0, "kids": []}
    try:
        entries = list(os.scandir(path))
    except OSError:
        return node
    for entry in entries:
        try:
            if entry.is_symlink():
                continue
            if entry.is_dir():
                if entry.name == common.LOG_DIR_NAME:
                    continue
                child = build(Path(entry.path), show_files)
                node["size"] += child["size"]
                node["kids"].append(child)
            else:
                size = entry.stat().st_size
                node["size"] += size
                if show_files:
                    node["kids"].append({"name": entry.name, "dir": False, "size": size,
                                         "kids": []})
        except OSError:
            pass
    node["kids"].sort(key=lambda k: -k["size"])
    return node


def render(ui, node, depth, limit, prefix=""):
    kids = node["kids"]
    shown = kids[:limit]
    hidden = kids[limit:]
    for i, kid in enumerate(shown):
        last = i == len(shown) - 1 and not hidden
        branch = "`-- " if last else "|-- "
        name = kid["name"] + ("/" if kid["dir"] else "")
        label = ui.c(name, "bold", "cyan") if kid["dir"] else name
        ui.say("{}{}{}  ({})".format(prefix, branch, label, common.human_size(kid["size"])))
        if kid["dir"] and depth > 1:
            render(ui, kid, depth - 1, limit, prefix + ("    " if last else "|   "))
    if hidden:
        ui.say("{}`-- ... {} more ({})".format(prefix, len(hidden),
                                                common.human_size(sum(k["size"] for k in hidden))))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Show a folder as a tree with sizes.")
    parser.add_argument("folder")
    parser.add_argument("--depth", type=int, default=2, help="how many levels to show (default 2)")
    parser.add_argument("--files", action="store_true", help="also show single files")
    parser.add_argument("--limit", type=int, default=12, help="max items per folder (default 12)")
    args = parser.parse_args(argv)

    ui = UI()
    folder = common.clean_path(args.folder)
    if not folder.is_dir():
        ui.error("'{}' is not a folder.".format(folder))
        return 2
    folder = folder.resolve()
    with ui.spinner("Measuring your folders"):
        root = build(folder, args.files)
    ui.say()
    ui.say("{}  ({})".format(ui.c(root["name"] + "/", "bold", "cyan"),
                              common.human_size(root["size"])))
    render(ui, root, max(1, args.depth), max(1, args.limit))
    ui.say()
    ui.info("Biggest items are listed first. Use --depth 3 to look deeper.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

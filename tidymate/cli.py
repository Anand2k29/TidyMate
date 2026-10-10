#!/usr/bin/env python3
"""
TidyMate - tidy, rename, archive, back up and check your files safely.

Just type  tidymate  in any folder (the folder you are in is pre-selected).
`start_here` is the same command under a second name.

    tidymate                       open the friendly menu
    tidymate "D:\\Inbox"            open the menu using that folder
    tidymate tidy FOLDER           sort into Images/, Documents/ ...  (add --dry-run to preview)
    tidymate rename FOLDER --lower --spaces
    tidymate archive FOLDER --days 180
    tidymate dupes FOLDER          find duplicate files
    tidymate empty FOLDER          remove empty folders
    tidymate disk FOLDER           what is using my disk space?
    tidymate tree FOLDER           folder picture with sizes
    tidymate backup FOLDER         dated zip backup
    tidymate checksum create|verify FOLDER
    tidymate migrate FOLDER        fix old ".txt / .mp4" folders
    tidymate undo [FOLDER]         undo the last change (default: current folder)
    tidymate explain svg .jpeg     what do these file types mean?
    tidymate config                create/show the file where you can edit categories
    tidymate setup | doctor        make the command work in every terminal / diagnose it

FOLDER can be  .  (the folder you are standing in).
"""
import importlib
import os
import subprocess
import sys
from pathlib import Path

from tidymate import __version__

TOOLS = {
    "tidy": "smart_organizer",
    "rename": "rename_files",
    "archive": "archive_old_files",
    "dupes": "find_duplicates",
    "duplicates": "find_duplicates",
    "empty": "cleanup_empty_folders",
    "disk": "disk_report",
    "tree": "folder_tree",
    "backup": "backup_folder",
    "checksum": "checksum_tool",
    "migrate": "migrate_old_folders",
}


def _run_module(name, args):
    module = importlib.import_module("tidymate." + name)
    return module.main(args)


def _undo(args):
    folder = args[0] if args and not args[0].startswith("-") else "."
    rest = args[1:] if args and not args[0].startswith("-") else args
    return _run_module("smart_organizer", ["--undo"] + rest + ["--", folder])


def _explain(args):
    from tidymate import explain, smart_organizer
    if "--markdown" in args:
        print(explain.markdown_glossary())
        return 0
    if not args:
        print("Usage: tidymate explain svg .jpeg photo.HEIC")
        return 2
    cfg = smart_organizer.load_config()
    for text in args:
        ext = explain.normalise_ext(text)
        name, description = explain.describe_ext(ext)
        folder = explain.folder_for_ext(ext, cfg)
        print("{}  -  {}".format(ext, name))
        print("    " + description)
        if folder is None:
            print("    Never moved by the organizer.")
        else:
            print("    Goes in: {}/  ({})".format(folder, explain.describe_folder(folder)))
        print()
    return 0


def _config(args):
    import json
    from tidymate import smart_organizer as so
    path = so.USER_CONFIG_PATH
    if "--reset" in args or not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(so.DEFAULT_CONFIG, indent=2), encoding="utf-8")
        print("Created the default settings file.")
    print("Your categories file:  {}".format(path))
    print("Edit it with any text editor. Add or move file types between folders, e.g.")
    print('    "Ebooks": [".epub", ".mobi"]')
    print("Delete the file (or run: tidymate config --reset) to go back to the defaults.")
    if "--open" in args:
        try:
            if os.name == "nt":
                os.startfile(str(path))                              # noqa
            elif sys.platform == "darwin":
                subprocess.call(["open", str(path)])
            else:
                subprocess.call(["xdg-open", str(path)])
        except OSError:
            print("Could not open it automatically - open the file above yourself.")
    else:
        print("Tip: 'tidymate config --open' opens it in your default editor.")
    return 0


def _menu(args):
    """Open the menu. The folder you are standing in is pre-selected ("This folder")
    unless you gave a folder yourself."""
    from tidymate import toolbox
    args = list(args)
    if "--here" not in args and not any(not a.startswith("--") for a in args):
        args = ["--here"] + args
    toolbox.main(args)
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    if not argv:
        return _menu([])
    cmd, rest = argv[0], argv[1:]
    low = cmd.lower()
    if low in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    if low in ("-v", "--version", "version"):
        print("tidymate {}".format(__version__))
        return 0
    if low in ("menu", "here"):
        return _menu(rest)
    if low in TOOLS:
        return int(_run_module(TOOLS[low], rest) or 0)
    if low == "undo":
        return int(_undo(rest) or 0)
    if low in ("explain", "what"):
        return _explain(rest)
    if low == "config":
        return _config(rest)
    if low in ("setup", "install"):
        return int(_run_module("setup_command", rest) or 0)
    if low in ("unsetup", "uninstall", "remove"):
        return int(_run_module("setup_command", ["--uninstall"] + rest) or 0)
    if low in ("doctor", "check"):
        return int(_run_module("setup_command", ["--check"] + rest) or 0)
    if cmd in ("--plain", "--here") or Path(cmd).expanduser().is_dir():   # tidymate .  /  tidymate "D:\Inbox"
        return _menu(argv)
    print("Unknown command: {}\n".format(cmd))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())

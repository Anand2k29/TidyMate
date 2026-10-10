#!/usr/bin/env python3
"""
toolbox.py - ONE menu for every tool. Start here.

    tidymate                     works in ANY folder ("This folder" is pre-selected)
    start_here                   the same thing under a second name
    tidymate "D:\\Inbox"               the same menu, using that folder
    python -m tidymate   (if you only unzipped the project)

You never type options: pick a number, pick a folder, answer a simple question.
Every tool shows a preview and asks before it changes anything.
Add --plain for no colours/animations.
"""
import sys

if sys.version_info < (3, 8):
    print("This tool needs Python 3.8 or newer (you have {}).".format(sys.version.split()[0]))
    print("Please install a newer Python from https://www.python.org/downloads/")
    input("Press Enter to close...")
    sys.exit(1)

import traceback  # noqa: E402
from pathlib import Path  # noqa: E402

ERROR_FILE = Path.home() / ".tidymate" / "last_error.txt"

from tidymate import archive_old_files    # noqa: E402
from tidymate import backup_folder        # noqa: E402
from tidymate import checksum_tool        # noqa: E402
from tidymate import cleanup_empty_folders  # noqa: E402
from tidymate import disk_report          # noqa: E402
from tidymate import easy_organizer as eo  # noqa: E402
from tidymate import find_duplicates      # noqa: E402
from tidymate import folder_tree          # noqa: E402
from tidymate import rename_files         # noqa: E402
from tidymate.ui import UI           # noqa: E402


# --------------------------------------------------------------------------- #
#  One small function per menu entry
# --------------------------------------------------------------------------- #
def run_tidy(ui, cfg):
    eo.tidy_flow(ui, cfg)


def run_rename(ui, cfg):
    folder = eo.pick_folder(ui, "Which folder has the files you want to rename?")
    if folder is None:
        return
    ui.say()
    ui.say("  " + ui.c("What kind of renaming?", "bold"))
    choice = ui.choose([
        "Make names lowercase            (Photo.JPG -> photo.jpg)",
        "Replace spaces with _           (my file.txt -> my_file.txt)",
        "Remove odd characters           (a#b&c%.pdf -> abc.pdf)",
        "Put the file's date first       (scan.pdf -> 2026-10-09_scan.pdf)",
        "Number them                     (trip_001.jpg, trip_002.jpg ...)",
        "Add some text at the start      (Invoice_...)",
        "Replace some text in the names  (IMG -> Holiday)"], back="Go back")
    if choice is None:
        return
    if choice < 4:
        flags = [["--lower"], ["--spaces"], ["--clean"], ["--date-prefix"]][choice]
    elif choice == 4:
        flags = ["--number=" + (ui.ask("Base name, e.g. trip") or "file")]
    elif choice == 5:
        text = ui.ask("Text to add at the start, e.g. Invoice_")
        if not text:
            ui.warn("You didn't type anything, so nothing was changed.")
            return
        flags = ["--prefix=" + text]
    else:
        old = ui.ask("Text to find, e.g. IMG")
        if not old:
            ui.warn("You didn't type anything, so nothing was changed.")
            return
        flags = ["--find=" + old, "--replace-with=" + ui.ask("Replace it with (can be empty)")]
    ui.say()
    ui.info("Optional: only rename some files. Type an extension like  jpg  or a pattern like  IMG_*")
    ui.info("Press Enter to rename ALL files in the folder.")
    only = ui.ask("Only these files")
    if only:
        flags.append("--only=" + only)
    rename_files.main(flags + ["--", str(folder)])


def run_archive(ui, cfg):
    folder = eo.pick_folder(ui, "Which folder should I look through for old files?")
    if folder is None:
        return
    raw = ui.ask("How many days untouched counts as old? (Enter = 365)")
    days = int(raw) if raw.isdigit() and int(raw) > 0 else 365
    archive_old_files.main(["--days", str(days), "--", str(folder)])


def run_duplicates(ui, cfg):
    folder = eo.pick_folder(ui, "Which folder should I search for duplicate files?")
    if folder is None:
        return
    ui.say()
    choice = ui.choose(["Just show me the duplicates (changes nothing)",
                        "Show them AND move the extra copies into '_Duplicates_Review'"],
                       back="Go back")
    if choice is None:
        return
    argv = []
    if choice == 1:
        argv += ["--move-to", str(folder / "_Duplicates_Review")]
    find_duplicates.main(argv + ["--", str(folder)])


def run_empty(ui, cfg):
    folder = eo.pick_folder(ui, "Which folder should I look for empty folders in?")
    if folder:
        cleanup_empty_folders.main(["--", str(folder)])


def run_disk(ui, cfg):
    folder = eo.pick_folder(ui, "Which folder do you want a space report for?")
    if folder:
        disk_report.main(["--top", "10", "--", str(folder)])


def run_tree(ui, cfg):
    folder = eo.pick_folder(ui, "Which folder do you want to see as a tree?")
    if folder:
        folder_tree.main(["--depth", "2", "--", str(folder)])


def run_backup(ui, cfg):
    folder = eo.pick_folder(ui, "Which folder do you want to back up?")
    if folder:
        backup_folder.main(["--", str(folder)])


def run_checksum(ui, cfg):
    folder = eo.pick_folder(ui, "Which folder do you want to check?")
    if folder is None:
        return
    ui.say()
    choice = ui.choose(["Save fingerprints now (so I can check later)",
                        "Check the files against saved fingerprints"], back="Go back")
    if choice is not None:
        checksum_tool.main(["create" if choice == 0 else "verify", "--", str(folder)])


def run_undo(ui, cfg):
    eo.undo_flow(ui)


def run_lookup(ui, cfg):
    eo.lookup_flow(ui, cfg)


def run_learn(ui, cfg):
    eo.learn_flow(ui)


def run_migrate(ui, cfg):
    eo.migrate_flow(ui)


MENU = [
    ("Tidy a folder into category folders", "Images/, Documents/, Videos/ ...", run_tidy),
    ("Rename many files at once", "lowercase, numbers, dates ...", run_rename),
    ("Archive old files", "move untouched files into _Old/<year>", run_archive),
    ("Find duplicate files", "exact copies, nothing is deleted", run_duplicates),
    ("Remove empty folders", "only truly empty ones", run_empty),
    ("What is using my disk space?", "sizes, biggest files", run_disk),
    ("Show a folder as a tree", "what's inside, how big", run_tree),
    ("Back up a folder (zip)", "dated .zip, checked afterwards", run_backup),
    ("Check files weren't changed", "fingerprints (checksums)", run_checksum),
    ("Undo the last change", "works for every tool above", run_undo),
    ("What does a file type mean?", ".jpeg, .svg, .pdf ...", run_lookup),
    ("Learn the basics", "files, folders, preview, undo", run_learn),
    ("Fix old '.txt / .mp4' folders", "from the very first script", run_migrate),
]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    ui = UI(plain="--plain" in argv)
    cfg = eo.load_config()
    ui.banner()
    eo.apply_start_args(ui, argv)
    ui.say()
    ui.typewriter("  Welcome! Pick a number. Every tool shows a preview first -")
    ui.typewriter("  nothing changes until you say yes, and you can undo.")
    labels = ["{:<36} {}".format(name, ui.c(hint, "dim")) for name, hint, _ in MENU]
    try:
        while True:
            ui.heading("Toolbox - what would you like to do?")
            choice = ui.choose(labels, back="Exit")
            if choice is None:
                break
            try:
                MENU[choice][2](ui, cfg)
            except KeyboardInterrupt:
                ui.say()
                ui.warn("Stopped.")
            except (Exception, SystemExit) as err:           # never crash the window
                ui.say()
                ui.error("Sorry, something went wrong: {}".format(err))
                try:
                    ERROR_FILE.write_text(traceback.format_exc(), encoding="utf-8")
                    ui.info("Technical details were saved to: {}".format(ERROR_FILE))
                except OSError:
                    pass
                ui.info("Anything finished before the problem can be reversed with "
                        "'Undo the last change'.")
            ui.say()
            ui.pause()
    except (EOFError, KeyboardInterrupt):
        ui.say()
    ui.say()
    ui.ok("Bye! Your files are safe.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
easy_organizer.py - the GUIDED way to use TidyMate.

No options to remember. Just run it and answer the numbered questions:

    tidymate

It will:
  * let you pick a folder (Downloads, Desktop ... or paste a path),
  * show a PREVIEW that explains every folder and file type (.jpeg, .svg ...),
  * move files only after you say yes (with a progress bar),
  * let you UNDO the last tidy-up,
  * let you look up what any file type means.

Needs Python 3.8+. No extra packages.  Add --plain for no colours/animations.
"""
import sys

if sys.version_info < (3, 8):
    print("This tool needs Python 3.8 or newer. Get it from https://www.python.org/downloads/")
    sys.exit(1)

import copy  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import time  # noqa: E402
from collections import Counter, defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent

from tidymate import common                       # noqa: E402  (shared undo log + helpers)
from tidymate import explain                      # noqa: E402  (plain-English explanations)
from tidymate import smart_organizer              # noqa: E402  (defaults + config)
from tidymate import migrate_old_folders          # noqa: E402
from tidymate.ui import UI                   # noqa: E402  (colours, spinner, menus)

MIN_AGE_MINUTES = 5

# --------------------------------------------------------------------------- #
#  Config
# --------------------------------------------------------------------------- #
def load_config():
    """Built-in categories, or your own file (see: tidymate config)."""
    try:
        return smart_organizer.load_config()
    except (OSError, ValueError):
        return copy.deepcopy(smart_organizer.DEFAULT_CONFIG)


# --------------------------------------------------------------------------- #
#  Scanning and moving
# --------------------------------------------------------------------------- #
def is_hidden(path):
    if path.name.startswith("."):
        return True
    try:
        attrs = getattr(path.stat(), "st_file_attributes", 0)   # Windows only
        return bool(attrs & 0x2 or attrs & 0x4)                 # hidden or system
    except OSError:
        return False


def scan(folder, cfg):
    """Return (plan, skipped). plan = [(Path, category)], skipped = {reason: [Path]}."""
    skip_ext = {e.lower() for e in cfg["skip_extensions"]}
    skip_names = {n.lower() for n in cfg["skip_names"]}
    me = Path(__file__).resolve()
    now = time.time()
    plan, skipped = [], defaultdict(list)
    for path in sorted(folder.iterdir(), key=lambda p: p.name.lower()):
        try:
            if path.is_dir():
                continue                                  # your folders are never touched
            ext = path.suffix.lower()
            if path.resolve() == me:
                skipped["this script"].append(path)
            elif path.name.lower() in skip_names:
                skipped["system file"].append(path)
            elif is_hidden(path):
                skipped["hidden/system file"].append(path)
            elif ext in skip_ext:
                skipped["unfinished download"].append(path)
            elif not ext:
                skipped["no extension"].append(path)
            elif MIN_AGE_MINUTES and now - path.stat().st_mtime < MIN_AGE_MINUTES * 60:
                skipped["modified very recently"].append(path)
            else:
                category = explain.folder_for_ext(ext, cfg)
                if category:
                    plan.append((path, category))
        except OSError:
            skipped["unreadable"].append(path)
    return plan, skipped


def unique_path(path):
    """name.ext -> name (1).ext -> name (2).ext ... so nothing is ever overwritten."""
    if not path.exists():
        return path
    n = 1
    while True:
        candidate = path.with_name("{} ({}){}".format(path.stem, n, path.suffix))
        if not candidate.exists():
            return candidate
        n += 1


def do_moves(ui, folder, plan):
    """Move the files, show a progress bar, write an undo log. Returns (moved, failed)."""
    moves, failed, created = [], [], []
    total = len(plan)
    for i, (src, category) in enumerate(plan, 1):
        ui.progress(i - 1, total, src.name)
        try:
            target_dir = folder / category
            if not target_dir.exists():
                target_dir.mkdir()
                created.append(category)
            dest = unique_path(target_dir / src.name)
            shutil.move(str(src), str(dest))
            moves.append({"from": str(src), "to": str(dest)})
        except OSError as err:
            failed.append((src.name, str(err)))
        time.sleep(0.02 if ui.animate else 0)             # lets the bar be seen
    ui.progress(total, total, "done")
    ui.end_progress()
    if moves:
        common.write_log(folder, "easy", moves, created)
    return moves, failed


def latest_log(folder):
    """Most recent change that can be undone (from ANY tool in this project)."""
    return common.latest_log(folder)


def do_undo(ui, folder, log_path):
    restored, missing = common.undo_log(log_path, lambda i, t, label: ui.progress(i, t, label))
    ui.end_progress()
    return restored, missing


# --------------------------------------------------------------------------- #
#  Screens
# --------------------------------------------------------------------------- #
clean_path = common.clean_path          # keeps real folder names (even with ' or ") intact


def browse_for_folder(ui, title):
    """Open the normal 'choose a folder' window. Returns a Path or None."""
    try:
        import tkinter
        from tkinter import filedialog
        root = tkinter.Tk()
        root.withdraw()
        try:
            root.attributes("-topmost", True)          # make sure the window shows on top
        except Exception:
            pass
        chosen = filedialog.askdirectory(title=title, mustexist=True)
        root.destroy()
    except Exception:
        ui.warn("The folder window is not available on this computer. "
                "Please paste the path instead.")
        return None
    return Path(chosen) if chosen else None


START_FOLDER = None          # set when started with --here or a folder argument


def apply_start_args(ui, argv):
    """`--here` (use the current folder) or a folder argument: every 'which folder?'
    question will then offer 'This folder' as the first (default) choice."""
    global START_FOLDER
    given = [a for a in argv if not a.startswith("--")]
    if given:
        folder = clean_path(given[0])
    elif "--here" in argv:
        folder = Path.cwd()
        # A fresh terminal starts in your home folder or in a system folder: don't suggest
        # those as "This folder" - let the person choose.
        system = os.environ.get("SystemRoot")
        try:
            risky = folder.resolve() == Path.home().resolve() or \
                (system and Path(system).resolve() in [folder.resolve()] + list(folder.resolve().parents))
        except OSError:
            risky = False
        if risky:
            ui.info("You are in your home/system folder, so please pick a folder below.")
            return
    else:
        return
    problem = common.check_folder(folder)
    if problem:
        ui.warn(problem + " I'll ask you to choose a folder instead.")
        return
    START_FOLDER = folder.resolve()
    ui.info("Working in: {}".format(START_FOLDER))


def pick_folder(ui, title="Step 1 - Which folder do you want to tidy?"):
    ui.heading(title)
    home = Path.home()
    entries, labels = [], []
    if START_FOLDER is not None:
        entries.append(("path", START_FOLDER))
        labels.append(ui.c("This folder", "bold", "green") + "  " +
                      ui.c("(" + str(START_FOLDER) + ")", "dim") + "  - just press Enter")
    for name in ("Downloads", "Desktop", "Documents"):
        p = home / name
        if p.is_dir() and p != START_FOLDER:
            entries.append(("path", p))
            labels.append("{:<10} {}".format(name, ui.c("(" + str(p) + ")", "dim")))
    entries.append(("browse", None))
    labels.append(ui.c("Browse...", "bold") + "  (a window opens - click the folder you want)")
    entries.append(("type", None))
    labels.append("Type or paste a folder path")
    choice = ui.choose(labels, back="Go back", default=0 if START_FOLDER is not None else None)
    if choice is None:
        return None
    kind, value = entries[choice]
    if kind == "path":
        folder = value
    elif kind == "browse":
        ui.info("A window is opening - it may appear behind this one. Pick a folder, click OK.")
        folder = browse_for_folder(ui, "Choose a folder")
        if folder is None:
            ui.info("No folder chosen.")
            return None
    else:
        ui.say()
        ui.info("How to paste a path:")
        ui.say(ui.wrap("Windows: open the folder in File Explorer, click the address bar at "
                       "the top, press Ctrl+C. Then come back here, RIGHT-CLICK in this window "
                       "(that pastes) and press Enter. You can also drag the folder into this "
                       "window.", indent=6))
        ui.say(ui.wrap("Mac: drag the folder into the Terminal window, then press Enter.",
                       indent=6))
        folder = clean_path(ui.ask("Folder path"))
    if not folder.is_dir():
        ui.error("I can't find a folder at that path. Nothing was changed.")
        return None
    if folder == Path(folder.anchor) or folder == folder.parent:
        ui.error("That's the top of a drive. For safety I won't use that.")
        return None
    ui.ok("Using: {}".format(folder))
    return folder


def show_plan(ui, folder, plan, skipped):
    groups = defaultdict(list)
    for src, category in plan:
        groups[category].append(src)
    ui.heading("Step 2 - Preview (nothing has moved yet)")
    ui.say("  Folder: " + ui.c(str(folder), "bold"))
    ui.say("  I found {} file(s) to organize into {} folder(s):".format(len(plan), len(groups)))
    for category in sorted(groups):
        files = groups[category]
        ui.say()
        ui.say("  " + ui.c(category + "/", "bold", "cyan") +
               "   {} file(s)".format(len(files)))
        ui.say(ui.wrap(explain.describe_folder(category), indent=6))
        for ext, n in Counter(f.suffix.lower() for f in files).most_common():
            ui.say("      {:<9} {} x {}".format(ext, n, explain.describe_ext(ext)[0]))
    if skipped:
        ui.say()
        ui.say("  " + ui.c("Left alone on purpose:", "bold", "yellow"))
        for reason, files in skipped.items():
            ui.say("    {} x {}".format(len(files), reason))
            ui.say(ui.wrap(explain.SKIP_INFO.get(reason, ""), indent=8))


def explain_types(ui, plan):
    ui.heading("What are these file types?")
    seen = []
    for src, _ in plan:
        ext = src.suffix.lower()
        if ext not in seen:
            seen.append(ext)
    for ext in seen:
        name, text = explain.describe_ext(ext)
        ui.say()
        ui.say("  " + ui.c(ext, "bold", "cyan") + "  -  " + ui.c(name, "bold"))
        ui.say(ui.wrap(text, indent=6))


def show_every_file(ui, plan):
    ui.heading("Every file and where it will go")
    for src, category in plan:
        ui.say("  {}  ->  {}/".format(src.name, ui.c(category, "cyan")))


def tidy_flow(ui, cfg):
    folder = pick_folder(ui)
    if folder is None:
        return
    try:
        with ui.spinner("Looking at the files in your folder"):
            plan, skipped = scan(folder, cfg)
    except OSError as err:
        ui.error("I'm not allowed to read that folder: {}".format(err))
        return
    if not plan:
        ui.info("Nothing to tidy here. The folder is already neat (or everything is protected).")
        for reason, files in skipped.items():
            ui.say("    {} x {}".format(len(files), reason))
        return
    show_plan(ui, folder, plan, skipped)
    while True:
        ui.say()
        ui.say("  " + ui.c("What now?", "bold"))
        choice = ui.choose(["Yes - tidy up now (you can undo it later)",
                            "Explain the file types in this list",
                            "Show every file and where it will go"],
                           back="Cancel - change nothing")
        if choice is None:
            ui.ok("Cancelled. Nothing was moved.")
            return
        if choice == 1:
            explain_types(ui, plan)
        elif choice == 2:
            show_every_file(ui, plan)
        else:
            break
    ui.heading("Step 3 - Tidying up")
    moves, failed = do_moves(ui, folder, plan)
    ui.say()
    ui.celebrate("Moved {} file(s)!".format(len(moves)))
    for name, err in failed:
        ui.warn("Could not move {}: {}".format(name, err))
    ui.info("Open the folder and you will see the new category folders.")
    ui.info("Don't like it? Choose 'Undo' in the main menu and everything goes back.")


def undo_flow(ui):
    ui.heading("Undo the last change")
    folder = pick_folder(ui, "Which folder do you want to undo a change in?")
    if folder is None:
        return
    log = latest_log(folder)
    if not log:
        ui.info("There is nothing to undo in that folder.")
        return
    data = common.read_log(log)
    count = len(data.get("moves", []))
    ui.say("  Last change there: {} file(s), made by '{}' ({})".format(
        count, data.get("tool", "?"), log.stem.split("_", 1)[1]))
    if not ui.confirm("Put these {} file(s) back where they were?".format(count)):
        ui.ok("OK, nothing changed.")
        return
    restored, missing = do_undo(ui, folder, log)
    ui.celebrate("Put back {} file(s).".format(restored))
    if missing:
        ui.warn("{} file(s) were no longer in the category folders (moved or deleted).".format(missing))


def lookup_flow(ui, cfg):
    ui.heading("What does this file type mean?")
    ui.info("Type a file type like  svg  or  .jpeg  - or a whole file name like  photo.HEIC")
    ui.info("Press Enter on an empty line to go back.")
    while True:
        text = ui.ask("File type")
        if not text:
            return
        ext = explain.normalise_ext(text)
        name, desc = explain.describe_ext(ext)
        folder = explain.folder_for_ext(ext, cfg)
        ui.say()
        ui.say("  " + ui.c(ext, "bold", "cyan") + "  -  " + ui.c(name, "bold"))
        ui.say(ui.wrap(desc, indent=6))
        if folder is None:
            ui.say(ui.wrap("This kind of file is never moved by the organizer.", indent=6))
        else:
            ui.say(ui.wrap("It would go in the '{}' folder: {}".format(
                folder, explain.describe_folder(folder)), indent=6))
        ui.say()


def learn_flow(ui):
    ui.heading("Learn the basics")
    titles = [t for t, _ in explain.CONCEPTS]
    while True:
        choice = ui.choose(titles, back="Go back")
        if choice is None:
            return
        ui.say()
        ui.say("  " + ui.c(explain.CONCEPTS[choice][0], "bold", "cyan"))
        ui.say(ui.wrap(explain.CONCEPTS[choice][1], indent=4))
        ui.say()


def migrate_flow(ui):
    ui.heading("Fix old folders (.txt, .mp4, .ipynb ...)")
    folder = pick_folder(ui)
    if folder is None:
        return
    ui.info("First a preview - nothing is changed:")
    migrate_old_folders.main(["--dry-run", "--", str(folder)])
    if ui.confirm("Convert these folders now?"):
        migrate_old_folders.main(["-y", "--", str(folder)])


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def main(argv=None):
    argv = sys.argv[1:] if argv is None else list(argv)
    ui = UI(plain="--plain" in argv)
    cfg = load_config()
    ui.banner()
    apply_start_args(ui, argv)
    ui.say()
    ui.typewriter("  Hi! I'll help you tidy a messy folder.")
    ui.typewriter("  Nothing moves until you say yes - and you can always undo.")
    menu = ["Tidy a folder (start here)",
            "Undo the last tidy-up",
            "What does a file type mean? (.jpeg, .svg ...)",
            "Learn the basics",
            "Fix old '.txt / .mp4' folders"]
    try:
        while True:
            ui.heading("Main menu")
            choice = ui.choose(menu, back="Exit")
            if choice is None:
                break
            if choice == 0:
                tidy_flow(ui, cfg)
            elif choice == 1:
                undo_flow(ui)
            elif choice == 2:
                lookup_flow(ui, cfg)
            elif choice == 3:
                learn_flow(ui)
            elif choice == 4:
                migrate_flow(ui)
            ui.say()
            ui.pause()
    except (EOFError, KeyboardInterrupt):
        ui.say()
    ui.say()
    ui.ok("Bye! Your files are safe.")


if __name__ == "__main__":
    main()

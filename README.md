<div align="center">

# TidyMate

**Tidy your messy folders in one minute - with a preview first and undo for everything.**

Sort Downloads, rename hundreds of files, find duplicates, back things up.
No commands to memorise. Nothing is ever deleted.

[![PyPI](https://img.shields.io/pypi/v/tidymate?color=blue)](https://pypi.org/project/tidymate/)
[![Python](https://img.shields.io/pypi/pyversions/tidymate)](https://pypi.org/project/tidymate/)
[![Tests](https://github.com/Anand2k29/TidyMate/actions/workflows/tests.yml/badge.svg)](https://github.com/Anand2k29/TidyMate/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

```text
pip install tidymate
tidymate
```

---

## Why TidyMate?

- **Safe by design.** Every tool shows a **preview** and asks before it changes anything.
  Files are never overwritten and **never deleted**. One **Undo** reverses any change.
- **Made for humans.** A numbered menu - just type a number. No flags to learn. It even
  explains what `.jpeg`, `.svg` or `.pdf` mean and why each file lands in its folder.
- **Works where you are.** Open a terminal in any folder, type `tidymate`, and that folder
  is already selected.
- **Private and tiny.** No dependencies, no accounts, no internet connection needed. Your
  files never leave your computer.
- **Cross-platform.** Windows, macOS and Linux (Python 3.8+).

## See it in action

```text
$ cd Downloads
$ tidymate

   1.  Tidy a folder into category folders
   2.  Rename many files at once
   3.  Archive old files
   ...
  > Type a number, then press Enter: 1

   1.  This folder  (C:\Users\you\Downloads)  - just press Enter
  > Type a number, then press Enter:

 Step 2 - Preview (nothing has moved yet)
  I found 14 file(s) to organize into 4 folder(s):

  Images/   6 file(s)
      Pictures, photos, screenshots and icons.
      .jpeg     3 x JPEG photo
      .svg      1 x SVG vector graphic
      .png      2 x PNG image

  Documents/   5 file(s)
      Text documents, PDFs, notes and e-books.
      .pdf      5 x PDF document

  Left alone on purpose:
    1 x unfinished download
        Still downloading (or interrupted). Moving it would break the download.

   1.  Yes - tidy up now (you can undo it later)
   2.  Explain the file types in this list
   3.  Show every file and where it will go
   0.  Cancel - change nothing
```

Changed your mind? Menu **10 - Undo the last change**, and every file goes back.

---

## Install

You need [Python 3.8+](https://www.python.org/downloads/) (on Windows, tick **"Add Python to PATH"**).
Pick **one** way:

### 1. pip (recommended)

```bash
pip install tidymate
```

**Windows tip:** if `pip` or `tidymate` is "not recognized", run these two lines instead:

```powershell
py -m pip install tidymate
py -m tidymate setup
```

`tidymate setup` makes the command work **immediately in every terminal**.
(Like isolated installs? `pipx install tidymate` works too.)

### 2. One-line installer

Creates a private environment, installs TidyMate and sets up the command. Run it again to update.

**Windows (PowerShell)**
```powershell
irm https://raw.githubusercontent.com/Anand2k29/TidyMate/main/install.ps1 | iex
```

**macOS / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/Anand2k29/TidyMate/main/install.sh | sh
```

### 3. No install

[Download the zip](https://github.com/Anand2k29/TidyMate/archive/refs/heads/main.zip),
unzip, and double-click **`START_HERE.bat`** (Windows) or **`start.command`** (Mac).
Windows may warn that the publisher couldn't be verified - that's normal for scripts; click **Run**.

---

## Quick start

1. Open a terminal **in the folder you want to tidy**.
   *(Windows: open the folder in File Explorer, click the address bar, type `cmd`, press Enter.)*
2. Type `tidymate` and press Enter.
3. Press **1** (Tidy), then **Enter** to use "This folder", read the preview, and choose **Yes**.

`start_here` is the same command under a second name.

**Choosing a folder** - every "which folder?" question offers:
**This folder** *(press Enter)* - **Downloads / Desktop / Documents** - **Browse...**
(a window opens, click any folder on any drive) - or **type / paste a path**.

---

## What it can do

| # | Tool | What it does | Command |
|---|---|---|---|
| 1 | **Tidy** | Sorts loose files into `Images/`, `Documents/`, `Videos/` ... and explains each folder | `tidymate tidy` |
| 2 | **Rename** | Lowercase, no spaces, date first, numbered (`trip_001.jpg`), add or replace text | `tidymate rename` |
| 3 | **Archive old files** | Moves files untouched for a year (you choose) into `_Old/<year>/` | `tidymate archive` |
| 4 | **Find duplicates** | Finds exact copies; can move the extras aside to review | `tidymate dupes` |
| 5 | **Remove empty folders** | Removes folders with nothing inside | `tidymate empty` |
| 6 | **Disk report** | Space per category, biggest files, stale files | `tidymate disk` |
| 7 | **Folder tree** | A picture of what's inside and how big it is | `tidymate tree` |
| 8 | **Backup** | A dated `.zip` copy, verified afterwards | `tidymate backup` |
| 9 | **Checksums** | Save "fingerprints" now; check later that nothing changed or got damaged | `tidymate checksum` |
| 10 | **Undo** | Reverses the last change from tidy, rename, archive, duplicates or migrate | `tidymate undo` |
| 11 | **File-type lookup** | What does `.svg` mean? Where would it go? | `tidymate explain` |
| 12 | **Learn the basics** | Files, folders, preview, undo - in plain English | menu |
| 13 | **Fix old folders** | Converts old `.txt` / `.mp4` extension folders | `tidymate migrate` |

Read-only tools (disk report, tree, checksum verify, duplicate report) never change your files.

### Command cheat sheet

The menu is all most people need. For scripts and power users, everything is also a command.
`.` means "the folder I'm standing in".

```bash
tidymate tidy . --dry-run              # preview sorting the current folder
tidymate tidy "D:\Inbox"               # sort it (asks first)
tidymate tidy . --mode category-date   # Images/2026-10/ ...
tidymate rename . --lower --spaces --only jpg
tidymate rename . --number holiday     # holiday_001.jpg, holiday_002.jpg ...
tidymate rename . --find IMG --replace-with Holiday
tidymate archive . --days 180          # untouched for 6 months -> _Old/<year>/
tidymate dupes .                       # report only
tidymate dupes . --move-to ./_review   # move the extra copies aside
tidymate empty . --dry-run
tidymate disk . --top 15 --stale-days 365
tidymate tree . --depth 3 --files
tidymate backup . --dest "D:\Backups"
tidymate checksum create .             # save fingerprints...
tidymate checksum verify .             # ...check them later
tidymate undo .
tidymate explain svg .jpeg photo.HEIC
tidymate config --open                 # edit the categories
tidymate doctor                        # diagnose installation problems
tidymate --help
```

---

## File types, explained

TidyMate tells you what your files are as it goes. Look any type up with `tidymate explain svg`.
The full list is in **[docs/GLOSSARY.md](docs/GLOSSARY.md)**.

| Type | In plain English |
|---|---|
| `.jpg` / `.jpeg` | The same thing - the common photo format |
| `.png` | Sharp image that can be see-through (screenshots, logos) |
| `.svg` | A drawing made of shapes - stays sharp at any size; opens in a browser |
| `.pdf` | A document that looks the same on every device |
| `.zip` | Many files squeezed into one |
| `.exe` / `.msi` | Programs and installers - only run ones you trust |

| Folder | Holds |
|---|---|
| `Images/` | Pictures, photos, screenshots, icons |
| `Documents/` | PDFs, Word files, notes, e-books |
| `Videos/` `Audio/` | Movies and clips / music and voice notes |
| `Archives/` | Zip files and other compressed bundles |
| `Installers/` | App installers |
| `Other/` | Types TidyMate doesn't know yet - nothing is wrong with them |
| `_Duplicates/` `_Duplicates_Review/` | Exact copies, safe to review and delete |
| `_Old/<year>/` | Files you haven't touched for a long time |

---

## How TidyMate keeps your files safe

| Risk | Protection |
|---|---|
| Changing something by mistake | Preview first - nothing happens until you say yes |
| Breaking a running download | `.crdownload`, `.part`, `.tmp` ... are skipped, and so is anything modified in the last 5 minutes |
| Overwriting a file | Name clashes become `name (1).ext` |
| Deleting a file | **No tool deletes files.** (Only truly empty folders can be removed.) |
| System files | Hidden and system files are skipped |
| Your own folders | Only loose files are touched; sub-folders are left alone |
| Running on `C:\` | Drive roots are refused |
| "Where did my file go?" | Every change is logged in `.organizer_logs/` inside the folder; **Undo** reverses it |

One Undo works for every tool. (Empty folders that were removed aren't restored - nothing was in them.)

## Make it yours

```bash
tidymate config --open
```

Creates `~/.tidymate/categories.json` with all the defaults and opens it. Move file types
between folders or add new ones, for example `"Ebooks": [".epub", ".mobi"]`.
Delete the file (or run `tidymate config --reset`) to get the defaults back.

---

## FAQ

**Will it delete my files?**
No. TidyMate only moves and renames, and you can undo every move. The one thing it removes is
a folder that is completely empty - and only when you ask.

**Is it safe to run on my Downloads folder?**
Yes - that's what it's for. You always see a preview first, unfinished downloads are skipped,
and your existing sub-folders are never touched.

**Does it send my data anywhere?**
No. TidyMate has no network code at all and no dependencies. It runs entirely on your computer.

**Where is the undo history kept?**
In a hidden `.organizer_logs` folder inside the folder you tidied.

**Does it look inside sub-folders?**
Tidy, rename and archive only handle the loose files at the top of the folder you choose - on
purpose. Duplicates, disk report, tree, backup and checksums do look inside sub-folders.

**A file went to `Other/`. Why?**
TidyMate doesn't recognise that file type yet. Add it to a category with `tidymate config`.

**Does it work on Mac and Linux?**
Yes. Everything works on Windows, macOS and Linux with Python 3.8 or newer.

## Troubleshooting

**`tidymate` is "not recognized"**
1. Run `py -m tidymate setup` (Windows) or `python3 -m tidymate setup`. It puts the command where
   your system already looks, so it works straight away.
2. Run `tidymate doctor` (or `py -m tidymate doctor`). It tests everything and tells you what to do.
3. A terminal opened *before* installing - or from File Explorer's address bar - keeps an old PATH.
   Open a fresh one from the Start menu, or sign out and back in once.

**Colours look like `[36m`** - run `tidymate --plain`.

**Something went wrong inside a tool** - the menu shows a friendly message, saves the details to
`~/.tidymate/last_error.txt` and carries on. Anything finished earlier can be undone.

**Update** - `pip install --upgrade tidymate` (or run the one-line installer again).

**Uninstall** - `tidymate setup --uninstall`, then `pip uninstall tidymate`.
(One-line-installer users: also delete `~/.tidymate` on Mac/Linux, or `%LOCALAPPDATA%\TidyMate` on Windows.)

---

## Contributing

Bug reports, ideas and pull requests are welcome.

```bash
git clone https://github.com/Anand2k29/TidyMate.git
cd tidymate
pip install -e .
python -m unittest discover -s tests -v
```

Please keep TidyMate dependency-free, and add a test for any behaviour change.
Maintainers: see **[docs/PUBLISHING.md](docs/PUBLISHING.md)** for releasing.

## License

[MIT](LICENSE) - free to use, change and share.

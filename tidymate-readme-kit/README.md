<div align="center">

<img src="https://raw.githubusercontent.com/Anand2k29/TidyMate/main/docs/assets/banner.gif" alt="TidyMate - Python file organizer with preview and undo" width="100%">

# TidyMate - Python File Organizer with Preview & Undo

**Organize your Downloads folder in one minute.**
Sort files by type, bulk rename, find duplicate files, archive old files and back things up -
with a **preview first** and an **undo for everything**. Nothing is ever deleted.

[![PyPI](https://img.shields.io/pypi/v/tidymate?color=1faf9a&label=PyPI)](https://pypi.org/project/tidymate/)
[![Python](https://img.shields.io/pypi/pyversions/tidymate?color=1faf9a)](https://pypi.org/project/tidymate/)
[![Downloads](https://img.shields.io/pypi/dm/tidymate?color=1faf9a&label=downloads)](https://pypi.org/project/tidymate/)
[![Tests](https://github.com/Anand2k29/TidyMate/actions/workflows/tests.yml/badge.svg)](https://github.com/Anand2k29/TidyMate/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-1faf9a.svg)](https://github.com/Anand2k29/TidyMate/blob/main/LICENSE)
[![Stars](https://img.shields.io/github/stars/Anand2k29/TidyMate?color=1faf9a)](https://github.com/Anand2k29/TidyMate/stargazers)
![Platforms](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-1faf9a)
![Dependencies](https://img.shields.io/badge/dependencies-none-1faf9a)

<a href="#-install">Install</a> &nbsp;·&nbsp;
<a href="#-see-it-in-action">Demo</a> &nbsp;·&nbsp;
<a href="#-what-it-can-do">Features</a> &nbsp;·&nbsp;
<a href="#-use-cases">Use cases</a> &nbsp;·&nbsp;
<a href="#-command-cheat-sheet">Commands</a> &nbsp;·&nbsp;
<a href="#-how-tidymate-keeps-your-files-safe">Safety</a> &nbsp;·&nbsp;
<a href="#-faq">FAQ</a> &nbsp;·&nbsp;
<a href="#-contributing">Contribute</a>

</div>

```text
pip install tidymate
tidymate
```

That's it. A numbered menu opens - type a number, read the preview, say yes. No flags to learn.

---

## ✨ Why TidyMate?

<table>
<tr>
<td valign="top" width="33%">

### 🔒 Safe by design
Every tool shows a **preview** and asks before it changes anything. Files are never overwritten and **never deleted**.

</td>
<td valign="top" width="33%">

### ↩️ One undo for everything
Tidy, rename, archive, duplicates - **one Undo** puts every file back exactly where it was.

</td>
<td valign="top" width="33%">

### 🧭 Made for humans
A numbered menu - just type a number. It even explains what `.jpeg`, `.svg` or `.pdf` mean and why each file lands in its folder.

</td>
</tr>
<tr>
<td valign="top">

### 📍 Works where you are
Open a terminal in any folder, type `tidymate`, and that folder is already selected.

</td>
<td valign="top">

### 🪶 Private & tiny
**No dependencies**, no accounts, no internet needed. Your files never leave your computer.

</td>
<td valign="top">

### 🖥️ Cross-platform
Windows, macOS and Linux with Python 3.8 or newer.

</td>
</tr>
</table>

---

## 🎬 See it in action

<div align="center">

<img src="https://raw.githubusercontent.com/Anand2k29/TidyMate/main/docs/assets/demo.gif" alt="Animated demo: opening TidyMate, previewing the tidy-up of a Downloads folder, the progress bar, and undo" width="780">

<sub>Illustrative demo of the TidyMate menus.</sub>

</div>

<br>

<div align="center">

<img src="https://raw.githubusercontent.com/Anand2k29/TidyMate/main/docs/assets/before-after.png" alt="Before and after: a messy Downloads folder sorted into Images, Documents, Videos and Archives" width="780">

</div>

Changed your mind? Menu **10 - Undo the last change**, and every file goes back.

---

## 📦 Install

You need [Python 3.8+](https://www.python.org/downloads/) (on Windows, tick **"Add Python to PATH"** during setup).

### Option 1 - pip (recommended)

```bash
pip install tidymate
```

> **💡 Windows tip:** if `pip` or `tidymate` is "not recognized", run these two lines instead:
>
> ```powershell
> py -m pip install tidymate
> py -m tidymate setup
> ```
>
> `tidymate setup` makes the command work **immediately in every terminal**.
> Like isolated installs? `pipx install tidymate` works too.

<details>
<summary><b>Option 2 - One-line installer</b> (creates a private environment; run it again to update)</summary>

<br>

**Windows (PowerShell)**
```powershell
irm https://raw.githubusercontent.com/Anand2k29/TidyMate/main/install.ps1 | iex
```

**macOS / Linux**
```bash
curl -fsSL https://raw.githubusercontent.com/Anand2k29/TidyMate/main/install.sh | sh
```

</details>

<details>
<summary><b>Option 3 - No install at all</b> (download and double-click)</summary>

<br>

[Download the zip](https://github.com/Anand2k29/TidyMate/archive/refs/heads/main.zip), unzip it, and double-click
**`START_HERE.bat`** (Windows) or **`start.command`** (Mac).
Windows may warn that the publisher couldn't be verified - that's normal for scripts; click **Run**.

</details>

**Update:** `pip install --upgrade tidymate`

---

## 🚀 Quick start

1. Open a terminal **in the folder you want to tidy**.
   *(Windows: open the folder in File Explorer, click the address bar, type `cmd`, press <kbd>Enter</kbd>.)*
2. Type `tidymate` and press <kbd>Enter</kbd>.
3. Press **1** (Tidy), then <kbd>Enter</kbd> to use "This folder", read the preview, and choose **Yes**.

`start_here` is the same command under a second name.

**Choosing a folder** - every "which folder?" question offers:
**This folder** *(press Enter)* · **Downloads / Desktop / Documents** · **Browse...**
(a window opens, click any folder on any drive) · or **type / paste a path**.

<details>
<summary><b>What the preview screen looks like</b></summary>

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

</details>

---

## 🧰 What it can do

| # | Tool | What it does | Command |
|---|---|---|---|
| 1 | 🗂️ **Tidy** | Sorts loose files into `Images/`, `Documents/`, `Videos/` ... and explains each folder | `tidymate tidy` |
| 2 | ✏️ **Rename** | Lowercase, no spaces, date first, numbered (`trip_001.jpg`), add or replace text | `tidymate rename` |
| 3 | 🕰️ **Archive old files** | Moves files untouched for a year (you choose) into `_Old/<year>/` | `tidymate archive` |
| 4 | 👯 **Find duplicates** | Finds exact copies; can move the extras aside to review | `tidymate dupes` |
| 5 | 🧹 **Remove empty folders** | Removes folders with nothing inside | `tidymate empty` |
| 6 | 📊 **Disk report** | Space per category, biggest files, stale files | `tidymate disk` |
| 7 | 🌳 **Folder tree** | A picture of what's inside and how big it is | `tidymate tree` |
| 8 | 💾 **Backup** | A dated `.zip` copy, verified afterwards | `tidymate backup` |
| 9 | 🔐 **Checksums** | Save "fingerprints" now; check later that nothing changed or got damaged | `tidymate checksum` |
| 10 | ↩️ **Undo** | Reverses the last change from tidy, rename, archive, duplicates or migrate | `tidymate undo` |
| 11 | 🔎 **File-type lookup** | What does `.svg` mean? Where would it go? | `tidymate explain` |
| 12 | 📚 **Learn the basics** | Files, folders, preview, undo - in plain English | menu |
| 13 | 🛠️ **Fix old folders** | Converts old `.txt` / `.mp4` extension folders | `tidymate migrate` |

Read-only tools (disk report, tree, checksum verify, duplicate report) never change your files.

---

## 🎯 Use cases

### 📥 Organize your Downloads folder
The classic mess: PDFs, installers, screenshots and zips all in one pile. TidyMate sorts them into
`Images/`, `Documents/`, `Installers/`, `Archives/` and more, skips downloads that are still running, and lets you undo.
```bash
tidymate tidy ~/Downloads --dry-run     # preview first
tidymate tidy ~/Downloads               # then do it (asks first)
```

### ✏️ Rename files in bulk
Fix hundreds of names at once: lowercase, replace spaces, add numbers or dates, find-and-replace text.
```bash
tidymate rename . --lower --spaces --only jpg
tidymate rename . --number holiday      # holiday_001.jpg, holiday_002.jpg ...
```

### 👯 Find duplicate files
Exact copies are found by their content, not their names. Move the extras aside, review them, and delete them yourself.
```bash
tidymate dupes . --move-to ./_review
```

### 🕰️ Archive old files
Move files you haven't touched for a long time into `_Old/<year>/` and free up your working folders.
```bash
tidymate archive . --days 365
```

### 💾 Back up a folder and check nothing changed
Make a dated zip, verified afterwards. Save checksums now and verify them later to catch changes or damage.
```bash
tidymate backup . --dest "D:\Backups"
tidymate checksum create .
tidymate checksum verify .
```

### ↩️ Undo any change
Moved something you didn't mean to? One command puts every file back where it was.
```bash
tidymate undo .
```

---

## 🧾 Command cheat sheet

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

## 📖 File types, explained

TidyMate tells you what your files are as it goes. Look any type up with `tidymate explain svg`.
The full list is in the **[glossary](https://github.com/Anand2k29/TidyMate/blob/main/docs/GLOSSARY.md)**.

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

## 🛡️ How TidyMate keeps your files safe

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

### TidyMate vs. the alternatives

| | Doing it by hand | A quick one-off script | **TidyMate** |
|---|:---:|:---:|:---:|
| Preview before anything moves | - | usually not | ✅ |
| Undo | - | usually not | ✅ |
| Skips downloads that are still running | - | usually not | ✅ |
| Explains what each file type is | - | - | ✅ |
| Never overwrites or deletes | easy to slip | depends | ✅ |
| Setup | none | write and debug it | `pip install tidymate` |

---

## 🎨 Make it yours

```bash
tidymate config --open
```

Creates `~/.tidymate/categories.json` with all the defaults and opens it. Move file types
between folders or add new ones, for example `"Ebooks": [".epub", ".mobi"]`.
Delete the file (or run `tidymate config --reset`) to get the defaults back.

---

## ❓ FAQ

<details>
<summary><b>Will it delete my files?</b></summary>

<br>

No. TidyMate only moves and renames, and you can undo every move. The one thing it removes is
a folder that is completely empty - and only when you ask.

</details>

<details>
<summary><b>Is it safe to run on my Downloads folder?</b></summary>

<br>

Yes - that's what it's for. You always see a preview first, unfinished downloads are skipped,
and your existing sub-folders are never touched.

</details>

<details>
<summary><b>Does it send my data anywhere?</b></summary>

<br>

No. TidyMate has no network code at all and no dependencies. It runs entirely on your computer.

</details>

<details>
<summary><b>Where is the undo history kept?</b></summary>

<br>

In a hidden `.organizer_logs` folder inside the folder you tidied.

</details>

<details>
<summary><b>Does it look inside sub-folders?</b></summary>

<br>

Tidy, rename and archive only handle the loose files at the top of the folder you choose - on
purpose. Duplicates, disk report, tree, backup and checksums do look inside sub-folders.

</details>

<details>
<summary><b>A file went to <code>Other/</code>. Why?</b></summary>

<br>

TidyMate doesn't recognise that file type yet. Add it to a category with `tidymate config`.

</details>

<details>
<summary><b>Does it work on Mac and Linux?</b></summary>

<br>

Yes. Everything works on Windows, macOS and Linux with Python 3.8 or newer.

</details>

<details>
<summary><b>Is it free?</b></summary>

<br>

Yes. TidyMate is open source under the [MIT license](https://github.com/Anand2k29/TidyMate/blob/main/LICENSE) - free to use, change and share.

</details>

---

## 🩺 Troubleshooting

<details>
<summary><b><code>tidymate</code> is "not recognized"</b></summary>

<br>

1. Run `py -m tidymate setup` (Windows) or `python3 -m tidymate setup`. It puts the command where
   your system already looks, so it works straight away.
2. Run `tidymate doctor` (or `py -m tidymate doctor`). It tests everything and tells you what to do.
3. A terminal opened *before* installing - or from File Explorer's address bar - keeps an old PATH.
   Open a fresh one from the Start menu, or sign out and back in once.

</details>

<details>
<summary><b>Colours look like <code>[36m</code></b></summary>

<br>

Run `tidymate --plain`.

</details>

<details>
<summary><b>Something went wrong inside a tool</b></summary>

<br>

The menu shows a friendly message, saves the details to `~/.tidymate/last_error.txt` and carries on.
Anything finished earlier can be undone.

</details>

<details>
<summary><b>Update or uninstall</b></summary>

<br>

- **Update:** `pip install --upgrade tidymate` (or run the one-line installer again).
- **Uninstall:** `tidymate setup --uninstall`, then `pip uninstall tidymate`.
  One-line-installer users: also delete `~/.tidymate` on Mac/Linux, or `%LOCALAPPDATA%\TidyMate` on Windows.

</details>

---

## 🤝 Contributing

Bug reports, ideas and pull requests are welcome.
**[Report a bug or suggest a feature](https://github.com/Anand2k29/TidyMate/issues/new)**

```bash
git clone https://github.com/Anand2k29/TidyMate.git
cd TidyMate
pip install -e .
python -m unittest discover -s tests -v
```

Please keep TidyMate dependency-free, and add a test for any behaviour change.
Maintainers: see the **[publishing guide](https://github.com/Anand2k29/TidyMate/blob/main/docs/PUBLISHING.md)** for releasing.
The README images are rebuilt with `python docs/assets/build_assets.py` (needs `pip install pillow`).

## ⭐ Support the project

If TidyMate saved you time, **[give it a star on GitHub](https://github.com/Anand2k29/TidyMate)** and tell a friend
whose Downloads folder needs help. It's the easiest way to help other people find it.

## 📄 License

[MIT](https://github.com/Anand2k29/TidyMate/blob/main/LICENSE) - free to use, change and share.

<div align="center">

Made with ❤️ by [@Anand2k29](https://github.com/Anand2k29)

</div>

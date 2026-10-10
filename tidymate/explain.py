#!/usr/bin/env python3
"""
explain.py - plain-English explanations of file types (.jpeg, .svg ...) and folders.

The guided mode (easy_organizer.py) uses this to tell you WHAT your files are and
WHY they were put in a certain folder.

You can also run it to rebuild the glossary document:
    tidymate explain --markdown > docs/GLOSSARY.md
"""
import re
import sys

# --------------------------------------------------------------------------- #
#  What each folder means
# --------------------------------------------------------------------------- #
CATEGORY_INFO = {
    "Images": "Pictures, photos, screenshots and icons.",
    "Videos": "Movies, clips and screen recordings.",
    "Audio": "Music, voice notes and other sound files.",
    "Documents": "Text documents, PDFs, notes and e-books.",
    "Spreadsheets": "Tables of numbers and data (Excel, CSV).",
    "Presentations": "Slide shows (PowerPoint and similar).",
    "Code": "Programming files, scripts and notebooks.",
    "Data": "Data files that programs read and write (JSON, databases, logs).",
    "Archives": "Compressed bundles of files (zip) and software packages.",
    "Installers": "Programs and installers for apps. Only run ones you trust.",
    "Design_3D": "3D models and design files (Photoshop, Blender, CAD).",
    "Certificates_Keys": "Security keys and certificates. Keep these private!",
    "Fonts": "Typefaces used in documents and designs.",
    "Shortcuts": "Small links that point to another file, program or website.",
    "Other": "Files this tool does not recognise yet. Nothing is wrong with them.",
    "_Duplicates": "Exact copies of files that already existed. Safe to review and delete.",
}

# --------------------------------------------------------------------------- #
#  What each file type means:  extension -> (short name, explanation)
# --------------------------------------------------------------------------- #
EXT_INFO = {
    # ---- Images
    ".jpg": ("JPEG photo", "The most common photo format. Small files that open everywhere. '.jpg' and '.jpeg' are exactly the same thing."),
    ".jpeg": ("JPEG photo", "The most common photo format. Small files that open everywhere. Exactly the same as '.jpg'."),
    ".png": ("PNG image", "Sharp pictures that can have a see-through background. Typical for screenshots and logos."),
    ".gif": ("GIF image", "Small pictures that can be animated - memes and short loops."),
    ".bmp": ("Bitmap image", "A very old picture format. Files are large because nothing is compressed."),
    ".webp": ("WebP image", "A modern web picture format by Google. Smaller than JPG/PNG. Often what you get when you save an image from a website."),
    ".svg": ("SVG vector graphic", "A drawing made from shapes and lines instead of tiny dots, so it stays sharp at any size. Used for logos and icons. Opens in any web browser."),
    ".ico": ("Icon", "A small picture used as an app or website icon."),
    ".heic": ("HEIC photo", "The photo format of iPhones. Smaller than JPG, but not every Windows program can open it."),
    ".tif": ("TIFF image", "A high-quality image used for printing and scanning. Files are big."),
    ".tiff": ("TIFF image", "A high-quality image used for printing and scanning. Files are big."),
    ".avif": ("AVIF image", "A very new picture format with very small files."),
    # ---- Videos
    ".mp4": ("MP4 video", "The most common video format. Plays almost everywhere."),
    ".mkv": ("MKV video", "A flexible video format common for movies. If it will not play, install VLC."),
    ".avi": ("AVI video", "An old Windows video format. Files tend to be large."),
    ".mov": ("QuickTime video", "Apple's video format - used by iPhone and Mac recordings."),
    ".wmv": ("Windows Media video", "An older Microsoft video format."),
    ".webm": ("WebM video", "A video format made for websites."),
    ".flv": ("Flash video", "An outdated video format from the Flash era."),
    ".m4v": ("M4V video", "Apple's MP4-style video format."),
    # ---- Audio
    ".mp3": ("MP3 audio", "The most common music format."),
    ".wav": ("WAV audio", "Uncompressed, high-quality sound. Files are big."),
    ".flac": ("FLAC audio", "Music with perfect quality, but smaller than WAV."),
    ".aac": ("AAC audio", "A compressed audio format, a bit better than MP3."),
    ".m4a": ("M4A audio", "Apple-style audio - voice memos and iTunes songs."),
    ".ogg": ("Ogg audio", "An open, free audio format."),
    ".wma": ("Windows Media audio", "An older Microsoft audio format."),
    # ---- Documents
    ".pdf": ("PDF document", "A document that looks the same on every device - forms, invoices, books."),
    ".doc": ("Word document (old)", "A Microsoft Word file in the older format."),
    ".docx": ("Word document", "A Microsoft Word file."),
    ".txt": ("Plain text", "Simple text with no formatting. Opens in Notepad."),
    ".rtf": ("Rich text", "Text with basic formatting such as bold and colours."),
    ".odt": ("OpenDocument text", "The LibreOffice version of a Word document."),
    ".md": ("Markdown text", "Text with simple marks for headings and lists. README files use it."),
    ".epub": ("E-book", "A book for e-readers and reading apps."),
    ".pkpass": ("Wallet pass", "A digital ticket or boarding pass for a phone wallet."),
    # ---- Spreadsheets
    ".xls": ("Excel spreadsheet (old)", "A Microsoft Excel table in the older format."),
    ".xlsx": ("Excel spreadsheet", "A Microsoft Excel table - numbers, formulas, charts."),
    ".xlsm": ("Excel spreadsheet with macros", "An Excel file that can contain automatic scripts (macros)."),
    ".csv": ("CSV table", "A table saved as plain text with commas between values. Opens in Excel; very common for data."),
    ".tsv": ("TSV table", "Like CSV, but values are separated by tabs."),
    ".ods": ("OpenDocument spreadsheet", "The LibreOffice version of an Excel file."),
    # ---- Presentations
    ".ppt": ("PowerPoint slides (old)", "A slide show in the older PowerPoint format."),
    ".pptx": ("PowerPoint slides", "A Microsoft PowerPoint slide show."),
    ".odp": ("OpenDocument slides", "The LibreOffice version of a PowerPoint."),
    # ---- Code
    ".py": ("Python script", "A program written in the Python language."),
    ".ipynb": ("Jupyter notebook", "Python code mixed with notes and charts. Popular in data science."),
    ".js": ("JavaScript file", "Code that makes websites interactive."),
    ".jsx": ("React JavaScript file", "JavaScript with HTML-like parts, used to build web apps with React."),
    ".ts": ("TypeScript file", "JavaScript with extra safety checks."),
    ".tsx": ("React TypeScript file", "TypeScript used to build web apps with React."),
    ".html": ("Web page", "A web page. Double-click to open it in your browser."),
    ".css": ("Style sheet", "Colours, fonts and layout rules for a web page."),
    ".java": ("Java source file", "A program written in Java."),
    ".c": ("C source file", "A program written in the C language."),
    ".cpp": ("C++ source file", "A program written in C++."),
    ".h": ("C/C++ header file", "A helper file for C or C++ programs."),
    ".cs": ("C# source file", "A program written in C#."),
    ".go": ("Go source file", "A program written in Go."),
    ".rs": ("Rust source file", "A program written in Rust."),
    ".php": ("PHP file", "Code that runs on web servers."),
    ".rb": ("Ruby file", "A program written in Ruby."),
    ".sh": ("Shell script", "A list of commands for Linux or Mac."),
    ".bat": ("Windows batch script", "A list of commands. Double-clicking RUNS it - only run ones you trust."),
    ".ps1": ("PowerShell script", "A Windows script. Running it can change your computer - only run ones you trust."),
    ".sql": ("SQL file", "Commands for a database."),
    ".vsix": ("VS Code extension", "An add-on for the Visual Studio Code editor."),
    # ---- Data
    ".json": ("JSON data", "Organised data that apps and websites use. Plain text you can open in Notepad."),
    ".xml": ("XML data", "Organised data written with tags. Older cousin of JSON."),
    ".yaml": ("YAML settings", "A readable settings or configuration file."),
    ".yml": ("YAML settings", "A readable settings or configuration file."),
    ".pkl": ("Python pickle file", "A saved Python object or trained model. Only open ones from people you trust."),
    ".parquet": ("Parquet table", "A compact data table used in data science."),
    ".db": ("Database file", "A database stored in one file."),
    ".sqlite": ("SQLite database", "A small database stored in one file."),
    ".h5": ("HDF5 data", "Big scientific or machine-learning data."),
    ".npy": ("NumPy array", "Saved numbers from Python's NumPy library."),
    ".npz": ("NumPy arrays (zipped)", "Several saved NumPy arrays in one file."),
    ".log": ("Log file", "A diary written by a program. Handy for finding errors."),
    # ---- Archives
    ".zip": ("ZIP archive", "Many files squeezed into one. Right-click > Extract All to open it."),
    ".rar": ("RAR archive", "Like ZIP. Needs 7-Zip or WinRAR to open."),
    ".7z": ("7-Zip archive", "A very strong compression format. Needs 7-Zip."),
    ".tar": ("TAR archive", "Many files bundled together (Linux style), not compressed."),
    ".gz": ("GZip file", "A compressed file (Linux style)."),
    ".tgz": ("Compressed TAR", "A TAR bundle that is also compressed."),
    ".bz2": ("BZip2 file", "A compressed file."),
    ".xz": ("XZ file", "A strongly compressed file."),
    ".whl": ("Python package", "A Python add-on you install with 'pip install'."),
    # ---- Installers
    ".exe": ("Windows program", "An app or an installer. Only run ones from sources you trust."),
    ".msi": ("Windows installer", "An installer for Windows software."),
    ".msix": ("Windows app package", "A modern Windows app installer."),
    ".appx": ("Windows app package", "A Windows app installer (Microsoft Store style)."),
    ".dmg": ("Mac disk image", "A Mac installer. It does not run on Windows."),
    ".pkg": ("Mac installer", "An installer for Mac software."),
    ".apk": ("Android app", "An app for Android phones."),
    ".deb": ("Linux package", "An installer for Debian/Ubuntu Linux."),
    ".rpm": ("Linux package", "An installer for Fedora/Red Hat Linux."),
    ".iso": ("Disk image", "An exact copy of a DVD or USB stick. Used to install operating systems."),
    # ---- Design / 3D
    ".glb": ("3D model (GLB)", "A 3D model in a single file. Used on websites, AR and games."),
    ".gltf": ("3D model (glTF)", "A 3D model for the web."),
    ".stl": ("3D-print model", "A 3D shape made for 3D printers."),
    ".obj": ("3D model (OBJ)", "A common, simple 3D model file."),
    ".fbx": ("3D model (FBX)", "A 3D model with animation, used in games and film."),
    ".blend": ("Blender project", "A project file of the Blender 3D program."),
    ".psd": ("Photoshop file", "A layered image made in Adobe Photoshop."),
    ".ai": ("Illustrator drawing", "A vector drawing made in Adobe Illustrator."),
    ".fig": ("Figma file", "A design made in Figma."),
    ".xd": ("Adobe XD file", "A design made in Adobe XD."),
    ".dwg": ("AutoCAD drawing", "A technical drawing used by engineers and architects."),
    # ---- Certificates / keys
    ".pem": ("Security certificate or key", "Often a private key. Keep it private and never share it."),
    ".crt": ("Security certificate", "A certificate that proves a website or person is who they say."),
    ".cer": ("Security certificate", "A certificate that proves a website or person is who they say."),
    ".pfx": ("Certificate + private key", "A bundle that contains a private key. Keep it private."),
    ".p12": ("Certificate + private key", "A bundle that contains a private key. Keep it private."),
    ".ppk": ("PuTTY private key", "A private key for connecting to servers. Keep it private."),
    # ---- Fonts
    ".ttf": ("TrueType font", "A typeface you can install on your computer."),
    ".otf": ("OpenType font", "A typeface you can install on your computer."),
    ".woff": ("Web font", "A typeface used on websites."),
    ".woff2": ("Web font", "A typeface used on websites (newer, smaller)."),
    # ---- Shortcuts
    ".lnk": ("Windows shortcut", "A tiny link that points to another file or program. It is not the real thing."),
    ".url": ("Internet shortcut", "A tiny link that opens a website."),
    # ---- Not moved (still working / temporary)
    ".crdownload": ("Unfinished Chrome download", "A download that is still running or was interrupted. Left alone on purpose."),
    ".part": ("Unfinished download", "A download that is still running or was interrupted. Left alone on purpose."),
    ".partial": ("Unfinished download", "A download that is still running or was interrupted. Left alone on purpose."),
    ".download": ("Unfinished download", "A download that is still running or was interrupted. Left alone on purpose."),
    ".opdownload": ("Unfinished Opera download", "A download that is still running or was interrupted. Left alone on purpose."),
    ".aria2": ("Unfinished download", "A download that is still running or was interrupted. Left alone on purpose."),
    ".tmp": ("Temporary file", "A scratch file a program uses while working. Left alone on purpose."),
    ".temp": ("Temporary file", "A scratch file a program uses while working. Left alone on purpose."),
    # ---- Seen in the wild
    ".winmd": ("Windows metadata", "A technical file used by Windows apps and developers."),
}

# --------------------------------------------------------------------------- #
#  Why files were skipped (reason text used by smart_organizer.py)
# --------------------------------------------------------------------------- #
SKIP_INFO = {
    "unfinished download": "Still downloading (or interrupted). Moving it would break the download.",
    "hidden/system file": "Windows and your apps use these. Moving them could break things.",
    "system file": "A file Windows creates by itself (like desktop.ini).",
    "no extension": "These files have no type (no '.something' at the end), so I can't tell what they are.",
    "modified very recently": "Changed in the last few minutes - it may still be saving. Run again later.",
    "excluded by --exclude": "You asked me to leave it alone.",
    "this script": "That is the tool itself.",
    "unreadable": "I was not allowed to read it.",
}

# --------------------------------------------------------------------------- #
#  Basic ideas, for the "Learn" menu
# --------------------------------------------------------------------------- #
CONCEPTS = [
    ("What is a file type (extension)?",
     "The letters after the last dot in a file name, like the '.jpg' in 'holiday.jpg'. "
     "It tells Windows which program should open the file. This tool reads it to decide "
     "which folder the file belongs in."),
    ("What is a folder?",
     "A container that holds files (and other folders), like a drawer in a cupboard. "
     "This tool creates folders such as 'Images' and 'Documents' and moves files into them. "
     "It never touches folders that already exist."),
    ("What does 'preview' mean?",
     "Preview (also called a 'dry run') shows what WOULD happen without changing anything. "
     "Nothing moves until you say yes."),
    ("What is undo?",
     "Every tidy-up is written to a history file inside the folder. Choose 'Undo' in the main "
     "menu and every file goes back to exactly where it was."),
    ("What are the '.mp4', '.jpg' ... folders I already have?",
     "An older version of this tool made one folder per file type, named with a dot. "
     "Use 'Fix old folders' in the main menu to convert them into the tidier folders."),
    ("Is it safe?",
     "Yes. Nothing moves without your OK. Nothing is ever deleted or overwritten. Files that are "
     "still downloading, hidden files, and your own folders are left alone. And you can undo."),
]


# --------------------------------------------------------------------------- #
#  Look-up helpers
# --------------------------------------------------------------------------- #
def normalise_ext(text):
    """'svg' -> '.svg',  'Photo.JPEG' -> '.jpeg',  ' .PNG ' -> '.png'."""
    text = text.strip().strip('"').strip("'").lower()
    if not text:
        return ""
    if "." in text[1:]:                 # looks like a file name: take its extension
        text = "." + text.rsplit(".", 1)[1]
    elif not text.startswith("."):
        text = "." + text
    return text


def describe_ext(ext):
    """Return (short name, explanation) for an extension like '.svg'."""
    ext = normalise_ext(ext)
    if ext in EXT_INFO:
        return EXT_INFO[ext]
    return ("{} file".format(ext.lstrip(".").upper() or "Unknown"),
            "A less common file type that this tool does not know yet. It goes to 'Other'. "
            "You can add it to a category in config/categories.json.")


def describe_folder(name):
    """Plain-English meaning of a destination folder such as 'Images', '2026-10', 'JPG'."""
    top = name.replace("\\", "/").split("/")[0]
    if top in CATEGORY_INFO:
        return CATEGORY_INFO[top]
    if re.fullmatch(r"\d{4}", top):
        return "Files grouped by the year and month they were last changed."
    if top == ".":
        return "Stays in the main folder."
    if top.isupper():
        return "All the .{} files.".format(top.lower())
    return "A folder from your own category list."


def folder_for_ext(ext, config):
    """Which category folder an extension belongs to (for the lookup screen)."""
    ext = normalise_ext(ext)
    if ext in {e.lower() for e in config.get("skip_extensions", [])}:
        return None                                  # never moved
    for category, exts in config["categories"].items():
        if ext in (e.lower() for e in exts):
            return category
    return config.get("other_folder", "Other")


def markdown_glossary():
    """Build docs/GLOSSARY.md from the built-in lists."""
    from tidymate.smart_organizer import DEFAULT_CONFIG
    out = ["# Glossary - what do the file types and folders mean?", "",
           "Generated by `tidymate explain --markdown`. In the guided tool, choose **Learn** to look",
           "any file type up. Folders are created automatically when needed.", ""]
    for category, exts in DEFAULT_CONFIG["categories"].items():
        out += ["## {}/".format(category), "", CATEGORY_INFO.get(category, ""), "",
                "| Type | Name | What it is |", "|---|---|---|"]
        for ext in exts:
            name, text = describe_ext(ext)
            out.append("| `{}` | {} | {} |".format(ext, name, text))
        out.append("")
    out += ["## Other/", "", CATEGORY_INFO["Other"], "",
            "## _Duplicates/", "", CATEGORY_INFO["_Duplicates"], "",
            "## Files that are never moved", "",
            "| Type | Name | What it is |", "|---|---|---|"]
    for ext in DEFAULT_CONFIG["skip_extensions"]:
        name, text = describe_ext(ext)
        out.append("| `{}` | {} | {} |".format(ext, name, text))
    out += ["", "## Basic ideas", ""]
    for title, text in CONCEPTS:
        out += ["**{}**  ".format(title), text, ""]
    return "\n".join(out)


if __name__ == "__main__":
    if "--markdown" in sys.argv:
        print(markdown_glossary())
    else:
        print(__doc__)

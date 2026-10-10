#!/usr/bin/env python3
"""
build_assets.py - regenerate the README images in this folder.

Creates:
    banner.gif          animated header (typing "pip install tidymate" + feature chips)
    demo.gif            animated terminal demo (menu -> preview -> progress bar -> undo)
    before-after.png    messy Downloads folder vs. the tidy result
    social-preview.png  1280x640 image for GitHub  (Settings -> Social preview)

This is a maintainer tool only. TidyMate itself has no dependencies; this script
needs Pillow:   pip install pillow
Run:            python docs/assets/build_assets.py

NOTE: demo.gif is an illustrative recreation of the menu text, not a screen recording.
To use a real recording instead, capture one with ScreenToGif and save it as demo.gif.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------- fonts ----
def find_font(candidates, size):
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()

MONO = ["DejaVuSansMono.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "consola.ttf", "Menlo.ttc", "Courier New.ttf"]
MONO_B = ["DejaVuSansMono-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
          "consolab.ttf", "Menlo.ttc"]
SANS = ["DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "arial.ttf"]
SANS_B = ["DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "arialbd.ttf"]

# ---------------------------------------------------------------- colours ---
OUTER = (13, 17, 23)
PANEL = (22, 27, 34)
BORDER = (48, 54, 61)
TEXT = (201, 209, 217)
DIM = (139, 148, 158)
WHITE = (240, 246, 252)
GREEN = (63, 185, 80)
CYAN = (57, 197, 207)
YELLOW = (210, 153, 34)
RED = (248, 81, 73)
TEAL = (31, 175, 154)
BLUE = (88, 166, 255)
MAGENTA = (188, 140, 255)


def save_gif(frames, path, colors=48):
    """frames = [(PIL image, milliseconds)]. Uses one shared palette to keep files small."""
    images = [f for f, _ in frames]
    step = max(1, len(images) // 8)
    sample = images[::step][:8]
    sheet = Image.new("RGB", (images[0].width, images[0].height * len(sample)))
    for i, im in enumerate(sample):
        sheet.paste(im, (0, i * images[0].height))
    palette = sheet.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in images]
    out[0].save(path, save_all=True, append_images=out[1:], duration=[ms for _, ms in frames],
                loop=0, optimize=True, disposal=1)
    print("wrote {} ({:.0f} KB, {} frames)".format(os.path.basename(path), os.path.getsize(path) / 1024, len(out)))


def draw_logo(d, x, y, s, fill=TEAL):
    """A folder with a check mark."""
    d.rounded_rectangle((x, y + 0.08 * s, x + 0.46 * s, y + 0.34 * s), radius=0.06 * s, fill=fill)
    d.rounded_rectangle((x, y + 0.2 * s, x + s, y + 0.92 * s), radius=0.1 * s, fill=fill)
    w = max(2, int(0.09 * s))
    pts = [(x + 0.27 * s, y + 0.57 * s), (x + 0.44 * s, y + 0.73 * s), (x + 0.74 * s, y + 0.42 * s)]
    d.line(pts, fill=WHITE, width=w, joint="curve")
    for px, py in (pts[0], pts[-1]):
        d.ellipse((px - w / 2, py - w / 2, px + w / 2, py + w / 2), fill=WHITE)


def chip(d, x, y, text, font, color=TEAL, pad=14):
    w = font.getlength(text) + pad * 2
    d.rounded_rectangle((x, y, x + w, y + font.size + 14), radius=(font.size + 14) // 2,
                        outline=color, width=2, fill=PANEL)
    d.text((x + pad, y + 6), text, font=font, fill=WHITE)
    return x + w + 12


# =====================================================================
#  1. Animated terminal demo
# =====================================================================
W, H = 820, 650
PAD_X, TOP, LH, ROWS = 26, 58, 22, 26
F_MONO = find_font(MONO, 16)
F_MONO_B = find_font(MONO_B, 16)
CW = F_MONO.getlength("M")


class Term:
    def __init__(self):
        self.lines = [[]]
        self.frames = []

    # -- building the screen
    def add(self, text, color=TEXT, bold=False):
        self.lines[-1].append((text, color, bold))

    def nl(self):
        self.lines.append([])

    def row(self, *segs):
        for seg in segs:
            self.add(*seg)
        self.nl()

    # -- drawing
    def render(self, cursor=True):
        img = Image.new("RGB", (W, H), OUTER)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((6, 6, W - 7, H - 7), radius=12, fill=PANEL, outline=BORDER, width=2)
        d.rounded_rectangle((7, 7, W - 8, 38), radius=11, fill=(30, 36, 44))
        d.rectangle((7, 26, W - 8, 38), fill=(30, 36, 44))
        for i, c in enumerate((RED, YELLOW, GREEN)):
            d.ellipse((24 + i * 22, 16, 36 + i * 22, 28), fill=c)
        title = "tidymate"
        d.text(((W - F_MONO.getlength(title)) / 2, 14), title, font=F_MONO, fill=DIM)
        visible = self.lines[-ROWS:]
        x = y = 0
        for i, line in enumerate(visible):
            x, y = PAD_X, TOP + i * LH
            for text, color, bold in line:
                d.text((x, y), text, font=F_MONO_B if bold else F_MONO, fill=color)
                x += len(text) * CW
        if cursor:
            d.rectangle((x + 1, y + 2, x + CW - 1, y + LH - 3), fill=TEXT)
        return img

    def snap(self, ms=80, cursor=True):
        self.frames.append((self.render(cursor), ms))

    def type(self, text, color=WHITE, bold=True, per=2, ms=55):
        for i in range(0, len(text), per):
            self.add(text[i:i + per], color, bold)
            self.snap(ms)


def build_demo():
    random.seed(7)
    t = Term()
    prompt = "C:\\Users\\you\\Downloads> "
    ask = [("  > ", GREEN, True), ("Type a number, then press Enter: ", TEXT, False)]

    # --- start the program
    t.add(prompt, DIM)
    t.snap(700)
    t.type("tidymate", WHITE, True)
    t.snap(350)
    t.nl()
    box = ["+" + "-" * 48 + "+", "|" + "T I D Y M A T E".center(48) + "|",
           "|" + "Tidy messy folders - with preview and undo".center(48) + "|", "+" + "-" * 48 + "+"]
    for line in box:
        t.row(("  " + line, CYAN, True))
        t.snap(90)
    t.nl()
    t.row(("  Welcome! Pick a number. Every tool shows a preview first -", TEXT, False))
    t.row(("  nothing changes until you say yes, and you can undo.", TEXT, False))
    t.snap(500)
    t.nl()
    t.row((" " + "=" * 64, CYAN, False))
    t.row((" Toolbox - what would you like to do?", CYAN, True))
    t.row((" " + "=" * 64, CYAN, False))
    menu = ["Tidy a folder into category folders", "Rename many files at once",
            "Archive old files", "Find duplicate files", "Remove empty folders",
            "What is using my disk space?", "Back up a folder (zip)", "Undo the last change"]
    numbers = ["1", "2", "3", "4", "5", "6", "8", "10"]
    for n, label in zip(numbers, menu):
        t.row(("   " + n.rjust(2) + ".  ", CYAN, True), (label, TEXT, False))
    t.row(("    ...", DIM, False))
    t.row(("    0.  ", CYAN, True), ("Exit", TEXT, False))
    for seg in ask:
        t.add(*seg)
    t.snap(900)
    t.type("1", CYAN, True)
    t.snap(300)
    t.nl()

    # --- choose folder
    t.nl()
    t.row((" Which folder do you want to tidy?", WHITE, True))
    t.row(("    1.  ", CYAN, True), ("This folder  ", TEXT, False), ("(C:\\Users\\you\\Downloads)", DIM, False),
          ("  - just press Enter", GREEN, False))
    for n, label in (("2", "Downloads"), ("3", "Desktop"), ("4", "Documents"), ("5", "Browse...")):
        t.row(("    " + n + ".  ", CYAN, True), (label, TEXT, False))
    t.row(("    0.  ", CYAN, True), ("Back", TEXT, False))
    for seg in ask:
        t.add(*seg)
    t.snap(1300)
    t.nl()

    # --- spinner
    frames = ["[" + " " * p + "==" + " " * (6 - p) + "]" for p in list(range(0, 7)) + list(range(5, 0, -1))]
    t.nl()
    for i in range(12):
        t.lines[-1] = [("  ", TEXT, False), (frames[i % len(frames)], CYAN, False), (" Looking at your files", TEXT, False)]
        t.snap(85, cursor=False)
    t.lines[-1] = [("  ", TEXT, False), ("[ok]", GREEN, True), (" Looking at your files", TEXT, False)]
    t.nl()

    # --- preview
    t.nl()
    t.row((" Step 2 - Preview (nothing has moved yet)", CYAN, True))
    t.row(("  I found ", TEXT, False), ("14 file(s)", WHITE, True), (" to organize into ", TEXT, False),
          ("4 folder(s)", WHITE, True), (":", TEXT, False))
    t.snap(650)
    t.nl()
    t.row(("  Images/", GREEN, True), ("   6 file(s)", TEXT, False))
    t.row(("      Pictures, photos, screenshots and icons.", DIM, False))
    for ext, n, name in ((".jpeg", 3, "JPEG photo"), (".svg", 1, "SVG vector graphic"), (".png", 2, "PNG image")):
        t.row(("      " + ext.ljust(8), CYAN, False), (str(n) + " x ", DIM, False), (name, TEXT, False))
    t.snap(900)
    t.nl()
    t.row(("  Documents/", GREEN, True), ("   5 file(s)", TEXT, False))
    t.row(("      Text documents, PDFs, notes and e-books.", DIM, False))
    t.row(("      " + ".pdf".ljust(8), CYAN, False), ("5 x ", DIM, False), ("PDF document", TEXT, False))
    t.snap(700)
    t.row(("  Videos/", GREEN, True), ("   2 file(s)   ", TEXT, False), (".mp4", CYAN, False))
    t.row(("  Archives/", GREEN, True), ("   1 file(s)   ", TEXT, False), (".zip", CYAN, False))
    t.snap(500)
    t.nl()
    t.row(("  Left alone on purpose:", YELLOW, True))
    t.row(("    1 x unfinished download", TEXT, False))
    t.row(("        Still downloading (or interrupted). Moving it would break the download.", DIM, False))
    t.snap(1400)
    t.nl()
    t.row(("   1.  ", CYAN, True), ("Yes - tidy up now (you can undo it later)", TEXT, False))
    t.row(("   2.  ", CYAN, True), ("Explain the file types in this list", TEXT, False))
    t.row(("   3.  ", CYAN, True), ("Show every file and where it will go", TEXT, False))
    t.row(("   0.  ", CYAN, True), ("Cancel - change nothing", TEXT, False))
    for seg in ask:
        t.add(*seg)
    t.snap(1500)
    t.type("1", CYAN, True)
    t.snap(300)
    t.nl()

    # --- progress bar
    jobs = [("IMG_2041.jpeg", "Images"), ("logo.svg", "Images"), ("screenshot.png", "Images"),
            ("holiday.jpeg", "Images"), ("diagram.png", "Images"), ("selfie.jpeg", "Images"),
            ("report_final.pdf", "Documents"), ("invoice (1).pdf", "Documents"), ("cv.pdf", "Documents"),
            ("notes.pdf", "Documents"), ("ticket.pdf", "Documents"), ("clip.mp4", "Videos"),
            ("movie.mp4", "Videos"), ("backup.zip", "Archives")]
    t.nl()
    for i, (name, dest) in enumerate(jobs, 1):
        filled = int(24 * i / len(jobs))
        pct = int(100 * i / len(jobs))
        t.lines[-1] = [("  [", TEXT, False), ("#" * filled, GREEN, False), ("." * (24 - filled), DIM, False),
                       ("] " + str(pct).rjust(3) + "%  " + str(i).rjust(2) + "/" + str(len(jobs)) + "  ", TEXT, False),
                       (name, WHITE, False), ("  ->  " + dest + "/", DIM, False)]
        t.snap(150, cursor=False)
    t.nl()
    for _ in range(8):
        sp = "".join(random.choice(["*", "+", ".", "o", " ", " "]) for _ in range(7))
        t.lines[-1] = [("  " + sp + "  ", YELLOW, False), ("All done!", GREEN, True), ("  " + sp[::-1], YELLOW, False)]
        t.snap(75, cursor=False)
    t.lines[-1] = [("  ", TEXT, False), ("[DONE]", GREEN, True), (" Tidied ", TEXT, False), ("14 files", WHITE, True),
                   (" into ", TEXT, False), ("4 folders", WHITE, True), (".", TEXT, False)]
    t.nl()
    t.row(("  ", TEXT, False), ("(i)", CYAN, True), (" Made a mistake? Choose 10 - Undo the last change.", TEXT, False))
    t.snap(2200)

    # --- undo
    t.nl()
    t.add(prompt, DIM)
    t.snap(500)
    t.type("tidymate undo .", WHITE, True)
    t.snap(350)
    t.nl()
    t.nl()
    for i in range(10):
        t.lines[-1] = [("  ", TEXT, False), (frames[i % len(frames)], CYAN, False), (" Putting files back", TEXT, False)]
        t.snap(85, cursor=False)
    t.lines[-1] = [("  ", TEXT, False), ("[ok]", GREEN, True), (" Restored ", TEXT, False), ("14 file(s)", WHITE, True),
                   (" - everything is back where it was.", TEXT, False)]
    t.nl()
    t.add(prompt, DIM)
    t.snap(3200)
    save_gif(t.frames, os.path.join(HERE, "demo.gif"), colors=72)


# =====================================================================
#  2. Animated banner
# =====================================================================
def banner_frame(typed, chips_shown, cursor=True):
    w, h = 1200, 340
    img = Image.new("RGB", (w, h), OUTER)
    d = ImageDraw.Draw(img)
    d.rectangle((0, h - 8, w, h), fill=TEAL)
    draw_logo(d, 70, 62, 150)
    d.text((250, 40), "TidyMate", font=find_font(SANS_B, 92), fill=WHITE)
    d.text((254, 156), "Python file organizer with preview and undo", font=find_font(SANS, 30), fill=DIM)
    d.rounded_rectangle((254, 212, 254 + 440, 262), radius=10, fill=PANEL, outline=BORDER, width=2)
    f = find_font(MONO_B, 26)
    d.text((274, 222), "$ ", font=f, fill=GREEN)
    d.text((274 + f.getlength("$ "), 222), typed + ("_" if cursor else ""), font=f, fill=WHITE)
    labels = ["Preview first", "Undo everything", "Nothing deleted", "No dependencies"]
    x, fc = 254, find_font(SANS_B, 20)
    for i, label in enumerate(labels):
        if i < chips_shown:
            x = chip(d, x, 282, label, fc)
        else:
            x += fc.getlength(label) + 40
    return img


def build_banner():
    frames, cmd = [], "pip install tidymate"
    frames.append((banner_frame("", 0), 500))
    for i in range(1, len(cmd) + 1):
        frames.append((banner_frame(cmd[:i], 0), 70))
    frames.append((banner_frame(cmd, 0, cursor=False), 450))
    for n in range(1, 5):
        frames.append((banner_frame(cmd, n, cursor=False), 380))
    frames.append((banner_frame(cmd, 4, cursor=False), 3200))
    save_gif(frames, os.path.join(HERE, "banner.gif"), colors=48)


# =====================================================================
#  3. Before / after
# =====================================================================
def folder_icon(d, x, y, s=26, fill=TEAL):
    d.rounded_rectangle((x, y, x + s * 0.45, y + s * 0.3), radius=3, fill=fill)
    d.rounded_rectangle((x, y + s * 0.15, x + s, y + s * 0.8), radius=4, fill=fill)


def build_before_after():
    w, h = 1100, 490
    img = Image.new("RGB", (w, h), OUTER)
    d = ImageDraw.Draw(img)
    fm, fmb = find_font(MONO, 18), find_font(MONO_B, 18)
    fs, fsb = find_font(SANS, 20), find_font(SANS_B, 22)

    # cards
    for x0, label, color in ((30, "BEFORE", RED), (600, "AFTER", GREEN)):
        d.rounded_rectangle((x0, 60, x0 + 470, 462), radius=14, fill=PANEL, outline=BORDER, width=2)
        d.rounded_rectangle((x0 + 20, 80, x0 + 130, 112), radius=16, fill=color)
        d.text((x0 + 40, 85), label, font=find_font(SANS_B, 18), fill=OUTER)
        d.text((x0 + 150, 83), "Downloads" + (" (messy)" if label == "BEFORE" else " (tidy)"), font=fsb, fill=WHITE)

    files = [("IMG_2041.jpeg", BLUE), ("report_final_v3.pdf", RED), ("setup.msi", YELLOW), ("holiday.mp4", MAGENTA),
             ("logo.svg", BLUE), ("notes.txt", RED), ("invoice (1).pdf", RED), ("song.mp3", MAGENTA),
             ("data.csv", GREEN), ("backup.zip", YELLOW), ("screenshot.png", BLUE),
             ("movie.mp4.crdownload", DIM)]
    for i, (name, color) in enumerate(files):
        y = 130 + i * 24
        d.rounded_rectangle((52, y + 5, 64, y + 17), radius=3, fill=color)
        d.text((76, y), name, font=fm, fill=TEXT)
    d.text((76, 130 + len(files) * 24), "+ 3 more files ...", font=fm, fill=DIM)

    # arrow
    d.polygon([(512, 250), (562, 250), (562, 232), (592, 262), (562, 292), (562, 274), (512, 274)], fill=TEAL)
    label_font = find_font(SANS_B, 17)
    d.text((550 - label_font.getlength("tidymate") / 2, 214), "tidymate", font=label_font, fill=TEAL)

    rows = [("Images/", 6, ".jpeg  .svg  .png"), ("Documents/", 5, ".pdf"), ("Videos/", 2, ".mp4"), ("Archives/", 1, ".zip")]
    for i, (name, n, exts) in enumerate(rows):
        y = 135 + i * 62
        folder_icon(d, 624, y + 4)
        d.text((664, y), name, font=fmb, fill=WHITE)
        d.text((664, y + 26), exts, font=find_font(MONO, 15), fill=DIM)
        d.rounded_rectangle((990, y + 2, 1042, y + 30), radius=14, fill=(33, 40, 49), outline=BORDER)
        d.text((1016 - find_font(MONO_B, 16).getlength(str(n)) / 2, y + 6), str(n), font=find_font(MONO_B, 16), fill=GREEN)
    d.rounded_rectangle((624, 392, 1046, 428), radius=8, fill=(45, 38, 20), outline=YELLOW)
    d.text((640, 399), "movie.mp4.crdownload - left alone", font=find_font(MONO, 15), fill=YELLOW)
    d.text((30, 20), "One command. Preview first. Undo any time.", font=find_font(SANS_B, 24), fill=WHITE)
    img.save(os.path.join(HERE, "before-after.png"), optimize=True)
    print("wrote before-after.png")


# =====================================================================
#  4. GitHub social preview (1280x640)
# =====================================================================
def build_social():
    w, h = 1280, 640
    img = Image.new("RGB", (w, h), OUTER)
    d = ImageDraw.Draw(img)
    d.rectangle((0, h - 14, w, h), fill=TEAL)
    draw_logo(d, 90, 120, 210)
    d.text((340, 90), "TidyMate", font=find_font(SANS_B, 128), fill=WHITE)
    d.text((346, 250), "Python file organizer with preview and undo", font=find_font(SANS, 40), fill=TEXT)
    line2, f2 = "Sort Downloads  -  Rename  -  Find duplicates  -  Back up", find_font(SANS, 28)
    assert 346 + f2.getlength(line2) < w - 60, "social preview text is too wide"
    d.text((346, 310), line2, font=f2, fill=DIM)
    d.rounded_rectangle((346, 390, 346 + 560, 460), radius=14, fill=PANEL, outline=BORDER, width=2)
    f = find_font(MONO_B, 38)
    d.text((372, 401), "$ ", font=f, fill=GREEN)
    d.text((372 + f.getlength("$ "), 401), "pip install tidymate", font=f, fill=WHITE)
    x = 346
    fc = find_font(SANS_B, 24)
    for label in ("Preview first", "Undo everything", "Nothing deleted"):
        x = chip(d, x, 500, label, fc)
    d.text((90, 570), "github.com/Anand2k29/TidyMate", font=find_font(MONO, 24), fill=DIM)
    img.save(os.path.join(HERE, "social-preview.png"), optimize=True)
    print("wrote social-preview.png")


if __name__ == "__main__":
    build_banner()
    build_demo()
    build_before_after()
    build_social()

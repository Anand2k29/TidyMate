#!/usr/bin/env python3
"""
ui.py - small, dependency-free terminal helpers for the guided mode.

Gives you: colours, an animated banner, a spinner, a progress bar, numbered menus,
yes/no questions and a little "all done" celebration.

Everything degrades gracefully: if the output is not a real terminal (a pipe, a log
file, a test) or you pass plain=True, there are no colours or animations - just
simple lines of text.
"""
import os
import random
import shutil
import sys
import threading
import time

STYLES = {"bold": "1", "dim": "2", "red": "31", "green": "32", "yellow": "33",
          "blue": "34", "magenta": "35", "cyan": "36"}


def _enable_windows_ansi():
    """Turn on colour codes in the Windows console. Returns True if it worked."""
    if os.name != "nt":
        return True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)                  # STD_OUTPUT_HANDLE
        mode = ctypes.c_ulong()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel32.SetConsoleMode(handle, mode.value | 0x0004))
    except Exception:
        return False


class Spinner:
    """Animated 'working...' indicator. Use:  with ui.spinner("Looking at files"): ..."""

    # A little block bouncing left and right:  [==      ]  [ ==     ] ...
    FRAMES = ["[" + " " * p + "==" + " " * (6 - p) + "]"
              for p in list(range(0, 7)) + list(range(5, 0, -1))]

    def __init__(self, ui, message, min_seconds=0.0):
        self.ui, self.message, self.min_seconds = ui, message, min_seconds
        self._stop = threading.Event()
        self._thread = None
        self._started = 0.0

    def _run(self):
        index = 0
        while not self._stop.is_set():
            frame = self.FRAMES[index % len(self.FRAMES)]
            self.ui.write("\r  " + self.ui.c(frame, "cyan") + " " + self.message)
            index += 1
            time.sleep(0.09)

    def __enter__(self):
        self._started = time.time()
        if self.ui.animate:
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()
        else:
            self.ui.say("  ... " + self.message)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.ui.animate:
            remaining = self.min_seconds - (time.time() - self._started)
            if remaining > 0:                      # let the animation be seen
                time.sleep(remaining)
            self._stop.set()
            self._thread.join()
            self.ui.write("\r" + " " * (len(self.FRAMES[0]) + len(self.message) + 6) + "\r")
        if exc_type is None:
            self.ui.say("  " + self.ui.c("[ok]", "green", "bold") + " " + self.message)
        return False


class UI:
    def __init__(self, plain=False, input_func=None):
        if hasattr(sys.stdout, "reconfigure"):          # never crash on odd file names
            sys.stdout.reconfigure(errors="replace")
        tty = sys.stdout.isatty()
        self.animate = tty and not plain
        ansi = _enable_windows_ansi() if tty else False
        self.color = ansi and not plain and "NO_COLOR" not in os.environ
        self.width = max(60, min(shutil.get_terminal_size((80, 20)).columns, 100))
        self._input = input_func or input
        self._last_line = 0

    # ---- low level -------------------------------------------------------
    def write(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()

    def c(self, text, *styles):
        """Colour/bold a piece of text (does nothing when colour is off)."""
        if not self.color or not styles:
            return text
        codes = ";".join(STYLES[s] for s in styles)
        return "\033[{}m{}\033[0m".format(codes, text)

    def say(self, text=""):
        print(text)

    # ---- message styles --------------------------------------------------
    def info(self, text):
        self.say("  " + self.c("(i)", "cyan", "bold") + " " + text)

    def ok(self, text):
        self.say("  " + self.c("[ok]", "green", "bold") + " " + text)

    def warn(self, text):
        self.say("  " + self.c("[!]", "yellow", "bold") + " " + text)

    def error(self, text):
        self.say("  " + self.c("[x]", "red", "bold") + " " + text)

    def heading(self, text):
        line = "=" * min(self.width - 2, 64)
        self.say()
        self.say(" " + self.c(line, "cyan"))
        self.say(" " + self.c(text, "bold", "cyan"))
        self.say(" " + self.c(line, "cyan"))

    def wrap(self, text, indent=4, width=None):
        import textwrap
        width = width or min(self.width, 90)
        return textwrap.fill(text, width=width, initial_indent=" " * indent,
                             subsequent_indent=" " * indent)

    # ---- animations ------------------------------------------------------
    def typewriter(self, text, delay=0.012):
        if not self.animate:
            self.say(text)
            return
        for ch in text:
            self.write(ch)
            time.sleep(delay)
        self.write("\n")

    def banner(self):
        lines = ["T I D Y M A T E",
                 "Tidy messy folders - with preview and undo"]
        inner = max(len(x) for x in lines) + 6
        box = ["+" + "-" * inner + "+"] + \
              ["|" + x.center(inner) + "|" for x in lines] + \
              ["+" + "-" * inner + "+"]
        self.say()
        for row in box:
            self.say("  " + self.c(row, "cyan", "bold"))
            if self.animate:
                time.sleep(0.09)

    def progress(self, i, total, label=""):
        """Draw (or update) a progress bar:  [#########...............]  37%"""
        if not self.animate:
            self.say("  [{}/{}] {}".format(i, total, label))
            return
        bar_width = 24
        filled = int(bar_width * i / total) if total else bar_width
        bar = "#" * filled + "." * (bar_width - filled)
        pct = int(100 * i / total) if total else 100
        room = max(10, self.width - bar_width - 22)
        line = "  [{}] {:>3}%  {:>3}/{}  {}".format(
            self.c(bar, "green"), pct, i, total, label[:room])
        visible = len("  [] 100%  000/000  ") + bar_width + len(label[:room])
        pad = max(0, self._last_line - visible)
        self.write("\r" + line + " " * pad)
        self._last_line = visible

    def end_progress(self):
        if self.animate:
            self.write("\n")
        self._last_line = 0

    def spinner(self, message, min_seconds=0.6):
        return Spinner(self, message, min_seconds)

    def celebrate(self, text):
        if self.animate:
            marks = ["*", "+", ".", "o", " ", " "]
            for _ in range(16):
                sparkle = "".join(random.choice(marks) for _ in range(7))
                self.write("\r  " + self.c(sparkle, "yellow") + "  " +
                           self.c(text, "green", "bold") + "  " + self.c(sparkle[::-1], "yellow"))
                time.sleep(0.06)
            self.write("\r" + " " * (len(text) + 30) + "\r")
        self.say("  " + self.c("[DONE]", "green", "bold") + " " + self.c(text, "bold"))

    # ---- questions -------------------------------------------------------
    def ask(self, prompt):
        """Ask a free-text question. EOFError (Ctrl+Z / closed input) is passed up."""
        return self._input("  " + self.c(">", "green", "bold") + " " + prompt + ": ").strip()

    def choose(self, options, back="Go back", default=None):
        """Show a numbered list. Returns the 0-based index, or None for 'back'."""
        for number, text in enumerate(options, 1):
            self.say("   {}  {}".format(self.c("{:>2}.".format(number), "cyan", "bold"), text))
        if back:
            self.say("   {}  {}".format(self.c(" 0.", "cyan", "bold"), back))
        while True:
            raw = self.ask("Type a number, then press Enter")
            if raw.isdigit():
                number = int(raw)
                if back and number == 0:
                    return None
                if 1 <= number <= len(options):
                    return number - 1
            elif raw == "" and default is not None:
                return default
            self.warn("Please type one of the numbers shown above (for example 1).")

    def confirm(self, question, default=False):
        hint = "[Y/n]" if default else "[y/N]"
        raw = self.ask("{} {}".format(question, hint)).lower()
        if raw == "":
            return default
        return raw in ("y", "yes")

    def pause(self, text="Press Enter to continue"):
        self.ask(text)

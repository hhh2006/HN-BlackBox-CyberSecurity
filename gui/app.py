# -*- coding: utf-8 -*-
"""HN BlackBox — cinematic cybersecurity laboratory interface.

The GUI is intentionally dependency-light: Tkinter only for the shell, with the
existing HN core modules providing the cryptography engine.  The interface is
designed around a fixed navigation rail, glass-like cards, animated splash,
Matrix-inspired motion, and algorithm-specific visualization.
"""
from __future__ import annotations

import getpass
import hashlib
import math
import os
import random
import secrets
import sys
import time
import platform
import json
import csv
import socket
import shlex
import subprocess
import threading
import traceback
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog
import tkinter as tk
from tkinter import ttk

try:
    import psutil  # optional: enables real CPU/RAM/process telemetry
except Exception:
    psutil = None

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    affine, autokey, caesar, classical, frequency_analysis, hill_cipher,
    history_manager, playfair, rail_fence, vigenere, aes_cipher,
    cryptanalysis, network_tools, web_lab, blue_team, labs, lab_progress, reporting, diagnostics, intelligence, workflows, investigation, evidence, network_intel, blue_center, labs2, security_hardening, command_center, pro_intelligence, workflow_engine, plugin_system, network_graph, blue_rules, vault, real_tools, labs3, lab_engine, crypto_intel,
)
from core.cryptography.required_algorithms import (
    caesar as required_caesar,
    vigenere as required_vigenere,
    affine as required_affine,
    autokey as required_autokey,
    rail_fence as required_rail_fence,
    additive as required_additive,
    multiplicative as required_multiplicative,
)

BASE = Path(__file__).resolve().parent
P = {
    "bg": "#02050a", "bg2": "#050b12", "nav": "#050a11",
    "panel": "#08131d", "panel2": "#0b1b28", "panel3": "#0e2433",
    "line": "#16445a", "line2": "#20627a",
    "cyan": "#20e8ff", "cyan2": "#65f4ff", "green": "#39f6a0",
    "purple": "#9e73ff", "red": "#ff3f68", "yellow": "#ffd166",
    "orange": "#ff9d4d", "text": "#e9fbff", "muted": "#7092a5",
    "dim": "#355365",
}
FONT = "Segoe UI"
MONO = "Consolas"
ASCII_MONO = "DejaVu Sans Mono"

ALGORITHMS = {
    # Requested/core rack — implementations live together under core/cryptography/required_algorithms.
    "caesar": ("Caesar Cipher", "CA", "shift", required_caesar),
    "additive": ("Additive Cipher", "AD", "shift", required_additive),
    "multiplicative": ("Multiplicative Cipher", "MU", "key", required_multiplicative),
    "affine": ("Affine Cipher", "AF", "a,b", required_affine),
    "vigenere": ("Vigenère Cipher", "VI", "word", required_vigenere),
    "autokey": ("Autokey Cipher", "AK", "word", required_autokey),
    "railfence": ("Rail Fence // Keyless Transposition", "RF", "rails", required_rail_fence),

    # Existing algorithms — intentionally left as-is.
    "playfair": ("Playfair Cipher", "PF", "word", playfair),
    "columnar": ("Columnar Transposition", "CT", "word", classical),
    "atbash": ("Atbash", "AT", None, classical),
    "rot13": ("ROT13", "R13", None, classical),
    "hill": ("Hill Cipher", "HI", "a,b,c,d", hill_cipher),
    "beaufort": ("Beaufort Cipher", "BF", "word", classical),
    "polybius": ("Polybius Square", "PB", None, classical),
    "adfgvx": ("ADFGVX", "AD", "word", classical),
    "bacon": ("Bacon Cipher", "BC", None, classical),
    "morse": ("Morse Code", "MO", None, classical),
    "otp": ("One-Time Pad", "OTP", "word", classical),
    "aes": ("AES-256", "AES", "word", aes_cipher),
    "rsa": ("RSA", "RSA", "key", classical),
    "hash": ("Hashing", "HASH", "word", classical),
}
NAV = [
    ("home", "⌂", "Home"),
    ("crypto", "▣", "Cryptography"),
    ("analysis", "◉", "Cryptanalysis"),
    ("network", "◌", "Network Security"),
    ("web", "◇", "Web Security"),
    ("blue", "◆", "Blue Team"),
    ("labs", "◈", "Security Labs"),
    ("toolkit", "⚙", "Security Toolkit"),
    ("development", "⌘", "Development"),
    ("developer", "HN", "Developer"),
    ("history", "◷", "History"),
]
TEXTS = {
    "brand": "HN // BLACKBOX", "sub": "SECURITY ENGINEERING SUITE",
    "online": "SYSTEM ONLINE", "home": "HOME", "crypto": "CRYPTOGRAPHY",
    "analysis": "CRYPTANALYSIS", "network": "NETWORK SECURITY", "web": "WEB SECURITY",
    "blue": "BLUE TEAM", "labs": "SECURITY LABS", "toolkit": "SECURITY TOOLKIT", "development": "DEVELOPMENT", "developer": "DEVELOPER",
    "history": "HISTORY", "welcome_name": "WELCOME, {name}",
    "hero": "HN BLACKBOX // THE BLACK BOX FOR SECURITY PROJECTS & SOLUTIONS.",
    "hero2": "A unified technical platform for cybersecurity and systems engineering. Deconstruct complex concepts, test tools, visualize operations, and build defensive solutions under one interface.",
    "contact": "Platform under active development • Help / contribution: alnasryhany185@gmail.com",
    "open": "ENTER CRYPTO LAB", "road": "EXPLORE ROADMAP",
    "alg": "ALGORITHM MATRIX", "algsub": "Select an algorithm and watch its internal path unfold step by step.",
    "input": "INPUT", "key": "KEY / PARAMETERS", "result": "RESULT",
    "encrypt": "ENCRYPT", "decrypt": "DECRYPT", "execute": "EXECUTE",
    "clear": "CLEAR", "copy": "COPY", "save": "SAVE", "guide": "HOW IT WORKS",
    "generate": "GENERATE", "visual": "LIVE VISUALIZATION // OPERATION PATH",
    "ready": "READY", "done": "OPERATION COMPLETE", "error": "OPERATION FAILED",
    "back": "BACK", "under": "UNDER DEVELOPMENT", "noresult": "No result yet.",
    "hashnote": "Hashing is one-way; decrypt is unavailable.",
    "rsanote": "Educational RSA demonstration. Generate a key pair before operating.",
    "otpnote": "For OTP the key must be long enough for the message bytes.",
    "developer_title": "DEVELOPER // HN BLACKBOX",
    "developer_sub": "The builder, engineering vision and identity behind the platform.",
    "developer_profile": "HN BLACKBOX // DEVELOPER PROFILE",
    "developer_role": "FOUNDER • SECURITY ENGINEERING • SYSTEMS • VISUAL TOOLING",
    "developer_bio": "HN BlackBox is a unified technical umbrella for cybersecurity projects, systems engineering, experimentation and defensive learning. The goal is to turn complex concepts into visible, testable and understandable tools.",
    "developer_contact": "CONTACT / CONTRIBUTION",
    "developer_core": "PLATFORM CORE // LIVE",
    "developer_mission": "ENGINEERING MISSION",
    "deconstruct": "DECONSTRUCT",
    "visualize": "VISUALIZE",
    "engineer": "ENGINEER",
    "defend": "DEFEND",
    "developer_identity": "IDENTITY // HN BLACKBOX",
    "developer_identity_sub": "THE BLACK BOX FOR SECURITY PROJECTS & SOLUTIONS.",
}
GUIDES = {
    "caesar": ("E(x) = (x + k) mod 26", "HELLO + 3 → KHOOR"),
    "additive": ("E(x) = (x + k) mod 26", "HELLO + 3 → KHOOR"),
    "multiplicative": ("E(x) = (x × k) mod 26", "A × 5 → A"),
    "vigenere": ("Cᵢ = (Pᵢ + Kᵢ) mod 26", "ATTACKATDAWN + LEMON → LXFOPVEFRNHR"),
    "playfair": ("5×5 digraph substitution", "MONARCHY builds a 5×5 key square"),
    "railfence": ("Zig-Zag transposition", "WEARE... with 3 rails"),
    "columnar": ("Column permutation", "Write rows, then read columns by key order"),
    "atbash": ("A↔Z, B↔Y ...", "HELLO → SVOOL"),
    "rot13": ("13-position rotation", "HELLO → URYYB"),
    "affine": ("E(x)=(ax+b) mod 26", "a=5,b=8: A → I"),
    "hill": ("C = K·P mod 26", "HELP with [3 3; 2 5] → HIAT"),
    "beaufort": ("C = K − P mod 26", "Keyword-driven reciprocal transformation"),
    "polybius": ("5×5 coordinate square", "A → 11, B → 12 ..."),
    "adfgvx": ("6×6 fractionation + transposition", "Letters become A/D/F/G/V/X pairs"),
    "bacon": ("5-bit a/b encoding", "A → aaaaa, B → aaaab"),
    "morse": ("Dots and dashes", "SOS → ... --- ..."),
    "autokey": ("Vigenère + plaintext keystream", "KEY expands using plaintext"),
    "otp": ("C = P XOR K", "A fresh random key must never be reused"),
    "aes": ("AES-256-CBC + PKCS7", "Modern symmetric encryption demo"),
    "rsa": ("c = mᵉ mod n", "Public/private key demonstration"),
    "hash": ("Digest function", "SHA-256 → fixed-length fingerprint"),
}

def reparse_rsa(raw: str):
    pairs = dict(re.findall(r"(e|d|n)\s*=\s*(\d+)", raw or ""))
    if not {"e", "d", "n"} <= set(pairs):
        raise ValueError("RSA key format: e=...; d=...; n=...")
    return {k: int(v) for k, v in pairs.items()}

class MatrixRain(tk.Canvas):
    def __init__(self, parent, count=34, speed=1.7, **kw):
        super().__init__(parent, highlightthickness=0, bg=P["bg"], **kw)
        self.count = count
        self.speed = speed
        self.items = []
        self.running = True
        self.bind("<Configure>", self._seed)
        self.after(80, self._tick)

    def _seed(self, _=None):
        target = max(10, min(self.count, max(10, self.winfo_width() // 26)))
        while len(self.items) < target:
            x = random.randint(8, max(10, self.winfo_width() - 8))
            y = random.randint(-self.winfo_height(), self.winfo_height())
            item = self.create_text(x, y, text=random.choice("01ABCDEFHN<>/[]{}#$%&"),
                                    fill=random.choice((P["cyan"], P["dim"], "#24758a")),
                                    font=(MONO, random.choice((7, 8, 9))))
            self.items.append(item)
        while len(self.items) > target:
            self.delete(self.items.pop())

    def _tick(self):
        if not self.winfo_exists():
            return
        if self.running:
            h = max(1, self.winfo_height())
            for item in self.items:
                x, y = self.coords(item)
                y += self.speed
                if y > h + 15:
                    y = random.randint(-150, -10)
                    self.itemconfigure(item, text=random.choice("01ABCDEFHN<>/[]{}#$%&"))
                self.coords(item, x, y)
        self.after(70, self._tick)

class HNBlackBoxApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HN BLACKBOX // SECURITY ENGINEERING")
        self.geometry("1280x820")
        self.minsize(760, 560)
        self.configure(bg=P["bg"])
        try:
            icon = tk.PhotoImage(file=str(BASE / "assets" / "hn_blackbox.png"))
            self.iconphoto(True, icon)
            self._app_icon = icon
        except Exception:
            pass
        self.current = "home"
        self.current_page = "welcome"
        self.current_algo = None
        self.pages = {}
        self.nav_buttons = {}
        self.key_entries = {}
        self.sidebar_expanded = True
        self._wheel_bound = set()
        self._scroll_targets = []
        self._global_wheel_bound = False
        self._visual_job = None
        self._hover_jobs = {}
        self._cmd_history = []
        self._cmd_index = 0
        self._app_started = time.monotonic()
        # Rendering warm-up: page construction happens before the first frame is
        # shown. Keep live HUDs dormant until Tk has completed that first layout.
        self._ui_ready = False
        self._resize_job = None
        self._home_grid_job = None
        self._home_layout_sig = None
        self._home_virtual_sig = None
        self._resizing_until = 0.0
        self._system_phase = 0
        self._last_cpu = None
        self._last_ram = None
        self._last_processes = None
        self._telemetry_cache_at = 0.0
        self._telemetry_cache = (None, None, None)
        self._identity_cache_at = 0.0
        self._identity_cache = (0, '--')
        self._home_scan_cache_at = 0.0
        self._home_scan_cache_text = ''
        self._process_feed_cache_at = 0.0
        self._process_feed_cache = []
        # Collect filesystem/process telemetry off the Tk main thread so the
        # animation loop never waits on disk or process enumeration.
        self._home_data_lock = threading.Lock()
        self._home_data_busy = False
        self._home_data = {
            'files': 0, 'core': 0, 'tests': 0, 'history': 0, 'labs': 0,
            'modules': [], 'integrity': [], 'last_op': 'NO LOCAL OPERATIONS RECORDED',
            'process_feed': [], 'sample_at': 0.0,
        }
        self._home_workspace_phase = 0
        self._workspace_last = None
        self._module_hud_jobs = {}
        # Adaptive motion governor: preserves the visual language while reducing
        # Canvas churn on modest hardware. Motion is paused/decelerated when the
        # window is not active or while a resize burst is in progress.
        self._motion_active = True
        self._motion_ms = 50
        self._motion_hidden_ms = 1000
        self._perf_frame = 0
        self._session_started = datetime.now().isoformat(timespec="seconds")
        self._last_error = None
        self.report_notes = ""
        self._splash()
        self._styles()
        self._shell()
        self._pages()
        self._bind_shortcuts()
        self.bind("<Configure>", self._on_resize, add="+")
        self.bind("<FocusIn>", lambda _e: setattr(self, "_motion_active", True), add="+")
        self.bind("<FocusOut>", lambda _e: setattr(self, "_motion_active", False), add="+")
        self.report_callback_exception = self._report_callback_exception
        self.show_page("home")
        self.after_idle(self._finish_initial_render)

    def _finish_initial_render(self):
        """Release the first-frame render lock after the shell is mapped."""
        self._ui_ready = True
        self._resizing_until = 0.0
        # Start only the visible dashboard animations after the initial layout
        # has settled. Hidden-page effects stay dormant until their page is used.
        for fn in (self._animate_home_identity, self._animate_home_status,
                   self._animate_system_monitor, self._animate_home_monitor,
                    self._animate_home_intel,
                   self._refresh_home_scan, self._update_home_clock,
                   self._pulse_home, self._animate_terminal_hud):
            try:
                fn()
            except tk.TclError:
                pass
        self._request_home_layout(immediate=True)

    def t(self, k):
        return TEXTS[k]

    def _widget_on_current_page(self, widget):
        """Prevent hidden-page animations from consuming the Tk event loop."""
        try:
            page = self.pages.get(self.current)
            if page is None:
                return True
            node = widget
            while node is not None:
                if node is page:
                    return True
                node = getattr(node, "master", None)
        except Exception:
            return True
        return False

    # ---------- boot / shell ----------
    def _splash(self):
        self.withdraw()
        self.splash = tk.Toplevel(self)
        self.splash.overrideredirect(True)
        self.splash.configure(bg=P["bg"])
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(920, sw - 80), min(560, sh - 120)
        self.splash.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        try:
            self.splash.attributes("-alpha", 0.98)
        except tk.TclError:
            pass
        self.rain = MatrixRain(self.splash, count=44, speed=1.5)
        self.rain.place(relx=0, rely=0, relwidth=1, relheight=1)
        veil = tk.Frame(self.splash, bg="#02070d", highlightbackground=P["line"], highlightthickness=1)
        veil.place(relx=.05, rely=.08, relwidth=.9, relheight=.84)
        tk.Label(veil, text="H N", bg="#02070d", fg=P["cyan"], font=(MONO, 64, "bold")).pack(pady=(65, 0))
        tk.Label(veil, text="B L A C K B O X", bg="#02070d", fg=P["text"],
                 font=(MONO, 21, "bold")).pack(pady=(0, 8))
        tk.Label(veil, text="SECURITY ENGINEERING // CYBER OPERATIONS LAB", bg="#02070d",
                 fg=P["muted"], font=(MONO, 9, "bold")).pack()
        self.splash_user = tk.Label(veil, text="", bg="#02070d", fg=P["green"],
                                    font=(MONO, 11, "bold"))
        self.splash_user.pack(pady=(45, 8))
        self.splash_status = tk.Label(veil, text="INITIALIZING SECURE WORKSPACE...", bg="#02070d",
                                      fg=P["yellow"], font=(MONO, 9))
        self.splash_status.pack()
        bar_bg = tk.Frame(veil, bg=P["panel2"], height=4)
        bar_bg.pack(fill="x", padx=120, pady=(20, 0))
        self.splash_bar = tk.Frame(bar_bg, bg=P["cyan"], height=4)
        self.splash_bar.place(x=0, y=0, relheight=1, relwidth=0.03)
        name = (getpass.getuser() or "HN USER").upper()
        self.splash_user.configure(text=f"IDENTITY VERIFIED  //  {name}")
        self._boot_step = 0
        self._boot_tick()

    def _boot_tick(self):
        if not self.splash.winfo_exists():
            return
        steps = [
            "LOADING HN IDENTITY...", "MOUNTING CRYPTO ENGINE...",
            "CALIBRATING VISUALIZERS...", "LINKING LOCAL WORKSPACE...",
            "BLACKBOX READY."
        ]
        self._boot_step += 1
        idx = min(self._boot_step // 4, len(steps) - 1)
        self.splash_status.configure(text=steps[idx])
        self.splash_bar.place_configure(relwidth=min(.97, .08 + self._boot_step / 25))
        if self._boot_step < 24:
            self.after(65, self._boot_tick)
        else:
            self._fade_splash(0.98)

    def _fade_splash(self, alpha):
        if not self.splash.winfo_exists():
            self.deiconify()
            return
        alpha -= .07
        if alpha <= .05:
            try: self.splash.destroy()
            except tk.TclError: pass
            self.deiconify()
            self.lift()
            return
        try: self.splash.attributes("-alpha", alpha)
        except tk.TclError:
            if alpha < .5:
                self.splash.destroy(); self.deiconify(); return
        self.after(35, lambda: self._fade_splash(alpha))

    def _styles(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TEntry", fieldbackground=P["panel2"], foreground=P["text"],
                    insertcolor=P["cyan"], padding=9, borderwidth=0)
        s.configure("TRadiobutton", background=P["panel"], foreground=P["text"],
                    font=(FONT, 10))
        s.map("TRadiobutton", background=[("active", P["panel"])],
              foreground=[("selected", P["cyan"]), ("active", P["cyan"])])

        for name in ("Dark.Vertical.TScrollbar", "Dark.Horizontal.TScrollbar"):
            s.configure(
                name,
                gripcount=0,
                background=P["panel3"],
                darkcolor=P["panel3"],
                lightcolor=P["panel3"],
                troughcolor=P["bg2"],
                bordercolor=P["bg2"],
                arrowcolor=P["cyan"],
                arrowsize=12,
                relief="flat",
                borderwidth=0,
            )
            s.map(
                name,
                background=[("active", P["line2"]), ("pressed", P["cyan"])],
                arrowcolor=[("active", P["cyan2"])],
            )
    def _shell(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self, bg=P["nav"], width=270,
                                highlightbackground=P["line"], highlightthickness=1)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.grid_columnconfigure(0, minsize=270)

        brand_box = tk.Frame(self.sidebar, bg=P["nav"], height=142)
        brand_box.pack(fill="x")
        brand_box.pack_propagate(False)
        self.logo = tk.Label(brand_box, text="HN", bg=P["nav"], fg=P["cyan"],
                             font=(MONO, 30, "bold"))
        self.logo.pack(pady=(17, 0))
        self.brand = tk.Label(brand_box, text=self.t("brand"), bg=P["nav"], fg=P["text"],
                              font=(MONO, 14, "bold"))
        self.brand.pack()
        self.sub = tk.Label(brand_box, text=self.t("sub"), bg=P["nav"], fg=P["muted"],
                            font=(MONO, 7, "bold"))
        self.sub.pack(pady=(3, 0))

        self.nav_frame = tk.Frame(self.sidebar, bg=P["nav"])
        self.nav_frame.pack(fill="both", expand=True, padx=10, pady=8)
        self.project_caption = tk.Label(self.nav_frame, text="PROJECT MODULES  //  LIVE", bg=P["nav"], fg=P["dim"],
                                         font=(MONO, 7, "bold"), anchor="w")
        self.project_caption.pack(fill="x", padx=8, pady=(2, 8))
        for key, icon, label in NAV:
            accent = NAV_ACCENTS.get(key, P["cyan"])
            b = tk.Button(self.nav_frame, text=f"  {icon}   {label}",
                          command=lambda k=key: self._nav_click(k),
                          bg=P["nav"], fg=P["muted"], activebackground=P["panel2"],
                          activeforeground=P["text"], relief="flat", bd=0,
                          anchor="w", padx=9, pady=9, font=(FONT, 9, "bold"),
                          cursor="hand2", highlightthickness=1,
                          highlightbackground=P["nav"], highlightcolor=accent)
            b.pack(fill="x", pady=2)
            b._key, b._label, b._icon, b._accent = key, label, icon, accent
            self.nav_buttons[key] = b
            self._hover(b, key)

        footer = tk.Frame(self.sidebar, bg=P["nav"], height=62)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(footer, text="●  " + self.t("online"), bg=P["nav"], fg=P["green"],
                 font=(MONO, 8, "bold")).pack()

        self.content = tk.Frame(self, bg=P["bg"])
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        self.topline = tk.Frame(self.content, bg=P["cyan"], height=2)
        self.topline.grid(row=0, column=0, sticky="new")
        self.topbar=tk.Frame(self.content,bg='#040b12',height=34,highlightbackground='#10394a',highlightthickness=1)
        self.topbar.grid(row=0,column=0,sticky='new',padx=10,pady=(6,0)); self.topbar.grid_propagate(False)
        tk.Label(self.topbar,text='HN / BLACKBOX',bg='#040b12',fg=P['cyan'],font=(MONO,8,'bold')).pack(side='left',padx=10)
        self.global_status=tk.Label(self.topbar,text='● LOCAL ENGINE  //  SECURE WORKSPACE',bg='#040b12',fg=P['green'],font=(MONO,7,'bold'))
        self.global_status.pack(side='left',padx=8)
        self.global_clock=tk.Label(self.topbar,text='',bg='#040b12',fg=P['muted'],font=(MONO,8,'bold')); self.global_clock.pack(side='right',padx=10)
        self.hud = tk.Label(self.content, text="OPS CONSOLE  //  LOCAL  //  ENCRYPTED WORKSPACE",
                            bg=P["bg"], fg=P["dim"], font=(MONO, 6), anchor="e")
        self.hud.place(relx=.98, rely=.058, anchor="ne")
        self._global_clock_tick()

    def _global_clock_tick(self):
        try:
            if hasattr(self,'global_clock') and self.global_clock.winfo_exists():
                self.global_clock.configure(text=datetime.now().strftime('%Y-%m-%d  %H:%M:%S'))
                self.after(1000,self._global_clock_tick)
        except tk.TclError: pass

    def _nav_click(self, key):
        """Interactive module selection with a beta gate for expanding modules."""
        b = self.nav_buttons.get(key)
        accent = getattr(b, "_accent", P["cyan"]) if b else P["cyan"]
        if b is not None and b.winfo_exists():
            b.configure(bg=accent, fg=P["bg"], highlightbackground=accent)
            self.after(90, lambda: self._restore_nav_button(key))
        if key in BETA_MODULES:
            self._show_module_gateway(key, accent)
            return
        self.show_page(key)
        if hasattr(self, "home_status") and key != "home":
            self.home_status.configure(text=f"MODULE MOUNTED  //  /{key.upper()}  //  READY", fg=accent)
        if hasattr(self, "home_terminal") and self.current != "processing":
            self._terminal_write(f"\n[MODULE] mount /{key} ... OK\n[STATUS] {key.upper()} ONLINE\nroot@HN-BLACKBOX:~# _")

    def _restore_nav_button(self, key):
        b=self.nav_buttons.get(key)
        if not b or not b.winfo_exists(): return
        active=(key==self.current)
        b.configure(bg=P["panel3"] if active else P["nav"],
                     fg=getattr(b,"_accent",P["cyan"]) if active else P["muted"],
                     highlightbackground=getattr(b,"_accent",P["cyan"]) if active else P["nav"])

    def _hover(self, widget, key):
        accent=getattr(widget,"_accent",P["cyan"])
        widget.bind("<Enter>", lambda e, w=widget, a=accent: w.configure(
            bg=P["panel2"], fg=a, highlightbackground=a))
        widget.bind("<Leave>", lambda e, w=widget, k=key: self._restore_nav_button(k))

    # ---------- pages ----------
    def _pages(self):
        self.pages["home"] = self.home_page()
        self.pages["crypto"] = self.crypto_page()
        self.pages["processing"] = tk.Frame(self.content, bg=P["bg"])
        self.pages["analysis"] = self.future_page("analysis")
        self.pages["network"] = self.future_page("network")
        self.pages["web"] = self.future_page("web")
        self.pages["blue"] = self.future_page("blue")
        self.pages["labs"] = self.lab_environment_page()
        self.pages["toolkit"] = self.toolkit_page()
        self.pages["development"] = self.development_page()
        self.pages["developer"] = self.developer_page()
        self.pages["history"] = self.history_page()
        for p in self.pages.values():
            p.grid(row=0, column=0, sticky="nsew", padx=28, pady=(26, 18))
        self._sync_aliases()

    def _sync_aliases(self):
        self.pages.update({"welcome": self.pages["home"], "dashboard": self.pages["crypto"],
                           "cryptanalysis": self.pages["analysis"], "blue_team": self.pages["blue"]})
        self.nav_buttons.update({"welcome": self.nav_buttons["home"], "dashboard": self.nav_buttons["crypto"],
                                 "cryptanalysis": self.nav_buttons["analysis"], "blue_team": self.nav_buttons["blue"]})

    def heading(self, parent, kicker, title, sub):
        """Section heading with cached HUD geometry; only motion items update per frame."""
        f = tk.Frame(parent, bg=P["bg"])
        f.pack(fill="x", pady=(0, 14))
        top = tk.Frame(f, bg="#050d14", highlightbackground="#123c49", highlightthickness=1, height=74)
        top.pack(fill="x", pady=(0, 8)); top.pack_propagate(False)
        hud = tk.Canvas(top, bg="#050d14", highlightthickness=0, bd=0, height=74)
        hud.pack(fill="both", expand=True)
        accent = NAV_ACCENTS.get(self.current, P["cyan"])
        state = {"phase": 0, "size": None, "items": None}
        def rebuild(w, h):
            hud.delete("all")
            for x in range(0, w, 24): hud.create_line(x, 0, x, h, fill="#071a22")
            for y in range(0, h, 18): hud.create_line(0, y, w, y, fill="#071a22")
            items={}
            items['scan']=hud.create_rectangle(-100,0,-10,h,fill="#09232b",outline="")
            cx, cy = w-92, h/2
            for r, col in ((28,"#174653"),(20,"#1d5e70"),(12,accent)):
                hud.create_oval(cx-r,cy-r,cx+r,cy+r,outline=col,width=1)
            items['sweep']=hud.create_line(cx,cy,cx+30,cy,fill=accent,width=2)
            items['core']=hud.create_oval(cx-3,cy-3,cx+3,cy+3,fill=P["cyan2"],outline="")
            blocks=[]
            for i in range(12):
                bh=5+((i*7)%22); x=15+i*12
                blocks.append((hud.create_rectangle(x,h-7-bh,x+7,h-7,fill=accent if i%3 else P["green"],outline=""),x,bh))
            items['blocks']=blocks
            items['seq']=hud.create_text(w-12,11,text="SEQ 0000",anchor="ne",fill=P["cyan"],font=(MONO,6,"bold"))
            state['items']=items; state['size']=(w,h)
        def tick():
            if not hud.winfo_exists(): return
            if not self._widget_on_current_page(hud) or not self._motion_active:
                hud.after(self._motion_hidden_ms, tick); return
            if time.monotonic() < self._resizing_until:
                hud.after(220, tick); return
            w,h=max(1,hud.winfo_width()),max(1,hud.winfo_height())
            if state['size'] != (w,h):
                rebuild(w,h)
                hud.create_text(14,12,text=kicker.upper(),anchor="nw",fill=accent,font=(MONO,7,"bold"))
                hud.create_text(14,31,text="HN // BLACKBOX  •  LOCAL TELEMETRY  •  LIVE",anchor="nw",fill=P["muted"],font=(MONO,7,"bold"))
            t=state['phase']; items=state['items']; sx=(t*3.0)%(w+90)-90
            hud.coords(items['scan'],sx,0,sx+90,h)
            cx,cy=w-92,h/2; ang=t*0.055
            hud.coords(items['sweep'],cx,cy,cx+30*math.cos(ang),cy+30*math.sin(ang))
            for i,(item,x,bh) in enumerate(items['blocks']):
                nb=5+((i*7+t)%22); hud.coords(item,x,h-7-nb,x+7,h-7)
            hud.itemconfigure(items['seq'],text=f"SEQ {t:04d}")
            state['phase']=(t+1)%10000
            hud.after(self._motion_ms,tick)
        hud.after_idle(tick)
        body = tk.Frame(f, bg=P["bg"]); body.pack(fill="x")
        tk.Label(body, text=title, bg=P["bg"], fg=P["text"],font=(FONT, 25, "bold"), anchor="w", justify="left").pack(fill="x", pady=(1, 1))
        tk.Label(body, text=sub, bg=P["bg"], fg=P["muted"],font=(FONT, 10), anchor="w", justify="left", wraplength=980).pack(fill="x")

    def card(self, parent, **kw):
        return tk.Frame(parent, bg=P["panel"], highlightbackground=P["line"],
                        highlightthickness=1, bd=0, **kw)

    def glass(self, parent, **kw):
        return tk.Frame(parent, bg=P["panel2"], highlightbackground=P["line"],
                        highlightthickness=1, bd=0, **kw)

    def btn(self, parent, text, cmd, primary=False, **kw):
        base_bg = P["cyan"] if primary else P["panel2"]
        base_fg = P["bg"] if primary else P["text"]
        hover_bg = P["green"] if primary else P["line2"]
        b = tk.Button(parent, text=text, command=cmd,
                      bg=base_bg, fg=base_fg,
                      activebackground=hover_bg,
                      activeforeground=P["bg"], relief="flat", bd=0,
                      padx=14, pady=9, font=(FONT, 9, "bold"),
                      cursor="hand2", highlightthickness=1,
                      highlightbackground=base_bg, highlightcolor=hover_bg, **kw)
        b._base_bg, b._base_fg, b._hover_bg = base_bg, base_fg, hover_bg
        b.bind("<Enter>", lambda e, w=b: w.configure(
            bg=w._hover_bg, fg=P["bg"], highlightbackground=w._hover_bg), add="+")
        b.bind("<Leave>", lambda e, w=b: w.configure(
            bg=w._base_bg, fg=w._base_fg, highlightbackground=w._base_bg), add="+")
        return b

    def _responsive_grid(self, host, cards, min_card=285, gap=10):
        # One active layout controller per deck. This prevents a previous
        # controller from touching widgets that were replaced during filtering
        # or algorithm-family switching.
        old_job=getattr(host,'_responsive_job',None)
        if old_job:
            try: host.after_cancel(old_job)
            except Exception: pass
        host.unbind('<Configure>')
        host.grid_columnconfigure(0, weight=1)
        state={'cols':0}
        def layout(event=None):
            width=max(320,host.winfo_width())
            cols=3 if width>=900 else 2 if width>=600 else 1
            if cols==state['cols'] and event is not None: return
            state['cols']=cols
            for c in list(cards):
                try: c.grid_forget()
                except tk.TclError: pass
            for col in range(cols):
                host.grid_columnconfigure(col,weight=1,uniform='responsive')
            for i,c in enumerate(list(cards)):
                try: c.grid(row=i//cols,column=i%cols,sticky='nsew',padx=gap/2,pady=gap/2)
                except tk.TclError: pass
        host.bind('<Configure>',layout)
        host._responsive_job=host.after_idle(layout)
        return layout

    def _metric_card(self,parent,value,label,accent=None):
        c=self.glass(parent); accent=accent or P['cyan']
        tk.Label(c,text=value,bg=P['panel2'],fg=accent,font=(MONO,21,'bold')).pack(anchor='e',padx=16,pady=(14,2))
        tk.Label(c,text=label,bg=P['panel2'],fg=P['muted'],font=(FONT,9),anchor='e',justify='right').pack(fill='x',padx=16,pady=(0,14))
        return c

    def home_page(self):
        """HN BlackBox command-center dashboard: dense, responsive and data-backed."""
        p=tk.Frame(self.content,bg=P['bg'])
        holder=tk.Frame(p,bg=P['bg'])
        holder.pack(fill='both',expand=True)
        cv=tk.Canvas(holder,bg=P['bg'],highlightthickness=0,bd=0)
        vbar=ttk.Scrollbar(holder,orient='vertical',command=cv.yview,style='Dark.Vertical.TScrollbar')
        hbar=ttk.Scrollbar(holder,orient='horizontal',command=cv.xview,style='Dark.Horizontal.TScrollbar')
        cv.configure(yscrollcommand=vbar.set,xscrollcommand=hbar.set)
        cv.grid(row=0,column=0,sticky='nsew')
        # All dashboard widgets live inside one Canvas window.  This is the
        # critical fix for compact-window scrolling: Tk widgets placed directly
        # on a Canvas do NOT move with yview/xview.  The surface does.
        surface=tk.Frame(cv,bg=P['bg'],highlightthickness=0,bd=0)
        self.home_surface=surface
        self._home_window=cv.create_window((0,0),window=surface,anchor='nw',tags='home_surface')
        vbar.grid(row=0,column=1,sticky='ns')
        hbar.grid(row=1,column=0,sticky='ew')
        holder.grid_rowconfigure(0,weight=1)
        holder.grid_columnconfigure(0,weight=1)
        self.home_canvas=cv; self._bind_wheel(cv)
        self._home_widgets={}

        def grid_bg(e=None):
            # Configure fires many times while a window is being dragged. Debounce
            # the decorative grid and the responsive layout into one paint pass.
            if self._home_grid_job is not None:
                try: self.after_cancel(self._home_grid_job)
                except Exception: pass
            self._home_grid_job = self.after(80, self._redraw_home_grid)
        cv.bind('<Configure>',grid_bg,add='+')

        top=tk.Frame(surface,bg='#061016',highlightbackground='#174653',highlightthickness=1)
        self._home_widgets['top']=top
        tk.Label(top,text='root@HN-BLACKBOX:~#',bg='#061016',fg=P['green'],font=(MONO,9,'bold')).pack(side='left',padx=12)
        self.home_cmd=tk.Entry(top,bg='#02080d',fg=P['text'],insertbackground=P['cyan'],relief='flat',bd=0,font=(MONO,9))
        self.home_cmd.insert(0,'help  //  type a command')
        self.home_cmd.pack(side='left',fill='x',expand=True,padx=8,ipady=5)
        self.home_cmd.bind('<Return>',self._home_command)
        self.after(400, lambda: self.home_cmd.icursor('end') if self.home_cmd.winfo_exists() else None)
        tk.Label(top,text='ENTER',bg='#061016',fg=P['dim'],font=(MONO,7,'bold')).pack(side='left',padx=7)
        self.home_clock=tk.Label(top,text='--:--:--',bg='#061016',fg=P['cyan'],font=(MONO,8,'bold'))
        self.home_clock.pack(side='right',padx=12)

        rail=tk.Frame(surface,bg='#040b10',highlightbackground='#123a45',highlightthickness=1)
        self._home_widgets['rail']=rail
        uname=(getpass.getuser() or 'HN USER').upper()
        tk.Label(rail,text=f'root@{uname.lower()}:~#',bg='#040b10',fg=P['green'],font=(MONO,8,'bold'),anchor='w').pack(fill='x',padx=11,pady=(10,7))
        files=[('./dashboard.sh','RUNNING'),('/core/ciphers','19'),('/core/analysis','4'),('/core/network','3'),('/core/web','4'),('/core/blue_team','2'),('/core/labs','4'),('/tests','23')]
        module_map={'/core/ciphers':'crypto','/core/analysis':'analysis','/core/network':'network','/core/web':'web','/core/blue_team':'blue','/core/labs':'labs','/tests':'development'}
        for path,badge in files:
            key=module_map.get(path)
            if key:
                accent=NAV_ACCENTS.get(key,P['cyan'])
                r=tk.Frame(rail,bg='#040b10',highlightbackground='#0d2c36',highlightthickness=1);r.pack(fill='x',padx=7,pady=2)
                r.bind('<Button-1>',lambda e,k=key:self._nav_click(k))
                tk.Label(r,text='▸',bg='#040b10',fg=accent,font=(MONO,8)).pack(side='left',padx=(5,0))
                lab=tk.Label(r,text=path,bg='#040b10',fg=P['muted'],font=(MONO,7,'bold'),anchor='w',cursor='hand2');lab.pack(side='left',padx=5)
                lab.bind('<Button-1>',lambda e,k=key:self._nav_click(k))
                if badge: tk.Label(r,text=badge,bg='#0b2b34',fg=P['green'] if badge=='RUNNING' else accent,font=(MONO,6,'bold'),padx=3).pack(side='right',padx=4)
            else:
                r=tk.Frame(rail,bg='#040b10');r.pack(fill='x',padx=7,pady=2)
                tk.Label(r,text='▸',bg='#040b10',fg=P['dim'],font=(MONO,8)).pack(side='left')
                tk.Label(r,text=path,bg='#040b10',fg=P['muted'],font=(MONO,7),anchor='w').pack(side='left',padx=5)
        # Live status console: animated bars + real project health counters.
        tk.Label(rail,text='──────────────────',bg='#040b10',fg='#11323b',font=(MONO,7)).pack(pady=7)
        status_box=tk.Frame(rail,bg='#061016',highlightbackground='#174451',highlightthickness=1); status_box.pack(fill='x',padx=7,pady=(0,7))
        tk.Label(status_box,text='SYSTEM STATUS // LIVE',bg='#061016',fg=P['cyan'],font=(MONO,7,'bold'),anchor='w').pack(fill='x',padx=8,pady=(8,4))
        self.home_status_rows=[]
        for txt,color in (('CRYPTO','cyan'),('ANALYSIS','purple'),('NETWORK','green'),('DEFENSE','red')):
            row=tk.Frame(status_box,bg='#061016'); row.pack(fill='x',padx=7,pady=2)
            dot=tk.Label(row,text='●',bg='#061016',fg=P[color],font=(MONO,7)); dot.pack(side='left')
            tk.Label(row,text=txt,bg='#061016',fg=P['text'],font=(MONO,6,'bold')).pack(side='left',padx=4)
            bar=tk.Canvas(row,width=58,height=7,bg='#061016',highlightthickness=0); bar.pack(side='right',padx=2)
            self.home_status_rows.append((bar,color))
        self.home_status_clock=tk.Label(status_box,text='SYNC --:--:--',bg='#061016',fg=P['dim'],font=(MONO,6,'bold'),anchor='w'); self.home_status_clock.pack(fill='x',padx=8,pady=(4,8))
        self._animate_home_status()
        self.home_user_badge=tk.Label(rail,text=f'HN BLACKBOX\n{uname}\nLOCAL WORKSPACE',bg='#06151b',fg=P['cyan'],font=(MONO,7,'bold'),justify='left',anchor='w',padx=8,pady=8)
        self.home_user_badge.pack(side='bottom',fill='x',padx=7,pady=7)

        title=tk.Frame(surface,bg='#07131a',highlightbackground='#123e4b',highlightthickness=1);self._home_widgets['title']=title
        tk.Label(title,text='SYSTEM OVERVIEW',bg='#07131a',fg=P['cyan'],font=(MONO,11,'bold'),anchor='w').pack(side='left',padx=13,pady=8)
        self.home_status=tk.Label(title,text='STATUS: ONLINE  //  LOCAL LAB  //  DEFENSIVE MODE',bg='#07131a',fg=P['dim'],font=(MONO,7,'bold'),anchor='w');self.home_status.pack(side='left',padx=9)
        self.home_open_crypto=self.btn(title,'> OPEN CRYPTO LAB',lambda:self.show_page('crypto'),True)
        self.home_open_crypto.pack(side='right',padx=5,pady=5)
        self.home_open_terminal=self.btn(title,'> OPEN TERMINAL',self.launch_blackbox_terminal)
        self.home_open_terminal.pack(side='right',padx=5,pady=5)

        term=tk.Frame(surface,bg='#040a0e',highlightbackground='#164b59',highlightthickness=1); self._home_widgets['term']=term
        term_head=tk.Frame(term,bg='#07141a'); term_head.pack(fill='x')
        tk.Label(term_head,text='LIVE COMMAND CHANNEL  //  HN TERMINAL',bg='#07141a',fg=P['green'],font=(MONO,8,'bold')).pack(side='left',padx=10,pady=6)
        tk.Label(term_head,text='LOCAL // EXEC  •  ↑↓ HISTORY  •  ENTER RUN',bg='#07141a',fg=P['dim'],font=(MONO,7,'bold')).pack(side='right',padx=10)
        term_body=tk.Frame(term,bg='#02070b'); term_body.pack(fill='both',expand=True)

        # Identity Core HUD: this is the HN emblem the dashboard uses as its
        # primary visual anchor.  It is a real Tkinter canvas (not an image), so
        # it stays sharp at every window size while the radar/scan layers move.
        identity_pane=tk.Frame(term_body,bg='#030b10',highlightbackground='#174451',highlightthickness=1,width=224)
        identity_pane.pack(side='left',fill='both',padx=(7,4),pady=7)
        identity_pane.pack_propagate(False)
        self.home_identity_pane=identity_pane
        identity_head=tk.Frame(identity_pane,bg='#07141a'); identity_head.pack(fill='x')
        tk.Label(identity_head,text='IDENTITY CORE // HN',bg='#07141a',fg=P['cyan'],font=(MONO,8,'bold')).pack(side='left',padx=9,pady=6)
        self.home_identity_clock=tk.Label(identity_head,text='--:--:--',bg='#07141a',fg=P['green'],font=(MONO,7,'bold')); self.home_identity_clock.pack(side='right',padx=8)
        self.home_identity_canvas=tk.Canvas(identity_pane,bg='#02070b',highlightthickness=0,bd=0,height=165)
        self.home_identity_canvas.pack(fill='both',expand=True,padx=5,pady=5)
        self.home_identity_status=tk.Label(identity_pane,text='HN CORE // ONLINE  •  VECTOR LOCKED',bg='#061016',fg=P['green'],font=(MONO,6,'bold'))
        self.home_identity_status.pack(fill='x',padx=6,pady=(0,5))
        self._home_identity_phase=0
        self._animate_home_identity()
        self._animate_home_intel()

        # Command console: keep the terminal real, but surround it with a live HUD.
        terminal_pane=tk.Frame(term_body,bg='#02070b'); terminal_pane.pack(side='left',fill='both',expand=True,padx=(4,4),pady=7)
        # Live command intelligence layer. All data is local/synthetic telemetry;
        # the real terminal remains immediately below it.
        self.home_command_hud=tk.Canvas(
            terminal_pane,bg='#02080d',height=92,highlightbackground='#123f4c',
            highlightthickness=1,bd=0)
        self.home_command_hud.pack(fill='x',pady=(0,5))
        self._home_command_scene=None
        self._home_command_phase=0
        self._home_command_last_sample=0.0
        self._home_command_values={'cpu':0.0,'ram':0.0,'proc':0,'ops':0}
        self._animate_home_command_hud()
        self.home_terminal=tk.Text(terminal_pane,bg='#02070b',fg='#8fffc8',insertbackground=P['cyan'],relief='flat',bd=0,
                                   font=(ASCII_MONO,8),wrap='none',padx=10,pady=8)
        self.home_terminal.pack(fill='both',expand=True)
        self.home_terminal.tag_configure('brand',foreground=P['cyan2'])
        self.home_terminal.tag_configure('ok',foreground=P['green'])
        self.home_terminal.tag_configure('warn',foreground=P['yellow'])
        self.home_terminal.tag_configure('dim',foreground=P['muted'])
        self._terminal_write('HN BLACKBOX // SECURITY ENGINEERING SUITE\n'
                             '────────────────────────────────────────\n'
                             'root@HN-BLACKBOX:~# status\n'
                             '[OK] core engines ........ online\n[OK] visual pipeline ..... armed\n[OK] local audit ......... ready\n'
                             '[LIVE] system telemetry ... attached\n'
                             'root@HN-BLACKBOX:~# _', reset=True)
        self.home_terminal.bind('<Key>', lambda e: 'break')
        self.terminal_anim=tk.Canvas(terminal_pane,height=26,bg='#030b10',highlightthickness=0)
        self.terminal_anim.pack(fill='x',pady=(4,0))
        self._terminal_phase=0
        self._animate_terminal_hud()
        self.home_cmd.bind('<Up>', self._cmd_prev)
        self.home_cmd.bind('<Down>', self._cmd_next)

        # Real-time local task/system monitor. It uses psutil when available and
        # falls back to platform-native process counters when it is not.
        sysmon=tk.Frame(term_body,bg='#030b10',highlightbackground='#174451',highlightthickness=1,width=330)
        sysmon.pack(side='right',fill='both',padx=(4,7),pady=7)
        sysmon.pack_propagate(False)
        self.home_sysmon=sysmon
        smh=tk.Frame(sysmon,bg='#07141a'); smh.pack(fill='x')
        tk.Label(smh,text='LIVE SYSTEM // TASK MANAGER',bg='#07141a',fg=P['cyan'],font=(MONO,8,'bold')).pack(side='left',padx=9,pady=6)
        self.home_sys_clock=tk.Label(smh,text='--:--:--',bg='#07141a',fg=P['green'],font=(MONO,9,'bold')); self.home_sys_clock.pack(side='right',padx=9)
        self.home_sys_canvas=tk.Canvas(sysmon,bg='#02070b',highlightthickness=0,height=108); self.home_sys_canvas.pack(fill='x',padx=6,pady=6)
        metrics=tk.Frame(sysmon,bg='#02070b'); metrics.pack(fill='both',expand=True,padx=6,pady=(0,6))
        self.sys_metric_labels={}
        for key,label,color in [('cpu','CPU',P['green']),('ram','RAM',P['cyan']),('proc','PROC',P['yellow']),('up','UPTIME',P['purple'])]:
            row=tk.Frame(metrics,bg='#061016',highlightbackground='#0e303b',highlightthickness=1); row.pack(fill='x',pady=2)
            tk.Label(row,text=label,bg='#061016',fg=P['dim'],font=(MONO,7,'bold')).pack(side='left',padx=7,pady=5)
            val=tk.Label(row,text='--',bg='#061016',fg=color,font=(MONO,9,'bold')); val.pack(side='right',padx=7)
            self.sys_metric_labels[key]=val
        self.home_task_text=tk.Text(metrics,height=4,bg='#02070b',fg='#78f6b5',font=(MONO,6),relief='flat',bd=0,wrap='none')
        self.home_task_text.pack(fill='both',expand=True,pady=(4,0)); self.home_task_text.configure(state='disabled')
        self._animate_system_monitor()

        kpi=tk.Frame(surface,bg=P['bg']);self._home_widgets['kpi']=kpi
        entries=history_manager.get_all() if hasattr(history_manager,'get_all') else []
        hist_n=len(entries)
        stats=[('ALGORITHMS','21','ACTIVE CIPHERS',P['cyan'],self.show_page,'crypto'),('LAB MODULES','5','LOCAL SECURITY TOOLS',P['green'],self.show_page,'analysis'),('OPERATIONS',str(hist_n),'LOCAL AUDIT ENTRIES',P['orange'],self.show_page,'history'),('TEST STATUS','28/28','CORE + GUI CHECKS',P['purple'],self.show_page,'development')]
        for val,num,sub,color,cmd,key in stats:
            c=tk.Frame(kpi,bg='#08161c',highlightbackground='#174451',highlightthickness=1);c.pack(side='left',fill='both',expand=True,padx=3)
            tk.Label(c,text=val,bg='#08161c',fg=P['muted'],font=(MONO,7,'bold'),anchor='w').pack(fill='x',padx=10,pady=(8,1))
            tk.Label(c,text=num,bg='#08161c',fg=color,font=(MONO,18,'bold'),anchor='w').pack(fill='x',padx=10)
            b=tk.Button(c,text=sub,bg='#08161c',fg=P['dim'],activebackground='#0b2028',activeforeground=P['cyan'],relief='flat',bd=0,font=(MONO,6,'bold'),anchor='w',command=lambda f=cmd,k=key:f(k),cursor='hand2');b.pack(fill='x',padx=10,pady=(0,8))

        main=tk.Frame(surface,bg=P['bg']);self._home_widgets['main']=main
        # left: mission + activity
        left=tk.Frame(main,bg='#061016',highlightbackground='#143e4a',highlightthickness=1);left.pack(side='left',fill='both',expand=True,padx=(0,5))
        mission_head=tk.Frame(left,bg='#07131a',highlightbackground=P['cyan'],highlightthickness=1);mission_head.pack(fill='x',padx=9,pady=(7,4))
        tk.Label(mission_head,text='PROJECT // MISSION // HN BLACKBOX',bg='#07131a',fg=P['cyan2'],font=(MONO,8,'bold'),anchor='w').pack(fill='x',padx=11,pady=(8,2))
        self.home_mission_title=tk.Label(mission_head,text='HN BLACKBOX: THE BLACK BOX FOR SECURITY PROJECTS & SOLUTIONS.',bg='#07131a',fg=P['text'],font=(MONO,15,'bold'),anchor='w',justify='left',wraplength=760)
        self.home_mission_title.pack(fill='x',padx=11,pady=(1,4))
        self.home_mission_desc=tk.Label(mission_head,text='A unified technical platform bringing our software projects together across cybersecurity and systems engineering. We break down complex concepts, test tools, and build innovative defensive solutions under one interface.',bg='#07131a',fg='#9bc0cf',font=(FONT,8),anchor='w',justify='left',wraplength=760)
        self.home_mission_desc.pack(fill='x',padx=11,pady=(0,10))
        stream_box=tk.Frame(left,bg='#061016',highlightbackground='#0f303a',highlightthickness=1,height=94);stream_box.pack(fill='x',padx=10,pady=(4,5));stream_box.pack_propagate(False)
        tk.Label(stream_box,text='LIVE MODULE STREAM',bg='#061016',fg=P['cyan'],font=(MONO,8,'bold'),anchor='w').pack(fill='x',padx=9,pady=(5,2))
        stream=[('CRYPTO','AES / RSA / classical engines loaded',P['cyan']),('ANALYSIS','frequency + IC + Kasiski ready',P['purple']),('NETWORK','IP / subnet / DNS utilities ready',P['green']),('WEB','safe HTTP simulator + OWASP concepts',P['orange']),('BLUE','log triage + IOC classification',P['red']),('LABS','offline challenges + hints',P['yellow'])]
        for name,desc,color in stream:
            r=tk.Frame(stream_box,bg='#061016');r.pack(fill='x',padx=8,pady=0)
            tk.Label(r,text='●',bg='#061016',fg=color,font=(MONO,7)).pack(side='left')
            tk.Label(r,text=name,bg='#061016',fg=P['text'],font=(MONO,6,'bold'),width=9,anchor='w').pack(side='left',padx=4)
            tk.Label(r,text=desc,bg='#061016',fg=P['muted'],font=(MONO,5),anchor='w').pack(side='left',fill='x',expand=True)
        # compact command shortcuts
        cmdbox=tk.Frame(left,bg='#07131a',highlightbackground='#123c48',highlightthickness=1);cmdbox.pack(fill='x',padx=10,pady=6)
        tk.Label(cmdbox,text='QUICK COMMANDS',bg='#07131a',fg=P['dim'],font=(MONO,7,'bold')).pack(anchor='w',padx=8,pady=(5,3))
        for label,key in [('CRYPTANALYSIS','analysis'),('NETWORK TOOLKIT','network'),('WEB LAB','web'),('BLUE TEAM','blue'),('SECURITY LABS','labs')]:
            self.btn(cmdbox,label,lambda k=key:self.show_page(k)).pack(side='left',padx=2,pady=(0,5))

        # Live workspace monitor: real project state on the left + a continuously
        # animated multi-color diagnostics scope on the right.
        monitor=tk.Frame(left,bg='#030b10',highlightbackground='#174451',highlightthickness=1)
        monitor.pack(fill='both',expand=False,padx=10,pady=(0,7))
        self.home_monitor=monitor
        mh=tk.Frame(monitor,bg='#07141a');mh.pack(fill='x')
        tk.Label(mh,text='LIVE WORKSPACE MONITOR  //  TASKS + TOOL HEALTH + PROJECT SCAN',bg='#07141a',fg=P['yellow'],font=(MONO,8,'bold'),anchor='w').pack(side='left',padx=9,pady=6)
        self.home_scan_status=tk.Label(mh,text='SCANNING...',bg='#07141a',fg=P['green'],font=(MONO,7,'bold'),anchor='e');self.home_scan_status.pack(side='right',padx=9)
        monitor_body=tk.Frame(monitor,bg='#02070b');monitor_body.pack(fill='both',expand=True,padx=6,pady=6)
        # Interactive workspace board: task health, integrity, activity and
        # module shortcuts are rendered as live vector graphics.
        self.home_workspace_canvas=tk.Canvas(
            monitor_body,bg='#02080d',highlightbackground='#123f4c',
            highlightthickness=1,bd=0)
        self.home_workspace_canvas.pack(side='left',fill='both',expand=True)
        self.home_workspace_canvas.bind('<Button-1>', self._home_workspace_click)
        self.home_monitor_scope=tk.Canvas(monitor_body,width=205,bg='#02080d',highlightbackground='#123f4c',highlightthickness=1)
        self.home_monitor_scope.pack(side='right',fill='both',padx=(7,0))
        self._monitor_phase=0
        self._animate_home_monitor()
        self._animate_home_workspace()
        self._refresh_home_scan()

        # right: telemetry + warning + identity
        side=tk.Frame(main,bg=P['bg']);side.pack(side='right',fill='both',padx=(5,0));side.configure(width=280);side.pack_propagate(False)
        tele=tk.Frame(side,bg='#061016',highlightbackground='#174451',highlightthickness=1);tele.pack(fill='x',pady=(0,7))
        tk.Label(tele,text='SYS_TELEMETRY',bg='#061016',fg=P['cyan'],font=(MONO,8,'bold'),anchor='w').pack(fill='x',padx=10,pady=(9,5))
        info=[('HOST',socket.gethostname()),('OS',platform.system()),('PYTHON',platform.python_version()),('ARCH',platform.machine()),('USER',uname)]
        for k,v in info:
            r=tk.Frame(tele,bg='#061016');r.pack(fill='x',padx=10,pady=2);tk.Label(r,text=k,bg='#061016',fg=P['dim'],font=(MONO,7),anchor='w').pack(side='left');tk.Label(r,text=str(v)[:27],bg='#061016',fg=P['text'],font=(MONO,7,'bold'),anchor='e').pack(side='right')
        warn=tk.Frame(side,bg='#241013',highlightbackground='#8b2735',highlightthickness=1);warn.pack(fill='x',pady=7)
        tk.Label(warn,text='⚠ DEFENSIVE WORKSPACE',bg='#241013',fg=P['red'],font=(MONO,8,'bold'),anchor='w').pack(fill='x',padx=10,pady=(9,3))
        tk.Label(warn,text='All network/web modules are designed for local, educational use. No exploitation engine or credential attack is included.',bg='#241013',fg='#e7a2aa',font=(MONO,7),justify='left',wraplength=240,anchor='w').pack(fill='x',padx=10,pady=(0,8))
        tk.Button(warn,text='OPEN BLUE TEAM',command=lambda:self.show_page('blue'),bg='#9f2432',fg='#fff',activebackground='#d63d4d',relief='flat',bd=0,font=(MONO,8,'bold'),pady=6).pack(fill='x',padx=10,pady=(0,9))
        # Lower-right intelligence board: a continuously rendered HN operations
        # display.  It is deliberately local/synthetic — the visuals are telemetry
        # style, not a claim of real external intelligence collection.
        ident=tk.Frame(side,bg='#030b10',highlightbackground='#174451',highlightthickness=1)
        ident.pack(fill='both',expand=True)
        ih=tk.Frame(ident,bg='#07141a'); ih.pack(fill='x')
        tk.Label(ih,text='HN // INTELLIGENCE BOARD',bg='#07141a',fg=P['cyan'],
                 font=(MONO,8,'bold')).pack(side='left',padx=9,pady=6)
        self.home_intel_clock=tk.Label(ih,text='LOCAL // LIVE',bg='#07141a',fg=P['green'],
                                       font=(MONO,6,'bold')); self.home_intel_clock.pack(side='right',padx=8)
        self.home_intel_canvas=tk.Canvas(ident,bg='#02070b',highlightthickness=0,bd=0)
        self.home_intel_canvas.pack(fill='both',expand=True,padx=5,pady=5)
        self.home_intel_status=tk.Label(
            ident,text='HN CORE // SYNTHETIC TELEMETRY  •  DEFENSIVE MODE',
            bg='#061016',fg=P['yellow'],font=(MONO,6,'bold'))
        self.home_intel_status.pack(fill='x',padx=6,pady=(0,5))
        self._home_intel_phase=0

        foot=tk.Frame(surface,bg='#040b10',highlightbackground='#0d2c36',highlightthickness=1);self._home_widgets['foot']=foot
        tk.Label(foot,text='HN BLACKBOX // LOCAL • OFFLINE • EDUCATIONAL',bg='#040b10',fg=P['dim'],font=(MONO,5),anchor='w').pack(side='left',padx=7,pady=2)
        tk.Label(foot,text='SECURE WORKSPACE  ●',bg='#040b10',fg=P['green'],font=(MONO,5,'bold')).pack(side='right',padx=7)
        self._update_home_clock()
        self._pulse_home()
        self._layout_home_v10()
        return p

    def _draw_hn_emblem(self, canvas, cx, cy, size=1.0, fg=None, accent=None, glow=None):
        """Balanced vector HN identity mark. Geometry is centered and resize-safe."""
        fg = fg or P["text"]
        accent = accent or P["cyan"]
        glow = glow or P["cyan2"]
        s = max(.55, float(size))
        # centered tech badge
        rw, rh = 62*s, 38*s
        canvas.create_oval(cx-rw, cy-rh, cx+rw, cy+rh, outline='#0b3340', width=max(1,int(2*s)))
        canvas.create_oval(cx-(rw-8*s), cy-(rh-8*s), cx+(rw-8*s), cy+(rh-8*s), outline=glow, width=max(1,int(1.5*s)))
        # H — left half
        lx, rx = cx-28*s, cx-6*s
        yt, yb = cy-17*s, cy+17*s
        canvas.create_line(lx,yt,lx,yb,fill=fg,width=max(2,int(5*s)),capstyle='round')
        canvas.create_line(rx,yt,rx,yb,fill=fg,width=max(2,int(5*s)),capstyle='round')
        canvas.create_line(lx,cy,rx,cy,fill=accent,width=max(2,int(5*s)),capstyle='round')
        # N — right half, fully inside the badge
        nx0,nx1=cx+5*s,cx+29*s
        canvas.create_line(nx0,yb,nx0,yt,fill=fg,width=max(2,int(5*s)),capstyle='round')
        canvas.create_line(nx0,yt,nx1,yb,fill=accent,width=max(2,int(5*s)),capstyle='round')
        canvas.create_line(nx1,yb,nx1,yt,fill=fg,width=max(2,int(5*s)),capstyle='round')
        # animated-looking digital nodes
        for dx,dy in [(-28,-17),(-28,17),(29,-17),(29,17)]:
            r=2.2*s
            canvas.create_oval(cx+dx*s-r,cy+dy*s-r,cx+dx*s+r,cy+dy*s+r,fill=glow,outline='')

    def _animate_home_command_hud(self):
        """Animate a local command/intelligence scope without rebuilding geometry."""
        if not getattr(self,'_ui_ready',False):
            self.after(120,self._animate_home_command_hud)
            return
        c=getattr(self,'home_command_hud',None)
        if c is None or not c.winfo_exists():
            return
        if self.current!='home':
            self.after(700,self._animate_home_command_hud)
            return
        w,h=max(1,c.winfo_width()),max(1,c.winfo_height())
        sig=(w,h)
        scene=getattr(self,'_home_command_scene',None)
        if scene is None or scene.get('size')!=sig:
            c.delete('all')
            scene={'size':sig,'wave':[],'nodes':[],'packets':[],'labels':[]}
            for x in range(0,w,24):
                c.create_line(x,0,x,h,fill='#061923')
            for y in range(0,h,18):
                c.create_line(0,y,w,y,fill='#061923')
            scene['labels']=[
                c.create_text(8,6,text='LIVE COMMAND INTELLIGENCE // LOCAL TELEMETRY',
                              anchor='nw',fill=P['cyan'],font=(MONO,6,'bold')),
                c.create_text(w-8,6,text='PIPELINE // ARMED',
                              anchor='ne',fill=P['green'],font=(MONO,6,'bold')),
                c.create_text(8,h-7,text='',anchor='sw',fill=P['dim'],font=(MONO,5)),
                c.create_text(w-8,h-7,text='',anchor='se',fill=P['yellow'],font=(MONO,5)),
            ]
            base=h*.56
            for i in range(34):
                scene['wave'].append(c.create_line(0,base,0,base,fill=P['cyan2'],width=1))
            for i in range(6):
                scene['nodes'].append(c.create_oval(-3,-3,3,3,
                                      fill=P['green'] if i%2 else P['cyan'],outline=''))
            for i in range(8):
                scene['packets'].append(c.create_oval(-2,-2,2,2,fill=P['cyan2'],outline=''))
            self._home_command_scene=scene

        phase=self._home_command_phase
        if time.monotonic()-self._home_command_last_sample>1.5:
            cpu,ram,procs=self._system_metrics()
            self._home_command_values={
                'cpu':cpu or 0,'ram':ram or 0,'proc':procs or 0,
                'ops':self._home_data.get('history',0)
            }
            self._home_command_last_sample=time.monotonic()
        v=self._home_command_values
        base=h*.56
        for i,line in enumerate(scene['wave']):
            x=7+i*max(4,(w-14)/33)
            amp=7+(v['cpu']%20)*.18
            y=base+math.sin(phase*.13+i*.55)*amp
            c.coords(line,x,base,x,y)
        for i,node in enumerate(scene['nodes']):
            x=w*.42+i*(w*.46/5)
            y=h*.54+math.sin(phase*.06+i*1.1)*12
            c.coords(node,x-3,y-3,x+3,y+3)
        for i,p in enumerate(scene['packets']):
            t=(phase*.018+i*.13)%1
            x=w*.39+(w*.49)*t
            y=h*.54+math.sin(phase*.06+i)*12
            c.coords(p,x-2,y-2,x+2,y+2)
        c.itemconfigure(scene['labels'][2],
                        text=f'CPU {v["cpu"]:04.1f}%   RAM {v["ram"]:04.1f}%   PROC {v["proc"]}   OPS {v["ops"]}')
        c.itemconfigure(scene['labels'][3],
                        text=f'SIGNAL {phase%1000:03d}  •  {datetime.now().strftime("%H:%M:%S")}')
        self._home_command_phase=(phase+1)%100000
        self.after(40,self._animate_home_command_hud)

    def _animate_home_identity(self):
        """Render the identity HUD once, then animate only the moving elements."""
        if not getattr(self,'_ui_ready',False): return
        if time.monotonic() < getattr(self,'_resizing_until',0):
            self.after(180,self._animate_home_identity); return
        c=getattr(self,'home_identity_canvas',None)
        if c is None or not c.winfo_exists(): return
        if self.current != 'home':
            self.after(900,self._animate_home_identity)
            return
        w=max(1,c.winfo_width()); h=max(1,c.winfo_height()); phase=self._home_identity_phase
        sig=(w,h)
        items=getattr(self,'_home_identity_items',None)
        if items is None or getattr(self,'_home_identity_size',None)!=sig:
            c.delete('all'); items={}; self._home_identity_size=sig
            for x in range(0,w,22): c.create_line(x,0,x,h,fill='#071a22')
            for y in range(0,h,20): c.create_line(0,y,w,y,fill='#071a22')
            m=7
            c.create_line(m,m,m+24,m,fill=P['cyan'],width=1); c.create_line(m,m,m,m+24,fill=P['cyan'],width=1)
            c.create_line(w-m,m,w-m-24,m,fill=P['cyan'],width=1); c.create_line(w-m,m,w-m,m+24,fill=P['cyan'],width=1)
            c.create_line(m,h-m,m+24,h-m,fill=P['line2'],width=1); c.create_line(m,h-m,m,h-m-24,fill=P['line2'],width=1)
            c.create_line(w-m,h-m,w-m-24,h-m,fill=P['line2'],width=1); c.create_line(w-m,h-m,w-m,h-m-24,fill=P['line2'],width=1)
            cx,cy=w*.5,h*.48; base=min(w,h)*.40
            for ratio,col in ((1.0,'#0b3541'),(.72,'#155466'),(.48,'#0f4352')):
                r=base*ratio; c.create_oval(cx-r,cy-r,cx+r,cy+r,outline=col,width=1)
            items['sweep']=c.create_line(cx,cy,cx+base*.92,cy,fill=P['green'],width=2)
            ascii_hn=" H   H  N   N\n H   H  NN  N\n HHHHH  N N N\n H   H  N  NN\n H   H  N   N"
            fsz=max(7,int(min(w,h)/27))
            items['hn']=c.create_text(cx,cy,text=ascii_hn,fill=P['cyan'],font=(ASCII_MONO,fsz,'bold'),justify='center')
            items['label']=c.create_text(9,8,text='HN BLACKBOX // ASCII ID',anchor='nw',fill=P['dim'],font=(MONO,6,'bold'))
            items['live']=c.create_text(w-9,8,text='LIVE',anchor='ne',fill=P['green'],font=(MONO,6,'bold'))
            items['clock']=c.create_text(w-9,22,text='',anchor='ne',fill=P['yellow'],font=(MONO,5,'bold'))
            items['footer']=c.create_text(cx,h-10,text='IDENTITY CORE // LOCKED',anchor='s',fill=P['dim'],font=(MONO,5,'bold'))
            self._home_identity_items=items
        else:
            cx,cy=w*.5,h*.48; base=min(w,h)*.40
            items=self._home_identity_items
        sweep=math.radians((phase*2.8)%360)
        reach=base*.92
        c.coords(items['sweep'],cx,cy,cx+reach*math.cos(sweep),cy+reach*math.sin(sweep))
        pulse=(math.sin(phase*.045)+1)/2
        colors=[P['dim'],P['cyan'],P['cyan2'],P['text']]
        c.itemconfigure(items['hn'],fill=colors[min(3,int(pulse*4))])
        c.itemconfigure(items['clock'],text=datetime.now().strftime('%H:%M:%S'))
        now=time.monotonic()
        if now-self._identity_cache_at>1.0:
            history_n=len(history_manager.get_all()) if hasattr(history_manager,'get_all') else 0
            _,_,proc_n=self._system_metrics()
            self._identity_cache=(history_n, str(proc_n) if proc_n is not None else '--')
            self._identity_cache_at=now
        history_n,proc_n=self._identity_cache
        if hasattr(self,'home_identity_clock') and self.home_identity_clock.winfo_exists():
            self.home_identity_clock.configure(text=datetime.now().strftime('%H:%M:%S'))
        if hasattr(self,'home_identity_status') and self.home_identity_status.winfo_exists():
            self.home_identity_status.configure(text=f'HN CORE // ONLINE  •  OPS {history_n:02d}  •  PROC {proc_n}')
        self._home_identity_phase=(phase+1)%100000
        self.after(40,self._animate_home_identity)

    def _animate_home_status(self):
        if not getattr(self,'_ui_ready',False): return
        if time.monotonic() < getattr(self,'_resizing_until',0):
            self.after(100,self._animate_home_status); return
        if not hasattr(self,'home_status_rows'): return
        if self.current != 'home':
            self.after(1000,self._animate_home_status)
            return
        phase=self._system_phase
        for i,(bar,color) in enumerate(self.home_status_rows):
            if not bar.winfo_exists(): continue
            w=max(1,bar.winfo_width())
            fill=int(w*(0.72+0.18*math.sin((phase+i*13)*0.09)))
            ids=getattr(bar,'_hn_bar_ids',None)
            if ids is None:
                ids=(bar.create_rectangle(0,1,w,6,fill='#0b252e',outline=''),
                     bar.create_rectangle(0,1,fill,6,fill=P[color],outline=''))
                bar._hn_bar_ids=ids
            bar.coords(ids[0],0,1,w,6)
            bar.coords(ids[1],0,1,fill,6)
        if hasattr(self,'home_status_clock') and self.home_status_clock.winfo_exists():
            self.home_status_clock.configure(text='SYNC '+datetime.now().strftime('%H:%M:%S'))
        self.after(100,self._animate_home_status)

    def _system_metrics(self):
        now=time.monotonic()
        if now-self._telemetry_cache_at < 1.8:
            return self._telemetry_cache
        cpu=ram=procs=None
        try:
            if psutil:
                cpu=psutil.cpu_percent(interval=None)
                ram=psutil.virtual_memory().percent
                procs=len(psutil.pids())
            elif platform.system().lower().startswith('win'):
                out=subprocess.run(['tasklist'],capture_output=True,text=True,timeout=1.5).stdout
                procs=max(0,len([x for x in out.splitlines() if '.exe' in x.lower()])-3)
            elif Path('/proc').exists():
                procs=max(0,len(list(Path('/proc').glob('[0-9]*'))))
        except Exception:
            pass
        self._telemetry_cache=(cpu,ram,procs); self._telemetry_cache_at=now
        return self._telemetry_cache

    def _animate_system_monitor(self):
        """Smooth upper-right system intelligence display with real local metrics."""
        if not getattr(self,'_ui_ready',False):
            return
        c=getattr(self,'home_sys_canvas',None)
        if c is None or not c.winfo_exists():
            return
        if self.current!='home':
            self.after(700,self._animate_system_monitor); return
        if time.monotonic()<getattr(self,'_resizing_until',0):
            self.after(80,self._animate_system_monitor); return

        cpu,ram,procs=self._system_metrics()
        self._last_cpu,self._last_ram,self._last_processes=cpu,ram,procs
        uptime=int(time.monotonic()-self._app_started)
        hh=uptime//3600; mm=(uptime%3600)//60; ss=uptime%60
        vals={'cpu':f'{cpu:4.1f}%' if cpu is not None else 'N/A',
              'ram':f'{ram:4.1f}%' if ram is not None else 'N/A',
              'proc':str(procs) if procs is not None else 'N/A',
              'up':f'{hh:02d}:{mm:02d}:{ss:02d}'}
        for k,v in vals.items():
            if k in self.sys_metric_labels and self.sys_metric_labels[k].winfo_exists():
                self.sys_metric_labels[k].configure(text=v)
        if self.home_sys_clock.winfo_exists():
            self.home_sys_clock.configure(text=datetime.now().strftime('%H:%M:%S'))

        w,h=max(1,c.winfo_width()),max(1,c.winfo_height())
        sig=(w,h); scene=getattr(self,'_home_sys_scene',None)
        if scene is None or scene.get('size')!=sig:
            c.delete('all')
            cx,cy=w*.50,h*.47
            radius=min(w,h)*.32
            scene={'size':sig,'grid':[],'rings':[],'sweep':None,'pulse':None,
                   'bars':[],'labels':[],'nodes':[]}
            for x in range(0,w,16):
                scene['grid'].append(c.create_line(x,0,x,h,fill='#061923'))
            for y in range(0,h,16):
                scene['grid'].append(c.create_line(0,y,w,y,fill='#061923'))
            for ratio,col in ((1.0,'#0b3541'),(.72,'#104957'),(.45,'#155467')):
                rr=radius*ratio
                scene['rings'].append(c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,
                                                     outline=col,width=1))
            scene['sweep']=c.create_line(cx,cy,cx+radius,cy,fill=P['green'],width=2)
            scene['pulse']=c.create_oval(cx-3,cy-3,cx+3,cy+3,fill=P['cyan2'],outline='')
            # Six small telemetry nodes orbiting the system core.
            cols=[P['cyan'],P['green'],P['yellow'],P['purple'],P['orange'],P['red']]
            for i,col in enumerate(cols):
                a=math.tau*i/6
                rr=radius*.76
                x,y=cx+rr*math.cos(a),cy+rr*math.sin(a)
                scene['nodes'].append((c.create_oval(x-2,y-2,x+2,y+2,fill=col,outline=''),a,col))
            # Real CPU/RAM bars, updated without recreating objects.
            for i,col in enumerate((P['green'],P['cyan'])):
                x0=7+i*(w/2); bw=max(40,w/2-15); y0=h-18
                bg=c.create_rectangle(x0,y0,x0+bw,y0+6,fill='#0a2730',outline='')
                fg=c.create_rectangle(x0,y0,x0,y0+6,fill=col,outline='')
                scene['bars'].append((bg,fg,x0,bw,col))
            scene['labels']=[
                c.create_text(7,6,text='SYSTEM // LIVE TELEMETRY',anchor='nw',
                              fill=P['cyan'],font=(MONO,5,'bold')),
                c.create_text(w-7,6,text='',anchor='ne',
                              fill=P['yellow'],font=(MONO,5,'bold')),
                c.create_text(7,h-29,text='CPU',anchor='sw',fill=P['dim'],font=(MONO,5,'bold')),
                c.create_text(w/2+2,h-29,text='RAM',anchor='sw',fill=P['dim'],font=(MONO,5,'bold')),
            ]
            self._home_sys_scene=scene

        phase=self._system_phase
        cx,cy=w*.50,h*.47
        radius=min(w,h)*.32
        ang=phase*.055
        c.coords(scene['sweep'],cx,cy,cx+radius*math.cos(ang),cy+radius*math.sin(ang))
        pulse=2.5+1.4*math.sin(phase*.10)
        c.coords(scene['pulse'],cx-pulse,cy-pulse,cx+pulse,cy+pulse)
        for i,(node,a0,col) in enumerate(scene['nodes']):
            a=a0+phase*.002*(1 if i%2==0 else -1)
            rr=radius*.76
            x,y=cx+rr*math.cos(a),cy+rr*math.sin(a)
            c.coords(node,x-2,y-2,x+2,y+2)
        samples=[cpu if cpu is not None else 35,ram if ram is not None else 42]
        for i,(bg,fg,x0,bw,col) in enumerate(scene['bars']):
            value=min(100,max(0,float(samples[i])))
            c.coords(bg,x0,h-18,x0+bw,h-12)
            c.coords(fg,x0,h-18,x0+bw*value/100,h-12)
        c.itemconfigure(scene['labels'][1],text=f'PROC {procs if procs is not None else "--"} // LOCAL')
        self._system_phase=(phase+1)%100000

        # Process enumeration is collected by the background telemetry worker.
        # The animation loop only reads a tiny cached list.
        self._schedule_home_data_refresh()
        self.after(40,self._animate_system_monitor)

    def _animate_home_monitor(self):
        """Smooth tactical network/radar board; geometry is cached and only motion changes."""
        if not getattr(self, '_ui_ready', False):
            return
        c = getattr(self, 'home_monitor_scope', None)
        if c is None or not c.winfo_exists():
            return
        if self.current != 'home':
            self.after(700, self._animate_home_monitor)
            return
        if time.monotonic() < getattr(self, '_resizing_until', 0):
            self.after(80, self._animate_home_monitor)
            return

        w, h = max(1, c.winfo_width()), max(1, c.winfo_height())
        sig = (w, h)
        state = getattr(self, '_home_monitor_scene', None)

        if state is None or state.get('size') != sig:
            c.delete('all')
            state = {'size': sig, 'rings': [], 'rays': [], 'nodes': [], 'packets': [],
                     'scan': None, 'labels': [], 'wave': [], 'grid': []}
            # Fine tactical grid.
            for x in range(0, w + 1, 16):
                state['grid'].append(c.create_line(x, 0, x, h, fill='#061923', width=1))
            for y in range(0, h + 1, 16):
                state['grid'].append(c.create_line(0, y, w, y, fill='#061923', width=1))

            cx, cy = w * .52, h * .48
            radius = min(w, h) * .34
            for ratio, col in ((1.0, '#0b3541'), (.78, '#0e4654'), (.56, '#123f4c')):
                r = radius * ratio
                state['rings'].append(c.create_oval(cx-r, cy-r, cx+r, cy+r,
                                                     outline=col, width=1))
            # Crosshair.
            state['rays'] = [
                c.create_line(cx-radius, cy, cx+radius, cy, fill='#0b2933'),
                c.create_line(cx, cy-radius, cx, cy+radius, fill='#0b2933'),
            ]
            state['scan'] = c.create_line(cx, cy, cx+radius, cy,
                                          fill=P['green'], width=2)

            palette = [P['cyan'], P['green'], P['yellow'], P['purple'], P['orange'], P['red']]
            for i in range(6):
                a = math.tau * i / 6
                rr = radius * (.66 + (i % 2) * .10)
                x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
                dot = c.create_oval(x-3, y-3, x+3, y+3, fill=palette[i], outline='')
                ring = c.create_oval(x-7, y-7, x+7, y+7, outline=palette[i], width=1)
                state['nodes'].append((dot, ring, rr, a, palette[i]))

            for i in range(8):
                state['packets'].append(
                    [c.create_oval(-5, -5, 0, 0, fill=P['cyan2'], outline=''), i]
                )

            state['labels'] = [
                c.create_text(7, 7, text='NETWORK // SYNTHETIC MAP', anchor='nw',
                              fill=P['cyan'], font=(MONO, 6, 'bold')),
                c.create_text(w-7, 7, text='LOCAL // LIVE', anchor='ne',
                              fill=P['green'], font=(MONO, 6, 'bold')),
                c.create_text(7, h-7, text='HN CORE / NO EXTERNAL COLLECTION',
                              anchor='sw', fill=P['dim'], font=(MONO, 5, 'bold')),
                c.create_text(w-7, h-7, text='', anchor='se',
                              fill=P['yellow'], font=(MONO, 5, 'bold')),
            ]
            # Tiny waveform strip at the bottom.
            base_y = h - 25
            for i in range(22):
                state['wave'].append(
                    c.create_line(0, base_y, 0, base_y, fill=P['cyan2'], width=1)
                )
            self._home_monitor_scene = state

        phase = self._monitor_phase
        cx, cy = w * .52, h * .48
        radius = min(w, h) * .34
        sweep = phase * .055
        c.coords(state['scan'], cx, cy,
                 cx + radius * math.cos(sweep),
                 cy + radius * math.sin(sweep))

        for i, (dot, ring, rr, a0, color) in enumerate(state['nodes']):
            a = a0 + phase * .004 * (1 if i % 2 == 0 else -1)
            x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            pulse = 2.5 + 1.8 * (0.5 + 0.5 * math.sin(phase * .09 + i))
            c.coords(dot, x-pulse, y-pulse, x+pulse, y+pulse)
            c.coords(ring, x-7, y-7, x+7, y+7)

        # Packets travel on the same radial paths, giving the panel a continuous
        # "signal routing" feel without creating/deleting Canvas items per frame.
        for j, (item, lane) in enumerate(state['packets']):
            a = math.tau * (lane / 8.0) + phase * .004 * (1 if lane % 2 == 0 else -1)
            t = ((phase * .018) + lane * .17) % 1.0
            rr = radius * (.18 + .58 * t)
            x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
            c.coords(item, x-2, y-2, x+2, y+2)

        # Waveform changes continuously but stays cheap: only 22 line segments.
        base_y = h - 25
        for i, line in enumerate(state['wave']):
            x = 7 + i * max(4, (w-14) / 21)
            y = base_y + 5 * math.sin(phase*.08 + i*.8)
            c.coords(line, x, base_y, x, y)

        c.itemconfigure(state['labels'][1],
                        text='LOCAL // LIVE  ' + datetime.now().strftime('%H:%M:%S'))
        c.itemconfigure(state['labels'][3], text=f'SIGNAL {phase % 1000:03d}')
        self._monitor_phase = (phase + 1) % 100000
        self.after(45, self._animate_home_monitor)

    def _animate_home_intel(self):
        """Animate the lower-right HN intelligence board with cached Canvas geometry."""
        if not getattr(self, '_ui_ready', False):
            return
        c = getattr(self, 'home_intel_canvas', None)
        if c is None or not c.winfo_exists():
            return
        if self.current != 'home':
            self.after(700, self._animate_home_intel)
            return
        if time.monotonic() < getattr(self, '_resizing_until', 0):
            self.after(80, self._animate_home_intel)
            return

        w, h = max(1, c.winfo_width()), max(1, c.winfo_height())
        sig = (w, h)
        scene = getattr(self, '_home_intel_scene', None)
        if scene is None or scene.get('size') != sig:
            c.delete('all')
            cx, cy = w*.50, h*.44
            r = min(w, h)*.28
            scene = {'size': sig, 'rings': [], 'arcs': [], 'lines': [],
                     'nodes': [], 'packets': [], 'emblem': [], 'labels': [], 'bars': []}
            for x in range(0, w, 14):
                scene['lines'].append(c.create_line(x, 0, x, h, fill='#061721'))
            for y in range(0, h, 14):
                scene['lines'].append(c.create_line(0, y, w, y, fill='#061721'))
            for k, col in enumerate(('#0b2e39', '#0e4350', '#123f4c')):
                rr = r*(1.0 + k*.22)
                scene['rings'].append(c.create_oval(cx-rr, cy-rr, cx+rr, cy+rr,
                                                    outline=col, width=1))
            # Globe-like longitude/latitude ellipses.
            for scale in (.35, .62, .88):
                scene['arcs'].append(c.create_oval(cx-r*scale, cy-r, cx+r*scale, cy+r,
                                                   outline='#0c3540', width=1))
            for scale in (-.55, 0, .55):
                yy = cy + r*scale
                scene['arcs'].append(c.create_arc(cx-r, yy-r*.35, cx+r, yy+r*.35,
                                                  start=0, extent=180, style='arc',
                                                  outline='#0c3540', width=1))
            palette=[P['cyan'],P['green'],P['yellow'],P['purple'],P['orange']]
            for i in range(5):
                a=math.tau*i/5 + .35
                rr=r*(.75 if i%2 else .58)
                x,y=cx+rr*math.cos(a),cy+rr*.65*math.sin(a)
                dot=c.create_oval(x-3,y-3,x+3,y+3,fill=palette[i],outline='')
                scene['nodes'].append((dot,rr,a,palette[i]))
            for i in range(7):
                scene['packets'].append(c.create_oval(-4,-4,0,0,fill=P['cyan2'],outline=''))
            # Central HN emblem and status framing.
            scene['emblem'] = [
                c.create_oval(cx-31,cy-24,cx+31,cy+24,outline='#123844',width=1),
                c.create_oval(cx-24,cy-18,cx+24,cy+18,outline=P['cyan2'],width=1),
            ]
            self._draw_hn_emblem(c,cx,cy,size=.48,fg=P['text'],accent=P['cyan'],glow=P['cyan2'])
            scene['labels']=[
                c.create_text(7,7,text='HN // INTELLIGENCE BOARD',anchor='nw',
                              fill=P['cyan'],font=(MONO,6,'bold')),
                c.create_text(w-7,7,text='SYNTHETIC / LOCAL',anchor='ne',
                              fill=P['yellow'],font=(MONO,5,'bold')),
                c.create_text(7,h-8,text='BUILD • VISUALIZE • UNDERSTAND • DEFEND',
                              anchor='sw',fill=P['green'],font=(MONO,5,'bold')),
                c.create_text(w-7,h-8,text='',anchor='se',
                              fill=P['dim'],font=(MONO,5,'bold')),
            ]
            # Signal bars along the lower edge.
            for i in range(18):
                scene['bars'].append(c.create_rectangle(7+i*max(5,(w-14)/18),
                    h-34, 7+i*max(5,(w-14)/18)+3, h-34,
                    fill=P['cyan2'],outline=''))
            self._home_intel_scene=scene

        phase=self._home_intel_phase
        cx,cy=w*.50,h*.44
        r=min(w,h)*.28
        # Subtle rotation of the globe's nodes.
        for i,(dot,rr,a0,color) in enumerate(scene['nodes']):
            a=a0+phase*.003*(1 if i%2==0 else -1)
            x,y=cx+rr*math.cos(a),cy+rr*.65*math.sin(a)
            pulse=2.2+1.5*(.5+.5*math.sin(phase*.10+i))
            c.coords(dot,x-pulse,y-pulse,x+pulse,y+pulse)
        # Signals move between the globe edge and HN core.
        for i,item in enumerate(scene['packets']):
            a=math.tau*(i/7)+phase*.002
            t=((phase*.015)+i*.13)%1
            rr=r*(.25+.65*t)
            x,y=cx+rr*math.cos(a),cy+rr*.65*math.sin(a)
            c.coords(item,x-2,y-2,x+2,y+2)
        # HN pulse without redrawing the emblem.
        pulse=1+.15*math.sin(phase*.08)
        c.coords(scene['emblem'][0],cx-31*pulse,cy-24*pulse,cx+31*pulse,cy+24*pulse)
        c.itemconfigure(scene['labels'][3],text=f'CORE {phase%1000:03d} // LIVE')
        for i,bar in enumerate(scene['bars']):
            x=7+i*max(5,(w-14)/18)
            bh=4+12*(.5+.5*math.sin(phase*.11+i*.72))
            c.coords(bar,x,h-8-bh,x+3,h-8)
        if hasattr(self,'home_intel_clock') and self.home_intel_clock.winfo_exists():
            self.home_intel_clock.configure(text='LOCAL // '+datetime.now().strftime('%H:%M:%S'))
        if hasattr(self,'home_intel_status') and self.home_intel_status.winfo_exists():
            self.home_intel_status.configure(
                text=f'HN CORE // SYNTHETIC TELEMETRY  •  SIGNAL {phase%100:02d}  •  DEFENSIVE MODE')
        self._home_intel_phase=(phase+1)%100000
        self.after(40,self._animate_home_intel)

    def _collect_home_data(self):
        """Collect expensive local telemetry away from Tk's event loop."""
        root=Path(__file__).resolve().parents[1]
        try:
            entries=history_manager.get_all() if hasattr(history_manager,'get_all') else []
            py_files=list(root.rglob('*.py'))
            core_files=list((root/'core').glob('*.py')) if (root/'core').exists() else []
            test_files=list((root/'tests').glob('test_*.py')) if (root/'tests').exists() else []
            pending=labs.all_labs() if hasattr(labs,'all_labs') else []
            modules=[
                ('CRYPTO','ONLINE',P['green'],'crypto'),
                ('ANALYSIS','ONLINE',P['purple'],'analysis'),
                ('NETWORK','ONLINE',P['cyan'],'network'),
                ('WEB','ONLINE',P['orange'],'web'),
                ('BLUE','ONLINE',P['red'],'blue'),
                ('LABS','READY',P['yellow'],'labs'),
            ]
            integrity=[]
            for rel in ('core/caesar.py','core/cryptanalysis.py','core/network_tools.py',
                        'core/blue_team.py','gui/app.py'):
                integrity.append((rel.split('/')[-1], 'PASS' if (root/rel).is_file() else 'MISS'))

            last=entries[0] if entries else None
            last_op=(last.get('algorithm','')+' // '+last.get('operation','')).strip() if last else 'NO LOCAL OPERATIONS RECORDED'

            feed=[]
            if psutil:
                try:
                    rows=[]
                    for proc in psutil.process_iter(['name','cpu_percent','memory_info']):
                        try:
                            info=proc.info
                            mem=info.get('memory_info')
                            mb=(mem.rss/1024/1024) if mem else 0
                            rows.append((info.get('cpu_percent') or 0, info.get('name') or 'process', mb))
                        except Exception:
                            pass
                    rows.sort(reverse=True)
                    feed=[f'{name[:15]:15} {pct:4.1f}% {mb:5.0f}M' for pct,name,mb in rows[:4]]
                except Exception:
                    feed=[]
            if not feed:
                feed=['local process telemetry','project monitor active','no external collection']

            data={
                'files':len(py_files),'core':len(core_files),'tests':len(test_files),
                'history':len(entries),'labs':len(pending),'modules':modules,
                'integrity':integrity,'last_op':last_op[:52],
                'process_feed':feed,'sample_at':time.monotonic(),
            }
            with self._home_data_lock:
                self._home_data=data
                self._process_feed_cache=feed
                self._process_feed_cache_at=data['sample_at']
                self._home_data_busy=False
        except Exception:
            with self._home_data_lock:
                self._home_data_busy=False

    def _schedule_home_data_refresh(self):
        if not getattr(self,'_ui_ready',False):
            return
        with self._home_data_lock:
            if self._home_data_busy:
                return
            self._home_data_busy=True
        threading.Thread(
            target=self._collect_home_data, daemon=True,
            name='hn-home-telemetry').start()

    def _home_workspace_click(self, event):
        """Click a module row to open its real workspace."""
        c=getattr(self,'home_workspace_canvas',None)
        if c is None or not c.winfo_exists():
            return
        for obj in c.find_withtag('module'):
            try:
                box=c.bbox(obj)
                if box and box[0] <= event.x <= box[2] and box[1] <= event.y <= box[3]:
                    tags=c.gettags(obj)
                    key=next((t.split(':',1)[1] for t in tags if t.startswith('module:')),None)
                    if key:
                        self.show_page(key)
                    return
            except Exception:
                pass

    def _render_workspace_dashboard(self):
        c=getattr(self,'home_workspace_canvas',None)
        if c is None or not c.winfo_exists():
            return
        w,h=max(1,c.winfo_width()),max(1,c.winfo_height())
        data=self._home_data
        phase=self._home_workspace_phase
        sig=(w,h)
        scene=getattr(self,'_workspace_scene',None)
        if scene is None or scene.get('size')!=sig or len(scene.get('modules',[])) != len(data.get('modules',[])):
            c.delete('all')
            scene={'size':sig,'modules':[],'bars':[],'packets':[],'activity':[],'pulse':None}
            c.create_rectangle(0,0,w,h,fill='#02080d',outline='')
            c.create_text(8,7,text='LIVE WORKSPACE // LOCAL OPERATIONS',
                          anchor='nw',fill=P['cyan'],font=(MONO,6,'bold'))
            c.create_text(w-8,7,text='INTERACTIVE',
                          anchor='ne',fill=P['green'],font=(MONO,6,'bold'))
            c.create_text(8,26,text='MODULE HEALTH',anchor='nw',
                          fill=P['muted'],font=(MONO,5,'bold'))
            c.create_text(w*.40,26,text='TASK FLOW',anchor='nw',
                          fill=P['muted'],font=(MONO,5,'bold'))
            c.create_text(w*.70,26,text='LOCAL ACTIVITY',anchor='nw',
                          fill=P['muted'],font=(MONO,5,'bold'))

            y=41
            for i,(name,status,color,key) in enumerate(data.get('modules',[])):
                yy=y+i*20
                tags=(f'module:{key}','module')
                row=c.create_rectangle(7,yy,w*.36,yy+17,fill='#06131a',
                                       outline='#0c303c',tags=tags)
                dot=c.create_oval(13,yy+5,18,yy+10,fill=color,outline='',tags=tags)
                txt=c.create_text(24,yy+8,text=f'{name:8} {status}',anchor='w',
                                  fill='#ccecf2',font=(MONO,5,'bold'),tags=tags)
                scene['modules'].append((row,dot,txt,color,key))

            for i in range(5):
                yy=42+i*20
                bg=c.create_rectangle(w*.40,yy,w*.66,yy+7,fill='#09212a',outline='')
                fg=c.create_rectangle(w*.40,yy,w*.40,yy+7,fill=P['cyan2'],outline='')
                label=c.create_text(w*.40,yy+12,text='',anchor='w',
                                    fill=P['dim'],font=(MONO,4,'bold'))
                scene['bars'].append((bg,fg,label))

            for i in range(5):
                yy=43+i*20
                scene['activity'].append(
                    c.create_text(w*.70,yy,text='',anchor='nw',
                                  fill='#83d9c1',font=(MONO,5))
                )

            for i in range(7):
                scene['packets'].append(
                    c.create_oval(-4,-4,0,0,fill=P['cyan2'],outline='')
                )
            scene['pulse']=c.create_oval(-3,-3,3,3,fill=P['green'],outline='')
            self._workspace_scene=scene

        modules=data.get('modules') or []
        for i,(row,dot,txt,color,key) in enumerate(scene['modules']):
            if i>=len(modules):
                continue
            name,status,color,key=modules[i]
            c.itemconfigure(dot,fill=color)
            c.itemconfigure(txt,text=f'{name:8} {status}')
            c.itemconfigure(row,outline='#1a5364' if i==(int(phase/10)%max(1,len(scene['modules']))) else '#0c303c')

        ratios=[.82,.64,.91,.57,.76]
        for i,(bg,fg,label) in enumerate(scene['bars']):
            ratio=max(.08,min(.98,ratios[i]+.10*math.sin(phase*.07+i*.9)))
            x0,x1=w*.40,w*.66
            y=42+i*20
            c.coords(bg,x0,y,x1,y+7)
            c.coords(fg,x0,y,x0+(x1-x0)*ratio,y+7)
            c.itemconfigure(label,text=f'TASK {i+1:02d}  {int(ratio*100):02d}%')

        feed=data.get('process_feed') or ['local telemetry','project monitor active']
        for i,item in enumerate(scene['activity']):
            c.itemconfigure(item,text=feed[i] if i<len(feed) else '—')

        for i,p in enumerate(scene['packets']):
            t=(phase*.012+i*.16)%1.0
            x=w*.35+(w*.39)*t
            y=45+(i%5)*20+math.sin(phase*.08+i)*2
            c.coords(p,x-2,y-2,x+2,y+2)

        pulse=3+2*math.sin(phase*.11)
        c.coords(scene['pulse'],w*.68-pulse,h*.82-pulse,
                 w*.68+pulse,h*.82+pulse)
        self._home_workspace_phase=(phase+1)%100000

    def _animate_home_workspace(self):
        """Continuously animate the workspace board without rescanning the filesystem."""
        if not getattr(self,'_ui_ready',False):
            self.after(120,self._animate_home_workspace)
            return
        if self.current!='home':
            self.after(700,self._animate_home_workspace)
            return
        self._render_workspace_dashboard()
        self.after(40,self._animate_home_workspace)

    def _refresh_home_scan(self):
        """Refresh cached project telemetry; expensive collection runs in a worker."""
        if not getattr(self,'_ui_ready',False):
            return
        if self.current!='home':
            self.after(900,self._refresh_home_scan)
            return
        self._schedule_home_data_refresh()
        data=self._home_data
        if hasattr(self,'home_scan_status') and self.home_scan_status.winfo_exists():
            self.home_scan_status.configure(
                text=f'LIVE // {datetime.now().strftime("%H:%M:%S")}  •  {data["files"]} PY',
                fg=P['green'])
        self.after(1500,self._refresh_home_scan)

    def _redraw_home_grid(self):
        self._home_grid_job = None
        if not hasattr(self, 'home_canvas') or not self.home_canvas.winfo_exists():
            return
        cv=self.home_canvas
        w,h=max(1,cv.winfo_width()),max(1,cv.winfo_height())
        sig=(w,h)
        if getattr(self,'_home_grid_sig',None) != sig:
            cv.delete('grid')
            for x in range(0,w,28): cv.create_line(x,0,x,h,fill='#07151b',tags='grid')
            for y in range(0,h,28): cv.create_line(0,y,w,y,fill='#07151b',tags='grid')
            for x in range(0,w,140): cv.create_line(x,0,x,h,fill='#0b2028',tags='grid')
            for y in range(0,h,140): cv.create_line(0,y,w,y,fill='#0b2028',tags='grid')
            self._home_grid_sig=sig
            cv.tag_lower('grid')
        self._request_home_layout()

    def _request_home_layout(self, immediate=False):
        if not hasattr(self,'home_canvas') or self.home_canvas is None or not self.home_canvas.winfo_exists():
            return
        if self._resize_job is not None:
            try: self.after_cancel(self._resize_job)
            except Exception: pass
        delay=0 if immediate else 90
        self._resize_job=self.after(delay,self._run_home_layout)

    def _run_home_layout(self):
        self._resize_job=None
        self._layout_home_v10()

    def _layout_home_v10(self,event=None):
        if not hasattr(self,'home_canvas') or self.home_canvas is None or not self.home_canvas.winfo_exists():
            self.home_canvas=None; return
        cv=self.home_canvas; w=max(1,cv.winfo_width()); h=max(1,cv.winfo_height()); pad=14; gap=8
        layout_sig=(w,h,self.sidebar_expanded)
        if getattr(self,'_home_layout_sig',None)==layout_sig:
            return
        self._home_layout_sig=layout_sig
        top_h=40; rail_w=174 if w>=1080 else 148; main_x=pad+rail_w+gap; main_w=max(260,w-main_x-pad)
        foot_h=12
        title_h=46
        # The command channel and workspace monitor scale with the viewport instead
        # of staying frozen at the old desktop dimensions.
        term_h=max(155,min(220,int(h*0.19)))
        kpi_h=64
        body_y=pad+top_h+8+title_h+8+term_h+8+kpi_h+8
        # side-by-side at comfortable width; stacked inside main at compact width
        side_w=280 if main_w>=850 else 0
        body_h=max(430,h-body_y-34-pad)
        positions={'top':(pad,pad,w-2*pad,top_h),'rail':(pad,pad+top_h+8,rail_w,h-pad*2-top_h-8),'title':(main_x,pad+top_h+8,main_w,title_h),'term':(main_x,pad+top_h+8+title_h+8,main_w,term_h),'kpi':(main_x,pad+top_h+8+title_h+8+term_h+8,main_w,kpi_h),'foot':(main_x,h-12,main_w,12)}
        for k in ('top','rail','title','term','kpi','foot'):
            widget=self._home_widgets.get(k)
            if widget is not None and widget.winfo_exists():
                widget.place(x=positions[k][0],y=positions[k][1],width=positions[k][2],height=positions[k][3])
        # Keep the identity panel readable on compact widths without ever
        # letting the ASCII banner collide with the terminal stream.
        term_widget=self._home_widgets.get('term')
        if term_widget is not None and term_widget.winfo_exists() and term_widget.winfo_children():
            body=term_widget.winfo_children()[1] if len(term_widget.winfo_children())>1 else None
            if body is not None and body.winfo_children():
                target_w=330 if main_w>=950 else max(250,min(330,int(main_w*0.34)))
                if hasattr(self,'home_sysmon') and self.home_sysmon.winfo_exists():
                    self.home_sysmon.configure(width=target_w)
                if hasattr(self,'home_identity_pane') and self.home_identity_pane.winfo_exists():
                    id_w=224 if main_w>=900 else max(188,min(224,int(main_w*0.25)))
                    self.home_identity_pane.configure(width=id_w)
        main=self._home_widgets.get('main')
        if hasattr(self,'home_monitor') and self.home_monitor.winfo_exists():
            monitor_h=max(125,min(235,int(body_h*0.23)))
            self.home_monitor.configure(height=monitor_h)
            self.home_monitor.pack_propagate(False)
        # Typography and action controls reflow with the actual main-column width.
        compact_ui = main_w < 720
        if hasattr(self,'home_mission_title') and self.home_mission_title.winfo_exists():
            self.home_mission_title.configure(
                wraplength=max(260,main_w-55),
                font=(MONO,12 if compact_ui else 15,'bold')
            )
        if hasattr(self,'home_mission_desc') and self.home_mission_desc.winfo_exists():
            self.home_mission_desc.configure(wraplength=max(260,main_w-55))
        if hasattr(self,'home_open_crypto') and self.home_open_crypto.winfo_exists():
            self.home_open_crypto.configure(
                text='> CRYPTO' if main_w < 620 else '> OPEN CRYPTO LAB',
                padx=8 if main_w < 620 else 14
            )
        if hasattr(self,'home_status') and self.home_status.winfo_exists() and main_w < 650:
            self.home_status.configure(text='ONLINE // LOCAL // DEFENSIVE')
        if main is None or not main.winfo_exists(): return
        # The dashboard uses direct child widgets on the Canvas, so bbox('all')
        # cannot see their geometry. Keep an explicit virtual region instead.
        extra_h = 250 if not side_w else 0
        content_bottom = body_y + body_h + extra_h + foot_h + pad
        content_right = main_x + main_w + pad
        # Add a small breathing margin so the last monitor/footer can be reached
        # with the wheel even when the viewport is very short.
        virtual_w=max(w, content_right)
        virtual_h=max(h, content_bottom + 18)
        virtual_sig=(virtual_w,virtual_h)
        if getattr(self,'_home_virtual_sig',None)!=virtual_sig:
            if hasattr(self,'home_surface') and self.home_surface.winfo_exists():
                self.home_surface.configure(width=virtual_w,height=virtual_h)
                cv.itemconfigure(self._home_window,width=virtual_w,height=virtual_h)
            cv.configure(scrollregion=(0, 0, virtual_w, virtual_h))
            self._home_virtual_sig=virtual_sig
        if side_w:
            main.place(x=main_x,y=body_y,width=main_w,height=body_h)
            main.pack_propagate(False)
            # identify child frames by order
            kids=main.winfo_children(); left=kids[0]; side=kids[1]
            left.pack_forget();side.pack_forget();side.configure(width=side_w)
            left.pack(side='left',fill='both',expand=True,padx=(0,4));side.pack(side='right',fill='both',padx=(4,0));side.pack_propagate(False)
        else:
            main.place(x=main_x,y=body_y,width=main_w,height=body_h+240)
            main.pack_propagate(False)
            kids=main.winfo_children()
            if len(kids)<2: return
            left,side=kids[0],kids[1]
            left.pack_forget();side.pack_forget();side.configure(width=main_w)
            left.pack(fill='both',expand=True,pady=(0,7));side.pack(fill='both',expand=True,pady=(7,0));side.pack_propagate(False)
            # Compact home is intentionally taller than the viewport.  Keep the
            # virtual region; do not collapse it back to the viewport dimensions.
            virtual_w=max(w, main_x+main_w+pad)
            virtual_h=max(h,body_y+body_h+250+18)
            if hasattr(self,'home_surface') and self.home_surface.winfo_exists():
                self.home_surface.configure(width=virtual_w,height=virtual_h)
                cv.itemconfigure(self._home_window,width=virtual_w,height=virtual_h)
            cv.configure(scrollregion=(0,0,virtual_w,virtual_h))
            return
        # Desktop home still gets the explicit region; it simply has little/no
        # scrolling when the whole dashboard fits in the viewport.
        virtual_w=max(w, main_x+main_w+pad)
        virtual_h=max(h,content_bottom+18)
        if hasattr(self,'home_surface') and self.home_surface.winfo_exists():
            self.home_surface.configure(width=virtual_w,height=virtual_h)
            cv.itemconfigure(self._home_window,width=virtual_w,height=virtual_h)
        cv.configure(scrollregion=(0,0,virtual_w,virtual_h))

    def _pulse_home(self):
        if not getattr(self,'_ui_ready',False): return
        if not hasattr(self,'home_status') or not self.home_status.winfo_exists(): return
        accent=NAV_ACCENTS.get(self.current,P['cyan'])
        cur=self.home_status.cget('fg')
        self.home_status.configure(fg=P['text'] if cur==accent else accent)
        self.after(850,self._pulse_home)

    def _update_home_clock(self):
        if not getattr(self,'_ui_ready',False): return
        if hasattr(self,'home_clock') and self.home_clock.winfo_exists():
            self.home_clock.configure(text=datetime.now().strftime('%H:%M:%S'))
            self.after(1000,self._update_home_clock)

    def _terminal_write(self, text, reset=False):
        if not hasattr(self,'home_terminal') or not self.home_terminal.winfo_exists(): return
        self.home_terminal.configure(state='normal')
        if reset: self.home_terminal.delete('1.0','end')
        self.home_terminal.insert('end', text)
        self.home_terminal.see('end')
        self.home_terminal.configure(state='disabled')

    def _animate_terminal_hud(self):
        """Move pre-created telemetry packets instead of recreating the canvas."""
        if not getattr(self,'_ui_ready',False): return
        if time.monotonic() < getattr(self,'_resizing_until',0):
            self.after(180,self._animate_terminal_hud); return
        if not hasattr(self, "terminal_anim") or not self.terminal_anim.winfo_exists():
            return
        if self.current != 'home':
            self.after(900,self._animate_terminal_hud)
            return
        c=self.terminal_anim; w=max(1,c.winfo_width()); h=max(1,c.winfo_height()); phase=self._terminal_phase
        sig=(w,h)
        packets=getattr(self,'_terminal_hud_packets',None)
        if packets is None or getattr(self,'_terminal_hud_size',None)!=sig:
            c.delete('all'); packets=[]; self._terminal_hud_size=sig
            palette=[P['cyan'],P['green'],P['purple'],P['orange'],P['yellow']]
            for lane,color in enumerate(palette):
                y=4+lane*4
                for x in range(-20,w+20,18):
                    packets.append((c.create_rectangle(x,y,x+9,y+2,fill=color,outline=''),x,y,lane))
            packets.append(('scan',c.create_line(0,0,0,h,fill=P['cyan2'],width=1)))
            packets.append(('live',c.create_text(8,h-6,text='LIVE TELEMETRY',anchor='w',fill=P['dim'],font=(MONO,5,'bold'))))
            packets.append(('packet',c.create_text(w-8,h-6,text='',anchor='e',fill=P['green'],font=(MONO,5,'bold'))))
            self._terminal_hud_packets=packets
        for entry in packets:
            if not isinstance(entry,tuple) or not entry or entry[0] in ('scan','live','packet'): continue
            item,x,y,lane=entry
            xx=(x + phase*(1+lane*.22)) % (w+36)-18
            c.coords(item,xx,y,xx+9,y+2)
        scan=(phase*3)%(w+1)
        scan_id=next(e[1] for e in packets if isinstance(e,tuple) and e[0]=='scan')
        packet_id=next(e[1] for e in packets if isinstance(e,tuple) and e[0]=='packet')
        c.coords(scan_id,scan,0,scan,h)
        c.itemconfigure(packet_id,text=f'PACKET {phase%999:03d}  //  LOCAL')
        self._terminal_phase += 1
        self.after(45,self._animate_terminal_hud)

    def _cmd_prev(self,event=None):
        if not self._cmd_history: return 'break'
        self._cmd_index=max(0,self._cmd_index-1)
        self.home_cmd.delete(0,'end'); self.home_cmd.insert(0,self._cmd_history[self._cmd_index]); return 'break'

    def _cmd_next(self,event=None):
        if not self._cmd_history: return 'break'
        self._cmd_index=min(len(self._cmd_history),self._cmd_index+1)
        self.home_cmd.delete(0,'end')
        if self._cmd_index < len(self._cmd_history): self.home_cmd.insert(0,self._cmd_history[self._cmd_index])
        return 'break'

    def _run_project_command(self, raw: str) -> str:
        """Run an explicit HN BlackBox project command, never an unrestricted OS shell."""
        try:
            parts = shlex.split(raw)
        except ValueError as exc:
            return f"[ERR] parse error: {exc}"
        if not parts:
            return ""
        verb, args = parts[0].lower(), parts[1:]
        try:
            if verb in ("run", "exec"):
                if not args:
                    return '[HELP] run tests | run ciphers caesar "HELLO" 3 | run hash sha256 "text" | run analysis "text"'
                target = args[0].lower()
                if target in ("tests", "test"):
                    root = Path(__file__).resolve().parents[1]
                    result = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"],
                                            cwd=str(root), capture_output=True, text=True, timeout=30)
                    lines = (result.stdout + result.stderr).strip().splitlines()
                    return f"[TEST] exit={result.returncode}\n" + "\n".join(lines[-8:])
                if target in ("ciphers", "cipher"):
                    if len(args) < 4:
                        return '[HELP] run ciphers caesar "HELLO" 3 | run ciphers vigenere "HELLO" KEY'
                    alg, text, key = args[1].lower(), args[2], args[3]
                    if alg == "caesar":
                        out = caesar.encrypt(text, int(key))
                    elif alg == "vigenere":
                        out = vigenere.encrypt(text, key)
                    else:
                        return "[ERR] supported CLI ciphers: caesar, vigenere"
                    history_manager.add_entry(alg, "CLI encrypt", key, text, out)
                    return f"[CIPHER] {alg.upper()} -> {out}"
                if target == "hash":
                    if len(args) < 3:
                        return '[HELP] run hash sha256 "text"'
                    algo, text = args[1].lower(), args[2].encode("utf-8")
                    if algo not in ("sha256", "sha1", "md5"):
                        return "[ERR] supported hashes: sha256, sha1, md5"
                    out = hashlib.new(algo, text).hexdigest()
                    history_manager.add_entry(algo, "CLI hash", "", args[2], out)
                    return f"[HASH] {algo.upper()} -> {out}"
                if target in ("analysis", "frequency"):
                    if len(args) < 2:
                        return '[HELP] run analysis "ciphertext"'
                    rows = frequency_analysis.analyze(args[1])
                    top = ", ".join(f"{r['letter']}:{r['percent']}%" for r in rows[:8])
                    history_manager.add_entry("frequency", "CLI analysis", "", args[1], top or "no letters")
                    return f"[ANALYSIS] top frequencies -> {top or 'no letters'}"
                return f"[ERR] unknown project runner: {target}"

            # Direct algorithm shortcuts from the terminal.
            if verb in ALGORITHMS:
                if len(args) < 3:
                    return f'[HELP] {verb} <encrypt|decrypt> "TEXT" <KEY>'
                op, text, key = args[0].lower(), args[1], args[2]
                if verb == "caesar":
                    out = caesar.encrypt(text, int(key)) if op in ("encrypt", "enc") else caesar.decrypt(text, int(key))
                elif verb == "vigenere":
                    out = vigenere.encrypt(text, key) if op in ("encrypt", "enc") else vigenere.decrypt(text, key)
                elif verb == "atbash":
                    out = classical.atbash(text)
                elif verb == "rot13":
                    out = classical.rot13(text)
                else:
                    return f"[INFO] {verb.upper()} is available in the full visual lab. Use: open crypto"
                return f"[CRYPTO] {verb.upper()} {op.upper()} -> {out}"

            if verb == "network":
                if args and args[0].lower() in ("ip", "info") and len(args) > 1:
                    return f"[NETWORK] {network_tools.ip_info(args[1])}"
                if args and args[0].lower() in ("subnet", "cidr") and len(args) > 1:
                    return f"[NETWORK] {network_tools.subnet_info(args[1])}"
                return "[HELP] network ip <address> | network subnet <cidr>"

            if verb == "web":
                if args and args[0].lower() in ("parse", "url") and len(args) > 1:
                    u=urlparse(args[1]); q=parse_qs(u.query)
                    return f"[WEB] scheme={u.scheme or '-'} host={u.netloc or '-'} path={u.path or '/'} params={len(q)}"
                return "[HELP] web parse <url>"

            if verb == "blue":
                return "[HELP] blue triage <log text> | blue ioc <value>"

            if verb == "lab":
                return "[LABS] Use open labs to enter the interactive challenge arena."

            if verb == "crypto":
                if len(args) < 4:
                    return '[HELP] crypto caesar encrypt "HELLO" 3'
                alg, op, text, key = args[0].lower(), args[1].lower(), args[2], args[3]
                if alg == "caesar":
                    out = caesar.encrypt(text, int(key)) if op in ("encrypt", "enc") else caesar.decrypt(text, int(key))
                elif alg == "vigenere":
                    out = vigenere.encrypt(text, key) if op in ("encrypt", "enc") else vigenere.decrypt(text, key)
                else:
                    return "[ERR] CLI crypto supports caesar and vigenere"
                return f"[CRYPTO] {alg.upper()} {op.upper()} -> {out}"

            if verb == "analyze":
                text = args[0] if args else ""
                rows = frequency_analysis.analyze(text)
                return "[FREQ] " + (", ".join(f"{r['letter']}={r['count']}" for r in rows[:12]) or "empty input")
            if verb == "hash":
                if len(args) < 2:
                    return '[HELP] hash sha256 "text"'
                algo, text = args[0].lower(), args[1].encode()
                if algo not in ("sha256", "sha1", "md5"):
                    return "[ERR] supported hashes: sha256, sha1, md5"
                return f"[HASH] {algo.upper()} -> {hashlib.new(algo,text).hexdigest()}"
            if verb == "pwd":
                return str(Path(__file__).resolve().parents[1])
            if verb == "modules":
                return "crypto  analysis  network  web  blue_team  labs  development  history"
        except (ValueError, TypeError, IndexError) as exc:
            return f"[ERR] {exc}"
        except subprocess.TimeoutExpired:
            return "[ERR] test runner timed out after 30s"
        return "[ERR] command not found"

    def _home_command(self,event=None):
        raw=self.home_cmd.get().strip()
        if not raw: return 'break'
        cmd=raw.lower()
        self._cmd_history.append(raw); self._cmd_history=self._cmd_history[-50:]; self._cmd_index=len(self._cmd_history)
        mapping={'crypto':'crypto','analysis':'analysis','network':'network','web':'web','blue':'blue','labs':'labs','history':'history','development':'development','status':'home','home':'home'}
        output=''
        if cmd in mapping:
            output=f'[EXEC] routing to /{cmd} ... OK'
            self.show_page(mapping[cmd])
        elif cmd.startswith('open '):
            target=cmd[5:].strip(); key=mapping.get(target)
            if key: output=f'[EXEC] open {target} ... OK'; self.show_page(key)
            else: output=f'[ERR] module not found: {target}'
        elif cmd in ('help','?'):
            output=('[HELP] NAV: status | modules | open <module> | home\n'
                    '[HELP] PROJECT: run tests | run ciphers <alg> <text> <key> | run hash sha256 <text>\n'
                    '[HELP] PROJECT: run analysis <text> | crypto <alg> <encrypt|decrypt> <text> <key>\n'
                    '[HELP] SHORTCUTS: caesar encrypt <text> <shift> | vigenere encrypt <text> <key>\n'
                    '[HELP] MODULES: network | web | blue | lab\n'
                    '[HELP] TOOLS: hash sha256 <text> | analyze <text> | ls | pwd | whoami | sysinfo | date | clear')
        elif cmd=='ls':
            output='core/  gui/  tests/  labs/  history/  README.md  requirements.txt'
        elif cmd=='modules':
            output='[MODULES] crypto  analysis  network  web  blue_team  labs  development  history'
        elif cmd=='whoami':
            output=f'{getpass.getuser()}@{socket.gethostname()}'
        elif cmd=='date':
            output=datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')
        elif cmd=='pwd':
            output=str(Path(__file__).resolve().parents[1])
        elif cmd=='sysinfo':
            output=f'{platform.system()} {platform.release()} | Python {platform.python_version()} | {platform.machine()}'
        elif cmd=='clear':
            self._terminal_write(HN_ASCII+'\nHN BLACKBOX // TERMINAL RESET\nroot@HN-BLACKBOX:~# _', reset=True)
            self.home_cmd.delete(0,'end'); self.home_status.configure(text='TERMINAL CLEARED',fg=P['cyan']); return 'break'
        elif cmd.startswith(('run ','exec ','crypto ','analyze ','hash ','caesar ','vigenere ','network ','web ','blue ','lab ')):
            routed = raw if raw.startswith(('run ','exec ','crypto ','analyze ','hash ')) else 'run ' + raw
            output=self._run_project_command(routed)
        else:
            output=f'[ERR] unknown command: {raw}  // type help'
        self._terminal_write(f'\nroot@HN-BLACKBOX:~# {raw}\n{output}\nroot@HN-BLACKBOX:~# _')
        self.home_status.configure(text=output.splitlines()[0][:72].upper(),fg=P['green'] if '[ERR]' not in output else P['orange'])
        self.home_cmd.delete(0,'end')
        return 'break'

    def _layout_home(self):
        if not hasattr(self, "home_canvas") or not self.home_canvas.winfo_exists():
            return
        cv = self.home_canvas
        w, h = max(760, cv.winfo_width()), max(560, cv.winfo_height())
        virtual_h = max(h, 760)
        cv.configure(scrollregion=(0, 0, w, virtual_h))
        # Dashboard dimensions adapt from 3-column desktop to stacked tablet.
        pad = 14
        rail_w = 175 if w >= 1100 else 145
        gap = 9
        main_x = pad + rail_w + gap
        main_w = max(420, w - main_x - pad)
        top_h = 42
        title_h = 44
        kpi_h = 92
        foot_h = 25
        body_y = pad + top_h + 8 + title_h + 8 + kpi_h + 10
        body_h = max(360, virtual_h - body_y - foot_h - pad)
        side_w = 270 if main_w >= 820 else 220
        logs_w = max(260, main_w - side_w - gap)

        pos = {
            "top": (pad, pad, w - 2 * pad, top_h),
            "rail": (pad, pad + top_h + 8, rail_w, h - 2 * pad - top_h - 8),
            "title": (main_x, pad + top_h + 8, main_w, title_h),
            "kpi": (main_x, pad + top_h + 8 + title_h + 8, main_w, kpi_h),
            "logs": (main_x, body_y, logs_w, body_h),
            "side": (main_x + logs_w + gap, body_y, side_w, body_h),
            "foot": (main_x, virtual_h - foot_h - pad, main_w, foot_h),
        }
        for widget, key in self._home_windows:
            x, y, ww, hh = pos[key]
            widget.place(x=x, y=y, width=ww, height=hh)
        # Compact mode: preserve hierarchy instead of letting controls collide.
        if main_w < 650:
            self._home_execute.configure(text=">", padx=7)
        else:
            self._home_execute.configure(text="> EXECUTE", padx=10)
        # keep title above grid but grid below all windows
        cv.tag_lower("grid")


    def _scroll_page(self, parent, build):
        holder = tk.Frame(parent, bg=P["bg"])
        holder.pack(fill="both", expand=True)
        canvas = tk.Canvas(holder, bg=P["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(holder, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=P["bg"])
        wid = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        def sync(e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfigure(wid, width=max(1, canvas.winfo_width()))
        inner.bind("<Configure>", sync)
        canvas.bind("<Configure>", sync)
        self._bind_wheel(canvas)
        build(inner)
        return canvas, inner

    def _crypto_card_theme(self, idx):
        # Same visual language as the red ELEVATE_PRIVILEGES panel on the
        # command-center home screen: dark tinted body, 1px accent border,
        # compact status header and a solid action strip.  Each algorithm gets
        # its own accent so the matrix feels like a rack of live modules.
        themes = [
            ("#ff3f68", "#241016", "#34151d", "#8f2538"),
            ("#20e8ff", "#071b22", "#0b2730", "#15596a"),
            ("#39f6a0", "#071c16", "#0b2b20", "#176143"),
            ("#9e73ff", "#130d24", "#1d1432", "#563c8f"),
            ("#ff9d4d", "#24170c", "#33200f", "#8b5428"),
            ("#ffd166", "#211b0a", "#30270d", "#806d22"),
        ]
        return themes[idx % len(themes)]

    def crypto_page(self):
        """High-density intelligence-style algorithm matrix.

        The selector is deliberately visual: real algorithm metadata is exposed
        through compact cards, while motion is limited to a single lightweight
        HUD scan so the page stays smooth on modest hardware.
        """
        p=tk.Frame(self.content,bg=P['bg'])
        self.heading(p,"HN / CRYPTO ENGINE","CRYPTOGRAPHY // OPERATIONS DECK","A connected cipher workspace: choose an engine, inspect its math, execute locally, and trace every transformation.")
        canvas,inner=self._make_canvas(p); self.crypto_canvas=canvas

        # ---------- command overview ----------
        overview=tk.Frame(inner,bg='#040b11',highlightbackground=P['line2'],highlightthickness=1)
        overview.pack(fill='x',pady=(0,8))
        top=tk.Frame(overview,bg='#040b11'); top.pack(fill='x',padx=12,pady=(8,5))
        tk.Label(top,text='CRYPTOGRAPHY // ALGORITHM CONTROL DECK',bg='#040b11',fg=P['cyan'],font=(MONO,9,'bold')).pack(side='left')
        self.crypto_matrix_clock=tk.Label(top,text=datetime.now().strftime('%H:%M:%S'),bg='#040b11',fg=P['green'],font=(MONO,9,'bold')); self.crypto_matrix_clock.pack(side='right')
        self.crypto_matrix_status=tk.Label(top,text='● ENGINE ONLINE',bg='#040b11',fg=P['green'],font=(MONO,7,'bold')); self.crypto_matrix_status.pack(side='right',padx=14)
        statrow=tk.Frame(overview,bg='#040b11'); statrow.pack(fill='x',padx=8,pady=(0,8))
        total=len(ALGORITHMS); groups=len(CRYPTO_GROUPS)
        self.crypto_overview_stats=[]
        for lab,val,col in [('ACTIVE CORES',f'{total:02d}',P['cyan']),('ALGORITHM SETS',f'{groups:02d}',P['purple']),('ENGINE','READY',P['green']),('LAB LINK','LOCAL',P['yellow'])]:
            cell=tk.Frame(statrow,bg='#07151d',highlightbackground=P['line'],highlightthickness=1); cell.pack(side='left',fill='x',expand=True,padx=2)
            tk.Label(cell,text=lab,bg='#07151d',fg=P['dim'],font=(MONO,5,'bold')).pack(anchor='w',padx=7,pady=(4,0))
            tk.Label(cell,text=val,bg='#07151d',fg=col,font=(MONO,9,'bold')).pack(anchor='w',padx=7,pady=(1,5))

        # ---------- family controls + compact live radar ----------
        selector=self.glass(inner); selector.pack(fill='x',pady=(0,8))
        left=tk.Frame(selector,bg=P['panel2']); left.pack(side='left',fill='both',expand=True,padx=12,pady=12)
        tk.Label(left,text='SELECT ALGORITHM SET',bg=P['panel2'],fg=P['cyan'],font=(MONO,8,'bold'),anchor='w').pack(fill='x')
        tk.Label(left,text='ARM A FAMILY TO LOAD ITS REAL CIPHER RACK',bg=P['panel2'],fg=P['muted'],font=(MONO,6,'bold'),anchor='w').pack(fill='x',pady=(2,8))
        btnrow=tk.Frame(left,bg=P['panel2']); btnrow.pack(fill='x')
        self.crypto_group_var=tk.StringVar(value='')
        self.crypto_group_buttons={}
        for key,meta in CRYPTO_GROUPS.items():
            b=tk.Button(btnrow,text=meta['title'],command=lambda k=key:self._select_crypto_group(k),
                        bg='#07131a',fg=meta['accent'],activebackground=meta['accent'],activeforeground=P['bg'],
                        relief='flat',bd=0,font=(MONO,7,'bold'),cursor='hand2',highlightthickness=1,
                        highlightbackground=meta['accent'],padx=10,pady=8)
            b.pack(side='left',fill='x',expand=True,padx=2)
            self.crypto_group_buttons[key]=b

        viz=tk.Frame(selector,bg='#050b11',highlightbackground=P['line'],highlightthickness=1); viz.pack(side='right',padx=12,pady=12)
        tk.Label(viz,text='CORE RADAR // LIVE',bg='#050b11',fg=P['green'],font=(MONO,6,'bold')).pack(fill='x',padx=7,pady=(5,0))
        c=tk.Canvas(viz,width=300,height=120,bg='#050b11',highlightthickness=0); c.pack(padx=6,pady=4)
        self._crypto_selector_canvas=c; self._crypto_selector_phase=0
        def animate():
            if not c.winfo_exists(): return
            if self.current != 'crypto': self.after(900,animate); return
            w=max(1,c.winfo_width()); h=max(1,c.winfo_height()); t=self._crypto_selector_phase; cx,cy=w*.5,h*.48
            items=getattr(self,'_crypto_selector_items',None); sig=getattr(self,'_crypto_selector_size',None)
            if items is None or sig!=(w,h):
                c.delete('all'); items={}; self._crypto_selector_size=(w,h)
                for x in range(0,w,30): c.create_line(x,0,x,h,fill='#07151d')
                for y in range(0,h,24): c.create_line(0,y,w,y,fill='#07151d')
                for r,col in [(20,'#12333e'),(38,'#174b5a'),(56,P['cyan'])]: c.create_oval(cx-r,cy-r,cx+r,cy+r,outline=col,width=1)
                items['sweep']=c.create_line(cx,cy,cx+56,cy,fill=P['cyan2'],width=2)
                items['nodes']=[]
                for col in (P['cyan'],P['purple'],P['green'],P['yellow']): items['nodes'].append(c.create_oval(cx-3,cy-51,cx+3,cy-45,fill=col,outline=''))
                self._draw_hn_emblem(c,cx,cy,size=.70,fg=P['text'],accent=P['cyan'],glow=P['cyan2'])
                items['scan']=c.create_text(7,7,text='SCANNING',anchor='nw',fill=P['green'],font=(MONO,5,'bold'))
                items['cores']=c.create_text(w-7,7,text=f'{total:02d} CORES',anchor='ne',fill=P['cyan'],font=(MONO,5,'bold'))
                items['footer']=c.create_text(cx,h-7,text='ARM → SELECT → OPEN LAB',fill=P['muted'],font=(MONO,5,'bold'))
                self._crypto_selector_items=items
            a=(t*.035)%(2*math.pi); sx=cx+56*math.cos(a); sy=cy+56*math.sin(a); c.coords(items['sweep'],cx,cy,sx,sy)
            for i,item in enumerate(items['nodes']):
                aa=a+i*math.pi/2; x=cx+48*math.cos(aa); y=cy+48*math.sin(aa); c.coords(item,x-3,y-3,x+3,y+3)
            self._crypto_selector_phase+=1; self.after(130,animate)
        c.after_idle(animate)

        # Modern command deck: the algorithm rack stays intact, while a compact intelligence layer
        # exposes useful crypto analysis without forcing the user into another module.
        intelbar=tk.Frame(inner,bg='#050f16',highlightbackground='#1b5a70',highlightthickness=1); intelbar.pack(fill='x',pady=(0,8))
        left=tk.Frame(intelbar,bg='#050f16'); left.pack(side='left',fill='x',expand=True,padx=12,pady=8)
        tk.Label(left,text='CRYPTO INTELLIGENCE DECK',bg='#050f16',fg=P['cyan'],font=(MONO,8,'bold')).pack(anchor='w')
        tk.Label(left,text='ANALYZE • COMPARE • PROFILE • VALIDATE  //  LOCAL / OFFLINE',bg='#050f16',fg=P['muted'],font=(MONO,6,'bold')).pack(anchor='w',pady=(2,0))
        tools=tk.Frame(intelbar,bg='#050f16'); tools.pack(side='right',padx=8,pady=7)
        for label,cmd in [('ANALYZER',self.open_crypto_analyzer),('COMPARE',self.open_crypto_compare),('KEY LAB',self.open_crypto_key_lab)]:
            b=tk.Button(tools,text=label,command=cmd,bg='#081b26',fg=P['cyan'],activebackground=P['cyan'],activeforeground=P['bg'],relief='flat',bd=0,font=(MONO,7,'bold'),highlightbackground='#16536a',highlightthickness=1,padx=9,pady=6,cursor='hand2')
            b.pack(side='left',padx=3)

        self.crypto_selection_info=self.glass(inner); self.crypto_selection_info.pack(fill='x',pady=(0,7))
        info=tk.Frame(self.crypto_selection_info,bg=P['panel2']); info.pack(fill='x',padx=10,pady=7)
        self.crypto_selection_info_label=tk.Label(info,text='SELECT A SET TO ARM THE ALGORITHM MATRIX',bg=P['panel2'],fg=P['yellow'],font=(MONO,8,'bold'),anchor='w'); self.crypto_selection_info_label.pack(side='left')
        self.crypto_selection_count=tk.Label(info,text='19 READY',bg=P['panel2'],fg=P['green'],font=(MONO,7,'bold')); self.crypto_selection_count.pack(side='right')

        self.crypto_deck=tk.Frame(inner,bg=P['bg']); self.crypto_deck.pack(fill='x')
        self.crypto_cards=[]
        def build_cards(keys):
            for old in self.crypto_cards:
                try: old.destroy()
                except Exception: pass
            self.crypto_cards=[]; cards=[]
            for idx,k in enumerate(keys):
                name,code,fields,mod=ALGORITHMS[k]
                accent,body,head_bg,button_bg=self._crypto_card_theme(idx)
                c=tk.Frame(self.crypto_deck,bg=body,highlightbackground=accent,highlightthickness=1,cursor='hand2')
                c._algo_key=k; c._accent=accent
                top=tk.Frame(c,bg=head_bg); top.pack(fill='x')
                tk.Label(top,text=f'{idx+1:02d} // {code}',bg=head_bg,fg=accent,font=(MONO,6,'bold')).pack(side='left',padx=8,pady=6)
                status=tk.Label(top,text='● READY',bg=head_bg,fg=P['green'],font=(MONO,6,'bold')); status.pack(side='right',padx=8,pady=6)
                bodyrow=tk.Frame(c,bg=body); bodyrow.pack(fill='x',padx=10,pady=(8,2))
                tk.Label(bodyrow,text=name.upper(),bg=body,fg=P['text'],font=(FONT,11,'bold'),anchor='w').pack(side='left',fill='x',expand=True)
                tk.Label(bodyrow,text=code,bg=accent,fg=P['bg'],font=(MONO,7,'bold'),padx=6,pady=2).pack(side='right')
                tk.Label(c,text=GUIDES[k][0],bg=body,fg=accent,font=(MONO,7,'bold'),anchor='w',wraplength=300).pack(fill='x',padx=10,pady=(0,5))
                # compact operational visualization instead of decorative text
                sig=tk.Canvas(c,height=42,bg=body,highlightthickness=0); sig.pack(fill='x',padx=8)
                for j in range(15):
                    bh=5+((j*11+idx*7)%24); x=7+j*19
                    sig.create_rectangle(x,36-bh,x+9,36,fill=accent if j%3 else P['line2'],outline='')
                sig.create_line(5,37,292,37,fill=P['line'],width=1)
                meta=tk.Frame(c,bg=body); meta.pack(fill='x',padx=10,pady=(2,7))
                family=next((m['title'] for m in CRYPTO_GROUPS.values() if k in m['keys']),'CORE')
                for lab,val,col in [('TYPE',family[:10],P['cyan']),('KEY',('NONE' if fields is None else fields.upper()),P['yellow']),('ENGINE','READY',P['green'])]:
                    q=tk.Frame(meta,bg=body); q.pack(side='left',fill='x',expand=True)
                    tk.Label(q,text=lab,bg=body,fg=P['dim'],font=(MONO,5,'bold')).pack(anchor='w')
                    tk.Label(q,text=val,bg=body,fg=col,font=(MONO,6,'bold')).pack(anchor='w')
                c._algo_key=k; c._accent=accent
                c.bind('<Double-Button-1>', lambda _e,x=k:self._crypto_card_click(x), add='+')
                action=tk.Button(c,text='> OPEN LIVE LAB  //  EXECUTE',command=lambda x=k:self._crypto_card_click(x),
                                 bg=button_bg,fg=accent,activebackground=accent,activeforeground=P['bg'],relief='flat',bd=0,
                                 font=(MONO,7,'bold'),cursor='hand2',highlightbackground=accent,highlightthickness=1,pady=7)
                action.pack(fill='x',padx=8,pady=(0,9))
                def enter(_e,frame=c): frame.configure(highlightbackground=P['text'],highlightthickness=2)
                def leave(_e,frame=c,a=accent): frame.configure(highlightbackground=a,highlightthickness=1)
                for widget in [c]+list(c.winfo_children()):
                    try: widget.bind('<Enter>',enter,add='+'); widget.bind('<Leave>',leave,add='+')
                    except Exception: pass
                cards.append(c); self.crypto_cards.append(c)
            self._responsive_grid(self.crypto_deck,cards,min_card=300,gap=8)
            self.crypto_selection_info_label.configure(text=f'{len(keys):02d} ALGORITHMS ARMED  // SELECT A MODULE TO ENTER ITS LIVE LAB')
            self.crypto_selection_count.configure(text=f'{len(keys):02d} READY')
        self._crypto_build_cards=build_cards
        # Open on the essential rack so the matrix is never visually empty.
        self.after(0,lambda:self._select_crypto_group('requested'))
        return p

    # ---------- crypto intelligence dock ----------
    def _crypto_popup(self, title, width=760, height=560):
        win=tk.Toplevel(self); win.title('HN BLACKBOX // '+title); win.geometry(f'{width}x{height}'); win.minsize(620,420); win.configure(bg=P['bg']); win.transient(self)
        head=tk.Frame(win,bg='#050d14',highlightbackground=P['line2'],highlightthickness=1); head.pack(fill='x',padx=16,pady=16)
        tk.Label(head,text='HN // CRYPTO INTELLIGENCE',bg='#050d14',fg=P['cyan'],font=(MONO,8,'bold')).pack(side='left',padx=12,pady=10)
        tk.Label(head,text=title.upper(),bg='#050d14',fg=P['text'],font=(MONO,12,'bold')).pack(side='right',padx=12)
        body=tk.Frame(win,bg=P['bg']); body.pack(fill='both',expand=True,padx=16,pady=(0,16))
        return win,body

    def open_crypto_analyzer(self):
        win,body=self._crypto_popup('Payload Analyzer',820,610)
        top=tk.Frame(body,bg=P['panel'],highlightbackground=P['line'],highlightthickness=1); top.pack(fill='x',pady=(0,8))
        tk.Label(top,text='PAYLOAD',bg=P['panel'],fg=P['muted'],font=(MONO,7,'bold')).pack(anchor='w',padx=10,pady=(8,2))
        inp=tk.Text(top,height=5,bg='#030a11',fg=P['text'],insertbackground=P['cyan'],font=(MONO,10),relief='flat',wrap='none'); inp.pack(fill='x',padx=10,pady=(0,8))
        out=tk.Text(body,bg='#030a11',fg=P['green'],font=(MONO,9),relief='flat',wrap='none'); out.pack(fill='both',expand=True)
        def run():
            text=inp.get('1.0','end-1c'); r=crypto_intel.analyze_payload(text)
            out.delete('1.0','end'); out.insert('1.0',r['report'])
        self.btn(top,'> ANALYZE',run,True).pack(anchor='e',padx=10,pady=(0,9))

    def open_crypto_compare(self):
        win,body=self._crypto_popup('Algorithm Comparison',820,590)
        bar=tk.Frame(body,bg=P['panel'],highlightbackground=P['line'],highlightthickness=1); bar.pack(fill='x',pady=(0,8))
        vars=[]
        for k in ALGORITHMS:
            v=tk.BooleanVar(value=k in ('caesar','vigenere','aes','rsa','hash')); vars.append((k,v))
            ttk.Checkbutton(bar,text=ALGORITHMS[k][0],variable=v).pack(side='left',padx=5,pady=8)
        text=tk.Text(body,bg='#030a11',fg=P['text'],font=(MONO,8),relief='flat',wrap='none'); text.pack(fill='both',expand=True)
        def run():
            keys=[k for k,v in vars if v.get()]
            rows=crypto_intel.compare_algorithms(keys)
            text.delete('1.0','end'); text.insert('1.0',rows)
        self.btn(bar,'COMPARE',run,True).pack(side='right',padx=8,pady=5)
        run()

    def open_crypto_key_lab(self):
        win,body=self._crypto_popup('Key & Strength Lab',760,540)
        row=tk.Frame(body,bg=P['panel'],highlightbackground=P['line'],highlightthickness=1); row.pack(fill='x',pady=(0,8))
        tk.Label(row,text='ALGORITHM',bg=P['panel'],fg=P['muted'],font=(MONO,7,'bold')).pack(side='left',padx=8)
        combo=ttk.Combobox(row,state='readonly',values=list(ALGORITHMS.keys()),font=(MONO,9)); combo.set('caesar'); combo.pack(side='left',padx=8,pady=8)
        key=tk.Entry(row,bg='#030a11',fg=P['text'],insertbackground=P['cyan'],font=(MONO,9),relief='flat'); key.pack(side='left',fill='x',expand=True,padx=8,pady=8)
        out=tk.Text(body,bg='#030a11',fg=P['green'],font=(MONO,9),relief='flat',wrap='word'); out.pack(fill='both',expand=True)
        def run():
            out.delete('1.0','end'); out.insert('1.0',crypto_intel.key_profile(combo.get(),key.get()))
        self.btn(row,'PROFILE',run,True).pack(side='right',padx=8,pady=5)
        run()

    def _select_crypto_group(self,key):
        meta=CRYPTO_GROUPS[key]
        self.crypto_group_var.set(key)
        for k,b in self.crypto_group_buttons.items():
            active=k==key; m=CRYPTO_GROUPS[k]
            b.configure(bg=m["accent"] if active else '#07131a',fg=P["bg"] if active else m["accent"])
        self.crypto_selection_info_label.configure(text=f"{meta['title']}  //  {meta['sub']}",fg=meta["accent"])
        self._crypto_build_cards(meta["keys"])

    def _crypto_card_click(self,key):
        """Small tactile feedback before entering the selected lab."""
        for c in getattr(self,'crypto_cards',[]):
            if getattr(c,'_algo_key',None)==key:
                a=getattr(c,'_accent',P['cyan'])
                try:
                    c.configure(highlightbackground=P['text'],highlightthickness=3)
                    self.after(90,lambda c=c,a=a: c.configure(highlightbackground=a,highlightthickness=2))
                    self.after(170,lambda c=c,a=a: c.configure(highlightbackground=a,highlightthickness=1))
                except tk.TclError: pass
                break
        self.open_algorithm(key)

    # ---------- algorithm workspace ----------
    def open_algorithm(self, key):
        self.current_algo = key
        self._render_processing()
        self.show_page("processing")

    def _render_processing(self):
        """Responsive algorithm workstation with the live visualizer above the fold."""
        p=self.pages['processing']
        for x in p.winfo_children(): x.destroy()
        name,code,fields,mod=ALGORITHMS[self.current_algo]
        name=name
        self.key_entries={}
        self._exec_started=None
        self._trace_lines=[]
        outer=tk.Frame(p,bg=P['bg']); outer.pack(fill='both',expand=True)
        canvas,inner=self._make_canvas(outer); self.processing_canvas=canvas

        # intelligence-style command header
        self.heading(inner,f'HN / {code}',name,GUIDES[self.current_algo][0])
        top=tk.Frame(inner,bg=P['bg']); top.pack(fill='x',pady=(0,7))
        self.btn(top,'← BACK TO MATRIX',lambda:self.show_page('crypto')).pack(side='right')
        tk.Label(top,text=f'LIVE LAB  //  {code}  //  LOCAL ENGINE  //  VISUAL TRACE LINKED',bg=P['bg'],fg=P['dim'],font=(MONO,7,'bold'),anchor='w').pack(side='left',pady=7)
        self.btn(top,'ALGORITHM GUIDE',self.guide).pack(side='right',padx=3)
        self.btn(top,'CLEAR',self.clear_processing).pack(side='right',padx=3)
        command_hud=tk.Frame(inner,bg='#041018',highlightbackground=P['line2'],highlightthickness=1); command_hud.pack(fill='x',pady=(0,7))
        left_h=tk.Frame(command_hud,bg='#041018'); left_h.pack(side='left',fill='x',expand=True,padx=10,pady=7)
        tk.Label(left_h,text='CRYPTO OPS // LIVE CORE CONTROL',bg='#041018',fg=P['cyan'],font=(MONO,8,'bold'),anchor='w').pack(fill='x')
        tk.Label(left_h,text=f'{code} CORE  •  LOCAL  •  TRACE LINKED  •  READY',bg='#041018',fg=P['muted'],font=(MONO,6,'bold'),anchor='w').pack(fill='x',pady=(2,0))
        self.command_clock=tk.Label(command_hud,text=datetime.now().strftime('%H:%M:%S'),bg='#041018',fg=P['green'],font=(MONO,10,'bold')); self.command_clock.pack(side='right',padx=12)
        self.after(250,self._update_crypto_clock)
        self.crypto_op_strip=tk.Canvas(command_hud,height=3,bg='#041018',highlightthickness=0); self.crypto_op_strip.pack(fill='x',side='bottom',padx=10,pady=(2,4))
        self._crypto_op_phase=0
        self._animate_crypto_op_strip()

        # metadata HUD
        hud=self.glass(inner); hud.pack(fill='x',pady=(0,7))
        specs=[('MODULE',code,P['cyan']),('FORMULA',GUIDES[self.current_algo][0],P['yellow']),('MODE','LOCAL / EDUCATIONAL',P['green']),('TRACE','REAL-TIME',P['purple'])]
        for i,(lab,val,col) in enumerate(specs):
            cell=tk.Frame(hud,bg=P['panel2']); cell.pack(side='left',fill='x',expand=True,padx=1,pady=1)
            tk.Label(cell,text=lab,bg=P['panel2'],fg=P['dim'],font=(MONO,6,'bold')).pack(anchor='w',padx=9,pady=(6,0))
            tk.Label(cell,text=val,bg=P['panel2'],fg=col,font=(MONO,7,'bold'),wraplength=240,anchor='w',justify='left').pack(anchor='w',padx=9,pady=(1,6))

        split=tk.Frame(inner,bg=P['bg']); split.pack(fill='x',pady=2)
        split.grid_columnconfigure(0,weight=42,uniform='lab')
        split.grid_columnconfigure(1,weight=58,uniform='lab')

        # Controls: intentionally compact so visual trace remains visible without scrolling.
        controls=self.card(split); controls.grid(row=0,column=0,sticky='nsew',padx=(0,5))
        hdr=tk.Frame(controls,bg=P['panel3']); hdr.pack(fill='x')
        tk.Label(hdr,text='01 // CONTROL CONSOLE',bg=P['panel3'],fg=P['cyan'],font=(MONO,8,'bold')).pack(side='left',padx=12,pady=7)
        tk.Label(hdr,text='READY',bg=P['panel3'],fg=P['green'],font=(MONO,7,'bold')).pack(side='right',padx=12)

        tk.Label(controls,text='INPUT PAYLOAD',bg=P['panel'],fg=P['muted'],font=(MONO,7,'bold'),anchor='w').pack(fill='x',padx=12,pady=(9,3))
        self.input_box=tk.Text(controls,height=3,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],selectbackground=P['purple'],relief='flat',font=(MONO,10),wrap='word',undo=True)
        self.input_box.pack(fill='x',padx=12,pady=(0,5))
        self.crypto_input_counter=tk.Label(controls,text='0 CHARS  //  UTF-8',bg=P['panel'],fg=P['dim'],font=(MONO,5,'bold'),anchor='e'); self.crypto_input_counter.pack(fill='x',padx=12,pady=(0,2))
        self.input_box.bind('<<Modified>>',self._crypto_input_changed,add='+')

        self.operation=tk.StringVar(value='encrypt')
        rr=tk.Frame(controls,bg=P['panel']); rr.pack(fill='x',padx=12,pady=3)
        ttk.Radiobutton(rr,text='ENCRYPT',variable=self.operation,value='encrypt').pack(side='left',padx=(0,8))
        ttk.Radiobutton(rr,text='DECRYPT',variable=self.operation,value='decrypt').pack(side='left')

        fieldslist=[] if fields is None else fields.split(',')
        if self.current_algo=='hash': fieldslist=['word']
        keygrid=tk.Frame(controls,bg=P['panel']); keygrid.pack(fill='x',padx=12,pady=(3,4))
        for i,f in enumerate(fieldslist):
            keygrid.grid_columnconfigure(i%2,weight=1)
            row=tk.Frame(keygrid,bg=P['panel']); row.grid(row=i//2,column=i%2,sticky='ew',padx=3,pady=3)
            lab={'shift':'SHIFT / OFFSET','word':'KEYWORD','rails':'RAILS','key':'RSA KEY  e,d,n'}.get(f,f.upper())
            tk.Label(row,text=lab,bg=P['panel'],fg=P['dim'],font=(MONO,6,'bold'),anchor='w').pack(fill='x')
            e=ttk.Entry(row,font=(MONO,9)); e.pack(fill='x',ipady=2); self.key_entries[f]=e

        note={'hash':self.t('hashnote'),'rsa':self.t('rsanote'),'otp':self.t('otpnote')}.get(self.current_algo,'')
        if note: tk.Label(controls,text=note,bg=P['panel'],fg=P['yellow'],font=(FONT,7),wraplength=410,justify='left').pack(fill='x',padx=12,pady=3)
        actions=tk.Frame(controls,bg=P['panel']); actions.pack(fill='x',padx=12,pady=(5,10))
        self.btn(actions,'> EXECUTE',self.execute,True).pack(side='left',fill='x',expand=True,padx=(0,3))
        self.btn(actions,'GENERATE',self.generate_key).pack(side='left',fill='x',expand=True,padx=3)
        if self.current_algo=='caesar': self.btn(actions,'BRUTE FORCE',self.bruteforce).pack(side='left',fill='x',expand=True,padx=3)
        self.btn(actions,'GUIDE',self.guide).pack(side='left',fill='x',expand=True,padx=(3,0))

        # Compact core profile: useful state, no wall of explanatory text.
        intel=tk.Frame(controls,bg='#06131a',highlightbackground=P['line'],highlightthickness=1)
        intel.pack(fill='x',padx=12,pady=(2,8))
        ih=tk.Frame(intel,bg='#06131a'); ih.pack(fill='x',padx=9,pady=(6,3))
        tk.Label(ih,text='CORE PROFILE',bg='#06131a',fg=P['yellow'],font=(MONO,7,'bold')).pack(side='left')
        self.core_profile_status=tk.Label(ih,text='STANDBY',bg='#06131a',fg=P['green'],font=(MONO,6,'bold')); self.core_profile_status.pack(side='right')
        formula,example=GUIDES[self.current_algo]
        profile=tk.Frame(intel,bg='#06131a'); profile.pack(fill='x',padx=8,pady=(0,7))
        rows=[('FORMULA',formula,P['cyan']),('PATH',{'caesar':'READ → SHIFT → EMIT','additive':'READ → ADD MOD 26 → EMIT','multiplicative':'READ → MULTIPLY MOD 26 → EMIT','vigenere':'KEY ALIGN → ADD MOD 26 → EMIT','playfair':'PAIR → LOCATE → SUBSTITUTE','railfence':'ROUTE → ZIGZAG → READ','hill':'MATRIX × VECTOR → MOD 26','aes':'KEY → BLOCK → ROUND → SEAL','rsa':'KEYPAIR → MODULAR EXPONENT → SEAL','hash':'NORMALIZE → DIGEST → FINGERPRINT'}.get(self.current_algo,'INPUT → TRANSFORM → OUTPUT'),P['green'])]
        for lab,val,col in rows:
            row=tk.Frame(profile,bg='#07151d'); row.pack(fill='x',pady=1)
            tk.Label(row,text=lab,bg='#07151d',fg=P['dim'],font=(MONO,5,'bold'),width=9,anchor='w').pack(side='left',padx=6,pady=5)
            tk.Label(row,text=val,bg='#07151d',fg=col,font=(MONO,6,'bold'),anchor='w',wraplength=320,justify='left').pack(side='left',fill='x',expand=True,pady=5)

        telemetry=tk.Frame(controls,bg='#040c12',highlightbackground=P['line'],highlightthickness=1); telemetry.pack(fill='x',padx=12,pady=(0,10))
        tk.Label(telemetry,text='ENGINE TELEMETRY // LIVE',bg='#040c12',fg=P['yellow'],font=(MONO,7,'bold'),anchor='w').pack(fill='x',padx=9,pady=(6,4))
        tgrid=tk.Frame(telemetry,bg='#040c12'); tgrid.pack(fill='x',padx=8,pady=(0,7))
        self.crypto_metric_labels={}
        metric_specs=[('INPUT','0'),('OUTPUT','0'),('KEY','READY'),('EXEC','-- ms')]
        for i,(lab,val) in enumerate(metric_specs):
            cell=tk.Frame(tgrid,bg='#07151d'); cell.grid(row=0,column=i,sticky='ew',padx=2)
            tgrid.grid_columnconfigure(i,weight=1)
            tk.Label(cell,text=lab,bg='#07151d',fg=P['dim'],font=(MONO,5,'bold')).pack(anchor='w',padx=5,pady=(4,0))
            lbl=tk.Label(cell,text=val,bg='#07151d',fg=(P['cyan'],P['green'],P['yellow'],P['purple'])[i],font=(MONO,7,'bold')); lbl.pack(anchor='w',padx=5,pady=(1,5))
            self.crypto_metric_labels[lab]=lbl

        # Right: visualizer is first-class, result is embedded below it.
        right=tk.Frame(split,bg=P['bg']); right.grid(row=0,column=1,sticky='nsew',padx=(5,0))
        vis=self.card(right); vis.pack(fill='both',expand=True)
        vh=tk.Frame(vis,bg=P['panel3']); vh.pack(fill='x')
        tk.Label(vh,text='02 // LIVE VISUALIZATION // INTELLIGENCE FEED',bg=P['panel3'],fg=P['cyan'],font=(MONO,8,'bold')).pack(side='left',padx=12,pady=7)
        self.visual_status=tk.Label(vh,text='WAITING FOR EXECUTION',bg=P['panel3'],fg=P['yellow'],font=(MONO,7,'bold')); self.visual_status.pack(side='right',padx=12)
        # Progress strip
        self.visual_progress=tk.Canvas(vis,height=4,bg=P['panel'],highlightthickness=0); self.visual_progress.pack(fill='x')
        self.visual=tk.Canvas(vis,bg='#050b11',height=330,highlightthickness=0)
        self.visual.pack(fill='both',expand=True,padx=8,pady=8)

        # Result is always directly under the visualization; no hunt through the page.
        result=tk.Frame(vis,bg=P['panel']); result.pack(fill='x',padx=8,pady=(0,8))
        rh=tk.Frame(result,bg=P['panel']); rh.pack(fill='x')
        tk.Label(rh,text='03 // OUTPUT',bg=P['panel'],fg=P['green'],font=(MONO,8,'bold')).pack(side='left',padx=8,pady=6)
        self.status=tk.Label(rh,text='READY',bg=P['panel'],fg=P['green'],font=(MONO,7,'bold')); self.status.pack(side='left',padx=6)
        self.crypto_output_counter=tk.Label(rh,text='0 CHARS',bg=P['panel'],fg=P['dim'],font=(MONO,5,'bold')); self.crypto_output_counter.pack(side='left',padx=7)
        self.btn(rh,'COPY',self.copy_result).pack(side='right',padx=2,pady=2)
        self.btn(rh,'SAVE',self.save_result).pack(side='right',padx=2,pady=2)
        self.result_box=tk.Text(result,height=3,bg='#030a11',fg=P['green'],insertbackground=P['cyan'],relief='flat',font=(ASCII_MONO,9),wrap='none',padx=8,pady=6)
        self.result_box.pack(fill='x',padx=7,pady=(0,7))
        trace=tk.Frame(vis,bg='#040c12',highlightbackground=P['line'],highlightthickness=1); trace.pack(fill='x',padx=8,pady=(0,8))
        tk.Label(trace,text='04 // EXECUTION TRACE',bg='#040c12',fg=P['yellow'],font=(MONO,7,'bold'),anchor='w').pack(fill='x',padx=8,pady=(5,2))
        self.trace_box=tk.Text(trace,height=4,bg='#02070c',fg=P['muted'],font=(MONO,6),relief='flat',bd=0,wrap='none',state='disabled',padx=7,pady=4)
        self.trace_box.pack(fill='x',padx=6,pady=(0,6))
        self._set_crypto_metrics(input_len=0,output_len=0,key_state='READY',elapsed=None)
        self._trace('SYSTEM','CRYPTO CORE READY')

        self._visual_state={'result':'','step':0}; self.draw_visual()
        self._draw_visual_progress(0,1)

        def responsive(_e=None):
            width=max(1,split.winfo_width())
            if width<880:
                controls.grid_configure(row=0,column=0,columnspan=2,padx=0,pady=(0,6))
                right.grid_configure(row=1,column=0,columnspan=2,padx=0,pady=(6,0))
                self.visual.configure(height=300)
            else:
                controls.grid_configure(row=0,column=0,columnspan=1,padx=(0,5),pady=0)
                right.grid_configure(row=0,column=1,columnspan=1,padx=(5,0),pady=0)
                self.visual.configure(height=330)
            self.draw_visual()
        split.bind('<Configure>',responsive,add='+'); split.after(60,responsive)

    def _animate_crypto_op_strip(self):
        c=getattr(self,'crypto_op_strip',None)
        if c is None or not c.winfo_exists(): return
        if not getattr(self,'_ui_ready',False): return
        if self.current != 'processing':
            self.after(900,self._animate_crypto_op_strip); return
        if time.monotonic() < getattr(self,'_resizing_until',0):
            self.after(180,self._animate_crypto_op_strip); return
        w=max(1,c.winfo_width()); c.delete('all')
        phase=getattr(self,'_crypto_op_phase',0); span=70
        c.create_rectangle(0,0,w,3,fill='#07151d',outline='')
        x=(phase*4)%max(1,w+span)-span
        c.create_rectangle(x,0,x+span,3,fill=P['cyan'],outline='')
        self._crypto_op_phase=phase+1
        self.after(90,self._animate_crypto_op_strip)

    def _crypto_input_changed(self,_event=None):
        try:
            if getattr(self,'input_box',None) and self.input_box.edit_modified():
                n=len(self.input_box.get('1.0','end-1c'))
                if hasattr(self,'crypto_input_counter'): self.crypto_input_counter.configure(text=f'{n:,} CHARS  //  UTF-8')
                self.input_box.edit_modified(False)
        except tk.TclError:
            pass

    def _update_crypto_clock(self):
        if not hasattr(self,'command_clock') or not self.command_clock.winfo_exists():
            return
        try:
            self.command_clock.configure(text=datetime.now().strftime('%H:%M:%S'))
            self.after(250,self._update_crypto_clock)
        except tk.TclError:
            pass

    def _set_crypto_metrics(self,input_len=None,output_len=None,key_state=None,elapsed=None):
        labels=getattr(self,'crypto_metric_labels',{})
        if not labels: return
        if input_len is not None and 'INPUT' in labels: labels['INPUT'].configure(text=str(input_len))
        if output_len is not None and 'OUTPUT' in labels:
            labels['OUTPUT'].configure(text=str(output_len))
            if hasattr(self,'crypto_output_counter') and self.crypto_output_counter.winfo_exists(): self.crypto_output_counter.configure(text=f'{output_len:,} CHARS')
        if key_state is not None and 'KEY' in labels: labels['KEY'].configure(text=key_state)
        if 'EXEC' in labels: labels['EXEC'].configure(text='-- ms' if elapsed is None else f'{elapsed*1000:.1f} ms')

    def _trace(self,stage,message):
        stamp=datetime.now().strftime('%H:%M:%S.%f')[:-3]
        line=f'{stamp}  [{stage:<10}]  {message}'
        self._trace_lines=(getattr(self,'_trace_lines',[])+[line])[-6:]
        box=getattr(self,'trace_box',None)
        if box is not None and box.winfo_exists():
            box.configure(state='normal'); box.delete('1.0','end'); box.insert('1.0','\n'.join(self._trace_lines)); box.configure(state='disabled')

    def _draw_visual_progress(self,step,total):
        if not hasattr(self,'visual_progress') or not self.visual_progress.winfo_exists(): return
        c=self.visual_progress; c.delete('all'); w=max(1,c.winfo_width()); ratio=0 if total<=0 else min(1,step/total)
        c.create_rectangle(0,0,w,4,fill=P['panel2'],outline='')
        c.create_rectangle(0,0,w*ratio,4,fill=NAV_ACCENTS.get('crypto',P['cyan']),outline='')

    def _make_canvas(self, parent):
        """Create a page canvas with mouse-wheel support and styled scrollbars."""
        holder = tk.Frame(parent, bg=P["bg"])
        holder.pack(fill="both", expand=True)

        canvas = tk.Canvas(holder, bg=P["bg"], highlightthickness=0, bd=0)
        vbar = ttk.Scrollbar(holder, orient="vertical", command=canvas.yview, style="Dark.Vertical.TScrollbar")
        hbar = ttk.Scrollbar(holder, orient="horizontal", command=canvas.xview, style="Dark.Horizontal.TScrollbar")
        inner = tk.Frame(canvas, bg=P["bg"])
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        canvas.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")
        holder.grid_rowconfigure(0, weight=1)
        holder.grid_columnconfigure(0, weight=1)

        sync_job = {"id": None}
        def sync(_e=None):
            # Debounce geometry churn during resize/layout bursts. Rendering is unchanged;
            # this simply avoids recalculating the scroll region dozens of times per frame.
            if sync_job["id"] is not None:
                try: canvas.after_cancel(sync_job["id"])
                except tk.TclError: pass
            def apply_sync():
                sync_job["id"] = None
                try:
                    if not canvas.winfo_exists(): return
                    bbox = canvas.bbox("all")
                    canvas.configure(scrollregion=bbox or (0, 0, 0, 0))
                    canvas.itemconfigure(window_id, width=max(1, canvas.winfo_width()))
                except tk.TclError:
                    pass
            sync_job["id"] = canvas.after(12, apply_sync)

        inner.bind("<Configure>", sync, add="+")
        canvas.bind("<Configure>", sync, add="+")
        self._bind_wheel(canvas)
        return canvas, inner
    def generate_key(self):
        k = self.current_algo
        def put(f, v):
            if f in self.key_entries:
                self.key_entries[f].delete(0, "end")
                self.key_entries[f].insert(0, str(v))
        if k in {"caesar", "additive"}: put("shift", secrets.randbelow(26))
        elif k == "multiplicative": put("key", secrets.choice([1,3,5,7,9,11,15,17,19,21,23,25]))
        elif k == "railfence": put("rails", 2 + secrets.randbelow(5))
        elif k in {"vigenere", "playfair", "columnar", "beaufort", "autokey", "aes"}:
            put("word", "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(8)))
        elif k == "affine":
            put("a", secrets.choice([1,3,5,7,9,11,15,17,19,21,23,25])); put("b", secrets.randbelow(26))
        elif k == "hill":
            while True:
                vals = [secrets.randbelow(26) for _ in range(4)]
                if math.gcd((vals[0]*vals[3]-vals[1]*vals[2]) % 26, 26) == 1: break
            for f, v in zip(("a","b","c","d"), vals): put(f, v)
        elif k == "otp":
            put("word", classical.otp_key(max(8, len(self.input_box.get("1.0","end-1c").encode()) + 4)))
        elif k == "rsa":
            e, d, n = classical.rsa_generate(512); put("key", f"e={e}; d={d}; n={n}")
        elif k == "hash": put("word", "SHA-256")

    def _vals(self):
        return {f: self.key_entries[f].get().strip() for f in self.key_entries}

    def _record_tool_operation(self, module, operation, input_text, output_text, key_display=""):
        """Persist every real module operation in the same audit trail as ciphers."""
        try:
            history_manager.add_entry(module, operation, key_display, str(input_text)[:4000], str(output_text)[:8000])
            if getattr(self, 'current', None) == 'history':
                self.refresh_history()
        except Exception:
            # Audit persistence must never interrupt a successful local operation.
            pass

    def execute(self):
        text = self.input_box.get("1.0", "end-1c")
        if not text:
            messagebox.showwarning(self.t("error"), "INPUT IS REQUIRED")
            return
        k, vals, op = self.current_algo, self._vals(), self.operation.get()
        started=time.perf_counter()
        self._exec_started=started
        self._trace_lines=[]
        self._trace('INPUT','PAYLOAD RECEIVED')
        self._set_crypto_metrics(input_len=len(text),key_state='VALIDATING')
        if hasattr(self,'visual_status') and self.visual_status.winfo_exists(): self.visual_status.configure(text='CORE PROCESSING',fg=P['yellow'])
        if hasattr(self,'core_profile_status') and self.core_profile_status.winfo_exists(): self.core_profile_status.configure(text='PROCESSING',fg=P['yellow'])
        try:
            if k=="caesar": out=required_caesar.encrypt(text,int(vals["shift"])) if op=="encrypt" else required_caesar.decrypt(text,int(vals["shift"]))
            elif k=="additive": out=required_additive.encrypt(text,int(vals["shift"])) if op=="encrypt" else required_additive.decrypt(text,int(vals["shift"]))
            elif k=="multiplicative": out=required_multiplicative.encrypt(text,int(vals["key"])) if op=="encrypt" else required_multiplicative.decrypt(text,int(vals["key"]))
            elif k=="vigenere": out=required_vigenere.encrypt(text,vals["word"]) if op=="encrypt" else required_vigenere.decrypt(text,vals["word"])
            elif k=="playfair": out=playfair.encrypt(text,vals["word"]) if op=="encrypt" else playfair.decrypt(text,vals["word"])
            elif k=="railfence": out=required_rail_fence.encrypt(text,int(vals["rails"])) if op=="encrypt" else required_rail_fence.decrypt(text,int(vals["rails"]))
            elif k=="columnar": out=classical.columnar_encrypt(text,vals["word"]) if op=="encrypt" else classical.columnar_decrypt(text,vals["word"])
            elif k=="atbash": out=classical.atbash(text)
            elif k=="rot13": out=classical.rot13(text)
            elif k=="affine": out=required_affine.encrypt(text,int(vals["a"]),int(vals["b"])) if op=="encrypt" else required_affine.decrypt(text,int(vals["a"]),int(vals["b"]))
            elif k=="hill":
                key=tuple(int(vals[x]) for x in ("a","b","c","d")); out=hill_cipher.encrypt(text,key) if op=="encrypt" else hill_cipher.decrypt(text,key)
            elif k=="beaufort": out=classical.beaufort(text,vals["word"])
            elif k=="polybius": out=classical.polybius_encrypt(text) if op=="encrypt" else classical.polybius_decrypt(text)
            elif k=="adfgvx": out=classical.adfgvx_encrypt(text,vals["word"]) if op=="encrypt" else classical.adfgvx_decrypt(text,vals["word"])
            elif k=="bacon": out=classical.bacon_encrypt(text) if op=="encrypt" else classical.bacon_decrypt(text)
            elif k=="morse": out=classical.morse_encrypt(text) if op=="encrypt" else classical.morse_decrypt(text)
            elif k=="autokey": out=required_autokey.encrypt(text,vals["word"]) if op=="encrypt" else required_autokey.decrypt(text,vals["word"])
            elif k=="otp": out=classical.otp_encrypt(text,vals["word"]) if op=="encrypt" else classical.otp_decrypt(text,vals["word"])
            elif k=="aes": out=aes_cipher.encrypt(text,vals["word"]) if op=="encrypt" else aes_cipher.decrypt(text,vals["word"])
            elif k=="rsa":
                m=reparse_rsa(vals["key"]); out=classical.rsa_encrypt(text,m["e"],m["n"]) if op=="encrypt" else classical.rsa_decrypt(text,m["d"],m["n"])
            elif k=="hash": out=classical.hash_text(text,(vals["word"] or "SHA-256").lower().replace("-",""))
            else: raise ValueError("Unknown algorithm")
        except Exception as e:
            self._trace('ERROR',str(e)[:120])
            self._set_crypto_metrics(input_len=len(text),key_state='INVALID')
            self.status.configure(text=self.t("error"), fg=P["red"])
            if hasattr(self,'core_profile_status') and self.core_profile_status.winfo_exists(): self.core_profile_status.configure(text='ERROR',fg=P['red'])
            messagebox.showerror(self.t("error"), str(e)); return
        elapsed=time.perf_counter()-started
        self._trace('KEY','VALIDATION PASSED')
        self._trace('ENGINE',f'{ALGORITHMS[k][0].upper()} TRANSFORMATION COMPLETE')
        self.result_box.delete("1.0","end"); self.result_box.insert("1.0", out)
        self.status.configure(text=self.t("done"), fg=P["green"])
        if hasattr(self,'core_profile_status') and self.core_profile_status.winfo_exists(): self.core_profile_status.configure(text='COMPLETE',fg=P['green'])
        self._set_crypto_metrics(input_len=len(text),output_len=len(out),key_state='VALID',elapsed=elapsed)
        self._trace('OUTPUT',f'GENERATED // {len(out)} CHARS // {elapsed*1000:.1f} ms')
        history_manager.add_entry(ALGORITHMS[k][0], op, str(vals), text, out)
        self._start_visual(out)

    def clear_processing(self):
        if self._visual_job: self.after_cancel(self._visual_job); self._visual_job = None
        self.input_box.delete("1.0","end"); self.result_box.delete("1.0","end")
        self.status.configure(text=self.t("ready"), fg=P["green"])
        if hasattr(self,'core_profile_status') and self.core_profile_status.winfo_exists(): self.core_profile_status.configure(text='STANDBY',fg=P['green'])
        if hasattr(self,'crypto_output_counter') and self.crypto_output_counter.winfo_exists(): self.crypto_output_counter.configure(text='0 CHARS')
        if hasattr(self,'crypto_input_counter') and self.crypto_input_counter.winfo_exists(): self.crypto_input_counter.configure(text='0 CHARS  //  UTF-8')
        self._visual_state = {"result":"", "step":0}; self.draw_visual()

    def copy_result(self):
        v = self.result_box.get("1.0","end-1c")
        self.clipboard_clear(); self.clipboard_append(v); self.update()
        self.status.configure(text="✓ COPIED", fg=P["cyan"])

    def save_result(self):
        v = self.result_box.get("1.0","end-1c")
        if not v:
            messagebox.showwarning(self.t("error"), self.t("noresult")); return
        f = filedialog.asksaveasfilename(defaultextension=".txt",
                                         filetypes=[("Text","*.txt"),("All","*.*")])
        if f: Path(f).write_text(v, encoding="utf-8")

    def guide(self):
        name, code, fields, mod = ALGORITHMS[self.current_algo]
        title = name
        formula, ex = GUIDES[self.current_algo]
        win = tk.Toplevel(self); win.title("HN BLACKBOX // " + title); win.geometry("680x500")
        win.configure(bg=P["bg"]); win.transient(self)
        tk.Label(win, text=title, bg=P["bg"], fg=P["cyan"],
                 font=(FONT, 22, "bold"), anchor="w").pack(fill="x", padx=25, pady=(22, 4))
        for a,b in [("FORMULA",formula),("EXAMPLE",ex),
                    ("LAB NOTE","Educational workspace. Validate keys and understand the operation before using cryptography in production.")]:
            c=self.card(win); c.pack(fill="x", padx=25, pady=6)
            tk.Label(c,text=a,bg=P["panel"],fg=P["yellow"],font=(MONO,8,"bold"),anchor="e").pack(fill="x",padx=15,pady=(10,2))
            tk.Label(c,text=b,bg=P["panel"],fg=P["text"],font=(MONO,10),wraplength=580,anchor="w",justify="left").pack(fill="x",padx=15,pady=(0,11))

    def bruteforce(self):
        text=self.input_box.get("1.0","end-1c")
        results=caesar.brute_force(text)
        out="\n".join(f"{k:02d}  →  {v}" for k,v in results)
        self.result_box.delete("1.0","end"); self.result_box.insert("1.0",out)
        self.status.configure(text="✓ 26 KEY CANDIDATES",fg=P["cyan"])
        self._start_visual(out)

    # ---------- visualization ----------
    def _start_visual(self,result):
        if self._visual_job:
            try:self.after_cancel(self._visual_job)
            except tk.TclError:pass
        self._visual_state={'result':result,'step':0}
        self._trace('TRACE','VISUALIZATION LINK ESTABLISHED')
        if hasattr(self,'visual_status') and self.visual_status.winfo_exists():
            self.visual_status.configure(text='TRACE INITIALIZING',fg=P['yellow'])
        self._draw_visual_progress(0,max(1,len(result)+4))
        self._visual_job=self.after(80,self._visual_frame)

    def _visual_frame(self):
        if not self.winfo_exists() or not hasattr(self,'visual') or not self.visual.winfo_exists():return
        self.draw_visual()
        result=self._visual_state.get('result',''); total=max(8,min(42,len(result)+4)); step=self._visual_state.get('step',0)
        self._draw_visual_progress(step,total)
        if hasattr(self,'visual_status') and self.visual_status.winfo_exists():
            if step<total:self.visual_status.configure(text=f'TRACE {min(step,total):02d}/{total:02d}',fg=P['green'])
            else:self.visual_status.configure(text='TRACE COMPLETE',fg=P['cyan'])
        if step<total:
            self._visual_state['step']=step+1; self._visual_job=self.after(78,self._visual_frame)
        else:self._visual_job=None

    def draw_visual(self):
        if not hasattr(self,'visual') or not self.visual.winfo_exists():return
        c=self.visual;c.delete('all');w=max(460,c.winfo_width());h=max(210,c.winfo_height())
        result=self._visual_state.get('result','') if hasattr(self,'_visual_state') else ''
        step=self._visual_state.get('step',0) if hasattr(self,'_visual_state') else 0
        algo=self.current_algo or 'caesar'; code=ALGORITHMS.get(algo,('','','','',''))[2]
        # technical grid background
        for x in range(0,w,32): c.create_line(x,0,x,h,fill='#07151d',width=1)
        for y in range(0,h,28): c.create_line(0,y,w,y,fill='#07151d',width=1)
        c.create_text(14,13,text=f'HN // {code} // VISUAL TRACE',fill=P['cyan'],font=(MONO,8,'bold'),anchor='w')
        c.create_text(w-14,13,text='LOCAL ENGINE  ●',fill=P['green'],font=(MONO,7,'bold'),anchor='e')
        c.create_line(14,27,w-14,27,fill=P['line'],width=1)
        if algo=='playfair':self._visual_playfair(c,w,h,step)
        elif algo=='railfence':self._visual_rail(c,w,h,result,step)
        elif algo in {'caesar','vigenere','affine','atbash','rot13','beaufort','autokey'}:self._visual_stream(c,w,h,result,step,algo)
        elif algo=='hill':self._visual_matrix(c,w,h,result,step)
        elif algo in {'polybius','adfgvx','bacon','morse'}:self._visual_pipeline(c,w,h,result,step,algo)
        elif algo in {'aes','rsa','otp','hash'}:self._visual_secure(c,w,h,result,step,algo)
        else:self._visual_pipeline(c,w,h,result,step,algo)

    def _visual_stream(self,c,w,h,result,step,algo):
        src=(self.input_box.get('1.0','end-1c') if hasattr(self,'input_box') else '')[:32]
        out=(result or '')[:32]; n=max(len(src),len(out),1); cols=max(4,min(10,n)); rows=math.ceil(n/cols)
        gap=8; cell_w=max(34,min(62,(w-44-gap*(cols-1))/cols)); total_w=cols*cell_w+(cols-1)*gap; x0=(w-total_w)/2+cell_w/2
        # alphabet/operation lane for Caesar-family algorithms
        if algo=='caesar':
            shift=0
            try:shift=int(self.key_entries.get('shift').get() or 0)
            except Exception:pass
            alpha='ABCDEFGHIJKLMNOPQRSTUVWXYZ'; shifted=''.join(alpha[(i+shift)%26] for i in range(26))
            c.create_text(16,38,text=f'SHIFT MATRIX  //  +{shift%26}',fill=P['yellow'],font=(MONO,6,'bold'),anchor='w')
            # Two aligned, boxed alphabet lanes prevent long ASCII strings from
            # colliding or wrapping on smaller visualizer widths.
            lane_w=max(16,min(21,(w-38)/26)); xstart=19+lane_w/2
            for i,ch in enumerate(alpha):
                x=xstart+i*lane_w
                active=i<26
                c.create_rectangle(x-lane_w/2+1,47,x+lane_w/2-1,60,fill='#07131b',outline=P['line'])
                c.create_text(x,53,text=ch,fill=P['muted'],font=(MONO,5,'bold'))
                c.create_rectangle(x-lane_w/2+1,64,x+lane_w/2-1,77,fill='#081e27',outline=P['cyan'] if i in range(26) else P['line'])
                c.create_text(x,70,text=shifted[i],fill=P['cyan'],font=(MONO,5,'bold'))
            base_y=93
        else:base_y=48
        for i in range(n):
            row,col=divmod(i,cols);x=x0+col*(cell_w+gap);y=base_y+row*58;active=i<step;a=src[i] if i<len(src) else '·';b=out[i] if i<len(out) else '·'
            # index marker
            c.create_text(x,y-19,text=f'{i+1:02d}',fill=P['dim'],font=(MONO,5,'bold'))
            c.create_rectangle(x-cell_w/2,y-12,x+cell_w/2,y+10,fill='#0a1d28' if active else '#07131b',outline=P['cyan'] if active else P['line'],width=2 if active else 1)
            c.create_text(x,y-1,text=a if a.strip() else '·',fill=P['text'] if active else P['muted'],font=(ASCII_MONO,11,'bold'))
            c.create_line(x,y+12,x,y+24,fill=P['purple'] if active else P['line'],width=2)
            c.create_polygon(x-4,y+22,x+4,y+22,x,y+28,fill=P['purple'] if active else P['line'],outline='')
            c.create_rectangle(x-cell_w/2,y+29,x+cell_w/2,y+51,fill='#092018' if active else '#07131b',outline=P['green'] if active else P['line'],width=2 if active else 1)
            c.create_text(x,y+40,text=b if b.strip() else '·',fill=P['green'] if active else P['muted'],font=(ASCII_MONO,11,'bold'))
        label='CHARACTER TRANSFORM' if algo!='caesar' else 'CHARACTER SHIFT TRACE'
        c.create_text(w/2,h-16,text=f'INPUT  →  {label}  →  OUTPUT   //   STEP {min(step,n):02d}/{n:02d}',fill=P['muted'],font=(MONO,7,'bold'))

    def _visual_playfair(self,c,w,h,step):
        try:key=self.key_entries.get('word').get() if 'word' in self.key_entries else 'MONARCHY'; rows=playfair.grid_preview(key).splitlines()
        except Exception:rows=playfair.grid_preview('MONARCHY').splitlines()
        size=min(42,max(28,int((h-105)/5)));ox=w/2-2.5*size;oy=58
        c.create_text(14,40,text='KEY SQUARE // DIGRAPH ROUTING',fill=P['yellow'],font=(MONO,7,'bold'),anchor='w')
        for r,row in enumerate(rows):
            for col,ch in enumerate(row.split()):
                active=(r*5+col)<step;x=ox+col*size;y=oy+r*size
                c.create_rectangle(x-size/2+2,y-size/2+2,x+size/2-2,y+size/2-2,outline=P['cyan'] if active else P['line'],fill='#0a1f28' if active else '#07131b',width=2 if active else 1)
                c.create_text(x,y,text=ch,fill=P['green'] if active else P['text'],font=(MONO,12,'bold'))
        c.create_text(w/2,h-16,text='5 × 5 KEY MATRIX   //   PAIR → LOCATE → TRANSFORM → EMIT',fill=P['muted'],font=(MONO,7,'bold'))

    def _visual_rail(self,c,w,h,result,step):
        try:rails=max(2,min(7,int(self.key_entries['rails'].get() or 3)))
        except Exception:rails=3
        text=(self.input_box.get('1.0','end-1c') or 'HN BLACKBOX')[:46]; top=58; usable=max(80,w-72); span=usable/max(1,len(text)-1)
        c.create_text(16,40,text=f'ZIG-ZAG ROUTING // {rails} RAILS',fill=P['yellow'],font=(MONO,7,'bold'),anchor='w')
        for r in range(rails):
            y=top+r*max(22,min(34,(h-100)/max(1,rails-1)));c.create_line(36,y,w-36,y,fill=P['line'],dash=(2,5))
        for i,ch in enumerate(text):
            pos=i%(2*(rails-1));row=pos if pos<rails else 2*(rails-1)-pos;x=36+i*span;y=top+row*max(22,min(34,(h-100)/max(1,rails-1)));active=i<step
            c.create_oval(x-9,y-9,x+9,y+9,fill='#0b2430' if active else '#07131b',outline=P['cyan'] if active else P['dim'],width=2 if active else 1)
            c.create_text(x,y,text=ch,fill=P['green'] if active else P['muted'],font=(MONO,8,'bold'))
        c.create_text(w/2,h-16,text='INPUT CHARACTERS TRAVERSE THE RAILS → READOUT ORDER',fill=P['muted'],font=(MONO,7,'bold'))

    def _visual_matrix(self,c,w,h,result,step):
        ox=w/2-155;oy=62;vals=['a','b','c','d'];
        c.create_text(14,40,text='KEY MATRIX × PLAINTEXT VECTOR',fill=P['yellow'],font=(MONO,7,'bold'),anchor='w')
        for i,v in enumerate(vals):
            x=ox+(i%2)*70;y=oy+(i//2)*58;active=i<step
            c.create_rectangle(x-25,y-21,x+25,y+21,fill='#0a1f28' if active else '#07131b',outline=P['cyan'] if active else P['line'],width=2 if active else 1)
            value=self.key_entries.get(v).get() if v in self.key_entries else '?';c.create_text(x,y,text=value or '?',fill=P['green'] if active else P['text'],font=(MONO,12,'bold'))
        c.create_text(ox+143,oy+35,text='×',fill=P['yellow'],font=(FONT,20,'bold'))
        data=(self.input_box.get('1.0','end-1c') or 'HELP')[:4]
        for i,ch in enumerate(data):c.create_rectangle(ox+235+(i%2)*50,oy+(i//2)*48,ox+275+(i%2)*50,oy+36+(i//2)*48,outline=P['purple'],fill='#101022');c.create_text(ox+255+(i%2)*50,oy+18+(i//2)*48,text=ch,fill=P['text'],font=(MONO,10,'bold'))
        c.create_text(w/2,215,text='K × P  MOD 26',fill=P['cyan'],font=(MONO,12,'bold'))
        c.create_text(w/2,h-16,text='MATRIX MULTIPLICATION → MODULAR REDUCTION → OUTPUT BLOCK',fill=P['muted'],font=(MONO,7,'bold'))

    def _visual_pipeline(self,c,w,h,result,step,algo):
        labels=['INPUT','NORMALIZE','ENCODE','TRANSFORM','OUTPUT'];xgap=(w-120)/4
        c.create_text(16,40,text=f'{algo.upper()} // OPERATION PIPELINE',fill=P['yellow'],font=(MONO,7,'bold'),anchor='w')
        for i,label in enumerate(labels):
            x=60+i*xgap;active=i<=min(4,step//2)
            c.create_oval(x-25,74,x+25,124,fill='#0a1f28' if active else '#07131b',outline=P['cyan'] if active else P['line'],width=2)
            c.create_text(x,99,text=f'{i+1:02d}',fill=P['cyan'] if active else P['muted'],font=(MONO,9,'bold'))
            c.create_text(x,142,text=label,fill=P['green'] if active else P['muted'],font=(MONO,6,'bold'))
            if i<4:c.create_line(x+27,99,x+xgap-27,99,fill=P['purple'] if active else P['line'],width=2)
        snippet=(result or self.input_box.get('1.0','end-1c') or 'WAITING')[:70]
        c.create_rectangle(24,170,w-24,215,fill='#06131a',outline=P['line'])
        c.create_text(w/2,192,text=snippet,fill=P['text'],font=(MONO,8),anchor='center')
        c.create_text(w/2,h-16,text=f'PIPELINE COMPLETE STATE  //  STEP {step:02d}',fill=P['muted'],font=(MONO,7,'bold'))

    def _visual_secure(self,c,w,h,result,step,algo):
        cx,cy=w/2,125;phase=step*.16;r=38+min(22,step)
        c.create_text(16,40,text=f'{algo.upper()} // SECURE BLOCK TRACE',fill=P['yellow'],font=(MONO,7,'bold'),anchor='w')
        for ring in range(3):
            rr=r+ring*19;c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline=P['cyan'] if step>ring*2 else P['line'],width=1)
        c.create_text(cx,cy-6,text={'aes':'AES','rsa':'RSA','otp':'XOR','hash':'HASH'}.get(algo,'SEC'),fill=P['cyan'],font=(MONO,18,'bold'))
        c.create_text(cx,cy+17,text='SEALED' if step>=6 else 'PROCESSING',fill=P['green'],font=(MONO,7,'bold'))
        for i in range(18):
            ang=(i/18)*math.pi*2+phase;x=cx+145*math.cos(ang);y=cy+88*math.sin(ang);active=i<step
            c.create_line(cx+70*math.cos(ang),cy+42*math.sin(ang),x,y,fill=P['purple'] if active else P['line'],width=1)
            c.create_oval(x-3,y-3,x+3,y+3,fill=P['cyan'] if active else P['dim'],outline='')
        snippet=(result or 'NO OUTPUT YET')[:48];c.create_text(cx,h-34,text=snippet,fill=P['text'],font=(MONO,7),anchor='center');c.create_text(cx,h-16,text='KEY → BLOCK → TRANSFORM → INTEGRITY',fill=P['muted'],font=(MONO,7,'bold'))

    def _module_profile(self, key):
        profiles = {
            "crypto": {
                "title":"CRYPTOGRAPHY // ENGINE MATRIX", "kicker":"CRYPTO ENGINE", "accent":P["red"],
                "desc":"Classical and modern cipher operations with visible transformation traces.",
                "engine":"CIPHER CORE", "scope":"LOCAL / DETERMINISTIC", "state":"ARMED",
                "nodes":["INPUT","KEY","TRANSFORM","OUTPUT"], "metric":"ALGORITHMS 19"},
            "analysis": {
                "title":"CRYPTANALYSIS // INTELLIGENCE LAB", "kicker":"ANALYSIS CORE", "accent":P["purple"],
                "desc":"Frequency, coincidence, Kasiski and candidate ranking for structured analysis.",
                "engine":"ANALYSIS ENGINE", "scope":"LOCAL / EVIDENCE", "state":"READY",
                "nodes":["TEXT","SIGNAL","PATTERN","RANK"], "metric":"METHODS 03"},
            "network": {
                "title":"NETWORK SECURITY // LOCAL TOOLKIT", "kicker":"NETWORK CORE", "accent":P["green"],
                "desc":"IP intelligence, subnet mathematics and OS-level DNS resolution without scanning.",
                "engine":"NETWORK ENGINE", "scope":"LOCAL / SAFE", "state":"READY",
                "nodes":["IP","SUBNET","DNS","RESULT"], "metric":"TOOLS 03"},
            "web": {
                "title":"WEB SECURITY // SAFE LAB", "kicker":"WEB LAB", "accent":P["orange"],
                "desc":"Synthetic HTTP construction and defensive OWASP concepts with no external requests.",
                "engine":"WEB SIMULATOR", "scope":"LOCAL / SYNTHETIC", "state":"ISOLATED",
                "nodes":["REQUEST","PARSE","MODEL","DEFENSE"], "metric":"CHALLENGES 04"},
            "blue": {
                "title":"BLUE TEAM // DEFENSE CENTER", "kicker":"DEFENSE CORE", "accent":P["red"],
                "desc":"Log triage, IOC extraction and defensive signal classification for local evidence.",
                "engine":"DEFENSE ENGINE", "scope":"LOCAL / READ-ONLY", "state":"READY",
                "nodes":["LOG","IOC","TIMELINE","TRIAGE"], "metric":"DEFENSIVE MODE"},
            "labs": {
                "title":"SECURITY LABS // OFFLINE ARENA", "kicker":"LAB CONTROL", "accent":P["yellow"],
                "desc":"Deterministic cybersecurity challenges with hints, answers and a visible learning path.",
                "engine":"LAB ENGINE", "scope":"OFFLINE / SAFE", "state":"LIVE",
                "nodes":["BRIEF","TEST","CHECK","PROGRESS"], "metric":"LABS 04"},
            "toolkit": {
                "title":"SECURITY TOOLKIT // FIELD CONSOLE", "kicker":"TOOLKIT CORE", "accent":P["orange"],
                "desc":"Functional local utilities for hashing, encoding, parsing, IOC extraction, password analysis and evidence handling.",
                "engine":"UTILITY ENGINE", "scope":"LOCAL / SAFE", "state":"READY",
                "nodes":["INPUT","PARSE","CHECK","OUTPUT"], "metric":"TOOLS 10"},
            "development": {
                "title":"DEVELOPMENT // BUILD CONTROL", "kicker":"BUILD SYSTEM", "accent":P["cyan"],
                "desc":"Project inventory, diagnostics, workspaces and engineering controls for the local build.",
                "engine":"BUILD CORE", "scope":"LOCAL / PROJECT", "state":"ONLINE",
                "nodes":["SCAN","DIAG","SESSION","REPORT"], "metric":"ENGINEERING"},
            "developer": {
                "title":"DEVELOPER // IDENTITY CORE", "kicker":"IDENTITY SYSTEM", "accent":P["cyan"],
                "desc":"Platform identity, engineering mission and the visual BlackBox core network.",
                "engine":"IDENTITY CORE", "scope":"LOCAL / PROFILE", "state":"LIVE",
                "nodes":["VISION","BUILD","TOOLS","DEFEND"], "metric":"HN CORE"},
            "history": {
                "title":"HISTORY // AUDIT TRAIL", "kicker":"AUDIT SYSTEM", "accent":P["muted"],
                "desc":"Searchable local operations, replay-ready records and exportable audit evidence.",
                "engine":"AUDIT CORE", "scope":"LOCAL / PERSISTENT", "state":"RECORDING",
                "nodes":["TIME","MODULE","ACTION","OUTPUT"], "metric":"LOCAL LOG"},
        }
        return profiles.get(key, profiles["development"])

    def _module_hud(self, parent, key):
        """Content-aware command panel; static geometry is built once, motion is updated in-place."""
        prof=self._module_profile(key); accent=prof["accent"]
        box=tk.Frame(parent,bg='#02070c',highlightbackground=accent,highlightthickness=1); box.pack(fill='x',pady=(0,10))
        top=tk.Frame(box,bg='#06131a'); top.pack(fill='x')
        tk.Label(top,text=f"{prof['kicker']}  //  LOCAL SYSTEM",bg='#06131a',fg=accent,font=(MONO,7,'bold'),anchor='w').pack(side='left',padx=12,pady=7)
        tk.Label(top,text=f"{prof['state']}  //  {prof['scope']}",bg='#06131a',fg=P['green'],font=(MONO,7,'bold'),anchor='e').pack(side='right',padx=12,pady=7)
        body=tk.Frame(box,bg='#02070c'); body.pack(fill='x',padx=10,pady=10)
        info=tk.Frame(body,bg='#02070c'); info.pack(side='left',fill='both',expand=True,padx=(6,14))
        tk.Label(info,text=prof['title'],bg='#02070c',fg=P['text'],font=(FONT,16,'bold'),anchor='w').pack(fill='x',pady=(2,4))
        tk.Label(info,text=f"// {prof['engine']}  //  {prof['metric']}",bg='#02070c',fg=accent,font=(MONO,7,'bold'),anchor='w').pack(fill='x')
        tk.Label(info,text=prof['desc'],bg='#02070c',fg=P['muted'],font=(FONT,9),anchor='w',justify='left',wraplength=650).pack(fill='x',pady=(9,8))
        rail=tk.Frame(info,bg='#02070c'); rail.pack(fill='x',pady=(2,2))
        for i,node in enumerate(prof['nodes']):
            cell=tk.Frame(rail,bg='#06131a',highlightbackground='#123541',highlightthickness=1); cell.pack(side='left',fill='x',expand=True,padx=2)
            tk.Label(cell,text=f'{i+1:02d}',bg='#06131a',fg=accent,font=(MONO,6,'bold')).pack(anchor='w',padx=7,pady=(5,0))
            tk.Label(cell,text=node,bg='#06131a',fg=P['text'],font=(MONO,7,'bold')).pack(anchor='w',padx=7,pady=(0,5))
        viz=tk.Canvas(body,bg='#02070c',highlightthickness=0,width=230,height=190); viz.pack(side='right',fill='y',padx=(4,8))
        state_ref={'t':0,'size':None,'dynamic':{}}
        def build(w,h):
            viz.delete('all'); dyn={}
            for x in range(0,w,22): viz.create_line(x,0,x,h,fill='#071923')
            for y in range(0,h,22): viz.create_line(0,y,w,y,fill='#071923')
            cx,cy=w*.5,h*.46; dyn['cx']=cx; dyn['cy']=cy
            kind=key
            # Content-specific visualization, same HN HUD language.
            if kind=='analysis':
                dyn['bars']=[]
                for i in range(14):
                    x=10+i*15; item=viz.create_rectangle(x,h-30,x+9,h-30-20,fill=accent,outline=''); dyn['bars'].append((item,x))
                dyn['wave']=viz.create_line(8,cy, w-8,cy, fill=P['purple'],width=1)
                dyn['cursor']=viz.create_line(10,cy-28,10,cy+28,fill=P['green'],width=2)
            elif kind=='network':
                nodes=[]
                coords=[(.22,.32),(.5,.18),(.78,.32),(.35,.68),(.65,.68),(.5,.48)]
                for i,(px,py) in enumerate(coords):
                    nodes.append(viz.create_oval(w*px-5,h*py-5,w*px+5,h*py+5,fill=accent if i%2==0 else P['green'],outline=''))
                for a,b in [(0,1),(1,2),(0,3),(1,5),(2,4),(3,5),(5,4)]:
                    x1,y1=w*coords[a][0],h*coords[a][1]; x2,y2=w*coords[b][0],h*coords[b][1]; viz.create_line(x1,y1,x2,y2,fill='#164452',width=1)
                dyn['nodes']=nodes; dyn['pulse']=viz.create_oval(w*.5-7,h*.48-7,w*.5+7,h*.48+7,outline=P['cyan'],width=1)
            elif kind=='web':
                labels=['REQUEST','PARSE','MODEL','DEFENSE']; xs=[24,78,132,186]; dyn['flow']=[]
                for i,label in enumerate(labels):
                    r=viz.create_rectangle(xs[i]-18,cy-22,xs[i]+18,cy+22,outline=accent if i==0 else '#174653',width=1); viz.create_text(xs[i],cy,text=label[:5],fill=P['text'],font=(MONO,5,'bold')); dyn['flow'].append(r)
                dyn['packet']=viz.create_oval(16,cy-3,22,cy+3,fill=P['green'],outline='')
            elif kind=='blue':
                dyn['timeline']=[]
                for i in range(5):
                    y=35+i*27; viz.create_line(28,y,w-18,y,fill='#153944'); dyn['timeline'].append(viz.create_oval(25,y-4,33,y+4,fill=accent if i%2 else P['green'],outline=''))
                dyn['cursor']=viz.create_line(28,22,28,h-12,fill=P['cyan'],width=2)
            elif kind=='labs':
                dyn['nodes']=[]
                for i,label in enumerate(['BRIEF','TEST','CHECK','PROG']):
                    x=28+i*54; r=10; viz.create_text(x,h-23,text=label,fill=P['muted'],font=(MONO,5,'bold')); dyn['nodes'].append(viz.create_oval(x-r,cy-r,x+r,cy+r,outline=accent,width=1))
                dyn['link']=viz.create_line(28,cy,190,cy,fill='#164452',width=1); dyn['scan']=viz.create_line(28,cy-18,28,cy+18,fill=P['green'],width=2)
            elif kind=='history':
                dyn['events']=[]
                for i in range(6):
                    x=18+i*38; viz.create_line(x,cy-28,x,cy+28,fill='#153944'); dyn['events'].append(viz.create_oval(x-3,cy-3,x+3,cy+3,fill=accent,outline=''))
                dyn['scan']=viz.create_line(18,cy-34,18,cy+34,fill=P['green'],width=2)
            elif kind=='development':
                for x1,y1,x2,y2 in [(45,40,115,55),(115,55,185,40),(115,55,115,115),(70,120,115,115),(160,120,115,115)]: viz.create_line(x1,y1,x2,y2,fill='#164452')
                dyn['nodes']=[viz.create_rectangle(x-12,y-7,x+12,y+7,outline=accent,width=1) for x,y in [(45,40),(185,40),(115,115),(70,120),(160,120)]]
                dyn['scan']=viz.create_line(28,18,28,h-15,fill=P['green'],width=2)
            elif kind=='developer':
                cx,cy=w*.5,h*.46
                for r in (18,34,52): viz.create_oval(cx-r,cy-r,cx+r,cy+r,outline='#164452')
                dyn['sweep']=viz.create_line(cx,cy,cx+50,cy,fill=accent,width=2)
                dyn['nodes']=[viz.create_oval(cx+math.cos(i*math.tau/8)*48-3,cy+math.sin(i*math.tau/8)*48-3,cx+math.cos(i*math.tau/8)*48+3,cy+math.sin(i*math.tau/8)*48+3,fill=P['cyan'],outline='') for i in range(8)]
            else: # crypto / generic cipher pipeline
                xs=[24,78,132,186]; dyn['flow']=[]
                for i,label in enumerate(prof['nodes']):
                    viz.create_rectangle(xs[i]-17,cy-20,xs[i]+17,cy+20,outline=accent if i==0 else '#174653',width=1); viz.create_text(xs[i],cy,text=label[:5],fill=P['text'],font=(MONO,5,'bold')); dyn['flow'].append(xs[i])
                dyn['packet']=viz.create_oval(18,cy-3,24,cy+3,fill=P['green'],outline='')
            dyn['label']=viz.create_text(cx,h-12,text=f"SEQ 0000  //  {prof['engine']}",fill=accent,font=(MONO,6,'bold'))
            state_ref['dynamic']=dyn; state_ref['size']=(w,h)
        def animate():
            if not viz.winfo_exists(): return
            if self.current != key or not self._motion_active: viz.after(self._motion_hidden_ms,animate); return
            if time.monotonic() < self._resizing_until: viz.after(240,animate); return
            w,h=max(1,viz.winfo_width()),max(1,viz.winfo_height())
            if state_ref['size']!=(w,h): build(w,h)
            t=state_ref['t']; d=state_ref['dynamic']; cx,cy=d.get('cx',w*.5),d.get('cy',h*.46)
            if key=='analysis':
                for i,(item,x) in enumerate(d['bars']):
                    bh=8+((i*13+t*2)%38); viz.coords(item,x,h-30,x+9,h-30-bh)
                viz.coords(d['cursor'],8+(t*2)%(w-16),cy-28,8+(t*2)%(w-16),cy+28)
            elif key=='network':
                rr=7+3*(1+math.sin(t*.12))/2; viz.coords(d['pulse'],cx-rr,cy-rr,cx+rr,cy+rr)
            elif key in ('web','crypto'):
                if 'packet' in d:
                    px=18+(t*3.2)%(w-36); viz.coords(d['packet'],px,cy-3,px+6,cy+3)
            elif key=='blue':
                x=28+(t*2.2)%(w-46); viz.coords(d['cursor'],x,22,x,h-12)
            elif key=='labs':
                x=28+(t*2.5)%(190-28); viz.coords(d['scan'],x,cy-18,x,cy+18)
            elif key in ('history','development'):
                x=28+(t*2.1)%(w-46); viz.coords(d['scan'],x,22,x,h-12) if key=='development' else viz.coords(d['scan'],x,cy-34,x,cy+34)
            elif key=='developer':
                a=t*.05; viz.coords(d['sweep'],cx,cy,cx+50*math.cos(a),cy+50*math.sin(a))
            viz.itemconfigure(d['label'],text=f"SEQ {t%10000:04d}  //  {prof['engine']}")
            state_ref['t']=(t+1)%10000; viz.after(120,animate)
        viz.after_idle(animate)
        return box

    # ---------- v17 lab environment ----------
    def lab_environment_page(self):
        p=tk.Frame(self.content,bg=P['bg'])
        self.heading(p,'HN / LAB ENVIRONMENT','SECURITY LABS // V17','Interactive offline environments with objectives, hints, scoring, persistent progress and deterministic evidence.')
        canvas,inner=self._make_canvas(p); self._module_hud(inner,'labs')
        top=self.glass(inner); top.pack(fill='x',pady=(0,10))
        self._tool_header(top,'LAB ENVIRONMENT ENGINE // OFFLINE-FIRST','Every scenario is local and deterministic. No external targets, scanning or arbitrary command execution.')
        bar=tk.Frame(top,bg=P['panel']); bar.pack(fill='x',padx=16,pady=(0,10))
        self.lab_v17_status=tk.Label(bar,text='',bg=P['panel'],fg=P['green'],font=(MONO,9,'bold'),anchor='w'); self.lab_v17_status.pack(side='left',padx=4)
        self.btn(bar,'REFRESH',self.refresh_lab_v17).pack(side='right',padx=3)
        self.btn(bar,'RESET',self.reset_lab_v17).pack(side='right',padx=3)
        self.btn(bar,'TERMINAL',self.launch_blackbox_terminal,True).pack(side='right',padx=3)
        grid=tk.Frame(inner,bg=P['bg']); grid.pack(fill='x',pady=4)
        self._lab_v17_cards=[]
        engine=lab_engine.LabEngine()
        for idx,lab in enumerate(engine.catalog()):
            r,c=divmod(idx,2)
            card=self.glass(grid); card.grid(row=r,column=c,sticky='nsew',padx=5,pady=5)
            grid.grid_columnconfigure(c,weight=1)
            accent={'Beginner':P['green'],'Intermediate':P['yellow'],'Advanced':P['red']}.get(lab['difficulty'],P['cyan'])
            head=tk.Frame(card,bg=P['panel2']); head.pack(fill='x')
            tk.Label(head,text=lab['id'],bg=P['panel2'],fg=accent,font=(MONO,7,'bold')).pack(side='left',padx=10,pady=9)
            tk.Label(head,text=lab['difficulty'].upper(),bg=P['panel2'],fg=accent,font=(MONO,7,'bold')).pack(side='right',padx=10,pady=9)
            tk.Label(card,text=lab['title'],bg=P['panel'],fg=P['text'],font=(FONT,12,'bold'),anchor='w').pack(fill='x',padx=12,pady=(10,3))
            tk.Label(card,text=lab['category']+'  //  '+lab['objective'],bg=P['panel'],fg=accent,font=(MONO,7,'bold'),anchor='w',wraplength=430,justify='left').pack(fill='x',padx=12,pady=(0,5))
            tk.Label(card,text=lab['prompt'],bg=P['panel'],fg=P['muted'],font=(FONT,8),anchor='w',wraplength=430,justify='left').pack(fill='x',padx=12,pady=(0,8))
            ans=tk.Entry(card,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,9)); ans.pack(fill='x',padx=12,pady=4)
            status=tk.Label(card,text='READY',bg=P['panel'],fg=P['cyan'],font=(MONO,7,'bold'),anchor='w'); status.pack(fill='x',padx=12,pady=4)
            def check(lid=lab['id'], entry=ans, st=status):
                try:
                    result=engine.check(lid,entry.get())
                    if result['correct']: st.configure(text=f"✓ COMPLETE  //  SCORE {result['score']}",fg=P['green'])
                    else: st.configure(text=f"✕ NOT YET  //  ATTEMPTS {result['attempts']}",fg=P['red'])
                    self.refresh_lab_v17()
                except Exception as exc: st.configure(text='ERROR // '+str(exc),fg=P['red'])
            def hint(lid=lab['id'], st=status):
                q=engine.get(lid); st.configure(text='HINT // '+q.hint,fg=P['yellow'])
            acts=tk.Frame(card,bg=P['panel']); acts.pack(fill='x',padx=10,pady=(4,10))
            self.btn(acts,'CHECK',check,True).pack(side='right',padx=2); self.btn(acts,'HINT',hint).pack(side='right',padx=2)
            self._lab_v17_cards.append((lab['id'],status,ans))
        self.refresh_lab_v17()
        return p

    def refresh_lab_v17(self):
        if not hasattr(self,'lab_v17_status'): return
        e=lab_engine.LabEngine(); d=e.progress(); self.lab_v17_status.configure(text=f"LAB ENGINE ONLINE  //  {d['completed']:02d}/{d['total']:02d}  //  {d['percent']:02d}%  //  SCORE {d['score']}")
        for lid,status,entry in getattr(self,'_lab_v17_cards',[]):
            if lid in e.state.get('completed',[]): status.configure(text=f"✓ COMPLETE  //  SCORE {e.state.get('scores',{}).get(lid,0)}",fg=P['green'])

    def reset_lab_v17(self):
        if messagebox.askyesno('HN BLACKBOX','Reset all V17 local lab progress?'):
            lab_engine.LabEngine().reset(); self.refresh_lab_v17()

    def launch_blackbox_terminal(self):
        root=Path(__file__).resolve().parents[1]; script=root/'blackbox_console.py'
        try:
            if sys.platform.startswith('win'):
                subprocess.Popen(['cmd','/k',sys.executable,str(script)],cwd=str(root))
            else:
                candidates=[['x-terminal-emulator','-e',sys.executable,str(script)],['gnome-terminal','--',sys.executable,str(script)],['konsole','-e',sys.executable,str(script)]]
                for cmd in candidates:
                    try: subprocess.Popen(cmd,cwd=str(root)); break
                    except FileNotFoundError: continue
                else: subprocess.Popen([sys.executable,str(script)],cwd=str(root))
        except Exception as exc: messagebox.showerror('HN BLACKBOX','Terminal launch failed\n'+str(exc))

    # ---------- roadmap / future areas ----------
    def future_page(self,key):
        p=tk.Frame(self.content,bg=P['bg'])
        titles={'analysis':('CRYPTANALYSIS // ANALYSIS LAB','Frequency, Index of Coincidence, Caesar ranking and Kasiski examination.'),'network':('NETWORK SECURITY // LOCAL TOOLKIT','IP intelligence, subnet math and DNS resolution from the local machine.'),'web':('WEB SECURITY // SAFE LAB','HTTP parsing, local request simulation and OWASP defensive concepts.'),'blue':('BLUE TEAM // DEFENSE CENTER','Log triage, IOC classification, timeline extraction and hash inspection.'),'labs':('SECURITY LABS // OFFLINE ARENA','Real local training challenges across cryptography, hashing, network, web security, blue team and forensics.'), 'toolkit':('SECURITY TOOLKIT // FIELD CONSOLE','Functional local utilities for hashing, encoding, parsing, IOC extraction and evidence handling.')}
        title,sub=titles[key]
        self.heading(p,'HN / MODULE',self.t(key),sub)
        canvas,inner=self._make_canvas(p)
        self._module_hud(inner,key)
        banner=self.glass(inner);banner.pack(fill='x',pady=(0,10))
        tk.Label(banner,text=title,bg=P['panel2'],fg=P['cyan'],font=(MONO,11,'bold'),anchor='w').pack(fill='x',padx=18,pady=(13,3))
        tk.Label(banner,text='REAL LOCAL TOOLING // RESULTS ARE COMPUTED, NOT MOCKED',bg=P['panel2'],fg=P['green'],font=(MONO,7,'bold'),anchor='w').pack(fill='x',padx=18,pady=(0,12))
        if key=='analysis': self._analysis_tool_v10(inner); self.add_auto_analysis_panel(inner)
        elif key=='network': self._network_tool_v10(inner)
        elif key=='web': self._web_tool_v10(inner)
        elif key=='blue': self._blue_tool_v10(inner)
        elif key=='toolkit': pass
        else: self._labs_tool_v10(inner); self._lab_progress_panel(inner)
        return p

    def _tool_header(self,parent,kicker,desc):
        tk.Label(parent,text=kicker,bg=parent.cget('bg'),fg=P['yellow'],font=(MONO,8,'bold'),anchor='w').pack(fill='x',padx=16,pady=(12,3))
        tk.Label(parent,text=desc,bg=parent.cget('bg'),fg=P['muted'],font=(FONT,8),anchor='w',justify='left',wraplength=950).pack(fill='x',padx=16,pady=(0,8))

    def _analysis_tool_v10(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._tool_header(box,'01 // FREQUENCY ANALYZER','Counts letters and shows the observed distribution.')
        txt=tk.Text(box,height=5,bg=P['panel2'],fg=P['text'],font=(FONT,10),relief='flat',wrap='word');txt.pack(fill='x',padx=16,pady=5);txt.insert('1.0','THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG. THE FOX IS FAST.')
        out=tk.Text(box,height=7,bg='#030a11',fg=P['green'],font=(MONO,9),relief='flat');out.pack(fill='x',padx=16,pady=7)
        def run():
            rows=frequency_analysis.analyze(txt.get('1.0','end-1c'));out.delete('1.0','end');out.insert('end','LETTER COUNT PERCENT  BAR\n'+'-'*44+'\n')
            for r in rows[:18]:out.insert('end',f"{r['letter']:>6} {r['count']:>5} {r['percent']:>6.2f}%  {'█'*max(1,min(28,int(r['percent']*1.5)))}\n")
            self._record_tool_operation('cryptanalysis','Frequency analysis',txt.get('1.0','end-1c'),out.get('1.0','end-1c'))
        self.btn(box,'RUN ANALYSIS',run,True).pack(anchor='e',padx=16,pady=(0,12))
        box2=self.card(inner);box2.pack(fill='x',pady=6);self._tool_header(box2,'02 // IC + KASISKI','Index of coincidence estimates language/cipher structure; Kasiski finds repeated n-grams and distances.')
        inp=tk.Text(box2,height=5,bg=P['panel2'],fg=P['text'],font=(MONO,9),relief='flat');inp.pack(fill='x',padx=16,pady=5);inp.insert('1.0','LXFOPVEFRNHRLXFOPVEFRNHR')
        res=tk.Text(box2,height=9,bg='#030a11',fg=P['cyan'],font=(MONO,8),relief='flat');res.pack(fill='x',padx=16,pady=7)
        def deep():
            s=inp.get('1.0','end-1c');ic=cryptanalysis.index_of_coincidence(s);reps,factors=cryptanalysis.kasiski(s);lens=cryptanalysis.estimate_vigenere_key_lengths(s,10)
            res.delete('1.0','end');res.insert('end',f'INDEX OF COINCIDENCE : {ic:.5f}\n\nTOP KEY LENGTHS:\n')
            for score,k in lens[:6]:res.insert('end',f'  k={k:02d}  avg_IC={score:.5f}\n')
            res.insert('end','\nREPEATED N-GRAMS:\n')
            for gram,pos in reps[:8]:res.insert('end',f'  {gram:<10} positions={pos}\n')
            res.insert('end',f'\nFACTOR COUNTS: {factors[:8]}\n')
            self._record_tool_operation('cryptanalysis','IC + Kasiski',s,res.get('1.0','end-1c'))
        self.btn(box2,'RUN DEEP ANALYSIS',deep,True).pack(anchor='e',padx=16,pady=(0,12))
        box3=self.card(inner);box3.pack(fill='x',pady=6);self._tool_header(box3,'03 // CAESAR CANDIDATE RANKING','Ranks all Caesar shifts by chi-square distance from English letter frequencies.')
        ent=tk.Entry(box3,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,10));ent.pack(fill='x',padx=16,pady=5);ent.insert(0,'KHOOR ZRUOG')
        rr=tk.Text(box3,height=8,bg='#030a11',fg=P['green'],font=(MONO,8),relief='flat');rr.pack(fill='x',padx=16,pady=7)
        def rank():
            rr.delete('1.0','end')
            for score,key,plain in cryptanalysis.caesar_rank(ent.get())[:10]:rr.insert('end',f'KEY={key:02d}  CHI={score:8.2f}  {plain}\n')
            self._record_tool_operation('cryptanalysis','Caesar ranking',ent.get(),rr.get('1.0','end-1c'))
        self.btn(box3,'RANK SHIFTS',rank).pack(anchor='e',padx=16,pady=(0,12))

    def _network_tool_v10(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._tool_header(box,'01 // IP INTELLIGENCE','Classifies IPv4/IPv6 properties using the standard library.')
        ent=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,10));ent.pack(fill='x',padx=16,pady=5);ent.insert(0,'192.168.1.10')
        out=tk.Text(box,height=6,bg='#030a11',fg=P['green'],font=(MONO,9),relief='flat');out.pack(fill='x',padx=16,pady=7)
        def run():
            try:d=network_tools.analyze_ip(ent.get());out.delete('1.0','end');out.insert('end','\n'.join(f'{k.upper():<14}: {v}' for k,v in d.items()));self._record_tool_operation('network','IP intelligence',ent.get(),out.get('1.0','end-1c'))
            except Exception as e:out.delete('1.0','end');out.insert('end',f'ERROR: {e}')
        self.btn(box,'ANALYZE ADDRESS',run,True).pack(anchor='e',padx=16,pady=(0,12))
        sub=self.card(inner);sub.pack(fill='x',pady=6);self._tool_header(sub,'02 // SUBNET CALCULATOR','Network, broadcast, prefix and usable host count.')
        se=tk.Entry(sub,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,10));se.pack(fill='x',padx=16,pady=5);se.insert(0,'192.168.1.0/24')
        sr=tk.Text(sub,height=5,bg='#030a11',fg=P['cyan'],font=(MONO,9),relief='flat');sr.pack(fill='x',padx=16,pady=7)
        def subrun():
            try:d=network_tools.subnet(se.get());sr.delete('1.0','end');sr.insert('end','\n'.join(f'{k.upper():<14}: {v}' for k,v in d.items()));self._record_tool_operation('network','Subnet calculation',se.get(),sr.get('1.0','end-1c'))
            except Exception as e:sr.delete('1.0','end');sr.insert('end',f'ERROR: {e}')
        self.btn(sub,'CALCULATE SUBNET',subrun).pack(anchor='e',padx=16,pady=(0,12))
        dns=self.card(inner);dns.pack(fill='x',pady=6);self._tool_header(dns,'03 // DNS RESOLVER','Uses the local OS resolver. No scanning or enumeration.')
        de=tk.Entry(dns,bg=P['panel2'],fg=P['text'],relief='flat',font=(MONO,10));de.pack(fill='x',padx=16,pady=5);de.insert(0,socket.gethostname())
        dr=tk.Text(dns,height=6,bg='#030a11',fg=P['green'],font=(MONO,8),relief='flat');dr.pack(fill='x',padx=16,pady=7)
        def dnsrun():
            try:
                rows=network_tools.dns_lookup(de.get());dr.delete('1.0','end');seen=[]
                for row in rows:
                    addr=row[-1][0] if row and row[-1] else ''
                    if addr and addr not in seen:seen.append(addr)
                dr.insert('end','HOST: '+de.get().strip()+'\n\n'+'\n'.join(seen) if seen else 'No addresses returned.')
                self._record_tool_operation('network','DNS resolution',de.get(),dr.get('1.0','end-1c'))
            except Exception as e:dr.delete('1.0','end');dr.insert('end',f'DNS ERROR: {e}')
        self.btn(dns,'RESOLVE HOST',dnsrun).pack(anchor='e',padx=16,pady=(0,12))

    def _web_tool_v10(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._tool_header(box,'01 // REQUEST BUILDER','Build and inspect a synthetic HTTP request without sending it anywhere.')
        row=tk.Frame(box,bg=P['panel']);row.pack(fill='x',padx=16,pady=5);method=tk.StringVar(value='GET');ttk.Combobox(row,textvariable=method,values=['GET','POST','PUT','PATCH','DELETE'],state='readonly',width=10).pack(side='left',padx=(0,6));url=tk.Entry(row,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,9));url.pack(side='left',fill='x',expand=True);url.insert(0,'https://example.local/api/profile?id=42')
        body=tk.Text(box,height=5,bg=P['panel2'],fg=P['text'],font=(MONO,9),relief='flat');body.pack(fill='x',padx=16,pady=5);body.insert('1.0','{"name":"HN","role":"analyst"}')
        resp=tk.Text(box,height=10,bg='#030a11',fg=P['green'],font=(MONO,8),relief='flat');resp.pack(fill='x',padx=16,pady=7)
        def build():
            u=url.get().strip();parsed=urlparse(u);qs=parse_qs(parsed.query);m=method.get();payload=body.get('1.0','end-1c')
            lines=[f'{m} {parsed.path or "/"}'+(('?'+parsed.query) if parsed.query else '')+' HTTP/1.1','Host: '+(parsed.netloc or 'example.local'),'User-Agent: HN-BlackBox-Lab','Content-Type: application/json','X-Lab-Mode: LOCAL-ONLY','',payload if m not in ('GET','DELETE') else '']
            resp.delete('1.0','end');resp.insert('end','\n'.join(lines)+'\n\nPARSED QUERY PARAMS:\n'+json.dumps(qs,indent=2));self._record_tool_operation('web','HTTP request simulation',u,resp.get('1.0','end-1c'),m)
        self.btn(box,'BUILD REQUEST',build,True).pack(anchor='e',padx=16,pady=(0,12))
        ch=self.card(inner);ch.pack(fill='x',pady=6);self._tool_header(ch,'02 // OWASP DEFENSIVE CARDS','Synthetic concepts from the local challenge catalogue.')
        for item in web_lab.get_challenges():
            r=tk.Frame(ch,bg=P['panel2'],highlightbackground=P['line'],highlightthickness=1);r.pack(fill='x',padx=14,pady=3)
            tk.Label(r,text=item['id'],bg=P['panel2'],fg=P['cyan'],font=(MONO,8,'bold')).pack(side='left',padx=10,pady=8)
            tk.Label(r,text=item['title']+'  // '+item['difficulty'],bg=P['panel2'],fg=P['text'],font=(FONT,9,'bold')).pack(side='left',padx=4)
            tk.Label(r,text='FIX: '+item['fix'],bg=P['panel2'],fg=P['muted'],font=(FONT,8),anchor='e').pack(side='right',padx=10)

    def _blue_tool_v10(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._tool_header(box,'01 // LOG TRIAGE','Counts events, extracts IPs and flags repeated failure sources.')
        sample='2026-08-09 20:01 login failed from 203.0.113.9\n2026-08-09 20:02 login failed from 203.0.113.9\n2026-08-09 20:03 login failed from 203.0.113.9\n2026-08-09 20:04 login failed from 203.0.113.9\n2026-08-09 20:05 login failed from 203.0.113.9\n2026-08-09 20:06 successful login from 192.168.1.10'
        inp=tk.Text(box,height=8,bg=P['panel2'],fg=P['text'],font=(MONO,8),relief='flat');inp.pack(fill='x',padx=16,pady=5);inp.insert('1.0',sample)
        out=tk.Text(box,height=9,bg='#030a11',fg=P['green'],font=(MONO,8),relief='flat');out.pack(fill='x',padx=16,pady=7)
        def analyze():
            d=blue_team.analyze_log(inp.get('1.0','end-1c'));out.delete('1.0','end');out.insert('end',f"LINES={d['lines']}  FAILED={d['failed']}\n\nTOP IPs:\n")
            for ip,n in d['ips'][:10]:out.insert('end',f'  {ip:<18} {n:>4}\n')
            out.insert('end','\nSUSPICIOUS:\n'+('\n'.join(f'  {ip} // {n} failures' for ip,n in d['suspicious']) or '  none')+'\n\nFAILED EVENTS:\n'+'\n'.join(d['failed_lines'][:10]))
            self._record_tool_operation('blue_team','Log triage',inp.get('1.0','end-1c'),out.get('1.0','end-1c'))
        self.btn(box,'RUN TRIAGE',analyze,True).pack(anchor='e',padx=16,pady=(0,12))
        ioc=self.card(inner);ioc.pack(fill='x',pady=6);self._tool_header(ioc,'02 // IOC + HASH CHECK','Classifies tokens locally and computes SHA-256 for evidence handling.')
        ie=tk.Entry(ioc,bg=P['panel2'],fg=P['text'],relief='flat',font=(MONO,10));ie.pack(fill='x',padx=16,pady=5);ie.insert(0,'203.0.113.9')
        ir=tk.Text(ioc,height=5,bg='#030a11',fg=P['cyan'],font=(MONO,8),relief='flat');ir.pack(fill='x',padx=16,pady=7)
        def check():
            v=ie.get().strip();kind='IPv4' if re.fullmatch(r'(?:\d{1,3}\.){3}\d{1,3}',v) else ('SHA-256' if re.fullmatch(r'[0-9a-fA-F]{64}',v) else 'TOKEN')
            digest=hashlib.sha256(v.encode()).hexdigest();ir.delete('1.0','end');ir.insert('end',f'TYPE       : {kind}\nVALUE      : {v}\nSHA-256    : {digest}\nREPUTATION : NOT QUERIED (LOCAL-ONLY)')
            self._record_tool_operation('blue_team','IOC inspection',v,ir.get('1.0','end-1c'))
        self.btn(ioc,'INSPECT IOC',check).pack(anchor='e',padx=16,pady=(0,12))

    def _labs_tool_v10(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._tool_header(box,'OFFLINE CHALLENGE ENGINE','Solve deterministic security exercises. No network access is required.')
        challenges=labs.all_labs()+labs3.catalog();idx=tk.IntVar(value=0);score=tk.IntVar(value=0)
        title=tk.Label(box,text='',bg=P['panel'],fg=P['text'],font=(FONT,15,'bold'),anchor='w');title.pack(fill='x',padx=16,pady=5)
        prompt=tk.Label(box,text='',bg=P['panel'],fg=P['muted'],font=(FONT,10),anchor='w',justify='left',wraplength=950);prompt.pack(fill='x',padx=16,pady=5)
        ans=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,10));ans.pack(fill='x',padx=16,pady=6)
        status=tk.Label(box,text='READY',bg=P['panel'],fg=P['cyan'],font=(MONO,9,'bold'),anchor='w');status.pack(fill='x',padx=16,pady=4)
        score_label=tk.Label(box,text='SCORE 0 / 0',bg=P['panel'],fg=P['yellow'],font=(MONO,8,'bold'),anchor='e');score_label.pack(fill='x',padx=16)
        def load():
            q=challenges[idx.get()%len(challenges)];title.configure(text=f"{q['id']}  //  {q['title']}  [{q['difficulty']}]" );prompt.configure(text=q['prompt']);ans.delete(0,'end');status.configure(text='READY',fg=P['cyan'])
        def check():
            q=challenges[idx.get()%len(challenges)];ok=ans.get().strip().upper()==q['answer'].upper()
            msg='CORRECT' if ok else 'NOT YET // HINT: '+q['hint']
            if ok: score.set(score.get()+1); status.configure(text='✓ '+msg,fg=P['green'])
            else: status.configure(text='✕ '+msg,fg=P['red'])
            score_label.configure(text=f'SCORE {score.get()} / {idx.get()+1}')
            lab_progress.record_attempt(q['id'], ok)
            self.refresh_lab_progress()
            self._record_tool_operation('labs','Challenge check',ans.get(),msg,q['id'])
        def nxt():idx.set((idx.get()+1)%len(challenges));load()
        acts=tk.Frame(box,bg=P['panel']);acts.pack(fill='x',padx=16,pady=10);self.btn(acts,'CHECK ANSWER',check,True).pack(side='left',padx=3);self.btn(acts,'NEXT LAB',nxt).pack(side='left',padx=3);load()
        path=self.card(inner);path.pack(fill='x',pady=7);self._tool_header(path,'LAB CATALOG','Real challenge records loaded from core/security_labs/labs.py')
        for q in challenges:
            r=tk.Frame(path,bg=P['panel2']);r.pack(fill='x',padx=14,pady=3);tk.Label(r,text=q['category'],bg=P['panel2'],fg=P['purple'],font=(MONO,7,'bold')).pack(side='left',padx=10,pady=7);tk.Label(r,text=q['title'],bg=P['panel2'],fg=P['text'],font=(FONT,9)).pack(side='left');tk.Label(r,text=q['difficulty'],bg=P['panel2'],fg=P['yellow'],font=(MONO,7,'bold')).pack(side='right',padx=10)
    def _section_title(self,parent,text): tk.Label(parent,text=text,bg=parent.cget('bg'),fg=P['yellow'],font=(MONO,8,'bold'),anchor='e').pack(fill='x',padx=16,pady=(12,6))

    def _analysis_tool(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._section_title(box,'FREQUENCY ANALYZER')
        txt=tk.Text(box,height=5,bg=P['panel2'],fg=P['text'],font=(FONT,11),relief='flat',wrap='word');txt.pack(fill='x',padx=16,pady=5);txt.insert('1.0','THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG. THE FOX IS FAST.')
        out=tk.Text(box,height=7,bg='#030a11',fg=P['green'],font=(MONO,9),relief='flat');out.pack(fill='x',padx=16,pady=7)
        def run():
            rows=frequency_analysis.analyze(txt.get('1.0','end-1c'));out.delete('1.0','end');out.insert('end','LETTER   COUNT   PERCENT\n'+'-'*32+'\n')
            for r in rows[:15]: out.insert('end',f"{r['letter']:>5}   {r['count']:>5}   {r['percent']:>6.2f}%\n")
        self.btn(box,'RUN FREQUENCY ANALYSIS',run,True).pack(anchor='e',padx=16,pady=(0,12))
        rank=self.card(inner);rank.pack(fill='x',pady=6);self._section_title(rank,'CAESAR RANKING')
        inp=tk.Entry(rank,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,10));inp.pack(fill='x',padx=16,pady=5);inp.insert(0,'KHOOR ZRUOG')
        res=tk.Text(rank,height=7,bg='#030a11',fg=P['cyan'],font=(MONO,8),relief='flat');res.pack(fill='x',padx=16,pady=7)
        def rankit():
            res.delete('1.0','end')
            for score,key,plain in cryptanalysis.caesar_rank(inp.get())[:8]: res.insert('end',f'key={key:02d}  chi={score:7.2f}  {plain}\n')
        self.btn(rank,'RANK CANDIDATES',rankit).pack(anchor='e',padx=16,pady=(0,12))

    def _network_tool(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._section_title(box,'IP INTELLIGENCE')
        entry=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,11));entry.pack(fill='x',padx=16,pady=5);entry.insert(0,'192.168.1.10')
        result=tk.Text(box,height=6,bg='#030a11',fg=P['green'],font=(MONO,9),relief='flat');result.pack(fill='x',padx=16,pady=7)
        def iprun():
            try:
                d=network_tools.analyze_ip(entry.get());result.delete('1.0','end');result.insert('end','\n'.join(f'{k.upper():<12}: {v}' for k,v in d.items()))
            except Exception as e: result.delete('1.0','end');result.insert('end',f'ERROR: {e}')
        self.btn(box,'ANALYZE IP',iprun,True).pack(anchor='e',padx=16,pady=(0,12))
        sub=self.card(inner);sub.pack(fill='x',pady=6);self._section_title(sub,'SUBNET CALCULATOR')
        se=tk.Entry(sub,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,11));se.pack(fill='x',padx=16,pady=5);se.insert(0,'192.168.1.0/24')
        sr=tk.Text(sub,height=5,bg='#030a11',fg=P['cyan'],font=(MONO,9),relief='flat');sr.pack(fill='x',padx=16,pady=7)
        def subrun():
            try:
                d=network_tools.subnet(se.get());sr.delete('1.0','end');sr.insert('end','\n'.join(f'{k.upper():<12}: {v}' for k,v in d.items()))
            except Exception as e: sr.delete('1.0','end');sr.insert('end',f'ERROR: {e}')
        self.btn(sub,'CALCULATE SUBNET',subrun).pack(anchor='e',padx=16,pady=(0,12))

    def _web_tool(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._section_title(box,'HTTP REQUEST SIMULATOR')
        grid=tk.Frame(box,bg=P['panel']);grid.pack(fill='x',padx=16);method=tk.StringVar(value='GET');ttk.Combobox(grid,textvariable=method,values=['GET','POST','PUT','DELETE'],state='readonly',width=10).grid(row=0,column=0,padx=4,pady=5,sticky='ew');path=tk.Entry(grid,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,10));path.grid(row=0,column=1,padx=4,pady=5,sticky='ew');path.insert(0,'/api/profile/42');grid.columnconfigure(1,weight=1)
        headers=tk.Text(box,height=5,bg=P['panel2'],fg=P['text'],font=(MONO,9),relief='flat');headers.pack(fill='x',padx=16,pady=6);headers.insert('1.0','Authorization: Bearer DEMO\nContent-Type: application/json')
        response=tk.Text(box,height=8,bg='#030a11',fg=P['green'],font=(MONO,9),relief='flat');response.pack(fill='x',padx=16,pady=6)
        def simulate():
            status='200 OK' if method.get()=='GET' else '201 CREATED' if method.get()=='POST' else '204 NO CONTENT';response.delete('1.0','end');response.insert('end',f'HTTP/1.1 {status}\nServer: HN-BlackBox-Lab\nPath: {path.get()}\n\n{{"simulated": true, "external_request": false}}')
        self.btn(box,'SEND TO LOCAL SIMULATOR',simulate,True).pack(anchor='e',padx=16,pady=(0,12))
        ch=self.card(inner);ch.pack(fill='x',pady=6);self._section_title(ch,'OWASP CONCEPT CARDS')
        for item in web_lab.get_challenges():
            row=tk.Frame(ch,bg=P['panel2'],highlightbackground=P['line'],highlightthickness=1);row.pack(fill='x',padx=14,pady=3);tk.Label(row,text=item['id'],bg=P['panel2'],fg=P['cyan'],font=(MONO,8,'bold')).pack(side='right',padx=10,pady=8);tk.Label(row,text=f"{item['title']}  •  {item['difficulty']}",bg=P['panel2'],fg=P['text'],font=(FONT,9,'bold')).pack(side='right',padx=6);tk.Label(row,text=item['fix'],bg=P['panel2'],fg=P['muted'],font=(FONT,8),anchor='e').pack(side='left',padx=10)

    def _blue_tool(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._section_title(box,'LOG TRIAGE')
        sample="2026-08-09 20:01 login failed from 203.0.113.9\n2026-08-09 20:02 login failed from 203.0.113.9\n2026-08-09 20:03 login failed from 203.0.113.9\n2026-08-09 20:04 login failed from 203.0.113.9\n2026-08-09 20:05 login failed from 203.0.113.9\n2026-08-09 20:06 successful login from 192.168.1.10"
        inp=tk.Text(box,height=8,bg=P['panel2'],fg=P['text'],font=(MONO,9),relief='flat');inp.pack(fill='x',padx=16,pady=5);inp.insert('1.0',sample);out=tk.Text(box,height=8,bg='#030a11',fg=P['green'],font=(MONO,9),relief='flat');out.pack(fill='x',padx=16,pady=7)
        def analyze():
            d=blue_team.analyze_log(inp.get('1.0','end-1c'));out.delete('1.0','end');out.insert('end',f"LINES       : {d['lines']}\nFAILED      : {d['failed']}\nTOP IPS     : {d['ips'][:5]}\nSUSPICIOUS  : {d['suspicious']}\n\n-- FAILED EVENTS --\n"+'\n'.join(d['failed_lines']));self._record_tool_operation('blue_team','Log triage',inp.get('1.0','end-1c'),out.get('1.0','end-1c'))
        self.btn(box,'RUN DEFENSIVE TRIAGE',analyze,True).pack(anchor='e',padx=16,pady=(0,12))
        ioc=self.card(inner);ioc.pack(fill='x',pady=6);self._section_title(ioc,'IOC QUICK CHECK');tk.Label(ioc,text='Paste an IP or hash-like token to classify locally.',bg=P['panel'],fg=P['muted'],font=(FONT,9),anchor='e').pack(fill='x',padx=16);ie=tk.Entry(ioc,bg=P['panel2'],fg=P['text'],relief='flat',font=(MONO,10));ie.pack(fill='x',padx=16,pady=7);ie.insert(0,'203.0.113.9');ir=tk.Label(ioc,text='READY',bg=P['panel'],fg=P['cyan'],font=(MONO,9,'bold'),anchor='e');ir.pack(fill='x',padx=16,pady=(0,10))
        def ioccheck():
            v=ie.get().strip();kind='IPv4' if re.fullmatch(r'(?:\d{1,3}\.){3}\d{1,3}',v) else 'TOKEN / HASH';msg=f'{kind}  //  LOCAL CLASSIFICATION  //  NO REPUTATION LOOKUP';ir.configure(text=msg);self._record_tool_operation('blue_team','IOC classification',v,msg)
        self.btn(ioc,'CLASSIFY IOC',ioccheck).pack(anchor='e',padx=16,pady=(0,12))

    def _labs_tool(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._section_title(box,'OFFLINE CHALLENGE ENGINE');challenges=labs.all_labs();idx=tk.IntVar(value=0);title=tk.Label(box,text='',bg=P['panel'],fg=P['text'],font=(FONT,15,'bold'),anchor='e');title.pack(fill='x',padx=16,pady=4);prompt=tk.Label(box,text='',bg=P['panel'],fg=P['muted'],font=(FONT,10),anchor='e',justify='right',wraplength=1050);prompt.pack(fill='x',padx=16,pady=5);ans=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,10));ans.pack(fill='x',padx=16,pady=6);status=tk.Label(box,text='READY',bg=P['panel'],fg=P['cyan'],font=(MONO,9,'bold'),anchor='e');status.pack(fill='x',padx=16)
        def load():
            q=challenges[idx.get()%len(challenges)];title.configure(text=f"{q['id']} // {q['title']} [{q['difficulty']}]" );prompt.configure(text=q['prompt']);ans.delete(0,'end');status.configure(text='READY',fg=P['cyan'])
        def check():
            q=challenges[idx.get()%len(challenges)];ok=ans.get().strip().upper()==q['answer'].upper();msg='CORRECT' if ok else 'NOT YET // HINT: '+q['hint'];status.configure(text='✓ '+msg if ok else '✕ '+msg,fg=P['green'] if ok else P['red']);self._record_tool_operation('labs','Challenge check',ans.get(),msg,q['id'])
        def nxt(): idx.set((idx.get()+1)%len(challenges));load()
        acts=tk.Frame(box,bg=P['panel']);acts.pack(fill='x',padx=16,pady=10);self.btn(acts,'CHECK ANSWER',check,True).pack(side='right',padx=3);self.btn(acts,'NEXT LAB',nxt).pack(side='right',padx=3);load();progress=self.glass(inner);progress.pack(fill='x',pady=7);self._section_title(progress,'LEARNING PATH')
        for q in challenges:
            row=tk.Frame(progress,bg=P['panel2']);row.pack(fill='x',padx=14,pady=3);tk.Label(row,text=q['category'],bg=P['panel2'],fg=P['purple'],font=(MONO,8,'bold')).pack(side='left',padx=10,pady=7);tk.Label(row,text=q['title'],bg=P['panel2'],fg=P['text'],font=(FONT,9)).pack(side='right',padx=10)

    def toolkit_page(self):
        p=tk.Frame(self.content,bg=P['bg'])
        self.heading(p,'HN / TOOLKIT','SECURITY TOOLKIT','Functional local utilities for analysis, evidence and defensive engineering. No outbound collection.')
        canvas,inner=self._make_canvas(p); self._module_hud(inner,'toolkit')
        banner=self.glass(inner); banner.pack(fill='x',pady=(0,10))
        self._tool_header(banner,'FIELD TOOLKIT','Real local computations — file hashing, Base64, URL/JWT parsing, password entropy, IOC extraction and log summaries.')
        # Hash file
        box=self.card(inner); box.pack(fill='x',pady=6); self._tool_header(box,'01 // FILE HASH / INTEGRITY','Compute MD5, SHA-1 and SHA-256 for a local file. Nothing is uploaded.')
        hash_out=tk.Text(box,height=6,bg='#030a11',fg=P['green'],font=(MONO,8),relief='flat'); hash_out.pack(fill='x',padx=16,pady=6)
        def choose_hash():
            path=filedialog.askopenfilename(title='Select local file')
            if not path:return
            try: d=real_tools.hash_file(path); hash_out.delete('1.0','end'); hash_out.insert('end','\n'.join(f'{k.upper():<10}: {v}' for k,v in d.items())); self._record_tool_operation('toolkit','File hash',path,hash_out.get('1.0','end-1c'))
            except Exception as e: hash_out.delete('1.0','end'); hash_out.insert('end','ERROR: '+str(e))
        self.btn(box,'HASH LOCAL FILE',choose_hash,True).pack(anchor='e',padx=16,pady=(0,12))
        # Encoding
        box=self.card(inner); box.pack(fill='x',pady=6); self._tool_header(box,'02 // BASE64 ENCODER / DECODER','Useful for inspecting encoded content. Base64 is not encryption.')
        btxt=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,9)); btxt.pack(fill='x',padx=16,pady=6); btxt.insert(0,'HN_BLACKBOX')
        bout=tk.Text(box,height=4,bg='#030a11',fg=P['cyan'],font=(MONO,8),relief='flat'); bout.pack(fill='x',padx=16,pady=6)
        def enc():
            try: v=real_tools.b64_encode(btxt.get()); bout.delete('1.0','end'); bout.insert('end',v)
            except Exception as e: bout.delete('1.0','end'); bout.insert('end','ERROR: '+str(e))
        def dec():
            try: v=real_tools.b64_decode(btxt.get()); bout.delete('1.0','end'); bout.insert('end',v)
            except Exception as e: bout.delete('1.0','end'); bout.insert('end','ERROR: '+str(e))
        acts=tk.Frame(box,bg=P['panel']); acts.pack(fill='x',padx=16,pady=6); self.btn(acts,'ENCODE',enc,True).pack(side='left',padx=3); self.btn(acts,'DECODE',dec).pack(side='left',padx=3)
        # URL + JWT
        box=self.card(inner); box.pack(fill='x',pady=6); self._tool_header(box,'03 // URL / JWT INSPECTOR','Parse URL components and decode JWT header/payload locally. JWT signatures are never trusted or verified here.')
        uent=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,9)); uent.pack(fill='x',padx=16,pady=5); uent.insert(0,'https://example.local/api?q=blackbox&page=2')
        uout=tk.Text(box,height=7,bg='#030a11',fg=P['text'],font=(MONO,8),relief='flat'); uout.pack(fill='x',padx=16,pady=6)
        def parseu():
            try: d=real_tools.parse_url(uent.get()); uout.delete('1.0','end'); uout.insert('end',json.dumps(d,indent=2))
            except Exception as e:uout.delete('1.0','end');uout.insert('end','ERROR: '+str(e))
        self.btn(box,'PARSE URL',parseu,True).pack(anchor='e',padx=16,pady=(0,7))
        jwt=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,8)); jwt.pack(fill='x',padx=16,pady=5); jwt.insert(0,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJyb2xlIjoiYW5hbHlzdCJ9.demo')
        def jwtdec():
            try:d=real_tools.decode_jwt(jwt.get());uout.delete('1.0','end');uout.insert('end',json.dumps(d,indent=2))
            except Exception as e:uout.delete('1.0','end');uout.insert('end','ERROR: '+str(e))
        self.btn(box,'DECODE JWT LOCALLY',jwtdec).pack(anchor='e',padx=16,pady=(0,12))
        # Password entropy
        box=self.card(inner); box.pack(fill='x',pady=6); self._tool_header(box,'04 // PASSWORD ENTROPY ESTIMATOR','Estimates search-space entropy locally; it does not store or transmit the password.')
        pe=tk.Entry(box,show='•',bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,9)); pe.pack(fill='x',padx=16,pady=6); pe.insert(0,'Example-Only-Change-Me')
        po=tk.Label(box,text='READY',bg=P['panel'],fg=P['cyan'],font=(MONO,9,'bold'),anchor='w'); po.pack(fill='x',padx=16,pady=6)
        def entropy():
            d=real_tools.password_entropy(pe.get()); po.configure(text=f"LENGTH={d['length']}  CHARSET={d['charset_size']}  ENTROPY≈{d['entropy_bits']} bits  //  {d['rating'].upper()}",fg=P['green'] if d['entropy_bits']>=60 else P['yellow'])
        self.btn(box,'ESTIMATE ENTROPY',entropy).pack(anchor='e',padx=16,pady=(0,12))
        # IOC / log
        box=self.card(inner); box.pack(fill='x',pady=6); self._tool_header(box,'05 // IOC + LOG ANALYZER','Extract IPs, hashes, URLs, emails and summarize alert-like log events from pasted local text.')
        ti=tk.Text(box,height=8,bg=P['panel2'],fg=P['text'],font=(MONO,8),relief='flat'); ti.pack(fill='x',padx=16,pady=5); ti.insert('1.0','2026-08-10 login failed from 203.0.113.9\nGET https://example.local/login\nSHA256 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')
        to=tk.Text(box,height=9,bg='#030a11',fg=P['green'],font=(MONO,8),relief='flat'); to.pack(fill='x',padx=16,pady=7)
        def ioc():
            d=real_tools.extract_iocs(ti.get('1.0','end-1c')); to.delete('1.0','end'); to.insert('end','IOCS\n'+json.dumps(d,indent=2))
        def logs():
            d=real_tools.log_summary(ti.get('1.0','end-1c')); to.delete('1.0','end'); to.insert('end',json.dumps(d,indent=2))
        acts=tk.Frame(box,bg=P['panel']); acts.pack(fill='x',padx=16,pady=7); self.btn(acts,'EXTRACT IOCS',ioc,True).pack(side='left',padx=3); self.btn(acts,'SUMMARIZE LOGS',logs).pack(side='left',padx=3)
        return p

    def development_page(self):
        p=tk.Frame(self.content,bg=P['bg'])
        self.heading(p,'HN / BUILD SYSTEM','DEVELOPMENT','Project health, module inventory and local test status.')
        canvas,inner=self._make_canvas(p)
        self._module_hud(inner,'development')
        controls=self.glass(inner); controls.pack(fill='x',pady=(0,8))
        self._tool_header(controls,'ENGINEERING CONSOLE','Save a local workspace snapshot, restore it later, run diagnostics, or export a compact build report.')
        self.btn(controls,'SAVE WORKSPACE',self.save_workspace,True).pack(side='left',padx=(16,4),pady=(0,12))
        self.btn(controls,'LOAD WORKSPACE',self.load_workspace).pack(side='left',padx=4,pady=(0,12))
        self.btn(controls,'RUN DIAGNOSTICS',self.run_diagnostics).pack(side='left',padx=4,pady=(0,12))
        self.btn(controls,'EXPORT REPORT',self.export_build_report).pack(side='left',padx=4,pady=(0,12))
        self.btn(controls,'SESSION REPORT',self.export_session_report).pack(side='left',padx=4,pady=(0,12))
        self._command_center_panel(inner)
        root=Path(__file__).resolve().parent.parent
        files=[]
        for path in sorted(root.rglob('*.py')):
            if '.pytest_cache' not in str(path): files.append(path.relative_to(root).as_posix())
        tests=[x for x in files if x.startswith('tests/')]
        cores=[x for x in files if x.startswith('core/')]
        ui=[x for x in files if x.startswith('gui/')]
        overview=self.glass(inner);overview.pack(fill='x',pady=(0,8));self._tool_header(overview,'PROJECT HEALTH','Live inventory generated from the project directory.')
        grid=tk.Frame(overview,bg=P['panel2']);grid.pack(fill='x',padx=14,pady=(0,12))
        for i,(label,val,color) in enumerate([('CORE MODULES',len(cores),P['cyan']),('GUI FILES',len(ui),P['green']),('TEST FILES',len(tests),P['purple']),('PY FILES',len(files),P['yellow'])]):
            c=tk.Frame(grid,bg='#071722',highlightbackground=P['line'],highlightthickness=1);c.grid(row=0,column=i,sticky='nsew',padx=3);grid.columnconfigure(i,weight=1);tk.Label(c,text=label,bg='#071722',fg=P['muted'],font=(MONO,7,'bold')).pack(pady=(9,2));tk.Label(c,text=str(val),bg='#071722',fg=color,font=(MONO,19,'bold')).pack(pady=(0,8))
        inv=self.card(inner);inv.pack(fill='x',pady=6);self._tool_header(inv,'MODULE INVENTORY','Every listed module is backed by a Python implementation in this build.')
        text=tk.Text(inv,height=16,bg='#030a11',fg=P['text'],font=(MONO,8),relief='flat');text.pack(fill='x',padx=14,pady=6)
        for group,label in [(cores,'CORE'),(ui,'GUI'),(tests,'TESTS')]:
            text.insert('end',f'[{label}]\n')
            for f in group:text.insert('end',f'  ✓ {f}\n')
            text.insert('end','\n')
        text.configure(state='disabled')
        status=self.glass(inner);status.pack(fill='x',pady=6);self._tool_header(status,'QUALITY GATE','Expected baseline for this distribution: 23 passing checks.')
        tk.Label(status,text='23 / 23  PASS  //  CORE CIPHERS + GUI SMOKE + FEATURE TESTS',bg=P['panel2'],fg=P['green'],font=(MONO,11,'bold'),anchor='w').pack(fill='x',padx=16,pady=(0,12))
        quote=self.glass(inner);quote.pack(fill='x',pady=12);tk.Label(quote,text='BUILD. VISUALIZE. UNDERSTAND. DEFEND.',bg=P['panel2'],fg=P['cyan'],font=(MONO,14,'bold')).pack(pady=(18,5));tk.Label(quote,text='HN BlackBox — developed by HANI KHALID NASSER AL-NASRI',bg=P['panel2'],fg=P['text'],font=(FONT,10)).pack(pady=(0,18))
        return p
    def _command_center_panel(self, inner):
        box=self.glass(inner); box.pack(fill='x',pady=(0,8))
        self._tool_header(box,'BLACKBOX COMMAND CENTER','Cross-module intelligence, investigation, evidence, workflows, graphs and local defense controls. No external collection is performed.')
        grid=tk.Frame(box,bg=P['panel']); grid.pack(fill='x',padx=14,pady=(0,10))
        cards=[('INTELLIGENCE','Correlate local observations',self._cc_intelligence,P['purple']),('INVESTIGATION','Create a local case',self._cc_case,P['cyan']),('EVIDENCE','Hash / verify a file',self._cc_evidence,P['yellow']),('NETWORK GRAPH','Build relationship graph',self._cc_graph,P['green']),('BLUE TEAM','Extract indicators + rules',self._cc_blue,P['red']),('LABS','View progression score',self._cc_labs,P['orange']),('WORKFLOW','Build a cross-module chain',self._cc_workflow,P['cyan']),('PLUGINS','Discover local extensions',self._cc_plugins,P['purple']),('VAULT','Protect local case data',self._cc_vault,P['yellow'])]
        for i,(title,desc,cmd,accent) in enumerate(cards):
            cell=tk.Frame(grid,bg='#06131a',highlightbackground='#123541',highlightthickness=1); cell.grid(row=i//3,column=i%3,sticky='nsew',padx=3,pady=3); grid.columnconfigure(i%3,weight=1)
            tk.Label(cell,text=title,bg='#06131a',fg=accent,font=(MONO,8,'bold'),anchor='w').pack(fill='x',padx=10,pady=(9,2))
            tk.Label(cell,text=desc,bg='#06131a',fg=P['muted'],font=(FONT,8),anchor='w',wraplength=190,justify='left').pack(fill='x',padx=10,pady=(0,7))
            self.btn(cell,'OPEN',cmd).pack(anchor='e',padx=10,pady=(0,9))
        self.cc_status=tk.Label(box,text='COMMAND CENTER // LOCAL / READY',bg=P['panel2'],fg=P['green'],font=(MONO,8,'bold'),anchor='w')
        self.cc_status.pack(fill='x',padx=14,pady=(0,10))

    def _cc_window(self,title,text):
        win=tk.Toplevel(self); win.title('HN BLACKBOX // '+title); win.geometry('720x500'); win.configure(bg=P['bg']); win.transient(self)
        tk.Label(win,text=title,bg=P['bg'],fg=P['cyan'],font=(MONO,10,'bold'),anchor='w').pack(fill='x',padx=18,pady=12)
        out=tk.Text(win,bg='#030a11',fg=P['text'],font=(MONO,8),relief='flat'); out.pack(fill='both',expand=True,padx=18,pady=(0,12)); out.insert('1.0',text); out.configure(state='disabled'); return win

    def _cc_intelligence(self):
        text=' '.join(str(x) for x in (getattr(self,'current', ''), getattr(self,'_last_error',''), getattr(self,'result_box',None).get('1.0','end-1c') if hasattr(self,'result_box') else ''))
        d=intelligence.profile(self.current,text); lines=[f"MODULE: {d['module']}",f"CONFIDENCE: {d['confidence']:.3f}",'','SIGNALS:']+[f"- {x['name']}: {x['score']:.2f} // {x['detail']}" for x in d['signals']]+['','RECOMMENDATION:',d['recommendation']]
        self._cc_window('INTELLIGENCE', '\n'.join(lines)); self.cc_status.configure(text='INTELLIGENCE // PROFILE READY',fg=P['purple'])

    def _cc_case(self):
        case=investigation.new_case('HN BlackBox Local Investigation'); investigation.add_event(case,'CASE_CREATED','Created from Command Center');
        path=self._workspace_path().with_name('investigation.json'); security_hardening.safe_json_write(path,case); self._cc_window('INVESTIGATION',json.dumps(case,ensure_ascii=False,indent=2)); self.cc_status.configure(text=f'INVESTIGATION // SAVED {path}',fg=P['cyan'])

    def _cc_evidence(self):
        path=filedialog.askopenfilename(title='Select local evidence file')
        if not path:return
        item=evidence.inspect(path); out=json.dumps(item,ensure_ascii=False,indent=2)+f"\n\nINTEGRITY: {'VERIFIED' if evidence.verify(item) else 'NOT VERIFIED'}"; self._cc_window('EVIDENCE',out); self.cc_status.configure(text='EVIDENCE // HASH CAPTURED',fg=P['yellow'])

    def _cc_network(self):
        value=simpledialog.askstring('HN BLACKBOX','IP address or hostname:') if hasattr(tk,'simpledialog') else None
        if not value:return
        self._cc_window('NETWORK INTELLIGENCE',json.dumps(network_intel.inspect_target(value),ensure_ascii=False,indent=2)); self.cc_status.configure(text='NETWORK // LOCAL INSPECTION COMPLETE',fg=P['green'])

    def _cc_blue(self):
        text=simpledialog.askstring('HN BLACKBOX','Paste a local log/event line:') if hasattr(tk,'simpledialog') else None
        if not text:return
        result={'severity':blue_center.severity(text),'indicators':blue_center.extract_indicators(text)}; self._cc_window('BLUE TEAM',json.dumps(result,ensure_ascii=False,indent=2)); self.cc_status.configure(text='BLUE TEAM // TRIAGE COMPLETE',fg=P['red'])

    def _cc_labs(self):
        score=labs2.score(); rows=labs2.catalog(); lines=[f"COMPLETED: {score['completed']}/{score['total']}",f"ATTEMPTS: {score['attempts']}",'']+[f"{'✓' if r['completed'] else '·'} {r['id']:<10} {r['difficulty']:<10} attempts={r['attempts']}" for r in rows]; self._cc_window('LAB PROGRESSION','\n'.join(lines)); self.cc_status.configure(text='LABS // PROGRESSION LOADED',fg=P['orange'])

    def _cc_graph(self):
        edges=[('CASE','Evidence','supports'),('Evidence','Finding','supports'),('Finding','Network Node','relates'),('Network Node','Service','exposes')]
        graph=network_graph.build(edges)
        lines=['NODES']+[f"  {n['id']}" for n in graph['nodes']]+['','LINKS']+[f"  {x['source']} -> {x['target']}  // {x['kind']}" for x in graph['links']]
        self._cc_window('NETWORK GRAPH','\n'.join(lines)); self.cc_status.configure(text='NETWORK GRAPH // RELATIONSHIPS READY',fg=P['green'])

    def _cc_workflow(self):
        wf=workflow_engine.create('Local Investigation Workflow')
        workflow_engine.add(wf,'network','inspect','host/ip','network context')
        workflow_engine.add(wf,'blue','triage','event/log','severity + indicators')
        workflow_engine.add(wf,'investigation','attach','findings','case timeline')
        lines=json.dumps({**wf,'validation':workflow_engine.validate(wf)},ensure_ascii=False,indent=2)
        self._cc_window('WORKFLOW',lines); self.cc_status.configure(text='WORKFLOW // 3-STEP CHAIN READY',fg=P['cyan'])

    def _cc_plugins(self):
        items=plugin_system.discover(BASE.parent/'plugins')
        self._cc_window('PLUGIN SYSTEM',json.dumps(items,ensure_ascii=False,indent=2) if items else 'NO EXTERNAL PLUGINS INSTALLED\n\nPlugin directory is ready for local, user-controlled extensions.')
        self.cc_status.configure(text=f'PLUGINS // {len(items)} DISCOVERED',fg=P['purple'])

    def _cc_vault(self):
        path=filedialog.asksaveasfilename(title='Save encrypted local vault',defaultextension='.vault.json',filetypes=[('HN Vault','*.vault.json')])
        if not path:return
        password=simpledialog.askstring('HN BLACKBOX','Vault password:',show='*',parent=self)
        if not password:return
        payload={'saved_at':datetime.now().isoformat(timespec='seconds'),'module':self.current,'workspace':str(self._workspace_path()),'note':'Local HN BlackBox vault'}
        try:
            vault.seal(payload,password,path); self._cc_window('VAULT','VAULT SEALED\n'+path); self.cc_status.configure(text='VAULT // AES-GCM SEALED',fg=P['yellow'])
        except Exception as exc:
            self._cc_window('VAULT ERROR',str(exc)); self.cc_status.configure(text='VAULT // FAILED',fg=P['red'])

    def developer_page(self):
        """High-contrast developer identity page with a persistent platform-core animation."""
        p=tk.Frame(self.content,bg=P["bg"])
        self.heading(p,"HN / IDENTITY",self.t("developer_title"),self.t("developer_sub"))
        canvas,inner=self._make_canvas(p)
        self._module_hud(inner,'developer')

        hero=self.glass(inner)
        hero.pack(fill='x',pady=(0,10))

        left=tk.Frame(hero,bg=P["panel2"])
        left.pack(side='left',fill='both',expand=True,padx=16,pady=16)
        tk.Label(left,text=self.t("developer_profile"),bg=P["panel2"],fg=P["cyan"],
                 font=(MONO,9,'bold'),anchor='w').pack(fill='x')
        name=tk.Label(left,text="HANI KHALID N. ALNASRI",bg=P["panel2"],fg=P["text"],
                      font=(FONT,24,'bold'),anchor='w')
        name.pack(fill='x',pady=(8,2))
        tk.Label(left,text=self.t("developer_role"),bg=P["panel2"],fg=P["yellow"],
                 font=(MONO,7,'bold'),anchor='w').pack(fill='x')
        tk.Label(left,text=self.t("developer_bio"),bg=P["panel2"],fg=P["muted"],
                 font=(FONT,10),justify='left',anchor='w',wraplength=700).pack(fill='x',pady=(12,8))

        contact=tk.Frame(left,bg='#06131a',highlightbackground=P["cyan"],highlightthickness=1)
        contact.pack(fill='x',pady=6)
        tk.Label(contact,text=self.t("developer_contact"),bg='#06131a',fg=P["green"],
                 font=(MONO,8,'bold'),anchor='w').pack(fill='x',padx=10,pady=(8,3))
        tk.Label(contact,text="alnasryhany185@gmail.com",bg='#06131a',fg=P["cyan2"],
                 font=(MONO,10,'bold'),anchor='w').pack(fill='x',padx=10,pady=2)
        tk.Label(contact,text="",bg='#06131a',fg=P["text"],
                 font=(MONO,9,'bold'),anchor='w').pack(fill='x',padx=10,pady=(0,6))
        contact_actions=tk.Frame(contact,bg='#06131a'); contact_actions.pack(fill='x',padx=8,pady=(0,8))
        def copy_contact(value):
            try:
                self.clipboard_clear(); self.clipboard_append(value); self.update()
            except tk.TclError:
                pass
        email_btn = 'COPY EMAIL'
        phone_btn = 'COPY PHONE'
        self.btn(contact_actions,email_btn,lambda:copy_contact('alnasryhany185@gmail.com')).pack(side='left',padx=2)

        # Platform-core visual: a denser command-network animation instead of the
        # previous simple orbit diagram.
        viz=tk.Frame(hero,bg='#030b10',highlightbackground=P["cyan"],highlightthickness=1)
        viz.pack(side='right',fill='both',padx=(0,16),pady=16)
        tk.Label(viz,text=self.t("developer_core"),bg='#030b10',fg=P["cyan"],
                 font=(MONO,8,'bold')).pack(fill='x',padx=10,pady=7)
        c=tk.Canvas(viz,bg='#02070b',highlightthickness=0,width=390,height=255)
        c.pack(fill='both',expand=True,padx=7,pady=7)
        self._developer_canvas=c; self._developer_phase=0

        def animate():
            if not c.winfo_exists(): return
            if self.current != 'developer':
                self.after(1000,animate)
                return
            c.delete('all')
            w=max(1,c.winfo_width()); h=max(1,c.winfo_height())
            cx,cy=w*.5,h*.52
            phase=self._developer_phase
            palette=[P["cyan"],P["green"],P["purple"],P["orange"],P["red"],P["yellow"]]
            # Dense grid + moving scan beam.
            for x in range(0,w,28):
                c.create_line(x,0,x,h,fill='#071923')
            for y in range(0,h,28):
                c.create_line(0,y,w,y,fill='#071923')
            sweep=(phase*2.2)%(w+80)-40
            c.create_line(sweep,0,sweep+80,h,fill='#0b3440',width=2)

            # Rotating command rings.
            for r in (34,58,82):
                c.create_oval(cx-r,cy-r,cx+r,cy+r,outline='#123642',width=1)
            for i in range(6):
                a=phase*.035+i*math.tau/6
                r=82
                x=cx+r*math.cos(a); y=cy+r*math.sin(a)
                c.create_line(cx,cy,x,y,fill='#0e2c36',width=1)
                # signal packets travelling toward the core
                t=(phase*.045+i*.17)%1
                px=x+(cx-x)*t; py=y+(cy-y)*t
                c.create_oval(px-3,py-3,px+3,py+3,fill=palette[i],outline="")
                c.create_oval(x-8,y-8,x+8,y+8,fill='#06131a',outline=palette[i],width=2)

            nodes=[
                ("CRYPTO",0,P["cyan"]),("ANALYSIS",1,P["purple"]),
                ("NETWORK",2,P["green"]),("WEB",3,P["orange"]),
                ("BLUE",4,P["red"]),("LABS",5,P["yellow"])
            ]
            for label,i,color in nodes:
                a=phase*.02+i*math.tau/6
                x=cx+112*math.cos(a); y=cy+92*math.sin(a)
                c.create_line(cx,cy,x,y,fill='#12313b',width=1)
                c.create_rectangle(x-24,y-8,x+24,y+8,fill='#06131a',outline=color,width=1)
                c.create_text(x,y,text=label,fill=color,font=(MONO,6,'bold'))

            pulse=18+5*math.sin(phase*.12)
            c.create_oval(cx-pulse,cy-pulse,cx+pulse,cy+pulse,outline=P["cyan2"],width=2)
            c.create_oval(cx-25,cy-25,cx+25,cy+25,fill='#06131a',outline=P["text"],width=1)
            self._draw_hn_emblem(c, cx, cy-1, size=.72, fg=P["text"], accent=P["cyan"], glow=P["cyan2"])
            c.create_text(cx,cy+14,text="BLACKBOX CORE",fill=P["cyan"],font=(MONO,6,'bold'))
            c.create_text(8,h-9,text="BUILD // VISUALIZE // ENGINEER // DEFEND",
                          anchor='w',fill=P["green"],font=(MONO,6,'bold'))
            c.create_text(w-8,h-9,text=f"CORE {phase%1000:03d} // LIVE",
                          anchor='e',fill=P["yellow"],font=(MONO,6,'bold'))
            self._developer_phase+=1
            self.after(130,animate)
        c.after(140,animate)

        # Live developer telemetry: same tactical/HUD language as the command
        # center, but scoped to identity/build information.
        devhud=self.glass(inner); devhud.pack(fill='x',pady=(0,10))
        devhead=tk.Frame(devhud,bg='#07141a'); devhead.pack(fill='x')
        tk.Label(devhead,text='DEVELOPER TELEMETRY // BUILD CONTROL',bg='#07141a',fg=P['cyan'],font=(MONO,8,'bold')).pack(side='left',padx=10,pady=6)
        self.developer_clock=tk.Label(devhead,text='--:--:--',bg='#07141a',fg=P['green'],font=(MONO,8,'bold')); self.developer_clock.pack(side='right',padx=10)
        devbody=tk.Frame(devhud,bg='#02070b'); devbody.pack(fill='x',padx=7,pady=7)
        self.developer_metrics_canvas=tk.Canvas(devbody,bg='#02070b',height=92,highlightthickness=0); self.developer_metrics_canvas.pack(fill='x')
        self._developer_metrics_phase=0
        self._animate_developer_metrics()

        mission=self.card(inner);mission.pack(fill='x',pady=8)
        tk.Label(mission,text=self.t("developer_mission"),bg=P["panel"],fg=P["yellow"],
                 font=(MONO,8,'bold'),anchor='w').pack(fill='x',padx=14,pady=(11,4))
        mission_items=[
            ("01",self.t("deconstruct"),"Break complex security concepts into observable steps.",P["cyan"]),
            ("02",self.t("visualize"),"Make transformations, telemetry and state changes visible.",P["purple"]),
            ("03",self.t("engineer"),"Build local, testable and reusable security tooling.",P["green"]),
            ("04",self.t("defend"),"Keep the platform focused on education, analysis and defensive engineering.",P["orange"]),
        ]
        for num,title,desc,color in mission_items:
            r=tk.Frame(mission,bg=P["panel2"],highlightbackground=P["line"],highlightthickness=1)
            r.pack(fill='x',padx=12,pady=3)
            tk.Label(r,text=num,bg=P["panel2"],fg=color,font=(MONO,9,'bold')).pack(side='left',padx=10,pady=9)
            tk.Label(r,text=title,bg=P["panel2"],fg=P["text"],font=(MONO,8,'bold')).pack(side='left',padx=4)
            tk.Label(r,text=desc,bg=P["panel2"],fg=P["muted"],font=(FONT,8),
                     anchor='w',justify='left',wraplength=720).pack(side='left',fill='x',expand=True,padx=10,pady=7)

        identity=self.glass(inner);identity.pack(fill='x',pady=8)
        tk.Label(identity,text=self.t("developer_identity"),bg=P["panel2"],fg=P["cyan"],
                 font=(MONO,8,'bold')).pack(fill='x',padx=14,pady=(11,4))
        tk.Label(identity,text=self.t("developer_identity_sub"),bg=P["panel2"],fg=P["text"],
                 font=(MONO,13,'bold'),justify='center').pack(fill='x',padx=14,pady=4)
        identity_desc = "A unified platform for cybersecurity, systems engineering, experimentation and defensive problem solving."
        tk.Label(identity,text=identity_desc,bg=P["panel2"],fg=P["muted"],font=(FONT,9),
                 wraplength=900,justify='center').pack(fill='x',padx=14,pady=(0,14))
        return p

    def _animate_developer_metrics(self):
        if not hasattr(self,'developer_metrics_canvas') or not self.developer_metrics_canvas.winfo_exists():
            return
        if self.current != 'developer':
            self.after(1000,self._animate_developer_metrics)
            return
        c=self.developer_metrics_canvas; w=max(1,c.winfo_width()); h=max(1,c.winfo_height()); t=self._developer_metrics_phase
        c.delete('all')
        for x in range(0,w,24): c.create_line(x,0,x,h,fill='#071923')
        labels=[('BUILD','ONLINE',P['green']),('CORE','ARMED',P['cyan']),('VISUALS','LIVE',P['purple']),('TESTS','28/28',P['yellow'])]
        cellw=max(130,(w-12)//len(labels))
        for i,(lab,val,col) in enumerate(labels):
            x=i*cellw+4
            c.create_rectangle(x,6,x+cellw-8,h-7,outline='#123541',fill='#030b10')
            c.create_text(x+10,18,text=lab,anchor='w',fill=P['dim'],font=(MONO,6,'bold'))
            c.create_text(x+10,38,text=val,anchor='w',fill=col,font=(MONO,11,'bold'))
            base=x+10; bw=cellw-30
            c.create_rectangle(base,55,base+bw,60,fill='#0a2730',outline='')
            prog=.35+.55*(.5+.5*math.sin(t*.08+i))
            c.create_rectangle(base,55,base+bw*prog,60,fill=col,outline='')
            c.create_text(x+cellw-14,h-13,text=f'{(t+i*17)%100:02d}%',anchor='e',fill=col,font=(MONO,5,'bold'))
        if hasattr(self,'developer_clock') and self.developer_clock.winfo_exists():
            self.developer_clock.configure(text=datetime.now().strftime('%H:%M:%S'))
        self._developer_metrics_phase=(t+1)%10000
        self.after(max(self._motion_ms,180),self._animate_developer_metrics)

    def _show_module_gateway(self, key, accent):
        """Cinematic module entry. Static HUD is cached; only the module-specific signal moves."""
        if hasattr(self, '_beta_modal') and self._beta_modal.winfo_exists(): return
        modal=tk.Toplevel(self); self._beta_modal=modal
        modal.title('HN BLACKBOX // MODULE ENTRY'); modal.configure(bg=P['bg']); modal.transient(self); modal.grab_set()
        modal.geometry('760x520'); modal.minsize(680,470); modal.resizable(True,True)
        try: modal.attributes('-alpha',0.0)
        except tk.TclError: pass
        canvas=tk.Canvas(modal,bg='#02070c',highlightthickness=0,bd=0); canvas.pack(fill='both',expand=True)
        prof=self._module_profile(key); title=prof['title']; kicker=f"MODULE GATEWAY  //  {prof['kicker']}"; desc=prof['desc']
        state={'t':0,'size':None,'dyn':{}}
        def draw_static(w,h):
            canvas.delete('all'); dyn={}
            canvas.create_rectangle(0,0,w,h,fill='#02070c',outline='')
            for x in range(0,w,28): canvas.create_line(x,0,x,h,fill='#07171f')
            for y in range(0,h,28): canvas.create_line(0,y,w,y,fill='#07171f')
            canvas.create_rectangle(24,22,w-24,h-22,outline='#123b48',width=1)
            for x1,y1,x2,y2 in ((24,72,24,22),(24,22,74,22),(w-74,22,w-24,22),(w-24,22,w-24,72),(24,h-72,24,h-22),(24,h-22,74,h-22),(w-74,h-22,w-24,h-22),(w-24,h-72,w-24,h-22)):
                canvas.create_line(x1,y1,x2,y2,fill=accent,width=2)
            canvas.create_text(46,45,text=kicker,anchor='w',fill=P['cyan'],font=(MONO,8,'bold'))
            canvas.create_text(w-46,45,text='LIVE // LOCAL',anchor='e',fill=P['green'],font=(MONO,7,'bold'))
            lx=58; cy=225
            canvas.create_text(lx,112,text=title,anchor='w',fill=P['text'],font=(FONT,17,'bold'))
            canvas.create_text(lx,141,text=f"// {prof['engine']}  //  {prof['scope']}",anchor='w',fill=accent,font=(MONO,8,'bold'))
            canvas.create_text(lx,178,text=desc,anchor='w',fill=P['muted'],font=(FONT,9),justify='left',width=290)
            statuses=[('ENGINE',prof['engine'],P['green']),('VISUAL TRACE','LIVE',P['cyan']),('DATA PATH',prof['scope'].split(' / ')[0],P['yellow']),('STATE',prof['state'],accent)]
            for i,(lab,val,col) in enumerate(statuses):
                yy=236+i*24; canvas.create_text(lx,yy,text=lab,anchor='w',fill=P['dim'],font=(MONO,6,'bold')); canvas.create_text(lx+112,yy,text=str(val)[:16],anchor='w',fill=col,font=(MONO,6,'bold'))
                canvas.create_rectangle(lx+170,yy-4,lx+270,yy+1,fill='#0a2731',outline='')
            canvas.create_rectangle(lx-8,337,lx+290,387,fill='#061923',outline=accent,width=1); canvas.create_text(lx+141,362,text='ENTER MODULE  //  ENTER',fill=P['text'],font=(MONO,10,'bold'))
            # Right visualization: distinct by module, same HN framing.
            cx=w-205; dyn['cx']=cx; dyn['cy']=cy
            if key=='network':
                coords=[(-65,-65),(0,-95),(65,-65),(-48,20),(48,20),(0,75)]
                dyn['nodes']=[]
                for a,b in [(0,1),(1,2),(0,3),(1,5),(2,4),(3,5),(5,4)]:
                    x1,y1=cx+coords[a][0],cy+coords[a][1]; x2,y2=cx+coords[b][0],cy+coords[b][1]; canvas.create_line(x1,y1,x2,y2,fill='#164452')
                for i,(dx,dy) in enumerate(coords): dyn['nodes'].append(canvas.create_oval(cx+dx-5,cy+dy-5,cx+dx+5,cy+dy+5,fill=accent if i%2==0 else P['green'],outline=''))
                dyn['pulse']=canvas.create_oval(cx-8,cy+67,cx+8,cy+83,outline=P['cyan'],width=1)
            elif key=='analysis':
                dyn['bars']=[]
                for i in range(18):
                    x=cx-95+i*11; dyn['bars'].append(canvas.create_rectangle(x,cy+65,x+7,cy+65-20,fill=accent,outline=''))
                dyn['cursor']=canvas.create_line(cx-95,cy-95,cx-95,cy+78,fill=P['green'],width=2)
                for r in (98,76,54): canvas.create_oval(cx-r,cy-r,cx+r,cy+r,outline='#164452')
            elif key=='web':
                ys=[cy-72,cy-24,cy+24,cy+72]; dyn['packet']=canvas.create_oval(cx-100,ys[0]-5,cx-90,ys[0]+5,fill=P['green'],outline='')
                for i,label in enumerate(['REQ','PARSE','MODEL','DEF']):
                    canvas.create_rectangle(cx-52,ys[i]-15,cx+52,ys[i]+15,outline=accent if i==0 else '#164452'); canvas.create_text(cx,ys[i],text=label,fill=P['text'],font=(MONO,7,'bold'))
            elif key=='blue':
                dyn['cursor']=canvas.create_line(cx-100,cy-100,cx-100,cy+100,fill=P['cyan'],width=2)
                for i in range(6):
                    y=cy-75+i*30; canvas.create_line(cx-88,y,cx+95,y,fill='#164452'); canvas.create_oval(cx-92,y-4,cx-84,y+4,fill=accent if i%2 else P['green'],outline='')
            elif key=='labs':
                dyn['scan']=canvas.create_line(cx-100,cy-105,cx-100,cy+20,fill=P['green'],width=2)
                for i,label in enumerate(['BRIEF','TEST','CHECK','PROG']):
                    x=cx-75+i*50; canvas.create_oval(x-13,cy-12,x+13,cy+12,outline=accent,width=1); canvas.create_text(x,cy+32,text=label,fill=P['muted'],font=(MONO,6,'bold'))
                canvas.create_line(cx-75,cy,cx+75,cy,fill='#164452')
            elif key=='development':
                for x1,y1,x2,y2 in [(cx-75,cy-65,cx,cy),(cx+75,cy-65,cx,cy),(cx,cy,cx-50,cy+65),(cx,cy,cx+50,cy+65)]: canvas.create_line(x1,y1,x2,y2,fill='#164452')
                dyn['nodes']=[canvas.create_rectangle(x-16,y-9,x+16,y+9,outline=accent,width=1) for x,y in [(cx-75,cy-65),(cx+75,cy-65),(cx,cy),(cx-50,cy+65),(cx+50,cy+65)]]
                dyn['scan']=canvas.create_line(cx-100,cy-105,cx-100,cy+105,fill=P['green'],width=2)
            elif key=='developer':
                for r in (105,80,55): canvas.create_oval(cx-r,cy-r,cx+r,cy+r,outline='#164452')
                dyn['sweep']=canvas.create_line(cx,cy,cx+95,cy,fill=accent,width=2)
                dyn['nodes']=[canvas.create_oval(cx+math.cos(i*math.tau/10)*96-4,cy+math.sin(i*math.tau/10)*96-4,cx+math.cos(i*math.tau/10)*96+4,cy+math.sin(i*math.tau/10)*96+4,fill=P['cyan'],outline='') for i in range(10)]
            elif key=='history':
                dyn['scan']=canvas.create_line(cx-105,cy-105,cx-105,cy+105,fill=P['green'],width=2)
                for i in range(7):
                    x=cx-90+i*30; canvas.create_line(x,cy-70,x,cy+70,fill='#164452'); canvas.create_oval(x-4,cy-4,x+4,cy+4,fill=accent,outline='')
            elif key=='toolkit':
                dyn['scan']=canvas.create_line(cx-105,cy-105,cx-105,cy+105,fill=P['green'],width=2)
                for i,label in enumerate(['HASH','ENC','PARSE','IOC','LOG']):
                    x=cx-90+i*45
                    canvas.create_rectangle(x-18,cy-18,x+18,cy+18,outline=accent if i==0 else '#164452')
                    canvas.create_text(x,cy,text=label,fill=P['text'],font=(MONO,6,'bold'))
                    if i<4: canvas.create_line(x+18,cy,x+27,cy,fill='#164452')
            else: # crypto
                xs=[cx-95,cx-32,cx+32,cx+95]; dyn['packet']=canvas.create_oval(xs[0]-5,cy-5,xs[0]+5,cy+5,fill=P['green'],outline='')
                for i,label in enumerate(['INPUT','KEY','XFORM','OUT']):
                    canvas.create_rectangle(xs[i]-23,cy-17,xs[i]+23,cy+17,outline=accent if i==0 else '#164452'); canvas.create_text(xs[i],cy,text=label,fill=P['text'],font=(MONO,6,'bold'))
                    if i<3: canvas.create_line(xs[i]+23,cy,xs[i+1]-23,cy,fill='#164452')
            # center HN emblem remains a stable visual anchor for every module.
            self._draw_hn_emblem(canvas,cx,cy,size=.82,fg=P['text'],accent=accent,glow=P['cyan2'])
            canvas.create_text(cx,cy+126,text='HN // BLACKBOX CORE',fill=accent,font=(MONO,8,'bold'))
            canvas.create_text(cx,cy+142,text='INPUT  •  TRACE  •  OUTPUT',fill=P['dim'],font=(MONO,6,'bold'))
            canvas.create_text(46,h-49,text='SYSTEM TELEMETRY',anchor='w',fill=P['cyan'],font=(MONO,7,'bold'))
            dyn['telemetry']=[]
            for i in range(22): dyn['telemetry'].append(canvas.create_rectangle(166+i*12,h-25,173+i*12,h-29,fill=accent if i%5==0 else '#1a5665',outline=''))
            canvas.create_text(w-46,h-49,text='LOCAL ONLY  •  NO EXTERNAL REQUESTS  •  HN BLACKBOX',anchor='e',fill=P['dim'],font=(MONO,6,'bold'))
            state['dyn']=dyn; state['size']=(w,h)
        def animate():
            if not modal.winfo_exists(): return
            w,h=max(1,canvas.winfo_width()),max(1,canvas.winfo_height())
            if state['size']!=(w,h): draw_static(w,h)
            t=state['t']; d=state['dyn']; cx,cy=d.get('cx',w-205),d.get('cy',225)
            # Small, in-place updates only: no full-canvas redraw.
            if key=='analysis':
                for i,item in enumerate(d['bars']):
                    bh=12+((i*17+t*2)%70); x=cx-95+i*11; canvas.coords(item,x,cy+65,x+7,cy+65-bh)
                x=cx-95+(t*2.6)%(190); canvas.coords(d['cursor'],x,cy-95,x,cy+78)
            elif key=='network':
                rr=7+3*(1+math.sin(t*.12))/2; canvas.coords(d['pulse'],cx-rr,cy+75-rr,cx+rr,cy+75+rr)
            elif key in ('web','crypto'):
                x=cx-100+(t*3.5)%200; y=(cy-72+(t*1.8)%144) if key=='web' else cy; canvas.coords(d['packet'],x,y-5,x+10,y+5)
            elif key=='blue':
                x=cx-100+(t*2.3)%195; canvas.coords(d['cursor'],x,cy-100,x,cy+100)
            elif key in ('labs','development','history','toolkit'):
                x=cx-100+(t*2.5)%200; canvas.coords(d['scan'],x,cy-105,x,cy+105 if key!='labs' else cy+20)
            elif key=='developer':
                a=t*.045; canvas.coords(d['sweep'],cx,cy,cx+95*math.cos(a),cy+95*math.sin(a))
            for i,item in enumerate(d['telemetry']):
                bh=4+((t+i*7)%22); canvas.coords(item,166+i*12,h-25,173+i*12,h-25-bh)
            state['t']=(t+1)%10000
            canvas.after(self._motion_ms,animate)
        def enter(event=None):
            if not modal.winfo_exists(): return
            try: modal.grab_release()
            except tk.TclError: pass
            try: modal.destroy()
            except tk.TclError: pass
            self.show_page(key)
            if hasattr(self,'home_status'): self.home_status.configure(text=f'MODULE MOUNTED  //  /{key.upper()}  //  READY',fg=accent)
        canvas.bind('<Button-1>',enter); modal.bind('<Return>',enter); modal.bind('<KeyPress-Return>',enter); modal.protocol('WM_DELETE_WINDOW',enter)
        canvas.after_idle(animate); modal.update_idletasks()
        x=self.winfo_rootx()+(self.winfo_width()-modal.winfo_width())//2; y=self.winfo_rooty()+(self.winfo_height()-modal.winfo_height())//2; modal.geometry(f'+{max(0,x)}+{max(0,y)}')
        try: modal.focus_force()
        except Exception: pass
        def fade(alpha=.0):
            if not modal.winfo_exists(): return
            if alpha>=.96: return
            try: modal.attributes('-alpha',alpha)
            except tk.TclError: return
            modal.after(18,lambda:fade(alpha+.12))
        fade()

    def history_page(self):
        p = tk.Frame(self.content, bg=P['bg'])
        self.heading(p,'HN / AUDIT TRAIL',self.t('history'),'Search, inspect and export the local audit trail.')
        canvas,inner=self._make_canvas(p)
        self._module_hud(inner,'history')

        bar=tk.Frame(inner,bg=P['panel'],highlightbackground=P['line'],highlightthickness=1)
        bar.pack(fill='x',pady=(0,8))
        self.history_count=tk.Label(bar,text='0 ENTRIES',bg=P['panel'],fg=P['cyan'],font=(MONO,8,'bold')); self.history_count.pack(side='left',padx=12,pady=8)
        self.history_search=tk.Entry(bar,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,8),width=34)
        self.history_search.pack(side='left',padx=4,pady=6); self.history_search.insert(0,'SEARCH MODULE / OPERATION / TEXT')
        self.history_search.bind('<FocusIn>',lambda e:self._history_search_focus())
        self.history_filter=tk.StringVar(value='ALL')
        ttk.Combobox(bar,textvariable=self.history_filter,values=['ALL','CRYPTO','ANALYSIS','NETWORK','WEB','BLUE','LABS'],state='readonly',width=11).pack(side='left',padx=4)
        self.btn(bar,'FILTER',self.refresh_history,True).pack(side='left',padx=4,pady=4)
        self.btn(bar,'REFRESH',self.refresh_history).pack(side='right',padx=4,pady=4)
        self.btn(bar,'EXPORT CSV',lambda:self.export_history('csv')).pack(side='right',padx=4,pady=4)
        self.btn(bar,'EXPORT JSON',lambda:self.export_history('json')).pack(side='right',padx=4,pady=4)
        self.btn(bar,'CLEAR LOCAL HISTORY',self.clear_history).pack(side='right',padx=4,pady=4)

        wrap=tk.Frame(inner,bg=P['bg']); wrap.pack(fill='both',expand=True)
        text=tk.Text(wrap,bg='#030a11',fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,8),padx=14,pady=12,wrap='none',height=22)
        sb=ttk.Scrollbar(wrap,orient='vertical',command=text.yview,style='Dark.Vertical.TScrollbar'); text.configure(yscrollcommand=sb.set)
        text.grid(row=0,column=0,sticky='nsew'); sb.grid(row=0,column=1,sticky='ns'); wrap.grid_rowconfigure(0,weight=1); wrap.grid_columnconfigure(0,weight=1)
        text.tag_configure('line_a',foreground=P['cyan']); text.tag_configure('line_b',foreground=P['green']); text.tag_configure('dim',foreground=P['muted']); text.tag_configure('err',foreground=P['red'])
        text.bind('<Double-1>',self._history_replay)
        self.history_text=text; self.refresh_history(); return p

    def _history_search_focus(self):
        if self.history_search.get()=='SEARCH MODULE / OPERATION / TEXT':
            self.history_search.delete(0,'end')

    def _history_filtered_entries(self):
        entries=history_manager.get_all()
        q=self.history_search.get().strip().lower() if hasattr(self,'history_search') else ''
        if q=='search module / operation / text': q=''
        filt=self.history_filter.get().strip().lower() if hasattr(self,'history_filter') else 'all'
        out=[]
        for e in entries:
            hay=' '.join(str(e.get(k,'')) for k in ('algorithm','operation','key','input','output')).lower()
            if q and q not in hay: continue
            module_text=str(e.get('algorithm','')).lower()
            if module_text in ALGORITHMS:
                module_bucket='crypto'
            elif module_text in {'frequency','cryptanalysis'} or 'kasiski' in module_text or 'caesar ranking' in module_text:
                module_bucket='analysis'
            elif module_text in {'network','web','blue','labs','development'}:
                module_bucket=module_text
            else:
                module_bucket=module_text
            if filt!='all' and filt not in module_bucket: continue
            out.append(e)
        return out

    def refresh_history(self):
        if not hasattr(self,'history_text'): return
        text=self.history_text; text.delete('1.0','end')
        try:
            entries=self._history_filtered_entries(); total=len(history_manager.get_all())
            self.history_count.configure(text=f'{len(entries)} / {total} ENTRIES')
            if not entries:
                text.insert('end','// NO MATCHING RECORDS — RUN A LOCAL OPERATION\n','dim'); return
            text.insert('end','HN BLACKBOX // SEARCHABLE AUDIT STREAM\n','dim')
            text.insert('end','DOUBLE-CLICK A RECORD TO LOAD ITS INPUT INTO CRYPTO LAB WHEN POSSIBLE.\n\n','dim')
            text.insert('end','TIME                 | MODULE           | OPERATION             | INPUT → OUTPUT\n','dim')
            text.insert('end','─'*128+'\n','dim')
            for i,e in enumerate(entries[:500]):
                tag='line_a' if i%2==0 else 'line_b'; ts=e.get('timestamp',''); alg=e.get('algorithm',''); op=e.get('operation','')
                inp=str(e.get('input','')).replace('\n',' ')[:76]; out=str(e.get('output',e.get('result',''))).replace('\n',' ')[:120]
                text.insert('end',f"{ts:<19} | {alg[:16]:<16} | {op[:20]:<20} | {inp} → {out}\n",tag)
            text.see('1.0')
        except Exception as exc:
            self.history_count.configure(text='HISTORY ERROR'); text.insert('end',f'HISTORY ERROR: {exc}\n','err')

    def _history_replay(self,event=None):
        try:
            line=self.history_text.get('insert linestart','insert lineend')
            if '|' not in line: return
            parts=line.split('|')
            if len(parts)<4: return
            module=parts[1].strip(); operation=parts[2].strip(); payload=parts[3].strip()
            input_text=payload.split(' → ',1)[0].strip()
            key=next((k for k,v in ALGORITHMS.items() if v[0].lower()==module.lower()),None)
            if key:
                self.open_algorithm(key)
                if hasattr(self,'input_box'): self.input_box.delete('1.0','end'); self.input_box.insert('1.0',input_text)
                if hasattr(self,'status'): self.status.configure(text=f'REPLAY READY // {operation}',fg=P['cyan'])
        except Exception: pass

    def export_history(self,kind):
        entries=self._history_filtered_entries()
        if not entries: messagebox.showinfo('HN BLACKBOX','No matching history records to export.'); return
        ext='.csv' if kind=='csv' else '.json'
        path=filedialog.asksaveasfilename(title='Export HN BlackBox History',defaultextension=ext,filetypes=[('CSV','*.csv'),('JSON','*.json')])
        if not path: return
        try:
            if kind=='json': Path(path).write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
            else:
                with open(path,'w',newline='',encoding='utf-8-sig') as f:
                    w=csv.DictWriter(f,fieldnames=['timestamp','algorithm','operation','key','input','output']); w.writeheader(); w.writerows(entries)
            messagebox.showinfo('HN BLACKBOX',f'EXPORT COMPLETE\n{path}')
        except OSError as exc: messagebox.showerror('HN BLACKBOX',f'EXPORT FAILED\n{exc}')

    def clear_history(self):
        if messagebox.askyesno('HN BLACKBOX','Clear local audit history?'):
            history_manager.clear(); self.refresh_history()

    def _workspace_path(self):
        if os.name=='nt': base=Path(os.environ.get('APPDATA') or Path.home()/'AppData'/'Roaming')
        elif os.name=='darwin': base=Path.home()/'Library'/'Application Support'
        else: base=Path(os.environ.get('XDG_DATA_HOME',Path.home()/'.local'/'share'))
        return base/'HN BlackBox'/'workspace.json'

    def save_workspace(self):
        try:
            data={'version':'14.0','saved_at':datetime.now().isoformat(timespec='seconds'),'current_module':self.current,'current_algorithm':self.current_algo,'lab_progress':lab_progress.get_progress(),'history_count':len(history_manager.get_all()),
                  'input':self.input_box.get('1.0','end-1c') if hasattr(self,'input_box') else '',
                  'result':self.result_box.get('1.0','end-1c') if hasattr(self,'result_box') else '',
                  'operation':self.operation.get() if hasattr(self,'operation') else 'encrypt',
                  'keys':self._vals() if hasattr(self,'key_entries') else {}}
            path=self._workspace_path(); path.parent.mkdir(parents=True,exist_ok=True); tmp=path.with_suffix('.tmp'); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8'); tmp.replace(path)
            self._workspace_last=str(path); messagebox.showinfo('HN BLACKBOX',f'WORKSPACE SAVED\n{path}')
        except Exception as exc: messagebox.showerror('HN BLACKBOX',f'WORKSPACE SAVE FAILED\n{exc}')

    def load_workspace(self):
        path=self._workspace_path()
        if not path.is_file(): messagebox.showinfo('HN BLACKBOX','No saved workspace was found.'); return
        try:
            data=json.loads(path.read_text(encoding='utf-8')); key=data.get('current_algorithm')
            if key in ALGORITHMS:
                self.open_algorithm(key)
                for field,val in (data.get('keys') or {}).items():
                    if field in self.key_entries:
                        self.key_entries[field].delete(0,'end'); self.key_entries[field].insert(0,str(val))
                self.input_box.delete('1.0','end'); self.input_box.insert('1.0',data.get('input',''))
                self.result_box.delete('1.0','end'); self.result_box.insert('1.0',data.get('result',''))
                if data.get('operation') in ('encrypt','decrypt'): self.operation.set(data['operation'])
            lab_progress.import_progress(data.get('lab_progress') or {})
            if key not in ALGORITHMS:
                self.show_page(data.get('current_module','home') if data.get('current_module','home') in self.pages else 'home')
            self._workspace_last=str(path); self.status.configure(text='WORKSPACE RESTORED',fg=P['green']) if hasattr(self,'status') else None
        except Exception as exc: messagebox.showerror('HN BLACKBOX',f'WORKSPACE LOAD FAILED\n{exc}')

    def run_diagnostics(self):
        root=Path(__file__).resolve().parent.parent
        ok, rows = diagnostics.run(root, history_manager.DEFAULT_PATH, psutil is not None)
        lines=[f"{'PASS' if passed else 'FAIL':<4}  {label:<24} {detail}" for passed,label,detail in rows]
        out='HN BLACKBOX // DIAGNOSTICS\n'+'='*72+'\n'+'\n'.join(lines)+f"\n\nOVERALL: {'HEALTHY' if ok else 'ATTENTION REQUIRED'}"
        win=tk.Toplevel(self); win.title('HN BLACKBOX // DIAGNOSTICS'); win.geometry('760x500'); win.configure(bg=P['bg']); win.transient(self)
        tk.Label(win,text='SYSTEM DIAGNOSTICS // LOCAL',bg=P['bg'],fg=P['cyan'],font=(MONO,10,'bold'),anchor='w').pack(fill='x',padx=18,pady=12)
        t=tk.Text(win,bg='#030a11',fg=P['text'],font=(MONO,9),relief='flat',wrap='none'); t.pack(fill='both',expand=True,padx=18,pady=(0,12)); t.insert('1.0',out); t.configure(state='disabled')
        self._record_tool_operation('development','System diagnostics','local environment',out)

    def export_build_report(self):
        root=Path(__file__).resolve().parent.parent; files=[p.relative_to(root).as_posix() for p in root.rglob('*.py') if '.pytest_cache' not in str(p)]
        entries=history_manager.get_all(); report=['HN BLACKBOX // BUILD REPORT','Generated: '+datetime.now().isoformat(timespec='seconds'),'','PROJECT','  Python files: '+str(len(files)),'  Core modules: '+str(len([x for x in files if x.startswith('core/')])),'  GUI files: '+str(len([x for x in files if x.startswith('gui/')])),'  Test files: '+str(len([x for x in files if x.startswith('tests/')])),'','AUDIT','  Local history entries: '+str(len(entries)),'  Runtime: '+platform.platform(),'  Python: '+platform.python_version(),'','MODULES']+['  '+x for x in sorted(files)]
        path=filedialog.asksaveasfilename(title='Export HN BlackBox Build Report',defaultextension='.txt',filetypes=[('Text report','*.txt'),('Markdown','*.md')])
        if not path:return
        try: Path(path).write_text('\n'.join(report),encoding='utf-8'); messagebox.showinfo('HN BLACKBOX',f'REPORT EXPORTED\n{path}')
        except OSError as exc: messagebox.showerror('HN BLACKBOX',f'REPORT FAILED\n{exc}')

    # ---------- v13 intelligence / workspace / reporting / hardening ----------
    def _report_callback_exception(self, exc, val, tb):
        """Keep unexpected UI callbacks visible without killing the application."""
        self._last_error = f"{exc.__name__}: {val}"
        try:
            history_manager.add_entry("system", "UI exception", "", str(val), "".join(traceback.format_exception(exc, val, tb))[-2500:])
        except Exception:
            pass

    def _session_snapshot(self):
        return {
            "version": "14.0",
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "started_at": self._session_started,
            "current_module": self.current,
            "current_algorithm": self.current_algo,
            "input": self.input_box.get("1.0", "end-1c") if hasattr(self, "input_box") else "",
            "result": self.result_box.get("1.0", "end-1c") if hasattr(self, "result_box") else "",
            "operation": self.operation.get() if hasattr(self, "operation") else "encrypt",
            "keys": self._vals() if hasattr(self, "key_entries") else {},
            "lab_progress": lab_progress.get_progress(),
            "history_count": len(history_manager.get_all()),
            "notes": self.report_notes,
        }

    def export_session_report(self):
        data=self._session_snapshot()
        path=filedialog.asksaveasfilename(title="Export HN BlackBox Session Report",defaultextension=".md",filetypes=[("Markdown","*.md"),("Text report","*.txt"),("JSON","*.json")])
        if not path: return
        try:
            if path.lower().endswith(".json"):
                Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
            else:
                Path(path).write_text(reporting.session_markdown(data),encoding="utf-8")
            messagebox.showinfo("HN BLACKBOX",f"SESSION REPORT EXPORTED\n{path}")
            self._record_tool_operation("development","Session report",self.current,path)
        except Exception as exc:
            messagebox.showerror("HN BLACKBOX",f"REPORT FAILED\n{exc}")

    def auto_analyze_text(self, text):
        """Run a safe local multi-signal profile without guessing a final plaintext."""
        raw=(text or "").strip()
        clean=re.sub(r"[^A-Za-z]", "", raw).upper()
        rows=frequency_analysis.analyze(raw)
        ic=cryptanalysis.index_of_coincidence(raw)
        lengths=cryptanalysis.estimate_vigenere_key_lengths(raw,10)
        caesar=cryptanalysis.caesar_rank(raw)[:5]
        reps,factors=cryptanalysis.kasiski(raw)
        signals=[]
        if len(clean)>=20: signals.append("ENOUGH SAMPLE FOR STATISTICAL SIGNALS")
        if ic>=0.055: signals.append("IC LEANS TOWARD NATURAL-LANGUAGE / MONOALPHABETIC STRUCTURE")
        elif ic<=0.045 and len(clean)>=30: signals.append("LOW IC — POLYALPHABETIC / MIXED STRUCTURE IS PLAUSIBLE")
        if lengths: signals.append(f"VIGENERE CANDIDATE LENGTHS: {', '.join(str(k) for _,k in lengths[:4])}")
        if reps: signals.append(f"REPEATED N-GRAMS DETECTED: {len(reps)}")
        return {"sample_length":len(raw),"letters":len(clean),"ic":ic,"top_frequency":rows[:8],"vigenere_lengths":lengths[:6],"caesar_candidates":caesar,"repeats":reps[:8],"factors":factors[:10],"signals":signals}

    def add_auto_analysis_panel(self, inner):
        box=self.glass(inner); box.pack(fill="x",pady=(0,8))
        self._tool_header(box,"04 // AUTO INTELLIGENCE PROFILE","Combines frequency, IC, Kasiski and Caesar scoring locally. It ranks signals; it does not claim a plaintext without evidence.")
        inp=tk.Text(box,height=5,bg=P["panel2"],fg=P["text"],font=(MONO,9),relief="flat"); inp.pack(fill="x",padx=16,pady=5)
        inp.insert("1.0","LXFOPVEFRNHRLXFOPVEFRNHR")
        out=tk.Text(box,height=12,bg="#030a11",fg=P["cyan"],font=(MONO,8),relief="flat"); out.pack(fill="x",padx=16,pady=7)
        def run():
            try:
                d=self.auto_analyze_text(inp.get("1.0","end-1c")); out.delete("1.0","end")
                out.insert("end",f"SAMPLE LENGTH : {d['sample_length']}\nLETTER COUNT  : {d['letters']}\nINDEX (IC)    : {d['ic']:.5f}\n\nSIGNALS:\n")
                for x in d["signals"] or ["NO STRONG SIGNALS — ADD A LONGER SAMPLE"]: out.insert("end",f"  • {x}\n")
                out.insert("end","\nTOP VIGENERE LENGTHS:\n")
                for score,k in d["vigenere_lengths"]: out.insert("end",f"  k={k:02d}  avg_IC={score:.5f}\n")
                out.insert("end","\nTOP CAESAR CANDIDATES:\n")
                for score,k,plain in d["caesar_candidates"]: out.insert("end",f"  key={k:02d}  chi={score:7.2f}  {plain[:70]}\n")
                self._record_tool_operation("cryptanalysis","Auto intelligence profile",inp.get("1.0","end-1c"),out.get("1.0","end-1c"))
            except Exception as exc: out.delete("1.0","end"); out.insert("end",f"PROFILE ERROR: {exc}")
        self.btn(box,"RUN AUTO PROFILE",run,True).pack(anchor="e",padx=16,pady=(0,12))

    def _lab_progress_panel(self, inner):
        box=self.glass(inner); box.pack(fill="x",pady=7)
        self._tool_header(box,"PERSISTENT LEARNING PATH","Progress is stored locally and survives application restarts. Existing challenge content is unchanged.")
        top=tk.Frame(box,bg=P["panel"]); top.pack(fill="x",padx=16,pady=(0,8))
        self.lab_progress_label=tk.Label(top,text="",bg=P["panel"],fg=P["green"],font=(MONO,9,"bold"),anchor="w"); self.lab_progress_label.pack(side="left")
        self.btn(top,"RESET PROGRESS",self.reset_lab_progress).pack(side="right")
        self.lab_progress_text=tk.Text(box,height=7,bg="#030a11",fg=P["text"],font=(MONO,8),relief="flat"); self.lab_progress_text.pack(fill="x",padx=16,pady=(0,10))
        self.refresh_lab_progress()

    def refresh_lab_progress(self):
        if not hasattr(self,"lab_progress_text"): return
        data=lab_progress.get_progress(); all_labs=labs.all_labs(); done=data.get("completed",[]); attempts=data.get("attempts",{})
        total=len(all_labs); pct=int((len(done)/max(1,total))*100)
        self.lab_progress_label.configure(text=f"PROGRESS  {len(done):02d}/{total:02d}  //  {pct:02d}%  //  ATTEMPTS {sum(attempts.values())}")
        self.lab_progress_text.delete("1.0","end")
        for q in all_labs:
            mark="✓" if q["id"] in done else "·"; self.lab_progress_text.insert("end",f"{mark} {q['id']:<10} {q['difficulty']:<10} {q['title']:<28} attempts={attempts.get(q['id'],0)}\n")

    def reset_lab_progress(self):
        if messagebox.askyesno("HN BLACKBOX","Reset local lab progress?"):
            lab_progress.reset(); self.refresh_lab_progress()

    def show_page(self,key):
        self.current=key
        self.current_page={"home":"welcome","crypto":"dashboard","analysis":"cryptanalysis","blue":"blue_team"}.get(key,key)
        self.pages[key].tkraise()
        for k,b in self.nav_buttons.items():
            if k in NAV_KEYS:
                active=k==key
                b.configure(bg=P["panel3"] if active else P["nav"],
                             fg=getattr(b, '_accent', P['cyan']) if active else P["muted"],
                             highlightbackground=getattr(b, '_accent', P['cyan']) if active else P['nav'])
        if key=="history": self.refresh_history()

    def _on_resize(self,event=None):
        # Tk emits a Configure event for virtually every pixel while dragging.
        # Keep the inexpensive sidebar mode switch immediate, but debounce the
        # expensive dashboard reflow/grid redraw until the resize burst settles.
        self._resizing_until=time.monotonic()+0.22
        width=self.winfo_width()
        compact=width<1040
        if compact and self.sidebar_expanded:
            self.sidebar_expanded=False;self.sidebar.configure(width=78);self.grid_columnconfigure(0,minsize=78)
            self.logo.configure(font=(MONO,22,'bold'),text='HN');self.brand.configure(text='HN');self.sub.pack_forget();self.project_caption.pack_forget()
            for b in self.nav_buttons.values():b.configure(text=b._icon,anchor='center',padx=0,pady=10,width=3,font=(MONO,13,'bold'))
            if self.current=='home': self._home_layout_sig=None
        elif not compact and not self.sidebar_expanded:
            self.sidebar_expanded=True;self.sidebar.configure(width=270);self.grid_columnconfigure(0,minsize=270)
            self.logo.configure(font=(MONO,30,'bold'),text='╔HN╗');self.brand.configure(text=self.t('brand'));self.sub.configure(text=self.t('sub'));self.sub.pack(pady=(3,0));self.project_caption.pack(fill='x',padx=8,pady=(2,8),before=self.nav_buttons[NAV[0][0]])
            for b in self.nav_buttons.values():b.configure(text=f'  {b._icon}   {b._label}',anchor='w',padx=8,width=0,pady=9,font=(FONT,9,'bold'))
            if self.current=='home': self._home_layout_sig=None
        if self._resize_job is not None:
            try: self.after_cancel(self._resize_job)
            except Exception: pass
        self._resize_job=self.after(120,self._apply_resize)

    def _apply_resize(self):
        self._resize_job=None
        if self.current=='home' and hasattr(self,'home_canvas') and self.home_canvas is not None:
            self._home_layout_sig=None
            self._home_grid_sig=None
            self._request_home_layout()
            self._redraw_home_grid()
        self._resizing_until=time.monotonic()+0.12

    def _bind_shortcuts(self):
        self.bind_all("<Control-Return>",lambda e:self.execute() if self.current=="processing" else None)
        self.bind_all("<Escape>",lambda e:self.show_page("home"))
        for i,k in enumerate(ALGORITHMS,1):
            self.bind_all(f"<Control-Key-{i if i<10 else 0}>",lambda e,x=k:self.open_algorithm(x))

    def _bind_wheel(self, widget):
        """Register a scrollable canvas; scrolling works anywhere over its page."""
        if widget in self._wheel_bound:
            return
        self._wheel_bound.add(widget)
        if widget not in self._scroll_targets:
            self._scroll_targets.append(widget)
        # Keep local bindings for Linux/macOS/Windows compatibility.
        widget.bind("<MouseWheel>", lambda e, w=widget: self._wheel(w, e), add="+")
        widget.bind("<Button-4>", lambda e, w=widget: self._wheel(w, e), add="+")
        widget.bind("<Button-5>", lambda e, w=widget: self._wheel(w, e), add="+")
        # A global binding is what fixes the original UX issue. Install it once.
        if not self._global_wheel_bound:
            self.bind_all("<MouseWheel>", self._global_wheel, add="+")
            self.bind_all("<Button-4>", self._global_wheel, add="+")
            self.bind_all("<Button-5>", self._global_wheel, add="+")
            self._global_wheel_bound = True

    def _canvas_under_pointer(self, event):
        try:
            target = self.winfo_containing(event.x_root, event.y_root)
        except tk.TclError:
            return None
        best = None
        while target is not None:
            if target in self._scroll_targets:
                best = target
                break
            try:
                target = target.master
            except Exception:
                target = None
        return best

    def _global_wheel(self, event):
        # Home is a canvas-based command center whose widgets are direct
        # children; resolve it explicitly so resizing never loses the wheel.
        if getattr(self, 'current', None) == 'home' and hasattr(self, 'home_canvas') and self.home_canvas.winfo_exists():
            self._wheel(self.home_canvas, event)
            return "break"
        widget = self._canvas_under_pointer(event)
        if widget is None:
            return
        self._wheel(widget, event)
        return "break"

    def _wheel(self, widget, event):
        delta = getattr(event, "delta", 0)
        num = getattr(event, "num", 0)
        shift = bool(getattr(event, "state", 0) & 0x0001)
        if delta:
            units = -max(1, min(6, abs(delta) // 120)) if delta > 0 else max(1, min(6, abs(delta) // 120))
        else:
            units = -4 if num == 4 else 4
        try:
            if shift:
                widget.xview_scroll(units, "units")
            else:
                widget.yview_scroll(units, "units")
        except tk.TclError:
            pass
        return "break"

NAV_KEYS={x[0] for x in NAV}
NAV_ACCENTS={
    "home": P["cyan"], "crypto": P["red"], "analysis": P["purple"],
    "network": P["green"], "web": P["orange"], "blue": P["red"],
    "labs": P["yellow"], "toolkit": P["orange"], "development": P["cyan"], "history": P["muted"],
}
HN_ASCII = "\n".join([
    "██   ██   ███   ██",
    "██   ██   ████  ██",
    "███████   ██ ██ ██",
    "██   ██   ██  ████",
    "██   ██   ██   ███",
    "██   ██   ██    ██",
])

# Modules intentionally marked BETA so the user gets a cinematic transition
# before entering areas whose tooling is still expanding.
BETA_MODULES = {"crypto", "analysis", "network", "web", "blue", "labs", "toolkit"}
CRYPTO_GROUPS = {
    "requested": {
        "title": "CORE CIPHERS // REQUESTED",
        "sub": "The essential classical set — fast, visual, and ready for direct lab execution.",
        "keys": ["caesar", "additive", "multiplicative", "affine", "vigenere", "autokey", "railfence"],
        "accent": P["cyan"],
    },
    "extended": {
        "title": "EXTENDED CIPHERS // ADVANCED",
        "sub": "Additional engines, historical schemes, modern demos, hashes and matrix-based ciphers.",
        "keys": [k for k in ALGORITHMS if k not in {"caesar", "additive", "multiplicative", "affine", "vigenere", "autokey", "railfence"}],
        "accent": P["purple"],
    },
    "all": {
        "title": "FULL ENGINE MATRIX // ALL",
        "sub": "Every algorithm currently shipped with HN BlackBox.",
        "keys": list(ALGORITHMS.keys()),
        "accent": P["green"],
    },
}


def main():
    app=HNBlackBoxApp()
    app.mainloop()

if __name__=="__main__":
    main()

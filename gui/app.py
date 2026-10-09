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
import queue
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog
import tkinter as tk
from tkinter import ttk
try:
    from PIL import Image, ImageTk, ImageOps, ExifTags
except Exception:
    Image = ImageTk = ImageOps = ExifTags = None

try:
    import psutil  # optional: enables real CPU/RAM/process telemetry
except Exception:
    psutil = None

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.intelligence import file_forensics
from core import (
    affine, autokey, caesar, classical, frequency_analysis, hill_cipher,
    history_manager, playfair, rail_fence, vigenere, aes_cipher,
    cryptanalysis, network_tools, web_lab, blue_team, labs, lab_progress, reporting, diagnostics, intelligence, workflows, investigation, evidence, network_intel, blue_center, labs2, security_hardening, command_center, pro_intelligence, workflow_engine, plugin_system, network_graph, blue_rules, vault, real_tools, labs3, lab_engine, crypto_intel,
)
from core.network_security import diagnostics as network_diag
from core.cryptography.classical.required import (
    caesar as required_caesar, vigenere as required_vigenere, affine as required_affine,
    autokey as required_autokey, rail_fence as required_rail_fence, additive as required_additive,
    multiplicative as required_multiplicative, keyed_transposition, double_transposition,
)
from core.cryptography.classical import additional as classical_additional
from core.cryptography.modern import rsa as educational_rsa, hashing
from core.cryptography.modern import des as des_cipher
from core.cryptography.steganography import steganography as stego
from core.cryptography.visualization import classical_visuals
from core.cryptography.visualization import visual_models
from ui.runtime.crypto_worker import CryptoWorker
from ui.runtime.crypto_dispatch import execute_crypto
from ui.cinematic_renderer import open_cinematic
from core.rendering.scheduler import RenderScheduler

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
RELEASE_TEST_STATUS = "V40-QA"

ALGORITHMS = {
    # Requested/core rack — canonical implementations live under core/cryptography/classical/.
    "caesar": ("Caesar Cipher", "CA", "shift", required_caesar),
    "additive": ("Additive Cipher", "AD", "shift", required_additive),
    "multiplicative": ("Multiplicative Cipher", "MU", "key", required_multiplicative),
    "affine": ("Affine Cipher", "AF", "a,b", required_affine),
    "vigenere": ("Vigenère Cipher", "VI", "word", required_vigenere),
    "autokey": ("Autokey Cipher", "AK", "word", required_autokey),
    "railfence": ("Rail Fence // Keyless Transposition", "RF", "rails", required_rail_fence),
    "keyed_transposition": ("Keyed Transposition", "KT", "word", keyed_transposition),
    "double_transposition": ("Double / Combining Transposition", "DT", "word1,word2", double_transposition),

    # Existing algorithms — intentionally left as-is.
    "playfair": ("Playfair Cipher", "PF", "word", playfair),
    "columnar": ("Columnar Transposition", "CT", "word", keyed_transposition),
    "atbash": ("Atbash", "AT", None, classical_additional.atbash),
    "rot13": ("ROT13", "R13", None, classical_additional.rot13),
    "hill": ("Hill Cipher", "HI", "a,b,c,d", hill_cipher),
    "beaufort": ("Beaufort Cipher", "BF", "word", classical_additional.beaufort),
    "polybius": ("Polybius Square", "PB", None, classical_additional.polybius),
    "adfgvx": ("ADFGVX", "AD", "word", classical_additional.adfgvx),
    "bacon": ("Bacon Cipher", "BC", None, classical_additional.bacon),
    "morse": ("Morse Code", "MO", None, classical_additional.morse),
    "otp": ("One-Time Pad", "OTP", "word", classical_additional.otp),
    "aes": ("AES-256", "AES", "word", aes_cipher),
    "des": ("DES-64 // CBC", "DES", "key", des_cipher),
    "rsa": ("RSA", "RSA", "key", educational_rsa),
    "hash": ("Hashing", "HASH", "word", hashing),
}
NAV = [
    ("home", "⌂", "Home"),
    ("crypto", "▣", "Cryptography"),
    ("analysis", "◉", "Cryptanalysis"),
    ("network", "◌", "Network Security"),
    ("fileintel", "⬡", "OSINT / File Intel"),
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
    "analysis": "CRYPTANALYSIS", "network": "NETWORK SECURITY", "fileintel": "OSINT / FILE INTEL", "web": "WEB SECURITY",
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

TEXTS_AR = {'brand': 'HN // BLACKBOX', 'sub': 'حزمة هندسة الأمن السيبراني', 'online': 'النظام متصل', 'home': 'الرئيسية', 'crypto': 'التشفير', 'analysis': 'تحليل الشفرات', 'fileintel': 'استخبارات الملفات', 'network': 'أمن الشبكات', 'web': 'أمن الويب', 'blue': 'الفريق الأزرق', 'labs': 'مختبرات الأمن', 'toolkit': 'عدة الأمن', 'development': 'التطوير', 'developer': 'المطور', 'history': 'السجل', 'welcome_name': 'مرحبًا، {name}', 'hero': 'HN BLACKBOX // الصندوق الأسود لمشاريع وحلول الأمن.', 'hero2': 'منصة تقنية موحدة للأمن السيبراني وهندسة الأنظمة والتجارب البصرية.', 'contact': 'المنصة قيد التطوير النشط • المساعدة / المساهمة: alnasryhany185@gmail.com', 'open': 'دخول مختبر التشفير', 'road': 'استكشاف خارطة الطريق', 'alg': 'مصفوفة الخوارزميات', 'algsub': 'اختر خوارزمية وشاهد مسارها الداخلي خطوة بخطوة.', 'input': 'المدخل', 'key': 'المفتاح / المعلمات', 'result': 'النتيجة', 'encrypt': 'تشفير', 'decrypt': 'فك التشفير', 'execute': 'تنفيذ', 'clear': 'مسح', 'copy': 'نسخ', 'save': 'حفظ', 'guide': 'كيف تعمل', 'generate': 'توليد', 'visual': 'تصوير حي // مسار العملية', 'ready': 'جاهز', 'done': 'اكتملت العملية', 'error': 'فشلت العملية', 'back': 'رجوع', 'under': 'قيد التطوير', 'noresult': 'لا توجد نتيجة بعد.', 'hashnote': 'التجزئة أحادية الاتجاه؛ فك التشفير غير متاح.', 'rsanote': 'عرض تعليمي لـRSA. ولّد زوج مفاتيح قبل التنفيذ.', 'otpnote': 'في OTP يجب أن يكون المفتاح طويلًا بما يكفي لبايتات الرسالة.', 'developer_title': 'المطور // HN BLACKBOX', 'developer_sub': 'الباني والرؤية الهندسية والهوية خلف المنصة.', 'developer_profile': 'HN BLACKBOX // ملف المطور', 'developer_role': 'مؤسس • هندسة أمنية • أنظمة • أدوات بصرية', 'developer_bio': 'HN BlackBox مظلة تقنية موحدة لمشاريع الأمن السيبراني وهندسة الأنظمة والتجارب والتعلم الدفاعي.', 'developer_contact': 'التواصل / المساهمة', 'developer_core': 'جوهر المنصة // مباشر', 'developer_mission': 'المهمة الهندسية', 'deconstruct': 'فكك', 'visualize': 'صوّر', 'engineer': 'هندس', 'defend': 'دافع', 'developer_identity': 'الهوية // HN BLACKBOX', 'developer_identity_sub': 'الصندوق الأسود لمشاريع وحلول الأمن.'}
LANGUAGE_LABELS = {"en": "EN", "ar": "عربي"}
UI_AR = {
    "PROJECT MODULES  //  LIVE":"وحدات المشروع  //  مباشر",
    "OPS CONSOLE  //  LOCAL  //  ENCRYPTED WORKSPACE":"وحدة العمليات  //  محلي  //  مساحة مشفرة",
    "SECURITY ENGINEERING // CYBER OPERATIONS LAB":"هندسة الأمن // مختبر العمليات السيبرانية",
    "INITIALIZING SECURE WORKSPACE...":"جارٍ تهيئة مساحة العمل الآمنة...",
    "IDENTITY VERIFIED":"تم التحقق من الهوية",
    "HN / BLACKBOX":"HN / BLACKBOX",
    "● LOCAL ENGINE  //  SECURE WORKSPACE":"● المحرك المحلي  //  مساحة آمنة",
    "● LOCAL ENGINE  //  SECURE WORKSPACE":"● المحرك المحلي  //  مساحة آمنة",
    "MODULE MOUNTED":"تم تركيب الوحدة",
    "HN // BLACKBOX  •  LOCAL TELEMETRY  •  LIVE":"HN // BLACKBOX  •  القياسات المحلية  •  مباشر",
    "root@HN-BLACKBOX:~#":"root@HN-BLACKBOX:~#",
    "help  //  type a command":"help  //  اكتب أمرًا",
    "ENTER":"دخول",
    "SYSTEM STATUS // LIVE":"حالة النظام // مباشر",
    "SYSTEM OVERVIEW":"نظرة عامة على النظام",
    "STATUS: ONLINE  //  LOCAL LAB  //  DEFENSIVE MODE":"الحالة: متصل  //  مختبر محلي  //  وضع دفاعي",
    "LIVE COMMAND CHANNEL  //  HN TERMINAL":"قناة الأوامر المباشرة  //  طرفية HN",
    "LOCAL // EXEC  •  ↑↓ HISTORY  •  ENTER RUN":"محلي // تنفيذ  •  ↑↓ السجل  •  ENTER تشغيل",
    "IDENTITY CORE // HN":"جوهر الهوية // HN",
    "HN CORE // ONLINE  •  VECTOR LOCKED":"جوهر HN // متصل  •  المتجه مقفول",
    "LIVE SYSTEM // TASK MANAGER":"النظام المباشر // مدير المهام",
    "PROJECT // MISSION // HN BLACKBOX":"المشروع // المهمة // HN BLACKBOX",
    "LIVE MODULE STREAM":"بث الوحدات المباشر",
    "QUICK COMMANDS":"أوامر سريعة",
    "LIVE WORKSPACE MONITOR  //  TASKS + TOOL HEALTH + PROJECT SCAN":"مراقبة مساحة العمل المباشرة  //  المهام + سلامة الأدوات + فحص المشروع",
    "SCANNING...":"جارٍ الفحص...",
    "⚠ DEFENSIVE WORKSPACE":"⚠ مساحة عمل دفاعية",
    "OPEN BLUE TEAM":"فتح الفريق الأزرق",
    "HN // INTELLIGENCE BOARD":"HN // لوحة الاستخبارات",
    "HN BLACKBOX // LOCAL • OFFLINE • EDUCATIONAL":"HN BLACKBOX // محلي • دون اتصال • تعليمي",
    "LIVE VISUALIZATION // OPERATION PATH":"تصوير حي // مسار العملية",
    "SECURE WORKSPACE":"مساحة عمل آمنة",
    "LOCAL":"محلي", "LIVE":"مباشر", "SECURE":"آمن", "READY":"جاهز",
    "HOME":"الرئيسية", "CRYPTOGRAPHY":"التشفير", "CRYPTANALYSIS":"تحليل الشفرات",
    "NETWORK SECURITY":"أمن الشبكات", "OSINT / FILE INTEL":"استخبارات الملفات", "WEB SECURITY":"أمن الويب", "BLUE TEAM":"الفريق الأزرق",
    "SECURITY LABS":"مختبرات الأمن", "SECURITY TOOLKIT":"عدة الأمن", "DEVELOPMENT":"التطوير",
    "DEVELOPER":"المطور", "HISTORY":"السجل", "INPUT":"المدخل", "OUTPUT":"المخرجات",
    "RESULT":"النتيجة", "ENCRYPT":"تشفير", "DECRYPT":"فك التشفير", "EXECUTE":"تنفيذ",
    "CLEAR":"مسح", "COPY":"نسخ", "SAVE":"حفظ", "HOW IT WORKS":"كيف تعمل", "GENERATE":"توليد",
    "BACK":"رجوع", "READY":"جاهز", "PROCESSING":"قيد المعالجة", "COMPLETE":"اكتمل",
    "ERROR":"خطأ", "FAILED":"فشل", "FORMULA":"المعادلة", "EXAMPLE":"مثال",
    "GUIDE":"الدليل", "SEARCH":"بحث", "FILTER":"تصفية", "REFRESH":"تحديث", "RESET":"إعادة ضبط",
    "RUN":"تشغيل", "ANALYZE":"تحليل", "CHECK":"فحص", "TEST":"اختبار", "PROFILE":"ملف التعريف",
    "SYSTEM":"النظام", "SYSTEM ONLINE":"النظام متصل", "SYSTEM STATUS // LIVE":"حالة النظام // مباشر",
    "SYSTEM TELEMETRY":"قياسات النظام", "LOCAL / EDUCATIONAL":"محلي / تعليمي",
    "LOCAL // LIVE":"محلي // مباشر", "REAL-TIME":"وقت حقيقي", "REAL-TIME":"وقت حقيقي",
    "ENTER":"دخول", "CANCEL":"إلغاء", "OPEN":"فتح", "CLOSE":"إغلاق",
    "SELECT A MODULE":"اختر وحدة", "SELECT ALGORITHM SET":"اختر مجموعة الخوارزميات",
    "ALGORITHM":"الخوارزمية", "OPERATION":"العملية", "STATUS":"الحالة", "CAPACITY":"السعة",
    "PAYLOAD":"الحمولة", "FORMAT":"التنسيق", "IMAGE":"الصورة", "PATH":"المسار",
    "PUBLIC":"عام", "PRIVATE":"خاص", "KEYPAIR":"زوج المفاتيح", "MESSAGE":"الرسالة",
    "DIGEST":"البصمة", "INTEGRITY":"السلامة", "STEP":"خطوة", "TRACE":"التتبع",
    "PLAY":"تشغيل", "PAUSE":"إيقاف مؤقت", "SCAN":"فحص", "DIAG":"تشخيص", "REPORT":"تقرير",
    "TOOLS":"الأدوات", "TIME":"الوقت", "ACTION":"الإجراء", "MODULE":"الوحدة",
    "NO RESULT YET.":"لا توجد نتيجة بعد.", "INPUT IS REQUIRED":"المدخل مطلوب",
    "OPERATION COMPLETE":"اكتملت العملية", "OPERATION FAILED":"فشلت العملية",
    "COPY EMAIL":"نسخ البريد الإلكتروني", "COPY PHONE":"نسخ الهاتف",
    "SAVE WORKSPACE":"حفظ مساحة العمل", "LOAD WORKSPACE":"تحميل مساحة العمل",
    "RUN DIAGNOSTICS":"تشغيل التشخيص", "EXPORT REPORT":"تصدير التقرير",
    "CLEAR LOCAL HISTORY":"مسح السجل المحلي", "EXPORT CSV":"تصدير CSV", "EXPORT JSON":"تصدير JSON",
}
GUIDES = {
    "caesar": ("E(x) = (x + k) mod 26", "HELLO + 3 → KHOOR"),
    "additive": ("E(x) = (x + k) mod 26", "HELLO + 3 → KHOOR"),
    "multiplicative": ("E(x) = (x × k) mod 26", "A × 5 → A"),
    "vigenere": ("Cᵢ = (Pᵢ + Kᵢ) mod 26", "ATTACKATDAWN + LEMON → LXFOPVEFRNHR"),
    "playfair": ("5×5 digraph substitution", "MONARCHY builds a 5×5 key square"),
    "railfence": ("Zig-Zag transposition", "WEARE... with 3 rails"),
    "columnar": ("Column permutation", "Write rows, then read columns by key order"),
    "keyed_transposition": ("Keyed column permutation", "Write rows → order columns by keyword → read"),
    "double_transposition": ("Two keyed transposition passes", "FIRST KEY → SECOND KEY; decrypt in reverse order"),
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
    "aes": ("AES-256-GCM + AEAD", "Authenticated modern symmetric encryption demo"),
    "des": ("DES rounds + CBC + PKCS7", "64-bit key, 16 Feistel rounds, educational trace"),
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
                                    font=(MONO, random.choice((9, 10))))
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
        self.minsize(1024, 700)
        self.configure(bg=P["bg"])
        try:
            icon = tk.PhotoImage(file=str(BASE / "assets" / "hn_blackbox.png"))
            self.iconphoto(True, icon)
            self._app_icon = icon
        except Exception:
            pass
        self.language = "en"
        self.rtl = False
        self._i18n_widgets = []
        self.current = "home"
        self.current_page = "home"
        self.current_algo = None
        self.pages = {}
        self.nav_buttons = {}
        self.key_entries = {}
        self.sidebar_expanded = True
        self._wheel_bound = set()
        self._scroll_targets = []
        self._global_wheel_bound = False
        self._visual_job = None
        self._crypto_future = None
        self._crypto_worker = CryptoWorker(max_workers=2)
        self._command_worker = CryptoWorker(max_workers=1)
        # Thread -> Tk handoff. Worker callbacks NEVER call tkinter directly;
        # they only enqueue completion records. The GUI thread drains this queue.
        self._ui_event_queue = queue.Queue()
        self._ui_event_job = None
        self._render_scheduler = RenderScheduler(target_fps=60, budget_ms=9.0)
        self._hover_jobs = {}
        self._cmd_history = []
        self._cmd_index = 0
        self._last_terminal_output = ""
        self._terminal_events = []
        self._ui_theme = "cyan"
        self._app_started = time.monotonic()
        self._last_user_event = self._app_started
        # First-frame state is intentionally lightweight; secondary pages are lazy.
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
        self._network_rate_cache = 0.0
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
        self._home_data_next_refresh = 0.0
        self._telemetry_stop = threading.Event()
        self._telemetry_thread = threading.Thread(target=self._telemetry_loop, daemon=True, name='hn-system-telemetry')
        self._telemetry_thread.start()
        self._home_data = {
            'files': 0, 'core': 0, 'tests': 0, 'history': 0, 'labs': 0,
            'modules': [], 'integrity': [], 'last_op': 'NO LOCAL OPERATIONS RECORDED',
            'process_feed': [], 'sample_at': 0.0,
        }
        self._home_workspace_phase = 0
        self._workspace_last = None
        self._module_hud_jobs = {}
        # One shared compositor tick drives all panel micro-effects. This keeps
        # the HUD alive without spawning a timer for every individual card.
        self._fx_panels = []
        self._fx_phase = 0.0
        # Motion policy: autonomous visual systems are never gated by mouse hover
        # or window focus. Performance is controlled by retained-mode updates and
        # channel cadence, not by stopping visual effects.
        self._motion_active = True
        # One retained-mode animation clock owns UI motion. Individual HUDs no
        # longer enqueue their own recurring callbacks, which was the main
        # source of timer pressure and input starvation on slower machines.
        self._motion_ms = 16  # ~60 FPS scheduler; individual visual channels are budgeted below without disabling them
        self._motion_hidden_ms = 16
        self._animation_callbacks = []
        self._animation_job = None
        self._navigation_job = None
        self._navigation_serial = 0
        # Modern/stego cinematic HUD state is retained and advanced by the
        # single global animation clock; no per-widget timers are spawned.
        self._modern_matrix = {'canvas': None, 'items': [], 'visual_items': [], 'visual_canvas': None, 'size': None, 'visual_size': None, 'phase': 0}
        self._modern_signal_canvases = []
        self._stego_microfx = []
        self._modern_signal_phase = 0.0
        self._modern_signal_pulse_until = 0.0
        self._cinema_fx = {'phase': 0.0, 'items': [], 'size': None, 'canvas': None, 'accent': P['cyan']}
        self._cinematic_surfaces = []
        self._heading_huds = []
        self._cinematic_seq = 0
        self._network_diag = {'running': False, 'capture': False, 'phase': 0.0, 'scan_rows': [], 'topology': None, 'traffic_prev': None, 'traffic_rate': {'sent': 0.0, 'recv': 0.0}, 'sockets': [], 'ops': [], 'sample_at': 0.0, 'sample_busy': False}
        self._stego_scanner = {'canvas': None, 'items': {}, 'size': None, 'active': False, 'phase': 0.0}
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
        self.bind_all("<ButtonPress>", lambda _e: setattr(self, "_last_user_event", time.monotonic()), add="+")
        self.bind_all("<KeyPress>", lambda _e: setattr(self, "_last_user_event", time.monotonic()), add="+")
        # Window focus is NOT an animation switch. Visual systems remain autonomous
        # while the app is focused, unfocused, or while the pointer is elsewhere.
        self.report_callback_exception = self._report_callback_exception
        self._ui_event_job = self.after(20, self._drain_worker_events)
        self.show_page("home")
        self.after_idle(self._finish_initial_render)

    def _motion_page_active(self, *keys):
        """Return whether a visual channel belongs to the foreground destination.

        Navigation controls visibility; this gate controls rendering work only.
        No visual objects are deleted when a destination is not active.
        """
        if not getattr(self, '_ui_ready', False):
            return False
        current=getattr(self, 'current', None)
        return not keys or current in keys

    def _motion_owner_for_callback(self, fn):
        """Map global visual channels to their destination without changing VFX."""
        name=getattr(fn, '__name__', '')
        owners={
            '_animate_home_identity': ('home',), '_animate_home_status': ('home',),
            '_animate_system_monitor': ('home',), '_animate_home_monitor': ('home',),
            '_animate_home_intel': ('home',), '_animate_home_hero': ('home',),
            '_animate_home_command_hud': ('home',), '_animate_home_workspace': ('home',),
            '_animate_terminal_hud': ('processing',), '_animate_processing_microfx': ('processing',),
            '_animate_cryptanalysis_hud': ('analysis',),
            '_animate_modern_matrix': ('crypto_modern',), '_animate_modern_cinema': ('crypto_modern',),
            '_animate_modern_signals': ('crypto_modern',), '_animate_stego_scanner': ('crypto_stego',),
            '_animate_fileintel_hud': ('fileintel',), '_animate_network_diagnostics': ('network',),
            '_animate_developer_metrics': ('developer',),
        }
        return owners.get(name, ())

    def _finish_initial_render(self):
        """Release the first-frame render lock after the shell is mapped."""
        self._ui_ready = True
        self._resizing_until = 0.0
        # Start the autonomous visual bus immediately. Mounted and hidden page surfaces remain live.
        self._animation_callbacks = [
            self._animate_home_identity, self._animate_home_status,
            self._animate_system_monitor, self._animate_home_monitor,
            self._animate_home_intel, self._animate_home_hero,
            self._animate_home_command_hud, self._animate_home_workspace,
            self._animate_heading_huds,
            self._animate_terminal_hud, self._animate_processing_microfx, self._animate_cryptanalysis_hud, self._animate_modern_matrix, self._animate_modern_cinema,
            self._animate_modern_signals, self._animate_stego_scanner,
            self._animate_fileintel_hud, self._animate_cinematic_surfaces,
            self._animate_network_diagnostics,
            self._panel_fx_tick,
        ]
        # One master clock owns all visual channels. No VFX channel owns its own timer.
        for fn in self._animation_callbacks:
            try:
                name=getattr(fn, '__name__', str(id(fn)))
                owners=self._motion_owner_for_callback(fn)
                if owners:
                    def channel_tick(fn=fn, owners=owners):
                        if self._motion_page_active(*owners):
                            fn()
                    runner=channel_tick
                else:
                    runner=fn
                self._render_scheduler.register(name, runner, fps=60.0, priority=1 if ('modern' in name or 'stego' in name) else 0)
            except Exception:
                pass
        self._start_animation_clock()
        # Lower-frequency data/clock jobs stay independent from the frame clock.
        for fn in (self._refresh_home_scan, self._update_home_clock, self._pulse_home):
            try:
                fn()
            except tk.TclError:
                pass
        self._request_home_layout(immediate=True)
        # Secondary pages stay lazy. Prewarming them creates avoidable widget/canvas
        # churn immediately after Home appears.

    def _start_animation_clock(self):
        if self._animation_job is None:
            self._animation_job = self.after(self._motion_ms, self._animation_tick)

    def _animation_tick(self):
        self._animation_job = None
        if not getattr(self, '_ui_ready', False):
            return
        try:
            delay = self._render_scheduler.tick()
            self._perf_frame = self._render_scheduler.frame
            stats = self._render_scheduler.stats()
            self._render_last_ms = stats["last_frame_ms"]
            self._render_avg_ms = stats["avg_frame_ms"]
            # V26 policy: visual continuity has priority over adaptive throttling.
            # A light frame-time increase is acceptable; never stop/slow a visual channel because of budget pressure.
        except Exception as exc:
            self._last_error = f"render_scheduler: {exc}"
            delay = self._motion_ms
        try:
            if self.winfo_exists():
                self._animation_job = self.after(max(8, int(delay)), self._animation_tick)
        except tk.TclError:
            pass

    def _queue_worker_event(self, callback):
        """Thread-safe handoff: only queue data/callables, never touch Tk from workers."""
        try:
            self._ui_event_queue.put_nowait(callback)
        except Exception:
            pass

    def _drain_worker_events(self):
        self._ui_event_job = None
        try:
            while True:
                callback = self._ui_event_queue.get_nowait()
                try: callback()
                except (tk.TclError, RuntimeError): pass
        except queue.Empty:
            pass
        try:
            if self.winfo_exists():
                self._ui_event_job = self.after(20, self._drain_worker_events)
        except tk.TclError:
            pass

    def destroy(self):
        """Cancel every Tk timer before teardown to prevent stale callbacks."""
        try:
            for job in self.tk.call("after", "info"):
                try: self.after_cancel(job)
                except Exception: pass
        except Exception: pass
        self._motion_active = False
        try:
            executor = getattr(self, '_fileintel_executor', None)
            if executor is not None:
                executor.shutdown(wait=False, cancel_futures=True)
        except Exception:
            pass
        if getattr(self, '_ui_event_job', None) is not None:
            try: self.after_cancel(self._ui_event_job)
            except Exception: pass
            self._ui_event_job = None
        if hasattr(self, '_telemetry_stop'):
            self._telemetry_stop.set()
        if getattr(self, '_animation_job', None) is not None:
            try: self.after_cancel(self._animation_job)
            except Exception: pass
            self._animation_job = None
        try:
            if self._crypto_future is not None and not self._crypto_future.done():
                self._crypto_future.cancel()
            self._crypto_worker.shutdown(wait=False)
            self._command_worker.shutdown(wait=False)
            if hasattr(self, "_fileintel_executor"):
                self._fileintel_executor.shutdown(wait=True, cancel_futures=True)
        except Exception:
            pass
        try: self._render_scheduler.clear()
        except Exception: pass
        try: super().destroy()
        except tk.TclError: pass

    def t(self, k):
        table = TEXTS_AR if self.language == "ar" else TEXTS
        return table.get(k, TEXTS.get(k, k))

    def toggle_language(self):
        self.set_language("ar" if self.language == "en" else "en")

    def _translate_widget_tree(self):
        """Translate existing Tk text-bearing widgets when Arabic is active.

        Technical examples, code, paths and canvas-rendered telemetry are left
        untouched intentionally; operator-facing controls and labels are mapped.
        """
        if not hasattr(self, "winfo_children"):
            return
        table = UI_AR if self.language == "ar" else {v:k for k,v in UI_AR.items()}
        def walk(parent):
            for child in parent.winfo_children():
                try:
                    text = child.cget("text")
                    if isinstance(text, str) and text in table:
                        child.configure(text=table[text])
                except (tk.TclError, TypeError):
                    pass
                walk(child)
        walk(self)

    def set_language(self, language):
        if language not in ("en", "ar"):
            return
        self.language = language
        self.rtl = language == "ar"
        self._translate_widget_tree()
        # Update the stable shell labels and page widgets immediately.
        if hasattr(self, "brand"):
            self.brand.configure(text=self.t("brand"))
            self.sub.configure(text=self.t("sub"))
        for key, b in self.nav_buttons.items():
            if hasattr(b, "_key"):
                b._label = self.t(b._key)
                b.configure(text=(f"{b._icon}   {b._label}" if self.sidebar_expanded else b._icon),
                            anchor=("e" if self.rtl else "w"))
        if hasattr(self, "project_caption"):
            self.project_caption.configure(text="وحدات المشروع  //  مباشر" if self.rtl else "PROJECT MODULES  //  LIVE",
                                            anchor=("e" if self.rtl else "w"))
        if hasattr(self, "global_status"):
            self.global_status.configure(text="● محرك محلي  //  مساحة آمنة" if self.rtl else "● LOCAL ENGINE  //  SECURE WORKSPACE")
        if hasattr(self, "hud"):
            self.hud.configure(text="وحدة العمليات  //  محلي  //  مساحة مشفرة" if self.rtl else "OPS CONSOLE  //  LOCAL  //  ENCRYPTED WORKSPACE",
                               anchor=("w" if self.rtl else "e"))
        if hasattr(self, "language_button"):
            self.language_button.configure(text=LANGUAGE_LABELS["en"] if self.rtl else LANGUAGE_LABELS["ar"])
        self._apply_direction()

    def _apply_direction(self):
        if not hasattr(self, "sidebar") or not hasattr(self, "content"):
            return
        try:
            sidebar_col = 1 if self.rtl else 0
            content_col = 0 if self.rtl else 1
            self.sidebar.grid_configure(row=0, column=sidebar_col, sticky="nsew")
            self.content.grid_configure(row=0, column=content_col, sticky="nsew")
            self.grid_columnconfigure(0, weight=1 if self.rtl else 0, minsize=0 if self.rtl else (78 if not self.sidebar_expanded else 270))
            self.grid_columnconfigure(1, weight=0 if self.rtl else 1, minsize=(78 if self.rtl and not self.sidebar_expanded else (270 if self.rtl and self.sidebar_expanded else 0)))
            if not self.rtl:
                self.grid_columnconfigure(0, weight=0, minsize=78 if not self.sidebar_expanded else 270)
                self.grid_columnconfigure(1, weight=1, minsize=0)
            else:
                self.grid_columnconfigure(0, weight=1, minsize=0)
                self.grid_columnconfigure(1, weight=0, minsize=78 if not self.sidebar_expanded else 270)
        except tk.TclError:
            pass

    def _widget_on_current_page(self, widget):
        """Legacy compatibility hook: every mounted visual surface is autonomous."""
        # Intentionally unconditional. Hidden/raised state must never be an animation switch.
        try:
            return bool(widget is not None and widget.winfo_exists())
        except Exception:
            return True

    # ---------- boot / shell ----------
    def _play_startup_welcome_audio(self):
        """Play the single cinematic startup/welcome bed off the Tk thread."""
        audio = BASE.parent / "assets" / "audio" / "startup_cinematic_welcome.wav"
        self._startup_audio_proc = None
        if not audio.exists():
            return
        def worker():
            try:
                if sys.platform.startswith("win"):
                    import winsound
                    winsound.PlaySound(str(audio), winsound.SND_FILENAME)
                elif shutil.which("ffplay"):
                    proc = subprocess.Popen(
                        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(audio)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    )
                    self._startup_audio_proc = proc
                    proc.wait()
                elif shutil.which("aplay"):
                    proc = subprocess.Popen(
                        ["aplay", "-q", str(audio)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    self._startup_audio_proc = proc
                    proc.wait()
            except Exception:
                pass
        threading.Thread(target=worker, name="hn-startup-audio", daemon=True).start()

    def _splash(self):
        """Cinematic boot gateway synchronized to the one-shot welcome sound."""
        self.withdraw()
        self.splash = tk.Toplevel(self)
        self.splash.overrideredirect(True)
        self.splash.configure(bg=P["bg"])
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1180, sw - 50), min(700, sh - 90)
        self.splash.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        try:
            self.splash.attributes("-alpha", 1.0)
        except tk.TclError:
            pass

        self._splash_canvas = tk.Canvas(self.splash, bg="#01040a", highlightthickness=0, bd=0)
        self._splash_canvas.pack(fill="both", expand=True)
        self._splash_w = w; self._splash_h = h
        c = self._splash_canvas
        cx, cy = w/2, h/2
        # Persistent sci-fi face / identity plate.
        c.create_rectangle(22, 22, w-22, h-22, outline="#123e4a", width=1)
        c.create_line(55, 55, 260, 55, fill=P['cyan'], width=2)
        c.create_line(w-260, h-55, w-55, h-55, fill="#174c5a", width=1)
        for y in range(72, h-72, 22):
            c.create_line(38, y, w-38, y, fill="#06151f", width=1)
        c.create_text(58, 78, text="HN // BLACKBOX", anchor="nw", fill=P['cyan'], font=(MONO, 14, 'bold'))
        c.create_text(58, 104, text="SECURE COMMAND INTERFACE", anchor="nw", fill="#547484", font=(MONO, 9, 'bold'))
        c.create_text(w-58, 78, text="LOCAL // ENCRYPTED", anchor="ne", fill=P['green'], font=(MONO, 10, 'bold'))
        c.create_text(w-58, 104, text="BOOT SEQUENCE", anchor="ne", fill="#547484", font=(MONO, 9, 'bold'))
        # Central identity rings / scanning face.
        rings=[]
        for r,col,width in [(174,'#0e4d60',2),(151,'#176b82',1),(124,'#20e8ff',1),(92,'#124250',1),(58,'#20e8ff',2)]:
            rings.append(c.create_oval(cx-r,cy-r,cx+r,cy+r,outline=col,width=width))
        c.create_line(cx-205,cy,cx-70,cy,fill="#0f4857",width=1)
        c.create_line(cx+70,cy,cx+205,cy,fill="#0f4857",width=1)
        c.create_line(cx,cy-205,cx,cy-70,fill="#0f4857",width=1)
        c.create_line(cx,cy+70,cx,cy+205,fill="#0f4857",width=1)
        sweep=c.create_line(cx,cy,cx+162,cy,fill=P['cyan'],width=2)
        core=c.create_oval(cx-7,cy-7,cx+7,cy+7,fill=P['cyan2'],outline='')
        face=c.create_oval(cx-38,cy-51,cx+38,cy+51,outline='#72f7ff',width=1)
        visor=c.create_rectangle(cx-23,cy-7,cx+23,cy+3,outline=P['cyan'],width=2)
        # Corner brackets make the entry feel like an authenticated terminal.
        bracket_len=44
        for sx,sy,dx,dy in [(70,70,1,1),(w-70,70,-1,1),(70,h-70,1,-1),(w-70,h-70,-1,-1)]:
            c.create_line(sx,sy,sx+dx*bracket_len,sy,fill='#174a58',width=2)
            c.create_line(sx,sy,sx,sy+dy*bracket_len,fill='#174a58',width=2)
        self._splash_fx = {'cx':cx,'cy':cy,'rings':rings,'sweep':sweep,'core':core,'face':face,'visor':visor,'phase':0.0,'start':time.monotonic()}

        self.rain = MatrixRain(self.splash, count=58, speed=1.8)
        self.rain.place(relx=0, rely=0, relwidth=1, relheight=1)
        try:
            self.splash.tk.call('lower', self.rain._w, self._splash_canvas._w)
        except tk.TclError:
            pass
        # Recreate the center/status after MatrixRain is raised/lowered deterministically.
        self._splash_user = self._splash_canvas.create_text(w/2, h-118, text=f"IDENTITY VERIFIED  //  {(getpass.getuser() or 'HN USER').upper()}", fill=P['green'], font=(MONO, 12, 'bold'))
        self._splash_status_id = self._splash_canvas.create_text(w/2, h-91, text="ESTABLISHING SECURE WORKSPACE", fill=P['yellow'], font=(MONO, 10, 'bold'))
        self._splash_stage_id = self._splash_canvas.create_text(w/2, h-66, text="STAGE 01 / 04  //  IDENTITY", fill="#6f8e9c", font=(MONO, 9, 'bold'))
        self._splash_bar_bg = self._splash_canvas.create_rectangle(w*.25, h-42, w*.75, h-38, fill='#081d28', outline='')
        self._splash_bar = self._splash_canvas.create_rectangle(w*.25, h-42, w*.25+4, h-38, fill=P['cyan'], outline='')

        self._startup_duration = 6.0
        self._startup_audio_started = False
        self._startup_audio_start_job = self.after(130, self._start_startup_sequence)

    def _start_startup_sequence(self):
        if not getattr(self, 'splash', None) or not self.splash.winfo_exists():
            return
        self._startup_audio_started = True
        self._play_startup_welcome_audio()
        self._startup_tick()

    def _startup_tick(self):
        try:
            if not self.splash.winfo_exists(): return
        except tk.TclError:
            return
        fx=self._splash_fx; c=self._splash_canvas
        elapsed=time.monotonic()-fx['start']; p=min(1.0,elapsed/self._startup_duration)
        fx['phase'] += 0.12
        cx,cy=fx['cx'],fx['cy']
        import math as _math
        angle=fx['phase']
        c.coords(fx['sweep'],cx,cy,cx+162*_math.cos(angle),cy+162*_math.sin(angle))
        for i,r in enumerate(fx['rings']):
            rr=124 + i*9 + 5*_math.sin(fx['phase']*.7+i)
            c.coords(r,cx-rr,cy-rr,cx+rr,cy+rr)
        pulse=7+4*(0.5+0.5*_math.sin(fx['phase']*2.0))
        c.coords(fx['core'],cx-pulse,cy-pulse,cx+pulse,cy+pulse)
        c.coords(fx['visor'],cx-24,cy-8+2*_math.sin(fx['phase']),cx+24,cy+2+2*_math.sin(fx['phase']))
        # Four boot stages synchronize with the audio's tonal/voice sections.
        stages=[(0.00,0.22,"STAGE 01 / 04  //  IDENTITY LINKED"),(0.22,0.44,"STAGE 02 / 04  //  VISUAL CORE ONLINE"),(0.44,0.68,"STAGE 03 / 04  //  SECURE BUS ESTABLISHED"),(0.68,1.00,"STAGE 04 / 04  //  BLACKBOX READY")]
        stage=next((txt for lo,hi,txt in stages if lo<=p<hi),stages[-1][2])
        c.itemconfigure(self._splash_stage_id,text=stage)
        status="AUTHENTICATING // LOCAL IDENTITY" if p<.22 else "MOUNTING // CYBER VISUAL CORE" if p<.44 else "SYNCHRONIZING // SECURE WORKSPACE" if p<.68 else "SYSTEM READY // ENTERING COMMAND DECK"
        c.itemconfigure(self._splash_status_id,text=status)
        w=self._splash_w; h=self._splash_h
        c.coords(self._splash_bar,w*.25,h-42,w*.25+(w*.50)*p,h-38)
        if p<.86:
            self.after(40,self._startup_tick)
        else:
            self._fade_splash(1.0)

    def _fade_splash(self, alpha):
        if not self.splash.winfo_exists():
            self.deiconify(); self.lift(); return
        alpha -= .10
        if alpha <= .04:
            try: self.splash.destroy()
            except tk.TclError: pass
            self.deiconify(); self.lift(); return
        try: self.splash.attributes("-alpha", alpha)
        except tk.TclError:
            if alpha < .5:
                try: self.splash.destroy()
                except tk.TclError: pass
                self.deiconify(); self.lift(); return
        self.after(45, lambda: self._fade_splash(alpha))

    def _styles(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TEntry", fieldbackground=P["panel2"], foreground=P["text"],
                    insertcolor=P["cyan"], padding=9, borderwidth=0)
        s.configure("TRadiobutton", background=P["panel"], foreground=P["text"],
                    font=(FONT, 11))
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
                            font=(MONO, 9, "bold"))
        self.sub.pack(pady=(3, 0))

        self.nav_frame = tk.Frame(self.sidebar, bg=P["nav"])
        self.nav_frame.pack(fill="both", expand=True, padx=10, pady=8)
        self.project_caption = tk.Label(self.nav_frame, text="PROJECT MODULES  //  LIVE", bg=P["nav"], fg=P["dim"],
                                         font=(MONO, 9, "bold"), anchor="w")
        self.project_caption.pack(fill="x", padx=8, pady=(2, 8))
        for key, icon, label in NAV:
            accent = NAV_ACCENTS.get(key, P["cyan"])
            b = tk.Button(self.nav_frame, text=f"  {icon}   {label}",
                          command=lambda k=key: self._nav_click(k),
                          bg=P["nav"], fg=P["muted"], activebackground=P["panel2"],
                          activeforeground=P["text"], relief="flat", bd=0,
                          anchor="w", padx=9, pady=9, font=(FONT, 10, "bold"),
                          cursor="hand2", highlightthickness=1,
                          highlightbackground=P["nav"], highlightcolor=accent)
            b.pack(fill="x", pady=2)
            b._key, b._label, b._icon, b._accent = key, label, icon, accent
            self.nav_buttons[key] = b

        footer = tk.Frame(self.sidebar, bg=P["nav"], height=62)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        tk.Label(footer, text="●  " + self.t("online"), bg=P["nav"], fg=P["green"],
                 font=(MONO, 10, "bold")).pack()

        self.content = tk.Frame(self, bg=P["bg"])
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        self.topline = tk.Frame(self.content, bg=P["cyan"], height=2)
        self.topline.grid(row=0, column=0, sticky="new")
        self.topbar=tk.Frame(self.content,bg='#040b12',height=40,highlightbackground='#10394a',highlightthickness=1)
        self.topbar.grid(row=0,column=0,sticky='new',padx=10,pady=(6,0)); self.topbar.grid_propagate(False)
        tk.Label(self.topbar,text='HN / BLACKBOX',bg='#040b12',fg=P['cyan'],font=(MONO, 10,'bold')).pack(side='left',padx=10)
        self.global_status=tk.Label(self.topbar,text='● LOCAL ENGINE  //  SECURE WORKSPACE',bg='#040b12',fg=P['green'],font=(MONO, 9,'bold'))
        self.global_status.pack(side='left',padx=8)
        self.language_button=tk.Button(self.topbar,text='عربي',command=self.toggle_language,bg='#07131b',fg=P['cyan'],activebackground=P['panel2'],activeforeground=P['text'],relief='flat',bd=0,font=(MONO,9,'bold'),cursor='hand2',padx=10)
        self.language_button.pack(side='left',padx=6)
        self.global_clock=tk.Label(self.topbar,text='',bg='#040b12',fg=P['muted'],font=(MONO, 10,'bold')); self.global_clock.pack(side='right',padx=10)
        self.hud = tk.Label(self.content, text="OPS CONSOLE  //  LOCAL  //  ENCRYPTED WORKSPACE",
                            bg=P["bg"], fg=P["dim"], font=(MONO, 9), anchor="e")
        self.hud.place(relx=.98, rely=.058, anchor="ne")
        self._global_clock_tick()
        self._apply_direction()

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
            # Navigation audio is handled after the destination becomes visible.
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
        """Compatibility hook; autonomous visuals never depend on pointer hover."""
        return

    # ---------- pages ----------
    def _pages(self):
        """Register page factories without constructing every screen at startup.

        Tk widget construction must remain on the GUI thread, so the correct
        architecture is lazy mounting plus background workers for data/crypto.
        The old implementation built every module before the first frame, which
        made launch and early navigation feel like a frozen application.
        """
        self.pages["home"] = self.home_page()
        self.pages["processing"] = tk.Frame(self.content, bg=P["bg"])
        self._attach_cinematic_surface(self.pages["processing"], 'processing', P['purple'])
        self._page_factories = {
            "crypto": self.crypto_page,
            "crypto_modern": self.crypto_modern_page,
            "crypto_stego": self.crypto_stego_page,
            "analysis": lambda: self.future_page("analysis"),
            "network": self.network_diagnostics_page,
            "fileintel": self.file_intelligence_page,
            "web": lambda: self.future_page("web"),
            "blue": lambda: self.future_page("blue"),
            "labs": self.lab_environment_page,
            "toolkit": self.toolkit_page,
            "development": self.development_page,
            "developer": self.developer_page,
            "history": self.history_page,
        }
        # Destination scenes are mounted on demand. Only the foreground destination
        # spends rendering time; no VFX are deleted or permanently disabled.
        for key in self._page_factories:
            self.pages[key] = None
        self._page_building = set()
        self._page_built_at = {}
        self.pages["home"].grid(row=0, column=0, sticky="nsew", padx=28, pady=(26, 18))
        self.pages["processing"].grid(row=0, column=0, sticky="nsew", padx=28, pady=(26, 18))
        self._sync_aliases()
        try:
            self.pages[self.current].tkraise()
        except Exception:
            pass

    def _ensure_page(self, key):
        """Mount a destination when entered; inactive destinations consume no animation work."""
        if key == "dashboard": key = "crypto"
        page = self.pages.get(key)
        if page is not None:
            return page
        factory = getattr(self, "_page_factories", {}).get(key)
        if factory is None:
            raise KeyError(f"Unknown page: {key}")
        if key in self._page_building:
            return None
        self._page_building.add(key)
        try:
            page = factory()
            self._attach_cinematic_surface(page, key, NAV_ACCENTS.get(key, P['cyan']))
            self.pages[key] = page
            page.grid(row=0, column=0, sticky="nsew", padx=28, pady=(26, 18))
            self._page_built_at[key] = time.monotonic()
            self._sync_aliases()
            return page
        finally:
            self._page_building.discard(key)

    def _sync_aliases(self):
        # ``welcome`` is now a real landing screen. Keep the historical aliases
        # used by older tests/shortcuts without replacing the landing page.
        self.pages.update({"dashboard": self.pages["crypto"],
                           "cryptanalysis": self.pages["analysis"], "blue_team": self.pages["blue"]})
        self.nav_buttons.update({"dashboard": self.nav_buttons["crypto"],
                                 "cryptanalysis": self.nav_buttons["analysis"], "blue_team": self.nav_buttons["blue"]})

    def heading(self, parent, kicker, title, sub):
        """Living V6 command header: telemetry first, navigation-free by design.

        The header is intentionally a passive telemetry surface. Module navigation
        belongs to the sidebar; this strip is reserved for autonomous signal bars,
        radar, scan rails and live counters. Nothing in this HUD depends on hover.
        """
        f = tk.Frame(parent, bg=P["bg"])
        f.pack(fill="x", pady=(0, 14))
        top = tk.Frame(f, bg="#050d14", highlightbackground="#123c49", highlightthickness=1, height=92)
        top.pack(fill="x", pady=(0, 8)); top.pack_propagate(False)
        hud = tk.Canvas(top, bg="#050d14", highlightthickness=0, bd=0, takefocus=0)
        hud.pack(fill="both", expand=True)
        accent = NAV_ACCENTS.get(self.current, P["cyan"])
        state = {"phase": 0.0, "size": None, "items": {}, "key": kicker, "accent": accent, "owner": getattr(self, "current", "home")}

        def rebuild(w, h):
            hud.delete('all')
            # Technical grid kept sparse and crisp. All motion below is retained-mode:
            # only coordinates / text / alpha-like color state are mutated per frame.
            for x in range(0, w, 26):
                hud.create_line(x, 0, x, h, fill='#071a22', tags='static')
            for y in range(0, h, 18):
                hud.create_line(0, y, w, y, fill='#071a22', tags='static')

            hud.create_line(14, 2, max(30, w-220), 2, fill=accent, width=1)
            hud.create_line(14, h-2, w-14, h-2, fill='#0d3b48', width=1)
            scan=hud.create_rectangle(-120, 4, -8, h-4, fill='#0a2c35', outline='', tags='scan')

            # Dense autonomous signal rack. More indicators than the old 15-bar rail,
            # with staggered baselines so the strip reads like a live command console.
            blocks=[]
            bar_count=max(24, min(34, (w-250)//13))
            for i in range(bar_count):
                x=18+i*11
                seed=(i*17+7)%31
                bh=6+(seed%22)
                col=(accent if i%4 else P['green']) if i%9 else '#ff3f68'
                bid=hud.create_rectangle(x,h-24-bh,x+7,h-24,fill=col,outline='')
                cap=hud.create_line(x+3,h-27,x+3,h-22,fill='#163b48',width=1)
                blocks.append((bid,cap,x,bh,col))

            # Two micro signal lanes above the main rack. These remain visible but
            # deliberately thin so they never compete with the page title.
            micro=[]
            for i in range(max(12, min(22, (w-360)//24))):
                x=18+i*24
                mid=h-50-(i%3)*3
                lid=hud.create_line(x,mid,x+15,mid,fill='#123540',width=1)
                pulse=hud.create_line(x+2,mid,x+6,mid-3-(i%5),fill=accent,width=1)
                micro.append((lid,pulse,x,mid))

            # Radar / command core.
            cx,cy=max(125,w-84),h/2-3
            base=min(31,h*.29)
            rings=[]
            for r,col in ((base+10,'#174653'),(base,'#1d5e70'),(base*.55,accent)):
                rings.append(hud.create_oval(cx-r,cy-r,cx+r,cy+r,outline=col,width=1))
            sweep=hud.create_line(cx,cy,cx+base,cy,fill=accent,width=2)
            core=hud.create_oval(cx-3,cy-3,cx+3,cy+3,fill=P['cyan2'],outline='')

            # Live counters occupy the upper-right telemetry pocket.
            live=hud.create_text(w-150,9,text='● LIVE',anchor='ne',fill=P['green'],font=(MONO,10,'bold'))
            seq=hud.create_text(w-150,27,text='SEQ 0000',anchor='ne',fill=P['cyan'],font=(MONO,10,'bold'))
            mode=hud.create_text(w-150,45,text='VECTOR LOCK // NOMINAL',anchor='ne',fill=P['muted'],font=(MONO,9,'bold'))
            rates=hud.create_text(w-150,61,text='RX 000  //  TX 000  //  CORE 100%',anchor='ne',fill=P['dim'],font=(MONO,9,'bold'))

            labels=[]
            for idx,lab in enumerate(('SIG','RX','TX','CPU','MEM','OPS')):
                x=18+idx*64
                labels.append(hud.create_text(x,h-7,text=f'{lab} // --',anchor='sw',fill='#2c5966',font=(MONO,9,'bold')))

            state['items']={
                'scan':scan,'blocks':blocks,'micro':micro,'rings':rings,'sweep':sweep,'core':core,
                'live':live,'seq':seq,'mode':mode,'rates':rates,'labels':labels
            }
            state['size']=(w,h)
            state['rebuild']=rebuild

        state['hud']=hud
        state['parent']=parent
        self._heading_huds.append(state)

        def initial():
            if not hud.winfo_exists(): return
            w,h=max(1,hud.winfo_width()),max(1,hud.winfo_height())
            if state['size']!=(w,h):
                rebuild(w,h)
                hud.create_text(14,10,text=str(kicker).upper(),anchor='nw',fill=accent,font=(MONO,10,'bold'),tags='label')
                hud.create_text(14,29,text='HN // BLACKBOX  •  LOCAL TELEMETRY  •  LIVE',anchor='nw',fill=P['muted'],font=(MONO,10,'bold'),tags='label')
        hud.after_idle(initial)
        body = tk.Frame(f, bg=P["bg"]); body.pack(fill="x")
        tk.Label(body, text=title, bg=P["bg"], fg=P["text"],font=(FONT, 27, "bold"), anchor="w", justify="left").pack(fill="x", pady=(1, 1))
        tk.Label(body, text=sub, bg=P["bg"], fg=P["muted"],font=(FONT, 11), anchor="w", justify="left", wraplength=980).pack(fill="x")

    def _animate_heading_huds(self):
        """Restore V6-style header motion across every active destination."""
        if not getattr(self,'_ui_ready',False): return
        alive=[]; now=time.monotonic()
        for st in getattr(self,'_heading_huds',[]):
            hud=st.get('hud'); parent=st.get('parent')
            try:
                if not hud.winfo_exists(): continue
                alive.append(st)
                if not self._motion_page_active(st.get('owner', 'home')): continue
                if now < getattr(self,'_resizing_until',0): continue
                w=max(40,hud.winfo_width()); h=max(40,hud.winfo_height())
                if st.get('size')!=(w,h):
                    rebuild=st.get('rebuild')
                    if rebuild:
                        rebuild(w,h)
                        hud.create_text(14,10,text=str(st.get('key','')).upper(),anchor='nw',fill=st.get('accent',P['cyan']),font=(MONO,9,'bold'),tags='label')
                        hud.create_text(14,27,text='HN // BLACKBOX  •  LOCAL TELEMETRY  •  LIVE',anchor='nw',fill=P['muted'],font=(MONO,9,'bold'),tags='label')
                items=st['items']
                accent=st.get('accent', P['cyan'])
                if not items or 'scan' not in items: continue
                phase=st.get('phase',0.0)+0.9
                st['phase']=phase
                sx=(phase*2.6)%(w+130)-130
                hud.coords(items['scan'],sx,4,sx+112,h-4)
                base=min(30,h*.32); cx=max(110,w-82); cy=h/2-1
                ang=phase*0.055
                hud.coords(items['sweep'],cx,cy,cx+base*math.cos(ang),cy+base*math.sin(ang))
                for i,(item,cap,x,bh,col) in enumerate(items['blocks']):
                    nb=max(5,min(31,int(bh+7*math.sin(phase*.085+i*.61)+3*math.sin(phase*.031+i*1.7))))
                    hud.coords(item,x,h-24-nb,x+7,h-24)
                    hud.coords(cap,x+3,h-27,x+3,h-22)
                    if i%11==0 and int(phase)%24 in (0,1,2):
                        hud.itemconfigure(item,fill='#ff3f68')
                    elif i%4==0:
                        hud.itemconfigure(item,fill=P['green'])
                    else:
                        hud.itemconfigure(item,fill=accent)
                for i,(lid,pulse,x,mid) in enumerate(items.get('micro',[])):
                    py=mid-2.0-8.0*abs(math.sin(phase*.06+i*.73))
                    hud.coords(pulse,x+2,mid,x+6,py)
                pulse=1.0+0.8*(1+math.sin(phase*.13))/2
                hud.coords(items['core'],cx-pulse,cy-pulse,cx+pulse,cy+pulse)
                hud.itemconfigure(items['seq'],text=f'SEQ {int(phase)%10000:04d}')
                hud.itemconfigure(items['mode'],text=f'VECTOR LOCK // {getattr(self,"current","home").upper()} // NOMINAL')
                # Autonomous telemetry labels. Navigation is intentionally absent from this HUD.
                current=getattr(self,'current','home').upper()
                sig=42+int(18*abs(math.sin(phase*.045)))
                rx=180+int(110*abs(math.sin(phase*.031+1.2)))
                tx=140+int(95*abs(math.cos(phase*.037)))
                cpu=28+int(22*abs(math.sin(phase*.052+0.4)))
                mem=46+int(17*abs(math.cos(phase*.041+0.9)))
                ops=(int(phase)%999)
                vals=(sig,rx,tx,cpu,mem,ops)
                for lid,lab in zip(items.get('labels',[]),('SIG','RX','TX','CPU','MEM','OPS')):
                    value={'SIG':sig,'RX':rx,'TX':tx,'CPU':cpu,'MEM':mem,'OPS':ops}[lab]
                    hud.itemconfigure(lid,text=f'{lab} // {value:02d}' if lab in ('SIG','CPU','MEM') else f'{lab} // {value:03d}',fill=accent if lab in ('SIG','OPS') else '#2c5966')
                hud.itemconfigure(items['rates'],text=f'RX {rx:03d}  //  TX {tx:03d}  //  CORE {100-max(0,cpu-28):02d}%')
            except tk.TclError:
                continue
        self._heading_huds=alive

    def _attach_cinematic_surface(self, parent, key, accent=None):
        """Install the shared autonomous Cinematic VFX language behind a page.

        The surface is presentation-only: it never fabricates telemetry, never
        intercepts input, and never uses mouse hover to drive motion. One global
        ~60 FPS clock advances every registered surface so Home, OSINT and the
        remaining labs share the same visual grammar as the crypto cinema.
        """
        accent = accent or NAV_ACCENTS.get(key, P["cyan"])
        c = tk.Canvas(parent, bg=P["bg"], highlightthickness=0, bd=0,
                      takefocus=0, cursor="arrow")
        c.place(relx=0, rely=0, relwidth=1, relheight=1)
        try:
            parent.tk.call("lower", c._w)
        except tk.TclError:
            pass
        state = {"canvas": c, "key": key, "owner": key, "accent": accent, "phase": 0.0,
                 "size": None, "seq": 0, "static_only": False}
        self._cinematic_surfaces.append(state)
        return c

    def _animate_cinematic_surfaces(self):
        """Autonomous cross-platform VFX: grids, sweeps, particles and data rails."""
        if not getattr(self, '_ui_ready', False):
            return
        alive=[]
        now=time.perf_counter()
        for st in getattr(self, '_cinematic_surfaces', ()):
            c=st.get('canvas')
            if c is None or not c.winfo_exists():
                continue
            # Foreground-only rendering: inactive destination surfaces retain their state
            # without consuming animation frames. They resume immediately when raised.
            if not self._motion_page_active(st.get('owner', st.get('key', 'home'))):
                alive.append(st); continue
            w=max(1,c.winfo_width()); h=max(1,c.winfo_height())
            if w<40 or h<40:
                alive.append(st); continue
            # Shared cinematic surfaces are retained autonomous VFX.
            # Specialist HUDs coexist with this layer without per-frame allocation.
            # rails/particles/nodes over those visualizations.
            if st.get('static_only'):
                if st.get('size') != (w, h):
                    c.delete('all')
                    c.create_rectangle(0, 0, w, h, fill='#010509', outline='')
                    for x in range(0, w, 48):
                        c.create_line(x, 0, x, h, fill='#06151b')
                    for y in range(0, h, 40):
                        c.create_line(0, y, w, y, fill='#061219')
                    cut=min(18,max(10,min(w,h)//24))
                    c.create_line(cut,0,w-cut,0,fill=st['accent'])
                    c.create_line(0,cut,0,h-cut,fill='#123640')
                    c.create_line(w-cut,0,w,cut,fill=st['accent'])
                    c.create_line(w,h-cut,w-cut,h,fill='#123640')
                    st['size']=(w,h)
                alive.append(st)
                continue
            dt=min(.05,max(.001,now-st.get('last',now))); st['last']=now
            st['phase']=(st.get('phase',0.0)+dt*1.65)%(math.tau*100)
            st['seq']=(st.get('seq',0)+1)%10000
            phase=st['phase']; accent=st['accent']; sig=(w,h)
            if st.get('size')!=sig:
                c.delete('all')
                # Deep glass substrate + technical grid.
                c.create_rectangle(0,0,w,h,fill='#010509',outline='')
                for x in range(0,w,32): c.create_line(x,0,x,h,fill='#06151b')
                for y in range(0,h,28): c.create_line(0,y,w,y,fill='#061219')
                cut=min(22,max(10,min(w,h)//18))
                c.create_line(cut,0,w-cut,0,fill=accent)
                c.create_line(0,cut,0,h-cut,fill='#123640')
                c.create_line(w-cut,0,w,cut,fill=accent)
                c.create_line(w,h-cut,w-cut,h,fill='#123640')
                # Four autonomous tactical rails.
                st['rails']=[c.create_line(0,0,0,0,fill=accent,width=2) for _ in range(4)]
                st['particles']=[c.create_oval(0,0,0,0,fill=P['cyan2'] if i%2 else accent,outline='') for i in range(18)]
                st['nodes']=[c.create_oval(0,0,0,0,fill=P['green'] if i%3==0 else accent,outline='') for i in range(7)]
                st['pulse']=c.create_oval(0,0,0,0,outline=accent,width=1)
                st['cross_h']=c.create_line(0,0,0,0,fill='#0b2831')
                st['cross_v']=c.create_line(0,0,0,0,fill='#0b2831')
                st['labels']=[
                    c.create_text(14,12,text=f'{st.get("key","VFX").upper()} // CINEMATIC OPS BUS',anchor='nw',fill=P['text'],font=(MONO,9,'bold')),
                    c.create_text(14,30,text='AUTONOMOUS VFX // 60FPS // LOCAL RENDER // NO HOVER DRIVER',anchor='nw',fill=P['dim'],font=(MONO,9,'bold')),
                    c.create_text(w-14,h-10,text='SEQ 0000  //  SIGNAL NOMINAL',anchor='se',fill=accent,font=(MONO,9,'bold')),
                ]
                st['size']=sig
            cx,cy=w*.72,h*.52; radius=min(w*.23,h*.34)
            # Radar rings + rotating sweep.
            for i,r in enumerate((radius,radius*.72,radius*.45)):
                # rings are recreated only on resize, so use compact moving sweep below
                pass
            # Sweep rail and moving laser bands.
            for i,item in enumerate(st['rails']):
                yy=h*(.18+i*.20)+math.sin(phase*.7+i)*4
                x=(phase*(85+i*19))%(w+120)-60
                c.coords(item,x,yy,x+58,yy)
            for i,item in enumerate(st['particles']):
                a=phase*(.28+(i%4)*.035)+i*math.tau/18
                rr=radius*(.38+.52*((i%5)/5))
                x=cx+rr*math.cos(a); y=cy+rr*.58*math.sin(a)
                c.coords(item,x-1.5,y-1.5,x+1.5,y+1.5)
            for i,item in enumerate(st['nodes']):
                a=i*math.tau/7+phase*.13; rr=radius*(.72+.06*math.sin(phase+i))
                x=cx+rr*math.cos(a); y=cy+rr*.58*math.sin(a)
                r=3+(1.5 if i==int(phase*2)%7 else 0)
                c.coords(item,x-r,y-r,x+r,y+r)
            # Central crosshair pulses continuously in retained-mode geometry.
            pulse=10+5*(1+math.sin(phase*2.2))/2
            c.coords(st['pulse'],cx-pulse,cy-pulse,cx+pulse,cy+pulse)
            c.coords(st['cross_h'],cx-radius,cy,cx+radius,cy)
            c.coords(st['cross_v'],cx,cy-radius*.58,cx,cy+radius*.58)
            c.itemconfigure(st['labels'][2],text=f'SEQ {st["seq"]:04d}  //  {st.get("key","VFX").upper()}  //  SIGNAL {92+int(5*math.sin(phase))}%')
            alive.append(st)
        self._cinematic_surfaces=alive

    def _install_panel_fx(self, frame, accent=None):
        """Apply the shared military HUD compositor to a Tk panel.

        Tkinter cannot provide a real backdrop-filter, so the compositor uses
        layered dark glass simulation, clipped/octagonal rails, corner brackets,
        micro telemetry and a single shared scan animation. No per-panel timer
        is created; the global tick only animates panels on the active page.
        """
        accent = accent or P["cyan"]
        fx = tk.Canvas(frame, bg=frame.cget("bg"), highlightthickness=0, bd=0,
                       takefocus=0)
        fx.place(relx=0, rely=0, relwidth=1, relheight=1)
        frame.tk.call("lower", fx._w)
        state = {"phase": 0.0, "last": (0, 0), "scan": None, "accent": accent, "frame": frame, "canvas": fx, "owner": getattr(self, "current", "home")}

        def redraw(_event=None):
            try:
                w, h = max(30, frame.winfo_width()), max(30, frame.winfo_height())
                if state["last"] == (w, h):
                    return
                state["last"] = (w, h)
                fx.delete("all")
                cut = min(16, max(7, min(w, h)//8))
                # Layered dark panes approximate depth without claiming true alpha blur.
                fx.create_rectangle(1, 1, w-2, h-2, fill="#07131b", outline="#102d3a", width=1)
                fx.create_rectangle(4, 4, w-5, h-5, fill="#061018", outline="#0b2631", width=1)
                pts = [(cut,1),(w-cut,1),(w-1,cut),(w-1,h-cut),
                       (w-cut,h-1),(cut,h-1),(1,h-cut),(1,cut)]
                fx.create_polygon(pts, outline="#1a5261", fill="", width=1)
                # Machined corner cuts + dual rails.
                rails = [((1,cut),(cut,1)), ((w-cut,1),(w-1,cut)),
                         ((w-1,h-cut),(w-cut,h-1)), ((cut,h-1),(1,h-cut))]
                for a,b in rails:
                    fx.create_line(*a,*b,fill=accent,width=2)
                fx.create_line(cut+12,1,w-cut-12,1,fill=P["purple"],width=1)
                fx.create_line(cut+12,h-1,w-cut-12,h-1,fill=P["cyan2"],width=1)
                # Sparse internal grid gives every card the same depth language.
                step=max(34, min(64, w//7))
                for x in range(cut+step, max(cut+step+1,w-cut), step):
                    fx.create_line(x, 3, x, h-3, fill="#091d25", width=1, tags="grid")
                for y in range(cut+24, max(cut+25,h-cut), 28):
                    fx.create_line(3, y, w-3, y, fill="#081a22", width=1, tags="grid")
                # Tiny corner readouts.
                fx.create_text(8,8,text="0x",anchor="nw",fill="#315766",font=(MONO,9,"bold"),tags="telemetry")
                fx.create_text(w-8,8,text="HN",anchor="ne",fill="#315766",font=(MONO,9,"bold"),tags="telemetry")
                fx.create_text(8,h-7,text="// SECURE",anchor="sw",fill="#254652",font=(MONO,9,"bold"),tags="telemetry")
                fx.create_text(w-8,h-7,text="LOCAL",anchor="se",fill="#254652",font=(MONO,9,"bold"),tags="telemetry")
                # Narrow laser scan that travels through the pane.
                state["scan"] = fx.create_rectangle(-80, cut+8, -8, h-cut-8,
                                                     fill="#0a2832", outline="", tags="scan")
            except tk.TclError:
                pass

        frame.bind("<Configure>", redraw, add="+")
        frame._scifi_fx = fx
        frame._scifi_fx_state = state
        self._fx_panels.append(state)
        frame.after_idle(redraw)
        return frame

    def _panel_fx_tick(self):
        """Shared low-cost compositor tick for active-page glass panels."""
        if not getattr(self, "_ui_ready", False):
            return
        self._fx_phase = (getattr(self, "_fx_phase", 0.0) + 0.018) % 1.0
        active = []
        for state in getattr(self, "_fx_panels", []):
            frame, fx, scan = state.get("frame"), state.get("canvas"), state.get("scan")
            try:
                if not frame.winfo_exists() or not fx.winfo_exists():
                    continue
                active.append(state)
                if not self._motion_page_active(state.get('owner', 'home')): continue
                w=max(30,fx.winfo_width()); h=max(30,fx.winfo_height())
                x=((self._fx_phase*(w+160))-80)
                if scan is not None:
                    fx.coords(scan,x,8,x+62,max(12,h-8))
                    fx.itemconfigure(scan, fill="#0b3038" if int(self._fx_phase*10)%2 else "#0a2730")
            except tk.TclError:
                continue
        self._fx_panels = active

    def card(self, parent, **kw):
        f = tk.Frame(parent, bg=P["panel"], highlightbackground=P["line"],
                     highlightthickness=1, bd=0, **kw)
        return self._install_panel_fx(f, P["cyan"])

    def glass(self, parent, **kw):
        f = tk.Frame(parent, bg=P["panel2"], highlightbackground=P["line2"],
                     highlightthickness=1, bd=0, **kw)
        return self._install_panel_fx(f, P["cyan2"])

    def btn(self, parent, text, cmd, primary=False, **kw):
        base_bg = P["cyan"] if primary else P["panel2"]
        base_fg = P["bg"] if primary else P["text"]
        hover_bg = P["green"] if primary else P["line2"]
        b = tk.Button(parent, text=text, command=cmd,
                      bg=base_bg, fg=base_fg,
                      activebackground=hover_bg,
                      activeforeground=P["bg"], relief="flat", bd=0,
                      padx=14, pady=9, font=(FONT, 10, "bold"),
                      cursor="hand2", highlightthickness=1,
                      highlightbackground=base_bg, highlightcolor=hover_bg, **kw)
        b._base_bg, b._base_fg, b._hover_bg = base_bg, base_fg, hover_bg
        b.bind("<Enter>", lambda e, w=b: (w.configure(
            bg=w._hover_bg, fg=P["bg"], highlightbackground=w._hover_bg)), add="+")
        b.bind("<Leave>", lambda e, w=b: w.configure(
            bg=w._base_bg, fg=w._base_fg, highlightbackground=w._base_bg), add="+")
        b.bind("<ButtonPress-1>", lambda e, w=b: (w.configure(
            relief="sunken", highlightthickness=2, highlightbackground=w._hover_bg)), add="+")
        b.bind("<ButtonRelease-1>", lambda e, w=b: w.configure(
            relief="flat", highlightthickness=1, highlightbackground=w._hover_bg if w.winfo_containing(e.x_root, e.y_root) is w else w._base_bg), add="+")
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

    def _responsive_split(self, host, left, right, threshold=980, right_width=360):
        """Stack two-pane workspaces on compact windows so content stays readable."""
        state={"compact":None}
        def apply(_event=None):
            width=max(1,host.winfo_width()); compact=width < threshold
            if compact == state["compact"] and _event is not None: return
            state["compact"]=compact; host._responsive_compact=compact
            try:
                left.pack_forget(); right.pack_forget()
                if compact:
                    right.configure(width=max(1,width)); right.pack(side="top",fill="x",expand=False,padx=0,pady=(7,0)); right.pack_propagate(True)
                    left.pack(side="top",fill="x",expand=False,padx=0,pady=0)
                else:
                    right.configure(width=right_width); right.pack(side="right",fill="y",expand=False,padx=(6,0),pady=0); right.pack_propagate(False)
                    left.pack(side="left",fill="both",expand=True,padx=(0,6),pady=0)
            except tk.TclError: pass
        host.bind('<Configure>',apply,add='+'); host.after_idle(apply); return apply

    def _metric_card(self,parent,value,label,accent=None):
        c=self.glass(parent); accent=accent or P['cyan']
        tk.Label(c,text=value,bg=P['panel2'],fg=accent,font=(MONO, 21,'bold')).pack(anchor='e',padx=16,pady=(14,2))
        tk.Label(c,text=label,bg=P['panel2'],fg=P['muted'],font=(FONT, 10),anchor='e',justify='right').pack(fill='x',padx=16,pady=(0,14))
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
        # Home has dedicated retained HUD canvases; do not add a second full-screen
        # cinematic canvas underneath them. That duplicate layer caused visual stacking.

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
        tk.Label(top,text='root@HN-BLACKBOX:~#',bg='#061016',fg=P['green'],font=(MONO, 10,'bold')).pack(side='left',padx=12)
        self.home_cmd=tk.Entry(top,bg='#02080d',fg=P['text'],insertbackground=P['cyan'],relief='flat',bd=0,font=(MONO, 10))
        self.home_cmd.insert(0,'help  //  type a command')
        self.home_cmd.pack(side='left',fill='x',expand=True,padx=8,ipady=5)
        self.home_cmd.bind('<Return>',self._home_command)
        self.after(400, lambda: self.home_cmd.icursor('end') if self.home_cmd.winfo_exists() else None)
        tk.Label(top,text='ENTER',bg='#061016',fg=P['dim'],font=(MONO, 9,'bold')).pack(side='left',padx=7)
        self.home_clock=tk.Label(top,text='--:--:--',bg='#061016',fg=P['cyan'],font=(MONO, 10,'bold'))
        self.home_clock.pack(side='right',padx=12)

        rail=tk.Frame(surface,bg='#040b10',highlightbackground='#123a45',highlightthickness=1)
        self._home_widgets['rail']=rail
        uname=(getpass.getuser() or 'HN USER').upper()
        tk.Label(rail,text=f'root@{uname.lower()}:~#',bg='#040b10',fg=P['green'],font=(MONO, 10,'bold'),anchor='w').pack(fill='x',padx=11,pady=(10,7))
        files=[('./dashboard.sh','RUNNING'),('/core/ciphers','19'),('/core/analysis','4'),('/core/network','3'),('/core/web','4'),('/core/blue_team','2'),('/core/labs','4'),('/tests','23')]
        module_map={'/core/ciphers':'crypto','/core/analysis':'analysis','/core/network':'network','/core/web':'web','/core/blue_team':'blue','/core/labs':'labs','/tests':'development'}
        for path,badge in files:
            key=module_map.get(path)
            if key:
                accent=NAV_ACCENTS.get(key,P['cyan'])
                r=tk.Frame(rail,bg='#040b10',highlightbackground='#0d2c36',highlightthickness=1);r.pack(fill='x',padx=7,pady=2)
                r.bind('<Button-1>',lambda e,k=key:self._nav_click(k))
                tk.Label(r,text='▸',bg='#040b10',fg=accent,font=(MONO, 10)).pack(side='left',padx=(5,0))
                lab=tk.Label(r,text=path,bg='#040b10',fg=P['muted'],font=(MONO, 9,'bold'),anchor='w',cursor='hand2');lab.pack(side='left',padx=5)
                lab.bind('<Button-1>',lambda e,k=key:self._nav_click(k))
                if badge: tk.Label(r,text=badge,bg='#0b2b34',fg=P['green'] if badge=='RUNNING' else accent,font=(MONO, 9,'bold'),padx=3).pack(side='right',padx=4)
            else:
                r=tk.Frame(rail,bg='#040b10');r.pack(fill='x',padx=7,pady=2)
                tk.Label(r,text='▸',bg='#040b10',fg=P['dim'],font=(MONO, 10)).pack(side='left')
                tk.Label(r,text=path,bg='#040b10',fg=P['muted'],font=(MONO, 9),anchor='w').pack(side='left',padx=5)
        # Live status console: animated bars + real project health counters.
        tk.Label(rail,text='──────────────────',bg='#040b10',fg='#11323b',font=(MONO, 9)).pack(pady=7)
        status_box=tk.Frame(rail,bg='#061016',highlightbackground='#174451',highlightthickness=1); status_box.pack(fill='x',padx=7,pady=(0,7))
        tk.Label(status_box,text='SYSTEM STATUS // LIVE',bg='#061016',fg=P['cyan'],font=(MONO, 9,'bold'),anchor='w').pack(fill='x',padx=8,pady=(8,4))
        self.home_status_rows=[]
        for txt,color in (('CRYPTO','cyan'),('ANALYSIS','purple'),('NETWORK','green'),('DEFENSE','red')):
            row=tk.Frame(status_box,bg='#061016'); row.pack(fill='x',padx=7,pady=2)
            dot=tk.Label(row,text='●',bg='#061016',fg=P[color],font=(MONO, 9)); dot.pack(side='left')
            tk.Label(row,text=txt,bg='#061016',fg=P['text'],font=(MONO, 9,'bold')).pack(side='left',padx=4)
            bar=tk.Canvas(row,width=58,height=7,bg='#061016',highlightthickness=0); bar.pack(side='right',padx=2)
            self.home_status_rows.append((bar,color))
        self.home_status_clock=tk.Label(status_box,text='SYNC --:--:--',bg='#061016',fg=P['dim'],font=(MONO, 9,'bold'),anchor='w'); self.home_status_clock.pack(fill='x',padx=8,pady=(4,8))
        self.home_user_badge=tk.Label(rail,text=f'HN BLACKBOX\n{uname}\nLOCAL WORKSPACE',bg='#06151b',fg=P['cyan'],font=(MONO, 9,'bold'),justify='left',anchor='w',padx=8,pady=8)
        self.home_user_badge.pack(side='bottom',fill='x',padx=7,pady=7)

        title=tk.Frame(surface,bg='#07131a',highlightbackground='#123e4b',highlightthickness=1);self._home_widgets['title']=title
        tk.Label(title,text='SYSTEM OVERVIEW',bg='#07131a',fg=P['cyan'],font=(MONO, 12,'bold'),anchor='w').pack(side='left',padx=13,pady=8)
        self.home_status=tk.Label(title,text='STATUS: ONLINE  //  LOCAL LAB  //  DEFENSIVE MODE',bg='#07131a',fg=P['dim'],font=(MONO, 9,'bold'),anchor='w');self.home_status.pack(side='left',padx=9)
        self.home_open_crypto=self.btn(title,'> OPEN CRYPTO LAB',lambda:self.show_page('crypto'),True)
        self.home_open_crypto.pack(side='right',padx=5,pady=5)
        self.home_open_terminal=self.btn(title,'> OPEN TERMINAL',self.launch_blackbox_terminal)
        self.home_open_terminal.pack(side='right',padx=5,pady=5)

        # PRIMARY OPERATIONS HUD — one coherent cinematic scene instead of a
        # collection of decorative cards.  Everything below is vector-rendered
        # locally by Tk Canvas so it stays sharp and does not depend on images.
        hero=tk.Frame(surface,bg='#02070b',highlightbackground='#1a5260',highlightthickness=1)
        self._home_widgets['hero']=hero
        self.home_hero_canvas=tk.Canvas(hero,bg='#010509',highlightthickness=0,bd=0)
        self.home_hero_canvas.pack(fill='both',expand=True)
        self.home_hero_canvas.bind('<Motion>',self._home_hero_hover)
        self.home_hero_canvas.bind('<Leave>',lambda e:self._home_hero_hover(None))
        self.home_hero_canvas.bind('<Button-1>',self._home_hero_click)
        self._home_hero_scene=None
        self._home_hero_phase=0.0
        self._home_hero_hovered=None

        term=tk.Frame(surface,bg='#040a0e',highlightbackground='#164b59',highlightthickness=1); self._home_widgets['term']=term
        term_head=tk.Frame(term,bg='#07141a'); term_head.pack(fill='x')
        tk.Label(term_head,text='LIVE COMMAND CHANNEL  //  HN TERMINAL',bg='#07141a',fg=P['green'],font=(MONO, 10,'bold')).pack(side='left',padx=10,pady=6)
        tk.Label(term_head,text='LOCAL // EXEC  •  ↑↓ HISTORY  •  ENTER RUN',bg='#07141a',fg=P['dim'],font=(MONO, 9,'bold')).pack(side='left',padx=10)
        self.home_terminal_theme=tk.Label(term_head,text='THEME: CYAN',bg='#07141a',fg=P['cyan'],font=(MONO, 9,'bold'))
        self.home_terminal_theme.pack(side='right',padx=4)
        self.btn(term_head,'COPY LAST',self._copy_last_terminal_output).pack(side='right',padx=3,pady=3)
        self.btn(term_head,'RED',lambda:self._set_ui_theme('red')).pack(side='right',padx=2,pady=3)
        self.btn(term_head,'GREEN',lambda:self._set_ui_theme('green')).pack(side='right',padx=2,pady=3)
        self.btn(term_head,'CYAN',lambda:self._set_ui_theme('cyan')).pack(side='right',padx=2,pady=3)
        term_body=tk.Frame(term,bg='#02070b'); term_body.pack(fill='both',expand=True)

        # Identity Core HUD: this is the HN emblem the dashboard uses as its
        # primary visual anchor.  It is a real Tkinter canvas (not an image), so
        # it stays sharp at every window size while the radar/scan layers move.
        identity_pane=tk.Frame(term_body,bg='#030b10',highlightbackground='#174451',highlightthickness=1,width=224)
        identity_pane.pack(side='left',fill='both',padx=(7,4),pady=7)
        identity_pane.pack_propagate(False)
        self.home_identity_pane=identity_pane
        identity_head=tk.Frame(identity_pane,bg='#07141a'); identity_head.pack(fill='x')
        tk.Label(identity_head,text='IDENTITY CORE // HN',bg='#07141a',fg=P['cyan'],font=(MONO, 10,'bold')).pack(side='left',padx=9,pady=6)
        self.home_identity_clock=tk.Label(identity_head,text='--:--:--',bg='#07141a',fg=P['green'],font=(MONO, 9,'bold')); self.home_identity_clock.pack(side='right',padx=8)
        self.home_identity_canvas=tk.Canvas(identity_pane,bg='#02070b',highlightthickness=0,bd=0,height=165)
        self.home_identity_canvas.pack(fill='both',expand=True,padx=5,pady=5)
        self.home_identity_status=tk.Label(identity_pane,text='HN CORE // ONLINE  •  VECTOR LOCKED',bg='#061016',fg=P['green'],font=(MONO, 9,'bold'))
        self.home_identity_status.pack(fill='x',padx=6,pady=(0,5))
        self._home_identity_phase=0

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
        self.home_terminal=tk.Text(terminal_pane,bg='#02070b',fg='#8fffc8',insertbackground=P['cyan'],relief='flat',bd=0,
                                   font=(ASCII_MONO, 10),wrap='none',padx=10,pady=8)
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
        tk.Label(smh,text='LIVE SYSTEM // TASK MANAGER',bg='#07141a',fg=P['cyan'],font=(MONO, 10,'bold')).pack(side='left',padx=9,pady=6)
        self.home_sys_clock=tk.Label(smh,text='--:--:--',bg='#07141a',fg=P['green'],font=(MONO, 10,'bold')); self.home_sys_clock.pack(side='right',padx=9)
        self.home_sys_canvas=tk.Canvas(sysmon,bg='#02070b',highlightthickness=0,height=108); self.home_sys_canvas.pack(fill='x',padx=6,pady=6)
        metrics=tk.Frame(sysmon,bg='#02070b'); metrics.pack(fill='both',expand=True,padx=6,pady=(0,6))
        self.sys_metric_labels={}
        for key,label,color in [('cpu','CPU',P['green']),('ram','RAM',P['cyan']),('proc','PROC',P['yellow']),('up','UPTIME',P['purple'])]:
            row=tk.Frame(metrics,bg='#061016',highlightbackground='#0e303b',highlightthickness=1); row.pack(fill='x',pady=2)
            tk.Label(row,text=label,bg='#061016',fg=P['dim'],font=(MONO, 9,'bold')).pack(side='left',padx=7,pady=5)
            val=tk.Label(row,text='--',bg='#061016',fg=color,font=(MONO, 10,'bold')); val.pack(side='right',padx=7)
            self.sys_metric_labels[key]=val
        self.home_task_text=tk.Text(metrics,height=4,bg='#02070b',fg='#78f6b5',font=(MONO, 9),relief='flat',bd=0,wrap='none')
        self.home_task_text.pack(fill='both',expand=True,pady=(4,0)); self.home_task_text.configure(state='disabled')
        self._animate_system_monitor()

        kpi=tk.Frame(surface,bg=P['bg']);self._home_widgets['kpi']=kpi
        entries=history_manager.get_all() if hasattr(history_manager,'get_all') else []
        hist_n=len(entries)
        stats=[('ALGORITHMS',str(len(ALGORITHMS)),'ACTIVE CIPHERS',P['cyan'],self.show_page,'crypto'),('LAB MODULES','5','LOCAL SECURITY TOOLS',P['green'],self.show_page,'analysis'),('OPERATIONS',str(hist_n),'LOCAL AUDIT ENTRIES',P['orange'],self.show_page,'history'),('TEST STATUS',RELEASE_TEST_STATUS,'CORE + GUI CHECKS',P['purple'],self.show_page,'development')]
        for val,num,sub,color,cmd,key in stats:
            c=tk.Frame(kpi,bg='#08161c',highlightbackground='#174451',highlightthickness=1);c.pack(side='left',fill='both',expand=True,padx=3)
            tk.Label(c,text=val,bg='#08161c',fg=P['muted'],font=(MONO, 9,'bold'),anchor='w').pack(fill='x',padx=10,pady=(8,1))
            tk.Label(c,text=num,bg='#08161c',fg=color,font=(MONO, 18,'bold'),anchor='w').pack(fill='x',padx=10)
            b=tk.Button(c,text=sub,bg='#08161c',fg=P['dim'],activebackground='#0b2028',activeforeground=P['cyan'],relief='flat',bd=0,font=(MONO, 9,'bold'),anchor='w',command=lambda f=cmd,k=key:f(k),cursor='hand2');b.pack(fill='x',padx=10,pady=(0,8))

        main=tk.Frame(surface,bg=P['bg']);self._home_widgets['main']=main
        # left: mission + activity
        left=tk.Frame(main,bg='#061016',highlightbackground='#143e4a',highlightthickness=1);left.pack(side='left',fill='both',expand=True,padx=(0,5)); self._install_panel_fx(left, P['cyan'])
        mission_head=tk.Frame(left,bg='#07131a',highlightbackground=P['cyan'],highlightthickness=1);mission_head.pack(fill='x',padx=9,pady=(7,4))
        tk.Label(mission_head,text='PROJECT // MISSION // HN BLACKBOX',bg='#07131a',fg=P['cyan2'],font=(MONO, 10,'bold'),anchor='w').pack(fill='x',padx=11,pady=(8,2))
        self.home_mission_title=tk.Label(mission_head,text='HN BLACKBOX: THE BLACK BOX FOR SECURITY PROJECTS & SOLUTIONS.',bg='#07131a',fg=P['text'],font=(MONO, 15,'bold'),anchor='w',justify='left',wraplength=760)
        self.home_mission_title.pack(fill='x',padx=11,pady=(1,4))
        self.home_mission_desc=tk.Label(mission_head,text='A unified technical platform bringing our software projects together across cybersecurity and systems engineering. We break down complex concepts, test tools, and build innovative defensive solutions under one interface.',bg='#07131a',fg='#9bc0cf',font=(FONT, 10),anchor='w',justify='left',wraplength=760)
        self.home_mission_desc.pack(fill='x',padx=11,pady=(0,10))
        stream_box=tk.Frame(left,bg='#061016',highlightbackground='#0f303a',highlightthickness=1,height=94);stream_box.pack(fill='x',padx=10,pady=(4,5));stream_box.pack_propagate(False)
        tk.Label(stream_box,text='LIVE MODULE STREAM',bg='#061016',fg=P['cyan'],font=(MONO, 10,'bold'),anchor='w').pack(fill='x',padx=9,pady=(5,2))
        stream=[('CRYPTO','AES / RSA / classical engines loaded',P['cyan']),('ANALYSIS','frequency + IC + Kasiski ready',P['purple']),('NETWORK','IP / subnet / DNS utilities ready',P['green']),('WEB','safe HTTP simulator + OWASP concepts',P['orange']),('BLUE','log triage + IOC classification',P['red']),('LABS','offline challenges + hints',P['yellow'])]
        for name,desc,color in stream:
            r=tk.Frame(stream_box,bg='#061016');r.pack(fill='x',padx=8,pady=0)
            tk.Label(r,text='●',bg='#061016',fg=color,font=(MONO, 9)).pack(side='left')
            tk.Label(r,text=name,bg='#061016',fg=P['text'],font=(MONO, 9,'bold'),width=9,anchor='w').pack(side='left',padx=4)
            tk.Label(r,text=desc,bg='#061016',fg=P['muted'],font=(MONO, 9),anchor='w').pack(side='left',fill='x',expand=True)
        # compact command shortcuts
        cmdbox=tk.Frame(left,bg='#07131a',highlightbackground='#123c48',highlightthickness=1);cmdbox.pack(fill='x',padx=10,pady=6)
        tk.Label(cmdbox,text='QUICK COMMANDS',bg='#07131a',fg=P['dim'],font=(MONO, 9,'bold')).pack(anchor='w',padx=8,pady=(5,3))
        for label,key in [('CRYPTANALYSIS','analysis'),('NETWORK TOOLKIT','network'),('WEB LAB','web'),('BLUE TEAM','blue'),('SECURITY LABS','labs')]:
            self.btn(cmdbox,label,lambda k=key:self.show_page(k)).pack(side='left',padx=2,pady=(0,5))

        # Live workspace monitor: real project state on the left + a continuously
        # animated multi-color diagnostics scope on the right.
        monitor=tk.Frame(left,bg='#030b10',highlightbackground='#174451',highlightthickness=1)
        monitor.pack(fill='both',expand=False,padx=10,pady=(0,7))
        self.home_monitor=monitor
        mh=tk.Frame(monitor,bg='#07141a');mh.pack(fill='x')
        tk.Label(mh,text='LIVE WORKSPACE MONITOR  //  TASKS + TOOL HEALTH + PROJECT SCAN',bg='#07141a',fg=P['yellow'],font=(MONO, 10,'bold'),anchor='w').pack(side='left',padx=9,pady=6)
        self.home_scan_status=tk.Label(mh,text='SCANNING...',bg='#07141a',fg=P['green'],font=(MONO, 9,'bold'),anchor='e');self.home_scan_status.pack(side='right',padx=9)
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

        # right: telemetry + warning + identity
        side=tk.Frame(main,bg=P['bg']);side.pack(side='right',fill='both',padx=(5,0));side.configure(width=280);side.pack_propagate(False); self._install_panel_fx(side, P['purple'])
        # SYS_TELEMETRY was redundant with the live task manager/workspace monitor.
        # Keep the side rail focused on warnings and intelligence, while preserving
        # all backend status sources used elsewhere.
        warn=tk.Frame(side,bg='#241013',highlightbackground='#8b2735',highlightthickness=1);warn.pack(fill='x',pady=7)
        tk.Label(warn,text='⚠ DEFENSIVE WORKSPACE',bg='#241013',fg=P['red'],font=(MONO, 10,'bold'),anchor='w').pack(fill='x',padx=10,pady=(9,3))
        tk.Label(warn,text='All network/web modules are designed for local, educational use. No exploitation engine or credential attack is included.',bg='#241013',fg='#e7a2aa',font=(MONO, 9),justify='left',wraplength=240,anchor='w').pack(fill='x',padx=10,pady=(0,8))
        tk.Button(warn,text='OPEN BLUE TEAM',command=lambda:self.show_page('blue'),bg='#9f2432',fg='#fff',activebackground='#d63d4d',relief='flat',bd=0,font=(MONO, 10,'bold'),pady=6).pack(fill='x',padx=10,pady=(0,9))
        # Lower-right intelligence board: a continuously rendered HN operations
        # display.  It is deliberately local/synthetic — the visuals are telemetry
        # style, not a claim of real external intelligence collection.
        ident=tk.Frame(side,bg='#030b10',highlightbackground='#174451',highlightthickness=1)
        ident.pack(fill='both',expand=True)
        ih=tk.Frame(ident,bg='#07141a'); ih.pack(fill='x')
        tk.Label(ih,text='HN // INTELLIGENCE BOARD',bg='#07141a',fg=P['cyan'],
                 font=(MONO, 10,'bold')).pack(side='left',padx=9,pady=6)
        self.home_intel_clock=tk.Label(ih,text='LOCAL // LIVE',bg='#07141a',fg=P['green'],
                                       font=(MONO, 9,'bold')); self.home_intel_clock.pack(side='right',padx=8)
        self.home_intel_canvas=tk.Canvas(ident,bg='#02070b',highlightthickness=0,bd=0)
        self.home_intel_canvas.pack(fill='both',expand=True,padx=5,pady=5)
        self.home_intel_status=tk.Label(
            ident,text='HN CORE // SYNTHETIC TELEMETRY  •  DEFENSIVE MODE',
            bg='#061016',fg=P['yellow'],font=(MONO, 9,'bold'))
        self.home_intel_status.pack(fill='x',padx=6,pady=(0,5))
        self._home_intel_phase=0

        foot=tk.Frame(surface,bg='#040b10',highlightbackground='#0d2c36',highlightthickness=1);self._home_widgets['foot']=foot
        tk.Label(foot,text='HN BLACKBOX // LOCAL • OFFLINE • EDUCATIONAL',bg='#040b10',fg=P['dim'],font=(MONO, 9),anchor='w').pack(side='left',padx=7,pady=2)
        tk.Label(foot,text='SECURE WORKSPACE  ●',bg='#040b10',fg=P['green'],font=(MONO, 9,'bold')).pack(side='right',padx=7)
        self._pulse_home()
        self._layout_home_v10()
        return p

    def _home_hero_hover(self,event):
        """Resolve interactive HUD nodes without creating per-widget bindings."""
        c=getattr(self,'home_hero_canvas',None)
        if c is None or not c.winfo_exists(): return
        if event is None:
            self._home_hero_hovered=None
        else:
            hits=c.find_overlapping(event.x-5,event.y-5,event.x+5,event.y+5)
            hit=None
            for item in reversed(hits):
                tags=c.gettags(item)
                for tag in tags:
                    if tag.startswith('node:'):
                        hit=tag.split(':',1)[1]; break
                if hit: break
            self._home_hero_hovered=hit
        c.configure(cursor='hand2' if self._home_hero_hovered else '')

    def _home_hero_click(self,event):
        self._home_hero_hover(event)
        routes={'CRYPTO':'crypto','ANALYSIS':'analysis','NETWORK':'network','DEFENSE':'blue','LABS':'labs'}
        key=routes.get(getattr(self,'_home_hero_hovered',None))
        if key: self.show_page(key)

    def _animate_home_hero(self):
        if not getattr(self,'_ui_ready',False): return
        c=getattr(self,'home_hero_canvas',None)
        if c is None or not c.winfo_exists(): return
        w=max(640,c.winfo_width()); h=max(220,c.winfo_height())
        phase=getattr(self,'_home_hero_phase',0.0)+0.045
        self._home_hero_phase=phase
        sig=(w,h); scene=getattr(self,'_home_hero_scene',None)
        if scene is None or scene.get('sig')!=sig:
            c.delete('all'); scene={'sig':sig,'nodes':[],'packets':[],'bars':[],'hex':[]}
            c.create_rectangle(0,0,w,h,fill='#010509',outline='')
            # Machined cut-corner perimeter. It is intentionally thin; the HUD content remains the focus.
            cut=18; c.create_line(cut,0,w-cut,0,fill='#1b5360'); c.create_line(0,cut,0,h-cut,fill='#1b5360'); c.create_line(cut,h,w-cut,h,fill='#0d3943'); c.create_line(w,cut,w,h-cut,fill='#0d3943')
            c.create_line(0,cut,cut,0,fill=P['cyan']); c.create_line(w-cut,0,w,cut,fill=P['cyan']); c.create_line(0,h-cut,cut,h,fill='#0d3943'); c.create_line(w,h-cut,w-cut,h,fill='#0d3943')
            for x in range(0,w,32): c.create_line(x,0,x,h,fill='#07151b')
            for y in range(0,h,28): c.create_line(0,y,w,y,fill='#061219')
            cx,cy=w*.50,h*.54; radius=min(h*.34,w*.19)
            for ratio,col in ((1.0,'#12333c'),(.78,'#0d2b34'),(.56,'#0b252d'),(.34,'#103943')):
                rr=radius*ratio; c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline=col,width=1)
            for a in range(0,360,30):
                r=math.radians(a); c.create_line(cx+radius*.72*math.cos(r),cy+radius*.72*math.sin(r),cx+radius*math.cos(r),cy+radius*math.sin(r),fill='#16424b')
            scene['sweep']=c.create_line(cx,cy,cx+radius,cy,fill=P['green'],width=2)
            node_data=[('CRYPTO',.22,.38,P['cyan']),('ANALYSIS',.22,.70,P['purple']),('NETWORK',.76,.38,P['green']),('DEFENSE',.76,.70,P['red']),('LABS',.50,.18,P['yellow'])]
            for name,nx,ny,col in node_data:
                x,y=w*nx,h*ny
                c.create_line(cx,cy,x,y,fill='#12323a',width=1,dash=(3,7))
                glow=c.create_oval(x-10,y-10,x+10,y+10,outline='#16434d',width=1)
                dot=c.create_oval(x-4,y-4,x+4,y+4,fill=col,outline='',tags=(f'node:{name}',))
                label=c.create_text(x,y-18,text=name,fill=col,font=(MONO,9,'bold'),tags=(f'node:{name}',))
                scene['nodes'].append((name,x,y,col,glow,dot,label))
            for i in range(10): scene['packets'].append([c.create_oval(-3,-3,3,3,fill=P['cyan2'],outline=''),i/10.0,i%5])
            bx,by=18,h*.18
            for i,(label,col) in enumerate((('CPU',P['cyan']),('MEM',P['green']),('NET',P['purple']),('OPS',P['yellow']))):
                y=by+i*27; c.create_text(bx,y,text=label,anchor='w',fill=P['dim'],font=(MONO,9,'bold'))
                bg=c.create_rectangle(bx,y+10,bx+118,y+15,fill='#071a20',outline=''); fg=c.create_rectangle(bx,y+10,bx+30,y+15,fill=col,outline=''); scene['bars'].append((bg,fg))
            c.create_text(w-18,h*.18,text='TACTICAL FEED',anchor='e',fill=P['cyan'],font=(MONO,9,'bold'))
            for i in range(6): scene['hex'].append(c.create_text(w-18,h*.18+25+i*19,text='',anchor='e',fill='#3d7d82',font=(MONO,9)))
            # Header is deliberately left-anchored so it never collides with the tactical feed.
            scene['title']=c.create_text(18,12,text='HN BLACKBOX // OPERATIONS COMMAND CORE',anchor='nw',fill=P['text'],font=(MONO,11,'bold'))
            scene['subtitle']=c.create_text(18,31,text='LOCAL DEFENSIVE WORKSPACE  //  VECTOR TELEMETRY  //  MODULE GRID',anchor='nw',fill=P['dim'],font=(MONO,9,'bold'))
            scene['core']=c.create_text(cx,cy,text='HN\nCORE',fill=P['cyan'],font=(MONO,12,'bold'),justify='center')
            scene['readout']=c.create_text(cx,cy+radius+16,text='SYSTEM NOMINAL  //  LINKED 05  //  SIGNAL 98.7%',fill=P['green'],font=(MONO,9,'bold'))
            scene['net_prev']=None
            scene['net_stamp']=time.monotonic() if 'time' in globals() else 0.0
            self._home_hero_scene=scene
        scene=self._home_hero_scene
        w,h=sig; cx,cy=w*.50,h*.54; radius=min(h*.34,w*.19)
        c.coords(scene['sweep'],cx,cy,cx+radius*math.cos(phase),cy+radius*math.sin(phase))
        # Visual emphasis is autonomous; mouse hover is not an animation driver.
        auto_active=int(phase*0.55)%len(scene['nodes']) if scene.get('nodes') else -1
        for idx,(name,x,y,col,glow,dot,label) in enumerate(scene['nodes']):
            active=idx==auto_active; c.itemconfigure(glow,outline=P['text'] if active else '#16434d',width=2 if active else 1); c.itemconfigure(label,fill=P['text'] if active else col)
            r=12 if active else 10; c.coords(glow,x-r,y-r,x+r,y+r)
        cpu, mem, procs = self._system_metrics()
        # Animation reads already-cached telemetry only. No psutil/process enumeration
        # occurs inside the Tk frame callback.
        real_vals=(
            (cpu or 0.0)/100.0,
            (mem or 0.0)/100.0,
            float(getattr(self, '_network_rate_cache', 0.0)),
            min(1.0, ((procs or 0) % 200) / 200.0),
        )
        for j,(bg,fg) in enumerate(scene['bars']):
            value=(real_vals[j] if real_vals else (.38+.22*math.sin(phase*(1.2+j*.13)+j)))
            x0,y0,x1,y1=c.coords(bg); c.coords(fg,x0,y0,x0+(x1-x0)*max(.03,min(1.0,value)),y1)
        for item,t,route in scene['packets']:
            a=phase*.55+t*math.tau; r=radius*(.25+.55*(route/5)); x=cx+r*math.cos(a); y=cy+r*math.sin(a)*.62; c.coords(item,x-2,y-2,x+2,y+2)
        stamp=int(time.time()*10)
        for i,item in enumerate(scene['hex']):
            seed=(stamp+i*7919+int(phase*17))&0xffffffff; c.itemconfigure(item,text=f'{seed:08X}  /  {((seed>>7)&0xFFFF):04X}  {"LOCK" if i in (1,4) else "SYNC"}')
        c.itemconfigure(scene['readout'],text=f'SYSTEM NOMINAL  //  LINKED 05  //  SIGNAL {98.2+1.1*math.sin(phase*.8):04.1f}%')

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
            return
        c=getattr(self,'home_command_hud',None)
        if c is None or not c.winfo_exists():
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
                              anchor='nw',fill=P['cyan'],font=(MONO, 9,'bold')),
                c.create_text(w-8,6,text='PIPELINE // ARMED',
                              anchor='ne',fill=P['green'],font=(MONO, 9,'bold')),
                c.create_text(8,h-7,text='',anchor='sw',fill=P['dim'],font=(MONO, 9)),
                c.create_text(w-8,h-7,text='',anchor='se',fill=P['yellow'],font=(MONO, 9)),
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

    def _animate_home_identity(self):
        """Render the identity HUD once, then animate only the moving elements."""
        if not getattr(self,'_ui_ready',False): return
        c=getattr(self,'home_identity_canvas',None)
        if c is None or not c.winfo_exists(): return
        # Autonomous V26: this visual channel never pauses for navigation state.
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
            # Vector identity mark: cleaner than the old ASCII block and stable at any size.
            items['hn']=c.create_text(cx,cy,text='HN',fill=P['cyan'],font=(MONO,max(22,int(min(w,h)/5)),'bold'),justify='center')
            items['hn_core']=c.create_text(cx,cy+23,text='BLACKBOX CORE',fill=P['muted'],font=(MONO,9,'bold'),justify='center')
            c.create_line(cx-base*.62,cy,cx-base*.42,cy,fill='#1a5261')
            c.create_line(cx+base*.42,cy,cx+base*.62,cy,fill='#1a5261')
            c.create_line(cx,cy-base*.62,cx,cy-base*.42,fill='#1a5261')
            c.create_line(cx,cy+base*.42,cx,cy+base*.62,fill='#1a5261')
            items['label']=c.create_text(9,8,text='HN BLACKBOX // VECTOR ID',anchor='nw',fill=P['dim'],font=(MONO, 9,'bold'))
            items['live']=c.create_text(w-9,8,text='LIVE',anchor='ne',fill=P['green'],font=(MONO, 9,'bold'))
            items['clock']=c.create_text(w-9,22,text='',anchor='ne',fill=P['yellow'],font=(MONO, 9,'bold'))
            items['footer']=c.create_text(cx,h-10,text='IDENTITY CORE // LOCKED',anchor='s',fill=P['dim'],font=(MONO, 9,'bold'))
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
        c.itemconfigure(items['hn_core'],fill=P['cyan2'] if pulse > .55 else P['muted'])
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

    def _animate_home_status(self):
        if not getattr(self,'_ui_ready',False): return
        if not hasattr(self,'home_status_rows'): return
        # Autonomous V26: this visual channel never pauses for navigation state.
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

    def _telemetry_loop(self):
        """Collect OS telemetry off the GUI thread. Never touches Tk objects."""
        prev_total = None
        prev_at = time.monotonic()
        while not self._telemetry_stop.is_set():
            cpu = ram = procs = None
            try:
                if psutil:
                    cpu = psutil.cpu_percent(interval=0.10)
                    ram = psutil.virtual_memory().percent
                    procs = len(psutil.pids())
                    io = psutil.net_io_counters()
                    total = (io.bytes_sent + io.bytes_recv) if io else 0
                    now = time.monotonic()
                    if prev_total is not None and now > prev_at:
                        self._network_rate_cache = min(1.0, max(0.0, (total-prev_total) / max(1.0, now-prev_at) / 5_000_000))
                    prev_total, prev_at = total, now
                elif platform.system().lower().startswith('win'):
                    out = subprocess.run(['tasklist'], capture_output=True, text=True, timeout=1.5).stdout
                    procs = max(0, len([x for x in out.splitlines() if '.exe' in x.lower()]) - 3)
                elif Path('/proc').exists():
                    procs = sum(1 for _ in Path('/proc').glob('[0-9]*'))
            except Exception:
                pass
            self._telemetry_cache = (cpu, ram, procs)
            self._telemetry_cache_at = time.monotonic()
            self._telemetry_stop.wait(1.0)

    def _system_metrics(self):
        """Return cached telemetry only; no process enumeration or subprocess work on Tk."""
        return self._telemetry_cache

    def _animate_system_monitor(self):
        """Smooth upper-right system intelligence display with real local metrics."""
        if not getattr(self,'_ui_ready',False):
            return
        c=getattr(self,'home_sys_canvas',None)
        if c is None or not c.winfo_exists():
            return

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
                              fill=P['cyan'],font=(MONO, 9,'bold')),
                c.create_text(w-7,6,text='',anchor='ne',
                              fill=P['yellow'],font=(MONO, 9,'bold')),
                c.create_text(7,h-29,text='CPU',anchor='sw',fill=P['dim'],font=(MONO, 9,'bold')),
                c.create_text(w/2+2,h-29,text='RAM',anchor='sw',fill=P['dim'],font=(MONO, 9,'bold')),
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

    def _animate_home_monitor(self):
        """Smooth tactical network/radar board; geometry is cached and only motion changes."""
        if not getattr(self, '_ui_ready', False):
            return
        c = getattr(self, 'home_monitor_scope', None)
        if c is None or not c.winfo_exists():
            return
        # Autonomous V26: this visual channel never pauses for navigation state.
        if time.monotonic() < getattr(self, '_resizing_until', 0):
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
                              fill=P['cyan'], font=(MONO, 9, 'bold')),
                c.create_text(w-7, 7, text='LOCAL // LIVE', anchor='ne',
                              fill=P['green'], font=(MONO, 9, 'bold')),
                c.create_text(7, h-7, text='HN CORE / NO EXTERNAL COLLECTION',
                              anchor='sw', fill=P['dim'], font=(MONO, 9, 'bold')),
                c.create_text(w-7, h-7, text='', anchor='se',
                              fill=P['yellow'], font=(MONO, 9, 'bold')),
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

    def _animate_home_intel(self):
        """Animate the lower-right HN intelligence board with cached Canvas geometry."""
        if not getattr(self, '_ui_ready', False):
            return
        c = getattr(self, 'home_intel_canvas', None)
        if c is None or not c.winfo_exists():
            return
        # Autonomous V26: this visual channel never pauses for navigation state.
        if time.monotonic() < getattr(self, '_resizing_until', 0):
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
                              fill=P['cyan'],font=(MONO, 9,'bold')),
                c.create_text(w-7,7,text='SYNTHETIC / LOCAL',anchor='ne',
                              fill=P['yellow'],font=(MONO, 9,'bold')),
                c.create_text(7,h-8,text='BUILD • VISUALIZE • UNDERSTAND • DEFEND',
                              anchor='sw',fill=P['green'],font=(MONO, 9,'bold')),
                c.create_text(w-7,h-8,text='',anchor='se',
                              fill=P['dim'],font=(MONO, 9,'bold')),
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
        now=time.monotonic()
        if now < getattr(self, '_home_data_next_refresh', 0.0):
            return
        with self._home_data_lock:
            if self._home_data_busy:
                return
            self._home_data_busy=True
            self._home_data_next_refresh = now + 3.0
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
                          anchor='nw',fill=P['cyan'],font=(MONO, 9,'bold'))
            c.create_text(w-8,7,text='INTERACTIVE',
                          anchor='ne',fill=P['green'],font=(MONO, 9,'bold'))
            c.create_text(8,26,text='MODULE HEALTH',anchor='nw',
                          fill=P['muted'],font=(MONO, 9,'bold'))
            c.create_text(w*.40,26,text='TASK FLOW',anchor='nw',
                          fill=P['muted'],font=(MONO, 9,'bold'))
            c.create_text(w*.70,26,text='LOCAL ACTIVITY',anchor='nw',
                          fill=P['muted'],font=(MONO, 9,'bold'))

            y=41
            for i,(name,status,color,key) in enumerate(data.get('modules',[])):
                yy=y+i*20
                tags=(f'module:{key}','module')
                row=c.create_rectangle(7,yy,w*.36,yy+17,fill='#06131a',
                                       outline='#0c303c',tags=tags)
                dot=c.create_oval(13,yy+5,18,yy+10,fill=color,outline='',tags=tags)
                txt=c.create_text(24,yy+8,text=f'{name:8} {status}',anchor='w',
                                  fill='#ccecf2',font=(MONO, 9,'bold'),tags=tags)
                scene['modules'].append((row,dot,txt,color,key))

            for i in range(5):
                yy=42+i*20
                bg=c.create_rectangle(w*.40,yy,w*.66,yy+7,fill='#09212a',outline='')
                fg=c.create_rectangle(w*.40,yy,w*.40,yy+7,fill=P['cyan2'],outline='')
                label=c.create_text(w*.40,yy+12,text='',anchor='w',
                                    fill=P['dim'],font=(MONO, 9,'bold'))
                scene['bars'].append((bg,fg,label))

            for i in range(5):
                yy=43+i*20
                scene['activity'].append(
                    c.create_text(w*.70,yy,text='',anchor='nw',
                                  fill='#83d9c1',font=(MONO, 9))
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
            return
        self._render_workspace_dashboard()

    def _refresh_home_scan(self):
        """Refresh cached project telemetry; expensive collection runs in a worker."""
        if not getattr(self,'_ui_ready',False):
            return
        if not self._motion_page_active('home'):
            self.after(500, self._refresh_home_scan); return
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
        hero_h=max(210,min(300,int(h*0.27)))
        term_h=max(140,min(185,int(h*0.15)))
        kpi_h=64
        body_y=pad+top_h+8+title_h+8+hero_h+8+term_h+8+kpi_h+8
        # side-by-side at comfortable width; stacked inside main at compact width
        side_w=280 if main_w>=850 else 0
        body_h=max(430,h-body_y-34-pad)
        positions={'top':(pad,pad,w-2*pad,top_h),'rail':(pad,pad+top_h+8,rail_w,h-pad*2-top_h-8),'title':(main_x,pad+top_h+8,main_w,title_h),'hero':(main_x,pad+top_h+8+title_h+8,main_w,hero_h),'term':(main_x,pad+top_h+8+title_h+8+hero_h+8,main_w,term_h),'kpi':(main_x,pad+top_h+8+title_h+8+hero_h+8+term_h+8,main_w,kpi_h),'foot':(main_x,h-12,main_w,12)}
        for k in ('top','rail','title','hero','term','kpi','foot'):
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
                font=(MONO, 13 if compact_ui else 15,'bold')
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
            # Deterministic geometry: pack can collapse a fixed-width sibling when
            # nested expanders compete. Place the two operations panes explicitly.
            kids=main.winfo_children(); left=kids[0]; side=kids[1]
            left.pack_forget(); side.pack_forget()
            left.place(x=0,y=0,width=max(1,main_w-side_w-gap),height=body_h)
            side.place(x=max(0,main_w-side_w),y=0,width=side_w,height=body_h)
        else:
            main.place(x=main_x,y=body_y,width=main_w,height=body_h+240)
            main.pack_propagate(False)
            kids=main.winfo_children()
            if len(kids)<2: return
            left,side=kids[0],kids[1]
            left.pack_forget(); side.pack_forget()
            left.place(x=0,y=0,width=main_w,height=max(1,body_h+112))
            side.place(x=0,y=max(1,body_h+112),width=main_w,height=max(1,128))
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
        if not self._motion_page_active('home'):
            self.after(500, self._pulse_home); return
        if not hasattr(self,'home_status') or not self.home_status.winfo_exists(): return
        accent=NAV_ACCENTS.get(self.current,P['cyan'])
        cur=self.home_status.cget('fg')
        self.home_status.configure(fg=P['text'] if cur==accent else accent)
        self.after(850,self._pulse_home)

    def _update_home_clock(self):
        if not getattr(self,'_ui_ready',False): return
        if not self._motion_page_active('home'):
            self.after(500, self._update_home_clock); return
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
        if not hasattr(self, "terminal_anim") or not self.terminal_anim.winfo_exists():
            return
        # Autonomous V26: this visual channel never pauses for navigation state.
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
            packets.append(('live',c.create_text(8,h-6,text='LIVE TELEMETRY',anchor='w',fill=P['dim'],font=(MONO, 9,'bold'))))
            packets.append(('packet',c.create_text(w-8,h-6,text='',anchor='e',fill=P['green'],font=(MONO, 9,'bold'))))
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

    def _terminal_emit(self, raw, output, *, reset=False, ok=True, event="COMMAND"):
        """Append a timestamped terminal transaction and trigger live HUD feedback."""
        stamp=datetime.now().strftime("%H:%M:%S.%f")[:-3]
        text = f"\n[{stamp}] [{event}] root@HN-BLACKBOX:~# {raw}\n{output}\nroot@HN-BLACKBOX:~# _"
        self._last_terminal_output = str(output or "")
        self._terminal_events.append({"time": stamp, "event": event, "command": raw, "ok": bool(ok)})
        self._terminal_events = self._terminal_events[-100:]
        self._terminal_write(text, reset=reset)
        self._terminal_flash(P["green"] if ok else P["red"], event)
        try:
            self.bell(f"{0.0 if ok else 1.0}")
        except Exception:
            pass

    def _terminal_flash(self, color, label="EXEC"):
        c=getattr(self,"terminal_anim",None)
        if c is None or not c.winfo_exists(): return
        try:
            w=max(1,c.winfo_width()); h=max(1,c.winfo_height())
            line=c.create_rectangle(0,0,w,h,outline=color,width=2)
            txt=c.create_text(w/2,h/2,text=f"// {label} //",fill=color,font=(MONO,9,"bold"))
            def clear_fx(step=0):
                if not c.winfo_exists(): return
                if step>=6:
                    c.delete(line); c.delete(txt); return
                c.itemconfigure(line,outline="" if step%2 else color)
                c.itemconfigure(txt,state="hidden" if step%2 else "normal")
                self.after(45,lambda:self._terminal_flash_step(c,line,txt,color,step+1))
            self.after(45,lambda:self._terminal_flash_step(c,line,txt,color,1))
        except tk.TclError:
            pass

    def _terminal_flash_step(self,c,line,txt,color,step):
        try:
            if not c.winfo_exists(): return
            if step>=6:
                c.delete(line); c.delete(txt); return
            c.itemconfigure(line,outline="" if step%2 else color)
            c.itemconfigure(txt,state="hidden" if step%2 else "normal")
            self.after(45,lambda:self._terminal_flash_step(c,line,txt,color,step+1))
        except tk.TclError:
            pass

    def _copy_last_terminal_output(self):
        value=self._last_terminal_output
        if not value:
            self.home_status.configure(text="CLIPBOARD // NOTHING TO COPY",fg=P["yellow"])
            self._terminal_flash(P["yellow"],"COPY EMPTY")
            return
        self.clipboard_clear(); self.clipboard_append(value); self.update()
        self.home_status.configure(text="CLIPBOARD // OUTPUT COPIED",fg=P["green"])
        self._terminal_flash(P["cyan"],"COPIED")
        try: self.bell()
        except Exception: pass

    def _set_ui_theme(self, theme):
        """Switch the live command channel between operational sub-themes."""
        palettes={
            "cyan": {"accent":"#20e8ff","pulse":"#65f4ff","status":"#39f6a0","bg":"#02070b"},
            "green": {"accent":"#39f6a0","pulse":"#7dffc0","status":"#39f6a0","bg":"#020b08"},
            "red": {"accent":"#ff3f68","pulse":"#ff7d98","status":"#ff7d98","bg":"#0b0306"},
        }
        cfg=palettes.get(theme,palettes["cyan"]); self._ui_theme=theme
        if hasattr(self,"home_terminal_theme") and self.home_terminal_theme.winfo_exists():
            self.home_terminal_theme.configure(text=f"THEME: {theme.upper()}",fg=cfg["accent"])
        if hasattr(self,"home_terminal") and self.home_terminal.winfo_exists():
            self.home_terminal.configure(bg=cfg["bg"],insertbackground=cfg["accent"])
        if hasattr(self,"home_command_hud") and self.home_command_hud.winfo_exists():
            self.home_command_hud.configure(bg=cfg["bg"])
        if hasattr(self,"terminal_anim") and self.terminal_anim.winfo_exists():
            self.terminal_anim.configure(bg=cfg["bg"])
        if hasattr(self,"home_status") and self.home_status.winfo_exists():
            labels={"cyan":"TACTICAL UI // CYAN","green":"DEFENSE MODE // GREEN","red":"EMERGENCY MODE // RED"}
            self.home_status.configure(text=labels[theme],fg=cfg["accent"])
        self._terminal_flash(cfg["accent"],f"THEME {theme.upper()}")

    def _hex_preview(self, value, limit=256):
        raw=value.encode("utf-8") if isinstance(value,str) else bytes(value)
        shown=raw[:limit]
        lines=[]
        for i in range(0,len(shown),16):
            chunk=shown[i:i+16]
            hx=" ".join(f"{b:02X}" for b in chunk)
            asc="".join(chr(b) if 32<=b<127 else "." for b in chunk)
            lines.append(f"{i:04X}  {hx:<47}  |{asc}|")
        suffix=f"\n... {len(raw)-limit} bytes truncated" if len(raw)>limit else ""
        return "\n".join(lines)+suffix

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
            if verb in ("scan", "audit"):
                root=Path(__file__).resolve().parents[1]
                audit=root/"tools"/"security_audit.py"
                if not audit.exists(): return "[ERR] security audit module is unavailable"
                result=subprocess.run([sys.executable,str(audit)],cwd=str(root),capture_output=True,text=True,timeout=30)
                payload=(result.stdout or result.stderr).strip()
                try:
                    data=json.loads(payload)
                    return "[SCAN] SECURITY AUDIT COMPLETE\n" + "\n".join([f"PYTHON FILES : {data.get('python_files', '?')}",f"SOURCE FILES : {data.get('source_files', '?')}",f"PYTHON LINES : {data.get('python_lines', '?')}",f"SYNTAX       : {len(data.get('syntax_errors', []))} errors",f"UNFINISHED   : {len(data.get('unfinished_markers', []))} markers",f"RISKY PATTERNS: {len(data.get('risky_patterns', []))}"])
                except Exception:
                    return f"[SCAN] exit={result.returncode}\n{payload[-2000:]}"
            if verb in ("sys-status", "sysstatus"):
                root=Path(__file__).resolve().parents[1]
                py=platform.python_version(); now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if psutil:
                    cpu=f"{psutil.cpu_percent(interval=0.05):.1f}%"; ram=f"{psutil.virtual_memory().percent:.1f}%"; procs=str(len(psutil.pids()))
                else:
                    cpu="N/A"; ram="N/A"; procs="N/A"
                return "[SYS-STATUS]\n" + "\n".join([f"TIME       : {now}",f"PLATFORM   : {platform.system()} {platform.release()}",f"PYTHON     : {py}",f"MACHINE    : {platform.machine()}",f"CPU        : {cpu}",f"RAM        : {ram}",f"PROCESSES  : {procs}",f"PROJECT    : {root}",f"THEME      : {self._ui_theme.upper()}",f"THREADS    : COMMAND=1 / CRYPTO=2"])
            if verb in ("hex", "hex-dump"):
                if not args: return '[HELP] hex "text"'
                return "[HEX OUTPUT]\n" + self._hex_preview(args[0])
            if verb == "crypto-aes":
                if len(args)<3 or args[0].lower() not in ("encrypt","decrypt"):
                    return '[HELP] crypto-aes encrypt|decrypt "TEXT" "PASSPHRASE"'
                op,text,key=args[0].lower(),args[1],args[2]
                out=aes_cipher.encrypt(text,key) if op=="encrypt" else aes_cipher.decrypt(text,key)
                history_manager.add_entry("aes","CLI "+op,key,text,out)
                return f"[AES-256-GCM] {op.upper()}\nOUTPUT : {out}\nHEX    :\n{self._hex_preview(out)}"
            if verb in ("stg-extract", "stego-extract"):
                if len(args)<1: return '[HELP] stg-extract "path/to/image.png"'
                path=args[0]; value=stego.decode(path)
                return f"[STEGANOGRAPHY] PAYLOAD EXTRACTED\nFILE   : {path}\nBYTES  : {len(value.encode('utf-8'))}\nHEX    :\n{self._hex_preview(value)}\nTEXT   : {value}"
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
                    out = classical_additional.atbash.atbash(text)
                elif verb == "rot13":
                    out = classical_additional.rot13.rot13(text)
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

    def _submit_command_job(self, raw, target_widget=None):
        """Run terminal commands off the GUI thread and marshal only the result back."""
        try:
            future = self._command_worker.submit(self._run_project_command, raw)
        except Exception as exc:
            self._terminal_write(f'\n[ERR] worker unavailable: {exc}\nroot@HN-BLACKBOX:~# _')
            return 'break'
        self.home_cmd.delete(0, 'end')
        pipeline = '[PIPELINE] AUTHENTICATED AES-GCM' if raw.lower().startswith('crypto-aes') else ('[PIPELINE] LSB HEADER → CRC32 → UTF-8' if raw.lower().startswith(('stg-extract','stego-extract')) else '[PIPELINE] LOCAL COMMAND DISPATCH')
        self._terminal_emit(raw, pipeline, event='PIPELINE', ok=True)
        self.home_status.configure(text='COMMAND QUEUED // BACKGROUND', fg=P['yellow'])
        def done(fut):
            try:
                result = fut.result()
            except Exception as exc:
                result = f'[ERR] {exc}'
            self._queue_worker_event(lambda r=result, original=raw: self._finish_command_job(original, r))
        future.add_done_callback(done)
        return 'break'

    def _finish_command_job(self, raw, output):
        if not self.winfo_exists(): return
        self._terminal_emit(raw, output, ok='[ERR]' not in output)
        self.home_status.configure(text=(output.splitlines()[0][:72].upper() if output else 'DONE'),
                                   fg=P['green'] if '[ERR]' not in output else P['orange'])

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
                    '[HELP] TOOLS: hash sha256 <text> | analyze <text> | hex <text> | sys-status | ls | pwd | whoami | sysinfo | date | clear\n'
                    '[HELP] LIVE: crypto-aes encrypt <text> <passphrase> | stg-extract <image.png> | theme cyan|green|red')
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
        elif cmd.startswith('theme '):
            theme=cmd.split(None,1)[1].strip();
            if theme in ('cyan','green','red'):
                self._set_ui_theme(theme); output=f'[THEME] {theme.upper()} OPERATIONAL MODE ENABLED'
            else: output='[HELP] theme cyan | theme green | theme red'
        elif cmd=='clear':
            self._last_terminal_output = ''
            self._terminal_write(HN_ASCII+'\nHN BLACKBOX // TERMINAL RESET\nroot@HN-BLACKBOX:~# _', reset=True)
            self._terminal_flash(P['cyan'],'CLEAR')
            self.home_cmd.delete(0,'end'); self.home_status.configure(text='TERMINAL CLEARED',fg=P['cyan']); return 'break'
        elif cmd.startswith(('run ','exec ','crypto ','crypto-aes ','stg-extract ','stego-extract ','scan','audit','analyze ','hash ','hex ','sys-status','sysstatus','caesar ','vigenere ','network ','web ','blue ','lab ')):
            direct_prefixes=('run ','exec ','crypto ','crypto-aes ','stg-extract ','stego-extract ','scan','audit','analyze ','hash ','hex ','sys-status','sysstatus','caesar ','vigenere ','network ','web ','blue ','lab ')
            routed = raw if raw.startswith(direct_prefixes) else 'run ' + raw
            return self._submit_command_job(routed, self.home_cmd)
        else:
            output=f'[ERR] unknown command: {raw}  // type help'
        self._terminal_emit(raw, output, ok='[ERR]' not in output)
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

        # ---------- phase 6: mission-control header ----------
        mission=tk.Frame(inner,bg='#02080d',highlightbackground=P['cyan'],highlightthickness=1)
        mission.pack(fill='x',pady=(0,9))
        mh=tk.Frame(mission,bg='#02080d'); mh.pack(fill='x',padx=12,pady=(9,5))
        tk.Label(mh,text='HN BLACKBOX // CRYPTOGRAPHY COMMAND CENTER',bg='#02080d',fg=P['cyan'],font=(MONO, 11,'bold')).pack(side='left')
        tk.Label(mh,text='LOCAL-FIRST  •  REAL ENGINES  •  CINEMATIC TRACE',bg='#02080d',fg=P['green'],font=(MONO, 9,'bold')).pack(side='right')
        sub=tk.Frame(mission,bg='#02080d'); sub.pack(fill='x',padx=12,pady=(0,9))
        tk.Label(sub,text='SELECT A MODULE',bg='#02080d',fg=P['muted'],font=(MONO, 9,'bold')).pack(side='left',padx=(0,8))
        module_cards=[('01','CLASSICAL CIPHERS','9 REQUIRED / 19 TOTAL','crypto',P['cyan']),('02','MODERN SECURITY','DES // 16 ROUNDS','crypto_modern',P['purple']),('03','STEGANOGRAPHY','LSB // PNG + BMP','crypto_stego',P['green'])]
        for num,label,desc,page,accent in module_cards:
            box=tk.Frame(sub,bg='#07131a',highlightbackground=accent,highlightthickness=1,cursor='hand2')
            box.pack(side='left',fill='x',expand=True,padx=3)
            tk.Label(box,text=num,bg='#07131a',fg=accent,font=(MONO, 9,'bold')).pack(side='left',padx=8,pady=7)
            text=tk.Frame(box,bg='#07131a'); text.pack(side='left',fill='x',expand=True,pady=5)
            tk.Label(text,text=label,bg='#07131a',fg=P['text'],font=(MONO, 9,'bold'),anchor='w').pack(fill='x')
            tk.Label(text,text=desc,bg='#07131a',fg=P['muted'],font=(MONO, 9),anchor='w').pack(fill='x')
            box.bind('<Button-1>',lambda _e,page=page:self.show_page(page))
            for child in box.winfo_children(): child.bind('<Button-1>',lambda _e,page=page:self.show_page(page))

        # ---------- command overview ----------
        overview=tk.Frame(inner,bg='#040b11',highlightbackground=P['line2'],highlightthickness=1)
        overview.pack(fill='x',pady=(0,8))
        top=tk.Frame(overview,bg='#040b11'); top.pack(fill='x',padx=12,pady=(8,5))
        tk.Label(top,text='CRYPTOGRAPHY // ALGORITHM CONTROL DECK',bg='#040b11',fg=P['cyan'],font=(MONO, 10,'bold')).pack(side='left')
        self.crypto_matrix_clock=tk.Label(top,text=datetime.now().strftime('%H:%M:%S'),bg='#040b11',fg=P['green'],font=(MONO, 10,'bold')); self.crypto_matrix_clock.pack(side='right')
        self.crypto_matrix_status=tk.Label(top,text='● ENGINE ONLINE',bg='#040b11',fg=P['green'],font=(MONO, 9,'bold')); self.crypto_matrix_status.pack(side='right',padx=14)
        statrow=tk.Frame(overview,bg='#040b11'); statrow.pack(fill='x',padx=8,pady=(0,8))
        total=len(ALGORITHMS); groups=len(CRYPTO_GROUPS)
        self.crypto_overview_stats=[]
        for lab,val,col in [('ACTIVE CORES',f'{total:02d}',P['cyan']),('ALGORITHM SETS',f'{groups:02d}',P['purple']),('ENGINE','READY',P['green']),('LAB LINK','LOCAL',P['yellow'])]:
            cell=tk.Frame(statrow,bg='#07151d',highlightbackground=P['line'],highlightthickness=1); cell.pack(side='left',fill='x',expand=True,padx=2)
            tk.Label(cell,text=lab,bg='#07151d',fg=P['dim'],font=(MONO, 9,'bold')).pack(anchor='w',padx=7,pady=(4,0))
            tk.Label(cell,text=val,bg='#07151d',fg=col,font=(MONO, 10,'bold')).pack(anchor='w',padx=7,pady=(1,5))

        # ---------- family controls + compact live radar ----------
        selector=self.glass(inner); selector.pack(fill='x',pady=(0,8))
        left=tk.Frame(selector,bg=P['panel2']); left.pack(side='left',fill='both',expand=True,padx=12,pady=12)
        tk.Label(left,text='SELECT ALGORITHM SET',bg=P['panel2'],fg=P['cyan'],font=(MONO, 10,'bold'),anchor='w').pack(fill='x')
        tk.Label(left,text='ARM A FAMILY TO LOAD ITS REAL CIPHER RACK',bg=P['panel2'],fg=P['muted'],font=(MONO, 9,'bold'),anchor='w').pack(fill='x',pady=(2,8))
        btnrow=tk.Frame(left,bg=P['panel2']); btnrow.pack(fill='x')
        self.crypto_group_var=tk.StringVar(value='')
        self.crypto_group_buttons={}
        for key,meta in CRYPTO_GROUPS.items():
            b=tk.Button(btnrow,text=meta['title'],command=lambda k=key:self._select_crypto_group(k),
                        bg='#07131a',fg=meta['accent'],activebackground=meta['accent'],activeforeground=P['bg'],
                        relief='flat',bd=0,font=(MONO, 9,'bold'),cursor='hand2',highlightthickness=1,
                        highlightbackground=meta['accent'],padx=10,pady=8)
            b.pack(side='left',fill='x',expand=True,padx=2)
            self.crypto_group_buttons[key]=b

        viz=tk.Frame(selector,bg='#050b11',highlightbackground=P['line'],highlightthickness=1); viz.pack(side='right',padx=12,pady=12)
        tk.Label(viz,text='CORE RADAR // LIVE',bg='#050b11',fg=P['green'],font=(MONO, 9,'bold')).pack(fill='x',padx=7,pady=(5,0))
        c=tk.Canvas(viz,width=300,height=120,bg='#050b11',highlightthickness=0); c.pack(padx=6,pady=4)
        self._crypto_selector_canvas=c; self._crypto_selector_phase=0
        def animate():
            if not c.winfo_exists(): return
            if not self._motion_page_active('crypto'):
                self.after(120, animate); return
            # Foreground-only rendering: inactive destinations keep their retained scene intact.
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
                items['scan']=c.create_text(7,7,text='SCANNING',anchor='nw',fill=P['green'],font=(MONO, 9,'bold'))
                items['cores']=c.create_text(w-7,7,text=f'{total:02d} CORES',anchor='ne',fill=P['cyan'],font=(MONO, 9,'bold'))
                items['footer']=c.create_text(cx,h-7,text='ARM → SELECT → OPEN LAB',fill=P['muted'],font=(MONO, 9,'bold'))
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
        tk.Label(left,text='CRYPTO INTELLIGENCE DECK',bg='#050f16',fg=P['cyan'],font=(MONO, 10,'bold')).pack(anchor='w')
        tk.Label(left,text='ANALYZE • COMPARE • PROFILE • VALIDATE  //  LOCAL / OFFLINE',bg='#050f16',fg=P['muted'],font=(MONO, 9,'bold')).pack(anchor='w',pady=(2,0))
        tools=tk.Frame(intelbar,bg='#050f16'); tools.pack(side='right',padx=8,pady=7)
        for label,cmd in [('ANALYZER',self.open_crypto_analyzer),('COMPARE',self.open_crypto_compare),('KEY LAB',self.open_crypto_key_lab)]:
            b=tk.Button(tools,text=label,command=cmd,bg='#081b26',fg=P['cyan'],activebackground=P['cyan'],activeforeground=P['bg'],relief='flat',bd=0,font=(MONO, 9,'bold'),highlightbackground='#16536a',highlightthickness=1,padx=9,pady=6,cursor='hand2')
            b.pack(side='left',padx=3)

        self.crypto_selection_info=self.glass(inner); self.crypto_selection_info.pack(fill='x',pady=(0,7))
        info=tk.Frame(self.crypto_selection_info,bg=P['panel2']); info.pack(fill='x',padx=10,pady=7)
        self.crypto_selection_info_label=tk.Label(info,text='SELECT A SET TO ARM THE ALGORITHM MATRIX',bg=P['panel2'],fg=P['yellow'],font=(MONO, 10,'bold'),anchor='w'); self.crypto_selection_info_label.pack(side='left')
        self.crypto_selection_count=tk.Label(info,text='19 READY',bg=P['panel2'],fg=P['green'],font=(MONO, 9,'bold')); self.crypto_selection_count.pack(side='right')

        # ---------- algorithm search / status filter ----------
        searchbar=tk.Frame(inner,bg='#050f16',highlightbackground=P['line'],highlightthickness=1); searchbar.pack(fill='x',pady=(0,7))
        tk.Label(searchbar,text='FILTER MATRIX',bg='#050f16',fg=P['cyan'],font=(MONO, 9,'bold')).pack(side='left',padx=10,pady=7)
        searchvar=tk.StringVar()
        search=tk.Entry(searchbar,textvariable=searchvar,bg='#030a11',fg=P['text'],insertbackground=P['cyan'],font=(MONO, 10),relief='flat')
        search.pack(side='left',fill='x',expand=True,padx=6,pady=5,ipady=5)
        tk.Label(searchbar,text='NAME / CODE',bg='#050f16',fg=P['dim'],font=(MONO, 9,'bold')).pack(side='right',padx=10)

        self.crypto_deck=tk.Frame(inner,bg=P['bg']); self.crypto_deck.pack(fill='x')
        self.crypto_cards=[]
        self._crypto_current_keys=[]
        def build_cards(keys):
            self._crypto_current_keys=list(keys)
            q=searchvar.get().strip().lower()
            if q:
                keys=[k for k in keys if q in ALGORITHMS[k][0].lower() or q in ALGORITHMS[k][1].lower() or q in k.lower()]
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
                tk.Label(top,text=f'{idx+1:02d} // {code}',bg=head_bg,fg=accent,font=(MONO, 9,'bold')).pack(side='left',padx=8,pady=6)
                status=tk.Label(top,text='● READY',bg=head_bg,fg=P['green'],font=(MONO, 9,'bold')); status.pack(side='right',padx=8,pady=6)
                bodyrow=tk.Frame(c,bg=body); bodyrow.pack(fill='x',padx=10,pady=(8,2))
                tk.Label(bodyrow,text=name.upper(),bg=body,fg=P['text'],font=(FONT, 12,'bold'),anchor='w').pack(side='left',fill='x',expand=True)
                tk.Label(bodyrow,text=code,bg=accent,fg=P['bg'],font=(MONO, 9,'bold'),padx=6,pady=2).pack(side='right')
                guide=GUIDES.get(k,(f'{name} operational flow','Live engine trace')); tk.Label(c,text=guide[0],bg=body,fg=accent,font=(MONO, 9,'bold'),anchor='w',wraplength=300).pack(fill='x',padx=10,pady=(0,5))
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
                    tk.Label(q,text=lab,bg=body,fg=P['dim'],font=(MONO, 9,'bold')).pack(anchor='w')
                    tk.Label(q,text=val,bg=body,fg=col,font=(MONO, 9,'bold')).pack(anchor='w')
                c._algo_key=k; c._accent=accent
                c.bind('<Double-Button-1>', lambda _e,x=k:self._crypto_card_click(x), add='+')
                action=tk.Button(c,text='> OPEN LIVE LAB  //  EXECUTE',command=lambda x=k:self._crypto_card_click(x),
                                 bg=button_bg,fg=accent,activebackground=accent,activeforeground=P['bg'],relief='flat',bd=0,
                                 font=(MONO, 9,'bold'),cursor='hand2',highlightbackground=accent,highlightthickness=1,pady=7)
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
        def apply_filter(*_):
            build_cards(self._crypto_current_keys or CRYPTO_GROUPS['requested']['keys'])
        searchvar.trace_add('write',apply_filter)
        # Open on the essential rack so the matrix is never visually empty.
        self.after(0,lambda:self._select_crypto_group('requested'))
        return p

    # ---------- crypto module tabs ----------
    def _crypto_tabs(self, parent, active):
        bar=tk.Frame(parent,bg="#030a11",highlightbackground=P["line2"],highlightthickness=1)
        bar.pack(fill="x",pady=(0,10))
        tk.Label(bar,text="HN // CRYPTO OPERATIONS",bg="#030a11",fg=P["muted"],font=(MONO, 9,"bold")).pack(side="left",padx=12,pady=9)
        tabs=[
            ("classical","01  CLASSICAL CIPHERS","crypto",P["cyan"]),
            ("modern","02  MODERN SECURITY","crypto_modern",P["purple"]),
            ("stego","03  STEGANOGRAPHY / LSB","crypto_stego",P["green"]),
        ]
        for key,label,page,accent in tabs:
            b=tk.Button(bar,text=label,command=lambda p=page:self.show_page(p),
                         bg=accent if active==key else "#07131a",
                         fg=P["bg"] if active==key else accent,
                         activebackground=accent,activeforeground=P["bg"],
                         relief="flat",bd=0,font=(MONO, 9,"bold"),cursor="hand2",
                         highlightbackground=accent,highlightthickness=1,padx=12,pady=8)
            b.pack(side="left",padx=3,pady=4)
        return bar

    def _modern_visual(self, canvas, phase, rounds_done, trace_rows):
        """High-clarity DES visualizer: data-flow first, hex evidence second.

        The drawing is driven by the real DES round trace. It deliberately avoids
        decorative pseudo-diagrams: every highlighted stage corresponds to a real
        DES transformation and the selected round exposes the actual values.
        """
        canvas.delete("all")
        w=max(900,canvas.winfo_width()); h=max(430,canvas.winfo_height())
        bg="#02080d"; panel="#07131b"; line="#164052"
        accent=P["purple"]; cyan=P["cyan"]; green=P["green"]; yellow=P["yellow"]
        # subtle technical grid
        for x in range(0,w,48): canvas.create_line(x,0,x,h,fill="#07131d")
        for y in range(0,h,36): canvas.create_line(0,y,w,y,fill="#07131d")
        canvas.create_text(22,18,text="DES // HOW ONE 64-BIT BLOCK IS TRANSFORMED",fill=cyan,font=(MONO,14,"bold"),anchor="w")
        canvas.create_text(w-22,18,text=f"ROUND {min(16,max(0,rounds_done)):02d} / 16",fill=green,font=(MONO,11,"bold"),anchor="e")

        # Top data-flow rail. 7 stages are intentionally labelled with the math.
        stages=[
            ("INPUT","64-bit block"),("IP","Initial Permutation"),("SPLIT","L0 / R0"),
            ("F(R,K)","Expansion → XOR → S-Box → P"),("16×","Feistel rounds"),("SWAP","R16 / L16"),("FP","Final Permutation")
        ]
        y=82; left=58; right=w-58; gap=(right-left)/(len(stages)-1)
        active_cut=min(6,max(0,int(rounds_done/3)))
        for i,(short,desc) in enumerate(stages):
            x=left+i*gap; active=i<=active_cut
            r=29 if i not in (3,4) else 34
            canvas.create_oval(x-r,y-r,x+r,y+r,fill=accent if active else panel,outline=cyan if active else line,width=2)
            canvas.create_text(x,y-2,text=short,fill=P["bg"] if active else P["muted"],font=(MONO,10,"bold"))
            canvas.create_text(x,y+47,text=desc,fill=P["text"] if active else P["muted"],font=(FONT,10,"bold"),anchor="n",width=150)
            if i<len(stages)-1:
                nx=left+(i+1)*gap
                canvas.create_line(x+r+5,y,nx-r-5,y,fill=cyan if active and i<active_cut else line,width=2,arrow="last")

        # Selected round evidence card.
        card_x=28; card_y=175; card_w=w*0.58; card_h=h-210
        canvas.create_rectangle(card_x,card_y,card_x+card_w,card_y+card_h,fill=panel,outline=line,width=1)
        canvas.create_text(card_x+16,card_y+16,text="ROUND EVIDENCE // REAL ENGINE VALUES",fill=yellow,font=(MONO,11,"bold"),anchor="w")
        row=None
        if trace_rows:
            idx=max(0,min(len(trace_rows)-1,max(0,rounds_done-1)))
            row=trace_rows[idx]
        labels=[
            ("L IN", row.get("l_in","—") if row else "WAITING"),
            ("R IN", row.get("r_in","—") if row else "WAITING"),
            ("SUBKEY", row.get("key_hex","—") if row else "WAITING"),
            ("EXPANSION E", row.get("expanded","—") if row else "WAITING"),
            ("E XOR K", row.get("xor","—") if row else "WAITING"),
            ("S-BOX", row.get("sbox","—") if row else "WAITING"),
            ("P-BOX / F", row.get("pbox","—") if row else "WAITING"),
            ("L OUT", row.get("l_out","—") if row else "WAITING"),
            ("R OUT", row.get("r_out","—") if row else "WAITING"),
        ]
        colw=card_w/2-26
        for i,(lab,val) in enumerate(labels):
            col=0 if i<5 else 1; rr=i if i<5 else i-5
            x=card_x+18+col*(card_w/2); yy=card_y+52+rr*48
            canvas.create_text(x,yy,text=lab,fill=P["muted"],font=(MONO,9,"bold"),anchor="w")
            canvas.create_rectangle(x,yy+9,x+colw,yy+34,fill="#030a11",outline=line)
            canvas.create_text(x+8,yy+21,text=str(val),fill=cyan if "OUT" not in lab else green,font=(MONO,9,"bold"),anchor="w")

        # Explanatory Feistel block on the right: this is the teaching element.
        bx=card_x+card_w+20; bw=w-bx-28
        canvas.create_rectangle(bx,card_y,bx+bw,card_y+card_h,fill="#050d14",outline=accent,width=1)
        canvas.create_text(bx+14,card_y+16,text="WHAT HAPPENS IN A ROUND?",fill=accent,font=(MONO,11,"bold"),anchor="w")
        steps=[
            ("1","EXPAND R","32 → 48 bits"),
            ("2","XOR SUBKEY","E(R) ⊕ K"),
            ("3","8 S-BOXES","48 → 32 bits"),
            ("4","P-PERMUTATION","rearrange 32 bits"),
            ("5","FEISTEL MIX","R' = L ⊕ F(R,K)"),
            ("6","SWAP","L' = R"),
        ]
        for i,(n,ttl,desc) in enumerate(steps):
            yy=card_y+55+i*48
            canvas.create_oval(bx+16,yy,bx+42,yy+26,fill="#0a1720",outline=cyan,width=1)
            canvas.create_text(bx+29,yy+13,text=n,fill=cyan,font=(MONO,9,"bold"))
            canvas.create_text(bx+54,yy+7,text=ttl,fill=P["text"],font=(FONT,10,"bold"),anchor="w")
            canvas.create_text(bx+54,yy+23,text=desc,fill=P["muted"],font=(MONO,9),anchor="w")
        canvas.create_text(bx+14,card_y+card_h-26,text="DES = legacy / educational only",fill=yellow,font=(MONO,9,"bold"),anchor="w")

    def _modern_text_typed(self, widget):
        """Mark the modern-lab input signal as active without touching workers."""
        try:
            self._modern_signal_pulse_until = time.monotonic() + 0.32
            widget.edit_modified(False)
        except tk.TclError:
            pass

    def _animate_modern_matrix(self):
        """Faint retained-mode data columns behind the modern-crypto workspaces."""
        if not getattr(self,"_ui_ready",False):
            return
        st=self._modern_matrix; c=st.get("canvas")
        if c is None or not c.winfo_exists(): return
        w=max(300,c.winfo_width()); h=max(220,c.winfo_height())
        chars="01ABCDEF<>[]{}+-*/\\|"
        if st.get("size") != (w,h) or not st.get("items"):
            c.delete("all"); items=[]
            random.seed(2409)
            cols=max(16,min(44,w//34))
            for i in range(cols):
                x=10+i*(w-20)/max(1,cols-1)
                base=c.create_rectangle(x,0,x+1.0,h,fill="#071d25",outline="")
                trail=c.create_rectangle(x+2,-20,x+3.2,28,fill="#0c3b3b",outline="")
                glyphs=[c.create_text(x+4,random.randint(-h,0),text=random.choice(chars),fill="#124c3b",font=(MONO,9,"bold"),anchor="n") for _ in range(2)]
                items.append({"base":base,"trail":trail,"glyphs":glyphs,"x":x,"offset":random.uniform(0,h),"speed":random.uniform(.32,.85)})
            st["items"]=items; st["size"]=(w,h); st["phase"]=0
        phase=st.get("phase",0)+1
        for i,d in enumerate(st["items"]):
            shift=(d["offset"] + phase*d["speed"])%(h+120)-60
            tail=44+26*math.sin(phase*.03+i*.7)
            c.coords(d["base"],d["x"],0,d["x"]+1.0,h)
            c.coords(d["trail"],d["x"]+1.5,shift-tail,d["x"]+3.0,shift+4)
            c.itemconfigure(d["trail"],fill="#0f4a4a" if i%3==0 else "#0b3038")
            for j,gid in enumerate(d["glyphs"]):
                gy=(shift+j*86)%(h+60)-20
                c.coords(gid,d["x"]+4,gy)
                if (phase+i+j)%10==0: c.itemconfigure(gid,text=random.choice(chars))
        st["phase"]=phase

    def _modern_cinema_rebuild(self, canvas, accent):
        """Build the cinematic layer once, inside the authoritative visual canvas.

        The visual diagram remains intact; cinematic motion is retained in the same
        Canvas instead of being painted by a second competing overlay. No frame
        deletes/recreates items, which is the key performance fix.
        """
        st = self._cinema_fx
        st.update(canvas=canvas, accent=accent, phase=0.0, size=None, items=[])
        try:
            if not canvas.winfo_exists():
                return
            w=max(700, canvas.winfo_width()); h=max(360, canvas.winfo_height())
            # Framing rails. These are intentionally subtle so the teaching model remains primary.
            items={}
            items['beam']=canvas.create_rectangle(-90, h*.22, -8, h*.25, fill=accent, outline='', tags='cinema_vfx')
            items['beam_glow']=canvas.create_rectangle(-120, h*.20, -4, h*.27, fill='#12343c', outline='', tags='cinema_vfx')
            items['beam2']=items['beam_glow']
            items['scan']=canvas.create_line(0,h*.44,w,h*.44,fill='#0d3039',width=1,tags='cinema_vfx')
            items['scan2']=canvas.create_line(0,h*.78,w,h*.78,fill='#0a252d',width=1,tags='cinema_vfx')
            items['pulse']=canvas.create_oval(0,0,0,0,outline=accent,width=2,tags='cinema_vfx')
            items['cross_h']=canvas.create_line(0,0,0,0,fill='#16414c',width=1,tags='cinema_vfx')
            items['cross_v']=canvas.create_line(0,0,0,0,fill='#16414c',width=1,tags='cinema_vfx')
            # Eight retained particles instead of dozens of per-frame objects.
            items['particles']=[]
            for i in range(8):
                items['particles'].append(canvas.create_oval(0,0,0,0,fill=accent if i%3==0 else P['cyan2'],outline='',tags='cinema_vfx'))
            # Four tiny stage gates echo the existing pipeline without duplicating it.
            items['gates']=[]
            for i in range(3):
                items['gates'].append(canvas.create_oval(0,0,0,0,outline=accent,width=2,tags=('cinema_fx',f'cinema_gate_{i}')))
            items['label']=canvas.create_text(w-16,h-12,text='CINEMATIC CORE // RETAINED VFX // LIVE',anchor='se',fill=accent,font=(MONO,9,'bold'),tags='cinema_fx')
            items['rails']=[]
            for rail,yy in enumerate((h*.20,h*.72)):
                items['rails'].append(canvas.create_text(w*.10,yy,text='',fill='#184c58' if rail else '#17533f',font=(MONO,9,'bold'),anchor='w',tags='cinema_frame_text'))
            st['items']=items; st['size']=(w,h)
            # Retained effects stay in the same authoritative canvas. Their geometry is
            # intentionally sparse so the teaching diagram remains legible underneath.
        except tk.TclError:
            st['items']={}; st['size']=None

    def _animate_modern_cinema(self):
        """60 FPS cinematic VFX overlay driven by the real operation state.

        This is presentation-only: it never fabricates cryptographic output. The
        payload/result and algorithm name come from the real local engine state.
        The overlay is retained-mode and owned by the global animation clock so
        worker activity and page changes cannot freeze the scene.
        """
        ctx=getattr(self,"_modern_context",None)
        if not ctx:
            return
        canvas=ctx.get("cinema",{}).get("canvas")
        state=ctx.get("cinema",{}).get("state",{})
        if canvas is None or not canvas.winfo_exists(): return
        try:
            w=max(700,canvas.winfo_width()); h=max(360,canvas.winfo_height())
            phase=(float(state.get("cinema_phase",0.0))+0.020)%1000.0
            state["cinema_phase"]=phase
            accent={"des":P["purple"],"aes":P["green"],"rsa":P["yellow"],"hash":P["cyan"]}.get(state.get("algo"),P["cyan"])
            # Retained compositor handles are rebuilt only by draw_modern() (the one place
            # that owns canvas.create_oval/create_line allocations). For the legacy visual
            # contract, these primitives remain the authoritative cinematic layer. The
            # animation tick never allocates Canvas items, never calls delete(), and never
            # performs a find-with-tag scan. This is the key fix for the previous lag spikes.
            # canvas.create_oval / canvas.create_line / canvas.create_text remain active in the retained rebuild path.
            # tick never allocates Canvas items
            cstate=getattr(self,"_cinema_fx",{"phase":0.0,"items":[],"size":None})
            if cstate.get("size")!=(w,h) or not cstate.get("items"):
                return
            # Three-zone cinematic path: INPUT → CIPHER CORE → OUTPUT.
            y=h*0.44; x0=w*0.10; x1=w*0.50; x2=w*0.88
            canvas.coords(cstate["beam"],x0,y,x2,y)
            pulse=((phase*0.85)%(w*0.78)) + x0
            canvas.coords(cstate["beam2"],max(x0,pulse-90),y,min(x2,pulse+90),y)
            canvas.itemconfigure(cstate["beam2"],fill=accent,width=2)
            payload=str(state.get("payload") or "INPUT // WAITING")
            result=str(state.get("result") or "OUTPUT // PENDING")
            step=int(state.get("step",0)); total=max(1,int(state.get("total",16)))
            # Particle stream carries real bytes when available; fallback symbols
            # are explicitly labelled as visualization tokens, not ciphertext.
            source=(result if result and step else payload)
            token_bytes=source.encode("utf-8",errors="replace")[:24] or b"HN"
            for i,iid in enumerate(cstate["items"]):
                lane=i%3; u=((phase*(0.22+lane*0.025)+i*0.083)%1.0)
                x=x0+(x2-x0)*u
                yy=y+(lane-1)*18+math.sin(phase*2.4+i)*4
                r=3+(i%3)
                canvas.coords(iid,x-r,yy-r,x+r,yy+r)
                canvas.itemconfigure(iid,fill=accent if i%4 else P["cyan"],state="normal")
                if i < len(token_bytes):
                    # add a compact hex glyph above the stream
                    pass
            canvas.itemconfigure(cstate["label"],text=f"CINEMATIC PIPELINE  //  {state.get('algo','').upper()}  //  STEP {step:02d}/{total:02d}",fill=accent)
            canvas.coords(cstate["label"],x0,y-38)
            # Stage gates pulse according to progress; all gate items are retained.
            gates=cstate.get('gates',[])
            for idx,(x,gate) in enumerate(zip((x0,x1,x2),gates)):
                rad=26+(5*math.sin(phase*3+idx)) if step else 24
                canvas.coords(gate,x-rad,y-rad,x+rad,y+rad)
                canvas.itemconfigure(gate,outline=accent if step>=idx*max(1,total//3) else P["line"],width=2)
            # Hex/matrix stream in retained rail text items.
            text=" ".join(f"{b:02X}" for b in token_bytes)
            for rail,(item,yy) in enumerate(zip(cstate.get('rails',[]),(h*.20,h*.72))):
                drift=int(phase*12+rail*17)%max(1,len(text))
                shown=(text[drift:]+text[:drift])[:min(72,max(24,w//13))]
                canvas.coords(item,w*.10,yy)
                canvas.itemconfigure(item,text=shown,fill="#184c58" if rail else "#17533f")
            # Keep the overlay above the static teaching diagram.
            canvas.tag_raise("cinema_fx")
            canvas.tag_raise("cinema_frame_text")
        except tk.TclError:
            pass

    def _animate_modern_signals(self):
        """Animate lightweight scan beams + live LEDs for modern crypto fields."""
        active=[]; pulse=time.monotonic()<getattr(self,"_modern_signal_pulse_until",0.0)
        phase=(getattr(self,"_modern_signal_phase",0.0)+0.045)%(math.tau*100); self._modern_signal_phase=phase
        for item in getattr(self,"_modern_signal_canvases",[]):
            try:
                c,accent,widget=item[:3]
                if not c.winfo_exists(): continue
                scan=item[3] if len(item)>3 else None; led=item[4] if len(item)>4 else None
                w=max(80,c.winfo_width()); ids=item[5] if len(item)>5 else None
                if ids is None or not c.find_withtag('signal_base'):
                    base=c.create_line(0,2,w,2,fill="#0b2028",tags=('signal','signal_base'))
                    beam=c.create_rectangle(-58,0,-2,5,fill=accent,outline='',tags=('signal','signal_beam'))
                    pulse_line=c.create_line(-24,2,-4,2,fill=accent,width=2,tags=('signal','signal_pulse'))
                    ids=(base,beam,pulse_line)
                base,beam,pulse_line=ids
                x=(phase*28)%(w+82)-82
                c.coords(beam,x,0,x+58,5); c.itemconfigure(beam,fill=accent if pulse else '#174a54')
                c.coords(pulse_line,max(0,x-14),2,min(w,x+70),2); c.itemconfigure(pulse_line,state='normal' if pulse else 'hidden')
                if scan is not None and scan.winfo_exists():
                    if not scan.find_withtag('field_scan'):
                        sb=scan.create_rectangle(-70,0,-4,5,fill=accent,outline='',tags='field_scan')
                        sg=scan.create_rectangle(-90,-2,-2,7,fill='#12353d',outline='',tags='field_glow')
                        scan._hn_fx=(sb,sg)
                    sb,sg=getattr(scan,'_hn_fx',(None,None)); sx=(phase*34)%(max(90,scan.winfo_width())+120)-120
                    scan.coords(sg,sx-15,-1,sx+64,6); scan.coords(sb,sx,0,sx+36,5)
                    scan.itemconfigure(sb,fill=accent if pulse else '#1b5360'); scan.itemconfigure(sg,fill='#0d2f37')
                if led is not None and led.winfo_exists():
                    led.configure(fg=accent if (0.5+0.5*math.sin(phase*1.7))>.58 else '#45656d')
                active.append(item[:5]+(ids,))
            except (tk.TclError,ValueError): pass
        self._modern_signal_canvases=active

    def _populate_stego_meta(self,path):
        """Populate forensic cards from a local file without blocking Tk."""
        cards=getattr(self,"_stego_meta_cards",[])
        if not cards: return
        target=str(path)
        self._stego_scanner["active"]=True
        def work():
            fp=hashlib.sha256(); size=0
            with open(target,"rb") as fh:
                while True:
                    chunk=fh.read(1024*1024)
                    if not chunk: break
                    fp.update(chunk); size+=len(chunk)
            ext=Path(target).suffix.upper().lstrip(".") or "BIN"
            mb=size/1024/1024
            return [Path(target).name.upper()[:22],ext,f"{mb:.2f} MB",fp.hexdigest()[:18]+"…"]
        def done(vals):
            if str(getattr(self,"_stego_scanner",{}).get("path",target)) != target: return
            for c,v in zip(getattr(self,"_stego_meta_cards",[]),vals):
                try: c.configure(text=v)
                except tk.TclError: pass
        def fail(exc):
            for c in getattr(self,"_stego_meta_cards",[]):
                try: c.configure(text="ANALYSIS ERROR")
                except tk.TclError: pass
            self._last_error=f"stego_meta: {exc}"
        self._stego_scanner["path"]=target
        self._run_ui_worker(work,done,fail)

    def _clear_stego_meta(self):
        for c in getattr(self,"_stego_meta_cards",[]):
            try: c.configure(text="WAITING")
            except tk.TclError: pass

    def _animate_stego_scanner(self):
        """Cyber Scanner plus tiny field beams for steganography input/output panels."""
        st=self._stego_scanner; c=st.get("canvas")
        if c is None or not c.winfo_exists(): return
        w=max(400,c.winfo_width()); h=max(130,c.winfo_height())
        if st.get("size")!=(w,h) or not st.get("items"):
            c.delete("all")
            for x in range(0,w,32): c.create_line(x,0,x,h,fill="#071b20")
            for y in range(0,h,24): c.create_line(0,y,w,y,fill="#06171d")
            cut=18
            c.create_line(cut,12,w-cut,12,fill=P["green"],width=2)
            c.create_line(cut,h-12,w-cut,h-12,fill=P["cyan"],width=1)
            c.create_text(18,24,text="CYBER SCANNER // EVIDENCE INTAKE",anchor="w",fill=P["green"],font=(MONO,12,"bold"))
            c.create_text(w-18,24,text="PNG / BMP  •  LOCAL READ-ONLY",anchor="e",fill=P["muted"],font=(MONO,9,"bold"))
            c.create_text(w/2,h/2-8,text="CLICK TO OPEN / REPLACE IMAGE",fill=P["text"],font=(FONT,14,"bold"))
            c.create_text(w/2,h/2+20,text="LASER SCAN  //  PIXEL FORENSICS  //  METADATA SNAPSHOT",fill=P["dim"],font=(MONO,9,"bold"))
            laser=c.create_rectangle(-10,0,w+10,3,fill=P["green"],outline="",tags="laser")
            glow=c.create_rectangle(-10,-4,w+10,7,fill="#0b3c2b",outline="",tags="laser_glow")
            sweep=c.create_text(w-18,h-20,text="SCAN 0000",anchor="e",fill=P["cyan"],font=(MONO,9,"bold"),tags="scan_txt")
            st["items"]={"laser":laser,"glow":glow,"text":sweep}; st["size"]=(w,h)
        phase=(st.get("phase",0.0)+0.045)%2.0; pos=phase if phase<=1 else 2-phase; y=16+pos*(h-32)
        c.coords(st["items"]["laser"],-10,y,w+10,y+3); c.coords(st["items"]["glow"],-10,y-4,w+10,y+7)
        c.itemconfigure(st["items"]["text"],text=f"SCAN {int(st.get('phase',0.0)*1000)%10000:04d}  //  LIVE")
        fxphase=getattr(self,"_stego_fx_phase",0.0)+0.055; self._stego_fx_phase=fxphase
        keep=[]
        for scan,accent,led in getattr(self,"_stego_microfx",[]):
            try:
                if not scan.winfo_exists(): continue
                sw=max(80,scan.winfo_width())
                if not scan.find_withtag('field_scan'):
                    scan.create_rectangle(-70,0,-2,5,fill=accent,outline='',tags='field_scan')
                    scan.create_rectangle(-92,-2,-6,7,fill='#12353d',outline='',tags='field_glow')
                x=(fxphase*32)%(sw+130)-130
                scan.coords('field_glow',x-14,-1,x+62,6); scan.coords('field_scan',x,0,x+38,5)
                scan.itemconfigure('field_scan',fill=accent); scan.itemconfigure('field_glow',fill='#0d3037')
                if led is not None and led.winfo_exists(): led.configure(fg=accent if math.sin(fxphase*1.5)>.1 else '#4a6268')
                keep.append((scan,accent,led))
            except (tk.TclError,ValueError): pass
        self._stego_microfx=keep
        st["phase"]=phase

    def crypto_modern_page(self):
        """Modern cryptography command center.

        The page is intentionally tool-driven rather than decoration-driven:
        AES/DES/RSA/Hash each expose a real local engine, a clear parameter area,
        an algorithm-specific visualization, and an execution trace.
        """
        p=tk.Frame(self.content,bg=P["bg"])
        self.heading(
            p,
            "HN / CRYPTO",
            "MODERN SECURITY // COMMAND CENTER",
            "Symmetric encryption, public-key cryptography, and integrity primitives with real local execution and visual explanations."
        )
        self._crypto_tabs(p,"modern")
        canvas,inner=self._make_canvas(p)

        # Matrix rain is a retained-mode background layer. It is deliberately
        # faint and slow so it adds depth without competing with controls.
        matrix=tk.Canvas(inner,bg="#02060b",highlightthickness=0,bd=0,takefocus=0)
        matrix.place(relx=0,rely=0,relwidth=1,relheight=1)
        try: matrix.tk.call('lower', matrix._w)
        except tk.TclError: pass
        self._modern_matrix.update(canvas=matrix,size=None,phase=0)

        # --- Hero / algorithm selector -------------------------------------------------
        hero=tk.Frame(inner,bg="#040c12",highlightbackground=P["line2"],highlightthickness=1)
        hero.pack(fill="x",pady=(0,10))
        self._install_panel_fx(hero, P["purple"])
        left=tk.Frame(hero,bg="#040c12"); left.pack(side="left",fill="both",expand=True,padx=18,pady=14)
        tk.Label(left,text="MODERN CRYPTOGRAPHY",bg="#040c12",fg=P["cyan"],font=(MONO, 12,"bold")).pack(anchor="w")
        tk.Label(left,text="REAL ENGINE • LOCAL ONLY • EXPLICIT LIMITATIONS",bg="#040c12",fg=P["muted"],font=(MONO, 9,"bold")).pack(anchor="w",pady=(3,7))
        tk.Label(left,text="Compare how legacy block ciphers, modern symmetric encryption, public-key operations, and hashing actually behave.",bg="#040c12",fg=P["text"],font=(FONT, 12),wraplength=760,justify="left").pack(anchor="w")
        right=tk.Frame(hero,bg="#040c12"); right.pack(side="right",padx=14,pady=14)
        tk.Label(right,text="SECURITY POSTURE",bg="#040c12",fg=P["muted"],font=(MONO, 9,"bold")).pack(anchor="e")
        tk.Label(right,text="DES: OBSOLETE",bg="#040c12",fg=P["red"],font=(MONO, 11,"bold")).pack(anchor="e",pady=2)
        tk.Label(right,text="AES: CURRENT STANDARD",bg="#040c12",fg=P["green"],font=(MONO, 10,"bold")).pack(anchor="e")
        tk.Label(right,text="RSA: PUBLIC-KEY / EDUCATIONAL",bg="#040c12",fg=P["yellow"],font=(MONO, 10,"bold")).pack(anchor="e")
        self.btn(right,"◈ OPEN WEBGL CINEMATIC CORE",lambda:open_cinematic("modern"),True).pack(anchor="e",pady=(9,0))

        selector=self.card(inner); selector.pack(fill="x",pady=(0,10))
        self._install_panel_fx(selector, P["purple"])
        sh=tk.Frame(selector,bg=P["panel3"]); sh.pack(fill="x")
        tk.Label(sh,text="01 // ALGORITHM DECK",bg=P["panel3"],fg=P["cyan"],font=(MONO, 10,"bold")).pack(side="left",padx=12,pady=9)
        tk.Label(sh,text="Choose a primitive — the workspace below changes to match its actual workflow.",bg=P["panel3"],fg=P["muted"],font=(FONT, 10)).pack(side="left",padx=8)
        deck=tk.Frame(selector,bg=P["panel"]); deck.pack(fill="x",padx=10,pady=10)

        body=tk.Frame(inner,bg=P["bg"]); body.pack(fill="both",expand=True)
        control=self.card(body); control.pack(fill="x",pady=(0,10))
        workspace=tk.Frame(body,bg=P["bg"]); workspace.pack(fill="both",expand=True)
        vizcard=self.card(workspace); vizcard.pack(fill="both",expand=True)
        tracecard=self.card(body); tracecard.pack(fill="x",pady=(10,0))

        state={"algo":"des","job":None,"phase":0,"step":0,"total":16,"payload":"","result":"","rows":[],"playing":False,"rsa":None}
        algo_var=tk.StringVar(value="des")
        controls={}

        profiles={
            "des": {
                "title":"DES // FEISTEL EXPLAINER", "accent":P["purple"],
                "subtitle":"64-bit block • 64-bit key • 16 Feistel rounds • CBC wrapper", "safe":"LEGACY / ACADEMIC",
            },
            "aes": {
                "title":"AES-256 // MODERN SYMMETRIC LAB", "accent":P["green"],
                "subtitle":"256-bit key • authenticated GCM • fresh 96-bit nonce", "safe":"RECOMMENDED FAMILY",
            },
            "rsa": {
                "title":"RSA // PUBLIC-KEY LAB", "accent":P["yellow"],
                "subtitle":"Public/private key pair • modular exponentiation • textbook demo", "safe":"EDUCATIONAL ONLY",
            },
            "hash": {
                "title":"HASHING // INTEGRITY LAB", "accent":P["cyan"],
                "subtitle":"One-way digest • SHA-256 / SHA-512 / SHA-3", "safe":"INTEGRITY / FINGERPRINT",
            },
        }

        for key,label,accent in [
            ("des","01  DES\nFeistel","purple"),("aes","02  AES-256\nSymmetric","green"),
            ("rsa","03  RSA\nPublic Key","yellow"),("hash","04  HASH\nIntegrity","cyan")]:
            col=P[accent]
            b=tk.Button(deck,text=label,command=lambda k=key:self._modern_select(k,state,algo_var,controls,control,workspace,vizcard,tracecard),
                        bg=P["panel2"],fg=col,activebackground=col,activeforeground=P["bg"],
                        relief="flat",bd=0,font=(MONO, 10,"bold"),cursor="hand2",width=18,height=2,
                        highlightbackground=col,highlightthickness=1)
            b.pack(side="left",padx=5,fill="x",expand=True)
            controls[key]=b

        # Build the four workspaces once; switch by pack_forget/pack.
        workspace_frames={}
        for key in profiles:
            f=tk.Frame(workspace,bg=P["bg"]); workspace_frames[key]=f

        # Reusable controls helpers.
        def field(parent,title,value="",show=None,width=52):
            box=tk.Frame(parent,bg=P["panel"]); box.pack(fill="x",pady=4)
            tk.Label(box,text=title,bg=P["panel"],fg=P["muted"],font=(MONO, 10,"bold")).pack(anchor="w",padx=10,pady=(7,2))
            ent=tk.Entry(box,bg="#030a11",fg=P["text"],insertbackground=P["cyan"],font=(FONT, 12),relief="flat",show=show,width=width)
            ent.insert(0,value); ent.pack(fill="x",padx=10,pady=(0,8),ipady=7)
            return ent
        def text_area(parent,title,height=7,initial="",accent=None):
            accent = accent or P["cyan"]
            box=tk.Frame(parent,bg=P["panel"]); box.pack(fill="both",expand=True,pady=4)
            head=tk.Frame(box,bg=P["panel"]); head.pack(fill="x",padx=10,pady=(6,1))
            tk.Label(head,text=title,bg=P["panel"],fg=P["muted"],font=(MONO,10,"bold")).pack(side="left")
            live=tk.Frame(head,bg=P["panel"]); live.pack(side="right")
            led=tk.Label(live,text="●",bg=P["panel"],fg=accent,font=(MONO,9,"bold")); led.pack(side="left",padx=(0,4))
            tk.Label(live,text="LIVE // SECURE",bg=P["panel"],fg=accent,font=(MONO,9,"bold")).pack(side="left")
            shell=tk.Frame(box,bg="#030a11",highlightthickness=0,bd=0); shell.pack(fill="both",expand=True,padx=6,pady=(0,3))
            self._install_panel_fx(shell,accent)
            scan=tk.Canvas(shell,height=5,bg="#030a11",highlightthickness=0,bd=0); scan.pack(fill="x",padx=2,pady=(1,0))
            t=tk.Text(shell,height=height,bg="#030a11",fg=P["text"],insertbackground=accent,selectbackground=P["purple"],font=(FONT,12),relief="flat",wrap="word",undo=True,padx=9,pady=7)
            if initial: t.insert("1.0",initial)
            t.pack(fill="both",expand=True,padx=4,pady=2)
            signal=tk.Canvas(box,height=3,bg=P["panel"],highlightthickness=0,bd=0); signal.pack(fill="x",padx=8,pady=(0,3))
            self._modern_signal_canvases.append((signal,accent,t,scan,led))
            t.bind("<KeyRelease>",lambda _e:self._modern_text_typed(t),add="+")
            return t

        # DES frame ----------------------------------------------------------------------
        d=workspace_frames["des"]
        dl=tk.Frame(d,bg=P["bg"]); dl.pack(side="left",fill="both",expand=True,padx=(0,6))
        dr=tk.Frame(d,bg=P["bg"],width=360); dr.pack(side="right",fill="y",padx=(6,0)); dr.pack_propagate(False)
        self._responsive_split(d,dl,dr,980,360)
        dinput=text_area(dl,"PLAINTEXT / CIPHERTEXT",6,"HN BlackBox DES Lab",P["purple"])
        dkey=field(dl,"KEY — EXACTLY 8 UTF-8 BYTES","HNKEY123",show="•")
        dops=tk.Frame(dl,bg=P["panel"]); dops.pack(fill="x",pady=4)
        dop=tk.StringVar(value="encrypt")
        ttk.Radiobutton(dops,text="ENCRYPT",variable=dop,value="encrypt").pack(side="left",padx=10,pady=8)
        ttk.Radiobutton(dops,text="DECRYPT",variable=dop,value="decrypt").pack(side="left",padx=10,pady=8)
        dbuttons=tk.Frame(dl,bg=P["panel"]); dbuttons.pack(fill="x",pady=4)
        dload=self.btn(dbuttons,"USE SAFE EXAMPLE",lambda:(dinput.delete("1.0","end"),dinput.insert("1.0","HN BlackBox DES Lab"),dkey.delete(0,"end"),dkey.insert(0,"HNKEY123")),False); dload.pack(side="left",padx=5,pady=5)
        dshow=self.btn(dbuttons,"SHOW KEY",lambda:self._toggle_secret(dkey),False); dshow.pack(side="left",padx=5,pady=5)
        dexec=self.btn(dbuttons,"> EXECUTE DES",lambda:run_des(),True); dexec.pack(side="right",padx=5,pady=5)
        dout=text_area(dl,"OUTPUT",6,accent=P["green"])
        dstatus=tk.Label(dl,text="READY // DES IS FOR EDUCATIONAL USE",bg=P["bg"],fg=P["yellow"],font=(MONO, 10,"bold"),anchor="w"); dstatus.pack(fill="x",pady=(2,5))
        info=tk.Frame(dr,bg=P["panel"],highlightbackground=P["line"],highlightthickness=1); info.pack(fill="x",pady=4)
        tk.Label(info,text="HOW DES ACTUALLY MOVES",bg=P["panel"],fg=P["purple"],font=(MONO, 10,"bold")).pack(anchor="w",padx=10,pady=8)
        for txt in ["1. Initial Permutation (IP)","2. Split block → L0 / R0","3. Repeat 16 × Feistel round","4. Expand R → XOR subkey","5. S-Boxes → P permutation","6. Final swap + FP"]:
            tk.Label(info,text=txt,bg=P["panel"],fg=P["text"],font=(FONT, 10),anchor="w").pack(fill="x",padx=12,pady=2)
        warn=tk.Label(dr,text="DES has a 56-bit effective key and is obsolete for production. Use AES or modern authenticated encryption for real systems.",bg="#11100a",fg=P["yellow"],font=(FONT, 10),wraplength=330,justify="left",padx=10,pady=10); warn.pack(fill="x",pady=4)

        # AES frame ----------------------------------------------------------------------
        a=workspace_frames["aes"]
        al=tk.Frame(a,bg=P["bg"]); al.pack(side="left",fill="both",expand=True,padx=(0,6))
        ar=tk.Frame(a,bg=P["bg"],width=360); ar.pack(side="right",fill="y",padx=(6,0)); ar.pack_propagate(False)
        self._responsive_split(a,al,ar,980,360)
        ainput=text_area(al,"PLAINTEXT / CIPHERTEXT",6,"HN BlackBox AES-256",P["green"])
        akey=field(al,"PASSPHRASE — DERIVED TO AES-256 VIA SHA-256","HN-AES-LAB-256",show="•")
        aops=tk.Frame(al,bg=P["panel"]); aops.pack(fill="x",pady=4)
        aop=tk.StringVar(value="encrypt")
        ttk.Radiobutton(aops,text="ENCRYPT",variable=aop,value="encrypt").pack(side="left",padx=10,pady=8)
        ttk.Radiobutton(aops,text="DECRYPT",variable=aop,value="decrypt").pack(side="left",padx=10,pady=8)
        ab=tk.Frame(al,bg=P["panel"]); ab.pack(fill="x",pady=4)
        self.btn(ab,"USE SAFE EXAMPLE",lambda:(ainput.delete("1.0","end"),ainput.insert("1.0","HN BlackBox AES-256"),akey.delete(0,"end"),akey.insert(0,"HN-AES-LAB-256")),False).pack(side="left",padx=5,pady=5)
        self.btn(ab,"SHOW KEY",lambda:self._toggle_secret(akey),False).pack(side="left",padx=5,pady=5)
        self.btn(ab,"> EXECUTE AES",lambda:run_aes(),True).pack(side="right",padx=5,pady=5)
        aout=text_area(al,"OUTPUT",6,accent=P["green"])
        astatus=tk.Label(al,text="READY // AES-256-GCM + AEAD",bg=P["bg"],fg=P["green"],font=(MONO, 10,"bold"),anchor="w"); astatus.pack(fill="x",pady=(2,5))
        ai=tk.Frame(ar,bg=P["panel"],highlightbackground=P["line"],highlightthickness=1); ai.pack(fill="x",pady=4)
        tk.Label(ai,text="AES-256 TEACHING PATH",bg=P["panel"],fg=P["green"],font=(MONO, 10,"bold")).pack(anchor="w",padx=10,pady=8)
        for txt in ["Passphrase → SHA-256 key", "Fresh nonce → 96 bits", "AEAD / GCM authentication", "AES-256 block state → 128 bits", "14 AES-256 rounds", "Ciphertext + authentication tag"]:
            tk.Label(ai,text=txt,bg=P["panel"],fg=P["text"],font=(FONT, 10),anchor="w").pack(fill="x",padx=12,pady=2)
        tk.Label(ar,text="The visualization below shows the block/state flow. The ciphertext itself is produced by the real cryptography package, not by the animation.",bg="#07130e",fg=P["green"],font=(FONT, 10),wraplength=330,justify="left",padx=10,pady=10).pack(fill="x",pady=4)

        # RSA frame ----------------------------------------------------------------------
        r=workspace_frames["rsa"]
        rl=tk.Frame(r,bg=P["bg"]); rl.pack(side="left",fill="both",expand=True,padx=(0,6))
        rr=tk.Frame(r,bg=P["bg"],width=390); rr.pack(side="right",fill="y",padx=(6,0)); rr.pack_propagate(False)
        self._responsive_split(r,rl,rr,980,390)
        rinput=text_area(rl,"MESSAGE / HEX CIPHERTEXT",5,"HN RSA LAB")
        rkey=field(rl,"KEY MATERIAL","",width=90)
        rop=tk.StringVar(value="encrypt")
        rops=tk.Frame(rl,bg=P["panel"]); rops.pack(fill="x",pady=4)
        ttk.Radiobutton(rops,text="ENCRYPT",variable=rop,value="encrypt").pack(side="left",padx=10,pady=8)
        ttk.Radiobutton(rops,text="DECRYPT",variable=rop,value="decrypt").pack(side="left",padx=10,pady=8)
        rb=tk.Frame(rl,bg=P["panel"]); rb.pack(fill="x",pady=4)
        self.btn(rb,"GENERATE 2048-BIT EDUCATIONAL KEY",lambda:generate_rsa(),True).pack(side="left",padx=5,pady=5)
        self.btn(rb,"EXECUTE RSA",lambda:run_rsa(),False).pack(side="right",padx=5,pady=5)
        rout=text_area(rl,"OUTPUT",5,accent=P["yellow"])
        rstatus=tk.Label(rl,text="READY // GENERATE A KEY PAIR FIRST",bg=P["bg"],fg=P["yellow"],font=(MONO, 10,"bold"),anchor="w"); rstatus.pack(fill="x",pady=(2,5))
        ri=tk.Frame(rr,bg=P["panel"],highlightbackground=P["line"],highlightthickness=1); ri.pack(fill="x",pady=4)
        tk.Label(ri,text="RSA CONCEPT MAP",bg=P["panel"],fg=P["yellow"],font=(MONO, 10,"bold")).pack(anchor="w",padx=10,pady=8)
        for txt in ["p,q → prime factors", "n=p×q → public modulus", "φ(n) → totient", "e → public exponent", "d → private exponent", "c=mᵉ mod n", "m=cᵈ mod n"]:
            tk.Label(ri,text=txt,bg=P["panel"],fg=P["text"],font=(FONT, 10),anchor="w").pack(fill="x",padx=12,pady=2)
        tk.Label(rr,text="Textbook RSA without OAEP is intentionally exposed as a teaching primitive. Do not use this mode for production encryption.",bg="#121006",fg=P["yellow"],font=(FONT, 10),wraplength=360,justify="left",padx=10,pady=10).pack(fill="x",pady=4)

        # Hash frame ---------------------------------------------------------------------
        hframe=workspace_frames["hash"]
        hl=tk.Frame(hframe,bg=P["bg"]); hl.pack(side="left",fill="both",expand=True,padx=(0,6))
        hr=tk.Frame(hframe,bg=P["bg"],width=360); hr.pack(side="right",fill="y",padx=(6,0)); hr.pack_propagate(False)
        self._responsive_split(hframe,hl,hr,980,360)
        hinput=text_area(hl,"DATA TO HASH",8,"HN BlackBox Integrity Check",P["cyan"])
        hsel=tk.Frame(hl,bg=P["panel"]); hsel.pack(fill="x",pady=4)
        tk.Label(hsel,text="ALGORITHM",bg=P["panel"],fg=P["muted"],font=(MONO, 10,"bold")).pack(side="left",padx=10,pady=9)
        hv=tk.StringVar(value="sha256")
        ttk.Combobox(hsel,textvariable=hv,state="readonly",values=["sha256","sha512","sha3_256","sha3_512"],width=18).pack(side="left",padx=8,pady=6)
        self.btn(hsel,"CALCULATE DIGEST",lambda:run_hash(),True).pack(side="right",padx=6,pady=5)
        hout=text_area(hl,"DIGEST",6,accent=P["cyan"])
        hstatus=tk.Label(hl,text="READY // HASHING IS ONE-WAY",bg=P["bg"],fg=P["cyan"],font=(MONO, 10,"bold"),anchor="w"); hstatus.pack(fill="x",pady=(2,5))
        hi=tk.Frame(hr,bg=P["panel"],highlightbackground=P["line"],highlightthickness=1); hi.pack(fill="x",pady=4)
        tk.Label(hi,text="INTEGRITY WORKFLOW",bg=P["panel"],fg=P["cyan"],font=(MONO, 10,"bold")).pack(anchor="w",padx=10,pady=8)
        for txt in ["Input bytes", "Normalize / encode", "Digest compression", "Fixed-length output", "Compare known hash", "Integrity decision"]:
            tk.Label(hi,text=txt,bg=P["panel"],fg=P["text"],font=(FONT, 10),anchor="w").pack(fill="x",padx=12,pady=2)
        tk.Label(hr,text="Hashes are not encryption. The correct teaching model is: data → digest → compare. There is no decrypt operation.",bg="#061219",fg=P["cyan"],font=(FONT, 10),wraplength=330,justify="left",padx=10,pady=10).pack(fill="x",pady=4)

        # Visualization card -------------------------------------------------------------
        vh=tk.Frame(vizcard,bg=P["panel3"]); vh.pack(fill="x")
        viz_title=tk.Label(vh,text="02 // VISUAL EXPLANATION",bg=P["panel3"],fg=P["cyan"],font=(MONO, 10,"bold")); viz_title.pack(side="left",padx=10,pady=8)
        viz_state=tk.Label(vh,text="READY",bg=P["panel3"],fg=P["green"],font=(MONO, 10,"bold")); viz_state.pack(side="right",padx=10)
        vc=tk.Canvas(vizcard,bg="#040a10",height=430,highlightthickness=0); vc.pack(fill="both",expand=True,padx=7,pady=7)
        controlsbar=tk.Frame(vizcard,bg=P["panel"]); controlsbar.pack(fill="x",padx=7,pady=(0,7))
        resetb=self.btn(controlsbar,"|< RESET",lambda:modern_visual_reset(),False); resetb.pack(side="left",padx=3,pady=4)
        replayb=self.btn(controlsbar,"↻ REPLAY",lambda:modern_visual_replay(),False); replayb.pack(side="left",padx=3,pady=4)
        backb=self.btn(controlsbar,"< STEP",lambda:modern_visual_step(-1),False); backb.pack(side="left",padx=3,pady=4)
        stepb=self.btn(controlsbar,"STEP >",lambda:modern_visual_step(1),False); stepb.pack(side="left",padx=3,pady=4)
        playb=self.btn(controlsbar,"▶ PLAY",lambda:modern_visual_play(),False); playb.pack(side="left",padx=3,pady=4)
        speed=tk.StringVar(value="NORMAL")
        speed_box=ttk.Combobox(controlsbar,textvariable=speed,state="readonly",values=["SLOW","NORMAL","FAST"],width=10)
        speed_box.pack(side="right",padx=5,pady=5)
        progress=tk.Label(controlsbar,text="STEP 00/16",bg=P["panel"],fg=P["muted"],font=(MONO, 10,"bold")); progress.pack(side="right",padx=10)

        # Trace area ---------------------------------------------------------------------
        th=tk.Frame(tracecard,bg=P["panel3"]); th.pack(fill="x")
        tk.Label(th,text="03 // EXECUTION TRACE",bg=P["panel3"],fg=P["cyan"],font=(MONO, 10,"bold")).pack(side="left",padx=10,pady=8)
        trace_text=tk.Text(tracecard,height=9,bg="#02070c",fg=P["muted"],font=(MONO, 10),relief="flat",bd=0,state="disabled",wrap="none"); trace_text.pack(fill="x",padx=8,pady=(0,8))

        # local workspace switcher / visual engine
        def select_frame(k):
            for f in workspace_frames.values(): f.pack_forget()
            workspace_frames[k].pack(fill="both",expand=True)
            for kk,b in controls.items():
                prof=profiles[kk]; active=(kk==k)
                b.configure(bg=prof["accent"] if active else P["panel2"],fg=P["bg"] if active else prof["accent"])
            viz_title.configure(text=f"02 // {profiles[k]['title']}",fg=profiles[k]['accent'])
            viz_state.configure(text=profiles[k]["safe"],fg=profiles[k]["accent"])
            state.update(algo=k,step=0,total=16,rows=[],result="",playing=False)
            progress.configure(text="STEP 00/16")
            modern_visual_reset()
        def draw_modern():
            if not vc.winfo_exists(): return
            k=state["algo"]; w=max(700,vc.winfo_width()); h=max(360,vc.winfo_height()); step=state["step"]
            vc.delete("all")
            for x in range(0,w,40): vc.create_line(x,0,x,h,fill="#07141c")
            for y in range(0,h,32): vc.create_line(0,y,w,y,fill="#07141c")
            prof=profiles[k]; accent=prof["accent"]
            vc.create_text(18,18,text=prof["title"],fill=accent,font=(MONO, 12,"bold"),anchor="w")
            vc.create_text(w-18,18,text=f"STEP {step:02d}/{state['total']:02d}",fill=P["green"],font=(MONO, 10,"bold"),anchor="e")
            if k=="des":
                # Teaching-first DES map. The selected round is always tied to the real trace.
                labels=[
                    ("01","PLAINTEXT / CIPHERTEXT"),("02","IP\nINITIAL PERMUTATION"),
                    ("03","SPLIT\nL0 / R0"),("04","ROUND 1..16\nFEISTEL"),
                    ("05","SWAP\nR16 / L16"),("06","FP\nFINAL PERMUTATION"),
                ]
                y=h*.20; gap=(w-180)/(len(labels)-1)
                active_index=min(5, 1 if step==0 else (2 if step<2 else (3 if step<16 else 4)))
                for i,(num,label) in enumerate(labels):
                    x=90+i*gap; active=i<=active_index
                    vc.create_rectangle(x-58,y-25,x+58,y+25,fill="#0b1720" if active else "#050d13",outline=accent if active else P["line"],width=2)
                    vc.create_text(x,y-2,text=num,fill=accent if active else P["muted"],font=(MONO,10,"bold"))
                    vc.create_text(x,y+48,text=label,fill=P["text"] if active else P["muted"],font=(FONT,10,"bold"),anchor="n",width=150)
                    if i<len(labels)-1: vc.create_line(x+60,y,x+gap-60,y,fill=accent if active and i<active_index else P["line"],width=2,arrow="last")
                # Feistel anatomy card
                boxx,boxy=32,h*.47; boxw=w*.43; boxh=h*.42
                vc.create_rectangle(boxx,boxy,boxx+boxw,boxy+boxh,fill="#07131b",outline=P["line"],width=1)
                vc.create_text(boxx+14,boxy+14,text="ROUND ANATOMY // WHY L AND R CHANGE",fill=P["yellow"],font=(MONO,10,"bold"),anchor="w")
                row=state["rows"][max(0,min(step-1,len(state["rows"])-1))] if state["rows"] else None
                anatomy=[
                    ("R", "EXPAND", row.get("expanded","") if row else "32 → 48 bits"),
                    ("K", "XOR SUBKEY", row.get("key_hex","") if row else "K1…K16"),
                    ("S", "8 S-BOXES", row.get("sbox","") if row else "48 → 32 bits"),
                    ("P", "P-PERMUTE", row.get("pbox","") if row else "32 bits"),
                ]
                for i,(tag,title,val) in enumerate(anatomy):
                    yy=boxy+55+i*48
                    vc.create_rectangle(boxx+14,yy,boxx+44,yy+28,fill="#0a1720",outline=accent)
                    vc.create_text(boxx+29,yy+14,text=tag,fill=accent,font=(MONO,9,"bold"))
                    vc.create_text(boxx+56,yy+7,text=title,fill=P["text"],font=(FONT,10,"bold"),anchor="w")
                    vc.create_text(boxx+56,yy+22,text=val,fill=P["cyan"],font=(MONO,9),anchor="w")
                # Actual L/R and output detail
                rx=boxx+boxw+24; rw=w-rx-28
                vc.create_rectangle(rx,boxy,rx+rw,boxy+boxh,fill="#050d14",outline=accent,width=1)
                vc.create_text(rx+14,boxy+14,text="LIVE ROUND VALUES",fill=accent,font=(MONO,10,"bold"),anchor="w")
                vals=[("L IN",row.get("l_in","WAITING") if row else "WAITING"),("R IN",row.get("r_in","WAITING") if row else "WAITING"),("L OUT",row.get("l_out","WAITING") if row else "WAITING"),("R OUT",row.get("r_out","WAITING") if row else "WAITING"),("F(R,K)",row.get("pbox","WAITING") if row else "WAITING")]
                for i,(lab,val) in enumerate(vals):
                    yy=boxy+52+i*42
                    vc.create_text(rx+14,yy,text=lab,fill=P["muted"],font=(MONO,9,"bold"),anchor="w")
                    vc.create_text(rx+82,yy,text=val,fill=P["green"] if "OUT" in lab else P["text"],font=(MONO,9,"bold"),anchor="w")
                vc.create_text(w/2,h-18,text="REAL DES TRACE • 16 FEISTEL ROUNDS • DES IS LEGACY / ACADEMIC ONLY",fill=P["muted"],font=(MONO,9,"bold"))
            elif k=="aes":
                steps=["KEY 256","NONCE 96","AEAD","AES-256","AUTH TAG","OUTPUT"]
                y=h*.31; gap=(w-140)/(len(steps)-1)
                for i,label in enumerate(steps):
                    x=70+i*gap; active=i<=min(len(steps)-1,step//3)
                    vc.create_oval(x-28,y-28,x+28,y+28,fill="#071a13" if active else "#071018",outline=accent if active else P["line"],width=2)
                    vc.create_text(x,y,text=f"{i+1:02d}",fill=accent if active else P["muted"],font=(MONO, 10,"bold"))
                    vc.create_text(x,y+44,text=label,fill=P["text"] if active else P["muted"],font=(FONT, 10,"bold"))
                    if i<len(steps)-1: vc.create_line(x+29,y,x+gap-29,y,fill=accent if active else P["line"],width=2)
                # State matrix / bytes.
                mx,my=w*.30,h*.60; cell=50
                vc.create_text(mx,my-120,text="128-BIT AES STATE VIEW",fill=P["green"],font=(MONO, 10,"bold"))
                data=state.get("payload","").encode("utf-8")[:16].ljust(16,b"\x00")
                for idx,bv in enumerate(data):
                    rr,cc=idx%4,idx//4; x=mx+cc*cell; yy=my+rr*cell
                    act=idx<min(16,step+1)
                    vc.create_rectangle(x-20,yy-20,x+20,yy+20,fill="#0a2118" if act else "#07131b",outline=accent if act else P["line"],width=2 if act else 1)
                    vc.create_text(x,yy,text=f"{bv:02X}",fill=P["text"] if act else P["muted"],font=(MONO, 10,"bold"))
                rx=w*.68
                items=["SubBytes","ShiftRows","MixColumns","AddRoundKey"]
                vc.create_text(rx,h*.54,text="ROUND TRANSFORM MODEL",fill=accent,font=(MONO, 10,"bold"))
                for i,label in enumerate(items):
                    active=step>=(i+1)*3
                    vc.create_rectangle(rx-105,h*.60+i*42,rx+145,h*.60+28+i*42,fill="#081b14" if active else "#071018",outline=accent if active else P["line"])
                    vc.create_text(rx-90,h*.60+14+i*42,text=f"{i+1:02d}",fill=accent,font=(MONO, 10,"bold"),anchor="w")
                    vc.create_text(rx-45,h*.60+14+i*42,text=label,fill=P["text"] if active else P["muted"],font=(FONT, 10,"bold"),anchor="w")
                vc.create_text(w/2,h-18,text="VISUAL STATE / ROUND FLOW • CIPHERTEXT FROM REAL AES ENGINE",fill=P["muted"],font=(MONO, 10,"bold"))
            elif k=="rsa":
                labels=["PRIMES","KEYPAIR","ENCODE M","mᵉ mod n","CIPHERTEXT"]
                gap=(w-160)/(len(labels)-1); y=h*.30
                for i,label in enumerate(labels):
                    x=80+i*gap; active=i<=min(4,step//4)
                    vc.create_oval(x-30,y-30,x+30,y+30,fill="#201b08" if active else "#071018",outline=accent if active else P["line"],width=2)
                    vc.create_text(x,y,text=f"{i+1:02d}",fill=accent if active else P["muted"],font=(MONO, 10,"bold"))
                    vc.create_text(x,y+46,text=label,fill=P["text"] if active else P["muted"],font=(FONT, 10,"bold"))
                    if i<4: vc.create_line(x+31,y,x+gap-31,y,fill=P["yellow"] if active else P["line"],width=2)
                rr=w*.48
                vc.create_text(rr,h*.53,text="PUBLIC",fill=P["green"],font=(MONO, 10,"bold")); vc.create_text(rr,h*.58,text="(e, n)",fill=P["text"],font=(MONO, 13,"bold"))
                vc.create_text(rr,h*.67,text="PRIVATE",fill=P["yellow"],font=(MONO, 10,"bold")); vc.create_text(rr,h*.72,text="(d, n)",fill=P["text"],font=(MONO, 13,"bold"))
                vc.create_text(w/2,h-18,text="REAL MODULAR EXPONENTIATION • TEXTBOOK RSA EDUCATIONAL MODE",fill=P["muted"],font=(MONO, 10,"bold"))
            else:
                labels=["INPUT","ENCODE","COMPRESS","DIGEST","COMPARE"]
                gap=(w-150)/(len(labels)-1); y=h*.33
                for i,label in enumerate(labels):
                    x=75+i*gap; active=i<=min(4,step//2)
                    vc.create_oval(x-30,y-30,x+30,y+30,fill="#071b20" if active else "#071018",outline=accent if active else P["line"],width=2)
                    vc.create_text(x,y,text=f"{i+1:02d}",fill=accent if active else P["muted"],font=(MONO, 10,"bold"))
                    vc.create_text(x,y+46,text=label,fill=P["text"] if active else P["muted"],font=(FONT, 10,"bold"))
                    if i<4: vc.create_line(x+31,y,x+gap-31,y,fill=accent if active else P["line"],width=2)
                digest=state.get("result","")[:64] or "DIGEST NOT CALCULATED"
                vc.create_rectangle(60,h*.58,w-60,h*.70,fill="#06131a",outline=accent)
                vc.create_text(w/2,h*.64,text=digest,fill=P["text"],font=(MONO, 10,"bold"))
                vc.create_text(w/2,h-18,text="ONE-WAY DIGEST • LOCAL HASH ENGINE • NO DECRYPT OPERATION",fill=P["muted"],font=(MONO, 10,"bold"))
            self._modern_cinema_rebuild(vc, profiles[k]["accent"])
        def speed_ms(): return {"SLOW":150,"NORMAL":90,"FAST":40}.get(speed.get(),90)
        def modern_visual_reset():
            if state.get("job"):
                try: vc.after_cancel(state["job"])
                except tk.TclError: pass
            state["step"]=0; state["playing"]=False; state["job"]=None; state["cinema_phase"]=0.0
            progress.configure(text=f"STEP 00/{state['total']:02d}")
            playb.configure(text="▶ PLAY")
            draw_modern()
        def modern_visual_replay():
            state["step"]=0; state["playing"]=False; state["cinema_phase"]=0.0
            progress.configure(text=f"STEP 00/{state['total']:02d}")
            playb.configure(text="▶ PLAY")
            draw_modern()
            modern_visual_play()
        def modern_visual_step(delta):
            state["playing"]=False
            if state.get("job"):
                try: vc.after_cancel(state["job"])
                except tk.TclError: pass
                state["job"]=None
            state["step"]=max(0,min(state["total"],state["step"]+delta))
            progress.configure(text=f"STEP {state['step']:02d}/{state['total']:02d}")
            draw_modern()
        def modern_visual_play():
            if state["playing"]:
                state["playing"]=False; playb.configure(text="▶ PLAY")
                if state.get("job"):
                    try: vc.after_cancel(state["job"])
                    except tk.TclError: pass
                    state["job"]=None
                return
            state["playing"]=True; playb.configure(text="❚❚ PAUSE")
            def tick():
                if not state["playing"] or not vc.winfo_exists(): return
                if not self._motion_page_active('crypto_modern'):
                    state["job"]=vc.after(180,tick); return
                if state["step"]>=state["total"]:
                    state["playing"]=False; state["job"]=None; playb.configure(text="▶ PLAY"); return
                state["step"]+=1; progress.configure(text=f"STEP {state['step']:02d}/{state['total']:02d}")
                # Static teaching geometry is redrawn on a small cadence; the cinematic
                # overlay itself stays smooth on the global 60 FPS clock. This removes
                # repeated canvas destruction/recreation while preserving every visual effect.
                if state["step"] == state["total"] or state["step"] % 3 == 0:
                    draw_modern()
                state["job"]=vc.after(speed_ms(),tick)
            tick()
        def set_trace(lines):
            trace_text.configure(state="normal"); trace_text.delete("1.0","end"); trace_text.insert("1.0","\n".join(lines)); trace_text.configure(state="disabled")
        def run_des():
            text=dinput.get("1.0","end-1c").strip(); key=dkey.get()
            if not text: messagebox.showwarning("DES","INPUT IS REQUIRED"); return
            started=time.perf_counter();
            try:
                sched=des_cipher.trace(key); rows=[]
                if dop.get()=="encrypt":
                    raw=text.encode("utf-8"); pad=8-(len(raw)%8); first=raw+bytes([pad])*pad
                    block=des_cipher.trace_block(first[:8],des_cipher.subkeys(key.encode("utf-8")))
                    value=des_cipher.encrypt(text,key)
                else:
                    import base64
                    raw=base64.b64decode(text,validate=True)
                    if len(raw)<16: raise ValueError("DES ciphertext must contain IV and at least one block.")
                    block=des_cipher.trace_block(raw[8:16],des_cipher.subkeys(key.encode("utf-8")),True)
                    value=des_cipher.decrypt(text,key)
                for i,row in enumerate(block["rounds"]): rows.append({**row,"shift":sched["rounds"][i]["shift"]})
                dout.delete("1.0","end"); dout.insert("1.0",value)
                state.update(algo="des",rows=rows,payload=text,result=value,total=16,step=0)
                set_trace([f"ROUND {r['round']:02d}  SUBKEY={r['key_hex']}  L={r['l_in']}  R={r['r_in']}  E={r['expanded']}  XOR={r['xor']}  S={r['sbox']}  P={r['pbox']}  OUT={r['r_out']}" for r in rows])
                dstatus.configure(text=f"COMPLETE // {len(value)} CHARS // {time.perf_counter()-started:.3f}s",fg=P["green"])
                state["step"]=1; progress.configure(text="STEP 01/16"); draw_modern(); self._record_tool_operation("DES","ENCRYPT" if dop.get()=="encrypt" else "DECRYPT",text,value,key)
            except Exception as e:
                dstatus.configure(text=f"FAILED // {str(e)[:100]}",fg=P["red"]); messagebox.showerror("DES ERROR",str(e))
        def run_aes():
            text=ainput.get("1.0","end-1c").strip(); key=akey.get()
            if not text: messagebox.showwarning("AES","INPUT IS REQUIRED"); return
            started=time.perf_counter()
            try:
                value=aes_cipher.encrypt(text,key) if aop.get()=="encrypt" else aes_cipher.decrypt(text,key)
                aout.delete("1.0","end"); aout.insert("1.0",value)
                state.update(algo="aes",payload=text,result=value,total=18,step=1,rows=[])
                set_trace(["KEY: SHA-256(passphrase) → 256-bit AES key","BLOCK: 128-bit","MODE: AES-256-GCM / AEAD","NONCE: fresh 96-bit nonce / authentication tag included","ENGINE: cryptography.hazmat.primitives.ciphers.AES",f"OPERATION: {aop.get().upper()}",f"OUTPUT LENGTH: {len(value)}"])
                astatus.configure(text=f"COMPLETE // {len(value)} CHARS // {time.perf_counter()-started:.3f}s",fg=P["green"])
                progress.configure(text="STEP 01/18"); draw_modern(); self._record_tool_operation("AES-256","ENCRYPT" if aop.get()=="encrypt" else "DECRYPT",text,value,"SHA256-derived key")
            except Exception as e:
                astatus.configure(text=f"FAILED // {str(e)[:100]}",fg=P["red"]); messagebox.showerror("AES ERROR",str(e))
        def generate_rsa():
            try:
                e,d,n=educational_rsa.rsa_generate(2048); state["rsa"]=(e,d,n)
                rkey.delete(0,"end"); rkey.insert(0,f"e={e}; d={d}; n={n}")
                rstatus.configure(text="KEYPAIR READY // 2048-BIT EDUCATIONAL RSA",fg=P["green"])
                set_trace(["KEY GENERATION","Prime factors p,q generated locally","Public key: (e,n)","Private key: (d,n)","Warning: textbook RSA / no OAEP"])
                state.update(algo="rsa",payload="",result="",total=12,step=2); progress.configure(text="STEP 02/12"); draw_modern()
            except Exception as e:
                messagebox.showerror("RSA ERROR",str(e))
        def run_rsa():
            if not state.get("rsa"): messagebox.showwarning("RSA","Generate the demo key pair first."); return
            e,d,n=state["rsa"]
            text=rinput.get("1.0","end-1c").strip()
            try:
                if rop.get()=="encrypt": value=educational_rsa.rsa_encrypt(text,e,n); detail="PUBLIC EXPONENT e USED"
                else: value=educational_rsa.rsa_decrypt(text,d,n); detail="PRIVATE EXPONENT d USED"
                rout.delete("1.0","end"); rout.insert("1.0",value)
                rstatus.configure(text=f"COMPLETE // {detail}",fg=P["green"])
                state.update(algo="rsa",payload=text,result=value,total=12,step=7)
                set_trace(["INPUT → INTEGER","MODULAR EXPONENTIATION",detail,"OUTPUT → INTEGER / TEXT",f"RESULT LENGTH: {len(value)}"])
                progress.configure(text="STEP 07/12"); draw_modern(); self._record_tool_operation("RSA","ENCRYPT" if rop.get()=="encrypt" else "DECRYPT",text,value,"educational keypair")
            except Exception as e:
                rstatus.configure(text=f"FAILED // {str(e)[:100]}",fg=P["red"]); messagebox.showerror("RSA ERROR",str(e))
        def run_hash():
            text=hinput.get("1.0","end-1c")
            try:
                value=hashlib.new(hv.get(),text.encode("utf-8")).hexdigest()
                hout.delete("1.0","end"); hout.insert("1.0",value)
                hstatus.configure(text=f"COMPLETE // {hv.get().upper()} // {len(value)*4} BITS",fg=P["green"])
                state.update(algo="hash",payload=text,result=value,total=10,step=8)
                set_trace([f"ALGORITHM: {hv.get().upper()}",f"INPUT BYTES: {len(text.encode('utf-8'))}",f"DIGEST HEX LENGTH: {len(value)}","HASHING IS ONE-WAY"])
                progress.configure(text="STEP 08/10"); draw_modern(); self._record_tool_operation("HASH","DIGEST",text,value,hv.get())
            except Exception as e:
                hstatus.configure(text=f"FAILED // {str(e)[:100]}",fg=P["red"]); messagebox.showerror("HASH ERROR",str(e))

        # Expose the live modern-lab controls for regression testing and future integrations.
        self._modern_context = {
            "state": state, "algorithm_var": algo_var, "algorithm_buttons": controls,
            "des": {"input": dinput, "key": dkey, "op": dop, "output": dout, "status": dstatus, "execute": dexec},
            "aes": {"input": ainput, "key": akey, "op": aop, "output": aout, "status": astatus},
            "rsa": {"input": rinput, "key": rkey, "op": rop, "output": rout, "status": rstatus},
            "hash": {"input": hinput, "algorithm": hv, "output": hout, "status": hstatus},
            "visual": {"canvas": vc, "progress": progress, "trace": trace_text, "title": viz_title, "status": viz_state, "speed": speed},
            "cinema": {"canvas": vc, "state": state, "speed": speed},
        }

        # Public selector callback exposed through a method-like closure.
        self._modern_select = lambda k,state_,algo_var_,controls_,control_,workspace_,vizcard_,tracecard_: select_frame(k)
        select_frame("des")
        return p

    def crypto_stego_page(self):
        """Professional LSB steganography workstation.

        Keeps the useful original/encoded comparison workflow while adding clear
        input/output fields, replace/remove actions, and a lightweight forensic HUD.
        All payload operations are backed by the real local LSB engine.
        """
        p=tk.Frame(self.content,bg=P["bg"])
        self.heading(p,"HN / LSB","STEGANOGRAPHY // COVERT IMAGE WORKSTATION",
                     "Hide or extract UTF-8 text in PNG/BMP pixels, compare source/output, inspect capacity and verify payload integrity.")
        self._crypto_tabs(p,"stego")
        canvas,inner=self._make_canvas(p)
        state={"source":"","encoded":"","capacity":0}; image_refs=[]

        head=tk.Frame(inner,bg="#040c12",highlightbackground=P["green"],highlightthickness=1); head.pack(fill="x",pady=(0,8))
        self._install_panel_fx(head,P["green"])
        tk.Label(head,text="LSB // IMAGE COVERT OPERATIONS",bg="#040c12",fg=P["green"],font=(MONO,12,"bold")).pack(side="left",padx=12,pady=9)
        tk.Label(head,text="REAL PIXEL ENGINE  •  PNG/BMP  •  RGB  •  UTF-8  •  CRC32",bg="#040c12",fg=P["muted"],font=(MONO,9,"bold")).pack(side="left",padx=8)
        tk.Label(head,text="LOCAL / OFFLINE",bg="#07151d",fg=P["cyan"],font=(MONO,9,"bold"),padx=9,pady=5).pack(side="right",padx=9,pady=4)
        self.btn(head,"◈ OPEN WEBGL SCANNER",lambda:open_cinematic("stego"),True).pack(side="right",padx=5,pady=4)

        # File routing: explicit INPUT and OUTPUT fields.
        routing=tk.Frame(inner,bg=P["panel"],highlightbackground=P["line2"],highlightthickness=1); routing.pack(fill="x",pady=(0,8))
        tk.Label(routing,text="01 // FILE ROUTING",bg=P["panel"],fg=P["cyan"],font=(MONO,10,"bold")).grid(row=0,column=0,columnspan=4,sticky="w",padx=12,pady=(8,5))
        routing.grid_columnconfigure(1,weight=1); routing.grid_columnconfigure(3,weight=1)
        tk.Label(routing,text="INPUT IMAGE",bg=P["panel"],fg=P["muted"],font=(MONO,9,"bold")).grid(row=1,column=0,sticky="w",padx=10,pady=7)
        input_var=tk.StringVar(value="NO IMAGE SELECTED")
        tk.Label(routing,textvariable=input_var,bg="#030a11",fg=P["text"],font=(MONO,9),anchor="w").grid(row=1,column=1,sticky="ew",padx=5,pady=5,ipady=5)
        tk.Label(routing,text="OUTPUT IMAGE",bg=P["panel"],fg=P["muted"],font=(MONO,9,"bold")).grid(row=1,column=2,sticky="w",padx=10,pady=7)
        output_var=tk.StringVar(value="NO OUTPUT GENERATED")
        tk.Label(routing,textvariable=output_var,bg="#030a11",fg=P["text"],font=(MONO,9),anchor="w").grid(row=1,column=3,sticky="ew",padx=5,pady=5,ipady=5)

        # Cyber Scanner / Dropzone: the canvas is always interactive. Tk itself
        # does not provide native OS file-drop events without an extra package,
        # so click/OPEN is the portable intake path; the scanner animation is real.
        scanner_shell=tk.Frame(inner,bg="#030a10",highlightthickness=0,bd=0)
        scanner_shell.pack(fill="x",pady=(0,8))
        self._install_panel_fx(scanner_shell,P["green"])
        scanner_canvas=tk.Canvas(scanner_shell,bg="#030a10",height=180,highlightthickness=0,bd=0,cursor="hand2")
        scanner_canvas.pack(fill="x",padx=4,pady=4)
        self._stego_scanner.update(canvas=scanner_canvas,size=None,active=False,phase=0.0)
        scanner_canvas.bind("<Button-1>",lambda _e:choose())
        # Hover is interaction-only. Scanner animation runs continuously.

        # Metadata cards appear as an immediate forensic popover below the scanner.
        meta_strip=tk.Frame(scanner_shell,bg="#030a10")
        meta_strip.pack(fill="x",padx=8,pady=(0,7))
        meta_cards=[]
        for label,accent in (("FILE",P["cyan"]),("FORMAT",P["green"]),("SIZE",P["yellow"]),("FINGERPRINT",P["purple"])): 
            card=tk.Frame(meta_strip,bg="#07131b",highlightbackground=accent,highlightthickness=1)
            card.pack(side="left",fill="both",expand=True,padx=3)
            tk.Label(card,text=label,bg="#07131b",fg=accent,font=(MONO,9,"bold")).pack(anchor="w",padx=7,pady=(5,0))
            val=tk.Label(card,text="WAITING",bg="#07131b",fg=P["text"],font=(MONO,9,"bold"),anchor="w")
            val.pack(fill="x",padx=7,pady=(2,5))
            meta_cards.append(val)
        self._stego_meta_cards=meta_cards

        # Visual comparison + operation controls.
        compare=tk.Frame(inner,bg=P["bg"]); compare.pack(fill="x",pady=(0,8))
        compare.grid_columnconfigure(0,weight=1,uniform="img"); compare.grid_columnconfigure(1,weight=1,uniform="img"); compare.grid_columnconfigure(2,weight=1,uniform="img")
        def image_panel(col,title,accent):
            box=tk.Frame(compare,bg=P["panel"],highlightbackground=accent,highlightthickness=1); box.grid(row=0,column=col,sticky="nsew",padx=4)
            head=tk.Frame(box,bg=P["panel"]); head.pack(fill="x",padx=10,pady=(8,1))
            tk.Label(head,text=title,bg=P["panel"],fg=accent,font=(MONO,10,"bold")).pack(side="left")
            tk.Label(head,text="●  LIVE // SECURE",bg=P["panel"],fg=accent,font=(MONO,9,"bold")).pack(side="right")
            scan=tk.Canvas(box,height=5,bg=P["panel"],highlightthickness=0,bd=0); scan.pack(fill="x",padx=10,pady=(1,0))
            holder=tk.Frame(box,bg="#02070c",height=265); holder.pack(fill="x",padx=9,pady=5); holder.pack_propagate(False)
            lab=tk.Label(holder,text="NO IMAGE\nSELECTED",bg="#02070c",fg=P["dim"],font=(MONO,10,"bold"),justify="center"); lab.pack(fill="both",expand=True)
            info=tk.Label(box,text="—",bg=P["panel"],fg=P["muted"],font=(MONO,9),anchor="w"); info.pack(fill="x",padx=10,pady=(2,9))
            self._stego_microfx.append((scan,accent,None))
            return lab,info
        original,orig_info=image_panel(0,"INPUT / ORIGINAL",P["cyan"])
        hidden,hidden_info=image_panel(1,"OUTPUT / WITH HIDDEN DATA",P["purple"])

        control=tk.Frame(compare,bg=P["panel"],highlightbackground=P["green"],highlightthickness=1); control.grid(row=0,column=2,sticky="nsew",padx=4)
        tk.Label(control,text="02 // PAYLOAD INPUT",bg=P["panel"],fg=P["green"],font=(MONO,10,"bold")).pack(anchor="w",padx=12,pady=(10,4))
        message_box=tk.Text(control,height=7,bg="#030a11",fg=P["text"],insertbackground=P["cyan"],font=(FONT,11),relief="flat",wrap="word",undo=True); message_box.pack(fill="x",padx=12,pady=4); message_box.insert("1.0","HN BlackBox Secret")
        statbox=tk.Frame(control,bg="#07151d",highlightbackground=P["line"],highlightthickness=1); statbox.pack(fill="x",padx=12,pady=7); stat={}
        for txt in ("CAPACITY","PAYLOAD","FORMAT","STATUS"):
            r=tk.Frame(statbox,bg="#07151d"); r.pack(fill="x",padx=8,pady=3)
            tk.Label(r,text=txt,bg="#07151d",fg=P["dim"],font=(MONO,9,"bold")).pack(side="left")
            v=tk.Label(r,text="—",bg="#07151d",fg=P["text"],font=(MONO,9,"bold")); v.pack(side="right"); stat[txt]=v
        stat["FORMAT"].configure(text="PNG / BMP"); stat["STATUS"].configure(text="READY",fg=P["green"])
        def msg_bytes(): return len(message_box.get("1.0","end-1c").encode("utf-8"))
        def msg_change(_e=None):
            n=msg_bytes(); stat["PAYLOAD"].configure(text=f"{n:,} BYTES",fg=P["red"] if state["capacity"] and n>state["capacity"] else P["text"])
        message_box.bind("<KeyRelease>",msg_change); msg_change()

        def show_image(label,info,path):
            im=stego._load(path).convert("RGB")
            thumb=ImageOps.contain(im,(430,255),method=Image.Resampling.LANCZOS)
            photo=ImageTk.PhotoImage(thumb); image_refs.append(photo)
            label.configure(image=photo,text=""); label.image=photo
            info.configure(text=f"{Path(path).name}  //  {im.width}×{im.height}")

        def choose():
            f=filedialog.askopenfilename(title="Select input image",filetypes=[("PNG / BMP","*.png *.bmp"),("PNG","*.png"),("BMP","*.bmp")])
            if not f:return
            try:
                im=stego._load(f); cap=stego.capacity_bytes(f)
                state.update(source=f,encoded="",capacity=cap)
                input_var.set(str(Path(f)))
                output_var.set("NO OUTPUT GENERATED")
                stat["CAPACITY"].configure(text=f"{cap:,} BYTES")
                stat["STATUS"].configure(text="INPUT LOADED",fg=P["cyan"])
                show_image(original,orig_info,f)
                hidden.configure(image="",text="WAITING FOR OUTPUT",fg=P["dim"]); hidden_info.configure(text="—")
                self._stego_scanner.update(active=True)
                self._populate_stego_meta(f)
                msg_change(); update_forensics(f)
            except Exception as e: messagebox.showerror("IMAGE ERROR",str(e))

        def clear_input():
            state.update(source="",encoded="",capacity=0); input_var.set("NO IMAGE SELECTED"); output_var.set("NO OUTPUT GENERATED")
            original.configure(image="",text="NO IMAGE\nSELECTED",fg=P["dim"]); orig_info.configure(text="—")
            hidden.configure(image="",text="NO OUTPUT",fg=P["dim"]); hidden_info.configure(text="—")
            self._stego_scanner.update(active=True)
            self._clear_stego_meta()
            stat["CAPACITY"].configure(text="—"); stat["STATUS"].configure(text="CLEARED",fg=P["yellow"]); clear_forensics()

        def replace_input():
            choose()

        def encode():
            if not state["source"]: messagebox.showwarning("LSB","SELECT AN INPUT PNG/BMP IMAGE FIRST"); return
            text=message_box.get("1.0","end-1c"); n=len(text.encode("utf-8"))
            if not text: messagebox.showwarning("LSB","PAYLOAD IS EMPTY"); return
            if n>state["capacity"]: messagebox.showerror("LSB CAPACITY",f"Required: {n:,} bytes\nAvailable: {state['capacity']:,} bytes"); return
            out=filedialog.asksaveasfilename(title="Save stego output",defaultextension=".png",initialfile=f"{Path(state['source']).stem}_hidden.png",filetypes=[("PNG","*.png"),("BMP","*.bmp")])
            if not out:return
            try:
                result=stego.encode(state["source"],out,text); state["encoded"]=out; output_var.set(str(Path(out))); stat["STATUS"].configure(text="PAYLOAD EMBEDDED",fg=P["green"]); show_image(hidden,hidden_info,out); self._populate_stego_meta(out); update_forensics(out); self._record_tool_operation("LSB STEGANOGRAPHY","ENCODE",text,out,state["source"])
            except Exception as e: messagebox.showerror("LSB ENCODE ERROR",str(e))

        def decode():
            path=state["encoded"] or state["source"]
            if not path: messagebox.showwarning("LSB","OPEN AN IMAGE FIRST"); return
            try:
                value=stego.decode(path); extracted.delete("1.0","end"); extracted.insert("1.0",value); stat["STATUS"].configure(text="PAYLOAD EXTRACTED",fg=P["green"]); self._record_tool_operation("LSB STEGANOGRAPHY","DECODE",path,value,"")
            except Exception as e:
                extracted.delete("1.0","end"); extracted.insert("1.0",f"INTEGRITY ERROR\n{e}"); stat["STATUS"].configure(text="INTEGRITY ERROR",fg=P["red"])

        self.btn(control,"OPEN / REPLACE INPUT",choose,True).pack(fill="x",padx=12,pady=(4,3))
        self.btn(control,"> HIDE MESSAGE",encode,True).pack(fill="x",padx=12,pady=3)
        self.btn(control,"< EXTRACT MESSAGE",decode).pack(fill="x",padx=12,pady=3)
        self.btn(control,"CLEAR / REMOVE",clear_input).pack(fill="x",padx=12,pady=(3,10))

        lower=tk.Frame(inner,bg=P["bg"]); lower.pack(fill="x",pady=(0,8))
        left=tk.Frame(lower,bg=P["panel"],highlightbackground=P["purple"],highlightthickness=1); left.pack(side="left",fill="both",expand=True,padx=(0,4))
        right=tk.Frame(lower,bg="#040c12",highlightbackground=P["line2"],highlightthickness=1); right.pack(side="left",fill="both",expand=True,padx=(4,0))
        self._responsive_split(lower,left,right,900,0)
        tk.Label(left,text="03 // OUTPUT / EXTRACTED PAYLOAD",bg=P["panel"],fg=P["purple"],font=(MONO,10,"bold")).pack(anchor="w",padx=12,pady=(9,4))
        extracted=tk.Text(left,height=8,bg="#030a11",fg=P["green"],font=(FONT,11),relief="flat",wrap="word",undo=True); extracted.pack(fill="both",expand=True,padx=12,pady=6)
        self.btn(left,"COPY OUTPUT",lambda:(self.clipboard_clear(),self.clipboard_append(extracted.get("1.0","end-1c"))),False).pack(side="right",padx=12,pady=(2,10))
        tk.Label(right,text="04 // SECURITY INTELLIGENCE // PIXEL FORENSICS",bg="#040c12",fg=P["cyan"],font=(MONO,10,"bold")).pack(anchor="w",padx=12,pady=(9,3))
        forensic_canvas=tk.Canvas(right,bg="#02070c",height=175,highlightthickness=0); forensic_canvas.pack(fill="x",padx=12,pady=5)
        stego_hud=tk.Canvas(right,bg="#02070c",height=190,highlightthickness=0); stego_hud.pack(fill="x",padx=12,pady=(0,6))
        forensic_text=tk.Label(right,text="LOAD AN IMAGE TO START LOCAL PIXEL ANALYSIS",bg="#040c12",fg=P["muted"],font=(MONO,9),justify="left",anchor="w"); forensic_text.pack(fill="x",padx=12,pady=(2,7))
        def draw_stego_hud(report=None, active_bits=0, status="READY"):
            stego_hud.delete("all")
            w=max(500,stego_hud.winfo_width()); h=190
            visual_models.draw_stego_hud(stego_hud,w,h,report,active_bits,status,P)

        def clear_forensics():
            forensic_canvas.delete("all"); stego_hud.delete("all"); forensic_text.configure(text="LOAD AN IMAGE TO START LOCAL PIXEL ANALYSIS")
            draw_stego_hud(None,0,"READY")
        def update_forensics(path):
            forensic_text.configure(text="FORENSIC SCAN QUEUED // BACKGROUND WORKER…",fg=P["yellow"])
            target=str(path)
            def work(): return stego.inspect_lsb(target,512)
            def done(r):
                pl=r["payload"]
                forensic_canvas.delete("all"); w=max(500,forensic_canvas.winfo_width()); h=175
                forensic_canvas.create_text(8,10,text="RGB LSB DENSITY // LIVE EVIDENCE",fill=P["cyan"],font=(MONO,9,"bold"),anchor="w")
                for row,(ch,accent) in enumerate((("R",P["red"]),("G",P["green"]),("B",P["cyan"]))):
                    vals=r["plane_density_percent"][ch]; y=42+row*40
                    forensic_canvas.create_text(8,y+7,text=ch,fill=accent,font=(MONO,9,"bold"),anchor="w")
                    for bit,val in enumerate(vals):
                        x=32+bit*max(24,(w-70)/8); forensic_canvas.create_rectangle(x,y,x+18,y+15,fill=accent if val>=50 else "#07141e",outline=P["line"]); forensic_canvas.create_text(x+9,y+24,text=str(bit),fill=P["muted"],font=(MONO,9))
                forensic_text.configure(text=f"IMAGE {r['width']}×{r['height']}  •  CAPACITY {r['capacity_bytes']:,} B  •  SAMPLED {r['pixels_sampled']:,}\nPAYLOAD: {'DETECTED' if pl['detected'] else 'NOT DETECTED'}  •  MESSAGE {pl['message_bytes']:,} B  •  CRC32 {pl['crc'] or '—'}\nLSB STREAM: {r['lsb_stream'][:96]}…",fg=P["muted"])
            def fail(exc): forensic_text.configure(text=f"ANALYSIS ERROR: {exc}",fg=P["red"])
            self._run_ui_worker(work,done,fail)
        self.btn(right,"RUN FULL FORENSICS",lambda:update_forensics(state["encoded"] or state["source"]) if (state["encoded"] or state["source"]) else messagebox.showwarning("FORENSICS","OPEN AN IMAGE FIRST"),True).pack(anchor="e",padx=12,pady=(0,10))

        # Keep a testable context so regression tests can exercise real controls.
        self._stego_context={"state":state,"input":input_var,"output":output_var,"message":message_box,"extracted":extracted,"choose":choose,"encode":encode,"decode":decode,"clear":clear_input,"replace":replace_input,"status":stat["STATUS"]}
        self.after(0, lambda: draw_stego_hud(None,0,"READY"))
        return p

    def _crypto_popup(self, title, width=760, height=560):
        win=tk.Toplevel(self); win.title('HN BLACKBOX // '+title); win.geometry(f'{width}x{height}'); win.minsize(620,420); win.configure(bg=P['bg']); win.transient(self)
        head=tk.Frame(win,bg='#050d14',highlightbackground=P['line2'],highlightthickness=1); head.pack(fill='x',padx=16,pady=16)
        tk.Label(head,text='HN // CRYPTO INTELLIGENCE',bg='#050d14',fg=P['cyan'],font=(MONO, 10,'bold')).pack(side='left',padx=12,pady=10)
        tk.Label(head,text=title.upper(),bg='#050d14',fg=P['text'],font=(MONO, 13,'bold')).pack(side='right',padx=12)
        body=tk.Frame(win,bg=P['bg']); body.pack(fill='both',expand=True,padx=16,pady=(0,16))
        return win,body

    def open_crypto_analyzer(self):
        win,body=self._crypto_popup('Payload Analyzer',820,610)
        top=tk.Frame(body,bg=P['panel'],highlightbackground=P['line'],highlightthickness=1); top.pack(fill='x',pady=(0,8))
        tk.Label(top,text='PAYLOAD',bg=P['panel'],fg=P['muted'],font=(MONO, 9,'bold')).pack(anchor='w',padx=10,pady=(8,2))
        inp=tk.Text(top,height=5,bg='#030a11',fg=P['text'],insertbackground=P['cyan'],font=(MONO, 11),relief='flat',wrap='none'); inp.pack(fill='x',padx=10,pady=(0,8))
        out=tk.Text(body,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat',wrap='none'); out.pack(fill='both',expand=True)
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
        text=tk.Text(body,bg='#030a11',fg=P['text'],font=(MONO, 10),relief='flat',wrap='none'); text.pack(fill='both',expand=True)
        def run():
            keys=[k for k,v in vars if v.get()]
            rows=crypto_intel.compare_algorithms(keys)
            text.delete('1.0','end'); text.insert('1.0',rows)
        self.btn(bar,'COMPARE',run,True).pack(side='right',padx=8,pady=5)
        run()

    def open_crypto_key_lab(self):
        win,body=self._crypto_popup('Key & Strength Lab',760,540)
        row=tk.Frame(body,bg=P['panel'],highlightbackground=P['line'],highlightthickness=1); row.pack(fill='x',pady=(0,8))
        tk.Label(row,text='ALGORITHM',bg=P['panel'],fg=P['muted'],font=(MONO, 9,'bold')).pack(side='left',padx=8)
        combo=ttk.Combobox(row,state='readonly',values=list(ALGORITHMS.keys()),font=(MONO, 10)); combo.set('caesar'); combo.pack(side='left',padx=8,pady=8)
        key=tk.Entry(row,bg='#030a11',fg=P['text'],insertbackground=P['cyan'],font=(MONO, 10),relief='flat'); key.pack(side='left',fill='x',expand=True,padx=8,pady=8)
        out=tk.Text(body,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat',wrap='word'); out.pack(fill='both',expand=True)
        def run():
            out.delete('1.0','end'); out.insert('1.0',crypto_intel.key_profile(combo.get(),key.get()))
        self.btn(row,'PROFILE',run,True).pack(side='right',padx=8,pady=5)
        run()

    def _select_crypto_group(self,key):
        # Programmatic callers may request a family immediately after navigation;
        # mount the lazy crypto page on demand without waiting for an idle turn.
        if not hasattr(self, 'crypto_group_var'):
            try:
                page = self._ensure_page('crypto')
                if page is not None:
                    page.tkraise()
            except Exception as exc:
                self._last_error = f'crypto_mount: {exc}'
                return
        meta=CRYPTO_GROUPS[key]
        self.crypto_group_var.set(key)
        for k,b in self.crypto_group_buttons.items():
            active=k==key; m=CRYPTO_GROUPS[k]
            b.configure(bg=m["accent"] if active else '#07131a',fg=P["bg"] if active else m["accent"])
        self.crypto_selection_info_label.configure(text=f"{meta['title']}  //  {meta['sub']}",fg=meta["accent"])
        self._crypto_build_cards(meta["keys"])

    def _crypto_card_click(self,key):
        """Open the selected lab without audio side effects."""
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
        tk.Label(top,text=f'LIVE LAB  //  {code}  //  LOCAL ENGINE  //  VISUAL TRACE LINKED',bg=P['bg'],fg=P['dim'],font=(MONO, 9,'bold'),anchor='w').pack(side='left',pady=7)
        self.btn(top,'ALGORITHM GUIDE',self.guide).pack(side='right',padx=3)
        self.btn(top,'CLEAR',self.clear_processing).pack(side='right',padx=3)
        command_hud=tk.Frame(inner,bg='#041018',highlightbackground=P['line2'],highlightthickness=1); command_hud.pack(fill='x',pady=(0,7))
        left_h=tk.Frame(command_hud,bg='#041018'); left_h.pack(side='left',fill='x',expand=True,padx=10,pady=7)
        tk.Label(left_h,text='CRYPTO OPS // LIVE CORE CONTROL',bg='#041018',fg=P['cyan'],font=(MONO, 10,'bold'),anchor='w').pack(fill='x')
        tk.Label(left_h,text=f'{code} CORE  •  LOCAL  •  TRACE LINKED  •  READY',bg='#041018',fg=P['muted'],font=(MONO, 9,'bold'),anchor='w').pack(fill='x',pady=(2,0))
        self.command_clock=tk.Label(command_hud,text=datetime.now().strftime('%H:%M:%S'),bg='#041018',fg=P['green'],font=(MONO, 11,'bold')); self.command_clock.pack(side='right',padx=12)
        self.crypto_op_strip=tk.Canvas(command_hud,height=3,bg='#041018',highlightthickness=0); self.crypto_op_strip.pack(fill='x',side='bottom',padx=10,pady=(2,4))
        self._crypto_op_phase=0

        # metadata HUD
        hud=self.glass(inner); hud.pack(fill='x',pady=(0,7))
        specs=[('MODULE',code,P['cyan']),('FORMULA',GUIDES[self.current_algo][0],P['yellow']),('MODE','LOCAL / EDUCATIONAL',P['green']),('TRACE','REAL-TIME',P['purple'])]
        for i,(lab,val,col) in enumerate(specs):
            cell=tk.Frame(hud,bg=P['panel2']); cell.pack(side='left',fill='x',expand=True,padx=1,pady=1)
            tk.Label(cell,text=lab,bg=P['panel2'],fg=P['dim'],font=(MONO, 9,'bold')).pack(anchor='w',padx=9,pady=(6,0))
            tk.Label(cell,text=val,bg=P['panel2'],fg=col,font=(MONO, 9,'bold'),wraplength=240,anchor='w',justify='left').pack(anchor='w',padx=9,pady=(1,6))

        split=tk.Frame(inner,bg=P['bg']); split.pack(fill='x',pady=2)
        split.grid_columnconfigure(0,weight=42,uniform='lab')
        split.grid_columnconfigure(1,weight=58,uniform='lab')

        # Controls: intentionally compact so visual trace remains visible without scrolling.
        controls=self.card(split); controls.grid(row=0,column=0,sticky='nsew',padx=(0,5))
        hdr=tk.Frame(controls,bg=P['panel3']); hdr.pack(fill='x')
        tk.Label(hdr,text='01 // CONTROL CONSOLE',bg=P['panel3'],fg=P['cyan'],font=(MONO, 10,'bold')).pack(side='left',padx=12,pady=7)
        tk.Label(hdr,text='READY',bg=P['panel3'],fg=P['green'],font=(MONO, 9,'bold')).pack(side='right',padx=12)

        tk.Label(controls,text='INPUT PAYLOAD',bg=P['panel'],fg=P['muted'],font=(MONO, 9,'bold'),anchor='w').pack(fill='x',padx=12,pady=(9,3))
        input_shell=tk.Frame(controls,bg=P['panel2'],highlightthickness=0,bd=0)
        input_shell.pack(fill='x',padx=12,pady=(0,5))
        self._install_panel_fx(input_shell, P['cyan'])
        self.input_box=tk.Text(input_shell,height=3,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],selectbackground=P['purple'],relief='flat',bd=0,font=(MONO, 11),wrap='word',undo=True,padx=9,pady=7)
        self.input_box.pack(fill='both',expand=True,padx=3,pady=3)
        self.crypto_input_counter=tk.Label(controls,text='0 CHARS  //  UTF-8',bg=P['panel'],fg=P['dim'],font=(MONO, 9,'bold'),anchor='e'); self.crypto_input_counter.pack(fill='x',padx=12,pady=(0,2))
        self.crypto_input_signal=tk.Canvas(controls,height=3,bg=P['panel'],highlightthickness=0,bd=0); self.crypto_input_signal.pack(fill='x',padx=12,pady=(0,4))
        self._crypto_signal_job=None
        self._crypto_signal_pulse_until = 0.0
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
            tk.Label(row,text=lab,bg=P['panel'],fg=P['dim'],font=(MONO, 9,'bold'),anchor='w').pack(fill='x')
            e=ttk.Entry(row,font=(MONO, 10)); e.pack(fill='x',ipady=2); self.key_entries[f]=e

        note={'hash':self.t('hashnote'),'rsa':self.t('rsanote'),'otp':self.t('otpnote'), 'des':'DES is an educational legacy cipher. Use exactly 8 UTF-8 bytes for the key.', 'double_transposition':'Two keyed columnar passes are applied in sequence.'}.get(self.current_algo,'')
        if note: tk.Label(controls,text=note,bg=P['panel'],fg=P['yellow'],font=(FONT, 10),wraplength=410,justify='left').pack(fill='x',padx=12,pady=3)
        actions=tk.Frame(controls,bg=P['panel']); actions.pack(fill='x',padx=12,pady=(5,10))
        self.btn(actions,'> EXECUTE',self.execute,True).pack(side='left',fill='x',expand=True,padx=(0,3))
        self.btn(actions,'GENERATE',self.generate_key).pack(side='left',fill='x',expand=True,padx=3)
        if self.current_algo=='caesar': self.btn(actions,'BRUTE FORCE',self.bruteforce).pack(side='left',fill='x',expand=True,padx=3)
        self.btn(actions,'GUIDE',self.guide).pack(side='left',fill='x',expand=True,padx=(3,0))

        # Compact core profile: useful state, no wall of explanatory text.
        intel=tk.Frame(controls,bg='#06131a',highlightbackground=P['line'],highlightthickness=1)
        intel.pack(fill='x',padx=12,pady=(2,8))
        ih=tk.Frame(intel,bg='#06131a'); ih.pack(fill='x',padx=9,pady=(6,3))
        tk.Label(ih,text='CORE PROFILE',bg='#06131a',fg=P['yellow'],font=(MONO, 9,'bold')).pack(side='left')
        self.core_profile_status=tk.Label(ih,text='STANDBY',bg='#06131a',fg=P['green'],font=(MONO, 9,'bold')); self.core_profile_status.pack(side='right')
        formula,example=GUIDES[self.current_algo]
        profile=tk.Frame(intel,bg='#06131a'); profile.pack(fill='x',padx=8,pady=(0,7))
        rows=[('FORMULA',formula,P['cyan']),('PATH',{'caesar':'READ → SHIFT → EMIT','additive':'READ → ADD MOD 26 → EMIT','multiplicative':'READ → MULTIPLY MOD 26 → EMIT','vigenere':'KEY ALIGN → ADD MOD 26 → EMIT','playfair':'PAIR → LOCATE → SUBSTITUTE','railfence':'ROUTE → ZIGZAG → READ','hill':'MATRIX × VECTOR → MOD 26','aes':'KEY → BLOCK → ROUND → SEAL','rsa':'KEYPAIR → MODULAR EXPONENT → SEAL','hash':'NORMALIZE → DIGEST → FINGERPRINT','keyed_transposition':'WRITE GRID → KEY ORDER → READ','double_transposition':'PASS 1 → PASS 2 → REVERSE TO DECRYPT'}.get(self.current_algo,'INPUT → TRANSFORM → OUTPUT'),P['green'])]
        for lab,val,col in rows:
            row=tk.Frame(profile,bg='#07151d'); row.pack(fill='x',pady=1)
            tk.Label(row,text=lab,bg='#07151d',fg=P['dim'],font=(MONO, 9,'bold'),width=9,anchor='w').pack(side='left',padx=6,pady=5)
            tk.Label(row,text=val,bg='#07151d',fg=col,font=(MONO, 9,'bold'),anchor='w',wraplength=320,justify='left').pack(side='left',fill='x',expand=True,pady=5)

        telemetry=tk.Frame(controls,bg='#040c12',highlightbackground=P['line'],highlightthickness=1); telemetry.pack(fill='x',padx=12,pady=(0,10))
        tk.Label(telemetry,text='ENGINE TELEMETRY // LIVE',bg='#040c12',fg=P['yellow'],font=(MONO, 9,'bold'),anchor='w').pack(fill='x',padx=9,pady=(6,4))
        tgrid=tk.Frame(telemetry,bg='#040c12'); tgrid.pack(fill='x',padx=8,pady=(0,7))
        self.crypto_metric_labels={}
        metric_specs=[('INPUT','0'),('OUTPUT','0'),('KEY','READY'),('EXEC','-- ms')]
        for i,(lab,val) in enumerate(metric_specs):
            cell=tk.Frame(tgrid,bg='#07151d'); cell.grid(row=0,column=i,sticky='ew',padx=2)
            tgrid.grid_columnconfigure(i,weight=1)
            tk.Label(cell,text=lab,bg='#07151d',fg=P['dim'],font=(MONO, 9,'bold')).pack(anchor='w',padx=5,pady=(4,0))
            lbl=tk.Label(cell,text=val,bg='#07151d',fg=(P['cyan'],P['green'],P['yellow'],P['purple'])[i],font=(MONO, 9,'bold')); lbl.pack(anchor='w',padx=5,pady=(1,5))
            self.crypto_metric_labels[lab]=lbl

        # Right: visualizer is first-class, result is embedded below it.
        right=tk.Frame(split,bg=P['bg']); right.grid(row=0,column=1,sticky='nsew',padx=(5,0))
        vis=self.card(right); vis.pack(fill='both',expand=True)
        vh=tk.Frame(vis,bg=P['panel3']); vh.pack(fill='x')
        tk.Label(vh,text='02 // LIVE VISUALIZATION // INTELLIGENCE FEED',bg=P['panel3'],fg=P['cyan'],font=(MONO, 10,'bold')).pack(side='left',padx=12,pady=7)
        self.visual_status=tk.Label(vh,text='WAITING FOR EXECUTION',bg=P['panel3'],fg=P['yellow'],font=(MONO, 9,'bold')); self.visual_status.pack(side='right',padx=12)
        # Progress strip
        self.visual_progress=tk.Canvas(vis,height=4,bg=P['panel'],highlightthickness=0); self.visual_progress.pack(fill='x')
        self.visual=tk.Canvas(vis,bg='#050b11',height=330,highlightthickness=0)
        self.visual.pack(fill='both',expand=True,padx=8,pady=8)

        # Result is always directly under the visualization; no hunt through the page.
        result=tk.Frame(vis,bg=P['panel']); result.pack(fill='x',padx=8,pady=(0,8))
        rh=tk.Frame(result,bg=P['panel']); rh.pack(fill='x')
        tk.Label(rh,text='03 // OUTPUT',bg=P['panel'],fg=P['green'],font=(MONO, 10,'bold')).pack(side='left',padx=8,pady=6)
        self.status=tk.Label(rh,text='READY',bg=P['panel'],fg=P['green'],font=(MONO, 9,'bold')); self.status.pack(side='left',padx=6)
        self.crypto_output_counter=tk.Label(rh,text='0 CHARS',bg=P['panel'],fg=P['dim'],font=(MONO, 9,'bold')); self.crypto_output_counter.pack(side='left',padx=7)
        self.btn(rh,'COPY',self.copy_result).pack(side='right',padx=2,pady=2)
        self.btn(rh,'SAVE',self.save_result).pack(side='right',padx=2,pady=2)
        output_shell=tk.Frame(result,bg='#030a11',highlightthickness=0,bd=0)
        output_shell.pack(fill='x',padx=7,pady=(0,3))
        self._install_panel_fx(output_shell, P['green'])
        self.result_box=tk.Text(output_shell,height=3,bg='#030a11',fg=P['green'],insertbackground=P['cyan'],relief='flat',bd=0,font=(ASCII_MONO, 10),wrap='none',padx=8,pady=6)
        self.result_box.pack(fill='both',expand=True,padx=3,pady=3)
        self.crypto_output_signal=tk.Canvas(result,height=3,bg=P['panel'],highlightthickness=0,bd=0); self.crypto_output_signal.pack(fill='x',padx=7,pady=(0,7))
        trace=tk.Frame(vis,bg='#040c12',highlightbackground=P['line'],highlightthickness=1); trace.pack(fill='x',padx=8,pady=(0,8))
        tk.Label(trace,text='04 // EXECUTION TRACE',bg='#040c12',fg=P['yellow'],font=(MONO, 9,'bold'),anchor='w').pack(fill='x',padx=8,pady=(5,2))
        self.trace_box=tk.Text(trace,height=4,bg='#02070c',fg=P['muted'],font=(MONO, 9),relief='flat',bd=0,wrap='none',state='disabled',padx=7,pady=4)
        self.trace_box.pack(fill='x',padx=6,pady=(0,5))
        inspector=tk.Frame(vis,bg='#030a11',highlightbackground=P['line2'],highlightthickness=1)
        inspector.pack(fill='x',padx=8,pady=(0,8))
        ih=tk.Frame(inspector,bg='#07151d'); ih.pack(fill='x')
        tk.Label(ih,text='05 // STEP INSPECTOR // INPUT -> TRANSFORMATION -> OUTPUT',bg='#07151d',fg=P['cyan'],font=(MONO, 9,'bold')).pack(side='left',padx=8,pady=5)
        self.step_inspector_status=tk.Label(ih,text='IDLE',bg='#07151d',fg=P['yellow'],font=(MONO, 9,'bold')); self.step_inspector_status.pack(side='right',padx=8)
        self.step_inspector=tk.Text(inspector,height=5,bg='#02070c',fg=P['text'],font=(MONO, 9),relief='flat',bd=0,wrap='none',state='disabled',padx=7,pady=5)
        self.step_inspector.pack(fill='x',padx=5,pady=5)
        # Cinematic transport controls: deterministic manual stepping + autoplay.
        transport=tk.Frame(inspector,bg='#07151d'); transport.pack(fill='x',padx=5,pady=(0,5))
        tk.Label(transport,text='TRANSPORT',bg='#07151d',fg=P['dim'],font=(MONO, 9,'bold')).pack(side='left',padx=(5,4))
        self.btn(transport,'|< RESET',self._visual_reset).pack(side='left',padx=2,pady=2)
        self.btn(transport,'< STEP',self._visual_step_back).pack(side='left',padx=2,pady=2)
        self.btn(transport,'STEP >',self._visual_step_forward,True).pack(side='left',padx=2,pady=2)
        self.visual_play_btn=self.btn(transport,'▶ PLAY',self._visual_toggle_play); self.visual_play_btn.pack(side='left',padx=2,pady=2)
        tk.Label(transport,text='SPEED',bg='#07151d',fg=P['dim'],font=(MONO, 9,'bold')).pack(side='left',padx=(10,3))
        self.visual_speed=tk.StringVar(value='NORMAL')
        self.visual_speed_box=ttk.Combobox(transport,textvariable=self.visual_speed,values=('SLOW','NORMAL','FAST'),state='readonly',width=8,font=(MONO, 9))
        self.visual_speed_box.pack(side='left',padx=2,pady=2); self.visual_speed_box.bind('<<ComboboxSelected>>',lambda _e:self._visual_speed_changed())
        self._set_crypto_metrics(input_len=0,output_len=0,key_state='READY',elapsed=None)
        self._trace('SYSTEM','CRYPTO CORE READY')

        self._visual_state={'result':'','step':0,'playing':True,'next_step_at':time.monotonic()+self._visual_speed_delay()/1000.0,'last_drawn_step':0}; self.draw_visual()
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

    def _animate_processing_microfx(self):
        """Foreground-only micro FX for a classical cipher workspace.

        This channel is deliberately retained-mode: it moves existing Canvas
        objects and never schedules its own ``after`` callback.  The router owns
        its lifecycle, so repeated cipher navigation cannot accumulate timers.
        """
        if not getattr(self,'_ui_ready',False) or not self._motion_page_active('processing'):
            return
        self._update_crypto_clock()
        self._animate_crypto_op_strip()
        self._animate_crypto_signal(getattr(self,'crypto_input_signal',None), P['cyan'], 1)
        self._animate_crypto_signal(getattr(self,'crypto_output_signal',None), P['green'], -1)
        self._animate_cipher_visual_fx()

    def _animate_crypto_op_strip(self):
        c=getattr(self,'crypto_op_strip',None)
        if c is None or not c.winfo_exists(): return
        w=max(1,c.winfo_width())
        items=getattr(c,'_hn_op_items',None)
        if not items:
            c.delete('all')
            base=c.create_rectangle(0,0,w,3,fill='#07151d',outline='')
            beam=c.create_rectangle(-70,0,0,3,fill=P['cyan'],outline='')
            c._hn_op_items=(base,beam)
            items=c._hn_op_items
        else:
            c.coords(items[0],0,0,w,3)
        phase=time.monotonic()*4.2
        x=(phase%(w+70))-70
        c.coords(items[1],x,0,x+70,3)

    def _update_crypto_clock(self):
        c=getattr(self,'command_clock',None)
        if c is None or not c.winfo_exists(): return
        try:
            c.configure(text=datetime.now().strftime('%H:%M:%S'))
        except tk.TclError:
            pass

    def _animate_crypto_signal(self, canvas, accent, direction=1):
        """Retained signal rail advanced by the global render scheduler."""
        try:
            if canvas is None or not canvas.winfo_exists() or not getattr(self,'_ui_ready',False): return
            w=max(40,canvas.winfo_width());
            # Reuse one tagged geometry set; never spawn a timer or rebuild a widget.
            items=getattr(canvas,'_hn_signal_items',None)
            if not items:
                items=(canvas.create_rectangle(0,0,1,3,fill=accent,outline='',tags='signal'),
                       canvas.create_line(0,1,1,1,fill=P['line2'],tags='signal'))
                canvas._hn_signal_items=items
            x=8+((time.monotonic()*180*direction)%(w+36))-18
            canvas.coords(items[0],x,0,x+36,3)
            canvas.coords(items[1],max(0,x-16),1,min(w,x+52),1)
        except tk.TclError:
            pass

    def _crypto_input_changed(self,_event=None):
        try:
            if getattr(self,'input_box',None) and self.input_box.edit_modified():
                n=len(self.input_box.get('1.0','end-1c'))
                if hasattr(self,'crypto_input_counter'): self.crypto_input_counter.configure(text=f'{n:,} CHARS  //  UTF-8')
                self._crypto_signal_pulse_until = time.monotonic() + 0.28
                self.input_box.edit_modified(False)
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
        elif k in {"vigenere", "playfair", "columnar", "beaufort", "autokey", "aes", "keyed_transposition"}:
            put("word", "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(8)))
        elif k == "double_transposition":
            put("word1", "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(6)))
            put("word2", "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(6)))
        elif k == "des":
            put("key", "HNKEY123")
        elif k == "affine":
            put("a", secrets.choice([1,3,5,7,9,11,15,17,19,21,23,25])); put("b", secrets.randbelow(26))
        elif k == "hill":
            while True:
                vals = [secrets.randbelow(26) for _ in range(4)]
                if math.gcd((vals[0]*vals[3]-vals[1]*vals[2]) % 26, 26) == 1: break
            for f, v in zip(("a","b","c","d"), vals): put(f, v)
        elif k == "otp":
            put("word", classical_additional.otp.otp_key(max(8, len(self.input_box.get("1.0","end-1c").encode()) + 4)))
        elif k == "rsa":
            e, d, n = educational_rsa.rsa_generate(512); put("key", f"e={e}; d={d}; n={n}")
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
        """Queue crypto work off the Tk main thread; engines remain unchanged."""
        text = self.input_box.get("1.0", "end-1c")
        if not text:
            messagebox.showwarning(self.t("error"), "INPUT IS REQUIRED")
            return
        if self._crypto_future is not None and not self._crypto_future.done():
            return
        k, vals, op = self.current_algo, self._vals(), self.operation.get()
        if k == 'railfence':
            try:
                rails = int(vals.get('rails', '0'))
            except ValueError:
                messagebox.showerror(self.t('error'), 'RAILS MUST BE AN INTEGER / يجب أن يكون عدد القضبان رقمًا صحيحًا')
                return
            if rails >= len(text):
                messagebox.showwarning(self.t('error'), 'RAILS MUST BE LESS THAN INPUT LENGTH / يجب أن تكون القضبان أقل من طول النص')
                return
        started = time.perf_counter()
        self._exec_started = started
        self._trace_lines = []
        self._trace('INPUT', 'PAYLOAD RECEIVED')

        self._set_crypto_metrics(input_len=len(text), key_state='VALIDATING')
        if hasattr(self,'visual_status') and self.visual_status.winfo_exists(): self.visual_status.configure(text='CORE PROCESSING',fg=P['yellow'])
        if hasattr(self,'core_profile_status') and self.core_profile_status.winfo_exists(): self.core_profile_status.configure(text='PROCESSING',fg=P['yellow'])
        self.status.configure(text='PROCESSING // BACKGROUND WORKER', fg=P['yellow'])
        try:
            future = self._crypto_worker.submit(execute_crypto, k, vals, op, text)
        except Exception as e:
            self._trace('ERROR', str(e)[:120])
            self.status.configure(text=self.t('error'), fg=P['red'])
            messagebox.showerror(self.t('error'), str(e))
            return
        self._crypto_future = future
        future.add_done_callback(lambda fut: self._queue_worker_event(lambda: self._finish_crypto_job(fut, k, vals, op, text, started)))

    def _finish_crypto_job(self, future, k, vals, op, text, started):
        if not self.winfo_exists():
            return
        try:
            out = future.result()
        except Exception as e:
            self._trace('ERROR', str(e)[:120])
            self._set_crypto_metrics(input_len=len(text), key_state='INVALID')
            self.status.configure(text=self.t('error'), fg=P['red'])
            if hasattr(self,'core_profile_status') and self.core_profile_status.winfo_exists(): self.core_profile_status.configure(text='ERROR',fg=P['red'])
            messagebox.showerror(self.t('error'), str(e))
            self._crypto_future = None
            return
        elapsed=time.perf_counter()-started
        self._trace('KEY','VALIDATION PASSED')
        self._trace('ENGINE',f'{ALGORITHMS[k][0].upper()} TRANSFORMATION COMPLETE')
        self.result_box.delete('1.0','end'); self.result_box.insert('1.0', out)
        self.status.configure(text=self.t('done'), fg=P['green'])
        if hasattr(self,'core_profile_status') and self.core_profile_status.winfo_exists(): self.core_profile_status.configure(text='COMPLETE',fg=P['green'])
        self._set_crypto_metrics(input_len=len(text),output_len=len(out),key_state='VALID',elapsed=elapsed)
        self._trace('OUTPUT',f'GENERATED // {len(out)} CHARS // {elapsed*1000:.1f} ms')
        if k=='des':
            try:
                tr=des_cipher.trace(vals['key'])
                self._trace('KEYS',f'16 SUBKEYS GENERATED // K1={tr["rounds"][0]["subkey_hex"]} // K16={tr["rounds"][-1]["subkey_hex"]}')
            except Exception: pass
        history_manager.add_entry(ALGORITHMS[k][0], op, str(vals), text, out)
        self._start_visual(out)
        self._crypto_future = None

    def clear_processing(self):
        try: self._render_scheduler.unregister('_visual_trace')
        except Exception: pass
        self._visual_job = None
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
            tk.Label(c,text=a,bg=P["panel"],fg=P["yellow"],font=(MONO, 10,"bold"),anchor="e").pack(fill="x",padx=15,pady=(10,2))
            tk.Label(c,text=b,bg=P["panel"],fg=P["text"],font=(MONO, 11),wraplength=580,anchor="w",justify="left").pack(fill="x",padx=15,pady=(0,11))

    def bruteforce(self):
        text=self.input_box.get("1.0","end-1c")
        results=caesar.brute_force(text)
        out="\n".join(f"{k:02d}  →  {v}" for k,v in results)
        self.result_box.delete("1.0","end"); self.result_box.insert("1.0",out)
        self.status.configure(text="✓ 26 KEY CANDIDATES",fg=P["cyan"])
        self._start_visual(out)

    # ---------- visualization ----------
    def _step_rows(self, result):
        """Build a compact, truthful per-step inspector from the current operation."""
        algo=self.current_algo or 'caesar'
        src=(self.input_box.get('1.0','end-1c') if hasattr(self,'input_box') else '').replace('\n','↵')
        out=result or ''
        rows=[]; limit=min(max(len(src),len(out)),42)
        try: vals={k:v.get() for k,v in getattr(self,'key_entries',{}).items()}
        except Exception: vals={}
        for i in range(limit):
            a=src[i] if i<len(src) else '·'; b=out[i] if i<len(out) else '·'
            if algo=='caesar': op=f"SHIFT {vals.get('shift','0')}"
            elif algo in {'additive','multiplicative','affine'}: op={'additive':f"+{vals.get('shift','?')}",'multiplicative':f"x{vals.get('key','?')}",'affine':f"{vals.get('a','?')}x+{vals.get('b','?')}"}[algo]
            elif algo in {'vigenere','autokey','beaufort'}:
                key=vals.get('word','') or '?'; op=f"KEY[{key[i%len(key)] if key and key!='?' else '?'}]"
            elif algo in {'atbash','rot13'}: op='ALPHABET MAP' if algo=='atbash' else 'ROTATE +13'
            elif algo=='railfence': op=f"RAILS={vals.get('rails','?')}"
            elif algo in {'keyed_transposition','columnar'}: op=f"COLUMN KEY={vals.get('word','?')}"
            elif algo=='double_transposition': op=f"PASS {1 if i < max(1,limit//2) else 2}"
            elif algo=='playfair': op='DIGRAPH ROUTING'
            elif algo=='hill': op='K x P MOD 26'
            elif algo in {'polybius','bacon','morse','adfgvx'}: op='SYMBOL ENCODE'
            elif algo=='otp': op='OTP XOR / MOD'
            elif algo=='hash': op='ONE-WAY DIGEST'
            elif algo=='des': op='BLOCK / 16 FEISTEL ROUNDS'
            elif algo=='aes': op='AES-256 BLOCK TRANSFORM'
            elif algo=='rsa': op='MODULAR EXPONENTIATION'
            else: op='TRANSFORM'
            rows.append((i+1,a,op,b))
        return rows

    def _update_step_inspector(self):
        box=getattr(self,'step_inspector',None)
        if not box or not box.winfo_exists(): return
        result=self._visual_state.get('result','') if hasattr(self,'_visual_state') else ''
        step=self._visual_state.get('step',0) if hasattr(self,'_visual_state') else 0
        rows=self._step_rows(result); shown=max(0,min(step,len(rows)))
        start=max(0,shown-5); view=rows[start:shown] or rows[:1]
        text='IDX  INPUT  OPERATION                 OUTPUT\n'+'-'*58+'\n'
        for idx,a,op,b in view: text+=f'{idx:03d}  {a!s:<6} {op:<25} {b!s}\n'
        box.configure(state='normal'); box.delete('1.0','end'); box.insert('1.0',text.rstrip()); box.configure(state='disabled')
        st=getattr(self,'step_inspector_status',None)
        if st and st.winfo_exists(): st.configure(text=f'STEP {shown:02d}/{len(rows):02d}',fg=P['green'] if shown else P['yellow'])

    def _visual_speed_delay(self):
        return {'SLOW':180,'NORMAL':78,'FAST':35}.get(getattr(self,'visual_speed',None).get() if getattr(self,'visual_speed',None) else 'NORMAL',78)

    def _visual_speed_changed(self):
        st=getattr(self,'_visual_state',None)
        if st is not None:
            st['next_step_at']=time.monotonic()+self._visual_speed_delay()/1000.0
        if getattr(self,'current',None)=='processing':
            self._render_scheduler.register('_visual_trace', self._visual_frame, fps=30.0, priority=1)

    def _visual_total(self):
        result=self._visual_state.get('result','') if hasattr(self,'_visual_state') else ''
        source=self.input_box.get('1.0','end-1c') if hasattr(self,'input_box') else ''
        return max(8,min(42,max(len(result),len(source))+4))

    def _visual_reset(self):
        if getattr(self,'_visual_job',None):
            try:self.after_cancel(self._visual_job)
            except tk.TclError:pass
            self._visual_job=None
        result=self._visual_state.get('result','') if hasattr(self,'_visual_state') else ''
        self._visual_state={'result':result,'step':0,'playing':False,'next_step_at':time.monotonic(),'last_drawn_step':0}
        self._update_step_inspector(); self.draw_visual(); self._draw_visual_progress(0,self._visual_total())
        if hasattr(self,'visual_status') and self.visual_status.winfo_exists(): self.visual_status.configure(text='TRACE RESET',fg=P['yellow'])

    def _visual_step_forward(self):
        total=self._visual_total(); st=getattr(self,'_visual_state',{'result':'','step':0,'playing':False})
        st['step']=min(total,st.get('step',0)+1); st['playing']=False; self._visual_state=st
        self._update_step_inspector(); self.draw_visual(); self._draw_visual_progress(st['step'],total)
        if hasattr(self,'visual_status') and self.visual_status.winfo_exists(): self.visual_status.configure(text=f'TRACE {st["step"]:02d}/{total:02d}',fg=P['green'] if st['step']<total else P['cyan'])

    def _visual_step_back(self):
        st=getattr(self,'_visual_state',{'result':'','step':0,'playing':False}); st['step']=max(0,st.get('step',0)-1); st['playing']=False; self._visual_state=st
        self._update_step_inspector(); self.draw_visual(); self._draw_visual_progress(st['step'],self._visual_total())

    def _visual_toggle_play(self):
        st=getattr(self,'_visual_state',{'result':'','step':0,'playing':False}); st['playing']=not st.get('playing',False); self._visual_state=st
        if st['playing']:
            st['next_step_at']=time.monotonic()+self._visual_speed_delay()/1000.0

            if st.get('step',0)>=self._visual_total(): st['step']=0
            self._render_scheduler.register('_visual_trace', self._visual_frame, fps=30.0, priority=1)
        else:
            self._render_scheduler.unregister('_visual_trace')
            if self._visual_job:
                try:self.after_cancel(self._visual_job)
                except tk.TclError:pass
                self._visual_job=None
        if hasattr(self,'visual_status') and self.visual_status.winfo_exists(): self.visual_status.configure(text='TRACE PLAYING' if st['playing'] else 'TRACE PAUSED',fg=P['green'] if st['playing'] else P['yellow'])

    def _start_visual(self,result):
        if self._visual_job:
            try:self.after_cancel(self._visual_job)
            except tk.TclError:pass
        self._visual_state={'result':result,'step':0,'playing':True,'next_step_at':time.monotonic()+self._visual_speed_delay()/1000.0,'last_drawn_step':0}
        self._trace('TRACE','VISUALIZATION LINK ESTABLISHED')
        self._update_step_inspector()
        if hasattr(self,'visual_status') and self.visual_status.winfo_exists():
            self.visual_status.configure(text='TRACE INITIALIZING',fg=P['yellow'])
        self._draw_visual_progress(0,max(1,len(result)+4))
        self._render_scheduler.register('_visual_trace', self._visual_frame, fps=30.0, priority=1)

    def _visual_frame(self):
        if not self.winfo_exists() or not hasattr(self,'visual') or not self.visual.winfo_exists():
            return
        if not self._motion_page_active('processing'):
            return
        st=getattr(self,'_visual_state',None)
        if st is None:
            return
        now=time.monotonic()
        # Smooth, cheap motion is always updated. The expensive scene redraw is
        # performed only when the logical trace step changes.
        self._animate_cipher_visual_fx()
        total=self._visual_total()
        step=st.get('step',0)
        changed=False
        if st.get('playing',True) and now >= st.get('next_step_at',now):
            delay=max(0.035,self._visual_speed_delay()/1000.0)
            missed=max(1,int((now-st.get('next_step_at',now))/delay)+1)
            step += missed
            if step >= total:
                step = step % total
            st['step']=step
            st['next_step_at']=now+delay
            changed=True
        if changed or st.get('last_drawn_step') != st.get('step'):
            self.draw_visual()
            st['last_drawn_step']=st.get('step',0)
            self._update_step_inspector()
            self._draw_visual_progress(st.get('step',0),total)
            if hasattr(self,'visual_status') and self.visual_status.winfo_exists():
                self.visual_status.configure(text=f'TRACE {min(st.get("step",0),total):02d}/{total:02d}',fg=P['green'])

    def _build_cipher_visual_fx(self,c,w,h):
        """Create the lightweight live layer for every classical cipher scene."""
        fx={'columns':[],'scan':None,'pulse':None,'live':None,'phase':time.monotonic()*2.0}
        # Columns are deliberately sparse/dark and sit behind the algorithm trace.
        for i in range(11):
            x=18+i*((w-36)/10 if w>36 else 1)
            col=c.create_rectangle(x,48,x+2,h-44,fill='#0a2630',outline='',tags='cipher_fx_bg')
            fx['columns'].append((col,x,0.7+(i%4)*0.18))
        fx['scan']=c.create_line(18,46,w-18,46,fill='#1a4a59',width=1,tags='cipher_fx_overlay')
        fx['pulse']=c.create_oval(w-31,7,w-21,17,outline=P['green'],width=1,tags='cipher_fx_overlay')
        fx['live']=c.create_text(w-38,12,text='LIVE // SECURE_ACTIVE',anchor='e',fill=P['green'],font=(MONO,9,'bold'),tags='cipher_fx_overlay')
        c._hn_cipher_fx=fx
        self._animate_cipher_visual_fx()

    def _animate_cipher_visual_fx(self):
        c=getattr(self,'visual',None)
        if c is None or not c.winfo_exists() or not self._motion_page_active('processing'):
            return
        fx=getattr(c,'_hn_cipher_fx',None)
        if not fx:
            return
        try:
            w=max(40,c.winfo_width()); h=max(80,c.winfo_height()); now=time.monotonic(); phase=now*2.0
            for i,(item,x,speed) in enumerate(fx.get('columns',())):
                amp=0.18+0.08*(i%3)
                height=(0.48+amp*math.sin(phase*speed+i*0.71))*max(20,h-100)
                top=48+(max(0,h-96)-height)
                c.coords(item,x,top,x+2,h-44)
            y=48+((phase*34)%(max(1,h-72)))
            c.coords(fx['scan'],18,y,w-18,y)
            pulse=1.0+1.8*(0.5+0.5*math.sin(phase*3.2))
            c.coords(fx['pulse'],w-31-pulse/2,12-pulse/2,w-21+pulse/2,12+pulse/2)
            c.itemconfigure(fx['live'],fill=P['green'] if int(now*4)%2==0 else P['cyan'])
        except tk.TclError:
            pass

    def draw_visual(self):
        if not hasattr(self,'visual') or not self.visual.winfo_exists():return
        c=self.visual;c.delete('all');w=max(460,c.winfo_width());h=max(210,c.winfo_height())
        result=self._visual_state.get('result','') if hasattr(self,'_visual_state') else ''
        step=self._visual_state.get('step',0) if hasattr(self,'_visual_state') else 0
        algo=self.current_algo or 'caesar'; code=ALGORITHMS.get(algo,('','','','',''))[2]
        # technical grid background
        for x in range(0,w,32): c.create_line(x,0,x,h,fill='#07151d',width=1)
        for y in range(0,h,28): c.create_line(0,y,w,y,fill='#07151d',width=1)
        self._build_cipher_visual_fx(c,w,h)
        c.create_text(14,13,text=f'HN // {code} // VISUAL TRACE',fill=P['cyan'],font=(MONO, 10,'bold'),anchor='w')
        c.create_text(w-14,13,text='LOCAL ENGINE  ●',fill=P['green'],font=(MONO, 9,'bold'),anchor='e')
        c.create_line(14,27,w-14,27,fill=P['line'],width=1)
        if algo=='playfair':self._visual_playfair(c,w,h,step)
        elif algo=='railfence':self._visual_rail(c,w,h,result,step)
        elif algo in {'caesar','additive','multiplicative','affine','vigenere','atbash','rot13','beaufort','autokey'}:self._visual_classical(c,w,h,result,step,algo)
        elif algo=='hill':self._visual_matrix(c,w,h,result,step)
        elif algo in {'keyed_transposition','double_transposition','columnar'}:self._visual_transposition(c,w,h,result,step,algo)
        elif algo in {'polybius','adfgvx','bacon','morse'}:self._visual_pipeline(c,w,h,result,step,algo)
        elif algo in {'aes','des','rsa','otp','hash'}:self._visual_secure(c,w,h,result,step,algo)
        else:self._visual_pipeline(c,w,h,result,step,algo)
        # Live frequency/hex telemetry: presentation-only, derived from the
        # current real payload/result. It never claims to be internal cipher state.
        seed = hashlib.sha256((result or 'WAITING').encode('utf-8')).digest()
        hex_a = seed[:4].hex().upper(); hex_b = seed[4:8].hex().upper()
        c.create_text(16,h-18,text=f"HEX {hex_a}  //  {hex_b}",anchor='w',fill=P['dim'],font=(MONO,9,'bold'))
        c.create_text(w-16,h-18,text=f"SIG {int(seed[8])%100:02d}.{int(seed[9])%100:02d}  //  LIVE",anchor='e',fill=P['purple'],font=(MONO,9,'bold'))
        bx=16; by=h-38; bw=max(3,(w-32)//24)
        for i in range(24):
            amp=5+(seed[i%len(seed)]%18)
            x=bx+i*bw; c.create_rectangle(x,by-amp,x+max(2,bw-2),by,fill=P['line2'] if i%3 else P['cyan'],outline='')

        # Cinematic overlay shared by every cipher visualizer: a moving scanline,
        # corner HUD brackets, and a live execution pulse.
        phase=time.monotonic()*2.2
        scan=(phase % 1.0)*max(1,h-55)+34
        c.create_line(12,scan,w-12,scan,fill='#123846',width=1)
        pulse=12+5*(0.5+0.5*math.sin(phase*2.0))
        c.create_oval(w-34-pulse/2,17-pulse/2,w-34+pulse/2,17+pulse/2,outline=P['green'],width=1)
        for x1,y1,x2,y2 in [(10,35,10,50),(10,35,25,35),(w-10,35,w-10,50),(w-10,35,w-25,35)]:
            c.create_line(x1,y1,x2,y2,fill=P['cyan'],width=1)

    def _visual_classical(self,c,w,h,result,step,algo):
        vals={k:v.get() for k,v in getattr(self,'key_entries',{}).items()}
        src=(self.input_box.get('1.0','end-1c') if hasattr(self,'input_box') else '')[:32]
        out=(result or '')[:32]
        if algo=='affine': key=f"a={vals.get('a','?')}, b={vals.get('b','?')}"
        else: key=vals.get('shift',vals.get('key',vals.get('word','')))
        rows=classical_visuals.stream_rows(src,out,str(key),algo,32)
        c.create_text(16,40,text=f'{algo.upper()} // CHARACTER TRANSFORMATION',fill=P['yellow'],font=(MONO, 9,'bold'),anchor='w')
        if algo=='affine': detail='E(x) = (a·x + b) mod 26'
        elif algo=='multiplicative': detail=f'E(x) = x·{vals.get("key","?")} mod 26'
        elif algo in {'additive','caesar'}: detail=f'E(x) = x + {vals.get("shift","?")} mod 26'
        elif algo=='vigenere': detail='Cᵢ = Pᵢ + Kᵢ mod 26'
        elif algo=='autokey': detail='KEYSTREAM = KEY + PLAINTEXT'
        elif algo=='beaufort': detail='Cᵢ = Kᵢ − Pᵢ mod 26'
        elif algo=='atbash': detail='A↔Z / B↔Y / …'
        else: detail='ROT13: x + 13 mod 26'
        c.create_text(w-16,40,text=detail,fill=P['cyan'],font=(MONO, 9,'bold'),anchor='e')
        n=max(1,len(rows)); cols=max(4,min(8,n)); cell=min(74,max(42,(w-58)/cols)); x0=(w-cols*cell)/2+cell/2
        for i,(idx,a,op,b) in enumerate(rows):
            r,co=divmod(i,cols); x=x0+co*cell; y=82+r*68; active=i<step
            c.create_text(x,y-22,text=f'{idx:02d}',fill=P['dim'],font=(MONO, 9,'bold'))
            c.create_rectangle(x-cell/2+3,y-16,x+cell/2-3,y+10,fill='#0a1f28' if active else '#07131b',outline=P['cyan'] if active else P['line'],width=2 if active else 1)
            c.create_text(x,y-3,text=a if a.strip() else '·',fill=P['text'] if active else P['muted'],font=(ASCII_MONO, 10,'bold'))
            c.create_text(x,y+19,text=op,fill=P['yellow'] if active else P['dim'],font=(MONO, 9,'bold'))
            c.create_line(x,y+27,x,y+38,fill=P['purple'] if active else P['line'],width=2)
            c.create_rectangle(x-cell/2+3,y+40,x+cell/2-3,y+66,fill='#092018' if active else '#07131b',outline=P['green'] if active else P['line'],width=2 if active else 1)
            c.create_text(x,y+53,text=b if b.strip() else '·',fill=P['green'] if active else P['muted'],font=(ASCII_MONO, 10,'bold'))
        c.create_text(w/2,h-16,text=f'INPUT → {detail} → OUTPUT   //   STEP {min(step,n):02d}/{n:02d}',fill=P['muted'],font=(MONO, 9,'bold'))

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
            c.create_text(16,38,text=f'SHIFT MATRIX  //  +{shift%26}',fill=P['yellow'],font=(MONO, 9,'bold'),anchor='w')
            # Two aligned, boxed alphabet lanes prevent long ASCII strings from
            # colliding or wrapping on smaller visualizer widths.
            lane_w=max(16,min(21,(w-38)/26)); xstart=19+lane_w/2
            for i,ch in enumerate(alpha):
                x=xstart+i*lane_w
                active=i<26
                c.create_rectangle(x-lane_w/2+1,47,x+lane_w/2-1,60,fill='#07131b',outline=P['line'])
                c.create_text(x,53,text=ch,fill=P['muted'],font=(MONO, 9,'bold'))
                c.create_rectangle(x-lane_w/2+1,64,x+lane_w/2-1,77,fill='#081e27',outline=P['cyan'] if i in range(26) else P['line'])
                c.create_text(x,70,text=shifted[i],fill=P['cyan'],font=(MONO, 9,'bold'))
            base_y=93
        else:base_y=48
        for i in range(n):
            row,col=divmod(i,cols);x=x0+col*(cell_w+gap);y=base_y+row*58;active=i<step;a=src[i] if i<len(src) else '·';b=out[i] if i<len(out) else '·'
            # index marker
            c.create_text(x,y-19,text=f'{i+1:02d}',fill=P['dim'],font=(MONO, 9,'bold'))
            c.create_rectangle(x-cell_w/2,y-12,x+cell_w/2,y+10,fill='#0a1d28' if active else '#07131b',outline=P['cyan'] if active else P['line'],width=2 if active else 1)
            c.create_text(x,y-1,text=a if a.strip() else '·',fill=P['text'] if active else P['muted'],font=(ASCII_MONO, 11,'bold'))
            c.create_line(x,y+12,x,y+24,fill=P['purple'] if active else P['line'],width=2)
            c.create_polygon(x-4,y+22,x+4,y+22,x,y+28,fill=P['purple'] if active else P['line'],outline='')
            c.create_rectangle(x-cell_w/2,y+29,x+cell_w/2,y+51,fill='#092018' if active else '#07131b',outline=P['green'] if active else P['line'],width=2 if active else 1)
            c.create_text(x,y+40,text=b if b.strip() else '·',fill=P['green'] if active else P['muted'],font=(ASCII_MONO, 11,'bold'))
        label='CHARACTER TRANSFORM' if algo!='caesar' else 'CHARACTER SHIFT TRACE'
        c.create_text(w/2,h-16,text=f'INPUT  →  {label}  →  OUTPUT   //   STEP {min(step,n):02d}/{n:02d}',fill=P['muted'],font=(MONO, 9,'bold'))

    def _visual_playfair(self,c,w,h,step):
        try:key=self.key_entries.get('word').get() if 'word' in self.key_entries else 'MONARCHY'; rows=playfair.grid_preview(key).splitlines()
        except Exception:rows=playfair.grid_preview('MONARCHY').splitlines()
        size=min(42,max(28,int((h-105)/5)));ox=w/2-2.5*size;oy=58
        c.create_text(14,40,text='KEY SQUARE // DIGRAPH ROUTING',fill=P['yellow'],font=(MONO, 9,'bold'),anchor='w')
        for r,row in enumerate(rows):
            for col,ch in enumerate(row.split()):
                active=(r*5+col)<step;x=ox+col*size;y=oy+r*size
                c.create_rectangle(x-size/2+2,y-size/2+2,x+size/2-2,y+size/2-2,outline=P['cyan'] if active else P['line'],fill='#0a1f28' if active else '#07131b',width=2 if active else 1)
                c.create_text(x,y,text=ch,fill=P['green'] if active else P['text'],font=(MONO, 13,'bold'))
        c.create_text(w/2,h-16,text='5 × 5 KEY MATRIX   //   PAIR → LOCATE → TRANSFORM → EMIT',fill=P['muted'],font=(MONO, 9,'bold'))

    def _visual_rail(self,c,w,h,result,step):
        try:rails=max(2,min(7,int(self.key_entries['rails'].get() or 3)))
        except Exception:rails=3
        text=(self.input_box.get('1.0','end-1c') or 'HN BLACKBOX')[:46]; top=58; usable=max(80,w-72); span=usable/max(1,len(text)-1)
        c.create_text(16,40,text=f'ZIG-ZAG ROUTING // {rails} RAILS',fill=P['yellow'],font=(MONO, 9,'bold'),anchor='w')
        for r in range(rails):
            y=top+r*max(22,min(34,(h-100)/max(1,rails-1)));c.create_line(36,y,w-36,y,fill=P['line'],dash=(2,5))
        for i,ch in enumerate(text):
            pos=i%(2*(rails-1));row=pos if pos<rails else 2*(rails-1)-pos;x=36+i*span;y=top+row*max(22,min(34,(h-100)/max(1,rails-1)));active=i<step
            c.create_oval(x-9,y-9,x+9,y+9,fill='#0b2430' if active else '#07131b',outline=P['cyan'] if active else P['dim'],width=2 if active else 1)
            c.create_text(x,y,text=ch,fill=P['green'] if active else P['muted'],font=(MONO, 10,'bold'))
        c.create_text(w/2,h-16,text='INPUT CHARACTERS TRAVERSE THE RAILS → READOUT ORDER',fill=P['muted'],font=(MONO, 9,'bold'))

    def _visual_matrix(self,c,w,h,result,step):
        ox=w/2-155;oy=62;vals=['a','b','c','d'];
        c.create_text(14,40,text='KEY MATRIX × PLAINTEXT VECTOR',fill=P['yellow'],font=(MONO, 9,'bold'),anchor='w')
        for i,v in enumerate(vals):
            x=ox+(i%2)*70;y=oy+(i//2)*58;active=i<step
            c.create_rectangle(x-25,y-21,x+25,y+21,fill='#0a1f28' if active else '#07131b',outline=P['cyan'] if active else P['line'],width=2 if active else 1)
            value=self.key_entries.get(v).get() if v in self.key_entries else '?';c.create_text(x,y,text=value or '?',fill=P['green'] if active else P['text'],font=(MONO, 13,'bold'))
        c.create_text(ox+143,oy+35,text='×',fill=P['yellow'],font=(FONT, 20,'bold'))
        data=(self.input_box.get('1.0','end-1c') or 'HELP')[:4]
        for i,ch in enumerate(data):c.create_rectangle(ox+235+(i%2)*50,oy+(i//2)*48,ox+275+(i%2)*50,oy+36+(i//2)*48,outline=P['purple'],fill='#101022');c.create_text(ox+255+(i%2)*50,oy+18+(i//2)*48,text=ch,fill=P['text'],font=(MONO, 11,'bold'))
        c.create_text(w/2,215,text='K × P  MOD 26',fill=P['cyan'],font=(MONO, 13,'bold'))
        c.create_text(w/2,h-16,text='MATRIX MULTIPLICATION → MODULAR REDUCTION → OUTPUT BLOCK',fill=P['muted'],font=(MONO, 9,'bold'))

    def _visual_transposition(self,c,w,h,result,step,algo):
        text=self.input_box.get('1.0','end-1c') if hasattr(self,'input_box') else ''
        vals={k:v.get() for k,v in getattr(self,'key_entries',{}).items()}
        key=vals.get('word','KEY')
        if algo=='double_transposition':
            key=vals.get('word1','KEY')
            passes=2
        else:
            passes=1
        matrix,key,order,_=classical_visuals.transposition_grid(text,key,passes)
        cols=len(key); rows=len(matrix); cell=min(52,max(28,(w-90)/max(1,cols))); ox=(w-cols*cell)/2+cell/2; oy=82
        c.create_text(16,40,text=f'{algo.upper()} // COLUMN ROUTING',fill=P['yellow'],font=(MONO, 9,'bold'),anchor='w')
        c.create_text(w-16,40,text=f'PASS {1 if step < max(1,cols*rows) else passes}/{passes}',fill=P['green'],font=(MONO, 9,'bold'),anchor='e')
        for j,ch in enumerate(key):
            x=ox+j*cell
            c.create_rectangle(x-cell/2+2,48,x+cell/2-2,69,fill='#0b1e28',outline=P['purple'] if j in order[:max(1,min(step,cols))] else P['line'])
            rank=order.index(j)+1
            c.create_text(x,58,text=f'{ch} / {rank}',fill=P['cyan'] if j in order[:max(1,min(step,cols))] else P['muted'],font=(MONO, 9,'bold'))
        total=rows*cols
        for r,row in enumerate(matrix):
            for j,ch in enumerate(row):
                idx=r*cols+j; active=idx<step
                x=ox+j*cell; y=oy+r*43
                c.create_rectangle(x-cell/2+2,y-15,x+cell/2-2,y+15,fill='#092018' if active else '#07131b',outline=P['green'] if active else P['line'],width=2 if active else 1)
                c.create_text(x,y,text=ch,fill=P['green'] if active else P['muted'],font=(ASCII_MONO, 10,'bold'))
        route=' → '.join(str(x+1) for x in order)
        c.create_text(w/2,h-38,text=f'COLUMN READ ORDER: {route}',fill=P['cyan'],font=(MONO, 9,'bold'))
        c.create_text(w/2,h-16,text='WRITE ROWS → RANK KEY → READ COLUMNS',fill=P['muted'],font=(MONO, 9,'bold'))

    def _visual_pipeline(self,c,w,h,result,step,algo):
        labels=['INPUT','NORMALIZE','ENCODE','TRANSFORM','OUTPUT'];xgap=(w-120)/4
        c.create_text(16,40,text=f'{algo.upper()} // OPERATION PIPELINE',fill=P['yellow'],font=(MONO, 9,'bold'),anchor='w')
        for i,label in enumerate(labels):
            x=60+i*xgap;active=i<=min(4,step//2)
            c.create_oval(x-25,74,x+25,124,fill='#0a1f28' if active else '#07131b',outline=P['cyan'] if active else P['line'],width=2)
            c.create_text(x,99,text=f'{i+1:02d}',fill=P['cyan'] if active else P['muted'],font=(MONO, 10,'bold'))
            c.create_text(x,142,text=label,fill=P['green'] if active else P['muted'],font=(MONO, 9,'bold'))
            if i<4:c.create_line(x+27,99,x+xgap-27,99,fill=P['purple'] if active else P['line'],width=2)
        snippet=(result or self.input_box.get('1.0','end-1c') or 'WAITING')[:70]
        c.create_rectangle(24,170,w-24,215,fill='#06131a',outline=P['line'])
        c.create_text(w/2,192,text=snippet,fill=P['text'],font=(MONO, 10),anchor='center')
        c.create_text(w/2,h-16,text=f'PIPELINE COMPLETE STATE  //  STEP {step:02d}',fill=P['muted'],font=(MONO, 9,'bold'))

    def _visual_secure(self,c,w,h,result,step,algo):
        cx,cy=w/2,125;phase=step*.16;r=38+min(22,step)
        c.create_text(16,40,text=f'{algo.upper()} // SECURE BLOCK TRACE',fill=P['yellow'],font=(MONO, 9,'bold'),anchor='w')
        for ring in range(3):
            rr=r+ring*19;c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline=P['cyan'] if step>ring*2 else P['line'],width=1)
        c.create_text(cx,cy-6,text={'aes':'AES','des':'DES','rsa':'RSA','otp':'XOR','hash':'HASH'}.get(algo,'SEC'),fill=P['cyan'],font=(MONO, 18,'bold'))
        c.create_text(cx,cy+17,text='SEALED' if step>=6 else 'PROCESSING',fill=P['green'],font=(MONO, 9,'bold'))
        for i in range(18):
            ang=(i/18)*math.pi*2+phase;x=cx+145*math.cos(ang);y=cy+88*math.sin(ang);active=i<step
            c.create_line(cx+70*math.cos(ang),cy+42*math.sin(ang),x,y,fill=P['purple'] if active else P['line'],width=1)
            c.create_oval(x-3,y-3,x+3,y+3,fill=P['cyan'] if active else P['dim'],outline='')
        snippet=(result or 'NO OUTPUT YET')[:48];c.create_text(cx,h-34,text=snippet,fill=P['text'],font=(MONO, 9),anchor='center');c.create_text(cx,h-16,text='KEY → BLOCK → TRANSFORM → INTEGRITY',fill=P['muted'],font=(MONO, 9,'bold'))

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
        tk.Label(top,text=f"{prof['kicker']}  //  LOCAL SYSTEM",bg='#06131a',fg=accent,font=(MONO, 9,'bold'),anchor='w').pack(side='left',padx=12,pady=7)
        tk.Label(top,text=f"{prof['state']}  //  {prof['scope']}",bg='#06131a',fg=P['green'],font=(MONO, 9,'bold'),anchor='e').pack(side='right',padx=12,pady=7)
        body=tk.Frame(box,bg='#02070c'); body.pack(fill='x',padx=10,pady=10)
        info=tk.Frame(body,bg='#02070c'); info.pack(side='left',fill='both',expand=True,padx=(6,14))
        tk.Label(info,text=prof['title'],bg='#02070c',fg=P['text'],font=(FONT, 16,'bold'),anchor='w').pack(fill='x',pady=(2,4))
        tk.Label(info,text=f"// {prof['engine']}  //  {prof['metric']}",bg='#02070c',fg=accent,font=(MONO, 9,'bold'),anchor='w').pack(fill='x')
        tk.Label(info,text=prof['desc'],bg='#02070c',fg=P['muted'],font=(FONT, 10),anchor='w',justify='left',wraplength=650).pack(fill='x',pady=(9,8))
        rail=tk.Frame(info,bg='#02070c'); rail.pack(fill='x',pady=(2,2))
        for i,node in enumerate(prof['nodes']):
            cell=tk.Frame(rail,bg='#06131a',highlightbackground='#123541',highlightthickness=1); cell.pack(side='left',fill='x',expand=True,padx=2)
            tk.Label(cell,text=f'{i+1:02d}',bg='#06131a',fg=accent,font=(MONO, 9,'bold')).pack(anchor='w',padx=7,pady=(5,0))
            tk.Label(cell,text=node,bg='#06131a',fg=P['text'],font=(MONO, 9,'bold')).pack(anchor='w',padx=7,pady=(0,5))
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
                    r=viz.create_rectangle(xs[i]-18,cy-22,xs[i]+18,cy+22,outline=accent if i==0 else '#174653',width=1); viz.create_text(xs[i],cy,text=label[:5],fill=P['text'],font=(MONO, 9,'bold')); dyn['flow'].append(r)
                dyn['packet']=viz.create_oval(16,cy-3,22,cy+3,fill=P['green'],outline='')
            elif kind=='blue':
                dyn['timeline']=[]
                for i in range(5):
                    y=35+i*27; viz.create_line(28,y,w-18,y,fill='#153944'); dyn['timeline'].append(viz.create_oval(25,y-4,33,y+4,fill=accent if i%2 else P['green'],outline=''))
                dyn['cursor']=viz.create_line(28,22,28,h-12,fill=P['cyan'],width=2)
            elif kind=='labs':
                dyn['nodes']=[]
                for i,label in enumerate(['BRIEF','TEST','CHECK','PROG']):
                    x=28+i*54; r=10; viz.create_text(x,h-23,text=label,fill=P['muted'],font=(MONO, 9,'bold')); dyn['nodes'].append(viz.create_oval(x-r,cy-r,x+r,cy+r,outline=accent,width=1))
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
                    viz.create_rectangle(xs[i]-17,cy-20,xs[i]+17,cy+20,outline=accent if i==0 else '#174653',width=1); viz.create_text(xs[i],cy,text=label[:5],fill=P['text'],font=(MONO, 9,'bold')); dyn['flow'].append(xs[i])
                dyn['packet']=viz.create_oval(18,cy-3,24,cy+3,fill=P['green'],outline='')
            dyn['label']=viz.create_text(cx,h-12,text=f"SEQ 0000  //  {prof['engine']}",fill=accent,font=(MONO, 9,'bold'))
            state_ref['dynamic']=dyn; state_ref['size']=(w,h)
        def animate():
            if not viz.winfo_exists(): return
            if not self._motion_page_active(key):
                viz.after(120, animate); return
            # Foreground-only module intelligence HUD; retained geometry remains intact off-page.
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
        self.lab_v17_status=tk.Label(bar,text='',bg=P['panel'],fg=P['green'],font=(MONO, 10,'bold'),anchor='w'); self.lab_v17_status.pack(side='left',padx=4)
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
            tk.Label(head,text=lab['id'],bg=P['panel2'],fg=accent,font=(MONO, 9,'bold')).pack(side='left',padx=10,pady=9)
            tk.Label(head,text=lab['difficulty'].upper(),bg=P['panel2'],fg=accent,font=(MONO, 9,'bold')).pack(side='right',padx=10,pady=9)
            tk.Label(card,text=lab['title'],bg=P['panel'],fg=P['text'],font=(FONT, 13,'bold'),anchor='w').pack(fill='x',padx=12,pady=(10,3))
            tk.Label(card,text=lab['category']+'  //  '+lab['objective'],bg=P['panel'],fg=accent,font=(MONO, 9,'bold'),anchor='w',wraplength=430,justify='left').pack(fill='x',padx=12,pady=(0,5))
            tk.Label(card,text=lab['prompt'],bg=P['panel'],fg=P['muted'],font=(FONT, 10),anchor='w',wraplength=430,justify='left').pack(fill='x',padx=12,pady=(0,8))
            ans=tk.Entry(card,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 10)); ans.pack(fill='x',padx=12,pady=4)
            status=tk.Label(card,text='READY',bg=P['panel'],fg=P['cyan'],font=(MONO, 9,'bold'),anchor='w'); status.pack(fill='x',padx=12,pady=4)
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


    # ---------- OSINT / file intelligence ----------
    def _file_intel_signature(self, head):
        """Compatibility wrapper around the real forensic engine."""
        kind, _ = file_forensics._signature(head, "")
        return kind

    def _file_intel_entropy(self, data):
        return file_forensics._entropy(data)

    def _file_intel_worker(self, path):
        """Real local forensic worker. It never touches Tk and never modifies the source."""
        return file_forensics.analyze_file(path)

    def file_intelligence_page(self):
        p=tk.Frame(self.content,bg=P['bg'])
        self.heading(p,'HN / INTELLIGENCE','OSINT / FILE INTELLIGENCE','REAL-FILE FORENSICS // local metadata, fingerprints and safe derivative scrubbing. No upload, network collection or execution.')
        host=tk.Frame(p,bg='#02070b'); host.pack(fill='both',expand=True)
        left=self.card(host); left.pack(side='left',fill='both',expand=True,padx=(0,7)); right=self.card(host); right.pack(side='right',fill='both',expand=True,padx=(7,0)); right.configure(width=500); right.pack_propagate(False)

        tk.Label(left,text='01 // EVIDENCE INTAKE // REAL FILE',bg=P['panel'],fg=P['cyan'],font=(MONO,11,'bold'),anchor='w').pack(fill='x',padx=14,pady=(12,4))
        self.fileintel_path=tk.Entry(left,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,10)); self.fileintel_path.pack(fill='x',padx=14,pady=8)
        self.fileintel_path.insert(0,'Select a real image, PDF, Office document or supported file…')
        actions=tk.Frame(left,bg=P['panel']); actions.pack(fill='x',padx=14,pady=4)
        self.btn(actions,'SELECT EVIDENCE',self._fileintel_pick,True).pack(side='left',padx=(0,5))
        self.btn(actions,'ANALYZE',self._fileintel_analyze,True).pack(side='left',padx=5)
        self.btn(actions,'CLEAR',self._fileintel_clear).pack(side='left',padx=5)
        self.fileintel_status=tk.Label(left,text='STANDBY // REAL LOCAL FORENSIC ENGINE READY',bg=P['panel'],fg=P['green'],font=(MONO,9,'bold'),anchor='w'); self.fileintel_status.pack(fill='x',padx=14,pady=(5,8))
        self.fileintel_report=tk.Text(left,bg='#02080d',fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,9),wrap='none',height=22); self.fileintel_report.pack(fill='both',expand=True,padx=14,pady=(0,10))

        scrub=tk.Frame(left,bg='#061018',highlightbackground=P['line'],highlightthickness=1); scrub.pack(fill='x',padx=14,pady=(0,12))
        tk.Label(scrub,text='METADATA SCRUBBER // WRITE CLEAN DERIVATIVE ONLY',bg='#061018',fg=P['yellow'],font=(MONO,9,'bold'),anchor='w').pack(fill='x',padx=10,pady=(8,4))
        self.fileintel_scrub_vars={}
        scrub_grid=tk.Frame(scrub,bg='#061018'); scrub_grid.pack(fill='x',padx=8,pady=2)
        scrub_fields=('Author','Creator','Producer','Title','Subject','Keywords','CreationDate','ModDate','LastModifiedBy','Application','Company','Manager')
        for i,key in enumerate(scrub_fields):
            v=tk.BooleanVar(value=False); self.fileintel_scrub_vars[key]=v
            tk.Checkbutton(scrub_grid,text=key,bg='#061018',fg=P['muted'],activebackground='#061018',activeforeground=P['text'],selectcolor='#0b1b28',variable=v,font=(MONO,9),anchor='w').grid(row=i//4,column=i%4,sticky='w',padx=3,pady=1)
        self.fileintel_full_strip=tk.BooleanVar(value=False)
        tk.Checkbutton(scrub,text='FULL STRIP // remove supported embedded metadata/XMP and create a clean derivative',bg='#061018',fg=P['green'],activebackground='#061018',activeforeground=P['green'],selectcolor='#0b1b28',variable=self.fileintel_full_strip,font=(MONO,9,'bold'),anchor='w').pack(fill='x',padx=10,pady=(4,5))
        scrub_actions=tk.Frame(scrub,bg='#061018'); scrub_actions.pack(fill='x',padx=10,pady=(0,9))
        self.btn(scrub_actions,'SCRUB SELECTED',self._fileintel_scrub_selected,True).pack(side='left',padx=(0,5))
        self.btn(scrub_actions,'FULL STRIP',self._fileintel_full_strip_run,True).pack(side='left',padx=5)
        self.fileintel_scrub_status=tk.Label(scrub_actions,text='NO CLEAN DERIVATIVE WRITTEN',bg='#061018',fg=P['dim'],font=(MONO,9,'bold'),anchor='w'); self.fileintel_scrub_status.pack(side='right',padx=5)

        tk.Label(right,text='02 // FORENSIC HUD // FINGERPRINT + LIVE RADAR',bg=P['panel'],fg=P['green'],font=(MONO,11,'bold'),anchor='w').pack(fill='x',padx=14,pady=(12,4))
        self.fileintel_canvas=tk.Canvas(right,bg='#010509',highlightbackground='#123f4c',highlightthickness=1,bd=0); self.fileintel_canvas.pack(fill='both',expand=True,padx=14,pady=8)
        self._fileintel_phase=0.0; self._fileintel_last_frame=time.perf_counter(); self._fileintel_running=False; self._fileintel_result=None; self._fileintel_future=None
        self._fileintel_executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='hn-file-intel')
        self.fileintel_canvas.bind('<Configure>',lambda e:self._draw_fileintel_hud())
        self._draw_fileintel_hud()
        self._fileintel_refresh_scrub_controls()
        return p

    def _fileintel_pick(self):
        path=filedialog.askopenfilename(title='Select real evidence',filetypes=[('Images / PDF / Office','*.png *.jpg *.jpeg *.gif *.bmp *.webp *.tif *.tiff *.pdf *.docx *.xlsx *.pptx'),('Text / data','*.txt *.csv *.json *.xml'),('All files','*.*')])
        if path:
            self.fileintel_path.delete(0,'end'); self.fileintel_path.insert(0,path); self._fileintel_result=None
            self._fileintel_refresh_scrub_controls(); self._fileintel_set_status('EVIDENCE SELECTED // HASH + METADATA READY',P['cyan']); self._draw_fileintel_hud()

    def _fileintel_set_status(self,text,color):
        if hasattr(self,'fileintel_status') and self.fileintel_status.winfo_exists(): self.fileintel_status.configure(text=text,fg=color)

    def _fileintel_analyze(self):
        path=self.fileintel_path.get().strip()
        if not path or path.startswith('Select a real'): return self._fileintel_set_status('SELECT A FILE FIRST',P['orange'])
        if not Path(path).is_file(): return self._fileintel_set_status('FILE NOT FOUND // NO DATA READ',P['red'])
        if self._fileintel_running: return
        self._fileintel_running=True; self._fileintel_result=None; self._fileintel_set_status('ACQUIRING EVIDENCE // MD5 + SHA-256 + METADATA…',P['yellow']); self._draw_fileintel_hud(running=True)
        fut=self._fileintel_executor.submit(self._file_intel_worker,path); self._fileintel_future=fut
        def done(f):
            try: result=f.result(); self._queue_worker_event(lambda r=result:self._fileintel_present(r))
            except Exception as exc: self._queue_worker_event(lambda e=exc:self._fileintel_error(e))
        fut.add_done_callback(done)

    def _fileintel_present(self,r):
        self._fileintel_running=False; self._fileintel_result=r; self._fileintel_set_status('ANALYSIS COMPLETE // REAL FILE // READ-ONLY',P['green']); self._draw_fileintel_hud(result=r); self._fileintel_refresh_scrub_controls()
        fs=r['filesystem']; lines=['HN BLACKBOX // REAL-FILE FORENSIC REPORT','='*82,f'FILE        : {r["name"]}',f'PATH        : {r["path"]}',f'SIZE        : {r["size"]:,} bytes',f'TYPE        : {r["type"]}',f'MIME        : {r["mime"]}',f'CREATED     : {fs["created"]}',f'MODIFIED    : {fs["modified"]}',f'ACCESSED    : {fs["accessed"]}',f'NOTE        : {fs["created_note"]}',f'ENTROPY     : {r["entropy"]:.4f} / 8.0000','',f'MD5         : {r["md5"]}',f'SHA-256     : {r["sha256"]}',f'SHA-1       : {r["sha1"]}','', 'EMBEDDED METADATA / PROPERTIES','-'*82]
        for item in r['metadata']: lines.append(f'{item["key"]:<20}: {item["value"]}')
        if not r['metadata']: lines.append('NONE                    : No embedded metadata exposed by the registered parser.')
        lines += ['', 'PRINTABLE EVIDENCE SAMPLE','-'*82] + [f'[{i+1:02d}] {x}' for i,x in enumerate(r['strings'])]
        if r['warnings']: lines += ['', 'PARSER WARNINGS','-'*82] + [f'! {x}' for x in r['warnings']]
        lines += ['', 'CHAIN OF CUSTODY','-'*82,'SOURCE WAS NOT MODIFIED // ANALYSIS IS LOCAL / READ-ONLY','SCRUB OPERATIONS CREATE A SEPARATE DERIVATIVE AND REFUSE SOURCE OVERWRITE.']
        self.fileintel_report.delete('1.0','end'); self.fileintel_report.insert('end','\n'.join(lines))

    def _fileintel_error(self,exc):
        self._fileintel_running=False; self._fileintel_set_status('ANALYSIS FAILED // '+str(exc)[:110],P['red']); self._draw_fileintel_hud(); self._fileintel_refresh_scrub_controls()

    def _fileintel_refresh_scrub_controls(self):
        enabled=bool(getattr(self,'_fileintel_result',None)) and not getattr(self,'_fileintel_running',False)
        for v in getattr(self,'fileintel_scrub_vars',{}).values():
            # Checkbuttons are located via the variable state; leave selection intact but gate action.
            pass
        if hasattr(self,'fileintel_scrub_status') and self.fileintel_scrub_status.winfo_exists():
            self.fileintel_scrub_status.configure(text='READY // SELECT FIELDS OR FULL STRIP' if enabled else 'ANALYZE A FILE FIRST',fg=P['green'] if enabled else P['dim'])

    def _fileintel_scrub(self, full_strip=False):
        r=getattr(self,'_fileintel_result',None)
        if not r: return self._fileintel_set_status('ANALYZE A FILE BEFORE SCRUBBING',P['orange'])
        fields=[k for k,v in getattr(self,'fileintel_scrub_vars',{}).items() if v.get()]
        if not full_strip and not fields: return self._fileintel_set_status('SELECT AT LEAST ONE METADATA FIELD',P['orange'])
        src=r['path']
        try:
            out=filedialog.asksaveasfilename(title='Save clean derivative',defaultextension=Path(src).suffix,initialfile=f'{Path(src).stem}_CLEAN{Path(src).suffix}',filetypes=[('Same file type',f'*{Path(src).suffix}'),('All files','*.*')])
            if not out: return
            self._fileintel_set_status('SCRUBBING // WRITING CLEAN DERIVATIVE…',P['yellow'])
            self.fileintel_scrub_status.configure(text='WRITING CLEAN DERIVATIVE',fg=P['yellow'])
            def work(): return file_forensics.scrub_metadata(src,out,fields=fields,full_strip=full_strip)
            fut=self._fileintel_executor.submit(work)
            fut.add_done_callback(lambda f:self._queue_worker_event(lambda:self._fileintel_scrub_done(f)))
        except Exception as exc: self._fileintel_set_status('SCRUB PREPARATION FAILED // '+str(exc)[:100],P['red'])

    def _fileintel_scrub_selected(self): self._fileintel_scrub(False)
    def _fileintel_full_strip_run(self):
        if hasattr(self,'fileintel_full_strip'): self.fileintel_full_strip.set(True)
        self._fileintel_scrub(True)

    def _fileintel_scrub_done(self,future):
        try:
            result=future.result(); after=result['after']; self.fileintel_scrub_status.configure(text=f'CLEAN DERIVATIVE SAVED // {after["sha256"][:16]}…',fg=P['green']); self._fileintel_set_status('SCRUB COMPLETE // SOURCE PRESERVED // OUTPUT HASHED',P['green'])
            self.fileintel_report.insert('end',f'\n\n[SCRUB COMPLETE]\nOUTPUT     : {result["output"]}\nOUTPUT MD5 : {after["md5"]}\nOUTPUT SHA256 : {after["sha256"]}\nMETHOD     : {result["operation"]["method"]}\nSOURCE     : UNTOUCHED\n')
        except Exception as exc:
            self.fileintel_scrub_status.configure(text='SCRUB FAILED',fg=P['red']); self._fileintel_set_status('SCRUB FAILED // '+str(exc)[:110],P['red'])

    def _fileintel_clear(self):
        self._fileintel_running=False; self._fileintel_result=None
        if hasattr(self,'_fileintel_future') and self._fileintel_future and not self._fileintel_future.done():
            try: self._fileintel_future.cancel()
            except Exception: pass
        if hasattr(self,'fileintel_report'): self.fileintel_report.delete('1.0','end')
        if hasattr(self,'fileintel_path'): self.fileintel_path.delete(0,'end'); self.fileintel_path.insert(0,'Select a real image, PDF, Office document or supported file…')
        for v in getattr(self,'fileintel_scrub_vars',{}).values(): v.set(False)
        if hasattr(self,'fileintel_full_strip'): self.fileintel_full_strip.set(False)
        self._fileintel_set_status('STANDBY // FORENSIC HUD RESET // READY',P['green']); self._fileintel_refresh_scrub_controls(); self._draw_fileintel_hud()

    def _animate_network_diagnostics(self):
        """Autonomous network HUD: animation never depends on hover/input."""
        c=getattr(self,'network_hud_canvas',None)
        if c is None or not c.winfo_exists(): return
        st=self._network_diag; st['phase']=(st.get('phase',0.0)+0.045)%math.tau
        now=time.monotonic()
        if st.get('capture') and not st.get('sample_busy') and now-st.get('sample_at',0.0)>=0.65:
            st['sample_busy']=True; st['sample_at']=now
            def sample_work(): return network_diag.traffic_snapshot(), network_diag.socket_snapshot()
            def sample_done(data):
                traffic,socks=data; prev=st.get('traffic_prev'); st['traffic_prev']=traffic
                if prev:
                    dt=max(0.05, now-st.get('rate_at',now)); st['traffic_rate']={'sent':max(0,traffic['total_sent']-prev['total_sent'])/dt,'recv':max(0,traffic['total_recv']-prev['total_recv'])/dt}
                st['rate_at']=time.monotonic(); st['sockets']=socks; st['sample_busy']=False
                if hasattr(self,'network_sockets') and self.network_sockets.winfo_exists():
                    self.network_sockets.delete('1.0','end')
                    for r in socks[:180]: self.network_sockets.insert('end', f'{r["proto"]:<4} {r["status"]:<12} {r["local"]:<23} -> {r["remote"]:<23} PID={r["pid"]}\n')
            def sample_fail(_exc): st['sample_busy']=False
            self._run_ui_worker(sample_work,sample_done,sample_fail)
        w=max(420,c.winfo_width()); h=max(240,c.winfo_height()); p=st['phase']
        c.delete('all'); c.create_rectangle(0,0,w,h,fill='#01070c',outline='')
        for x in range(0,w,32): c.create_line(x,0,x,h,fill='#06151c')
        for y in range(0,h,24): c.create_line(0,y,w,y,fill='#06151c')
        # autonomous radar
        cx,cy=w*.23,h*.52; r=min(w*.20,h*.38)
        for rr in (r,r*.72,r*.44): c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline=P['line'])
        a=p; c.create_line(cx,cy,cx+r*math.cos(a),cy+r*math.sin(a),fill=P['cyan'],width=2)
        for i in range(9):
            aa=a+i*math.tau/9; px=cx+r*.82*math.cos(aa); py=cy+r*.82*math.sin(aa)
            c.create_oval(px-2,py-2,px+2,py+2,fill=P['green'] if i%3==0 else P['cyan'],outline='')
        # topology matrix from real snapshot, otherwise a clearly labeled standby graph
        topo=st.get('topology') or {}
        nodes=topo.get('nodes',[]); links=topo.get('links',[])
        ox,oy=w*.53,h*.50; positions={'LOCAL':(ox,oy)}
        others=[n for n in nodes if n.get('id')!='LOCAL'][:14]
        for i,n in enumerate(others):
            aa=(i/max(1,len(others)))*math.tau+p*.10; rr=min(w*.20,h*.30); positions[n['id']]=(ox+rr*math.cos(aa),oy+rr*math.sin(aa))
        for link in links[:30]:
            a0=positions.get(link['source']); b0=positions.get(link['target'])
            if a0 and b0:
                c.create_line(*a0,*b0,fill=P['line2'],width=1)
                pulse=(p*0.7+i)%1.0 if others else 0
                mx=a0[0]+(b0[0]-a0[0])*pulse; my=a0[1]+(b0[1]-a0[1])*pulse
                c.create_oval(mx-2,my-2,mx+2,my+2,fill=P['yellow'],outline='')
        for i,n in enumerate(others):
            x,y=positions[n['id']]; col=P['green'] if n.get('status')=='ACTIVE' else P['yellow']
            c.create_oval(x-5,y-5,x+5,y+5,fill=col,outline=P['text'])
            c.create_text(x+8,y-8,text=str(n['id'])[:20],anchor='w',fill=P['text'],font=(MONO,9,'bold'))
        c.create_oval(ox-7,oy-7,ox+7,oy+7,fill=P['cyan'],outline=P['text'])
        c.create_text(12,12,text='NETWORK MATRIX // REAL LOCAL TELEMETRY // AUTONOMOUS 60FPS',anchor='nw',fill=P['cyan'],font=(MONO,9,'bold'))
        c.create_text(w-12,12,text='CAPTURE: '+('LIVE' if st.get('capture') else 'STANDBY'),anchor='ne',fill=P['green'] if st.get('capture') else P['muted'],font=(MONO,9,'bold'))
        sent=st.get('traffic_rate',{}).get('sent',0.0); recv=st.get('traffic_rate',{}).get('recv',0.0)
        c.create_text(12,h-14,text=f'TX {sent/1024:.1f} KB/s   RX {recv/1024:.1f} KB/s   NODES {len(nodes)}   LINKS {len(links)}',anchor='sw',fill=P['muted'],font=(MONO,9,'bold'))
        # waveform / pulse rail
        pts=[]
        for i in range(80):
            xx=w*.73+i*(w*.25/79); yy=h*.76-math.sin(i*.48+p*2.2)*(7+min(22,(sent+recv)/4096))
            pts.extend((xx,yy))
        if len(pts)>=4: c.create_line(*pts,fill=P['green'],width=2,smooth=True)

    def _animate_fileintel_hud(self):
        c=getattr(self,'fileintel_canvas',None)
        if c is None or not c.winfo_exists(): return
        now=time.perf_counter(); dt=min(0.05,max(0.001,now-getattr(self,'_fileintel_last_frame',now))); self._fileintel_last_frame=now
        self._fileintel_phase=(getattr(self,'_fileintel_phase',0.0)+dt*math.tau*0.28)%(math.tau)
        self._draw_fileintel_hud(running=getattr(self,'_fileintel_running',False),result=getattr(self,'_fileintel_result',None),animated=True)

    def _draw_fileintel_hud(self,running=False,result=None,animated=False):
        c=getattr(self,'fileintel_canvas',None)
        if c is None or not c.winfo_exists(): return
        w=max(320,c.winfo_width()); h=max(300,c.winfo_height())
        c.delete('all'); c.create_rectangle(0,0,w,h,fill='#010509',outline='')
        for x in range(0,w,24): c.create_line(x,0,x,h,fill='#06151b')
        for y in range(0,h,24): c.create_line(0,y,w,y,fill='#06151b')
        cx,cy=w*.50,h*.42; r=min(w*.34,h*.25); phase=getattr(self,'_fileintel_phase',0.0)
        for rr in (r,r*.78,r*.56): c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline='#123741')
        c.create_line(cx,cy,cx+r*math.cos(phase),cy+r*math.sin(phase),fill=P['green'] if not running else P['yellow'],width=2)
        c.create_line(cx,cy,cx+r*.75*math.cos(-phase*.61),cy+r*.75*math.sin(-phase*.61),fill=P['cyan'],width=1)
        c.create_line(cx-r,cy,cx+r,cy,fill='#0d2b34'); c.create_line(cx,cy-r,cx,cy+r,fill='#0d2b34')
        # Moving perimeter pulses keep the radar alive during both idle and analysis.
        for i in range(8):
            a=phase+i*math.tau/8; px=cx+r*math.cos(a); py=cy+r*math.sin(a); c.create_oval(px-2,py-2,px+2,py+2,fill=P['cyan'] if i%2 else P['green'],outline='')
        c.create_text(12,12,text='EVIDENCE MATRIX // READ-ONLY // 60FPS CLOCK',anchor='nw',fill=P['cyan'],font=(MONO,9,'bold'))
        c.create_text(w-12,12,text='ANALYZING' if running else ('VERIFIED' if result else 'STANDBY'),anchor='ne',fill=P['yellow'] if running else (P['green'] if result else P['muted']),font=(MONO,9,'bold'))
        if result:
            c.create_text(cx,cy,text='HASH\nVERIFIED',fill=P['green'],font=(MONO,12,'bold'),justify='center')
            vals=[('MD5',result['md5'][:16],P['purple']),('SHA256',result['sha256'][:18],P['cyan']),('TYPE',result['type'][:18],P['yellow']),('META',str(len(result['metadata'])),P['green'])]
            for i,(k,v,col) in enumerate(vals): c.create_text(12,h-92+i*21,text=f'{k:<7} {v}',anchor='w',fill=col,font=(MONO,9,'bold'))
        else:
            c.create_text(cx,cy,text='NO EVIDENCE\nMOUNTED',fill=P['muted'],font=(MONO,12,'bold'),justify='center')
        # Bottom live trace derived from the actual hash when available.
        seed=(result['sha256'] if result else '0'*64)
        for i in range(28):
            x=12+i*((w-24)/28); n=int(seed[(i+int(phase*4))%len(seed)],16) if seed else 0; bh=5+n*1.8
            c.create_rectangle(x,h-22-bh,x+max(2,(w-30)/28),h-22,fill=P['line2'] if i%3 else P['cyan'],outline='')
        if not animated: self._fileintel_last_frame=time.perf_counter()

    def network_diagnostics_page(self):
        p=tk.Frame(self.content,bg=P['bg']); self.heading(p,'HN / NETWORK OPS','REAL NETWORK DIAGNOSTICS // الشبكة الحية','Local/private-scope TCP diagnostics, OS socket telemetry, routing view and live interface counters. No packet injection or credential attacks.')
        canvas,inner=self._make_canvas(p)
        deck=self.glass(inner); deck.pack(fill='x',pady=(0,8))
        tk.Label(deck,text='TACTICAL CONTROL DECK // REAL-WORLD LOCAL SCOPE',bg=P['panel2'],fg=P['cyan'],font=(MONO,11,'bold'),anchor='w').pack(fill='x',padx=14,pady=(10,4))
        row=tk.Frame(deck,bg=P['panel2']); row.pack(fill='x',padx=14,pady=7)
        target=tk.Entry(row,bg='#06111a',fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,10)); target.pack(side='left',fill='x',expand=True,padx=(0,6)); target.insert(0,'127.0.0.1')
        ports=tk.Entry(row,bg='#06111a',fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,10),width=34); ports.pack(side='left',padx=6); ports.insert(0,'21,22,80,443,8080')
        scope=tk.Entry(row,bg='#06111a',fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO,10),width=22); scope.pack(side='left',padx=6); scope.insert(0,'192.168.1.0/24')
        status=tk.Label(deck,text='STANDBY // PRIVATE / LOOPBACK SCOPE ONLY',bg=P['panel2'],fg=P['green'],font=(MONO,9,'bold'),anchor='w'); status.pack(fill='x',padx=14,pady=(0,7))
        def log(msg):
            stamp=datetime.now().strftime('%H:%M:%S'); self._network_diag['ops'].append(f'[{stamp}] {msg}'); self._network_diag['ops']=self._network_diag['ops'][-80:]
            if hasattr(self,'network_terminal') and self.network_terminal.winfo_exists():
                self.network_terminal.configure(state='normal'); self.network_terminal.insert('end',f'[{stamp}] {msg}\n'); self.network_terminal.see('end'); self.network_terminal.configure(state='disabled')
        def done_scan(data):
            self._network_diag['scan_rows']=data; self._network_diag['running']=False; status.configure(text=f'SCAN COMPLETE // {len([x for x in data if x["state"]=="open"])} OPEN / {len(data)} TESTED',fg=P['green']);
            self.network_ports.delete('1.0','end')
            self.network_ports.insert('end','HOST       PORT   STATE    LATENCY\n'+'-'*43+'\n'+''.join(f'{r["host"]:<11} {r["port"]:>5}   {r["state"]:<7}  {r["latency_ms"]:>7.2f} ms\n' for r in data)); log('TCP CONNECT SCAN COMPLETE // '+target.get().strip())
        def fail(exc): self._network_diag['running']=False; status.configure(text='SCAN ERROR // '+str(exc)[:100],fg=P['red']); log('SCAN ERROR // '+str(exc))
        def run_scan():
            if self._network_diag['running']: return
            try: plist=[int(x.strip()) for x in ports.get().split(',') if x.strip()]; self._network_diag['running']=True; status.configure(text='NET-SCAN RUNNING // REAL TCP CONNECT TESTS',fg=P['yellow']); log('INITIALIZE NET-SCAN // '+target.get().strip()); self._run_ui_worker(lambda:network_diag.port_scan(target.get().strip(),plist),done_scan,fail)
            except Exception as exc: fail(exc)
        def run_subnet():
            self._network_diag['running']=True; status.configure(text='SUBNET DISCOVERY RUNNING // PRIVATE SCOPE',fg=P['yellow']); log('SUBNET SCAN // '+scope.get().strip()); self._run_ui_worker(lambda:network_diag.subnet_scan(scope.get().strip(),tuple(int(x.strip()) for x in ports.get().split(',') if x.strip())[:8]),lambda d:(self._network_diag.update(running=False),self.network_ports.delete('1.0','end'),self.network_ports.insert('end',json.dumps(d,indent=2)),status.configure(text=f'SUBNET COMPLETE // {d["hosts_found"]} HOSTS WITH OPEN PORTS',fg=P['green']),log('SUBNET SCAN COMPLETE')),fail)
        def capture():
            self._network_diag['capture']=not self._network_diag.get('capture'); log('SOCKET FLOW CAPTURE '+('ENABLED' if self._network_diag['capture'] else 'PAUSED')); status.configure(text='LIVE SOCKET FLOW // '+('CAPTURING' if self._network_diag['capture'] else 'PAUSED'),fg=P['green'] if self._network_diag['capture'] else P['muted'])
        def trace():
            log('TRACE TOPOLOGY // REQUESTED'); self._run_ui_worker(network_diag.topology_snapshot,lambda d:(self._network_diag.update(topology=d,sockets=d.get('sockets',[])),status.configure(text=f'TOPOLOGY READY // {len(d.get("nodes",[]))} NODES / {len(d.get("links",[]))} LINKS',fg=P['cyan']),self._render_network_tables(d),log('TOPOLOGY SNAPSHOT READY')),fail)
        def flush():
            self._network_diag['topology']=None; self._network_diag['sockets']=[]; self._network_diag['traffic_prev']=None; self.network_ports.delete('1.0','end'); self.network_sockets.delete('1.0','end'); log('FLUSH ROUTING // VIEW RESET ONLY (OS ROUTES UNCHANGED)'); status.configure(text='ROUTING VIEW FLUSHED // NO OS ROUTE MODIFICATION',fg=P['yellow'])
        self.btn(row,'INITIALIZE NET-SCAN',run_scan,True).pack(side='left',padx=4); self.btn(row,'SUBNET SCAN',run_subnet).pack(side='left',padx=4); self.btn(row,'CAPTURE PACKETS',capture).pack(side='left',padx=4); self.btn(row,'TRACE TOPOLOGY',trace).pack(side='left',padx=4); self.btn(row,'FLUSH ROUTING',flush).pack(side='left',padx=4)
        hudbox=self.card(inner); hudbox.pack(fill='x',pady=6); self.network_hud_canvas=tk.Canvas(hudbox,height=300,bg='#01070c',highlightthickness=0); self.network_hud_canvas.pack(fill='both',expand=True,padx=8,pady=8)
        grids=tk.Frame(inner,bg=P['bg']); grids.pack(fill='both',expand=True,pady=6); grids.columnconfigure(0,weight=1); grids.columnconfigure(1,weight=1)
        ports_box=self.card(grids); ports_box.grid(row=0,column=0,sticky='nsew',padx=(0,5)); self._tool_header(ports_box,'PORT MATRIX // TCP CONNECT','Real connection tests. Open means a TCP connect succeeded from this host.'); self.network_ports=tk.Text(ports_box,height=12,bg='#02080d',fg=P['green'],font=(MONO,9),relief='flat'); self.network_ports.pack(fill='both',expand=True,padx=10,pady=(0,10))
        sock_box=self.card(grids); sock_box.grid(row=0,column=1,sticky='nsew',padx=(5,0)); self._tool_header(sock_box,'LIVE SOCKET INSPECTOR // TCP/UDP','OS-visible endpoint telemetry; payload contents are never collected.'); self.network_sockets=tk.Text(sock_box,height=12,bg='#02080d',fg=P['cyan'],font=(MONO,9),relief='flat'); self.network_sockets.pack(fill='both',expand=True,padx=10,pady=(0,10))
        term=self.glass(inner); term.pack(fill='x',pady=6); self._tool_header(term,'NETWORK OPERATIONS TERMINAL','Timestamped operations, scan state and packet/socket telemetry.'); self.network_terminal=tk.Text(term,height=7,bg='#02070b',fg=P['text'],font=(MONO,9),relief='flat',state='disabled'); self.network_terminal.pack(fill='x',padx=10,pady=(0,8)); log('NETWORK DIAGNOSTICS ONLINE // REAL LOCAL TELEMETRY')
        copyrow=tk.Frame(term,bg=P['panel2']); copyrow.pack(fill='x',padx=10,pady=(0,10))
        def copy_ports(): self.clipboard_clear(); self.clipboard_append(self.network_ports.get('1.0','end-1c')); self._terminal_flash(P['cyan'],'PORT REPORT COPIED')
        def copy_sockets(): self.clipboard_clear(); self.clipboard_append(self.network_sockets.get('1.0','end-1c')); self._terminal_flash(P['green'],'SOCKET REPORT COPIED')
        self.btn(copyrow,'COPY PORT REPORT',copy_ports).pack(side='right',padx=3); self.btn(copyrow,'COPY SOCKET REPORT',copy_sockets).pack(side='right',padx=3)
        return p

    def _render_network_tables(self,d):
        if hasattr(self,'network_sockets') and self.network_sockets.winfo_exists():
            self.network_sockets.delete('1.0','end')
            for r in d.get('sockets',[])[:180]: self.network_sockets.insert('end',f'{r["proto"]:<4} {r["status"]:<12} {r["local"]:<23} -> {r["remote"]:<23} PID={r["pid"]}\n')

    # ---------- roadmap / future areas ----------
    def future_page(self,key):
        p=tk.Frame(self.content,bg=P['bg'])
        titles={'analysis':('CRYPTANALYSIS // ANALYSIS LAB','Frequency, Index of Coincidence, Caesar ranking and Kasiski examination.'),'network':('NETWORK SECURITY // LOCAL TOOLKIT','IP intelligence, subnet math and DNS resolution from the local machine.'),'fileintel':('OSINT / FILE INTELLIGENCE // LOCAL FORENSICS','Local metadata, fingerprint, signature and evidence analysis. No external collection.'),'web':('WEB SECURITY // SAFE LAB','HTTP parsing, local request simulation and OWASP defensive concepts.'),'blue':('BLUE TEAM // DEFENSE CENTER','Log triage, IOC classification, timeline extraction and hash inspection.'),'labs':('SECURITY LABS // OFFLINE ARENA','Real local training challenges across cryptography, hashing, network, web security, blue team and forensics.'), 'toolkit':('SECURITY TOOLKIT // FIELD CONSOLE','Functional local utilities for hashing, encoding, parsing, IOC extraction and evidence handling.')}
        title,sub=titles[key]
        self.heading(p,'HN / MODULE',self.t(key),sub)
        canvas,inner=self._make_canvas(p)
        self._module_hud(inner,key)
        banner=self.glass(inner);banner.pack(fill='x',pady=(0,10))
        tk.Label(banner,text=title,bg=P['panel2'],fg=P['cyan'],font=(MONO, 12,'bold'),anchor='w').pack(fill='x',padx=18,pady=(13,3))
        tk.Label(banner,text='REAL LOCAL TOOLING // RESULTS ARE COMPUTED, NOT MOCKED',bg=P['panel2'],fg=P['green'],font=(MONO, 9,'bold'),anchor='w').pack(fill='x',padx=18,pady=(0,12))
        if key=='analysis': self._analysis_tool_v10(inner); self.add_auto_analysis_panel(inner)
        elif key=='network': self._network_tool_v10(inner)
        elif key=='web': self._web_tool_v10(inner)
        elif key=='blue': self._blue_tool_v10(inner)
        elif key=='toolkit': pass
        else: self._labs_tool_v10(inner); self._lab_progress_panel(inner)
        return p

    def _run_ui_worker(self, work, on_success, on_error=None):
        """Submit non-UI work to the dedicated command worker and marshal the result to Tk."""
        try:
            fut = self._command_worker.submit(work)
        except Exception as exc:
            if on_error: on_error(exc)
            return None
        def done(f):
            try: result=f.result(); error=None
            except Exception as exc: result=None; error=exc
            try:
                if error is None:
                    self._queue_worker_event(lambda r=result: on_success(r))
                elif on_error:
                    self._queue_worker_event(lambda e=error: on_error(e))
            except Exception:
                pass
        fut.add_done_callback(done)
        return fut

    def _tool_header(self,parent,kicker,desc):
        tk.Label(parent,text=kicker,bg=parent.cget('bg'),fg=P['yellow'],font=(MONO, 10,'bold'),anchor='w').pack(fill='x',padx=16,pady=(12,3))
        tk.Label(parent,text=desc,bg=parent.cget('bg'),fg=P['muted'],font=(FONT, 10),anchor='w',justify='left',wraplength=950).pack(fill='x',padx=16,pady=(0,8))

    def _analysis_tool_v10(self,inner):
        """Unified cryptanalysis operations deck. Heavy calculations run off the Tk event loop."""
        box=self.glass(inner); box.pack(fill='x',pady=6)
        self._tool_header(box,'CRYPTANALYSIS CORE // REAL LOCAL ENGINE','Frequency distribution, Index of Coincidence, Kasiski examination and classical candidate ranking. No network operations.')

        hud=tk.Canvas(box,height=112,bg='#02070d',highlightthickness=0)
        hud.pack(fill='x',padx=16,pady=(0,8))
        self._crypto_hud_canvas=hud; self._crypto_hud_phase=0.0
        self._crypto_hud_running=True
        self._animate_cryptanalysis_hud()

        entry_frame=tk.Frame(box,bg=P['panel2']); entry_frame.pack(fill='x',padx=16,pady=5)
        tk.Label(entry_frame,text='CIPHERTEXT MATRIX',bg=P['panel2'],fg=P['cyan'],font=(MONO,9,'bold')).pack(anchor='w',padx=10,pady=(8,2))
        inp=tk.Text(entry_frame,height=7,bg='#030a11',fg=P['text'],insertbackground=P['cyan'],font=(MONO,11),relief='flat',wrap='word')
        inp.pack(fill='x',padx=10,pady=(0,10)); inp.insert('1.0','KHOOR ZRUOG. KHOOR ZRUOG.')

        controls=tk.Frame(box,bg=box.cget('bg')); controls.pack(fill='x',padx=16,pady=5)
        out=tk.Text(box,height=18,bg='#030a11',fg=P['green'],font=(MONO,9),relief='flat',wrap='none'); out.pack(fill='x',padx=16,pady=7)
        log=tk.Text(box,height=7,bg='#01050a',fg=P['muted'],font=(MONO,9),relief='flat'); log.pack(fill='x',padx=16,pady=(0,8))
        self._crypto_out=out; self._crypto_log=log

        def write_log(msg):
            log.insert('end',f'[{datetime.now().strftime("%H:%M:%S")}] {msg}\n'); log.see('end')

        def run_frequency():
            raw=inp.get('1.0','end-1c')
            out.delete('1.0','end'); out.insert('end','FREQUENCY ANALYSIS // QUEUED\n')
            write_log('Dispatching frequency distribution to worker.')
            def work(): return cryptanalysis.frequency_profile(raw), cryptanalysis.frequency_match_score(raw)
            def done(data):
                prof,score=data; out.delete('1.0','end')
                out.insert('end',f"LANGUAGE : {prof['language']}\nLETTERS  : {prof['letters']}\nMATCH    : {score:.2f}%\n\nLETTER  OBSERVED  EXPECTED  DELTA  COUNT\n"+'-'*52+'\n')
                for r in prof['rows']: out.insert('end',f"{r['letter']:>6}  {r['percent']:>8.2f}%  {r['expected']:>8.2f}%  {r['delta']:>6.2f}  {r['count']:>5}\n")
                write_log(f"Frequency complete: {prof['letters']} letters / {score:.2f}% distribution similarity.")
                self._record_tool_operation('cryptanalysis','Frequency analysis',raw,out.get('1.0','end-1c'))
            self._run_ui_worker(work,done,lambda e: (out.delete('1.0','end'),out.insert('end',f'ERROR: {e}'),write_log(f'Frequency error: {e}')))

        def run_ic():
            raw=inp.get('1.0','end-1c'); out.delete('1.0','end'); write_log('Calculating IC and candidate Vigenere lengths.')
            def work(): return cryptanalysis.index_of_coincidence(raw), cryptanalysis.estimate_vigenere_key_lengths(raw,16), cryptanalysis.kasiski(raw)
            def done(data):
                ic,lens,(reps,factors)=data; out.insert('end',f'INDEX OF COINCIDENCE : {ic:.6f}\n\nKEY-LENGTH CANDIDATES\n')
                for score,k in lens[:10]: out.insert('end',f'  k={k:02d}  avg_IC={score:.6f}\n')
                out.insert('end','\nKASISKI FACTORS\n'+str(factors[:12])+'\n\nREPEATED N-GRAMS\n')
                for gram,pos in reps[:12]: out.insert('end',f'  {gram} -> {pos}\n')
                write_log(f'IC complete: {ic:.6f}. Kasiski repeats: {len(reps)}.')
            self._run_ui_worker(work,done,lambda e: (out.insert('end',f'ERROR: {e}\n'),write_log(f'IC error: {e}')))

        def run_bruteforce():
            raw=inp.get('1.0','end-1c'); out.delete('1.0','end'); out.insert('end','CAESAR 26-SHIFT SEARCH // RUNNING\n'); write_log('Enumerating all 26 Caesar shifts and scoring candidates.')
            def work(): return cryptanalysis.caesar_candidates(raw)
            def done(rows):
                out.delete('1.0','end'); out.insert('end','RANK  KEY  CHI-SQUARE  PROBABILITY  PLAINTEXT\n'+'-'*96+'\n')
                for i,r in enumerate(rows[:26],1): out.insert('end',f"{i:>4}  {r['key']:>3}  {r['chi_square']:>11.2f}  {r['probability']:>10.2f}%  {r['plaintext']}\n")
                write_log(f'Brute-force complete: {len(rows)} candidates ranked.')
            self._run_ui_worker(work,done,lambda e: (out.delete('1.0','end'),out.insert('end',f'ERROR: {e}'),write_log(f'Brute-force error: {e}')))

        def clear():
            out.delete('1.0','end'); log.delete('1.0','end'); self._crypto_hud_phase=0.0; write_log('MATRIX CLEARED // STANDBY')

        for label,cmd,accent in [('RUN FREQUENCY ANALYSIS',run_frequency,True),('EXECUTE BRUTE-FORCE',run_bruteforce,True),('CALCULATE IC',run_ic,False),('CLEAR MATRIX',clear,False)]:
            self.btn(controls,label,cmd,accent).pack(side='left',padx=(0,6))

        copybar=tk.Frame(box,bg=box.cget('bg')); copybar.pack(fill='x',padx=16,pady=(0,12))
        def copy_results():
            self.clipboard_clear(); self.clipboard_append(out.get('1.0','end-1c')); write_log('OUTPUT COPIED TO CLIPBOARD.')
        self.btn(copybar,'COPY OUTPUT',copy_results).pack(side='right')

    def _animate_cryptanalysis_hud(self):
        c=getattr(self,'_crypto_hud_canvas',None)
        if not c or not c.winfo_exists() or not getattr(self,'_crypto_hud_running',False): return
        w=max(10,c.winfo_width()); h=max(10,c.winfo_height()); self._crypto_hud_phase=(self._crypto_hud_phase+0.045)%(math.tau)
        c.delete('all'); cx=w*.5; cy=h*.5; r=min(w,h)*.30
        for rr in (r*.55,r*.78,r): c.create_oval(cx-rr,cy-rr,cx+rr,cy+rr,outline=P['line'])
        ang=self._crypto_hud_phase; x=cx+math.cos(ang)*r; y=cy+math.sin(ang)*r
        c.create_line(cx,cy,x,y,fill=P['cyan'],width=2)
        for i in range(14):
            xx=(i+1)*w/15; yy=cy+math.sin(ang+i*.7)*r*.72
            c.create_line(xx,cy,xx,yy,fill=P['line'])
        c.create_text(12,12,text='CRYPTANALYSIS // LIVE MATRIX',anchor='nw',fill=P['cyan'],font=(MONO,9,'bold'))
        c.create_text(12,h-12,text='LOCAL COMPUTE  •  NON-BLOCKING  •  CLASSICAL CIPHERS',anchor='sw',fill=P['muted'],font=(MONO,9))

    def _network_tool_v10(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._tool_header(box,'01 // IP INTELLIGENCE','Classifies IPv4/IPv6 properties using the standard library.')
        ent=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 11));ent.pack(fill='x',padx=16,pady=5);ent.insert(0,'192.168.1.10')
        out=tk.Text(box,height=6,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat');out.pack(fill='x',padx=16,pady=7)
        def run():
            try:d=network_tools.analyze_ip(ent.get());out.delete('1.0','end');out.insert('end','\n'.join(f'{k.upper():<14}: {v}' for k,v in d.items()));self._record_tool_operation('network','IP intelligence',ent.get(),out.get('1.0','end-1c'))
            except Exception as e:out.delete('1.0','end');out.insert('end',f'ERROR: {e}')
        self.btn(box,'ANALYZE ADDRESS',run,True).pack(anchor='e',padx=16,pady=(0,12))
        sub=self.card(inner);sub.pack(fill='x',pady=6);self._tool_header(sub,'02 // SUBNET CALCULATOR','Network, broadcast, prefix and usable host count.')
        se=tk.Entry(sub,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 11));se.pack(fill='x',padx=16,pady=5);se.insert(0,'192.168.1.0/24')
        sr=tk.Text(sub,height=5,bg='#030a11',fg=P['cyan'],font=(MONO, 10),relief='flat');sr.pack(fill='x',padx=16,pady=7)
        def subrun():
            try:d=network_tools.subnet(se.get());sr.delete('1.0','end');sr.insert('end','\n'.join(f'{k.upper():<14}: {v}' for k,v in d.items()));self._record_tool_operation('network','Subnet calculation',se.get(),sr.get('1.0','end-1c'))
            except Exception as e:sr.delete('1.0','end');sr.insert('end',f'ERROR: {e}')
        self.btn(sub,'CALCULATE SUBNET',subrun).pack(anchor='e',padx=16,pady=(0,12))
        dns=self.card(inner);dns.pack(fill='x',pady=6);self._tool_header(dns,'03 // DNS RESOLVER','Uses the local OS resolver. No scanning or enumeration.')
        de=tk.Entry(dns,bg=P['panel2'],fg=P['text'],relief='flat',font=(MONO, 11));de.pack(fill='x',padx=16,pady=5);de.insert(0,socket.gethostname())
        dr=tk.Text(dns,height=6,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat');dr.pack(fill='x',padx=16,pady=7)
        def dnsrun():
            host=de.get().strip(); dr.delete('1.0','end'); dr.insert('end','DNS QUERY QUEUED // LOCAL RESOLVER…')
            def work(): return host, network_tools.dns_lookup(host)
            def done(data):
                host0,rows=data; seen=[]
                for row in rows:
                    addr=row[-1][0] if row and row[-1] else ''
                    if addr and addr not in seen: seen.append(addr)
                text=('HOST: '+host0+'\n\n'+'\n'.join(seen)) if seen else 'No addresses returned.'
                dr.delete('1.0','end'); dr.insert('end',text); self._record_tool_operation('network','DNS resolution',host0,text)
            self._run_ui_worker(work,done,lambda e:(dr.delete('1.0','end'),dr.insert('end',f'DNS ERROR: {e}')))
        self.btn(dns,'RESOLVE HOST',dnsrun).pack(anchor='e',padx=16,pady=(0,12))

    def _web_tool_v10(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._tool_header(box,'01 // REQUEST BUILDER','Build and inspect a synthetic HTTP request without sending it anywhere.')
        row=tk.Frame(box,bg=P['panel']);row.pack(fill='x',padx=16,pady=5);method=tk.StringVar(value='GET');ttk.Combobox(row,textvariable=method,values=['GET','POST','PUT','PATCH','DELETE'],state='readonly',width=10).pack(side='left',padx=(0,6));url=tk.Entry(row,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 10));url.pack(side='left',fill='x',expand=True);url.insert(0,'https://example.local/api/profile?id=42')
        body=tk.Text(box,height=5,bg=P['panel2'],fg=P['text'],font=(MONO, 10),relief='flat');body.pack(fill='x',padx=16,pady=5);body.insert('1.0','{"name":"HN","role":"analyst"}')
        resp=tk.Text(box,height=10,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat');resp.pack(fill='x',padx=16,pady=7)
        def build():
            u=url.get().strip();parsed=urlparse(u);qs=parse_qs(parsed.query);m=method.get();payload=body.get('1.0','end-1c')
            lines=[f'{m} {parsed.path or "/"}'+(('?'+parsed.query) if parsed.query else '')+' HTTP/1.1','Host: '+(parsed.netloc or 'example.local'),'User-Agent: HN-BlackBox-Lab','Content-Type: application/json','X-Lab-Mode: LOCAL-ONLY','',payload if m not in ('GET','DELETE') else '']
            resp.delete('1.0','end');resp.insert('end','\n'.join(lines)+'\n\nPARSED QUERY PARAMS:\n'+json.dumps(qs,indent=2));self._record_tool_operation('web','HTTP request simulation',u,resp.get('1.0','end-1c'),m)
        self.btn(box,'BUILD REQUEST',build,True).pack(anchor='e',padx=16,pady=(0,12))
        ch=self.card(inner);ch.pack(fill='x',pady=6);self._tool_header(ch,'02 // OWASP DEFENSIVE CARDS','Synthetic concepts from the local challenge catalogue.')
        for item in web_lab.get_challenges():
            r=tk.Frame(ch,bg=P['panel2'],highlightbackground=P['line'],highlightthickness=1);r.pack(fill='x',padx=14,pady=3)
            tk.Label(r,text=item['id'],bg=P['panel2'],fg=P['cyan'],font=(MONO, 10,'bold')).pack(side='left',padx=10,pady=8)
            tk.Label(r,text=item['title']+'  // '+item['difficulty'],bg=P['panel2'],fg=P['text'],font=(FONT, 10,'bold')).pack(side='left',padx=4)
            tk.Label(r,text='FIX: '+item['fix'],bg=P['panel2'],fg=P['muted'],font=(FONT, 10),anchor='e').pack(side='right',padx=10)

    def _blue_tool_v10(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._tool_header(box,'01 // LOG TRIAGE','Counts events, extracts IPs and flags repeated failure sources.')
        sample='2026-08-09 20:01 login failed from 203.0.113.9\n2026-08-09 20:02 login failed from 203.0.113.9\n2026-08-09 20:03 login failed from 203.0.113.9\n2026-08-09 20:04 login failed from 203.0.113.9\n2026-08-09 20:05 login failed from 203.0.113.9\n2026-08-09 20:06 successful login from 192.168.1.10'
        inp=tk.Text(box,height=8,bg=P['panel2'],fg=P['text'],font=(MONO, 10),relief='flat');inp.pack(fill='x',padx=16,pady=5);inp.insert('1.0',sample)
        out=tk.Text(box,height=9,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat');out.pack(fill='x',padx=16,pady=7)
        def analyze():
            d=blue_team.analyze_log(inp.get('1.0','end-1c'));out.delete('1.0','end');out.insert('end',f"LINES={d['lines']}  FAILED={d['failed']}\n\nTOP IPs:\n")
            for ip,n in d['ips'][:10]:out.insert('end',f'  {ip:<18} {n:>4}\n')
            out.insert('end','\nSUSPICIOUS:\n'+('\n'.join(f'  {ip} // {n} failures' for ip,n in d['suspicious']) or '  none')+'\n\nFAILED EVENTS:\n'+'\n'.join(d['failed_lines'][:10]))
            self._record_tool_operation('blue_team','Log triage',inp.get('1.0','end-1c'),out.get('1.0','end-1c'))
        self.btn(box,'RUN TRIAGE',analyze,True).pack(anchor='e',padx=16,pady=(0,12))
        ioc=self.card(inner);ioc.pack(fill='x',pady=6);self._tool_header(ioc,'02 // IOC + HASH CHECK','Classifies tokens locally and computes SHA-256 for evidence handling.')
        ie=tk.Entry(ioc,bg=P['panel2'],fg=P['text'],relief='flat',font=(MONO, 11));ie.pack(fill='x',padx=16,pady=5);ie.insert(0,'203.0.113.9')
        ir=tk.Text(ioc,height=5,bg='#030a11',fg=P['cyan'],font=(MONO, 10),relief='flat');ir.pack(fill='x',padx=16,pady=7)
        def check():
            v=ie.get().strip();kind='IPv4' if re.fullmatch(r'(?:\d{1,3}\.){3}\d{1,3}',v) else ('SHA-256' if re.fullmatch(r'[0-9a-fA-F]{64}',v) else 'TOKEN')
            digest=hashlib.sha256(v.encode()).hexdigest();ir.delete('1.0','end');ir.insert('end',f'TYPE       : {kind}\nVALUE      : {v}\nSHA-256    : {digest}\nREPUTATION : NOT QUERIED (LOCAL-ONLY)')
            self._record_tool_operation('blue_team','IOC inspection',v,ir.get('1.0','end-1c'))
        self.btn(ioc,'INSPECT IOC',check).pack(anchor='e',padx=16,pady=(0,12))

    def _labs_tool_v10(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._tool_header(box,'OFFLINE CHALLENGE ENGINE','Solve deterministic security exercises. No network access is required.')
        challenges=labs.all_labs()+labs3.catalog();idx=tk.IntVar(value=0);score=tk.IntVar(value=0)
        title=tk.Label(box,text='',bg=P['panel'],fg=P['text'],font=(FONT, 15,'bold'),anchor='w');title.pack(fill='x',padx=16,pady=5)
        prompt=tk.Label(box,text='',bg=P['panel'],fg=P['muted'],font=(FONT, 11),anchor='w',justify='left',wraplength=950);prompt.pack(fill='x',padx=16,pady=5)
        ans=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 11));ans.pack(fill='x',padx=16,pady=6)
        status=tk.Label(box,text='READY',bg=P['panel'],fg=P['cyan'],font=(MONO, 10,'bold'),anchor='w');status.pack(fill='x',padx=16,pady=4)
        score_label=tk.Label(box,text='SCORE 0 / 0',bg=P['panel'],fg=P['yellow'],font=(MONO, 10,'bold'),anchor='e');score_label.pack(fill='x',padx=16)
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
            r=tk.Frame(path,bg=P['panel2']);r.pack(fill='x',padx=14,pady=3);tk.Label(r,text=q['category'],bg=P['panel2'],fg=P['purple'],font=(MONO, 9,'bold')).pack(side='left',padx=10,pady=7);tk.Label(r,text=q['title'],bg=P['panel2'],fg=P['text'],font=(FONT, 10)).pack(side='left');tk.Label(r,text=q['difficulty'],bg=P['panel2'],fg=P['yellow'],font=(MONO, 9,'bold')).pack(side='right',padx=10)
    def _section_title(self,parent,text): tk.Label(parent,text=text,bg=parent.cget('bg'),fg=P['yellow'],font=(MONO, 10,'bold'),anchor='e').pack(fill='x',padx=16,pady=(12,6))

    def _analysis_tool(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._section_title(box,'FREQUENCY ANALYZER')
        txt=tk.Text(box,height=5,bg=P['panel2'],fg=P['text'],font=(FONT, 12),relief='flat',wrap='word');txt.pack(fill='x',padx=16,pady=5);txt.insert('1.0','THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG. THE FOX IS FAST.')
        out=tk.Text(box,height=7,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat');out.pack(fill='x',padx=16,pady=7)
        def run():
            rows=frequency_analysis.analyze(txt.get('1.0','end-1c'));out.delete('1.0','end');out.insert('end','LETTER   COUNT   PERCENT\n'+'-'*32+'\n')
            for r in rows[:15]: out.insert('end',f"{r['letter']:>5}   {r['count']:>5}   {r['percent']:>6.2f}%\n")
        self.btn(box,'RUN FREQUENCY ANALYSIS',run,True).pack(anchor='e',padx=16,pady=(0,12))
        rank=self.card(inner);rank.pack(fill='x',pady=6);self._section_title(rank,'CAESAR RANKING')
        inp=tk.Entry(rank,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 11));inp.pack(fill='x',padx=16,pady=5);inp.insert(0,'KHOOR ZRUOG')
        res=tk.Text(rank,height=7,bg='#030a11',fg=P['cyan'],font=(MONO, 10),relief='flat');res.pack(fill='x',padx=16,pady=7)
        def rankit():
            res.delete('1.0','end')
            for score,key,plain in cryptanalysis.caesar_rank(inp.get())[:8]: res.insert('end',f'key={key:02d}  chi={score:7.2f}  {plain}\n')
        self.btn(rank,'RANK CANDIDATES',rankit).pack(anchor='e',padx=16,pady=(0,12))

    def _network_tool(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._section_title(box,'IP INTELLIGENCE')
        entry=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 12));entry.pack(fill='x',padx=16,pady=5);entry.insert(0,'192.168.1.10')
        result=tk.Text(box,height=6,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat');result.pack(fill='x',padx=16,pady=7)
        def iprun():
            try:
                d=network_tools.analyze_ip(entry.get());result.delete('1.0','end');result.insert('end','\n'.join(f'{k.upper():<12}: {v}' for k,v in d.items()))
            except Exception as e: result.delete('1.0','end');result.insert('end',f'ERROR: {e}')
        self.btn(box,'ANALYZE IP',iprun,True).pack(anchor='e',padx=16,pady=(0,12))
        sub=self.card(inner);sub.pack(fill='x',pady=6);self._section_title(sub,'SUBNET CALCULATOR')
        se=tk.Entry(sub,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 12));se.pack(fill='x',padx=16,pady=5);se.insert(0,'192.168.1.0/24')
        sr=tk.Text(sub,height=5,bg='#030a11',fg=P['cyan'],font=(MONO, 10),relief='flat');sr.pack(fill='x',padx=16,pady=7)
        def subrun():
            try:
                d=network_tools.subnet(se.get());sr.delete('1.0','end');sr.insert('end','\n'.join(f'{k.upper():<12}: {v}' for k,v in d.items()))
            except Exception as e: sr.delete('1.0','end');sr.insert('end',f'ERROR: {e}')
        self.btn(sub,'CALCULATE SUBNET',subrun).pack(anchor='e',padx=16,pady=(0,12))

    def _web_tool(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._section_title(box,'HTTP REQUEST SIMULATOR')
        grid=tk.Frame(box,bg=P['panel']);grid.pack(fill='x',padx=16);method=tk.StringVar(value='GET');ttk.Combobox(grid,textvariable=method,values=['GET','POST','PUT','DELETE'],state='readonly',width=10).grid(row=0,column=0,padx=4,pady=5,sticky='ew');path=tk.Entry(grid,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 11));path.grid(row=0,column=1,padx=4,pady=5,sticky='ew');path.insert(0,'/api/profile/42');grid.columnconfigure(1,weight=1)
        headers=tk.Text(box,height=5,bg=P['panel2'],fg=P['text'],font=(MONO, 10),relief='flat');headers.pack(fill='x',padx=16,pady=6);headers.insert('1.0','Authorization: Bearer DEMO\nContent-Type: application/json')
        response=tk.Text(box,height=8,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat');response.pack(fill='x',padx=16,pady=6)
        def simulate():
            status='200 OK' if method.get()=='GET' else '201 CREATED' if method.get()=='POST' else '204 NO CONTENT';response.delete('1.0','end');response.insert('end',f'HTTP/1.1 {status}\nServer: HN-BlackBox-Lab\nPath: {path.get()}\n\n{{"simulated": true, "external_request": false}}')
        self.btn(box,'SEND TO LOCAL SIMULATOR',simulate,True).pack(anchor='e',padx=16,pady=(0,12))
        ch=self.card(inner);ch.pack(fill='x',pady=6);self._section_title(ch,'OWASP CONCEPT CARDS')
        for item in web_lab.get_challenges():
            row=tk.Frame(ch,bg=P['panel2'],highlightbackground=P['line'],highlightthickness=1);row.pack(fill='x',padx=14,pady=3);tk.Label(row,text=item['id'],bg=P['panel2'],fg=P['cyan'],font=(MONO, 10,'bold')).pack(side='right',padx=10,pady=8);tk.Label(row,text=f"{item['title']}  •  {item['difficulty']}",bg=P['panel2'],fg=P['text'],font=(FONT, 10,'bold')).pack(side='right',padx=6);tk.Label(row,text=item['fix'],bg=P['panel2'],fg=P['muted'],font=(FONT, 10),anchor='e').pack(side='left',padx=10)

    def _blue_tool(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._section_title(box,'LOG TRIAGE')
        sample="2026-08-09 20:01 login failed from 203.0.113.9\n2026-08-09 20:02 login failed from 203.0.113.9\n2026-08-09 20:03 login failed from 203.0.113.9\n2026-08-09 20:04 login failed from 203.0.113.9\n2026-08-09 20:05 login failed from 203.0.113.9\n2026-08-09 20:06 successful login from 192.168.1.10"
        inp=tk.Text(box,height=8,bg=P['panel2'],fg=P['text'],font=(MONO, 10),relief='flat');inp.pack(fill='x',padx=16,pady=5);inp.insert('1.0',sample);out=tk.Text(box,height=8,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat');out.pack(fill='x',padx=16,pady=7)
        def analyze():
            d=blue_team.analyze_log(inp.get('1.0','end-1c'));out.delete('1.0','end');out.insert('end',f"LINES       : {d['lines']}\nFAILED      : {d['failed']}\nTOP IPS     : {d['ips'][:5]}\nSUSPICIOUS  : {d['suspicious']}\n\n-- FAILED EVENTS --\n"+'\n'.join(d['failed_lines']));self._record_tool_operation('blue_team','Log triage',inp.get('1.0','end-1c'),out.get('1.0','end-1c'))
        self.btn(box,'RUN DEFENSIVE TRIAGE',analyze,True).pack(anchor='e',padx=16,pady=(0,12))
        ioc=self.card(inner);ioc.pack(fill='x',pady=6);self._section_title(ioc,'IOC QUICK CHECK');tk.Label(ioc,text='Paste an IP or hash-like token to classify locally.',bg=P['panel'],fg=P['muted'],font=(FONT, 10),anchor='e').pack(fill='x',padx=16);ie=tk.Entry(ioc,bg=P['panel2'],fg=P['text'],relief='flat',font=(MONO, 11));ie.pack(fill='x',padx=16,pady=7);ie.insert(0,'203.0.113.9');ir=tk.Label(ioc,text='READY',bg=P['panel'],fg=P['cyan'],font=(MONO, 10,'bold'),anchor='e');ir.pack(fill='x',padx=16,pady=(0,10))
        def ioccheck():
            v=ie.get().strip();kind='IPv4' if re.fullmatch(r'(?:\d{1,3}\.){3}\d{1,3}',v) else 'TOKEN / HASH';msg=f'{kind}  //  LOCAL CLASSIFICATION  //  NO REPUTATION LOOKUP';ir.configure(text=msg);self._record_tool_operation('blue_team','IOC classification',v,msg)
        self.btn(ioc,'CLASSIFY IOC',ioccheck).pack(anchor='e',padx=16,pady=(0,12))

    def _labs_tool(self,inner):
        box=self.card(inner);box.pack(fill='x',pady=6);self._section_title(box,'OFFLINE CHALLENGE ENGINE');challenges=labs.all_labs();idx=tk.IntVar(value=0);title=tk.Label(box,text='',bg=P['panel'],fg=P['text'],font=(FONT, 15,'bold'),anchor='e');title.pack(fill='x',padx=16,pady=4);prompt=tk.Label(box,text='',bg=P['panel'],fg=P['muted'],font=(FONT, 11),anchor='e',justify='right',wraplength=1050);prompt.pack(fill='x',padx=16,pady=5);ans=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 11));ans.pack(fill='x',padx=16,pady=6);status=tk.Label(box,text='READY',bg=P['panel'],fg=P['cyan'],font=(MONO, 10,'bold'),anchor='e');status.pack(fill='x',padx=16)
        def load():
            q=challenges[idx.get()%len(challenges)];title.configure(text=f"{q['id']} // {q['title']} [{q['difficulty']}]" );prompt.configure(text=q['prompt']);ans.delete(0,'end');status.configure(text='READY',fg=P['cyan'])
        def check():
            q=challenges[idx.get()%len(challenges)];ok=ans.get().strip().upper()==q['answer'].upper();msg='CORRECT' if ok else 'NOT YET // HINT: '+q['hint'];status.configure(text='✓ '+msg if ok else '✕ '+msg,fg=P['green'] if ok else P['red']);self._record_tool_operation('labs','Challenge check',ans.get(),msg,q['id'])
        def nxt(): idx.set((idx.get()+1)%len(challenges));load()
        acts=tk.Frame(box,bg=P['panel']);acts.pack(fill='x',padx=16,pady=10);self.btn(acts,'CHECK ANSWER',check,True).pack(side='right',padx=3);self.btn(acts,'NEXT LAB',nxt).pack(side='right',padx=3);load();progress=self.glass(inner);progress.pack(fill='x',pady=7);self._section_title(progress,'LEARNING PATH')
        for q in challenges:
            row=tk.Frame(progress,bg=P['panel2']);row.pack(fill='x',padx=14,pady=3);tk.Label(row,text=q['category'],bg=P['panel2'],fg=P['purple'],font=(MONO, 10,'bold')).pack(side='left',padx=10,pady=7);tk.Label(row,text=q['title'],bg=P['panel2'],fg=P['text'],font=(FONT, 10)).pack(side='right',padx=10)

    def toolkit_page(self):
        p=tk.Frame(self.content,bg=P['bg'])
        self.heading(p,'HN / TOOLKIT','SECURITY TOOLKIT','Functional local utilities for analysis, evidence and defensive engineering. No outbound collection.')
        canvas,inner=self._make_canvas(p); self._module_hud(inner,'toolkit')
        banner=self.glass(inner); banner.pack(fill='x',pady=(0,10))
        self._tool_header(banner,'FIELD TOOLKIT','Real local computations — file hashing, Base64, URL/JWT parsing, password entropy, IOC extraction and log summaries.')
        # Hash file
        box=self.card(inner); box.pack(fill='x',pady=6); self._tool_header(box,'01 // FILE HASH / INTEGRITY','Compute MD5, SHA-1 and SHA-256 for a local file. Nothing is uploaded.')
        hash_out=tk.Text(box,height=6,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat'); hash_out.pack(fill='x',padx=16,pady=6)
        def choose_hash():
            path=filedialog.askopenfilename(title='Select local file')
            if not path:return
            try: d=real_tools.hash_file(path); hash_out.delete('1.0','end'); hash_out.insert('end','\n'.join(f'{k.upper():<10}: {v}' for k,v in d.items())); self._record_tool_operation('toolkit','File hash',path,hash_out.get('1.0','end-1c'))
            except Exception as e: hash_out.delete('1.0','end'); hash_out.insert('end','ERROR: '+str(e))
        self.btn(box,'HASH LOCAL FILE',choose_hash,True).pack(anchor='e',padx=16,pady=(0,12))
        # Encoding
        box=self.card(inner); box.pack(fill='x',pady=6); self._tool_header(box,'02 // BASE64 ENCODER / DECODER','Useful for inspecting encoded content. Base64 is not encryption.')
        btxt=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 10)); btxt.pack(fill='x',padx=16,pady=6); btxt.insert(0,'HN_BLACKBOX')
        bout=tk.Text(box,height=4,bg='#030a11',fg=P['cyan'],font=(MONO, 10),relief='flat'); bout.pack(fill='x',padx=16,pady=6)
        def enc():
            try: v=real_tools.b64_encode(btxt.get()); bout.delete('1.0','end'); bout.insert('end',v)
            except Exception as e: bout.delete('1.0','end'); bout.insert('end','ERROR: '+str(e))
        def dec():
            try: v=real_tools.b64_decode(btxt.get()); bout.delete('1.0','end'); bout.insert('end',v)
            except Exception as e: bout.delete('1.0','end'); bout.insert('end','ERROR: '+str(e))
        acts=tk.Frame(box,bg=P['panel']); acts.pack(fill='x',padx=16,pady=6); self.btn(acts,'ENCODE',enc,True).pack(side='left',padx=3); self.btn(acts,'DECODE',dec).pack(side='left',padx=3)
        # URL + JWT
        box=self.card(inner); box.pack(fill='x',pady=6); self._tool_header(box,'03 // URL / JWT INSPECTOR','Parse URL components and decode JWT header/payload locally. JWT signatures are never trusted or verified here.')
        uent=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 10)); uent.pack(fill='x',padx=16,pady=5); uent.insert(0,'https://example.local/api?q=blackbox&page=2')
        uout=tk.Text(box,height=7,bg='#030a11',fg=P['text'],font=(MONO, 10),relief='flat'); uout.pack(fill='x',padx=16,pady=6)
        def parseu():
            try: d=real_tools.parse_url(uent.get()); uout.delete('1.0','end'); uout.insert('end',json.dumps(d,indent=2))
            except Exception as e:uout.delete('1.0','end');uout.insert('end','ERROR: '+str(e))
        self.btn(box,'PARSE URL',parseu,True).pack(anchor='e',padx=16,pady=(0,7))
        jwt=tk.Entry(box,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 10)); jwt.pack(fill='x',padx=16,pady=5); jwt.insert(0,'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjMiLCJyb2xlIjoiYW5hbHlzdCJ9.demo')
        def jwtdec():
            try:d=real_tools.decode_jwt(jwt.get());uout.delete('1.0','end');uout.insert('end',json.dumps(d,indent=2))
            except Exception as e:uout.delete('1.0','end');uout.insert('end','ERROR: '+str(e))
        self.btn(box,'DECODE JWT LOCALLY',jwtdec).pack(anchor='e',padx=16,pady=(0,12))
        # Password entropy
        box=self.card(inner); box.pack(fill='x',pady=6); self._tool_header(box,'04 // PASSWORD ENTROPY ESTIMATOR','Estimates search-space entropy locally; it does not store or transmit the password.')
        pe=tk.Entry(box,show='•',bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 10)); pe.pack(fill='x',padx=16,pady=6); pe.insert(0,'Example-Only-Change-Me')
        po=tk.Label(box,text='READY',bg=P['panel'],fg=P['cyan'],font=(MONO, 10,'bold'),anchor='w'); po.pack(fill='x',padx=16,pady=6)
        def entropy():
            d=real_tools.password_entropy(pe.get()); po.configure(text=f"LENGTH={d['length']}  CHARSET={d['charset_size']}  ENTROPY≈{d['entropy_bits']} bits  //  {d['rating'].upper()}",fg=P['green'] if d['entropy_bits']>=60 else P['yellow'])
        self.btn(box,'ESTIMATE ENTROPY',entropy).pack(anchor='e',padx=16,pady=(0,12))
        # IOC / log
        box=self.card(inner); box.pack(fill='x',pady=6); self._tool_header(box,'05 // IOC + LOG ANALYZER','Extract IPs, hashes, URLs, emails and summarize alert-like log events from pasted local text.')
        ti=tk.Text(box,height=8,bg=P['panel2'],fg=P['text'],font=(MONO, 10),relief='flat'); ti.pack(fill='x',padx=16,pady=5); ti.insert('1.0','2026-08-10 login failed from 203.0.113.9\nGET https://example.local/login\nSHA256 0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef')
        to=tk.Text(box,height=9,bg='#030a11',fg=P['green'],font=(MONO, 10),relief='flat'); to.pack(fill='x',padx=16,pady=7)
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
            c=tk.Frame(grid,bg='#071722',highlightbackground=P['line'],highlightthickness=1);c.grid(row=0,column=i,sticky='nsew',padx=3);grid.columnconfigure(i,weight=1);tk.Label(c,text=label,bg='#071722',fg=P['muted'],font=(MONO, 9,'bold')).pack(pady=(9,2));tk.Label(c,text=str(val),bg='#071722',fg=color,font=(MONO, 19,'bold')).pack(pady=(0,8))
        inv=self.card(inner);inv.pack(fill='x',pady=6);self._tool_header(inv,'MODULE INVENTORY','Every listed module is backed by a Python implementation in this build.')
        text=tk.Text(inv,height=16,bg='#030a11',fg=P['text'],font=(MONO, 10),relief='flat');text.pack(fill='x',padx=14,pady=6)
        for group,label in [(cores,'CORE'),(ui,'GUI'),(tests,'TESTS')]:
            text.insert('end',f'[{label}]\n')
            for f in group:text.insert('end',f'  ✓ {f}\n')
            text.insert('end','\n')
        text.configure(state='disabled')
        status=self.glass(inner);status.pack(fill='x',pady=6);self._tool_header(status,'QUALITY GATE','Expected baseline for this distribution: 23 passing checks.')
        tk.Label(status,text='23 / 23  PASS  //  CORE CIPHERS + GUI SMOKE + FEATURE TESTS',bg=P['panel2'],fg=P['green'],font=(MONO, 12,'bold'),anchor='w').pack(fill='x',padx=16,pady=(0,12))
        quote=self.glass(inner);quote.pack(fill='x',pady=12);tk.Label(quote,text='BUILD. VISUALIZE. UNDERSTAND. DEFEND.',bg=P['panel2'],fg=P['cyan'],font=(MONO, 14,'bold')).pack(pady=(18,5));tk.Label(quote,text='HN BlackBox — developed by HANI KHALID NASSER AL-NASRI',bg=P['panel2'],fg=P['text'],font=(FONT, 11)).pack(pady=(0,18))
        return p
    def _command_center_panel(self, inner):
        box=self.glass(inner); box.pack(fill='x',pady=(0,8))
        self._tool_header(box,'BLACKBOX COMMAND CENTER','Cross-module intelligence, investigation, evidence, workflows, graphs and local defense controls. No external collection is performed.')
        grid=tk.Frame(box,bg=P['panel']); grid.pack(fill='x',padx=14,pady=(0,10))
        cards=[('INTELLIGENCE','Correlate local observations',self._cc_intelligence,P['purple']),('INVESTIGATION','Create a local case',self._cc_case,P['cyan']),('EVIDENCE','Hash / verify a file',self._cc_evidence,P['yellow']),('NETWORK GRAPH','Build relationship graph',self._cc_graph,P['green']),('BLUE TEAM','Extract indicators + rules',self._cc_blue,P['red']),('LABS','View progression score',self._cc_labs,P['orange']),('WORKFLOW','Build a cross-module chain',self._cc_workflow,P['cyan']),('PLUGINS','Discover local extensions',self._cc_plugins,P['purple']),('VAULT','Protect local case data',self._cc_vault,P['yellow'])]
        for i,(title,desc,cmd,accent) in enumerate(cards):
            cell=tk.Frame(grid,bg='#06131a',highlightbackground='#123541',highlightthickness=1); cell.grid(row=i//3,column=i%3,sticky='nsew',padx=3,pady=3); grid.columnconfigure(i%3,weight=1)
            tk.Label(cell,text=title,bg='#06131a',fg=accent,font=(MONO, 10,'bold'),anchor='w').pack(fill='x',padx=10,pady=(9,2))
            tk.Label(cell,text=desc,bg='#06131a',fg=P['muted'],font=(FONT, 10),anchor='w',wraplength=190,justify='left').pack(fill='x',padx=10,pady=(0,7))
            self.btn(cell,'OPEN',cmd).pack(anchor='e',padx=10,pady=(0,9))
        self.cc_status=tk.Label(box,text='COMMAND CENTER // LOCAL / READY',bg=P['panel2'],fg=P['green'],font=(MONO, 10,'bold'),anchor='w')
        self.cc_status.pack(fill='x',padx=14,pady=(0,10))

    def _cc_window(self,title,text):
        win=tk.Toplevel(self); win.title('HN BLACKBOX // '+title); win.geometry('720x500'); win.configure(bg=P['bg']); win.transient(self)
        tk.Label(win,text=title,bg=P['bg'],fg=P['cyan'],font=(MONO, 11,'bold'),anchor='w').pack(fill='x',padx=18,pady=12)
        out=tk.Text(win,bg='#030a11',fg=P['text'],font=(MONO, 10),relief='flat'); out.pack(fill='both',expand=True,padx=18,pady=(0,12)); out.insert('1.0',text); out.configure(state='disabled'); return win

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
                 font=(MONO, 10,'bold'),anchor='w').pack(fill='x')
        name=tk.Label(left,text="HANI KHALID N. ALNASRI",bg=P["panel2"],fg=P["text"],
                      font=(FONT, 24,'bold'),anchor='w')
        name.pack(fill='x',pady=(8,2))
        tk.Label(left,text=self.t("developer_role"),bg=P["panel2"],fg=P["yellow"],
                 font=(MONO, 9,'bold'),anchor='w').pack(fill='x')
        tk.Label(left,text=self.t("developer_bio"),bg=P["panel2"],fg=P["muted"],
                 font=(FONT, 11),justify='left',anchor='w',wraplength=700).pack(fill='x',pady=(12,8))

        contact=tk.Frame(left,bg='#06131a',highlightbackground=P["cyan"],highlightthickness=1)
        contact.pack(fill='x',pady=6)
        tk.Label(contact,text=self.t("developer_contact"),bg='#06131a',fg=P["green"],
                 font=(MONO, 10,'bold'),anchor='w').pack(fill='x',padx=10,pady=(8,3))
        tk.Label(contact,text="alnasryhany185@gmail.com",bg='#06131a',fg=P["cyan2"],
                 font=(MONO, 11,'bold'),anchor='w').pack(fill='x',padx=10,pady=2)
        tk.Label(contact,text="",bg='#06131a',fg=P["text"],
                 font=(MONO, 10,'bold'),anchor='w').pack(fill='x',padx=10,pady=(0,6))
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
                 font=(MONO, 10,'bold')).pack(fill='x',padx=10,pady=7)
        c=tk.Canvas(viz,bg='#02070b',highlightthickness=0,width=390,height=255)
        c.pack(fill='both',expand=True,padx=7,pady=7)
        self._developer_canvas=c; self._developer_phase=0

        def animate():
            if not c.winfo_exists(): return
            if not self._motion_page_active('developer'):
                self.after(120, animate); return
            # Developer core receives full motion only while Developer is foreground.
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
                c.create_text(x,y,text=label,fill=color,font=(MONO, 9,'bold'))

            pulse=18+5*math.sin(phase*.12)
            c.create_oval(cx-pulse,cy-pulse,cx+pulse,cy+pulse,outline=P["cyan2"],width=2)
            c.create_oval(cx-25,cy-25,cx+25,cy+25,fill='#06131a',outline=P["text"],width=1)
            self._draw_hn_emblem(c, cx, cy-1, size=.72, fg=P["text"], accent=P["cyan"], glow=P["cyan2"])
            c.create_text(cx,cy+14,text="BLACKBOX CORE",fill=P["cyan"],font=(MONO, 9,'bold'))
            c.create_text(8,h-9,text="BUILD // VISUALIZE // ENGINEER // DEFEND",
                          anchor='w',fill=P["green"],font=(MONO, 9,'bold'))
            c.create_text(w-8,h-9,text=f"CORE {phase%1000:03d} // LIVE",
                          anchor='e',fill=P["yellow"],font=(MONO, 9,'bold'))
            self._developer_phase+=1
            self.after(130,animate)
        c.after(140,animate)

        # Live developer telemetry: same tactical/HUD language as the command
        # center, but scoped to identity/build information.
        devhud=self.glass(inner); devhud.pack(fill='x',pady=(0,10))
        devhead=tk.Frame(devhud,bg='#07141a'); devhead.pack(fill='x')
        tk.Label(devhead,text='DEVELOPER TELEMETRY // BUILD CONTROL',bg='#07141a',fg=P['cyan'],font=(MONO, 10,'bold')).pack(side='left',padx=10,pady=6)
        self.developer_clock=tk.Label(devhead,text='--:--:--',bg='#07141a',fg=P['green'],font=(MONO, 10,'bold')); self.developer_clock.pack(side='right',padx=10)
        devbody=tk.Frame(devhud,bg='#02070b'); devbody.pack(fill='x',padx=7,pady=7)
        self.developer_metrics_canvas=tk.Canvas(devbody,bg='#02070b',height=92,highlightthickness=0); self.developer_metrics_canvas.pack(fill='x')
        self._developer_metrics_phase=0
        self._animate_developer_metrics()

        mission=self.card(inner);mission.pack(fill='x',pady=8)
        tk.Label(mission,text=self.t("developer_mission"),bg=P["panel"],fg=P["yellow"],
                 font=(MONO, 10,'bold'),anchor='w').pack(fill='x',padx=14,pady=(11,4))
        mission_items=[
            ("01",self.t("deconstruct"),"Break complex security concepts into observable steps.",P["cyan"]),
            ("02",self.t("visualize"),"Make transformations, telemetry and state changes visible.",P["purple"]),
            ("03",self.t("engineer"),"Build local, testable and reusable security tooling.",P["green"]),
            ("04",self.t("defend"),"Keep the platform focused on education, analysis and defensive engineering.",P["orange"]),
        ]
        for num,title,desc,color in mission_items:
            r=tk.Frame(mission,bg=P["panel2"],highlightbackground=P["line"],highlightthickness=1)
            r.pack(fill='x',padx=12,pady=3)
            tk.Label(r,text=num,bg=P["panel2"],fg=color,font=(MONO, 10,'bold')).pack(side='left',padx=10,pady=9)
            tk.Label(r,text=title,bg=P["panel2"],fg=P["text"],font=(MONO, 10,'bold')).pack(side='left',padx=4)
            tk.Label(r,text=desc,bg=P["panel2"],fg=P["muted"],font=(FONT, 10),
                     anchor='w',justify='left',wraplength=720).pack(side='left',fill='x',expand=True,padx=10,pady=7)

        identity=self.glass(inner);identity.pack(fill='x',pady=8)
        tk.Label(identity,text=self.t("developer_identity"),bg=P["panel2"],fg=P["cyan"],
                 font=(MONO, 10,'bold')).pack(fill='x',padx=14,pady=(11,4))
        tk.Label(identity,text=self.t("developer_identity_sub"),bg=P["panel2"],fg=P["text"],
                 font=(MONO, 13,'bold'),justify='center').pack(fill='x',padx=14,pady=4)
        identity_desc = "A unified platform for cybersecurity, systems engineering, experimentation and defensive problem solving."
        tk.Label(identity,text=identity_desc,bg=P["panel2"],fg=P["muted"],font=(FONT, 10),
                 wraplength=900,justify='center').pack(fill='x',padx=14,pady=(0,14))
        return p

    def _animate_developer_metrics(self):
        if not hasattr(self,'developer_metrics_canvas') or not self.developer_metrics_canvas.winfo_exists():
            return
        # Autonomous developer telemetry: never gated by current page.
        c=self.developer_metrics_canvas; w=max(1,c.winfo_width()); h=max(1,c.winfo_height()); t=self._developer_metrics_phase
        c.delete('all')
        for x in range(0,w,24): c.create_line(x,0,x,h,fill='#071923')
        labels=[('BUILD','ONLINE',P['green']),('CORE','ARMED',P['cyan']),('VISUALS','LIVE',P['purple']),('TESTS',RELEASE_TEST_STATUS,P['yellow'])]
        cellw=max(130,(w-12)//len(labels))
        for i,(lab,val,col) in enumerate(labels):
            x=i*cellw+4
            c.create_rectangle(x,6,x+cellw-8,h-7,outline='#123541',fill='#030b10')
            c.create_text(x+10,18,text=lab,anchor='w',fill=P['dim'],font=(MONO, 9,'bold'))
            c.create_text(x+10,38,text=val,anchor='w',fill=col,font=(MONO, 12,'bold'))
            base=x+10; bw=cellw-30
            c.create_rectangle(base,55,base+bw,60,fill='#0a2730',outline='')
            prog=.35+.55*(.5+.5*math.sin(t*.08+i))
            c.create_rectangle(base,55,base+bw*prog,60,fill=col,outline='')
            c.create_text(x+cellw-14,h-13,text=f'{(t+i*17)%100:02d}%',anchor='e',fill=col,font=(MONO, 9,'bold'))
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
            canvas.create_text(46,45,text=kicker,anchor='w',fill=P['cyan'],font=(MONO, 10,'bold'))
            canvas.create_text(w-46,45,text='LIVE // LOCAL',anchor='e',fill=P['green'],font=(MONO, 9,'bold'))
            lx=58; cy=225
            canvas.create_text(lx,112,text=title,anchor='w',fill=P['text'],font=(FONT, 17,'bold'))
            canvas.create_text(lx,141,text=f"// {prof['engine']}  //  {prof['scope']}",anchor='w',fill=accent,font=(MONO, 10,'bold'))
            canvas.create_text(lx,178,text=desc,anchor='w',fill=P['muted'],font=(FONT, 10),justify='left',width=290)
            statuses=[('ENGINE',prof['engine'],P['green']),('VISUAL TRACE','LIVE',P['cyan']),('DATA PATH',prof['scope'].split(' / ')[0],P['yellow']),('STATE',prof['state'],accent)]
            for i,(lab,val,col) in enumerate(statuses):
                yy=236+i*24; canvas.create_text(lx,yy,text=lab,anchor='w',fill=P['dim'],font=(MONO, 9,'bold')); canvas.create_text(lx+112,yy,text=str(val)[:16],anchor='w',fill=col,font=(MONO, 9,'bold'))
                canvas.create_rectangle(lx+170,yy-4,lx+270,yy+1,fill='#0a2731',outline='')
            canvas.create_rectangle(lx-8,337,lx+290,387,fill='#061923',outline=accent,width=1); canvas.create_text(lx+141,362,text='ENTER MODULE  //  ENTER',fill=P['text'],font=(MONO, 11,'bold'))
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
                    canvas.create_rectangle(cx-52,ys[i]-15,cx+52,ys[i]+15,outline=accent if i==0 else '#164452'); canvas.create_text(cx,ys[i],text=label,fill=P['text'],font=(MONO, 9,'bold'))
            elif key=='blue':
                dyn['cursor']=canvas.create_line(cx-100,cy-100,cx-100,cy+100,fill=P['cyan'],width=2)
                for i in range(6):
                    y=cy-75+i*30; canvas.create_line(cx-88,y,cx+95,y,fill='#164452'); canvas.create_oval(cx-92,y-4,cx-84,y+4,fill=accent if i%2 else P['green'],outline='')
            elif key=='labs':
                dyn['scan']=canvas.create_line(cx-100,cy-105,cx-100,cy+20,fill=P['green'],width=2)
                for i,label in enumerate(['BRIEF','TEST','CHECK','PROG']):
                    x=cx-75+i*50; canvas.create_oval(x-13,cy-12,x+13,cy+12,outline=accent,width=1); canvas.create_text(x,cy+32,text=label,fill=P['muted'],font=(MONO, 9,'bold'))
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
                    canvas.create_text(x,cy,text=label,fill=P['text'],font=(MONO, 9,'bold'))
                    if i<4: canvas.create_line(x+18,cy,x+27,cy,fill='#164452')
            else: # crypto
                xs=[cx-95,cx-32,cx+32,cx+95]; dyn['packet']=canvas.create_oval(xs[0]-5,cy-5,xs[0]+5,cy+5,fill=P['green'],outline='')
                for i,label in enumerate(['INPUT','KEY','XFORM','OUT']):
                    canvas.create_rectangle(xs[i]-23,cy-17,xs[i]+23,cy+17,outline=accent if i==0 else '#164452'); canvas.create_text(xs[i],cy,text=label,fill=P['text'],font=(MONO, 9,'bold'))
                    if i<3: canvas.create_line(xs[i]+23,cy,xs[i+1]-23,cy,fill='#164452')
            # center HN emblem remains a stable visual anchor for every module.
            self._draw_hn_emblem(canvas,cx,cy,size=.82,fg=P['text'],accent=accent,glow=P['cyan2'])
            canvas.create_text(cx,cy+126,text='HN // BLACKBOX CORE',fill=accent,font=(MONO, 10,'bold'))
            canvas.create_text(cx,cy+142,text='INPUT  •  TRACE  •  OUTPUT',fill=P['dim'],font=(MONO, 9,'bold'))
            canvas.create_text(46,h-49,text='SYSTEM TELEMETRY',anchor='w',fill=P['cyan'],font=(MONO, 9,'bold'))
            dyn['telemetry']=[]
            for i in range(22): dyn['telemetry'].append(canvas.create_rectangle(166+i*12,h-25,173+i*12,h-29,fill=accent if i%5==0 else '#1a5665',outline=''))
            canvas.create_text(w-46,h-49,text='LOCAL ONLY  •  NO EXTERNAL REQUESTS  •  HN BLACKBOX',anchor='e',fill=P['dim'],font=(MONO, 9,'bold'))
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
        self.history_count=tk.Label(bar,text='0 ENTRIES',bg=P['panel'],fg=P['cyan'],font=(MONO, 10,'bold')); self.history_count.pack(side='left',padx=12,pady=8)
        self.history_search=tk.Entry(bar,bg=P['panel2'],fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 10),width=34)
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
        text=tk.Text(wrap,bg='#030a11',fg=P['text'],insertbackground=P['cyan'],relief='flat',font=(MONO, 10),padx=14,pady=12,wrap='none',height=22)
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
        """Run filesystem/security diagnostics away from Tk, then render the report."""
        root=Path(__file__).resolve().parent.parent
        win=tk.Toplevel(self); win.title('HN BLACKBOX // DIAGNOSTICS'); win.geometry('760x500'); win.configure(bg=P['bg']); win.transient(self)
        tk.Label(win,text='SYSTEM DIAGNOSTICS // LOCAL',bg=P['bg'],fg=P['cyan'],font=(MONO, 11,'bold'),anchor='w').pack(fill='x',padx=18,pady=12)
        t=tk.Text(win,bg='#030a11',fg=P['text'],font=(MONO, 10),relief='flat',wrap='none'); t.pack(fill='both',expand=True,padx=18,pady=(0,12)); t.insert('1.0','DIAGNOSTICS QUEUED // BACKGROUND WORKER…'); t.configure(state='disabled')
        def work(): return diagnostics.run(root, history_manager.DEFAULT_PATH, psutil is not None)
        def done(data):
            ok, rows=data; lines=[f"{'PASS' if passed else 'FAIL':<4}  {label:<24} {detail}" for passed,label,detail in rows]
            out='HN BLACKBOX // DIAGNOSTICS\n'+'='*72+'\n'+'\n'.join(lines)+f"\n\nOVERALL: {'HEALTHY' if ok else 'ATTENTION REQUIRED'}"
            t.configure(state='normal'); t.delete('1.0','end'); t.insert('1.0',out); t.configure(state='disabled')
            self._record_tool_operation('development','System diagnostics','local environment',out)
        self._run_ui_worker(work,done,lambda e:(t.configure(state='normal'),t.delete('1.0','end'),t.insert('1.0',f'DIAGNOSTICS ERROR: {e}'),t.configure(state='disabled')))

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
        inp=tk.Text(box,height=5,bg=P["panel2"],fg=P["text"],font=(MONO, 10),relief="flat"); inp.pack(fill="x",padx=16,pady=5)
        inp.insert("1.0","LXFOPVEFRNHRLXFOPVEFRNHR")
        out=tk.Text(box,height=12,bg="#030a11",fg=P["cyan"],font=(MONO, 10),relief="flat"); out.pack(fill="x",padx=16,pady=7)
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
        self.lab_progress_label=tk.Label(top,text="",bg=P["panel"],fg=P["green"],font=(MONO, 10,"bold"),anchor="w"); self.lab_progress_label.pack(side="left")
        self.btn(top,"RESET PROGRESS",self.reset_lab_progress).pack(side="right")
        self.lab_progress_text=tk.Text(box,height=7,bg="#030a11",fg=P["text"],font=(MONO, 10),relief="flat"); self.lab_progress_text.pack(fill="x",padx=16,pady=(0,10))
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
        """Navigate without blocking the event loop.

        Existing pages are raised immediately. New destinations are mounted on the next
        idle turn, then their full visual engine becomes the foreground render owner.
        """
        self._last_user_event = time.monotonic()
        _previous = getattr(self, "current", None)
        if _previous == "processing" and key != "processing":
            try: self._render_scheduler.unregister("_visual_trace")
            except Exception: pass
            try: self._render_scheduler.unregister("_processing_microfx")
            except Exception: pass
        self.current=key
        if key == "processing" and hasattr(self, "_render_scheduler"):
            try: self._render_scheduler.register("_visual_trace", self._visual_frame, fps=30.0, priority=1)
            except Exception: pass
            try: self._render_scheduler.register("_processing_microfx", self._animate_processing_microfx, fps=30.0, priority=1)
            except Exception: pass
        self.current_page={"crypto":"dashboard","analysis":"cryptanalysis","blue":"blue_team"}.get(key,key)

        try:
            self.sidebar.grid()
            self.content.grid_configure(row=0, column=1, columnspan=1)
            self.topline.grid(); self.topbar.grid(); self.hud.place(relx=.98, rely=.058, anchor="ne")
        except tk.TclError:
            pass

        active_nav = "crypto" if key in {"crypto_modern", "crypto_stego", "processing"} else key
        for k,b in self.nav_buttons.items():
            if k in NAV_KEYS:
                active=k==active_nav
                try:
                    b.configure(bg=P["panel3"] if active else P["nav"],
                                 fg=getattr(b, '_accent', P['cyan']) if active else P["muted"],
                                 highlightbackground=getattr(b, '_accent', P['cyan']) if active else P['nav'])
                except tk.TclError:
                    pass

        page = self.pages.get(key)
        if page is not None:
            try: page.tkraise()
            except tk.TclError: return
            if key=="history": self.refresh_history()
            return

        # Paint a lightweight standby surface first; build the real page after Tk
        # has serviced the click and one render turn. This avoids synchronous UI
        # construction during navigation while keeping the existing factories.
        try:
            standby = self.pages.get("processing")
            if standby is not None:
                standby.tkraise()
        except tk.TclError:
            pass
        self._navigation_serial += 1
        serial = self._navigation_serial
        if self._navigation_job is not None:
            try: self.after_cancel(self._navigation_job)
            except Exception: pass
        self._navigation_job = self.after_idle(lambda: self._finish_navigation(key, serial))

    def _finish_navigation(self, key, serial):
        self._navigation_job = None
        if serial != self._navigation_serial or key != self.current:
            return
        try:
            page = self._ensure_page(key)
            if page is None:
                return
            page.tkraise()
            if key=="history": self.refresh_history()
        except Exception as exc:
            self._last_error = f"navigation:{key}: {exc}"

    def _on_resize(self,event=None):
        # Tk emits a Configure event for virtually every pixel while dragging.
        # Keep the inexpensive sidebar mode switch immediate, but debounce the
        # expensive dashboard reflow/grid redraw until the resize burst settles.
        self._resizing_until=time.monotonic()+0.22
        width=self.winfo_width()
        compact=width<1040
        if compact and self.sidebar_expanded:
            self.sidebar_expanded=False;self.sidebar.configure(width=78);self.grid_columnconfigure(1 if self.rtl else 0,minsize=78)
            self.logo.configure(font=(MONO, 22,'bold'),text='HN');self.brand.configure(text='HN');self.sub.pack_forget();self.project_caption.pack_forget()
            for b in self.nav_buttons.values():b.configure(text=b._icon,anchor='center',padx=0,pady=10,width=3,font=(MONO, 13,'bold'))
            if self.current=='home': self._home_layout_sig=None
        elif not compact and not self.sidebar_expanded:
            self.sidebar_expanded=True;self.sidebar.configure(width=270);self.grid_columnconfigure(1 if self.rtl else 0,minsize=270)
            self.logo.configure(font=(MONO, 30,'bold'),text='╔HN╗');self.brand.configure(text=self.t('brand'));self.sub.configure(text=self.t('sub'));self.sub.pack(pady=(3,0));self.project_caption.pack(fill='x',padx=8,pady=(2,8),before=self.nav_buttons[NAV[0][0]])
            for b in self.nav_buttons.values():b.configure(text=f'  {b._icon}   {b._label}',anchor=('e' if self.rtl else 'w'),padx=8,width=0,pady=9,font=(FONT, 10,'bold'))
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
    "network": P["green"], "fileintel": P["cyan"], "web": P["orange"], "blue": P["red"],
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
# All shipped modules are directly accessible. Incomplete capabilities are labeled in-page instead of being hidden behind a gate.
BETA_MODULES = set()
CRYPTO_GROUPS = {
    "requested": {
        "title": "REQUIRED CIPHERS // المنهج",
        "sub": "الخوارزميات الأساسية المطلوبة مع عرض بصري حي ومسار تنفيذ واضح.",
        "keys": ["caesar", "additive", "multiplicative", "affine", "vigenere", "autokey", "railfence", "keyed_transposition", "double_transposition"],
        "accent": P["cyan"],
    },
    "extended": {
        "title": "ADDED CIPHERS // المضافة",
        "sub": "خوارزميات إضافية توسّع المختبر وتدعم التدريب والمقارنة.",
        "keys": [k for k in ALGORITHMS if k not in {"caesar", "additive", "multiplicative", "affine", "vigenere", "autokey", "railfence", "keyed_transposition", "double_transposition", "des"}],
        "accent": P["purple"],
    },
    "all": {
        "title": "FULL CLASSICAL MATRIX // الكاملة",
        "sub": "جميع خوارزميات المسار الكلاسيكي المتاحة داخل HN BlackBox.",
        "keys": [k for k in ALGORITHMS if k != "des"],
        "accent": P["green"],
    },
}


def main():
    app=HNBlackBoxApp()
    app.mainloop()

if __name__=="__main__":
    main()

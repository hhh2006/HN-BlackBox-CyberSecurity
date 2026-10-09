
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui.app import HNBlackBoxApp, ALGORITHMS

def test_algorithm_inventory():
    assert len(ALGORITHMS) >= 18
    for key in ("caesar","vigenere","playfair","railfence","columnar","atbash","rot13","affine","hill","beaufort","polybius","adfgvx","bacon","morse","autokey","otp","aes","rsa","hash"):
        assert key in ALGORITHMS

def test_bilingual_interface_default_english():
    app=HNBlackBoxApp()
    assert hasattr(app, "toggle_language")
    assert hasattr(app, "language")
    assert app.language == "en"
    assert app.t("brand") == "HN // BLACKBOX"
    app.set_language("ar")
    assert app.t("crypto") == "التشفير"
    assert app.rtl is True
    app.set_language("en")
    assert app.t("crypto") == "CRYPTOGRAPHY"
    assert app.rtl is False
    app.destroy()


def test_one_time_launcher():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    launcher=(root / "run_blackbox.bat").read_text(encoding="utf-8")
    assert "%LOCALAPPDATA%\\HNBlackBox\\venv" in launcher
    assert "Get-FileHash" in launcher
    assert "pip install -r requirements.txt" in launcher


def test_welcome_screen_removed_and_dashboard_is_start():
    app=HNBlackBoxApp(); app.update_idletasks()
    assert app.current == "home"
    assert app.current_page == "home"
    assert "welcome" not in app.pages
    app.destroy()

def test_transposition_labs_open():
    app=HNBlackBoxApp(); app.update_idletasks(); app.show_page("crypto"); app._select_crypto_group("all"); app.update_idletasks()
    for key in ("keyed_transposition", "double_transposition"):
        app._crypto_card_click(key); app.update_idletasks()
        assert app.current == "processing"
        assert app.current_algo == key
        assert "word" in app.key_entries or key == "double_transposition"
        app.show_page("crypto")
    app.destroy()


def test_global_font_floor():
    import re
    from pathlib import Path
    src=Path(__file__).resolve().parents[1] / "gui" / "app.py"
    text=src.read_text(encoding="utf-8")
    for fam, floor in (("MONO", 9), ("FONT", 10), ("ASCII_MONO", 10)):
        for raw in re.findall(rf"font=\({fam},\s*(\d+)", text):
            assert int(raw) >= floor

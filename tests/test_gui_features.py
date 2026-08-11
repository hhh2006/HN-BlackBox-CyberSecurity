
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gui.app import HNBlackBoxApp, ALGORITHMS

def test_algorithm_inventory():
    assert len(ALGORITHMS) >= 18
    for key in ("caesar","vigenere","playfair","railfence","columnar","atbash","rot13","affine","hill","beaufort","polybius","adfgvx","bacon","morse","autokey","otp","aes","rsa","hash"):
        assert key in ALGORITHMS

def test_english_only_interface():
    app=HNBlackBoxApp()
    assert not hasattr(app, "toggle_language")
    assert not hasattr(app, "lang")
    assert app.t("brand") == "HN // BLACKBOX"
    app.destroy()

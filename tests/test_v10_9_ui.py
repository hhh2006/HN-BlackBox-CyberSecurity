import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from gui.app import HNBlackBoxApp

def test_crypto_selector_and_developer_page():
    app=HNBlackBoxApp()
    app.show_page("crypto"); app.update_idletasks()
    assert len(app.crypto_cards) == 0
    app._select_crypto_group("requested"); app.update_idletasks()
    assert len(app.crypto_cards) == 9
    app._select_crypto_group("extended"); app.update_idletasks()
    assert len(app.crypto_cards) == 14
    app._select_crypto_group("all"); app.update_idletasks()
    assert len(app.crypto_cards) == len(__import__("gui.app", fromlist=["ALGORITHMS"]).ALGORITHMS) - 1
    app.show_page("developer"); app.update_idletasks()
    assert app._developer_canvas.winfo_exists()
    app.destroy()

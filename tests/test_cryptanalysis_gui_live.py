import tkinter as tk

from gui.app import HNBlackBoxApp


def _buttons(parent):
    found=[]
    for child in parent.winfo_children():
        if isinstance(child, tk.Button):
            found.append(child)
        found.extend(_buttons(child))
    return found


def test_cryptanalysis_deck_mounts_and_exposes_live_controls():
    app = HNBlackBoxApp()
    try:
        app.show_page('analysis')
        app.update()
        app.update_idletasks()
        # Lazy navigation is intentionally deferred; force the queued idle work.
        app.update()
        assert app.pages['analysis'] is not None
        labels = {str(b.cget('text')) for b in _buttons(app.pages['analysis'])}
        assert 'RUN FREQUENCY ANALYSIS' in labels
        assert 'EXECUTE BRUTE-FORCE' in labels
        assert 'CALCULATE IC' in labels
        assert 'CLEAR MATRIX' in labels
    finally:
        app.destroy()

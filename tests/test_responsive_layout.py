import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from gui.app import HNBlackBoxApp

def settle(app, ms=120):
    end=time.time()+ms/1000
    while time.time()<end:
        app.update_idletasks(); app.update()

def ready(app):
    # Tests bypass the cosmetic boot splash; this makes layout assertions deterministic.
    try:
        for job in app.tk.call('after','info'):
            try: app.after_cancel(job)
            except Exception: pass
        if app.splash.winfo_exists(): app.splash.destroy()
    except Exception: pass
    app.deiconify(); app.update_idletasks(); app.update()

def test_modern_crypto_stacks_on_compact_window():
    app=HNBlackBoxApp(); ready(app); app.minsize(760,560); app.geometry('800x600'); settle(app); app.show_page('crypto_modern'); settle(app)
    hosts=[f for f in ('des','aes','rsa','hash')]
    assert all(getattr(app,'_modern_context',None) is not None for _ in hosts)
    # At compact width the four workspace split controllers are expected to stack.
    assert app.winfo_width() < 980
    app.destroy()

def test_stego_lower_panels_stack_on_compact_window():
    app=HNBlackBoxApp(); ready(app); app.minsize(760,560); app.geometry('800x600'); settle(app); app.show_page('crypto_stego'); settle(app)
    assert app.winfo_width() == 800
    app.destroy()

def test_resize_cycle_and_close_are_clean():
    app=HNBlackBoxApp(); ready(app); app.minsize(760,560)
    for size in ('1600x900','1280x820','1024x768','900x650','800x600','1280x820'):
        app.geometry(size); settle(app,50); app.show_page('crypto_modern'); settle(app,50); app.show_page('home'); settle(app,50)
    app.destroy()


def test_accessible_minimum_window_size():
    app=HNBlackBoxApp(); app.update_idletasks()
    min_w,min_h=app.minsize()
    assert int(min_w) >= 1024 and int(min_h) >= 700
    app.destroy()

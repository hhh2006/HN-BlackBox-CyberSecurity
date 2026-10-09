from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]

def test_foreground_render_contract():
    app = (ROOT / "gui/app.py").read_text()
    scheduler = (ROOT / "core/rendering/scheduler.py").read_text()
    js = (ROOT / "renderer/src/main.js").read_text()
    css = (ROOT / "renderer/src/styles.css").read_text()
    assert "_motion_page_active" in app
    assert "_motion_owner_for_callback" in app
    assert '"static_only": False' in app
    assert "if not self._widget_on_current_page(frame)" not in app
    assert "if not self._widget_on_current_page(hud)" not in app
    assert "except Exception as exc:" in scheduler
    assert "A faulty visual channel must never poison the master clock" in scheduler
    assert "requestAnimationFrame(frame)" in js
    assert "setInterval" in js
    assert "gridDrift" in css and "panelLaser" in css and "panelHeartbeat" in css and "fieldScan" in css

def test_foreground_visual_clock_and_suspension_survive_navigation():
    import sys
    sys.path.insert(0, str(ROOT))
    from gui.app import HNBlackBoxApp
    app = HNBlackBoxApp()
    try:
        try: app.splash.destroy()
        except Exception: pass
        app.deiconify(); app.update_idletasks(); app.update()
        end = time.monotonic() + 0.35
        while time.monotonic() < end:
            app.update(); time.sleep(0.01)
        start_frame = app._perf_frame
        assert start_frame >= 5
        app.show_page("crypto")
        app.update_idletasks(); app.update()
        end = time.monotonic() + 0.30
        while time.monotonic() < end:
            app.update(); time.sleep(0.01)
        assert app._perf_frame > start_frame
        assert app._render_scheduler.stats()["channel_errors"] == 0
        assert app.pages["crypto"] is not None
        # Non-current destinations remain unmounted until entered, so they consume no animation work.
        assert app.pages["network"] is None
        assert app.pages["developer"] is None
        app.show_page("network")
        app.update_idletasks(); app.update()
        assert app.pages["network"] is not None
        assert app.current == "network"
        assert app._render_scheduler.stats()["channel_errors"] == 0
    finally:
        app.destroy()

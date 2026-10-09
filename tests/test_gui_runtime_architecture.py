import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from gui.app import HNBlackBoxApp


def release_splash(app):
    try:
        app.splash.destroy()
    except Exception:
        pass
    app.deiconify()
    app.update_idletasks()
    app.update()


def settle(app, seconds=0.18):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.update()
        time.sleep(0.008)


def test_home_hud_is_live_vector_motion_not_static_image():
    app = HNBlackBoxApp()
    try:
        release_splash(app)
        settle(app, 0.18)
        canvas = app.home_hero_canvas
        items = [i for i in canvas.find_all() if canvas.type(i) == "line"]
        assert items, "Home HUD did not render vector geometry"
        before = {i: tuple(canvas.coords(i)) for i in items}
        settle(app, 0.28)
        after = {i: tuple(canvas.coords(i)) for i in items}
        assert any(before[i] != after.get(i) for i in before)
        assert app._perf_frame >= 5
    finally:
        app.destroy()


def test_terminal_worker_event_does_not_block_gui_callback():
    app = HNBlackBoxApp()
    try:
        release_splash(app)
        app.home_cmd.delete(0, "end")
        app.home_cmd.insert(0, 'run hash sha256 "hello"')
        started = time.perf_counter()
        app._home_command()
        elapsed = (time.perf_counter() - started) * 1000
        assert elapsed < 50, elapsed
        settle(app, 0.5)
        text = app.home_terminal.get("1.0", "end-1c")
        assert "SHA256" in text and "2cf24dba" in text
    finally:
        app.destroy()


def test_foreground_destination_gets_motion_and_inactive_destination_suspends():
    app = HNBlackBoxApp()
    try:
        release_splash(app)
        settle(app, 0.20)
        # Home is the initial foreground destination and must move.
        canvas = app.home_hero_canvas
        lines = [i for i in canvas.find_all() if canvas.type(i) == "line"]
        assert lines
        before = {i: tuple(canvas.coords(i)) for i in lines}
        settle(app, 0.20)
        after = {i: tuple(canvas.coords(i)) for i in lines}
        assert any(before[i] != after.get(i) for i in before)

        # Enter Crypto: its scene is mounted and active; Home's visual channel suspends.
        app._nav_click("crypto")
        app.update_idletasks()
        settle(app, 0.35)
        assert app.current == "crypto" and app.pages["crypto"] is not None
        home_before = {i: tuple(canvas.coords(i)) for i in lines}
        settle(app, 0.25)
        home_after = {i: tuple(canvas.coords(i)) for i in lines}
        assert all(home_before[i] == home_after.get(i) for i in home_before)

        # Return Home: Home resumes motion without rebuilding its scene.
        app._nav_click("home")
        app.update_idletasks()
        settle(app, 0.25)
        resumed = {i: tuple(canvas.coords(i)) for i in lines}
        settle(app, 0.20)
        resumed_after = {i: tuple(canvas.coords(i)) for i in lines}
        assert any(resumed[i] != resumed_after.get(i) for i in resumed)
    finally:
        app.destroy()


import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.app import HNBlackBoxApp


def test_gui_smoke():
    app = HNBlackBoxApp()
    app.minsize(760, 560)  # exercise compact layout without changing the production floor
    try:
        app.update_idletasks()
        assert set(("dashboard", "processing", "cryptanalysis", "network", "web", "blue_team", "labs", "development", "developer", "history", "crypto_stego")).issubset(app.pages)
        assert "welcome" not in app.pages

        app.show_page("dashboard")
        app.open_algorithm("caesar")
        app.input_box.insert("1.0", "HELLO")
        app.key_entries["shift"].insert(0, "3")
        app.execute()
        for _ in range(100):
            app.update()
            if app._crypto_future is None:
                break
        assert app.result_box.get("1.0", "end-1c") == "KHOOR"

        app.clear_processing()
        assert app.input_box.get("1.0", "end-1c") == ""

        app.geometry("780x580")
        app.update_idletasks()
        small_sidebar = app.sidebar.winfo_width()
        app.geometry("1240x800")
        app.update_idletasks()
        large_sidebar = app.sidebar.winfo_width()
        assert small_sidebar <= 100, small_sidebar
        assert large_sidebar >= 200, large_sidebar

        app.nav_buttons["history"].invoke()
        assert app.current_page == "history"
        for section in ("analysis", "network", "web", "blue", "labs"):
            app._nav_click(section)
            app.update()
            expected = {"analysis":"cryptanalysis","network":"network","web":"web","blue":"blue_team","labs":"labs"}[section]
            assert app.current_page == expected
            assert not hasattr(app, "_beta_modal") or not app._beta_modal.winfo_exists()
        app.nav_buttons["development"].invoke()
        assert app.current_page == "development"
        app.nav_buttons["developer"].invoke()
        assert app.current_page == "developer"

        app.nav_buttons["crypto"].invoke()
        assert app.current_page == "dashboard"
    finally:
        app.destroy()

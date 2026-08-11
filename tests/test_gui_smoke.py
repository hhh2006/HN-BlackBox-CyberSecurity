import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gui.app import HNBlackBoxApp


app = HNBlackBoxApp()
app.update_idletasks()
assert set(("welcome", "dashboard", "processing", "cryptanalysis", "network", "web", "blue_team", "labs", "development", "developer", "history")).issubset(app.pages)

app.show_page("dashboard")
app.open_algorithm("caesar")
app.input_box.insert("1.0", "HELLO")
app.key_entries["shift"].insert(0, "3")
app.execute()
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
    assert hasattr(app, "_beta_modal") and app._beta_modal.winfo_exists()
    # Deterministically emulate the user's confirmation action in CI.
    app._beta_modal.destroy()
    app.show_page(section)
    app.update()
    expected = {"analysis":"cryptanalysis","network":"network","web":"web","blue":"blue_team","labs":"labs"}[section]
    assert app.current_page == expected
app.nav_buttons["development"].invoke()
assert app.current_page == "development"
app.nav_buttons["developer"].invoke()
assert app.current_page == "developer"

app.nav_buttons["welcome"].invoke()
assert app.current_page == "welcome"

app.destroy()
print("GUI SMOKE TEST PASSED")

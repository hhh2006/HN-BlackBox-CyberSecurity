import sys, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gui.app import HNBlackBoxApp

app=HNBlackBoxApp()
app.withdraw()
# Exercise terminal command parser without rendering the splash.
app.current='home'
app.home_cmd = __import__('tkinter').Entry(app)
app.home_terminal = __import__('tkinter').Text(app)
for cmd in ['caesar encrypt "HELLO" 3','hash sha256 "HN BLACKBOX"','analyze "THE QUICK BROWN FOX"','modules']:
    app.home_cmd.delete(0,'end'); app.home_cmd.insert(0,cmd); app._home_command()
# Render crypto lab at desktop and compact sizes.
app.show_page('crypto')
app.update_idletasks()
for w,h in [(1440,900),(1100,760),(820,650),(760,560)]:
    app.geometry(f'{w}x{h}'); app.update_idletasks(); app.update()
# Render Caesar processing and ensure visual exists.
app.open_algorithm('caesar'); app.update_idletasks(); app.geometry('1280x820'); app.update_idletasks()
app.input_box.insert('1.0','HELLO WORLD')
app.key_entries['shift'].insert(0,'3')
app.execute(); app.update_idletasks(); app.update()
print('terminal_and_resize=PASS')
print('processing_visual=PASS')
app.destroy()

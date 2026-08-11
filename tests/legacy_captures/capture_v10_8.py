import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gui.app import HNBlackBoxApp
from PIL import ImageGrab
app=HNBlackBoxApp(); app.withdraw(); app.geometry('1280x820'); app.update_idletasks(); app.deiconify(); app.update(); time.sleep(.2)
ImageGrab.grab(bbox=(0,0,1280,820)).save('/mnt/data/HN_BlackBox_v10_8_HOME.png')
app.open_algorithm('caesar'); app.update_idletasks(); app.update();
app.input_box.insert('1.0','HELLO WORLD'); app.key_entries['shift'].insert(0,'3'); app.execute();
for _ in range(18): app.update(); time.sleep(.08)
ImageGrab.grab(bbox=(0,0,1280,820)).save('/mnt/data/HN_BlackBox_v10_8_CAESAR.png')
app.destroy()

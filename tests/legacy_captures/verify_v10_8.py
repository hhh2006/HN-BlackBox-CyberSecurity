import sys, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gui.app import HNBlackBoxApp

app=HNBlackBoxApp(); app.withdraw()
for size in ('1280x820','1100x760','900x650','760x560'):
    app.geometry(size); app.update_idletasks(); app.update()
    app.open_algorithm('caesar'); app.update_idletasks(); app.update()
    assert app.visual.winfo_width() > 0 and app.visual.winfo_height() > 0
    app.input_box.delete('1.0','end'); app.input_box.insert('1.0','HELLO WORLD')
    app.key_entries['shift'].delete(0,'end'); app.key_entries['shift'].insert(0,'3')
    app.execute(); app.update_idletasks(); app.update()
    assert app.result_box.get('1.0','end-1c') == 'KHOOR ZRUOG'
    assert app.visual_status.cget('text')
app.destroy()
print('V10.8 RESPONSIVE CRYPTO TEST PASSED')

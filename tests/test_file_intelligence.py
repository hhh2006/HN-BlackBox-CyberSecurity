import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from gui.app import HNBlackBoxApp

def test_file_intel_worker_fingerprints_local_file():
    app=HNBlackBoxApp()
    try:
        fd,path=tempfile.mkstemp(suffix='.txt'); os.write(fd,b'HN BLACKBOX LOCAL EVIDENCE 12345\n'); os.close(fd)
        try:
            r=app._file_intel_worker(path)
            assert r['type']=='Unknown / application data'
            assert len(r['sha256'])==64 and len(r['sha1'])==40 and len(r['md5'])==32
            assert r['entropy'] > 0
            assert r['strings']
        finally: os.unlink(path)
    finally: app.destroy()

def test_file_intel_page_is_mounted_and_read_only_ui_exists():
    app=HNBlackBoxApp()
    try:
        assert 'fileintel' in app.pages
        app.show_page('fileintel'); app.update_idletasks()
        assert app.fileintel_canvas.winfo_exists()
        assert app.fileintel_report.winfo_exists()
    finally: app.destroy()

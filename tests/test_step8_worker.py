import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ui.runtime.crypto_worker import CryptoWorker
from ui.runtime.crypto_dispatch import execute_crypto

def test_worker_dispatch_preserves_engine_result():
    w = CryptoWorker(max_workers=2)
    try:
        f = w.submit(execute_crypto, "caesar", {"shift":"3"}, "encrypt", "HELLO")
        assert f.result(timeout=3) == "KHOOR"
    finally:
        w.shutdown()

def test_worker_is_non_ui_boundary():
    w = CryptoWorker(max_workers=1)
    try:
        f = w.submit(time.sleep, 0.05)
        assert not f.done()
        assert f.result(timeout=1) is None
    finally:
        w.shutdown()

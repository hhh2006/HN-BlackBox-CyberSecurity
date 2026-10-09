"""Optional high-performance web renderer bridge for HN BlackBox.

The native Tk renderer remains the deterministic fallback. When the web
renderer is requested, this module serves the local cinematic frontend on
127.0.0.1 and opens it in pywebview when available, otherwise in the system
browser. No crypto operation is executed by the web layer; it is a visualization
surface only.
"""
from __future__ import annotations

import functools
import http.server
import os
import socket
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "renderer"

_server = None
_thread = None
_port = None
_lock = threading.Lock()


def _find_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def ensure_server():
    global _server, _thread, _port
    with _lock:
        if _server is not None:
            return _port
        port = _find_port()
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
        _server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
        _server.daemon_threads = True
        _port = port
        _thread = threading.Thread(target=_server.serve_forever, name="hn-cinematic-http", daemon=True)
        _thread.start()
        return _port


def open_cinematic(mode="modern"):
    """Open the cinematic renderer without blocking the Tk event loop."""
    mode = "stego" if mode == "stego" else "modern"
    port = ensure_server()
    url = f"http://127.0.0.1:{port}/?mode={mode}"

    def launch():
        try:
            import webview  # optional dependency: pywebview >= 6.2.1
            webview.create_window(
                f"HN BLACKBOX // {mode.upper()} // CINEMATIC CORE",
                url,
                width=1440,
                height=900,
                min_size=(960, 640),
                background_color="#02050a",
            )
            webview.start(debug=False)
        except Exception:
            webbrowser.open_new(url)

    threading.Thread(target=launch, name="hn-cinematic-launch", daemon=True).start()
    return url


def shutdown_server():
    global _server, _thread, _port
    with _lock:
        if _server is not None:
            _server.shutdown()
            _server.server_close()
        _server = _thread = _port = None

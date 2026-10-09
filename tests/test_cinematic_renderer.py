import json
from pathlib import Path
from urllib.request import urlopen

from ui.cinematic_renderer import ensure_server, shutdown_server

ROOT = Path(__file__).resolve().parents[1]


def test_cinematic_renderer_manifest_is_gpu_first():
    data = json.loads((ROOT / "renderer" / "package.json").read_text(encoding="utf-8"))
    assert data["version"] == "2.1.0"
    assert "WebGL2" in data["description"]


def test_cinematic_renderer_local_server_serves_visual_surface():
    try:
        port = ensure_server()
        with urlopen(f"http://127.0.0.1:{port}/?mode=modern", timeout=2) as response:
            body = response.read().decode("utf-8")
        assert response.status == 200
        assert "CINEMATIC SECURITY CORE" in body
        assert "gpu-canvas" in body
    finally:
        shutdown_server()


def test_cinematic_renderer_source_contains_real_gpu_compositor_and_adaptive_guards():
    js = (ROOT / "renderer" / "src" / "main.js").read_text(encoding="utf-8")
    assert "webgl2" in js
    assert "WebGL2" in js
    assert "high-performance" in js
    assert "requestAnimationFrame" in js
    assert "autonomousTelemetryBus" in js
    assert "autonomousHexStreamBus" in js
    assert "qualityScale" in js
    assert "uAccent" in js
    assert "uPointer" in js
    assert "uBurst" in js

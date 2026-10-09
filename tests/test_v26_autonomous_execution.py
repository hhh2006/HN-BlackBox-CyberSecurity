from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_v26_autonomous_execution_contract():
    js=(ROOT/"renderer/src/main.js").read_text()
    css=(ROOT/"renderer/src/styles.css").read_text()
    app=(ROOT/"gui/app.py").read_text()
    scheduler=(ROOT/"core/rendering/scheduler.py").read_text()
    assert "requestAnimationFrame(frame)" in js
    assert "setInterval" in js
    assert "autonomousTelemetryBus" in js
    assert "autonomousHexStreamBus" in js
    assert "autoSweep" in js and "autoLens" in js
    assert "gridDrift" in css and "panelLaser" in css and "panelHeartbeat" in css
    assert "fieldScan" in css
    assert "self._motion_ms = 16" in app
    assert "self._motion_hidden_ms = 16" in app
    assert "V26 policy: visual continuity" in app
    assert "V26 autonomous mode" in scheduler
    # Visual functions must not gate motion on the current navigation page.
    visual=app[app.index("    def _animate_home_identity"):app.index("    def _attach_cinematic_surface")]
    assert "if self.current != 'home'" not in visual

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / 'renderer' / 'src' / 'main.js').read_text(encoding='utf-8')
CSS = (ROOT / 'renderer' / 'src' / 'styles.css').read_text(encoding='utf-8')


def test_gpu_surface_uses_single_raf_clock_for_animation():
    assert 'requestAnimationFrame(frame)' in JS
    assert 'setInterval(' in JS
    assert 'autonomousTelemetryBus' in JS
    assert 'autonomousHexStreamBus' in JS
    assert 'advanceCryptoAnimation(now)' in JS


def test_gpu_canvas_has_compositor_hints():
    assert 'will-change:transform' in CSS
    assert 'translateZ(0)' in CSS
    assert 'contain:strict' in CSS


def test_visual_channels_remain_autonomous():
    assert 'pointermove' in JS
    assert 'pointerdown' in JS
    # Pointer input changes the lens/burst state, but the render loop itself is unconditional.
    frame_start = JS.index('function frame(now)')
    frame_body = JS[frame_start:JS.index('if(now-state.lastFps', frame_start)]
    assert 'advanceCryptoAnimation(now)' in frame_body
    assert 'state.active' not in frame_body

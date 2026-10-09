from pathlib import Path
from core.rendering.scheduler import RenderScheduler

ROOT = Path(__file__).resolve().parents[1]


def test_single_master_render_scheduler():
    calls = []
    s = RenderScheduler(target_fps=60, budget_ms=9)
    s.register('a', lambda: calls.append('a'), fps=60, priority=1)
    s.register('b', lambda: calls.append('b'), fps=30, priority=0)
    s.tick()
    assert calls == ['a', 'b']
    assert s.stats()['channels'] == 2


def test_prewarm_removed_and_native_app_uses_scheduler():
    src = (ROOT / 'gui' / 'app.py').read_text(encoding='utf-8')
    assert '_prewarm_pages' not in src
    assert 'RenderScheduler' in src
    assert 'self._render_scheduler.tick()' in src

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_header_hud_is_telemetry_only_and_dense():
    app = (ROOT / 'gui/app.py').read_text()
    assert 'route_nodes' not in app
    assert 'route_pages()' not in app
    assert 'bar_count=max(24' in app
    assert "'rates':rates" in app
    assert "'labels':labels" in app
    assert 'Autonomous telemetry labels' in app


def test_header_hud_navigation_is_not_rendered_as_buttons():
    app = (ROOT / 'gui/app.py').read_text()
    heading = app[app.index('    def heading('):app.index('    def _animate_heading_huds(')]
    assert 'Button-1' not in heading
    assert 'cursor="hand2"' not in heading
    assert "route_items" not in heading

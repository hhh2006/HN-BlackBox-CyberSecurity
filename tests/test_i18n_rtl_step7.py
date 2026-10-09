import sys
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def test_translation_catalog_complete():
    import gui.app as mod
    assert set(mod.TEXTS).issubset(set(mod.TEXTS_AR))
    assert mod.TEXTS_AR['crypto'] == 'التشفير'


def test_language_and_rtl_shell():
    tk = pytest.importorskip('tkinter')
    import gui.app as mod
    try:
        app = mod.HNBlackBoxApp()  # type: ignore[name-defined]
    except Exception as exc:
        pytest.skip(f'GUI display unavailable: {exc}')
    try:
        app.set_language('ar')
        assert app.language == 'ar'
        assert app.rtl is True
        assert app.brand.cget('text') == 'HN // BLACKBOX'
        assert app.nav_buttons['crypto'].cget('text') != '  ▣   Cryptography'
        app.set_language('en')
        assert app.rtl is False
        assert 'CRYPTOGRAPHY' in app.nav_buttons['crypto'].cget('text')
    finally:
        app.destroy()

from pathlib import Path
import wave

ROOT = Path(__file__).resolve().parents[1]


def test_startup_audio_is_single_cinematic_asset():
    audio_dir = ROOT / 'assets' / 'audio'
    files = sorted(p.name for p in audio_dir.glob('*') if p.is_file())
    assert files == ['startup_cinematic_welcome.wav']
    with wave.open(str(audio_dir / files[0]), 'rb') as wav:
        assert wav.getnchannels() == 2
        assert wav.getframerate() == 48000
        assert wav.getsampwidth() == 2
        assert 5.7 <= wav.getnframes() / wav.getframerate() <= 6.1


def test_startup_sequence_is_synchronized_and_non_repetitive():
    app = (ROOT / 'gui' / 'app.py').read_text(encoding='utf-8')
    assert '_play_startup_welcome_audio' in app
    assert '_start_startup_sequence' in app
    assert '_startup_audio_started' in app
    assert 'startup_cinematic_welcome.wav' in app
    # Only the single startup sequence is allowed; no hover/click/ambient API.
    assert 'announce_module' not in app
    assert 'play_click' not in app
    assert 'play_hover' not in app

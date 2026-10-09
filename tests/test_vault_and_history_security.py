from pathlib import Path
from core.platform import history_manager
from core.security_tools import vault


def test_history_masks_secret_key(tmp_path):
    p = tmp_path / "history.json"
    history_manager.add_entry("AES", "encrypt", "SUPER-SECRET-KEY", "hello", "cipher", str(p))
    item = history_manager.get_all(str(p))[0]
    assert item["key"] != "SUPER-SECRET-KEY"
    assert "SECRET" not in item["key"]


def test_vault_requires_strong_enough_password_and_roundtrips(tmp_path):
    path = tmp_path / "vault.json"
    try:
        vault.seal({"x": 1}, "short", str(path))
    except ValueError:
        pass
    else:
        raise AssertionError("short vault passwords must be rejected")
    vault.seal({"x": "عربي"}, "long-enough-password", str(path))
    assert vault.open_vault("long-enough-password", str(path)) == {"x": "عربي"}

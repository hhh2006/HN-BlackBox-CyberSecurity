from core.cryptanalysis import cryptanalysis as c

def test_frequency_profile_and_similarity():
    d = c.frequency_profile("THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG")
    assert d["language"] == "EN"
    assert d["letters"] > 20
    assert any(r["letter"] == "E" and r["count"] > 0 for r in d["rows"])
    assert 0 <= c.frequency_match_score("HELLO WORLD", "EN") <= 100

def test_ic_and_kasiski_are_computed():
    text = "LXFOPVEFRNHRLXFOPVEFRNHR"
    assert c.index_of_coincidence(text) > 0
    lengths = c.estimate_vigenere_key_lengths(text, 10)
    assert lengths and all(len(x) == 2 for x in lengths)

def test_caesar_enumerates_all_real_shifts_and_ranks():
    rows = c.caesar_candidates("KHOOR ZRUOG")
    assert len(rows) == 26
    assert rows[0]["plaintext"] == "HELLO WORLD"
    assert rows[0]["key"] == 3
    assert "probability" in rows[0]

def test_vigenere_key_recovery_uses_existing_cipher_engine():
    from core.cryptography.classical.required import vigenere
    cipher = vigenere.encrypt("THIS IS A LONGER ENGLISH SAMPLE THAT SHOULD PROVIDE A SIGNAL", "KEY")
    result = c.recover_vigenere_key(cipher, 3)
    assert len(result["key"]) == 3
    assert result["plaintext"]

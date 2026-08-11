# -*- coding: utf-8 -*-
"""
نفس اختبارات test_ciphers.py بس بصيغة pytest عشان GitHub Actions يقدر
يشغّلها تلقائيًا على كل push (`pytest` بس، بدون أي إعداد إضافي).
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import caesar, vigenere, affine, rail_fence, autokey, playfair, hill_cipher, frequency_analysis


def test_caesar_roundtrip():
    assert caesar.encrypt("HELLO", 3) == "KHOOR"
    assert caesar.decrypt("KHOOR", 3) == "HELLO"
    assert caesar.encrypt("Hi, World!", 5) == "Mn, Btwqi!"


def test_caesar_bruteforce_finds_key():
    results = caesar.brute_force("KHOOR")
    assert any(k == 3 and t == "HELLO" for k, t in results)


def test_vigenere_textbook_example():
    assert vigenere.encrypt("ATTACKATDAWN", "LEMON") == "LXFOPVEFRNHR"
    assert vigenere.decrypt("LXFOPVEFRNHR", "LEMON") == "ATTACKATDAWN"


def test_affine_roundtrip_and_validation():
    enc = affine.encrypt("AFFINECIPHER", 5, 8)
    assert affine.decrypt(enc, 5, 8) == "AFFINECIPHER"
    assert affine.encrypt("A", 5, 8) == "I"
    try:
        affine.encrypt("TEST", 4, 3)
        assert False, "المفروض يرمي ValueError لأن gcd(4,26) != 1"
    except ValueError:
        pass


def test_railfence_textbook_example():
    assert rail_fence.encrypt("WEAREDISCOVEREDFLEEATONCE", 3) == "WECRLTEERDSOEEFEAOCAIVDEN"
    assert rail_fence.decrypt("WECRLTEERDSOEEFEAOCAIVDEN", 3) == "WEAREDISCOVEREDFLEEATONCE"


def test_autokey_roundtrip():
    enc = autokey.encrypt("HELLO", "KEY")
    assert enc == "RIJSS"
    assert autokey.decrypt(enc, "KEY") == "HELLO"


def test_playfair_roundtrip():
    enc = playfair.encrypt("INSTRUMENTS", "MONARCHY")
    dec = playfair.decrypt(enc, "MONARCHY")
    assert dec == "INSTRUMENTSX"


def test_hill_cipher_textbook_example():
    assert hill_cipher.encrypt("HELP", (3, 3, 2, 5)) == "HIAT"
    assert hill_cipher.decrypt("HIAT", (3, 3, 2, 5)) == "HELP"


def test_frequency_analysis():
    result = frequency_analysis.analyze("EEEAAABBC")
    assert result[0]["letter"] == "E"
    assert result[0]["count"] == 3

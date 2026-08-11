# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import caesar, vigenere, affine, rail_fence, autokey, playfair, frequency_analysis, hill_cipher

results = []


def check(name, condition, extra=""):
    status = "PASS" if condition else "FAIL"
    results.append((name, condition))
    print(f"{status} - {name} {extra}")


# ---------------- Caesar ----------------
check("caesar encrypt", caesar.encrypt("HELLO", 3) == "KHOOR")
check("caesar decrypt", caesar.decrypt("KHOOR", 3) == "HELLO")
check("caesar preserves case/punctuation", caesar.encrypt("Hi, World!", 5) == "Mn, Btwqi!")
check("caesar roundtrip random", caesar.decrypt(caesar.encrypt("Testing 123!", 17), 17) == "Testing 123!")
bf = caesar.brute_force("KHOOR")
check("caesar brute_force contains correct key", any(k == 3 and t == "HELLO" for k, t in bf))

# ---------------- Vigenere ----------------
# مثال معروف من الكتب: plaintext ATTACKATDAWN key LEMON -> LXFOPVEFRNHR
check("vigenere textbook example",
      vigenere.encrypt("ATTACKATDAWN", "LEMON") == "LXFOPVEFRNHR")
check("vigenere decrypt textbook example",
      vigenere.decrypt("LXFOPVEFRNHR", "LEMON") == "ATTACKATDAWN")
check("vigenere roundtrip with punctuation",
      vigenere.decrypt(vigenere.encrypt("Hello, Friend!", "KEY"), "KEY") == "Hello, Friend!")

# ---------------- Affine ----------------
# مثال معروف: a=5, b=8 => "AFFINE CIPHER" -> "IHHWVC SWFRCP" (تحقق حسابيًا)
enc = affine.encrypt("AFFINECIPHER", 5, 8)
dec = affine.decrypt(enc, 5, 8)
check("affine roundtrip", dec == "AFFINECIPHER", f"(enc={enc})")
check("affine known value A->I with a=5,b=8", affine.encrypt("A", 5, 8) == "I")
try:
    affine.encrypt("TEST", 4, 3)  # gcd(4,26) != 1 لازم يفشل
    check("affine rejects invalid a", False)
except ValueError:
    check("affine rejects invalid a", True)

# ---------------- Rail Fence ----------------
# مثال معروف: "WEAREDISCOVEREDFLEEATONCE" بـ 3 قضبان -> "WECRLTEERDSOEEFEAOCAIVDEN"
check("railfence textbook example",
      rail_fence.encrypt("WEAREDISCOVEREDFLEEATONCE", 3) == "WECRLTEERDSOEEFEAOCAIVDEN")
check("railfence decrypt textbook example",
      rail_fence.decrypt("WECRLTEERDSOEEFEAOCAIVDEN", 3) == "WEAREDISCOVEREDFLEEATONCE")
check("railfence roundtrip random",
      rail_fence.decrypt(rail_fence.encrypt("Cybersecurity is fun!", 4), 4) == "Cybersecurity is fun!")

# ---------------- Autokey ----------------
check("autokey known example HELLO/KEY", autokey.encrypt("HELLO", "KEY") == "RIJSS")
enc_ak = autokey.encrypt("HELLO", "KEY")
dec_ak = autokey.decrypt(enc_ak, "KEY")
check("autokey roundtrip", dec_ak == "HELLO", f"(enc={enc_ak})")
enc_ak2 = autokey.encrypt("Attack at dawn, hurry!", "QUEEN")
dec_ak2 = autokey.decrypt(enc_ak2, "QUEEN")
check("autokey roundtrip with punctuation", dec_ak2 == "Attack at dawn, hurry!", f"(enc={enc_ak2})")

# ---------------- Playfair ----------------
# مثال معروف: key MONARCHY, plaintext INSTRUMENTS -> GATLMPBZWQDG (نسخة قياسية شائعة بالكتب)
enc_pf = playfair.encrypt("INSTRUMENTS", "MONARCHY")
dec_pf = playfair.decrypt(enc_pf, "MONARCHY")
check("playfair roundtrip", dec_pf.replace("X", "") in "INSTRUMENTSX" or dec_pf == "INSTRUMENTS",
      f"(enc={enc_pf}, dec={dec_pf})")
check("playfair grid preview 5x5", len(playfair.grid_preview("MONARCHY").split("\n")) == 5)

# ---------------- Hill Cipher (bonus) ----------------
check("hill cipher textbook example HELP->HIAT", hill_cipher.encrypt("HELP", (3, 3, 2, 5)) == "HIAT")
check("hill cipher decrypt roundtrip",
      hill_cipher.decrypt(hill_cipher.encrypt("HELP", (3, 3, 2, 5)), (3, 3, 2, 5)) == "HELP")
try:
    hill_cipher.encrypt("TEST", (2, 4, 6, 8))  # determinant غير صالح لازم يفشل
    check("hill cipher rejects invalid matrix", False)
except ValueError:
    check("hill cipher rejects invalid matrix", True)

# ---------------- Frequency analysis ----------------
freq = frequency_analysis.analyze("EEEAAABBC")
check("frequency analysis top letter", freq[0]["letter"] == "E" and freq[0]["count"] == 3)

print("=" * 60)
failed = [n for n, ok in results if not ok]
if failed:
    print(f"FAILED: {failed}")
    sys.exit(1)
print(f"ALL TESTS PASSED ({len(results)}/{len(results)})")

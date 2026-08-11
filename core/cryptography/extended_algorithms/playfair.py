# -*- coding: utf-8 -*-
"""
playfair.py

تشفير بلايفير — أشهر خوارزمية كلاسيكية تشفّر أزواج حروف (Digraphs) مو
حرف حرف، وهذا يخليها أقوى بكثير من الاستبدال الأحادي. تبني شبكة 5×5
من كلمة المفتاح (I و J يُعاملان كحرف واحد لأنه ما فيه مكان لـ 26 حرف
بشبكة 25 خانة).

ملاحظة مهمة (طبيعة الخوارزمية نفسها، مو قصور بالتنفيذ): بلايفير أصلًا
يشتغل على أحرف فقط بدون مسافات أو ترقيم، والناتج دايمًا أحرف كبيرة.
لو حرفين متكررين وقعوا بنفس الزوج نحط حرف حشو X بينهم، ولو طول النص
فردي نضيف X بالنهاية.
"""

GRID_SIZE = 5
FILLER = "X"


def _build_grid(key: str):
    key = key.upper().replace("J", "I")
    seen = []
    for ch in key:
        if ch.isalpha() and ch not in seen:
            seen.append(ch)
    for ch in "ABCDEFGHIKLMNOPQRSTUVWXYZ":  # بدون J (مدمج مع I)
        if ch not in seen:
            seen.append(ch)
    grid = [seen[i * GRID_SIZE:(i + 1) * GRID_SIZE] for i in range(GRID_SIZE)]
    positions = {ch: (r, c) for r, row in enumerate(grid) for c, ch in enumerate(row)}
    return grid, positions


def _prepare_digraphs(text: str):
    letters = [c.upper().replace("J", "I") for c in text if c.isalpha()]
    digraphs = []
    i = 0
    while i < len(letters):
        a = letters[i]
        if i + 1 < len(letters):
            b = letters[i + 1]
            if a == b:
                digraphs.append((a, FILLER))
                i += 1
            else:
                digraphs.append((a, b))
                i += 2
        else:
            digraphs.append((a, FILLER))
            i += 1
    return digraphs


def encrypt(text: str, key: str) -> str:
    grid, positions = _build_grid(key)
    digraphs = _prepare_digraphs(text)
    result = []

    for a, b in digraphs:
        ra, ca = positions[a]
        rb, cb = positions[b]
        if ra == rb:
            result.append(grid[ra][(ca + 1) % GRID_SIZE])
            result.append(grid[rb][(cb + 1) % GRID_SIZE])
        elif ca == cb:
            result.append(grid[(ra + 1) % GRID_SIZE][ca])
            result.append(grid[(rb + 1) % GRID_SIZE][cb])
        else:
            result.append(grid[ra][cb])
            result.append(grid[rb][ca])

    return "".join(result)


def decrypt(cipher: str, key: str) -> str:
    grid, positions = _build_grid(key)
    letters = [c.upper() for c in cipher if c.isalpha()]
    if len(letters) % 2 != 0:
        raise ValueError("نص التشفير المشفّر بـ Playfair لازم يكون طوله زوجي (أزواج حروف).")

    result = []
    for i in range(0, len(letters), 2):
        a, b = letters[i], letters[i + 1]
        ra, ca = positions[a]
        rb, cb = positions[b]
        if ra == rb:
            result.append(grid[ra][(ca - 1) % GRID_SIZE])
            result.append(grid[rb][(cb - 1) % GRID_SIZE])
        elif ca == cb:
            result.append(grid[(ra - 1) % GRID_SIZE][ca])
            result.append(grid[(rb - 1) % GRID_SIZE][cb])
        else:
            result.append(grid[ra][cb])
            result.append(grid[rb][ca])

    return "".join(result)


def grid_preview(key: str):
    """يرجّع الشبكة 5×5 كنص جاهز للعرض بالواجهة — يفيد الطالب يتحقق بصريًا."""
    grid, _ = _build_grid(key)
    return "\n".join(" ".join(row) for row in grid)

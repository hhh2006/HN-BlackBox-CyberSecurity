# -*- coding: utf-8 -*-
"""
frequency_analysis.py

أداة مساعدة لتحليل تكرار الحروف بنص معيّن — أساس أي هجوم تحليل شيفري
كلاسيكي (Cryptanalysis). كل لغة إلها بصمة تكرارية معروفة (بالإنجليزية
حرف E هو الأكثر تكرارًا مثلًا)، فلو شفت نص مشفّر وتكراره يشبه توزيع
لغة معينة بس بحروف مختلفة، هذا مؤشر قوي إنه تشفير استبدال بسيط
(زي القيصرية) وتقدر تخمّن المفتاح.
"""

from collections import Counter

ENGLISH_LETTER_FREQ = {
    "E": 12.70, "T": 9.06, "A": 8.17, "O": 7.51, "I": 6.97, "N": 6.75,
    "S": 6.33, "H": 6.09, "R": 5.99, "D": 4.25, "L": 4.03, "C": 2.78,
    "U": 2.76, "M": 2.41, "W": 2.36, "F": 2.23, "G": 2.02, "Y": 1.97,
    "P": 1.93, "B": 1.49, "V": 0.98, "K": 0.77, "J": 0.15, "X": 0.15,
    "Q": 0.10, "Z": 0.07,
}


def analyze(text: str):
    """يرجّع (عدد كل حرف, نسبته المئوية) لكل حرف أبجدي بالنص، مرتّبة من الأكثر تكرارًا."""
    letters = [c.upper() for c in text if c.isalpha()]
    total = len(letters)
    counts = Counter(letters)

    result = []
    for letter, count in counts.most_common():
        percent = (count / total * 100) if total else 0
        result.append({"letter": letter, "count": count, "percent": round(percent, 2)})
    return result

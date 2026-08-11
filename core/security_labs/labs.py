"""Offline CTF-style educational challenges with deterministic answers."""
LABS=[
 {"id":"CRYPTO-01","title":"Caesar Warmup","category":"Cryptography","difficulty":"Easy","prompt":"Decrypt: KHOOR using Caesar shift 3.","answer":"HELLO","hint":"Move each letter backward by 3."},
 {"id":"CRYPTO-02","title":"Frequency Detective","category":"Cryptanalysis","difficulty":"Easy","prompt":"Which letter is usually most frequent in English?","answer":"E","hint":"Think of common English plaintext."},
 {"id":"BLUE-01","title":"IOC Triage","category":"Blue Team","difficulty":"Easy","prompt":"What does IOC stand for in incident response?","answer":"INDICATOR OF COMPROMISE","hint":"It is evidence associated with malicious activity."},
 {"id":"NET-01","title":"Private IPv4","category":"Network","difficulty":"Easy","prompt":"Is 192.168.1.10 a private IPv4 address?","answer":"YES","hint":"It belongs to RFC1918 private space."},
]
def all_labs(): return LABS

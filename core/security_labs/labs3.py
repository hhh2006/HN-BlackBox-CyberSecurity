"""Offline, deterministic cybersecurity training labs. Safe by design."""
from __future__ import annotations
import base64, hashlib, ipaddress, json, urllib.parse

LABS=[
{"id":"CRYPTO-01","title":"Caesar Recovery","category":"Cryptography","difficulty":"Beginner","prompt":"Decrypt 'KHOOR' with a Caesar shift of 3. Enter the plaintext.","answer":"HELLO","hint":"Shift each letter three positions backward."},
{"id":"CRYPTO-02","title":"Base64 Recognition","category":"Encoding","difficulty":"Beginner","prompt":"Decode the Base64 value 'SE5fQkxBQ0tCT1g='.","answer":"HN_BLACKBOX","hint":"Use Base64 decoding; it is encoding, not encryption."},
{"id":"HASH-01","title":"Digest Identification","category":"Hashing","difficulty":"Beginner","prompt":"What algorithm is represented by a 64-character hexadecimal digest?", "answer":"SHA-256","hint":"Compare common digest lengths."},
{"id":"NET-01","title":"Private IPv4","category":"Network","difficulty":"Beginner","prompt":"Is 192.168.10.5 a private IPv4 address? Enter YES or NO.","answer":"YES","hint":"192.168.0.0/16 is RFC1918 private space."},
{"id":"NET-02","title":"Subnet Hosts","category":"Network","difficulty":"Intermediate","prompt":"How many usable IPv4 host addresses are in 192.168.50.0/28?", "answer":"14","hint":"A /28 has 16 addresses; reserve network and broadcast."},
{"id":"WEB-01","title":"Query Parsing","category":"Web Security","difficulty":"Beginner","prompt":"In /search?q=blackbox&page=2, what is the value of page?", "answer":"2","hint":"Parse the query string."},
{"id":"WEB-02","title":"Header Defense","category":"Web Security","difficulty":"Intermediate","prompt":"Name one header commonly used to reduce clickjacking risk.","answer":"X-FRAME-OPTIONS","hint":"It can restrict framing by other origins."},
{"id":"BLUE-01","title":"IOC Extraction","category":"Blue Team","difficulty":"Beginner","prompt":"From 'failed login from 203.0.113.9', enter the IPv4 IOC.","answer":"203.0.113.9","hint":"Look for the dotted-quad address."},
{"id":"BLUE-02","title":"Severity Triage","category":"Blue Team","difficulty":"Intermediate","prompt":"Five consecutive failed logins followed by success: choose LOW, MEDIUM, or HIGH.","answer":"MEDIUM","hint":"Repeated authentication failures warrant investigation but are not automatically critical."},
{"id":"FORENSIC-01","title":"File Integrity","category":"Forensics","difficulty":"Intermediate","prompt":"Which hash is recommended for a modern integrity record in BlackBox: MD5 or SHA-256?", "answer":"SHA-256","hint":"Prefer a modern collision-resistant digest."},
{"id":"LOG-01","title":"Alert Count","category":"Log Analysis","difficulty":"Beginner","prompt":"How many alert words are in: 'OK\nFAILED\nERROR\nOK'?", "answer":"2","hint":"Count FAILED and ERROR."},
{"id":"WEB-03","title":"URL Scheme","category":"Web Security","difficulty":"Beginner","prompt":"What scheme is used by https://example.local/login?", "answer":"HTTPS","hint":"Read the part before ://."},
]

def catalog(): return [dict(x) for x in LABS]

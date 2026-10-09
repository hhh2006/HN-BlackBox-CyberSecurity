"""HN BlackBox cryptography domain, organized by implementation family.

Canonical layout:
- classical/: classical cipher engines
- modern/: modern cipher/crypto engines
- steganography/: data-hiding engine
- visualization/: presentation-only visual models

Legacy module paths remain as compatibility shims so existing integrations and
third-party callers do not break while there is only one implementation source.
"""

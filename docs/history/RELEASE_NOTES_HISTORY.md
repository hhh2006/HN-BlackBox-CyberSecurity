# Release Notes History

Historical release notes retained from earlier development stages.

# HN BlackBox v14.0 — BlackBox Command Center

This is a cumulative release snapshot. Existing UI, navigation, visual identity, cryptography, network, web, blue-team, labs, history, workspace and performance work are preserved.

## Included in this snapshot
- Unified Command Center; Intelligence; Investigation; Evidence; Network; Blue Team; Labs controls; cumulative platform release.
- No external collection or remote scanning is introduced.
- The HN BlackBox visual language remains unchanged.

## Validation
- GUI/core test suite: 24 passed under Xvfb in the build environment.

---

HN BLACKBOX v16.0
FIELD LABS + REAL LOCAL TOOLKIT

This release keeps the existing visual identity and adds functional, local security utilities and a larger offline learning catalog.

New module:
  SECURITY TOOLKIT // FIELD CONSOLE

Tools:
  - File integrity hashing (MD5/SHA-1/SHA-256)
  - Base64 encoder/decoder
  - URL parser
  - JWT header/payload decoder (signature not verified)
  - Password entropy estimator
  - IOC extractor
  - Log summarizer

Labs:
  12 deterministic offline challenges across crypto, encoding, hashing, network, web, blue team, forensics and logs.

Safety:
  Utilities are local-only. No outbound scanning, exploitation, credential attacks, or external reputation lookups are performed.

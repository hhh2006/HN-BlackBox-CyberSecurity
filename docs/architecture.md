# Project Architecture

HN BlackBox is divided by responsibility instead of keeping every Python module directly under `core/`.

## Core sections

| Folder | Purpose |
|---|---|
| `core/cryptography/classical/required/` | Required classical rack: nine requested algorithms including keyed and double/combining transposition. |
| `core/cryptography/classical/additional/` | Additional classical/educational ciphers. |
| `core/cryptography/modern/` | AES, DES, RSA, and hashing. |
| `core/cryptography/steganography/` | Complete data-hiding/LSB engine. |
| `core/cryptography/visualization/` | Presentation-only crypto visualization helpers. |
| `core/cryptanalysis/` | Cipher analysis and statistical/frequency helpers. |
| `core/network_security/` | Network inspection, network intelligence, graphs, and network tools. |
| `core/web_security/` | Controlled web-security laboratory functionality. |
| `core/blue_team/` | Defensive rules, blue-team analysis, and blue-team workspace logic. |
| `core/security_labs/` | Offline labs, lab engine, scoring, progress, and lab catalogs. |
| `core/intelligence/` | Local investigation, evidence, intelligence, and analysis components. |
| `core/security_tools/` | Diagnostics, hardening, local tools, and vault/storage utilities. |
| `core/platform/` | Shared platform services such as workflows, history, plugins, reporting, and command-center aggregation. |

## Interface

`gui/app.py` contains the main desktop interface and connects the domain modules to the visual workspace. The animated dashboard is intentionally kept in the GUI layer so security logic remains separate from rendering code.

## Tests

`tests/` contains current automated tests. Historical capture/verification scripts that were useful during earlier development are kept under `tests/legacy_captures/` so they do not clutter the current test suite.

## Documentation

The root contains only the documents needed by a new contributor. Historical release notes are consolidated under `docs/history/`.

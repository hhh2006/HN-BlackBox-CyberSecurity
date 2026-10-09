# V40.0.0 — SOVEREIGN HOLOGRAPHIC OVERLAY

- Established V40.0.0 as the canonical public release identity.
- Preserved the existing WebGL2/GSAP/PixiJS/tsParticles cinematic stack and foreground-aware rendering model.
- Fixed the remaining 8pt HUD typography regression so the project readability floor is enforced.
- Updated CLI/runtime branding from the legacy v20.1 label to V40.0.0.
- Updated release gates and visual audit claims to the current 101-test / 127-Python-file state.
- Clarified that tactical renderer telemetry is synthetic visualization unless explicitly marked as local measured data.
- Removed duplicate unused icon assets from the release tree.
- Added the V40 release notes and preserved earlier V27/V28/v1.x history below.

# V27 — ALWAYS-ON VISUAL RUNTIME

- Removed page/visibility animation gating.
- Mounted all visual destinations at startup.
- Re-enabled dynamic shared cinematic surfaces.
- Added per-channel exception isolation so one broken HUD callback cannot freeze the master compositor.
- Preserved WebGL2 RAF + telemetry/hex interval buses.
- No cryptography implementation changes.


## V17 — V6 Header Refinement
- Restored the cleaner V6-style telemetry header proportions.
- Replaced bulky destination buttons with a compact interactive command rail.
- Preserved destination navigation while reducing visual clutter and Canvas work.
- Kept live scan/radar/activity/sequence VFX on the retained global animation clock.
# HN BlackBox CyberSecurity — Changelog

## v1.8.2 — Responsive UI & Readability Validation

- Completed a project-wide visual audit at 1024×768 and 1280×820 class window sizes.
- Raised the production minimum window size to 1024×700 so content is not rendered into an unreadably compressed viewport.
- Added responsive two-pane stacking for Modern Crypto workspaces and the Steganography lower analysis panels.
- Preserved the existing compact sidebar behavior while preventing fixed-width content panes from forcing horizontal reading/zooming.
- Increased the top-bar height to keep the project readability floor comfortable at normal Windows scaling.
- Added resize-cycle regression coverage and deterministic GUI teardown that cancels Tk timers before destruction.
- Refactored the GUI smoke test into a normal pytest test so the complete suite can execute cleanly.


## v1.8.1 — Global Readability & Accessibility Pass

- Raised all explicit UI fonts below the project readability floor: MONO 9pt minimum, FONT 10pt minimum, and ASCII_MONO 10pt minimum.
- Applied the typography pass across Dashboard, navigation, telemetry, cryptography, modern crypto, steganography, analysis, network, web, labs, reports, settings, and developer surfaces.
- Preserved intentionally large display titles and cinematic branding sizes.
- Added a regression test that enforces the font-size floor for future UI changes.
- Verified the updated application with the full GUI-capable test suite.

## v1.7.4 — Crypto UX & Steganography Stabilization

- Fixed the missing `GUIDES` entries that prevented Keyed Transposition and Double / Combining Transposition labs from opening.
- Verified both transposition labs open through the GUI and expose the correct key fields.
- Removed the cinematic Welcome Screen completely; the application now starts directly in the command-center dashboard.
- Rebuilt the Steganography workspace around the requested Original / With Hidden Data comparison: image previews, message payload, capacity, hidden bytes, format/status, hide/extract controls and pixel analysis.
- Added regression tests for keyed transposition, double transposition, PNG LSB roundtrip and capacity validation.
- Release checks: 35 non-GUI tests PASS and 6 GUI tests PASS under Xvfb.

## v1.7.2 — Runtime & Interaction Stabilization

- Removed the beta gateway from shipped modules; available modules now open directly.
- Reduced Welcome HUD Canvas churn and animation load for smoother Tkinter rendering.
- Fixed the visual PLAY button reference so its widget remains addressable after creation.
- Updated GUI regression coverage for direct module navigation.
- Earlier release validation: 36/36 automated tests PASS (superseded by the current 61/61 gate).
- Existing one-time Windows dependency bootstrap remains in place; unchanged requirements reuse the existing local environment.


## v1.7.1 — Reference Welcome Experience

- Replaced the previous vector-only landing screen with the supplied HN BlackBox reference artwork as the actual welcome background.
- Added live Tkinter HUD overlays: scanline, floating particles, orbital markers, status rail, click/keyboard entry.
- Welcome screen now runs immersive/full-window without the normal sidebar chrome.
- Added a reusable Windows launcher environment under `%LOCALAPPDATA%\HNBlackBox\venv`; dependencies are installed only on first run or when `requirements.txt` changes.
- `run_blackbox.bat` and `run_windows.bat` now reuse the same environment across project upgrades.

# Changelog

## v1.7.0 — Final Release Gate
- Final QA pass for the crypto upgrade.
- Fixed Classical Matrix card guide lookup for newly added transposition algorithms.
- Updated GUI regression expectation to the expanded 9-item Required Ciphers set.
- Verified Python compilation and full GUI test suite under Xvfb.

# HN BlackBox — Crypto Evolution Upgrade

## 2026-09-06
- Added modern DES educational engine: 64-bit key validation, CBC mode, PKCS#7 padding, 16-round Feistel implementation, key-schedule trace, and known-vector test coverage.
- Added LSB steganography for PNG/BMP with capacity calculation, UTF-8 payloads, CRC32 integrity validation, and invalid/corrupt input handling.
- Added Keyed Transposition and Double/Combining Transposition to the classical cipher matrix.
- Added dedicated Classical / Modern Security / Steganography tabs with a consistent HN BlackBox cyberpunk visual language.
- Added DES cinematic round visualizer and steganography operational panels.
- Classical set now exposes Required / Added / Full collections.
- Added focused cryptography upgrade tests.

# Changelog

## 20.1 — Public Portfolio Release

- Reorganized the core codebase by cybersecurity domain.
- Isolated the seven requested cryptography algorithms in `core/cryptography/required_algorithms/`.
- Kept additional cipher implementations under `core/cryptography/extended_algorithms/`.
- Consolidated historical release notes under `docs/history/`.
- Moved legacy capture scripts into `tests/legacy_captures/`.
- Added GitHub-oriented documentation and development guidance.
- Updated the cryptography test expectations to the current seven-algorithm requested set.
- Preserved the existing GUI design and animated visual language.

## Previous development

The detailed historical record is preserved in [`docs/history/CHANGELOG_HISTORY.md`](docs/history/CHANGELOG_HISTORY.md).

## Crypto Upgrade v1.2 — Bit-Plane Forensics
- Added deterministic LSB bit-plane inspection API.
- Added RGB bit-plane density visualization and raw LSB stream inspector.
- Added source-image preview and embedded-payload metadata panel.
- Preserved PNG/BMP-only validation and existing encode/decode behavior.
- Added automated inspector coverage.

## v1.3 — DES Deep Trace
- Added real per-round DES execution tracing: IP, L/R state, Expansion, XOR, S-Box, P permutation, and round outputs.
- Modern DES visualizer now consumes the real first-block Feistel trace instead of displaying key-schedule data only.
- Added decrypt-side block tracing with reversed subkeys.
- Non-GUI regression suite: 27/27 passed.

## Crypto Upgrade v1.4 — Classical Cinematic Engine
- Added `core/cryptography/classical_visuals.py` as a presentation-only visual model layer.
- Added algorithm-specific visual treatment for Caesar, Additive, Multiplicative, Affine, Vigenere, Autokey, Beaufort, Atbash and ROT13.
- Added matrix/ranking visualization for Columnar, Keyed Transposition and Double Transposition.
- Visual data is derived from the current input, result and key fields; it does not perform a second encryption implementation.
- Added explicit formulas and operation labels to reduce decorative-only visualization.
- Regression suite: 18 tests passed.

## v1.7.1 — Cinematic Welcome Experience
- Added a dedicated animated HN BlackBox welcome/landing screen inspired by the supplied visual direction.
- Added vector HUD grid, central HN shield, rotating radial markers, live status cards, local uptime and release indicators.
- Added interactive `ENTER COMMAND CENTER` action and Enter-key shortcut into the existing dashboard.
- Added a dashboard `WELCOME SCREEN` return action.
- Kept the landing screen local-only and data-honest: no fabricated external intelligence or threat events.
- Added GUI regression coverage for the welcome screen and navigation path.

## v1.8.0 — Modern Crypto Command Center
- Rebuilt the Modern Security area as a real multi-primitive command center: DES, AES-256, RSA, and hashing.
- Added algorithm-specific control panels, clear operation labels, educational explanations, visual pipelines, and execution traces.
- DES now presents its real 16-round Feistel trace with IP/round/FP flow and per-round values.
- AES-256, RSA, and SHA-family operations use the existing local engines; visualizations explicitly distinguish model/flow views from engine output.
- Added regression-accessible `_modern_context` bindings for GUI validation of real operations.
- Kept the project dependency-light by retaining Tkinter rather than introducing a second GUI framework.
- Accessibility/font sizing is intentionally scheduled as a separate project-wide phase and is not mixed into this release.

## 2026-09-07 — Command Core / File Intelligence Hardening
- Reworked the Home dashboard around a single vector-rendered Operations Command Core with radar, live local telemetry, packet flow, module nodes, tactical feed and interactive routing.
- Reduced high-frequency dashboard animation timers to lower Tkinter CPU/event-loop pressure during normal use and resize cycles.
- Added OSINT / File Intelligence as a local read-only forensic module for image/PDF/other-file metadata, signatures, SHA-256/SHA-1/MD5 fingerprints, entropy and bounded printable-string triage.
- File analysis runs in a dedicated worker executor so the UI event loop is not blocked by hashing/parsing.
- Corrected AES educational visualization/documentation from legacy CBC/IV wording to the actual AES-256-GCM/AEAD design used by the hardened engine.
- Added regression coverage for the File Intelligence module and preserved the existing cryptographic regression suite.

## 2026-09-07 — Shared HUD Compositor / Visual Polish
- Added one shared low-cost HUD compositor for glass/tech panels across the GUI.
- Added clipped/octagonal rails, layered dark-depth surfaces, sparse internal grid, corner telemetry and a moving laser scan.
- Replaced the legacy ASCII identity block on the Home command channel with a clean vector HN core mark.
- Kept the existing Tkinter runtime and crypto/stego architecture intact; no forced framework migration or new runtime dependency was introduced.


### 2026-09-07 — GUI Architecture Hardening / Zero-Lag Event Path
- Replaced startup construction of every screen with lazy page factories; first-frame startup no longer builds the complete application tree.
- Added a single retained-mode ~30 FPS HUD animation clock for the main command dashboard instead of multiple recurring Home timers.
- Added a thread-safe worker-to-Tk event queue. Background workers never call tkinter directly.
- Moved system telemetry, project test execution and blocking diagnostics/DNS/deep-analysis work off the GUI event loop.
- Added real input-activity laser pulse and retained vector HUD motion validation.
- Full automated validation: 64/64 tests PASS.

### 2026-09-07 — Modern Crypto + Steganography HUD Rebuild
- Rebuilt the Modern Security screen with a low-intensity Matrix data-rain layer and retained-mode live motion.
- Added laser signal rails to Modern Crypto input/output panels; typing triggers a short high-energy pulse.
- Rebuilt the Steganography intake surface as an interactive Cyber Scanner with an actual vertical scan laser.
- Added live file metadata/fingerprint cards and moved stego forensic inspection plus file fingerprint hashing to background workers.
- Preserved the existing cryptography backend and `ui/runtime` source unchanged.
- Full validation: 64/64 tests passed; 98 Python files parsed successfully with AST.

## Cinematic WebGL Renderer — 2026-09-07

- Added an optional GPU-accelerated renderer under `renderer/`.
- Pinned current production versions: Three.js 0.185.1, GSAP 3.15.0, PixiJS 8.20.1, tsParticles Slim 4.4.0, Vite 8.2.2.
- Modern Security and Steganography pages expose one-click Cinematic Core / Scanner launchers.
- Added adaptive performance controls: capped device pixel ratio, reduced particle density, hidden-tab pause, and automatic quality downgrade when sustained FPS drops.
- Added optional `pywebview==6.2.1` integration; native Tk remains the deterministic fallback.
- Python crypto/stego engines and `ui/runtime` remain unchanged.

## Current Gate — 2026-09-07

- Cinematic WebGL renderer configured: Three.js 0.185.1, GSAP 3.15.0, PixiJS 8.20.1, tsParticles Slim 4.4.0, Vite 8.2.2.
- Optional pywebview 6.2.1 bridge with native Tk fallback.
- Full automated validation: 67/67 tests PASS; 100 Python files parse successfully with AST.
- Core crypto and `ui/runtime` source remain unchanged versus the baseline.

## 2026-09-08 — Real-File Forensics / OSINT activation

- Replaced the OSINT file-analysis presentation path with a real local forensic engine.
- Added complete-file MD5/SHA-1/SHA-256 fingerprinting and bounded entropy/string triage.
- Added image EXIF/PNG metadata extraction, PDF info/XMP inspection, and OOXML property extraction.
- Added metadata-aware selective scrubbing and full embedded-metadata stripping to a separate clean derivative.
- Refused source overwrite during scrub operations.
- Moved the forensic radar into the shared ~60 FPS animation clock so analysis cannot stop the HUD animation loop.
- Added explicit CLEAR/reset handling and worker-to-Tk event marshalling.
- Added `pypdf>=5.0` dependency and dedicated real-file forensic regression tests.

# HN BlackBox — UI Readability & Responsive Layout Audit

## Scope

This pass audits the desktop GUI independently from cryptographic engine changes. The goal is to keep controls, explanations, results, and navigation readable without requiring the user to zoom or rely on an unusually large monitor.

## Production baseline

- Minimum window size: **1024×700**.
- Explicit typography floor: **MONO 9pt**, **FONT 10pt**, **ASCII_MONO 10pt**.
- Navigation collapses to a compact icon rail below the desktop content threshold.
- Selected two-pane workspaces stack vertically when their content area becomes compact.
- Long content remains inside scrollable page canvases where applicable.

## Responsive surfaces validated

- Dashboard
- Cryptography matrix
- Modern Security / DES / AES / RSA / Hash workspaces
- Steganography
- Cryptanalysis
- Network Security
- Security Labs
- Security Toolkit
- Developer / History surfaces
- Processing / live algorithm lab

## Validation

- Core/crypto regression suite: **35 passed**.
- GUI feature + Modern Crypto + responsive + UI regression suite: **13 passed** under Xvfb.
- GUI smoke workflow: **PASS** as an isolated Windows-style GUI smoke script.
- Python compilation: **PASS**.

The GUI checks are intentionally executed in isolated groups because Tk applications create native GUI resources; keeping GUI suites isolated avoids cross-test contamination while preserving deterministic coverage.

## Design rule for future changes

Do not introduce a smaller explicit font merely to make a panel fit. Prefer, in order:

1. responsive stacking;
2. wrapping / scrolling;
3. shorter labels with clear tooltips or guides;
4. only then a layout-specific size adjustment that remains above the project typography floor.

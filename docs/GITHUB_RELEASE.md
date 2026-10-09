# GitHub Release Playbook — V40.0.0

## Repository identity

- **Repository:** `hhh2006/HN-BlackBox-CyberSecurity`
- **Release:** `v40.0.0`
- **Codename:** `SOVEREIGN HOLOGRAPHIC OVERLAY`
- **License:** MIT
- **Primary language:** Python
- **Desktop stack:** Python + Tkinter/CustomTkinter
- **Cinematic renderer:** WebGL2 / Three.js / GSAP / PixiJS / tsParticles

## Recommended repository description

> Local-first cybersecurity learning & engineering command center for cryptography, cryptanalysis, network security, blue-team workflows, security labs, and cinematic security visualization.

## Recommended topics

```text
cybersecurity
cyber-security
information-security
cryptography
cryptanalysis
python
tkinter
security-tools
blue-team
network-security
web-security
cybersecurity-education
security-labs
ethical-hacking
student-project
webgl
threejs
```

## First public release

The public repository should contain the complete V40 source tree, not only the ZIP artifact. The ZIP is the reproducible release artifact and should be attached to the GitHub Release.

Suggested commit message:

```text
release: HN BlackBox v40.0.0
```

Suggested tag:

```text
v40.0.0
```

Suggested release title:

```text
HN BlackBox v40.0.0 — SOVEREIGN HOLOGRAPHIC OVERLAY
```

## Release asset

Attach:

```text
HN-BlackBox-v40.0.0-SOVEREIGN-HOLOGRAPHIC-OVERLAY.zip
```

The SHA-256 is published with the release asset so it can be verified independently.

## GitHub Pages

The browser-native cinematic preview lives in `docs/site/` and is deployed by `.github/workflows/pages.yml`.

After the first push:

1. Open **Settings → Pages**.
2. Confirm the source is **GitHub Actions** if GitHub requests a Pages source selection.
3. Wait for the Pages workflow to finish.
4. Open the generated Pages URL and verify the animation on desktop and mobile widths.

## Repository presentation

- Keep the README hero above the fold.
- Keep the current screenshots in `docs/screenshots/`.
- Use `docs/screenshots/social-preview.png` as the repository social preview.
- Pin the repository to the GitHub profile.
- Enable Issues and Discussions only if they will be actively maintained.
- Keep release notes factual and tied to implemented features.

## Verification before publishing

```bash
python -m compileall -q core gui ui
xvfb-run -a python -m pytest -q
node --check renderer/src/main.js
```

Expected release verification for V40.0.0:

```text
101 passed
Python compile check: PASS
Renderer syntax check: PASS
Archive integrity: PASS
```

## Important disclosure

The cinematic HUD and browser preview may display synthetic telemetry for visual presentation. Synthetic values must not be described as live network measurements unless a specific module explicitly reports measured local data.

DES is retained for educational interoperability and visualization. It must not be presented as a modern production encryption primitive.

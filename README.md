# HN BlackBox CyberSecurity

**HN BlackBox** is my cybersecurity learning and engineering project. I built it to turn the topics I study into practical software that I can test, improve, and keep using as I learn more.

The project brings several areas together in one desktop workspace: cryptography, cryptanalysis, network security, web-security labs, blue-team exercises, security tools, local intelligence, and hands-on labs.

> **Educational / defensive use:** only test systems, applications, networks, and data that you own or are explicitly authorized to test.

## Highlights

- **Cryptography:** classical ciphers, extended algorithms, AES utilities, and algorithm-focused visual explanations.
- **Cryptanalysis:** frequency analysis, coincidence analysis, Kasiski-style analysis, and related tools.
- **Modern Security:** DES, AES-256, RSA, hashing, and step-by-step teaching views.
- **Steganography:** image-based LSB hiding/extraction with pixel and payload analysis.
- **Network Security:** local network inspection, diagnostics, graphs, and defensive utilities.
- **Web Security:** controlled educational web-security labs.
- **Blue Team:** defensive analysis, rules, and investigation workflows.
- **Security Labs:** deterministic offline labs with progress, hints, attempts, and scoring.
- **File Intelligence:** hashes, metadata, entropy, strings, and related local analysis.
- **Desktop GUI:** a dark HN command-center interface with animated visual effects and live local status views.
- **CLI / Console:** local command-line workflows for Windows and Linux/Kali.

## Cryptography

The core requested classical algorithms are kept together under `core/cryptography/required_algorithms/`:

```text
caesar.py
additive.py
multiplicative.py
affine.py
vigenere.py
autokey.py
rail_fence.py
```

The application also exposes additional classical and modern algorithms through the extended/full views.

## Project layout

```text
core/                  Core security and cryptography logic
gui/                   Desktop application
renderer/              WebGL2 cinematic renderer
tests/                 Automated tests
docs/                  Current documentation and project history
docs/site/             GitHub Pages visual site
assets/                Application assets
plugins/               Plugin area
main.py                GUI entry point
blackbox_cli.py        CLI entry point
blackbox_console.py    Interactive console
```

More details are in [`docs/architecture.md`](docs/architecture.md).

## Run it

### Windows

The easiest option is:

```text
run_windows.bat
```

For the desktop application directly:

```bash
python main.py
```

### CLI

```bash
python blackbox_cli.py --help
```

### Interactive console

```bash
python blackbox_console.py
```

### Linux / Kali

```bash
./run_blackbox_cli.sh
```

## Installation

Python 3.11 or newer is recommended.

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Then install the Python dependencies:

```bash
pip install -r requirements.txt
```

The optional WebGL renderer has its own Node/Vite dependencies in `renderer/`.

## Testing

Run the test suite with:

```bash
pytest -q
```

The project is tested locally and in CI. GUI tests on Linux can run under Xvfb.

## Visual renderer

The cinematic layer uses WebGL2 with Three.js, GSAP, PixiJS, and tsParticles. It is a presentation layer; cryptographic operations remain in the Python application and are not replaced by browser-side mock implementations.

The GitHub Pages site contains a visual demonstration. Telemetry shown there is synthetic presentation data unless explicitly identified as a real local measurement.

## Project history

HN BlackBox has gone through several internal iterations. The current public release is **V40.0.0 — SOVEREIGN HOLOGRAPHIC OVERLAY**.

Older development notes are kept in [`docs/history/`](docs/history/) where they are useful for understanding how the project evolved. The current documentation describes V40 rather than those earlier iterations.

See [`CHANGELOG.md`](CHANGELOG.md) for the consolidated release history.

## Author

**Hani Khaled Nasser Al-Nasseri**  
Cybersecurity Student & Developer

This is a personal long-term project that I develop while studying cybersecurity and building practical experience.

- Email: `alnasryhany185@gmail.com`
- GitHub: `hhh2006`

## Contributing

Bug reports, improvements, and pull requests are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Security

For security issues, please read [`SECURITY.md`](SECURITY.md) before opening a public issue.

## License

MIT License. See [`LICENSE`](LICENSE).

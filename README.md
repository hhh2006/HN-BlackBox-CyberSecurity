# HN BlackBox // CyberSecurity

**A local-first cybersecurity learning and engineering workspace built by Hani Khaled Nasser Al-Nasseri (HN).**

HN BlackBox started as a student project for learning cybersecurity and turning university assignments and difficult technical topics into practical software. It has grown into a modular workspace covering cryptography, cryptanalysis, network security, web-security labs, blue-team exercises, security tooling, local intelligence, and hands-on labs.

The project is intentionally built to keep growing: new concepts, university projects, experiments, and tools can be added without turning the whole codebase into one large file.

> **Educational / defensive scope:** use the project only on systems, networks, applications, and data that you own or are explicitly authorized to test.

## What is inside?

- **Cryptography** — classical ciphers, AES utilities, and an organized algorithm matrix.
- **Requested cipher set** — Caesar, Additive, Multiplicative, Affine, Vigenère, Autokey, and Rail Fence in one dedicated folder.
- **Cryptanalysis** — frequency analysis, coincidence analysis, Kasiski-style analysis, and related helpers.
- **Network Security** — local network inspection, network graphs, and defensive utilities.
- **Web Security** — controlled educational web-security lab functionality.
- **Blue Team** — defensive rules, analysis helpers, and blue-team workflows.
- **Security Labs** — deterministic offline labs, progress tracking, hints, and scoring.
- **Intelligence** — local investigation, evidence, and intelligence-oriented analysis modules.
- **Security Tools** — diagnostics, hardening helpers, local tooling, and encrypted storage utilities.
- **Platform** — history, workflows, plugins, reporting, and command-center components.
- **Live GUI** — an animated cybersecurity operations-style interface built with Tkinter/CustomTkinter.
- **CLI / Console** — command-line and allow-listed terminal workflows for local use.

## Cryptography organization

The seven requested algorithms live here:

```text
core/
└── cryptography/
    ├── required_algorithms/
    │   ├── caesar.py
    │   ├── additive.py
    │   ├── multiplicative.py
    │   ├── affine.py
    │   ├── vigenere.py
    │   ├── autokey.py
    │   └── rail_fence.py
    └── extended_algorithms/
        ├── aes_cipher.py
        ├── classical.py
        ├── hill_cipher.py
        ├── playfair.py
        └── additional cipher implementations
```

The other cryptography options remain available through the **Extended** and **Full** views in the application.

## Project structure

```text
HN-BlackBox-CyberSecurity/
├── core/
│   ├── cryptography/
│   ├── cryptanalysis/
│   ├── network_security/
│   ├── web_security/
│   ├── blue_team/
│   ├── security_labs/
│   ├── intelligence/
│   ├── security_tools/
│   └── platform/
├── gui/
├── tests/
├── assets/
├── docs/
├── plugins/
├── main.py
├── blackbox_cli.py
├── blackbox_console.py
└── requirements.txt
```

A full explanation of the folders is available in [`docs/architecture.md`](docs/architecture.md).

## Run the project

### Python GUI

```bash
python main.py
```

### Windows launcher

```text
run_windows.bat
```

### CLI

```bash
python blackbox_cli.py --help
```

### Interactive console

```bash
python blackbox_console.py
```

Linux/Kali launcher:

```bash
./run_blackbox_cli.sh
```

## Installation

Python 3.11+ is recommended.

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

Then:

```bash
pip install -r requirements.txt
```

## Testing

The project includes core, GUI, cipher, lab, and tooling tests.

```bash
pytest -q
```

On Linux CI, the GUI tests can run under Xvfb.

## Why I built it

I am **Hani Khaled Nasser Al-Nasseri**, a cybersecurity student at **Al-Razi University in Yemen**. HN BlackBox is my long-term learning and engineering project. I use it to practice what I study, turn university work into reusable software, and keep difficult cybersecurity concepts in one place where I can continue improving them.

The goal is not to present a finished commercial security product. The goal is to build a serious portfolio project that demonstrates continuous learning, software engineering, cybersecurity fundamentals, testing, documentation, and the ability to grow a codebase over time.

## Author

**Hani Khaled Nasser Al-Nasseri**  
*Cybersecurity Student & Developer*

HN BlackBox CyberSecurity is developed and maintained as a long-term cybersecurity learning and engineering project.

### Contact & Contributions

If you would like to contribute, report a bug, suggest an improvement, or discuss collaboration:

- **Email:** alnasryhany185@gmail.com
- **GitHub:** Use Issues and Pull Requests in this repository.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution guidelines.

## Roadmap

The project is intentionally open-ended. Planned areas include stronger cryptography education, deeper network analysis, additional defensive labs, better reporting, more automated tests, improved plugin architecture, and additional blue-team workflows.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Security

See [`SECURITY.md`](SECURITY.md).

## License

MIT License. See [`LICENSE`](LICENSE).

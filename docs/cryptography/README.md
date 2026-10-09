# Cryptography module layout

```text
core/cryptography/
├── classical/
│   ├── required/
│   └── additional/
├── modern/
├── steganography/
└── visualization/
```

The required classical rack contains the nine requested algorithms. The additional rack contains the rest of the classical/educational ciphers. Modern cryptography is isolated under `modern/`, and steganography has its own complete engine directory.

There are no legacy duplicate implementation/shim trees in the release package.

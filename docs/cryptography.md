# Cryptography Map

## Required classical rack

`core/cryptography/classical/required/` contains the requested set:

1. Caesar
2. Additive
3. Multiplicative
4. Affine
5. Vigenère
6. Autokey
7. Rail Fence (keyless transposition)
8. Keyed Transposition
9. Double / Combining Transposition

## Additional classical rack

`core/cryptography/classical/additional/` contains the remaining classical/educational ciphers: Playfair, Hill, Atbash, ROT13, Beaufort, Polybius, ADFGVX, Bacon, Morse, and OTP.

## Modern rack

`core/cryptography/modern/` contains AES, DES, educational RSA, secure RSA, and hashing.

## Data hiding and visualization

`core/cryptography/steganography/` contains the complete LSB data-hiding engine.
`core/cryptography/visualization/` contains presentation-only crypto visualizations.

There is one canonical implementation location per algorithm; legacy duplicate engine trees were removed during V18 cleanup.

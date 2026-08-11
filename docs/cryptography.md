# Cryptography Map

## Requested algorithms

The main requested set is intentionally isolated under:

`core/cryptography/required_algorithms/`

It contains:

1. Caesar
2. Additive
3. Multiplicative
4. Affine
5. Vigenère
6. Autokey
7. Rail Fence

## Extended algorithms

Additional implementations live under:

`core/cryptography/extended_algorithms/`

This separation makes it possible to change the requested university-learning set without disturbing the rest of the cipher library.

The cryptography UI exposes the requested, extended, and full algorithm views separately.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hn_blackbox_cli.py

Command-line interface for automation and quick testing without opening the GUI.

Examples:
    python hn_blackbox_cli.py caesar encrypt "HELLO" --key 3
    python hn_blackbox_cli.py vigenere decrypt "LXFOPVEFRNHR" --key LEMON
    python hn_blackbox_cli.py affine encrypt "AFFINE" --a 5 --b 8
    python hn_blackbox_cli.py railfence encrypt "WEAREDISCOVERED" --key 3
    python hn_blackbox_cli.py hill encrypt "HELP" --matrix 3 3 2 5
    python hn_blackbox_cli.py caesar crack "KHOOR"
"""

import argparse
import sys
import getpass

from core import caesar, vigenere, affine, rail_fence, autokey, playfair, hill_cipher

SIMPLE_KEY_ALGOS = {"vigenere": vigenere, "autokey": autokey, "playfair": playfair}
INT_KEY_ALGOS = {"caesar": caesar, "railfence": rail_fence}


def banner():
    user = (getpass.getuser() or "HN USER").upper()
    print("\033[96m╔════════════════════════════════════════════════════╗")
    print("║  HN // HN BLACKBOX   •   SECURITY WORKSPACE         ║")
    print(f"║  OPERATOR: {user:<40}║")
    print("║  STATUS: ONLINE     MODE: EDUCATIONAL / LOCAL     ║")
    print("╚════════════════════════════════════════════════════╝\033[0m")


def main():
    banner()
    parser = argparse.ArgumentParser(description="HN BlackBox CLI - Classical encryption and decryption")
    sub = parser.add_subparsers(dest="algorithm", required=True)

    for name in list(SIMPLE_KEY_ALGOS) + list(INT_KEY_ALGOS):
        p = sub.add_parser(name)
        p.add_argument("operation", choices=["encrypt", "decrypt"])
        p.add_argument("text")
        p.add_argument("--key", required=True)

    affine_p = sub.add_parser("affine")
    affine_p.add_argument("operation", choices=["encrypt", "decrypt"])
    affine_p.add_argument("text")
    affine_p.add_argument("--a", type=int, required=True)
    affine_p.add_argument("--b", type=int, required=True)

    hill_p = sub.add_parser("hill")
    hill_p.add_argument("operation", choices=["encrypt", "decrypt"])
    hill_p.add_argument("text")
    hill_p.add_argument("--matrix", type=int, nargs=4, required=True, metavar=("a", "b", "c", "d"))

    crack_p = sub.add_parser("crack-caesar", help="Break Caesar without knowing the key")
    crack_p.add_argument("text")

    args = parser.parse_args()

    try:
        if args.algorithm == "crack-caesar":
            for key, guess in caesar.brute_force(args.text):
                print(f"KEY {key:>2}: {guess}")
            return

        if args.algorithm == "affine":
            fn = affine.encrypt if args.operation == "encrypt" else affine.decrypt
            print(fn(args.text, args.a, args.b))
            return

        if args.algorithm == "hill":
            fn = hill_cipher.encrypt if args.operation == "encrypt" else hill_cipher.decrypt
            print(fn(args.text, tuple(args.matrix)))
            return

        if args.algorithm in INT_KEY_ALGOS:
            module = INT_KEY_ALGOS[args.algorithm]
            key = int(args.key)
        else:
            module = SIMPLE_KEY_ALGOS[args.algorithm]
            key = args.key

        fn = module.encrypt if args.operation == "encrypt" else module.decrypt
        print(fn(args.text, key))

    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

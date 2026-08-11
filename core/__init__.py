"""HN BlackBox core package.

The package keeps the public module names stable while implementations are
organized by domain for easier maintenance and contribution.
"""

# Cryptography
from .cryptography.extended_algorithms import (
    affine, autokey, caesar, vigenere, rail_fence, aes_cipher,
    classical, hill_cipher, playfair,
)

# Analysis
from .cryptanalysis import cryptanalysis, frequency_analysis, crypto_intel

# Security domains
from .network_security import network_tools, network_graph, network_intel
from .web_security import web_lab
from .blue_team import blue_team, blue_center, blue_rules
from .security_labs import labs, labs2, labs3, lab_engine, lab_progress
from .intelligence import intelligence, investigation, evidence, pro_intelligence
from .security_tools import real_tools, security_hardening, vault, diagnostics
from .platform import (
    command_center, history_manager, plugin_system, reporting,
    workflows, workflow_engine,
)

__all__ = [
    "affine", "autokey", "caesar", "vigenere", "rail_fence", "aes_cipher",
    "classical", "hill_cipher", "playfair", "cryptanalysis", "frequency_analysis",
    "crypto_intel", "network_tools", "network_graph", "network_intel", "web_lab",
    "blue_team", "blue_center", "blue_rules", "labs", "labs2", "labs3",
    "lab_engine", "lab_progress", "intelligence", "investigation", "evidence",
    "pro_intelligence", "real_tools", "security_hardening", "vault", "diagnostics",
    "command_center", "history_manager", "plugin_system", "reporting", "workflows",
    "workflow_engine",
]

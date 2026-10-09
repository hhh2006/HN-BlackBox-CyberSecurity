# Modern Crypto Visual Cleanup — V9

The modern cryptography command center now uses one authoritative teaching visualization per algorithm.

## Removed duplication
- Disabled the cinematic overlay that was drawing a second pipeline over the teaching diagram.
- Removed the second Matrix rain layer inside the live visualization canvas.
- Removed duplicate AES state/round-pipeline drawing from `visual_models.py` when the modern page already renders its own authoritative model.
- Removed duplicate RSA and HASH overlay models from the same path.

## Runtime behavior
- Real cryptographic execution remains unchanged.
- This cleanup is presentation-only; cipher implementation modules were not modified.
- The modern visualization still responds to the actual operation state and step controls.
- The global animation clock remains the only continuous animation scheduler for this page.

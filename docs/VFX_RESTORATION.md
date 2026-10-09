# VFX Restoration

This release intentionally preserves the full cinematic visual layer from V10 while retaining the V11 crypto directory organization.

Preserved visual systems include:
- Modern Crypto cinematic pipeline, particles, rails, pulses, stage gates, Matrix/Hex streams, and replay/step controls.
- Shared cinematic surfaces and global animation clock.
- Home HUD visual systems.
- OSINT/Forensics HUD and radar.
- Network diagnostics HUD.
- Existing specialist visualizations across the remaining labs.

No cryptographic implementation code was changed as part of this restoration.
No visual system was removed to solve performance issues; performance work must be done by lifecycle/retained-rendering/backend-style scheduling rather than deleting the visual language.

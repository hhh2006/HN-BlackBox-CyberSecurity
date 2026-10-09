# HN BLACKBOX — Shared Cinematic VFX Language

V7 extends the cinematic visual language beyond the cryptography cinema.

## Shared visual grammar

- Dark glass substrate with clipped/cut-corner technical framing.
- Neon accent rails, scan sweeps, moving data pulses and node matrices.
- Autonomous motion driven by the single application animation clock (~60 FPS).
- No mouse hover is used as an animation driver.
- Hidden pages stop consuming frame work; visible pages resume automatically.
- VFX are presentation-only and do not fabricate operational telemetry.

## Coverage

The shared background compositor is mounted on Home and every lazily-created laboratory/module page, including OSINT/File Intelligence, Network Diagnostics, Cryptanalysis, Web, Blue Team, Labs, Toolkit, Developer, Development and History screens.

Existing specialist HUDs remain intact and can render above the shared layer. This keeps the crypto cinema, network diagnostics, file forensics radar and other module-specific visualizations distinct while giving the platform one coherent visual identity.

## Performance / Layering Guardrails (V8)

- Home does **not** mount a second full-screen cinematic canvas behind its dedicated HUDs.
- Shared cinematic surfaces on secondary pages are a **static substrate** (grid + cut-corner frame) only; specialist canvases own animated motion.
- The old recurring heading-level Canvas timer was removed; headings render once and no longer create an independent animation loop.
- The retained global motion clock runs at ~30 FPS to keep Tk input responsive on modest hardware.
- Heavy Home HUDs are frame-gated, while filesystem/process telemetry is sampled no more than once every 3 seconds.
- Secondary-page prewarming is disabled so opening Home does not build every laboratory in the background.
- These changes are presentation/performance-only and do not modify cipher implementation code.

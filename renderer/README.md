# HN BlackBox Cinematic Renderer — Modern Security + Steganography

GPU-accelerated visual surface for the HN BlackBox Modern Security and Steganography decks.

## Stack

- Three.js 0.185.1 — lightweight 3D security core.
- GSAP 3.15.0 — cinematic sequencing and UI transitions.
- PixiJS 8.20.1 — high-throughput laser/matrix layer.
- @tsparticles/engine + @tsparticles/slim 4.4.0 — restrained interactive particle field.
- Vite 8.2.2 — production build tooling.

These versions are pinned in the project manifest for reproducible builds.

## Modern Security deck

- AES-256-GCM executes through the browser Web Crypto API with a SHA-256 derived key and random 96-bit nonce.
- DES has a dedicated 16-round cinematic telemetry surface and is explicitly marked legacy/educational in the standalone renderer. The authoritative HN BlackBox Python DES engine remains the production cryptography implementation.
- PLAY / STEP / STEP BACK / RESET controls drive the live round matrix.
- Clipboard actions provide one-click output copying with laser flash/toast feedback.
- Dark glass panels, clipped geometry, neon borders, adaptive GPU quality.

## Steganography deck

- Dual operation switch: Hide Text in Image / Extract Text from Image.
- Local image intake with drag/drop and responsive perfect-fit glass frames.
- RGB LSB payload format compatible with HN BlackBox's `HNLSB1` header + UTF-8 payload + CRC32 structure.
- PNG output generation and extraction/integrity validation in-browser.
- No network upload of image contents is performed by the renderer.

## Performance guardrails

- Three.js pixel ratio capped at 1.35 desktop / 1.0 compact.
- PixiJS ticker capped at 45 FPS and uses resolution 1.
- tsParticles capped at 24 FPS with a small particle budget.
- Rendering pauses when the document is hidden.
- Sustained FPS below 42 automatically drops the Three.js pixel ratio to 1x.
- `prefers-reduced-motion` disables the heaviest continuous motion.
- UI remains DOM-light; visual effects live on GPU/canvas layers.

Absolute zero-lag cannot be guaranteed across arbitrary hardware/webviews, but the renderer is designed to degrade gracefully instead of allowing effects to starve the UI thread.

## Run

```bash
cd renderer
npm install
npm run dev
```

Or build for production:

```bash
npm install
npm run build
```

Open `/?mode=modern` for Modern Security or `/?mode=stego` for Steganography.

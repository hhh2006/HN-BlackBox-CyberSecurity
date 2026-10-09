# HN BLACKBOX — Real-File Forensics / OSINT

The OSINT / File Intelligence page now uses a real local forensic engine instead of presentation-only values.

## Analysis

`core/intelligence/file_forensics.py` performs read-only analysis and returns:

- MD5, SHA-1 and SHA-256 over the complete file bytes.
- File size, MIME guess, signature/type and sampled entropy.
- Filesystem created/modified/accessed timestamps (with platform-specific ctime semantics documented in the report).
- Image dimensions, format, mode, frame count and EXIF/PNG informational metadata when available.
- PDF document information and XMP presence through `pypdf` when available, with a bounded fallback parser.
- OOXML (`docx/xlsx/pptx`) core/app/custom properties.
- A bounded printable-string sample for triage only.

Analysis runs in a worker thread. Tk/Canvas is never touched by the worker.

## Metadata scrubber

Scrubbing always writes a **new derivative** and refuses to overwrite the source evidence.

Supported clean-derivative paths:

- JPEG / PNG / WEBP / BMP / TIFF / GIF via Pillow.
- PDF via pypdf.
- OOXML metadata parts for DOCX/XLSX/PPTX and compatible ZIP-based Office documents.

`FULL STRIP` removes the supported embedded metadata families and PDF XMP packet. Selective mode removes only the selected logical fields where the file format exposes them safely.

> A clean derivative cannot erase filesystem history, prior copies, network traces, backups, thumbnails, or metadata hidden in unsupported/private application structures. The UI therefore reports this as an embedded-metadata scrub, not as a claim of forensic erasure from every storage system.

## Animation architecture

The forensic radar is driven by the application's shared retained-mode animation clock at approximately 60 FPS. There is no page-specific 120 ms HUD timer anymore. File hashing and metadata parsing execute off the Tk main thread, while results are marshalled back to the UI event queue.

## Dependency

`pypdf>=5.0` is required for the strongest PDF metadata inspection/scrubbing path.

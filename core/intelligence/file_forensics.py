# -*- coding: utf-8 -*-
"""Local real-file forensic inspection and metadata scrubbing.

This module is deliberately offline/read-only for analysis. Scrubbing always
writes a new output file and never overwrites the evidence source.
"""
from __future__ import annotations

import hashlib
import math
import mimetypes
import os
import re
import shutil
import tempfile
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    from PIL import Image, ExifTags
except Exception:  # pragma: no cover - optional runtime dependency
    Image = ExifTags = None

try:
    from pypdf import PdfReader, PdfWriter
except Exception:  # pragma: no cover - optional runtime dependency
    PdfReader = PdfWriter = None

MAX_SAMPLE = 2 * 1024 * 1024
MAX_PDF_PARSE = 64 * 1024 * 1024

EXIF_NAMES = {v: k for k, v in (getattr(ExifTags, "TAGS", {}) or {}).items()}

_IMAGE_TYPES = {"JPEG image", "PNG image", "GIF image", "BMP image", "TIFF image", "WEBP image"}
_OFFICE_EXTS = {".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp"}
_METADATA_KEYS = (
    "Author", "Creator", "Producer", "Title", "Subject", "Keywords",
    "CreationDate", "ModDate", "LastModifiedBy", "Application",
    "Description", "Company", "Manager",
)


def _signature(head: bytes, suffix: str = "") -> tuple[str, str]:
    signatures = (
        (b"\x89PNG\r\n\x1a\n", "PNG image", "image/png"),
        (b"\xff\xd8\xff", "JPEG image", "image/jpeg"),
        (b"GIF87a", "GIF image", "image/gif"),
        (b"GIF89a", "GIF image", "image/gif"),
        (b"BM", "BMP image", "image/bmp"),
        (b"II*\x00", "TIFF image", "image/tiff"),
        (b"MM\x00*", "TIFF image", "image/tiff"),
        (b"RIFF", "RIFF container", "application/octet-stream"),
        (b"%PDF-", "PDF document", "application/pdf"),
        (b"PK\x03\x04", "ZIP / Office archive", "application/zip"),
        (b"\x7fELF", "ELF executable", "application/x-executable"),
        (b"MZ", "PE / Windows executable", "application/vnd.microsoft.portable-executable"),
    )
    for sig, kind, mime in signatures:
        if head.startswith(sig):
            if kind == "RIFF" and head[8:12] == b"WEBP":
                return "WEBP image", "image/webp"
            return kind, mime
    guessed = mimetypes.guess_type("evidence" + suffix)[0] or "application/octet-stream"
    return "Unknown / application data", guessed


def _entropy(data: bytes) -> float:
    if not data:
        return 0.0
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in Counter(data).values())


def _safe_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return str(value).replace("\x00", "").strip()


def _stat_times(st) -> dict:
    return {
        "created": datetime.fromtimestamp(st.st_ctime).isoformat(sep=" ", timespec="seconds"),
        "modified": datetime.fromtimestamp(st.st_mtime).isoformat(sep=" ", timespec="seconds"),
        "accessed": datetime.fromtimestamp(st.st_atime).isoformat(sep=" ", timespec="seconds"),
        "created_note": "filesystem ctime; interpreted as creation time on Windows and inode-change time on Unix-like systems",
    }


def _hash_file(path: Path) -> tuple[dict, bytes]:
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    md5 = hashlib.md5()
    sample = bytearray()
    total = 0
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            sha256.update(chunk); sha1.update(chunk); md5.update(chunk)
            if len(sample) < MAX_SAMPLE:
                sample.extend(chunk[:MAX_SAMPLE - len(sample)])
    return {
        "size": total,
        "sha256": sha256.hexdigest(),
        "sha1": sha1.hexdigest(),
        "md5": md5.hexdigest(),
    }, bytes(sample)


def _image_metadata(path: Path) -> tuple[list[dict], list[str]]:
    metadata: list[dict] = []
    warnings: list[str] = []
    if Image is None:
        return metadata, ["Pillow is unavailable; image metadata parser skipped."]
    try:
        with Image.open(path) as im:
            metadata.extend([
                {"key": "Format", "value": _safe_text(im.format)},
                {"key": "Dimensions", "value": f"{im.width} x {im.height}"},
                {"key": "Mode", "value": _safe_text(im.mode)},
                {"key": "Frames", "value": str(getattr(im, "n_frames", 1))},
            ])
            exif = getattr(im, "getexif", lambda: {})()
            for tag, value in list(exif.items()):
                key = (getattr(ExifTags, "TAGS", {}) or {}).get(tag, str(tag))
                if isinstance(value, bytes):
                    value = value.decode("utf-8", "replace")
                metadata.append({"key": f"EXIF:{key}", "value": _safe_text(value)[:500], "tag": int(tag) if isinstance(tag, int) else None})
            # PNG textual chunks / application-specific fields.
            for key, value in getattr(im, "info", {}).items():
                if key in {"exif", "icc_profile", "transparency"}:
                    continue
                text = _safe_text(value)
                if text:
                    metadata.append({"key": f"INFO:{key}", "value": text[:500]})
    except Exception as exc:
        warnings.append(f"Image metadata parse warning: {exc}")
    return metadata, warnings


def _pdf_metadata(path: Path) -> tuple[list[dict], list[str]]:
    metadata: list[dict] = []
    warnings: list[str] = []
    if PdfReader is not None and path.stat().st_size <= MAX_PDF_PARSE:
        try:
            reader = PdfReader(str(path), strict=False)
            info = reader.metadata or {}
            for key, value in info.items():
                k = str(key).lstrip("/")
                if k in _METADATA_KEYS or k.lower() in {x.lower() for x in _METADATA_KEYS}:
                    metadata.append({"key": k, "value": _safe_text(value)[:500]})
            root = getattr(reader, "root_object", None)
            if root is not None and "/Metadata" in root:
                metadata.append({"key": "XMP Metadata", "value": "Embedded XMP packet present"})
            metadata.append({"key": "PDF:Pages", "value": str(len(reader.pages))})
            return metadata, warnings
        except Exception as exc:
            warnings.append(f"pypdf parse warning: {exc}")
    try:
        raw = path.read_bytes() if path.stat().st_size <= MAX_PDF_PARSE else path.open("rb").read(MAX_SAMPLE)
        for key, value in re.findall(rb"/([A-Za-z][A-Za-z0-9]+)\s*\(([^)]{1,500})\)", raw):
            k = key.decode("latin1", "replace")
            if k in _METADATA_KEYS:
                metadata.append({"key": k, "value": _safe_text(value).replace("\\n", " ")})
    except Exception as exc:
        warnings.append(f"PDF fallback parser warning: {exc}")
    return metadata, warnings


def _office_metadata(path: Path) -> tuple[list[dict], list[str]]:
    metadata: list[dict] = []
    warnings: list[str] = []
    if not zipfile.is_zipfile(path):
        return metadata, ["ZIP signature detected but archive is not readable."]
    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            if "docProps/core.xml" in names:
                root = ET.fromstring(zf.read("docProps/core.xml"))
                ns = {"dc": "http://purl.org/dc/elements/1.1/", "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties", "dcterms": "http://purl.org/dc/terms/"}
                mapping = {
                    "dc:creator": "Author", "dc:title": "Title", "dc:subject": "Subject",
                    "dc:description": "Description", "dc:language": "Language", "cp:lastModifiedBy": "LastModifiedBy",
                    "dcterms:created": "CreationDate", "dcterms:modified": "ModDate",
                }
                for expr, label in mapping.items():
                    node = root.find(expr, ns)
                    if node is not None and _safe_text(node.text):
                        metadata.append({"key": label, "value": _safe_text(node.text)[:500], "xml": expr})
            if "docProps/app.xml" in names:
                root = ET.fromstring(zf.read("docProps/app.xml"))
                for local, label in (("Application", "Application"), ("Company", "Company"), ("Manager", "Manager")):
                    for node in root.iter():
                        if node.tag.rsplit("}", 1)[-1] == local and _safe_text(node.text):
                            metadata.append({"key": label, "value": _safe_text(node.text)[:500], "xml": local})
                            break
            if "docProps/custom.xml" in names:
                root = ET.fromstring(zf.read("docProps/custom.xml"))
                for prop in list(root):
                    name = prop.attrib.get("name", "CustomProperty")
                    value = next((_safe_text(child.text) for child in prop if _safe_text(child.text)), "")
                    if value:
                        metadata.append({"key": f"Custom:{name}", "value": value[:500]})
    except Exception as exc:
        warnings.append(f"Office metadata parse warning: {exc}")
    return metadata, warnings


def analyze_file(path: str | os.PathLike) -> dict:
    """Analyze a real local file without executing or modifying it."""
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise FileNotFoundError(str(p))
    st = p.stat()
    hashes, sample = _hash_file(p)
    kind, mime = _signature(sample[:64], p.suffix.lower())
    if kind == "ZIP / Office archive" and p.suffix.lower() in _OFFICE_EXTS:
        kind = f"Office document ({p.suffix.lower()})"
        mime = mimetypes.guess_type(p.name)[0] or mime
    metadata: list[dict] = []
    warnings: list[str] = []
    if kind in _IMAGE_TYPES:
        metadata, warnings = _image_metadata(p)
    elif kind == "PDF document":
        metadata, warnings = _pdf_metadata(p)
    elif p.suffix.lower() in _OFFICE_EXTS:
        metadata, warnings = _office_metadata(p)
    strings = []
    for match in re.finditer(rb"[ -~]{6,}", sample):
        text = match.group(0).decode("ascii", "replace")[:160]
        if text not in strings and len(strings) < 24:
            strings.append(text)
    return {
        "name": p.name, "path": str(p), "size": st.st_size, "type": kind, "mime": mime,
        "filesystem": _stat_times(st), "sha256": hashes["sha256"], "sha1": hashes["sha1"], "md5": hashes["md5"],
        "entropy": _entropy(sample), "metadata": metadata, "strings": strings, "warnings": warnings,
        "analyzed_at": datetime.now().isoformat(timespec="milliseconds"),
    }


def _clean_image(src: Path, dst: Path, fields: set[str], full_strip: bool) -> dict:
    if Image is None:
        raise RuntimeError("Pillow is required for image scrubbing")
    suffix = src.suffix.lower()
    fields = {str(f).strip().lower() for f in fields}
    with Image.open(src) as im:
        fmt = im.format or suffix.lstrip(".").upper()
        # Logical selectors intentionally map to common EXIF/PNG metadata families.
        exif_remove = set()
        tags = getattr(ExifTags, "TAGS", {}) or {}
        for tag_id, name in tags.items():
            lname = str(name).lower()
            if full_strip:
                exif_remove.add(tag_id)
            elif "author" in fields and lname in {"artist", "copyright", "xpcomment", "xpkeywords", "xpsubject", "xptitle", "xpkeywords"}:
                exif_remove.add(tag_id)
            elif "creator" in fields and lname in {"software", "artist", "make", "model", "hostcomputer"}:
                exif_remove.add(tag_id)
            elif "creationdate" in fields and lname in {"datetime", "datetimeoriginal", "datetimedigitized"}:
                exif_remove.add(tag_id)
            elif "moddate" in fields and lname == "datetime":
                exif_remove.add(tag_id)
        info = dict(getattr(im, "info", {}) or {})
        if Image is not None and hasattr(im, "getexif"):
            try:
                exif = im.getexif()
                for tag_id in exif_remove:
                    exif.pop(tag_id, None)
            except Exception:
                exif = None
        else:
            exif = None

        if suffix in {".jpg", ".jpeg"}:
            clean = im.convert("RGB") if im.mode not in {"RGB", "L"} else im.copy()
            kwargs = {"quality": 95, "optimize": True}
            if not full_strip:
                if exif is not None and len(exif): kwargs["exif"] = exif.tobytes()
                if info.get("icc_profile"): kwargs["icc_profile"] = info["icc_profile"]
                if info.get("dpi"): kwargs["dpi"] = info["dpi"]
            clean.save(dst, format="JPEG", **kwargs)
        elif suffix == ".png":
            kwargs = {"optimize": True}
            if not full_strip:
                try:
                    from PIL.PngImagePlugin import PngInfo
                    pnginfo = PngInfo()
                    for key, value in info.items():
                        if key in {"exif", "icc_profile", "transparency"}: continue
                        if not isinstance(value, (str, bytes)): continue
                        logical = str(key).lower()
                        if ("author" in fields and logical in {"author", "artist", "creator"}) or ("creator" in fields and logical in {"creator", "software", "author"}) or ("creationdate" in fields and logical in {"creationdate", "date", "creation_time"}) or ("moddate" in fields and logical in {"moddate", "modifydate", "modification_time"}):
                            continue
                        pnginfo.add_text(str(key), value.decode("utf-8", "replace") if isinstance(value, bytes) else str(value))
                    kwargs["pnginfo"] = pnginfo
                    if info.get("icc_profile"): kwargs["icc_profile"] = info["icc_profile"]
                except Exception:
                    pass
            if exif is not None and not full_strip and len(exif): kwargs["exif"] = exif.tobytes()
            im.save(dst, format="PNG", **kwargs)
        elif suffix == ".webp":
            clean = im.convert("RGB") if im.mode not in {"RGB", "L"} else im.copy()
            kwargs = {"quality": 95, "method": 6}
            if not full_strip and exif is not None and len(exif): kwargs["exif"] = exif.tobytes()
            clean.save(dst, format="WEBP", **kwargs)
        elif suffix == ".bmp":
            im.save(dst, format="BMP")
        elif suffix in {".tif", ".tiff"}:
            # TIFF tags are format-specific; re-encoding without the original tag dictionary
            # is the safe full-strip path. Selective mode therefore removes the requested family.
            kwargs = {"compression": "tiff_deflate"}
            if not full_strip and exif is not None and len(exif): kwargs["exif"] = exif.tobytes()
            im.save(dst, format=fmt, **kwargs)
        elif suffix == ".gif":
            frames = []; durations = []
            try:
                for i in range(getattr(im, "n_frames", 1)):
                    im.seek(i); frames.append(im.convert("P").copy()); durations.append(im.info.get("duration", 0))
            except EOFError:
                pass
            if len(frames) > 1:
                frames[0].save(dst, format="GIF", save_all=True, append_images=frames[1:], duration=durations, loop=im.info.get("loop", 0), optimize=True)
            else:
                im.convert("P").save(dst, format="GIF", optimize=True)
        else:
            raise ValueError(f"Unsupported image scrub format: {suffix}")
    return {"method": "Pillow metadata-aware image rewrite", "full_strip": full_strip, "fields": sorted(fields)}

def _xml_local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _clean_ooxml(src: Path, dst: Path, fields: set[str], full_strip: bool) -> dict:
    # Only metadata property parts are changed; document content is copied byte-for-byte.
    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            name = info.filename
            if name == "docProps/core.xml":
                root = ET.fromstring(zin.read(name))
                field_map = {"Author": "creator", "Title": "title", "Subject": "subject", "Description": "description", "LastModifiedBy": "lastModifiedBy", "CreationDate": "created", "ModDate": "modified"}
                for node in list(root):
                    local = _xml_local(node.tag)
                    label = next((k for k, v in field_map.items() if v == local), None)
                    if full_strip or (label and label in fields):
                        node.text = None
                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)
                zout.writestr(info, data)
            elif name == "docProps/app.xml" and (full_strip or bool(fields & {"Application", "Company", "Manager"})):
                root = ET.fromstring(zin.read(name))
                targets = {"Application", "Company", "Manager"} if full_strip else fields
                for node in root.iter():
                    if _xml_local(node.tag) in targets:
                        node.text = None
                zout.writestr(info, ET.tostring(root, encoding="utf-8", xml_declaration=True))
            elif name == "docProps/custom.xml" and full_strip:
                # Removing custom properties is the strongest supported OOXML strip.
                continue
            else:
                zout.writestr(info, zin.read(name))
    return {"method": "OOXML metadata-part rewrite", "full_strip": full_strip, "fields": sorted(fields)}


def _clean_pdf(src: Path, dst: Path, fields: set[str], full_strip: bool) -> dict:
    if PdfReader is None or PdfWriter is None:
        raise RuntimeError("pypdf is required for PDF metadata scrubbing")
    reader = PdfReader(str(src), strict=False)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    current = dict(reader.metadata or {})
    clean = {}
    for key, value in current.items():
        label = str(key).lstrip("/")
        if full_strip or label in fields:
            continue
        clean[key] = value
    # Reset the document info dictionary rather than merging with the source.
    from pypdf.generic import DictionaryObject
    writer._info = DictionaryObject()
    if clean:
        writer.add_metadata(clean)
    # Remove XMP packet from the writer root when performing a full strip.
    try:
        if full_strip and "/Metadata" in writer._root_object:
            del writer._root_object["/Metadata"]
    except Exception:
        pass
    with dst.open("wb") as fh:
        writer.write(fh)
    return {"method": "pypdf metadata dictionary rewrite", "full_strip": full_strip, "fields": sorted(fields), "xmp_removed": full_strip}


def scrub_metadata(path: str | os.PathLike, output_path: str | os.PathLike | None = None, fields: list[str] | None = None, full_strip: bool = False) -> dict:
    """Create a cleaned derivative. Never overwrites the source evidence file."""
    src = Path(path).expanduser().resolve()
    if not src.is_file():
        raise FileNotFoundError(str(src))
    requested = {str(x) for x in (fields or []) if str(x)}
    if not full_strip and not requested:
        raise ValueError("Select at least one metadata field or use FULL STRIP")
    if output_path is None:
        suffix = src.suffix or ".bin"
        output_path = src.with_name(src.stem + "_CLEAN" + suffix)
    dst = Path(output_path).expanduser().resolve()
    if dst == src:
        raise ValueError("Refusing to overwrite source evidence")
    dst.parent.mkdir(parents=True, exist_ok=True)
    kind, _ = _signature(src.read_bytes()[:64], src.suffix.lower())
    if kind in _IMAGE_TYPES:
        result = _clean_image(src, dst, requested, full_strip)
    elif kind == "PDF document":
        result = _clean_pdf(src, dst, requested, full_strip)
    elif src.suffix.lower() in _OFFICE_EXTS or kind == "ZIP / Office archive":
        result = _clean_ooxml(src, dst, requested, full_strip)
    else:
        # For arbitrary binary/text files there is no generic metadata schema to safely strip.
        # Copying would falsely imply sanitization, so fail closed.
        raise ValueError(f"No safe metadata scrubber is registered for {src.suffix or 'this file type'}")
    before = analyze_file(src)
    after = analyze_file(dst)
    return {"source": str(src), "output": str(dst), "operation": result, "before": before, "after": after}

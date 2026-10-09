# -*- coding: utf-8 -*-
"""PNG/BMP LSB steganography engine for HN BlackBox."""
from __future__ import annotations
from pathlib import Path
import struct, zlib
from PIL import Image

MAGIC = b"HNLSB1"
HEADER = len(MAGIC) + 4 + 4  # magic + payload length + CRC32

class StegoError(ValueError):
    pass

def _load(path: str) -> Image.Image:
    p=Path(path)
    if not p.exists() or not p.is_file(): raise StegoError("Image file not found.")
    if p.suffix.lower() not in {".png",".bmp"}: raise StegoError("Only PNG and BMP images are supported.")
    try: img=Image.open(p)
    except Exception as e: raise StegoError("Invalid or unreadable image file.") from e
    if img.format not in {"PNG","BMP"}: raise StegoError("Only PNG and BMP images are supported.")
    if img.mode not in {"RGB","RGBA"}: img=img.convert("RGBA" if "A" in img.getbands() else "RGB")
    return img

def capacity_bytes(path: str) -> int:
    img=_load(path)
    channels=3
    return max(0, (img.width*img.height*channels)//8 - HEADER)

def encode(input_path: str, output_path: str, message: str) -> dict:
    img=_load(input_path)
    raw=message.encode("utf-8")
    capacity=capacity_bytes(input_path)
    if len(raw)>capacity: raise StegoError(f"Message is too large for this image. Capacity: {capacity} bytes.")
    crc=zlib.crc32(raw) & 0xFFFFFFFF
    payload=MAGIC+struct.pack(">I",len(raw))+struct.pack(">I",crc)+raw
    bits=''.join(f'{byte:08b}' for byte in payload)
    pix=img.load(); idx=0
    for y in range(img.height):
        for x in range(img.width):
            px=pix[x,y]
            vals=list(px)
            for ch in range(3):
                if idx>=len(bits): break
                vals[ch]=(vals[ch]&0xFE)|int(bits[idx]); idx+=1
            pix[x,y]=tuple(vals)
            if idx>=len(bits): break
        if idx>=len(bits): break
    out=Path(output_path)
    if out.suffix.lower() not in {".png",".bmp"}: raise StegoError("Output must be PNG or BMP.")
    img.save(out)
    return {"message_bytes":len(raw),"capacity_bytes":capacity,"output":str(out),"format":img.format}

def decode(input_path: str) -> str:
    img=_load(input_path); pix=img.load()
    # Read header bytes first.
    bits=[]
    for y in range(img.height):
        for x in range(img.width):
            px=pix[x,y]
            for ch in range(3): bits.append(str(px[ch]&1))
            if len(bits)>=HEADER*8: break
        if len(bits)>=HEADER*8: break
    head=bytes(int(''.join(bits[i:i+8]),2) for i in range(0,HEADER*8,8))
    if head[:len(MAGIC)]!=MAGIC: raise StegoError("No HN LSB payload was detected in this image.")
    n=struct.unpack(">I",head[len(MAGIC):len(MAGIC)+4])[0]
    crc_expected=struct.unpack(">I",head[len(MAGIC)+4:HEADER])[0]
    total_bits=(HEADER+n)*8
    if total_bits > img.width*img.height*3: raise StegoError("Embedded payload is truncated or corrupt.")
    bits=[]
    for y in range(img.height):
        for x in range(img.width):
            px=pix[x,y]
            for ch in range(3): bits.append(str(px[ch]&1))
            if len(bits)>=total_bits: break
        if len(bits)>=total_bits: break
    data=bytes(int(''.join(bits[i:i+8]),2) for i in range(HEADER*8,total_bits,8))
    if zlib.crc32(data)&0xFFFFFFFF != crc_expected: raise StegoError("Payload integrity check failed. The image may be corrupted.")
    try: return data.decode("utf-8")
    except UnicodeDecodeError as e: raise StegoError("Embedded payload is not valid UTF-8 text.") from e


def inspect_lsb(path: str, sample_pixels: int = 256) -> dict:
    """Return a deterministic educational LSB/bit-plane inspection report.

    The report never modifies the source image. It exposes channel statistics,
    bit-plane densities, a compact RGB LSB stream preview, and payload metadata.
    """
    img = _load(path).convert("RGB")
    pix = img.load()
    channels = {"R": [], "G": [], "B": []}
    plane_counts = {c: [0] * 8 for c in channels}
    lsb_stream = []
    limit = max(1, int(sample_pixels))
    seen = 0
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pix[x, y]
            for name, value in (("R", r), ("G", g), ("B", b)):
                channels[name].append(value)
                for bit in range(8):
                    plane_counts[name][bit] += (value >> bit) & 1
                if len(lsb_stream) < limit * 3:
                    lsb_stream.append(str(value & 1))
            seen += 1
            if seen >= limit:
                break
        if seen >= limit:
            break
    total = max(1, seen)
    density = {c: [round(n / total * 100, 2) for n in counts] for c, counts in plane_counts.items()}
    payload = {"detected": False, "message_bytes": 0, "crc": None}
    try:
        bits = []
        for y in range(img.height):
            for x in range(img.width):
                px = pix[x, y]
                bits.extend(str(px[ch] & 1) for ch in range(3))
                if len(bits) >= HEADER * 8:
                    break
            if len(bits) >= HEADER * 8:
                break
        head = bytes(int(''.join(bits[i:i+8]), 2) for i in range(0, HEADER * 8, 8))
        if head[:len(MAGIC)] == MAGIC:
            n = struct.unpack(">I", head[len(MAGIC):len(MAGIC)+4])[0]
            crc = struct.unpack(">I", head[len(MAGIC)+4:HEADER])[0]
            payload.update(detected=True, message_bytes=n, crc=f"{crc:08X}")
    except Exception:
        pass
    return {
        "width": img.width, "height": img.height, "mode": img.mode,
        "pixels_sampled": seen, "capacity_bytes": capacity_bytes(path),
        "plane_density_percent": density,
        "lsb_stream": "".join(lsb_stream), "payload": payload,
    }

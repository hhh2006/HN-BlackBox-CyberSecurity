"""Presentation-only visual models for Step 6.

These helpers draw educational HUD layers around real crypto/steganography
results. They never encrypt, decrypt, hash, or modify image payloads.
"""
from __future__ import annotations
import hashlib
import math


def _hex_bytes(text: str, n: int = 16) -> list[str]:
    raw = (text or "").encode("utf-8")[:n].ljust(n, b"\x00")
    return [f"{b:02X}" for b in raw]


def _rounded_box(c, x1, y1, x2, y2, fill, outline, r=10, width=1):
    # Canvas rounded rectangles are approximated with a polygon + arcs.
    c.create_rectangle(x1+r, y1, x2-r, y2, fill=fill, outline="")
    c.create_rectangle(x1, y1+r, x2, y2-r, fill=fill, outline="")
    c.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, fill=fill, outline=fill)
    c.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, fill=fill, outline=fill)
    c.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, fill=fill, outline=fill)
    c.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, fill=fill, outline=fill)
    c.create_rectangle(x1+r, y1, x2-r, y1+1, outline=outline, fill="")
    c.create_rectangle(x1+r, y2-1, x2-r, y2, outline=outline, fill="")
    c.create_line(x1, y1+r, x1, y2-r, fill=outline, width=width)
    c.create_line(x2, y1+r, x2, y2-r, fill=outline, width=width)


def draw_aes_state_hud(c, w, h, step, payload, accent, P):
    """Add an animated-looking AES state/round HUD without claiming real internals."""
    x0, y0 = 30, h * .58
    cell = min(44, max(30, (w * .36) / 4))
    data = _hex_bytes(payload, 16)
    active = min(16, max(0, step + 1))
    c.create_text(x0, y0-92, text="AES STATE // 128-BIT VIEW", fill=P["green"], font=(P.get("MONO","Consolas"),10,"bold"), anchor="w")
    for i, val in enumerate(data):
        rr, cc = i % 4, i // 4
        x=x0+cc*cell+cell/2; y=y0+rr*cell
        on=i<active
        c.create_rectangle(x-cell/2+2,y-cell/2+2,x+cell/2-2,y+cell/2-2,fill="#0a2118" if on else "#071018",outline=accent if on else P["line"],width=2 if on else 1)
        c.create_text(x,y,text=val,fill=P["text"] if on else P["muted"],font=("Consolas",9,"bold"))
    c.create_text(w*.53,h*.55,text="ROUND PIPELINE",fill=accent,font=("Consolas",10,"bold"),anchor="w")
    stages=["SUB BYTES","SHIFT ROWS","MIX COLUMNS","ADD ROUND KEY"]
    for i,stage in enumerate(stages):
        yy=h*.61+i*30; on=step >= (i+1)*3
        c.create_rectangle(w*.53,yy,w*.91,yy+21,fill="#0a2118" if on else "#071018",outline=accent if on else P["line"])
        c.create_text(w*.55,yy+10,text=f"0{i+1}",fill=accent,font=("Consolas",8,"bold"),anchor="w")
        c.create_text(w*.61,yy+10,text=stage,fill=P["text"] if on else P["muted"],font=("Segoe UI",9,"bold"),anchor="w")


def draw_rsa_flow_hud(c, w, h, step, payload, accent, P):
    """Render RSA concepts as a modular-exponentiation story."""
    c.create_text(w*.08,h*.55,text="MESSAGE",fill=P["yellow"],font=("Consolas",9,"bold"),anchor="w")
    c.create_text(w*.08,h*.62,text=(payload[:18] or "WAITING"),fill=P["text"],font=("Consolas",10,"bold"),anchor="w")
    stages=[("M","ENCODE"),("E","EXPONENTIATE"),("N","MODULO N"),("C","OUTPUT")]
    for i,(tag,title) in enumerate(stages):
        x=w*.30+i*w*.17; y=h*.59; on=step >= i*4+1
        c.create_oval(x-22,y-22,x+22,y+22,fill="#201b08" if on else "#071018",outline=accent if on else P["line"],width=2)
        c.create_text(x,y,text=tag,fill=accent if on else P["muted"],font=("Consolas",11,"bold"))
        c.create_text(x,y+34,text=title,fill=P["text"] if on else P["muted"],font=("Consolas",8,"bold"))
        if i<3:c.create_line(x+25,y,x+w*.17-25+x,y,fill=accent if on else P["line"],width=2,arrow="last")
    c.create_text(w*.30,h*.80,text="PUBLIC / PRIVATE KEY RELATIONSHIP",fill=P["yellow"],font=("Consolas",9,"bold"),anchor="w")
    c.create_text(w*.30,h*.86,text="c = mᵉ mod n    •    m = cᵈ mod n",fill=P["text"],font=("Consolas",10,"bold"),anchor="w")


def draw_hash_hud(c, w, h, step, payload, result, accent, P):
    """Show deterministic digest bytes plus an avalanche-style activity meter."""
    digest = result or hashlib.sha256((payload or "").encode("utf-8")).hexdigest()
    c.create_text(30,h*.56,text="DIGEST FINGERPRINT",fill=P["cyan"],font=("Consolas",10,"bold"),anchor="w")
    for i in range(4):
        part=digest[i*16:(i+1)*16]
        yy=h*.62+i*22; on=step >= i*2
        c.create_text(30,yy,text=part,fill=P["text"] if on else P["muted"],font=("Consolas",9,"bold"),anchor="w")
    c.create_text(w*.67,h*.57,text="COMPRESSION",fill=accent,font=("Consolas",9,"bold"),anchor="w")
    bars=12; active=min(bars,max(0,step))
    for i in range(bars):
        x=w*.67+i*17; hh=16+int(20*(0.5+0.5*math.sin(i*1.7)))
        c.create_rectangle(x,h*.72-hh,x+9,h*.72,fill=accent if i<active else P["line"],outline="")
    c.create_text(w*.67,h*.82,text="ONE-WAY • DETERMINISTIC FOR SAME INPUT",fill=P["muted"],font=("Consolas",8,"bold"),anchor="w")


def draw_stego_hud(c, w, h, report, active_bits, status, P):
    """Render a compact LSB bit-plane / payload HUD from the real inspection report."""
    accent=P["green"] if "DETECTED" in status or "COMPLETE" in status else P["cyan"]
    c.create_text(8,10,text="LSB PAYLOAD CHANNEL // LIVE BIT-PLANE MAP",fill=accent,font=("Consolas",9,"bold"),anchor="w")
    c.create_text(w-8,10,text=status,fill=P["green"] if "DETECTED" in status else P["muted"],font=("Consolas",8,"bold"),anchor="e")
    for i in range(32):
        x=10+i*max(12,(w-20)/32); on=i<active_bits
        c.create_rectangle(x,30,x+8,52,fill=accent if on else "#071018",outline=P["line"])
    c.create_text(10,65,text="R",fill=P["red"],font=("Consolas",8,"bold"),anchor="w")
    c.create_text(10,91,text="G",fill=P["green"],font=("Consolas",8,"bold"),anchor="w")
    c.create_text(10,117,text="B",fill=P["cyan"],font=("Consolas",8,"bold"),anchor="w")
    if report:
        for row,(ch,accent2) in enumerate((("R",P["red"]),("G",P["green"]),("B",P["cyan"]))):
            vals=report["plane_density_percent"][ch]
            y=68+row*26
            for bit,val in enumerate(vals):
                x=30+bit*max(28,(w-50)/8)
                level=max(2,min(18,int(val/100*18)))
                c.create_rectangle(x,y+18-level,x+15,y+18,fill=accent2 if val>=50 else "#0b1820",outline="")
                c.create_text(x+7,y+24,text=str(bit),fill=P["muted"],font=("Consolas",7))
        cap=report["capacity_bytes"]
        pl=report["payload"]
        c.create_text(w-10,h-12,text=f"CAP {cap:,} B  •  PAYLOAD {pl['message_bytes']:,} B  •  CRC {pl['crc'] or '—'}",fill=P["muted"],font=("Consolas",8,"bold"),anchor="e")
    else:
        c.create_text(w-10,h-12,text="LOAD PNG/BMP TO ACTIVATE FORENSIC CHANNEL",fill=P["muted"],font=("Consolas",8,"bold"),anchor="e")

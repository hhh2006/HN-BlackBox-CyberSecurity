"""Local network intelligence helpers built on the existing safe network toolkit."""
from __future__ import annotations
import ipaddress, socket

def inspect_target(value):
    value=(value or "").strip(); result={"input":value,"kind":"unknown"}
    try:
        ip=ipaddress.ip_address(value); result.update(kind="ip",version=ip.version,private=ip.is_private,loopback=ip.is_loopback)
    except ValueError:
        try:
            infos=socket.getaddrinfo(value,None); addrs=sorted({x[4][0] for x in infos}); result.update(kind="hostname",addresses=addrs[:16])
        except OSError: result["error"]="Unable to resolve locally"
    return result

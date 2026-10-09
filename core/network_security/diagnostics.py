"""Real local network diagnostics for HN BlackBox.

Safety boundary: diagnostics are passive/local or limited to private/local subnets
explicitly supplied by the operator. No exploit, credential attack, packet
injection, or raw packet payload collection is performed.
"""
from __future__ import annotations

import ipaddress
import platform
import socket
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import psutil
except Exception:  # pragma: no cover
    psutil = None

DEFAULT_PORTS = (21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3306, 3389, 5432, 6379, 8080, 8443)


def _private_or_local(ip: str) -> bool:
    try:
        obj = ipaddress.ip_address(str(ip).strip())
    except (ValueError, TypeError):
        return False

    return obj.is_private or obj.is_loopback or obj.is_link_local


def validate_scope(target: str) -> ipaddress._BaseNetwork:
    net = ipaddress.ip_network(target.strip(), strict=False)
    if not (net.is_private or net.network_address.is_loopback or net.network_address.is_link_local):
        raise ValueError("NETWORK SCOPE BLOCKED: only private/loopback/link-local networks are allowed")
    if net.version != 4:
        raise ValueError("Subnet scanner currently accepts IPv4 private/local networks")
    if net.num_addresses > 256:
        raise ValueError("Subnet scope too large: maximum 256 addresses per run")
    return net


def local_interfaces() -> list[dict]:
    rows = []
    if psutil:
        for name, addrs in psutil.net_if_addrs().items():
            for a in addrs:
                if a.family == socket.AF_INET:
                    try:
                        ip = ipaddress.ip_address(a.address)
                        rows.append({"interface": name, "address": a.address, "netmask": a.netmask or "", "private": ip.is_private, "loopback": ip.is_loopback})
                    except ValueError:
                        pass
    if not rows:
        rows.append({"interface": "hostname", "address": socket.gethostbyname(socket.gethostname()), "netmask": "", "private": True, "loopback": False})
    return rows


def gateways() -> list[dict]:
    if not psutil:
        return []
    try:
        data = psutil.net_if_stats()
        out = []
        for family, gw, iface, _metric in psutil.net_if_addrs() if False else []:
            pass
        # psutil exposes default gateways through net_if_addrs only indirectly;
        # use the platform route table for a real OS view below.
    except Exception:
        pass
    return route_table()


def route_table() -> list[dict]:
    """Read the host OS routing table without changing it."""
    system = platform.system().lower()
    commands = [["route", "-4", "print"] if system == "windows" else ["ip", "route", "show", "table", "main"]]
    raw = ""
    for cmd in commands:
        try:
            raw = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=2.5, errors="replace")
            break
        except Exception:
            continue
    rows = []
    for line in raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if system == "windows":
            parts = s.split()
            if len(parts) >= 5 and (parts[0] == "0.0.0.0" or parts[0].count(".") == 3):
                rows.append({"route": parts[0], "mask": parts[1], "gateway": parts[2], "interface": parts[3], "metric": parts[4]})
        else:
            parts = s.split()
            if parts[0] == "default" and "via" in parts:
                i = parts.index("via"); gw = parts[i + 1] if i + 1 < len(parts) else ""
                dev = parts[parts.index("dev") + 1] if "dev" in parts else ""
                rows.append({"route": "default", "gateway": gw, "interface": dev})
            elif "/" in parts[0]:
                rows.append({"route": parts[0], "gateway": parts[parts.index("via") + 1] if "via" in parts else "", "interface": parts[parts.index("dev") + 1] if "dev" in parts else ""})
    return rows[:64]


def scan_port(host: str, port: int, timeout: float = 0.45) -> dict:
    started = time.perf_counter()
    status = "closed"
    err = ""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            rc = s.connect_ex((host, int(port)))
            status = "open" if rc == 0 else "closed"
            if rc != 0:
                err = str(rc)
    except OSError as exc:
        err = str(exc)
    return {"host": host, "port": int(port), "state": status, "latency_ms": round((time.perf_counter() - started) * 1000, 2), "error": err}


def port_scan(host: str, ports=DEFAULT_PORTS, timeout: float = 0.45) -> list[dict]:
    """TCP connect scan against one explicitly selected local/private host."""
    ip = ipaddress.ip_address(socket.gethostbyname(host))
    if not _private_or_local(str(ip)):
        raise ValueError("TARGET BLOCKED: scanner only permits private/loopback/link-local hosts")
    clean = sorted({int(p) for p in ports if 1 <= int(p) <= 65535})[:64]
    with ThreadPoolExecutor(max_workers=min(16, max(1, len(clean)))) as pool:
        futures = [pool.submit(scan_port, str(ip), p, timeout) for p in clean]
        return sorted((f.result() for f in as_completed(futures)), key=lambda x: x["port"])


def subnet_scan(cidr: str, ports=(22, 80, 443, 8080), timeout: float = 0.35, max_hosts: int = 64) -> dict:
    net = validate_scope(cidr)
    hosts = list(net.hosts())[:max_hosts]
    clean = sorted({int(p) for p in ports if 1 <= int(p) <= 65535})[:8]
    results = {}
    # One bounded worker pool avoids nested executors and excessive local load.
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {(pool.submit(scan_port, str(ip), port, timeout)): (str(ip), port) for ip in hosts for port in clean}
        for f in as_completed(futures):
            host, port = futures[f]
            try:
                row = f.result()
                if row['state'] == 'open':
                    results.setdefault(host, []).append(row)
            except Exception:
                continue
    hosts_out = [{'host': h, 'open_ports': sorted(rows, key=lambda x: x['port']), 'latency_ms': min(r['latency_ms'] for r in rows)} for h, rows in sorted(results.items())]
    return {'scope': str(net), 'hosts_checked': len(hosts), 'hosts_found': len(hosts_out), 'hosts': hosts_out}


def socket_snapshot() -> list[dict]:
    """Current TCP/UDP socket endpoints visible to the OS/user process."""
    if not psutil:
        return []
    rows = []
    try:
        conns = psutil.net_connections(kind="inet")
    except Exception:
        conns = []
    for c in conns:
        laddr = getattr(c, "laddr", None)
        raddr = getattr(c, "raddr", None)
        lip, lp = (laddr.ip, laddr.port) if laddr else ("", "")
        rip, rp = (raddr.ip, raddr.port) if raddr else ("", "")
        rows.append({"family": "IPv6" if c.family == socket.AF_INET6 else "IPv4", "proto": "TCP" if c.type == socket.SOCK_STREAM else "UDP", "local": f"{lip}:{lp}", "remote": f"{rip}:{rp}" if rip else "-", "status": c.status or "-", "pid": c.pid or "-"})
    return sorted(rows, key=lambda r: (r["proto"], r["status"], r["remote"]))[:250]


def traffic_snapshot() -> dict:
    """Interface byte/packet counters; this is not raw packet payload capture."""
    if not psutil:
        return {"interfaces": {}, "total_sent": 0, "total_recv": 0}
    data = psutil.net_io_counters(pernic=True)
    interfaces = {}
    sent = recv = 0
    for name, c in data.items():
        interfaces[name] = {"bytes_sent": c.bytes_sent, "bytes_recv": c.bytes_recv, "packets_sent": c.packets_sent, "packets_recv": c.packets_recv, "errin": c.errin, "errout": c.errout, "dropin": getattr(c, "dropin", 0), "dropout": getattr(c, "dropout", 0)}
        sent += c.bytes_sent; recv += c.bytes_recv
    return {"interfaces": interfaces, "total_sent": sent, "total_recv": recv}


def topology_snapshot() -> dict:
    interfaces = local_interfaces()
    routes = route_table()
    sockets = socket_snapshot()
    nodes = {"LOCAL": {"id": "LOCAL", "kind": "HOST", "status": "ACTIVE"}}
    links = []
    for row in interfaces:
        node = row["address"]
        nodes[node] = {"id": node, "kind": "INTERFACE", "status": "ACTIVE", "label": row["interface"]}
        links.append({"source": "LOCAL", "target": node, "kind": "LINK"})
    for route in routes:
        gw = route.get("gateway")
        if gw and _private_or_local(gw):
            nodes.setdefault(gw, {"id": gw, "kind": "GATEWAY", "status": "ACTIVE"})
            links.append({"source": "LOCAL", "target": gw, "kind": "ROUTE"})
    for s in sockets:
        remote = s["remote"].rsplit(":", 1)[0] if s["remote"] != "-" else ""
        if remote:
            try:
                if _private_or_local(remote):
                    nodes.setdefault(remote, {"id": remote, "kind": "PEER", "status": "ACTIVE"})
                    links.append({"source": "LOCAL", "target": remote, "kind": s["proto"]})
            except ValueError:
                pass
    return {"nodes": list(nodes.values()), "links": links, "routes": routes, "interfaces": interfaces, "sockets": sockets}

"""Blue-team correlation primitives for local logs and IOC evidence."""
from __future__ import annotations
import re

def extract_indicators(text):
    s=str(text or "")
    ips=sorted(set(re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b",s)))
    urls=sorted(set(re.findall(r"https?://[^\s]+",s)))
    users=sorted(set(re.findall(r"(?:user|username)=([A-Za-z0-9_.-]+)",s,re.I)))
    return {"ips":ips,"urls":urls,"users":users}

def severity(text):
    s=str(text or "").lower()
    if any(k in s for k in ("critical","ransomware","credential theft")): return "CRITICAL"
    if any(k in s for k in ("malware","failed login","suspicious","ioc")): return "HIGH"
    if any(k in s for k in ("warning","denied","blocked")): return "MEDIUM"
    return "INFO"

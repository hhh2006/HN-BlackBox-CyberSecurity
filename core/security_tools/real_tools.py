"""Safe, local cybersecurity utility functions for HN BlackBox.
No outbound requests are made by this module.
"""
from __future__ import annotations
import base64, hashlib, json, math, re, socket, urllib.parse
from pathlib import Path
from collections import Counter


def hash_bytes(data: bytes, algorithms=("sha256", "sha1", "md5")):
    return {a: hashlib.new(a, data).hexdigest() for a in algorithms}

def hash_file(path: str, chunk_size=1024*1024):
    p=Path(path); hs={a:hashlib.new(a) for a in ("sha256","sha1","md5")}
    with p.open('rb') as f:
        while chunk:=f.read(chunk_size):
            for h in hs.values(): h.update(chunk)
    st=p.stat()
    return {"path":str(p),"size":st.st_size,"sha256":hs['sha256'].hexdigest(),"sha1":hs['sha1'].hexdigest(),"md5":hs['md5'].hexdigest()}

def b64_encode(text): return base64.b64encode(text.encode()).decode()
def b64_decode(value): return base64.b64decode(value.encode(), validate=True).decode('utf-8')

def parse_url(url):
    u=urllib.parse.urlsplit(url)
    return {"scheme":u.scheme,"hostname":u.hostname or "","port":u.port or (443 if u.scheme=='https' else 80 if u.scheme=='http' else ''),"path":u.path or '/',"query":dict(urllib.parse.parse_qsl(u.query,keep_blank_values=True)),"fragment":u.fragment}

def parse_headers(text):
    out={}
    for line in text.splitlines():
        if ':' in line:
            k,v=line.split(':',1);out[k.strip().lower()]=v.strip()
    return out

def decode_jwt(token):
    parts=token.strip().split('.')
    if len(parts)!=3: raise ValueError('JWT must contain three segments')
    def dec(x): return json.loads(base64.urlsafe_b64decode(x+'='*((4-len(x)%4)%4)).decode())
    return {"header":dec(parts[0]),"payload":dec(parts[1]),"signature_present":bool(parts[2]),"note":"Signature is not verified; decoding is local only."}

def password_entropy(password):
    p=str(password); pool=0
    if re.search(r'[a-z]',p): pool+=26
    if re.search(r'[A-Z]',p): pool+=26
    if re.search(r'\d',p): pool+=10
    if re.search(r'[^A-Za-z0-9]',p): pool+=33
    entropy=len(p)*math.log2(pool) if pool else 0
    return {"length":len(p),"charset_size":pool,"entropy_bits":round(entropy,2),"rating":"very weak" if entropy<28 else "weak" if entropy<36 else "fair" if entropy<60 else "strong" if entropy<80 else "very strong"}

def extract_iocs(text):
    ips=sorted(set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b',text)))
    hashes=sorted(set(re.findall(r'\b[0-9a-fA-F]{32}\b|\b[0-9a-fA-F]{40}\b|\b[0-9a-fA-F]{64}\b',text)))
    urls=sorted(set(re.findall(r'https?://[^\s\"\'<>]+',text)))
    emails=sorted(set(re.findall(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b',text)))
    return {"ipv4":ips,"hashes":hashes,"urls":urls,"emails":emails}

def log_summary(text):
    lines=[x for x in text.splitlines() if x.strip()]
    failed=[x for x in lines if re.search(r'\b(failed|denied|error|invalid|blocked)\b',x,re.I)]
    ips=Counter(ip for x in lines for ip in re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b',x))
    return {"lines":len(lines),"alerts":len(failed),"top_ips":ips.most_common(10),"failed_lines":failed[:25]}

def local_dns(host):
    return sorted(set(x[4][0] for x in socket.getaddrinfo(host,None)))

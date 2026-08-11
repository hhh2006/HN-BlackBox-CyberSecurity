from __future__ import annotations
from collections import Counter
from datetime import datetime
import re

def correlate(observations):
    rows=[str(x) for x in observations if str(x).strip()]
    blob=' '.join(rows)
    ips=sorted(set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b',blob)))
    hashes=sorted(set(re.findall(r'\b[a-fA-F0-9]{64}\b',blob)))
    urls=sorted(set(re.findall(r'https?://[^\s]+',blob)))
    counts=Counter(x.lower() for x in re.findall(r'\b[a-z_]{4,}\b',blob))
    signals=[]
    if ips: signals.append({'type':'network','count':len(ips),'items':ips})
    if hashes: signals.append({'type':'evidence','count':len(hashes),'items':hashes})
    if urls: signals.append({'type':'web','count':len(urls),'items':urls})
    return {'generated_at':datetime.now().isoformat(timespec='seconds'),'observations':len(rows),'signals':signals,'keywords':counts.most_common(10)}

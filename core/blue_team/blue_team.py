"""Defensive log-analysis helpers."""
from collections import Counter
import re
FAILED=re.compile(r"(?:failed|failure|invalid|denied)",re.I)
IP=re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
def analyze_log(text):
    lines=text.splitlines(); failed=[]; ips=Counter()
    for line in lines:
        found=IP.findall(line); ips.update(found)
        if FAILED.search(line): failed.append(line.strip())
    suspicious=[(ip,n) for ip,n in ips.items() if n>=5]
    return {"lines":len(lines),"failed":len(failed),"ips":ips.most_common(),"suspicious":suspicious,"failed_lines":failed[:50]}

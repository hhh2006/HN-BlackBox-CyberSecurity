from __future__ import annotations
import re
DEFAULT_RULES=[
 {'id':'AUTH_FAIL','pattern':r'(?i)(failed|failure).*(login|authentication)|invalid password','severity':'medium'},
 {'id':'IOC_IP','pattern':r'\b(?:\d{1,3}\.){3}\d{1,3}\b','severity':'low'},
 {'id':'SUSPICIOUS_EXEC','pattern':r'(?i)(powershell|cmd\.exe|wscript|cscript)','severity':'high'},
]
def evaluate(text,rules=None):
    out=[]
    for r in rules or DEFAULT_RULES:
        if re.search(r['pattern'],str(text)):
            out.append({'rule':r['id'],'severity':r['severity']})
    return out

"""HN BlackBox V40 offline lab environment engine.
Safe, deterministic labs: no network access, no arbitrary command execution.
"""
from __future__ import annotations
import base64, hashlib, ipaddress, json, re, urllib.parse
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

@dataclass(frozen=True)
class Lab:
    id: str
    title: str
    category: str
    difficulty: str
    objective: str
    prompt: str
    answer: str
    hint: str
    artifact: str = ""

LABS = [
    Lab("CRYPTO-01","Caesar Recovery","Cryptography","Beginner","Recover a known Caesar shift","Decrypt KHOOR using shift 3.","HELLO","Shift each letter three positions backward.","ciphertext=KHOOR"),
    Lab("CRYPTO-02","Base64 Recognition","Encoding","Beginner","Decode an encoded artifact","Decode SE5fQkxBQ0tCT1g=.","HN_BLACKBOX","Base64 is encoding, not encryption.","encoding=base64"),
    Lab("CRYPTO-03","Digest Identification","Hashing","Beginner","Identify a digest family","Which common digest has 64 hexadecimal characters?","SHA-256","Compare common digest lengths.","digest=64-hex"),
    Lab("NET-01","Private IPv4","Network","Beginner","Classify an address","Is 192.168.10.5 private? Answer YES or NO.","YES","192.168.0.0/16 is RFC1918 private space.","ip=192.168.10.5"),
    Lab("NET-02","Subnet Hosts","Network","Intermediate","Calculate usable hosts","How many usable IPv4 hosts are in 192.168.50.0/28?","14","A /28 has 16 addresses; reserve network and broadcast.","cidr=192.168.50.0/28"),
    Lab("WEB-01","Query Parsing","Web Security","Beginner","Inspect a URL query","In /search?q=blackbox&page=2, what is page?","2","Parse the query string.","url=/search?q=blackbox&page=2"),
    Lab("WEB-02","Header Defense","Web Security","Intermediate","Select a defensive header","Name one header commonly used to reduce clickjacking risk.","X-FRAME-OPTIONS","It can restrict framing by other origins.","header=clickjacking"),
    Lab("BLUE-01","IOC Extraction","Blue Team","Beginner","Extract an IPv4 IOC","Extract the IP from: failed login from 203.0.113.9","203.0.113.9","Look for the dotted-quad address.","log=failed login from 203.0.113.9"),
    Lab("BLUE-02","Severity Triage","Blue Team","Intermediate","Prioritize an event","Five failed logins followed by success: LOW, MEDIUM, or HIGH?","MEDIUM","Repeated failures warrant investigation but are not automatically critical.","event=5 failures then success"),
    Lab("FORENSIC-01","File Integrity","Forensics","Intermediate","Choose a modern integrity digest","Which is preferred for a modern integrity record: MD5 or SHA-256?","SHA-256","Prefer a modern collision-resistant digest.","artifact=local-file"),
    Lab("LOG-01","Alert Count","Log Analysis","Beginner","Count alert lines","How many alert words are in: OK / FAILED / ERROR / OK?","2","Count FAILED and ERROR.","log=4-lines"),
    Lab("WEB-03","URL Scheme","Web Security","Beginner","Identify transport scheme","What scheme is used by https://example.local/login?","HTTPS","Read the part before ://.","url=https://example.local/login"),
    Lab("FORENSIC-02","SHA-256 Verification","Forensics","Intermediate","Verify an artifact fingerprint","Compute SHA-256 for the artifact text HN-BLACKBOX-ARTIFACT.",hashlib.sha256(b"HN-BLACKBOX-ARTIFACT").hexdigest(),"Use SHA-256 on the exact bytes of the artifact text.","artifact=HN-BLACKBOX-ARTIFACT"),
    Lab("WEB-04","Header Parsing","Web Security","Beginner","Parse a synthetic response","What is the Content-Type value in 'Content-Type: application/json'?","APPLICATION/JSON","Read the value after the colon.","response=synthetic"),
    Lab("BLUE-03","IOC Bundle","Blue Team","Intermediate","Extract multiple IOC types","Extract the IPv4 from the sample bundle.","198.51.100.42","Look for the dotted-quad value.","bundle=198.51.100.42 + SHA256"),
    Lab("CRYPTO-04","URL Encoding","Encoding","Beginner","Decode URL encoding","Decode HN%20BLACKBOX.","HN BLACKBOX","Percent encoding maps bytes to readable characters.","encoding=url"),
]

class LabEngine:
    def __init__(self, state_path: str | Path | None = None):
        root = Path(state_path) if state_path else Path.home() / ".hn_blackbox" / "lab_state.json"
        self.state_path = root
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load()

    def _load(self):
        try: return json.loads(self.state_path.read_text(encoding="utf-8"))
        except Exception: return {"attempts": {}, "completed": [], "scores": {}, "started": {}, "last": None}

    def save(self):
        tmp=self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state,indent=2,ensure_ascii=False),encoding="utf-8")
        tmp.replace(self.state_path)

    def catalog(self, category=None):
        return [asdict(x) for x in LABS if category is None or x.category.lower()==category.lower()]

    def get(self, lab_id):
        for lab in LABS:
            if lab.id.upper()==lab_id.upper(): return lab
        raise KeyError(lab_id)

    def start(self, lab_id):
        lab=self.get(lab_id); self.state["started"][lab.id]=datetime.now().isoformat(timespec="seconds"); self.state["last"]=lab.id; self.save(); return asdict(lab)

    def check(self, lab_id, answer, hints_used=0, elapsed=0):
        lab=self.get(lab_id); attempts=self.state["attempts"].get(lab.id,0)+1; self.state["attempts"][lab.id]=attempts
        ok=str(answer).strip().upper()==lab.answer.strip().upper()
        if ok:
            score=max(10,100-min(60,hints_used*15)-min(25,int(elapsed)//30)-min(20,(attempts-1)*5))
            self.state["completed"]=sorted(set(self.state["completed"]+[lab.id])); self.state["scores"][lab.id]=score
        self.state["last"]=lab.id; self.save()
        return {"correct":ok,"score":self.state["scores"].get(lab.id,0),"attempts":attempts,"completed":lab.id in self.state["completed"]}

    def reset(self):
        self.state={"attempts":{},"completed":[],"scores":{},"started":{},"last":None}; self.save()

    def progress(self):
        total=len(LABS); done=len(self.state["completed"]); return {"total":total,"completed":done,"percent":round(done*100/total),"score":sum(self.state["scores"].values())}

"""Cross-module local intelligence: deterministic scoring and recommendations."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass
class Signal:
    name: str
    score: float
    detail: str


def profile(module: str, payload: Any) -> dict:
    text = str(payload or "")
    signals=[]
    if text:
        signals.append(Signal("DATA_PRESENT", min(1.0,len(text)/500), f"{len(text)} characters available"))
    if module == "cryptanalysis":
        letters=sum(c.isalpha() for c in text)
        signals.append(Signal("LETTER_DENSITY", min(1.0,letters/max(1,len(text))), f"{letters} alphabetic characters"))
    elif module == "network":
        signals.append(Signal("NETWORK_CONTEXT", 0.7 if any(x in text.lower() for x in ("ip","dns","subnet","host")) else 0.2, "network indicators inspected"))
    elif module == "web":
        signals.append(Signal("HTTP_CONTEXT", 0.8 if any(x in text.upper() for x in ("GET ","POST ","HTTP/")) else 0.2, "HTTP-like indicators inspected"))
    elif module == "blue":
        signals.append(Signal("DEFENSIVE_CONTEXT", 0.8 if any(x in text.lower() for x in ("ioc","alert","error","login")) else 0.2, "defensive indicators inspected"))
    confidence=round(sum(s.score for s in signals)/max(1,len(signals)),3)
    return {"module":module,"confidence":confidence,"signals":[asdict(s) for s in signals],"recommendation":recommend(module,signals)}


def recommend(module, signals):
    if module=="cryptanalysis": return "Run frequency/IC/Kasiski next; compare candidates before accepting plaintext."
    if module=="network": return "Validate the parsed address/subnet and preserve the result in the workspace."
    if module=="web": return "Inspect request structure and defensive controls in the safe lab."
    if module=="blue": return "Correlate IOC/event evidence with the incident timeline."
    return "Attach the observation to the current workspace or investigation."

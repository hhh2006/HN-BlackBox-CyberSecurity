"""Local investigation/case container. No external collection is performed."""
from __future__ import annotations
from datetime import datetime
from uuid import uuid4

def new_case(title="Untitled Investigation"):
    return {"id":uuid4().hex[:12],"title":title,"created_at":datetime.now().isoformat(timespec="seconds"),"status":"OPEN","evidence":[],"findings":[],"timeline":[]}

def add_finding(case,title,detail,severity="INFO"):
    case["findings"].append({"title":title,"detail":str(detail),"severity":severity,"at":datetime.now().isoformat(timespec="seconds")})

def add_event(case,event,detail=""):
    case["timeline"].append({"event":event,"detail":str(detail),"at":datetime.now().isoformat(timespec="seconds")})

def close_case(case):
    case["status"]="CLOSED"; case["closed_at"]=datetime.now().isoformat(timespec="seconds"); return case

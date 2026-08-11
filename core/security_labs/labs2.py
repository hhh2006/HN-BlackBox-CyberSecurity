"""Extended local lab progression built around existing labs."""
from __future__ import annotations
from . import labs, lab_progress

def catalog():
    rows=[]
    p=lab_progress.get_progress(); done=set(p.get("completed",[])); attempts=p.get("attempts",{})
    for q in labs.all_labs():
        rows.append({"id":q["id"],"title":q["title"],"difficulty":q["difficulty"],"completed":q["id"] in done,"attempts":attempts.get(q["id"],0)})
    return rows

def score():
    rows=catalog(); return {"completed":sum(r["completed"] for r in rows),"total":len(rows),"attempts":sum(r["attempts"] for r in rows)}

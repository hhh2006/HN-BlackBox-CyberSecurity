"""Small, dependency-free report builders for HN BlackBox."""
from __future__ import annotations

def session_markdown(data):
    lines=["# HN BlackBox // Session Report","",f"- Version: {data.get('version','13.0')}",f"- Saved: {data.get('saved_at','--')}",f"- Started: {data.get('started_at','--')}",f"- Current module: {data.get('current_module','--')}",f"- Current algorithm: {data.get('current_algorithm','--')}",f"- Local history entries: {data.get('history_count',0)}","","## Lab Progress"]
    lp=data.get("lab_progress") or {}; done=lp.get("completed",[]); attempts=lp.get("attempts",{})
    lines.append(f"Completed: {len(done)}")
    for k in done: lines.append(f"- [x] {k} (attempts: {attempts.get(k,0)})")
    lines += ["","## Input","```text",str(data.get("input",'')),"```","","## Result","```text",str(data.get("result",'')),"```","","## Notes",str(data.get("notes",'')) or "No notes.",""]
    return "\n".join(lines)

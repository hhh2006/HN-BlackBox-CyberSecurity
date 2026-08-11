"""Safe cross-module workflow registry."""
from __future__ import annotations
from datetime import datetime
from uuid import uuid4

def new_workflow(name="Untitled Workflow"):
    return {"id":uuid4().hex[:12],"name":name,"created_at":datetime.now().isoformat(timespec="seconds"),"steps":[]}

def add_step(workflow,module,action,input_data="",output_data=""):
    workflow["steps"].append({"module":module,"action":action,"input":str(input_data),"output":str(output_data),"at":datetime.now().isoformat(timespec="seconds")})
    return workflow

def summary(workflow):
    return {"id":workflow.get("id"),"name":workflow.get("name"),"steps":len(workflow.get("steps",[])),"modules":sorted({s.get("module") for s in workflow.get("steps",[])})}

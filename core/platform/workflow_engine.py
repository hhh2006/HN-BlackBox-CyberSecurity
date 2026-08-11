from __future__ import annotations
from datetime import datetime
from uuid import uuid4

def create(name='Untitled Workflow'):
    return {'id':uuid4().hex[:12],'name':name,'created_at':datetime.now().isoformat(timespec='seconds'),'steps':[]}

def add(workflow,module,action,input_data='',output_data=''):
    workflow.setdefault('steps',[]).append({'id':uuid4().hex[:8],'module':module,'action':action,'input':str(input_data),'output':str(output_data),'at':datetime.now().isoformat(timespec='seconds')})
    return workflow

def validate(workflow):
    steps=workflow.get('steps',[])
    return {'valid':bool(workflow.get('name')) and all(s.get('module') and s.get('action') for s in steps),'steps':len(steps),'modules':sorted({s.get('module') for s in steps})}

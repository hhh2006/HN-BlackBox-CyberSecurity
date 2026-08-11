from __future__ import annotations
import importlib.util
from pathlib import Path

def discover(root):
    root=Path(root); root.mkdir(parents=True,exist_ok=True); found=[]
    for path in sorted(root.glob('*/plugin.py')):
        try:
            spec=importlib.util.spec_from_file_location('hn_plugin_'+path.parent.name,path)
            mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            meta=getattr(mod,'PLUGIN',{'name':path.parent.name,'version':'0.0','description':''})
            found.append({'id':path.parent.name,**meta})
        except Exception as exc:
            found.append({'id':path.parent.name,'error':str(exc)})
    return found

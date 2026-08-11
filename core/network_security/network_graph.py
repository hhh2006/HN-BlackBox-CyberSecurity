from __future__ import annotations

def build(edges):
    nodes={}; links=[]
    for a,b,kind in edges:
        a=str(a); b=str(b); nodes.setdefault(a,{'id':a,'kind':'entity'}); nodes.setdefault(b,{'id':b,'kind':'entity'})
        links.append({'source':a,'target':b,'kind':str(kind)})
    return {'nodes':list(nodes.values()),'links':links}

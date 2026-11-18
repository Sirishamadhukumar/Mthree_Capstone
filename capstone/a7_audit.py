from __future__ import annotations
import json,hashlib,datetime
from pathlib import Path
try: from .a7_guard import redact_pii
except Exception:
    from a7_guard import redact_pii
def _scrub(v):
    if isinstance(v,str):return redact_pii(v)
    if isinstance(v,dict):return {k:_scrub(x) for k,x in v.items()}
    if isinstance(v,list):return [_scrub(x) for x in v]
    if isinstance(v,tuple):return [_scrub(x) for x in v]
    return v
def _hash(d):return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
class AuditLog:
    def __init__(self,path):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True);self.path.touch(exist_ok=True)
    def entries(self):
        out=[]
        for line in self.path.read_text(encoding='utf-8').splitlines():
            try:out.append(json.loads(line))
            except json.JSONDecodeError:out.append({'_invalid':line})
        return out
    def append(self,trace_id,user,tool,args,sources,outcome):
        prev=self.entries();seq=len(prev);prev_hash=prev[-1].get('hash','0'*64) if prev else '0'*64
        entry={'seq':seq,'ts':datetime.datetime.now(datetime.timezone.utc).isoformat(),'trace_id':str(trace_id),'user':redact_pii(str(user)),'tool':str(tool),'args':_scrub(args or {}),'sources':_scrub(list(sources or [])),'outcome':redact_pii(str(outcome)),'prev_hash':prev_hash}
        entry['hash']=_hash(entry); 
        with self.path.open('a',encoding='utf-8') as f:f.write(json.dumps(entry,sort_keys=True,ensure_ascii=False)+'\n')
        return entry
    def verify(self):
        entries=self.entries();prev='0'*64
        for i,e in enumerate(entries):
            if '_invalid' in e:return {'ok':False,'first_bad':i,'entries':len(entries)}
            h=e.get('hash'); raw={k:v for k,v in e.items() if k!='hash'}
            if e.get('seq')!=i or e.get('prev_hash')!=prev or h!=_hash(raw):return {'ok':False,'first_bad':i,'entries':len(entries)}
            prev=h
        return {'ok':True,'first_bad':None,'entries':len(entries)}

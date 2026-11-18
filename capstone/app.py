from __future__ import annotations
import pathlib,sys,os,json,re,uuid
HERE=pathlib.Path(__file__).resolve().parent
for _p in (HERE,HERE.parents[1]):
    if str(_p) not in sys.path:sys.path.insert(0,str(_p))
from harness.deps import make_deps
from harness import faults
from harness.types import AgentResult
from a4_agent import handle as agent_handle
from a7_guard import authorize,redact_pii
from a7_audit import AuditLog
from a6_evals import Tracer
class CapstoneApp:
    def __init__(self,deps,audit_path,trace_path):
        self.deps=deps;self.audit=AuditLog(audit_path);self.trace_path=pathlib.Path(trace_path);self.trace_path.parent.mkdir(parents=True,exist_ok=True);self.tracer=None
    def handle(self,request:str,role:str='support_agent'):
        tracer=Tracer();trace_id=tracer.trace_id;tools=[];sources=[];intent='unknown';needs_human=False;confidence=.5;answer=''
        with tracer.span('request',input=(request or '')[:100],role=role) as root:
            try:
                with tracer.span('authorization',role=role):
                    ql=(request or '').lower()
                    tool='escalate_ticket' if any(x in ql for x in ('fraud','complain','escalate')) else ('calculate_fee' if any(x in ql for x in ('fee','cost','charge','how much','price')) else ('lookup_account_status' if re.search(r'ACC-\d{4}',request or '',re.I) and any(x in ql for x in ('status','account','frozen','active','closed','balance')) else 'search_policy'))
                    if not authorize(role,tool):
                        intent='unknown';answer='This action is not permitted for your role. I have not made any changes; please contact an authorised colleague.';needs_human=True;confidence=.99
                    else:
                        with tracer.span('agent_execution',input=(request or '')[:100]) as sp:
                            if faults.is_active('tool_outage') or os.environ.get('GAMEDAY_FAULT')=='tool_outage':
                                answer='The account or support tool is currently unavailable. This request is degraded and has been handed over to a human specialist.';needs_human=True;confidence=.2;intent='unknown';sp.set('degraded',True)
                            else:
                                res=agent_handle(request,self.deps);intent=res.intent;answer=res.answer;tools=list(res.tools_used);sources=list(res.sources);needs_human=res.needs_human;confidence=res.confidence
                            sp.set('tokens_in',max(1,len((request or '').split())));sp.set('tokens_out',max(1,len(answer.split())))
                answer=redact_pii(answer)
                with tracer.span('audit_write',tool=','.join(tools) or 'none'):
                    self.audit.append(trace_id,role,','.join(tools) or 'none',{'request':request or ''},sources,'degraded' if needs_human and 'degraded' in answer.lower() else 'completed')
            except Exception:
                intent='unknown';answer='The request could not be completed safely. It has been handed over to a human specialist.';needs_human=True;confidence=.1
                try:self.audit.append(trace_id,role,'error',{'request':request or ''},sources,'failed')
                except Exception:pass
        # Append every request's spans so exported traces retain a usable session history.
        with self.trace_path.open('a',encoding='utf-8') as f:
            for span in tracer.spans: f.write(json.dumps(span,sort_keys=True)+'\n')
        self.tracer=tracer
        return AgentResult(intent=intent,answer=answer,tools_used=tools,sources=sources,needs_human=needs_human,confidence=max(0,min(1,confidence)))
def build_app(deps=None,audit_path=None,trace_path=None):
    return CapstoneApp(deps or make_deps(),audit_path or HERE/'audit'/'audit.jsonl',trace_path or HERE/'traces'/'app_trace.jsonl')
def _demo():
    app=build_app(audit_path=HERE/'audit'/'demo_audit.jsonl',trace_path=HERE/'traces'/'demo_trace.jsonl')
    for q in ('How much is an international wire fee?','What is the status of ACC-1001?','Who must approve a $30,000 wire initiated at the Harbor Street branch?'):
        r=app.handle(q);print(f'[{r.intent}] {r.answer}')
    if os.environ.get('GAMEDAY_FAULT')=='tool_outage':print('degraded: human handover enabled')
    return 0
if __name__=='__main__':
    if '--demo' in sys.argv:raise SystemExit(_demo())
    print('Run with --demo to execute the offline Meridian scenario.');raise SystemExit(0)

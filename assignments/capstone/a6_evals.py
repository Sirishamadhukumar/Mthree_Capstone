from __future__ import annotations
import time,json,uuid,math,re
from pathlib import Path
from harness.text import tokenize,HashingEmbedder,cosine

def context_precision(retrieved,gold):
    g=set(gold); positions=[i for i,x in enumerate(retrieved,1) if x in g]
    return sum(sum(1 for y in retrieved[:i] if y in g)/i for i in positions)/len(positions) if positions else 0.0
def context_recall(retrieved,gold):
    g=set(gold); return len(set(retrieved)&g)/len(g) if g else 0.0
def faithfulness(answer,contexts,threshold=0.6):
    ct=set(t for c in contexts for t in tokenize(c)); sents=re.split(r'[.!?\n]+',answer or ''); vals=[]
    for s in sents:
        toks=tokenize(s)
        if toks: vals.append(sum(t in ct for t in toks)/len(toks)>=threshold)
    return sum(vals)/len(vals) if vals else 0.0
def answer_relevance(question,answer):
    if not answer: return 0.0
    e=HashingEmbedder(); return max(0.0,cosine(e.embed(question),e.embed(answer)))
def tool_call_accuracy(expected,actual):
    if not expected and not actual:return 1.0
    cursor=0;matched=0
    for e in expected:
        for i in range(cursor,len(actual)):
            a=actual[i]
            if a.get('name')==e.get('name') and all(a.get('args',{}).get(k)==v for k,v in e.get('args',{}).items()):
                matched+=1;cursor=i+1;break
    return matched/max(len(expected),len(actual))

def _pct(xs,p):
    if not xs:return 0.0
    ys=sorted(xs); return ys[max(0,math.ceil(p*len(ys))-1)]
def run_eval(system_fn,dataset,clock=time.perf_counter,usd_per_1k_tokens=0.002):
    rows=[]; lats=[]; tin=tout=0; metrics={k:[] for k in ('context_precision','context_recall','faithfulness','answer_relevance','tool_call_accuracy')}
    for item in dataset:
        st=clock(); result=system_fn(item['question']); elapsed=max(0,(clock()-st)*1000); lats.append(elapsed)
        result=result or {}; gold=item.get('gold_docs',[]); retrieved=result.get('retrieved_ids',[]); answer=result.get('answer',''); contexts=result.get('contexts',[])
        if gold: metrics['context_precision'].append(context_precision(retrieved,gold)); metrics['context_recall'].append(context_recall(retrieved,gold))
        metrics['faithfulness'].append(faithfulness(answer,contexts)); metrics['answer_relevance'].append(answer_relevance(item['question'],answer))
        if 'expected_tool_calls' in item: metrics['tool_call_accuracy'].append(tool_call_accuracy(item['expected_tool_calls'],result.get('tool_calls',[])))
        ti=int(result.get('tokens_in',0)); to=int(result.get('tokens_out',0));tin+=ti;tout+=to
        rows.append({'id':item.get('id'),'latency_ms':elapsed,'tokens_in':ti,'tokens_out':to,'context_precision':context_precision(retrieved,gold) if gold else None,'context_recall':context_recall(retrieved,gold) if gold else None,'faithfulness':faithfulness(answer,contexts),'answer_relevance':answer_relevance(item['question'],answer)})
    out={'n':len(rows),'metrics':{k:sum(v)/len(v) for k,v in metrics.items() if v},'latency_ms':{'p50':_pct(lats,.5),'p95':_pct(lats,.95)},'tokens':{'in':tin,'out':tout},'sim_cost_usd':(tin+tout)/1000*usd_per_1k_tokens,'per_sample':rows}
    return out
class _Span:
    def __init__(self,tracer,name,attrs,parent): self.t=tracer;self.name=name;self.attrs=dict(attrs);self.parent=parent;self.start=None;self.item=None
    def __enter__(self):
        self.start=self.t.clock(); self.item={'trace_id':self.t.trace_id,'span_id':uuid.uuid4().hex,'parent_id':self.parent,'name':self.name,'start_ms':(self.start-self.t.origin)*1000,'end_ms':None,'attrs':self.attrs}; self.t.spans.append(self.item);self.t.stack.append(self.item['span_id']);return self
    def set(self,key,value): self.attrs[key]=value; self.item['attrs'][key]=value
    def __exit__(self,typ,val,tb):
        end=self.t.clock();self.item['end_ms']=(end-self.t.origin)*1000
        if typ:self.item['attrs']['error']=typ.__name__
        if self.t.stack:self.t.stack.pop()
        return False
class Tracer:
    def __init__(self,clock=time.perf_counter): self.clock=clock;self.origin=clock();self.trace_id=uuid.uuid4().hex;self.spans=[];self.stack=[]
    def span(self,name,**attrs): return _Span(self,name,attrs,self.stack[-1] if self.stack else None)
    def to_jsonl(self,path):
        p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('w',encoding='utf-8') as f:
            for s in self.spans:f.write(json.dumps(s,sort_keys=True)+'\n')
def analyze_trace(path_or_spans):
    if isinstance(path_or_spans,(str,Path)):
        p=Path(path_or_spans); spans=[json.loads(x) for x in p.read_text(encoding='utf-8').splitlines() if x.strip()]
    else: spans=list(path_or_spans)
    if not spans:return {'total_ms':0,'slowest_span':None,'slowest_ms':0,'duplicate_calls':[],'total_tokens':0,'span_count':0}
    dur=lambda s:(s.get('end_ms') or s.get('start_ms',0))-s.get('start_ms',0)
    roots=[s for s in spans if s.get('parent_id') is None]; root=roots[0] if roots else spans[0]; kids=[s for s in spans if s is not root]
    counts={}
    for s in kids:
        inp=s.get('attrs',{}).get('input')
        if inp is not None:
            key=(s.get('name'),str(inp));counts[key]=counts.get(key,0)+1
    dup=[{'name':n,'count':c} for (n,_),c in counts.items() if c>1];dup.sort(key=lambda x:-x['count'])
    slow=max(kids,key=dur) if kids else None
    return {'total_ms':dur(root),'slowest_span':slow.get('name') if slow else None,'slowest_ms':dur(slow) if slow else 0,'duplicate_calls':dup,'total_tokens':sum(s.get('attrs',{}).get('tokens_in',0)+s.get('attrs',{}).get('tokens_out',0) for s in spans),'span_count':len(spans)}

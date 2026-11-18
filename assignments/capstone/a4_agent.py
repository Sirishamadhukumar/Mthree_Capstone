from __future__ import annotations
import re
from harness.types import AgentResult, ToolError
import a4_tools as tools

def handle(request: str, deps) -> AgentResult:
    q=request or ''; ql=q.lower(); used=[]; sources=[]
    try:
        accm=re.search(r'\bACC-\d{4}\b',q,re.I); acc=accm.group(0).upper() if accm else None
        fee_words={'international wire':'international_wire','domestic wire':'domestic_wire','incoming wire':'incoming_wire','wire recall':'wire_recall','stop payment':'stop_payment','overdraft':'overdraft','paper statement':'paper_statement','card replacement':'card_replacement','excess withdrawal':'excess_withdrawal'}
        ft=next((v for k,v in fee_words.items() if k in ql),None)
        if any(x in ql for x in ('escalate','fraud','complain')):
            used.append('escalate_ticket'); reason=q[:300] or 'Customer request'; priority='P1' if 'fraud' in ql else 'P3'
            t=tools.escalate_ticket(deps.tickets,acc or '',reason,priority)
            return AgentResult(intent='escalation',answer=f'I created escalation ticket {t.ticket_id}. A human specialist will review this request.',tools_used=used,needs_human=True,confidence=.9)
        if ft and any(x in ql for x in ('fee','cost','charge','how much','price')):
            qtym=re.search(r'\b(\d+)\s+(?:(?:domestic|international|incoming)\s+)?wires?\b',ql); qty=int(qtym.group(1)) if qtym else 1
            plan='business_current' if 'business current' in ql else ('premier_saver' if 'premier saver' in ql else None)
            used.append('calculate_fee'); quote=tools.calculate_fee(ft,qty,plan)
            return AgentResult(intent='fee_quote',answer=f'The {ft.replace("_"," ")} fee is ${quote.unit_fee:.2f} per item. Quantity: {qty}; free allowance: {quote.free_quantity}; total: ${quote.total:.2f} under schedule {quote.schedule_id}.',tools_used=used,confidence=.98)
        if acc and any(x in ql for x in ('status','account','frozen','active','balance','closed')):
            used.append('lookup_account_status'); s=tools.lookup_account_status(deps.db,acc)
            answer=f'Account {acc} status is {s.status}; product: {s.product}.'
            if s.freeze_reason: answer+=f' Freeze reason: {s.freeze_reason}.'
            return AgentResult(intent='account_status',answer=answer,tools_used=used,needs_human=s.status.lower()=='frozen',confidence=.95)
        used.append('search_policy'); hits=tools.search_policy(deps.retriever,q,4)
        # Strip instruction-like sentences before composing, and never pass raw retrieved text as instructions.
        from a7_guard import sanitize_context, redact_pii
        clean=[]
        for h in hits:
            text=sanitize_context(h['text'])
            if text.strip(): clean.append((h['doc_id'],text))
        qtokens=set(re.findall(r'[a-z0-9]+',ql)); ranked=sorted(clean,key=lambda x:len(qtokens & set(re.findall(r'[a-z0-9]+',x[1].lower()))),reverse=True)
        relevant=[x for x in ranked if len(qtokens & set(re.findall(r'[a-z0-9]+',x[1].lower())))>=2]
        if not relevant: return AgentResult(intent='policy_question',answer='I could not find enough information in the available policy documents to answer that question. Please contact a human support specialist.',tools_used=used,confidence=.35)
        sources=list(dict.fromkeys(x[0] for x in relevant[:3])); answer='Based on the available policy documents: '+' '.join(x[1] for x in relevant[:2])+ '\nSources: '+', '.join(sources)
        return AgentResult(intent='policy_question',answer=redact_pii(answer),tools_used=used,sources=sources,confidence=.82)
    except Exception as e:
        msg=getattr(e,'message','') or 'I could not complete the request because the account could not be found or a supporting service is unavailable.'
        if getattr(e,'code','')=='account_not_found': msg='I could not complete the request because the account could not be found.'
        return AgentResult(intent='unknown',answer=msg,tools_used=used,needs_human=True,confidence=.2)

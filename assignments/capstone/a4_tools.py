from __future__ import annotations
from typing import Optional
import re
from pydantic import BaseModel
from harness.types import ToolError
from harness.backends import load_fee_schedule
class AccountStatus(BaseModel):
    account_id:str; product:str; status:str; masked_account_number:str; freeze_reason:Optional[str]=None
class FeeQuote(BaseModel):
    fee_type:str; unit_fee:float; quantity:int; free_quantity:int; total:float; schedule_id:str
class Ticket(BaseModel):
    ticket_id:str; account_id:str; reason:str; priority:str; created_new:bool
ACC=re.compile(r'^ACC-\d{4}$')
def _acc(db, account_id):
    if not isinstance(account_id,str) or not ACC.fullmatch(account_id): raise ToolError('invalid_account_id','Account ID must match ACC-0000.')
    row=db.get(account_id)
    if not row: raise ToolError('account_not_found','No account was found for that ID.')
    return row
def lookup_account_status(db, account_id):
    row=_acc(db,account_id); number=str(row.get('account_number',row.get('card_number','')))
    digits=re.sub(r'\D','',number)
    masked='*'*max(0,len(digits)-4)+digits[-4:] if digits else '************'
    return AccountStatus(account_id=account_id,product=row.get('product','unknown'),status=row.get('status','unknown'),masked_account_number=masked,freeze_reason=row.get('freeze_reason'))
def calculate_fee(fee_type, quantity=1, plan=None):
    schedule=load_fee_schedule()
    if fee_type not in schedule['fees']: raise ToolError('unknown_fee_type','That fee type is not supported.')
    if not isinstance(quantity,int) or quantity<1 or quantity>1000: raise ToolError('invalid_quantity','Quantity must be between 1 and 1000.')
    if plan not in (None,'business_current','premier_saver'): raise ToolError('unknown_plan','That plan is not supported.')
    free=int(schedule.get('free_allowance',{}).get(fee_type,{}).get(plan,0)) if plan else 0
    billable=max(0,quantity-free)
    return FeeQuote(fee_type=fee_type,unit_fee=float(schedule['fees'][fee_type]),quantity=quantity,free_quantity=free,total=round(float(schedule['fees'][fee_type])*billable,2),schedule_id=schedule['schedule_id'])
def escalate_ticket(store, account_id, reason, priority):
    if not isinstance(account_id,str) or not ACC.fullmatch(account_id): raise ToolError('invalid_account_id','Account ID must match ACC-0000.')
    norm=' '.join(str(reason).split())
    if priority not in ('P1','P2','P3'): raise ToolError('invalid_priority','Priority must be P1, P2 or P3.')
    if not norm or len(norm)>300: raise ToolError('invalid_reason','Reason must contain 1 to 300 characters.')
    for t in store.all():
        if t['account_id']==account_id and ' '.join(t['reason'].split()).casefold()==norm.casefold() and t['priority']==priority:
            return Ticket(ticket_id=t['ticket_id'],account_id=account_id,reason=t['reason'],priority=priority,created_new=False)
    tid=f'TCK-{len(store.all())+1:04d}'; store.add({'ticket_id':tid,'account_id':account_id,'reason':norm,'priority':priority})
    return Ticket(ticket_id=tid,account_id=account_id,reason=norm,priority=priority,created_new=True)
def search_policy(retriever, query, k=4):
    hits=retriever(query,k)
    return [{'doc_id':h['doc_id'],'chunk_id':h['chunk_id'],'text':h['text']} for h in hits]

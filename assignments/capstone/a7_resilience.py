from __future__ import annotations
import time
class CircuitBreaker:
    def __init__(self,failure_threshold=3,reset_after_s=30.0,clock=time.monotonic):
        self.failure_threshold=max(1,int(failure_threshold));self.reset_after_s=reset_after_s;self.clock=clock;self.failures=0;self._state='closed';self.opened_at=None;self.trial=False
    @property
    def state(self): return self._state
    def allow(self):
        if self._state=='closed':return True
        if self._state=='open' and self.clock()-self.opened_at>=self.reset_after_s:self._state='half_open';self.trial=True;return True
        if self._state=='half_open' and not self.trial:self.trial=True;return True
        return False
    def record_success(self): self.failures=0;self._state='closed';self.opened_at=None;self.trial=False
    def record_failure(self):
        if self._state=='half_open' or self.failures+1>=self.failure_threshold:self._state='open';self.opened_at=self.clock();self.trial=False;self.failures=self.failure_threshold
        else:self.failures+=1

def call_with_resilience(fn,*,retries=3,base_delay=.1,max_delay=2.0,timeout_budget_s=5.0,fallback=None,breaker=None,sleep=time.sleep,clock=time.monotonic,retry_on=(Exception,)):
    start=clock();attempts=0;err=None;value=None;ok=False
    if breaker is not None and not breaker.allow(): err={'type':'CircuitOpen','message':'Circuit breaker is open'}
    else:
        for n in range(max(0,retries)+1):
            attempts+=1
            try:value=fn();ok=True;err=None
            except Exception as e:
                err={'type':type(e).__name__,'message':str(e)}
                if breaker:breaker.record_failure()
                if not isinstance(e,retry_on) or n>=retries:break
                delay=min(base_delay*(2**n),max_delay)
                if clock()-start+delay>timeout_budget_s:err={'type':'TimeoutBudgetExceeded','message':'Retry delay would exceed timeout budget'};break
                sleep(delay);continue
            if breaker:breaker.record_success()
            break
    elapsed=max(0,clock()-start);used=False
    if not ok and fallback is not None:
        try:value=fallback();ok=True;used=True
        except Exception as e:err={'type':type(e).__name__,'message':str(e)}
    return {'ok':ok,'value':value,'attempts':attempts,'error':err,'used_fallback':used,'elapsed_s':elapsed}

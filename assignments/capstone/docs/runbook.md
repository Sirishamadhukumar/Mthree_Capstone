# Operations runbook

## Start
From `kit/`, create a Python 3.11+ virtual environment, install `requirements.txt`, and run `python assignments/capstone/app.py --demo`. No network access is required.

## Health and probes
Run `python assignments/capstone/app.py --demo` for a smoke test. Run `python -m autograde.run --capstone --root . -v` for the public checks. Inspect `assignments/capstone/traces/` for span timings and `assignments/capstone/audit/` for the hash-chained audit log. Verify a log by importing `AuditLog(path).verify()`.

## Game day
Set `GAMEDAY_FAULT=tool_outage`, run the demo, and confirm the output says degraded and a human handover is recommended. Unset the variable and repeat to confirm recovery. The harness also supports `bad_retrieval`, `cost_spike` and `slow_tool`; use these in controlled tests and compare p95 latency, token usage, top-ranked source, degraded count and slowest span.

## Incidents
- **Tool outage:** preserve traces/audit, confirm degraded handover, check the backend dependency, restore it, then rerun the smoke test. Never report success while the dependency is down.
- **Wrong source:** verify corpus metadata and current status; compare BM25/hybrid rankings and ensure FEES-000 is excluded.
- **PII or injection finding:** stop affected flow, preserve sanitized evidence, inspect source document, update detector/tests, rerun safety suite.
- **Audit verification failure:** restrict writes, preserve a copy, record the first bad sequence, and investigate deletion/reordering/editing before recovery.

This is a local proof-of-concept runbook. Production needs paging, durable queues, access-controlled logs and approved recovery procedures.

## Health check
Check the Python process exits successfully, the demo returns a valid AgentResult, audit verification returns `ok: true`, and the trace file has a root span plus child spans. Compare the newest audit sequence and trace timestamp to confirm requests are still being processed.

## Troubleshooting
If imports fail, confirm the working directory is the kit root and dependencies from requirements.txt are installed in the active environment. If the policy answer is unsupported, inspect the top retrieval hits and the document status metadata. If PII appears in an answer, stop the demo and add a regression case to the guard tests before proceeding. If the audit chain fails, do not delete the offending entry or silently start a new chain; preserve the original evidence.

## Escalation
A degraded response, frozen account, fraud allegation, or uncertain policy interpretation should go to a human support specialist. In this local demo, handover is represented in the answer and `needs_human` field; it is not a live ticketing queue. Notify the service owner with the request ID, time, sanitized trace and audit verification result. Do not include raw customer data in incident notes.

## Rollback
For a code release, preserve the prior zip and the evaluation outputs. Revert to the last known-good version if the smoke test, safety checks, evidence checks or quality gate fail. Re-run the demo and evaluation after rollback. Do not roll back policy data without confirming the effective date and status, because an older fee schedule can produce incorrect quotes.

## Known issues
The RuleLLM and fake backends are deterministic teaching doubles. Retrieval uses lexical/hashing features and can miss paraphrases. Pattern-based injection detection is not comprehensive. Audit hash chaining detects individual modifications but cannot defend against an attacker who can rewrite the entire file and every hash. No production authentication, encrypted log storage, durable tickets, alerting or real human queue is implemented. These limitations must be closed and independently reviewed before real customer use.

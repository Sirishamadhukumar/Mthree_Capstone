# Threat model

| Threat | Example | Control | Residual risk |
|---|---|---|---|
| Prompt injection | Retrieved FAQ asks the assistant to reveal secrets | Detect patterns and remove flagged sentences; system prompt treats excerpts as data | Novel indirect attacks may evade patterns |
| PII exposure | Account backend contains phone/email/card data | Narrow schemas, output redaction, audit argument redaction | Redaction can have false positives/negatives |
| Unauthorized action | Analyst attempts account lookup or transaction | Explicit role/tool allowlist before execution | Identity/role provenance is outside this local demo |
| Stale policy | 2023 fee schedule outranks current policy | Status metadata and superseded filter | Metadata errors require governance |
| Backend outage | Account service fails | Safe degraded response and human handover | Manual queue is simulated |
| Audit tampering | Edit or remove a JSONL entry | Sequence, previous hash and SHA-256 verification | Full-chain rewrite by privileged attacker remains possible |
| Duplicate side effect | Retry escalation request | Idempotency key based on normalized account/reason/priority | In-memory store resets on restart |

Assets are synthetic accounts, policy text, support tickets, trace and audit files. Trust boundaries exist between caller, retrieved corpus, model, tools and back-office adapters.

# Business case

Meridian Support Assistant is a proof of concept for reducing repetitive policy lookups while retaining human control over sensitive actions. The initial use case is support triage: account status checks, fee quotes, policy answers and escalation tickets. The expected value is faster, more consistent answers and auditable evidence of which policy documents were used.

The demo is offline and has no usage-based model spend. Evaluation reports use simulated token cost only; it is not an invoice or forecast. A production business case should measure average handle time, deflection rate, escalation precision, answer correctness and operational cost against a staffed baseline. No savings claim is made until those measurements are collected.

Risks include stale policy content, prompt injection, personal-data leakage, inappropriate access and backend outages. Mitigations include superseded-document filtering, untrusted-context sanitization, least-privilege role checks, output/audit redaction, human handover and a circuit-breaker utility. The pilot should be limited to read-only support use until the bank's security, privacy, legal and operations teams approve a broader scope.

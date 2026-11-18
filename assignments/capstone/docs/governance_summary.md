# Governance summary

The assistant is a support aid, not an autonomous financial decision-maker. It must identify the current policy source, decline unsupported questions, protect personal data, enforce role-based permissions and route ambiguous or failed cases to a human. High-impact actions require explicit authorization and human approval.

Policy owners should approve and version corpus changes, mark superseded documents, and review evaluation failures before release. Operations should monitor p95 latency, token counts, source ranking, degraded responses and slow spans. Audit integrity should be verified during deployment and incident response. Access to audit and trace files must be restricted; retention and deletion should follow bank policy.

Before production, add authenticated identity propagation, centralized secret management, encrypted storage, access-controlled immutable log export, human queue integration, privacy/legal review, formal threat modeling and evaluation against representative approved data.


## Release controls and accountability
A named business owner should approve each supported intent, define acceptable error rates and confirm the current policy corpus. A technical owner should maintain regression tests, document model and retrieval changes, and approve deployments only when the evaluation gate passes. The support team remains accountable for customer outcomes; the assistant cannot override bank policy or make final decisions on fraud, disputes, or payment approvals.

Evaluation results should be reviewed for subgroup or workflow-specific failures rather than only an overall average. New policy documents, attack examples and data schemas require tests before release. Incidents involving possible disclosure, unauthorized access, incorrect financial guidance or broken audit integrity must be escalated to security and the policy owner.

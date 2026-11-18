# Agent design brief

## Purpose
Provide policy-grounded support answers, safe fee quotes and account status lookups, with escalation for cases requiring human judgment.

## Users and scope
Support agents and payments agents may use authorized support tools; analysts have read-only policy/fee access. This local demo does not execute transfers.

## Success criteria
The app starts offline, cites real policy sources, uses current documents, does not leak PII, logs each request, emits at least three trace spans and degrades safely under an injected tool outage. Automated evaluation and human review are required before any production use.

## Non-goals
No real banking connection, production identity, autonomous money movement, external model API or production service-level guarantee.

# Decision log

## 2026-10-24 — offline architecture
- **Decision:** use the provided harness, deterministic rule-based LLM, pure-Python tools and JSONL traces/audit.
- **Reason:** the capstone explicitly requires offline operation, zero keyed/paid services and reproducibility.
- **Alternatives:** hosted LLM and managed vector database were rejected because they violate the constraints; a local Ollama model remains optional, not a dependency.
- **Retrieval:** section chunks for policy interpretability; hybrid retrieval is available for experiments; superseded documents are filtered by default.
- **Safety:** narrow typed tools, role authorization before side effects, prompt-injection filtering, PII redaction and explicit human handover on outage.
- **Trade-off:** deterministic lexical methods are less semantic than modern embedding models, but transparent and reliable offline.
- **AI disclosure:** an AI assistant helped draft and implement parts of this completion. I will review, test, and be prepared to explain and modify all submitted code.

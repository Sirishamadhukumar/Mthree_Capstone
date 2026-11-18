# Meridian Support Assistant — offline capstone

## Quick start
Use Python 3.11+ (tested with 3.13). From the `kit` directory create and activate a virtual environment, install `-r requirements.txt`, then run `python assignments/capstone/app.py --demo`. No API keys, network services, `.env`, or paid model are needed. Run checks with `python -m autograde.run --capstone --root . -v`.

## What it does
This is a fictional bank support assistant combining policy retrieval, typed tools, role authorization, PII redaction, an append-only hash-chained audit log, trace spans, evaluation metrics and graceful degradation. The data under `data/` is synthetic. The local harness provides a deterministic rule-based LLM and BM25 retriever, so the project runs offline and is repeatable. The app routes fee and account questions to narrow tools and policy questions to retrieval; it does not move money. Escalations create idempotent tickets and request human review. Tool failures return a safe handover rather than a stack trace.

## Chunking and retrieval choices
The RAG index supports section, fixed-window and sentence-grouped semantic chunking. Section chunking is the default because policy headings preserve context and make document-level citations understandable; fixed chunks help long sections but may split conditions from their exceptions. The index stores `doc_id`, `chunk_id`, and current/superseded status. Hybrid retrieval fuses BM25 and deterministic hashing-embedding ranks using reciprocal-rank fusion. This is a low-cost lexical/dense approximation, not a semantic embedding model. Superseded documents are excluded by default to avoid returning the 2023 fee schedule. Optional reranking favors query-token overlap.

## Safety and limitations
Retrieved content is untrusted data. Injection-like sentences are removed before evidence reaches answer composition. The guard uses families of patterns rather than a fixed attack list; this is defense in depth, not a proof against every adversarial phrasing. PII is redacted in answers and recursively in audit arguments. The audit hash chain detects edits, deletions and reordering but does not prevent an attacker with write access from rebuilding the entire chain. Restrict filesystem access and export logs to protected retention storage in a real deployment. Account and ticket backends are in-memory test doubles, not production systems.

## Evaluation and operations
`a6_evals.py` implements context precision/recall, faithfulness, answer relevance, tool-call accuracy, latency percentiles, token totals and explicitly simulated cost. `eval_gate.py` is suitable for a CI threshold gate. The game-day probe and reports are under `reports/`; regenerate measurements with your own run before submission. The deterministic hashing embedder is reproducible but can miss paraphrases, so review retrieval failures instead of relying on one aggregate metric.

## Project structure
- `a2_rag.py`: chunking, indexing and retrieval.
- `a4_tools.py`, `a4_agent.py`: safe tools and routing.
- `a6_evals.py`, `eval_gate.py`: evaluation and tracing.
- `a7_guard.py`, `a7_resilience.py`, `a7_audit.py`: safety, retry/circuit breaker and tamper evidence.
- `app.py`: integrated request path.
- `stretch/`: optional graph, memory and human-approval orchestration.

## AI-use disclosure
An AI assistant was used to help draft and implement parts of this starter completion. Review and understand every function, run the tests yourself, and update `docs/decision_log.md` with any changes you make before submission.

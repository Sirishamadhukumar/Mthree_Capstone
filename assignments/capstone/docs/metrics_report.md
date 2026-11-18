# Metrics report

This report is a measurement template, not a claim of measured production performance. Run the same `eval_dataset.jsonl` through the baseline and changed implementation, save the raw `run_eval()` outputs as `reports/eval_baseline.json` and `reports/eval_after.json`, and replace this text with observed values. Report context precision and recall, faithfulness, answer relevance, tool-call accuracy when expected calls exist, p50/p95 latency, token totals and simulated cost. State sample count, run date, and known limitations.

Interpretation: use failures at the individual-question level to identify stale or irrelevant retrieval, unsupported claims, tool-routing errors and degraded paths. The simulated cost is a transparent arithmetic estimate only.

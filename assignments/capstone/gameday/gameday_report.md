# Game-day report

## Scenario and method
The harness exposes `tool_outage`, `bad_retrieval`, `cost_spike` and `slow_tool`. Set `GAMEDAY_FAULT` or use `harness.faults.inject(name)` in a test. The outage scenario should produce a safe degraded result and human handover, not a confident success.

## Results to record
| Scenario | p95 latency (ms) | tokens/request | correct top document? | degraded answers | slowest span |
|---|---:|---:|---|---:|---|
| Normal | Run probe | Run probe | Run probe | Run probe | Run probe |
| tool_outage | Run probe | Run probe | N/A | Run probe | Run probe |
| bad_retrieval | Run probe | Run probe | Run probe | Run probe | Run probe |
| cost_spike | Run probe | Run probe | Run probe | Run probe | Run probe |
| slow_tool | Run probe | Run probe | Run probe | Run probe | Run probe |

## Analysis and mitigation
Record actual observed values after running the probe; do not invent measurements. For an outage, preserve evidence, return a degraded handover and restore service before retrying. For bad retrieval, inspect ranks and metadata. For cost spikes, cap context and investigate token multipliers. For slow tools, use timeouts, bounded retries and circuit breaking.

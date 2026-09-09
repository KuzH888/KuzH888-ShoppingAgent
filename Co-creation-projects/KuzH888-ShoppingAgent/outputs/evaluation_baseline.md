# Development Baseline Evaluation

> This is a development baseline. Re-run after replacing products and images; it is not the final submission score.

## Evaluation context

- Mode: `offline-simulation`
- Cases: 19
- Products: 24
- Catalogue version: `1.0.0`
- Catalogue SHA-256: `e6ed2e4b30b08a5da7b1509a83abbff77cebf349c842f517ff1a7a964ea4b2f8`
- Generated at: `2026-09-09T11:53:30.289997+00:00`

## Metrics

| Metric | Result |
|---|---:|
| Overall case pass rate | 100.00% |
| Expected recommendation result | 100.00% |
| Hard-constraint satisfaction | 100.00% |
| Catalogue grounding | 100.00% |
| Language consistency | 100.00% |
| Average local latency | 1.319 ms |
| P95 local latency | 18.203 ms |

## Case results

| Case | Type | Passed | Actual result | Latency |
|---|---|:---:|---|---:|
| ZH-REC-001 | recommendation | Yes | matched | 18.203 ms |
| EN-REC-001 | recommendation | Yes | matched | 1.201 ms |
| ZH-REC-002 | recommendation | Yes | matched | 0.744 ms |
| EN-REC-002 | recommendation | Yes | matched | 0.560 ms |
| ZH-REC-003 | recommendation | Yes | matched | 0.365 ms |
| EN-REC-003 | recommendation | Yes | matched | 0.615 ms |
| ZH-REC-004 | recommendation | Yes | matched | 0.413 ms |
| EN-REC-004 | recommendation | Yes | matched | 0.681 ms |
| ZH-REC-005 | recommendation | Yes | matched | 0.503 ms |
| EN-REC-005 | recommendation | Yes | matched | 0.422 ms |
| ZH-REC-006 | recommendation | Yes | matched | 0.343 ms |
| EN-REC-006 | recommendation | Yes | matched | 0.433 ms |
| ZH-NO-MATCH | recommendation | Yes | no_exact_match | 0.364 ms |
| ZH-DETAIL | assistant | Yes | product_details | 0.091 ms |
| EN-DETAIL | assistant | Yes | product_details | 0.035 ms |
| ZH-COMPARE | assistant | Yes | comparison | 0.027 ms |
| EN-COMPARE | assistant | Yes | comparison | 0.018 ms |
| ZH-POLICY | assistant | Yes | policy | 0.023 ms |
| EN-POLICY | assistant | Yes | policy | 0.017 ms |

## Interpretation

These measurements cover deterministic simulation behaviour. They do not measure live LLM response quality or network latency. The final report must be regenerated after catalogue edits and live-provider testing.

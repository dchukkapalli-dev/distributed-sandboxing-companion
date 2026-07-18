# Data Availability

All artefacts supporting this survey are in this `companion/` archive and are
mirrored at the public repository and DOI recorded below (to be filled at
deposit time).

| Artefact | File | Regeneration |
|---|---|---|
| PRISMA scoping search log (§3, Fig. 1) | `search_log.csv` | Re-run the queries in the `query_or_action` column over the stated sources/date window; the stage rows sum to 520 identified → 410 after de-duplication → 80 included. |
| Eight-axis evidence matrix of surveyed works | `evidence_matrix.csv` | Hand-coded from the cited primary sources; each row's `bibkey` resolves to `references.bib`. Mirrors the paper's Tables 1–4 (§4). |
| Trace-contract schema | `sandbox-bench/schema/trace_schema.yaml` | Authored; the contract definition of §9. |
| Example trace | `sandbox-bench/schema/example_trace.jsonl` | Synthetic, schema-conformant, ≥3 records over ≥2 mechanism classes; validates with `sandbox-bench/validate_trace.py`. |
| Trace validator | `sandbox-bench/validate_trace.py` | Stdlib-only (no `jsonschema`/`pydantic`/`PyYAML`); exits 0 on a conformant JSONL trace. |
| Two-regime CPU replay pilot | `sandbox-bench/replay_harness/cpu_pilot.py` | Deterministic, pure-stdlib, fixed-seed; emits a cold/warm-cache restore trace that passes the validator. |

No human-subjects data, proprietary traces, or licensed corpora are
included. All cited works are public preprints or published papers; see the
manuscript's references and the grey-literature provenance advisory in §8.5.

**Repository:** `<GITHUB URL>` · **Archived DOI:** `<ZENODO DOI>`
(populated at submission via the companion-archive deposit step).

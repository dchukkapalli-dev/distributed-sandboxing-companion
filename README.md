# Companion archive — Distributed Sandboxing and Secure Execution of LLM-Generated Code at Scale (Scope Survey)

Machine-readable artefacts accompanying the survey. Everything here is
regenerable and human-auditable; nothing requires a GPU, a cluster, or any
third-party Python package.

## Contents

| Path | What it is |
|---|---|
| `search_log.csv` | The PRISMA-style scoping search log (paper §3, Fig. 1). Stage rows sum to 520 identified → 410 after de-duplication → 80 included. |
| `evidence_matrix.csv` | The machine-readable eight-axis classification of every surveyed work — the data form of the paper's evidence-matrix tables (§4). One row per work; `bibkey` resolves to `references.bib`. |
| `references.bib` | BibTeX for every surveyed work; the target of each `evidence_matrix.csv` `bibkey`. |
| `sandbox-bench/` | The **trace-contract harness** of §9: a trace schema, an example trace, a stdlib-only validator, and a two-regime CPU replay pilot. |
| `CITATION.cff` | Citation metadata. |
| `LICENSE` | Dual license (MIT for code, CC-BY-4.0 for data). |
| `DATA_AVAILABILITY.md` | Where each artefact lives and how to regenerate it. |

## sandbox-bench — the trace-contract harness

`sandbox-bench/` is **not** a production sandbox-fleet benchmark. It is a
*contract* that makes the survey's two central claims independently checkable:

1. that the agentic-security benchmarks do not exercise the isolation substrate
   (the paper's Table 4), and
2. that a substrate-aware benchmark must record *which* taxonomy axis it
   stresses.

It contains:

1. **Trace schema** — `sandbox-bench/schema/trace_schema.yaml`: the required and
   optional fields, one per taxonomy axis (A1–A8) plus the agentic extensions
   `turn_index`, `stateful`, `egress_policy`.
2. **Trace validator** — `sandbox-bench/validate_trace.py`: stdlib-only (no
   `jsonschema` / `pydantic` / `PyYAML`); checks a JSON Lines trace against the
   schema, exits 0 on pass.
3. **Two-regime replay pilot** — `sandbox-bench/replay_harness/cpu_pilot.py`: a
   deterministic, fixed-seed, pure-stdlib simulation of cold-cache vs warm-cache
   sandbox restore that emits a trace which *passes* the validator, in under a
   minute on a commodity laptop.

Quick start (three commands, stdlib Python 3 only — no install):

```bash
cd sandbox-bench
python validate_trace.py schema/example_trace.jsonl
python replay_harness/cpu_pilot.py --out pilot_trace.json && python validate_trace.py pilot_trace.json
```

## What sandbox-bench IS / IS NOT

| IS | IS NOT |
|---|---|
| A trace **contract** + a validator for it | A measurement of real isolation strength |
| A two-regime (cold/warm restore) existence proof | A production fleet benchmark |
| Reproducible on a laptop, stdlib-only, deterministic | A claim about any specific microVM / gVisor / WASM deployment |
| A template a future benchmark can adopt to report which axis it stresses | The benchmark itself (scaling it to real substrates is open problem OP3) |

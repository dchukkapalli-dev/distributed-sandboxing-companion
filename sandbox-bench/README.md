# sandbox-bench — a trace-contract validator + CPU replay pilot

`sandbox-bench` is the runnable companion to the survey *Distributed Sandboxing
and Secure Execution of LLM-Generated Code at Scale* (§9). It makes the paper's
proposed evaluation contract **checkable today, on a laptop, with no GPU and no
third-party packages.**

## What this IS

- A **trace schema** (`schema/trace_schema.yaml`) that fixes the fields any
  agent-sandbox measurement must report, one column per taxonomy axis
  (mechanism class, startup latency, steady-state overhead, TCB depth, memory
  footprint / density, restore kind + latency, adversary model, scheduler),
  plus the agentic fields `turn_index`, `stateful`, and `egress_policy`.

> **Note on `schema/example_trace.jsonl`.** The example records are
> **deliberately synthetic** — they are *not* rows of the survey's corpus, and
> they intentionally span configurations (including an
> `adversary_model = active-escape` record with an explicit scheduler) **purely
> to exercise the validator's accept path** across the full field space. They
> therefore do **not** contradict the paper's empty-cell finding (no *surveyed
> system* occupies the active-escape × explicit-fleet-scheduling cell); the
> empty-cell claim is a property of `companion/evidence_matrix.csv`, not of this
> illustrative trace.
- A **stdlib-only validator** (`validate_trace.py`) that checks whether a
  JSON Lines trace conforms to that schema — so an external party can verify
  their own measurements satisfy the contract before claiming comparability.
- A **two-regime CPU replay pilot** (`replay_harness/cpu_pilot.py`) that
  emits a conforming trace and the §9 normalised reporting template,
  demonstrating the contract is satisfiable and that the cold-cache vs
  warm-cache regimes are distinguishable (Proposition 1).

## What this IS NOT

- It is **not** a production sandbox-fleet benchmark. It does not boot
  Firecracker, gVisor, Kata, or any real isolation substrate, and it reports
  **no** real-system numbers. The pilot is a deterministic simulation whose
  only job is to show the contract is well-formed and satisfiable.
- The numbers it prints are illustrative of the *shape* of the contract
  (cold > warm restore), not measurements of any deployed system.

## Seven-file layout

```
sandbox-bench/
  README.md                      <- this file
  schema/trace_schema.yaml       <- required + optional fields, with types
  schema/example_trace.jsonl     <- >=3 hand-written records, >=2 mechanism classes
  validate_trace.py              <- stdlib-only JSONL-vs-schema validator
  replay_harness/cpu_pilot.py    <- deterministic two-regime CPU pilot (SEED-fixed)
  replay_harness/requirements.txt<- stdlib only (nothing to install)
  replay_harness/README.md       <- scale-down framing + expected output shape
```

## Three-command laptop quick-start

```bash
# 1. validate the shipped example trace against the schema  -> exits 0
python validate_trace.py schema/example_trace.jsonl

# 2. run the two-regime CPU pilot (no install, <1 min)      -> writes pilot_trace.json
python replay_harness/cpu_pilot.py --out pilot_trace.json

# 3. validate the pilot's own output against the schema     -> exits 0
python validate_trace.py pilot_trace.json
```

All three commands run under a stock Python 3 interpreter (3.9+); no
`jsonschema`, `pydantic`, `pyyaml`, `torch`, or network access is required.
Randomness in the pilot is seeded by a fixed constant, so its output is
bit-for-bit reproducible.

## License & citation

See `../LICENSE` (MIT for code, CC-BY-4.0 for data) and `../CITATION.cff`.

# sandbox-bench replay harness (two-regime CPU pilot)

`cpu_pilot.py` is a **deterministic, pure-stdlib simulation** of sandbox restore
across two regimes — a *cold-cache* restore (working set faulted in on the
critical path, governed by the paper's Proposition 1) and a *warm-cache* restore
(working set already resident). It emits a JSON Lines trace conforming to
`../schema/trace_schema.yaml` and prints the §9 normalised reporting template.

```bash
# no install needed — standard library only
python cpu_pilot.py --out pilot_trace.json
python ../validate_trace.py pilot_trace.json     # must print OK and exit 0
```

## Scale-down framing

This is a *pilot of the contract*, not a measurement of any real sandbox. It
exists so that:

- the trace contract is demonstrably **satisfiable** on a commodity laptop in
  under a minute, with no GPU, no cluster, and no third-party package; and
- the **two regimes** produce distinguishable restore-time records, so a future
  benchmark cannot silently report one operating point as the whole frontier
  (the anti-pattern the trade-off model of §6 warns against).

All randomness is seeded by a fixed constant (`SEED = 20260531`), so the emitted
trace is bit-for-bit reproducible — running it twice yields identical output.

## Expected output shape

`cpu_pilot.py` prints a JSON object like:

```json
{
  "n_records": 8,
  "mean_startup_ms": ...,
  "cold_mean_restore_ms": ...,
  "warm_mean_restore_ms": ...,
  "cold_warm_restore_ratio": >1.0,
  "mean_mem_footprint_mb": 5.0
}
```

The key invariant is `cold_warm_restore_ratio > 1.0`: the cold regime is slower
than the warm regime, exactly as the working-set-fault-in floor predicts. The
written `pilot_trace.json` then passes `../validate_trace.py` with exit code 0.

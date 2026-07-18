#!/usr/bin/env python3
"""Two-regime CPU replay pilot for sandbox-bench (survey §9).

A deterministic, pure-stdlib simulation of sandbox restore across two regimes:

  * cold cache  — the working set must be faulted in on the critical path, so
    restore latency is governed by Proposition 1 (|W| * c_io); and
  * warm cache  — the working set is already resident, so only a small
    reconnect cost is paid.

It emits a JSON Lines trace (one `exec` record per agent turn) that PASSES
`validate_trace.py`, then prints the §9 normalised reporting template. No model
weights, no GPU, no network, no third-party package. All randomness is seeded by
a FIXED constant, so the emitted trace is bit-for-bit reproducible.

Usage:
    python cpu_pilot.py --out pilot_trace.json
    python cpu_pilot.py                       # writes ./pilot_trace.json
"""
import argparse
import json
import random
import sys

SEED = 20260531          # fixed seed -> reproducible output (no wall-clock entropy)

# Simulated sandbox configuration (illustrative operating point, NOT a
# measurement of any real system; see §9 scope note).
MECHANISM = "microvm-snapshot"
TCB_DEPTH = "per-guest-kernel"
ADVERSARY = "active-escape"
SCHEDULER = "yes-explicit"
EGRESS = "default-deny"
MEM_FOOTPRINT_MB = 5.0
DENSITY = 1200

WORKING_SET_PAGES = 256      # |W| pages the guest must touch before progress
C_IO_MS_PER_PAGE = 0.45      # per-page fault-in cost on the cold path
WARM_RECONNECT_MS = 5.0      # fixed reconnect cost when W already resident
N_TURNS = 8                  # one multi-turn agent session


def simulate(n_turns):
    """Yield one exec record per agent turn, alternating cold/warm regimes."""
    rng = random.Random(SEED)
    records = []
    for turn in range(n_turns):
        # Turn 0 is always a cold restore (fresh session); later turns are warm
        # except for a deterministic periodic eviction that forces a cold reload.
        cold = (turn == 0) or (turn % 4 == 0)
        if cold:
            # Proposition-1 floor plus a small bounded jitter (seeded).
            base = WORKING_SET_PAGES * C_IO_MS_PER_PAGE
            jitter = rng.uniform(0.0, 8.0)
            restore_ms = round(base + jitter, 3)
            restore_kind = "cold"
        else:
            jitter = rng.uniform(0.0, 1.5)
            restore_ms = round(WARM_RECONNECT_MS + jitter, 3)
            restore_kind = "warm"
        rec = {
            "record_type": "exec",
            "turn_index": turn,
            "mechanism_class": MECHANISM,
            "startup_ms": restore_ms,
            "steadystate_overhead": 1.05,
            "tcb_depth": TCB_DEPTH,
            "mem_footprint_mb": MEM_FOOTPRINT_MB,
            "density": DENSITY,
            "restore_kind": restore_kind,
            "restore_ms": restore_ms,
            "adversary_model": ADVERSARY,
            "scheduler": SCHEDULER,
            "stateful": True,
            "egress_policy": EGRESS,
        }
        records.append(rec)
    return records


def aggregate(records):
    """Compute the §9 reporting template.

    Timing fields are read defensively as (r.get(f) or 0) so that a record
    omitting an optional axis (e.g. restore_ms=null) still aggregates.
    """
    startups = [(r.get("startup_ms") or 0) for r in records]
    cold = [(r.get("restore_ms") or 0) for r in records if r.get("restore_kind") == "cold"]
    warm = [(r.get("restore_ms") or 0) for r in records if r.get("restore_kind") == "warm"]
    mems = [(r.get("mem_footprint_mb") or 0) for r in records]

    cold_mean = (sum(cold) / len(cold)) if cold else 0.0
    warm_mean = (sum(warm) / len(warm)) if warm else 0.0
    ratio = (cold_mean / warm_mean) if warm_mean else None

    return {
        "n_records": len(records),
        "mean_startup_ms": round(sum(startups) / len(startups), 4) if startups else None,
        "cold_mean_restore_ms": round(cold_mean, 4),
        "warm_mean_restore_ms": round(warm_mean, 4),
        "cold_warm_restore_ratio": round(ratio, 4) if ratio is not None else None,
        "mean_mem_footprint_mb": round(sum(mems) / len(mems), 4) if mems else None,
    }


def main():
    ap = argparse.ArgumentParser(description="Two-regime sandbox-restore replay pilot.")
    ap.add_argument("--out", default="pilot_trace.json",
                    help="path to write the emitted JSONL trace (default: pilot_trace.json)")
    ap.add_argument("--turns", type=int, default=N_TURNS,
                    help=f"number of agent turns to simulate (default: {N_TURNS})")
    args = ap.parse_args()

    records = simulate(args.turns)

    # Emit the trace as JSON Lines (one record per line) so validate_trace.py
    # can consume it directly.
    with open(args.out, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    report = aggregate(records)
    print(json.dumps(report, indent=2))

    # Sanity guard: the two regimes must be distinguishable (cold slower).
    if report["cold_warm_restore_ratio"] is None or report["cold_warm_restore_ratio"] <= 1.0:
        print("ERROR: cold and warm regimes are not distinguishable", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()

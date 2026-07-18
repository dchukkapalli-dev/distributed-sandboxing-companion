#!/usr/bin/env python3
"""Validate a sandbox-bench trace (JSON Lines) against the §9 trace contract.

Usage:
    python validate_trace.py schema/example_trace.jsonl
    python validate_trace.py <trace.jsonl>

Exit 0 if every record conforms; exit 1 with a per-line report otherwise.

STDLIB ONLY. The trace contract (schema/trace_schema.yaml) is embedded below as
a Python dict so this validator needs no third-party YAML/jsonschema/pydantic
package. The embedded copy is kept byte-compatible with the YAML file, which
remains the human-readable source of truth.
"""
import argparse
import json
import sys

# ---------------------------------------------------------------------------
# Embedded contract — mirrors schema/trace_schema.yaml (v0.1). Each field maps
# to {type, required, [enum]}. type is one of: int, float, str, bool.
# A present-but-null value for an OPTIONAL field is accepted (treated as absent
# for type-checking) so traces may carry e.g. "restore_ms": null.
# ---------------------------------------------------------------------------
SCHEMA_VERSION = "0.1"
RECORD_TYPES = ["exec"]

FIELDS = {
    "record_type":          {"type": "str",   "required": True,  "enum": ["exec"]},
    "turn_index":           {"type": "int",   "required": True},
    "mechanism_class":      {"type": "str",   "required": True,
                             "enum": ["microvm-snapshot", "gvisor-restore", "wasm-sfi",
                                      "container", "unikernel", "tee-enclave", "tee-cvm"]},
    "startup_ms":           {"type": "float", "required": True},
    "steadystate_overhead": {"type": "float", "required": False},
    "tcb_depth":            {"type": "str",   "required": True,
                             "enum": ["shared-host-kernel", "user-space-sentry",
                                      "per-guest-kernel", "sfi-in-process", "hw-root-of-trust"]},
    "mem_footprint_mb":     {"type": "float", "required": True},
    "density":              {"type": "int",   "required": False},
    "restore_kind":         {"type": "str",   "required": True,
                             "enum": ["cold", "warm", "fork", "remote-fork", "none"]},
    "restore_ms":           {"type": "float", "required": False},
    "adversary_model":      {"type": "str",   "required": True,
                             "enum": ["benign-tenant", "buggy-code", "malicious-tenant",
                                      "malicious-guest-os", "active-escape", "side-channel",
                                      "prompt-injection"]},
    "scheduler":            {"type": "str",   "required": True,
                             "enum": ["none", "partial", "yes-explicit"]},
    "stateful":             {"type": "bool",  "required": True},
    "egress_policy":        {"type": "str",   "required": True,
                             "enum": ["default-deny", "allowlist", "open"]},
}

# float accepts int too (JSON has no float/int distinction for whole numbers);
# bool is checked explicitly because bool is a subclass of int in Python.
TYPE_MAP = {"int": int, "float": (int, float), "str": str, "bool": bool}


def validate_record(rec, lineno):
    errs = []
    if not isinstance(rec, dict):
        return [f"line {lineno}: record is not a JSON object"]
    rt = rec.get("record_type")
    if rt not in RECORD_TYPES:
        errs.append(f"line {lineno}: record_type {rt!r} not in {RECORD_TYPES}")
    for name, spec in FIELDS.items():
        present = name in rec
        value = rec.get(name, None)
        if spec.get("required") and not present:
            errs.append(f"line {lineno}: missing required field {name!r}")
            continue
        if not present:
            continue
        # An optional field present-but-null is allowed (means "not reported").
        if value is None:
            if spec.get("required"):
                errs.append(f"line {lineno}: required field {name!r} is null")
            continue
        want = TYPE_MAP[spec["type"]]
        if spec["type"] == "bool":
            ok = isinstance(value, bool)
        elif spec["type"] in ("int", "float"):
            ok = isinstance(value, want) and not isinstance(value, bool)
        else:
            ok = isinstance(value, want)
        if not ok:
            errs.append(f"line {lineno}: field {name!r} expected {spec['type']}, got {type(value).__name__}")
            continue
        if "enum" in spec and value not in spec["enum"]:
            errs.append(f"line {lineno}: field {name!r}={value!r} not in {spec['enum']}")
    return errs


def main():
    ap = argparse.ArgumentParser(description="Validate a sandbox-bench JSONL trace.")
    ap.add_argument("trace")
    args = ap.parse_args()

    all_errs, n = [], 0
    with open(args.trace) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            n += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                all_errs.append(f"line {i}: invalid JSON ({e})")
                continue
            all_errs.extend(validate_record(rec, i))

    if all_errs:
        print(f"FAIL: {len(all_errs)} error(s) across {n} record(s)")
        for e in all_errs:
            print("  " + e)
        sys.exit(1)
    print(f"OK: {n} record(s) conform to schema v{SCHEMA_VERSION}")
    sys.exit(0)


if __name__ == "__main__":
    main()

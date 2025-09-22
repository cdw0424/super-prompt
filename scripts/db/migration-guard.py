#!/usr/bin/env python3
"""
Migration Guard — lightweight heuristic checker for Prisma schema changes.
English only. Logs must start with '--------'.

Usage:
  python3 scripts/db/migration-guard.py --current prisma/schema.prisma --proposed prisma/new_schema.prisma
Exit codes: 0 OK, 1 warn, 2 error
"""
from __future__ import annotations
import argparse, os, re, sys


def log(msg: str) -> None:
    print(f"-------- {msg}", file=sys.stderr)


def read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def parse_models(schema: str) -> dict[str, dict[str, str]]:
    models: dict[str, dict[str, str]] = {}
    for m, body in re.findall(r"model\s+([A-Za-z0-9_]+)\s*{([^}]+)}", schema, re.S):
        fields: dict[str, str] = {}
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("@@"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                fields[parts[0]] = parts[1]
        models[m] = fields
    return models


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--current", required=True)
    ap.add_argument("--proposed", required=True)
    args = ap.parse_args(argv[1:])

    cur = read(args.current)
    new = read(args.proposed)
    if not cur or not new:
        log("Schema files missing or unreadable")
        return 2

    cur_m = parse_models(cur)
    new_m = parse_models(new)

    errors = 0
    warns = 0

    # Dropped models
    for model in cur_m.keys() - new_m.keys():
        log(f"ERROR: model dropped → {model} (consider deprecation strategy)")
        errors += 1

    # Added models (OK but report)
    for model in new_m.keys() - cur_m.keys():
        log(f"OK: new model → {model}")

    # Field checks
    for model in cur_m.keys() & new_m.keys():
        cur_fields = cur_m[model]
        new_fields = new_m[model]

        # Dropped fields
        for f in cur_fields.keys() - new_fields.keys():
            log(
                f"ERROR: field dropped → {model}.{f} (plan data migration + soft delete?)"
            )
            errors += 1

        # Type changes / nullability tightening
        for f in cur_fields.keys() & new_fields.keys():
            old = cur_fields[f]
            newt = new_fields[f]
            if old != newt:
                if old.endswith("?") and not newt.endswith("?"):
                    log(f"WARN: nullability tightened → {model}.{f} {old} → {newt}")
                    warns += 1
                else:
                    log(f"WARN: type changed → {model}.{f} {old} → {newt}")
                    warns += 1

    if errors:
        log(
            "Summary: breaking changes detected — review migration steps and consider phased rollout"
        )
        return 2
    if warns:
        log("Summary: warnings present — ensure backfills/validations are planned")
        return 1
    log("Summary: no risky changes detected")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

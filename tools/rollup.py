#!/usr/bin/env python3
"""Derived cloud / hybrid / on-prem rollup over taxonomy.yaml.

This is a DERIVED lens, not stored data. The approved taxonomy schema is
unchanged; each category keeps its 8-value `deployment` enum. This rollup
answers the CLAUDE.md §3 gate ("who controls the infra?") by collapsing those
8 values into two mutually-exclusive infra-control buckets plus one hybrid flag.

Mapping (Tuo-approved 2026-07-24):
  on-prem side  <- on-prem, edge, private, OEM   (customer/operator controls hw)
  cloud side    <- public, SaaS, managed         (vendor controls hw)
  hybrid        <- the boundary marker itself (never a bucket)

Rules:
  bucket(cat)  = side of the first-listed deployment (primary). If the first is
                 'hybrid', fall through to the next non-hybrid value.
  spans(cat)   = deployment set touches BOTH sides, or contains literal 'hybrid'
                 => crosses the customer<->vendor infra boundary.
  hot(cat)     = bucket == on-prem AND hw_pull >= 3  (real hardware deal)

Usage: python3 tools/rollup.py [--json]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
TAX = REPO / "data" / "taxonomy.yaml"

ONPREM_SIDE = {"on-prem", "edge", "private", "OEM"}
CLOUD_SIDE = {"public", "SaaS", "managed"}


def bucket(dep):
    for d in dep:
        if d == "hybrid":
            continue
        return "on-prem" if d in ONPREM_SIDE else "cloud"
    return "hybrid"  # only if deployment is literally ['hybrid']


def spans(dep):
    s = set(dep)
    return ("hybrid" in s) or (bool(s & ONPREM_SIDE) and bool(s & CLOUD_SIDE))


def compute(cats):
    out = []
    for c in cats:
        dep = c["deployment"]
        b = bucket(dep)
        out.append({
            "id": c["id"], "name_en": c["name_en"], "bucket": b,
            "spans": spans(dep), "hw_pull": c["hw_pull"],
            "hot": b == "on-prem" and c["hw_pull"] >= 3,
            "play_refs": c.get("play_refs", []), "deployment": dep,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    tax = yaml.safe_load(open(TAX, encoding="utf-8"))
    rows = compute(tax["categories"])

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    by_bucket = collections.Counter(r["bucket"] for r in rows)
    spanning = sum(1 for r in rows if r["spans"])
    hot = [r for r in rows if r["hot"]]

    print(f"\n  Rollup over {len(rows)} categories (derived from taxonomy.yaml)\n")
    print(f"  {'Bucket':<10}{'Count':>7}   hw_pull distribution")
    print(f"  {'-'*46}")
    for b in ("on-prem", "cloud", "hybrid"):
        rs = [r for r in rows if r["bucket"] == b]
        if not rs and b == "hybrid":
            print(f"  {b:<10}{0:>7}   (never a primary bucket — flag only)")
            continue
        dist = collections.Counter(r["hw_pull"] for r in rs)
        dstr = "  ".join(f"{dist[k]}x hw{k}" for k in (4, 3, 2, 1) if dist[k])
        print(f"  {b:<10}{len(rs):>7}   {dstr}")
    print(f"\n  spans_infra_boundary (hybrid flag true): {spanning}/{len(rows)}")
    print(f"\n  HOT (on-prem & hw_pull>=3): {len(hot)} categories")
    for r in sorted(hot, key=lambda x: (-x["hw_pull"], x["id"])):
        plays = ",".join(p[-1] for p in r["play_refs"]) or "-"
        print(f"    hw{r['hw_pull']}  [{plays}]  {r['id']}")
    print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Progressive drill-down over taxonomy.yaml (derived, schema unchanged).

Three lenses, all computed from taxonomy.yaml (single source of truth):
  1. HOT tree:  on-prem & hw_pull>=3  ->  hw_pull -> play -> segment -> category
  2. by data_modality  (which modality pulls the most / heaviest hardware)
  3. by role           (system-of-record / analytics-AI / ... footprint)

Bucket + HOT definitions match tools/rollup.py (Tuo-approved mapping).

Usage:
  python3 tools/drilldown.py            # all three lenses
  python3 tools/drilldown.py --axis modality|role|hot
"""
import argparse
import collections
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
TAX = REPO / "data" / "taxonomy.yaml"
ONPREM_SIDE = {"on-prem", "edge", "private", "OEM"}


def bucket(dep):
    for d in dep:
        if d == "hybrid":
            continue
        return "on-prem" if d in ONPREM_SIDE else "cloud"
    return "hybrid"


def load():
    return yaml.safe_load(open(TAX, encoding="utf-8"))["categories"]


def play_label(refs):
    if not refs:
        return "(no play)"
    return ",".join(r.upper().replace("PLAY-", "Play ") for r in refs)


def hot_tree(cats):
    hot = [c for c in cats if bucket(c["deployment"]) == "on-prem" and c["hw_pull"] >= 3]
    print(f"\n=== HOT drill-down: on-prem & hw_pull>=3  ({len(hot)} categories) ===")
    print("    hw_pull -> play -> segment -> category\n")
    for hw in (4, 3):
        tier = [c for c in hot if c["hw_pull"] == hw]
        if not tier:
            continue
        print(f"  hw_pull {hw}  ({len(tier)})")
        by_play = collections.defaultdict(list)
        for c in tier:
            by_play[play_label(c.get("play_refs"))].append(c)
        for play in sorted(by_play, key=lambda k: (k == "(no play)", k)):
            print(f"    {play}")
            for c in sorted(by_play[play], key=lambda x: x["id"]):
                segs = ", ".join(c["segments"])
                print(f"      - {c['id']:<28} [{segs}]")
        print()


def by_axis(cats, axis, title):
    print(f"\n=== by {title} (all {len(cats)} categories; a category can appear in several) ===\n")
    tally = collections.defaultdict(lambda: {"n": 0, "hot": 0, "hw": collections.Counter()})
    for c in cats:
        is_hot = bucket(c["deployment"]) == "on-prem" and c["hw_pull"] >= 3
        for v in c[axis]:
            t = tally[v]
            t["n"] += 1
            t["hw"][c["hw_pull"]] += 1
            if is_hot:
                t["hot"] += 1
    rows = sorted(tally.items(), key=lambda kv: (-kv[1]["hot"], -kv[1]["n"]))
    print(f"  {'value':<20}{'total':>6}{'HOT':>5}   hw_pull dist")
    print(f"  {'-'*54}")
    for v, t in rows:
        dist = " ".join(f"{t['hw'][k]}x{k}" for k in (4, 3, 2, 1) if t["hw"][k])
        print(f"  {v:<20}{t['n']:>6}{t['hot']:>5}   {dist}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis", choices=["hot", "modality", "role"], help="one lens only")
    args = ap.parse_args()
    cats = load()
    if args.axis in (None, "hot"):
        hot_tree(cats)
    if args.axis in (None, "modality"):
        by_axis(cats, "data_modality", "data_modality")
    if args.axis in (None, "role"):
        by_axis(cats, "role", "role")
    print()


if __name__ == "__main__":
    main()

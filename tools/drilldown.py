#!/usr/bin/env python3
"""Buyer-aware drill-down over taxonomy.yaml (derived; needs hardware_opportunity_by_buyer, v4+).

Lenses (HOT uses the per-buyer pull, not a blended number):
  1. HOT_customer tree  : customer pull>=3  ->  pull -> play -> segment
  2. HOT_operator list  : operator pull>=3  (ISV / service-provider co-sell)
  3. OEM design-wins    : oem buyer present (oem pull shown)
  4. by data_modality / by role  (reachable categories, marking customer-HOT)

Usage: python3 tools/drilldown.py [--axis customer|operator|oem|modality|role]
"""
import argparse
import collections
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
TAX = REPO / "data" / "taxonomy.yaml"
OPP = {1: "minimal", 2: "modest", 3: "significant", 4: "flagship"}


def load():
    doc = yaml.safe_load(open(TAX, encoding="utf-8"))
    if doc.get("version", 0) < 4 or "hardware_opportunity_by_buyer" not in doc["categories"][0]:
        sys.exit("taxonomy.yaml has no hardware_opportunity_by_buyer (need v4). Run assemble_pull first.")
    return doc["categories"]


def pull(c, b):
    return c["hardware_opportunity_by_buyer"].get(b, 0)


def play_label(refs):
    return ",".join(r.upper().replace("PLAY-", "Play ") for r in refs) if refs else "(no play)"


def customer_tree(cats):
    hot = [c for c in cats if pull(c, "customer") >= 3]
    print(f"\n=== HOT_customer (SMCI direct): customer opportunity>=3  ({len(hot)}) ===")
    print("    customer opportunity -> play -> segment\n")
    for hw in (4, 3):
        tier = [c for c in hot if pull(c, "customer") == hw]
        if not tier:
            continue
        print(f"  opportunity {hw} ({OPP[hw]})  ({len(tier)})")
        by_play = collections.defaultdict(list)
        for c in tier:
            by_play[play_label(c.get("plays"))].append(c)
        for play in sorted(by_play, key=lambda k: (k == "(no play)", k)):
            print(f"    {play}")
            for c in sorted(by_play[play], key=lambda x: x["id"]):
                print(f"      - {c['id']:<28} [{', '.join(c['segments'])}]")
        print()


def buyer_list(cats, b, title, motion, require_hw=True):
    sel = [c for c in cats if b in c["hardware_buyer"] and (not require_hw or pull(c, b) >= 3)]
    print(f"=== {title}: {len(sel)}  ({motion}) ===")
    for c in sorted(sel, key=lambda x: (-pull(x, b), x["id"])):
        other = " ".join(f"{k[:4]}{v}" for k, v in c["hardware_opportunity_by_buyer"].items() if k != b)
        print(f"  {b[:4]}{pull(c,b)}  {c['id']:<28} [{', '.join(c['segments'])}]  (also {other or '-'})")
    print()


def by_axis(cats, axis, title):
    reach = [c for c in cats if c["supermicro_reachable"]]
    print(f"=== by {title} (reachable {len(reach)}; multi-valued; cHOT=customer pull>=3) ===\n")
    tally = collections.defaultdict(lambda: {"n": 0, "hot": 0, "hw": collections.Counter()})
    for c in reach:
        chot = pull(c, "customer") >= 3
        for v in c[axis]:
            t = tally[v]
            t["n"] += 1
            t["hw"][c["hardware_opportunity"]] += 1
            if chot:
                t["hot"] += 1
    print(f"  {'value':<20}{'total':>6}{'cHOT':>6}")
    print(f"  {'-'*34}")
    for v, t in sorted(tally.items(), key=lambda kv: (-kv[1]["hot"], -kv[1]["n"])):
        print(f"  {v:<20}{t['n']:>6}{t['hot']:>6}")
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis", choices=["customer", "operator", "oem", "modality", "role"])
    args = ap.parse_args()
    cats = load()
    a = args.axis
    if a in (None, "customer"):
        customer_tree(cats)
    if a in (None, "operator"):
        buyer_list(cats, "operator", "HOT_operator (ISV co-sell)", "vendor buys dedicated iron")
    if a in (None, "oem"):
        buyer_list(cats, "oem", "OEM design-wins", "embedded BOM", require_hw=False)
    if a in (None, "modality"):
        by_axis(cats, "data_modality", "data_modality")
    if a in (None, "role"):
        by_axis(cats, "role", "role")


if __name__ == "__main__":
    main()

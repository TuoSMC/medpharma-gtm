#!/usr/bin/env python3
"""Buyer-aware drill-down over taxonomy.yaml (derived; needs hardware_buyer, v3+).

Lenses:
  1. HOT_customer tree  : buyer=customer & hw_pull>=3  ->  hw_pull -> play -> segment
  2. HOT_operator list  : buyer=operator & hw_pull>=3  (ISV / service-provider co-sell)
  3. OEM design-wins    : buyer=oem
  4. by data_modality / by role  (reachable categories, marking customer-HOT)

Usage:
  python3 tools/drilldown.py [--axis customer|operator|oem|modality|role]
"""
import argparse
import collections
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
TAX = REPO / "data" / "taxonomy.yaml"


def load():
    doc = yaml.safe_load(open(TAX, encoding="utf-8"))
    if doc.get("version", 0) < 3 or "hardware_buyer" not in doc["categories"][0]:
        sys.exit("taxonomy.yaml has no hardware_buyer (need v3). Run assemble_buyer first.")
    return doc["categories"]


def play_label(refs):
    return ",".join(r.upper().replace("PLAY-", "Play ") for r in refs) if refs else "(no play)"


def customer_tree(cats):
    hot = [c for c in cats if "customer" in c["hardware_buyer"] and c["hw_pull"] >= 3]
    print(f"\n=== HOT_customer (SMCI direct): buyer=customer & hw_pull>=3  ({len(hot)}) ===")
    print("    hw_pull -> play -> segment\n")
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
                print(f"      - {c['id']:<28} [{', '.join(c['segments'])}]")
        print()


def simple_list(cats, key, title, motion, require_hw=True):
    sel = [c for c in cats if key in c["hardware_buyer"] and (not require_hw or c["hw_pull"] >= 3)]
    print(f"=== {title}: {len(sel)}  ({motion}) ===")
    for c in sorted(sel, key=lambda x: (-x["hw_pull"], x["id"])):
        also = "+".join(b for b in c["hardware_buyer"] if b != key)
        print(f"  hw{c['hw_pull']}  {c['id']:<28} [{', '.join(c['segments'])}]" + (f"  (also: {also})" if also else ""))
    print()


def by_axis(cats, axis, title):
    reach = [c for c in cats if c["smc_reachable"]]
    print(f"=== by {title} (reachable {len(reach)} categories; multi-valued) ===\n")
    tally = collections.defaultdict(lambda: {"n": 0, "hot": 0, "hw": collections.Counter()})
    for c in reach:
        chot = "customer" in c["hardware_buyer"] and c["hw_pull"] >= 3
        for v in c[axis]:
            t = tally[v]
            t["n"] += 1
            t["hw"][c["hw_pull"]] += 1
            if chot:
                t["hot"] += 1
    print(f"  {'value':<20}{'total':>6}{'cHOT':>6}   hw_pull dist")
    print(f"  {'-'*52}")
    for v, t in sorted(tally.items(), key=lambda kv: (-kv[1]["hot"], -kv[1]["n"])):
        dist = " ".join(f"{t['hw'][k]}x{k}" for k in (4, 3, 2, 1) if t["hw"][k])
        print(f"  {v:<20}{t['n']:>6}{t['hot']:>6}   {dist}")
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
        simple_list(cats, "operator", "HOT_operator (ISV co-sell)", "vendor buys dedicated iron")
    if a in (None, "oem"):
        simple_list(cats, "oem", "OEM design-wins", "embedded BOM", require_hw=False)
    if a in (None, "modality"):
        by_axis(cats, "data_modality", "data_modality")
    if a in (None, "role"):
        by_axis(cats, "role", "role")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Buyer-centric rollup over taxonomy.yaml (derived; needs hardware_opportunity_by_buyer, v4+).

The authoritative "who buys the iron" axis is `hardware_buyer`, and each buyer
now carries its OWN hardware-pull score (`hardware_opportunity_by_buyer`) — a customer deal
and an operator deal for the same category are sized independently. HOT lists
use the per-buyer pull, not a single blended number:

  customer     -> SMCI DIRECT       HOT if hardware_opportunity_by_buyer.customer >= 3
  operator     -> ISV / co-sell     HOT if hardware_opportunity_by_buyer.operator >= 3
  oem          -> OEM design-win     listed if oem buyer present (pull shown)
  hyperscaler  -> out of scope (public cloud)

Deployment survives only as a secondary SUBSTRATE descriptor.

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
MOTION = {"customer": "direct", "operator": "ISV/co-sell",
          "oem": "OEM design-win", "hyperscaler": "out of scope"}


def substrate(dep):
    if not dep:
        return "unknown"
    if set(dep) <= {"hybrid"}:
        return "hybrid"
    for d in dep:
        if d == "hybrid":
            continue
        if d in ONPREM_SIDE:
            return "on-prem"
        if d in CLOUD_SIDE:
            return "cloud"
        return "unknown"
    return "hybrid"


def load():
    doc = yaml.safe_load(open(TAX, encoding="utf-8"))
    if doc.get("version", 0) < 4 or "hardware_opportunity_by_buyer" not in doc["categories"][0]:
        sys.exit("taxonomy.yaml has no hardware_opportunity_by_buyer (need v4). Run assemble_pull first.")
    return doc["categories"]


def rows(cats):
    out = []
    for c in cats:
        hb = c["hardware_buyer"]
        p = c["hardware_opportunity_by_buyer"]
        out.append({
            "id": c["id"], "name_en": c["name_en"], "hardware_buyer": hb,
            "primary_buyer": c["primary_buyer"], "supermicro_reachable": c["supermicro_reachable"],
            "pull": p, "plays": c.get("plays", []),
            "substrate": substrate(c["deployment"]),
            "hot_customer": p.get("customer", 0) >= 3,
            "hot_operator": p.get("operator", 0) >= 3,
            "oem": "oem" in hb,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rs = rows(load())
    if args.json:
        print(json.dumps(rs, ensure_ascii=False, indent=2))
        return

    print(f"\n  Per-buyer rollup over {len(rs)} categories (taxonomy.yaml v4)\n")
    pb = collections.Counter(r["primary_buyer"] for r in rs)
    print("  primary_buyer:")
    for b in ("customer", "operator", "oem", "hyperscaler"):
        print(f"    {b:<12}{pb[b]:>3}   -> {MOTION[b]}")

    def show(title, key, motion):
        hot = [r for r in rs if r[key]]
        print(f"\n  {title}: {len(hot)}  ({motion})")
        for r in sorted(hot, key=lambda x: (-x["pull"][key.split('_')[1]], x["id"])):
            b = key.split('_')[1]
            plays = ",".join(p[-1] for p in r["plays"]) or "-"
            other = " ".join(f"{k[:4]}{v}" for k, v in r["pull"].items() if k != b)
            print(f"    {b[:4]}{r['pull'][b]} [{plays}]  {r['id']:<28} (also {other or '-'})")

    show("HOT_customer", "hot_customer", MOTION["customer"])
    show("HOT_operator", "hot_operator", MOTION["operator"])
    oem = [r for r in rs if r["oem"]]
    print(f"\n  OEM design-wins: {len(oem)}  ({MOTION['oem']})")
    for r in sorted(oem, key=lambda x: (-x["pull"].get("oem", 0), x["id"])):
        print(f"    oem{r['pull'].get('oem','?')}  {r['id']}")

    sub = collections.Counter(r["substrate"] for r in rs)
    print(f"\n  substrate (informational): {dict(sub)}\n")


if __name__ == "__main__":
    main()

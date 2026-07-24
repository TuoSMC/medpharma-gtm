#!/usr/bin/env python3
"""Buyer-centric rollup over taxonomy.yaml (derived; needs hardware_buyer, v3+).

A hardware-vendor GTM reviewer showed the deployment-only on-prem/cloud split
conflated four things (substrate, buyer, service model, deal motion). The
authoritative "who controls / buys the iron" axis is now the explicit
`hardware_buyer` field. This rollup reports by buyer and splits the HOT list by
sales motion:

  customer     -> SMCI DIRECT          HOT if hw_pull>=3
  operator     -> ISV / co-sell        HOT if hw_pull>=3
  oem          -> OEM design-win       (embedded; listed regardless of hw_pull)
  hyperscaler  -> out of scope (public cloud; hardware bought by the hyperscaler)

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

# substrate descriptor only (NOT the buyer axis) — with codex-flagged guards
ONPREM_SIDE = {"on-prem", "edge", "private", "OEM"}
CLOUD_SIDE = {"public", "SaaS", "managed"}
MOTION = {"customer": "direct", "operator": "ISV/co-sell",
          "oem": "OEM design-win", "hyperscaler": "out of scope"}


def substrate(dep):
    """On-prem vs cloud vs hybrid, guarded. Informational only now."""
    if not dep:
        return "unknown"
    s = set(dep)
    if s <= {"hybrid"}:
        return "hybrid"
    for d in dep:
        if d == "hybrid":
            continue
        if d in ONPREM_SIDE:
            return "on-prem"
        if d in CLOUD_SIDE:
            return "cloud"
        return "unknown"  # guard: don't silently map unknown -> cloud
    return "hybrid"


def load():
    doc = yaml.safe_load(open(TAX, encoding="utf-8"))
    if doc.get("version", 0) < 3 or "hardware_buyer" not in doc["categories"][0]:
        sys.exit("taxonomy.yaml has no hardware_buyer (need v3). Run assemble_buyer first.")
    return doc["categories"]


def rows(cats):
    out = []
    for c in cats:
        hb = c["hardware_buyer"]
        out.append({
            "id": c["id"], "name_en": c["name_en"], "hardware_buyer": hb,
            "primary_buyer": c["primary_buyer"], "smc_reachable": c["smc_reachable"],
            "hw_pull": c["hw_pull"], "play_refs": c.get("play_refs", []),
            "substrate": substrate(c["deployment"]),
            "hot_customer": "customer" in hb and c["hw_pull"] >= 3,
            "hot_operator": "operator" in hb and c["hw_pull"] >= 3,
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

    print(f"\n  Buyer rollup over {len(rs)} categories (derived from taxonomy.yaml v3)\n")
    pb = collections.Counter(r["primary_buyer"] for r in rs)
    print("  primary_buyer:")
    for b in ("customer", "operator", "oem", "hyperscaler"):
        print(f"    {b:<12}{pb[b]:>3}   -> {MOTION[b]}")
    reach = sum(1 for r in rs if r["smc_reachable"])
    print(f"\n  smc_reachable: {reach}/{len(rs)}  (hyperscaler-only skipped: {len(rs)-reach})")

    def show(title, key, motion):
        hot = [r for r in rs if r[key]]
        print(f"\n  {title}: {len(hot)}  ({motion})")
        for r in sorted(hot, key=lambda x: (-x["hw_pull"], x["id"])):
            plays = ",".join(p[-1] for p in r["play_refs"]) or "-"
            pr = "*" if r["primary_buyer"] in ("customer", "operator") and key.endswith(r["primary_buyer"]) else " "
            print(f"    hw{r['hw_pull']} [{plays}] {pr} {r['id']}")

    show("HOT_customer (hw>=3)", "hot_customer", MOTION["customer"])
    show("HOT_operator (hw>=3)", "hot_operator", MOTION["operator"])
    oem = [r for r in rs if r["oem"]]
    print(f"\n  OEM design-wins: {len(oem)}  ({MOTION['oem']})")
    for r in sorted(oem, key=lambda x: x["id"]):
        print(f"    hw{r['hw_pull']}  {r['id']}")

    sub = collections.Counter(r["substrate"] for r in rs)
    print(f"\n  substrate (informational): {dict(sub)}")
    print()


if __name__ == "__main__":
    main()

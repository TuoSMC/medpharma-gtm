#!/usr/bin/env python3
"""expand-vendor-registry — graduate a provisional vendor into the curated tier (plan-v6.1 #4).

A provisional vendor earns curated status when it has the fields the strict tier requires: a resolved
`listing` block (status in the allowed set + A-D confidence + a source), non-null headquarters, a
founded year. This tool CHECKS that and, if met, MOVES the record from data/vendors_provisional.yaml to
data/vendors.yaml. It never fabricates the missing fields — you (or a focused research pass) fill them
first; promotion is the last, mechanical step.

  python3 tools/promote_provisional.py --check          # list each provisional's gaps to curated
  python3 tools/promote_provisional.py <id> [<id> ...]  # promote the named vendors (must pass the bar)
Then rebuild: ./build.sh
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
VEN = DATA / "vendors.yaml"
PROV = DATA / "vendors_provisional.yaml"
LISTING_STATUS = {"public", "subsidiary_of_public", "subsidiary_of_private", "private",
                  "acquired", "nonprofit_or_gov"}  # NOT "unknown" — must be resolved


def gaps(v):
    """what a provisional record still lacks to meet the curated bar (empty list == promotable)."""
    g = []
    if not (v.get("headquarters") and str(v["headquarters"]).strip()):
        g.append("headquarters")
    if not v.get("founded"):
        g.append("founded")
    lst = v.get("listing")
    if not isinstance(lst, dict):
        g.append("listing{status,confidence,source}")
    else:
        if lst.get("status") not in LISTING_STATUS:
            g.append("listing.status(resolved)")
        if lst.get("confidence") not in {"A", "B", "C", "D"}:
            g.append("listing.confidence")
        if lst.get("status") != "unknown" and not str(lst.get("source", "")).strip():
            g.append("listing.source")
    for f in ("leadership", "history", "market_position", "market_share"):
        if f not in v:
            g.append(f)  # curated requires the key present (may be an honest null)
    return g


def main():
    args = sys.argv[1:]
    prov_doc = yaml.safe_load(PROV.read_text(encoding="utf-8")) or {}
    prov = prov_doc.get("vendors", [])
    by_id = {v["id"]: v for v in prov}

    if not args or args[0] == "--check":
        promotable = [v["id"] for v in prov if not gaps(v)]
        print(f"[promote] {len(prov)} provisional; {len(promotable)} promotable now.", file=sys.stderr)
        for v in prov:
            g = gaps(v)
            print(f"  {'READY ' if not g else 'needs '}{v['id']:32} {'' if not g else ', '.join(g)}")
        return

    ven_doc = yaml.safe_load(VEN.read_text(encoding="utf-8"))
    cur_ids = {v["id"] for v in ven_doc["vendors"]}
    moved = []
    for vid in args:
        v = by_id.get(vid)
        if not v:
            sys.exit(f"[promote] {vid} not in provisional tier")
        if vid in cur_ids:
            sys.exit(f"[promote] {vid} already curated")
        g = gaps(v)
        if g:
            sys.exit(f"[promote] {vid} not ready — fill first: {', '.join(g)}")
        rec = {k: x for k, x in v.items() if k not in ("provenance", "buyer_signal")}  # drop provisional-only
        ven_doc["vendors"].append(rec)
        moved.append(vid)

    if moved:
        remaining = [v for v in prov if v["id"] not in moved]
        prov_doc["vendors"] = remaining
        VEN.write_text(yaml.safe_dump(ven_doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
        PROV.write_text(
            "# GENERATED provisional vendor tier (expand-vendor-registry). Web-sourced, PARTIAL.\n"
            + yaml.safe_dump(prov_doc, sort_keys=False, allow_unicode=True), encoding="utf-8")
        print(f"[promote] promoted {len(moved)} -> curated: {', '.join(moved)}. Rebuild: ./build.sh", file=sys.stderr)


if __name__ == "__main__":
    main()

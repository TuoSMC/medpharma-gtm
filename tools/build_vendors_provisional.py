#!/usr/bin/env python3
"""expand-vendor-registry · Phase 3 — build data/vendors_provisional.yaml (the second, lighter tier).

The curated data/vendors.yaml is a fully-verified tier (resolved listing, non-null HQ, no 'unknown').
Web-researched additions are sourced but PARTIAL, so they live here instead, held to a lighter bar
(id/name/source/deployment/sources) and flagged `provenance: expand-registry`. The FK matchers and the
app read curated ∪ provisional, so these vendors resolve sub-vendor + intel prose without diluting the
curated guarantee. Honest: unverified fields stay null; never fabricated (CLAUDE.md §8).

Run: python3 tools/build_vendors_provisional.py    (from private/vendor-drafts-ready.yaml)
"""
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
READY = REPO / "private" / "vendor-drafts-ready.yaml"
OUT = DATA / "vendors_provisional.yaml"

DEPLOY = {
    "cloud": "public-cloud", "public cloud": "public-cloud", "cloud platform": "public-cloud",
    "saas": "software-as-a-service", "cloud/saas": "software-as-a-service", "software-as-a-service": "software-as-a-service",
    "mobile": "software-as-a-service", "mobile applications": "software-as-a-service",
    "on-premise": "on-premises", "on premise": "on-premises", "on-premises": "on-premises",
    "hybrid": "hybrid", "private-cloud": "private-cloud", "private cloud": "private-cloud",
    "edge": "edge", "edge-native": "edge", "vendor-managed": "vendor-managed", "service": "vendor-managed",
    "hardware": "on-premises", "hardware device": "on-premises", "hardware-software": "on-premises",
    "wearable device": "on-premises",
}
DEFAULT_DEPLOY = {"oem": "on-premises", "isv": "software-as-a-service",
                  "service-provider": "vendor-managed", "hyperscaler": "public-cloud", "unknown": "software-as-a-service"}
ORDER = ["id", "name", "categories", "deployment_models", "partner_type", "buyer_signal", "confidence",
         "source", "sources", "headquarters", "founded", "market_position", "provenance"]


def norm(v):
    v = re.split(r"[(/—]", str(v))[0].lower()
    v = re.sub(r"\b(inc|llc|ltd|gmbh|corp|co|sa|ag|plc|the)\b", "", v)
    return re.sub(r"[^a-z0-9]+", " ", v).strip()


def main():
    drafts = yaml.safe_load(READY.read_text(encoding="utf-8"))["vendors"]
    tax = yaml.safe_load((DATA / "taxonomy.yaml").read_text(encoding="utf-8"))
    subs = tax.get("subcategories", [])
    cat_ids = {c["id"] for c in tax["categories"]}
    sub_by_id = {s["id"]: s for s in subs}
    curated_ids = {v["id"] for v in yaml.safe_load((DATA / "vendors.yaml").read_text(encoding="utf-8"))["vendors"]}

    def root_cat(sid):
        cur, seen = sid, set()
        while cur in sub_by_id and cur not in seen:
            seen.add(cur); cur = sub_by_id[cur]["parent"]
        return cur if cur in cat_ids else None

    from collections import Counter
    cats_for, buyer_for = {}, {}
    for s in subs:
        rc = root_cat(s["id"])
        pb = s.get("primary_buyer")
        for prose in (s.get("vendors") or []):
            k = norm(prose)
            if rc:
                cats_for.setdefault(k, set()).add(rc)
            if pb:
                buyer_for.setdefault(k, Counter())[pb] += 1

    out, skipped = [], []
    for d in drafts:
        pid = d["id"]
        if pid in curated_ids:                       # never shadow a curated vendor
            skipped.append((pid, "id already curated"))
            continue
        pt = "isv" if pid == "nuance" else d.get("partner_type", "unknown")
        dm = []
        for x in (d.get("deployment_models") or []):
            m = DEPLOY.get(str(x).strip().lower())
            if m and m not in dm:
                dm.append(m)
        if not dm:
            dm = [DEFAULT_DEPLOY.get(pt, "software-as-a-service")]
        srcs = d.get("sources") or []
        if not srcs:
            skipped.append((pid, "no sources"))
            continue
        nk = norm(d["name"])
        cats = sorted(cats_for.get(nk, set()) or cats_for.get(pid.replace("-", " "), set()))
        # buyer_signal: the dominant primary_buyer of the sub-markets that actually name this vendor —
        # a GROUNDED GTM signal (customer=direct, operator=co-sell, oem=design-win), unlike the haiku
        # partner_type guess. Derived from taxonomy data, 0 tokens. null if no referencing sub-market.
        bc = buyer_for.get(nk) or buyer_for.get(pid.replace("-", " "))
        buyer_signal = bc.most_common(1)[0][0] if bc else None
        rec = {"id": pid, "name": d.get("name"), "categories": cats, "deployment_models": dm,
               "partner_type": pt, "buyer_signal": buyer_signal, "confidence": d.get("confidence", "C"),
               "source": srcs[0], "sources": srcs, "headquarters": d.get("headquarters"),
               "founded": d.get("founded"), "market_position": d.get("market_position"),
               "provenance": "expand-registry"}
        out.append({k: rec[k] for k in ORDER})

    OUT.write_text(
        "# GENERATED provisional vendor tier (expand-vendor-registry). Web-sourced, PARTIAL — lighter\n"
        "# schema than data/vendors.yaml (no resolved listing/HQ requirement). Regenerate from\n"
        "# private/vendor-drafts-ready.yaml with tools/build_vendors_provisional.py.\n"
        + yaml.safe_dump({"provenance": "expand-registry", "vendors": out}, sort_keys=False, allow_unicode=True),
        encoding="utf-8")
    print(f"[build_vendors_provisional] wrote {len(out)} provisional vendors -> {OUT.relative_to(REPO)} "
          f"({len(skipped)} skipped)", file=sys.stderr)
    for pid, why in skipped:
        print(f"   skip {pid}: {why}", file=sys.stderr)


if __name__ == "__main__":
    main()

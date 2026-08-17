#!/usr/bin/env python3
"""expand-vendor-registry · Phase 3 helper — append validated drafts to data/vendors.yaml (schema-conformant).

Transforms private/vendor-drafts-ready.yaml records into the vendors.yaml schema and text-appends them
(clean diff, no reformat of the 309). Honest: unverified enrichment -> null (never fabricated). Derives
`categories` from the taxonomy sub-markets that actually name the vendor, so each new vendor is tied to
real categories. Maps free-text deployment strings onto the deployment enum.

Run: python3 tools/append_vendor_drafts.py    (then rebuild: build_sub_vendor_fk + migrate_intel + build_app)
"""
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
READY = REPO / "private" / "vendor-drafts-ready.yaml"
VEN = DATA / "vendors.yaml"

DEPLOY = {  # free-text -> deployment enum
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
# fields every vendors.yaml record carries (test_registry_schema + TestVendorEnrichment)
ORDER = ["id", "name", "categories", "deployment_models", "confidence", "source",
         "headquarters", "founded", "leadership", "history", "market_position",
         "market_share", "sources", "partner_type", "listing"]


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

    def root_cat(sid):
        cur, seen = sid, set()
        while cur in sub_by_id and cur not in seen:
            seen.add(cur); cur = sub_by_id[cur]["parent"]
        return cur if cur in cat_ids else None

    # vendor-norm -> set of root categories of sub-markets that name it (for accurate `categories`)
    cats_for = {}
    for s in subs:
        rc = root_cat(s["id"])
        if not rc:
            continue
        for prose in (s.get("vendors") or []):
            cats_for.setdefault(norm(prose), set()).add(rc)

    out = []
    for d in drafts:
        pid = d["id"]
        pt = "isv" if pid == "nuance" else d.get("partner_type", "unknown")  # nuance fix
        dm = []
        for x in (d.get("deployment_models") or []):
            m = DEPLOY.get(str(x).strip().lower())
            if m and m not in dm:
                dm.append(m)
        if not dm:
            dm = [DEFAULT_DEPLOY.get(pt, "software-as-a-service")]
        srcs = d.get("sources") or []
        cats = sorted(cats_for.get(norm(d["name"]), set()) or cats_for.get(pid.replace("-", " "), set()))
        rec = {
            "id": pid, "name": d.get("name"), "categories": cats, "deployment_models": dm,
            "confidence": d.get("confidence", "C"), "source": (srcs[0] if srcs else ""),
            "headquarters": d.get("headquarters"), "founded": d.get("founded"),
            "leadership": None, "history": None, "market_position": d.get("market_position"),
            "market_share": None, "sources": srcs, "partner_type": pt, "listing": "unknown",
        }
        if not rec["source"].strip():
            print(f"  SKIP {pid}: no source", file=sys.stderr)
            continue
        out.append({k: rec[k] for k in ORDER})

    # text-append as YAML list items (no reformat of the existing 309)
    block = yaml.safe_dump(out, sort_keys=False, allow_unicode=True, default_flow_style=False)
    text = VEN.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        text += "\n"
    VEN.write_text(text + block, encoding="utf-8")

    total = len(yaml.safe_load(VEN.read_text(encoding="utf-8"))["vendors"])
    print(f"[append_vendor_drafts] appended {len(out)} vendors -> {VEN.relative_to(REPO)} "
          f"(registry now {total}). nuance -> isv. Rebuild: build_sub_vendor_fk + migrate_intel + build_app.",
          file=sys.stderr)


if __name__ == "__main__":
    main()

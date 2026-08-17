#!/usr/bin/env python3
"""expand-vendor-registry · Phase 2 — validate the research drafts before they touch vendors.yaml (0 tokens).

Reads private/vendor-drafts.yaml (the `confirmed` records returned by the expand-vendor-registry
workflow) and gates each against the schema + the existing registry:
  - id is kebab-case, unique vs the 309 existing AND vs the batch,
  - name present, partner_type in enum, confidence in A-D,
  - sources[] non-empty (no source -> rejected; CLAUDE.md: never fabricate),
  - not a duplicate of an existing vendor by normalized name.
Ready records -> private/vendor-drafts-ready.yaml (append-shaped). Rejects -> reported with reasons.
Nothing is written to data/vendors.yaml here — that is the human-gated Phase 3 (review then append).

Run: python3 tools/validate_vendor_drafts.py
"""
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
PRIV = REPO / "private"
DRAFTS = PRIV / "vendor-drafts.yaml"
READY = PRIV / "vendor-drafts-ready.yaml"

PARTNER = {"isv", "oem", "service-provider", "hyperscaler", "unknown"}
CONF = {"A", "B", "C", "D"}


def norm(v):
    v = re.split(r"[(/—]", str(v))[0].lower()
    v = re.sub(r"\b(inc|llc|ltd|gmbh|corp|co|sa|ag|plc|the)\b", "", v)
    return re.sub(r"[^a-z0-9]+", " ", v).strip()


def main():
    if not DRAFTS.exists():
        sys.exit(f"no drafts at {DRAFTS.relative_to(REPO)} — run the expand-vendor-registry workflow first "
                 f"and write its `confirmed` records there.")
    drafts = yaml.safe_load(DRAFTS.read_text(encoding="utf-8"))
    drafts = drafts.get("confirmed", drafts) if isinstance(drafts, dict) else drafts

    vendors = yaml.safe_load((DATA / "vendors.yaml").read_text(encoding="utf-8"))["vendors"]
    have_ids = {v["id"] for v in vendors}
    have_norm = {norm(v["name"]) for v in vendors}

    ready, rejects, seen_ids, seen_norm = [], [], set(), set()
    for d in drafts:
        rid, name = d.get("id"), d.get("name")
        why = None
        if not rid or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", rid or ""):
            why = "id missing / not kebab-case"
        elif not name:
            why = "name missing"
        elif not (d.get("sources") or []):
            why = "no sources (never add an unsourced vendor)"
        elif d.get("partner_type") not in PARTNER:
            why = f"partner_type {d.get('partner_type')!r} not in enum"
        elif d.get("confidence") not in CONF:
            why = f"confidence {d.get('confidence')!r} not in A-D"
        elif rid in have_ids or rid in seen_ids:
            why = "id collides with existing / earlier draft"
        elif norm(name) in have_norm or norm(name) in seen_norm:
            why = "normalized name already in registry / batch (duplicate)"
        if why:
            rejects.append({"name": name or rid, "why": why})
            continue
        seen_ids.add(rid)
        seen_norm.add(norm(name))
        # strip workflow-internal keys; keep the vendors.yaml-shaped record
        ready.append({k: v for k, v in d.items() if not k.startswith("_") and k != "is_real_relevant_vendor"})

    READY.write_text(yaml.safe_dump({"vendors": ready}, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"[validate_vendor_drafts] {len(ready)} ready -> {READY.relative_to(REPO)}; "
          f"{len(rejects)} rejected", file=sys.stderr)
    for r in rejects:
        print(f"   REJECT  {r['name']}: {r['why']}", file=sys.stderr)
    print(f"[validate_vendor_drafts] Phase 3 (human gate): review {READY.name}, then append approved "
          f"records to data/vendors.yaml and rebuild (build_index + build_sub_vendor_fk + build_app).",
          file=sys.stderr)


if __name__ == "__main__":
    main()

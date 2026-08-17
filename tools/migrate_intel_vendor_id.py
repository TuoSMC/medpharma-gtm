#!/usr/bin/env python3
"""plan-v6.1 E4a — resolve a real vendor_id FK for each vendor_intel record.

Adds a nullable `vendor_id` to every record in data/vendor_intel.yaml, pointing at a
vendors.yaml id. Resolves ONLY on a UNIQUE match — slug(key/alias/name) == a vendor id,
or normalized(key/alias/name) == exactly one vendor's normalized name. Ambiguous or
unmatched -> `vendor_id: null` + logged to private/unresolved-intel.txt. NEVER invents a
slug (CLAUDE.md: never fabricate). Idempotent (re-run replaces the vendor_id lines).

The insertion is text-based (one `vendor_id:` line after each record's `key:` line) so the
627 KB file keeps its formatting and the diff is one line per record, reviewable.

Run: python3 tools/migrate_intel_vendor_id.py
"""
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
VEN = REPO / "data" / "vendors.yaml"
INT = REPO / "data" / "vendor_intel.yaml"
UNRESOLVED = REPO / "private" / "unresolved-intel.txt"


def norm(v):
    """normalized company name — MUST match build_app.py normVendor()."""
    v = re.split(r"[(/—]", str(v))[0].lower()
    v = re.sub(r"\b(inc|llc|ltd|gmbh|corp|co|sa|ag|plc|the)\b", "", v)
    return re.sub(r"[^a-z0-9]+", " ", v).strip()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def main():
    vendors = yaml.safe_load(VEN.read_text(encoding="utf-8"))["vendors"]
    intel = yaml.safe_load(INT.read_text(encoding="utf-8"))["vendors"]

    id_set = {v["id"] for v in vendors}
    norm_to_ids = {}
    for v in vendors:
        norm_to_ids.setdefault(norm(v["name"]), set()).add(v["id"])

    resolved = []  # vendor_id or None, in record order
    for rec in intel:
        cands = set()
        for t in [rec.get("key"), rec.get("name")] + list(rec.get("aliases") or []):
            if not t:
                continue
            if slug(t) in id_set:
                cands.add(slug(t))
            cands |= norm_to_ids.get(norm(t), set())
        # an EXACT slug(key)==vendor id is the canonical company match; it breaks a tie with product /
        # duplicate variants (e.g. "meditech" wins over "meditech-expanse-laboratory"). This is not a
        # fabricated slug — the exact company slug is the strongest possible signal.
        exact = slug(rec.get("key", ""))
        if exact in cands:
            resolved.append(exact)
        elif len(cands) == 1:
            resolved.append(next(iter(cands)))
        else:
            resolved.append(None)

    # text insertion: one vendor_id line after each `key:` line (i-th key line == i-th record)
    lines = INT.read_text(encoding="utf-8").splitlines()
    out, i = [], 0
    for ln in lines:
        if re.match(r"^  vendor_id:", ln):  # drop any prior FK line (idempotent)
            continue
        out.append(ln)
        if re.match(r"^  key: ", ln):
            vid = resolved[i] if i < len(resolved) else None
            out.append(f"  vendor_id: {vid if vid else 'null'}")
            i += 1
    if i != len(intel):
        sys.exit(f"[migrate_intel] ABORT: matched {i} key-lines but {len(intel)} records — "
                 f"file structure unexpected, refusing to write.")
    INT.write_text("\n".join(out) + "\n", encoding="utf-8")

    unres = sorted(rec.get("key") for rec, vid in zip(intel, resolved) if not vid)
    UNRESOLVED.parent.mkdir(exist_ok=True)
    UNRESOLVED.write_text("\n".join(unres) + "\n", encoding="utf-8")
    n_ok = sum(1 for v in resolved if v)
    pct = 100 * n_ok // len(intel)
    print(f"[migrate_intel] resolved {n_ok}/{len(intel)} intel records ({pct}%); "
          f"{len(unres)} unresolved -> {UNRESOLVED.relative_to(REPO)}", file=sys.stderr)


if __name__ == "__main__":
    main()

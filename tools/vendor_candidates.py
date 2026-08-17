#!/usr/bin/env python3
"""expand-vendor-registry · Phase 0 — extract + rank the missing-vendor candidates (0 model tokens).

The intel-FK and sub-vendor-FK matchers leave companies unresolved because they are NOT in
data/vendors.yaml (309). This reads the two unresolved logs, folds product qualifiers to the parent
company, drops anything already covered or obviously not-a-company, and ranks the rest by how often
they appear (a company in 20 sub-markets is worth researching before one seen once).

Output: private/vendor-candidates.yaml — a prioritized work-list. Phase 1 (the research workflow)
then web-verifies the TOP-N of these into vendors.yaml records. This step spends ZERO model tokens;
it just decides WHAT is worth researching, so the paid step stays small.

Run: python3 tools/vendor_candidates.py
"""
import re
from collections import defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
PRIV = REPO / "private"
OUT = PRIV / "vendor-candidates.yaml"

# obvious non-companies / unresearchable placeholders — never become vendor records
STOP = {"internal", "in house", "in-house", "custom", "various", "multiple", "n a", "na", "tbd",
        "unknown", "proprietary", "home grown", "homegrown", "open source", "none"}


def norm(v):
    v = re.split(r"[(/—]", str(v))[0].lower()             # fold "Company (Product)" -> company
    v = re.sub(r"\b(inc|llc|ltd|gmbh|corp|co|sa|ag|plc|the)\b", "", v)
    return re.sub(r"[^a-z0-9]+", " ", v).strip()


def parse_unresolved_subs(path):
    """lines: '  12  Company (Product)'  ->  (freq, raw_string)."""
    out = []
    if not path.exists():
        return out
    for ln in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*(\d+)\s+(.*)$", ln)
        if m:
            out.append((int(m.group(1)), m.group(2)))
    return out


def parse_unresolved_intel(path):
    """lines: 'company key'  ->  (1, key)  (intel keys are already normalized, one mention each)."""
    if not path.exists():
        return []
    return [(1, ln.strip()) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main():
    vendors = yaml.safe_load((DATA / "vendors.yaml").read_text(encoding="utf-8"))["vendors"]
    covered = {norm(v["name"]) for v in vendors} | {v["id"] for v in vendors}

    agg = defaultdict(lambda: {"freq": 0, "display": None, "seen_in": set(), "samples": set()})
    for src, rows in [("sub", parse_unresolved_subs(PRIV / "unresolved-sub-vendors.txt")),
                      ("intel", parse_unresolved_intel(PRIV / "unresolved-intel.txt"))]:
        for freq, raw in rows:
            n = norm(raw)
            if not n or len(n) < 3 or n in STOP or n in covered:
                continue
            a = agg[n]
            a["freq"] += freq
            a["seen_in"].add(src)
            a["samples"].add(raw)
            # display name: prefer the shortest original with capitals (the bare company form)
            cand = re.split(r"\s*[(/—]", raw)[0].strip()
            if a["display"] is None or len(cand) < len(a["display"]):
                a["display"] = cand

    cands = sorted(agg.items(), key=lambda kv: (-kv[1]["freq"], kv[0]))
    rows = [{
        "name": a["display"],
        "norm": n,
        "freq": a["freq"],
        "seen_in": sorted(a["seen_in"]),
        "samples": sorted(a["samples"])[:4],
    } for n, a in cands]

    doc = {"version": 1, "generated_by": "tools/vendor_candidates.py",
           "note": "Phase-0 work-list for expand-vendor-registry. Research the TOP-N; never fabricate.",
           "counts": {"candidates": len(rows),
                      "freq_ge_5": sum(1 for r in rows if r["freq"] >= 5),
                      "freq_ge_3": sum(1 for r in rows if r["freq"] >= 3)},
           "candidates": rows}
    PRIV.mkdir(exist_ok=True)
    OUT.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8")

    import sys
    c = doc["counts"]
    print(f"[vendor_candidates] {c['candidates']} candidates "
          f"({c['freq_ge_5']} seen >=5x, {c['freq_ge_3']} >=3x) -> {OUT.relative_to(REPO)}", file=sys.stderr)
    print("[vendor_candidates] top 20 by frequency:", file=sys.stderr)
    for r in rows[:20]:
        print(f"   {r['freq']:4d}  {r['name']}", file=sys.stderr)


if __name__ == "__main__":
    main()

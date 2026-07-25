#!/usr/bin/env python3
"""Score an account card against data/scoring.yaml.

Usage:
    python3 tools/score.py data/accounts/<account>.yaml [--json]

Outputs weighted score, tier, and gap fields (unscored items, missing lite-card
fields, low-confidence evidence).
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCORING_FILE = REPO_ROOT / "data" / "scoring.yaml"

# Lite card required fields (templates/account-card-lite.md)
LITE_FIELDS = [
    "company", "facility", "segment", "software", "deployment",
    "operator", "trigger", "infrastructure_control", "evidence", "next_step",
]

FULL_CARD_THRESHOLD = 70


def load_yaml(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        sys.exit(f"error: file not found: {path}")
    except yaml.YAMLError as e:
        sys.exit(f"error: bad YAML in {path}: {e}")


def score_account(account: dict, scoring: dict):
    items = scoring["items"]
    tiers = sorted(scoring["tiers"], key=lambda t: -t["min"])
    scale_max = scoring.get("scale", {}).get("max", 5)

    raw = account.get("scoring", {}) or {}
    rows, total, gaps = [], 0.0, []

    for item in items:
        key, weight = item["key"], item["weight"]
        val = raw.get(key)
        if val is None:
            gaps.append(f"scoring.{key} missing (counts as 0)")
            val = 0
        if not (0 <= val <= scale_max):
            sys.exit(f"error: scoring.{key}={val} out of range 0-{scale_max}")
        weighted = (val / scale_max) * weight
        total += weighted
        rows.append({"key": key, "label": item["label"], "score": val,
                     "weight": weight, "weighted": round(weighted, 1)})

    tier = next(t for t in tiers if total >= t["min"])

    # Gap fields: missing lite-card fields
    for f in LITE_FIELDS:
        if f not in account or account[f] in (None, ""):
            gaps.append(f"lite-card field '{f}' missing")

    # Evidence confidence check
    evidence = account.get("evidence", []) or []
    if isinstance(evidence, list):
        d_count = sum(1 for e in evidence
                      if isinstance(e, dict) and e.get("confidence") == "D")
        if evidence and d_count == len(evidence):
            gaps.append("all evidence is confidence D (inference only) — needs verification")

    return {
        "total": round(total, 1),
        "tier": tier["name"],
        "tier_action": tier.get("action", ""),
        "rows": rows,
        "gaps": gaps,
        "full_card_required": total >= FULL_CARD_THRESHOLD,
    }


def print_report(account: dict, result: dict):
    name = f"{account.get('company', '?')} — {account.get('facility', '?')}"
    print(f"\n  {name}")
    print(f"  {'=' * len(name)}")
    print(f"  {'Item':<38}{'Score':>6}{'Weight':>8}{'Weighted':>10}")
    print(f"  {'-' * 62}")
    for r in result["rows"]:
        print(f"  {r['label']:<38}{r['score']:>4}/5{r['weight']:>8}{r['weighted']:>10}")
    print(f"  {'-' * 62}")
    print(f"  {'TOTAL':<52}{result['total']:>10}")
    print(f"\n  Tier: {result['tier']}  →  {result['tier_action']}")
    if result["full_card_required"]:
        print("  ≥70: FULL account card required (templates/account-card-full.md)")
    if result["gaps"]:
        print("\n  Gaps:")
        for g in result["gaps"]:
            print(f"    - {g}")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("account_file", type=Path)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    scoring = load_yaml(SCORING_FILE)
    account = load_yaml(args.account_file)

    result = score_account(account, scoring)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_report(account, result)


if __name__ == "__main__":
    main()

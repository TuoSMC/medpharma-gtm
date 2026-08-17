#!/usr/bin/env python3
"""taxquery — the retrieval CLI over the taxonomy index (plan-v6.1 E2 / B-Query).

Answers "which categories pull gpu-server / are HOT / belong to Play A?" and "show me
ONE node / its children / its path" by reading the small index files, NEVER the 2.27 MB
taxonomy.yaml. A model calls this instead of loading the tree into context (D2).

  python3 tools/taxquery.py hot [--min N] [--visibility default|card|archived]
  python3 tools/taxquery.py index [--visibility V] [--play P] [--buyer B] [--profile C] [--min N]
  python3 tools/taxquery.py show <id>
  python3 tools/taxquery.py children <id>
  python3 tools/taxquery.py path <id>

Reads: data/taxonomy_index.yaml (59 categories, always) + data/taxonomy_tree_index.yaml
(999 subs, loaded only for drill queries). Rebuild them with tools/build_index.py.
"""
import argparse
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
SPINE = DATA / "taxonomy_index.yaml"
TREE = DATA / "taxonomy_tree_index.yaml"


def _load(path):
    if not path.exists():
        sys.exit(f"{path.relative_to(REPO)} missing — run: python3 tools/build_index.py")
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    return {r["id"]: r for r in (doc.get("rows") or [])}


def load_spine():
    return _load(SPINE)


def load_all():
    d = _load(SPINE)
    d.update(_load(TREE))
    return d


def _match(r, args):
    if getattr(args, "visibility", None) and r.get("visibility") != args.visibility:
        return False
    if getattr(args, "play", None) and args.play not in (r.get("play") or []):
        return False
    if getattr(args, "buyer", None) and r.get("primary_buyer") != args.buyer:
        return False
    if getattr(args, "profile", None) and args.profile not in (r.get("hardware_profile") or []):
        return False
    if getattr(args, "min", None) is not None and (r.get("hardware_opportunity") or 0) < args.min:
        return False
    return True


def _fmt(r):
    opp = r.get("hardware_opportunity")
    prof = ",".join(r.get("hardware_profile") or []) or "-"
    play = ",".join(p.replace("play-", "").upper() for p in (r.get("play") or [])) or "-"
    return f"  opp{opp if opp is not None else '-'} {str(r.get('primary_buyer') or '-'):<9} [{play:<3}] {r['id']:<40} {prof}"


def cmd_hot(args):
    rows = load_spine()  # HOT lives on the default-visible spine; categories only
    vis = args.visibility or "default"
    hot = sorted(r["id"] for r in rows.values()
                 if r.get("visibility") == vis and (r.get("hardware_opportunity") or 0) >= args.min)
    for rid in hot:
        print(rid)
    print(f"[taxquery] hot --min {args.min} --visibility {vis}: {len(hot)} categories", file=sys.stderr)


def cmd_index(args):
    vis = getattr(args, "visibility", None)
    rows = load_spine() if vis in (None, "default") else load_all()
    sel = sorted((r for r in rows.values() if _match(r, args)), key=lambda r: r["id"])
    for r in sel:
        print(_fmt(r))
    print(f"[taxquery] index: {len(sel)} rows", file=sys.stderr)


def cmd_show(args):
    rows = load_all()
    r = rows.get(args.id)
    if not r:
        sys.exit(f"unknown id: {args.id}")
    print(yaml.safe_dump(r, sort_keys=False, allow_unicode=True).rstrip())


def cmd_children(args):
    rows = load_all()
    if args.id not in rows:
        sys.exit(f"unknown id: {args.id}")
    kids = sorted((r for r in rows.values() if r.get("parent") == args.id), key=lambda r: r["id"])
    for r in kids:
        print(_fmt(r))
    print(f"[taxquery] children of {args.id}: {len(kids)}", file=sys.stderr)


def cmd_path(args):
    rows = load_all()
    if args.id not in rows:
        sys.exit(f"unknown id: {args.id}")
    chain, cur, seen = [], args.id, set()
    while cur and cur in rows and cur not in seen:
        seen.add(cur)
        chain.append(cur)
        cur = rows[cur].get("parent")
    for i, rid in enumerate(reversed(chain)):
        print(f"{'  ' * i}{rid}")


def main():
    ap = argparse.ArgumentParser(description="retrieval CLI over the taxonomy index (reads index, not taxonomy.yaml)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("hot", help="categories with hardware_opportunity >= N (default-visible)")
    p.add_argument("--min", type=int, default=3)
    p.add_argument("--visibility", choices=["default", "card", "archived"])
    p.set_defaults(func=cmd_hot)

    p = sub.add_parser("index", help="list rows, filtered")
    p.add_argument("--visibility", choices=["default", "card", "archived"])
    p.add_argument("--play")
    p.add_argument("--buyer")
    p.add_argument("--profile")
    p.add_argument("--min", type=int)
    p.set_defaults(func=cmd_index)

    for name, fn, helptext in [("show", cmd_show, "print one node's full record"),
                               ("children", cmd_children, "direct children of a node"),
                               ("path", cmd_path, "parent chain from root to node")]:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("id")
        p.set_defaults(func=fn)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

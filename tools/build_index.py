#!/usr/bin/env python3
"""Generate data/taxonomy_index.yaml — the small retrieval surface (plan-v6.1 E2 / M3).

Why: every tool and every model otherwise `safe_load`s the 2.27 MB taxonomy.yaml just
to answer "which categories pull gpu-server?". This emits a <100 KB index so `taxquery.py`
(and, in E3, the app) can read ONE record instead of the whole tree. The index is the
SINGLE source of truth for `visibility`, the HOT set, and the C1 card rollup (D7): nobody
recomputes those downstream.

Columns per row (plan §7 E2):
  id, parent, depth, name_en, play, hardware_opportunity, primary_buyer, hardware_profile, visibility
Category rows (depth 0) additionally carry the C1/C2 rollup:
  child_count, descendant_profiles, divergent_children

visibility (locked §6, NOT the failed L2 rule):
  category (depth 0) -> default   |   depth == 1 -> card   |   depth >= 2 -> archived

This is a MACHINE reading taxonomy.yaml in the interpreter (allowed). Models must not Read
taxonomy.yaml (D2); they read this index or call taxquery.py.
Rebuild after any taxonomy.yaml change:  python3 tools/build_index.py
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
TAX = DATA / "taxonomy.yaml"
# Two-tier index (mirrors the plan's spine/archive split so the loadable surface stays <100 KB, L1):
#   OUT_SPINE = the 59 category rows + C1 rollup  → the retrieval surface (hot/index default read this)
#   OUT_TREE  = the 999 subcategory rows          → taxquery loads only for show/children/path of subs
OUT_SPINE = DATA / "taxonomy_index.yaml"
OUT_TREE = DATA / "taxonomy_tree_index.yaml"

HOT_THRESHOLD = 3  # hardware_opportunity >= 3 == HOT (D4); the acceptance count is 35


def load_taxonomy():
    doc = yaml.safe_load(TAX.read_text(encoding="utf-8"))
    return doc["categories"], doc.get("subcategories", []) or []


def build_rows(cats, subs):
    cat_ids = {c["id"] for c in cats}
    sub_by_id = {s["id"]: s for s in subs}

    # children adjacency (parent id -> list of child sub ids), for depth + rollups
    children = {}
    for s in subs:
        children.setdefault(s["parent"], []).append(s["id"])

    def depth_of(sid):
        """steps from a subcategory up to its root category (L1 == 1)."""
        d = 0
        cur = sid
        seen = set()
        while cur in sub_by_id and cur not in seen:
            seen.add(cur)
            d += 1
            cur = sub_by_id[cur]["parent"]
        # cur is now a category id (chain roots at a category — enforced by tests)
        return d

    def root_category(sid):
        cur = sid
        seen = set()
        while cur in sub_by_id and cur not in seen:
            seen.add(cur)
            cur = sub_by_id[cur]["parent"]
        return cur if cur in cat_ids else None

    def descendants(node_id):
        """all transitive descendant sub ids of a node (category or sub)."""
        out = []
        stack = list(children.get(node_id, []))
        seen = set()
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            out.append(n)
            stack.extend(children.get(n, []))
        return out

    rows = []

    # --- category rows (depth 0, visibility default) + C1 rollup ---
    for c in sorted(cats, key=lambda x: x["id"]):
        cid = c["id"]
        cprofile = set(c.get("hardware_profile") or [])
        cbuyer = c.get("primary_buyer")
        l1 = sorted(children.get(cid, []))
        # descendant_profiles: distinct component pull across the whole sub-tree (C1 diversity line)
        desc = descendants(cid)
        desc_profiles = sorted({p for sid in desc for p in (sub_by_id[sid].get("hardware_profile") or [])})
        # divergent_children: <=3 L1 subs whose profile SET or buyer differs from the parent (C1 chips)
        divergent = []
        for sid in l1:
            s = sub_by_id[sid]
            if set(s.get("hardware_profile") or []) != cprofile or s.get("primary_buyer") != cbuyer:
                divergent.append(sid)
        divergent = divergent[:3]
        rows.append({
            "id": cid,
            "parent": None,
            "depth": 0,
            "name_en": c.get("name_en"),
            "play": list(c.get("plays") or []),
            "hardware_opportunity": c.get("hardware_opportunity"),
            "primary_buyer": cbuyer,
            "hardware_profile": list(c.get("hardware_profile") or []),
            "visibility": "default",
            "child_count": len(l1),
            "descendant_profiles": desc_profiles,
            "divergent_children": divergent,
        })

    # --- subcategory rows (depth >= 1) ---
    for s in sorted(subs, key=lambda x: x["id"]):
        d = depth_of(s["id"])
        rc = root_category(s["id"])
        vis = "card" if d == 1 else "archived"
        rows.append({
            "id": s["id"],
            "parent": s["parent"],
            "depth": d,
            "name_en": s.get("name_en"),
            # subs have no plays of their own — inherit the root category's plays
            "play": list(next((c.get("plays") or [] for c in cats if c["id"] == rc), [])),
            "hardware_opportunity": s.get("hardware_opportunity"),
            "primary_buyer": s.get("primary_buyer"),
            "hardware_profile": list(s.get("hardware_profile") or []),
            "visibility": vis,
        })
    return rows


def _write_index(path, tier, rows, extra):
    """emit one index file: a header block + one compact flow-style row per line (deterministic)."""
    header = {"version": 1, "generated_by": "tools/build_index.py",
              "source": "data/taxonomy.yaml", "tier": tier}
    header.update(extra)
    lines = ["# GENERATED by tools/build_index.py — do not hand-edit. Rebuild: python3 tools/build_index.py"]
    lines.append(yaml.safe_dump(header, sort_keys=False, allow_unicode=True).rstrip())
    lines.append("rows:")
    for r in rows:
        line = yaml.safe_dump(r, sort_keys=False, allow_unicode=True,
                              default_flow_style=True, width=10 ** 9).strip()
        lines.append("- " + line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path.stat().st_size / 1024


def dump(rows, cats, subs):
    spine = [r for r in rows if r["depth"] == 0]           # 59 categories + C1 rollup
    tree = [r for r in rows if r["depth"] >= 1]             # 999 subs (archive)
    hot = [r for r in spine if (r["hardware_opportunity"] or 0) >= HOT_THRESHOLD]
    spine_kb = _write_index(OUT_SPINE, "spine", spine, {
        "hot_threshold": HOT_THRESHOLD,
        "counts": {"categories": len(spine), "hot_default": len(hot)},
        "tree_index": OUT_TREE.name,
    })
    tree_kb = _write_index(OUT_TREE, "tree", tree, {
        "counts": {"subcategories": len(tree),
                   "depth": {d: sum(r["depth"] == d for r in tree) for d in sorted({r["depth"] for r in tree})}},
        "spine_index": OUT_SPINE.name,
    })
    return {"hot": len(hot), "cats": len(spine), "subs": len(tree),
            "spine_kb": spine_kb, "tree_kb": tree_kb}


def main():
    cats, subs = load_taxonomy()
    rows = build_rows(cats, subs)
    r = dump(rows, cats, subs)
    # freshness signal — a silent build and a silently-broken build look identical (brain #4)
    print(f"[build_index] spine={OUT_SPINE.name} {r['cats']} cats {r['spine_kb']:.1f} KB "
          f"(HOT_default={r['hot']}) | tree={OUT_TREE.name} {r['subs']} subs {r['tree_kb']:.1f} KB",
          file=sys.stderr)
    if r["hot"] != 35:
        print(f"[build_index] WARNING: HOT_default={r['hot']} (expected 35 — see plan D4); "
              f"index may be wrong or the taxonomy changed.", file=sys.stderr)
    if r["spine_kb"] > 100:
        print(f"[build_index] WARNING: spine index {r['spine_kb']:.1f} KB > 100 KB target (L1 lamp).",
              file=sys.stderr)


if __name__ == "__main__":
    main()

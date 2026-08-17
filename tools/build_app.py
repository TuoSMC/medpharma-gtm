#!/usr/bin/env python3
"""Generate app/index.html from /data — a shell + an on-demand archive that ship together.

Data stays the single source of truth: this reads every /data yaml and injects
it as JSON into a static template. The template has NO domain content — updating
a vendor list, category, trigger, or account means editing yaml and re-running
this build, never touching app code (CLAUDE.md §8 rule 1).

Output (plan-v6.1 C3/D8): the default-visible spine (59 categories + L1 sub-markets +
the retrieval index) is embedded in index.html; the archived L2+ sub-tree ships beside it
in taxonomy_tree.js, loaded lazily by a <script> element on "Show deeper". No remote deps —
both files ship together in app/ AND docs/ (byte-identical each).

Rendering is done entirely with DOM text nodes (no innerHTML with data), so the
embedded content cannot execute as markup.

Usage: python3 tools/build_app.py
Open:  app/index.html directly in a browser — file:// works; the archive loads via a
       <script> element (permitted from file://, unlike fetch/XHR).
"""
import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
OUT = REPO / "app" / "index.html"
DOCS = REPO / "docs" / "index.html"  # GitHub Pages copy (byte-identical; single source = this build)

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/ on path for lib.load
from lib.load import load_yaml as load  # shared loader (E5 / B-Load) — plain load + clear errors, no cache


def main():
    accounts = []
    for p in sorted(glob.glob(str(DATA / "accounts" / "*.yaml"))):
        a = load(p)
        a["_file"] = Path(p).name
        accounts.append(a)

    taxonomy = load(DATA / "taxonomy.yaml")
    # merge authored per-category explainers (data/detail.yaml) into each category
    detail_path = DATA / "detail.yaml"
    if detail_path.exists():
        details = (load(detail_path) or {}).get("details", {})
        for c in taxonomy["categories"]:
            if c["id"] in details:
                c["detail"] = details[c["id"]]

    # plan-v6.1 C3/D8: ship DEFAULT-ONLY HTML. Embed categories + L1 sub-markets (+ the index);
    # push the archived L2+ tree to a sibling taxonomy_tree.js loaded lazily on drill (a <script>
    # element load works from file://; fetch does not — see the app's loadArchive()).
    all_subs = taxonomy.get("subcategories", []) or []
    sub_by_id = {s["id"]: s for s in all_subs}
    kids = {}
    for s in all_subs:
        kids.setdefault(s["parent"], []).append(s["id"])

    def _depth(sid):
        d, cur, seen = 0, sid, set()
        while cur in sub_by_id and cur not in seen:
            seen.add(cur); d += 1; cur = sub_by_id[cur]["parent"]
        return d

    def _deep_count(sid):  # transitive descendants (all archived below this node)
        n, stack, seen = 0, list(kids.get(sid, [])), set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x); n += 1; stack.extend(kids.get(x, []))
        return n

    l1_subs, deep_subs = [], []
    for s in all_subs:
        if _depth(s["id"]) == 1:
            s2 = dict(s); s2["_deep"] = _deep_count(s["id"])  # count of archived descendants (card hint)
            l1_subs.append(s2)
        else:
            deep_subs.append(s)
    taxonomy["subcategories"] = l1_subs  # only L1 ships inside index.html; L2+ -> taxonomy_tree.js

    vendors = load(DATA / "vendors.yaml")  # load once; reused for the dict AND the built stamp (no reload)
    data = {
        "taxonomy": taxonomy,
        "plays": load(DATA / "plays.yaml"),
        "triggers": load(DATA / "triggers.yaml"),
        "scoring": load(DATA / "scoring.yaml"),
        "vendors": vendors,
        "vendor_intel": (load(DATA / "vendor_intel.yaml") if (DATA / "vendor_intel.yaml").exists() else {"vendors": []}),
        # plan-v6.1 C2/D7: the ONE source of truth for visibility / HOT / the C1 card rollup.
        # The app reads HOT + descendant_profiles + divergent_children from here; it does NOT recompute.
        # Regenerate with tools/build_index.py after any taxonomy change.
        "taxonomy_index": (load(DATA / "taxonomy_index.yaml") if (DATA / "taxonomy_index.yaml").exists() else {"rows": []}),
        "leaderboards": load(DATA / "leaderboards.yaml"),
        "accounts": accounts,
        "built": f"taxonomy v{taxonomy.get('version', '?')} · vendors v{vendors.get('version', '?')}",  # reuse loaded objs
    }

    # C3 finish: relocate the two big blobs out of the HTML into sibling scripts. vendors (~612 KB) +
    # vendor_intel (~643 KB) were half the page weight; they ship in vendors.js / vendor_intel.js
    # (loaded before the app) and get reattached to DATA in the template. Pushes index.html to ~1 MB.
    vendors_arr = data["vendors"].pop("vendors", [])       # keep version etc. inline; move the array out
    vintel_arr = data["vendor_intel"].pop("vendors", [])

    html = TEMPLATE.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    OUT.write_text(html, encoding="utf-8")
    DOCS.parent.mkdir(exist_ok=True)
    DOCS.write_text(html, encoding="utf-8")            # GitHub Pages serves /docs
    (DOCS.parent / ".nojekyll").write_text("", encoding="utf-8")  # serve the file as-is

    def sib(name, glob_expr, arr):  # write a sibling JS asset to BOTH app/ and docs/ (byte-identical)
        js = f"window.{glob_expr}=" + json.dumps(arr, ensure_ascii=False) + ";\n"
        (OUT.parent / name).write_text(js, encoding="utf-8")
        (DOCS.parent / name).write_text(js, encoding="utf-8")

    # taxonomy_tree.js loads on demand (loadArchive); vendors/vendor_intel load before the app.
    sib("taxonomy_tree.js", "__ARCHIVE__", deep_subs)
    sib("vendors.js", "__VENDORS__", vendors_arr)
    sib("vendor_intel.js", "__VINTEL__", vintel_arr)
    print(f"OK: wrote {OUT}")
    print(f"OK: wrote {DOCS}")
    print(f"OK: wrote taxonomy_tree.js (archive: {len(deep_subs)} L2+ subs; {len(l1_subs)} L1 embedded)")
    print(f"    {len(data['taxonomy']['categories'])} categories, "
          f"{len(data['plays']['plays'])} plays, {len(data['triggers']['triggers'])} triggers, "
          f"{len(accounts)} accounts")


TEMPLATE = (REPO / "app" / "template.html").read_text(encoding="utf-8")  # extracted to app/template.html (E5)


if __name__ == "__main__":
    main()

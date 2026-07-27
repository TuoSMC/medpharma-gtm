#!/usr/bin/env python3
"""Generate docs/hunting-guide.md — the sales-facing synthesis of the taxonomy.

Single source of truth = /data. This collapses the six-layer chain
(segment -> category -> buyer -> opportunity -> hardware_profile+sizing -> play)
plus vendors and triggers into the artifact an account manager actually hunts
with: per-play ranked target maps, master HOT lists, and a trigger->action index.

Run: python3 tools/hunting_guide.py   (writes docs/hunting-guide.md)
"""
import collections
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
OUT = REPO / "docs" / "hunting-guide.md"

OPP = {1: "minimal", 2: "modest", 3: "significant", 4: "flagship"}
MOTION = {"customer": "direct sale", "operator": "ISV / service-provider co-sell",
          "original-equipment-manufacturer": "OEM design-win"}


def load(name):
    return yaml.safe_load((DATA / name).read_text(encoding="utf-8"))


def main():
    tax = load("taxonomy.yaml")
    cats = {c["id"]: c for c in tax["categories"]}
    vendors = {v["id"]: v for v in load("vendors.yaml")["vendors"]}
    triggers = load("triggers.yaml")["triggers"]
    plays = {p["id"]: p for p in load("plays.yaml")["plays"]}

    def cust(c):
        return c["hardware_opportunity_by_buyer"].get("customer", 0)

    def oper(c):
        return c["hardware_opportunity_by_buyer"].get("operator", 0)

    def oem(c):
        return c["hardware_opportunity_by_buyer"].get("original-equipment-manufacturer", 0)

    def maxopp(c):
        return max(c["hardware_opportunity_by_buyer"].values())

    def rig(c):
        """what to quote: hardware components with sizing tier."""
        sz = c.get("hardware_profile_sizing", {})
        parts = [f"{comp} ({sz.get(comp, '?')})" for comp in c["hardware_profile"]]
        return ", ".join(parts) if parts else "—"

    def vends(c):
        names = [vendors[v]["name"] for v in c["vendors"] if v in vendors]
        return ", ".join(names) if names else "—"

    def trigs(cid):
        return [t for t in triggers if cid in t.get("related_categories", [])]

    L = []
    L.append("# SMCI Medical / Pharma Hunting Guide")
    L.append("")
    L.append(f"> Generated from `/data` — {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}. "
             "Do not edit by hand; regenerate with `python3 tools/hunting_guide.py`.")
    L.append(">")
    L.append("> **Gate question first (CLAUDE.md §3): who controls the infrastructure behind the software?** "
             "No answer → not in pipeline.")
    L.append("")
    L.append("**Opportunity scale** 1 minimal · 2 modest · 3 significant · 4 flagship. "
             "**Sizing** node < rack < cluster. "
             "**Buyer motions**: customer = direct · operator = ISV/co-sell · OEM = design-win · hyperscaler = out of scope.")
    L.append("")

    # ---- Part 1: per-play ranked target maps ----
    L.append("## 1 · The three plays — ranked target maps")
    L.append("")
    for pid in ("play-a", "play-b", "play-c"):
        p = plays[pid]
        members = sorted((c for c in cats.values() if pid in c["plays"]),
                         key=lambda c: (-maxopp(c), -cust(c), c["id"]))
        L.append(f"### {p['name']}  (`{pid}`)")
        L.append(f"*Hardware anchor:* {', '.join(p['hardware_anchor'])}")
        if p.get("regulatory_notes"):
            L.append(f"*Regulatory:* {p['regulatory_notes']}")
        L.append("")
        L.append("| Category | Cust | Oper | OEM | What to quote (component · scale) | Co-sell / incumbent vendors |")
        L.append("|---|:--:|:--:|:--:|---|---|")
        for c in members:
            L.append(f"| **{c['name_en']}** <br><small>{c['id']}</small> "
                     f"| {cust(c) or '·'} | {oper(c) or '·'} | {oem(c) or '·'} "
                     f"| {rig(c)} | {vends(c)} |")
        L.append("")

    # ---- Part 2: cross-play standalone deals ----
    exempt = sorted((c for c in cats.values() if c.get("play_exemption")),
                    key=lambda c: (-maxopp(c), c["id"]))
    L.append("## 2 · Cross-play standalone deals (reachable-HOT, outside the three plays)")
    L.append("")
    L.append("| Category | Cust | Oper | OEM | What to quote | Why it's outside the plays |")
    L.append("|---|:--:|:--:|:--:|---|---|")
    for c in exempt:
        L.append(f"| **{c['name_en']}** <br><small>{c['id']}</small> "
                 f"| {cust(c) or '·'} | {oper(c) or '·'} | {oem(c) or '·'} "
                 f"| {rig(c)} | {c['play_exemption']} |")
    L.append("")

    # ---- Part 3: master HOT lists ----
    L.append("## 3 · Master HOT lists")
    L.append("")
    def master(title, keyfn, motion):
        hot = sorted((c for c in cats.values() if keyfn(c) >= 3),
                     key=lambda c: (-keyfn(c), c["id"]))
        L.append(f"### {title} — {len(hot)} categories ({motion})")
        for c in hot:
            pl = ",".join(x[-1].upper() for x in c["plays"]) or "cross-play"
            L.append(f"- **{keyfn(c)}** [{pl}] `{c['id']}` — {c['name_en']}")
        L.append("")
    master("HOT_customer (direct sale)", cust, MOTION["customer"])
    master("HOT_operator (ISV co-sell)", oper, MOTION["operator"])
    oemlist = sorted((c for c in cats.values() if "original-equipment-manufacturer" in c["hardware_buyer"]),
                     key=lambda c: (-oem(c), c["id"]))
    L.append(f"### OEM design-wins — {len(oemlist)} categories ({MOTION['original-equipment-manufacturer']})")
    for c in oemlist:
        L.append(f"- **{oem(c)}** `{c['id']}` — {c['name_en']}")
    L.append("")

    # ---- Part 4: trigger -> action index ----
    L.append("## 4 · Trigger → action index")
    L.append("")
    L.append("| Signal | Urgency | Window | Opens (categories) | Play | Action |")
    L.append("|---|---|---|---|:--:|---|")
    urg_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    for t in sorted(triggers, key=lambda t: urg_rank.get(t["urgency"], 9)):
        rc = ", ".join(f"`{x}`" for x in t.get("related_categories", [])) or "—"
        rp = ",".join(x[-1].upper() for x in t.get("related_plays", [])) or "—"
        L.append(f"| **{t['signal']}** | {t['urgency']} | {t['window']} | {rc} | {rp} | {t['action']} |")
    L.append("")

    # ---- footer: component pipelines ----
    L.append("## 5 · Component pipelines (which categories feed each SMCI product line)")
    L.append("")
    comp_cats = collections.defaultdict(list)
    for c in cats.values():
        for comp in c["hardware_profile"]:
            comp_cats[comp].append(c)
    order = ["gpu-server", "high-performance-computing-cpu", "nvme-performance-storage",
             "capacity-archive-storage", "high-memory", "edge-industrial",
             "high-availability-redundant", "disaster-recovery-backup"]
    for comp in order:
        cs = comp_cats.get(comp, [])
        chot = [c for c in cs if cust(c) >= 3]
        L.append(f"- **{comp}** — {len(cs)} categories, {len(chot)} customer-HOT: "
                 + ", ".join(f"`{c['id']}`" for c in sorted(cs, key=lambda c: (-cust(c), c["id"]))[:8])
                 + (" …" if len(cs) > 8 else ""))
    L.append("")

    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"OK: wrote {OUT} ({len(L)} lines)")


if __name__ == "__main__":
    main()

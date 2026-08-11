#!/usr/bin/env python3
"""Generate app/index.html from /data — single self-contained file, zero deps.

Data stays the single source of truth: this reads every /data yaml and injects
it as JSON into a static template. The template has NO domain content — updating
a vendor list, category, trigger, or account means editing yaml and re-running
this build, never touching app code (CLAUDE.md §8 rule 1).

Rendering is done entirely with DOM text nodes (no innerHTML with data), so the
embedded content cannot execute as markup.

Usage: python3 tools/build_app.py
Open:  app/index.html directly in a browser (file:// works — data is embedded).
"""
import glob
import json
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
OUT = REPO / "app" / "index.html"
DOCS = REPO / "docs" / "index.html"  # GitHub Pages copy (byte-identical; single source = this build)


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


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

    data = {
        "taxonomy": taxonomy,
        "plays": load(DATA / "plays.yaml"),
        "triggers": load(DATA / "triggers.yaml"),
        "scoring": load(DATA / "scoring.yaml"),
        "vendors": load(DATA / "vendors.yaml"),
        "leaderboards": load(DATA / "leaderboards.yaml"),
        "accounts": accounts,
        "built": f"taxonomy v{load(DATA / 'taxonomy.yaml').get('version', '?')} · vendors v{load(DATA / 'vendors.yaml').get('version', '?')}",
    }

    html = TEMPLATE.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))
    OUT.write_text(html, encoding="utf-8")
    DOCS.parent.mkdir(exist_ok=True)
    DOCS.write_text(html, encoding="utf-8")            # GitHub Pages serves /docs
    (DOCS.parent / ".nojekyll").write_text("", encoding="utf-8")  # serve the file as-is
    print(f"OK: wrote {OUT}")
    print(f"OK: wrote {DOCS}")
    print(f"    {len(data['taxonomy']['categories'])} categories, "
          f"{len(data['plays']['plays'])} plays, {len(data['triggers']['triggers'])} triggers, "
          f"{len(accounts)} accounts")


TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SMCI MedPharma GTM Playbook</title>
<style>
:root{
  /* neutrals — whisper-cool (hue 255), instrument feel */
  --bg:oklch(0.984 0.004 255); --panel:oklch(1 0 0); --ink:oklch(0.27 0.013 255); --muted:oklch(0.47 0.014 255); --line:oklch(0.905 0.006 255);
  --accent:oklch(0.55 0.16 255); --accentbg:oklch(0.955 0.028 255);
  /* semantic shelf — equal weight, hue-only variation, so meanings read as one system */
  --hw1:oklch(0.62 0.02 255); --hw2:oklch(0.60 0.14 255); --hw3:oklch(0.66 0.15 60); --hw4:oklch(0.575 0.18 25);
  --u-crit:oklch(0.575 0.18 25); --u-high:oklch(0.66 0.15 60); --u-med:oklch(0.72 0.13 90); --u-low:oklch(0.60 0.02 255);
  --a:oklch(0.56 0.15 150); --b:oklch(0.55 0.16 290); --c:oklch(0.62 0.16 50); --d:oklch(0.57 0.10 200);
  /* design tokens (P2 unified system) — snapped scales; 0 pre-existing --s* usages so redefining shifts nothing until each ad-hoc px is migrated */
  --s0:2px; --s1:4px; --s2:6px; --s3:8px; --s4:12px; --s5:16px; --s6:24px;   /* spacing — instrument-dense */
  --r-tag:6px; --r-card:12px; --r-pill:999px; --r-dot:50%;                   /* radius — hard-fact / surface / round / circle */
  --f-1:10px; --f-2:11px; --f-3:12px; --f-4:13px; --f-5:14px; --f-6:15px;    /* type ramp — half-px noise removed */
  --f-d1:17px; --f-d2:24px; --f-d3:40px;                                     /* display sizes */
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:oklch(0.20 0.012 255); --panel:oklch(0.245 0.014 255); --ink:oklch(0.94 0.008 255); --muted:oklch(0.705 0.016 255); --line:oklch(0.325 0.014 255);
    --accent:oklch(0.72 0.13 255); --accentbg:oklch(0.315 0.05 255);
    --hw1:oklch(0.63 0.02 255); --hw2:oklch(0.68 0.13 255); --hw3:oklch(0.73 0.14 60); --hw4:oklch(0.665 0.17 25);
    --u-crit:oklch(0.665 0.17 25); --u-high:oklch(0.73 0.14 60); --u-med:oklch(0.79 0.12 90); --u-low:oklch(0.66 0.02 255);
    --a:oklch(0.68 0.15 150); --b:oklch(0.665 0.15 290); --c:oklch(0.70 0.15 50); --d:oklch(0.66 0.10 200);
  }
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang TC","Microsoft JhengHei",sans-serif;
  font-variant-numeric:tabular-nums lining-nums;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
/* functional micro-motion only (no decoration); honor reduced-motion */
button,summary,a,.trow,.pitem,.mkitem,.prow,.lplay,.ldoor,.dchip,.sfstage,.vn,.pcat,.msn,.tnode{
  transition:background-color .14s cubic-bezier(.22,1,.36,1),border-color .14s cubic-bezier(.22,1,.36,1),color .14s cubic-bezier(.22,1,.36,1)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:var(--r-tag)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;scroll-behavior:auto!important}}
header{padding:var(--s6) clamp(16px,3vw,44px);border-bottom:1px solid var(--line);background:var(--panel);position:sticky;top:0;z-index:5}
h1{margin:0;font-size:var(--f-d1);letter-spacing:.2px}
.sub{color:var(--muted);font-size:var(--f-3);margin-top:3px}
.byline{color:var(--ink);font-size:var(--f-3);font-weight:700;margin-top:4px;letter-spacing:.2px}
nav{display:flex;gap:var(--s1);flex-wrap:wrap;padding:var(--s4) clamp(16px,3vw,44px) 0;background:var(--panel);border-bottom:1px solid var(--line);position:sticky;top:61px;z-index:5}
nav button{border:0;background:transparent;color:var(--muted);font:inherit;font-weight:600;
  padding:var(--s3) var(--s5);border-radius:var(--r-tag) var(--r-tag) 0 0;cursor:pointer;border-bottom:2px solid transparent}
nav button.on{color:var(--accent);border-bottom-color:var(--accent);background:var(--accentbg)}
main{max-width:none;margin:0 auto;padding:var(--s6) clamp(16px,3vw,44px) 60px}
.tab{display:none}.tab.on{display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(340px,100%),1fr));gap:var(--s4)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r-card);padding:var(--s5) 15px}
.card h3{margin:0 0 2px;font-size:var(--f-5)}
.zh{color:var(--muted);font-size:var(--f-3);margin-bottom:8px}
.row{display:flex;flex-wrap:wrap;gap:var(--s2);margin:5px 0}
.chip{font-size:var(--f-2);padding:var(--s0) var(--s3);border-radius:var(--r-pill);background:var(--accentbg);color:var(--accent);white-space:nowrap}
.chip.dim{background:transparent;border:1px solid var(--line);color:var(--muted)}
.hwc{font-size:var(--f-1);padding:var(--s0) var(--s3);border-radius:var(--r-tag);background:var(--accentbg);color:var(--accent);font-weight:600;white-space:nowrap}
.tagk{font-size:var(--f-1);color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-right:4px;align-self:center}
.hw{display:inline-block;min-width:20px;text-align:center;font-weight:700;color:#fff;border-radius:var(--r-tag);padding:var(--s0) var(--s3);font-size:var(--f-2)}
.hw1{background:var(--hw1)}.hw2{background:var(--hw2)}.hw3{background:var(--hw3)}.hw4{background:var(--hw4)}
.bkt{font-size:var(--f-1);font-weight:700;padding:var(--s0) var(--s3);border-radius:var(--r-tag);text-transform:uppercase;letter-spacing:.4px}
.bon{background:var(--a);color:#fff}
.bcl{background:transparent;border:1px solid var(--line);color:var(--muted)}
.by{font-size:var(--f-1);font-weight:700;padding:var(--s0) var(--s3);border-radius:var(--r-tag);color:#fff;text-transform:uppercase;letter-spacing:.3px}
.bcust{background:var(--a)}.boper{background:var(--b)}.boem{background:var(--c)}.bhyp{background:var(--hw1)}
.byo{font-size:var(--f-1);padding:var(--s0) var(--s2);border-radius:var(--r-pill);border:1px solid var(--line);color:var(--muted)}
.rollup{font-size:var(--f-3);margin:-6px 0 12px;color:var(--muted)}
.rollup b{color:var(--ink)}
.ckbox{display:inline-flex;align-items:center;gap:var(--s2);font-size:var(--f-3);color:var(--muted);border:1px solid var(--line);border-radius:var(--r-tag);padding:var(--s2) var(--s3)}
.grouphdr{font-size:var(--f-4);font-weight:700;margin:18px 0 8px;display:flex;align-items:center;gap:var(--s3);border-bottom:1px solid var(--line);padding-bottom:6px}
.subhdr{font-size:var(--f-2);font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);margin:10px 0 6px}
.backbtn{position:sticky;top:64px;z-index:6;align-items:center;gap:var(--s1);font-family:inherit;font-size:var(--f-3);font-weight:600;color:var(--accent);background:var(--panel);border:1px solid var(--line);border-radius:var(--r-tag);padding:var(--s2) var(--s4);cursor:pointer;margin:2px 0 6px}
.backbtn:hover{border-color:var(--accent);background:var(--accentbg)}
.twopane{display:grid;grid-template-columns:minmax(300px,5fr) 7fr;gap:var(--s5);align-items:start;margin-top:6px}
@media(max-width:840px){.twopane{grid-template-columns:1fr}}
.tree{font-size:var(--f-4);min-width:0}
.detail{position:sticky;top:118px}
@media(max-width:840px){.detail{position:static}}
.tnode{display:flex;align-items:center;gap:var(--s3);font-weight:700;cursor:pointer;padding:var(--s3) 0 var(--s2);border-bottom:1px solid var(--line);margin-top:10px}
.tnode .tcar{color:var(--accent);font-size:var(--f-1);width:10px}
.tnode .tcount{color:var(--muted);font-weight:600;font-size:var(--f-3)}
.tnode .tflag{font-size:var(--f-1);font-weight:700;color:var(--hw4);border:1px solid var(--hw4);border-radius:var(--r-tag);padding:0 var(--s2)}
.tnode .thot{font-size:var(--f-1);font-weight:700;color:var(--a);border:1px solid var(--a);border-radius:var(--r-tag);padding:0 var(--s2)}
.vflag{font-size:var(--f-1);font-weight:700;color:var(--hw4);border:1px solid var(--hw4);border-radius:var(--r-tag);padding:0 var(--s2)}
.vhot{font-size:var(--f-1);font-weight:700;color:var(--a);border:1px solid var(--a);border-radius:var(--r-tag);padding:0 var(--s2)}
.master{border:1px solid var(--line);border-radius:var(--r-card);padding:var(--s4) var(--s5);margin:4px 0 16px;background:var(--panel)}
.master h3{font-size:var(--f-6)}
.mkpi{display:flex;flex-wrap:wrap;gap:var(--s6);margin:8px 0 6px}
.mk{display:flex;flex-direction:column;line-height:1.05}
.mk b{font-size:var(--f-d2)}.mk span{font-size:var(--f-2);color:var(--muted);text-transform:uppercase;letter-spacing:.3px}
.mk.k-flag b{color:var(--hw4)}.mk.k-hot b{color:var(--a)}.mk.k-lead b{color:var(--accent)}
.msec{margin:4px 0 0;border-top:1px solid var(--line);padding-top:4px}
.msec>summary{font-size:var(--f-2);font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);cursor:pointer;list-style:none;padding:var(--s2) 0}
.msec>summary::-webkit-details-marker{display:none}
.msec>summary::before{content:"\25be  ";color:var(--accent)}
.msec:not([open])>summary::before{content:"\25b8  "}
.mrow{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s2) var(--s3);padding:var(--s2) var(--s2);border-radius:var(--r-tag);font-size:var(--f-4)}
.mrow:hover{background:var(--accentbg)}
.mlabel{flex:1 1 200px;min-width:150px;overflow-wrap:anywhere;font-weight:600}
.mbadges{display:flex;gap:var(--s2);flex:0 0 auto}
.mtop{display:flex;flex-wrap:wrap;gap:var(--s1);justify-content:flex-end;flex:1 1 220px}
/* legend: defines + links the 3 signals (count lives here too) */
.mlegend{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--s4);margin:10px 0 8px}
@media(max-width:760px){.mlegend{grid-template-columns:1fr}}
.mleg{border:1px solid var(--line);border-radius:var(--r-tag);padding:var(--s3) var(--s4);background:var(--bg)}
.mleg.g-flag{border-color:color-mix(in oklch,var(--hw4) 45%,var(--line))}.mleg.g-hot{border-color:color-mix(in oklch,var(--a) 45%,var(--line))}.mleg.g-lead{border-color:color-mix(in oklch,var(--accent) 45%,var(--line))}
.mleg.g-flag .llab{color:var(--hw4)}.mleg.g-hot .llab{color:var(--a)}.mleg.g-lead .llab{color:var(--accent)}
.mleg .lh{display:flex;align-items:baseline;gap:var(--s3)}
.mleg .ln{font-size:var(--f-d2);font-weight:800;line-height:1}
.mleg.g-flag .ln{color:var(--hw4)}.mleg.g-hot .ln{color:var(--a)}.mleg.g-lead .ln{color:var(--accent)}
.mleg .llab{font-weight:700;font-size:var(--f-4)}
.mleg .lv{margin-left:auto;font-size:var(--f-1);font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);border:1px solid var(--line);border-radius:var(--r-pill);padding:var(--s0) var(--s3);white-space:nowrap}
.mleg .ld{font-size:var(--f-2);color:var(--muted);margin-top:5px;line-height:1.4}
.mleg .lq{font-size:var(--f-2);font-weight:600;margin-top:4px}
.mleg.g-flag .lq{color:var(--hw4)}.mleg.g-hot .lq{color:var(--a)}.mleg.g-lead .lq{color:var(--accent)}
.mpath{font-size:var(--f-3);color:var(--muted);background:var(--accentbg);border-radius:var(--r-tag);padding:var(--s3) var(--s4);margin:0 0 6px;line-height:1.5}
.mpath b{color:var(--ink)}
/* pipeline: aligned opportunity matrix per play */
.play-h{display:flex;align-items:baseline;gap:var(--s4);margin:14px 0 5px;flex-wrap:wrap}
.play-h .pl{font-weight:700;font-size:var(--f-4)}
.play-h .ps{font-size:var(--f-2);color:var(--muted)}
.ptbl{display:grid;grid-template-columns:minmax(min(150px,40%),1.25fr) minmax(min(140px,40%),2fr) auto;border:1px solid var(--line);border-radius:var(--r-tag);overflow:hidden}
.ptbl .ph{font-size:var(--f-1);font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);background:var(--panel);padding:var(--s2) var(--s4);border-bottom:1px solid var(--line)}
.ptbl .pc{padding:var(--s3) var(--s4);border-bottom:1px solid var(--line);font-size:var(--f-3);display:flex;align-items:center;gap:var(--s2);flex-wrap:wrap;min-width:0}
.ptbl .pc.last{border-bottom:none}
.pcat{font-weight:600;cursor:pointer;overflow-wrap:anywhere}
.pcat:hover{color:var(--accent)}
.pc .cb{font-size:var(--f-1);font-weight:700;border-radius:var(--r-tag);padding:0 var(--s2);white-space:nowrap;text-transform:uppercase;letter-spacing:.3px}
.pc .cb.f{color:var(--hw4);border:1px solid var(--hw4)}.pc .cb.h{color:var(--a);border:1px solid var(--a)}
.pven{color:var(--muted);overflow-wrap:anywhere}.pven b{color:var(--ink);font-weight:600}
.prank{justify-content:flex-end;text-align:right}
.prank .rb{font-size:var(--f-1);font-weight:700;color:var(--accent);border:1px solid var(--accent);border-radius:var(--r-tag);padding:0 var(--s2);white-space:nowrap}
.prank .rn{font-size:var(--f-1);color:var(--muted);white-space:nowrap}
.tbody{padding-left:2px}
.tsub{font-size:var(--f-1);font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);margin:8px 0 3px}
.trow{display:flex;align-items:center;gap:var(--s3);padding:var(--s2) var(--s3);border-radius:var(--r-tag);cursor:pointer}
.trow:hover{background:var(--accentbg)}
.trow:hover{background:var(--accentbg)}
.trow.sel{background:var(--accentbg);box-shadow:inset 3px 0 0 var(--accent)}
.trow .tname{flex:1;min-width:0;overflow-wrap:anywhere}
.trow .tby{width:9px;height:9px;border-radius:50%;flex:0 0 auto}
.tby.bcust{background:var(--a)}.tby.boper{background:var(--b)}.tby.boem{background:var(--c)}.tby.bhyp{background:var(--muted)}
.tiers6{margin:12px 0}
.tier6{display:grid;grid-template-columns:92px 1fr;gap:var(--s4);padding:var(--s3) 0 var(--s3) var(--s5);position:relative;border-left:1px solid var(--line)}
.tier6:before{content:"";position:absolute;left:-5px;top:15px;width:8px;height:8px;border-radius:50%;background:var(--accent)}
.tier6 .tlab{font-size:var(--f-2);font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.3px;padding-top:2px}
.tier6 .tcont{font-size:var(--f-4);display:flex;flex-wrap:wrap;gap:var(--s2);align-items:center}
.flowstrip{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s1)}
.fbox{border:1px solid var(--accent);color:var(--accent);border-radius:var(--r-tag);padding:var(--s0) var(--s3);font-size:var(--f-3);background:var(--accentbg)}
.farrow{color:var(--muted);font-weight:700}
.dsec{margin:14px 0}
.dsec .dsh{font-size:var(--f-2);font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);margin-bottom:4px}
/* battle card: the actionable sell layer at the top of a category */
.battle{border-radius:var(--r-card);background:var(--accentbg);padding:var(--s4) 13px;margin:10px 0 6px}
.brow{display:grid;grid-template-columns:104px 1fr;gap:var(--s4);align-items:baseline;padding:var(--s2) 0}
.brow+.brow{border-top:1px solid var(--line)}
.blab{font-size:var(--f-1);font-weight:700;text-transform:uppercase;letter-spacing:.3px;color:var(--muted)}
.bval{font-size:var(--f-3);line-height:1.45}
.rarch{display:flex;flex-wrap:wrap;gap:var(--s2)}
.raxx{font-size:var(--f-2);font-weight:600;color:var(--accent);border:1px solid var(--accent);border-radius:var(--r-tag);padding:var(--s0) var(--s3)}
.twrow{display:flex;flex-wrap:wrap;gap:var(--s1) var(--s3);align-items:baseline;padding:var(--s0) 0}
.twrow .tsig{font-weight:600}
.twrow .tact{color:var(--muted);font-size:var(--f-2)}
/* hunt launcher: the 4 doors into the battle card */
.launch{border:1px solid var(--line);border-radius:var(--r-card);padding:var(--s4) var(--s5);margin:4px 0 16px;background:var(--panel)}
.launch h3{font-size:var(--f-6)}
.hsearch{width:100%;padding:var(--s3) var(--s4);border:1px solid var(--line);border-radius:var(--r-tag);background:var(--bg);color:var(--ink);font-size:var(--f-4);margin:2px 0 8px;font-family:inherit}
.hsearch:focus{outline:none;border-color:var(--accent)}
.hnote{font-size:var(--f-3);color:var(--muted);margin:0 0 8px;background:var(--accentbg);border-radius:var(--r-tag);padding:var(--s3) var(--s4);line-height:1.45}
.hnote:empty{display:none}
.hnote b{color:var(--ink)}
.drow{display:flex;flex-wrap:wrap;gap:var(--s2);align-items:center;margin:7px 0}
.dlab{font-size:var(--f-1);font-weight:700;text-transform:uppercase;letter-spacing:.3px;color:var(--muted);width:92px;flex:0 0 auto}
.dchip{display:inline-flex;align-items:center;gap:var(--s2);font-size:var(--f-3);border:1px solid var(--line);border-radius:var(--r-pill);padding:var(--s1) var(--s4);background:var(--bg);color:var(--ink);cursor:pointer;font-family:inherit}
.dchip:hover{border-color:var(--accent);background:var(--accentbg)}
.dchip .dn{font-size:var(--f-1);color:var(--muted);font-weight:700}
.hkey{margin-top:8px;border-top:1px solid var(--line);padding-top:6px}
.hkey>summary{font-size:var(--f-2);font-weight:700;color:var(--muted);cursor:pointer;list-style:none}
.hkey>summary::-webkit-details-marker{display:none}
.hkey>summary::before{content:"\25b8 ";color:var(--accent)}
.hkey[open]>summary::before{content:"\25be "}
.krow{font-size:var(--f-3);margin:5px 0;display:flex;align-items:baseline;gap:var(--s3);flex-wrap:wrap}
.kdot{width:9px;height:9px;border-radius:var(--r-dot);flex:0 0 auto;position:relative;top:1px}
.kdot.g-flag{background:var(--hw4)}.kdot.g-hot{background:var(--a)}.kdot.g-lead{background:var(--accent)}
/* Method = "how to use this map" learn page */
.lsec{font-size:var(--f-4);font-weight:700;color:var(--ink);margin:18px 0 8px;border-bottom:1px solid var(--line);padding-bottom:6px}
.ldoors{display:grid;grid-template-columns:repeat(2,1fr);gap:var(--s3);margin:2px 0 8px}
@media(max-width:720px){.ldoors{grid-template-columns:1fr}}
.ldoor{border:1px solid var(--line);border-radius:var(--r-tag);padding:var(--s3) var(--s4);display:flex;flex-direction:column;gap:var(--s1)}
.ldoor b{font-size:var(--f-4)}
.ldoor .muted{font-size:var(--f-3);line-height:1.4}
.lbtn{font-family:inherit;font-size:var(--f-3);font-weight:700;color:#fff;background:var(--accent);border:none;border-radius:var(--r-tag);padding:var(--s3) var(--s5);cursor:pointer;margin:2px 0 4px}
.lbtn:hover{filter:brightness(1.08)}
.lsteps{margin:4px 0 8px;padding-left:22px;max-width:820px}
.lsteps li{margin:6px 0;font-size:var(--f-4);line-height:1.5}
.lplays{display:flex;flex-direction:column;gap:var(--s2);margin:2px 0}
.lplay{display:flex;align-items:center;gap:var(--s3);border:1px solid var(--line);border-radius:var(--r-tag);padding:var(--s3) var(--s4);cursor:pointer;font-size:var(--f-4);flex-wrap:wrap}
.lplay:hover{border-color:var(--accent);background:var(--accentbg)}
.lpct{font-size:var(--f-2);font-weight:700;color:var(--muted);white-space:nowrap}
.lsecsub{font-size:var(--f-2);font-weight:600;color:var(--muted);text-transform:none;letter-spacing:0}
/* system flow diagram — static, click-through */
.sysflow{display:flex;align-items:stretch;flex-wrap:wrap;gap:0;margin:4px 0 6px}
.sfstage{flex:1 1 150px;min-width:138px;border:1px solid var(--line);border-radius:var(--r-card);padding:var(--s4) var(--s4);background:var(--panel)}
.sfstage[style*="cursor"]:hover{border-color:var(--accent)}
.sftag{font-size:var(--f-1);font-weight:800;letter-spacing:.3px;color:var(--accent)}
.sftitle{font-weight:700;font-size:var(--f-4);margin:2px 0 6px}
.sfbody{display:flex;flex-direction:column;gap:var(--s1)}
.sfrow{font-size:var(--f-2);color:var(--muted)}
.sfdots{display:flex;flex-wrap:wrap;gap:var(--s1) var(--s3);margin:1px 0}
.sfdot{display:inline-flex;align-items:center;gap:var(--s1);font-size:var(--f-1);color:var(--muted)}
.sfarrow{display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:var(--f-d2);font-weight:800;padding:0 var(--s1);flex:0 0 auto}
@media(max-width:760px){.sysflow{flex-direction:column}.sfstage{flex-basis:auto}.sfarrow{transform:rotate(90deg);padding:var(--s0) 0}}
.dhdr{font-size:var(--f-2);font-weight:700;color:var(--muted);margin:9px 0 5px}
.ldrawer{margin:8px 0 2px}
.ldrawer>summary{font-size:var(--f-2);font-weight:700;color:var(--muted);cursor:pointer;list-style:none;padding:var(--s1) 0}
.ldrawer>summary::-webkit-details-marker{display:none}
.ldrawer>summary::before{content:"\25b8  ";color:var(--accent)}
.ldrawer[open]>summary::before{content:"\25be  "}
.plist{display:flex;flex-direction:column;gap:var(--s0);margin:1px 0 2px}
.pgrp{font-size:var(--f-1);font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--accent);margin:7px 0 1px}
.pitem{display:flex;align-items:baseline;gap:var(--s3);padding:var(--s2) var(--s3);border-radius:var(--r-tag);cursor:pointer}
.pitem:hover{background:var(--accentbg)}
.pitem .pnm{font-weight:600;font-size:var(--f-3);flex:0 0 auto}
.pitem .pgl{color:var(--muted);font-size:var(--f-2);flex:1;min-width:0}
.pitem .pct{font-weight:700;color:var(--muted);font-size:var(--f-2);flex:0 0 auto;white-space:nowrap}
.mklist{display:flex;flex-direction:column;gap:var(--s1);margin-top:5px}
.mkitem{display:flex;align-items:center;gap:var(--s3);padding:var(--s2) var(--s3);border:1px solid var(--line);border-radius:var(--r-tag);cursor:pointer;font-size:var(--f-3)}
.mkitem:hover{background:var(--accentbg);border-color:var(--accent)}
.mkitem .mknm{flex:1;font-weight:600;overflow-wrap:anywhere}
/* vendors-in-market drawer with cited market-share bars */
.vdrawer{margin-top:12px;border-top:1px solid var(--line);padding-top:6px}
.vdrawer>summary{font-size:var(--f-2);font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);cursor:pointer;list-style:none;padding:var(--s1) 0}
.vdrawer>summary::-webkit-details-marker{display:none}
.vdrawer>summary::before{content:"\25b8  ";color:var(--accent)}
.vdrawer[open]>summary::before{content:"\25be  "}
.vsbody{margin-top:6px}
/* fixed track column so every bar shares one scale (comparable market share) */
.msrow{display:grid;grid-template-columns:minmax(120px,1fr) clamp(90px,18vw,150px) 46px;gap:var(--s4);align-items:center;padding:var(--s1) var(--s0);font-size:var(--f-3)}
.msn{display:flex;flex-wrap:wrap;align-items:baseline;gap:var(--s2);min-width:0}
.msn .vn{font-weight:600;cursor:pointer;overflow-wrap:anywhere}
.msn .vn:hover{color:var(--accent)}
.msrk{font-size:var(--f-1);font-weight:700;color:var(--accent);border:1px solid var(--accent);border-radius:var(--r-tag);padding:0 var(--s2);white-space:nowrap}
.mstrack{height:9px;width:100%;background:var(--line);border-radius:var(--r-tag);overflow:hidden}
.mstrack.empty{background:transparent}
.msfill{height:100%;background:var(--accent);border-radius:var(--r-tag)}
.msp{text-align:right;font-weight:700;font-size:var(--f-2)}
.msund{text-align:right;font-size:var(--f-1);color:var(--muted)}
.prow{display:flex;gap:var(--s3);align-items:baseline;padding:var(--s2) var(--s0);font-size:var(--f-3);flex-wrap:wrap}
.pvn{font-weight:600;cursor:pointer;flex:0 0 auto;min-width:120px;max-width:200px;overflow-wrap:anywhere}
.pvn:hover{color:var(--accent)}
.pchips{display:flex;flex-wrap:wrap;gap:var(--s1);flex:1}
.pchip{font-size:var(--f-1);border-radius:var(--r-tag);padding:var(--s0) var(--s3);border:1px solid var(--line);color:var(--muted);cursor:default;white-space:nowrap}
.pchip.pk-hw{color:var(--hw3);border-color:var(--hw3);font-weight:700}
.dstep{display:flex;gap:var(--s3);margin:3px 0;font-size:var(--f-4)}
.dstep b{color:var(--accent);flex:0 0 auto}
.gcount{font-size:var(--f-2);font-weight:600;color:var(--muted);background:var(--accentbg);border-radius:var(--r-pill);padding:var(--s0) var(--s3)}
.play{font-size:var(--f-2);font-weight:700;padding:var(--s0) var(--s3);border-radius:var(--r-tag);color:#fff}
.playa{background:var(--a)}.playb{background:var(--b)}.playc{background:var(--c)}.playd{background:var(--d)}
.notes{color:var(--muted);font-size:var(--f-3);margin-top:8px;border-top:1px dashed var(--line);padding-top:8px}
.filters{display:flex;gap:var(--s3);flex-wrap:wrap;align-items:center;margin-bottom:14px}
.filters select,.filters input{font:inherit;padding:var(--s3) var(--s3);border:1px solid var(--line);border-radius:var(--r-tag);background:var(--panel);color:var(--ink)}
.count{color:var(--muted);font-size:var(--f-3);margin-left:auto}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:var(--r-card);overflow:hidden}
th,td{text-align:left;padding:var(--s3) var(--s4);border-bottom:1px solid var(--line);vertical-align:top;font-size:var(--f-4)}
th{background:var(--accentbg);color:var(--accent);font-size:var(--f-2);text-transform:uppercase;letter-spacing:.5px;position:sticky;top:112px}
tr:last-child td{border-bottom:0}
.u{font-weight:700;font-size:var(--f-2);text-transform:uppercase}
.u.critical{color:var(--u-crit)}.u.high{color:var(--u-high)}.u.medium{color:var(--u-med)}.u.low{color:var(--u-low)}
.wrap{overflow-x:auto}
/* narrow-width safety: long-text chips wrap instead of forcing overflow; grid content columns can shrink
   (grid/flex items default to min-width:auto = content size, which overflows on long unbreakable strings) */
.chip,.gtag,.hwc,.pchip,.raxx{white-space:normal;overflow-wrap:anywhere;max-width:100%}
.kv>*,.brow>*,.tier6>*,.msrow>*,.rarch{min-width:0;overflow-wrap:anywhere}
.card,.battle,.notes,.detail{overflow-wrap:anywhere;min-width:0}
.scorer{display:grid;grid-template-columns:1fr auto;gap:var(--s3) 14px;align-items:center;max-width:560px}
.scorer label{font-size:var(--f-4)}
.scorer input[type=range]{width:100%}
.bignum{font-size:var(--f-d3);font-weight:800;line-height:1}
.tierbadge{display:inline-block;padding:var(--s1) var(--s4);border-radius:var(--r-tag);font-weight:700;color:#fff}
.mini{height:6px;border-radius:var(--r-pill);background:var(--line);overflow:hidden;margin-top:4px}
.mini>i{display:block;height:100%}
.kv{display:grid;grid-template-columns:130px 1fr;gap:var(--s0) var(--s4);font-size:var(--f-3)}
.kv dt{color:var(--muted)}
.muted{color:var(--muted)}
.pill{font-size:var(--f-2);border:1px solid var(--line);border-radius:var(--r-pill);padding:var(--s0) var(--s3);color:var(--muted)}
.pill.lead{border-color:var(--accent);color:var(--accent);font-weight:600}
.hero{padding:var(--s2) 0 var(--s5)}
.hero h2{margin:0 0 4px;font-size:var(--f-d2);letter-spacing:.2px}
.hero p{margin:0;color:var(--muted);font-size:var(--f-4);max-width:760px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(300px,100%),1fr));gap:var(--s4);margin:14px 0}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:var(--r-card);padding:var(--s5);cursor:pointer;transition:border-color .12s,transform .12s}
.tile:hover{border-color:var(--accent);transform:translateY(-2px)}
.tile h3{margin:0 0 2px;font-size:var(--f-6)}
.tile .anchor{color:var(--muted);font-size:var(--f-2);margin-bottom:10px}
.tile .cat{display:flex;align-items:baseline;justify-content:space-between;gap:var(--s3);font-size:var(--f-3);padding:var(--s1) 0;border-top:1px dashed var(--line)}
.tile .cat span{min-width:0;overflow-wrap:anywhere}
.tile .cat b{color:var(--ink);flex:0 0 auto;white-space:nowrap}
.tile .go{margin-top:10px;color:var(--accent);font-weight:600;font-size:var(--f-3)}
.statbar{display:flex;flex-wrap:wrap;gap:var(--s4);margin:6px 0 4px}
.stat{flex:1;min-width:150px;background:var(--panel);border:1px solid var(--line);border-radius:var(--r-card);padding:var(--s4) var(--s5);cursor:pointer}
.stat:hover{border-color:var(--accent)}
.stat .n{font-size:var(--f-d2);font-weight:800;line-height:1}
.stat .l{color:var(--muted);font-size:var(--f-2);margin-top:2px}
.trigrow{display:flex;gap:var(--s3);align-items:baseline;font-size:var(--f-3);padding:var(--s2) 0;border-top:1px dashed var(--line)}
.refine>summary{cursor:pointer;font-weight:600;font-size:var(--f-3);color:var(--muted);padding:var(--s2) 0;list-style:none}
.refine>summary::-webkit-details-marker{display:none}
.refine>summary::before{content:"\25B8 ";color:var(--accent)}
.refine[open]>summary::before{content:"\25BE "}
.section-title{font-size:var(--f-3);font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);margin:20px 0 8px}
.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s4);margin:4px 0 8px}
.seg{display:inline-flex;flex-wrap:wrap;border:1px solid var(--line);border-radius:var(--r-tag);overflow:hidden}
.seg button{border:0;border-right:1px solid var(--line);background:var(--panel);color:var(--muted);font:inherit;font-size:var(--f-3);font-weight:600;padding:var(--s3) 13px;cursor:pointer}
.seg button:last-child{border-right:0}
.seg button.on{background:var(--accent);color:#fff}
.seg button:hover:not(.on){background:var(--accentbg);color:var(--accent)}
.jump{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s3);font-size:var(--f-3);color:var(--muted);margin-bottom:10px}
.jbtn{border:1px solid var(--line);background:var(--panel);color:var(--ink);font:inherit;font-size:var(--f-3);padding:var(--s2) var(--s4);border-radius:var(--r-pill);cursor:pointer;display:inline-flex;gap:var(--s2);align-items:center}
.jbtn b{font-size:var(--f-4)}
.jbtn:hover{border-color:var(--accent);background:var(--accentbg)}
.jbtn.sc-cust b{color:var(--a)}.jbtn.sc-oper b{color:var(--b)}.jbtn.sc-oem b{color:var(--c)}
.flab{display:flex;flex-direction:column;gap:var(--s0);font-size:var(--f-1);color:var(--muted);text-transform:uppercase;letter-spacing:.4px}
.flab>select,.flab>input{margin:0}
#fTxt{min-width:170px}
/* vendor filter bar + bundle-ranking matrix */
.filterbar{display:flex;flex-wrap:wrap;align-items:flex-end;gap:var(--s4);margin:2px 0 6px}
.vflab{display:flex;flex-direction:column;gap:var(--s1);font-size:var(--f-1);color:var(--muted);text-transform:uppercase;letter-spacing:.4px}
.vfsel{margin:0;font:inherit;font-size:var(--f-3);padding:var(--s2) var(--s3);border:1px solid var(--line);border-radius:var(--r-tag);background:var(--panel);color:var(--ink);cursor:pointer}
.covchips{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s2);margin:2px 0 6px}
.covchip{font-size:var(--f-2);padding:var(--s1) var(--s4);border-radius:var(--r-pill);border:1px solid var(--line);background:var(--panel);color:var(--muted);cursor:pointer;user-select:none}
.covchip:hover{border-color:var(--accent);color:var(--accent)}
.covchip.on{background:var(--accent);color:#fff;border-color:var(--accent)}
.vfclear{font:inherit;font-size:var(--f-2);padding:var(--s2) var(--s4);border:1px solid var(--line);border-radius:var(--r-pill);background:transparent;color:var(--muted);cursor:pointer;align-self:flex-end}
.vfclear:hover{border-color:var(--accent);color:var(--accent)}
.fortpill{border-color:var(--accent);color:var(--accent);font-weight:700}
.uspill{border-color:var(--b);color:var(--b);font-weight:700}
.listpill{border-color:var(--muted);color:var(--ink);font-weight:600}
.neuropill{border-color:oklch(0.58 0.17 300);color:oklch(0.58 0.17 300);font-weight:700}
/* compute_class pills — colour+weight distinguish (no emoji) */
.ccpill{font-weight:700}
.ccws{border-color:oklch(0.6 0.15 150);color:oklch(0.5 0.15 150)}
.ccgpu{border-color:var(--accent);color:var(--accent)}
.ccdb{border-color:oklch(0.6 0.13 255);color:oklch(0.52 0.13 255)}
.ccedge{border-color:oklch(0.65 0.14 60);color:oklch(0.52 0.14 60)}
.ccstor{border-color:var(--muted);color:var(--muted)}
.ccsaas{border-color:var(--line);color:var(--muted);font-weight:500}
.ccchip{cursor:pointer;border:1px solid var(--line);border-radius:var(--r-tag);padding:var(--s2) var(--s3);display:inline-flex;gap:var(--s2);align-items:center;background:var(--panel)}
.ccchip:hover{border-color:var(--accent);background:var(--accentbg)}
.ccchip .dn{font-weight:700;color:var(--muted);font-size:var(--f-2)}
.gtag{font-size:var(--f-1);padding:var(--s0) var(--s3);border-radius:var(--r-tag);background:var(--panel);border:1px solid var(--line);color:var(--muted);white-space:nowrap}
table.rankmatrix{border-collapse:collapse;width:100%;font-size:var(--f-3)}
table.rankmatrix th,table.rankmatrix td{text-align:left;padding:var(--s2) var(--s3);border-bottom:1px solid var(--line);white-space:nowrap;vertical-align:middle}
table.rankmatrix th{color:var(--muted);font-size:var(--f-1);text-transform:uppercase;letter-spacing:.4px;position:sticky;top:0;background:var(--bg)}
table.rankmatrix td.rnum{color:var(--muted);font-variant-numeric:tabular-nums}
table.rankmatrix tr:hover td{background:var(--accentbg)}
.scbar{display:inline-block;width:70px;height:7px;border-radius:var(--r-pill);background:var(--line);overflow:hidden;vertical-align:middle}
.scbarfill{display:block;height:100%;background:var(--accent)}
.rankmatrix .vflag,.rankmatrix .vhot{margin-right:4px}
</style>
</head>
<body>
<header>
  <button id="langtog" style="position:absolute;top:14px;right:16px;padding:var(--s2) var(--s4);border:1px solid var(--line);border-radius:var(--r-card);background:var(--card);color:var(--fg);font-size:var(--f-4);font-weight:700;cursor:pointer">中文</button>
  <h1>SMCI Medical / Pharma GTM Playbook <span class="pill" id="ver"></span></h1>
  <div class="byline" id="byline"></div>
  <div class="sub" id="built"></div>
</header>
<nav id="nav"></nav>
<main>
  <section class="tab on" id="tab-taxonomy"></section>
  <section class="tab" id="tab-method"></section>
  <section class="tab" id="tab-vendors"></section>
</main>
<script>
const DATA = /*__DATA__*/null;
const $ = (s,r=document)=>r.querySelector(s);
const el=(t,a={},...kids)=>{const n=document.createElement(t);
  for(const k in a){if(k==='class')n.className=a[k];else n.setAttribute(k,a[k]);}
  for(const c of kids)n.append(c&&c.nodeType?c:document.createTextNode(c));return n;};
const clear=n=>n.replaceChildren();
const playClass=p=>({'play-a':'playa','play-b':'playb','play-c':'playc','play-d':'playd'}[p]||'');
// ---- i18n: EN <-> 中文 toggle (category names come from data name_zh; chrome from T()) ----
let LANG='en';
const nm=c=>LANG==='zh'?(c.name_zh||c.name_en):c.name_en;   // category display name
const sub=c=>LANG==='zh'?c.name_en:(c.name_zh||'');         // the secondary line under it
const T=(en,zh)=>LANG==='zh'?zh:en;                          // chrome string
const playName=p=>({'play-a':'A · Imaging/Path','play-b':'B · Genomics/AI','play-c':'C · GMP Edge','play-d':'D · Clinical Core'}[p]||p);
const PLAY_BY={};(DATA.plays.plays||[]).forEach(p=>PLAY_BY[p.id]=p);  // play id -> full play (name, hardware_anchor)
const DOM_ZH={'hospital-clinical-core':'醫院·臨床核心','hospital-business-administration':'醫院·行政','hospital-device-facility-operations':'醫院·設備設施','diagnostics-laboratory':'診斷實驗室','pharmaceutical-research-clinical-development':'藥廠研發','manufacturing-quality-supply-chain':'製造·品管·供應鏈','data-analytics-payer-platforms':'資料·支付方','medical-technology-device-software':'醫材裝置軟體'};
const DOM_EN={'hospital-clinical-core':'Hospital · Clinical Core','hospital-business-administration':'Hospital · Administration','hospital-device-facility-operations':'Hospital · Device & Facility','diagnostics-laboratory':'Diagnostics Lab','pharmaceutical-research-clinical-development':'Pharma R&D','manufacturing-quality-supply-chain':'Manufacturing · QC · Supply','data-analytics-payer-platforms':'Data · Payer Platforms','medical-technology-device-software':'MedTech Device Software'};
const domLabel=k=>(LANG==='zh'?DOM_ZH[k]:DOM_EN[k])||k;
// SMCI server family per hardware_profile component (the "workload SMCI can help with")
const SMCI_FAMILY={'gpu-server':['GPU servers (NVIDIA HGX / MGX)','GPU 伺服器 (NVIDIA HGX/MGX)'],
 'high-performance-computing-cpu':['HPC compute nodes (dense multi-node)','HPC 運算節點 (高密度多節點)'],
 'nvme-performance-storage':['NVMe all-flash performance storage','NVMe 全快閃效能儲存'],
 'capacity-archive-storage':['High-capacity archive (top-load JBOD)','大容量封存儲存 (頂載 JBOD)'],
 'high-memory':['High-memory servers (multi-TB DRAM)','大記憶體伺服器 (多-TB DRAM)'],
 'edge-industrial':['Industrial / short-depth edge servers','工業／短機身邊緣伺服器'],
 'high-availability-redundant':['High-availability redundant pairs','高可用冗餘配對'],
 'disaster-recovery-backup':['Disaster-recovery / backup nodes','災難備援節點']};
const smciFam=h=>(LANG==='zh'?(SMCI_FAMILY[h]||[h,h])[1]:(SMCI_FAMILY[h]||[h,h])[0]);
// plain-language gloss + role group per SMCI box, so the product-line door reads
// as three clear buckets (compute / storage / deploy) not eight unexplained acronyms.
// [group, short_en, short_zh, gloss_en, gloss_zh]
const PLINE={
 'gpu-server':['compute','GPU servers','GPU 伺服器','GPU compute — AI, GPU-HPC','GPU 運算 — AI、GPU-HPC'],
 'high-performance-computing-cpu':['compute','HPC (CPU)','HPC(CPU)','CPU-only cluster','純 CPU 叢集'],
 'high-memory':['compute','High-memory','大記憶體','one box, huge RAM','單機大 RAM'],
 'nvme-performance-storage':['storage','NVMe all-flash','NVMe 全快閃','hot data, fast (SSD)','熱資料・快(SSD)'],
 'capacity-archive-storage':['storage','Capacity archive','大容量封存','cold bulk (HDD)','冷資料・大量(傳統硬碟)'],
 'edge-industrial':['deploy','Industrial edge','工業邊緣','on-site / plant floor','現場／廠房'],
 'high-availability-redundant':['deploy','HA pairs','高可用配對','keeps it running','維持不中斷'],
 'disaster-recovery-backup':['deploy','DR / backup','災難備援','recover after disaster','災後復原']};
const PGRP=[['compute','Compute','運算'],['storage','Storage','儲存'],['deploy','Deploy & resilience','部署・韌性']];
const plineGloss=h=>PLINE[h]?(LANG==='zh'?PLINE[h][4]:PLINE[h][3]):'';

// ===== compute_class — "what iron does the software pull" (the actionable SKU axis) =====
// Derived from workload gpu_role + hardware_profile + sizing. Buyer axis carries ~no signal
// (near-universal vendor co-sell); THIS decides which SMCI box you walk in with. Two CPU tiers
// are kept separate per Tuo: cpu-workstation (single/small node, no GPU) vs cpu-server (DB/edge).
function computeClassOf(c){
  const hp=new Set(c.hardware_profile||[]);
  const gr=(c.workload_envelope||{}).gpu_role;
  if(hp.has('gpu-server')||gr==='inference'||gr==='training'||gr==='mixed') return gr==='mixed'?'gpu-mixed':'gpu';
  if(hp.has('high-performance-computing-cpu')||hp.has('high-memory')) return 'cpu-workstation';
  if(hp.has('high-availability-redundant')) return 'cpu-db';
  if(hp.has('edge-industrial')) return 'cpu-edge';
  if(hp.has('capacity-archive-storage')||hp.has('nvme-performance-storage')||hp.has('disaster-recovery-backup')) return 'storage';
  return 'saas-light';
}
// [label_en, label_zh, gloss_en, gloss_zh, sku_en, sku_zh, cssclass, noGpu]
const CC_META={
 'cpu-workstation':['CPU workstation','CPU 工作站','CPU-bound, memory-heavy, single/small node — no GPU','純 CPU、吃記憶體、單/小節點 — 無 GPU','Workstation / dual-socket CPU node','工作站／雙路 CPU 節點','ccws',true],
 'gpu-mixed':['GPU + CPU','GPU + CPU','GPU rack with a heavy CPU co-stage','GPU 機架 + 重 CPU 階段','GPU server + CPU nodes','GPU 伺服器 + CPU 節點','ccgpu',false],
 'gpu':['GPU','GPU','GPU inference / training','GPU 推論／訓練','GPU server (NVIDIA HGX/MGX)','GPU 伺服器 (HGX/MGX)','ccgpu',false],
 'cpu-db':['CPU server · DB/OLTP','CPU 伺服器 · DB/OLTP','transactional DB, no GPU — resilience play','交易型 DB、無 GPU — 韌性打法','1U/2U NVMe OLTP + HA pair + DR','1U/2U NVMe OLTP + HA 配對 + DR','ccdb',true],
 'cpu-edge':['CPU edge','CPU 邊緣','industrial / on-site, no GPU','工業／現場、無 GPU','Industrial / short-depth edge server','工業／短機身邊緣伺服器','ccedge',true],
 'storage':['Storage / DR','儲存／DR','archive + fast NVMe + backup, no compute','封存 + NVMe + 備援、非運算','Archive JBOD + NVMe + DR nodes','封存 JBOD + NVMe + DR','ccstor',true],
 'saas-light':['SaaS-light','SaaS 輕量','no dedicated on-prem box','無專屬機房機箱','—','—','ccsaas',false]};
const CC_ORDER=['cpu-workstation','gpu-mixed','gpu','cpu-db','cpu-edge','storage','saas-light'];
const ccLabel=k=>{const m=CC_META[k];return m?(LANG==='zh'?m[1]:m[0]):k;};
const ccGloss=k=>{const m=CC_META[k];return m?(LANG==='zh'?m[3]:m[2]):'';};
const ccSku=k=>{const m=CC_META[k];return m?(LANG==='zh'?m[5]:m[4]):'';};
const ccClass=k=>(CC_META[k]||[])[6]||'';
const ccNoGpu=k=>!!(CC_META[k]||[])[7];

// ---- derived infra-control rollup (mirrors tools/rollup.py; Tuo-approved mapping) ----
const ONPREM_SIDE=new Set(['on-premises','edge','private-cloud','original-equipment-manufacturer']);
const CLOUD_SIDE=new Set(['public-cloud','software-as-a-service','vendor-managed']);
function bucketOf(c){for(const d of c.deployment){if(d==='hybrid')continue;return ONPREM_SIDE.has(d)?'on-prem':'cloud';}return 'hybrid';}
function spansOf(c){const s=new Set(c.deployment);return s.has('hybrid')||([...s].some(x=>ONPREM_SIDE.has(x))&&[...s].some(x=>CLOUD_SIDE.has(x)));}
// hardware_buyer = WHO buys the iron (authoritative §3 axis, taxonomy v3)
const BUYER_C={customer:'bcust',operator:'boper','original-equipment-manufacturer':'boem',hyperscaler:'bhyp'};
const OPP={1:'minimal',2:'modest',3:'significant',4:'flagship'};
const VNAME={};(DATA.vendors.vendors||[]).forEach(v=>VNAME[v.id]=v.name);
// ---- relationship fusion: cross-tab lookups (category <-> vendor <-> leaderboard) ----
const VBYID={};(DATA.vendors.vendors||[]).forEach(v=>VBYID[v.id]=v);
const CATBYID={};(DATA.taxonomy.categories||[]).forEach(c=>CATBYID[c.id]=c);
const LB_BY_VID={};
(function(){const LB=DATA.leaderboards&&DATA.leaderboards.leaderboards;if(!LB)return;
  [['ai',LB.ai],['no_ai',LB.no_ai]].forEach(([bk,b])=>{if(!b)return;(b.entries||[]).forEach(e=>{
    if(e.vendor_id){(LB_BY_VID[e.vendor_id]=LB_BY_VID[e.vendor_id]||[]).push({board:bk,rank:e.rank});}});});})();
const lbBadge=vid=>{const r=LB_BY_VID[vid];return r?r.map(x=>(x.board==='ai'?'AI':'No-AI')+' #'+x.rank).join(' · '):null;};
// ---- value signals (flagship=opp4, HOT=customer opp>=3) reused everywhere ----
const isFlag=c=>c.hardware_opportunity===4, isHot=c=>(c.hardware_opportunity_by_buyer.customer||0)>=3;
function catsVal(ids){let flag=0,hot=0;(ids||[]).forEach(id=>{const c=CATBYID[id];if(!c)return;if(isFlag(c))flag++;if(isHot(c))hot++;});return {flag,hot,n:(ids||[]).length};}
const vendorVal=v=>catsVal(v.categories);
// value badges (text, no icons): red flagship + green HOT
function valBadges(v,into){if(v.flag)into.append(el('span',{class:'vflag',title:'flagship categories (opportunity 4)'},v.flag+' '+T('flagship','旗艦')));if(v.hot)into.append(el('span',{class:'vhot',title:'customer-HOT categories (opportunity ≥3)'},v.hot+' HOT'));return into;}
function goVendor(id){goTab('vendors');const q=$('#tab-vendors input[type=search]');const v=VBYID[id];if(q&&v){q.value=v.name;q.dispatchEvent(new Event('input'));}}
function goCategory(id){goTab('taxonomy');const ft=$('#fTxt');const c=CATBYID[id];if(ft&&c){ft.value=c.name_en;ft.dispatchEvent(new Event('input'));}}

// ===== vendor filter derivations — region/state/coverage computed in-app from existing data;
//        fortune + us_market_share_pct come from data/vendors.yaml (web-researched, §8-sourced) =====
const US_STATES_SET=new Set(['Alabama','Alaska','Arizona','Arkansas','California','Colorado','Connecticut','Delaware','Florida','Georgia','Hawaii','Idaho','Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana','Maine','Maryland','Massachusetts','Michigan','Minnesota','Mississippi','Missouri','Montana','Nebraska','Nevada','New Hampshire','New Jersey','New Mexico','New York','North Carolina','North Dakota','Ohio','Oklahoma','Oregon','Pennsylvania','Rhode Island','South Carolina','South Dakota','Tennessee','Texas','Utah','Vermont','Virginia','Washington','West Virginia','Wisconsin','Wyoming','District of Columbia']);
const EU_SET=new Set(['Germany','United Kingdom','UK','Scotland','England','Switzerland','France','Netherlands','Sweden','Denmark','Ireland','Finland','Italy','Belgium','Portugal','Poland','Spain','Norway','Austria','Czech Republic','Luxembourg','Iceland']);
const APAC_SET=new Set(['Japan','South Korea','Korea','China','Hong Kong','Taiwan','Singapore','Australia','New Zealand','India','Malaysia','Thailand']);
const ME_SET=new Set(['Israel','United Arab Emirates','UAE','Saudi Arabia','Qatar']);
function hqParse(v){
  const hq=v.headquarters; if(!hq)return {region:'Unknown',country:null,state:null};
  const toks=String(hq).split(',').map(t=>t.replace(/[)]/g,'').trim()).filter(Boolean);
  const last=toks.length?toks[toks.length-1]:'';
  const isUS=/\b(USA|United States)\b/.test(hq)||US_STATES_SET.has(last);
  if(isUS){let st=null;for(let i=toks.length-1;i>=0;i--){if(US_STATES_SET.has(toks[i])){st=toks[i];break;}}return {region:'North America',country:'USA',state:st};}
  if(last==='Canada'||last==='Mexico')return {region:'North America',country:last,state:null};
  if(EU_SET.has(last))return {region:'Europe',country:last,state:null};
  if(APAC_SET.has(last))return {region:'Asia-Pacific',country:last,state:null};
  if(ME_SET.has(last))return {region:'Middle East',country:last,state:null};
  if(/United States/.test(hq))return {region:'North America',country:'USA',state:null};
  return {region:'Other',country:last||null,state:null};
}
const REGIONS=['North America','Europe','Asia-Pacific','Middle East','Other'];
function coverageOf(v){const s=new Set();(v.categories||[]).forEach(id=>{const c=CATBYID[id];if(c&&c.domain)s.add(c.domain);});return [...s];}
const FORT_LABEL={'fortune-500':'Fortune 500','fortune-1000':'Fortune 1000','global-500':'Global 500'};
const FORT_WT={'fortune-500':3,'global-500':2,'fortune-1000':1};
function fortuneOf(v){const f=v.fortune;return (f&&f.list&&f.list!=='none')?f:null;}
function usShareOf(v){return (typeof v.us_market_share_pct==='number')?v.us_market_share_pct:null;}
// public-listing status (web-verified) + brain/neuro clinical flag — enrichment from data/vendors.yaml
function listedOf(v){return v.listing||null;}
function neuroOf(v){return v.neuro===true;}
const LISTED_LABEL={public:['Public','上市'],subsidiary_of_public:['Sub · public parent','母公司上市'],subsidiary_of_private:['Sub · private','私有·子公司'],private:['Private','私有'],acquired:['Acquired','被併'],'nonprofit_or_gov':['Nonprofit / Gov','非營利 / 政府'],unknown:['Unknown','未知']};
function listedLabel(l){const m=LISTED_LABEL[(l&&l.status)]||LISTED_LABEL.unknown;return T(m[0],m[1]);}
// bundle-fit score (0-100): hardware pull (the anchor) + coverage breadth + US share + Fortune + US-region
function bundleScore(v){
  const val=vendorVal(v);
  const hw=Math.min(1,(val.flag*2+val.hot)/6);
  const cover=coverageOf(v);
  const cov=Math.min(1,cover.length/3);
  const share=usShareOf(v);
  const sh=Math.min(1,(share||0)/50);
  const f=fortuneOf(v);
  const ft=f?((FORT_WT[f.list]||0)/3):0;
  const p=hqParse(v);
  const rg=p.country==='USA'?1:(p.region==='North America'?0.7:0.3);
  const score=Math.round(hw*35+cov*20+sh*20+ft*15+rg*10);
  return {score,hw,cov,sh,ft,rg,val,cover,region:p.region,state:p.state,country:p.country,fort:f,share};
}

// ---- header ----
$('#ver').textContent='taxonomy v'+DATA.taxonomy.version+' · '+DATA.taxonomy.status;
function setBuilt(){const cats=DATA.taxonomy.categories;const nv=(DATA.vendors.vendors||[]).length;
  $('#built').textContent=cats.length+T(' software categories · ',' 軟體類別 · ')+nv+T(' vendors mapped to the Supermicro hardware behind them',' 家廠商對應其背後的 Supermicro 硬體');
  $('#byline').textContent=T('Sales Manager, Team 1 · Tuo Cheng','業務經理・第一組 · 鄭鐸');}
setBuilt();

// ---- tabs ----
const TABS=[['taxonomy','Explore'],['method','Method'],['vendors','Vendors']];
const nav=$('#nav');
const NAVBTN={};
function goTab(id,opts){opts=opts||{};
  document.querySelectorAll('nav button').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));
  if(NAVBTN[id])NAVBTN[id].classList.add('on');
  const sec=$('#tab-'+id); if(sec)sec.classList.add('on');
  if(opts.scrollTo){const t=document.getElementById(opts.scrollTo);if(t){t.scrollIntoView({behavior:'smooth',block:'start'});return;}}
  window.scrollTo(0,0);
}
TABS.forEach(([id,label],i)=>{
  const b=el('button',{class:i===0?'on':''},label);
  NAVBTN[id]=b; b.onclick=()=>goTab(id);
  nav.append(b);
});

// ---- scoring helpers (mirrors tools/score.py; weights from scoring.yaml) ----
const SC=DATA.scoring, SMAX=(SC.scale&&SC.scale.max)||5;
const TIERS=[...SC.tiers].sort((a,b)=>b.min-a.min);
function scoreAccount(acc){
  const raw=acc.scoring||{}; let total=0; const rows=[];
  for(const it of SC.items){const v=raw[it.key]??0; const w=(v/SMAX)*it.weight; total+=w;
    rows.push({label:it.label,key:it.key,score:v,weight:it.weight,weighted:Math.round(w*10)/10});}
  const tier=TIERS.find(t=>total>=t.min);
  return {total:Math.round(total*10)/10,tier,rows};
}
function tierColor(name){return {'Active pursuit':'var(--a)','Nurture / partner-led':'var(--u-med)','Monitor':'var(--u-low)','Drop':'var(--u-crit)'}[name]||'var(--muted)';}

// isAI: derived AI/no-AI flag (role/modality/gpu) — used by the stakeholder view.
const isAI=c=>(c.role||[]).includes('analytics-artificial-intelligence')||(c.data_modality||[]).includes('artificial-intelligence-models')||(c.hardware_profile||[]).includes('gpu-server');

// ================= EXPLORE (unified universe: Home's stakeholder view folded in) =================
function renderTaxonomy(){
  const cats=DATA.taxonomy.categories, E=DATA.taxonomy.enums, root=$('#tab-taxonomy'); clear(root);
  // single search input, rendered prominently in the launcher (below) and read by render()
  const fTxt=el('input',{id:'fTxt',class:'hsearch',type:'search',placeholder:T('Search a category, vendor, or SMCI box — “digital pathology” · “Sectra” · “GPU”…','搜尋類別、廠商、或 SMCI 硬體 —「數位病理」·「Sectra」·「GPU」…')});
  root.append(el('h2',{style:'margin:2px 0 6px'},T('The medical / pharma software universe','醫療／藥廠軟體宇宙')));
  masterTable();
  const mk=(id,opts,label)=>{const s=el('select',{id});s.append(el('option',{value:''},label));
    opts.forEach(o=>s.append(el('option',{value:o},o)));return s;};
  const fBuyer=mk('fBuyer',['customer','operator','original-equipment-manufacturer','hyperscaler'],'all buyers'),
        fBucket=mk('fBucket',['on-prem','cloud'],'all substrate'),
        fSeg=mk('fSeg',E.segments,'all segments'),
        fPlay=mk('fPlay',['play-a','play-b','play-c'],'all plays'),
        fDep=mk('fDep',E.deployment,'all deployments'),
        fHw=mk('fHw',['1','2','3','4'],'opportunity ≥'),
        fProfile=mk('fProfile',['gpu-server','high-performance-computing-cpu','nvme-performance-storage','capacity-archive-storage','high-memory','edge-industrial','high-availability-redundant','disaster-recovery-backup'],'all hardware'),
        fCompute=mk('fCompute',CC_ORDER,'all compute types'),
        fGroup={value:''},
        fSpansBox=el('input',{type:'checkbox'}),
        cnt=el('span',{class:'count'});
  const fSpans=el('label',{class:'ckbox'},fSpansBox,T('spans on-prem↔cloud','橫跨 on-prem↔雲'));
  const hotC=cats.filter(c=>(c.hardware_opportunity_by_buyer.customer||0)>=3).length,
        hotO=cats.filter(c=>(c.hardware_opportunity_by_buyer.operator||0)>=3).length,
        nOem=cats.filter(c=>(c.hardware_opportunity_by_buyer['original-equipment-manufacturer']||0)>=3).length;
  const resetSel=()=>{[fBuyer,fBucket,fSeg,fPlay,fDep,fHw,fProfile,fCompute].forEach(x=>x.value='');fSpansBox.checked=false;fTxt.value='';};
  // ---- toolbar: one segmented control to regroup all categories, + search ----
  const seg=el('div',{class:'seg'});
  function setGroup(g){hotFilter=null;catFilter=null;fGroup.value=g;[...seg.querySelectorAll('button')].forEach(x=>x.classList.toggle('on',x.dataset.g===g));render();}
  [['domain',T('care area','照護領域')],['compute',T('compute type','計算類型')],['stakeholder',T('who uses it','使用者')],['play',T('play','打法')]]
    .forEach(([g,lab])=>{const b=el('button',{'data-g':g},lab);b.onclick=()=>setGroup(g);seg.append(b);});
  const tb=el('div',{class:'toolbar'});
  tb.append(el('span',{class:'tagk'},T('view by','檢視')),seg,el('span',{style:'flex:1 1 20px'}),cnt);
  root.append(tb);
  // ---- one thin line of high-opportunity target shortcuts (colour = who buys) ----
  const jump=el('div',{class:'jump'});
  const jb=(n,txt,fn,cls)=>{const s=el('button',{class:'jbtn '+cls});s.append(el('b',{},String(n)),txt);s.onclick=fn;return s;};
  jump.append(el('span',{},T('jump to targets','跳到目標')+' ▸'),
    jb(hotC,T('customer direct','客戶直銷'),()=>window.exploreFilter('customer',3),'sc-cust'),
    jb(hotO,T('ISV co-sell','ISV 共銷'),()=>window.exploreFilter('operator',3),'sc-oper'),
    jb(nOem,'OEM',()=>window.exploreFilter('original-equipment-manufacturer',3),'sc-oem'),
    jb(cats.length,T('all','全部'),()=>{hotFilter=null;resetSel();setGroup('domain');},'sc-all'));
  root.append(jump);
  // ---- collapsible advanced filters, each labeled ----
  const labeled=(lab,elm)=>el('label',{class:'flab'},el('span',{},lab),elm);
  root.append(el('details',{class:'refine'},el('summary',{},T('More filters','更多篩選')),
    el('div',{class:'filters'},
      labeled(T('substrate','substrate'),fBucket),labeled(T('segment','客群'),fSeg),
      labeled(T('min opportunity','最低機會'),fHw),
      labeled(T('compute type (SKU)','計算類型(SKU)'),fCompute))));
  const treePane=el('div',{class:'tree'}), detailPane=el('div',{class:'detail'});
  let selected=null;
  let navStack=[], dv={kind:'none',id:null};
  const backBtn=el('button',{class:'backbtn',style:'display:none'},'← '+T('Back','返回'));
  root.append(backBtn);
  root.append(el('div',{class:'twopane',id:'twopane'},treePane,detailPane));
  const byOpp=(a,b)=>b.hardware_opportunity-a.hardware_opportunity||a.id.localeCompare(b.id);
  function showDetail(c){selected=c||null;clear(detailPane);
    if(!c){detailPane.append(el('div',{class:'muted',style:'padding:24px var(--s1)'},T('Select a category on the left.','在左邊選一個類別。')));return;}
    detailPane.append(detailCard(c));dv={kind:'cat',id:c.id};
    [...treePane.querySelectorAll('.trow')].forEach(r=>r.classList.toggle('sel',r.dataset.id===c.id));}
  // ---- back navigation: a stack of {catFilter, detail-view} snapshots ----
  const TRIG_BY={};(DATA.triggers.triggers||[]).forEach(t=>TRIG_BY[t.id]=t);
  function updateBack(){backBtn.style.display=navStack.length?'inline-flex':'none';}
  function pushNav(){navStack.push({cf:catFilter?catFilter.slice():null,dv:{kind:dv.kind,id:dv.id}});updateBack();}
  function applyDv(){if(dv.kind==='cat'&&CATBYID[dv.id])showDetail(CATBYID[dv.id]);
    else if(dv.kind==='trigger'&&TRIG_BY[dv.id]){clear(detailPane);detailPane.append(triggerBrief(TRIG_BY[dv.id]));}
    else if(dv.kind==='play'){clear(detailPane);detailPane.append(playBrief(dv.id));}}
  function goBack(){if(!navStack.length)return;const s=navStack.pop();catFilter=s.cf;hotFilter=null;fTxt.value='';render();dv=s.dv;applyDv();updateBack();scrollToPanes();}
  function viewCat(c){pushNav();showDetail(c);}
  backBtn.onclick=goBack;
  // expose Explore navigation so the Method "how to use" walkthrough can deep-link in
  window._exp={goTrigger:goTrigger,goPlay:goPlay,goCat:function(id){const c=CATBYID[id];if(c)viewCat(c);}};
  // trigger brief: a signal, organized — window · where to catch · the move · the markets it opens
  function triggerBrief(t){
    const cd=el('div',{class:'card'});
    cd.append(el('div',{class:'row',style:'align-items:center'},
      el('span',{class:'u '+t.urgency,style:'font-weight:800;text-transform:uppercase;font-size:var(--f-3)'},t.urgency),
      el('span',{class:'tagk'},T('trigger','觸發訊號')),
      ...(t.related_plays||[]).map(pid=>{const ch=el('span',{class:'play play'+pid.split('-')[1].toLowerCase(),style:'cursor:pointer'},'Play '+pid.split('-')[1].toUpperCase());ch.onclick=()=>goPlay(pid);return ch;})));
    cd.append(el('h3',{style:'margin:6px 0 4px'},t.signal));
    const bc=el('div',{class:'battle'});
    const brow=(lab,val)=>{const r=el('div',{class:'brow'});r.append(el('div',{class:'blab'},lab));r.append(el('div',{class:'bval'},val||'—'));bc.append(r);};
    brow(T('Window','時機窗口'),t.window);
    brow(T('Where to catch','哪裡抓'),t.source);
    brow(T('The move','該做什麼'),t.action);
    cd.append(bc);
    const ms=el('div',{class:'dsec'});ms.append(el('div',{class:'dsh'},T('Markets this opens — click for the battle card','開哪些市場 — 點看戰卡')));
    const mw=el('div',{class:'mklist'});
    (t.related_categories||[]).map(id=>CATBYID[id]).filter(Boolean)
      .sort((a,b)=>b.hardware_opportunity-a.hardware_opportunity).forEach(c=>{
      const it=el('div',{class:'mkitem'},el('span',{class:'hw hw'+c.hardware_opportunity,style:'font-size:var(--f-1);padding:0 var(--s2)'},String(c.hardware_opportunity)),el('span',{class:'mknm'},nm(c)));
      if(isFlag(c))it.append(el('span',{class:'cb f'},T('flagship','旗艦')));
      if(isHot(c))it.append(el('span',{class:'cb h'},T('direct','直銷')));
      it.onclick=()=>viewCat(c);mw.append(it);});
    if(!(t.related_categories||[]).length)mw.append(el('div',{class:'muted'},'—'));
    ms.append(mw);cd.append(ms);
    return cd;
  }
  // play brief: the play's bet, organized — hardware anchor · segments · the triggers that open it · target categories
  function playBrief(pid){
    const p=PLAY_BY[pid]; if(!p)return el('div',{});const L=pid.split('-')[1].toUpperCase();
    const cd=el('div',{class:'card'});
    cd.append(el('div',{class:'row',style:'align-items:center'},el('span',{class:'play play'+L.toLowerCase()},'Play '+L),el('span',{class:'tagk'},T('play','打法'))));
    cd.append(el('h3',{style:'margin:6px 0 4px'},p.name));
    const bc=el('div',{class:'battle'});
    const brow=(lab,val)=>{const r=el('div',{class:'brow'});r.append(el('div',{class:'blab'},lab));r.append(el('div',{class:'bval'},val||'—'));bc.append(r);};
    brow(T('Hardware anchor','硬體錨'),(p.hardware_anchor||[]).join(' · '));
    brow(T('Segments','客群'),(p.target_segments||[]).join(' · '));
    if(p.regulatory_notes)brow(T('Notes','備註'),p.regulatory_notes);
    cd.append(bc);
    // compute split — which SMCI box each part of the play pulls (GPU vs CPU-workstation vs CPU-server)
    const pmem0=cats.filter(c=>(c.plays||[]).includes(pid));
    const csec=el('div',{class:'dsec'});csec.append(el('div',{class:'dsh'},T('Compute split — the CPU / GPU parts of this play','計算拆分 — 此打法的 CPU／GPU 部分')));
    const cw0=el('div',{style:'display:flex;flex-wrap:wrap;gap:var(--s2)'});
    CC_ORDER.forEach(cc=>{const n=pmem0.filter(c=>computeClassOf(c)===cc).length;if(!n)return;
      const chip=el('span',{class:'pill ccpill '+ccClass(cc),style:'cursor:pointer',title:ccGloss(cc)+' → '+ccSku(cc)},ccLabel(cc)+' · '+n);
      chip.onclick=()=>window.exploreCompute(cc);cw0.append(chip);});
    csec.append(cw0);cd.append(csec);
    const feed=(DATA.triggers.triggers||[]).filter(t=>(t.related_plays||[]).includes(pid))
      .sort((a,b)=>({critical:0,high:1,medium:2,low:3}[a.urgency]-{critical:0,high:1,medium:2,low:3}[b.urgency]));
    if(feed.length){const ts=el('div',{class:'dsec'});ts.append(el('div',{class:'dsh'},T('Triggers that open this play — click for the signal brief','開啟此打法的訊號 — 點看訊號簡報')));
      const tw=el('div',{style:'display:flex;flex-wrap:wrap;gap:var(--s2)'});
      feed.forEach(t=>{const ch=el('span',{class:'pill',style:'cursor:pointer'},el('span',{class:'u '+t.urgency,style:'font-weight:700'},'● '),t.signal);ch.onclick=()=>goTrigger(t);tw.append(ch);});
      ts.append(tw);cd.append(ts);}
    const mem=cats.filter(c=>(c.plays||[]).includes(pid)).sort((a,b)=>b.hardware_opportunity-a.hardware_opportunity);
    const ms=el('div',{class:'dsec'});ms.append(el('div',{class:'dsh'},T('Target categories — click for the battle card','目標類別 — 點看戰卡')+' · '+mem.length));
    const mw=el('div',{class:'mklist'});
    mem.forEach(c=>{const it=el('div',{class:'mkitem'},el('span',{class:'hw hw'+c.hardware_opportunity,style:'font-size:var(--f-1);padding:0 var(--s2)'},String(c.hardware_opportunity)),el('span',{class:'mknm'},nm(c)));
      if(isFlag(c))it.append(el('span',{class:'cb f'},T('flagship','旗艦')));
      if(isHot(c))it.append(el('span',{class:'cb h'},T('direct','直銷')));
      it.onclick=()=>viewCat(c);mw.append(it);});
    ms.append(mw);cd.append(ms);
    return cd;
  }
  // shared navigation: filter the tree + land on the matching brief (used by doors AND by every play/trigger chip)
  function setNote(node){const nb=document.querySelector('.hnote');if(nb){clear(nb);if(node)nb.append(node);}}
  function scrollToPanes(){const tp=document.getElementById('twopane');if(tp)tp.scrollIntoView({behavior:'smooth',block:'start'});}
  function goTrigger(t){pushNav();catFilter=(t.related_categories||[]);hotFilter=null;fTxt.value='';render();
    clear(detailPane);detailPane.append(triggerBrief(t));dv={kind:'trigger',id:t.id};
    setNote(el('span',{},el('span',{class:'u '+t.urgency,style:'font-weight:700;text-transform:uppercase'},t.urgency+' · '),el('b',{},t.signal),T(' — brief on the right','— 右側簡報')));scrollToPanes();}
  function goPlay(pid){pushNav();const p=PLAY_BY[pid];catFilter=cats.filter(c=>(c.plays||[]).includes(pid)).map(c=>c.id);hotFilter=null;fTxt.value='';render();
    clear(detailPane);detailPane.append(playBrief(pid));dv={kind:'play',id:pid};
    setNote(el('span',{},el('span',{class:'play play'+pid.split('-')[1].toLowerCase()},'Play '+pid.split('-')[1].toUpperCase()),' ',el('b',{},p?p.name:''),' — '+catFilter.length+T(' categories · brief on the right',' 個類別 · 右側簡報')));scrollToPanes();}
  function catRow(c){const r=el('div',{class:'trow','data-id':c.id});
    r.append(el('span',{class:'hw hw'+c.hardware_opportunity,style:'font-size:var(--f-1);padding:0 var(--s2)',title:OPP[c.hardware_opportunity]},String(c.hardware_opportunity)));
    r.append(el('span',{class:'tname'},nm(c)));
    r.append(el('span',{class:'tby '+BUYER_C[c.primary_buyer],title:c.primary_buyer}));
    r.onclick=()=>viewCat(c);return r;}
  function l2into(body,list){[['ai',T('AI-driven','AI 驅動')],['no',T('No-AI','非 AI')]].forEach(([ak,alab])=>{
    const sub=list.filter(c=>ak==='ai'?isAI(c):!isAI(c));if(!sub.length)return;
    body.append(el('div',{class:'tsub'},alab+' · '+sub.length));
    sub.slice().sort(byOpp).forEach(c=>body.append(catRow(c)));});}
  const flagN=l=>l.filter(c=>c.hardware_opportunity===4).length;
  const hotN=l=>l.filter(c=>(c.hardware_opportunity_by_buyer.customer||0)>=3).length;
  function l1node(label,list,leaf,open){if(!list.length)return;
    if(open===undefined)open=true;
    const car=el('span',{class:'tcar'},open?'▾':'▸');
    const fl=flagN(list), ho=hotN(list);
    const hdr=el('div',{class:'tnode'},car,el('span',{style:'flex:1'},label));
    if(fl)hdr.append(el('span',{class:'tflag',title:T('flagship (opportunity 4)','旗艦 (機會 4)')},fl+' '+T('flagship','旗艦')));
    if(ho)hdr.append(el('span',{class:'thot',title:T('customer-HOT (opportunity ≥3)','客戶-HOT (機會≥3)')},ho+' HOT'));
    hdr.append(el('span',{class:'tcount'},String(list.length)));
    const body=el('div',{class:'tbody'});
    if(!open)body.style.display='none';
    hdr.onclick=()=>{const o=body.style.display!=='none';body.style.display=o?'none':'';car.textContent=o?'▸':'▾';};
    treePane.append(hdr,body);
    if(leaf)list.slice().sort(byOpp).forEach(c=>body.append(catRow(c)));else l2into(body,list);}
  // (dead taxonomy card() + tagRow() removed in P2 — live category renderer is detailCard(); the vendor
  //  registry has its own card(v). Both used a removed buyer-pill layout + a ⇄ glyph.)
  function detailCard(c){
    const det=c.detail||{}, cd=el('div',{class:'card'});
    // head = one glance line: opportunity · play · compute SKU. Buyer (weak, near-universal co-sell) is NOT a
    // head pill — it lives in the motion sentence + the tree colour dot.
    const head=el('div',{class:'row'},el('span',{class:'hw hw'+c.hardware_opportunity,title:OPP[c.hardware_opportunity]},String(c.hardware_opportunity)));
    (c.plays||[]).forEach(p=>{const ch=el('span',{class:'play '+playClass(p),style:'cursor:pointer',title:playName(p)},playName(p).split(' ')[0]);ch.onclick=()=>goPlay(p);head.append(ch);});
    const cck=computeClassOf(c);
    head.append(el('span',{class:'pill ccpill '+ccClass(cck),style:'cursor:pointer',title:ccGloss(cck)+' → '+ccSku(cck)},ccLabel(cck)));
    cd.append(head);
    cd.append(el('h3',{style:'margin:6px 0 0'},nm(c)));
    cd.append(el('div',{class:'zh'},sub(c)));
    if(c.name_full)cd.append(el('div',{class:'muted',style:'font-size:var(--f-3);margin-bottom:6px'},c.name_full));
    // ---- battle card: the actionable sell layer (motion · reference arch · trigger→move) ----
    const bc=el('div',{class:'battle'});
    const brow=(lab,node)=>{const r=el('div',{class:'brow'});r.append(el('div',{class:'blab'},lab));const v=el('div',{class:'bval'});v.append(node);r.append(v);bc.append(r);};
    const hb=c.hardware_buyer||[];
    const motion=(hb.includes('customer')&&isHot(c))?T('Direct sale — the end org buys and runs its own iron.','直銷 — 終端機構自己採購並運行硬體。')
      :hb.includes('operator')?T('Co-sell — an ISV / service operator runs the iron; sell through them.','共銷 — ISV／服務營運商運行硬體;透過他們賣。')
      :hb.includes('oem')?T('OEM design-win — hardware embedded in a device; per-unit BOM.','OEM 設計導入 — 硬體嵌入裝置;按台計 BOM。')
      :hb.includes('customer')?T('Direct sale (modest scale).','直銷(規模較小)。'):T('—','—');
    brow(T('Your motion','你的打法'),el('span',{},motion));
    const ra=el('div',{class:'rarch'});
    if((c.hardware_profile||[]).length)c.hardware_profile.forEach(h=>ra.append(el('span',{class:'raxx',title:plineGloss(h)},smciFam(h)+((c.hardware_profile_sizing||{})[h]?' · '+c.hardware_profile_sizing[h]:''))));
    else ra.append(el('span',{class:'muted'},T('SaaS-light — little on-prem iron to sell.','SaaS 輕量 — 幾乎無地端硬體可賣。')));
    if(ccSku(cck)!=='—')ra.append(el('span',{class:'raxx',style:'border-style:dashed',title:ccGloss(cck)},ccSku(cck)+' · '+(ccNoGpu(cck)?T('no GPU','無 GPU'):T('GPU','GPU'))));
    brow(T('Reference arch · SMCI box','建議配置 · SMCI 機箱'),ra);
    const trigs=(DATA.triggers.triggers||[]).filter(t=>(t.related_categories||[]).includes(c.id));
    if(trigs.length){const tw=el('div',{});trigs.forEach(t=>{const row=el('div',{class:'twrow'});
      row.append(el('span',{class:'u '+t.urgency,style:'font-size:var(--f-1);font-weight:700;text-transform:uppercase'},t.urgency));
      row.append(el('span',{class:'tsig'},t.signal));row.append(el('span',{class:'tact'},'→ '+t.action));tw.append(row);});
      brow(T('Trigger → move','盯訊號 → 動作'),tw);}
    cd.append(bc);
    // ---- context ladder: Who-uses scent only (Purpose/Flow/Tech folded into the drawer; Hardware/SMCI in the battle card) ----
    const tiers=el('div',{class:'tiers6'});
    const tier=(lab,cont)=>{tiers.append(el('div',{class:'tier6'},el('div',{class:'tlab'},lab),el('div',{class:'tcont'},cont)));};
    const who=el('span',{style:'display:flex;flex-wrap:wrap;gap:var(--s2)'});(c.segments||[]).forEach(s=>who.append(el('span',{class:'chip'},s)));(((c.hospital_view||{}).stakeholder)||[]).forEach(s=>who.append(el('span',{class:'chip dim'},s)));
    tier(T('Who uses','使用方'),who);
    cd.append(tiers);
    // ---- full explainer (authored prose) — folded; the 6-tier diagram above is its summary ----
    const expl=el('details',{class:'ldrawer',style:'margin-top:10px'});
    const eb=el('div',{});
    const sec=(lab,txt)=>{if(!txt)return;eb.append(el('div',{class:'dsec'},el('div',{class:'dsh'},lab),el('div',{},txt)));};
    sec(T('Purpose','目的'),(LANG==='zh'?det.purpose_zh:det.purpose_en));
    if(det.usage_flow&&det.usage_flow.length){const fs=el('div',{class:'dsec'});fs.append(el('div',{class:'dsh'},T('Usage flow','使用流程')));det.usage_flow.forEach((s,i)=>fs.append(el('div',{class:'dstep'},el('b',{},(i+1)+'.'),el('span',{},LANG==='zh'?s.zh:s.en))));eb.append(fs);}
    sec(T('How it works','技術講解'),(LANG==='zh'?det.tech_zh:det.tech_en));
    sec(T('Supermicro workload fit','SMCI 可協助的 workload'),(LANG==='zh'?det.smci_zh:det.smci_en));
    if(eb.children.length){expl.append(el('summary',{},T('How this category works','這個類別怎麼運作')));expl.append(eb);cd.append(expl);}
    if(c.infrastructure_notes)cd.append(el('div',{class:'notes'},c.infrastructure_notes));
    // ---- vendors in this market — collapsible drawer with cited market-share bars ----
    if(c.vendors&&c.vendors.length){
      const rows=c.vendors.map(vid=>{const v=VBYID[vid]||{};return {vid:vid,name:VNAME[vid]||vid,rank:lbBadge(vid),
        pct:(typeof v.market_share_pct==='number'?v.market_share_pct:null),src:v.market_share||''};});
      rows.sort((a,b)=>(b.pct==null?-1:b.pct)-(a.pct==null?-1:a.pct)||((a.rank?0:1)-(b.rank?0:1))||a.name.localeCompare(b.name));
      const nShare=rows.filter(r=>r.pct!=null).length;
      const d=el('details',{class:'vdrawer'});
      d.append(el('summary',{},T('Vendors in this market','此市場的廠商')+' · '+rows.length+(nShare?' · '+nShare+T(' with cited share',' 家有引用市佔'):'')));
      const body=el('div',{class:'vsbody'});
      rows.forEach(r=>{const row=el('div',{class:'msrow'});
        const nmc=el('span',{class:'msn'});const vn=el('span',{class:'vn'},r.name);vn.onclick=()=>goVendor(r.vid);nmc.append(vn);
        if(r.rank)nmc.append(el('span',{class:'msrk'},r.rank));
        row.append(nmc);
        if(r.pct!=null){const tr=el('div',{class:'mstrack',title:r.src});tr.append(el('div',{class:'msfill',style:'width:'+Math.min(100,r.pct)+'%'}));row.append(tr);row.append(el('span',{class:'msp'},r.pct+'%'));}
        else{row.append(el('div',{class:'mstrack empty'}));row.append(el('span',{class:'msund',title:r.src||''},T('n/a','未公開')));}
        body.append(row);});
      d.append(body);
      d.append(el('div',{class:'muted',style:'font-size:var(--f-1);margin-top:5px;line-height:1.4'},T('Bars = cited market share (hover a bar for the source); “n/a” = no public share figure. Each share is of that vendor’s own market.','長條=有引用來源的市佔率(游標移到長條看來源);「未公開」=無公開市佔數字。每個市佔為該廠商所屬市場之比例。')));
      cd.append(d);
    }
    // ---- partner landscape drawer: who this market's vendors run with (SMCI co-sell / displacement) ----
    if(c.vendors&&c.vendors.length){
      const pv=c.vendors.map(vid=>({vid:vid,name:VNAME[vid]||vid,ps:((VBYID[vid]||{}).partnerships||[])})).filter(x=>x.ps.length);
      const hwc=x=>x.ps.some(p=>p.kind==='hardware'||p.kind==='cloud');
      pv.sort((a,b)=>((hwc(b)?1:0)-(hwc(a)?1:0))||a.name.localeCompare(b.name));
      if(pv.length){
        const d=el('details',{class:'vdrawer'});
        d.append(el('summary',{},T('Who these vendors partner with','這些廠商跟誰合作')+' · '+pv.length));
        const body=el('div',{class:'vsbody'});
        pv.forEach(x=>{const row=el('div',{class:'prow'});
          const vn=el('span',{class:'pvn'},x.name);vn.onclick=()=>goVendor(x.vid);row.append(vn);
          const chips=el('span',{class:'pchips'});
          x.ps.forEach(p=>{const hl=(p.kind==='hardware'||p.kind==='cloud');
            chips.append(el('span',{class:'pchip'+(hl?' pk-hw':''),title:p.partner+' ('+p.kind+') — '+(p.note||'')+(p.source?'  ['+p.source+']':'')},p.partner));});
          row.append(chips);body.append(row);});
        d.append(body);
        d.append(el('div',{class:'muted',style:'font-size:var(--f-1);margin-top:5px;line-height:1.4'},T('Hardware / cloud partners are highlighted — each is an SMCI co-sell or displacement angle (the vendor already runs on someone’s iron). Hover a partner for the note + source.','硬體／雲夥伴標亮 — 每個都是 SMCI 共銷或替換切入點(該廠商已跑在別人的鐵上)。游標移到夥伴看說明與來源。')));
        cd.append(d);
      }
    }
    return cd;
  }
  function groupsOf(c,axis){
    if(axis==='hardware_opportunity')return [String(c.hardware_opportunity)];
    if(axis==='bucket')return [bucketOf(c)];
    if(axis==='primary_buyer')return [c.primary_buyer];
    if(axis==='hardware_buyer')return c.hardware_buyer.slice();
    if(axis==='play')return (c.plays&&c.plays.length)?c.plays.slice():['(no play)'];
    if(axis==='hardware_profile')return (c.hardware_profile&&c.hardware_profile.length)?c.hardware_profile.slice():['(no hardware)'];
    if(axis==='domain')return [c.domain];
    if(axis==='compute')return [computeClassOf(c)];
    if(axis==='ai')return [isAI(c)?T('AI-driven','AI 驅動'):T('No-AI','非 AI')];
    return (c[axis]||[]).slice();
  }
  // ---- stakeholder view: WHO uses the software (Home's axis, folded in) ----
  // L1 = point-of-care stakeholder; the non-hospital "other" bucket is split by
  // care domain so it is not a 30-item dump. L2 = AI-driven / No-AI.
  const STAKE=[['facility',T('Facility','設施')],['doctor',T('Doctor','醫生')],['nurse',T('Nurse','護理')],['patient',T('Patient','病人')],
    ['other:pharmaceutical-research-clinical-development',T('R&D / Pharma','研發／藥廠')],
    ['other:manufacturing-quality-supply-chain',T('Manufacturing','製造')],
    ['other:diagnostics-laboratory',T('Lab','實驗室')],
    ['other:data-analytics-payer-platforms',T('Data / Payer','資料／支付方')],
    ['other:medical-technology-device-software',T('MedTech','醫材軟體')]];
  const stakeKey=c=>c.home_stakeholder==='other'?('other:'+c.domain):c.home_stakeholder;
  // ---- hunt launcher: four doors (search · product line · trigger · play),
  //      every door filters the tree and lands on the category's battle card ----
  function masterTable(){
    const box=el('div',{class:'launch'});
    box.append(el('div',{class:'row',style:'justify-content:space-between;align-items:baseline;margin-bottom:2px'},
      el('h3',{style:'margin:0'},T('Start the hunt — pick a door','開始獵單 — 選一道門')),
      el('span',{class:'muted',style:'font-size:var(--f-3)'},cats.length+T(' categories · ',' 類 · ')+(DATA.vendors.vendors||[]).length+T(' vendors',' 廠商'))));
    box.append(el('div',{class:'muted',style:'font-size:var(--f-3);margin:0 0 8px'},T('Search, or start from a Supermicro product line, a trigger, or a play. Every door opens the category’s battle card — your motion, the reference architecture to pitch, and the trigger to act on.','搜尋,或從 Supermicro 產品線、觸發訊號、或打法開始。每道門都打開該類別的戰卡 — 你的打法、要提的建議配置、該盯的訊號。')));
    // door: search — the single search input (also read by render); no duplicate in the toolbar
    box.append(fTxt);
    const note=el('div',{class:'hnote'});box.append(note);
    const openDoor=(labelNode,ids,brief)=>{pushNav();catFilter=ids;hotFilter=null;fTxt.value='';render();
      clear(note);if(labelNode)note.append(labelNode);
      if(brief){selected=null;clear(detailPane);detailPane.append(brief);}
      const tp=document.getElementById('twopane');if(tp)tp.scrollIntoView({behavior:'smooth',block:'start'});};
    const URANK={critical:0,high:1,medium:2,low:3};
    // door: SMCI product line (facet 1) — folded drawer so the workspace stays above the fold
    const pdrawer=el('details',{class:'ldrawer'});
    pdrawer.append(el('summary',{},T('Product line (SMCI box)','產品線(SMCI 機箱)')));
    const plist=el('div',{class:'plist'});
    PGRP.forEach(([gk,gen,gzh])=>{
      const rows=Object.keys(PLINE).filter(h=>PLINE[h][0]===gk)
        .map(h=>[h,cats.filter(c=>(c.hardware_profile||[]).includes(h)).map(c=>c.id)]).filter(([h,ids])=>ids.length);
      if(!rows.length)return;
      plist.append(el('div',{class:'pgrp'},LANG==='zh'?gzh:gen));
      rows.forEach(([h,ids])=>{const nm2=LANG==='zh'?PLINE[h][2]:PLINE[h][1],gl=plineGloss(h);
        const it=el('div',{class:'pitem'},el('span',{class:'pnm'},nm2),el('span',{class:'pgl'},'— '+gl),el('span',{class:'pct'},String(ids.length)));
        it.onclick=()=>openDoor(el('span',{},el('b',{},nm2),' — '+gl+'. '+ids.length+T(' categories pull this box.',' 個類別拉動此機箱。')),ids);
        plist.append(it);});
    });
    pdrawer.append(plist);
    pdrawer.append(el('div',{class:'muted',style:'font-size:var(--f-2);margin:1px 0 4px'},T('Counts overlap — a category often pulls several boxes.','數字會重疊 — 一個類別常拉多台機箱。')));
    box.append(pdrawer);
    // door: trigger (facet 3) — folded drawer; grouped by urgency; each row -> an organized brief
    const tdrawer=el('details',{class:'ldrawer'});
    tdrawer.append(el('summary',{},T('Trigger — a signal that starts a deal','觸發訊號 — 啟動一單的訊號')+' · '+(DATA.triggers.triggers||[]).length));
    const URG=[['critical',T('Critical','危急')],['high',T('High','高')],['medium',T('Medium','中')],['low',T('Low','低')]];
    const tlist=el('div',{class:'plist'});
    URG.forEach(([uk,ulab])=>{
      const ts=(DATA.triggers.triggers||[]).filter(t=>t.urgency===uk);if(!ts.length)return;
      tlist.append(el('div',{class:'pgrp u '+uk},ulab+' · '+ts.length));
      ts.forEach(t=>{const ids=(t.related_categories||[]);
        const pg=el('span',{class:'pgl',style:'display:flex;gap:var(--s1);justify-content:flex-end;align-items:baseline'});
        (t.related_plays||[]).forEach(pid=>{const L=pid.split('-')[1].toUpperCase();pg.append(el('span',{class:'play play'+L.toLowerCase()},'Play '+L));});
        const it=el('div',{class:'pitem'},el('span',{class:'u '+t.urgency,style:'font-weight:700'},'●'),el('span',{class:'pnm'},t.signal),pg,
          el('span',{class:'pct'},ids.length+T(' mkts ▸',' 市場 ▸')));
        it.onclick=()=>goTrigger(t);
        tlist.append(it);});
    });
    tdrawer.append(tlist);
    box.append(tdrawer);
    // door: play
    const prow=el('div',{class:'drow'});prow.append(el('span',{class:'dlab'},T('Play','打法')));
    DATA.plays.plays.forEach(p=>{const letter=p.id.split('-')[1].toUpperCase();const ids=cats.filter(c=>(c.plays||[]).includes(p.id)).map(c=>c.id);
      const chip=el('button',{class:'dchip'},el('span',{class:'play play'+letter.toLowerCase()},'Play '+letter),' '+p.name+' ',el('span',{class:'dn'},String(ids.length)));
      chip.onclick=()=>goPlay(p.id);prow.append(chip);});
    box.append(prow);
    // door: compute type (SKU) — the actionable "which SMCI box" cut (buyer axis carries ~no signal; this does).
    // Chip number = flagship (deal size) · direct-HOT (can we sell direct) — NOT raw category count, which
    // over-weights low-value buckets (saas-light 8, cpu-db 14 look big but carry ~no flagship deals).
    const crow=el('div',{class:'drow'});crow.append(el('span',{class:'dlab'},T('Compute (SKU)','計算(SKU)')));
    CC_ORDER.forEach(cc=>{const mem=cats.filter(c=>computeClassOf(c)===cc);if(!mem.length)return;
      const flag=mem.filter(c=>c.hardware_opportunity===4).length,
            hot=mem.filter(c=>(c.hardware_opportunity_by_buyer.customer||0)>=3).length;
      const chip=el('button',{class:'ccchip',title:ccGloss(cc)+' → '+ccSku(cc)+'  ·  '+mem.length+T(' categories',' 類')});
      chip.append(el('span',{class:'pill ccpill '+ccClass(cc)},ccLabel(cc)),
        el('span',{class:'dn'},String(flag)+' '+T('flagship','旗艦')+' · '+(LANG==='zh'?('直銷'+hot):(hot+' direct'))));
      chip.onclick=()=>window.exploreCompute(cc);crow.append(chip);});
    box.append(crow);
    box.append(el('div',{class:'muted',style:'font-size:var(--f-2);margin:2px 0 5px'},T('numbers = flagship deals (biggest SMCI box) · direct = the end org buys its own iron. Deliberately NOT category count — that over-weights low-value buckets.','數字 = 旗艦單(最大 SMCI 機箱)· 直銷 = 終端機構自購硬體。刻意不用類別數 — 類別數會高估低價值桶。')));
    // folded signal key — definitions preserved, no longer the dominant surface
    const key=el('details',{class:'hkey'});key.append(el('summary',{},T('What do flagship / customer-HOT / market-leader mean?','旗艦／客戶-HOT／市場領導者是什麼意思?')));
    [['g-flag',T('flagship','旗艦'),T('the biggest SMCI box the category pulls (opportunity 4/4) — how big the deal is.','該類別拉動的最大 SMCI 機箱(機會 4/4)— 單子多大。')],
     ['g-hot',T('customer-HOT','客戶-HOT'),T('the end org buys and runs its own iron — a direct sale (§3 gate = customer, ≥3).','終端機構自己買鐵、自建機房 — 直銷(§3 閘門=客戶,≥3)。')],
     ['g-lead',T('market leader','市場領導者'),T('the vendor is ranked on the AI / No-AI leaderboard — it already owns the account.','廠商在 AI／No-AI 榜有名次 — 已握有客戶。')]
    ].forEach(([cls,lab,def])=>key.append(el('div',{class:'krow'},el('span',{class:'kdot '+cls}),el('b',{},lab),el('span',{class:'muted'},' — '+def))));
    box.append(key);
    root.append(box);
  }
  let hotFilter=null, catFilter=null;
  function render(){
    const by=fBuyer.value,bk=fBucket.value,sp=fSpansBox.checked,seg2=fSeg.value,pl=fPlay.value,dep=fDep.value,
          hw=+fHw.value||0,prof=fProfile.value,cmp=fCompute.value,gp=fGroup.value,q=fTxt.value.toLowerCase();
    const shown=cats.filter(c=>{
      if(catFilter&&!catFilter.includes(c.id))return false;
      if(hotFilter&&(c.hardware_opportunity_by_buyer[hotFilter.buyer]||0)<hotFilter.min)return false;
      if(by&&!c.hardware_buyer.includes(by))return false;
      if(prof&&!(c.hardware_profile||[]).includes(prof))return false;
      if(cmp&&computeClassOf(c)!==cmp)return false;
      if(bk&&bucketOf(c)!==bk)return false;
      if(sp&&!spansOf(c))return false;
      if(seg2&&!(c.segments||[]).includes(seg2))return false;
      if(pl&&!(c.plays||[]).includes(pl))return false;
      if(dep&&!(c.deployment||[]).includes(dep))return false;
      if(hw&&c.hardware_opportunity<hw)return false;
      if(q&&!((c.name_en+' '+c.name_zh+' '+(c.infrastructure_notes||'')).toLowerCase().includes(q)))return false;
      return true;
    });
    clear(treePane);
    cnt.textContent=shown.length+' / '+cats.length+T(' shown',' 顯示')+(hotFilter?' · HOT_'+hotFilter.buyer:'');
    // auto-collapse groups when browsing many; keep open when narrowed, and always open the group holding the selected category
    const sel=(selected&&shown.find(c=>c.id===selected.id))||shown[0]||null;
    const openIf=list=>shown.length<=12||(sel&&list.indexOf(sel)>=0);
    if(gp==='stakeholder'){STAKE.forEach(([k,lab])=>{const li=shown.filter(c=>stakeKey(c)===k);l1node(lab,li,false,openIf(li));});}
    else if(gp==='ai'){l1node(T('AI-driven','AI 驅動'),shown.filter(isAI),true);l1node(T('No-AI','非 AI'),shown.filter(c=>!isAI(c)),true);}
    else if(!gp){l1node(T('All categories','全部類別'),shown);}
    else{
      const map=new Map();shown.forEach(c=>groupsOf(c,gp).forEach(k=>{if(!map.has(k))map.set(k,[]);map.get(k).push(c);}));
      let keys=[...map.keys()];
      if(gp==='hardware_opportunity')keys.sort((a,b)=>b-a);
      else if(gp==='play')keys.sort((a,b)=>((a==='(no play)')-(b==='(no play)'))||a.localeCompare(b));
      else if(gp==='compute')keys.sort((a,b)=>CC_ORDER.indexOf(a)-CC_ORDER.indexOf(b));
      else keys.sort((a,b)=>flagN(map.get(b))-flagN(map.get(a))||hotN(map.get(b))-hotN(map.get(a))||map.get(b).length-map.get(a).length);
      keys.forEach(k=>{const label=gp==='hardware_opportunity'?('opportunity '+k+' ('+OPP[k]+')'):(gp==='play'?playName(k):gp==='domain'?domLabel(k):gp==='compute'?ccLabel(k):k);l1node(label,map.get(k),false,openIf(map.get(k)));});
    }
    showDetail(sel);
  }
  [fBuyer,fBucket,fSeg,fPlay,fDep,fHw,fProfile,fCompute,fGroup].forEach(x=>x.onchange=()=>{hotFilter=null;catFilter=null;render();});
  window.exploreFilter=function(buyer,minOpp){hotFilter={buyer:buyer,min:minOpp||3};catFilter=null;
    [fBuyer,fBucket,fSeg,fPlay,fDep,fHw,fProfile,fCompute].forEach(x=>x.value='');fSpansBox.checked=false;fTxt.value='';
    fGroup.value='domain';[...seg.querySelectorAll('button')].forEach(b=>b.classList.toggle('on',b.dataset.g==='domain'));
    render();window.scrollTo(0,0);};
  // compute-type door: filter to a compute_class and regroup by play so the per-play split shows
  window.exploreCompute=function(cc){catFilter=null;hotFilter=null;
    [fBuyer,fBucket,fSeg,fPlay,fDep,fHw,fProfile].forEach(x=>x.value='');fSpansBox.checked=false;fTxt.value='';
    fCompute.value=cc;setGroup('play');window.scrollTo(0,0);};
  fSpansBox.onchange=()=>{hotFilter=null;catFilter=null;render();};fTxt.oninput=()=>{hotFilter=null;catFilter=null;render();};setGroup('domain');
}

// ================= VENDORS (enriched registry) =================
// ===== shared vendor filter model (drives both Registry and Bundle ranking) =====
const VF={region:'',state:'',fortune:'',cover:new Set(),share:'',listed:'',neuro:''};
function usStatesPresent(){const s=new Set();(DATA.vendors.vendors||[]).forEach(v=>{const p=hqParse(v);if(p.country==='USA'&&p.state)s.add(p.state);});return [...s].sort();}
function vfMatch(v){
  const p=hqParse(v);
  if(VF.region&&p.region!==VF.region)return false;
  if(VF.state&&p.state!==VF.state)return false;
  if(VF.fortune){const f=fortuneOf(v);
    if(VF.fortune==='any'){if(!f)return false;}
    else if(VF.fortune==='na'){if(f)return false;}
    else if(!f||f.list!==VF.fortune)return false;}
  if(VF.cover.size){const cov=new Set(coverageOf(v));let ok=false;VF.cover.forEach(k=>{if(cov.has(k))ok=true;});if(!ok)return false;}
  if(VF.share){const sh=usShareOf(v);if(VF.share==='has'){if(sh==null)return false;}else if(sh==null||sh<+VF.share)return false;}
  if(VF.listed){const l=listedOf(v);const s=l&&l.status;const pub=s==='public'||s==='subsidiary_of_public';const pri=s==='private'||s==='subsidiary_of_private';if(VF.listed==='public'&&!pub)return false;if(VF.listed==='private'&&!pri)return false;if(VF.listed==='other'&&(pub||pri))return false;}
  if(VF.neuro==='yes'&&!neuroOf(v))return false;
  return true;
}
function vfActive(){return VF.region||VF.state||VF.fortune||VF.cover.size||VF.share||VF.listed||VF.neuro;}
function renderFilterBar(host,onChange){
  const bar=el('div',{class:'filterbar'});
  const mk=(label,opts,cur,cb)=>{const sel=el('select',{class:'vfsel'});opts.forEach(([val,txt])=>{const o=el('option',{value:val},txt);if(val===cur)o.selected=true;sel.append(o);});sel.onchange=()=>cb(sel.value);return el('label',{class:'vflab'},el('span',{},label),sel);};
  bar.append(mk(T('Region (HQ)','地區(總部)'),[['',T('All','全部')]].concat(REGIONS.map(r=>[r,r])),VF.region,val=>{VF.region=val;if(val!=='North America')VF.state='';onChange();}));
  if(VF.region==='North America'){bar.append(mk(T('State','州'),[['',T('All states','全部州')]].concat(usStatesPresent().map(s=>[s,s])),VF.state,val=>{VF.state=val;onChange();}));}
  bar.append(mk('Fortune',[['',T('All','全部')],['fortune-500','Fortune 500'],['fortune-1000','Fortune 1000'],['global-500','Global 500'],['any',T('On any list','任一榜')],['na','N/A']],VF.fortune,val=>{VF.fortune=val;onChange();}));
  bar.append(mk(T('US market share','美國市佔'),[['',T('Any','不限')],['has',T('Has a figure','有數據')],['1','≥1%'],['5','≥5%'],['10','≥10%'],['25','≥25%']],VF.share,val=>{VF.share=val;onChange();}));
  bar.append(mk(T('Listing','上市/私有'),[['',T('All','全部')],['public',T('Public','上市')],['private',T('Private','私有')],['other',T('Other','其他')]],VF.listed,val=>{VF.listed=val;onChange();}));
  bar.append(mk(T('Neuro','神經'),[['',T('All','全部')],['yes',T('Neuro only','只神經')]],VF.neuro,val=>{VF.neuro=val;onChange();}));
  const clr=el('button',{class:'vfclear'},T('Clear','清除'));clr.onclick=()=>{VF.region='';VF.state='';VF.fortune='';VF.cover.clear();VF.share='';VF.listed='';VF.neuro='';onChange();};
  if(vfActive())bar.append(clr);
  const covwrap=el('div',{class:'covchips'});covwrap.append(el('span',{class:'vflab',style:'flex-direction:row;align-items:center'},el('span',{},T('Coverage','涵蓋'))));
  Object.keys(DOM_EN).forEach(k=>{const on=VF.cover.has(k);const c=el('span',{class:'covchip'+(on?' on':'')},domLabel(k));c.onclick=()=>{if(VF.cover.has(k))VF.cover.delete(k);else VF.cover.add(k);onChange();};covwrap.append(c);});
  host.append(bar,covwrap);
}
function renderRegistryInto(host){
  const root=host;
  const vsAll=(DATA.vendors.vendors||[]);
  const conf=(DATA.vendors.version)||'?';
  const cnt=el('span',{class:'count'});
  const q=el('input',{type:'search',placeholder:T('search vendor / HQ / leader / category...','搜尋廠商 / 總部 / 負責人 / 類別...')});
  root.append(el('div',{class:'rollup'},T('Vendor registry v'+conf+' — '+vsAll.length+' vendors, web-researched + adversarially verified. Filter by HQ region / state, Fortune standing, software coverage, US market share, public-listing status, or brain / neuro focus; sort by value = the vendors serving the most flagship / customer-HOT SMCI categories.','廠商登錄 v'+conf+' — '+vsAll.length+' 家,網路研究 + 對抗式查核。可依總部地區／州、Fortune 地位、軟體涵蓋、美國市佔、上市／私有、腦神經領域篩選;依價值排序 = 服務最多旗艦／客戶-HOT SMCI 類的廠商。')));
  let sortMode='value';
  function byValue(a,b){const A=vendorVal(a),B=vendorVal(b);return B.flag-A.flag||B.hot-A.hot||((LB_BY_VID[b.id]?1:0)-(LB_BY_VID[a.id]?1:0))||a.name.localeCompare(b.name);}
  const sseg=el('div',{class:'seg',style:'margin:0'});
  [['value',T('by value','依價值')],['az','A–Z']].forEach(([k,lab])=>{const b=el('button',{'data-k':k,class:k==='value'?'on':''},lab);b.onclick=()=>{sortMode=k;[...sseg.querySelectorAll('button')].forEach(x=>x.classList.toggle('on',x.dataset.k===k));render();};sseg.append(b);});
  const fbHost=el('div',{});root.append(fbHost);
  root.append(el('div',{class:'toolbar'},el('span',{class:'tagk'},T('sort','排序')),sseg,el('span',{style:'flex:1 1 20px'}),q,cnt));
  const vhost=el('div',{});root.append(vhost);
  function card(v){
    const c=el('div',{class:'card'});c.style.marginBottom='8px';
    const h=el('div',{class:'row'},el('h3',{style:'margin:0'},v.name));
    const bd=lbBadge(v.id);
    if(bd){const lp=el('span',{class:'pill',style:'cursor:pointer;background:var(--accentbg);color:var(--accent);font-weight:700'},bd);lp.title=T('on the market leaderboard — open','在市場榜單上 — 開啟');lp.onclick=()=>goVendorsBoard();h.append(lp);}
    valBadges(vendorVal(v),h);
    // Fortune + Listing shown once, in the kv rows below (with parent + ticker + evidence) — not also as head pills.
    const fo=fortuneOf(v);
    const us=usShareOf(v);if(us!=null){const up=el('span',{class:'pill uspill'},'US '+us+'%');if(v.us_share_basis)up.title=v.us_share_basis;h.append(up);}
    const lg=listedOf(v);
    if(neuroOf(v)){const np=el('span',{class:'pill neuropill'},T('Neuro','神經'));np.title=T('brain / neuro / stroke domain','腦 / 神經 / 中風領域');h.append(np);}
    if(/exclud/i.test(v.note||''))h.append(el('span',{class:'pill'},'§5.4 co-sell excluded'));
    c.append(h);
    const kv=el('dl',{class:'kv'});
    const add=(k,x)=>{if(x==null||x==='')return;kv.append(el('dt',{},k),el('dd',{},String(x)));};
    const p=hqParse(v);
    add(T('HQ','總部'),v.headquarters); add(T('Region','地區'),p.region+(p.state?' · '+p.state:'')); add(T('Founded','成立'),v.founded); add(T('Leadership','負責人'),v.leadership);
    add(T('Market position','市場地位'),v.market_position); add(T('Market share','市佔'),v.market_share);
    if(fo)add('Fortune',(FORT_LABEL[fo.list]+(fo.rank?' #'+fo.rank:''))+(fo.parent&&fo.parent!==v.name?' ('+fo.parent+')':''));
    if(lg)add(T('Listing','上市/私有'),listedLabel(lg)+(lg.ticker?' · '+lg.ticker:'')+(lg.parent?' ('+lg.parent+')':'')+' · '+T('evidence ','證據 ')+(lg.confidence||'?'));
    add(T('Deployment','部署'),(v.deployment_models||[]).join(', '));
    c.append(kv);
    const cov=coverageOf(v);if(cov.length){const cg=el('div',{class:'row'});cg.append(el('span',{class:'tagk'},T('coverage','涵蓋')));cov.forEach(k=>cg.append(el('span',{class:'gtag'},domLabel(k))));c.append(cg);}
    const seg=el('div',{class:'row'});(v.categories||[]).forEach(x=>{const cc=CATBYID[x];const ch=el('span',{class:'chip',style:'cursor:pointer'},cc?nm(cc):x);ch.title=T('view category','看類別');ch.onclick=()=>goCategory(x);seg.append(ch);});c.append(seg);
    if(v.history)c.append(el('div',{class:'notes'},v.history));
    const srcs=[...((v.sources&&v.sources.length)?v.sources:(v.source?[v.source]:[]))];
    if(lg&&lg.source&&/^https?:\/\//.test(lg.source)&&!srcs.includes(lg.source))srcs.push(lg.source);
    if(srcs.length){const sr=el('div',{class:'row'});sr.append(el('span',{class:'tagk'},T('sources','來源')));
      srcs.forEach(u=>{const isurl=/^https?:\/\//.test(u);
        sr.append(isurl?el('a',{href:u,target:'_blank',class:'pill'},u.replace(/^https?:\/\//,'').split('/')[0]):el('span',{class:'pill'},u.slice(0,40)));});
      c.append(sr);}
    return c;
  }
  function render(){
    const s=q.value.toLowerCase();
    const shown=vsAll.filter(vfMatch).filter(v=>!s||JSON.stringify([v.name,v.headquarters,v.leadership,v.market_position,v.market_share,(v.categories||[]).join(' ')]).toLowerCase().includes(s))
      .slice().sort(sortMode==='az'?(a,b)=>a.name.localeCompare(b.name):byValue);
    clear(vhost);shown.forEach(v=>vhost.append(card(v)));
    cnt.textContent=shown.length+' / '+vsAll.length+T(' shown',' 顯示');
  }
  function refresh(){clear(fbHost);renderFilterBar(fbHost,refresh);render();}
  q.oninput=render;refresh();
}
// ===== Bundle-fit ranking matrix — the promising-target ranking the filters drive =====
function renderBundleRankingInto(host){
  const root=host;
  root.append(el('div',{class:'rollup'},T('Bundle-fit ranking — which vendors are most promising to co-engineer a Supermicro hardware bundle with. Score 0-100 = hardware pull 35 (flagship/HOT categories — the anchor) + software coverage 20 + US market share 20 + Fortune standing 15 + US-region fit 10. Apply the filters above; the matrix re-ranks live.','捆綁契合排名 — 哪些廠商最值得與 Supermicro 共同設計硬體捆綁。分數 0-100 = 硬體拉動 35(旗艦/HOT 類別 — 核心)+ 軟體涵蓋 20 + 美國市佔 20 + Fortune 地位 15 + 美國地區契合 10。套用上方篩選,矩陣即時重排。')));
  const fbHost=el('div',{});root.append(fbHost);
  const cnt=el('span',{class:'count'});root.append(el('div',{class:'toolbar'},el('span',{class:'tagk'},T('ranked by bundle-fit score','依捆綁契合分數排名')),el('span',{style:'flex:1'}),cnt));
  const tblHost=el('div',{class:'wrap'});root.append(tblHost);
  function render(){
    const rows=(DATA.vendors.vendors||[]).filter(vfMatch).map(v=>({v,b:bundleScore(v)})).sort((a,b)=>b.b.score-a.b.score||b.b.val.flag-a.b.val.flag||a.v.name.localeCompare(b.v.name));
    clear(tblHost);
    const t=el('table',{class:'rankmatrix'});
    t.append(el('thead',{},el('tr',{},el('th',{},'#'),el('th',{},T('Vendor','廠商')),el('th',{},T('Bundle score','捆綁分數')),el('th',{},T('HW pull','硬體拉動')),el('th',{},T('Coverage','涵蓋')),el('th',{},T('US share','美國市佔')),el('th',{},'Fortune'),el('th',{},T('Region','地區')))));
    const tb=el('tbody');
    rows.forEach((r,i)=>{const b=r.b,v=r.v;
      const nm=el('span',{style:'cursor:pointer;font-weight:600;text-decoration:underline dotted var(--accent)'},v.name);nm.onclick=()=>goVendor(v.id);
      const vcell=el('td',{},nm);const bd=lbBadge(v.id);if(bd)vcell.append(el('span',{class:'pill',style:'margin-left:6px'},bd));
      // listing/neuro are filter axes, not bundleScore factors — not shown in the ranked row (leaderboard badge only)
      const bar=el('span',{class:'scbar'},el('span',{class:'scbarfill',style:'width:'+b.score+'%'}));
      const hwc=el('td',{});if(b.val.flag)hwc.append(el('span',{class:'vflag'},b.val.flag+' F'));if(b.val.hot)hwc.append(el('span',{class:'vhot'},b.val.hot+' HOT'));if(!b.val.flag&&!b.val.hot)hwc.append(el('span',{class:'muted'},'—'));
      const fo=b.fort;
      tb.append(el('tr',{},
        el('td',{class:'rnum'},String(i+1)),vcell,
        el('td',{},el('div',{class:'row',style:'gap:var(--s3)'},el('b',{style:'min-width:22px'},String(b.score)),bar)),
        hwc,
        el('td',{},String(b.cover.length)+'/8'),
        el('td',{},b.share!=null?('US '+b.share+'%'):el('span',{class:'muted'},'—')),
        el('td',{},fo?el('span',{class:'pill fortpill'},FORT_LABEL[fo.list]+(fo.rank?' #'+fo.rank:'')):el('span',{class:'muted'},'—')),
        el('td',{},b.region+(b.state?' · '+b.state:''))));
    });
    t.append(tb);tblHost.append(t);
    cnt.textContent=rows.length+T(' vendors ranked',' 家排名');
  }
  function refresh(){clear(fbHost);renderFilterBar(fbHost,refresh);render();}
  refresh();
}

// ================= PLAYS =================
function renderScoringInto(host){
  const root=host;
  root.append(el('h3',{},T('Model - ','評分模型 - ')+SC.items.reduce((s,i)=>s+i.weight,0)+T(' pts - ',' 分 - ')+SC.formula));
  const mt=el('table');mt.append(el('thead',{},el('tr',{},el('th',{},T('Item','項目')),el('th',{},T('Weight','權重')))));
  const mb=el('tbody');SC.items.forEach(i=>mb.append(el('tr',{},el('td',{},i.label),el('td',{},String(i.weight)))));
  mt.append(mb);root.append(el('div',{class:'wrap'},mt));
  const tr=el('div',{class:'row'});tr.style.margin='14px 0';
  TIERS.slice().reverse().forEach(t=>tr.append(el('span',{class:'tierbadge',style:'background:'+tierColor(t.name)},t.name+' >='+t.min)));
  root.append(el('div',{},el('div',{class:'tagk'},T('tiers','分級')),tr));
  root.append(el('h3',{},T('Try it','試算')));
  const wrap=el('div',{class:'card'});wrap.style.maxWidth='680px';
  const sg=el('div',{class:'scorer'});
  const out=el('div',{});
  const inputs={};
  SC.items.forEach(i=>{
    const r=el('input',{type:'range',min:'0',max:String(SMAX),value:'3',step:'1'});
    inputs[i.key]=r;const val=el('span',{},'3');
    r.oninput=()=>{val.textContent=r.value;calc();};
    sg.append(el('label',{},i.label+' ('+i.weight+')'),el('div',{},r,' ',val));
  });
  function calc(){
    const acc={scoring:{}};SC.items.forEach(i=>acc.scoring[i.key]=+inputs[i.key].value);
    const res=scoreAccount(acc);
    clear(out);
    out.append(el('div',{class:'bignum'},String(res.total)));
    out.append(el('div',{},el('span',{class:'tierbadge',style:'background:'+tierColor(res.tier.name)},res.tier.name)));
    out.append(el('div',{class:'muted',style:'margin-top:6px;font-size:var(--f-3)'},res.tier.action));
  }
  wrap.append(sg,el('hr',{style:'border:0;border-top:1px solid var(--line);margin:14px 0'}),out);
  root.append(wrap);calc();
}

// ================= ACCOUNTS =================
function subNav(root, items, defaultKey){
  const seg=el('div',{class:'seg',style:'margin:6px 0 14px'});
  const host=el('div',{});
  function pick(k){const it=items.find(i=>i[0]===k)||items[0];k=it[0];
    [...seg.querySelectorAll('button')].forEach(b=>b.classList.toggle('on',b.dataset.k===k));
    clear(host);it[2](host);}
  items.forEach(([k,lab])=>{const b=el('button',{'data-k':k},lab);b.onclick=()=>pick(k);seg.append(b);});
  root.append(seg,host);pick(defaultKey||items[0][0]);return {pick};
}
let _vendorsNav=null;
function renderMethod(){
  const root=$('#tab-method'); clear(root);
  root.append(el('h2',{style:'margin:2px 0 4px'},T('How to use this map','怎麼用這張地圖')));
  root.append(el('p',{class:'muted',style:'margin:0 0 8px;font-size:var(--f-4);max-width:820px;line-height:1.55'},
    T('We sell the hardware — but the buying decision starts one layer up, at the software. This map turns that into a repeatable flow: from the software universe, through a door, to a battle card, to the deal.',
      '我們賣硬體 —— 但採購決策在上一層,在軟體。這張地圖把它變成一條可複製的流程:從軟體宇宙,經一道門,到戰卡,到成交。')));
  const goExplore=(fn)=>{goTab('taxonomy');if(window._exp&&fn)fn(window._exp);};
  const sech=(t,sub)=>{const h=el('div',{class:'lsec'},t);if(sub)h.append(el('span',{class:'lsecsub'},'  '+sub));root.append(h);};
  const lbtn=(label,onclick)=>{const b=el('button',{class:'lbtn'},label);b.onclick=onclick;return b;};

  // ===== the system, one animated picture =====
  sech(T('The system','整套系統'),T('a hunt flows left → right','一次獵單由左 → 右'));
  const flow=el('div',{class:'sysflow'});
  const sdots=()=>{const d=el('div',{class:'sfdots'});
    [['g-flag',T('flagship','旗艦')],['g-hot',T('customer-HOT','客戶-HOT')],['g-lead',T('market leader','市場領導者')]]
      .forEach(([c,l])=>d.append(el('span',{class:'sfdot'},el('i',{class:'kdot '+c}),l)));return d;};
  const stage=(i,tag,title,rows,onclick)=>{const s=el('div',{class:'sfstage',style:'--i:'+i});
    if(onclick){s.style.cursor='pointer';s.onclick=onclick;}
    s.append(el('div',{class:'sftag'},tag),el('div',{class:'sftitle'},title));
    const b=el('div',{class:'sfbody'});rows.forEach(r=>b.append(typeof r==='string'?el('div',{class:'sfrow'},r):r));s.append(b);return s;};
  const arrow=(i)=>el('div',{class:'sfarrow',style:'--i:'+i},'→');
  flow.append(
    stage(0,T('① Universe','① 宇宙'),T('The software map','軟體地圖'),
      [DATA.taxonomy.categories.length+T(' software categories','個軟體類別'),sdots(),T('each → its SMCI box','每類 → 其 SMCI 機箱')],()=>goTab('taxonomy')),
    arrow(0),
    stage(1,T('② Door','② 門'),T('How you enter','怎麼進'),
      [T('search','搜尋'),T('product line','產品線'),T('trigger','觸發訊號'),T('play','打法')],()=>goTab('taxonomy')),
    arrow(1),
    stage(2,T('③ Battle card','③ 戰卡'),T('What to do','怎麼打'),
      [T('your motion','你的打法'),T('reference architecture','建議配置'),T('trigger to watch','盯的訊號'),T('market share','市佔率'),T('who to co-sell with','跟誰共銷')],()=>goExplore(e=>e.goCat('ehr-emr-core'))),
    arrow(2),
    stage(3,T('④ Deal','④ 成交'),T('The attach','拿下'),
      [T('SMCI hardware','SMCI 硬體'),T('+ co-sell partner','+ 共銷夥伴')]));
  root.append(flow);
  root.append(el('div',{class:'muted',style:'font-size:var(--f-2);margin:2px 0'},T('Click any stage to jump into it. The rest of this page unpacks each one.','點任一階段直接跳進去。下面逐一拆解。')));

  // ===== ① signals =====
  sech(T('① The three signals — on every category','① 三個訊號 —— 每個類別都有'));
  const leg=el('div',{class:'mlegend'});
  [['g-flag',T('flagship','旗艦'),T('The biggest SMCI box this category pulls (opportunity 4/4).  →  the biggest deals.','該類別拉動的最大 SMCI 機箱(機會 4/4)。 → 最大的單。')],
   ['g-hot',T('customer-HOT','客戶-HOT'),T('The end org buys and runs its own iron — a direct SMCI sale.  →  who you can sell to directly.','終端機構自己買鐵、自建機房 —— SMCI 直銷。 → 可以直接賣的對象。')],
   ['g-lead',T('market leader','市場領導者'),T('The vendor is ranked on the market leaderboard — it already owns the account.  →  who to co-sell through.','廠商在市場榜單有名次 —— 已握有客戶。 → 透過誰共銷。')]
  ].forEach(([cls,lab,def])=>{const c=el('div',{class:'mleg '+cls});c.append(el('div',{class:'lh'},el('span',{class:'llab'},lab)));c.append(el('div',{class:'ld'},def));leg.append(c);});
  root.append(leg);

  // ===== ② doors =====
  sech(T('② The four doors — when to use each','② 四道門 —— 何時用哪個'));
  const dg=el('div',{class:'ldoors'});
  [[T('Search','搜尋'),T('You have a name in mind — a category, a vendor, or an SMCI box.','心裡有個名字 —— 類別、廠商、或 SMCI 硬體。')],
   [T('Product line','產品線'),T('You sell a specific box (GPU, NVMe, archive, edge) and want its whole pipeline.','你賣某一款機箱(GPU、NVMe、封存、邊緣),想看它整條管線。')],
   [T('Trigger','觸發訊號'),T('Something happened — an FDA filing, a ransomware hit, an EHR go-live.','發生了某件事 —— FDA 申報、勒索軟體、EHR 上線。')],
   [T('Play','打法'),T('You are running one of the four hardware bets.','你正在跑四個硬體賭注之一。')]
  ].forEach(([n,w])=>dg.append(el('div',{class:'ldoor'},el('b',{},n),el('span',{class:'muted'},w))));
  root.append(dg);
  root.append(lbtn(T('Open Explore →','開啟 Explore →'),()=>goTab('taxonomy')));

  // ===== ③ walkthrough =====
  sech(T('③ Watch one flow through','③ 看一次完整流程'));
  const ol=el('ol',{class:'lsteps'});
  [T('A hospital just disclosed a ransomware incident.','某醫院剛揭露勒索軟體事件。'),
   T('Open the “Cyber incident / ransomware” trigger — the brief shows the 7 markets it opens and the move: immutable / air-gapped backup.','開「Cyber incident／ransomware」觸發 —— 簡報顯示它開的 7 個市場,以及動作:不可變／氣隙備份。'),
   T('Click the EHR / EMR market → its battle card.','點 EHR／EMR 市場 → 它的戰卡。'),
   T('The card gives you: your motion (direct sale), the reference architecture (NVMe + HA + DR, zero GPU), and who already runs there.','戰卡給你:打法(直銷)、建議配置(NVMe + HA + DR,零 GPU)、以及誰已跑在那。'),
   T('That is the deal — the resilience iron under the EHR, funded by the breach budget.','這就是那張單 —— EHR 底下的韌性硬體,用資安預算買。')
  ].forEach(s=>ol.append(el('li',{},s)));
  root.append(ol);
  root.append(lbtn(T('Try it live →','實際走一遍 →'),()=>goExplore(e=>e.goTrigger(DATA.triggers.triggers.find(t=>t.id==='cyber-incident')))));

  // ===== ④ the four bets =====
  sech(T('④ The four bets — click to open','④ 四個賭注 —— 點開'));
  const pg=el('div',{class:'lplays'});
  DATA.plays.plays.forEach(p=>{const L=p.id.split('-')[1].toUpperCase();const n=DATA.taxonomy.categories.filter(c=>(c.plays||[]).includes(p.id)).length;
    const row=el('div',{class:'lplay'},el('span',{class:'play play'+L.toLowerCase()},'Play '+L),el('b',{},p.name),el('span',{class:'muted',style:'flex:1'},' — '+(p.hardware_anchor||[]).slice(0,2).join(' · ')),el('span',{class:'lpct'},n+T(' categories','類')));
    row.onclick=()=>goExplore(e=>e.goPlay(p.id));pg.append(row);});
  root.append(pg);

  // ===== folded: prioritize (scoring) =====
  const d=el('details',{class:'hkey',style:'margin-top:18px'});
  d.append(el('summary',{},T('Advanced — how an account gets prioritized (scoring)','進階 —— 帳號怎麼排優先序(評分)')));
  const sc=el('div',{style:'padding-top:8px'});
  sc.append(el('p',{class:'muted',style:'font-size:var(--f-3);max-width:740px;line-height:1.5'},
    T('When you do work a specific account, rank it on two things: how BIG the hardware deal is, and how WINNABLE it is (does the customer control the iron, is there a refresh trigger, is it repeatable across sites…). 100 points; ≥70 = pursue now. Try the sliders:',
      '當你真的去攻一個帳號,用兩件事排序:硬體單有多大、以及多好贏(客戶是否掌控硬體、有沒有換機觸發、能不能跨點複製…)。滿分 100;≥70 = 現在追。拉拉看:')));
  renderScoringInto(sc);
  d.append(sc);root.append(d);
}
function renderLeaderboardsInto(host){
  const root=host;
  const LB=DATA.leaderboards&&DATA.leaderboards.leaderboards;
  if(!LB){root.append(el('div',{class:'muted'},T('No leaderboards data.','無榜單資料。')));return;}
  root.append(el('div',{class:'rollup'},T('Market vendor leaderboards — ranked by market share / installed base. Every entry §8-sourced (a real figure or a sourced market position); grouped by sub-market. A vendor that plays both sides (e.g. GE, Philips) appears on both boards.','市場廠商榜 — 按市佔／裝機量排名。每一項 §8 有來源(真數字或有來源的市場地位),依次級市場分組。雙棲廠商(如 GE、Philips)兩榜都上。')));
  const wrap=el('div',{class:'grid',style:'grid-template-columns:repeat(auto-fill,minmax(min(430px,100%),1fr))'});
  [['ai',LB.ai],['no_ai',LB.no_ai]].forEach(([key,board])=>{
    if(!board)return;
    const col=el('div',{class:'card'});
    col.append(el('h3',{style:'margin-bottom:6px'},(LANG==='zh'?board.label_zh:board.label_en)+' · '+board.count));
    let curSeg=null;
    (board.entries||[]).forEach(e=>{
      if(e.segment!==curSeg){curSeg=e.segment;
        col.append(el('div',{class:'tagk',style:'display:block;margin:12px 0 2px'},(LANG==='zh'?e.segment_zh:e.segment)));}
      const row=el('div',{style:'padding:var(--s2) 0;border-top:1px solid var(--line)'});
      const nmEl=el('span',{style:'font-weight:600'+(e.vendor_id?';cursor:pointer;text-decoration:underline dotted var(--accent)':'')},e.name+(e.vendor_id?' ↩':''));
      if(e.vendor_id){nmEl.title=T('in the registry — view vendor card','在登錄中 — 看廠商卡');nmEl.onclick=()=>goVendor(e.vendor_id);}
      const rowline=el('div',{class:'row'},el('b',{style:'color:var(--accent);min-width:34px'},'#'+e.rank),nmEl);
      if(e.vendor_id&&VBYID[e.vendor_id])valBadges(vendorVal(VBYID[e.vendor_id]),rowline);
      row.append(rowline);
      row.append(el('div',{class:'muted',style:'font-size:var(--f-2);margin:3px 0'},e.market_basis));
      if(e.source){const isurl=/^https?:\/\//.test(e.source);
        row.append(isurl?el('a',{href:e.source,target:'_blank',class:'pill'},T('source','來源')+' ↗'):el('span',{class:'pill'},String(e.source).slice(0,60)));}
      col.append(row);
    });
    wrap.append(col);
  });
  root.append(wrap);
}
function renderVendors(){
  const root=$('#tab-vendors'); clear(root);
  root.append(el('h2',{style:'margin:2px 0 8px'},T('Market players — vendors & leaders','市場玩家 — 廠商與領導者')));
  _vendorsNav=subNav(root,[
    ['registry',T('Registry','登錄')+' ('+(DATA.vendors.vendors||[]).length+')',renderRegistryInto],
    ['ranking',T('Bundle ranking','捆綁排名'),renderBundleRankingInto],
    ['leaderboards',T('Leaderboards','榜單'),renderLeaderboardsInto]],'registry');
}
function goVendorsBoard(){goTab('vendors');if(_vendorsNav)_vendorsNav.pick('leaderboards');}

// ================= i18n wiring: render all tabs + language toggle =================
const TAB_ZH={taxonomy:'探索',method:'方法',vendors:'廠商'};
function relabelTabs(){TABS.forEach(([id,label])=>{if(NAVBTN[id])NAVBTN[id].textContent=LANG==='zh'?(TAB_ZH[id]||label):label;});}
function renderAll(){setBuilt();renderTaxonomy();renderMethod();renderVendors();}
renderAll();
$('#langtog').onclick=()=>{LANG=(LANG==='zh')?'en':'zh';$('#langtog').textContent=(LANG==='zh')?'EN':'中文';relabelTabs();renderAll();window.scrollTo(0,0);};
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()

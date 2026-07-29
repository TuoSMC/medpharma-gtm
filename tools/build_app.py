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
    print(f"OK: wrote {OUT}")
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
  --bg:#f6f7f9; --panel:#fff; --ink:#1a1d21; --muted:#5b6470; --line:#e3e6ea;
  --accent:#0b6bcb; --accentbg:#e7f0fb;
  --hw1:#9aa4b2; --hw2:#5b8def; --hw3:#f0993e; --hw4:#e0464b;
  --u-crit:#e0464b; --u-high:#f0993e; --u-med:#d9a91f; --u-low:#7a8794;
  --a:#1f9d57; --b:#7a5cd0; --c:#c2560c; --d:#0e8a94;
}
@media (prefers-color-scheme:dark){
  :root{--bg:#14171b;--panel:#1c2026;--ink:#e6e9ee;--muted:#98a2b0;--line:#2b313a;
        --accent:#5aa2f0;--accentbg:#182636;}
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang TC","Microsoft JhengHei",sans-serif}
header{padding:18px 22px;border-bottom:1px solid var(--line);background:var(--panel);position:sticky;top:0;z-index:5}
h1{margin:0;font-size:17px;letter-spacing:.2px}
.sub{color:var(--muted);font-size:12px;margin-top:3px}
nav{display:flex;gap:4px;flex-wrap:wrap;padding:10px 22px 0;background:var(--panel);border-bottom:1px solid var(--line);position:sticky;top:61px;z-index:5}
nav button{border:0;background:transparent;color:var(--muted);font:inherit;font-weight:600;
  padding:9px 14px;border-radius:8px 8px 0 0;cursor:pointer;border-bottom:2px solid transparent}
nav button.on{color:var(--accent);border-bottom-color:var(--accent);background:var(--accentbg)}
main{max-width:1180px;margin:0 auto;padding:20px 22px 60px}
.tab{display:none}.tab.on{display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 15px}
.card h3{margin:0 0 2px;font-size:14px}
.zh{color:var(--muted);font-size:12px;margin-bottom:8px}
.row{display:flex;flex-wrap:wrap;gap:5px;margin:5px 0}
.chip{font-size:11px;padding:2px 8px;border-radius:20px;background:var(--accentbg);color:var(--accent);white-space:nowrap}
.chip.dim{background:transparent;border:1px solid var(--line);color:var(--muted)}
.hwc{font-size:10px;padding:1px 7px;border-radius:6px;background:var(--accentbg);color:var(--accent);font-weight:600;white-space:nowrap}
.tagk{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-right:4px;align-self:center}
.hw{display:inline-block;min-width:20px;text-align:center;font-weight:700;color:#fff;border-radius:6px;padding:1px 7px;font-size:11px}
.hw1{background:var(--hw1)}.hw2{background:var(--hw2)}.hw3{background:var(--hw3)}.hw4{background:var(--hw4)}
.bkt{font-size:10px;font-weight:700;padding:1px 7px;border-radius:6px;text-transform:uppercase;letter-spacing:.4px}
.bon{background:var(--a);color:#fff}
.bcl{background:transparent;border:1px solid var(--line);color:var(--muted)}
.by{font-size:10px;font-weight:700;padding:1px 7px;border-radius:6px;color:#fff;text-transform:uppercase;letter-spacing:.3px}
.bcust{background:var(--a)}.boper{background:var(--b)}.boem{background:var(--c)}.bhyp{background:var(--hw1)}
.byo{font-size:10px;padding:1px 6px;border-radius:20px;border:1px solid var(--line);color:var(--muted)}
.rollup{font-size:12px;margin:-6px 0 12px;color:var(--muted)}
.rollup b{color:var(--ink)}
.ckbox{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:var(--muted);border:1px solid var(--line);border-radius:8px;padding:6px 9px}
.grouphdr{font-size:13px;font-weight:700;margin:18px 0 8px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--line);padding-bottom:6px}
.subhdr{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);margin:10px 0 6px}
.backbtn{position:sticky;top:64px;z-index:6;align-items:center;gap:4px;font-family:inherit;font-size:12px;font-weight:600;color:var(--accent);background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:5px 11px;cursor:pointer;margin:2px 0 6px}
.backbtn:hover{border-color:var(--accent);background:var(--accentbg)}
.twopane{display:grid;grid-template-columns:minmax(300px,5fr) 7fr;gap:18px;align-items:start;margin-top:6px}
@media(max-width:840px){.twopane{grid-template-columns:1fr}}
.tree{font-size:13px;min-width:0}
.detail{position:sticky;top:118px}
@media(max-width:840px){.detail{position:static}}
.tnode{display:flex;align-items:center;gap:7px;font-weight:700;cursor:pointer;padding:8px 0 6px;border-bottom:1px solid var(--line);margin-top:10px}
.tnode .tcar{color:var(--accent);font-size:10px;width:10px}
.tnode .tcount{color:var(--muted);font-weight:600;font-size:12px}
.tnode .tflag{font-size:10px;font-weight:700;color:var(--hw4);border:1px solid var(--hw4);border-radius:10px;padding:0 6px}
.tnode .thot{font-size:10px;font-weight:700;color:var(--a);border:1px solid var(--a);border-radius:10px;padding:0 6px}
.vflag{font-size:10px;font-weight:700;color:var(--hw4);border:1px solid var(--hw4);border-radius:10px;padding:0 6px}
.vhot{font-size:10px;font-weight:700;color:var(--a);border:1px solid var(--a);border-radius:10px;padding:0 6px}
.master{border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin:4px 0 16px;background:var(--panel)}
.master h3{font-size:15px}
.mkpi{display:flex;flex-wrap:wrap;gap:20px;margin:8px 0 6px}
.mk{display:flex;flex-direction:column;line-height:1.05}
.mk b{font-size:24px}.mk span{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.3px}
.mk.k-flag b{color:var(--hw4)}.mk.k-hot b{color:var(--a)}.mk.k-lead b{color:var(--accent)}
.msec{margin:4px 0 0;border-top:1px solid var(--line);padding-top:4px}
.msec>summary{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);cursor:pointer;list-style:none;padding:5px 0}
.msec>summary::-webkit-details-marker{display:none}
.msec>summary::before{content:"\25be  ";color:var(--accent)}
.msec:not([open])>summary::before{content:"\25b8  "}
.mrow{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px;padding:5px 6px;border-radius:7px;font-size:13px}
.mrow:hover{background:var(--accentbg)}
.mlabel{flex:1 1 200px;min-width:150px;overflow-wrap:anywhere;font-weight:600}
.mbadges{display:flex;gap:5px;flex:0 0 auto}
.mtop{display:flex;flex-wrap:wrap;gap:4px;justify-content:flex-end;flex:1 1 220px}
/* legend: defines + links the 3 signals (count lives here too) */
.mlegend{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:10px 0 8px}
@media(max-width:760px){.mlegend{grid-template-columns:1fr}}
.mleg{border:1px solid var(--line);border-left-width:3px;border-radius:9px;padding:9px 11px;background:var(--bg)}
.mleg.g-flag{border-left-color:var(--hw4)}.mleg.g-hot{border-left-color:var(--a)}.mleg.g-lead{border-left-color:var(--accent)}
.mleg .lh{display:flex;align-items:baseline;gap:8px}
.mleg .ln{font-size:23px;font-weight:800;line-height:1}
.mleg.g-flag .ln{color:var(--hw4)}.mleg.g-hot .ln{color:var(--a)}.mleg.g-lead .ln{color:var(--accent)}
.mleg .llab{font-weight:700;font-size:13px}
.mleg .lv{margin-left:auto;font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);border:1px solid var(--line);border-radius:20px;padding:1px 7px;white-space:nowrap}
.mleg .ld{font-size:11.5px;color:var(--muted);margin-top:5px;line-height:1.4}
.mleg .lq{font-size:11.5px;font-weight:600;margin-top:4px}
.mleg.g-flag .lq{color:var(--hw4)}.mleg.g-hot .lq{color:var(--a)}.mleg.g-lead .lq{color:var(--accent)}
.mpath{font-size:12px;color:var(--muted);background:var(--accentbg);border-radius:9px;padding:8px 11px;margin:0 0 6px;line-height:1.5}
.mpath b{color:var(--ink)}
/* pipeline: aligned opportunity matrix per play */
.play-h{display:flex;align-items:baseline;gap:10px;margin:14px 0 5px;flex-wrap:wrap}
.play-h .pl{font-weight:700;font-size:13.5px}
.play-h .ps{font-size:11px;color:var(--muted)}
.ptbl{display:grid;grid-template-columns:minmax(150px,1.25fr) minmax(170px,2fr) auto;border:1px solid var(--line);border-radius:9px;overflow:hidden}
.ptbl .ph{font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);background:var(--panel);padding:6px 10px;border-bottom:1px solid var(--line)}
.ptbl .pc{padding:8px 10px;border-bottom:1px solid var(--line);font-size:12.5px;display:flex;align-items:center;gap:6px;flex-wrap:wrap;min-width:0}
.ptbl .pc.last{border-bottom:none}
.pcat{font-weight:600;cursor:pointer;overflow-wrap:anywhere}
.pcat:hover{color:var(--accent)}
.pc .cb{font-size:9px;font-weight:700;border-radius:9px;padding:0 5px;white-space:nowrap;text-transform:uppercase;letter-spacing:.3px}
.pc .cb.f{color:var(--hw4);border:1px solid var(--hw4)}.pc .cb.h{color:var(--a);border:1px solid var(--a)}
.pven{color:var(--muted);overflow-wrap:anywhere}.pven b{color:var(--ink);font-weight:600}
.prank{justify-content:flex-end;text-align:right}
.prank .rb{font-size:10px;font-weight:700;color:var(--accent);border:1px solid var(--accent);border-radius:10px;padding:0 6px;white-space:nowrap}
.prank .rn{font-size:10px;color:var(--muted);white-space:nowrap}
.tbody{padding-left:2px}
.tsub{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);margin:8px 0 3px}
.trow{display:flex;align-items:center;gap:8px;padding:4px 7px;border-radius:6px;cursor:pointer}
.trow:hover{background:var(--accentbg)}
.trow.sel{background:var(--accentbg);box-shadow:inset 3px 0 0 var(--accent)}
.trow .tname{flex:1;min-width:0;overflow-wrap:anywhere}
.trow .tby{width:9px;height:9px;border-radius:50%;flex:0 0 auto}
.tby.bcust{background:var(--a)}.tby.boper{background:var(--b)}.tby.boem{background:var(--c)}.tby.bhyp{background:var(--muted)}
.tiers6{margin:12px 0}
.tier6{display:grid;grid-template-columns:92px 1fr;gap:10px;padding:8px 0 8px 14px;position:relative;border-left:2px solid var(--line)}
.tier6:before{content:"";position:absolute;left:-5px;top:15px;width:8px;height:8px;border-radius:50%;background:var(--accent)}
.tier6 .tlab{font-size:11px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.3px;padding-top:2px}
.tier6 .tcont{font-size:13px;display:flex;flex-wrap:wrap;gap:5px;align-items:center}
.flowstrip{display:flex;flex-wrap:wrap;align-items:center;gap:4px}
.fbox{border:1px solid var(--accent);color:var(--accent);border-radius:6px;padding:2px 8px;font-size:12px;background:var(--accentbg)}
.farrow{color:var(--muted);font-weight:700}
.dsec{margin:14px 0}
.dsec .dsh{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);margin-bottom:4px}
/* battle card: the actionable sell layer at the top of a category */
.battle{border:1px solid var(--line);border-radius:9px;background:var(--accentbg);padding:8px 11px;margin:8px 0 4px}
.brow{display:grid;grid-template-columns:108px 1fr;gap:10px;align-items:baseline;padding:4px 0}
.brow+.brow{border-top:1px solid var(--line)}
.blab{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.3px;color:var(--muted)}
.bval{font-size:12.5px;line-height:1.45}
.rarch{display:flex;flex-wrap:wrap;gap:5px}
.raxx{font-size:11px;font-weight:600;color:var(--accent);border:1px solid var(--accent);border-radius:8px;padding:1px 7px}
.twrow{display:flex;flex-wrap:wrap;gap:4px 7px;align-items:baseline;padding:2px 0}
.twrow .tsig{font-weight:600}
.twrow .tact{color:var(--muted);font-size:11.5px}
/* hunt launcher: the 4 doors into the battle card */
.launch{border:1px solid var(--line);border-radius:12px;padding:12px 14px;margin:4px 0 16px;background:var(--panel)}
.launch h3{font-size:15px}
.hsearch{width:100%;padding:9px 12px;border:1px solid var(--line);border-radius:9px;background:var(--bg);color:var(--ink);font-size:13px;margin:2px 0 8px;font-family:inherit}
.hsearch:focus{outline:none;border-color:var(--accent)}
.hnote{font-size:12px;color:var(--muted);margin:0 0 8px;background:var(--accentbg);border-radius:8px;padding:7px 10px;line-height:1.45}
.hnote:empty{display:none}
.hnote b{color:var(--ink)}
.drow{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:7px 0}
.dlab{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.3px;color:var(--muted);width:92px;flex:0 0 auto}
.dchip{display:inline-flex;align-items:center;gap:5px;font-size:12px;border:1px solid var(--line);border-radius:20px;padding:4px 10px;background:var(--bg);color:var(--ink);cursor:pointer;font-family:inherit}
.dchip:hover{border-color:var(--accent);background:var(--accentbg)}
.dchip .dn{font-size:10px;color:var(--muted);font-weight:700}
.hkey{margin-top:8px;border-top:1px solid var(--line);padding-top:6px}
.hkey>summary{font-size:11px;font-weight:700;color:var(--muted);cursor:pointer;list-style:none}
.hkey>summary::-webkit-details-marker{display:none}
.hkey>summary::before{content:"\25b8 ";color:var(--accent)}
.hkey[open]>summary::before{content:"\25be "}
.krow{font-size:12px;margin:5px 0;display:flex;align-items:baseline;gap:7px;flex-wrap:wrap}
.kdot{width:9px;height:9px;border-radius:3px;flex:0 0 auto;position:relative;top:1px}
.kdot.g-flag{background:var(--hw4)}.kdot.g-hot{background:var(--a)}.kdot.g-lead{background:var(--accent)}
.dhdr{font-size:11px;font-weight:700;color:var(--muted);margin:9px 0 1px}
.plist{display:flex;flex-direction:column;gap:1px;margin:1px 0 2px}
.pgrp{font-size:9.5px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--accent);margin:7px 0 1px}
.pitem{display:flex;align-items:baseline;gap:8px;padding:4px 8px;border-radius:7px;cursor:pointer}
.pitem:hover{background:var(--accentbg)}
.pitem .pnm{font-weight:600;font-size:12.5px;flex:0 0 auto}
.pitem .pgl{color:var(--muted);font-size:11.5px;flex:1;min-width:0}
.pitem .pct{font-weight:700;color:var(--muted);font-size:11px;flex:0 0 auto;white-space:nowrap}
.mklist{display:flex;flex-direction:column;gap:3px;margin-top:5px}
.mkitem{display:flex;align-items:center;gap:7px;padding:6px 8px;border:1px solid var(--line);border-radius:8px;cursor:pointer;font-size:12.5px}
.mkitem:hover{background:var(--accentbg);border-color:var(--accent)}
.mkitem .mknm{flex:1;font-weight:600;overflow-wrap:anywhere}
/* vendors-in-market drawer with cited market-share bars */
.vdrawer{margin-top:12px;border-top:1px solid var(--line);padding-top:6px}
.vdrawer>summary{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.4px;color:var(--muted);cursor:pointer;list-style:none;padding:3px 0}
.vdrawer>summary::-webkit-details-marker{display:none}
.vdrawer>summary::before{content:"\25b8  ";color:var(--accent)}
.vdrawer[open]>summary::before{content:"\25be  "}
.vsbody{margin-top:6px}
/* fixed track column so every bar shares one scale (comparable market share) */
.msrow{display:grid;grid-template-columns:minmax(120px,1fr) clamp(90px,18vw,150px) 46px;gap:10px;align-items:center;padding:3px 2px;font-size:12.5px}
.msn{display:flex;flex-wrap:wrap;align-items:baseline;gap:5px;min-width:0}
.msn .vn{font-weight:600;cursor:pointer;overflow-wrap:anywhere}
.msn .vn:hover{color:var(--accent)}
.msrk{font-size:9px;font-weight:700;color:var(--accent);border:1px solid var(--accent);border-radius:9px;padding:0 5px;white-space:nowrap}
.mstrack{height:9px;width:100%;background:var(--line);border-radius:5px;overflow:hidden}
.mstrack.empty{background:transparent}
.msfill{height:100%;background:var(--accent);border-radius:5px}
.msp{text-align:right;font-weight:700;font-size:11px}
.msund{text-align:right;font-size:10px;color:var(--muted)}
.dstep{display:flex;gap:8px;margin:3px 0;font-size:13px}
.dstep b{color:var(--accent);flex:0 0 auto}
.gcount{font-size:11px;font-weight:600;color:var(--muted);background:var(--accentbg);border-radius:20px;padding:1px 8px}
.play{font-size:11px;font-weight:700;padding:2px 8px;border-radius:6px;color:#fff}
.playa{background:var(--a)}.playb{background:var(--b)}.playc{background:var(--c)}.playd{background:var(--d)}
.notes{color:var(--muted);font-size:12px;margin-top:8px;border-top:1px dashed var(--line);padding-top:8px}
.filters{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:14px}
.filters select,.filters input{font:inherit;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:var(--panel);color:var(--ink)}
.count{color:var(--muted);font-size:12px;margin-left:auto}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top;font-size:13px}
th{background:var(--accentbg);color:var(--accent);font-size:11px;text-transform:uppercase;letter-spacing:.5px;position:sticky;top:112px}
tr:last-child td{border-bottom:0}
.u{font-weight:700;font-size:11px;text-transform:uppercase}
.u.critical{color:var(--u-crit)}.u.high{color:var(--u-high)}.u.medium{color:var(--u-med)}.u.low{color:var(--u-low)}
.wrap{overflow-x:auto}
.scorer{display:grid;grid-template-columns:1fr auto;gap:8px 14px;align-items:center;max-width:560px}
.scorer label{font-size:13px}
.scorer input[type=range]{width:100%}
.bignum{font-size:40px;font-weight:800;line-height:1}
.tierbadge{display:inline-block;padding:4px 12px;border-radius:8px;font-weight:700;color:#fff}
.mini{height:6px;border-radius:4px;background:var(--line);overflow:hidden;margin-top:4px}
.mini>i{display:block;height:100%}
.kv{display:grid;grid-template-columns:130px 1fr;gap:2px 10px;font-size:12px}
.kv dt{color:var(--muted)}
.muted{color:var(--muted)}
.pill{font-size:11px;border:1px solid var(--line);border-radius:20px;padding:1px 9px;color:var(--muted)}
.pill.lead{border-color:var(--accent);color:var(--accent);font-weight:600}
.hero{padding:6px 0 16px}
.hero h2{margin:0 0 4px;font-size:22px;letter-spacing:.2px}
.hero p{margin:0;color:var(--muted);font-size:13px;max-width:760px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;margin:14px 0}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;cursor:pointer;transition:border-color .12s,transform .12s}
.tile:hover{border-color:var(--accent);transform:translateY(-2px)}
.tile h3{margin:0 0 2px;font-size:15px}
.tile .anchor{color:var(--muted);font-size:11px;margin-bottom:10px}
.tile .cat{display:flex;align-items:baseline;justify-content:space-between;gap:8px;font-size:12px;padding:4px 0;border-top:1px dashed var(--line)}
.tile .cat span{min-width:0;overflow-wrap:anywhere}
.tile .cat b{color:var(--ink);flex:0 0 auto;white-space:nowrap}
.tile .go{margin-top:10px;color:var(--accent);font-weight:600;font-size:12px}
.statbar{display:flex;flex-wrap:wrap;gap:10px;margin:6px 0 4px}
.stat{flex:1;min-width:150px;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:12px 14px;cursor:pointer}
.stat:hover{border-color:var(--accent)}
.stat .n{font-size:26px;font-weight:800;line-height:1}
.stat .l{color:var(--muted);font-size:11px;margin-top:2px}
.trigrow{display:flex;gap:8px;align-items:baseline;font-size:12px;padding:5px 0;border-top:1px dashed var(--line)}
.refine>summary{cursor:pointer;font-weight:600;font-size:12px;color:var(--muted);padding:6px 0;list-style:none}
.refine>summary::-webkit-details-marker{display:none}
.refine>summary::before{content:"\25B8 ";color:var(--accent)}
.refine[open]>summary::before{content:"\25BE "}
.section-title{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--muted);margin:20px 0 8px}
.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:4px 0 8px}
.seg{display:inline-flex;flex-wrap:wrap;border:1px solid var(--line);border-radius:9px;overflow:hidden}
.seg button{border:0;border-right:1px solid var(--line);background:var(--panel);color:var(--muted);font:inherit;font-size:12px;font-weight:600;padding:7px 13px;cursor:pointer}
.seg button:last-child{border-right:0}
.seg button.on{background:var(--accent);color:#fff}
.seg button:hover:not(.on){background:var(--accentbg);color:var(--accent)}
.jump{display:flex;flex-wrap:wrap;align-items:center;gap:7px;font-size:12px;color:var(--muted);margin-bottom:10px}
.jbtn{border:1px solid var(--line);background:var(--panel);color:var(--ink);font:inherit;font-size:12px;padding:5px 11px;border-radius:15px;cursor:pointer;display:inline-flex;gap:5px;align-items:center}
.jbtn b{font-size:13px}
.jbtn:hover{border-color:var(--accent);background:var(--accentbg)}
.jbtn.sc-cust b{color:var(--a)}.jbtn.sc-oper b{color:var(--b)}.jbtn.sc-oem b{color:var(--c)}
.flab{display:flex;flex-direction:column;gap:2px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.4px}
.flab>select,.flab>input{margin:0}
#fTxt{min-width:170px}
</style>
</head>
<body>
<header>
  <button id="langtog" style="position:absolute;top:14px;right:16px;padding:5px 12px;border:1px solid var(--line);border-radius:14px;background:var(--card);color:var(--fg);font-size:13px;font-weight:700;cursor:pointer">中文</button>
  <h1>SMCI Medical / Pharma GTM Playbook <span class="pill" id="ver"></span></h1>
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

// ---- header ----
$('#ver').textContent='taxonomy v'+DATA.taxonomy.version+' · '+DATA.taxonomy.status;
function setBuilt(){const cats=DATA.taxonomy.categories;const nv=(DATA.vendors.vendors||[]).length;
  $('#built').textContent=cats.length+T(' software categories · ',' 軟體類別 · ')+nv+T(' vendors mapped to the Supermicro hardware behind them',' 家廠商對應其背後的 Supermicro 硬體');}
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
        fGroup={value:''},
        fSpansBox=el('input',{type:'checkbox'}),
        fTxt=el('input',{id:'fTxt',type:'search',placeholder:'search name / notes...'}),
        cnt=el('span',{class:'count'});
  const fSpans=el('label',{class:'ckbox'},fSpansBox,T('spans on-prem↔cloud','橫跨 on-prem↔雲'));
  const hotC=cats.filter(c=>(c.hardware_opportunity_by_buyer.customer||0)>=3).length,
        hotO=cats.filter(c=>(c.hardware_opportunity_by_buyer.operator||0)>=3).length,
        nOem=cats.filter(c=>(c.hardware_opportunity_by_buyer['original-equipment-manufacturer']||0)>=3).length;
  const resetSel=()=>{[fBuyer,fBucket,fSeg,fPlay,fDep,fHw,fProfile].forEach(x=>x.value='');fSpansBox.checked=false;fTxt.value='';};
  // ---- toolbar: one segmented control to regroup all categories, + search ----
  const seg=el('div',{class:'seg'});
  function setGroup(g){hotFilter=null;catFilter=null;fGroup.value=g;[...seg.querySelectorAll('button')].forEach(x=>x.classList.toggle('on',x.dataset.g===g));render();}
  [['domain',T('care area','照護領域')],['primary_buyer',T('who buys','誰買硬體')],['stakeholder',T('who uses it','使用者')],
   ['ai',T('AI / no-AI','AI／非AI')],['play',T('play','打法')],['hardware_profile',T('hardware','硬體元件')]]
    .forEach(([g,lab])=>{const b=el('button',{'data-g':g},lab);b.onclick=()=>setGroup(g);seg.append(b);});
  fTxt.placeholder=T('search…','搜尋…');
  const tb=el('div',{class:'toolbar'});
  tb.append(el('span',{class:'tagk'},T('view by','檢視')),seg,el('span',{style:'flex:1 1 20px'}),fTxt,cnt);
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
      labeled(T('who buys','誰買'),fBuyer),labeled(T('substrate','substrate'),fBucket),
      labeled(T('segment','客群'),fSeg),labeled(T('play','play'),fPlay),
      labeled(T('deployment','部署'),fDep),labeled(T('min opportunity','最低機會'),fHw),
      labeled(T('hardware component','硬體元件'),fProfile),
      el('div',{style:'display:flex;align-items:flex-end'},fSpans))));
  const treePane=el('div',{class:'tree'}), detailPane=el('div',{class:'detail'});
  let selected=null;
  let navStack=[], dv={kind:'none',id:null};
  const backBtn=el('button',{class:'backbtn',style:'display:none'},'← '+T('Back','返回'));
  root.append(backBtn);
  root.append(el('div',{class:'twopane',id:'twopane'},treePane,detailPane));
  const byOpp=(a,b)=>b.hardware_opportunity-a.hardware_opportunity||a.id.localeCompare(b.id);
  function showDetail(c){selected=c||null;clear(detailPane);
    if(!c){detailPane.append(el('div',{class:'muted',style:'padding:24px 4px'},T('Select a category on the left.','在左邊選一個類別。')));return;}
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
  // trigger brief: a signal, organized — window · where to catch · the move · the markets it opens
  function triggerBrief(t){
    const cd=el('div',{class:'card'});
    cd.append(el('div',{class:'row',style:'align-items:center'},
      el('span',{class:'u '+t.urgency,style:'font-weight:800;text-transform:uppercase;font-size:12px'},t.urgency),
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
      const it=el('div',{class:'mkitem'},el('span',{class:'hw hw'+c.hardware_opportunity,style:'font-size:10px;padding:0 5px'},String(c.hardware_opportunity)),el('span',{class:'mknm'},nm(c)));
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
    const feed=(DATA.triggers.triggers||[]).filter(t=>(t.related_plays||[]).includes(pid))
      .sort((a,b)=>({critical:0,high:1,medium:2,low:3}[a.urgency]-{critical:0,high:1,medium:2,low:3}[b.urgency]));
    if(feed.length){const ts=el('div',{class:'dsec'});ts.append(el('div',{class:'dsh'},T('Triggers that open this play — click for the signal brief','開啟此打法的訊號 — 點看訊號簡報')));
      const tw=el('div',{style:'display:flex;flex-wrap:wrap;gap:5px'});
      feed.forEach(t=>{const ch=el('span',{class:'pill',style:'cursor:pointer'},el('span',{class:'u '+t.urgency,style:'font-weight:700'},'● '),t.signal);ch.onclick=()=>goTrigger(t);tw.append(ch);});
      ts.append(tw);cd.append(ts);}
    const mem=cats.filter(c=>(c.plays||[]).includes(pid)).sort((a,b)=>b.hardware_opportunity-a.hardware_opportunity);
    const ms=el('div',{class:'dsec'});ms.append(el('div',{class:'dsh'},T('Target categories — click for the battle card','目標類別 — 點看戰卡')+' · '+mem.length));
    const mw=el('div',{class:'mklist'});
    mem.forEach(c=>{const it=el('div',{class:'mkitem'},el('span',{class:'hw hw'+c.hardware_opportunity,style:'font-size:10px;padding:0 5px'},String(c.hardware_opportunity)),el('span',{class:'mknm'},nm(c)));
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
    r.append(el('span',{class:'hw hw'+c.hardware_opportunity,style:'font-size:10px;padding:0 5px',title:OPP[c.hardware_opportunity]},String(c.hardware_opportunity)));
    r.append(el('span',{class:'tname'},nm(c)));
    r.append(el('span',{class:'tby '+BUYER_C[c.primary_buyer],title:c.primary_buyer}));
    r.onclick=()=>viewCat(c);return r;}
  function l2into(body,list){[['ai',T('AI-driven','AI 驅動')],['no',T('No-AI','非 AI')]].forEach(([ak,alab])=>{
    const sub=list.filter(c=>ak==='ai'?isAI(c):!isAI(c));if(!sub.length)return;
    body.append(el('div',{class:'tsub'},alab+' · '+sub.length));
    sub.slice().sort(byOpp).forEach(c=>body.append(catRow(c)));});}
  const flagN=l=>l.filter(c=>c.hardware_opportunity===4).length;
  const hotN=l=>l.filter(c=>(c.hardware_opportunity_by_buyer.customer||0)>=3).length;
  function l1node(label,list,leaf){if(!list.length)return;
    const car=el('span',{class:'tcar'},'▾');
    const fl=flagN(list), ho=hotN(list);
    const hdr=el('div',{class:'tnode'},car,el('span',{style:'flex:1'},label));
    if(fl)hdr.append(el('span',{class:'tflag',title:T('flagship (opportunity 4)','旗艦 (機會 4)')},fl+' '+T('flagship','旗艦')));
    if(ho)hdr.append(el('span',{class:'thot',title:T('customer-HOT (opportunity ≥3)','客戶-HOT (機會≥3)')},ho+' HOT'));
    hdr.append(el('span',{class:'tcount'},String(list.length)));
    const body=el('div',{class:'tbody'});
    hdr.onclick=()=>{const open=body.style.display!=='none';body.style.display=open?'none':'';car.textContent=open?'▸':'▾';};
    treePane.append(hdr,body);
    if(leaf)list.slice().sort(byOpp).forEach(c=>body.append(catRow(c)));else l2into(body,list);}
  function tagRow(k,arr){const r=el('div',{class:'row'});r.append(el('span',{class:'tagk'},k));
    (arr||[]).forEach(v=>r.append(el('span',{class:'chip dim'},v)));return r;}
  function card(c){
    const cd=el('div',{class:'card'});
    const pbP=c.hardware_opportunity_by_buyer[c.primary_buyer];
    const head=el('div',{class:'row'},el('span',{class:'hw hw'+c.hardware_opportunity,title:'hardware opportunity: '+OPP[c.hardware_opportunity]+' ('+c.hardware_opportunity+'/4)'},String(c.hardware_opportunity)),
      el('span',{class:'by '+BUYER_C[c.primary_buyer],title:'primary buyer '+c.primary_buyer+(pbP?' · '+OPP[pbP]+' opportunity':'')},c.primary_buyer+(pbP?'·'+pbP:'')));
    (c.hardware_buyer||[]).filter(x=>x!==c.primary_buyer).forEach(x=>head.append(el('span',{class:'byo',title:x+' buys iron'+(c.hardware_opportunity_by_buyer[x]?' · '+OPP[c.hardware_opportunity_by_buyer[x]]+' opportunity':'')},x+(c.hardware_opportunity_by_buyer[x]?'·'+c.hardware_opportunity_by_buyer[x]:''))));
    if(spansOf(c))head.append(el('span',{class:'byo',title:'deployment spans customer↔vendor'},'⇄'));
    (c.plays||[]).forEach(p=>{const ch=el('span',{class:'play '+playClass(p),style:'cursor:pointer',title:playName(p)},playName(p).split(' ')[0]);ch.onclick=()=>goPlay(p);head.append(ch);});
    cd.append(head);
    cd.append(el('h3',{},nm(c)));
    cd.append(el('div',{class:'zh'},sub(c)));
    const segr=el('div',{class:'row'});(c.segments||[]).forEach(s=>segr.append(el('span',{class:'chip'},s)));
    cd.append(segr);
    cd.append(tagRow(T('lifecycle','生命週期'),c.lifecycle));
    cd.append(tagRow(T('role','角色'),c.role));
    cd.append(tagRow(T('data','資料型態'),c.data_modality));
    cd.append(tagRow(T('deploy','部署'),c.deployment));
    if(c.hardware_profile&&c.hardware_profile.length){const hr=el('div',{class:'row'});hr.append(el('span',{class:'tagk'},T('hardware','硬體')));c.hardware_profile.forEach(h=>hr.append(el('span',{class:'hwc',title:'deployment scale'},h+((c.hardware_profile_sizing||{})[h]?' · '+c.hardware_profile_sizing[h]:''))));cd.append(hr);}
    if(c.vendors&&c.vendors.length){const vr=el('div',{class:'row'});vr.append(el('span',{class:'tagk'},T('vendors','廠商')));
      c.vendors.forEach(v=>{const bd=lbBadge(v);const p=el('span',{class:'pill'+(bd?' lead':''),style:'cursor:pointer'},VNAME[v]||v);
        p.title=bd?(T('market leader: ','市場領導 ')+bd+' — '+T('view vendor','看廠商')):T('view vendor','看廠商');p.onclick=()=>goVendor(v);vr.append(p);});
      cd.append(vr);}
    if(c.hospital_view){cd.append(tagRow(T('hosp-who','醫院·誰'),c.hospital_view.stakeholder));
      cd.append(tagRow(T('hosp-dim','醫院·面向'),c.hospital_view.dimension));}
    if(c.infrastructure_notes)cd.append(el('div',{class:'notes'},c.infrastructure_notes));
    if(c.play_exemption)cd.append(el('div',{class:'notes'},T('Outside play scope: ','play 範圍外:')+c.play_exemption));
    return cd;
  }
  function detailCard(c){
    const det=c.detail||{}, cd=el('div',{class:'card'});
    const pbP=c.hardware_opportunity_by_buyer[c.primary_buyer];
    const head=el('div',{class:'row'},el('span',{class:'hw hw'+c.hardware_opportunity,title:OPP[c.hardware_opportunity]},String(c.hardware_opportunity)),
      el('span',{class:'by '+BUYER_C[c.primary_buyer]},c.primary_buyer+(pbP?'·'+pbP:'')));
    (c.hardware_buyer||[]).filter(x=>x!==c.primary_buyer).forEach(x=>head.append(el('span',{class:'byo'},x+(c.hardware_opportunity_by_buyer[x]?'·'+c.hardware_opportunity_by_buyer[x]:''))));
    (c.plays||[]).forEach(p=>{const ch=el('span',{class:'play '+playClass(p),style:'cursor:pointer',title:playName(p)},playName(p).split(' ')[0]);ch.onclick=()=>goPlay(p);head.append(ch);});
    cd.append(head);
    cd.append(el('h3',{style:'margin:6px 0 0'},nm(c)));
    cd.append(el('div',{class:'zh'},sub(c)));
    if(c.name_full)cd.append(el('div',{class:'muted',style:'font-size:12px;margin-bottom:6px'},c.name_full));
    // ---- battle card: the actionable sell layer (motion · reference arch · trigger→move) ----
    const bc=el('div',{class:'battle'});
    const brow=(lab,node)=>{const r=el('div',{class:'brow'});r.append(el('div',{class:'blab'},lab));const v=el('div',{class:'bval'});v.append(node);r.append(v);bc.append(r);};
    const hb=c.hardware_buyer||[];
    const motion=(hb.includes('customer')&&isHot(c))?T('Direct sale — the end org buys and runs its own iron.','直銷 — 終端機構自己採購並運行硬體。')
      :hb.includes('operator')?T('Co-sell — an ISV / service operator runs the iron; sell through them.','共銷 — ISV／服務營運商運行硬體;透過他們賣。')
      :hb.includes('oem')?T('OEM design-win — hardware embedded in a device; per-unit BOM.','OEM 設計導入 — 硬體嵌入裝置;按台計 BOM。')
      :hb.includes('customer')?T('Direct sale (modest scale).','直銷(規模較小)。'):T('—','—');
    brow(T('Your motion','你的打法'),el('span',{},motion+'  ('+c.primary_buyer+(pbP?'·'+pbP:'')+')'));
    const ra=el('div',{class:'rarch'});
    if((c.hardware_profile||[]).length)c.hardware_profile.forEach(h=>ra.append(el('span',{class:'raxx',title:plineGloss(h)},smciFam(h)+((c.hardware_profile_sizing||{})[h]?' · '+c.hardware_profile_sizing[h]:''))));
    else ra.append(el('span',{class:'muted'},T('SaaS-light — little on-prem iron to sell.','SaaS 輕量 — 幾乎無地端硬體可賣。')));
    brow(T('Reference arch','建議配置'),ra);
    const trigs=(DATA.triggers.triggers||[]).filter(t=>(t.related_categories||[]).includes(c.id));
    if(trigs.length){const tw=el('div',{});trigs.forEach(t=>{const row=el('div',{class:'twrow'});
      row.append(el('span',{class:'u '+t.urgency,style:'font-size:10px;font-weight:700;text-transform:uppercase'},t.urgency));
      row.append(el('span',{class:'tsig'},t.signal));row.append(el('span',{class:'tact'},'→ '+t.action));tw.append(row);});
      brow(T('Trigger → move','盯訊號 → 動作'),tw);}
    cd.append(bc);
    // ---- 6-tier hierarchy diagram (階級圖) ----
    const tiers=el('div',{class:'tiers6'});
    const tier=(lab,cont)=>{tiers.append(el('div',{class:'tier6'},el('div',{class:'tlab'},lab),el('div',{class:'tcont'},cont)));};
    const who=el('span',{style:'display:flex;flex-wrap:wrap;gap:5px'});(c.segments||[]).forEach(s=>who.append(el('span',{class:'chip'},s)));(((c.hospital_view||{}).stakeholder)||[]).forEach(s=>who.append(el('span',{class:'chip dim'},s)));
    tier(T('Who uses','使用方'),who);
    tier(T('Purpose','目的'),el('span',{},(LANG==='zh'?det.purpose_zh:det.purpose_en)||'—'));
    const flow=el('div',{class:'flowstrip'});(det.usage_flow||[]).forEach((s,i)=>{if(i)flow.append(el('span',{class:'farrow'},'→'));flow.append(el('span',{class:'fbox'},LANG==='zh'?s.zh:s.en));});
    tier(T('Usage flow','使用流程'),(det.usage_flow&&det.usage_flow.length)?flow:el('span',{},'—'));
    const tech=el('span',{style:'display:flex;flex-wrap:wrap;gap:5px;align-items:center'});(c.role||[]).forEach(r=>tech.append(el('span',{class:'chip dim'},r)));(c.data_modality||[]).forEach(m=>tech.append(el('span',{class:'chip dim'},m)));
    tier(T('Tech','技術'),tech);
    const hw=el('span',{style:'display:flex;flex-wrap:wrap;gap:5px'});(c.hardware_profile||[]).forEach(h=>hw.append(el('span',{class:'hwc'},h+((c.hardware_profile_sizing||{})[h]?'·'+c.hardware_profile_sizing[h]:''))));if(!(c.hardware_profile||[]).length)hw.append(el('span',{class:'muted'},T('SaaS-light','SaaS 輕量')));
    tier(T('Hardware','硬體'),hw);
    const sm=el('span',{style:'display:flex;flex-wrap:wrap;gap:5px'});(c.hardware_profile||[]).forEach(h=>sm.append(el('span',{class:'pill lead'},smciFam(h))));if(!(c.hardware_profile||[]).length)sm.append(el('span',{class:'muted'},'—'));
    tier(T('SMCI workload','SMCI'),sm);
    cd.append(tiers);
    // ---- prose sections (authored, bilingual) ----
    const sec=(lab,txt)=>{if(!txt)return;cd.append(el('div',{class:'dsec'},el('div',{class:'dsh'},lab),el('div',{},txt)));};
    sec(T('Purpose','目的'),(LANG==='zh'?det.purpose_zh:det.purpose_en));
    if(det.usage_flow&&det.usage_flow.length){const fs=el('div',{class:'dsec'});fs.append(el('div',{class:'dsh'},T('Usage flow','使用流程')));det.usage_flow.forEach((s,i)=>fs.append(el('div',{class:'dstep'},el('b',{},(i+1)+'.'),el('span',{},LANG==='zh'?s.zh:s.en))));cd.append(fs);}
    sec(T('How it works','技術講解'),(LANG==='zh'?det.tech_zh:det.tech_en));
    sec(T('Supermicro workload fit','SMCI 可協助的 workload'),(LANG==='zh'?det.smci_zh:det.smci_en));
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
      d.append(el('div',{class:'muted',style:'font-size:10px;margin-top:5px;line-height:1.4'},T('Bars = cited market share (hover a bar for the source); “n/a” = no public share figure. Each share is of that vendor’s own market.','長條=有引用來源的市佔率(游標移到長條看來源);「未公開」=無公開市佔數字。每個市佔為該廠商所屬市場之比例。')));
      cd.append(d);
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
      el('span',{class:'muted',style:'font-size:12px'},cats.length+T(' categories · ',' 類 · ')+(DATA.vendors.vendors||[]).length+T(' vendors',' 廠商'))));
    box.append(el('div',{class:'muted',style:'font-size:12px;margin:0 0 8px'},T('Search, or start from a Supermicro product line, a trigger, or a play. Every door opens the category’s battle card — your motion, the reference architecture to pitch, and the trigger to act on.','搜尋,或從 Supermicro 產品線、觸發訊號、或打法開始。每道門都打開該類別的戰卡 — 你的打法、要提的建議配置、該盯的訊號。')));
    // door: search (proxies the toolbar search)
    const sb=el('input',{class:'hsearch',type:'search',placeholder:T('Search a category, vendor, or SMCI box — “digital pathology” · “Sectra” · “GPU”…','搜尋類別、廠商、或 SMCI 硬體 —「數位病理」·「Sectra」·「GPU」…')});
    sb.oninput=()=>{fTxt.value=sb.value;catFilter=null;hotFilter=null;render();};
    box.append(sb);
    const note=el('div',{class:'hnote'});box.append(note);
    const openDoor=(labelNode,ids,brief)=>{pushNav();catFilter=ids;hotFilter=null;fTxt.value='';render();
      clear(note);if(labelNode)note.append(labelNode);
      if(brief){selected=null;clear(detailPane);detailPane.append(brief);}
      const tp=document.getElementById('twopane');if(tp)tp.scrollIntoView({behavior:'smooth',block:'start'});};
    const URANK={critical:0,high:1,medium:2,low:3};
    // door: SMCI product line (facet 1) — grouped by role + plain gloss, not acronym soup
    box.append(el('div',{class:'dhdr'},T('Product line (SMCI box)','產品線(SMCI 機箱)')));
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
    box.append(plist);
    box.append(el('div',{class:'muted',style:'font-size:11px;margin:1px 0 4px'},T('Counts overlap — a category often pulls several boxes.','數字會重疊 — 一個類別常拉多台機箱。')));
    // door: trigger (facet 3) — grouped by urgency; each row -> an organized brief
    box.append(el('div',{class:'dhdr'},T('Trigger — a signal that starts a deal (click for the brief)','觸發訊號 — 啟動一單的訊號(點看簡報)')));
    const URG=[['critical',T('Critical','危急')],['high',T('High','高')],['medium',T('Medium','中')],['low',T('Low','低')]];
    const tlist=el('div',{class:'plist'});
    URG.forEach(([uk,ulab])=>{
      const ts=(DATA.triggers.triggers||[]).filter(t=>t.urgency===uk);if(!ts.length)return;
      tlist.append(el('div',{class:'pgrp u '+uk},ulab+' · '+ts.length));
      ts.forEach(t=>{const ids=(t.related_categories||[]);
        const pg=el('span',{class:'pgl',style:'display:flex;gap:4px;justify-content:flex-end;align-items:baseline'});
        (t.related_plays||[]).forEach(pid=>{const L=pid.split('-')[1].toUpperCase();pg.append(el('span',{class:'play play'+L.toLowerCase()},'Play '+L));});
        const it=el('div',{class:'pitem'},el('span',{class:'u '+t.urgency,style:'font-weight:700'},'●'),el('span',{class:'pnm'},t.signal),pg,
          el('span',{class:'pct'},ids.length+T(' mkts ▸',' 市場 ▸')));
        it.onclick=()=>goTrigger(t);
        tlist.append(it);});
    });
    box.append(tlist);
    // door: play
    const prow=el('div',{class:'drow'});prow.append(el('span',{class:'dlab'},T('Play','打法')));
    DATA.plays.plays.forEach(p=>{const letter=p.id.split('-')[1].toUpperCase();const ids=cats.filter(c=>(c.plays||[]).includes(p.id)).map(c=>c.id);
      const chip=el('button',{class:'dchip'},el('span',{class:'play play'+letter.toLowerCase()},'Play '+letter),' '+p.name+' ',el('span',{class:'dn'},String(ids.length)));
      chip.onclick=()=>goPlay(p.id);prow.append(chip);});
    box.append(prow);
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
          hw=+fHw.value||0,prof=fProfile.value,gp=fGroup.value,q=fTxt.value.toLowerCase();
    const shown=cats.filter(c=>{
      if(catFilter&&!catFilter.includes(c.id))return false;
      if(hotFilter&&(c.hardware_opportunity_by_buyer[hotFilter.buyer]||0)<hotFilter.min)return false;
      if(by&&!c.hardware_buyer.includes(by))return false;
      if(prof&&!(c.hardware_profile||[]).includes(prof))return false;
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
    if(gp==='stakeholder'){STAKE.forEach(([k,lab])=>l1node(lab,shown.filter(c=>stakeKey(c)===k)));}
    else if(gp==='ai'){l1node(T('AI-driven','AI 驅動'),shown.filter(isAI),true);l1node(T('No-AI','非 AI'),shown.filter(c=>!isAI(c)),true);}
    else if(!gp){l1node(T('All categories','全部類別'),shown);}
    else{
      const map=new Map();shown.forEach(c=>groupsOf(c,gp).forEach(k=>{if(!map.has(k))map.set(k,[]);map.get(k).push(c);}));
      let keys=[...map.keys()];
      if(gp==='hardware_opportunity')keys.sort((a,b)=>b-a);
      else if(gp==='play')keys.sort((a,b)=>((a==='(no play)')-(b==='(no play)'))||a.localeCompare(b));
      else keys.sort((a,b)=>flagN(map.get(b))-flagN(map.get(a))||hotN(map.get(b))-hotN(map.get(a))||map.get(b).length-map.get(a).length);
      keys.forEach(k=>{const label=gp==='hardware_opportunity'?('opportunity '+k+' ('+OPP[k]+')'):(gp==='play'?playName(k):gp==='domain'?domLabel(k):k);l1node(label,map.get(k));});
    }
    const keep=selected&&shown.find(c=>c.id===selected.id);
    showDetail(keep||shown[0]||null);
  }
  [fBuyer,fBucket,fSeg,fPlay,fDep,fHw,fProfile,fGroup].forEach(x=>x.onchange=()=>{hotFilter=null;catFilter=null;render();});
  window.exploreFilter=function(buyer,minOpp){hotFilter={buyer:buyer,min:minOpp||3};catFilter=null;
    [fBuyer,fBucket,fSeg,fPlay,fDep,fHw,fProfile].forEach(x=>x.value='');fSpansBox.checked=false;fTxt.value='';
    fGroup.value='domain';[...seg.querySelectorAll('button')].forEach(b=>b.classList.toggle('on',b.dataset.g==='domain'));
    render();window.scrollTo(0,0);};
  fSpansBox.onchange=()=>{hotFilter=null;catFilter=null;render();};fTxt.oninput=()=>{hotFilter=null;catFilter=null;render();};setGroup('domain');
}

// ================= VENDORS (enriched registry) =================
function renderRegistryInto(host){
  const root=host;
  const vsAll=(DATA.vendors.vendors||[]);
  const conf=(DATA.vendors.version)||'?';
  const cnt=el('span',{class:'count'});
  const q=el('input',{type:'search',placeholder:T('search vendor / HQ / leader / category...','搜尋廠商 / 總部 / 負責人 / 類別...')});
  root.append(el('div',{class:'rollup'},T('Vendor registry v'+conf+' — '+vsAll.length+' vendors, web-researched + adversarially verified. Sort by value = the vendors serving the most flagship / customer-HOT SMCI categories, market leaders first.','廠商登錄 v'+conf+' — '+vsAll.length+' 家,網路研究 + 對抗式查核。依價值排序 = 服務最多旗艦／客戶-HOT SMCI 類的廠商,市場領導者在前。')));
  let sortMode='value';
  function byValue(a,b){const A=vendorVal(a),B=vendorVal(b);return B.flag-A.flag||B.hot-A.hot||((LB_BY_VID[b.id]?1:0)-(LB_BY_VID[a.id]?1:0))||a.name.localeCompare(b.name);}
  const sseg=el('div',{class:'seg',style:'margin:0'});
  [['value',T('by value','依價值')],['az','A–Z']].forEach(([k,lab])=>{const b=el('button',{'data-k':k,class:k==='value'?'on':''},lab);b.onclick=()=>{sortMode=k;[...sseg.querySelectorAll('button')].forEach(x=>x.classList.toggle('on',x.dataset.k===k));render();};sseg.append(b);});
  root.append(el('div',{class:'toolbar'},el('span',{class:'tagk'},T('sort','排序')),sseg,el('span',{style:'flex:1 1 20px'}),q,cnt));
  const vhost=el('div',{});root.append(vhost);
  function excl(v){return "exclud" in Object.assign({},v)?false:/exclud/i.test(v.note||'');}
  function card(v){
    const c=el('div',{class:'card'});c.style.marginBottom='8px';
    const h=el('div',{class:'row'},el('h3',{style:'margin:0'},v.name));
    const bd=lbBadge(v.id);
    if(bd){const lp=el('span',{class:'pill',style:'cursor:pointer;background:var(--accentbg);color:var(--accent);font-weight:700'},bd);lp.title=T('on the market leaderboard — open','在市場榜單上 — 開啟');lp.onclick=()=>goVendorsBoard();h.append(lp);}
    valBadges(vendorVal(v),h);
    if(/exclud/i.test(v.note||''))h.append(el('span',{class:'pill'},'§5.4 co-sell excluded'));
    c.append(h);
    const kv=el('dl',{class:'kv'});
    const add=(k,x)=>{if(x==null||x==='')return;kv.append(el('dt',{},k),el('dd',{},String(x)));};
    add(T('HQ','總部'),v.headquarters); add(T('Founded','成立'),v.founded); add(T('Leadership','負責人'),v.leadership);
    add(T('Market position','市場地位'),v.market_position); add(T('Market share','市佔'),v.market_share);
    add(T('Deployment','部署'),(v.deployment_models||[]).join(', '));
    c.append(kv);
    const seg=el('div',{class:'row'});(v.categories||[]).forEach(x=>{const cc=CATBYID[x];const ch=el('span',{class:'chip',style:'cursor:pointer'},cc?nm(cc):x);ch.title=T('view category','看類別');ch.onclick=()=>goCategory(x);seg.append(ch);});c.append(seg);
    if(v.history)c.append(el('div',{class:'notes'},v.history));
    const srcs=(v.sources&&v.sources.length)?v.sources:(v.source?[v.source]:[]);
    if(srcs.length){const sr=el('div',{class:'row'});sr.append(el('span',{class:'tagk'},T('sources','來源')));
      srcs.forEach(u=>{const isurl=/^https?:\/\//.test(u);
        sr.append(isurl?el('a',{href:u,target:'_blank',class:'pill'},u.replace(/^https?:\/\//,'').split('/')[0]):el('span',{class:'pill'},u.slice(0,40)));});
      c.append(sr);}
    return c;
  }
  function render(){
    const s=q.value.toLowerCase();
    const shown=vsAll.filter(v=>!s||JSON.stringify([v.name,v.headquarters,v.leadership,v.market_position,v.market_share,(v.categories||[]).join(' ')]).toLowerCase().includes(s))
      .slice().sort(sortMode==='az'?(a,b)=>a.name.localeCompare(b.name):byValue);
    clear(vhost);shown.forEach(v=>vhost.append(card(v)));
    cnt.textContent=shown.length+' / '+vsAll.length+T(' shown',' 顯示');
  }
  q.oninput=render;render();
}

// ================= PLAYS =================
function renderPlaysInto(host){
  const root=host;
  const grid=el('div',{class:'grid'});root.append(grid);
  DATA.plays.plays.forEach(p=>{
    const letter=p.id.split('-')[1].toUpperCase();
    const card=el('div',{class:'card'});
    card.append(el('div',{class:'row'},el('span',{class:'play play'+letter.toLowerCase()},'Play '+letter)));
    card.append(el('h3',{},p.name));
    const members=DATA.taxonomy.categories.filter(c=>(c.plays||[]).includes(p.id));
    const vv=catsVal(members.map(c=>c.id));
    const vrow=el('div',{class:'row',style:'margin:2px 0 8px'});
    vrow.append(el('span',{class:'tagk'},T('pipeline','管線')),el('span',{class:'muted',style:'font-size:12px'},members.length+T(' targets','個目標')));
    valBadges(vv,vrow);card.append(vrow);
    const top=members.filter(isFlag).slice().sort((a,b)=>a.id.localeCompare(b.id)).slice(0,4);
    if(top.length){const tr=el('div',{class:'row',style:'margin-bottom:8px'});tr.append(el('span',{class:'tagk'},T('top targets','頂級目標')));top.forEach(c=>{const pp=el('span',{class:'pill lead',style:'cursor:pointer'},nm(c));pp.onclick=()=>goCategory(c.id);tr.append(pp);});card.append(tr);}
    const sec=(t,arr)=>{card.append(el('div',{class:'tagk'},t));
      const ul=el('ul',{class:'muted'});(arr||[]).forEach(x=>ul.append(el('li',{},x)));
      ul.style.margin='4px 0 8px';ul.style.paddingLeft='18px';ul.style.fontSize='12px';card.append(ul);};
    sec(T('workloads','工作負載'),p.workloads);
    sec(T('target segments','目標客群'),p.target_segments);
    sec(T('hardware anchor','硬體錨點'),p.hardware_anchor);
    if(p.regulatory_notes)card.append(el('div',{class:'notes'},T('reg: ','法規:')+p.regulatory_notes));
    grid.append(card);
  });
}

// ================= TRIGGERS =================
function renderTriggersInto(host){
  const root=host;
  const t=el('table');
  const TH=LANG==='zh'?['訊號','類別','急迫','窗口','來源','行動','關聯']:['Signal','Cat','Urgency','Window','Source','Action','Related'];
  t.append(el('thead',{},el('tr',{},...TH.map(h=>el('th',{},h)))));
  const tb=el('tbody');
  const rank={critical:0,high:1,medium:2,low:3};
  DATA.triggers.triggers.slice().sort((a,b)=>rank[a.urgency]-rank[b.urgency]
    ||catsVal(b.related_categories).flag-catsVal(a.related_categories).flag
    ||catsVal(b.related_categories).hot-catsVal(a.related_categories).hot).forEach(x=>{
    const vv=catsVal(x.related_categories);
    const rrow=el('div',{class:'row'});
    (x.related_plays||[]).forEach(p=>rrow.append(el('span',{class:'play '+playClass(p)},playName(p).split(' ')[0])));
    valBadges(vv,rrow);
    (x.related_categories||[]).forEach(cid=>{const c=CATBYID[cid];const p=el('span',{class:'pill'+((c&&isFlag(c))?' lead':''),style:'cursor:pointer'},c?nm(c):cid);p.onclick=()=>goCategory(cid);rrow.append(p);});
    tb.append(el('tr',{},
      el('td',{},el('strong',{},x.signal)),
      el('td',{},el('span',{class:'pill'},x.category)),
      el('td',{},el('span',{class:'u '+x.urgency},x.urgency)),
      el('td',{class:'muted'},x.window),
      el('td',{class:'muted'},x.source),
      el('td',{},x.action),
      el('td',{},rrow)));
  });
  t.append(tb);root.append(el('div',{class:'wrap'},t));
}

// ================= SCORING =================
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
    out.append(el('div',{class:'muted',style:'margin-top:6px;font-size:12px'},res.tier.action));
  }
  wrap.append(sg,el('hr',{style:'border:0;border-top:1px solid var(--line);margin:14px 0'}),out);
  root.append(wrap);calc();
}

// ================= ACCOUNTS =================
function renderAccountsInto(host){
  const root=host;
  if(!DATA.accounts.length){root.append(el('div',{class:'muted'},T('No accounts in data/accounts/ yet.','data/accounts/ 尚無帳號。')));return;}
  const scored=DATA.accounts.map(a=>({a,r:scoreAccount(a)})).sort((x,y)=>y.r.total-x.r.total);
  scored.forEach(({a,r})=>{
    const card=el('div',{class:'card'});card.style.marginBottom='12px';
    const head=el('div',{class:'row'},
      el('span',{class:'tierbadge',style:'background:'+tierColor(r.tier.name)},r.total+' - '+r.tier.name));
    (a.plays?[a.plays]:(a.play?[a.play]:[])).flat().forEach(p=>head.append(el('span',{class:'play '+playClass(p)},playName(p))));
    if(a.fictional)head.append(el('span',{class:'pill'},'fictional / demo'));
    card.append(head);
    card.append(el('h3',{},(a.company||'?')+' - '+(a.facility||'?')));
    const kv=el('dl',{class:'kv'});
    const add=(k,v)=>{if(v==null||v==='')return;kv.append(el('dt',{},k),el('dd',{},typeof v==='object'?JSON.stringify(v):String(v)));};
    add(T('Segment','客群'),a.segment);
    add(T('Software','軟體'),a.software&&(a.software.domain||''));
    add(T('Deployment','部署'),a.deployment);add(T('Operator','營運者'),a.operator);
    add(T('Trigger','觸發訊號'),a.trigger&&(a.trigger.detail||a.trigger.id));
    add(T('Infra control','基建掌控'),a.infrastructure_control);
    add(T('Next step','下一步'),a.next_step);
    card.append(kv);
    const bd=el('div',{});bd.style.marginTop='10px';
    r.rows.forEach(row=>{
      const pct=(row.score/SMAX)*100;
      const line=el('div',{});line.style.margin='6px 0';
      line.append(el('div',{class:'muted',style:'font-size:11px;display:flex;justify-content:space-between'},
        el('span',{},row.label+' ('+row.score+'/'+SMAX+' x'+row.weight+')'),el('span',{},String(row.weighted))));
      const bar=el('div',{class:'mini'});const fill=el('i',{style:'width:'+pct+'%;background:'+(row.score<=2?'var(--u-crit)':row.score>=4?'var(--a)':'var(--u-med)')});
      bar.append(fill);line.append(bar);bd.append(line);
    });
    card.append(bd);
    const ev=(a.evidence||[]);if(ev.length){
      const confs=ev.map(e=>e.confidence).filter(Boolean);
      card.append(el('div',{class:'notes'},T('Evidence: ','證據:')+ev.length+T(' claim(s), confidence ',' 項聲明,信心 ')+[...new Set(confs)].join('/')+(confs.length&&confs.every(c=>c==='D')?T(' - all inference, verify before pursuit',' - 全為推論,追蹤前先查證'):'')));
    }
    root.append(card);
  });
}

// ================= LEADERBOARDS (market vendor rankings) =================
function renderLeaderboardsInto(host){
  const root=host;
  const LB=DATA.leaderboards&&DATA.leaderboards.leaderboards;
  if(!LB){root.append(el('div',{class:'muted'},T('No leaderboards data.','無榜單資料。')));return;}
  root.append(el('div',{class:'rollup'},T('Market vendor leaderboards — ranked by market share / installed base. Every entry §8-sourced (a real figure or a sourced market position); grouped by sub-market. A vendor that plays both sides (e.g. GE, Philips) appears on both boards.','市場廠商榜 — 按市佔／裝機量排名。每一項 §8 有來源(真數字或有來源的市場地位),依次級市場分組。雙棲廠商(如 GE、Philips)兩榜都上。')));
  const wrap=el('div',{class:'grid',style:'grid-template-columns:repeat(auto-fill,minmax(430px,1fr))'});
  [['ai',LB.ai],['no_ai',LB.no_ai]].forEach(([key,board])=>{
    if(!board)return;
    const col=el('div',{class:'card'});
    col.append(el('h3',{style:'margin-bottom:6px'},(LANG==='zh'?board.label_zh:board.label_en)+' · '+board.count));
    let curSeg=null;
    (board.entries||[]).forEach(e=>{
      if(e.segment!==curSeg){curSeg=e.segment;
        col.append(el('div',{class:'tagk',style:'display:block;margin:12px 0 2px'},(LANG==='zh'?e.segment_zh:e.segment)));}
      const row=el('div',{style:'padding:6px 0;border-top:1px solid var(--line)'});
      const nmEl=el('span',{style:'font-weight:600'+(e.vendor_id?';cursor:pointer;text-decoration:underline dotted var(--accent)':'')},e.name+(e.vendor_id?' ↩':''));
      if(e.vendor_id){nmEl.title=T('in the registry — view vendor card','在登錄中 — 看廠商卡');nmEl.onclick=()=>goVendor(e.vendor_id);}
      const rowline=el('div',{class:'row'},el('b',{style:'color:var(--accent);min-width:34px'},'#'+e.rank),nmEl);
      if(e.vendor_id&&VBYID[e.vendor_id])valBadges(vendorVal(VBYID[e.vendor_id]),rowline);
      row.append(rowline);
      row.append(el('div',{class:'muted',style:'font-size:11px;margin:3px 0'},e.market_basis));
      if(e.source){const isurl=/^https?:\/\//.test(e.source);
        row.append(isurl?el('a',{href:e.source,target:'_blank',class:'pill'},T('source','來源')+' ↗'):el('span',{class:'pill'},String(e.source).slice(0,60)));}
      col.append(row);
    });
    wrap.append(col);
  });
  root.append(wrap);
}

// ================= fused-tab section toggles (Method, Vendors) =================
// reusable in-page sub-navigation (reuses the .seg segmented-control style)
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
  root.append(el('h2',{style:'margin:2px 0 8px'},T('GTM method — how to run the motion','GTM 方法 — 怎麼打')));
  subNav(root,[
    ['plays',T('Plays','打法'),renderPlaysInto],
    ['signals',T('Signals','訊號'),renderTriggersInto],
    ['scoring',T('Scoring','評分'),renderScoringInto],
    ['accounts',T('Accounts','帳號'),renderAccountsInto]],'plays');
}
function renderVendors(){
  const root=$('#tab-vendors'); clear(root);
  root.append(el('h2',{style:'margin:2px 0 8px'},T('Market players — vendors & leaders','市場玩家 — 廠商與領導者')));
  _vendorsNav=subNav(root,[
    ['registry',T('Registry','登錄')+' ('+(DATA.vendors.vendors||[]).length+')',renderRegistryInto],
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

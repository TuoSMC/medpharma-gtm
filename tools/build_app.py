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

    data = {
        "taxonomy": load(DATA / "taxonomy.yaml"),
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
  --a:#1f9d57; --b:#7a5cd0; --c:#c2560c;
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
.gcount{font-size:11px;font-weight:600;color:var(--muted);background:var(--accentbg);border-radius:20px;padding:1px 8px}
.play{font-size:11px;font-weight:700;padding:2px 8px;border-radius:6px;color:#fff}
.playa{background:var(--a)}.playb{background:var(--b)}.playc{background:var(--c)}
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
.statchips{display:flex;flex-wrap:wrap;gap:8px;margin:4px 0}
.statchip{border:1px solid var(--line);background:var(--panel);color:var(--ink);font:inherit;font-size:13px;padding:7px 12px;border-radius:18px;cursor:pointer;display:inline-flex;align-items:center;gap:5px}
.statchip b{font-size:15px}
.statchip:hover{border-color:var(--accent);background:var(--accentbg)}
.statchip.qv{padding:5px 11px;font-size:12px;border-radius:14px}
.statchip.qv.on{border-color:var(--accent);background:var(--accentbg);color:var(--accent);font-weight:700}
.sc-cust b{color:var(--a)}.sc-oper b{color:var(--b)}.sc-oem b{color:var(--c)}
.flab{display:flex;flex-direction:column;gap:2px;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.4px}
.flab>select,.flab>input{margin:0}
.legend{font-size:11px;color:var(--muted);margin:6px 0 2px}
.legend .dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin:0 3px 0 8px;vertical-align:middle}
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
  <section class="tab on" id="tab-home"></section>
  <section class="tab" id="tab-taxonomy"></section>
  <section class="tab" id="tab-hunt"></section>
  <section class="tab" id="tab-plays"></section>
  <section class="tab" id="tab-triggers"></section>
  <section class="tab" id="tab-scoring"></section>
  <section class="tab" id="tab-accounts"></section>
  <section class="tab" id="tab-vendors"></section>
  <section class="tab" id="tab-leaderboards"></section>
</main>
<script>
const DATA = /*__DATA__*/null;
const $ = (s,r=document)=>r.querySelector(s);
const el=(t,a={},...kids)=>{const n=document.createElement(t);
  for(const k in a){if(k==='class')n.className=a[k];else n.setAttribute(k,a[k]);}
  for(const c of kids)n.append(c&&c.nodeType?c:document.createTextNode(c));return n;};
const clear=n=>n.replaceChildren();
const playClass=p=>({'play-a':'playa','play-b':'playb','play-c':'playc'}[p]||'');
// ---- i18n: EN <-> 中文 toggle (category names come from data name_zh; chrome from T()) ----
let LANG='en';
const nm=c=>LANG==='zh'?(c.name_zh||c.name_en):c.name_en;   // category display name
const sub=c=>LANG==='zh'?c.name_en:(c.name_zh||'');         // the secondary line under it
const T=(en,zh)=>LANG==='zh'?zh:en;                          // chrome string
const playName=p=>({'play-a':'A · Imaging/Path','play-b':'B · Genomics/AI','play-c':'C · GMP Edge'}[p]||p);

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
function goVendor(id){goTab('vendors');const q=$('#tab-vendors input[type=search]');const v=VBYID[id];if(q&&v){q.value=v.name;q.dispatchEvent(new Event('input'));}}
function goCategory(id){goTab('taxonomy');const ft=$('#fTxt');const c=CATBYID[id];if(ft&&c){ft.value=c.name_en;ft.dispatchEvent(new Event('input'));}}

// ---- header ----
$('#ver').textContent='taxonomy v'+DATA.taxonomy.version+' · '+DATA.taxonomy.status;
$('#built').textContent='Rendered from /data — '+DATA.built+' · '+DATA.taxonomy.categories.length+' categories · '+DATA.plays.plays.length+' plays · '+DATA.triggers.triggers.length+' triggers · '+DATA.accounts.length+' accounts';

// ---- tabs ----
const TABS=[['home','Home'],['taxonomy','Explore'],['hunt','Hunt'],['plays','Plays'],['triggers','Triggers'],['scoring','Scoring'],['accounts','Accounts'],['vendors','Vendors'],['leaderboards','Leaderboards']];
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

// ================= HOME (software universe by point-of-care stakeholder x AI) =================
const isAI=c=>(c.role||[]).includes('analytics-artificial-intelligence')||(c.data_modality||[]).includes('artificial-intelligence-models')||(c.hardware_profile||[]).includes('gpu-server');
function renderHome(){
  const root=$('#tab-home'); clear(root);
  const cats=DATA.taxonomy.categories;
  const hero=el('div',{class:'hero'});
  hero.append(el('h2',{},T('Who uses the software?','誰在用這些軟體?')));
  hero.append(el('p',{},T('The software universe by point-of-care stakeholder — each split AI-driven vs conventional (for now). Click a category to open it in Explore; hunt by hardware buyer & play there.','以照護現場的使用者切分軟體宇宙 — 每格再分 AI 驅動 vs 傳統(暫定)。點類別到 Explore 開啟;在那裡依硬體買家與 play 狩獵。')));
  root.append(hero);
  const lbLink=el('div',{class:'go',style:'cursor:pointer;margin:2px 0 14px'},T('🏆 See the market leaderboards — who leads AI vs conventional →','🏆 看市場榜單 — AI 對傳統誰領先 →'));lbLink.onclick=()=>goTab('leaderboards');root.append(lbLink);
  const GROUPS=[['facility',T('Facility','設施'),'🏥'],['doctor',T('Doctor','醫生'),'🩺'],
                ['nurse',T('Nurse','護理'),'🩹'],['patient',T('Patient','病人'),'🧑'],['other',T('Others','其他'),'⚙️']];
  const openCat=c=>{goTab('taxonomy');const ft=$('#fTxt');if(ft){ft.value=c.name_en;ft.dispatchEvent(new Event('input'));}};
  GROUPS.forEach(([key,label,icon])=>{
    const members=cats.filter(c=>c.home_stakeholder===key);
    if(!members.length)return;
    const ai=members.filter(isAI), noai=members.filter(c=>!isAI(c));
    root.append(el('div',{class:'section-title'},icon+' '+label+' · '+members.length+'  ('+T('AI','AI')+' '+ai.length+' · '+T('No-AI','非 AI')+' '+noai.length+')'));
    const grid=el('div',{class:'tiles'});
    [[T('AI-driven','AI 驅動'),ai,'playa'],[T('No-AI','非 AI'),noai,'playc']].forEach(([sub,list,cls])=>{
      const col=el('div',{class:'tile'});
      col.append(el('div',{class:'row'},el('span',{class:'play '+cls},sub),el('b',{},String(list.length))));
      list.slice().sort((a,b)=>b.hardware_opportunity-a.hardware_opportunity||a.id.localeCompare(b.id)).forEach(c=>{
        const row=el('div',{class:'cat',style:'cursor:pointer'},el('span',{},nm(c)),el('b',{title:'hardware opportunity'},'hw·'+c.hardware_opportunity));
        row.onclick=()=>openCat(c); col.append(row);
      });
      if(!list.length)col.append(el('div',{class:'muted',style:'font-size:12px;padding:4px 0'},'—'));
      grid.append(col);
    });
    root.append(grid);
  });
  const ex=el('div',{class:'go',style:'cursor:pointer;margin-top:18px'},T('Or hunt by hardware buyer & play in Explore / Hunt →','或到 Explore / Hunt 依硬體買家與 play 狩獵 →'));ex.onclick=()=>goTab('taxonomy');root.append(ex);
}

// ================= TAXONOMY =================
function renderTaxonomy(){
  const cats=DATA.taxonomy.categories, E=DATA.taxonomy.enums, root=$('#tab-taxonomy'); clear(root);
  const mk=(id,opts,label)=>{const s=el('select',{id});s.append(el('option',{value:''},label));
    opts.forEach(o=>s.append(el('option',{value:o},o)));return s;};
  const fBuyer=mk('fBuyer',['customer','operator','original-equipment-manufacturer','hyperscaler'],'all buyers'),
        fBucket=mk('fBucket',['on-prem','cloud'],'all substrate'),
        fSeg=mk('fSeg',E.segments,'all segments'),
        fPlay=mk('fPlay',['play-a','play-b','play-c'],'all plays'),
        fDep=mk('fDep',E.deployment,'all deployments'),
        fHw=mk('fHw',['1','2','3','4'],'opportunity ≥'),
        fProfile=mk('fProfile',['gpu-server','high-performance-computing-cpu','nvme-performance-storage','capacity-archive-storage','high-memory','edge-industrial','high-availability-redundant','disaster-recovery-backup'],'all hardware'),
        fGroup=mk('fGroup',['domain','primary_buyer','hardware_buyer','hardware_opportunity','hardware_profile','play','segment','data_modality','role','bucket'],'no grouping'),
        fSpansBox=el('input',{type:'checkbox'}),
        fTxt=el('input',{id:'fTxt',type:'search',placeholder:'search name / notes...'}),
        cnt=el('span',{class:'count'});
  const fSpans=el('label',{class:'ckbox'},fSpansBox,T('spans on-prem↔cloud','橫跨 on-prem↔雲'));
  const hotC=cats.filter(c=>(c.hardware_opportunity_by_buyer.customer||0)>=3).length,
        hotO=cats.filter(c=>(c.hardware_opportunity_by_buyer.operator||0)>=3).length,
        nOem=cats.filter(c=>(c.hardware_opportunity_by_buyer['original-equipment-manufacturer']||0)>=3).length;
  // ---- plain intro ----
  root.append(el('p',{class:'muted',style:'margin:2px 0 10px;font-size:13px'},
    T('Every category is tagged by who buys the hardware and how big the deal is. Click a shortcut below to jump straight to a ready target list, or pick a quick view to regroup all '+cats.length+' categories.',
      '每個類別都標好「誰買硬體、機會多大」。點下面的捷徑直接跳到現成目標清單,或選一個快速視角把全部 '+cats.length+' 類重新分組。')));
  // ---- clickable shortcut chips (hyperlink guidance to the HOT lists) ----
  const stats=el('div',{class:'statchips'});
  const chip=(n,txt,fn,cls)=>{const s=el('button',{class:'statchip '+(cls||'')});s.append(el('b',{},String(n)),el('span',{},txt));s.onclick=fn;return s;};
  const resetSel=()=>{[fBuyer,fBucket,fSeg,fPlay,fDep,fHw,fProfile].forEach(x=>x.value='');fSpansBox.checked=false;fTxt.value='';};
  stats.append(
    chip(hotC,'🎯 '+T('sell direct','直接銷售'),()=>window.exploreFilter('customer',3),'sc-cust'),
    chip(hotO,'🤝 '+T('ISV co-sell','ISV 共同銷售'),()=>window.exploreFilter('operator',3),'sc-oper'),
    chip(nOem,'🔩 '+T('OEM design-win','OEM 設計勝出'),()=>window.exploreFilter('original-equipment-manufacturer',3),'sc-oem'),
    chip(cats.length,'📋 '+T('show all','顯示全部'),()=>{hotFilter=null;resetSel();setGroup('domain');},'sc-all')
  );
  root.append(stats);
  root.append(el('div',{class:'legend'},
    T('Shortcuts = high-opportunity target lists (opportunity ≥ 3 of 4). Card badge = who buys the hardware:','捷徑 = 高機會目標清單(機會 ≥ 3/4)。卡片徽章 = 誰買硬體:'),
    el('span',{class:'dot',style:'background:var(--a)'}),T('customer','客戶'),
    el('span',{class:'dot',style:'background:var(--b)'}),T('operator (ISV)','營運者 (ISV)'),
    el('span',{class:'dot',style:'background:var(--c)'}),'OEM'));
  // ---- quick views: one-click regroup (replaces the cryptic group-by dropdown) ----
  const qv=el('div',{class:'statchips',style:'margin-top:8px'});
  qv.append(el('span',{class:'tagk',style:'align-self:center'},T('Quick views','快速視角')));
  function setGroup(g){hotFilter=null;fGroup.value=g;[...qv.querySelectorAll('.qv')].forEach(x=>x.classList.toggle('on',x.dataset.g===g));render();}
  [['domain',T('by care area','依照護領域')],['primary_buyer',T('by who buys','依誰買硬體')],['play',T('by play','依 play')],
   ['hardware_profile',T('by hardware','依硬體元件')],['data_modality',T('by data type','依資料型態')],['',T('flat list','平舖清單')]]
    .forEach(([g,lab])=>{const b=el('button',{class:'statchip qv','data-g':g},lab);b.onclick=()=>setGroup(g);qv.append(b);});
  root.append(qv);
  // ---- collapsible advanced filters, now each labeled ----
  const labeled=(lab,elm)=>el('label',{class:'flab'},el('span',{},lab),elm);
  root.append(el('details',{class:'refine'},el('summary',{},T('More filters','更多篩選')),
    el('div',{class:'filters'},
      labeled(T('who buys','誰買'),fBuyer),labeled(T('substrate','substrate'),fBucket),
      labeled(T('segment','客群'),fSeg),labeled(T('play','play'),fPlay),
      labeled(T('deployment','部署'),fDep),labeled(T('min opportunity','最低機會'),fHw),
      labeled(T('hardware component','硬體元件'),fProfile),
      el('div',{style:'display:flex;flex-direction:column;gap:4px;justify-content:flex-end'},fSpans,fTxt),cnt)));
  const host=el('div',{});root.append(host);
  function tagRow(k,arr){const r=el('div',{class:'row'});r.append(el('span',{class:'tagk'},k));
    (arr||[]).forEach(v=>r.append(el('span',{class:'chip dim'},v)));return r;}
  function card(c){
    const cd=el('div',{class:'card'});
    const pbP=c.hardware_opportunity_by_buyer[c.primary_buyer];
    const head=el('div',{class:'row'},el('span',{class:'hw hw'+c.hardware_opportunity,title:'hardware opportunity: '+OPP[c.hardware_opportunity]+' ('+c.hardware_opportunity+'/4)'},String(c.hardware_opportunity)),
      el('span',{class:'by '+BUYER_C[c.primary_buyer],title:'primary buyer '+c.primary_buyer+(pbP?' · '+OPP[pbP]+' opportunity':'')},c.primary_buyer+(pbP?'·'+pbP:'')));
    (c.hardware_buyer||[]).filter(x=>x!==c.primary_buyer).forEach(x=>head.append(el('span',{class:'byo',title:x+' buys iron'+(c.hardware_opportunity_by_buyer[x]?' · '+OPP[c.hardware_opportunity_by_buyer[x]]+' opportunity':'')},x+(c.hardware_opportunity_by_buyer[x]?'·'+c.hardware_opportunity_by_buyer[x]:''))));
    if(spansOf(c))head.append(el('span',{class:'byo',title:'deployment spans customer↔vendor'},'⇄'));
    (c.plays||[]).forEach(p=>head.append(el('span',{class:'play '+playClass(p)},playName(p).split(' ')[0])));
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
      c.vendors.forEach(v=>{const bd=lbBadge(v);const p=el('span',{class:'pill',style:'cursor:pointer'},(VNAME[v]||v)+(bd?' 🏆':''));
        p.title=bd?(T('market leader: ','市場領導 ')+bd+' — '+T('view vendor','看廠商')):T('view vendor','看廠商');p.onclick=()=>goVendor(v);vr.append(p);});
      cd.append(vr);}
    if(c.hospital_view){cd.append(tagRow(T('hosp-who','醫院·誰'),c.hospital_view.stakeholder));
      cd.append(tagRow(T('hosp-dim','醫院·面向'),c.hospital_view.dimension));}
    if(c.infrastructure_notes)cd.append(el('div',{class:'notes'},c.infrastructure_notes));
    if(c.play_exemption)cd.append(el('div',{class:'notes'},T('Outside play scope: ','play 範圍外:')+c.play_exemption));
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
    return (c[axis]||[]).slice();
  }
  let hotFilter=null;
  function render(){
    const by=fBuyer.value,bk=fBucket.value,sp=fSpansBox.checked,seg=fSeg.value,pl=fPlay.value,dep=fDep.value,
          hw=+fHw.value||0,prof=fProfile.value,gp=fGroup.value,q=fTxt.value.toLowerCase();
    const shown=cats.filter(c=>{
      if(hotFilter&&(c.hardware_opportunity_by_buyer[hotFilter.buyer]||0)<hotFilter.min)return false;
      if(by&&!c.hardware_buyer.includes(by))return false;
      if(prof&&!(c.hardware_profile||[]).includes(prof))return false;
      if(bk&&bucketOf(c)!==bk)return false;
      if(sp&&!spansOf(c))return false;
      if(seg&&!(c.segments||[]).includes(seg))return false;
      if(pl&&!(c.plays||[]).includes(pl))return false;
      if(dep&&!(c.deployment||[]).includes(dep))return false;
      if(hw&&c.hardware_opportunity<hw)return false;
      if(q&&!((c.name_en+' '+c.name_zh+' '+(c.infrastructure_notes||'')).toLowerCase().includes(q)))return false;
      return true;
    });
    clear(host);
    cnt.textContent=shown.length+' / '+cats.length+' shown'+(hotFilter?' · HOT_'+hotFilter.buyer+' (opp≥'+hotFilter.min+')':(gp?' · grouped by '+gp:''));
    if(!gp){const grid=el('div',{class:'grid'});shown.forEach(c=>grid.append(card(c)));host.append(grid);return;}
    const map=new Map();
    shown.forEach(c=>groupsOf(c,gp).forEach(k=>{if(!map.has(k))map.set(k,[]);map.get(k).push(c);}));
    let keys=[...map.keys()];
    if(gp==='hardware_opportunity')keys.sort((a,b)=>b-a);
    else keys.sort((a,b)=>map.get(b).length-map.get(a).length);
    keys.forEach(k=>{
      const label=gp==='hardware_opportunity'?('opportunity '+k+' ('+OPP[k]+')'):(gp==='play'?playName(k):k);
      host.append(el('div',{class:'grouphdr'},label,el('span',{class:'gcount'},String(map.get(k).length))));
      const grid=el('div',{class:'grid'});map.get(k).forEach(c=>grid.append(card(c)));host.append(grid);
    });
  }
  [fBuyer,fBucket,fSeg,fPlay,fDep,fHw,fProfile,fGroup].forEach(x=>x.onchange=()=>{hotFilter=null;render();});
  window.exploreFilter=function(buyer,minOpp){hotFilter={buyer:buyer,min:minOpp||3};fBuyer.value='';fBucket.value='';fSeg.value='';fPlay.value='';fDep.value='';fHw.value='';fProfile.value='';fSpansBox.checked=false;fTxt.value='';fGroup.value='';render();window.scrollTo(0,0);};
  fSpansBox.onchange=()=>{hotFilter=null;render();};fTxt.oninput=()=>{hotFilter=null;render();};setGroup('domain');
}

// ================= HUNT (per-play ranked target map) =================
function renderHunt(){
  const root=$('#tab-hunt'); clear(root);
  const cats=DATA.taxonomy.categories, plays=DATA.plays.plays;
  const VN={};(DATA.vendors.vendors||[]).forEach(v=>VN[v.id]=v.name);
  const opp=(c,b)=>c.hardware_opportunity_by_buyer[b]||0;
  const maxo=c=>Math.max(...Object.values(c.hardware_opportunity_by_buyer));
  const rig=c=>(c.hardware_profile||[]).map(h=>h+'·'+((c.hardware_profile_sizing||{})[h]||'?')).join('  ')||'—';
  root.append(el('div',{class:'rollup'},T('Per-play ranked target map — what to quote (component·scale) and who to co-sell with. Opportunity 1 minimal → 4 flagship. Full printable version: docs/hunting-guide.md','各 play 排序目標圖 — 報什麼(元件·規模)、和誰共同銷售。機會 1 微 → 4 旗艦。完整可列印版:docs/hunting-guide.md')));
  plays.forEach(p=>{
    const letter=p.id.split('-')[1].toUpperCase();
    const members=cats.filter(c=>(c.plays||[]).includes(p.id)).sort((a,b)=>maxo(b)-maxo(a)||opp(b,'customer')-opp(a,'customer'));
    root.append(el('div',{class:'grouphdr',id:'hunt-'+p.id},el('span',{class:'play play'+letter.toLowerCase()},'Play '+letter),p.name,el('span',{class:'gcount'},String(members.length))));
    members.forEach(c=>{
      const card=el('div',{class:'card'});card.style.marginBottom='8px';
      const head=el('div',{class:'row'},
        el('span',{class:'by bcust',title:'customer opportunity'},'cust·'+opp(c,'customer')),
        el('span',{class:'by boper',title:'operator opportunity'},'oper·'+opp(c,'operator')));
      if(opp(c,'original-equipment-manufacturer'))head.append(el('span',{class:'by boem'},'oem·'+opp(c,'original-equipment-manufacturer')));
      card.append(head);
      card.append(el('h3',{},nm(c)));
      const q=el('div',{class:'row'});q.append(el('span',{class:'tagk'},T('quote','報價')));(c.hardware_profile||[]).forEach(h=>q.append(el('span',{class:'hwc'},h+'·'+((c.hardware_profile_sizing||{})[h]||'?'))));
      if(c.hardware_profile&&c.hardware_profile.length)card.append(q);
      const v=el('div',{class:'row'});v.append(el('span',{class:'tagk'},T('vendors','廠商')));(c.vendors||[]).forEach(x=>v.append(el('span',{class:'pill'},VN[x]||x)));
      if(c.vendors&&c.vendors.length)card.append(v);
      root.append(card);
    });
  });
}

// ================= VENDORS (enriched registry) =================
function renderVendors(){
  const root=$('#tab-vendors'); clear(root);
  const vs=(DATA.vendors.vendors||[]).slice().sort((a,b)=>a.name.localeCompare(b.name));
  const conf=(DATA.vendors.version)||'?';
  const cnt=el('span',{class:'count'});
  const q=el('input',{type:'search',placeholder:T('search vendor / HQ / leader / category...','搜尋廠商 / 總部 / 負責人 / 類別...')});
  root.append(el('div',{class:'rollup'},T('Vendor registry v'+conf+' — '+vs.length+' vendors, web-researched + adversarially verified. Every claim sourced; unverifiable fields are honest nulls / "not publicly disclosed" (§8).','廠商登錄 v'+conf+' — '+vs.length+' 家,網路研究 + 對抗式查核。每項聲明有來源;查不到的欄位為誠實 null /「未公開揭露」(§8)。')));
  root.append(el('div',{class:'filters'},q,cnt));
  const host=el('div',{});root.append(host);
  function excl(v){return "exclud" in Object.assign({},v)?false:/exclud/i.test(v.note||'');}
  function card(v){
    const c=el('div',{class:'card'});c.style.marginBottom='8px';
    const h=el('div',{class:'row'},el('h3',{style:'margin:0'},v.name));
    const bd=lbBadge(v.id);
    if(bd){const lp=el('span',{class:'pill',style:'cursor:pointer;background:var(--accentbg);color:var(--accent);font-weight:700'},'🏆 '+bd);lp.title=T('on the market leaderboard — open','在市場榜單上 — 開啟');lp.onclick=()=>goTab('leaderboards');h.append(lp);}
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
    const shown=vs.filter(v=>!s||JSON.stringify([v.name,v.headquarters,v.leadership,v.market_position,v.market_share,(v.categories||[]).join(' ')]).toLowerCase().includes(s));
    clear(host);shown.forEach(v=>host.append(card(v)));
    cnt.textContent=shown.length+' / '+vs.length+T(' shown',' 顯示');
  }
  q.oninput=render;render();
}

// ================= PLAYS =================
function renderPlays(){
  const root=$('#tab-plays'); clear(root);
  const grid=el('div',{class:'grid'});root.append(grid);
  DATA.plays.plays.forEach(p=>{
    const letter=p.id.split('-')[1].toUpperCase();
    const card=el('div',{class:'card'});
    card.append(el('div',{class:'row'},el('span',{class:'play play'+letter.toLowerCase()},'Play '+letter)));
    card.append(el('h3',{},p.name));
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
function renderTriggers(){
  const root=$('#tab-triggers'); clear(root);
  const t=el('table');
  const TH=LANG==='zh'?['訊號','類別','急迫','窗口','來源','行動','關聯']:['Signal','Cat','Urgency','Window','Source','Action','Related'];
  t.append(el('thead',{},el('tr',{},...TH.map(h=>el('th',{},h)))));
  const tb=el('tbody');
  DATA.triggers.triggers.forEach(x=>{
    tb.append(el('tr',{},
      el('td',{},el('strong',{},x.signal)),
      el('td',{},el('span',{class:'pill'},x.category)),
      el('td',{},el('span',{class:'u '+x.urgency},x.urgency)),
      el('td',{class:'muted'},x.window),
      el('td',{class:'muted'},x.source),
      el('td',{},x.action),
      el('td',{},el('div',{class:'row'},
        ...(x.related_plays||[]).map(p=>el('span',{class:'play '+playClass(p)},playName(p).split(' ')[0])),
        ...(x.related_categories||[]).map(c=>el('span',{class:'pill'},c))))));
  });
  t.append(tb);root.append(el('div',{class:'wrap'},t));
}

// ================= SCORING =================
function renderScoring(){
  const root=$('#tab-scoring'); clear(root);
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
function renderAccounts(){
  const root=$('#tab-accounts'); clear(root);
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
function renderLeaderboards(){
  const root=$('#tab-leaderboards'); clear(root);
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
      row.append(el('div',{class:'row'},el('b',{style:'color:var(--accent);min-width:34px'},'#'+e.rank),nmEl));
      row.append(el('div',{class:'muted',style:'font-size:11px;margin:3px 0'},e.market_basis));
      if(e.source){const isurl=/^https?:\/\//.test(e.source);
        row.append(isurl?el('a',{href:e.source,target:'_blank',class:'pill'},T('source','來源')+' ↗'):el('span',{class:'pill'},String(e.source).slice(0,60)));}
      col.append(row);
    });
    wrap.append(col);
  });
  root.append(wrap);
}

// ================= i18n wiring: render all tabs + language toggle =================
const TAB_ZH={home:'首頁',taxonomy:'探索',hunt:'獵場',plays:'打法',triggers:'訊號',scoring:'評分',accounts:'帳號',vendors:'廠商',leaderboards:'榜單'};
function relabelTabs(){TABS.forEach(([id,label])=>{if(NAVBTN[id])NAVBTN[id].textContent=LANG==='zh'?(TAB_ZH[id]||label):label;});}
function renderAll(){renderHome();renderTaxonomy();renderHunt();renderPlays();renderTriggers();renderScoring();renderAccounts();renderVendors();renderLeaderboards();}
renderAll();
$('#langtog').onclick=()=>{LANG=(LANG==='zh')?'en':'zh';$('#langtog').textContent=(LANG==='zh')?'EN':'中文';relabelTabs();renderAll();window.scrollTo(0,0);};
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()

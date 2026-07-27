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
from datetime import datetime, timezone
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
        "accounts": accounts,
        "built": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
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
.tile .cat{display:flex;justify-content:space-between;gap:8px;font-size:12px;padding:4px 0;border-top:1px dashed var(--line)}
.tile .cat b{color:var(--ink)}
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
</style>
</head>
<body>
<header>
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
</main>
<script>
const DATA = /*__DATA__*/null;
const $ = (s,r=document)=>r.querySelector(s);
const el=(t,a={},...kids)=>{const n=document.createElement(t);
  for(const k in a){if(k==='class')n.className=a[k];else n.setAttribute(k,a[k]);}
  for(const c of kids)n.append(c&&c.nodeType?c:document.createTextNode(c));return n;};
const clear=n=>n.replaceChildren();
const playClass=p=>({'play-a':'playa','play-b':'playb','play-c':'playc'}[p]||'');
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

// ---- header ----
$('#ver').textContent='taxonomy v'+DATA.taxonomy.version+' · '+DATA.taxonomy.status;
$('#built').textContent='Rendered from /data — '+DATA.built+' · '+DATA.taxonomy.categories.length+' categories · '+DATA.plays.plays.length+' plays · '+DATA.triggers.triggers.length+' triggers · '+DATA.accounts.length+' accounts';

// ---- tabs ----
const TABS=[['home','Home'],['taxonomy','Explore'],['hunt','Hunt'],['plays','Plays'],['triggers','Triggers'],['scoring','Scoring'],['accounts','Accounts'],['vendors','Vendors']];
const nav=$('#nav');
const NAVBTN={};
function goTab(id){
  document.querySelectorAll('nav button').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));
  if(NAVBTN[id])NAVBTN[id].classList.add('on');
  const sec=$('#tab-'+id); if(sec)sec.classList.add('on');
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

// ================= HOME (guided funnel) =================
(function(){
  const root=$('#tab-home'), cats=DATA.taxonomy.categories, plays=DATA.plays.plays, trigs=DATA.triggers.triggers;
  const cust=c=>c.hardware_opportunity_by_buyer.customer||0, oper=c=>c.hardware_opportunity_by_buyer.operator||0;
  const oem=c=>c.hardware_opportunity_by_buyer['original-equipment-manufacturer']||0;
  const mx=c=>Math.max(...Object.values(c.hardware_opportunity_by_buyer));
  const hero=el('div',{class:'hero'});
  hero.append(el('h2',{},'Where do you want to hunt?'));
  hero.append(el('p',{},'Gate question first (§3): who controls the infrastructure behind the software? Pick a play to see its ranked hardware targets — what to quote and who to co-sell with — or act on a fired trigger.'));
  root.append(hero);
  const hc=cats.filter(c=>cust(c)>=3).length, ho=cats.filter(c=>oper(c)>=3).length, ho2=cats.filter(c=>oem(c)>=3).length;
  const bar=el('div',{class:'statbar'});
  [['HOT_customer',hc,'direct sale'],['HOT_operator',ho,'ISV / co-sell'],['OEM design-wins',ho2,'embedded per-unit']].forEach(([lab,n,sub])=>{
    const st=el('div',{class:'stat'},el('div',{class:'n'},String(n)),el('div',{class:'l'},lab+' · '+sub));
    st.onclick=()=>goTab('hunt'); bar.append(st);
  });
  root.append(bar);
  root.append(el('div',{class:'section-title'},'The three plays — pick your motion'));
  const tiles=el('div',{class:'tiles'});
  plays.forEach(p=>{
    const letter=p.id.split('-')[1].toUpperCase();
    const members=cats.filter(c=>(c.plays||[]).includes(p.id)).sort((a,b)=>mx(b)-mx(a)||cust(b)-cust(a)).slice(0,4);
    const t=el('div',{class:'tile'});
    t.append(el('div',{class:'row'},el('span',{class:'play play'+letter.toLowerCase()},'Play '+letter)));
    t.append(el('h3',{},p.name));
    t.append(el('div',{class:'anchor'},(p.hardware_anchor||[]).join(' · ')));
    members.forEach(c=>t.append(el('div',{class:'cat'},el('span',{},c.name_en.length>42?c.name_en.slice(0,42)+'…':c.name_en),el('b',{},'cust·'+cust(c)))));
    t.append(el('div',{class:'go'},'Open ranked targets →'));
    t.onclick=()=>goTab('hunt');
    tiles.append(t);
  });
  root.append(tiles);
  root.append(el('div',{class:'section-title'},'A trigger fired? — act on the window'));
  const tp=el('div',{class:'card'});
  const rank={critical:0,high:1,medium:2,low:3};
  trigs.slice().sort((a,b)=>rank[a.urgency]-rank[b.urgency]).slice(0,4).forEach(t=>{
    tp.append(el('div',{class:'trigrow'},el('span',{class:'u '+t.urgency},t.urgency),el('b',{},t.signal),
      el('span',{class:'muted'},'→ '+(t.related_categories||[]).slice(0,3).join(', '))));
  });
  const more=el('div',{class:'go',style:'cursor:pointer;margin-top:8px'},'All 14 triggers →');more.onclick=()=>goTab('triggers');tp.append(more);
  root.append(tp);
  const ex=el('div',{class:'go',style:'cursor:pointer;margin-top:18px'},'Or browse & filter all 53 categories in Explore →');ex.onclick=()=>goTab('taxonomy');root.append(ex);
})();

// ================= TAXONOMY =================
(function(){
  const cats=DATA.taxonomy.categories, E=DATA.taxonomy.enums, root=$('#tab-taxonomy');
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
  const fSpans=el('label',{class:'ckbox'},fSpansBox,'spans boundary');
  root.append(el('details',{class:'refine'},el('summary',{},'Refine — filters & grouping'),el('div',{class:'filters'},fBuyer,fBucket,fSeg,fPlay,fDep,fHw,fProfile,fGroup,fSpans,fTxt,cnt)));
  // static buyer rollup summary (authoritative axis)
  const pb={customer:0,operator:0,'original-equipment-manufacturer':0,hyperscaler:0};cats.forEach(c=>pb[c.primary_buyer]++);
  const hotC=cats.filter(c=>(c.hardware_opportunity_by_buyer.customer||0)>=3).length,
        hotO=cats.filter(c=>(c.hardware_opportunity_by_buyer.operator||0)>=3).length,
        nOem=cats.filter(c=>c.hardware_buyer.includes('original-equipment-manufacturer')).length;
  const sum=el('div',{class:'rollup'});
  sum.append('Hardware-buyer rollup (§3 gate — WHO buys the iron): primary ',
    el('b',{},String(pb.customer)),' customer · ',el('b',{},String(pb.operator)),' operator. ',
    el('b',{},String(hotC)),' HOT_customer (direct) · ',
    el('b',{},String(hotO)),' HOT_operator (ISV co-sell) · ',
    el('b',{},String(nOem)),' OEM design-wins. Badge = primary buyer (green customer / purple operator / orange OEM). Opportunity scale 1 minimal · 2 modest · 3 significant · 4 flagship.');
  root.append(sum);
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
    cd.append(el('h3',{},c.name_en));
    cd.append(el('div',{class:'zh'},c.name_zh));
    const segr=el('div',{class:'row'});(c.segments||[]).forEach(s=>segr.append(el('span',{class:'chip'},s)));
    cd.append(segr);
    cd.append(tagRow('lifecycle',c.lifecycle));
    cd.append(tagRow('role',c.role));
    cd.append(tagRow('data',c.data_modality));
    cd.append(tagRow('deploy',c.deployment));
    if(c.hardware_profile&&c.hardware_profile.length){const hr=el('div',{class:'row'});hr.append(el('span',{class:'tagk'},'hardware'));c.hardware_profile.forEach(h=>hr.append(el('span',{class:'hwc',title:'deployment scale'},h+((c.hardware_profile_sizing||{})[h]?' · '+c.hardware_profile_sizing[h]:''))));cd.append(hr);}
    if(c.vendors&&c.vendors.length){const vr=el('div',{class:'row'});vr.append(el('span',{class:'tagk'},'vendors'));c.vendors.forEach(v=>vr.append(el('span',{class:'pill'},VNAME[v]||v)));cd.append(vr);}
    if(c.hospital_view){cd.append(tagRow('hosp-who',c.hospital_view.stakeholder));
      cd.append(tagRow('hosp-dim',c.hospital_view.dimension));}
    if(c.infrastructure_notes)cd.append(el('div',{class:'notes'},c.infrastructure_notes));
    if(c.play_exemption)cd.append(el('div',{class:'notes'},'Outside play scope: '+c.play_exemption));
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
  function render(){
    const by=fBuyer.value,bk=fBucket.value,sp=fSpansBox.checked,seg=fSeg.value,pl=fPlay.value,dep=fDep.value,
          hw=+fHw.value||0,prof=fProfile.value,gp=fGroup.value,q=fTxt.value.toLowerCase();
    const shown=cats.filter(c=>{
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
    cnt.textContent=shown.length+' / '+cats.length+' shown'+(gp?' · grouped by '+gp:'');
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
  [fBuyer,fBucket,fSeg,fPlay,fDep,fHw,fProfile,fGroup].forEach(x=>x.onchange=render);
  fSpansBox.onchange=render;fTxt.oninput=render;fGroup.value='domain';render();
})();

// ================= HUNT (per-play ranked target map) =================
(function(){
  const root=$('#tab-hunt'), cats=DATA.taxonomy.categories, plays=DATA.plays.plays;
  const VN={};(DATA.vendors.vendors||[]).forEach(v=>VN[v.id]=v.name);
  const opp=(c,b)=>c.hardware_opportunity_by_buyer[b]||0;
  const maxo=c=>Math.max(...Object.values(c.hardware_opportunity_by_buyer));
  const rig=c=>(c.hardware_profile||[]).map(h=>h+'·'+((c.hardware_profile_sizing||{})[h]||'?')).join('  ')||'—';
  root.append(el('div',{class:'rollup'},'Per-play ranked target map — what to quote (component·scale) and who to co-sell with. Opportunity 1 minimal → 4 flagship. Full printable version: docs/hunting-guide.md'));
  plays.forEach(p=>{
    const letter=p.id.split('-')[1].toUpperCase();
    const members=cats.filter(c=>(c.plays||[]).includes(p.id)).sort((a,b)=>maxo(b)-maxo(a)||opp(b,'customer')-opp(a,'customer'));
    root.append(el('div',{class:'grouphdr'},el('span',{class:'play play'+letter.toLowerCase()},'Play '+letter),p.name,el('span',{class:'gcount'},String(members.length))));
    members.forEach(c=>{
      const card=el('div',{class:'card'});card.style.marginBottom='8px';
      const head=el('div',{class:'row'},
        el('span',{class:'by bcust',title:'customer opportunity'},'cust·'+opp(c,'customer')),
        el('span',{class:'by boper',title:'operator opportunity'},'oper·'+opp(c,'operator')));
      if(opp(c,'original-equipment-manufacturer'))head.append(el('span',{class:'by boem'},'oem·'+opp(c,'original-equipment-manufacturer')));
      card.append(head);
      card.append(el('h3',{},c.name_en));
      const q=el('div',{class:'row'});q.append(el('span',{class:'tagk'},'quote'));(c.hardware_profile||[]).forEach(h=>q.append(el('span',{class:'hwc'},h+'·'+((c.hardware_profile_sizing||{})[h]||'?'))));
      if(c.hardware_profile&&c.hardware_profile.length)card.append(q);
      const v=el('div',{class:'row'});v.append(el('span',{class:'tagk'},'vendors'));(c.vendors||[]).forEach(x=>v.append(el('span',{class:'pill'},VN[x]||x)));
      if(c.vendors&&c.vendors.length)card.append(v);
      root.append(card);
    });
  });
})();

// ================= VENDORS (enriched registry) =================
(function(){
  const root=$('#tab-vendors'), vs=(DATA.vendors.vendors||[]).slice().sort((a,b)=>a.name.localeCompare(b.name));
  const conf=(DATA.vendors.version)||'?';
  const cnt=el('span',{class:'count'});
  const q=el('input',{type:'search',placeholder:'search vendor / HQ / leader / category...'});
  root.append(el('div',{class:'rollup'},'Vendor registry v'+conf+' — '+vs.length+' vendors, web-researched + adversarially verified. Every claim sourced; unverifiable fields are honest nulls / "not publicly disclosed" (§8).'));
  root.append(el('div',{class:'filters'},q,cnt));
  const host=el('div',{});root.append(host);
  function excl(v){return "exclud" in Object.assign({},v)?false:/exclud/i.test(v.note||'');}
  function card(v){
    const c=el('div',{class:'card'});c.style.marginBottom='8px';
    const h=el('div',{class:'row'},el('h3',{style:'margin:0'},v.name));
    if(/exclud/i.test(v.note||''))h.append(el('span',{class:'pill'},'§5.4 co-sell excluded'));
    c.append(h);
    const kv=el('dl',{class:'kv'});
    const add=(k,x)=>{if(x==null||x==='')return;kv.append(el('dt',{},k),el('dd',{},String(x)));};
    add('HQ',v.headquarters); add('Founded',v.founded); add('Leadership',v.leadership);
    add('Market position',v.market_position); add('Deployment',(v.deployment_models||[]).join(', '));
    c.append(kv);
    const seg=el('div',{class:'row'});(v.categories||[]).forEach(x=>seg.append(el('span',{class:'chip'},x)));c.append(seg);
    if(v.history)c.append(el('div',{class:'notes'},v.history));
    const srcs=(v.sources&&v.sources.length)?v.sources:(v.source?[v.source]:[]);
    if(srcs.length){const sr=el('div',{class:'row'});sr.append(el('span',{class:'tagk'},'sources'));
      srcs.forEach(u=>{const isurl=/^https?:\/\//.test(u);
        sr.append(isurl?el('a',{href:u,target:'_blank',class:'pill'},u.replace(/^https?:\/\//,'').split('/')[0]):el('span',{class:'pill'},u.slice(0,40)));});
      c.append(sr);}
    return c;
  }
  function render(){
    const s=q.value.toLowerCase();
    const shown=vs.filter(v=>!s||JSON.stringify([v.name,v.headquarters,v.leadership,v.market_position,(v.categories||[]).join(' ')]).toLowerCase().includes(s));
    clear(host);shown.forEach(v=>host.append(card(v)));
    cnt.textContent=shown.length+' / '+vs.length+' shown';
  }
  q.oninput=render;render();
})();

// ================= PLAYS =================
(function(){
  const root=$('#tab-plays'),grid=el('div',{class:'grid'});root.append(grid);
  DATA.plays.plays.forEach(p=>{
    const letter=p.id.split('-')[1].toUpperCase();
    const card=el('div',{class:'card'});
    card.append(el('div',{class:'row'},el('span',{class:'play play'+letter.toLowerCase()},'Play '+letter)));
    card.append(el('h3',{},p.name));
    const sec=(t,arr)=>{card.append(el('div',{class:'tagk'},t));
      const ul=el('ul',{class:'muted'});(arr||[]).forEach(x=>ul.append(el('li',{},x)));
      ul.style.margin='4px 0 8px';ul.style.paddingLeft='18px';ul.style.fontSize='12px';card.append(ul);};
    sec('workloads',p.workloads);
    sec('target segments',p.target_segments);
    sec('hardware anchor',p.hardware_anchor);
    if(p.regulatory_notes)card.append(el('div',{class:'notes'},'reg: '+p.regulatory_notes));
    grid.append(card);
  });
})();

// ================= TRIGGERS =================
(function(){
  const root=$('#tab-triggers');
  const t=el('table');
  t.append(el('thead',{},el('tr',{},...['Signal','Cat','Urgency','Window','Source','Action','Related'].map(h=>el('th',{},h)))));
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
})();

// ================= SCORING =================
(function(){
  const root=$('#tab-scoring');
  root.append(el('h3',{},'Model - '+SC.items.reduce((s,i)=>s+i.weight,0)+' pts - '+SC.formula));
  const mt=el('table');mt.append(el('thead',{},el('tr',{},el('th',{},'Item'),el('th',{},'Weight'))));
  const mb=el('tbody');SC.items.forEach(i=>mb.append(el('tr',{},el('td',{},i.label),el('td',{},String(i.weight)))));
  mt.append(mb);root.append(el('div',{class:'wrap'},mt));
  const tr=el('div',{class:'row'});tr.style.margin='14px 0';
  TIERS.slice().reverse().forEach(t=>tr.append(el('span',{class:'tierbadge',style:'background:'+tierColor(t.name)},t.name+' >='+t.min)));
  root.append(el('div',{},el('div',{class:'tagk'},'tiers'),tr));
  root.append(el('h3',{},'Try it'));
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
})();

// ================= ACCOUNTS =================
(function(){
  const root=$('#tab-accounts');
  if(!DATA.accounts.length){root.append(el('div',{class:'muted'},'No accounts in data/accounts/ yet.'));return;}
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
    add('Segment',a.segment);
    add('Software',a.software&&(a.software.domain||''));
    add('Deployment',a.deployment);add('Operator',a.operator);
    add('Trigger',a.trigger&&(a.trigger.detail||a.trigger.id));
    add('Infra control',a.infrastructure_control);
    add('Next step',a.next_step);
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
      card.append(el('div',{class:'notes'},'Evidence: '+ev.length+' claim(s), confidence '+[...new Set(confs)].join('/')+(confs.length&&confs.every(c=>c==='D')?' - all inference, verify before pursuit':'')));
    }
    root.append(card);
  });
})();
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()

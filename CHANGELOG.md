# CHANGELOG

## 2026-08-11 — vendor page a11y/UX: keyboard scan + sticky group headers + zero-state (impeccable critique) + v5.0
Ran an impeccable **dual-agent critique** of the Vendors page (Design Health 26/40; detector 0 slop). Implemented the top findings:
- **[P1] Keyboard scan** — the vendor list is now a `listbox` (role=listbox/option, tabindex, aria-selected); Arrow ↑/↓ moves the selection and streams the right-pane profile, Enter confirms, the selected row scrolls into view. The 309-row triage is no longer mouse-only.
- **[P1] Sticky grouped headers** — `.vghdr` is `position:sticky` within the list scroll container, so "ISV · 244" stays pinned while scanning that group.
- **[P2] Zero-result recovery** — filtering to no matches now renders an empty-state block with an inline **"Clear filters"** button (+ a detail-pane placeholder) instead of a silent double blank.
- **Recognition** — list-row flagship/HOT badges gained tooltips, and the flagship badge now reads "N flagship" (not a bare "F" that collided with the Fortune filter).
- 122 tests green; app=docs; impeccable detector clean; browser-verified (↓↓ Philips→GE HealthCare, profile-synced; sticky header; partner-type=reseller → 0 → empty+Clear → recovers to 309); no emoji. **v5.0.**

## 2026-08-10 — vendor page → browsable list + rich profile (two-pane) + v4.9
Tuo: the per-vendor card was both bare (陽春) and crowded (擁擠) — a wide card cramming shallow facts. Restructured the registry into **a scannable list + a spacious detail profile** (like Explore's tree→battle-card): a compact left list (name · partner-type · flag/HOT · richness · 2-line summary, honouring the group/filter/sort), click any vendor → a full-width right profile with room to breathe. Added an **SMCI hardware pull** section to the profile (the sell hook, un-陽春) — the SMCI boxes + compute classes the vendor's software footprint pulls (HGX/MGX GPU · NVMe · archive · edge · HA pairs …) with flagship/HOT counts, derived from its categories. Two-pane collapses to a single column on mobile. 122 tests green; app=docs; browser-verified (wide 1500px: list 44→486 + profile 502→1441 with the hardware-pull section; mobile 390px: single column, 0 overflow, no console errors). **v4.9.**

## 2026-08-10 — vendor registry: group-by partner-type / richness + v4.8
Tuo: group vendors by partner-type. Added a GROUP control to the registry (none / partner-type / data-richness) beside SORT. Grouping renders a sticky group header per bucket — e.g. **"ISV · 244 — co-sell / OEM / reference architecture"**, **"OEM/Device · 58 — embedded BOM"**, SI · 4, MSP · 2, Channel · 1 — each carrying its SMCI motion, groups ordered by the GTM order, cards inside sorted by the active sort. Browser-verified. 122 tests green; app=docs. **v4.8.**

## 2026-08-10 — vendor page: partner-type classification + data-richness + card redesign + v4.7
Tuo: the vendor card is too cramped / feels thin, and wanted vendors classified by GTM partner-type (ISV / VAR / SI / MSP / channel-partner / reseller) + data richness. (Data wasn't actually sparse — every vendor has HQ/history/market-position/sources/listing; the card layout was crushing it, and partner-type was missing.)
- **partner_type** (new web-verified public fact) — an 11-agent sweep (10 classify + 1 QA, grounded in our vendor context + web) tagged all **309** vendors, multi-tag, from the view of how SMCI engages them: **244 ISV · 58 OEM/device · 4 SI · 2 MSP · 1 channel** (86 multi-tag; 182 confidence-B). Each carries `{primary, also[], confidence}` in vendors.yaml.
- **Card redesign** — replaced the crushed kv-dump with a sectioned layout: header + a tag strip (partner-type · listing · Fortune · US-share · neuro · richness), a compact one-line spec strip (HQ · Region · Founded · Deploy · Lead), an **SMCI-motion** line per partner-type, and prose sections with headers + breathing room (Market position / Market share / Coverage / Software categories / About / **Partnerships** [now surfaced] / Sources).
- **Data-richness tier** (derived: rich / medium / sparse from field completeness) — a badge on each card + a filter to find enrichment targets.
- **Filters** — added Partner-type + Data-richness to the vendor filter bar (both drive the registry + bundle ranking).
- 12x+ tests green (+partner-type lock-in); app=docs; browser-verified (Philips → OEM/Device+ISV pills + "SMCI motion: embedded BOM"; partner-type filter oem-device = 69/309; sectioned card fills cleanly), no emoji. **v4.7.**

## 2026-08-10 — fix: narrow-viewport dead space / overflow (responsive) + v4.5
Tuo flagged idiotic left/right dead space + messy layout on a narrow view. Root cause: several grids used `minmax(340px/430px/300px, 1fr)` — a hard min-width WIDER than a narrow viewport, so the content overflowed and the page couldn't shrink (min-content-width ~360px), leaving dead space + cramming below that. Real phones (≥390px) were fine; it broke on very narrow widths (the preview pane / a narrowed window). Fixes, desktop untouched:
- `minmax(Npx,1fr)` → `minmax(min(Npx,100%),1fr)` on `.grid` (340), `.tiles` (300), the leaderboard grid (430), and `.ptbl` — columns can now shrink below their min instead of forcing overflow.
- `main` side padding `22px` → `clamp(12px,4vw,22px)` — reclaims side space on narrow screens, stays 22px on desktop.
- Verified: at 158–350px content fills the full width, 0 overflow elements, 0 horizontal scroll; at desktop padding + grids are unchanged. 120 GREEN; app=docs. **v4.5.**

## 2026-08-10 — P2 declutter: token system (type ramp) + structural edits (design workflow) + v4.4
Ran a 4-agent P2 design-system workflow (3 diverse token proposals — compact / balanced / airy → 1 judge, grounded in the real CSS value inventory: 12 gaps · 12 radii · 19 font-sizes · 26 pill classes). Verified key fact: **0 pre-existing `--s*` usages** — the scale was defined-but-dead, so redefining it moves nothing until each ad-hoc px is migrated. Landed the full structural + token migration of P2:
- **Unified `:root` token set** — spacing `--s0..--s6` (2/4/6/8/12/16/24), radius `--r-tag/card/pill/dot`, type ramp `--f-1..--f-6` + `--f-d1..d3`. (Verified fact: 0 pre-existing `--s*` usages — the scale was defined-but-dead.)
- **Full value migration to tokens: 397 swaps** — font-size 140 (19 distinct → 9, every half-px gone; the five "big number" sizes collapse to one `--f-d2`), gap 66, padding 130, border-radius 61 (12 radii → 4 roles: tag 6 / card 12 / pill 999 / dot; `.battle`/`.sfstage` panels kept at `--r-card`). Pill SHAPE now reads as 2 families (round 999 vs square 6) straight from the radius tokens.
- **Bug caught + fixed:** the first gap/padding migration script used the wrong regex group and blanked every value (`gap:;`). Caught on browser inspection, reverted build_app.py to HEAD, replayed all P2 edits cleanly, re-ran a corrected migration; verified 0 empty declarations, 0 collapsed gaps, tokens resolve on real elements.
- **Content edits**: view-by 6→4 (dropped AI/no-AI — already an auto L2 sub-header — + hardware, compute's coarser twin); Compute-door **`★` glyph → bold number + "flagship"** (fixes the no-pictograph rule); deleted the **dead taxonomy `card()`+`tagRow()`** (~30 lines, incl a stray `⇄` glyph); matrix ranked rows drop listing/neuro pills (filter axes, not ranking factors); category ladder folded to **Who-uses only**, with Purpose/Flow/Tech in the renamed **"How this category works"** drawer.
- **Overrode one subagent over-reach**: kept the compute-class + neuro pill COLOURS (the axes Tuo values) instead of neutralizing them; demoted only the buyer axis.
- **Held** (only): the 26→2 pill-class *rename* — pure code-hygiene; the visual 2-family outcome is already achieved by the radius tokens, and the rename would touch every pill emit in the JS for no visual gain.
- **120 GREEN**; app=docs byte-identical; browser-verified (head 3 pills, tiers 1, drawer renamed, view-by 4, filters 4, no `★`, compute colour kept, gap/radius/font tokens resolve on real elements, zero collapsed gaps, zero console errors), no emoji. **v4.4.**

## 2026-08-10 — declutter pass: category card + Explore controls (design workflow) + v4.3
Tuo: layout still too cluttered — asked me to design a workflow to improve it. Ran a 6-agent **design-declutter workflow** (5 diverse design critics grounded in the live-DOM element inventory + reading build_app.py → 1 synthesizer, adversarially signal-guarded). 39 findings → a 13-item ranked plan. Implemented **P0+P1** (every cut preserves the fact in data / hover / a sibling surface):
- **Category head 7→3 pills** (opportunity · play · compute). The weak buyer axis (near-universal co-sell) is off the head — it stays in the plain-language **motion sentence** + the tree colour dot.
- **Battle card 3→2 rows**: folded "Compute · SMCI box" into **"Reference arch · SMCI box"** (SMCI families + a compute-SKU + GPU/no-GPU chip). compute_class now shows **2×** (head glance + ref-arch), was 4-5×.
- **6-tier ladder → 4-tier** (dropped the Hardware + SMCI-workload tiers — byte-identical to the ref-arch row).
- **Explore controls**: view-by **7→6** (removed the buyer group), More-filters **8→4** (kept substrate / segment / min-opp / compute; dropped play / deployment / hardware-component / spans — each duplicates a launcher door or a demoted axis). Filter objects kept + wired; DOM-only removal.
- **Vendor card**: dropped the duplicate **Fortune + Listing** header pills (both already in the kv rows with parent / ticker / evidence).
- Skipped the buyer-colour recolor (plan rank 7) — it conflicted with keeping the tree buyer dot, and the prominent buyer colour already left with the head pill. Held **P2** (spacing/type system, tier→drawer fold, dead-code removal) for a later pass.
- **120 GREEN**; app=docs byte-identical; browser-verified (head 7→3, battle 3→2, tiers 6→4, view-by 7→6, filters 8→4, motion still carries buyer, vendor pills deduped, zero console errors), no emoji. **v4.3.**

## 2026-08-10 — compute_class lens: GPU vs CPU-workstation vs CPU-server, per play + v4.2
Tuo: the hardware_buyer axis (customer/operator/oem) is weak — with near-universal vendor co-sell, "who buys the iron" carries ~no signal; the axis that decides which SKU you walk in with is **what iron the software pulls**. Integrate that into the site, split the CPU side into two tiers (workstation vs server).
- **`compute_class`** — derived (no new data) from `workload_envelope.gpu_role` + `hardware_profile` + sizing: `cpu-workstation · gpu-mixed · gpu · cpu-db (OLTP) · cpu-edge · storage · saas-light`. Two CPU tiers kept separate per request: **cpu-workstation** (single/small node, no GPU) vs **cpu-server** (DB/OLTP + edge).
- **Surfaced as a first-class Explore lens**: a group-by **compute type**, a **compute type (SKU)** filter, a per-category badge + a **"Compute · SMCI box"** battle-card row (SMCI box + no-GPU marker), a launcher **"Compute (SKU)" door** (chips per class → filter + regroup by play; chip number = **★flagship · direct-HOT** = deal size + can-we-direct-sell, deliberately NOT raw category count, which over-weights low-value buckets — saas-light ★0·0 and cpu-db ★1 look big by count but carry ~no flagship deals), and a **per-play compute split** in every play brief (the GPU vs CPU parts of each play).
- **Finding surfaced:** pure CPU-workstation is thin (5/59) and plays A/C/D carry zero; the broad CPU volume is **CPU-server DB/OLTP (14, Play D)**. **3 of the 5** workstation categories are play-orphans (payer actuarial/fraud + pop-health) — the rejected "Play E payer" crowd — flagged as a cross-cutting **CPU-Workstation Analytics** group candidate (not a new play).
- **120 GREEN** (+4 compute-class lock-in, distribution frozen: workstation 5 · GPU 22 · DB 14); deterministic; app=docs byte-identical; browser-verified (door → "5/59 shown" grouped by play, `exploreCompute` live, zero console errors), no emoji. **v4.2.**

## 2026-08-10 — vendor public-listing status + brain/neuro flag (web-verified) + v4.1
Tuo: reflect the verified findings from the sales workbook into the live project. Added two web-verified, **public-fact** dimensions to every one of the 309 vendors in `data/vendors.yaml` (no SMCI-internal lead data — that stays in git-ignored `/private/`):
- **`listing`** — public / private / subsidiary_of_public / subsidiary_of_private / acquired / nonprofit_or_gov, with `ticker`, `parent`, `confidence` (A–D), and a `source` per §8. Resolved via two adversarial-verify Workflow sweeps (15-agent for 131 unknowns, 10-agent for 40 low-confidence D guesses): each "public" verdict's ticker was independently confirmed to map to the exact issuer (name+HQ), refute-default. Result: **0 unknown, 0 D** — 132 listed-side (public / listed-parent), 167 private-side, 8 acquired, 2 nonprofit/gov; 115 confidence-B (SEC/exchange/IR primary), 194 C. Caught 14 that were wrongly "unknown" but are in fact public (Certara NASDAQ:CERT, ICON ICLR, QIAGEN QGEN, Veradigm MDRX, Sectra STO:SECT-B, Tecsys TSX:TCS, …).
- **`neuro`** — brain / neuro / stroke / neurosurgery focus. A full 309-vendor scan grew the set 4→**8** (added Elekta/Gamma-Knife radiosurgery, Annalise.ai head-CT, Aidoc ICH+stroke, Nanox.AI intracranial). The same scan confirmed **zero** implantable brain-chip (BCI) makers — correct for a software registry.
- **App**: `listedOf` / `neuroOf` helpers, a listing badge (上市 · TICKER / 私有 / 母公司上市) + neuro tag on each vendor card, the listing verification URL added to the card's clickable sources, and **two new shared filters** (上市／私有 · 神經) that drive both the registry and the bundle ranking. Registry rollup text updated.
- **116 GREEN** (+6 listing/neuro lock-in tests); deterministic; app=docs byte-identical; browser-verified both languages (badges, `神經` filter 309→8, EN/中文 toggle intact), no emoji. **v4.1.**

## 2026-07-30 — Method→learn page, layout/drawer cleanup, single search, premium instrument pass + v3.9
A tuning session (on an `experiment` branch, then merged) driven by Tuo's feedback + /hyakushikiflow + /darwin-combo + /grill-me + /impeccable.
- **Method → "How to use this map."** The old plays/signals/scoring/accounts sub-nav (which duplicated Explore and confused newcomers, and included a fictional demo account that contradicted the map-not-accounts goal) was replaced by a single teaching page: a static **system-flow diagram** (① Universe → ② Door → ③ Battle card → ④ Deal, each click-jumps into Explore via a new `window._exp` bridge), the three signals, the four doors, a worked walkthrough, the four bets, and a folded plain-language scoring aside. Removed the fictional account; deleted 127 lines of now-dead render functions.
- **Layout / flow (impeccable `layout` pass).** The launcher was a ~2.5-screen wall of always-open lists; folded the **Product-line** and **Trigger** lists into closed drawers (workspace top moved 1900px→798px), and folded the battle card's **duplicate prose** into a "Full explainer" drawer (the 6-tier diagram + action block stay open).
- **Single search.** Removed the duplicate toolbar search; the one prominent launcher input is now the canonical `#fTxt` that `render()` reads.
- **Tree auto-collapse.** Category-tree groups collapse by default when browsing many; the group holding the selected category auto-opens; narrowing (search/door) re-opens.
- **Premium-instrument pass (impeccable, grill-me plan).** Register = professional-instrument. Palette moved to **OKLCH** with all semantic hues on **one lightness shelf** (cohesive, not a rainbow) + cool-tinted neutrals + one blue accent + dark-mode variants; **tabular lining numerals** everywhere (columns/bars stop jittering) + antialiasing + a 4pt spacing scale + unified row density; **functional micro-motion** only (140ms ease-out, focus-visible ring, `prefers-reduced-motion` honored). Elevated the battle-card hero. **Fixed two side-stripe AI-slop violations** (tier6 2px rail → 1px; `.mleg` legend 3px stripe → full subtle border + colored label) — the impeccable detector now returns **`[]`** (zero slop).
- **101 GREEN** (+4 lock-in tests); deterministic; app=docs byte-identical; browser-verified both languages, desktop + mobile, zero console errors, no emoji.
- **Tagged `v3.9`.**

## 2026-07-29 — researched the remaining 169 non-leaderboard vendors + v3.8
Tuo: research the rest too. Ran the same verified pipeline on all 169 non-leaderboard vendors → 25 share candidates + **135 with partnerships**. After the same reality-check curation (kept 12, rejected/skipped the rest), the registry now has **245/309 vendors with partnerships and 45 with a cited market share** (the remaining 64 genuinely have no public partner/share — left blank, not fabricated).
- **Kept 12** genuine market-share figures: Nuance 80% (US radiology speech-rec), Rockwell 50% (NA PLC), Elekta 42% (linac), Hamamatsu 40% (PMT), ICON 35% (decentralized trials), OPTEL 25.7% (serialization), TeleTracking 17% (patient throughput), Amwell 13.7% (telehealth), ScriptPro 13% (pharmacy automation), Cognex 11.4% (machine vision), Canon Medical 8.7% (imaging), athenahealth-2 7.5%.
- **Rejected/skipped:** adoption ("Wolters Kluwer UpToDate — 90% of AMCs *use* it"), reach ("Advarra — 60% of NA *trials*"), market-mismatch (Cadence 30% EDA vs its OpenEye comp-chem role; Medtronic 5.8% whole-conglomerate), tech-tracker precision (UKG 7.81%, Manhattan 4.85%), and 7 vendors that already carried a share figure — **never overwritten** (e.g. ABB kept its 19% DCS, not the new 13% robotics).
- Co-sell payoff, e.g. Play C / SCADA-DCS: every industrial vendor's NVIDIA + cloud ties are now visible — ABB→NVIDIA, Rockwell→NVIDIA+Azure, Siemens→NVIDIA+MS+AWS, AVEVA→AWS+Azure.
- **97 GREEN**; deterministic; browser-verified (DOM), zero console errors, no emoji. **Tagged `v3.8`.**

## 2026-07-29 — researched vendor market share + partnerships; Back nav + a partner-landscape drawer + v3.6/v3.7
Three asks from Tuo: fill the "未公開" market-share gaps (with sources), add a back button, and surface each vendor's peer ranking + who they partner with.
- **Back navigation (v3.6):** every drill-down (door → brief → battle card; play chip ⇄ trigger chip ⇄ category) now pushes a `{catFilter, detail-view}` snapshot onto a nav stack; a sticky "← Back" button pops it and restores the prior view. Verified: PlayD → trigger → market, Back → trigger brief, Back → play brief.
- **Researched the data (v3.7):** a 12-agent web-research workflow covered all 133 leaderboard vendors lacking a share figure → 25 market-share candidates + **110 vendors with partnerships**, every claim carrying a source.
- **Verified, didn't trust (TUo Brain #1/#3):** reality-checking the 25 share figures exposed that agents conflated **adoption/reach with market share** (OpenEvidence "65% of physicians use it", FinThrive, Phreesia, Optum-Change reach) and leaned on **unreliable tech-trackers** (Enlyft/6sense: epic-beaker 35.29%, greenway 0.19%, orchard, solutionreach), plus a **wrong-product mislabel** (meditech-expanse-laboratory got MEDITECH's *EHR* share) and **market-mismatch cloud share** (Microsoft/Google). **Kept 13** genuine market-share figures (eClinicalWorks 13.9, athenahealth 7.5, McKesson 33, Optum 23, CompuGroup 19.5 [DE], Arxium 19.1, Philips 15, Clinisys 9.2, Sectra 25, Abridge 30, Oracle Life Sciences 60, Veradigm 3.1, Altera 2.9), **rejected 12** — kept as "未公開" rather than show a misleading bar.
- **Partner-landscape drawer:** a second battle-card drawer, "Who these vendors partner with", lists each vendor's partners with **hardware / cloud partners highlighted** (NVIDIA, AWS, Azure, GCP, Dell, HPE) — each is a concrete SMCI co-sell / displacement angle (the vendor already runs on someone's iron). E.g. Imaging-AI: Aidoc → NVIDIA + AWS; DeepHealth → GE + AWS + Google Cloud. Sorted hardware/cloud-first; hover a partner for the note + source.
- Structured `partnerships: [{partner, kind, note, source}]` and the 13 `market_share_pct` merged into vendors.yaml (line-oriented, prose kept as the bar's source).
- **97 GREEN** (+4: back-nav, partner drawer, partnerships sourced, share-rejection); deterministic; browser-verified (DOM), zero console errors, no emoji.
- **Tagged `v3.7`.** Note: partnerships/share are point-in-time research (2025-26 sources); refresh periodically.

## 2026-07-29 — battle-card vendors → a collapsible drawer with cited market-share bars + v3.5
Tuo, pointing at the battle card's vendor lists: make it a drawer too, and inside show a proportional bar of each vendor's market share. Done — honestly.
- The two old vendor blocks (ranked incumbents + full vendor pills) are fused into one collapsible **`<details>` drawer** — "Vendors in this market · N · M with cited share" — rows sorted by share, each: vendor name (→ registry) · leaderboard rank · a **proportional market-share bar** · the %.
- **Real data only (§8, no fabrication):** market share lived as *cited prose* on 33/309 vendors. Classified it — **20 carry a clean, sourced market-*share* %** (share of a defined market: Epic 42.3, Oracle 22.9, NVIDIA 92, Illumina 90, Veeva 80, SAP 6.6, …); the other 13 were rank/award/revenue/adoption/coverage metrics, NOT share, so they were **excluded**, not guessed. Extracted the 20 into a structured `market_share_pct` field; the prose stays as the bar's hover **source**. Vendors with no cited share show **"n/a / 未公開"** — never a made-up bar.
- Bug caught in verification: the bars weren't comparable because each row was its own grid and a long rank badge (Oracle's `#2·#28·#75`) shrank its track. Fixed to a **fixed-width track column** so every bar shares one scale — Epic's 42.3% bar now renders ~2× Oracle's 22.9%, ~3× MEDITECH's 14.8% (pixel-verified 63/34/22 px on a 150px track).
- **94 GREEN** (+2: app drawer/bars + data integrity — market_share_pct must be a 0-100 number AND have market_share prose to source it); deterministic; browser-verified (DOM + pixel), zero console errors, no emoji.
- **Tagged `v3.5`.**

## 2026-07-29 — Play D added (data-driven), Play E rejected; plays made navigable + v3.4
Tuo asked whether the 3-play scope should grow to D/E, why, and how to wire it in Explore. Ran a 5-agent adversarial evaluation (3 lenses + a keep-3 skeptic + synthesis) grounded in the orphaned-category data. Unanimous verdict: **add Play D, reject Play E.**
- **Why D:** 35 of 59 categories had no play — including the taxonomy's ONLY play-less flagship, **EHR/EMR (opp4/cust4)**, plus 8 customer-HOT clinical/payer-core systems that verifiably share ONE distinct zero-GPU anchor: **NVMe-OLTP + HA-redundant + immutable DR/backup**. Five triggers (cyber/ransomware, EHR go-live, hospital M&A, new campus, KLAS) dead-ended with no play to route to. **Play D — "Clinical Core Resilience & Ransomware DR"** is genuinely distinct from A/B (GPU/HPC compute) and C (industrial edge): the bet is transactional-DB resilience, pitched as uptime + ransomware recovery, not AI.
- **Why NOT E:** the proposed payer/RWD play was a segment bucket wearing a hardware costume — its slices split three ways (Payer Core Admin = D's NVMe/HA/DR anchor; Payer Actuarial/UM/Fraud = Play B's CPU-HPC; RWD/lakehouse = A/B's GPU+archive), zero triggers point at it, and a 5th play breaks the §5 one-person focus. "Payer" stays a **segment tag**, not a play.
- **Data changes (§8 — app renders from /data):** added `play-d` to plays.yaml (v2); tagged 9 categories `plays:[play-d]`; **reassigned 3 GPU categories** (CDSS, Smart-Room AI, HIM coding) to Play A so a resilience buyer's screen never surfaces an imaging pitch; dropped the now-stale `play_exemption` on the 9; wired `related_plays:[play-d]` into the 7 triggers that open it. CLAUDE.md §5 updated 3→4 plays.
- **Explore wiring (the connective tissue Tuo asked for):** plays are now **navigable, not decorations**. Every play chip (door, trigger brief, battle card) calls `goPlay` → a **play brief** (hardware anchor · segments · the triggers that open it · target categories). Every trigger chip calls `goTrigger` → the signal brief. So the full loop closes: **trigger ⇄ play ⇄ category → battle card**. Play D gets its own teal chip colour (`--d`). The door now shows 4 chips (A·10 B·9 C·8 D·9 — A grew from the reassigned GPU cats).
- **92 GREEN** (+4 lock-in tests); deterministic; browser-verified the full navigation loop + both languages, zero console errors, no emoji.
- **Tagged `v3.4`.**

## 2026-07-29 — product-line door de-jargoned: grouped + plain-glossed + v3.2.1
Tuo on the product-line door: "GPU 22 · HPC 11 · NVMe 17 · 封存 19 · 邊緣 17 · HA 17 · DR 9 — 這裏很奇怪…HPC 可以搭配 GPU,NVMe 就是 storage,封存又是什麼?HA 呢?DR 呢?你會讓人搞不清楚啊." Right — eight raw hardware_profile acronyms in a flat row read as soup, overlap (GPU/HPC both compute; NVMe/archive both storage), and never say what HA / DR / archive are. Rebuilt the door as a **labeled menu grouped by role**, each line with a plain one-line gloss:
- **Compute — runs the workload:** GPU servers (AI training & inference) · HPC nodes CPU (CPU-dense parallel compute — simulation, genomics) · High-memory (multi-TB in-memory).
- **Storage — where the data lives:** NVMe all-flash (hot, fast working storage, high IOPS) · Capacity archive (cold bulk PB storage — low cost).
- **Deploy & resilience — how it runs and stays up:** Industrial edge (on-site / plant-floor) · HA pairs (no-downtime redundancy) · DR / backup (disaster recovery & backup).
- Added a note that a category pulls several boxes, so the counts overlap by design (an AI pipeline pulls GPU + NVMe). The battle-card reference-arch chips also carry the plain gloss as a tooltip.
- **89 GREEN**; deterministic; browser-verified both languages, zero console errors, no emoji. **Tagged `v3.2.1`.**

## 2026-07-29 — killed the passive summary; Explore is now an active hunt launcher + battle cards + v3.2
Tuo, after v3.1: "改了有個屁用, 想別的方式優化" — polishing the summary table was useless; find a different shape. Diagnosis: the master table was a **passive poster** — it aggregated 59 categories into numbers you couldn't *act* on. An account manager opens the tool *with a context* (a product line to push, a meeting, a trigger) that a summary doesn't answer. So the whole top-of-Explore was rebuilt from a poster into a **tool**. Tuo wanted all four proposed directions — so they were unified: **three doors + one destination.**
- **Battle card (the destination).** The category detail pane now leads with an actionable sell layer, pulled from data: **Your motion** (direct / co-sell / OEM, derived from hardware_buyer), **Reference architecture** (the exact SMCI server families to pitch, from hardware_profile → SMCI family + sizing), and **Trigger → move** (the triggers that touch this category, reverse-looked-up, each with its urgency and the prescribed outreach action). Explainer → weapon.
- **Door 1 — SMCI product line.** Chips for each Supermicro line (GPU servers · HPC · NVMe · archive · high-memory · edge · HA · DR) with the pipeline count; click → the tree filters to every category that pulls that box → open one for the reference architecture. This is how a hardware seller carries quota.
- **Door 2 — Trigger.** All 14 signals, urgency-colored and sorted critical→low; click → the tree filters to the affected markets *and* a banner shows the prescribed action (e.g. "FDA IND filing → Flag account; R&D compute demand rising — probe genomics/AI workloads (Play B)"). Selling starts from a signal, not a taxonomy.
- **Door 3 — Search** (+ Play door). A prominent ask box for any category / vendor / SMCI term; every door lands on the battle card.
- The old passive master table (legend + per-play matrix + rollups) is gone; the 3-signal definitions survive in a folded key so nothing is lost. New `catFilter` drives all doors; each scrolls to the tree + battle card.
- **89 GREEN** (2 tests rewritten for the launcher + battle card); deterministic; browser-verified both languages, door→filter→action→battle-card flow, zero console errors, no emoji.
- **Tagged `v3.2`.**

## 2026-07-29 — Opportunity master rebuilt: signals defined + linked + real products, professionally aligned + v3.1
Tuo's verdict on v3.0's master table: the three badges (旗艦 / 客戶-HOT / 市場領導者) were never defined, never linked, each pipeline gave no real market-product examples, and the boxing wasn't professionally aligned — "非常的醜". All four fixed, and the definitions were adversarially verified before shipping (a 4-agent workflow across framework-correctness / mutual-distinctness / sales-clarity lenses caught real errors — see below).
1. **Defined** — a 3-card legend now defines each signal with its *level* and the *sales question* it answers: **flagship** (software category · size) "the biggest SMCI box this category pulls — hardware opportunity 4/4, the max across buyers; sizes the deal, doesn't say who buys → *How big is the biggest deal?*"; **customer-HOT** (software category · buyer) "the §3 gate answered *customer* — end org buys its own iron, a direct sale, one of three gate answers → *Is it a direct sale?*"; **market leader** (vendor · standing) "holds a ranked slot on the AI/No-AI leaderboard — already owns the account; the motion still depends on the buyer → *Which software vendor do I go through?*".
2. **Linked** — a read-path states the chain (Play → flagship+customer-HOT categories → market-leader vendors) and the level split (two signals grade the *category*, one grades the *vendor*). The nesting "flagship is the top tier of customer-HOT — every flagship here is also a direct sale" is **computed live** (`isFlag(c)&&!isHot(c)` count), so it can't silently go stale.
3. **Real products** — each play is now an aligned opportunity matrix whose "Leading products in this market" column is pulled **live from the vendor registry** (never hardcoded): PACS → GE HealthCare · Philips · Fujifilm Synapse · Sectra (No-AI #17–27); Imaging AI → Aidoc · Qure.ai · Lunit · RapidAI (AI #1–12); AI drug discovery → Schrödinger · Recursion · Isomorphic (AI #30–49); GMP → Körber · Rockwell · Siemens. Leaderboard-ranked vendors surface first (board matched to the category, never AI>No-AI globally); winding-down vendors are dropped from the headline; uncovered domains (GMP/MES, comp-chem) show real leaders with a "—" + an explicit note that absence of a rank ≠ "no leader".
4. **Aligned** — a real 3-column grid (category + FLAGSHIP/DIRECT chips | leading products | market-leader rank) with a header row and hairline rules, per play, replacing the ragged flex chips.
- **Adversarial-verify caught real errors** (would have shipped wrong): flagship is the *max across buyers* so it does NOT imply a direct deal (fixed the "flagship = direct" conflation); customer-HOT is `by_buyer.customer≥3` (customer *among* buyers), not "hardware_buyer=customer"; leaderboard rank is vendor *standing*, not the co-sell *motion* (renamed the detail-pane "…— co-sell" label and the "Co-sell rank" column to motion-neutral). 
- **89 GREEN** (+2 lock-in tests); deterministic; browser-verified desktop + narrow, both languages, zero console errors, no emoji.
- **Tagged `v3.1`.** Open follow-up (optional): app-wide, "customer-HOT" and "market leader" are still the friendly labels; a full rename to "customer-direct" / "leaderboard-ranked" everywhere would remove the last terminology collision with "market leader" prose in vendor notes.

## 2026-07-29 — the 6 value signals fused into one Opportunity master table + v3.0
Tuo: "these [6 value signals] — can't they be fused into a hierarchy master-table that replaces the currently-useless one?" Yes. The passive header stat-line (*59 categories · 9 flagship · 31 customer-HOT · …*) was a dead readout — it stated the totals but you couldn't *act* on it. Replaced it with a **價值總表 / Opportunity master** — one collapsible, fully drill-through dashboard pinned at the top of Explore that fuses all six value signals into a single big→small hierarchy:
- **KPI row** — 9 flagship · 31 customer-HOT · 155 market leaders (the totals, now the headline).
- **Pipeline by play** (open by default) — each of the 3 plays with its flagship/HOT value + its top flagship targets as click-through chips (chip → opens that category in the detail pane; row → re-roots the tree by play).
- **Opportunity by care area** — top 5 domains ranked by flagship opened, each row → `view by: care area`.
- **Top vendors to work** — top 6 vendors ranked by flagship/HOT categories served, each with its leaderboard rank, each row → the vendor in the registry.
- **Hot signals — open most flagship** — top 5 triggers ranked by flagship categories they unlock, each row → Method/Signals.
- The header stat-line reverts to a plain scope line (*59 software categories · 309 vendors mapped to the Supermicro hardware behind them*); the value KPI now lives in the master table, surfaced *and* actionable.
- Full category / vendor names (no `…` truncation, per Tuo); rows wrap gracefully at narrow widths.
- **87 GREEN** (+1 lock-in test); deterministic; browser-verified both languages, desktop + narrow, zero console errors, no emoji.
- **Tagged `v3.0`.**

## 2026-07-29 — value-surfacing rolled out across 6 components + v2.9
Extended the flagship/HOT "value-surfacing" from the Explore lens to five more surfaces (Tuo: apply it to Vendors + Leaderboards, then find ≥4 more). One shared helper (`catsVal` → flagship = opportunity 4, HOT = customer opportunity ≥3) now drives value signals everywhere; no emoji, all text/colour badges.
1. **Vendors** — each card shows how many flagship / customer-HOT SMCI categories the vendor serves (plus its leaderboard rank); a **sort toggle (by value / A–Z)** defaults to value, so the vendors serving the most high-opportunity categories (and market leaders) float to the top.
2. **Leaderboards** — each ranked entry now carries a flagship / HOT badge = how many high-opportunity SMCI categories that market leader touches, i.e. which leaders are actually a hardware opportunity, not just a big brand.
3. **Plays** — each play card shows its pipeline value (targets · flagship · HOT) and its **top flagship targets** as click-through chips → the play is now a pipeline view, not just a definition.
4. **Signals (Triggers)** — each trigger shows the flagship / HOT categories it *opens*, its related categories are click-through and flagship-highlighted, and the table is **sorted by urgency then opportunity opened** — act on the signal that unlocks the most flagship deals.
5. **Header** — the build stamp became a **portfolio value summary**: *59 categories · 9 flagship · 31 customer-HOT · 309 vendors · 155 market leaders* (updates with the language toggle).
6. **Explore detail pane** — a new **"Market leaders serving this — co-sell"** section lists the category's vendors that are on a leaderboard, with rank, as click-through co-sell targets.
- **86 GREEN**; deterministic; browser-verified all six, both languages, zero console errors, no emoji.
- **Tagged `v2.9`.**

## 2026-07-29 — Explore "view by" lens strengthened into a value-surfacing hunter + v2.8
Tuo challenged the GROUP control ("does it earn its space? if useful, how — and strengthen it"). Verdict: it's genuinely useful (multi-lens re-rooting of the 59-category tree serves different sales tasks), so it was trimmed and strengthened rather than removed.
- **Trimmed 8 → 6 lenses:** dropped `data` (a technical, not sales, cut) and `flat` (search already does that). Kept **care area · who buys · who uses it · AI/no-AI · play · hardware** — each a real sales lens. Renamed the label GROUP → **view by / 檢視**, and led with the two most sales-actionable (care area, who buys).
- **Every group now surfaces where the money is:** each L1 header carries a **flagship** count (opportunity 4, red) and a **customer-HOT** count (opportunity ≥3, green), and groups are **sorted by value** (flagship, then HOT, then size) instead of raw count. So "who buys → customer: 9 flagship · 30 HOT" and "care area → Pharma R&D: 4 flagship · 8 HOT" jump out — the lens now answers *where do I hunt* at a glance, not just *how is it grouped*. Text badges, no emoji.
- **86 GREEN**; deterministic; browser-verified (6 lenses, value badges + value sort on every axis, both languages, zero console errors).
- **Tagged `v2.8`.**

## 2026-07-29 — per-category explainer detail: 6-tier hierarchy + flow diagram (via /hyakushikiflow) + v2.7
Click a category → the right pane is now a rich, bilingual one-pager that explains the whole thing at a glance, per Tuo's six dimensions.
- **New `data/detail.yaml`** — bilingual (EN + 繁中) explainers authored + accuracy-verified for all **59 categories** (8-domain workflow, 16 agents): `purpose`, `usage_flow` (289 ordered steps total), `tech_note`, and `smci_fit`. Kept in a separate file (not bloating taxonomy.yaml) and merged into each category at build time.
- **6-tier hierarchy diagram (階級圖)** in the detail pane, top→down: **Who uses → Purpose → Usage flow → Tech → Hardware → SMCI workload**, connected by a rail with a node per tier. The Usage-flow tier embeds a **horizontal flow diagram** (step boxes + arrows, e.g. *Modalities acquire → Ingest to NVMe → Migrate to archive → Serve → Retain 10yr+*). Below it, full prose sections (Purpose / Usage flow numbered / How it works / Supermicro workload fit).
- **Supermicro workload mapping** — each `hardware_profile` component resolves to a server family (GPU servers · NVMe all-flash · high-capacity archive JBOD · HPC nodes · high-memory · industrial edge · HA-redundant · DR/backup) so the "what SMCI can help with" is concrete, plus the authored per-category `smci_fit` note. Server FAMILIES only — no invented SKUs (§8).
- Tests: `TestCategoryDetail` (every category has a complete bilingual detail with usage-flow steps; the pane renders the hierarchy + flow). **86 GREEN**; deterministic; browser-verified in both languages, zero console errors, no emoji.
- **Tagged `v2.7`.**

## 2026-07-29 — Explore rebuilt as a big→small hierarchy tree + detail (via /hyakushikiflow) + v2.6
Replaced Explore's wall of full cards with a **master–detail two-pane** so the whole 59-category universe is legible at a glance.
- **Level architecture (big → small):** L1 = the chosen axis (default **domain** — the 8 care areas, with nice labels: Pharma R&D, Hospital · Clinical Core, Manufacturing · QC · Supply, …), L2 = **AI-driven / No-AI**, L3 = the category (a compact row: opportunity badge · full name · primary-buyer colour dot). Counts at every level; each L1 collapses.
- **Left tree / right detail:** the left pane is the compact, scannable hierarchy (all 59 as rows under their groups); clicking a row shows that category's full card in the sticky right pane (stays put while you scroll the tree). Responsive — panes stack below 840px. The GROUP control still re-roots the tree (stakeholder / who-buys / AI / play / hardware / data / flat), and filters / jump shortcuts / search narrow it live.
- Removed the old full-card-grid render path (`renderStake` + card grids); `render()` now builds the tree via `l1node`/`l2into`/`catRow` and drives `showDetail`.
- **84 GREEN**; deterministic; browser-verified (tree + detail on wide and stacked on narrow, collapse, selection highlight, every axis, both languages, zero console errors, no emoji).
- **Tagged `v2.6`.**

## 2026-07-29 — 7 tabs fused into 3 pillars — WHAT / HOW / WHO (via /hyakushikiflow) + v2.5
Reviewed all tabs, then fused on natural seams into three pillars, each with an in-page section toggle (reusing Explore's `.seg` segmented control).
- **Explore** (WHAT — the software universe): unchanged; already absorbed Home + Hunt (v2.3–v2.4).
- **Method** (HOW — the GTM motion): fuses the old **Plays · Triggers · Scoring · Accounts** tabs into one, switched by an in-page sub-nav (Plays / Signals / Scoring / Accounts). The 3 plays, the 14-signal watchlist, the 100-pt scoring model + live calculator, and the scored demo account now live under one roof.
- **Vendors** (WHO — the market players): fuses **Registry + Leaderboards**. Sub-nav toggles Registry (309 vendors) / Leaderboards (the AI + No-AI ranked boards). The leaderboard deep-links (Explore's link, a vendor card's rank badge) now switch to the Vendors→Leaderboards view via `goVendorsBoard()`.
- Render functions refactored to `render*Into(host)` so a section renders into any container, driven by the reusable `subNav()` helper. Caught a real parse error in browser-verify (TUo #1): `renderRegistryInto(host)` also declared an internal `const host` — the whole script failed to parse (blank page); renamed the internal container to `vhost`.
- Tests: `tab-triggers` marker → `tab-method`. **84 GREEN**; deterministic; browser-verified (all sub-navs, deep-links, both languages, zero console errors, no emoji). **7 tabs → 3.**
- **Tagged `v2.5`.**

## 2026-07-29 — Home + Explore merged into one unified surface (via /hyakushikiflow) + v2.3
Ran the request through `/hyakushikiflow`: organize each tab's hierarchy first, then integrate. Home and Explore both rendered the SAME 59 categories grouped differently — so they collapse into one surface.
- **Level architecture, fixed first.** Home's axis = point-of-care stakeholder (WHO uses it); its 30-item "Others" dump is now **split by care domain** (R&D/Pharma 11 · Manufacturing 9 · Lab 4 · Data/Payer 5 · MedTech 1). Explore's controls organized into three tiers: GROUP (how to slice) / FILTER (narrow) / JUMP (shortcuts to HOT lists) → card → attribute levels.
- **Integrated into one tab.** The separate Home tab is gone; the unified **Explore** is the landing. Its GROUP segmented control gained **who uses it** (default — the stakeholder × AI/No-AI 2-level view, Others split by domain) and **AI / no-AI**, alongside care area / who buys / play / hardware / data / flat. One card style throughout; filters, jump shortcuts, search, and the leaderboard link all live on the one surface. Bilingual; no emoji.
- Fixed a real bug found in browser-verify (TUo #1): `fGroup` was a `<select>` whose fixed option list rejected the new `stakeholder`/`ai` values, silently falling back to a flat list — changed it to a plain value-holder so the segmented control drives grouping.
- Tests: `test_default_tab_is_home` → `test_default_tab_is_unified_explore` (tab-taxonomy is the landing; no tab-home); `test_home_registered_first_in_nav` → `test_unified_explore_registered_first_in_nav`. **84 GREEN**; deterministic; browser-verified (stakeholder 2-level, Others-by-domain, every GROUP axis, both languages, zero console errors).
- **Tagged `v2.3`.**

## 2026-07-28 — backfill 78 leaderboard leaders into registry (FK 46%→96%) + Explore overhaul + v2.0
Two asks: complete the leaderboard↔registry fusion, and fix the confusing Explore filter panel.
- **Registry 231 → 309 (v8).** Backfilled **78 of the 84** market-leaders that were on a leaderboard but absent from the registry (Qure.ai, Lunit, HeartFlow, Cleerly, DeepScribe, Iambic, Bayesian Health, Greenway, SCC Soft, Tecsys, …). Each researched full §8 (HQ, founded, current-and-verified leadership, history, deployment) by the `backfill-vendors` workflow (9 chunks + 9 adversarial verifiers = 18 agents); the verify pass caught real tenure changes (DeepScribe's founder-CEO departed 2025 → current CEO Matthew Ko). Each is filed under its sub-segment's taxonomy category (imaging-ai-deployment, digital-pathology, ai-drug-discovery, ehr-emr-core, lis, …), so those 15 categories now carry a far fuller vendor list. **Leaderboard→registry FK: 71/155 → 150/155 (96%)** — nearly every ranked leader now click-throughs to a vendor card (verified: Qure.ai row → its card with 🏆 badge + Mumbai HQ). The 5 residual are the leaders the enrich pass couldn't confirm (ScriptPro, Datavant ×2, Health Gorilla, Foundation Medicine) — honest null.
- **Explore wayfinding overhaul** (committed in the same arc): the dense "Hardware-buyer rollup §3 gate…" text and raw 8-dropdown Refine panel replaced with a plain intro, clickable HOT shortcut chips (🎯 sell direct / 🤝 ISV co-sell / 🔩 OEM / 📋 show all — hyperlink guidance straight to each target list), one-click quick-view chips (by care area / who buys / play / hardware / data type / flat) replacing the cryptic group-by dropdown, a colour legend for the buyer badge, and labeled advanced filters under "More filters". Fully bilingual.
- **84 tests GREEN**; app deterministic; browser clean both languages.
- **Tagged `v2.0`** — the software-universe map is now fully fused: 59 categories · 309 vendors · 2 ranked leaderboards, cross-linked Home↔Explore↔Vendors↔Leaderboards.

## 2026-07-28 — relationship fusion across Home · Explore · Vendors · Leaderboards + v1.9
Wove the four browsing tabs into one connected graph instead of four separate lists, per Tuo ("關係統整以及融合").
- **Foreign key: leaderboard → registry.** `data/leaderboards.yaml` v2 adds `vendor_id` to every entry — **71 / 155** entries resolve to a registry vendor (name/alias/parenthetical matching); the other 84 are leaders not (yet) in the 231-vendor registry (mostly pure-AI startups — Qure.ai, Lunit, HeartFlow…) and stay honest `null`. This FK is what fuses Leaderboards ↔ Vendors ↔ Explore.
- **Bidirectional cross-navigation** (JS helpers `goVendor` / `goCategory` + the `LB_BY_VID` rank map): Explore vendor pills are now click-through to the vendor card (and carry a 🏆 badge when that vendor is a market leader); Vendors category chips show the real category name and click through to Explore; Vendors cards show a 🏆 `AI #n` / `No-AI #n` rank badge (63 cards) linking to the board; linked leaderboard rows (↩, 71 of them) click through to the vendor card; Home gains a 🏆 link to the leaderboards. Every link works both directions and in both languages.
- Tests: `test_vendor_id_foreign_key` (every entry has vendor_id; non-null ⇒ real registry id; ≥1 linked) + `test_cross_tab_fusion_wired` (goVendor/goCategory/lbBadge/LB_BY_VID present). **84 tests GREEN**; app deterministic; browser clean, cross-nav verified (Explore→vendor, leaderboard→vendor, vendor→category all jump correctly).
- **Tagged `v1.9`.**

## 2026-07-28 — market vendor leaderboards (AI + No-AI, ranked, sourced) + v1.8
Two market-wide leaderboards of the leading medical/pharma software vendors, ranked by market share / installed base, per Tuo (asked for ~100 each; "fewer is fine — don't pad").
- **`data/leaderboards.yaml`**: **AI board 66 · No-AI board 89** (155 total), every entry §8-sourced — a real cited figure or a sourced market position, no fabrication. Built by the `market-leaderboards` workflow (16 sub-segment researchers + 16 adversarial verifiers = 32 agents); the verify pass caught and fixed real errors (e.g. Qure.ai's "105 countries" was a TIME100 artifact → corrected to 100+). Grouped by sub-market and ranked by installed base / share within each: AI led by Aidoc (31 FDA clearances, ~2,000 hospitals), Qure.ai (4,800+ sites), Lunit (KOSDAQ-audited revenue); No-AI led by Epic, Oracle Health, MEDITECH (KLAS acute-care EHR share). Dual-play vendors (GE, Philips) appear on both boards.
- **New "Leaderboards / 榜單" app tab** (9th): two ranked columns, grouped by sub-segment, each row rank · vendor · market_basis · clickable source (155 source links). Fully bilingual.
- Ranking basis is market share / installed base first, sourced market-leader position where no number is public (§8) — never a bare number. `market-leaderboards.yaml` version 1.
- Tests: `TestLeaderboards` (both boards present, dense 1..N ranks, every entry has a market_basis, ≥80% sourced). **82 tests GREEN**; app deterministic; browser clean both languages.
- **Tagged `v1.8`.**

## 2026-07-28 — Home re-organised by point-of-care stakeholder × AI/No-AI + v1.7
Replaced the Home page's hunting-funnel (plays / HOT stats / trigger panel — those live on in Explore·Hunt·Triggers) with a stakeholder-first map of the whole 59-category universe, per Tuo's scheme.
- **New data axis `home_stakeholder`** (facility / doctor / nurse / patient / other) on every category + an enum. The taxonomy's `clinician` tag doesn't split doctor vs nurse, so this is an explicit editable-in-data judgment: 8 doctor (PACS, CDSS, RIS/CVIS, radiation-oncology, surgical video, 3D viz, digital pathology, EHR), 4 nurse (ICU monitoring, pharmacy automation, smart-room ambient, clinical-communication), 3 patient (portal, access/scheduling, telehealth), 14 facility (ERP, RCM, HIM, workforce, device-integration, RTLS, CMMS, IoT-sec, BMS, capacity-command, imaging-AI, data-lakehouse, HIE, LLM-serving), 30 other (all non-hospital-point-of-care: pharma, manufacturing, lab back-end, payer, medtech).
- **Home = 5 stakeholder blocks, each split AI-driven vs No-AI.** AI-ness is derived (role analytics-AI OR modality AI-models OR gpu-server in profile) — a JS helper, not stored. Counts render live (e.g. Facility 14 = AI 8 · No-AI 6; Patient 3 = AI 0 · No-AI 3). Clicking a category deep-links into Explore pre-searched to it. Fully bilingual via the existing toggle (設施/醫生/護理/病人/其他 · AI 驅動/非 AI).
- Tests: `home_stakeholder` added to REQUIRED_CATEGORY_FIELDS + enum-membership test; the two obsolete Home invariants (play-tile deep-link, trigger-panel label) replaced by `test_home_groups_by_stakeholder_and_ai` and a slimmed honesty check (still bars a false "trigger fired" CRM label). **79 tests GREEN**; app deterministic; browser clean both languages.
- **Tagged `v1.7`.** The doctor/nurse assignments are a first defensible pass — correct any in `data/taxonomy.yaml` (one line per category), no code change.

## 2026-07-28 — category #59 clinical-communication + full EN⇄中文 app toggle + v1.6
Two asks: close the on-shift-clinician-communication gap in the map, and make the whole universe map viewable in Chinese.
- **+1 category → 59: `clinical-communication-collaboration`** (nurse call, secure messaging, on-call scheduling, shift handoff) under `hospital-device-facility-operations`. Full six layers + workload_envelope (derived from tags via the helper: gpu none, capacity none, availability high-availability, latency real-time; judgment low/random-transactional/high). Deliberately modest (opportunity 2) — pure comms is SaaS-light under the §3 hardware gate — but real for a complete software-universe map. **7 vendors**: added the category to ascom/connexall/spok/qgenda + researched 3 new (Vocera/Stryker, TigerConnect, PerfectServe) §8-verified — Vocera leadership honest-null (now a Stryker unit, no independent current exec), TigerConnect → Sean O'Neal CEO, PerfectServe → Guillaume Castel CEO. Registry → 231.
- **EN ⇄ 中文 toggle across the whole app.** A header button flips a global `LANG`; all 8 tab renders refactored from run-once IIFEs into named functions + a `renderAll()` so a toggle re-renders live. Category display names switch to `name_zh` (with the English as the sub-line); nav labels, tab chrome, section titles, field labels (HQ→總部, Leadership→負責人, Market share→市佔, …), and the key hero/rollup strings switch via a `T(en, zh)` helper. Vendor company names stay English (proper nouns). Browser-verified both directions, category #59 renders in both languages, zero console errors.
- **78 tests GREEN** (59 categories, 231 vendors); app + hunting guide rebuilt (deterministic).
- **Tagged `v1.6`.**

## 2026-07-28 — vendor leadership backfill + market_share layer (registry v7) + v1.5
Closed the two vendor-page gaps: the 28 vendors missing a named leader, and a new **market_share** field across all 228. Filled by the `vendor-enrich2` workflow (10 chunks × research + adversarial verify, 20 agents) under the §8 no-fabrication rule.
- **leadership +22** (of 28 missing) — each a current, sourced named exec with tenure verified (e.g. Intelerad → Jordan Bazinsky CEO; ETQ → Vick Vaishnavi; Varian → Arthur Kaindl; Nonlinear Dynamics → Udit Batra via parent Waters). **6 stay honest null** (eq2, gatan, matrix-science, open-systems-pharmacology, systech, terarecon — no public exec found). Leadership coverage 200 → 222 / 228.
- **market_share +33** — a cited figure for a *defined* market, or null (bare percentages are §8-meaningless). Real ones landed: Epic 42.3% US hospitals / 54.9% beds, Oracle Health 22.9%, Meditech 14.8% (KLAS); NVIDIA ~90-94% GPU (Jon Peddie); Illumina >90% clinical NGS; Veeva ~80% pharma CRM; Olympus >70% GI endoscope; Varian >60% radiotherapy; ABB #1 DCS ~19%; Thermo Fisher ~24.5% mass-spec; SAP ~6.6% ERP; Databricks ~11% lakehouse; IQVIA largest CRO; Roche #1 IVD; plus Best-in-KLAS ranks (Sectra, Abridge, Dolbey). The other 195 are honest null — most vendors publish no share figure.
- **§8 held:** every filled value carries a real source folded into the vendor's `sources`; HTML entities from scraped text decoded; the adversarial verify pass nulled anything weak or tenure-stale. `market_share` is a descriptive **string** (figure + market + source), never a bare number — enforced by `test_market_share_shape`.
- Registry **v6 → v7**; vendor card + search now render market_share; RED `d23e271` → GREEN. **78 tests**; app rebuilt (deterministic), browser clean — 33 cards show market share, 222 show leadership.
- **Tagged `v1.5`.**

## 2026-07-28 — workload axis + codex/grok dual review actioned + v1.4
Shipped `drilldown.py --axis workload` (queryable envelope slices by gpu_role / capacity_band / concurrency / availability_class, reading STORED values — no second derivation), then ran the **codex + grok dual review** of the whole workload layer and actioned every real finding. codex = **RED** (§8 + correctness), grok = **YELLOW** (market, "ship for internal GTM; fix H1/H2"). They **converged** on the two load-bearing issues.
- **§8 (both reviewers): two per_unit numbers whose citations didn't support them → nulled.** `pacs-vna` 0.1–1.5 GB (Purview article gives no such general range) and `digital-pathology` 1–4 GB (DPA FAQ only says "may exceed 1 GB"; the 4 GB upper + CLIA/CAP WSI extension is practice/inference, not a cited interval). Both `per_unit_data_size → null`, sources trimmed to their real retention citations. `per_unit` now 2/58 (bioinformatics WGS, cryo-EM — both grok order-of-magnitude-OK); dropped the URL-less CAP source line. §8 held: a number is nulled unless its own citation carries it.
- **Correctness (both): the derived-band heuristics over-claimed.** `gpu_role` used `images && !AI → visualization`, which mislabelled GPU **dose-calculation** (radiation-oncology) and **video-AI** (surgical) as visualisation → helper now maps `simulation → mixed` and **never auto-emits `visualization`** (reserved for a tag-driven override). `latency_class` mapped `edge-industrial + time-series → deterministic-real-time`, over-claiming hard-real-time for soft edge telemetry (asset tracking, cold-chain) → helper now emits `real-time` and **never auto-emits `deterministic-real-time`** (reserved for genuine control-loop categories via tags). Re-derived: 0 spurious `visualization`, 0 spurious `deterministic-real-time`; `radiation-oncology`/`pat-twin`/`samd` correctly `mixed`.
- **Test hardening (codex):** INV-4 now checks the exact 5-key set + finite non-bool numeric bounds + `0 ≤ low ≤ high` + non-empty unit; INV-18 couples `massive` concurrency to a rack/cluster **compute/GPU/HA** tier, not arbitrary sizing (archive can't serve thousands of sessions).
- **grok market/ZH nits:** `advanced-visualization-3d` + `qc-lims-cds` `io_pattern → mixed`; `ms-proteomics-metabolomics` name_zh → 質譜蛋白質體學與代謝體學資訊分析. grok confirmed the `explosive` data_growth club (pathology/omics/genomics), the retention statute mapping (CMS/CLIA/MQSA/DSCSA/EU-CTR), and the 5 newest categories' ZH as A−.
- **77 tests GREEN**; app + hunting guide rebuilt (deterministic). This is the review-hardened workload layer.
- **Tagged `v1.4`.**

## 2026-07-28 — per-category workload_envelope quantification layer (taxonomy v7) + v1.3
Added the seventh layer of the chain: a per-category **workload_envelope** — the *typical* hardware demand a software category implies — so the taxonomy now bridges (software category) → (concrete SMCI sizing). Built by a **two-workflow chain the user asked for**: `design-next-step` (judge-panel that designed + adversarially self-reviewed the schema) → the `quantify-fields` **skill** (executes the fill). The design workflow's spec came back `survives=False` (3 field-scoped fails); owner-adjudicated 9 findings, then a re-verify workflow confirmed the hardened spec `survives=True` grounded on the real repo.
- **12-field envelope, provenance fixed by field identity** (nothing mislabelable): **derived** (`gpu_role` `capacity_band` `availability_class` `latency_class`) = `tools/workload_ceiling.py`, a PURE tag-only helper, `value == helper(tags)` exactly (INV-14); **framework-judgment** (`data_growth` `io_pattern` `concurrency`) = expert ordinals, same epistemic class as `hardware_opportunity`, no citation; **sourced** (`retention_horizon` `per_unit_data_size`) = real citation or honest null. Plus `scaling_driver` (the SE discovery question), `sources`, `notes`.
- **§8 held under fire**: no fabricated numbers. Bands not fake precision; the ONLY numeric atom is `per_unit_data_size`, gated to confidence A/B/C + a real, cross-listed, non-placeholder citation. Fill ran 8 domain-chunk agents + adversarial verify (16 agents); sourced fields came back conservative — **14/58 retention** (CMS 42 CFR 482.24, CLIA 493.1105, MQSA/ACR — genuine category-wide statutes) and **4/58 per_unit** (whole-slide image, NGS run, cryo-EM movie, imaging study, each cited); everything else honest null.
- **`concurrency`** added as a standalone queryable band on Tuo's call (design flagged it as the one cut sales signal). `single|low|moderate|high|massive`; INV-18 couples `massive` ⇒ a rack/cluster-sized component.
- **18 invariants** (`TestWorkloadEnvelope`, INV-1..18): provenance gate, helper-is-tag-only (so positive-equality can't go vacuous), per_unit/retention source-quality, prose digit guard, GPU crown + totality, capacity/io/growth/availability/latency ↔ tag coherence, SaaS-light degenerate, flagship non-degenerate. RED `be801f8` → GREEN. **76 tests** pass.
- Taxonomy **v6 → v7**; verified NO tool-gate edits needed (`rollup.py` gates `<6`, `drilldown.py` `<4`) — only the cosmetic rollup version string was fixed (it hardcoded "v6"). App + hunting guide rebuilt (deterministic, byte-identical run-to-run); browser clean, Home 31/15, `taxonomy v7`.
- Reusable: re-running the `quantify-fields` skill on category #59+ auto-fills its derived bands and scaffolds the rest. Deferred (separate wave): `drilldown.py --axis workload`.
- **Tagged `v1.3`.**

## 2026-07-28 — completeness-audit categories 53→58 (taxonomy v6) + v1.2
The v1 `.jsx` cross-check stayed blocked (files never on disk — Spotlight/find both empty). Pivoted to its actual purpose — *did we miss anything?* — via a 4-lens opus completeness audit (research-lifecycle · data-modality · role · AI-infra finders + adversarial verifier). 10 candidates surfaced, **5 confirmed genuine gaps**, 5 rejected with reasons.
- **+5 categories** (full six-layer, each aligned to every chain invariant): `pharmacometrics-modeling-simulation`, `ms-proteomics-metabolomics`, `spatial-biology-omics`, `healthcare-llm-serving`, `payer-actuarial-hpc`. These are pharma/omics/AI-infra targets the v1 hospital matrix never covered — `healthcare-llm-serving` (fastest-growing GPU buy) and spatial/MS omics are net-new hunting ground, so the pivot beat the diff it replaced.
- **+21 new vendors** (§8 web-researched + opus verify): Certara, Simulations Plus, ICON, Metrum, Open Systems Pharmacology; Biognosys, SCIEX, Bruker Spatial, Matrix Science, Nonlinear Dynamics (Waters); 10x Genomics, Akoya, Vizgen; NVIDIA NIM/BioNeMo, John Snow Labs, Hippocratic AI, Microsoft/Nuance DAX; Milliman, Moody's Analytics, FIS Prophet, WTW. **+4 category-adds** to existing (Thermo Fisher, Bruker, Indica Labs, Aidoc). Registry now **228 vendors (v6)**.
- RED `eb37cf4` (58 fixtures + 5 glossary terms, vendors:[] pending) → GREEN. **58 tests** pass; every new category ≥4 vendors, headline==max per-buyer, primary∈argmax, sizing keys==profile, payer carries play-exemption. Browser: Home 31/15, all 5 cats + vendors render, zero console errors.
- **Tagged `v1.2`.**

## 2026-07-28 — vendor market-gap adds (registry v5) + v1.1
Closed the vendor-gap backlog flagged by the codex/grok reviews. Same §8 web-research + opus verify discipline.
- **+11 new vendors**: Viz.ai, Hyland Acuo (VNA), Hamamatsu, Indica Labs (HALO), Flatiron Health (Roche), Velsera (Seven Bridges), ABB, Critical Manufacturing, Tulip, Olympus, Medtronic. **+5 category-adds** to existing enriched vendors (Epic Radiant → ris-cvis; GE / Philips / Siemens Healthineers → imaging-ai-deployment; Brainlab → or-surgical-video). Registry now **207 vendors (v5)**.
- §8 caught a resigned exec: Olympus CEO draft "Stefan Kaufmann" (resigned Oct 2024) → corrected to Bob White (current, June 2025); Flatiron/ABB sources swapped to verify current CEOs. Honest-null discipline held.
- imaging-ai-deployment went from a thin/aging list to 9 vendors incl. the major platform channels; ris-cvis gained Epic Radiant. Tests 58 GREEN.
- Also: app build made deterministic (dropped wall-clock "built" timestamp — same fix as hunting_guide; rebuild is now byte-identical run-to-run).
- **Tagged `v1.1`.**

### Still blocked
- v1 `.jsx` cross-check — `/source/` remains empty; drop the two files to diff v1 vendor/category data against the current 207 vendors + 53 categories.


## 2026-07-27 — Home-UX dual review actioned (deep-links + honesty)
codex + grok reviewed the new Home funnel; consensus P1s = the funnel made false promises. `8859aa1` RED → `9b367d6` GREEN (58 tests).
- **Deep-links, not dumps**: `goTab(id, opts)` parameterized; play tiles scroll to their own Play section in Hunt (`hunt-play-*` anchors); HOT stat cards prefilter Explore to the exact per-buyer HOT list.
- **Card count == delivered count**: clicking HOT_customer shows 26, operator 14, OEM 3. The first cut filtered on headline opportunity and wrongly showed 30 — caught by live JS eval (TUo #1: verify against reality), then fixed with a per-buyer opportunity filter.
- **Consistency + honesty**: Explore OEM count now opp≥3 (3, matching Home + guide, was 8); "A trigger fired?" → "Highest-urgency signals" (it is a static slice, not CRM state); hardcoded 14/53 → dynamic lengths; play tiles show operator/OEM opportunity + a ranking tie-break.

## 2026-07-27 — guided Home funnel + classified Explore (wayfinding redesign)
The app landing was a filter-wall (8 dropdowns + 53 flat cards) — no guidance. Grilled (Tuo, Q1 → funnel front door). `5b19eb9` RED → `9453037` GREEN.
- **Home** tab (new default): "Where do you want to hunt?" + §3 gate; 3 HOT stat cards (26/14/8); three Play tiles with their top categories → Hunt; a fired-trigger panel → Triggers. `goTab()` wires the funnel.
- **Taxonomy → Explore** (demoted): 8 filters collapsed into a "Refine" `<details>` panel; defaults to **group-by-domain** (8 clean buckets), never a flat 53-wall. `domain` added as a group-by axis.
- Tests 48 → **53** (Home-is-default + surfaces plays/HOT/trigger + Explore filters collapsible). Browser-verified.

## 2026-07-27 — vendor enrichment: HQ / leadership / history / market (registry v4)
Every vendor now carries the profile a salesperson needs, all sourced. `5fb4dde` RED → `61ffc6a` GREEN.
- 8 web-research agents + 8 opus adversarial verifiers over all **196 vendors** (419 web searches). Added `headquarters`, `founded`, `leadership`, `history`, `market_position`, `sources[]`.
- **§8 fabrication guard, machine-enforced**: unsourced revenue figures → "not publicly disclosed" (InterSystems, Thermo Fisher, Veeva, Yokogawa, Cotiviti…); unconfirmable or stale CEO names → nulled/corrected (Cognex Willett→Moschner; Optum Conway[OptumRx]→Cianfrocco; Ordr/Infinitt/Ziosoft/Connexall/Körber nulled); 404 and copy-paste-error source URLs dropped. Honest nulls beat guesses.
- Coverage: HQ 187/196 · founded 178 · leadership 173 · market_position disclosed 107 (89 honestly "not publicly disclosed" — private companies without public share data).
- Tests 44 → **48**: enrichment schema + the §8 sourcing invariant (any named leader / market claim / history requires ≥1 source). App gains a **Vendors** tab (searchable registry, clickable sources); browser-verified.
- Note: `v1.0` tag predates this; the enriched registry is a superset — re-tag as `v1.1` when the vendor-market-gap adds also land.

## 2026-07-27 — v1.0 freeze: docs + deliverable dual-review + tag
Closed the loop on the deliverable and froze a stable release.
- **Docs**: `docs/glossary.md` now generated from `taxonomy.yaml` glossary (49 terms, single source, `tools/glossary_md.py`); `docs/workflow.md` per-phase checklists expanded to reference the real artifacts; `hunting_guide.py` made deterministic (version+counts, not wall-clock) so the smoke test no longer dirties the tree; `rollup.py` v4→v6 drift fixed.
- **Deliverable dual-review** (codex + grok on `hunting-guide.md`, web-search): actioned P1s — OEM master-HOT filter bug (8→3), §5.4-excluded vendors now marked ⊘, trigger index shows category→play/standalone, fail-closed generator validation; play re-routing (samd off play-a, rwd/ngs-lims/genomics-reporting off play-b); radiation-oncology +storage; NVIDIA product-line name fixed; cloud-cost-pressure action + trigger category opens.
- **Tests 43 → 44** GREEN; determinism proven (repeat runs leave the tree clean).
- **Tag `v1.0`** — taxonomy v6, 53 categories × six-layer chain + domain + name_full + glossary + hardware_profile + sizing, 196 sourced vendors, 14 triggers with foreign keys, the hunting guide, and a 44-test regression net.

### Open backlog (post-v1.0, not blockers)
- Vendor enrichment: market-gap adds flagged by grok (Epic Radiant on ris-cvis; Viz.ai / GE / Siemens / Philips on imaging-ai-deployment; Hyland Acuo on pacs-vna; Flatiron on rwd-rwe; Hamamatsu/Indica on digital-pathology; ABB on scada-dcs). Each needs a cited source per §8.
- Per-buyer "what to quote" (customer vs operator vs OEM hardware split).
- ris-cvis-workflow profile/score (grok flagged; prior opus ruling stands — revisit with evidence).
- v1 `.jsx` cross-check — still blocked on `/source/` file drop.

## 2026-07-27 — hunting guide: the sales-facing deliverable
The payoff — four rounds of verified six-layer data synthesized into the artifact an account manager hunts with. `688391b`.
- `tools/hunting_guide.py` → `docs/hunting-guide.md` (single-source from `/data`): per-play ranked target maps (category × opportunity × what-to-quote [component·sizing] × co-sell/incumbent vendors), cross-play standalone deals, master HOT lists, trigger→action index, component pipelines.
- App gains a **Hunt** tab rendering the per-play ranked view (quote + vendors); browser-verified.
- Correctness fix the guide surfaced: `clinical-data-lakehouse` dropped `play-b` (it's a clinical data warehouse, not genomics/research-AI — grok flagged this in round 1) → `play_exemption`; `hospital-ma` trigger `related_plays` → `[play-a]`.
- Tests 42 → **43** (hunting-guide smoke test). All GREEN.

## 2026-07-27 — refinement round 4: component sizing + vendor dual-review (registry v3)
Two parallel tracks, same TDD + dual-review discipline. `1cf8339` RED → `c09559f` sizing GREEN → `f132f15` vendor fixes.

**Per-component sizing** (`hardware_profile_sizing`): node / rack / cluster deployment scale per component → each category maps to a Supermicro quote size. Opus sizer + opus verifier (18 agents); 2 inflations deflated. Tiers: 50 node, 37 rack, 15 cluster. Test enforces sizing keys == profile and flagship-customer → ≥1 rack/cluster component. App chips show the tier.

**Vendor dual review** (codex on repo + grok on worktree, both web-search + citations):
- Acquisition/ownership updates with cited close dates: AspenTech→Emerson, Dotmatics→Siemens, Nuvolo→Trane, Paige→Tempus AI, Intelerad→GE HealthCare, Fabric Genomics→GeneDx, Congenica→SeqOne, AVEVA→Schneider, Wind River→Aptiv; Siemens scope corrected.
- Deployment corrections (MasterControl/Nuvolo cloud-only, TeraRecon +SaaS, DNAnexus overclaim dropped); blackford-analysis Bayer wind-down noted.
- Removed brightinsight (cloud SaaS mis-filed as embedded-OEM); merged duplicate philips-healthcare→philips.
- Market gaps filled: GE HealthCare & Philips added to pacs-vna; new vendors PathAI (digital-pathology) and Tempus AI (real-world-data + clinical genomics).
- §8 hygiene: 6 unverifiable note claims stripped; 24 confidence B→C downgrades where the sole source was a listicle/blog.
- Registry v3, 196 vendors, every category still ≥2. Tests 41 → **42** GREEN.

**Still blocked:** v1 `.jsx` cross-check — `/source/` empty; drop the files to run a diff of v1 vendor/category data against the current 196 vendors + 53 categories.

## 2026-07-24 — refinement round 3: vendors layer filled (196 vendors, web-researched)
`5ca96df` RED (registry schema + foreign keys + ≥2-per-category invariants) → `1f78bab` GREEN.
- 8 domain research agents (live web search) + 8 opus adversarial verifiers → **196 unique vendors**, every entry source-cited per §8. Confidence: 146 B / 50 C (verifiers downgraded ~25 entries whose only source was an aggregator blog).
- **Verification caught one fabrication** (TriNetX "acquired by Roche" — false; Carlyle majority-owned) and stripped unverifiable revenue/date claims — the §8 no-fabrication rule enforced by machine, not trust.
- Cloud-locked clinical SaaS (Veeva, Medidata, Benchling) carries the §5.4 co-sell-exclusion note.
- Coverage: all 53 categories, 3-8 vendors each. Category vendor lists injected into taxonomy; app cards render vendor chips.
- Tests 34 → **38** GREEN. Note: v1 `.jsx` extraction is now superseded — the researched registry is richer than the v1 vendor examples; drop the files in `/source/` anytime for a cross-check diff.

## 2026-07-24 — refinement round 2 (play-scope honesty + trigger foreign keys + market rulings)
Same discipline loop (test-driven-development RED→GREEN, opus adjudication, codex+grok dual delta review). Commits: `e7868fa` RED → `c315a3e` GREEN → `9fd35dc` opus rulings → `2ff3b2a` dual-review actioned.

1. **Play-scope honesty**: 10 reachable-HOT categories outside the three plays now carry an explicit `play_exemption` reason — no silent unroutable pipeline.
2. **Trigger foreign keys**: all 14 triggers bind `related_categories` + `related_plays` (validated; every trigger routes to ≥1 category; every routed play must be carried by a related category).
3. **Opus market rulings** on the 9-item grok backlog: 3 accepts / 6 evidence-rule rejects (per-buyer score = per-deal size, not market share; graphics-memory ≠ system memory).
4. **Dual delta review**: grok found 5 trigger-binding P1s + 2 weak exemption texts + 7 test escapes; codex found 4 P2s including a dead-binding test gap. **Cross-model consensus overrode two opus accepts** (clinical-trial-suite NVMe, capacity-command-center HPC-CPU — profiles reverted to empty; §5.4 co-sell exclusion + wrong component semantics). 9 trigger bindings fixed; 2 exemptions rewritten.
5. **Test suite: 33 → 34**, all GREEN. App renders trigger Related column + exemption notes.

**Open:** grok's declined suggestions logged (action-text↔play string matching — fragile; exemption-quality semantic checks — not mechanically testable).

## 2026-07-24 — six-layer chain refinement (taxonomy v6) — TDD + grill-me + superpowers + codex/grok dual review
Pipeline per Tuo's directive: three disciplines (test-driven-development · grill-me · using-superpowers), opus refinement agents, codex reviewing this repo + grok reviewing a dedicated worktree (`/Volumes/ClaudeNVME/medical-software-grok-review`).

**Commits:** `398cc59` RED (17 tests, 10 failing) → `828a56f` GREEN v6 → `00849a5` opus audit fixes → `36d8c40` dual-review hardening.

1. **Grill decision D1 (Tuo)**: ids stay compact; every category gains `name_full` (zero-abbreviation full name); enum values + field names expand; `glossary` block (now 49 entries, EN+ZH, Latin-free zh) canonically expands every surviving acronym.
2. **Abbreviations opened everywhere**: `cro`→`contract-research-organization`, `on-prem`→`on-premises`, `SaaS`→`software-as-a-service`, `oem`→`original-equipment-manufacturer`, `dr-backup`→`disaster-recovery-backup`, trigger categories, tool constants, …
3. **Everything classified**: `domain` field (8-value closed enum, was comments); triggers gained closed enums; headline opportunity = max(per-buyer) rule.
4. **Opus layer audit** (6 agents, high effort): 7 accepted fixes — payer added to hie (CMS-0057-F), digital-pathology +biotechnology-pharmaceutical, advanced-visualization-3d de-labbed, 3 name_full fixes, payer-um per-buyer scores un-inverted.
5. **Dual external review**: codex 11 P1 + 4 P2; grok P1/P2 sets. Overlap (highest confidence): rollup.py OEM KeyError crash (real, reproduced — earlier verification had truncated output with `head`, hiding it), no smoke tests, samd domain misfiled, name_full under-expansion, thin glossary. All P1s actioned; market fixes: ai-hpc deflated (GPU double-count), rcm operator deflated, primary_buyer=argmax rule (him-coding/cdss→operator, samd→oem), hyperscaler-buyer↔cloud-substrate coherence, OEM removed from deployment enum.
6. **Test suite v2**: 17 → **29 tests** — inventory lock (53 + exact ids), id→domain fixture, enum membership (not blacklist), primary=argmax, buyer-substrate coherence, glossary coverage + Latin-free zh, trigger vocabulary lock, subprocess smoke tests for rollup/drilldown/score. **29/29 GREEN.**

**Open (for Tuo):** grok P2 backlog not yet actioned (rd-lab modality omics?, ai-drug-discovery high-memory?, population-health storage, HOT-without-play marker, trigger↔category foreign keys) — next refinement loop candidates.

## 2026-07-24 — hardware_profile: category → SMCI component bridge (v5)
Next drill-down layer: what hardware each category actually pulls, structured from the prose `infrastructure_notes` into a controlled component set — the bridge from software category to Supermicro product line.
- `data/taxonomy.yaml` → **v5**. New enum + per-category `hardware_profile` (subset of `gpu-server · hpc-cpu · nvme-performance · capacity-archive · high-memory · edge-industrial · ha-redundant · dr-backup`). Assigned by a 17-agent workflow (profile → adversarial verify → consistency critic). Verify pruned speculative tags (pacs-vna dropped gpu-server — GPU belongs to imaging-ai-deployment; comp-chem dropped then re-added high-memory). 7 consistency fixes applied (icu +nvme; workforce/patient-access dropped thin-terminal edge; ngs-lims + genomics-reporting nvme→[]; comp-chem + cryo-em +high-memory).
- Component pipelines (categories pulling each): **gpu-server 20 (15 customer-HOT)**, edge-industrial 16, ha-redundant 16, nvme-performance 15, capacity-archive 15, dr-backup 9, hpc-cpu 8, high-memory 2. 8 SaaS-light categories carry an empty profile (honest).
- `tools/drilldown.py --axis component` prints the pipelines; `app` gains a hardware filter, hardware_profile group-by, and per-card component chips. CLAUDE.md §3 documents it. Live-verified in browser (no console errors; chips render; pacs-vna correctly GPU-free).

## 2026-07-24 — tidy remaining abbreviated field names
Renamed jargon/abbreviated fields across data + tools + app + spec for readability:
- `smc_reachable` → `supermicro_reachable`
- `play_refs` → `plays` · `vendor_refs` → `vendors` · `vendor_ref` → `vendor`
- `infra_control` → `infrastructure_control` (account lite field + scoring item key)
- `infra_notes` → `infrastructure_notes`
- account `trigger.ref` → `trigger.id`
- 234 + 56 token replacements across taxonomy.yaml, scoring.yaml, accounts/*, score.py, rollup.py, drilldown.py, build_app.py, templates. 0 residual abbreviations. Re-verified: score.py → 77.0 Active pursuit (unchanged); rollup/drilldown/build green; app renders (no console errors, taxonomy cards + badges intact).

## 2026-07-24 — rename hw_pull → hardware_opportunity (clarity)
Field name `hw_pull` was internal jargon. Renamed across data + tools + app + spec to read professionally and pair with `hardware_buyer`:
- `hw_pull` → **`hardware_opportunity`**; `hw_pull_by_buyer` → **`hardware_opportunity_by_buyer`**; `hw_pull_rollup` → `hardware_opportunity_rollup`.
- Added the 1–4 scale in words everywhere: **1 minimal · 2 modest · 3 significant · 4 flagship** (taxonomy enum comment, CLAUDE.md §3, app summary legend, CLI, per-badge tooltips).
- App: filter now reads `opportunity ≥`, group-by shows `opportunity 4 (flagship)`, badges tooltip the tier word.
- 141 token replacements across taxonomy.yaml + 3 tools + templates + README; CLAUDE.md prose reworded. 0 residual `hw_pull`. Tools + app re-verified (v4, 53 cats; HOT_customer 25 / HOT_operator 16 / OEM 8 unchanged; browser-checked).

## 2026-07-24 — per-buyer hw_pull (taxonomy v4) + icu flip + spec note
Actioned all three open items from the hardware_buyer round ("三個都要"):
1. **icu-central-monitoring** primary_buyer customer→**oem** — device-maker channel (Philips/GE/Draeger supply the FDA-cleared central-station servers) is the larger motion; hospital surveillance analytics is the smaller customer pull. (primary_buyer dist now 43 customer / 9 operator / 1 oem.)
2. **Per-buyer `hw_pull_by_buyer`** (taxonomy → **v4**): each buyer scored independently (customer/operator/oem; hyperscaler never scored). Assigned by a 17-agent workflow (score → adversarial verify → consistency critic). Verify caught lazy customer→operator copies (or-surgical-video oem 3→2, workforce-management operator 2→1, etc.). Consistency critic → 1 fix applied: patient-portal-engagement operator 2→1 (commodity multi-tenant portal SaaS = hyperscaler-diluted; GxP-validated hosting is what earns operator 2 — principle now stated).
3. **CLAUDE.md §3** documents the hardware_buyer axis + per-buyer pull + HOT lists.
- Refined HOT lists (per-buyer, not blended): **HOT_customer 25** (customer pull≥3) · **HOT_operator 16** (operator pull≥3) · **OEM design-wins 8**. Now surfaces cases where operator > customer (e.g. cdss-clinical-ai customer 2 / operator 3; him-coding, rcm-billing-claims, payer-um-fraud-analytics, rwd-rwe-analytics all operator-3 / customer-2 — invisible under a blended score).
- `tools/rollup.py` + `tools/drilldown.py` use per-buyer pull; `app` cards show per-buyer pull on each buyer badge (e.g. `CUSTOMER·4  operator·3`). Live-verified in browser.

## 2026-07-24 — hardware_buyer axis (taxonomy v3) + codex review actioned
**Why:** codex (independent review) showed the deployment-only on-prem/cloud split conflated substrate, hardware buyer, service model and deal motion — and buried the operator (ISV/managed) hardware deals the playbook §3 explicitly wants. Decision (Tuo: "我都要 + 把 buyer 更明確排出"): make **who buys the iron** an explicit field.

**Changed:**
- `data/taxonomy.yaml` → **v3**. New enum + per-category `hardware_buyer` (array of customer/operator/hyperscaler/oem), `primary_buyer`, `smc_reachable`. Assigned by a 17-agent workflow (per-cluster assign → adversarial verify → cross-cluster consistency critic). 5 consistency fixes applied (healthcare-cmms→operator primary; +oem smart-room; +operator or-surgical-video & radiation-oncology; icu-central-monitoring oem→customer primary for tie-break consistency — **the one debatable call, easy to flip**).
- Distribution: primary_buyer 44 customer / 9 operator. **26 HOT_customer (SMCI direct), 18 HOT_operator (ISV co-sell — previously invisible), 8 OEM design-wins.** 53/53 reachable.
- `tools/rollup.py` + `tools/drilldown.py` rewritten around hardware_buyer (buyer is now the authoritative "who controls hw" axis; deployment demoted to a guarded substrate descriptor — fixes codex's unknown→cloud and `['hybrid']` bugs).
- `app`: Taxonomy tab gains a hardware_buyer filter, primary_buyer/hardware_buyer group-by, per-card primary-buyer badge + other-buyer chips; rollup summary is buyer-centric. Live-verified in browser (group-by primary_buyer → 44/9; counts match rollup.py).

**Codex verdict was HOLD; actioned as:** applied the sharp/cheap fixes (OEM≠on-prem, explicit buyer replaces first-listed-deployment heuristic, substrate guards, operator co-sell surfaced). Did NOT accept codex's cloud-first reordering of ai-drug-discovery / clinical-data-lakehouse (fights Play B's on-prem + cloud-repatriation thesis).

**Open (for Tuo):**
1. `icu-central-monitoring` primary_buyer = customer (was oem) — flip back if the device-maker channel is really the bigger deal.
2. Per-actor hw_pull (codex wanted HOT_customer vs HOT_operator scored separately) — worth splitting, or leave single hw_pull?
3. Note hardware_buyer in CLAUDE.md §3 spec, or keep it as an evolved-in-repo field?

## 2026-07-24 — Cloud/hybrid/on-prem rollup lens (derived, schema unchanged)
**Decision (Tuo-approved):** collapse the 8-value `deployment` enum into the §3 infra-control gate as **two mutually-exclusive buckets + one hybrid flag**, NOT three buckets. Mapping: on-prem side ← on-prem/edge/private/OEM; cloud side ← public/SaaS/managed; `hybrid` is the boundary marker only. Primary bucket = first-listed deployment; `spans_infra_boundary` = deployment set touches both sides (or literal hybrid).

**Changed (derived only — `taxonomy.yaml` untouched, stays approved v2):**
- `tools/rollup.py` — CLI over taxonomy.yaml. Result: **37 on-prem · 16 cloud · 0 hybrid-primary**, 44/53 span the boundary, **26 HOT** (on-prem & hw_pull≥3, incl. all 9 hw4 flagship categories).
- `tools/build_app.py` / `app/index.html` — Taxonomy tab gains an infra-bucket filter, spans-boundary toggle, per-card bucket badge (green on-prem / muted cloud, `⇄` when spanning), and a top rollup summary.
- **Live-verified**: CLI and app agree (both single-source from taxonomy.yaml, independent code paths). In-browser filter on-prem + hw_pull≥3 → "26 / 53 shown" = rollup.py HOT count.

**Note:** cloud bucket = 0 categories at hw_pull≥3 → SMCI direct-sell skips it; enter only via ISV/operator. The hardware list IS the 26 HOT on-prem categories.

**Open (for Tuo):** run `codex` (+ optional Grok) as a second-opinion reviewer over this deployment mapping? Next drill-down axis after infra bucket: hw_pull → play → segment.

## 2026-07-24 — App built + taxonomy boundaries sharpened
**Changed:**
- `tools/build_app.py` + `app/index.html` — single-file playbook UI (67 KB, zero external deps, file:// works). Generated from `/data`; app code holds no domain content. 5 tabs: Taxonomy (filter by segment/play/deployment/hw_pull + search), Plays, Triggers (urgency-coloured), Scoring (interactive scorer mirroring score.py), Accounts (live-scored + ranked + evidence flag).
- **Live-verified in a real browser** (http server, JS executed): all 5 tabs render; scorer all-3 → 60.0 Nurture; Riverbend account → 77 breakdown matches score.py; evidence-D flag shows.
- Rendering via DOM text nodes only (no innerHTML with data).
- Taxonomy boundary fixes (no merge — granularity kept): `smart-room-ambient-ai` dropped "OR video routing" (→ `or-surgical-video`); `bioinformatics-secondary`↔`clinical-genomics-reporting` handoff (compute→SaaS) defined on both.

**Open questions (for Tuo):**
1. Drop v1 `.jsx` into `/source/` → vendor extraction (vendors.yaml still empty) + cross-check vs the 53 categories.
2. Remaining overlap pairs — merge or keep? `medical-device-integration`↔`icu-central-monitoring` · `ngs-lab-lims`↔`rd-lab-informatics` (both left separate for now).
3. Start filling real target accounts (30 max) via the lite-card workflow?

## 2026-07-24 — Taxonomy filled (schema approved)
**Changed:**
- `data/taxonomy.yaml` → `status: approved`, `version: 2`. **53 categories** (3 pre-approved examples + 50 new), 0 enum violations, no vendor-name leakage.
- Built via multi-agent workflow: 7 domain clusters drafted in parallel → adversarial verify per cluster (enum compliance, deployment/hw_pull honesty, Taiwan繁中 terminology) → completeness critic.
- Verifier corrections applied (highlights): EHR `SaaS`→`managed` (vendor-hosted single-tenant, not multi-tenant); `ngs-lab-lims` hw_pull 3→2 (LIMS ≠ the sequencer/analysis storage anchor); many name_zh fixes to Taiwan usage (量能 not 容量, 建築 not 樓宇, 視訊 not 視頻, 數位分身 not 數位孿生, 醫療器材軟體 for SaMD, 紀錄簿 orthography).
- Coverage critic added 4 hardware-relevant categories: `radiation-oncology-tps-ois` (GPU dose calc, play-a), `advanced-visualization-3d` (GPU render farm, play-a), `automated-visual-inspection` (edge-GPU line QC, play-c), `ai-hpc-orchestration` (GPU/HPC scheduler + MLOps — strongest ISV co-sell anchor, play-b).
- Distribution: hw_pull {1:9, 2:18, 3:17, 4:9} · plays a8/b9/c8 + 28 cross-cutting · 29 hospital-matrix / 24 non-hospital · all 8 segments covered.

**Open questions (for Tuo):**
1. Overlap pairs flagged by critic — keep separate (current) or merge? `medical-device-integration`↔`icu-central-monitoring` · `or-surgical-video`↔`smart-room-ambient-ai` (OR video double-count) · `ngs-lab-lims`↔`rd-lab-informatics` · `clinical-genomics-reporting`↔`bioinformatics-secondary` (tertiary handoff).
2. 53 categories vs "lean" — trim any before building the app?
3. Drop v1 `.jsx` into `/source/` → vendor extraction + cross-check against these 53.
4. Build `/app` (renders taxonomy + plays + triggers + scoring + accounts from `/data`)?

## 2026-07-24 — First Task executed
**Changed:**
- Repo scaffolded per §7 (`git init` done, no commit yet): `/data` `/templates` `/tools` `/app` `/docs` `/source`
- `CLAUDE.md` saved at root
- Seeded `data/scoring.yaml` (8 items, 100 pts, 4 tiers), `data/plays.yaml` (Play A/B/C), `data/triggers.yaml` (10 v1 + 4 framework = 14 triggers), `data/vendors.yaml` (empty registry, extraction TODO)
- `templates/account-card-lite.md` (10 fields) + `account-card-full.md`
- `tools/score.py` built + verified end-to-end: fictional Riverbend digital-pathology account → 77.0 / Active pursuit; gap detection works (flags all-D evidence, missing fields)
- `data/accounts/example-riverbend-pathology.yaml` — FICTIONAL demo, all confidence D
- `docs/workflow.md` (lean 10-phase with kill rules) + `docs/glossary.md` (EN/ZH seed, 17 terms)
- `data/taxonomy.yaml` — SCHEMA PROPOSAL with 3 examples (pacs-vna, bioinformatics-secondary, mes-ebr). `status: PROPOSAL`.

**Open questions (for Tuo):**
1. Taxonomy schema approval — approve / modify before full fill (§9.4 gate)
2. Confirm or swap default Play A/B/C trio (§5.1)
3. Drop v1 `.jsx` files into `/source/` → vendor + category extraction
4. First git commit — say the word

# Lean 10-Phase Research Workflow (one-person execution)

> Timebox each account: lite card ≤ 30 min. Full card only at score ≥ 70.
> The framework artifacts this workflow drives: [`hunting-guide.md`](hunting-guide.md)
> (where to hunt), [`../data/taxonomy.yaml`](../data/taxonomy.yaml) (what the software is),
> [`../data/triggers.yaml`](../data/triggers.yaml) (when), `tools/score.py` (is it worth a full card),
> and the [lite](../templates/account-card-lite.md) / [full](../templates/account-card-full.md) card templates.

| # | Phase | Output | Kill rule |
|---|---|---|---|
| 1 | Pick candidate (trigger fired or list import) | Name + facility | No facility identifiable → park |
| 2 | Gate question: who controls infra behind the software? | Y/N/partial | Pure SaaS user, no control → drop now |
| 3 | Segment + play mapping | 1 of 8 segments, 1 of 4 plays (A/B/C/D) | Fits no play → cross-play standalone infra deal or drop |
| 4 | Software stack ID (domain + vendor) | software block | — |
| 5 | Deployment operator → GTM motion | direct / ISV / service-provider / OEM | — |
| 6 | Trigger + timing | trigger block | No trigger, no timeline → Monitor tier max |
| 7 | Evidence collection (A-D tagged) | evidence block | Job postings ≠ installed base |
| 8 | Score (`tools/score.py`) | total + tier | <30 → drop, don't archive-polish |
| 9 | If ≥70: full card (workload quant + committee + hardware hypothesis) | full card | — |
| 10 | Next step + CHANGELOG | 1 concrete action + date | No next step = not an account |

## Per-phase checklist

**1 · Pick candidate.** Source from a fired trigger (trigger→action index in
[`hunting-guide.md`](hunting-guide.md) §4) or a list import from the financial-analysis
universe. Record at *facility* level — a pharma's genomics center ≠ its sterile plant (§5.2).

**2 · Gate (§3).** Ask who owns the servers/GPU/storage behind the software. Map to
`hardware_buyer`: **customer** (buys the iron → direct), **operator** (ISV/CRO/CDMO runs
dedicated iron → co-sell), **OEM** (embedded → design-win), **hyperscaler** (public cloud → out).
Hyperscaler-only → drop.

**3 · Segment + play.** Pick 1 of 8 segments and check the play via the category's `plays`
field. A category carrying a `play_exemption` is a legitimate cross-play standalone infrastructure
deal (hunting-guide §2), not a drop.

**4 · Software stack.** Identify the taxonomy category and the incumbent vendor from that
category's co-sell/incumbent list (hunting-guide §1, or `vendors.yaml`). The category tells you
the expected `hardware_profile` + sizing — *what to quote*.

**5 · Deployment operator → motion.** Confirm the operator decision-tree outcome drives the
motion: customer-operated → direct; SaaS/managed operator → ISV platform team; CRO/CDMO-run →
service provider; embedded-in-device → OEM. Excludes AWS-committed clinical SaaS (§5.4).

**6 · Trigger + timing.** Bind to a `triggers.yaml` entry (or note it is example-local). Capture
the monitoring window and prescribed action. No trigger + no timeline → Monitor tier at best.

**7 · Evidence (A–D).** Every factual claim tagged: **A** customer/RFP/contract · **B** official
public source · **C** job posting/conference/case study · **D** inference. Job postings are never
"confirmed installed base" (§8).

**8 · Score.** `python3 tools/score.py <account.yaml>` → 100-pt weighted total + tier
(≥70 Active · 50–69 Nurture · 30–49 Monitor · <30 Drop). Below 30, drop — do not archive-polish.

**9 · Full card (score ≥ 70 only).** Extend the lite card with the quantified workload profile,
the 6-role buying committee, the hardware hypothesis + reference architecture (anchor it on the
category's `hardware_profile_sizing`: node/rack/cluster), regulatory flags, competitive position,
estimated value, and PoC success criteria.

**10 · Next step + CHANGELOG.** One concrete action with a date. Log the session in `CHANGELOG.md`.
No next step = not an account.

export const meta = {
  name: 'design-next-step',
  description: 'Design + adversarially self-review the spec for the next taxonomy refinement (this run: per-category quantified workload envelopes). No human gate — the agent owns the review.',
  phases: [
    { title: 'Propose', detail: '4 lens strategists each propose the envelope schema' },
    { title: 'Judge', detail: 'merge the 4 proposals into one authoritative spec + build plan' },
    { title: 'Review', detail: 'adversarial verify the spec against fabrication / test-breakage / sales-uselessness' },
  ],
}

// ---- shared context (single source of truth for every agent) ----
const CONTEXT = `Project: SMCI (Supermicro) medical/pharma GTM taxonomy asset "medpharma-gtm".
This is a CLASSIFICATION ASSET used to hunt server/GPU/storage deals — NOT a CRM. Saved
constraint: do NOT invent or fill real customer accounts.

Current state — data/taxonomy.yaml v6, 58 categories, each ALREADY carries six layers:
  id, name_en/name_zh/name_full, domain, lifecycle, role, data_modality, deployment, segments,
  hardware_opportunity + hardware_opportunity_by_buyer{customer,operator,oem},
  hardware_buyer[], primary_buyer, supermicro_reachable,
  hardware_profile[]  (gpu-server|hpc-cpu|nvme-performance|capacity-archive|high-memory|
                       edge-industrial|ha-redundant|dr-backup),
  hardware_profile_sizing{<component>: node|rack|cluster},
  infrastructure_notes, plays[], vendors[].
228 vendors in data/vendors.yaml (v6). Regression net: tools/tests/test_chain_integrity.py (58 tests).

RULE §8 (binding): never fabricate vendor/account/market facts. Every surfaced value carries a
source OR is an honest null. Unverifiable -> confidence D + TODO marker. Absence != a negative fact.

GOAL THIS RUN: add a PER-CATEGORY quantified workload envelope — the *typical* hardware demand a
software category implies — so the taxonomy bridges (software category) -> (concrete SMCI sizing).
It must COMPLEMENT the existing coarse hardware_profile_sizing (node|rack|cluster), not duplicate it.
Candidate quantities (from CLAUDE.md §3, but expressed as per-category TYPICAL RANGES/BANDS, never
per-account point values): data ingested/day, total capacity, growth %/yr, retention, GPU type+qty,
train-vs-inference split, IOPS, throughput, latency class, concurrency, RTO/RPO, compute platform
(bare-metal / VM / Kubernetes / HPC-scheduler).`

const PROPOSAL_SCHEMA = {
  type: 'object',
  required: ['lens', 'fields', 'notes'],
  properties: {
    lens: { type: 'string' },
    fields: {
      type: 'array',
      items: {
        type: 'object',
        required: ['name', 'keep', 'rationale'],
        properties: {
          name: { type: 'string' },
          value_shape: { type: 'string', description: 'range | band-enum | scalar | boolean | free-note' },
          unit: { type: 'string' },
          keep: { type: 'boolean', description: 'true = belongs in the envelope, false = noise/cut' },
          rationale: { type: 'string' },
        },
      },
    },
    sourcing_policy: { type: 'string', description: 'how a per-category typical value is defensibly sourced under §8' },
    test_invariants: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string' },
  },
}

const SPEC_SCHEMA = {
  type: 'object',
  required: ['block_name', 'fields', 'sourcing_policy', 'confidence_rubric', 'test_invariants', 'fill_method', 'build_plan', 'risks'],
  properties: {
    block_name: { type: 'string', description: 'the yaml key added per category, e.g. workload_envelope' },
    fields: {
      type: 'array',
      items: {
        type: 'object',
        required: ['name', 'type', 'sourceable', 'rationale'],
        properties: {
          name: { type: 'string' },
          type: { type: 'string', description: 'range | band-enum | scalar | boolean | string' },
          enum_values: { type: 'array', items: { type: 'string' } },
          unit: { type: 'string' },
          sourceable: { type: 'string', enum: ['public', 'sometimes', 'honest-null-default'] },
          rationale: { type: 'string' },
        },
      },
    },
    sourcing_policy: { type: 'string' },
    confidence_rubric: { type: 'string' },
    test_invariants: { type: 'array', items: { type: 'string' } },
    fill_method: { type: 'string', description: 'exactly how the executor skill fills one category' },
    build_plan: { type: 'array', items: { type: 'string' } },
    risks: { type: 'array', items: { type: 'string' } },
  },
}

const REVIEW_SCHEMA = {
  type: 'object',
  required: ['lens', 'verdict', 'reasoning'],
  properties: {
    lens: { type: 'string' },
    verdict: { type: 'string', enum: ['pass', 'fail'] },
    killFields: { type: 'array', items: { type: 'string' }, description: 'field names that must be dropped' },
    fixes: { type: 'array', items: { type: 'string' } },
    reasoning: { type: 'string' },
  },
}

// ---- Phase 1: propose (4 diverse lenses, barrier) ----
phase('Propose')
const LENSES = [
  { key: 'fidelity', ask: 'Decide the FIELD SET and the value shape of each field (typical range? a small band-enum like small/medium/large? scalar? boolean?). Keep what genuinely characterises a category\'s hardware demand; cut vanity metrics. A per-category envelope must be a defensible TYPICAL, not a fake-precise point value.' },
  { key: 'sales-leverage', ask: 'Rank candidate fields by how much they change the SMCI hardware pitch — the numbers that make a rep pick up the phone (GPU type+count, PB-scale archive, IOPS/throughput, RTO/RPO, train-vs-inference). Cut fields that carry no sales signal even if technically interesting.' },
  { key: 'sourcing', ask: 'For EACH candidate field, judge under §8: is a per-category typical value publicly knowable (vendor sizing guides, reference architectures, published benchmarks, peer-reviewed cohort papers) or must it default to an honest null? Define the sourcing policy and a concrete A/B/C/D confidence rubric for envelope values.' },
  { key: 'schema-integrity', ask: 'Define exactly how the new block plugs into data/taxonomy.yaml and the 58-test net WITHOUT breaking invariants. Specify the precise machine-checkable test invariants the new block must satisfy (key presence, enum membership, coherence with existing hardware_profile / sizing, no fabricated non-null where source is absent).' },
]
const proposals = (await parallel(LENSES.map(l => () =>
  agent(`${CONTEXT}\n\nYou are the "${l.key}" design lens. ${l.ask}\nReturn your proposal as structured data.`,
    { label: `propose:${l.key}`, phase: 'Propose', effort: 'high', schema: PROPOSAL_SCHEMA })
))).filter(Boolean)

// ---- Phase 2: judge (merge into one spec) ----
phase('Judge')
const spec = await agent(
  `${CONTEXT}\n\nYou are the chief designer. Merge these ${proposals.length} lens proposals into ONE ` +
  `authoritative spec for the per-category workload envelope. Resolve conflicts, drop noise, keep ONLY ` +
  `§8-defensible fields. Produce: the final field schema (name/type/enum/unit/sourceable), the sourcing ` +
  `policy, an A/B/C/D confidence rubric, the exact machine-checkable test invariants, the per-category ` +
  `fill methodology the executor skill will follow, a step-by-step build plan, and the residual risks.\n\n` +
  `Proposals:\n${JSON.stringify(proposals, null, 2)}`,
  { label: 'judge:merge', phase: 'Judge', effort: 'high', schema: SPEC_SCHEMA })

// ---- Phase 3: adversarial self-review (no human gate — the agent owns the review) ----
phase('Review')
const REVIEW_LENSES = ['fabrication-risk', 'test-breakage', 'sales-uselessness']
const reviews = (await parallel(REVIEW_LENSES.map(lens => () =>
  agent(`${CONTEXT}\n\nADVERSARIALLY review the proposed spec through the "${lens}" lens. Try to BREAK it.\n` +
    `- fabrication-risk: would any field pressure the executor into inventing a number that isn't publicly sourceable? That violates §8.\n` +
    `- test-breakage: would adding this block break an existing invariant or fight the current schema/tests?\n` +
    `- sales-uselessness: is any field noise that no SMCI rep would ever act on?\n` +
    `Default to fail if you find a real problem. Name the exact fields to kill and the fixes.\n\n` +
    `Spec under review:\n${JSON.stringify(spec, null, 2)}`,
    { label: `review:${lens}`, phase: 'Review', effort: 'high', schema: REVIEW_SCHEMA })
))).filter(Boolean)

const killFields = [...new Set(reviews.flatMap(r => r.killFields || []))]
const survives = reviews.length > 0 && reviews.every(r => r.verdict === 'pass')

return {
  spec,
  reviews,
  survives,
  killFields,
  fixes: reviews.flatMap(r => r.fixes || []),
}

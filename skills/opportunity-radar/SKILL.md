---
name: opportunity-radar
version: "0.1.0"
description: "Find, validate, and score build-and-monetize opportunities from fresh cross-source signals."
argument-hint: "opportunity-radar [optional theme]"
allowed-tools: Bash, Read, Write, WebSearch
license: MIT
user-invocable: true
---

# Opportunity Radar

Use this skill to find **actionable business opportunities**, not generic startup ideas.

The system is intentionally two-stage:

1. **Discovery** finds fresh evidence.
2. **Enrichment + scoring** decides whether an opportunity is worth testing.

Do not score raw social posts as businesses. Group multiple signals into one opportunity thesis first.

## Step 1 — Run discovery

Resolve the repository root and run:

```bash
python3 scripts/opportunity_radar.py --days 14 --limit-per-bucket 10 --emit json
```

If the user supplied a theme, use it as an additional WebSearch enrichment lens. Do not remove the default buckets unless explicitly asked.

The discovery bundle covers:

- open-source breakouts
- build-cost collapse
- incumbent pricing pain
- shutdown/migration openings
- newly available APIs
- painful heavyweight workflows
- Turkey/local-market whitespace

The script's `discovery_score` is **only an evidence-priority score**. Never present it as the opportunity score.

## Step 2 — Collapse signals into opportunity theses

Cluster candidates that point to the same underlying business opportunity.

Example:

- "Photoshop alternative gains stars"
- "Adobe pricing complaints"
- "seller asks for batch background removal"

may collapse into:

> Marketplace-specific product image compiler for sellers.

Prefer a strong narrow thesis over a broad category.

## Step 3 — Enrich the strongest theses

Enrich the top 8–12 themes with current evidence.

For each theme verify, where applicable:

### Problem evidence
- repeated complaints
- manual workaround
- high switching intent
- existing budget
- urgency or regulatory deadline

### Incumbent economics
- current price
- contract friction
- implementation cost
- obvious bloat
- margin or take-rate opportunity

### Build-cost collapse
- newly capable model/API
- permissively licensed OSS
- commodity infrastructure now available
- implementation that became materially easier in the last 6–18 months

### License
For code-led opportunities, verify the repository license.

Treat MIT, Apache-2.0, BSD, and similarly permissive licenses as commercially friendly subject to their terms.

Treat GPL/AGPL/source-available/custom licenses as a **review gate**, not an automatic green light.

Do not assume a GitHub repository is commercially reusable merely because the source is visible.

### Distribution
Identify a concrete first channel:
- SEO query
- marketplace/app store
- existing installer/reseller network
- community
- outbound list
- integration directory
- partner ecosystem
- user-generated sharing loop

"Run ads" is not a distribution thesis.

### Turkey whitespace
Search Turkish-language and Turkey-specific competitors separately.

Check whether the opportunity is:
- absent locally
- present but poorly localized
- present but enterprise-only
- priced in foreign currency
- missing Turkish integrations
- blocked by local workflow/regulation
- already crowded

## Step 4 — Apply kill gates

An opportunity cannot be **TEST** if any unresolved gate below is true:

1. **No payer** — user pain exists but buyer/budget is unclear.
2. **License trap** — commercial use depends on code whose license is incompatible with the intended model.
3. **No distribution wedge** — only generic paid acquisition is visible.
4. **Commodity trap** — dozens of near-identical products and no structural wedge.
5. **MVP too slow** — credible first validation requires >14 days for a small technical team, unless upside is exceptional.
6. **Weak evidence** — thesis relies on one low-signal post or one unverified claim.
7. **Regulatory dependency** — economics require legal/regulatory assumptions that are not verified.

A failed gate normally means **WATCH** or **IGNORE**.

## Step 5 — Business score

Rate each factor from 0–5.

```
Opportunity Score =
4 × Pain
+ 3 × Willingness to Pay
+ 2 × Incumbent Pricing Opportunity
+ 3 × Build-Cost Collapse
+ 3 × Distribution Access
+ 2 × Global Whitespace
+ 1 × Signal Momentum
+ 2 × Evidence Confidence
```

Maximum = 100.

Interpretation:

- **72–100: TEST** only if all hard gates pass
- **55–71: WATCH**
- **0–54: IGNORE**
- any hard-gate failure can override the numeric score

Do not inflate scores to create excitement.

## Step 6 — Turkey score

For opportunities with a plausible Turkish market, score 0–5:

```
Turkey Score =
4 × Local Whitespace
+ 3 × Localization Advantage
+ 3 × Local Distribution Access
+ 3 × Pain Fit
+ 2 × Willingness to Pay
+ 2 × Turkey-Specific Workflow Advantage
+ 1 × Existing Stack Reuse
+ 2 × Evidence Confidence
```

Maximum = 100.

A high Turkey score does not mean the global opportunity is strong. Show both.

## Step 7 — Estimate MVP honestly

Provide:

- **validation artifact**: what can be shown/sold before building
- **MVP scope**
- **estimated build time**
- **external dependencies**
- **reusable repository/components**
- **first 20 prospects/users**
- **first monetization test**

Prefer a landing/demo/outbound validation before full implementation.

## Required output

Start with a compact table:

| Opportunity | Why now | Global | Turkey | MVP | Fatal flaw | Decision |
|---|---|---:|---:|---:|---|---|

Then provide detail only for **TEST** and strongest **WATCH** items.

For each detailed item:

### [Opportunity]

**Signal**
What changed recently.

**Evidence**
Specific sources, dates, engagement, repo/license facts, pricing, or shutdown/API evidence.

**Buyer + pain**
Who pays and what expensive/annoying outcome is being avoided.

**Product wedge**
The narrow initial product. Avoid platform fantasies.

**Monetization**
Concrete price hypothesis or transaction model.

**Distribution**
First acquisition channel and why it is structurally available.

**Turkey angle**
Local whitespace, integrations, pricing, language, regulation, or reseller advantage.

**MVP**
What can be built or faked in <=14 days.

**Reuse**
Relevant existing code/assets where verified.

**Fatal flaw**
The single most likely reason to kill it.

**Next test**
A test that costs little and can change the decision within 48 hours.

## Rules

- Prefer evidence from the last 30 days for momentum claims.
- Use older sources only for stable facts such as market structure or license text.
- Separate facts from inference.
- Never claim keyword volume without a real source.
- Never call an OSS project "free to commercialize" before verifying the license.
- Penalize products that are easy to build but hard to distribute.
- Penalize generic AI wrappers.
- Reward workflow ownership, embedded distribution, and local-market asymmetry.
- The goal is to kill weak ideas early and surface a small number worth testing.

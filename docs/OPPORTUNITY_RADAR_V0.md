# Opportunity Radar v0

Status: **POC / internal only**

## Goal

Continuously detect fresh **build-and-monetize** openings before they become obvious mainstream startup ideas.

This is not a trend dashboard and not an "AI startup idea generator".

It answers:

> What changed recently that makes a previously unattractive, expensive, or impossible product suddenly testable?

## Current architecture

```
last30days cross-source retrieval
        ↓
opportunity_radar.py
        ↓
deduped discovery bundle
        ↓
Opportunity Radar skill
        ↓
business enrichment
        ↓
hard kill gates
        ↓
Global Score + Turkey Score
        ↓
TEST / WATCH / IGNORE
```

## Why this base

The existing `last30days-skill` already provides much of the expensive plumbing:

- Reddit
- Hacker News
- GitHub
- X when configured
- YouTube
- TikTok/Instagram when configured
- grounded web search
- query planning
- reranking
- clustering
- SQLite persistence/watchlists

Its MIT license is commercially friendly subject to the license terms.

## What we deliberately do NOT reuse

`worldmonitor`, `crucix`, and the open-source Firecrawl server are useful architecture references, but their AGPL licensing makes them poor foundations for a future closed-source commercial Opportunity Radar.

If web extraction is needed, prefer the Firecrawl API/service or independently licensed components rather than copying AGPL server code into the product.

## v0 signal buckets

1. OSS breakout
2. Build-cost collapse
3. Incumbent pricing pain
4. Product shutdown / migration
5. New APIs / capabilities
6. Heavy workflow pain
7. Turkey whitespace

## Scoring doctrine

Scoring happens **after enrichment**.

The system has two independent outputs:

- **Global Opportunity Score**
- **Turkey Opportunity Score**

The score is subordinate to hard kill gates. A great-looking numeric score cannot rescue:
- no payer
- a license trap
- no distribution
- commodity competition
- a >14-day MVP without exceptional upside
- weak evidence
- unresolved regulatory dependency

## Decision thresholds

- TEST: >=72 and no hard gate failure
- WATCH: 55–71 or a fixable unresolved gate
- IGNORE: <55 or a structural fatal flaw

## Phase plan

### Phase 0 — immediate
A ChatGPT recurring Opportunity Radar scan provides daily live research while the code POC is being proven.

### Phase 1 — this branch
- discovery wrapper
- opportunity scoring skill
- manual enrichment
- daily/weekly reports
- no UI

Success criterion:
At least **3 genuinely testable opportunities in 14 days**, with one surviving direct customer/market validation.

### Phase 2 — persistence
Add:
- GitHub star snapshots and deltas
- product/pricing snapshots
- shutdown/change events
- license cache
- competitor entities
- opportunity history
- score history
- dismiss/watch/test state

### Phase 3 — internal web console
Build only after Phase 1 proves signal quality.

Views:
- Inbox
- TEST
- WATCH
- Turkey
- Sources
- Opportunity history
- Rejected / kill reasons

### Phase 4 — productization decision
Do not sell the radar until it repeatedly produces opportunities we would actually build or test ourselves.

## First vertical after Radar

**SahaBox AI** is a strong first case study for the Radar because it combines:
- commodity cameras
- rapidly improving vision models
- clear operational pain
- reseller/installer distribution
- Turkish local-market potential

Once Radar v0 is producing structured outputs, SahaBox should be evaluated through the same gates rather than receiving special treatment.

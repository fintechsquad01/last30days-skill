#!/usr/bin/env python3
"""Opportunity Radar v0.

Builds a cross-source discovery bundle by reusing the existing last30days
retrieval pipeline. This script intentionally stops before making business
judgments. The opportunity-radar skill enriches and scores the resulting
evidence with current pricing, licensing, competition, and Turkey whitespace.

Usage:
    python3 scripts/opportunity_radar.py
    python3 scripts/opportunity_radar.py --days 14 --limit-per-bucket 8
    python3 scripts/opportunity_radar.py --emit md
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).parent.resolve()
LAST30DAYS = SCRIPT_DIR / "last30days.py"


@dataclass(frozen=True)
class Bucket:
    key: str
    query: str


BUCKETS = [
    Bucket(
        "oss_breakout",
        "new open source software launch GitHub breakout stars alternative to expensive SaaS",
    ),
    Bucket(
        "build_cost_collapse",
        "small team built software that previously required a large company AI open source",
    ),
    Bucket(
        "pricing_pain",
        "software pricing increase expensive subscription users looking for alternatives",
    ),
    Bucket(
        "shutdown_migration",
        "software product shutdown sunset discontinued customers need migration alternative",
    ),
    Bucket(
        "new_api_capability",
        "new developer API launch previously impossible workflow automation",
    ),
    Bucket(
        "workflow_pain",
        "repetitive manual workflow painful enterprise software users asking for simpler tool",
    ),
    Bucket(
        "turkey_whitespace",
        "Turkey Turkish market software users local alternative missing expensive foreign SaaS",
    ),
]


def _run_bucket(bucket: Bucket, days: int) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(LAST30DAYS),
        bucket.query,
        "--emit=json",
        "--quick",
        "--days",
        str(days),
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=360,
    )
    if result.returncode != 0:
        return {
            "bucket": bucket.key,
            "query": bucket.query,
            "status": "failed",
            "error": (result.stderr or result.stdout)[-1000:],
        }
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return {
            "bucket": bucket.key,
            "query": bucket.query,
            "status": "failed",
            "error": f"invalid JSON: {exc}",
        }
    return {
        "bucket": bucket.key,
        "query": bucket.query,
        "status": "ok",
        "report": report,
    }


def _source_count(candidate: dict[str, Any]) -> int:
    sources = candidate.get("sources") or []
    if sources:
        return len(set(sources))
    return 1 if candidate.get("source") else 0


def _candidate_to_signal(
    candidate: dict[str, Any],
    bucket: str,
    query: str,
) -> dict[str, Any]:
    final_score = float(candidate.get("final_score") or 0)
    rerank_score = float(candidate.get("rerank_score") or 0)
    source_count = _source_count(candidate)
    engagement = candidate.get("engagement")
    try:
        engagement_value = float(engagement or 0)
    except (TypeError, ValueError):
        engagement_value = 0.0

    # Discovery score is deliberately only an evidence-priority heuristic.
    # It is NOT the business opportunity score used by the skill.
    discovery_score = (
        final_score * 0.55
        + rerank_score * 0.20
        + min(source_count, 4) * 5.0
        + min(engagement_value, 1000.0) / 1000.0 * 5.0
    )

    return {
        "bucket": bucket,
        "query": query,
        "title": candidate.get("title") or "",
        "url": candidate.get("url") or "",
        "snippet": candidate.get("snippet") or "",
        "source": candidate.get("source") or "",
        "sources": candidate.get("sources") or [],
        "source_count": source_count,
        "published_at": _best_published_at(candidate),
        "discovery_score": round(discovery_score, 3),
        "pipeline_final_score": final_score,
        "pipeline_rerank_score": rerank_score,
        "pipeline_explanation": candidate.get("explanation") or "",
        "subquery_labels": candidate.get("subquery_labels") or [],
    }


def _best_published_at(candidate: dict[str, Any]) -> str | None:
    dates = []
    for item in candidate.get("source_items") or []:
        value = item.get("published_at")
        if value:
            dates.append(value)
    return max(dates) if dates else None


def _dedupe(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for signal in signals:
        key = (signal.get("url") or "").strip().lower()
        if not key:
            key = (signal.get("title") or "").strip().lower()
        if not key:
            continue

        existing = seen.get(key)
        if existing is None:
            seen[key] = signal
            continue

        existing_buckets = set(existing.get("buckets") or [existing["bucket"]])
        existing_buckets.add(signal["bucket"])
        existing["buckets"] = sorted(existing_buckets)
        existing["discovery_score"] = max(
            float(existing.get("discovery_score") or 0),
            float(signal.get("discovery_score") or 0),
        )
        existing_sources = set(existing.get("sources") or [])
        existing_sources.update(signal.get("sources") or [])
        if signal.get("source"):
            existing_sources.add(signal["source"])
        existing["sources"] = sorted(s for s in existing_sources if s)
        existing["source_count"] = len(existing["sources"]) or max(
            int(existing.get("source_count") or 0),
            int(signal.get("source_count") or 0),
        )
    return list(seen.values())


def discover(days: int, limit_per_bucket: int, selected: set[str] | None) -> dict[str, Any]:
    bucket_runs = []
    signals: list[dict[str, Any]] = []

    for bucket in BUCKETS:
        if selected and bucket.key not in selected:
            continue
        run = _run_bucket(bucket, days)
        bucket_runs.append({
            "bucket": bucket.key,
            "query": bucket.query,
            "status": run["status"],
            "error": run.get("error"),
        })
        if run["status"] != "ok":
            continue

        candidates = run["report"].get("ranked_candidates") or []
        for candidate in candidates[:limit_per_bucket]:
            signals.append(_candidate_to_signal(candidate, bucket.key, bucket.query))

    deduped = _dedupe(signals)
    deduped.sort(
        key=lambda item: (
            float(item.get("discovery_score") or 0),
            int(item.get("source_count") or 0),
        ),
        reverse=True,
    )

    return {
        "version": "0.1.0",
        "days": days,
        "bucket_runs": bucket_runs,
        "candidate_count": len(deduped),
        "candidates": deduped,
        "note": (
            "discovery_score ranks evidence for enrichment only. "
            "Do not treat it as a business opportunity score."
        ),
    }


def _render_md(bundle: dict[str, Any]) -> str:
    lines = [
        "# Opportunity Radar discovery bundle",
        "",
        f"Candidates: **{bundle['candidate_count']}**",
        f"Lookback: **{bundle['days']} days**",
        "",
        "| # | Discovery | Sources | Bucket | Signal |",
        "|---:|---:|---:|---|---|",
    ]
    for index, item in enumerate(bundle["candidates"], start=1):
        title = (item.get("title") or "").replace("|", "\\|")
        buckets = ", ".join(item.get("buckets") or [item.get("bucket") or ""])
        lines.append(
            f"| {index} | {item.get('discovery_score', 0):.1f} | "
            f"{item.get('source_count', 0)} | {buckets} | {title} |"
        )
    lines += [
        "",
        "> Discovery score is an evidence-priority heuristic, not the business score.",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover build-and-monetize signals.")
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--limit-per-bucket", type=int, default=10)
    parser.add_argument("--emit", choices=["json", "md"], default="json")
    parser.add_argument(
        "--buckets",
        help="Comma-separated bucket keys. Default: all.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    selected = None
    if args.buckets:
        selected = {item.strip() for item in args.buckets.split(",") if item.strip()}
        known = {bucket.key for bucket in BUCKETS}
        unknown = sorted(selected - known)
        if unknown:
            raise SystemExit(f"Unknown bucket(s): {', '.join(unknown)}")

    bundle = discover(
        days=max(1, args.days),
        limit_per_bucket=max(1, args.limit_per_bucket),
        selected=selected,
    )
    if args.emit == "md":
        print(_render_md(bundle))
    else:
        print(json.dumps(bundle, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

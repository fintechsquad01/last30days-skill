import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "opportunity_radar.py"
spec = importlib.util.spec_from_file_location("opportunity_radar", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_dedupe_merges_same_url():
    signals = [
        {
            "bucket": "oss_breakout",
            "url": "https://example.com/a",
            "title": "A",
            "sources": ["github"],
            "source_count": 1,
            "discovery_score": 10,
        },
        {
            "bucket": "pricing_pain",
            "url": "https://example.com/a",
            "title": "A duplicate",
            "sources": ["reddit"],
            "source_count": 1,
            "discovery_score": 20,
        },
    ]

    result = module._dedupe(signals)

    assert len(result) == 1
    assert result[0]["discovery_score"] == 20
    assert result[0]["buckets"] == ["oss_breakout", "pricing_pain"]
    assert result[0]["source_count"] == 2


def test_source_count_prefers_sources_array():
    candidate = {"source": "reddit", "sources": ["reddit", "github", "web"]}
    assert module._source_count(candidate) == 3


def test_known_bucket_keys_are_unique():
    keys = [bucket.key for bucket in module.BUCKETS]
    assert len(keys) == len(set(keys))

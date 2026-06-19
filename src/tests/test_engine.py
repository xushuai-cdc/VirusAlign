"""Unit tests for AlignmentEngine."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.engine import AlignmentEngine, MatchResult
from src.constants import IMPORTANT_VIRUS_ALIASES
from src.utils import normalize_virus_name, normalize_taxonomy_key


def test_engine_init():
    e = AlignmentEngine()
    assert e is not None
    assert "exact" in e.match_stats


def test_exact_match():
    e = AlignmentEngine()
    r = e.match_one("Betacoronavirus pandemicum")
    assert r.is_matched()
    assert r.match_source == "exact"
    assert r.taxonomy.get("Family") == "Coronaviridae"


def test_alias_sars():
    e = AlignmentEngine()
    r = e.match_one("SARS-CoV-2")
    assert r.is_matched()
    assert r.standard_name == "Betacoronavirus pandemicum"
    assert r.match_source == "alias"


def test_alias_covid():
    e = AlignmentEngine()
    r = e.match_one("COVID-19")
    assert r.is_matched()
    assert r.standard_name == "Betacoronavirus pandemicum"


def test_ncbi_id():
    e = AlignmentEngine()
    r = e.match_one("3418604")
    assert r.is_matched()
    assert r.standard_name == "Betacoronavirus pandemicum"
    assert r.match_source == "ncbi_id"


def test_zika():
    e = AlignmentEngine()
    r = e.match_one("Zika virus")
    assert r.is_matched()
    assert r.standard_name == "Orthoflavivirus zikaense"


def test_unmatched():
    e = AlignmentEngine()
    r = e.match_one("This virus does not exist")
    assert not r.is_matched()
    assert r.match_source == "unmatched"


def test_empty():
    e = AlignmentEngine()
    r = e.match_one("")
    assert not r.is_matched()


def test_batch():
    e = AlignmentEngine()
    names = ["SARS-CoV-2", "Zika virus", "Unknown virus", "Betacoronavirus pandemicum"]
    results = e.match_batch(names)
    assert len(results) == 4
    assert results[0].is_matched()
    assert not results[2].is_matched()


def test_all_aliases():
    e = AlignmentEngine()
    failed = []
    for alias, ictv in IMPORTANT_VIRUS_ALIASES.items():
        r = e.match_one(alias)
        if not r.is_matched() or r.standard_name != ictv:
            failed.append((alias, ictv, r.standard_name))
    assert len(failed) == 0, f"{len(failed)} failures: {failed[:3]}"


def test_to_dict():
    r = MatchResult(input_name="test", standard_name="X", match_source="exact",
                   taxonomy={"Family": "Test"})
    d = r.to_dict()
    assert d["ictv_standard_name"] == "X"
    assert d["ictv_match_source"] == "exact"
    assert d["ictv_family"] == "Test"


def test_normalize():
    assert normalize_virus_name("SARS-CoV-2") == "sars cov 2"
    assert normalize_virus_name("Zika_Virus") == "zika virus"
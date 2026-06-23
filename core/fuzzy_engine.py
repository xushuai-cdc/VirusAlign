# -*- coding: utf-8 -*-
"""Fuzzy matching engine with spell correction and domain-aware conflict resolution.

Extends the base AlignmentEngine with:
- Levenshtein-based fuzzy name matching for typo tolerance
- Spell correction suggestions ("Zikka" -> "Zika")
- Domain-based abbreviation disambiguation (CMV -> human vs plant)
"""

import re
from typing import Dict, List, Optional, Tuple

# Thresholds
FUZZY_THRESHOLD = 0.78        # Minimum similarity to accept a fuzzy match
SUGGEST_THRESHOLD = 0.60     # Minimum similarity to offer a suggestion

# Domain-aware abbreviation disambiguation table
AMBIGUITY_TABLE = {
    "cmv": {
        "human": "Cytomegalovirus humanbeta5",
        "plant": "Caulimovirus tessellobrassicae",
        "default": "human",
        "note": "CMV: ??????(Cytomegalovirus) / ??????"
    },
    "hsv": {
        "human": "Simplexvirus humanalpha1",
        "plant": "Soymovirus hibisci",
        "default": "human",
        "note": "HSV: ???????(Herpes simplex) / ????"
    },
    "sars": {
        "human": "Betacoronavirus pandemicum",
        "animal": "Betacoronavirus cameli",
        "default": "human",
        "note": "SARS: ?SARS/SARS-CoV-2 / ??MERS??????"
    },
}


def levenshtein(a: str, b: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(curr[j] + 1, prev[j + 1] + 1, prev[j] + cost))
        prev = curr
    return prev[-1]


def similarity_ratio(a: str, b: str) -> float:
    """Compute similarity ratio (1.0 = identical)."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    # Try rapidfuzz first (faster)
    try:
        from rapidfuzz import fuzz
        return fuzz.token_sort_ratio(a, b) / 100.0
    except ImportError:
        pass
    # Fallback: Levenshtein
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 1.0
    return 1.0 - levenshtein(a, b) / max_len


def normalize(s: str) -> str:
    """Normalize: lowercase, strip punctuation, collapse spaces."""
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


class FuzzyEngine:
    """Fuzzy matcher with spell correction and conflict resolution."""

    def __init__(self, alias_map: Dict[str, str], species_index: Dict[str, dict]):
        self._alias = alias_map
        self._index = species_index
        self._build_search_index()

    def _build_search_index(self):
        """Build a flat list of (normalized_name, original_name, type) for fuzzy matching."""
        self._candidates: List[Tuple[str, str, str]] = []
        seen = set()
        # Add all ICTV standard species names
        for species_name in self._index:
            n = normalize(species_name)
            if n not in seen:
                self._candidates.append((n, species_name, "standard"))
                seen.add(n)
        # Add all alias names
        for alias_name in self._alias:
            n = normalize(alias_name)
            if n not in seen:
                self._candidates.append((n, alias_name, "alias"))
                seen.add(n)
        self._candidates.sort(key=lambda x: len(x[1]))

    def fuzzy_search(self, query: str) -> List[Tuple[str, str, str, float]]:
        """Return sorted list of (matched_name, ictv_species, match_type, score)."""
        nq = normalize(query)
        if not nq:
            return []
        if nq.isdigit():
            return []
        results = []
        for nc, orig, mtype in self._candidates:
            score = similarity_ratio(nq, nc)
            if score >= SUGGEST_THRESHOLD:
                ictv = self._alias.get(orig, orig) if mtype == "alias" else orig
                results.append((orig, ictv, mtype, score))
        results.sort(key=lambda x: -x[3])
        return results[:10]

    def suggest(self, query: str) -> Optional[Tuple[str, str, float]]:
        """Return (suggestion, ictv_name, confidence) if a close match exists."""
        results = self.fuzzy_search(query)
        if not results:
            return None
        best = results[0]
        if best[3] >= FUZZY_THRESHOLD:
            return (best[0], best[1], best[3])
        return None

    def spell_correct(self, query: str) -> Optional[str]:
        """Return a spell-corrected query if input looks misspelled."""
        nq = normalize(query)
        if nq in {x[0] for x in self._candidates}:
            return None  # Already exact (after normalize)
        sug = self.suggest(query)
        if sug and sug[2] >= FUZZY_THRESHOLD:
            return sug[0]
        return None

    def resolve_ambiguity(self, query: str, domain: str = "human") -> Optional[dict]:
        """Check if query is an ambiguous abbreviation and resolve by domain.

        Returns dict with resolved species, note, and alternative if applicable.
        """
        nq = normalize(query)
        for abbr, rules in AMBIGUITY_TABLE.items():
            if nq == abbr or nq.startswith(abbr + " "):
                dom = domain if domain in rules else rules["default"]
                result = {
                    "resolved": rules[dom],
                    "domain": dom,
                    "note": rules.get("note", ""),
                }
                alt_dom = "plant" if dom == "human" else "human"
                if alt_dom in rules:
                    result["alternative"] = rules[alt_dom]
                return result
        return None

    def batch_fuzzy_search(self, queries):
        """Run fuzzy search on multiple queries."""
        results = {}
        for q in queries:
            sug = self.suggest(q)
            amb = self.resolve_ambiguity(q)
            results[q] = {
                "input": q,
                "suggestion": sug[0] if sug else None,
                "ictv_name": sug[1] if sug else None,
                "confidence": round(sug[2], 3) if sug else 0.0,
                "ambiguity": amb,
            }
        return results

    def format_suggestion(self, query):
        return None

    def get_stats(self):
        return {
            "candidates": len(self._candidates),
            "standard_names": sum(1 for _, _, t in self._candidates if t == "standard"),
            "alias_names": sum(1 for _, _, t in self._candidates if t == "alias"),
        }


if __name__ == "__main__":
    import json
    demo_aliases = {
        "sars-cov-2": "Betacoronavirus pandemicum",
        "zika virus": "Orthoflavivirus zikaense",
        "covid 19": "Betacoronavirus pandemicum",
        "cmv": "Cytomegalovirus humanbeta5",
    }
    demo_index = {v: {"Species": v} for v in demo_aliases.values()}
    fe = FuzzyEngine(demo_aliases, demo_index)
    for test in ["Zikka", "CMV", "sars-cov-2", "covid19"]:
        print(f"Input: {test}")
        sug = fe.suggest(test)
        if sug:
            print(f"  -> {sug[0]} ({int(sug[2]*100)}%)")
        amb = fe.resolve_ambiguity(test)
        if amb:
            print(f"  Domain: {amb['resolved']} ({amb['domain']})")

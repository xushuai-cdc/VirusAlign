# -*- coding: utf-8 -*-
"""VirusAlign core matching engine - three-tier heuristic alignment."""

import urllib.request
import re
from typing import Dict, List, Optional, Tuple

from core.config import MATCH_CONFIDENCE, TAXONOMY_LEVELS
from core.data_manager import DataManager
from core.exceptions import NCBIAPIError, NetworkTimeoutError
from core.logger import get_logger
from core.utils import ncbi_efetch_taxonomy, normalize_taxonomy_key

logger = get_logger("engine")


class MatchResult:
    """Represents the outcome of a single virus name matching operation.

    Stores the matched standard name, match source type, confidence score,
    full taxonomic path, and detailed taxonomy hierarchy.

    Attributes:
        input_name (str): Original input string provided by the user.
        standard_name (str): Standardized ICTV species name (empty if unmatched).
        match_source (str): Matching method: exact | alias | ncbi_id | unmatched.
        match_confidence (float): Confidence score between 0.0 and 1.0.
        full_path (str): Complete taxonomic path delimited by " / ".
        taxonomy (dict): Dictionary mapping taxonomic levels to their values.
    """

    def __init__(
        self,
        input_name: str = "",
        standard_name: str = "",
        match_source: str = "unmatched",
        match_confidence: float = 0.0,
        full_path: str = "",
        taxonomy: Optional[Dict[str, str]] = None,
    ):
        self.input_name = input_name
        self.standard_name = standard_name
        self.match_source = match_source
        self.match_confidence = match_confidence
        self.full_path = full_path
        self.taxonomy = taxonomy or {}

    def is_matched(self) -> bool:
        """Check whether this result represents a successful match."""
        return self.match_source != "unmatched"

    def to_dict(self) -> Dict[str, str]:
        """Convert to flat dict for CSV output.

        Returns a dict containing ICTV standard fields plus all taxonomic
        levels, prefixed with 'ictv_'.
        """
        result: Dict[str, str] = {
            "ictv_standard_name": self.standard_name,
            "ictv_match_source": self.match_source,
            "ictv_full_path": self.full_path,
        }
        for level in TAXONOMY_LEVELS:
            key = level.lower()
            result["ictv_" + key] = self.taxonomy.get(level, "")
        return result

    def __repr__(self) -> str:
        return (
            f"MatchResult(input={self.input_name}, "
            f"standard={self.standard_name}, "
            f"source={self.match_source})"
        )


class AlignmentEngine:
    """Three-tier heuristic matching engine for virus name alignment.

    Performs staged matching: exact hash lookup -> alias map lookup ->
    NCBI tax_id lookup (local + live API fallback). Results include
    full taxonomic hierarchy reconstructed from the ICTV taxonomy tree.

    Examples:
        >>> engine = AlignmentEngine()
        >>> result = engine.match_one("SARS-CoV-2")
        >>> result.standard_name
        'Betacoronavirus pandemicum'
    """

    def __init__(self, data_manager: Optional[DataManager] = None) -> None:
        """Initialize the engine with a DataManager instance.

        Args:
            data_manager: DataManager instance for loading taxonomy and mappings.
                Creates a new one if not provided.
        """
        self._data = data_manager or DataManager()
        # 累计匹配统计，用于会话级别的结果审计
        self._stats: Dict[str, int] = {
            "exact": 0, "alias": 0, "ncbi_id": 0, "unmatched": 0
        }
        self._idx_lower = None
        logger.info("AlignmentEngine initialized")

    @property
    def match_stats(self) -> Dict[str, int]:
        """Get cumulative match statistics for the current session."""
        return dict(self._stats)

    def _match_exact(self, name: str) -> Optional[MatchResult]:
        """Stage 1: Exact match against the ICTV species index.

        Searches the in-memory hash index (species name -> taxonomy entry)
        for direct ICTV formal name matches. O(1) lookup.

        Args:
            name: Normalized species name.
        Returns:
            MatchResult if found, None otherwise.
        """
        idx = self._data.get_species_index()
        if name in idx:
            self._stats["exact"] += 1
            logger.debug(f"Exact match: {name}")
            return self._build_match(name, "exact", idx[name])
        if self._idx_lower is None:
            self._idx_lower = {k.lower(): (k, v) for k, v in idx.items()}
        if name in self._idx_lower:
            orig_name, entry = self._idx_lower[name]
            self._stats["exact"] += 1
            logger.debug(f"Exact match (case-insensitive): {name}")
            return self._build_match(orig_name, "exact", entry)
        return None

    def _match_alias(self, name: str) -> Optional[MatchResult]:
        """Stage 2: Alias match against the semantic alias mapping table.

        Queries the 52,844-entry alias dictionary which covers common
        abbreviations, informal names, and historical synonyms.

        Args:
            name: Normalized name to look up.
        Returns:
            MatchResult if alias found, None otherwise.
        """
        alias = self._data.get_alias_map()
        idx = self._data.get_species_index()
        if name in alias:
            ictv_name = alias[name]
            if ictv_name in idx:
                self._stats["alias"] += 1
                logger.debug(f"Alias match: {name} -> {ictv_name}")
                return self._build_match(ictv_name, "alias", idx[ictv_name])
        return None

    def _match_ncbi_local(self, name: str) -> Optional[MatchResult]:
        """Stage 3a: Local NCBI tax_id mapping lookup.

        Args:
            name: Numeric tax_id string.
        Returns:
            MatchResult if tax_id found in pre-built mapping, None otherwise.
        """
        ncbi = self._data.get_ncbi_map()
        idx = self._data.get_species_index()
        if name in ncbi:
            ictv_name = ncbi[name]
            if ictv_name in idx:
                self._stats["ncbi_id"] += 1
                logger.debug(f"NCBI local: {name} -> {ictv_name}")
                return self._build_match(ictv_name, "ncbi_id", idx[ictv_name])
        return None

    def _match_ncbi_live(self, name: str) -> Optional[MatchResult]:
        """Stage 3b: Real-time NCBI API fallback for unknown tax_ids.

        When a numeric ID is not found in the local mapping table,
        this method queries the NCBI Taxonomy API in real-time to
        resolve the current scientific name, then attempts to match
        it against the alias map and species index.

        Args:
            name: Numeric tax_id string (possibly legacy/obsolete).
        Returns:
            MatchResult if resolved, None otherwise.
        """
        try:
            sci_names = ncbi_efetch_taxonomy(name)
            if not sci_names:
                return None
            # 用 NCBI 返回的科学名再次尝试匹配
            sci = normalize_taxonomy_key(sci_names[0])
            idx = self._data.get_species_index()
            if sci in idx:
                self._stats["ncbi_id"] += 1
                return self._build_match(sci, "ncbi_id", idx[sci])
            alias = self._data.get_alias_map()
            if sci in alias and alias[sci] in idx:
                self._stats["ncbi_id"] += 1
                return self._build_match(alias[sci], "ncbi_id", idx[alias[sci]])
        except (NCBIAPIError, NetworkTimeoutError) as e:
            logger.warning(f"Live lookup failed: {name}: {e}")
        except Exception as e:
            logger.error(f"Live lookup error: {name}: {e}")
        return None

    def _build_match(self, ictv_name: str, source: str, entry: dict) -> MatchResult:
        """Construct a MatchResult from match results.

        Args:
            ictv_name: The matched ICTV species name.
            source: Match source type (exact/alias/ncbi_id).
            entry: Species entry from the taxonomy tree containing all levels.
        Returns:
            A fully populated MatchResult instance.
        """
        confidence = MATCH_CONFIDENCE.get(source, 0.0)
        return MatchResult(
            standard_name=ictv_name,
            match_source=source,
            match_confidence=confidence,
            full_path=entry.get("full_path", ""),
            taxonomy=entry,
        )

    def match_one(self, raw_name: str) -> MatchResult:
        """Execute three-tier matching on a single virus name.

        Priority: exact match > alias match > NCBI ID lookup (local + live).
        Also tries format variants (underscore, hyphen) during alias matching.

        Args:
            raw_name: Virus name string or NCBI tax_id from user input.
        Returns:
            MatchResult with the best available match information.
        """
        name = raw_name.strip()
        if not name:
            return MatchResult(input_name=raw_name)

        normalized = normalize_taxonomy_key(name)

        # 第一级：哈希精确匹配
        result = self._match_exact(normalized)
        if result:
            result.input_name = raw_name
            return result

        # 第二级：语义别名匹配
        result = self._match_alias(normalized)
        if result:
            result.input_name = raw_name
            return result

        # 尝试剥离所有非字母数字字符（连写变体：covid19, sarscov2）
        stripped = re.sub(r"[^a-z0-9]", "", normalized)
        if stripped and stripped != normalized:
            result = self._match_exact(stripped)
            if result:
                result.input_name = raw_name
                return result
            result = self._match_alias(stripped)
            if result:
                result.input_name = raw_name
                return result

        # 尝试格式变体（下划线、短横线）
        for variant in [normalized.replace(" ", "_"), normalized.replace(" ", "-")]:
            if variant != normalized:
                result = self._match_alias(variant)
                if result:
                    result.input_name = raw_name
                    return result

        # 第三级：NCBI ID 匹配（先本地后实时查询）
        if name.isdigit():
            result = self._match_ncbi_local(name)
            if result:
                result.input_name = raw_name
                return result
            # 本地未命中时激活 API 回退
            result = self._match_ncbi_live(name)
            if result:
                result.input_name = raw_name
                return result

        # 全链路过未匹配
        self._stats["unmatched"] += 1
        logger.debug(f"Unmatched: {raw_name}")
        return MatchResult(input_name=raw_name)

    def match_batch(
        self,
        names: List[str],
        callback=None,
    ) -> List[MatchResult]:
        """Batch process multiple names through the matching pipeline.

        Processes names sequentially with an optional progress callback.
        Suitable for handling CSV batch uploads with thousands of entries.

        Args:
            names: List of virus name strings to process.
            callback: Optional function(current, total) for progress reporting.
        Returns:
            List of MatchResult objects, one per input name.
        """
        results: List[MatchResult] = []
        total = len(names)
        for i, name in enumerate(names):
            results.append(self.match_one(name))
            if callback and i % 10 == 0:
                callback(i + 1, total)
        logger.info(f"Batch done: {total} items, stats={self._stats}")
        return results
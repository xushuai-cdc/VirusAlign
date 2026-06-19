# -*- coding: utf-8 -*-
"""Data manager for VirusAlign JSON file loading and caching."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.config import DataPaths
from src.exceptions import DataIntegrityError, MappingDataError, TaxonomyTreeError
from src.logger import get_logger

logger = get_logger("data_manager")


class DataManager:
    """Central data manager for loading and caching VirusAlign JSON data files."""

    def __init__(self, cache_ttl_seconds: int = 300) -> None:
        self._cache_ttl = cache_ttl_seconds
        self._taxonomy_tree: Optional[Dict[str, Any]] = None
        self._alias_map: Optional[Dict[str, str]] = None
        self._ncbi_map: Optional[Dict[str, str]] = None
        self._species_index: Optional[Dict[str, Dict[str, str]]] = None
        self._load_time: Dict[str, float] = {}

    def _needs_reload(self, key: str) -> bool:
        if key not in self._load_time:
            return True
        return (time.time() - self._load_time[key]) > self._cache_ttl

    def _load_json(self, path: Path, key: str) -> Dict:
        if not path.exists():
            raise TaxonomyTreeError(f"Data file not found: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._load_time[key] = time.time()
            logger.info(f"Loaded {path.name}")
            return data
        except json.JSONDecodeError as e:
            raise TaxonomyTreeError(f"JSON parse error: {path.name}: {e}")

    def get_taxonomy_tree(self) -> Dict[str, Any]:
        if self._taxonomy_tree is None or self._needs_reload("tree"):
            self._taxonomy_tree = self._load_json(DataPaths.TAXONOMY_TREE, "tree")
            self._species_index = None
        return self._taxonomy_tree

    def get_species_index(self) -> Dict[str, Dict[str, str]]:
        if self._species_index is not None and not self._needs_reload("idx"):
            return self._species_index
        tree = self.get_taxonomy_tree()
        species_list = tree.get("species", [])
        if not species_list:
            raise MappingDataError("No species data in taxonomy tree")
        self._species_index = {s["Species"]: s for s in species_list}
        self._load_time["idx"] = time.time()
        return self._species_index

    def get_alias_map(self) -> Dict[str, str]:
        if self._alias_map is None or self._needs_reload("alias"):
            self._alias_map = self._load_json(DataPaths.ALIAS_MAP, "alias")
        return self._alias_map

    def get_ncbi_map(self) -> Dict[str, str]:
        if self._ncbi_map is None or self._needs_reload("ncbi"):
            self._ncbi_map = self._load_json(DataPaths.NCBI_MAP, "ncbi")
        return self._ncbi_map

    def reload_all(self) -> None:
        """Force reload all data files from disk."""
        logger.info("Force reloading all data files")
        self._taxonomy_tree = None
        self._alias_map = None
        self._ncbi_map = None
        self._species_index = None
        self._load_time.clear()
        self.get_taxonomy_tree()
        self.get_alias_map()
        self.get_ncbi_map()
        logger.info("All data files reloaded")

    def verify_integrity(self) -> Tuple[bool, List[str]]:
        errors: List[str] = []
        for name, path in [("tree", DataPaths.TAXONOMY_TREE),
                          ("alias", DataPaths.ALIAS_MAP),
                          ("ncbi", DataPaths.NCBI_MAP)]:
            if not path.exists():
                errors.append(f"{name} file missing: {path}")
        if not errors:
            tree = self.get_taxonomy_tree()
            if "species_count" not in tree:
                errors.append("Missing species_count")
            alias = self.get_alias_map()
            if len(alias) < 1000:
                errors.append(f"Too few alias entries: {len(alias)}")
        return len(errors) == 0, errors
"""VirusAlign 全局配置模块"""
import os
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class DataPaths:
    RAW_DIR = PROJECT_ROOT / "data" / "raw"
    PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
    TAXONOMY_TREE = PROCESSED_DIR / "ictv_taxonomy_tree.json"
    ALIAS_MAP = PROCESSED_DIR / "alias_to_ictv.json"
    NCBI_MAP = PROCESSED_DIR / "ncbi_to_ictv.json"
    EXAMPLES_DIR = PROJECT_ROOT / "examples"
    OUTPUT_DIR = PROJECT_ROOT / "output"

NCBI_EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
NCBI_USER_AGENT = "VirusAlign/1.0"
NCBI_REQUEST_TIMEOUT = 10

MATCH_CONFIDENCE = {"exact": 1.0, "alias": 0.9, "ncbi_id": 0.95}
DEFAULT_NAME_COLUMN = "name"
STREAMLIT_TITLE = "VirusAlign"

TAXONOMY_LEVELS = [
    "Realm", "Subrealm", "Kingdom", "Subkingdom",
    "Phylum", "Subphylum", "Class", "Subclass",
    "Order", "Suborder", "Family", "Subfamily",
    "Genus", "Subgenus", "Species",
]

OUTPUT_FIELD_NAMES = [
    "ictv_standard_name", "ictv_match_source", "ictv_full_path",
    "ictv_realm", "ictv_kingdom", "ictv_phylum", "ictv_class",
    "ictv_order", "ictv_family", "ictv_genus", "ictv_species",
]

SOFTWARE_VERSION = "1.0"
SOFTWARE_NAME_CN = "基于ICTV标准的病原体物种语义映射与分类标准化系统V1.0"
SOFTWARE_NAME_EN = "VirusAlign"

# -*- coding: utf-8 -*-
"""VirusAlign web interface - Streamlit implementation."""

import importlib.util
import sys
import types
from pathlib import Path

import streamlit as st
import pandas as pd

# 绕过 sys.path, 直接从文件路径加载模块（解决 Streamlit Cloud 路径冲突）
FILE_DIR = Path(__file__).resolve().parent
CORE_DIR = FILE_DIR / "core"

# 注册 core 包到 sys.modules
core_pkg = types.ModuleType("core")
core_pkg.__path__ = [str(CORE_DIR)]
core_pkg.__file__ = str(CORE_DIR / "__init__.py")
sys.modules["core"] = core_pkg

def _load(name, fp):
    spec = importlib.util.spec_from_file_location(name, fp)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

dep_order = ["exceptions","logger","utils","config","constants","data_manager","engine"]
for mod_name in dep_order:
    _load("core." + mod_name, CORE_DIR / (mod_name + ".py"))

_mod = sys.modules["core.config"]
SOFTWARE_NAME_CN = _mod.SOFTWARE_NAME_CN
SOFTWARE_NAME_EN = _mod.SOFTWARE_NAME_EN
SOFTWARE_VERSION = _mod.SOFTWARE_VERSION
ICTV_VERSION = _mod.ICTV_VERSION
_mod = sys.modules["core.constants"]
MATCH_SOURCE_LABELS = _mod.MATCH_SOURCE_LABELS
VIRUS_COVERAGE_CATEGORIES = _mod.VIRUS_COVERAGE_CATEGORIES
_mod = sys.modules["core.data_manager"]
DataManager = _mod.DataManager
_mod = sys.modules["core.engine"]
AlignmentEngine = _mod.AlignmentEngine
_mod = sys.modules["core.logger"]
configure_logger = _mod.configure_logger

st.set_page_config(
    page_title=SOFTWARE_NAME_EN + " - " + SOFTWARE_NAME_CN,
    page_icon="",
    layout="centered",
)

# --------------- Initialize engine ---------------
@st.cache_resource
def init_engine():
    """Initialize the AlignmentEngine with data integrity check."""
    dm = DataManager(cache_ttl_seconds=600)
    ok, errs = dm.verify_integrity()
    if not ok:
        st.error(f"Data integrity check failed: {errs[0]}")
        return None
    engine = AlignmentEngine(dm)
    # Pre-load data to warm the cache
    dm.get_taxonomy_tree()
    dm.get_alias_map()
    dm.get_ncbi_map()
    return engine

engine = init_engine()
if engine is None:
    st.stop()

# --------------- Sidebar ---------------
with st.sidebar:
    st.markdown(f"### {SOFTWARE_NAME_EN}")
    st.caption(f"v{SOFTWARE_VERSION} | {ICTV_VERSION}")
    st.divider()
    st.markdown("**Data Overview**")
    dm = engine._data
    st.markdown(f"- Species in taxonomy tree: {dm.get_taxonomy_tree().get("species_count", 0)}")
    st.markdown(f"- Alias mappings: {len(dm.get_alias_map()):,}")
    st.markdown(f"- NCBI tax_id mappings: {len(dm.get_ncbi_map()):,}")
    st.divider()
    st.markdown("**Session Stats**")
    stats = engine.match_stats
    st.markdown(f"- Exact matches: {stats["exact"]}")
    st.markdown(f"- Alias matches: {stats["alias"]}")
    st.markdown(f"- API fallback: {stats["ncbi_id"]}")
    st.markdown(f"- Unmatched: {stats["unmatched"]}")
    st.divider()
    st.markdown("**Pathogen Coverage**")
    for cat, viruses in VIRUS_COVERAGE_CATEGORIES:
        st.markdown(f"- **{cat}**: {', '.join(viruses[:4])}")

# --------------- Main interface ---------------
st.title(SOFTWARE_NAME_EN)
st.caption(f"v{SOFTWARE_VERSION} | {SOFTWARE_NAME_CN}")
st.caption("Enter a virus name or NCBI tax_id to get standardized ICTV classification.")

tab1, tab2 = st.tabs([
    "Quick Lookup (单名查询)",
    "Batch Process (批量处理)",
])

# ===== Tab 1: Quick Lookup =====
with tab1:
    query = st.text_input(
        "Virus name or NCBI tax_id",
        placeholder="e.g. SARS-CoV-2, 3418604, 1003835, Zika virus",
        label_visibility="collapsed",
    )
    if query:
        with st.spinner("Matching..."):
            result = engine.match_one(query)
        if result.is_matched():
            label = MATCH_SOURCE_LABELS.get(result.match_source, result.match_source)
            st.success(f"Recognized  |  {label}")
            c1, c2 = st.columns(2)
            c1.metric("Standard Name", result.standard_name)
            c2.metric("Match Method", label)
            c3, c4 = st.columns(2)
            c3.metric("Family (科)", result.taxonomy.get("Family", "-"))
            c4.metric("Genus (属)", result.taxonomy.get("Genus", "-"))
            with st.expander("Full Taxonomy Path (完整分类路径)", expanded=True):
                st.code(result.full_path, language="text")
            with st.expander("All Levels (各级分类)"):
                for level in ["Realm","Kingdom","Phylum","Class","Order","Family","Genus","Species"]:
                    val = result.taxonomy.get(level, "-")
                    st.text(f"{level:>12}: {val}")
        else:
            st.error("Unmatched (未匹配到 ICTV 物种)")
            st.info("Tip: Check spelling, or try the NCBI tax_id instead.")

# ===== Tab 2: Batch Process =====
with tab2:
    uploaded = st.file_uploader(
        "Upload CSV / Excel file (上传文件)",
        type=["csv", "xlsx"],
        help="File must contain a column with virus names (ICTV name, alias, or NCBI tax_id).",
    )
    if uploaded:
        try:
            if uploaded.name.endswith(".csv"):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
        except Exception as e:
            st.error(f"Failed to read file: {e}")
            st.stop()
        name_col = st.text_input(
            "Column name for virus names (病毒名列)",
            value="name",
        )
        if name_col not in df.columns:
            cols = ", ".join(df.columns)
            st.error(f'Column "{name_col}" not found. Available: {cols}')
            st.stop()
        if st.button("Standardize Now (开始标准化)", type="primary"):
            bar = st.progress(0, text="Processing...")
            total = len(df)
            names = df[name_col].astype(str).tolist()

            def update_progress(cur, tot):
                bar.progress(cur / tot, f"{cur}/{tot} ({cur*100//tot}%)")

            results = engine.match_batch(names, callback=update_progress)
            bar.empty()
            out_rows = []
            for i, (_, row) in enumerate(df.iterrows()):
                merged = row.to_dict()
                merged.update(results[i].to_dict())
                out_rows.append(merged)
            out_df = pd.DataFrame(out_rows)
            stats = engine.match_stats
            matched = total - stats["unmatched"]
            pct = matched * 100 // total if total else 0
            st.success(f"Done! Match rate: {matched}/{total} ({pct}%)")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Exact (精确)", stats["exact"])
            c2.metric("Alias (别名)", stats["alias"])
            c3.metric("API (回退)", stats["ncbi_id"])
            c4.metric("Unmatched", stats["unmatched"])
            with st.expander("Preview (预览)", expanded=True):
                preview_cols = [name_col, "ictv_standard_name", "ictv_match_source", "ictv_family"]
                preview_cols = [c for c in preview_cols if c in out_df.columns]
                st.dataframe(out_df[preview_cols].head(30), use_container_width=True, hide_index=True)
            csv_data = out_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Result (下载标准化 CSV)",
                data=csv_data,
                file_name="virusalign_result.csv",
                mime="text/csv",
                type="primary",
            )

# --------------- Footer ---------------
st.divider()
st.caption(f"VirusAlign v{SOFTWARE_VERSION} | {SOFTWARE_NAME_CN} | ICTV MSL41")
st.caption("Online: https://virusalign.streamlit.app/ | GitHub: VirusAlign")
# -*- coding: utf-8 -*-
"""VirusAlign web interface - Streamlit implementation."""

import sys
from pathlib import Path

import streamlit as st
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import SOFTWARE_NAME_CN, SOFTWARE_NAME_EN, SOFTWARE_VERSION, ICTV_VERSION
from core.constants import MATCH_SOURCE_LABELS, VIRUS_COVERAGE_CATEGORIES
from core.data_manager import DataManager
from core.engine import AlignmentEngine
from core.logger import configure_logger
from urllib.parse import quote

st.set_page_config(
    page_title=SOFTWARE_NAME_EN + " - " + SOFTWARE_NAME_CN,
    page_icon="🦠",
    layout="centered",
)


@st.cache_resource
def init_engine():
    """Initialize the AlignmentEngine with data integrity check."""
    dm = DataManager(cache_ttl_seconds=600)
    ok, errs = dm.verify_integrity()
    if not ok:
        st.error(f"Data integrity check failed: {errs[0]}")
        return None
    engine = AlignmentEngine(dm)
    dm.get_taxonomy_tree()
    dm.get_alias_map()
    dm.get_ncbi_map()
    return engine


engine = init_engine()
if engine is None:
    st.stop()

# ======================== Sidebar ========================
with st.sidebar:
    st.markdown("### VirusAlign v1.0")
    st.caption("MSL41 (2025 Release)")
    st.divider()
    st.markdown("### 数据看板 - Data Overview")
    st.caption("本库已集成：")
    dm = engine._data
    st.markdown(f"{dm.get_taxonomy_tree().get('species_count', 0):,} 标准物种 (ICTV)")
    st.markdown(f"{len(dm.get_alias_map()):,} 语义别名")
    st.markdown(f"{len(dm.get_ncbi_map()):,} 跨库 ID 映射")
    st.divider()
    st.markdown("**当前会话 - Session Stats**")
    st.caption("(动态统计本次查询情况)")
    stats = engine.match_stats
    st.markdown(f"精确匹配: {stats['exact']} | 别名对齐: {stats['alias']}")
    st.markdown(f"API 溯源: {stats['ncbi_id']} | 未能匹配: {stats['unmatched']}")
    st.divider()
    st.markdown("**重点关注病原谱 - Priority Pathogens**")
    st.caption("系统全量覆盖 1.7 万种物种，重点对齐以下高风险类：")
    pathogens = [
        ("冠状病毒科 (Coronaviridae)", "新型冠状病毒 (SARS-CoV-2), 中东呼吸综合征 (MERS-CoV), 非典 (SARS-CoV)"),
        ("正粘病毒科 (Orthomyxoviridae)", "甲型流感 (Flu A), 乙型流感 (Flu B)"),
        ("黄病毒科 (Flaviviridae)", "登革病毒 (DENV), 寨卡病毒 (ZIKV), 乙型脑炎 (JEV), 丙型肝炎 (HCV)"),
        ("布尼亚病毒目 (Bunyavirales)", "新布尼亚病毒 (SFTSV), 汉坦病毒 (HV), 克里米亚-刚果出血热 (CCHF)"),
        ("副黏病毒科 (Paramyxoviridae)", "尼帕病毒 (NiV), 呼吸道合胞病毒 (RSV), 麻疹病毒 (Measles), 腮腺炎病毒 (Mumps)"),
        ("丝状病毒科 (Filoviridae)", "埃博拉病毒 (Ebola), 马尔堡病毒 (MARV)"),
        ("小核糖核酸病毒科 (Picornaviridae)", "脊髓灰质炎 (PV), 鼻病毒 (HRV), 手足口病 (EV-A71/CA16)"),
        ("逆转录病毒科 (Retroviridae)", "艾滋病毒 (HIV-1/2), 人T细胞白血病病毒 (HTLV)"),
        ("疱疹病毒科 (Herpesviridae)", "单纯疱疹 (HSV-1/2), 水痘-带状疱疹 (VZV), EB病毒 (EBV), 巨细胞病毒 (CMV)"),
        ("肝病毒科 (Hepadnaviridae)", "乙型肝炎 (HBV)"),
        ("披盖病毒科 (Togaviridae)", "基孔肯雅病毒 (CHIKV), 风疹病毒 (Rubella)"),
        ("痘病毒科 (Poxviridae)", "猴痘 (Mpox), 牛痘 (Vaccinia), 天花 (Smallpox)"),
        ("弹状病毒科 (Rhabdoviridae)", "狂犬病毒 (Rabies)"),
        ("杯状病毒科 (Caliciviridae)", "诺如病毒 (NoV), 扎幌病毒 (SaV)"),
        ("呼肠孤病毒科 (Reoviridae)", "轮状病毒 (RV)"),
        ("其他高风险类", "乳头瘤 (HPV), 腺病毒 (Adv), 星状病毒 (AstV), 多瘤病毒 (BKV/JCV)"),
    ]
    for cat, viruses in pathogens:
        m = __import__("re").search(r"\(([^)]+)\)", cat)
        if m:
            cn = cat[:m.start()].strip()
            la = m.group(1)
            st.markdown(f"- **{cn} (*{la}*)**: {viruses}")
        else:
            st.markdown(f"- **{cat}**: {viruses}")
    st.divider()
    st.markdown("**底层声明 - Privacy & Safety**")
    st.caption("\U0001f512 Privacy Note: Data processed in memory only; cleared after session.")

# ======================== Main Interface ========================
st.title(SOFTWARE_NAME_EN)
st.markdown(f"**{SOFTWARE_NAME_CN}**")
st.caption(f"v{SOFTWARE_VERSION} | {ICTV_VERSION}")
st.write("Enter a virus name or NCBI tax_id to get standardized ICTV classification.")

tab1, tab2 = st.tabs(["🔍 Quick Lookup (单名查询)", "📂 Batch Process (批量处理)"])

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
                st.success(f"已识别 — {label}")
                st.markdown(f"**标准物种名**: *{result.standard_name}*")
                col1, col2 = st.columns(2)
                col1.markdown(f"**科 (Family)**: *{result.taxonomy.get('Family', '-')}*")
                col2.markdown(f"**属 (Genus)**: *{result.taxonomy.get('Genus', '-')}*")

                enc = quote(result.standard_name)
                st.markdown(
                    "🔗 **外部链接**: "
                    "[ICTV Taxonomy](https://ictv.global/taxonomy/) | "
                    f"[NCBI Taxonomy](https://www.ncbi.nlm.nih.gov/taxonomy/?term={enc})"
                )

                explanations = {
                    "exact": "系统识别到您的输入与 ICTV 正式物种名完全一致，已精确匹配至标准分类路径。",
                    "alias": "系统识别到您的输入为常见别名，已自动对齐至 ICTV 2025 标准名。",
                    "ncbi_id": "系统通过 NCBI Taxonomy ID 回溯至当前科学名称，已对齐至 ICTV 标准分类。",
                }
                st.caption(explanations.get(result.match_source, ""))

                with st.expander("完整分类路径", expanded=True):
                    st.markdown(f"*{result.full_path}*")

                with st.expander("各级分类"):
                    levels = ["Realm", "Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
                    vals = [result.taxonomy.get(l, "-") for l in levels]
                    color_map = {
                        "Realm": "#003366", "Kingdom": "#004d99", "Phylum": "#336699",
                        "Class": "#008080", "Order": "#2E8B57", "Family": "#50C878",
                        "Genus": "#9ACD32", "Species": "#FF8C00"
                    }
                    for level, val in zip(levels, vals):
                        c = color_map.get(level, "#888")
                        label = f"<span style='color:{c};font-weight:bold'>{level}</span>"
                        if val == "-":
                            st.markdown(f"{label}: -", unsafe_allow_html=True)
                        else:
                            st.markdown(f"{label}: <i>{val}</i>", unsafe_allow_html=True)

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

        name_col = st.selectbox(
            "Select column containing virus names (选择病毒名列)",
            options=df.columns,
            index=0 if "name" not in df.columns else list(df.columns).index("name"),
        )

        if st.button("Standardize Now (开始标准化)", type="primary"):
            bar = st.progress(0, text="Processing...")
            total = len(df)
            names = df[name_col].astype(str).tolist()

            def update_progress(cur, tot):
                bar.progress(cur / tot, f"{cur}/{tot} ({cur * 100 // tot}%)")

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

            chart_df = pd.DataFrame({
                "Method": ["Exact", "Alias", "NCBI API", "Unmatched"],
                "Count": [stats["exact"], stats["alias"], stats["ncbi_id"], stats["unmatched"]]
            })
            st.bar_chart(chart_df, x="Method", y="Count", use_container_width=True)

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

# ======================== Footer ========================
st.divider()
st.caption(f"**VirusAlign** v{SOFTWARE_VERSION} | {SOFTWARE_NAME_CN} | {ICTV_VERSION}")
st.caption(
    "🏗️ 开发单位：中国疾病预防控制中心传染病预防控制所 | "
    "🧧 项目资助：国家科技重大专项 (No. 2025ZD01900116)"
)
st.caption(
    "🌐 在线服务：https://virusalign.streamlit.app/ | "
    "📄 标准规范：ICTV MSL41 (2025)"
)

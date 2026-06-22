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
    layout="wide", #开启宽屏模式
)

# Custom ICTV-aligned styles
st.markdown("""
<style>
/* 1. 全局字体优化：正文使用无衬线，科学名专用类使用衬线斜体 */
@import url('https://fonts.googleapis.com/css2?family=PT+Serif:ital,wght@1,700&display=swap');

.scientific-name {
    font-family: 'PT Serif', 'Times New Roman', serif;
    font-style: italic;
    font-weight: bold;
    color: #003680;
}

/* 2. 按钮样式统一：椭圆设计，增加专业感 */
div.stButton > button {
    border-radius: 20px !important;
    border: 1px solid #ccd1d9 !important;
    background-color: #f8f9fa !important;
    color: #333 !important;
    transition: all 0.3s ease !important;
    height: 3em !important;
    width: 100% !important;
}


/* 悬停效果：使用 ICTV 经典的深蓝色 */
div.stButton > button:hover {
    border-color: #003366 !important;
    background-color: #003366 !important;
    color: white !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
}

/* 3. Tab 导航条居中且加粗 */
div[data-testid="stTabs"] {
    display: flex !important;
    justify-content: center !important;
}

div[data-testid="stTabs"] button {
    font-size: 1.1rem !important;
    font-weight: bold !important;
    min-width: 200px !important;
}

/* 4. 确保 st.success 里的文字是白色的 */
.stAlert {
    border-radius: 10px !important;
}

/* 5. 调整主容器宽度，防止在超宽屏上内容太稀疏 */
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
}

/* 6. ??????? */
.stButton button {
    font-size: 0.7rem !important;
    padding: 2px 4px !important;
    min-width: 0 !important;
    white-space: nowrap !important;
}
.stButton > div {
    padding: 0 1px !important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_engine():
    """Initialize the AlignmentEngine with data integrity check."""
    dm = DataManager(cache_ttl_seconds=600)
    ok, errs = dm.verify_integrity()
    if not ok:
        st.error(f"Data integrity check failed: {errs[0]}")
        return None
    engine = AlignmentEngine(dm)
    # 预加载数据，减少用户第一次查询的等待时间
    engine._data.get_taxonomy_tree()
    engine._data.get_alias_map()
    engine._data.get_ncbi_map()
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
st.markdown(
    '<h1 style="color:#003680;font-size:6.0rem;font-weight:900;margin-bottom:2px;text-align:center;'
    'font-family:Source Sans Pro,sans-serif">VirusAlign</h1>'
    '<p style="color:#222;font-size:2.2rem;margin-top:0;margin-bottom:20px;text-align:center;'
    'font-family:Source Sans Pro,sans-serif">'
    '基于ICTV标准的病原体物种语义映射与分类标准化系统</p>',
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        '<div style="background:#F0F7FF;padding:12px 16px;border-radius:8px;border-left:4px solid #003680;font-size:1.2rem">'
        '<strong>权威合规：</strong><br>深度集成ICTV MSL41分类标准</div>',
        unsafe_allow_html=True
    )
with c2:
    st.markdown(
        '<div style="background:#F0F7FF;padding:12px 16px;border-radius:8px;border-left:4px solid #003680;font-size:1.2rem">'
        '<strong>多源对齐：</strong><br>支持异构命名体系的无缝转换</div>',
        unsafe_allow_html=True
    )
with c3:
    st.markdown(
        '<div style="background:#F0F7FF;padding:12px 16px;border-radius:8px;border-left:4px solid #003680;font-size:1.2rem">'
        '<strong>秒级处理：</strong><br>万级规模数据的自动化治理</div>',
        unsafe_allow_html=True
    )

st.caption(f"v{SOFTWARE_VERSION} | {ICTV_VERSION}")


tab1, tab2 = st.tabs(["🔍 Quick Lookup (单名查询)", "📂 Batch Process (批量处理)"])

# ===== Tab 1: Quick Lookup ====
st.markdown("""
    <style>
    /* 1. 只针对按钮进行外观美化 */
    div.stButton > button {
        width: 100% !important;
        height: 2.6em !important;
        border-radius: 15px !important; /* 圆角矩形 */
        border: 1px solid #ccd1d9 !important;
        background-color: #f8f9fa !important;
        color: #333 !important;
        font-size: 0.85rem !important; /* 稍微缩小字号，防止溢出 */
        transition: all 0.2s ease;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }

    /* 2. 悬停效果 */
    div.stButton > button:hover {
        border-color: #003366 !important;
        background-color: #003366 !important;
        color: white !important;
    }

    /* 3. 强制让按钮容器之间留有微小空隙（防止边框粘连） */
    div.stButton {
        padding: 2px !important;
    }
    </style>
    """, unsafe_allow_html=True)

with tab1:
    st.markdown("<h3 style='text-align:center;color:#000;font-size:2.4rem'>Find the Species</h3>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;color:#888;font-size:1.2rem'>"
        "Identify current official taxon names by searching with virus names, common abbreviations, isolate names, or NCBI Taxonomy IDs."
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='text-align:center;color:#888;font-size:1.1rem;margin-bottom:20px'>"
        "(支持通过病毒名称、常用缩写、分离株名或NCBI分类ID识别标准化物种)"
        "</div>",
        unsafe_allow_html=True
    )

    # 初始化 session_state，用于存储当前查询词
    if "query_input" not in st.session_state:
        st.session_state["query_input"] = ""

    # 搜索布局
    _, search_col, _ = st.columns([1.5, 3, 1.5])
    with search_col:
        # 搜索框：使用 key 绑定
        user_input = st.text_input(
            "Virus name or NCBI tax_id",
            placeholder="e.g. SARS-CoV-2, 3418604, 1003835, Zika",
            key="query_text_field",
            label_visibility="collapsed",
        )

        st.markdown("<div style='text-align:center; font-size:1.0rem; color:#666; margin-top:15px'>Try Samples (点击直接体验):</div>", unsafe_allow_html=True)
        
        # 按钮列
        # ????3???
        row1 = st.columns(3)
        for i, s in enumerate(["SARS-CoV-2", "SFTSV", "3418604"]):
            if row1[i].button(s, key=f"s1_{i}"):
                st.session_state["query_input"] = s
                st.rerun()

        # ????2???
        row2 = st.columns(2)
        for i, s in enumerate(["Zika", "Rabies"]):
            if row2[i].button(s, key=f"s2_{i}"):
                st.session_state["query_input"] = s
                st.rerun()

    # 确定最终查询词：优先用点击按钮的词，否则用用户输入的词
    final_query = st.session_state["query_input"] if st.session_state["query_input"] else user_input

    # 执行匹配并展示结果（只有一个判断块）
    if final_query:
        # 重置 session_state 供下次使用
        st.session_state["query_input"] = ""
        
        with st.spinner("Matching..."):
            result = engine.match_one(final_query)
            
            if result.is_matched():
                # --- A. 状态条 ---
                status_text = MATCH_SOURCE_LABELS.get(result.match_source, result.match_source)
                match_colors = {"exact": "#167f78", "alias": "#003680", "ncbi_id": "#6a0dad"}
                bg_color = match_colors.get(result.match_source, "#888")
                st.markdown(
                    f"<div style='background-color:{bg_color};padding:12px 16px;border-radius:10px;color:white;margin-bottom:16px'>"
                    f"<strong>✅ Status: Identified (状态：已识别) — {status_text}</strong></div>",
                    unsafe_allow_html=True
                )
                
                # --- B. 核心标准名 (斜体) ---
                st.info(f"**Current Taxon Name (当前官方名称)**: *{result.standard_name}*")

                # --- C. 关键层级 (斜体) ---
                col1, col2 = st.columns(2)
                f_val = result.taxonomy.get('Family', '-')
                g_val = result.taxonomy.get('Genus', '-')
                # 如果不是 '-'，则加上斜体标签
                f_display = f"*{f_val}*" if f_val != "-" else "-"
                g_display = f"*{g_val}*" if g_val != "-" else "-"
                
                col1.markdown(f"**Family (科)**: {f_display}")
                col2.markdown(f"**Genus (属)**: {g_display}")

                # --- D. 权威链接 ---
                enc = quote(result.standard_name)
                st.markdown("---")
                st.markdown("**Authoritative Links (权威链接)**")
                l_col1, l_col2, _ = st.columns([1.2, 1.2, 2])
                l_col1.link_button("🌐 ICTV Taxonomy", "https://ictv.global/taxonomy/")
                l_col2.link_button("🔗 NCBI Taxonomy", f"https://www.ncbi.nlm.nih.gov/taxonomy/?term={enc}")

                # --- E. 匹配原理解释 ---
                explanations = {
                    "exact": "系统识别到您的输入与 ICTV 正式物种名完全一致，已精确匹配至标准分类路径。",
                    "alias": "系统识别到您的输入为常见别名，已自动对齐至 ICTV 2025 标准名。",
                    "ncbi_id": "系统通过 NCBI Taxonomy ID 回溯至当前科学名称，已对齐至 ICTV 标准分类。",
                }
                st.caption(f"**Search Context (匹配依据)**: {explanations.get(result.match_source, '')}")

                # --- F. 完整路径 ---
                with st.expander("**Taxonomic Lineage (分类全路径)**", expanded=True):
                    st.markdown(f"*{result.full_path}*")

                # --- G. 详细层级 (带颜色和斜体) ---
                with st.expander("**All Taxonomic Levels (各级分类)**"):
                    levels = ["Realm", "Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
                    color_map = {
                        "Realm": "#003366", "Kingdom": "#004d99", "Phylum": "#336699",
                        "Class": "#008080", "Order": "#2E8B57", "Family": "#50C878",
                        "Genus": "#9ACD32", "Species": "#FF8C00"
                    }
                    for level in levels:
                        val = result.taxonomy.get(level, "-")
                        c = color_map.get(level, "#888")
                        label = f"<span style='color:{c};font-weight:bold'>{level}</span>"
                        if val == "-":
                            st.markdown(f"{label}: -", unsafe_allow_html=True)
                        else:
                            st.markdown(f"{label}: <i>{val}</i>", unsafe_allow_html=True)
            else:
                st.error("Unmatched (未匹配到 ICTV 物种)")
                st.info("💡 Tip: 请检查拼写，或者尝试输入 NCBI Taxonomy ID")

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
st.markdown(
    "<div style='text-align:center'>"
    f"VirusAlign v{SOFTWARE_VERSION} | {SOFTWARE_NAME_CN} | {ICTV_VERSION}"
    "</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div style='text-align:center;font-size:0.85rem'>"
    "🏗️ 开发单位：中国疾病预防控制中心传染病预防控制所 | "
    "🧧 项目资助：国家科技重大专项 (No. 2025ZD01900116)"
    "</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div style='text-align:center;font-size:0.85rem'>"
    "🌐 在线服务：https://virusalign.streamlit.app/ | "
    "📄 标准规范：ICTV MSL41 (2025)"
    "</div>",
    unsafe_allow_html=True
)
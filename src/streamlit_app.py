"""VirusAlign Web 界面 — Streamlit 实现"""
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.config import SOFTWARE_NAME_CN, SOFTWARE_NAME_EN, SOFTWARE_VERSION, ICTV_VERSION, OUTPUT_FIELD_NAMES
from src.constants import MATCH_SOURCE_LABELS, VIRUS_COVERAGE_CATEGORIES
from src.data_manager import DataManager
from src.engine import AlignmentEngine
from src.logger import configure_logger
configure_logger("VirusAlign")
# ---- 页面配置 ----
st.set_page_config(
page_title=SOFTWARE_NAME_EN,
page_icon="",
layout="centered",
)
# ---- 初始化 ----
@st.cache_resource
def init_engine():
dm = DataManager(cache_ttl_seconds=600)
# 验证完整性
ok, errs = dm.verify_integrity()
if not ok:
st.error(f"数据完整性检查失败: {errs[0]}")
return None
return AlignmentEngine(dm)
engine = init_engine()
if engine is None:
st.stop()
# ---- 会话状态 ----
if "query_result" not in st.session_state:
st.session_state.query_result = None
# ---- 侧边栏 ----
with st.sidebar:
st.markdown(f"### {SOFTWARE_NAME_CN}")
st.caption(f"版本 {SOFTWARE_VERSION} · 数据标准 {ICTV_VERSION}")
st.divider()
st.markdown("**数据概况**")
stats = engine.match_stats
dm = engine._data
st.markdown(f"- 分类树物种数: {dm.get_taxonomy_tree().get('species_count', 0)}")
st.markdown(f"- 别名映射条目: {len(dm.get_alias_map()):,}")
st.markdown(f"- NCBI tax_id 映射: {len(dm.get_ncbi_map()):,}")
st.divider()
st.markdown("**当前会话匹配统计**")
st.markdown(f"- 精确: {stats['exact']}")
st.markdown(f"- 别名: {stats['alias']}")
st.markdown(f"- NCBI ID: {stats['ncbi_id']}")
st.markdown(f"- 未匹配: {stats['unmatched']}")
st.divider()
st.markdown("**覆盖病毒类别**")
for category, viruses in VIRUS_COVERAGE_CATEGORIES:
st.markdown(f"- **{category}**: {', '.join(viruses[:4])}")
# ---- 主界面 ----
st.title(SOFTWARE_NAME_EN)
st.caption(SOFTWARE_NAME_CN + " — 输入病毒名称或 NCBI tax_id，即可获得 ICTV 标准化分类结果")
tab1, tab2 = st.tabs(["单名查询", "批量处理"])
# === Tab 1: 单名查询 ===
with tab1:
with st.container():
query = st.text_input(
"输入病毒名或 NCBI tax_id",
placeholder="例如: SARS-CoV-2, COVID-19, 3418604, 1003835, Zika virus",
label_visibility="collapsed",
)
if query:
with st.spinner("正在匹配..."):
result = engine.match_one(query)
if result.is_matched():
label = MATCH_SOURCE_LABELS.get(result.match_source, result.match_source)
st.success(f"已识别 — {label}")
col1, col2 = st.columns(2)
col1.metric("标准物种名", result.standard_name)
col2.metric("匹配方式", label)
col3, col4 = st.columns(2)
col3.metric("科 (Family)", result.taxonomy.get("Family", "-"))
col4.metric("属 (Genus)", result.taxonomy.get("Genus", "-"))
with st.expander("完整分类路径", expanded=True):
st.code(result.full_path, language="text")
with st.expander("查看完整分类层级"):
for level in ["Realm", "Kingdom", "Phylum", "Class",
"Order", "Family", "Genus", "Species"]:
val = result.taxonomy.get(level, "-")
st.text(f"{level:>12}: {val}")
else:
st.error("未匹配到 ICTV 物种")
st.info("建议: 检查名称拼写，或尝试输入 NCBI tax_id")
# === Tab 2: 批量处理 ===
with tab2:
uploaded_file = st.file_uploader(
"上传 CSV 文件",
type="csv",
help="CSV 文件需包含一列病毒名称（支持 ICTV 正式名、别名、NCBI tax_id）",
)
if uploaded_file:
try:
df = pd.read_csv(uploaded_file)
except Exception as e:
st.error(f"无法读取 CSV: {e}")
st.stop()
name_col = st.text_input(
"病毒名称列名",
value="name",
help="CSV 文件中哪一列是病毒名称",
)
if name_col not in df.columns:
cols = ", ".join(df.columns)
st.error(f"CSV 中未找到列 '{name_col}'。可用列: {cols}")
st.stop()
if st.button("开始标准化", type="primary"):
progress_bar = st.progress(0, text="处理中...")
status_text = st.empty()
def update_progress(current, total):
pct = current / total
progress_bar.progress(pct, f"处理 {current}/{total} ({pct*100:.0f}%)")
status_text.text(f"已处理 {current}/{total} 条")
total = len(df)
status_text.text(f"开始处理 {total} 条数据...")
names = df[name_col].astype(str).tolist()
results = engine.match_batch(names, callback=update_progress)
progress_bar.empty()
status_text.empty()
# 合并结果
out_rows = []
for i, (_, row) in enumerate(df.iterrows()):
merged = row.to_dict()
merged.update(results[i].to_dict())
out_rows.append(merged)
out_df = pd.DataFrame(out_rows)
# 统计
stats = engine.match_stats
matched = total - stats["unmatched"]
pct = matched * 100 // total if total else 0
st.success(f"处理完成！匹配率: {matched}/{total} ({pct}%)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("精确匹配", stats["exact"])
c2.metric("别名匹配", stats["alias"])
c3.metric("NCBI ID", stats["ncbi_id"])
c4.metric("未匹配", stats["unmatched"], delta_color="inverse")
with st.expander("结果预览", expanded=True):
preview_cols = [name_col, "ictv_standard_name",
"ictv_match_source", "ictv_family"]
preview_cols = [c for c in preview_cols if c in out_df.columns]
st.dataframe(
out_df[preview_cols].head(30),
use_container_width=True,
hide_index=True,
)
csv_data = out_df.to_csv(index=False).encode("utf-8")
st.download_button(
label="下载标准化结果 CSV",
data=csv_data,
file_name="virusalign_result.csv",
mime="text/csv",
type="primary",
)
st.divider()
st.caption(
f"{SOFTWARE_NAME_EN} v{SOFTWARE_VERSION} · "
f"ICTV MSL41 · "
f"在线文档: https://virusalign.streamlit.app/"
)

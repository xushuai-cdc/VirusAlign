# VirusAlign User Manual / 用户手册

## Overview / 概述

VirusAlign maps virus names from heterogeneous sources (NCBI, GISAID, EBI) to standardized ICTV taxonomic classifications. 

将来自 NCBI、GISAID 等多源数据库的病毒名称标准化为 ICTV 官方物种名和完整分类路径。

Full name: 基于ICTV标准的病原体物种语义映射与分类标准化系统V1.0

## Quick Start / 快速开始

`ash
pip install -r requirements.txt
streamlit run streamlit_app.py
`
Open / 打开: http://localhost:8501

## Online Demo / 在线演示
https://virusalign.streamlit.app/

## Interface / 界面说明

The web interface uses bilingual labels (English with Chinese annotations). / 界面采用双语标签（英文标注 + 中文说明）。

- **Quick Lookup (单名查询)**: Enter a single virus name or NCBI tax_id
- **Batch Process (批量处理)**: Upload CSV/Excel for large-scale processing
- **Sidebar (侧边栏)**: Shows data stats, session match statistics, and pathogen coverage

## Deployment Modes / 部署模式

### 1. Streamlit Cloud (Online / 在线)
Zero installation: https://virusalign.streamlit.app/

### 2. Local Streamlit (Interactive / 交互式科研模式)
`ash
streamlit run streamlit_app.py
`

### 3. Flask API (Industrial / 工业级集成模式)
`ash
python src/webapp.py
`
API endpoint: http://localhost:5188

### 4. CLI (Command-line / 命令行批处理)
`ash
python src/cli_handler.py -i input.csv -o output.csv
`

## Input Format / 输入格式

| Format / 格式 | Example / 示例 | Match Method / 匹配方式 |
|---|---|---|
| ICTV formal name | Betacoronavirus pandemicum | Hash exact match |
| Alias / common name | SARS-CoV-2, COVID-19, Zika virus | Semantic alias mapping |
| NCBI tax_id | 3418604, 1003835 | Local + live API fallback |

Batch input: CSV or Excel file with a column containing virus names. / 批量输入支持 CSV 和 Excel 格式。

## Output Fields / 输出字段

| Field / 字段 | Description / 说明 | Example / 示例 |
|---|---|---|
| ictv_standard_name | Standardized ICTV species name | Betacoronavirus pandemicum |
| ictv_match_source | Match method: exact/alias/ncbi_id/unmatched | alias |
| ictv_full_path | Full taxonomic path | Riboviria / Coronaviridae / ... |
| ictv_family | Family / 科 | Coronaviridae |
| ictv_genus | Genus / 属 | Betacoronavirus |
| ictv_species | Species / 种 | Betacoronavirus pandemicum |

## Matching Engine / 匹配引擎

Four-stage heuristic mapping / 四级启发式映射:
1. **Hash exact match / 哈希精确匹配**: O(1) lookup in 17,554 species index
2. **Semantic alias conversion / 语义别名转换**: 52,844-entry alias dictionary
3. **Cross-db ID sync / 跨库 ID 同步**: 15,875 NCBI tax_id mappings + live API fallback
4. **Recursive hierarchy reconstruction / 递归层级补全**: Auto-fills Realm~Species path

## Data Coverage / 数据覆盖

- ICTV Master Species List 2025 (MSL41): 17,554 species / 物种
- Alias mappings / 别名映射: 52,844 entries / 条
- NCBI tax_id mappings / tax_id 映射: 15,875 entries / 条 (90% ICTV coverage)
- 20 viral families / 病毒科, 50+ important human pathogens / 重要人类病原体

## Citation / 引用

本课题系新发突发与重大传染病防控国家科技重大专项《X传染病全景病原图谱和序列数据库构建》的技术产出。
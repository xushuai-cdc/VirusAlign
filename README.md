# VirusAlign-Taxon

基于 ICTV 标准的病原体物种语义映射与分类标准化系统 V1.0

---

## 概述

VirusAlign-Taxa 是专为解决全球病原体大数据整合中命名冲突与语义断层而设计的治理工具。本系统深度集成 ICTV (国际病毒分类委员会)最新的 MSL41 标准，构建了从异构原始名称到标准化分类体系的自动化映射链路。

### 核心功能

- **实时语义对齐**：输入病毒名称、常用缩写或 NCBI Taxonomy ID，经五阶段级联算法毫秒级输出 ICTV 标准物种名及完整八级分类路径
- **高通量批处理**：支持万级 CSV/XLSX 数据全量接入，自动完成字段提取与标准化填充
- **分类学双向溯源**：不仅支持乱名→标准名的正向对齐，更支持标准名→历史曾用名/缩写/临床别名的反向扩展
- **RESTful API**：提供 Flask HTTP 接口，支持第三方系统集成

### 数据规模

| 指标            | 数据   |
| :-------------- | ------ |
| ICTV 标准物种   | 17,554 |
| 语义别名        | 80,705 |
| 跨库 ID 映射    | 15,941 |
| NCBI 对齐覆盖率 | 90.8%  |

### 快速开始

```bash
git clone https://github.com/your-repo/VirusAlign.git
cd VirusAlign
pip install -r requirements.txt
streamlit run streamlit_app.py
```

浏览器访问 http://localhost:8501

### 在线体验

https://virusalign.streamlit.app/

### 命令行批处理

```
python -m core.cli_handler -i input.csv -o output.csv -c name
```

### 项目依赖

Python ≥ 3.9 · streamlit · pandas · openpyxl · requests


---


## Overview

VirusAlign-Taxon is a virus name alignment and standardization system based on the ICTV Master Species List (MSL41). It maps pathogen names from heterogeneous sources (NCBI, GISAID, EBI) to standardized ICTV taxonomic classifications.

### Key Features

- **Real-time Alignment**: Enter virus names, abbreviations, or NCBI Taxonomy IDs for instant ICTV-standardized species names with full 8-level taxonomic paths
- **Batch Processing**: Upload CSV/XLSX files for large-scale automated standardization with quality dashboards
- **Bidirectional Lookup**: Forward alignment (raw name → standard name) and reverse expansion (standard name → historical aliases, abbreviations, and common names)
- **RESTful API**: Flask HTTP interface for third-party system integration

### Data Coverage

| Metric               | Value  |
| -------------------- | ------ |
| ICTV Species (MSL41) | 17,554 |
| Semantic Aliases     | 80,705 |
| Cross-DB ID Mappings | 15,941 |
| NCBI Alignment Rate  | 90.8%  |

### Quick Start

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open http://localhost:8501

### Online Demo

https://virusalign.streamlit.app/

### CLI Batch Processing

```
python -m core.cli_handler -i input.csv -o output.csv -c name
```

### Requirements

Python ≥ 3.9 · streamlit · pandas · openpyxl · requests

### Algorithm Pipeline

Five-stage cascade: Exact Hash Match → Alias Mapping → Fuzzy Edit Distance → Local NCBI ID Lookup → NCBI API Fallback

### License

MIT

### Acknowledgement

国家科技重大专项 (No. 2025ZD01900116)

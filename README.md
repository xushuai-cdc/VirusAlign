# VirusAlign

**ICTV-based Pathogen Species Semantic Mapping & Classification Standardization System V1.0**
**基于ICTV标准的病原体物种语义映射与分类标准化系统V1.0**

---

## English

### Overview
VirusAlign maps virus names from heterogeneous sources (NCBI, GISAID, EBI) to standardized ICTV taxonomic classifications. It supports three input modes: ICTV formal names, common aliases/abbreviations, and NCBI taxonomy IDs. The system automatically resolves legacy tax IDs via real-time NCBI API lookup.

### Quick Start
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Open http://localhost:8501

### Online Demo
https://virusalign.streamlit.app/

### Features
- **Real-time Matching**: Enter a virus name or NCBI tax_id
- **Batch Processing**: Upload CSV/Excel for large-scale standardization
- **Three-tier Engine**: Hash exact match -> Semantic alias -> Recursive hierarchy completion
- **Multi-mode Deployment**: Streamlit UI / Flask API / CLI

### Data
- ICTV MSL41: 17,554 species, 52,844 alias mappings
- NCBI tax_id: 15,875 entries (90% coverage)

---

## 中文说明

### 概述
VirusAlign 是一个基于 ICTV 病毒分类标准的病原体物种名称映射工具。它接收来自 NCBI、GISAID 等多源数据库的病毒名称或分类 ID，通过三级启发式映射引擎将其标准化为 ICTV 官方物种名和完整分类路径。

### 快速开始
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
浏览器访问 http://localhost:8501

### 在线演示
https://virusalign.streamlit.app/

### 核心功能
- **实时对齐**: 输入病毒名或 NCBI tax_id, 即时返回标准分类
- **批量处理**: 上传 CSV/Excel, 大规模标准化
- **三级映射**: 哈希精确匹配 -> 语义别名转换 -> 递归层级补全
- **旧 ID 回退**: 旧 NCBI tax_id 自动实时查询解析
- **多模式部署**: Streamlit 交互界面 / Flask API / CLI 命令行

### 数据覆盖
- ICTV MSL41: 17,554 个物种, 52,844 条别名映射
- NCBI tax_id: 15,875 条 (ICTV 覆盖率 90%)
- 20 个病毒科, 50+ 种重要人类病原体

### 课题归属
本课题系新发突发与重大传染病防控国家科技重大专项《X传染病全景病原图谱和序列数据库构建》的技术产出。
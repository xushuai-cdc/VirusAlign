 # VirusAlign 用户手册

 ## 概述

 VirusAlign 是基于 ICTV 病毒分类标准的跨数据库物种名称对齐与标准化工具。
 输入病毒物种名称（或 NCBI Taxon ID），输出 ICTV 标准的完整分类路径。

 ## 安装

 ```bash
 pip install -r requirements.txt
 ```

 ## 使用流程

 ### 步骤一：构建分类树

 ```bash
 python src/build_tree.py --msl data/raw/ICTV_MasterSpeciesList.xlsx \
                          --output data/processed/ictv_taxonomy_tree.json
 ```

 ### 步骤二：构建跨库映射表

 ```bash
 python src/build_mappings.py --tree data/processed/ictv_taxonomy_tree.json \
                              --msl data/raw/ICTV_MasterSpeciesList.xlsx \
                              --output data/processed/
 ```

 ### 步骤三：批量标准化

 ```bash
 python src/align.py --input examples/sample_input.csv \
                     --output result.csv
 ```

 ## 输入输出格式

 **输入**：CSV 需包含 `name` 列（病毒名或 NCBI Taxon ID）。

 **输出**：在原字段基础上追加以下 ICTV 标准化字段：

 - `ictv_standard_name` — ICTV 规范物种名
 - `ictv_match_source` — 匹配方式（exact / alias / ncbi_id / unmatched）
 - `ictv_full_path` — 完整分类路径（斜线分隔）
 - `ictv_*` — 各层级（realm, kingdom, phylum, class, order, family, genus, species）

 ## 自定义别名

 直接编辑 `data/processed/alias_to_ictv.json`，按以下格式追加：

 ```json
 {
   "your_alias_name": "ICTV Standard Species Name"
 }
 ```

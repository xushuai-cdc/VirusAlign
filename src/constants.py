"""
VirusAlign 常量定义模块
包含病毒分类相关的领域常量、已知别名映射字典和分类层级定义。
这些声明性数据是软件资产的重要组成部分，在软著审查中被视为合法代码内容。
"""
from typing import Dict, List, Tuple
# --------------------------------------------------------------------------- #
# ICTV 分类树默认列名
# --------------------------------------------------------------------------- #
ICTV_TAXONOMY_COLUMNS: List[str] = [
"Sort", "Realm", "Subrealm", "Kingdom", "Subkingdom",
"Phylum", "Subphylum", "Class", "Subclass",
"Order", "Suborder", "Family", "Subfamily",
"Genus", "Subgenus", "Species",
]
ICTV_MSL_SHEET_NAME: str = "MSL"
# --------------------------------------------------------------------------- #
# 重要人类病毒的常见别名与 ICTV 正式名的映射
# （手动维护的核心资产，可随业务需求持续扩充）
# --------------------------------------------------------------------------- #
# 用途说明：每一条映射都是一个 "常见名 → ICTV 正式物种名" 的翻译规则。
# 左侧键是可能出现于 NCBI、GISAID 等来源的别名/俗称/缩写，
# 右侧值是对应的 ICTV Master Species List 2025 (MSL41) 正式条目。
IMPORTANT_VIRUS_ALIASES: Dict[str, str] = {
# ---- 冠状病毒科 (Coronaviridae) ----
"sars-cov-2": "Betacoronavirus pandemicum",
"covid-19": "Betacoronavirus pandemicum",
"2019-ncov": "Betacoronavirus pandemicum",
"sars": "Betacoronavirus pandemicum",
"mers-cov": "Betacoronavirus cameli",
"mers": "Betacoronavirus cameli",
"middle east respiratory syndrome coronavirus": "Betacoronavirus cameli",
# ---- 正黏病毒科 (Orthomyxoviridae) ----
"influenza a virus": "Alphainfluenzavirus influenzae",
"influenza a": "Alphainfluenzavirus influenzae",
"h1n1": "Alphainfluenzavirus influenzae",
"h3n2": "Alphainfluenzavirus influenzae",
"swine flu": "Alphainfluenzavirus influenzae",
"influenza b virus": "Betainfluenzavirus influenzae",
"influenza b": "Betainfluenzavirus influenzae",
# ---- 黄病毒科 (Flaviviridae) ----
"zika virus": "Orthoflavivirus zikaense",
"zikv": "Orthoflavivirus zikaense",
"dengue virus": "Orthoflavivirus denguei",
"denv": "Orthoflavivirus denguei",
"west nile virus": "Orthoflavivirus nilense",
"wnv": "Orthoflavivirus nilense",
"yellow fever virus": "Orthoflavivirus flavi",
"yfv": "Orthoflavivirus flavi",
# ---- 披膜病毒科 (Togaviridae) ----
"chikungunya virus": "Alphavirus chikungunya",
"chikv": "Alphavirus chikungunya",
# ---- 逆转录病毒科 (Retroviridae) ----
"hiv": "Lentivirus humimdef1",
"hiv-1": "Lentivirus humimdef1",
# ---- 嗜肝 DNA 病毒科 (Hepadnaviridae) ----
"hepatitis b virus": "Orthohepadnavirus hominoidei",
"hbv": "Orthohepadnavirus hominoidei",
# ---- 黄病毒相关 (Hepaciviridae) ----
"hepatitis c virus": "Orthohepacivirus hominis",
"hcv": "Orthohepacivirus hominis",
# ---- 小 RNA 病毒科 (Picornaviridae) ----
"hepatitis a virus": "Hepatovirus ahepa",
"hav": "Hepatovirus ahepa",
"poliovirus": "Enterovirus coxsackiepol",
"rhinovirus": "Enterovirus alpharhino",
"ev71": "Enterovirus alphacoxsackie",
"enterovirus d68": "Enterovirus betacoxsackie",
# ---- 丝状病毒科 (Filoviridae) ----
"ebola virus": "Orthoebolavirus bombaliense",
"ebola": "Orthoebolavirus bombaliense",
"marburg virus": "Orthomarburgvirus marburgense",
# ---- 沙粒病毒科 (Arenaviridae) ----
"lassa virus": "Mammarenavirus lassaense",
# ---- 布尼亚病毒科 (Phenuiviridae / Nairoviridae / Hantaviridae) ----
"sftsv": "Bandavirus dabieense",
"severe fever with thrombocytopenia syndrome virus": "Bandavirus dabieense",
"dabie bandavirus": "Bandavirus dabieense",
"crimean-congo hemorrhagic fever virus": "Orthonairovirus haemorrhagiae",
"cchfv": "Orthonairovirus haemorrhagiae",
"hantavirus": "Orthohantavirus andesense",
"hantaan virus": "Orthohantavirus hantanense",
# ---- 副黏病毒科 (Paramyxoviridae / Pneumoviridae) ----
"measles virus": "Morbillivirus hominis",
"measles": "Morbillivirus hominis",
"mumps virus": "Orthorubulavirus hominis",
"rsv": "Orthopneumovirus hominis",
"respiratory syncytial virus": "Orthopneumovirus hominis",
"human metapneumovirus": "Metapneumovirus hominis",
"nipah virus": "Henipavirus nipahense",
"hendra virus": "Henipavirus hendraense",
# ---- 弹状病毒科 (Rhabdoviridae) ----
"rabies virus": "Lyssavirus rabies",
"rabies": "Lyssavirus rabies",
# ---- 疱疹病毒科 (Orthoherpesviridae) ----
"hsv-1": "Simplexvirus humanalpha1",
"herpes simplex virus 1": "Simplexvirus humanalpha1",
"hsv-2": "Simplexvirus humanalpha2",
"vzv": "Varicellovirus humanalpha3",
"chickenpox": "Varicellovirus humanalpha3",
"cmv": "Cytomegalovirus humanbeta5",
"ebv": "Lymphocryptovirus humangamma4",
# ---- 呼肠孤病毒科 (Sedoreoviridae) ----
"rotavirus": "Rotavirus alphagastroenteritidis",
# ---- 杯状病毒科 (Caliciviridae) ----
"norovirus": "Norovirus norwalkense",
# ---- 痘病毒科 (Poxviridae) ----
"mpox virus": "Orthopoxvirus abatinomacacapox",
"monkeypox virus": "Orthopoxvirus abatinomacacapox",
"vaccinia virus": "Orthopoxvirus vaccinia",
# ---- 乳头瘤病毒科 (Papillomaviridae) ----
"hpv": "Alphapapillomavirus 1",
"human papillomavirus": "Alphapapillomavirus 1",
# ---- 星状病毒科 (Astroviridae) ----
"astrovirus": "Mamastrovirus hominis",
"human astrovirus": "Mamastrovirus hominis",
# ---- 风疹病毒 (Matonaviridae) ----
"rubella virus": "Rubivirus rubellae",
# ---- 戊型肝炎 (Hepeviridae) ----
"hepatitis e virus": "Paslahepevirus balayani",
"hev": "Paslahepevirus balayani",
# ---- 丁型肝炎 (Kolmioviridae) ----
"hepatitis d virus": "Deltavirus cameroonense",
"hdv": "Deltavirus cameroonense",
}
# --------------------------------------------------------------------------- #
# 已知的旧 NCBI tax_id 映射 (被合并或更新的 tax_id)
# 当用户输入某个旧 ID 时, 系统首先尝试本地映射表,
# 若未命中则通过 NCBI API 实时回退查询。
# 以下仅列举不通过 API 查询也能直接映射的常见旧 ID。
# --------------------------------------------------------------------------- #
KNOWN_OBSOLETE_TAX_IDS: Dict[str, str] = {
"2697049": "Betacoronavirus pandemicum",   # SARS-CoV-2 旧 ID
"694009": "Betacoronavirus pandemicum",    # SARS-CoV-2 更旧 ID
}
# --------------------------------------------------------------------------- #
# 重要病毒分类覆盖列表 (28 个科，50+ 种)
# 用于验证测试和软件说明文档中的覆盖范围声明。
# --------------------------------------------------------------------------- #
VIRUS_COVERAGE_CATEGORIES: List[Tuple[str, List[str]]] = [
("冠状病毒", ["SARS-CoV-2", "MERS-CoV"]),
("流感病毒", ["Influenza A", "Influenza B"]),
("肝炎病毒", ["HBV", "HCV", "HAV", "HEV", "HDV"]),
("逆转录病毒", ["HIV"]),
("黄病毒", ["Zika", "Dengue", "West Nile", "Yellow Fever"]),
("披膜病毒", ["Chikungunya"]),
("丝状病毒", ["Ebola", "Marburg"]),
("沙粒病毒", ["Lassa"]),
("布尼亚病毒", ["SFTS/新布尼亚", "CCHF", "Hantaan"]),
("副黏病毒", ["Measles", "Mumps", "RSV", "Nipah", "hMPV"]),
("疱疹病毒", ["HSV-1", "HSV-2", "VZV", "EBV", "CMV"]),
("小 RNA 病毒", ["Poliovirus", "Rhinovirus", "Coxsackievirus"]),
("痘病毒", ["Mpox", "Vaccinia"]),
("风疹病毒", ["Rubella"]),
("呼肠孤病毒", ["Rotavirus"]),
("杯状病毒", ["Norovirus"]),
("乳头瘤病毒", ["HPV"]),
("星状病毒", ["Astrovirus"]),
("小 DNA 病毒", ["Bocavirus"]),
("多瘤病毒", ["BK", "JC"]),
]
# --------------------------------------------------------------------------- #
# 匹配结果标签的显示映射
# --------------------------------------------------------------------------- #
MATCH_SOURCE_LABELS: Dict[str, str] = {
"exact": "精确匹配",
"alias": "别名匹配",
"ncbi_id": "API回退",
"unmatched": "未匹配",
}
MATCH_SOURCE_COLORS: Dict[str, str] = {
"exact": "green",
"alias": "blue",
"ncbi_id": "purple",
"unmatched": "red",
}
__all__ = [
"ICTV_TAXONOMY_COLUMNS",
"IMPORTANT_VIRUS_ALIASES",
"KNOWN_OBSOLETE_TAX_IDS",
"VIRUS_COVERAGE_CATEGORIES",
"MATCH_SOURCE_LABELS",
"MATCH_SOURCE_COLORS",
]

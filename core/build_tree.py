"""分类树构建工具 — 解析 ICTV MSL Excel 输出 JSON 分类树"""

import json
import argparse
from pathlib import Path

import pandas as pd

TAXONOMY_COLS = [
    "Realm", "Subrealm", "Kingdom", "Subkingdom",
    "Phylum", "Subphylum", "Class", "Subclass",
    "Order", "Suborder", "Family", "Subfamily",
    "Genus", "Subgenus", "Species",
]

SHEET_NAME = "MSL"


def parse_msl(filepath: str) -> pd.DataFrame:
    """读取 ICTV MSL Excel 文件，返回分类信息 DataFrame。"""
    df = pd.read_excel(filepath, sheet_name=SHEET_NAME)
    available = [c for c in TAXONOMY_COLS if c in df.columns]
    if not available:
        raise ValueError(f"未找到分类列，可用列: {list(df.columns)}")
    return df[available].dropna(subset=["Species"])


def build_tree(df: pd.DataFrame) -> dict:
    """构建分类树字典。"""
    species_list = []
    for _, row in df.iterrows():
        entry = {}
        path_parts = []
        for col in TAXONOMY_COLS:
            val = str(row.get(col, "")).strip()
            if val and val != "nan":
                entry[col] = val
                path_parts.append(val)
            else:
                entry[col] = ""
        entry["full_path"] = " / ".join(filter(None, path_parts))
        species_list.append(entry)
    return {"species_count": len(species_list), "species": species_list}


def main() -> None:
    parser = argparse.ArgumentParser(description="ICTV MSL 分类树构建工具")
    parser.add_argument("--msl", required=True, help="ICTV Master Species List Excel")
    parser.add_argument("--output", required=True, help="输出 JSON 路径")
    args = parser.parse_args()

    print(f"[VirusAlign] 读取 ICTV MSL: {args.msl}")
    df = parse_msl(args.msl)
    print(f"[VirusAlign] 提取到 {len(df)} 条物种记录")

    tree = build_tree(df)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)

    print(f"[VirusAlign] 分类树已写入: {args.output}")
    print(f"[VirusAlign] 共 {tree['species_count']} 个病毒物种")


if __name__ == "__main__":
    main()

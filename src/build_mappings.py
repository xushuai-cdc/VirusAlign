"""映射表构建工具 — 生成别名映射表和 NCBI tax_id 映射"""

import json
import argparse
from pathlib import Path

import pandas as pd

SHEET_NAME = "MSL"


def load_tree(tree_path: str) -> dict:
    with open(tree_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_ncbi_mappings(msl_path: str, tree_species: list) -> dict:
    df = pd.read_excel(msl_path, sheet_name=SHEET_NAME)
    ncbi_map = {}
    if "NCBI Taxon ID" not in df.columns:
        print("[WARN] MSL 中未找到 NCBI Taxon ID 列")
        return ncbi_map
    for _, row in df.iterrows():
        species_name = str(row.get("Species", "")).strip()
        ncbi_id = str(row.get("NCBI Taxon ID", "")).strip()
        if species_name and ncbi_id and ncbi_id != "nan":
            ncbi_map[ncbi_id.split(".")[0]] = species_name
    return ncbi_map


def build_alias_map(tree_species: list) -> dict:
    alias_map = {}
    for entry in tree_species:
        species = entry.get("Species", "")
        if not species:
            continue
        low = species.lower()
        alias_map[low] = species
        alias_map[low.replace(" ", "_")] = species
        alias_map[low.replace(" ", "-")] = species
    return alias_map


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tree", required=True)
    parser.add_argument("--msl", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    tree = load_tree(args.tree)
    species = tree.get("species", [])

    ncbi_map = extract_ncbi_mappings(args.msl, species)
    alias_map = build_alias_map(species)

    with open(out_dir / "ncbi_to_ictv.json", "w", encoding="utf-8") as f:
        json.dump(ncbi_map, f, ensure_ascii=False, indent=2)

    with open(out_dir / "alias_to_ictv.json", "w", encoding="utf-8") as f:
        json.dump(alias_map, f, ensure_ascii=False, indent=2)

    print(f"[VirusAlign] NCBI 映射表: {len(ncbi_map)} 条")
    print(f"[VirusAlign] 别名映射表: {len(alias_map)} 条")


if __name__ == "__main__":
    main()

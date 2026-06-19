"""VirusAlign 单元测试"""
import json
import tempfile
from pathlib import Path
import pandas as pd
from src.align import resolve_name, build_species_index, fill_path
def make_test_mappings():
alias_map = {
"sars-cov-2": "Severe acute respiratory syndrome coronavirus 2",
"zika virus": "Zika virus",
"influenza a virus": "Influenza A virus",
}
ncbi_map = {"2697049": "Severe acute respiratory syndrome coronavirus 2",
"11320": "Influenza A virus"}
return alias_map, ncbi_map
def make_species_index():
return {
"Severe acute respiratory syndrome coronavirus 2": {
"Species": "Severe acute respiratory syndrome coronavirus 2",
"Genus": "Betacoronavirus",
"Family": "Coronaviridae",
"Order": "Nidovirales",
"full_path": "Riboviria / Nidovirales / Coronaviridae / Betacoronavirus / Severe acute respiratory syndrome coronavirus 2"
},
"Influenza A virus": {
"Species": "Influenza A virus",
"Genus": "Alphainfluenzavirus",
"Family": "Orthomyxoviridae",
"full_path": "Riboviria / Articulavirales / Orthomyxoviridae / Alphainfluenzavirus / Influenza A virus"
},
}
def test_exact_match():
alias_map, ncbi_map = make_test_mappings()
name, source = resolve_name("Zika virus", alias_map, ncbi_map)
assert name == "Zika virus"
assert source == "exact"
def test_alias_match():
alias_map, ncbi_map = make_test_mappings()
name, source = resolve_name("sars-cov-2", alias_map, ncbi_map)
assert name == "Severe acute respiratory syndrome coronavirus 2"
assert source == "alias"
def test_ncbi_id_match():
alias_map, ncbi_map = make_test_mappings()
name, source = resolve_name("2697049", alias_map, ncbi_map)
assert name == "Severe acute respiratory syndrome coronavirus 2"
assert source == "ncbi_id"
def test_unmatched():
alias_map, ncbi_map = make_test_mappings()
name, source = resolve_name("Unknown virus", alias_map, ncbi_map)
assert source is None
def test_fill_path():
index = make_species_index()
entry = fill_path("Influenza A virus", index)
assert entry["Family"] == "Orthomyxoviridae"
def test_pipeline_integration(tmp_path):
"""端到端测试"""
alias_map, ncbi_map = make_test_mappings()
species_index = make_species_index()
df_in = pd.DataFrame({"name": ["SARS-CoV-2", "Influenza A virus", "11292"]})
results = []
for _, row in df_in.iterrows():
raw_name = row["name"]
std_name, source = resolve_name(raw_name, alias_map, ncbi_map)
path_entry = fill_path(std_name, species_index) if source else {}
results.append({
"name": raw_name,
"ictv_standard_name": std_name if source else "",
"ictv_match_source": source or "unmatched",
"ictv_family": path_entry.get("Family", ""),
})
df_out = pd.DataFrame(results)
assert len(df_out) == 3
assert df_out.iloc[0]["ictv_standard_name"] == "Severe acute respiratory syndrome coronavirus 2"
assert df_out.iloc[1]["ictv_match_source"] == "exact"
assert df_out.iloc[2]["ictv_family"] == "Coronaviridae"

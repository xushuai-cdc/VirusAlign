"""VirusAlign 工具函数模块"""

import csv
import io
import re
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def normalize_virus_name(name: str) -> str:
    """将病毒名称统一规范化为小写加空格分隔的格式。"""
    return name.lower().strip().replace("_", " ").replace("-", " ")


def normalize_taxonomy_key(name: str) -> str:
    """生成分类名称的归一化键值。"""
    return re.sub(r"\s+", " ", normalize_virus_name(name))


def is_valid_taxonomy_name(name: str) -> bool:
    """检查字符串是否为合法的分类名称。"""
    if not name or len(name) < 2:
        return False
    if re.search(r"[\x00-\x1f\x7f]", name):
        return False
    return True


def validate_csv_content(
    content: str,
    expected_column: Optional[str] = None,
    max_rows: int = 100000,
) -> Tuple[bool, str, List[str]]:
    """校验 CSV 内容的合法性。"""
    if not content.strip():
        return False, "CSV 内容为空", []

    lines = content.strip().split("\n")
    if len(lines) < 2:
        return False, "CSV 仅有表头无数据行", []

    if len(lines) - 1 > max_rows:
        return False, f"数据行数超限", []

    reader = csv.reader(io.StringIO(content))
    headers = [h.strip() for h in next(reader)]
    if not headers:
        return False, "CSV 表头为空", []

    if expected_column and expected_column not in headers:
        return False, f"缺少必要列: {expected_column}", headers

    row_num = 1
    for row in reader:
        row_num += 1
        if len(row) != len(headers):
            return False, f"第 {row_num} 行列数不匹配", headers

    return True, "", headers


def ncbi_efetch_taxonomy(
    tax_id_or_name: str,
    max_retries: int = 2,
) -> List[str]:
    """调用 NCBI efetch 接口查询分类信息。"""
    encoded = urllib.request.quote(tax_id_or_name, safe="")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=taxonomy&id={encoded}&retmode=xml"

    for attempt in range(1, max_retries + 2):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "VirusAlign/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                xml_text = resp.read().decode("utf-8")
            names = re.findall(r"<ScientificName>(.*?)</ScientificName>", xml_text)
            if names:
                return names
            return []
        except urllib.error.HTTPError as e:
            if e.code == 400:
                return []
            if attempt > max_retries:
                return []
        except Exception:
            if attempt > max_retries:
                return []
            time.sleep(attempt * 2)
    return []


def detect_file_encoding(filepath: str) -> str:
    """尝试检测文件的字符编码。"""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {filepath}")
    raw = path.read_bytes()
    if raw[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig"
    for enc in ["utf-8", "gbk", "gb2312"]:
        try:
            raw.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return "utf-8"

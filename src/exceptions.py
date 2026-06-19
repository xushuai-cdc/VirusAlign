"""VirusAlign 自定义异常模块"""

class VirusAlignError(Exception):
    def __init__(self, message="", code=1000):
        self.code = code
        super().__init__(f"[V{code}] {message}")

class TaxonomyTreeError(VirusAlignError):
    def __init__(self, message="分类树加载失败"):
        super().__init__(message, code=2001)

class MappingDataError(VirusAlignError):
    def __init__(self, message="映射表数据异常"):
        super().__init__(message, code=2002)

class ICTVFileFormatError(VirusAlignError):
    def __init__(self, detail=""):
        msg = f"ICTV MSL 文件格式异常: {detail}" if detail else "ICTV MSL 文件格式异常"
        super().__init__(msg, code=2101)

class TaxonomyNotFoundError(VirusAlignError):
    def __init__(self, name=""):
        msg = f"未在 ICTV 分类树中找到匹配: {name}" if name else "未找到匹配的分类信息"
        super().__init__(msg, code=2201)

class CSVValidationError(VirusAlignError):
    def __init__(self, detail=""):
        msg = f"CSV 文件校验失败: {detail}" if detail else "CSV 文件校验失败"
        super().__init__(msg, code=3001)

class FileEncodingError(VirusAlignError):
    def __init__(self, filepath="", encoding=""):
        super().__init__(f"无法以编码 {encoding} 读取文件: {filepath}", code=3002)

class NCBIAPIError(VirusAlignError):
    def __init__(self, detail=""):
        msg = f"NCBI API 请求失败: {detail}" if detail else "NCBI API 请求失败"
        super().__init__(msg, code=4001)

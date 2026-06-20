# -*- coding: utf-8 -*-
"""VirusAlign custom exception classes."""

class VirusAlignError(Exception):
    def __init__(self, message="", code=1000):
        self.code = code
        super().__init__(f"[V{code}] {message}")

class TaxonomyTreeError(VirusAlignError):
    def __init__(self, message="Taxonomy tree error"):
        super().__init__(message, code=2001)

class MappingDataError(VirusAlignError):
    def __init__(self, message="Mapping data error"):
        super().__init__(message, code=2002)

class ICTVFileFormatError(VirusAlignError):
    def __init__(self, detail=""):
        msg = f"ICTV format: {detail}" if detail else "ICTV format error"
        super().__init__(msg, code=2101)

class TaxonomyNotFoundError(VirusAlignError):
    def __init__(self, name=""):
        msg = f"Not found: {name}" if name else "Taxonomy not found"
        super().__init__(msg, code=2201)

class CSVValidationError(VirusAlignError):
    def __init__(self, detail=""):
        msg = f"CSV error: {detail}" if detail else "CSV validation error"
        super().__init__(msg, code=3001)

class FileEncodingError(VirusAlignError):
    def __init__(self, filepath="", encoding=""):
        super().__init__(f"Cannot decode {filepath} with {encoding}", code=3002)

class NCBIAPIError(VirusAlignError):
    def __init__(self, detail=""):
        msg = f"NCBI API: {detail}" if detail else "NCBI API error"
        super().__init__(msg, code=4001)

class DataIntegrityError(VirusAlignError):
    def __init__(self, detail=""):
        msg = f"Integrity: {detail}" if detail else "Data integrity error"
        super().__init__(msg, code=5001)

class NetworkTimeoutError(VirusAlignError):
    def __init__(self, host=""):
        msg = f"Timeout: {host}" if host else "Network timeout"
        super().__init__(msg, code=4003)

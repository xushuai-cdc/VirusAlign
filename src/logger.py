"""VirusAlign 日志配置模块"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOGGER_CACHE = {}


def get_logger(name: str = "VirusAlign") -> logging.Logger:
    """获取已配置的日志器。"""
    if name in _LOGGER_CACHE:
        return _LOGGER_CACHE[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[VirusAlign] %(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    ch = logging.StreamHandler(sys.stderr)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    fh = RotatingFileHandler(
        str(_LOG_DIR / "virusalign.log"),
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    _LOGGER_CACHE[name] = logger
    return logger

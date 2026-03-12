# -*- coding: utf-8 -*-
"""
配置文件
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据目录
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"

# 创建必要的目录
for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API 配置
YAHOO Finance API = "yfinance"

# 数据源配置
DATA_SOURCES = {
    "primary": "yfinance",
    "fallback": ["sinajs", "eastmoney"]
}

# 技术指标配置
INDICATORS = {
    "ma_periods": [5, 10, 20, 50, 200],
    "rsi_period": 14,
    "mac_params": (12, 26, 9),
    "bollinger_period": 20,
    "bollinger_std": 2
}

# 机器学习配置
ML_CONFIG = {
    "train_test_split": 0.8,
    "random_state": 42,
    "epochs": 100,
    "batch_size": 32
}

# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Web UI 配置
WEB_CONFIG = {
    "title": "📊 股票分析系统",
    "layout": "wide",
    "theme": "light"
}

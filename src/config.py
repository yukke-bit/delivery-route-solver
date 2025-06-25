
# src/config.py

"""
プロジェクト全体で使用する設定値や定数を定義するモジュール。
"""

from pathlib import Path

# --- ディレクトリ設定 ---
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
DEFAULT_INSTANCE_PATH = BASE_DIR / "data/large_instances/X-n101-k25.vrp"

# --- 可視化設定 ---
VISUALIZER_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
    '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
    '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA'
]
FIGURE_SIZE = (12, 8)
DPI = 300

# --- アルゴリズム設定 ---
# 列生成法
COLUMN_GENERATION_MAX_ITERATIONS_LARGE = 20
COLUMN_GENERATION_MAX_ITERATIONS_NORMAL = 50

# --- ログ設定 ---
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

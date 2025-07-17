
# src/config.py

"""
プロジェクト全体で使用する設定値や定数を定義するモジュール。
YAMLファイルから設定を読み込む機能を提供。
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import os

class Config:
    """設定管理クラス"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.base_dir = Path(__file__).resolve().parent.parent
        
        # デフォルト設定
        self.default_config = {
            'general': {
                'default_instance': 'data/instances/A-n32-k5.vrp',
                'enable_visualization': True,
                'output_directory': 'results',
                'verbose': True
            },
            'algorithms': {
                'greedy': {'enabled': True},
                'column_generation': {
                    'enabled': True,
                    'max_iterations': 50,
                    'max_iterations_large': 20,
                    'large_instance_threshold': 100,
                    'time_limit': 300,
                    'tolerance': 1e-6
                }
            },
            'performance': {
                'max_initial_routes': 100,
                'route_generation_method': 'nearest_neighbor',
                'parallel_processing': False
            },
            'output': {
                'show_route_details': True,
                'show_comparison': True,
                'show_optimal_gap': True,
                'decimal_places': 2
            },
            'visualization': {
                'figure_size': [12, 8],
                'dpi': 300,
                'save_format': 'png',
                'show_depot': True,
                'show_customer_labels': True,
                'route_colors': ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
            }
        }
        
        # 設定ファイルから読み込み
        if config_path is None:
            config_path = self.base_dir / "config.yaml"
        
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f)
                    # デフォルト設定とマージ
                    return self._merge_config(self.default_config, yaml_config)
            else:
                print(f"設定ファイルが見つかりません: {config_path}")
                print("デフォルト設定を使用します")
                return self.default_config
        except Exception as e:
            print(f"設定ファイルの読み込みに失敗しました: {e}")
            print("デフォルト設定を使用します")
            return self.default_config
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """設定を再帰的にマージする"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def get(self, section: str, key: str = None, default=None):
        """設定値を取得"""
        try:
            if key is None:
                return self.config.get(section, default)
            return self.config.get(section, {}).get(key, default)
        except:
            return default
    
    @property
    def base_dir(self) -> Path:
        """ベースディレクトリ"""
        return self._base_dir
    
    @base_dir.setter
    def base_dir(self, value: Path):
        self._base_dir = value
    
    @property
    def results_dir(self) -> Path:
        """結果出力ディレクトリ"""
        return self.base_dir / self.get('general', 'output_directory', 'results')
    
    @property
    def default_instance_path(self) -> Path:
        """デフォルトインスタンスファイルのパス"""
        return self.base_dir / self.get('general', 'default_instance')

# グローバル設定インスタンス
config = Config()

# 後方互換性のための定数
BASE_DIR = config.base_dir
RESULTS_DIR = config.results_dir
DEFAULT_INSTANCE_PATH = config.default_instance_path
VISUALIZER_COLORS = config.get('visualization', 'route_colors', [])
FIGURE_SIZE = tuple(config.get('visualization', 'figure_size', [12, 8]))
DPI = config.get('visualization', 'dpi', 300)
COLUMN_GENERATION_MAX_ITERATIONS_LARGE = config.get('algorithms', 'column_generation').get('max_iterations_large', 20)
COLUMN_GENERATION_MAX_ITERATIONS_NORMAL = config.get('algorithms', 'column_generation').get('max_iterations', 50)
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

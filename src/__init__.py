"""
配送経路問題（VRP）ソルバーパッケージ

このパッケージは配送経路問題を解くためのツールを提供します:
- VRPファイル解析（TSPLIB95形式）
- 貪欲アルゴリズムソルバー
- 列生成フレームワーク
- 可視化ツール

メインモジュール:
- vrp_parser: TSPLIB95 VRPファイルの解析
- simple_vrp_solver: 貪欲アルゴリズムの実装
- column_generation: 列生成フレームワーク
- visualizer: ルートと問題の可視化
"""

__version__ = "1.0.0"
__author__ = "VRPソルバーチーム"

# メインクラスを簡単にアクセスできるようにインポート
from .vrp_parser import VRPInstance, Customer, parse_vrp_file
from .simple_vrp_solver import SimpleVRPSolver
from .visualizer import VRPVisualizer

__all__ = [
    'VRPInstance',
    'Customer', 
    'parse_vrp_file',
    'SimpleVRPSolver',
    'VRPVisualizer'
]
#!/usr/bin/env python3
"""
コマンドライン引数処理モジュール
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any
from .config import config

def create_parser() -> argparse.ArgumentParser:
    """コマンドライン引数パーサーを作成"""
    parser = argparse.ArgumentParser(
        description="配送経路問題（VRP）ソルバー",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py                                    # デフォルト設定で実行
  python main.py data/instances/A-n32-k5.vrp       # 特定のファイルを指定
  python main.py --no-visualization                # 可視化を無効化
  python main.py --algorithm greedy                # 貪欲法のみ実行
  python main.py --config my_config.yaml           # カスタム設定ファイル
  python main.py --max-iterations 100              # 列生成法の最大反復回数
        """
    )
    
    # 必須引数
    parser.add_argument(
        'instance_file',
        nargs='?',
        help='VRPインスタンスファイルのパス'
    )
    
    # 設定ファイル
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='設定ファイルのパス (デフォルト: config.yaml)'
    )
    
    # アルゴリズム選択
    parser.add_argument(
        '--algorithm', '-a',
        choices=['greedy', 'column_generation', 'both'],
        default='both',
        help='使用するアルゴリズム (デフォルト: both)'
    )
    
    # 可視化設定
    parser.add_argument(
        '--no-visualization',
        action='store_true',
        help='可視化を無効化'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        help='結果出力ディレクトリ'
    )
    
    # アルゴリズム固有の設定
    parser.add_argument(
        '--max-iterations',
        type=int,
        help='列生成法の最大反復回数'
    )
    
    parser.add_argument(
        '--time-limit',
        type=float,
        help='列生成法の制限時間（秒）'
    )
    
    # 出力設定
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細な出力を表示'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='最小限の出力のみ表示'
    )
    
    parser.add_argument(
        '--no-route-details',
        action='store_true',
        help='ルート詳細を表示しない'
    )
    
    # パフォーマンス設定
    parser.add_argument(
        '--max-initial-routes',
        type=int,
        help='初期ルートの最大数'
    )
    
    return parser

def parse_args(args=None) -> Dict[str, Any]:
    """コマンドライン引数を解析し、設定を統合"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # 設定ファイルを読み込み（コマンドライン引数で指定されている場合）
    if parsed_args.config:
        from .config import Config
        config_instance = Config(parsed_args.config)
    else:
        config_instance = config
    
    # コマンドライン引数で設定を上書き
    runtime_config = {
        'instance_file': parsed_args.instance_file or str(config_instance.default_instance_path),
        'algorithm': parsed_args.algorithm,
        'enable_visualization': not parsed_args.no_visualization,
        'output_directory': parsed_args.output_dir or config_instance.get('general', 'output_directory'),
        'verbose': parsed_args.verbose or (config_instance.get('general', 'verbose') and not parsed_args.quiet),
        'quiet': parsed_args.quiet,
        'show_route_details': not parsed_args.no_route_details and config_instance.get('output', 'show_route_details'),
        'config_instance': config_instance
    }
    
    # アルゴリズム固有の設定
    cg_config = config_instance.get('algorithms', 'column_generation')
    if parsed_args.max_iterations:
        cg_config['max_iterations'] = parsed_args.max_iterations
    if parsed_args.time_limit:
        cg_config['time_limit'] = parsed_args.time_limit
    if parsed_args.max_initial_routes:
        perf_config = config_instance.get('performance')
        perf_config['max_initial_routes'] = parsed_args.max_initial_routes
    
    return runtime_config

def validate_args(runtime_config: Dict[str, Any]) -> bool:
    """引数の妥当性を検証"""
    instance_file = Path(runtime_config['instance_file'])
    
    if not instance_file.exists():
        print(f"エラー: インスタンスファイルが見つかりません: {instance_file}")
        return False
    
    if not instance_file.suffix.lower() == '.vrp':
        print(f"警告: ファイル拡張子が .vrp ではありません: {instance_file}")
    
    return True

def print_config_summary(runtime_config: Dict[str, Any]):
    """設定内容の要約を表示"""
    if not runtime_config['verbose']:
        return
    
    print("=== 設定内容 ===")
    print(f"インスタンスファイル: {runtime_config['instance_file']}")
    print(f"アルゴリズム: {runtime_config['algorithm']}")
    print(f"可視化: {'有効' if runtime_config['enable_visualization'] else '無効'}")
    print(f"出力ディレクトリ: {runtime_config['output_directory']}")
    
    config_instance = runtime_config['config_instance']
    cg_config = config_instance.get('algorithms', 'column_generation')
    print(f"列生成法最大反復回数: {cg_config.get('max_iterations')}")
    print(f"列生成法制限時間: {cg_config.get('time_limit')}秒")
    print()
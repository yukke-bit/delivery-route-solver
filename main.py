#!/usr/bin/env python3
"""
配送経路問題（VRP）ソルバー
貪欲アルゴリズムと列生成法を使用してVRPを解く
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

from src.vrp_parser import parse_vrp_file
from src.simple_vrp_solver import SimpleVRPSolver
from src.visualizer import VRPVisualizer
from src.column_generation import ColumnGeneration
from src.cli import parse_args, validate_args, print_config_summary
from src.optimal_solutions import get_optimal_cost, get_optimal_vehicles, calculate_gap

def solve_vrp_problem(runtime_config: dict) -> Optional[tuple]:
    """
    VRP問題を解く
    
    Args:
        runtime_config: 実行時設定辞書
    
    Returns:
        成功時は(routes, total_cost)のタプル、失敗時はNone
    """
    file_path = runtime_config['instance_file']
    config_instance = runtime_config['config_instance']
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return None
    
    try:
        # VRPインスタンスを読み込み
        if runtime_config['verbose']:
            print(f"VRPファイルを読み込み中: {file_path}")
        instance = parse_vrp_file(file_path)
        
        # 問題情報を表示
        print_problem_info(instance, runtime_config)
        
        # 実行するアルゴリズムを決定
        algorithms = []
        if runtime_config['algorithm'] in ['greedy', 'both']:
            algorithms.append('greedy')
        if runtime_config['algorithm'] in ['column_generation', 'both']:
            algorithms.append('column_generation')
        
        results = {}
        
        # 1. 貪欲アルゴリズムで解く
        if 'greedy' in algorithms:
            if not runtime_config['quiet']:
                print("=== 貪欲アルゴリズム ===")
            start_time = time.time()
            
            greedy_solver = SimpleVRPSolver(instance)
            greedy_routes, greedy_cost = greedy_solver.solve()
            
            greedy_time = time.time() - start_time
            
            results['greedy'] = {
                'routes': greedy_routes,
                'cost': greedy_cost,
                'time': greedy_time,
                'solver': greedy_solver
            }
            
            print_solution_results(greedy_routes, greedy_cost, greedy_time, "貪欲法", runtime_config)
        
        # 2. 列生成法で解く
        if 'column_generation' in algorithms:
            if not runtime_config['quiet']:
                print("\n=== 列生成法 ===")
            start_time = time.time()
            
            try:
                cg_solver = ColumnGeneration(instance)
                cg_config = config_instance.get('algorithms', 'column_generation')
                
                # 大規模問題用の設定調整
                threshold = cg_config.get('large_instance_threshold', 100)
                if len(instance.customers) > threshold:
                    max_iter = cg_config.get('max_iterations_large', 20)
                else:
                    max_iter = cg_config.get('max_iterations', 50)
                
                cg_route_objects, cg_cost = cg_solver.solve(max_iterations=max_iter)
                
                # Route オブジェクトから通常のルート形式に変換
                cg_routes = [route.customers for route in cg_route_objects]
                
                cg_time = time.time() - start_time
                
                results['column_generation'] = {
                    'routes': cg_routes,
                    'cost': cg_cost,
                    'time': cg_time,
                    'solver': cg_solver
                }
                
                print_solution_results(cg_routes, cg_cost, cg_time, "列生成法", runtime_config)
                
            except Exception as e:
                print(f"列生成法でエラーが発生しました: {e}")
                print("貪欲法の結果のみを使用します。")
                results['column_generation'] = None
        
        # 結果の比較
        if len(results) > 1 and not runtime_config['quiet']:
            print_algorithm_comparison(results, instance, runtime_config)
        
        # より良い解を選択
        best_result = select_best_solution(results)
        routes, total_cost, solver = best_result['routes'], best_result['cost'], best_result.get('solver')
        
        # 解の妥当性を検証（貪欲法の場合のみ）
        if solver and runtime_config['verbose']:
            is_valid = solver.validate_solution(routes)
            print(f"解の検証: {'成功' if is_valid else '失敗'}")
        
        # 可視化を生成
        if runtime_config['enable_visualization']:
            generate_visualizations(instance, routes, file_path, runtime_config)
        
        return routes, total_cost
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        if runtime_config['verbose']:
            import traceback
            traceback.print_exc()
        return None

def print_problem_info(instance, runtime_config):
    """VRP問題情報を表示"""
    if runtime_config['quiet']:
        return
        
    print(f"問題名: {instance.name}")
    print(f"顧客数: {len(instance.get_customer_nodes())}")
    print(f"車両容量: {instance.capacity}")
    
    if runtime_config['verbose']:
        print(f"コメント: {instance.comment}")
    
    # 既知の最適解情報を表示
    instance_name = Path(runtime_config['instance_file']).stem
    optimal_cost = get_optimal_cost(instance_name)
    optimal_vehicles = get_optimal_vehicles(instance_name)
    
    if optimal_cost:
        print(f"既知の最適コスト: {optimal_cost}")
    if optimal_vehicles:
        print(f"既知の最適車両数: {optimal_vehicles}")
    
    print()

def print_solution_results(routes, total_cost, computation_time, algorithm_name="", runtime_config=None):
    """解の結果を表示"""
    if runtime_config and runtime_config['quiet']:
        return
        
    decimal_places = 2
    if runtime_config:
        decimal_places = runtime_config['config_instance'].get('output', 'decimal_places', 2)
    
    print("\n" + "=" * 50)
    title = f"解の結果 ({algorithm_name})" if algorithm_name else "解の結果:"
    print(title)
    print(f"総コスト: {total_cost:.{decimal_places}f}")
    print(f"使用車両数: {len(routes)}")
    print(f"計算時間: {computation_time:.{decimal_places}f}秒")
    
    # 最適解との比較
    if runtime_config:
        instance_name = Path(runtime_config['instance_file']).stem
        gap = calculate_gap(instance_name, total_cost)
        if gap is not None:
            print(f"最適解とのギャップ: {gap:.{decimal_places}f}%")
    
    print()
    
    # ルート詳細の表示
    if runtime_config and runtime_config['show_route_details']:
        print("ルート詳細:")
        for i, route in enumerate(routes, 1):
            route_str = " -> ".join(map(str, route))
            print(f"  車両 {i}: 0 -> {route_str} -> 0")

def print_algorithm_comparison(results, instance, runtime_config):
    """アルゴリズムの比較結果を表示"""
    config_instance = runtime_config['config_instance']
    decimal_places = config_instance.get('output', 'decimal_places', 2)
    
    print("\n" + "=" * 60)
    print("アルゴリズム比較:")
    
    if 'greedy' in results:
        greedy = results['greedy']
        print(f"貪欲法     : コスト={greedy['cost']:.{decimal_places}f}, 時間={greedy['time']:.{decimal_places}f}秒")
    
    if 'column_generation' in results and results['column_generation']:
        cg = results['column_generation']
        print(f"列生成法   : コスト={cg['cost']:.{decimal_places}f}, 時間={cg['time']:.{decimal_places}f}秒")
        
        if 'greedy' in results:
            improvement = ((greedy['cost'] - cg['cost']) / greedy['cost']) * 100
            print(f"改善率     : {improvement:.{decimal_places}f}%")
    
    # 最適解との比較
    if config_instance.get('output', 'show_optimal_gap', True):
        instance_name = Path(runtime_config['instance_file']).stem
        optimal_cost = get_optimal_cost(instance_name)
        
        if optimal_cost:
            print(f"最適解     : {optimal_cost}")
            
            if 'greedy' in results:
                greedy_gap = calculate_gap(instance_name, results['greedy']['cost'])
                if greedy_gap is not None:
                    print(f"貪欲法ギャップ: {greedy_gap:.{decimal_places}f}%")
            
            if 'column_generation' in results and results['column_generation']:
                cg_gap = calculate_gap(instance_name, results['column_generation']['cost'])
                if cg_gap is not None:
                    print(f"列生成法ギャップ: {cg_gap:.{decimal_places}f}%")

def select_best_solution(results):
    """最良の解を選択"""
    if not results:
        return {'routes': [], 'cost': float('inf'), 'time': 0}
    
    best_result = None
    best_cost = float('inf')
    
    for algorithm, result in results.items():
        if result and result['cost'] < best_cost:
            best_cost = result['cost']
            best_result = result
    
    return best_result or list(results.values())[0]

def generate_visualizations(instance, routes, file_path, runtime_config):
    """可視化画像を生成"""
    if runtime_config['quiet']:
        return
        
    print("\n" + "=" * 50)
    print("可視化を生成中")
    
    try:
        # 出力ディレクトリが存在することを確認
        output_dir = Path(runtime_config['output_directory'])
        output_dir.mkdir(exist_ok=True)
        
        config_instance = runtime_config['config_instance']
        viz_config = config_instance.get('visualization', {})
        
        visualizer = VRPVisualizer(instance)
        
        # 問題インスタンスの可視化を生成
        if runtime_config['verbose']:
            print("問題インスタンスの可視化を作成中...")
        
        problem_path = output_dir / "problem_instance.png"
        visualizer.plot_problem_instance(
            save_path=str(problem_path),
            show_plot=False
        )
        
        # 解の可視化を生成
        if runtime_config['verbose']:
            print("解の可視化を作成中...")
        
        solution_title = f"VRP Solution - {instance.name}"
        solution_path = output_dir / "solution_visualization.png"
        visualizer.plot_solution(
            routes=routes,
            title=solution_title,
            save_path=str(solution_path), 
            show_plot=False
        )
        
        if not runtime_config['quiet']:
            print(f"可視化画像を {output_dir}/ ディレクトリに保存しました:")
            print("- problem_instance.png: 問題インスタンス（顧客分布）")
            print("- solution_visualization.png: VRP解の可視化")
        
    except Exception as viz_error:
        print(f"可視化エラー: {viz_error}")
        if runtime_config['verbose']:
            print("matplotlibが正しくインストールされていない可能性があります")

def main():
    """メインエントリポイント"""
    # コマンドライン引数を解析
    runtime_config = parse_args()
    
    # 引数の妥当性を検証
    if not validate_args(runtime_config):
        sys.exit(1)
    
    # 設定内容の表示
    print_config_summary(runtime_config)
    
    if not runtime_config['quiet']:
        print("配送経路問題（VRP）ソルバー")
        print("=" * 50)
    
    # VRP問題を解く
    result = solve_vrp_problem(runtime_config)
    
    if result is None:
        print("VRP問題の解決に失敗しました")
        sys.exit(1)
    
    if not runtime_config['quiet']:
        print("\nVRP解決が正常に完了しました!")

if __name__ == "__main__":
    main()
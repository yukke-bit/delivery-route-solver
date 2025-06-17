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

def solve_vrp_problem(file_path: str, visualize: bool = True) -> Optional[tuple]:
    """
    ファイルからVRP問題を解く
    
    Args:
        file_path: VRPファイルのパス
        visualize: 可視化を生成するかどうか
    
    Returns:
        成功時は(routes, total_cost)のタプル、失敗時はNone
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return None
    
    try:
        # VRPインスタンスを読み込み
        print(f"VRPファイルを読み込み中: {file_path}")
        instance = parse_vrp_file(file_path)
        
        # 問題情報を表示
        print_problem_info(instance)
        
        # 両方のアルゴリズムで解く
        results = {}
        
        # 1. 貪欲アルゴリズムで解く
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
        
        print_solution_results(greedy_routes, greedy_cost, greedy_time, "貪欲法")
        
        # 2. 列生成法で解く
        print("\n=== 列生成法 ===")
        start_time = time.time()
        
        try:
            cg_solver = ColumnGeneration(instance)
            cg_route_objects, cg_cost = cg_solver.solve(max_iterations=50)
            
            # Route オブジェクトから通常のルート形式に変換
            cg_routes = [route.customers for route in cg_route_objects]
            
            cg_time = time.time() - start_time
            
            results['column_generation'] = {
                'routes': cg_routes,
                'cost': cg_cost,
                'time': cg_time,
                'solver': cg_solver
            }
            
            print_solution_results(cg_routes, cg_cost, cg_time, "列生成法")
            
        except Exception as e:
            print(f"列生成法でエラーが発生しました: {e}")
            print("貪欲法の結果のみを使用します。")
            results['column_generation'] = None
        
        # 結果の比較
        print("\n" + "=" * 60)
        print("アルゴリズム比較:")
        print(f"貪欲法     : コスト={greedy_cost:.2f}, 時間={greedy_time:.2f}秒")
        if results['column_generation']:
            print(f"列生成法   : コスト={cg_cost:.2f}, 時間={cg_time:.2f}秒")
            improvement = ((greedy_cost - cg_cost) / greedy_cost) * 100
            print(f"改善率     : {improvement:.2f}%")
        
        # 最適解が既知の場合は比較
        optimal_cost = extract_optimal_cost(instance.comment)
        if optimal_cost:
            print(f"最適解     : {optimal_cost}")
            greedy_gap = ((greedy_cost - optimal_cost) / optimal_cost) * 100
            print(f"貪欲法ギャップ: {greedy_gap:.2f}%")
            
            if results['column_generation']:
                cg_gap = ((cg_cost - optimal_cost) / optimal_cost) * 100
                print(f"列生成法ギャップ: {cg_gap:.2f}%")
        
        # より良い解を選択
        if results['column_generation'] and cg_cost < greedy_cost:
            print("\n最良解: 列生成法")
            routes, total_cost, solver = cg_routes, cg_cost, None
        else:
            print("\n最良解: 貪欲法")
            routes, total_cost, solver = greedy_routes, greedy_cost, greedy_solver
        
        # 解の妥当性を検証（貪欲法の場合のみ）
        if solver:
            is_valid = solver.validate_solution(routes)
            print(f"解の検証: {'成功' if is_valid else '失敗'}")
        
        # 可視化を生成
        if visualize:
            generate_visualizations(instance, routes, file_path)
        
        return routes, total_cost
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None

def print_problem_info(instance):
    """VRP問題情報を表示"""
    print(f"問題名: {instance.name}")
    print(f"顧客数: {len(instance.get_customer_nodes())}")
    print(f"車両容量: {instance.capacity}")
    print(f"コメント: {instance.comment}")
    print()

def print_solution_results(routes, total_cost, computation_time, algorithm_name=""):
    """解の結果を表示"""
    print("\n" + "=" * 50)
    title = f"解の結果 ({algorithm_name})" if algorithm_name else "解の結果:"
    print(title)
    print(f"総コスト: {total_cost:.2f}")
    print(f"使用車両数: {len(routes)}")
    print(f"計算時間: {computation_time:.2f}秒")
    print()
    
    print("ルート詳細:")
    for i, route in enumerate(routes, 1):
        route_str = " -> ".join(map(str, route))
        print(f"  車両 {i}: 0 -> {route_str} -> 0")

def extract_optimal_cost(comment: str) -> Optional[float]:
    """コメント文字列から最適コストを抽出"""
    try:
        # "Optimal value: XXX" パターンを探す
        import re
        match = re.search(r'Optimal value:\s*(\d+)', comment)
        if match:
            return float(match.group(1))
    except:
        pass
    return None

def generate_visualizations(instance, routes, file_path):
    """可視化画像を生成"""
    print("\n" + "=" * 50)
    print("可視化を生成中")
    
    try:
        # resultsディレクトリが存在することを確認
        Path("results").mkdir(exist_ok=True)
        
        visualizer = VRPVisualizer(instance)
        
        # 問題インスタンスの可視化を生成
        print("問題インスタンスの可視化を作成中...")
        visualizer.plot_problem_instance(
            save_path="results/problem_instance.png",
            show_plot=False
        )
        
        # 解の可視化を生成
        print("解の可視化を作成中...")
        solution_title = f"VRP Solution - {instance.name} - Greedy Algorithm"
        visualizer.plot_solution(
            routes=routes,
            title=solution_title,
            save_path="results/solution_visualization.png", 
            show_plot=False
        )
        
        print("可視化画像を results/ ディレクトリに保存しました:")
        print("- problem_instance.png: 問題インスタンス（顧客分布）")
        print("- solution_visualization.png: VRP解の可視化")
        
    except Exception as viz_error:
        print(f"可視化エラー: {viz_error}")
        print("matplotlibが正しくインストールされていない可能性があります")

def main():
    """メインエントリポイント"""
    print("配送経路問題（VRP）ソルバー")
    print("=" * 50)
    
    # デフォルトテストファイル
    test_file = "data/instances/A-n32-k5.vrp"
    
    # VRP問題を解く
    result = solve_vrp_problem(test_file, visualize=True)
    
    if result is None:
        print("VRP問題の解決に失敗しました")
        sys.exit(1)
    
    print("\nVRP解決が正常に完了しました!")

if __name__ == "__main__":
    main()
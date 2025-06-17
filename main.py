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
# from src.column_generation import ColumnGeneration  # TODO: 実装を完成させる

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
        
        # 貪欲アルゴリズムで解く
        print("貪欲アルゴリズムで解いています...")
        start_time = time.time()
        
        solver = SimpleVRPSolver(instance)
        routes, total_cost = solver.solve()
        
        end_time = time.time()
        
        # 結果を表示
        print_solution_results(routes, total_cost, end_time - start_time)
        
        # 解の妥当性を検証
        is_valid = solver.validate_solution(routes)
        print(f"解の検証: {'成功' if is_valid else '失敗'}")
        
        # 最適解が既知の場合は比較
        optimal_cost = extract_optimal_cost(instance.comment)
        if optimal_cost:
            gap = ((total_cost - optimal_cost) / optimal_cost) * 100
            print(f"最適コスト: {optimal_cost}")
            print(f"最適解からのギャップ: {gap:.2f}%")
        
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

def print_solution_results(routes, total_cost, computation_time):
    """解の結果を表示"""
    print("\n" + "=" * 50)
    print("解の結果:")
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
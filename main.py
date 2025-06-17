#!/usr/bin/env python3
"""
配送経路問題を解くためのメインファイル
列生成法を使用してVRPを解く
"""

import os
import sys
import time
from src.vrp_parser import parse_vrp_file
from src.simple_vrp_solver import SimpleVRPSolver
from src.visualizer import VRPVisualizer
# from src.column_generation import ColumnGeneration  # 後で使用

def main():
    """メイン処理：VRPファイルを読み込んで貪欲法で解く"""
    print("配送経路問題ソルバー（列生成法）")
    print("=" * 50)
    
    # テスト用のVRPファイルを指定
    test_file = "data/instances/A-n32-k5.vrp"
    
    # ファイルの存在確認
    if not os.path.exists(test_file):
        print(f"エラー: ファイル {test_file} が見つかりません")
        return
    
    try:
        # VRPファイルを読み込んで問題インスタンスを作成
        print(f"VRPファイルを読み込み中: {test_file}")
        instance = parse_vrp_file(test_file)
        
        # 問題の基本情報を表示
        print(f"問題名: {instance.name}")
        print(f"顧客数: {len(instance.get_customer_nodes())}")
        print(f"車両容量: {instance.capacity}")
        print(f"コメント: {instance.comment}")
        print()
        
        # シンプルな貪欲法で解く（動作テスト用）
        print("貪欲法で解法開始...")
        start_time = time.time()
        
        # ソルバーを初期化して実行
        solver = SimpleVRPSolver(instance)
        routes, total_cost = solver.solve()
        
        end_time = time.time()
        
        # 解法結果の表示
        print("\n" + "=" * 50)
        print("解法結果:")
        print(f"総コスト: {total_cost:.2f}")
        print(f"使用車両数: {len(routes)}")
        print(f"計算時間: {end_time - start_time:.2f}秒")
        print()
        
        # 各車両のルートを詳細表示
        print("ルート詳細:")
        for i, route in enumerate(routes, 1):
            print(f"  車両 {i}: 0 -> {' -> '.join(map(str, route))} -> 0")
        
        # 解の妥当性をチェック
        print(f"\n解の妥当性: {'OK' if solver.validate_solution(routes) else 'NG'}")
        
        # 既知の最適解との比較
        optimal_cost = 784  # A-n32-k5の最適解（COMMENTから取得）
        gap = ((total_cost - optimal_cost) / optimal_cost) * 100
        print(f"最適解: {optimal_cost}")
        print(f"ギャップ: {gap:.2f}%")
        
        # 最適解ファイルの存在確認
        optimal_file = test_file.replace('.vrp', '').replace('A-n', 'opt-A-n')
        if os.path.exists(f"data/instances/{os.path.basename(optimal_file)}"):
            print(f"\n最適解ファイル: {optimal_file}")
            # TODO: 最適解の読み込みと詳細比較は後で実装
        
        # 解の可視化
        print("\n" + "=" * 50)
        print("解の可視化")
        
        try:
            # 可視化クラスを初期化
            visualizer = VRPVisualizer(instance)
            
            # 問題インスタンス（顧客分布）を表示
            print("Generating problem instance visualization...")
            visualizer.plot_problem_instance(
                save_path="results/problem_instance.png",
                show_plot=False  # ターミナル環境では表示しない
            )
            
            # VRP解を可視化
            print("Generating VRP solution visualization...")
            solution_title = f"VRP Solution: {instance.name} (Greedy Algorithm)"
            visualizer.plot_solution(
                routes=routes,
                title=solution_title,
                save_path="results/solution_visualization.png", 
                show_plot=False  # ターミナル環境では表示しない
            )
            
            print("Visualization images saved to results/ directory:")
            print("- problem_instance.png: Problem instance (customer distribution)")
            print("- solution_visualization.png: VRP solution visualization")
            
        except Exception as viz_error:
            print(f"Visualization error: {viz_error}")
            print("matplotlib may not be properly installed")
        
    except Exception as e:
        # エラーが発生した場合の処理
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # スクリプトが直接実行された場合のみmain()を呼び出し
    main()
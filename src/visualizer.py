"""
VRP解の可視化モジュール
配送ルートを地図上にプロットして表示
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import List, Tuple
import numpy as np
from .vrp_parser import VRPInstance, Customer

# 日本語フォント問題の回避：英語ラベルを使用
plt.rcParams['font.family'] = 'DejaVu Sans'

class VRPVisualizer:
    """VRP解の可視化を行うクラス"""
    
    def __init__(self, instance: VRPInstance):
        """可視化クラスの初期化
        
        Args:
            instance: VRP問題インスタンス
        """
        self.instance = instance
        self.depot = instance.get_depot()
        self.customers = instance.get_customer_nodes()
        
        # 色のパレットを準備（車両別に異なる色を使用）
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
            '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F',
            '#BB8FCE', '#85C1E9', '#F8C471', '#82E0AA'
        ]
    
    def plot_solution(self, routes: List[List[int]], title: str = "VRP Solution Visualization", 
                     save_path: str = None, show_plot: bool = True) -> None:
        """VRP解を可視化してプロット
        
        Args:
            routes: 各車両のルート（顧客IDのリスト）
            title: グラフのタイトル
            save_path: 保存パス（Noneの場合は保存しない）
            show_plot: プロットを表示するかどうか
        """
        plt.figure(figsize=(12, 8))
        plt.title(title, fontsize=16, fontweight='bold')
        
        # デポを特別な記号で表示
        plt.scatter(self.depot.x, self.depot.y, 
                   c='red', s=200, marker='s', 
                   label=f'Depot (ID: {self.depot.id})', 
                   edgecolor='black', linewidth=2, zorder=5)
        
        # デポにテキストラベルを追加
        plt.annotate(f'Depot\n{self.depot.id}', 
                    (self.depot.x, self.depot.y),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # 全顧客を薄い色で表示
        customer_x = [c.x for c in self.customers]
        customer_y = [c.y for c in self.customers]
        plt.scatter(customer_x, customer_y, 
                   c='lightgray', s=50, alpha=0.6, zorder=1)
        
        # 顧客にIDラベルを追加
        for customer in self.customers:
            plt.annotate(str(customer.id), 
                        (customer.x, customer.y),
                        xytext=(3, 3), textcoords='offset points',
                        fontsize=8, alpha=0.7)
        
        # 各車両のルートを異なる色で描画
        for i, route in enumerate(routes):
            if not route:  # 空のルートはスキップ
                continue
                
            color = self.colors[i % len(self.colors)]
            
            # ルート上の顧客を強調表示
            route_customers = [c for c in self.instance.customers if c.id in route]
            route_x = [c.x for c in route_customers]
            route_y = [c.y for c in route_customers]
            
            plt.scatter(route_x, route_y, 
                       c=color, s=100, alpha=0.8, 
                       label=f'Vehicle {i+1} ({len(route)} customers)',
                       edgecolor='black', linewidth=1, zorder=3)
            
            # ルートの線を描画
            self._draw_route_lines(route, color, i+1)
        
        # グラフの設定
        plt.xlabel('X Coordinate', fontsize=12)
        plt.ylabel('Y Coordinate', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.axis('equal')  # 縦横比を等しくする
        
        # グラフを調整
        plt.tight_layout()
        
        # 保存
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved: {save_path}")
        
        # 表示
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def _draw_route_lines(self, route: List[int], color: str, vehicle_num: int) -> None:
        """単一ルートの線を描画
        
        Args:
            route: 顧客IDのリスト
            color: 線の色
            vehicle_num: 車両番号
        """
        if not route:
            return
        
        # デポから最初の顧客への線
        first_customer = next(c for c in self.instance.customers if c.id == route[0])
        plt.plot([self.depot.x, first_customer.x], 
                [self.depot.y, first_customer.y], 
                color=color, linewidth=2, alpha=0.7, zorder=2)
        
        # 顧客間の線
        for i in range(len(route) - 1):
            from_customer = next(c for c in self.instance.customers if c.id == route[i])
            to_customer = next(c for c in self.instance.customers if c.id == route[i + 1])
            plt.plot([from_customer.x, to_customer.x], 
                    [from_customer.y, to_customer.y], 
                    color=color, linewidth=2, alpha=0.7, zorder=2)
        
        # 最後の顧客からデポへの線
        last_customer = next(c for c in self.instance.customers if c.id == route[-1])
        plt.plot([last_customer.x, self.depot.x], 
                [last_customer.y, self.depot.y], 
                color=color, linewidth=2, alpha=0.7, zorder=2)
        
        # 車両番号をルートの中央付近に表示
        if len(route) > 0:
            mid_idx = len(route) // 2
            mid_customer = next(c for c in self.instance.customers if c.id == route[mid_idx])
            plt.annotate(f'V{vehicle_num}', 
                        (mid_customer.x, mid_customer.y),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=9, fontweight='bold', color=color,
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                alpha=0.8, edgecolor=color))
    
    def plot_solution_comparison(self, routes1: List[List[int]], routes2: List[List[int]],
                               cost1: float, cost2: float, 
                               label1: str = "Solution 1", label2: str = "Solution 2",
                               save_path: str = None) -> None:
        """2つの解を比較表示
        
        Args:
            routes1: 第1の解のルート
            routes2: 第2の解のルート  
            cost1: 第1の解のコスト
            cost2: 第2の解のコスト
            label1: 第1の解のラベル
            label2: 第2の解のラベル
            save_path: 保存パス
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
        
        # 第1の解
        plt.sca(ax1)
        self.plot_solution(routes1, 
                          title=f"{label1} (Cost: {cost1:.2f})", 
                          show_plot=False)
        
        # 第2の解
        plt.sca(ax2) 
        self.plot_solution(routes2, 
                          title=f"{label2} (Cost: {cost2:.2f})", 
                          show_plot=False)
        
        # 全体のタイトル
        fig.suptitle(f'VRP Solution Comparison: {self.instance.name}', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Comparison result saved: {save_path}")
        
        plt.show()
    
    def plot_problem_instance(self, save_path: str = None, show_plot: bool = True) -> None:
        """問題インスタンス（顧客分布）のみを可視化
        
        Args:
            save_path: 保存パス
            show_plot: プロットを表示するかどうか
        """
        plt.figure(figsize=(10, 8))
        plt.title(f'VRP Problem Instance: {self.instance.name}', fontsize=16, fontweight='bold')
        
        # デポを表示
        plt.scatter(self.depot.x, self.depot.y, 
                   c='red', s=300, marker='s', 
                   label=f'Depot (ID: {self.depot.id})', 
                   edgecolor='black', linewidth=2)
        
        # 顧客を表示（需要量に応じてサイズを変更）
        max_demand = max(c.demand for c in self.customers) if self.customers else 1
        
        for customer in self.customers:
            # 需要量に比例したサイズ（最小50、最大200）
            size = 50 + (customer.demand / max_demand) * 150
            plt.scatter(customer.x, customer.y, 
                       c='lightblue', s=size, alpha=0.7,
                       edgecolor='navy', linewidth=1)
            
            # 顧客IDと需要量を表示
            plt.annotate(f'{customer.id}\n(D:{customer.demand})', 
                        (customer.x, customer.y),
                        xytext=(0, 0), textcoords='offset points',
                        fontsize=8, ha='center', va='center')
        
        plt.scatter([], [], c='lightblue', s=100, alpha=0.7, 
                   label='Customer (size=demand)', edgecolor='navy')
        
        plt.xlabel('X Coordinate', fontsize=12)
        plt.ylabel('Y Coordinate', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        
        # 問題情報を表示
        info_text = f"Customers: {len(self.customers)}\nVehicle Capacity: {self.instance.capacity}"
        plt.text(0.02, 0.98, info_text, transform=plt.gca().transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Problem instance saved: {save_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
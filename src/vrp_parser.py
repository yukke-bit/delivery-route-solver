"""
VRP問題ファイルのパーサー
TSPLIB95形式のVRPファイルを読み込む
"""

import re
import math
from typing import Dict, List, Tuple, NamedTuple

class Customer(NamedTuple):
    """顧客情報を表すクラス"""
    id: int          # 顧客ID
    x: float         # X座標
    y: float         # Y座標  
    demand: int      # 需要量

class VRPInstance:
    """VRP問題インスタンスを表すクラス"""
    def __init__(self):
        self.name = ""               # 問題名
        self.comment = ""            # コメント（最適解情報など）
        self.type = ""               # 問題タイプ（CVRP等）
        self.dimension = 0           # ノード数（デポ+顧客数）
        self.edge_weight_type = ""   # 距離計算方法（EUC_2D等）
        self.capacity = 0            # 車両容量
        self.customers = []          # 顧客リスト（デポ含む） List[Customer]
        self.depot_id = 1            # デポのID（通常は1）
    
    def euclidean_distance(self, customer1: Customer, customer2: Customer) -> float:
        """2点間のユークリッド距離を計算"""
        dx = customer1.x - customer2.x
        dy = customer1.y - customer2.y
        return math.sqrt(dx * dx + dy * dy)
    
    def get_distance_matrix(self) -> List[List[float]]:
        """全顧客間の距離行列を生成"""
        n = len(self.customers)
        matrix = [[0.0] * n for _ in range(n)]  # n×n行列を初期化
        
        # 全ペアの距離を計算
        for i in range(n):
            for j in range(n):
                if i != j:  # 同じ顧客同士は距離0
                    matrix[i][j] = self.euclidean_distance(self.customers[i], self.customers[j])
        
        return matrix
    
    def get_depot(self) -> Customer:
        """デポ（ID=1）を取得"""
        for customer in self.customers:
            if customer.id == self.depot_id:
                return customer
        return self.customers[0]  # フォールバック
    
    def get_customer_nodes(self) -> List[Customer]:
        """デポ以外の顧客ノードを取得"""
        return [c for c in self.customers if c.id != self.depot_id]

def parse_vrp_file(filepath: str) -> VRPInstance:
    """TSPLIB95形式のVRPファイルを解析してVRPInstanceを返す"""
    instance = VRPInstance()
    
    # ファイルを読み込み、各行をトリム
    with open(filepath, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # ヘッダー情報の解析
        if line.startswith('NAME'):
            instance.name = line.split(':')[1].strip()
        elif line.startswith('COMMENT'):
            instance.comment = line.split(':', 1)[1].strip()  # コロンが複数ある場合対応
        elif line.startswith('TYPE'):
            instance.type = line.split(':')[1].strip()
        elif line.startswith('DIMENSION'):
            instance.dimension = int(line.split(':')[1].strip())
        elif line.startswith('EDGE_WEIGHT_TYPE'):
            instance.edge_weight_type = line.split(':')[1].strip()
        elif line.startswith('CAPACITY'):
            instance.capacity = int(line.split(':')[1].strip())
        elif line.startswith('NODE_COORD_SECTION'):
            # 座標データセクションの読み取り
            i += 1
            while i < len(lines) and not lines[i].startswith('DEMAND_SECTION'):
                if lines[i] and not lines[i].startswith('EOF'):
                    parts = lines[i].split()
                    if len(parts) >= 3:
                        node_id = int(parts[0])    # ノードID
                        x = float(parts[1])        # X座標
                        y = float(parts[2])        # Y座標
                        # 需要は後で設定するため、とりあえず0で初期化
                        instance.customers.append(Customer(node_id, x, y, 0))
                i += 1
            i -= 1  # 次のセクション処理のため戻す
        elif line.startswith('DEMAND_SECTION'):
            # 需要データセクションの読み取り
            i += 1
            demand_dict = {}  # 需要の一時格納用辞書
            while i < len(lines) and not lines[i].startswith('DEPOT_SECTION'):
                if lines[i] and not lines[i].startswith('EOF'):
                    parts = lines[i].split()
                    if len(parts) >= 2:
                        node_id = int(parts[0])    # ノードID
                        demand = int(parts[1])     # 需要量
                        demand_dict[node_id] = demand
                i += 1
            
            # 既存の顧客データに需要情報を追加
            updated_customers = []
            for customer in instance.customers:
                demand = demand_dict.get(customer.id, 0)  # 見つからない場合は0
                updated_customers.append(Customer(customer.id, customer.x, customer.y, demand))
            instance.customers = updated_customers
            i -= 1
        
        i += 1
    
    return instance

if __name__ == "__main__":
    # テスト用
    instance = parse_vrp_file("data/instances/A-n32-k5.vrp")
    print(f"問題名: {instance.name}")
    print(f"次元: {instance.dimension}")
    print(f"容量: {instance.capacity}")
    print(f"顧客数: {len(instance.get_customer_nodes())}")
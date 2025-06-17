"""
シンプルなVRPソルバー（貪欲法）
列生成法の代替として、まず動作確認用の実装
"""

from typing import List, Tuple
from .vrp_parser import VRPInstance, Customer
import math

class SimpleVRPSolver:
    """シンプルな貪欲法によるVRPソルバー"""
    
    def __init__(self, instance: VRPInstance):
        """ソルバーの初期化"""
        self.instance = instance                    # VRP問題インスタンス
        self.depot = instance.get_depot()           # デポ情報
        self.customers = instance.get_customer_nodes()  # 顧客リスト（デポ除く）
        
    def solve(self) -> Tuple[List[List[int]], float]:
        """貪欲法でVRPを解く
        
        Returns:
            routes: 各車両のルート（顧客IDのリスト）
            total_cost: 総移動コスト
        """
        routes = []           # 解として得られるルート集合
        total_cost = 0.0      # 総移動コスト
        unvisited = self.customers.copy()  # 未訪問顧客リスト
        
        # 全顧客が訪問されるまでルートを構築
        while unvisited:
            # 1台の車両でのルートを構築
            route, route_cost = self.construct_route(unvisited)
            routes.append(route)
            total_cost += route_cost
            
            # 訪問済みの顧客を未訪問リストから削除
            for customer_id in route:
                unvisited = [c for c in unvisited if c.id != customer_id]
        
        return routes, total_cost
    
    def construct_route(self, available_customers: List[Customer]) -> Tuple[List[int], float]:
        """1台の車両で実行可能なルートを構築（貪欲法）
        
        Args:
            available_customers: 未訪問の顧客リスト
            
        Returns:
            route: 構築されたルート（顧客IDのリスト）
            route_cost: ルートの総移動コスト
        """
        route = []                              # 構築中のルート
        current_load = 0                        # 現在の積載量
        current_pos = self.depot                # 現在位置（デポから開始）
        route_cost = 0.0                       # ルートの累積コスト
        remaining = available_customers.copy()  # 残り顧客リスト
        
        # 容量制約内で可能な限り顧客を追加
        while remaining:
            # 現在位置から最も近い、容量制約を満たす顧客を選択
            best_customer = None
            best_distance = float('inf')
            
            # 全候補顧客を評価
            for customer in remaining:
                # 容量制約チェック
                if current_load + customer.demand <= self.instance.capacity:
                    distance = self.instance.euclidean_distance(current_pos, customer)
                    # より近い顧客を選択（貪欲法）
                    if distance < best_distance:
                        best_distance = distance
                        best_customer = customer
            
            # 追加可能な顧客がない場合はルート完了
            if best_customer is None:
                break
            
            # 選択された顧客をルートに追加
            route.append(best_customer.id)
            current_load += best_customer.demand
            route_cost += best_distance
            current_pos = best_customer           # 位置を更新
            remaining.remove(best_customer)       # 候補から削除
        
        # デポに戻るコストを追加
        if route:
            return_cost = self.instance.euclidean_distance(current_pos, self.depot)
            route_cost += return_cost
        
        return route, route_cost
    
    def calculate_total_distance(self, routes: List[List[int]]) -> float:
        """ルート集合の総距離を計算"""
        total = 0.0
        for route in routes:
            if not route:
                continue
            
            # デポから最初の顧客
            first_customer = next(c for c in self.instance.customers if c.id == route[0])
            total += self.instance.euclidean_distance(self.depot, first_customer)
            
            # 顧客間の移動
            for i in range(len(route) - 1):
                from_customer = next(c for c in self.instance.customers if c.id == route[i])
                to_customer = next(c for c in self.instance.customers if c.id == route[i + 1])
                total += self.instance.euclidean_distance(from_customer, to_customer)
            
            # 最後の顧客からデポ
            last_customer = next(c for c in self.instance.customers if c.id == route[-1])
            total += self.instance.euclidean_distance(last_customer, self.depot)
        
        return total
    
    def validate_solution(self, routes: List[List[int]]) -> bool:
        """解の妥当性をチェック
        
        Args:
            routes: 検証するルート集合
            
        Returns:
            bool: 解が妥当な場合True、そうでなければFalse
        """
        visited = set()  # 訪問済み顧客のID集合
        
        # 各ルートをチェック
        for route in routes:
            route_load = 0  # このルートの積載量
            
            for customer_id in route:
                # 重複訪問チェック
                if customer_id in visited:
                    print(f"エラー: 顧客 {customer_id} が複数回訪問されています")
                    return False
                visited.add(customer_id)
                
                # 積載量を累積
                customer = next(c for c in self.instance.customers if c.id == customer_id)
                route_load += customer.demand
            
            # 容量制約チェック
            if route_load > self.instance.capacity:
                print(f"エラー: ルート {route} の積載量 {route_load} が容量 {self.instance.capacity} を超えています")
                return False
        
        # 全顧客訪問チェック
        customer_ids = {c.id for c in self.customers}
        if visited != customer_ids:
            print(f"エラー: 未訪問の顧客があります: {customer_ids - visited}")
            return False
        
        return True
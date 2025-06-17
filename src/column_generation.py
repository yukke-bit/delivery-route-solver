"""
列生成法によるVRP解法の実装
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import pulp
from .vrp_parser import VRPInstance, Customer

@dataclass
class Route:
    """ルート（列）を表すクラス"""
    customers: List[int]  # 訪問する顧客ID（デポは含まない）
    cost: float
    load: int
    
    def __str__(self):
        return f"Route: 0 -> {' -> '.join(map(str, self.customers))} -> 0 (cost={self.cost:.2f}, load={self.load})"

class ColumnGeneration:
    def __init__(self, instance: VRPInstance):
        self.instance = instance
        self.depot = instance.get_depot()
        self.customers = instance.get_customer_nodes()
        self.distance_matrix = instance.get_distance_matrix()
        
        # インデックスマッピング作成
        self.customer_to_index = {c.id: i for i, c in enumerate(instance.customers)}
        self.routes = []  # 生成されたルート一覧
        self.dual_prices = []  # 双対価格
        
    def calculate_route_cost(self, route_customers: List[int]) -> float:
        """ルートのコストを計算"""
        if not route_customers:
            return 0.0
        
        cost = 0.0
        # デポから最初の顧客
        depot_idx = self.customer_to_index[self.depot.id]
        first_idx = self.customer_to_index[route_customers[0]]
        cost += self.distance_matrix[depot_idx][first_idx]
        
        # 顧客間の移動
        for i in range(len(route_customers) - 1):
            from_idx = self.customer_to_index[route_customers[i]]
            to_idx = self.customer_to_index[route_customers[i + 1]]
            cost += self.distance_matrix[from_idx][to_idx]
        
        # 最後の顧客からデポ
        last_idx = self.customer_to_index[route_customers[-1]]
        cost += self.distance_matrix[last_idx][depot_idx]
        
        return cost
    
    def calculate_route_load(self, route_customers: List[int]) -> int:
        """ルートの積載量を計算"""
        return sum(c.demand for c in self.instance.customers if c.id in route_customers)
    
    def is_feasible_route(self, route_customers: List[int]) -> bool:
        """ルートが実行可能かチェック"""
        load = self.calculate_route_load(route_customers)
        return load <= self.instance.capacity
    
    def generate_initial_routes(self) -> List[Route]:
        """初期ルート生成（各顧客への単独ルート）"""
        routes = []
        for customer in self.customers:
            if customer.demand <= self.instance.capacity:
                cost = self.calculate_route_cost([customer.id])
                load = customer.demand
                routes.append(Route([customer.id], cost, load))
        return routes
    
    def solve_master_problem(self, routes: List[Route]) -> Tuple[float, List[float]]:
        """マスター問題を解く（線形計画緩和）"""
        # 決定変数: 各ルートを使用するかどうか
        prob = pulp.LpProblem("Master_Problem", pulp.LpMinimize)
        
        # 変数定義
        route_vars = []
        for i, route in enumerate(routes):
            var = pulp.LpVariable(f"route_{i}", lowBound=0, cat='Continuous')
            route_vars.append(var)
        
        # 目的関数: 総移動コストの最小化
        prob += pulp.lpSum([route.cost * var for route, var in zip(routes, route_vars)])
        
        # 制約: 各顧客は1回だけ訪問
        customer_constraints = {}
        for customer in self.customers:
            constraint = []
            for route, var in zip(routes, route_vars):
                if customer.id in route.customers:
                    constraint.append(var)
            
            if constraint:
                prob += pulp.lpSum(constraint) == 1, f"customer_{customer.id}"
                customer_constraints[customer.id] = len(prob.constraints) - 1
        
        # 問題を解く（複数のソルバーを試す）
        solved = False
        solvers = [
            lambda: prob.solve(),
            lambda: prob.solve(pulp.GLPK_CMD(msg=0)) if pulp.GLPK_CMD().available() else None,
            lambda: prob.solve(pulp.PYGLPK()) if pulp.PYGLPK().available() else None
        ]
        
        for solver in solvers:
            try:
                result = solver()
                if result is not None:
                    solved = True
                    break
            except Exception:
                continue
        
        if not solved:
            # 最後の手段：簡単な線形計画問題として解く
            prob.solve()
        
        if prob.status != pulp.LpStatusOptimal:
            raise ValueError("マスター問題が解けませんでした")
        
        # 目的関数値
        objective_value = pulp.value(prob.objective)
        
        # 双対価格を取得
        dual_prices = []
        for customer in self.customers:
            constraint_name = f"customer_{customer.id}"
            for constraint in prob.constraints.values():
                if constraint.name == constraint_name:
                    dual_prices.append(constraint.pi if constraint.pi is not None else 0.0)
                    break
            else:
                dual_prices.append(0.0)
        
        return objective_value, dual_prices
    
    def solve_pricing_problem(self, dual_prices: List[float]) -> Optional[Route]:
        """価格問題を解く（最短路問題）"""
        # シンプルな貪欲法で近似解を求める
        best_route = None
        best_reduced_cost = 0.0
        
        # 各顧客を起点として貪欲にルートを構築
        for start_customer in self.customers:
            current_route = [start_customer.id]
            current_load = start_customer.demand
            current_pos = start_customer
            unvisited = [c for c in self.customers if c.id != start_customer.id]
            
            # 貪欲にルートを拡張
            while unvisited:
                best_next = None
                best_distance = float('inf')
                
                for candidate in unvisited:
                    if current_load + candidate.demand <= self.instance.capacity:
                        distance = self.instance.euclidean_distance(current_pos, candidate)
                        if distance < best_distance:
                            best_distance = distance
                            best_next = candidate
                
                if best_next is None:
                    break
                
                current_route.append(best_next.id)
                current_load += best_next.demand
                current_pos = best_next
                unvisited.remove(best_next)
            
            # このルートの被約費用を計算
            route_cost = self.calculate_route_cost(current_route)
            dual_cost = sum(dual_prices[i] for i, c in enumerate(self.customers) 
                          if c.id in current_route)
            reduced_cost = route_cost - dual_cost
            
            if reduced_cost < best_reduced_cost:
                best_reduced_cost = reduced_cost
                best_route = Route(current_route, route_cost, current_load)
        
        return best_route if best_reduced_cost < -1e-6 else None
    
    def solve(self, max_iterations: int = 100, tolerance: float = 1e-6) -> Tuple[List[Route], float]:
        """列生成アルゴリズムのメインループ"""
        print("列生成アルゴリズム開始...")
        
        # 初期ルート生成
        self.routes = self.generate_initial_routes()
        print(f"初期ルート数: {len(self.routes)}")
        
        for iteration in range(max_iterations):
            print(f"\n反復 {iteration + 1}:")
            
            # マスター問題を解く
            try:
                objective_value, dual_prices = self.solve_master_problem(self.routes)
                print(f"  マスター問題目的関数値: {objective_value:.2f}")
                
                # 価格問題を解く
                new_route = self.solve_pricing_problem(dual_prices)
                
                if new_route is None:
                    print("  負の被約費用を持つルートが見つからません。終了。")
                    break
                
                print(f"  新しいルート追加: {new_route}")
                self.routes.append(new_route)
                
            except Exception as e:
                print(f"  エラー: {e}")
                break
        
        # 最終的な整数解を求める
        final_routes, final_cost = self.solve_integer_master_problem()
        
        return final_routes, final_cost
    
    def solve_integer_master_problem(self) -> Tuple[List[Route], float]:
        """最終的な整数マスター問題を解く"""
        print("\n整数マスター問題を解いています...")
        
        prob = pulp.LpProblem("Integer_Master_Problem", pulp.LpMinimize)
        
        # 変数定義（整数変数）
        route_vars = []
        for i, route in enumerate(self.routes):
            var = pulp.LpVariable(f"route_{i}", lowBound=0, cat='Binary')
            route_vars.append(var)
        
        # 目的関数
        prob += pulp.lpSum([route.cost * var for route, var in zip(self.routes, route_vars)])
        
        # 制約: 各顧客は1回だけ訪問
        for customer in self.customers:
            constraint = []
            for route, var in zip(self.routes, route_vars):
                if customer.id in route.customers:
                    constraint.append(var)
            
            if constraint:
                prob += pulp.lpSum(constraint) == 1, f"customer_{customer.id}"
        
        # 問題を解く（複数のソルバーを試す）
        solved = False
        solvers = [
            lambda: prob.solve(),
            lambda: prob.solve(pulp.GLPK_CMD(msg=0)) if pulp.GLPK_CMD().available() else None,
            lambda: prob.solve(pulp.PYGLPK()) if pulp.PYGLPK().available() else None
        ]
        
        for solver in solvers:
            try:
                result = solver()
                if result is not None:
                    solved = True
                    break
            except Exception:
                continue
        
        if not solved:
            # 最後の手段：簡単な線形計画問題として解く
            prob.solve()
        
        if prob.status != pulp.LpStatusOptimal:
            raise ValueError("整数マスター問題が解けませんでした")
        
        # 選択されたルートを取得
        selected_routes = []
        for route, var in zip(self.routes, route_vars):
            if pulp.value(var) > 0.5:  # バイナリ変数なので0.5を閾値とする
                selected_routes.append(route)
        
        total_cost = pulp.value(prob.objective)
        
        print(f"最終コスト: {total_cost:.2f}")
        print(f"使用ルート数: {len(selected_routes)}")
        
        return selected_routes, total_cost
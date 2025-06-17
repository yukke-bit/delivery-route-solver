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
        
        # インデックスマッピング作成（デポを含む全ノード）
        all_nodes = [self.depot] + self.customers
        self.customer_to_index = {node.id: i for i, node in enumerate(all_nodes)}
        self.routes = []  # 生成されたルート一覧
        self.dual_prices = []  # 双対価格
        
    def calculate_route_cost(self, route_customers: List[int]) -> float:
        """ルートのコストを計算"""
        if not route_customers:
            return 0.0
        
        cost = 0.0
        
        # すべてのノードに対してインデックスマッピングを確認
        def get_node_index(node_id):
            if node_id == self.depot.id:
                return 0  # デポは常にインデックス0
            return self.customer_to_index.get(node_id, 0)
        
        # デポから最初の顧客
        depot_idx = get_node_index(self.depot.id)
        first_idx = get_node_index(route_customers[0])
        cost += self.distance_matrix[depot_idx][first_idx]
        
        # 顧客間の移動
        for i in range(len(route_customers) - 1):
            from_idx = get_node_index(route_customers[i])
            to_idx = get_node_index(route_customers[i + 1])
            cost += self.distance_matrix[from_idx][to_idx]
        
        # 最後の顧客からデポ
        last_idx = get_node_index(route_customers[-1])
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
        """初期ルート生成（多様なルートパターンを作成）"""
        routes = []
        
        # 1. 各顧客への単独ルート
        for customer in self.customers:
            if customer.demand <= self.instance.capacity:
                cost = self.calculate_route_cost([customer.id])
                load = customer.demand
                routes.append(Route([customer.id], cost, load))
        
        # 2. 貪欲法による複数顧客ルート
        remaining_customers = self.customers.copy()
        
        while remaining_customers:
            current_route = []
            current_load = 0
            current_pos = self.depot
            
            # 最も遠い顧客から開始（多様性確保）
            if remaining_customers:
                farthest_customer = max(remaining_customers, 
                    key=lambda c: self.instance.euclidean_distance(self.depot, c))
                
                current_route.append(farthest_customer.id)
                current_load += farthest_customer.demand
                current_pos = farthest_customer
                remaining_customers.remove(farthest_customer)
            
            # 貪欲にルートを拡張
            while remaining_customers:
                best_next = None
                best_distance = float('inf')
                
                for candidate in remaining_customers:
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
                remaining_customers.remove(best_next)
            
            # ルートが有効な場合は追加
            if current_route:
                cost = self.calculate_route_cost(current_route)
                routes.append(Route(current_route, cost, current_load))
        
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
        
        # 問題を解く（優先順位: GLPK → CBC → 近似解法）
        try:
            # LP緩和問題として解く
            for var in route_vars:
                var.cat = 'Continuous'
                var.lowBound = 0
                var.upBound = 1
            
            # GLPKを優先的に使用（Termux環境で安定）
            if pulp.GLPK_CMD().available():
                status = prob.solve(pulp.GLPK_CMD(msg=0, timeLimit=30))
                if status == pulp.LpStatusOptimal:
                    print("    GLPKソルバーで正常に解決")
                else:
                    print(f"    GLPK結果: {pulp.LpStatus[status]}")
                    return self._solve_master_problem_approximation(routes)
            else:
                # フォールバック: CBC
                status = prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=10))
                if status == pulp.LpStatusOptimal:
                    print("    CBCソルバーで正常に解決")
                else:
                    print("    CBCソルバーが失敗、代替手法を使用...")
                    return self._solve_master_problem_approximation(routes)
                    
        except Exception as e:
            print(f"    ソルバーエラー: {e}")
            return self._solve_master_problem_approximation(routes)
        
        # 目的関数値
        objective_value = pulp.value(prob.objective)
        
        # 双対価格を取得
        dual_prices = []
        for customer in self.customers:
            constraint_name = f"customer_{customer.id}"
            dual_value = 0.0
            
            # 制約から双対価格を取得
            for constraint in prob.constraints.values():
                if hasattr(constraint, 'name') and constraint.name == constraint_name:
                    if hasattr(constraint, 'pi') and constraint.pi is not None:
                        dual_value = constraint.pi
                    break
            
            # 双対価格が取得できない場合はコスト効率で近似
            if dual_value == 0.0:
                # この顧客を含む最も効率的なルートのコスト効率を使用
                min_efficiency = float('inf')
                for route in routes:
                    if customer.id in route.customers:
                        efficiency = route.cost / max(len(route.customers), 1)
                        min_efficiency = min(min_efficiency, efficiency)
                
                if min_efficiency != float('inf'):
                    dual_value = min_efficiency
            
            dual_prices.append(dual_value)
        
        return objective_value, dual_prices
    
    def solve_pricing_problem(self, dual_prices: List[float]) -> Optional[Route]:
        """価格問題を解く（ESPPRC - 容量制約付き最短路問題）"""
        
        # 価格問題を線形計画問題として定式化
        prob = pulp.LpProblem("Pricing_Problem", pulp.LpMinimize)
        
        # ノード集合（デポ + 顧客）
        nodes = [self.depot.id] + [c.id for c in self.customers]
        
        # 決定変数: アーク変数 x[i,j] (i→jのアークを使用するか)
        x = {}
        for i in nodes:
            for j in nodes:
                if i != j:
                    x[i, j] = pulp.LpVariable(f"x_{i}_{j}", cat='Binary')
        
        # 目的関数: 被約費用の最小化
        objective = []
        for i in nodes:
            for j in nodes:
                if i != j:
                    # 距離コスト
                    i_idx = self.customer_to_index.get(i, 0)
                    j_idx = self.customer_to_index.get(j, 0)
                    distance_cost = self.distance_matrix[i_idx][j_idx]
                    
                    # 双対価格の減算：顧客を訪問する時のみ
                    reduced_cost = distance_cost
                    if j != self.depot.id:  # jが顧客の場合
                        customer_idx = next((idx for idx, c in enumerate(self.customers) if c.id == j), None)
                        if customer_idx is not None and customer_idx < len(dual_prices):
                            # アークコストから訪問先顧客の双対価格を減算
                            reduced_cost = distance_cost - dual_prices[customer_idx]
                    
                    objective.append(reduced_cost * x[i, j])
        
        prob += pulp.lpSum(objective)
        
        # 制約1: デポから出発（1回のみ）
        prob += pulp.lpSum([x[self.depot.id, j] for j in nodes if j != self.depot.id]) == 1
        
        # 制約2: デポに帰着（1回のみ）
        prob += pulp.lpSum([x[i, self.depot.id] for i in nodes if i != self.depot.id]) == 1
        
        # 制約3: 各顧客での流れ保存
        for customer in self.customers:
            i = customer.id
            inflow = pulp.lpSum([x[j, i] for j in nodes if j != i])
            outflow = pulp.lpSum([x[i, j] for j in nodes if j != i])
            prob += inflow == outflow
        
        # 制約4: 容量制約
        capacity_constraint = []
        for customer in self.customers:
            i = customer.id
            customer_flow = pulp.lpSum([x[j, i] for j in nodes if j != i])
            capacity_constraint.append(customer.demand * customer_flow)
        
        prob += pulp.lpSum(capacity_constraint) <= self.instance.capacity
        
        # 制約5: 各顧客は最大1回訪問
        for customer in self.customers:
            i = customer.id
            prob += pulp.lpSum([x[j, i] for j in nodes if j != i]) <= 1
        
        # 問題を解く（優先順位: GLPK → CBC → 貪欲法）
        try:
            solved = False
            
            # GLPKを優先使用
            if pulp.GLPK_CMD().available():
                try:
                    status = prob.solve(pulp.GLPK_CMD(msg=0, timeLimit=30))
                    if status == pulp.LpStatusOptimal:
                        solved = True
                        print("    価格問題をGLPKで解決")
                except Exception as e:
                    print(f"    GLPK価格問題エラー: {e}")
            
            # フォールバック: CBC
            if not solved:
                try:
                    status = prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=10))
                    if status == pulp.LpStatusOptimal:
                        solved = True
                        print("    価格問題をCBCで解決")
                except Exception as e:
                    print(f"    CBC価格問題エラー: {e}")
            
            if not solved or prob.status != pulp.LpStatusOptimal:
                # 価格問題が解けない場合は貪欲法にフォールバック
                print("    価格問題LP解法失敗、貪欲法を使用")
                return self._solve_pricing_problem_greedy(dual_prices)
            
            # 解が存在し、被約費用が負の場合のみルートを返す
            objective_value = pulp.value(prob.objective)
            if objective_value >= -1e-6:  # 負の被約費用がない
                return None
            
            # 解からルートを抽出
            route_customers = []
            current_node = self.depot.id
            
            # デポから始まるパスを追跡
            while True:
                next_node = None
                for j in nodes:
                    if j != current_node and (current_node, j) in x:
                        if pulp.value(x[current_node, j]) > 0.5:
                            next_node = j
                            break
                
                if next_node is None or next_node == self.depot.id:
                    break
                
                route_customers.append(next_node)
                current_node = next_node
            
            if not route_customers:  # 空のルート
                return None
            
            # ルートの情報を計算
            route_cost = self.calculate_route_cost(route_customers)
            route_load = self.calculate_route_load(route_customers)
            
            return Route(route_customers, route_cost, route_load)
            
        except Exception as e:
            print(f"  価格問題でエラー: {e}")
            # エラーの場合は貪欲法にフォールバック
            return self._solve_pricing_problem_greedy(dual_prices)
    
    def _solve_pricing_problem_greedy(self, dual_prices: List[float]) -> Optional[Route]:
        """価格問題の貪欲法による近似解法（フォールバック用）"""
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
        
        if not self.routes:
            print("初期ルートが生成できませんでした。")
            return [], float('inf')
        
        # 列生成の反復
        for iteration in range(max_iterations):
            print(f"\n反復 {iteration + 1}:")
            
            try:
                # マスター問題を解く
                objective_value, dual_prices = self.solve_master_problem(self.routes)
                print(f"  マスター問題目的関数値: {objective_value:.2f}")
                
                # 双対価格の表示（デバッグ用）
                print(f"  双対価格: {[f'{dp:.3f}' for dp in dual_prices[:min(5, len(dual_prices))]]}...")
                
                # 価格問題を解く
                new_route = self.solve_pricing_problem(dual_prices)
                
                if new_route is None:
                    print("  負の被約費用を持つルートが見つからません。最適解に到達しました。")
                    break
                
                # 重複チェック
                is_duplicate = any(
                    set(route.customers) == set(new_route.customers) 
                    for route in self.routes
                )
                
                if is_duplicate:
                    print("  新しいルートは既存のルートと重複しています。終了。")
                    break
                
                print(f"  新しいルート追加: {new_route}")
                self.routes.append(new_route)
                
                # 収束チェック
                if len(self.routes) > len(self.customers) * 10:  # 無限ループ防止
                    print(f"  ルート数が上限({len(self.customers) * 10})に達しました。終了。")
                    break
                
            except Exception as e:
                print(f"  エラー: {e}")
                import traceback
                traceback.print_exc()
                break
        
        print(f"\n列生成終了。総ルート数: {len(self.routes)}")
        
        # 最終的な整数解を求める
        try:
            final_routes, final_cost = self.solve_integer_master_problem()
            return final_routes, final_cost
        except Exception as e:
            print(f"整数マスター問題でエラー: {e}")
            # フォールバック: 最初のいくつかのルートから貪欲に選択
            return self._fallback_solution()
    
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
        
        # 問題を解く（優先順位: GLPK → CBC）
        try:
            # まずLP緩和で解く
            for var in route_vars:
                var.cat = 'Continuous'
                var.lowBound = 0
                var.upBound = 1
            
            solved = False
            
            # GLPKを優先使用
            if pulp.GLPK_CMD().available():
                try:
                    status = prob.solve(pulp.GLPK_CMD(msg=0, timeLimit=60))
                    if status == pulp.LpStatusOptimal:
                        solved = True
                        print("整数マスター問題をGLPK（LP緩和）で解決")
                except Exception as e:
                    print(f"GLPK整数問題エラー: {e}")
            
            # フォールバック: CBC
            if not solved:
                try:
                    status = prob.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=30))
                    if status == pulp.LpStatusOptimal:
                        solved = True
                        print("整数マスター問題をCBC（LP緩和）で解決")
                except Exception as e:
                    print(f"CBC整数問題エラー: {e}")
            
            if not solved:
                raise ValueError("整数マスター問題が解けませんでした")
                
        except Exception as e:
            print(f"整数問題解法エラー: {e}")
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
    
    def _solve_master_problem_approximation(self, routes: List[Route]) -> Tuple[float, List[float]]:
        """マスター問題の近似解法（ソルバーが使用できない場合）"""
        print("    近似解法を使用してマスター問題を解きます...")
        
        # 各顧客を最もコスト効率の良いルートに割り当て
        customer_assignments = {}
        total_cost = 0.0
        
        for customer in self.customers:
            best_route = None
            best_efficiency = float('inf')
            
            for route in routes:
                if customer.id in route.customers:
                    # コスト効率 = コスト / 顧客数
                    efficiency = route.cost / max(len(route.customers), 1)
                    if efficiency < best_efficiency:
                        best_efficiency = efficiency
                        best_route = route
            
            if best_route:
                customer_assignments[customer.id] = best_route
                total_cost += best_efficiency
        
        # 双対価格の近似値（コスト効率の逆数）
        dual_prices = []
        for customer in self.customers:
            if customer.id in customer_assignments:
                route = customer_assignments[customer.id]
                dual_price = route.cost / max(len(route.customers), 1)
                dual_prices.append(dual_price)
            else:
                dual_prices.append(0.0)
        
        return total_cost, dual_prices
    
    def _fallback_solution(self) -> Tuple[List[Route], float]:
        """整数問題が解けない場合のフォールバック解法"""
        print("フォールバック解法を使用...")
        
        if not self.routes:
            return [], float('inf')
        
        # 各顧客をカバーするルートを貪欲に選択
        selected_routes = []
        covered_customers = set()
        remaining_customers = set(c.id for c in self.customers)
        
        # コスト効率の良いルートから選択
        available_routes = sorted(self.routes, key=lambda r: r.cost / max(len(r.customers), 1))
        
        for route in available_routes:
            # このルートが新しい顧客をカバーするかチェック
            new_customers = set(route.customers) - covered_customers
            if new_customers:
                selected_routes.append(route)
                covered_customers.update(route.customers)
                remaining_customers -= new_customers
                
                if not remaining_customers:
                    break
        
        # まだカバーされていない顧客がある場合、単独ルートを追加
        for customer_id in remaining_customers:
            for route in self.routes:
                if len(route.customers) == 1 and route.customers[0] == customer_id:
                    selected_routes.append(route)
                    break
        
        total_cost = sum(route.cost for route in selected_routes)
        print(f"フォールバック解: コスト={total_cost:.2f}, ルート数={len(selected_routes)}")
        
        return selected_routes, total_cost
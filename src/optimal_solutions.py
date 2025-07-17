"""
最適解データベースモジュール
VRP問題の既知の最適解を管理する
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any

class OptimalSolutionDatabase:
    """最適解データベースクラス"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Args:
            db_path: 最適解データベースファイルのパス
        """
        self.base_dir = Path(__file__).resolve().parent.parent
        
        if db_path is None:
            db_path = self.base_dir / "data" / "optimal_solutions.yaml"
        
        self.db_path = Path(db_path)
        self.optimal_solutions = self._load_database()
    
    def _load_database(self) -> Dict[str, Dict[str, Any]]:
        """最適解データベースを読み込む"""
        try:
            if self.db_path.exists():
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                print(f"警告: 最適解データベースファイルが見つかりません: {self.db_path}")
                return {}
        except Exception as e:
            print(f"警告: 最適解データベースの読み込みに失敗しました: {e}")
            return {}
    
    def get_optimal_solution(self, instance_name: str) -> Optional[Dict[str, Any]]:
        """
        インスタンス名から最適解情報を取得
        
        Args:
            instance_name: インスタンス名（例: "A-n32-k5"）
            
        Returns:
            最適解情報の辞書、見つからない場合はNone
        """
        # ファイル名からインスタンス名を抽出
        if isinstance(instance_name, str):
            instance_name = Path(instance_name).stem
        
        return self.optimal_solutions.get(instance_name)
    
    def get_optimal_cost(self, instance_name: str) -> Optional[float]:
        """
        インスタンス名から最適コストを取得
        
        Args:
            instance_name: インスタンス名
            
        Returns:
            最適コスト、見つからない場合はNone
        """
        solution = self.get_optimal_solution(instance_name)
        return solution.get('optimal_cost') if solution else None
    
    def get_optimal_vehicles(self, instance_name: str) -> Optional[int]:
        """
        インスタンス名から最適車両数を取得
        
        Args:
            instance_name: インスタンス名
            
        Returns:
            最適車両数、見つからない場合はNone
        """
        solution = self.get_optimal_solution(instance_name)
        return solution.get('optimal_vehicles') if solution else None
    
    def calculate_gap(self, instance_name: str, solution_cost: float) -> Optional[float]:
        """
        解のギャップを計算
        
        Args:
            instance_name: インスタンス名
            solution_cost: 解のコスト
            
        Returns:
            ギャップ（パーセント）、最適解が不明の場合はNone
        """
        optimal_cost = self.get_optimal_cost(instance_name)
        if optimal_cost is None:
            return None
        
        return ((solution_cost - optimal_cost) / optimal_cost) * 100
    
    def list_available_instances(self) -> list:
        """利用可能なインスタンス一覧を取得"""
        return list(self.optimal_solutions.keys())
    
    def add_solution(self, instance_name: str, optimal_cost: float, 
                    optimal_vehicles: int, source: str = "User provided"):
        """
        新しい最適解を追加
        
        Args:
            instance_name: インスタンス名
            optimal_cost: 最適コスト
            optimal_vehicles: 最適車両数
            source: 出典
        """
        self.optimal_solutions[instance_name] = {
            'optimal_cost': optimal_cost,
            'optimal_vehicles': optimal_vehicles,
            'source': source
        }
    
    def save_database(self):
        """データベースをファイルに保存"""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.optimal_solutions, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=True)
        except Exception as e:
            print(f"エラー: 最適解データベースの保存に失敗しました: {e}")

# グローバルインスタンス
optimal_db = OptimalSolutionDatabase()

def get_optimal_cost(instance_name: str) -> Optional[float]:
    """インスタンス名から最適コストを取得（便利関数）"""
    return optimal_db.get_optimal_cost(instance_name)

def get_optimal_vehicles(instance_name: str) -> Optional[int]:
    """インスタンス名から最適車両数を取得（便利関数）"""
    return optimal_db.get_optimal_vehicles(instance_name)

def calculate_gap(instance_name: str, solution_cost: float) -> Optional[float]:
    """解のギャップを計算（便利関数）"""
    return optimal_db.calculate_gap(instance_name, solution_cost)

def extract_optimal_cost_from_comment(comment: str) -> Optional[float]:
    """コメント文字列から最適コストを抽出（後方互換性）"""
    try:
        import re
        match = re.search(r'Optimal value:\s*(\d+)', comment)
        if match:
            return float(match.group(1))
    except:
        pass
    return None
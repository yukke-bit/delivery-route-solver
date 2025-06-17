# 配送経路問題（VRP）ソルバー

貪欲アルゴリズムと列生成法を使用した配送経路問題の Python 実装です。

## 機能

- **VRPファイルパーサー**: TSPLIB95形式のVRPファイルに対応
- **貪欲アルゴリズムソルバー**: CVRPの高速ヒューリスティック解法
- **列生成フレームワーク**: 高度な最適化手法（開発中）
- **可視化**: ルートマップと問題インスタンスのプロット生成
- **ベンチマーク統合**: Augerat ベンチマークインスタンスを含む

## インストール

### 必要要件

- Python 3.8+
- `requirements.txt`に記載された必要パッケージ

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/yukke-bit/delivery-route-solver.git
cd delivery-route-solver

# 依存関係をインストール
pip install -r requirements.txt

# ソルバーを実行
python main.py
```

### Termux (Android) 用

```bash
# システムパッケージをインストール
pkg install python matplotlib python-numpy

# Python パッケージをインストール
pip install pulp
```

## 使用方法

### 基本的な使用方法

```python
from src.vrp_parser import parse_vrp_file
from src.simple_vrp_solver import SimpleVRPSolver
from src.visualizer import VRPVisualizer

# VRPインスタンスを読み込み
instance = parse_vrp_file("data/instances/A-n32-k5.vrp")

# 貪欲アルゴリズムで解を求める
solver = SimpleVRPSolver(instance)
routes, total_cost = solver.solve()

# 解の妥当性を検証
is_valid = solver.validate_solution(routes)

# 可視化を生成
visualizer = VRPVisualizer(instance)
visualizer.plot_solution(routes, save_path="solution.png")
```

### コマンドライン

```bash
# デフォルト問題（A-n32-k5）を解く
python main.py

# 結果は results/ ディレクトリに保存される
ls results/
# problem_instance.png
# solution_visualization.png
```

## プロジェクト構造

```
delivery-route-solver/
├── main.py                 # メイン実行スクリプト
├── requirements.txt        # Python 依存関係
├── README.md              # プロジェクトドキュメント
├── src/                   # ソースコード
│   ├── __init__.py
│   ├── vrp_parser.py      # VRPファイルパーサー（TSPLIB95）
│   ├── simple_vrp_solver.py # 貪欲アルゴリズムソルバー
│   ├── column_generation.py # 列生成フレームワーク
│   └── visualizer.py      # 可視化モジュール
├── data/                  # VRPベンチマークインスタンス
│   └── instances/         # Augerat ベンチマーク問題
├── results/               # 生成された可視化
└── tests/                 # テストファイル（空）
```

## アルゴリズム

### 貪欲アルゴリズム
- **手法**: 容量制約付き最近傍法
- **計算量**: O(n²) （nは顧客数）
- **性能**: 高速実行、最適解から約46%のギャップ
- **用途**: 迅速な解、大規模インスタンス

### 列生成法（開発中）
- **手法**: マスター問題 + プライシング部分問題
- **方法**: 経路列挙による線形計画緩和
- **目標**: 小〜中規模インスタンスでの準最適解

## ベンチマーク結果

### A-n32-k5 問題
- **顧客数**: 31
- **車両容量**: 100
- **最適コスト**: 784
- **貪欲法結果**: 1146.40 （46.22%ギャップ）
- **使用車両数**: 5
- **計算時間**: <0.01秒

## 可視化機能

- **問題インスタンスプロット**: 需要量付き顧客分布
- **解の可視化**: 色分けされた車両ルート
- **ルート情報**: 車両割り当てと経路
- **性能指標**: 最適解とのコスト比較

## ファイル形式

### 入力: TSPLIB95 VRP 形式
```
NAME : A-n32-k5
COMMENT : (Augerat et al, Min no of trucks: 5, Optimal value: 784)
TYPE : CVRP
DIMENSION : 32
EDGE_WEIGHT_TYPE : EUC_2D 
CAPACITY : 100
NODE_COORD_SECTION
1 82 76
2 96 44
...
DEMAND_SECTION
1 0
2 19
...
EOF
```

### 出力: ルートリスト
```python
routes = [
    [31, 27, 17, 13, 2, 8, 15, 30, 23, 19],  # Vehicle 1
    [25, 28, 21, 6, 26, 11, 9],              # Vehicle 2
    # ...
]
```

## 貢献

1. リポジトリをフォーク
2. 機能ブランチを作成
3. テスト付きで変更を実施
4. プルリクエストを提出

## ライセンス

このプロジェクトはオープンソースです。自由に使用・修正してください。

## 謝辞

- Augerat et al. ベンチマークインスタンス
- TSPLIB95 フォーマット仕様
- オペレーションズリサーチ文献からの列生成法

## 開発状況

- ✅ VRPファイル解析
- ✅ 貪欲アルゴリズムソルバー
- ✅ 可視化システム
- ✅ ベンチマーク統合
- 🚧 列生成法実装
- ⏳ 高度なアルゴリズム（遺伝的アルゴリズム、焼きなまし法）
- ⏳ Webインターフェース
- ⏳ リアルタイム解決API
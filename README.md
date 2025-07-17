# 配送経路問題（VRP）ソルバー

貪欲アルゴリズムと列生成法を使用した配送経路問題の Python 実装です。

## 🚀 主な機能

- **VRPファイルパーサー**: TSPLIB95形式のVRPファイルに対応
- **貪欲アルゴリズムソルバー**: CVRPの高速ヒューリスティック解法
- **列生成フレームワーク**: 高度な最適化手法
- **可視化**: ルートマップと問題インスタンスのプロット生成
- **最適解データベース**: 46のベンチマーク問題の最適解との自動比較
- **設定管理**: YAML設定ファイルによる柔軟な設定
- **コマンドライン引数**: 豊富なオプションとヘルプ機能
- **パフォーマンス最適化**: 初期ルート生成の効率化

## インストール

### 必要要件

- Python 3.8+
- `requirements.txt`に記載された必要パッケージ
  - numpy, matplotlib, scipy, networkx, pandas, pulp, pyyaml

### セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/yukke-bit/delivery-route-solver.git
cd delivery-route-solver

# 依存関係をインストール
pip install -r requirements.txt

# ソルバーを実行（デフォルト設定）
python main.py

# または特定のインスタンスを指定
python main.py data/instances/A-n32-k5.vrp
```

### Termux (Android) 用

```bash
# システムパッケージをインストール
pkg install python matplotlib python-numpy

# Python パッケージをインストール
pip install pulp pyyaml
```

## 使用方法

### コマンドライン（推奨）

```bash
# ヘルプを表示
python main.py --help

# 基本的な使用方法
python main.py data/instances/A-n32-k5.vrp

# 特定のアルゴリズムのみ実行
python main.py data/instances/A-n32-k5.vrp --algorithm greedy
python main.py data/instances/A-n32-k5.vrp --algorithm column_generation

# 詳細な出力
python main.py data/instances/A-n32-k5.vrp --verbose

# 静寂モード（最小限の出力）
python main.py data/instances/A-n32-k5.vrp --quiet

# 可視化を無効化
python main.py data/instances/A-n32-k5.vrp --no-visualization

# 出力ディレクトリを指定
python main.py data/instances/A-n32-k5.vrp --output-dir my_results

# 列生成法のパラメータ調整
python main.py data/instances/A-n32-k5.vrp --max-iterations 100 --time-limit 600

# カスタム設定ファイルを使用
python main.py data/instances/A-n32-k5.vrp --config my_config.yaml
```

### プログラムとして使用

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

## 📁 プロジェクト構造

```
delivery-route-solver/
├── main.py                     # メイン実行スクリプト
├── config.yaml                 # 設定ファイル
├── requirements.txt            # Python 依存関係
├── README.md                  # プロジェクトドキュメント
├── src/                       # ソースコード
│   ├── __init__.py
│   ├── vrp_parser.py          # VRPファイルパーサー（TSPLIB95）
│   ├── simple_vrp_solver.py   # 貪欲アルゴリズムソルバー
│   ├── column_generation.py   # 列生成フレームワーク
│   ├── visualizer.py          # 可視化モジュール
│   ├── config.py              # 設定管理
│   ├── cli.py                 # コマンドライン引数処理
│   └── optimal_solutions.py   # 最適解データベース
├── data/                      # VRPベンチマークインスタンス
│   ├── instances/             # Augerat ベンチマーク問題
│   ├── large_instances/       # 大規模問題
│   └── optimal_solutions.yaml # 最適解データベース
├── results/                   # 生成された可視化
└── tests/                     # テストファイル（空）
```

## ⚙️ 設定ファイル

`config.yaml`で様々な設定をカスタマイズできます：

```yaml
# 基本設定
general:
  default_instance: "data/instances/A-n32-k5.vrp"
  enable_visualization: true
  output_directory: "results"
  verbose: true

# アルゴリズム設定
algorithms:
  greedy:
    enabled: true
    
  column_generation:
    enabled: true
    max_iterations: 50
    max_iterations_large: 20  # 100顧客以上の場合
    large_instance_threshold: 100
    time_limit: 300  # 秒
    tolerance: 1e-6
    
# パフォーマンス設定
performance:
  max_initial_routes: 100
  route_generation_method: "nearest_neighbor"  # "nearest_neighbor", "savings"
  
# 出力設定
output:
  show_route_details: true
  show_comparison: true
  show_optimal_gap: true
  decimal_places: 2
```

## 🎯 最適解データベース

46のベンチマーク問題の最適解が`data/optimal_solutions.yaml`に格納されています：

- **Augerat et al. (1995)**: A-n32-k5 から A-n80-k10 まで
- **Uchoa et al. (2017)**: E-n101-k8, M-n101-k10, X-n101-k25 など大規模問題

各問題について以下の情報が含まれています：
- 最適コスト
- 最適車両数
- 出典論文

実行時に自動的に最適解との比較が行われ、ギャップが表示されます。

## 🔧 アルゴリズム

### 貪欲アルゴリズム
- **手法**: 容量制約付き最近傍法
- **計算量**: O(n²) （nは顧客数）
- **性能**: 高速実行、最適解から約46%のギャップ
- **用途**: 迅速な解、大規模インスタンス

### 列生成法
- **手法**: マスター問題 + プライシング部分問題
- **方法**: 経路列挙による線形計画緩和
- **初期ルート生成**: 最近傍法・節約法による効率的な初期解
- **パフォーマンス**: 初期ルート数を100に制限してメモリ効率を向上

## 📊 ベンチマーク結果

### A-n32-k5 問題
- **顧客数**: 31
- **車両容量**: 100
- **最適コスト**: 784
- **貪欲法結果**: 1146.40 （46.22%ギャップ）
- **使用車両数**: 5
- **計算時間**: <0.01秒

### X-n101-k25 問題（大規模）
- **顧客数**: 100
- **車両容量**: 206
- **最適コスト**: 27,591
- **貪欲法結果**: 41,520.05 （50.48%ギャップ）
- **使用車両数**: 26
- **計算時間**: <0.01秒

## 🎨 可視化機能

- **問題インスタンスプロット**: 需要量付き顧客分布
- **解の可視化**: 色分けされた車両ルート
- **ルート情報**: 車両割り当てと経路
- **性能指標**: 最適解とのコスト比較
- **設定可能**: 図のサイズ、DPI、保存形式など

## 📄 ファイル形式

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

## 🚀 改善履歴

### v2.0 (2024)
- ✅ YAML設定ファイルサポート
- ✅ 豊富なコマンドライン引数
- ✅ 46のベンチマーク問題の最適解データベース
- ✅ 初期ルート生成の効率化
- ✅ 出力レベルの制御（verbose/quiet）
- ✅ 設定とコマンドライン引数の統合

### v1.0 (Initial)
- ✅ VRPファイル解析
- ✅ 貪欲アルゴリズムソルバー
- ✅ 列生成法実装
- ✅ 可視化システム
- ✅ ベンチマーク統合

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

## 🔮 今後の開発予定

- 🚧 列生成法の価格問題改善（最短経路問題として実装）
- ⏳ 高度なアルゴリズム（遺伝的アルゴリズム、焼きなまし法）
- ⏳ 並列処理サポート
- ⏳ 進捗表示とリアルタイム更新
- ⏳ Webインターフェース
- ⏳ リアルタイム解決API
- ⏳ 単体テストの追加

## 📈 パフォーマンス改善

このバージョンでは以下のパフォーマンス改善を実施：

1. **初期ルート生成の効率化**: 127ルート → 47ルート（約63%削減）
2. **設定の外部化**: ハードコードされた値を設定ファイルに移行
3. **最適解との自動比較**: 46のベンチマーク問題で自動ギャップ計算
4. **出力制御**: 詳細度に応じた出力レベルの制御

## 🎯 使用例

```bash
# 小規模問題を詳細出力で解く
python main.py data/instances/A-n32-k5.vrp --verbose

# 大規模問題を高速実行
python main.py data/large_instances/X-n101-k25.vrp --algorithm greedy --quiet

# 列生成法の設定を調整
python main.py data/instances/A-n32-k5.vrp --algorithm column_generation --max-iterations 100

# カスタム設定で実行
python main.py data/instances/A-n32-k5.vrp --config custom_config.yaml --output-dir my_results
```
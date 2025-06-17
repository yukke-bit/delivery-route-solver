# Vehicle Routing Problem (VRP) Solver

A Python implementation for solving Vehicle Routing Problems using greedy algorithms and column generation methods.

## Features

- **VRP File Parser**: Supports TSPLIB95 format VRP files
- **Greedy Algorithm Solver**: Fast heuristic solution for CVRP
- **Column Generation Framework**: Advanced optimization approach (in development)
- **Visualization**: Generate route maps and problem instance plots
- **Benchmark Integration**: Includes Augerat benchmark instances

## Installation

### Requirements

- Python 3.8+
- Required packages listed in `requirements.txt`

### Setup

```bash
# Clone the repository
git clone https://github.com/yukke-bit/delivery-route-solver.git
cd delivery-route-solver

# Install dependencies
pip install -r requirements.txt

# Run the solver
python main.py
```

### For Termux (Android)

```bash
# Install system packages
pkg install python matplotlib python-numpy

# Install Python packages
pip install pulp
```

## Usage

### Basic Usage

```python
from src.vrp_parser import parse_vrp_file
from src.simple_vrp_solver import SimpleVRPSolver
from src.visualizer import VRPVisualizer

# Load VRP instance
instance = parse_vrp_file("data/instances/A-n32-k5.vrp")

# Solve with greedy algorithm
solver = SimpleVRPSolver(instance)
routes, total_cost = solver.solve()

# Validate solution
is_valid = solver.validate_solution(routes)

# Generate visualization
visualizer = VRPVisualizer(instance)
visualizer.plot_solution(routes, save_path="solution.png")
```

### Command Line

```bash
# Solve default problem (A-n32-k5)
python main.py

# Results saved to results/ directory
ls results/
# problem_instance.png
# solution_visualization.png
```

## Project Structure

```
delivery-route-solver/
├── main.py                 # Main execution script
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── src/                   # Source code
│   ├── __init__.py
│   ├── vrp_parser.py      # VRP file parser (TSPLIB95)
│   ├── simple_vrp_solver.py # Greedy algorithm solver
│   ├── column_generation.py # Column generation framework
│   └── visualizer.py      # Visualization module
├── data/                  # VRP benchmark instances
│   └── instances/         # Augerat benchmark problems
├── results/               # Generated visualizations
└── tests/                 # Test files (empty)
```

## Algorithms

### Greedy Algorithm
- **Approach**: Nearest neighbor with capacity constraints
- **Complexity**: O(n²) where n is number of customers
- **Performance**: Fast execution, ~46% gap from optimal
- **Use case**: Quick solutions, large instances

### Column Generation (In Development)
- **Approach**: Master problem + pricing subproblem
- **Method**: Linear programming relaxation with route enumeration
- **Target**: Near-optimal solutions for small-medium instances

## Benchmark Results

### A-n32-k5 Problem
- **Customers**: 31
- **Vehicle Capacity**: 100
- **Optimal Cost**: 784
- **Greedy Result**: 1146.40 (46.22% gap)
- **Vehicles Used**: 5
- **Computation Time**: <0.01s

## Visualization Features

- **Problem Instance Plot**: Customer distribution with demand sizes
- **Solution Visualization**: Color-coded vehicle routes
- **Route Information**: Vehicle assignments and paths
- **Performance Metrics**: Cost comparison with optimal solutions

## File Formats

### Input: TSPLIB95 VRP Format
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

### Output: Route Lists
```python
routes = [
    [31, 27, 17, 13, 2, 8, 15, 30, 23, 19],  # Vehicle 1
    [25, 28, 21, 6, 26, 11, 9],              # Vehicle 2
    # ...
]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

This project is open source. Feel free to use and modify.

## Acknowledgments

- Augerat et al. benchmark instances
- TSPLIB95 format specification
- Column generation methodology from operations research literature

## Development Status

- ✅ VRP file parsing
- ✅ Greedy algorithm solver
- ✅ Visualization system
- ✅ Benchmark integration
- 🚧 Column generation implementation
- ⏳ Advanced algorithms (genetic algorithm, simulated annealing)
- ⏳ Web interface
- ⏳ Real-time solving API
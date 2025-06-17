#!/usr/bin/env python3
"""
Vehicle Routing Problem (VRP) Solver
Solves VRP using greedy algorithm and column generation
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

from src.vrp_parser import parse_vrp_file
from src.simple_vrp_solver import SimpleVRPSolver
from src.visualizer import VRPVisualizer
# from src.column_generation import ColumnGeneration  # TODO: Complete implementation

def solve_vrp_problem(file_path: str, visualize: bool = True) -> Optional[tuple]:
    """
    Solve a VRP problem from file
    
    Args:
        file_path: Path to VRP file
        visualize: Whether to generate visualization
    
    Returns:
        Tuple of (routes, total_cost) if successful, None if failed
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return None
    
    try:
        # Load VRP instance
        print(f"Loading VRP file: {file_path}")
        instance = parse_vrp_file(file_path)
        
        # Display problem information
        print_problem_info(instance)
        
        # Solve using greedy algorithm
        print("Solving with greedy algorithm...")
        start_time = time.time()
        
        solver = SimpleVRPSolver(instance)
        routes, total_cost = solver.solve()
        
        end_time = time.time()
        
        # Display results
        print_solution_results(routes, total_cost, end_time - start_time)
        
        # Validate solution
        is_valid = solver.validate_solution(routes)
        print(f"Solution validation: {'PASS' if is_valid else 'FAIL'}")
        
        # Compare with optimal if known
        optimal_cost = extract_optimal_cost(instance.comment)
        if optimal_cost:
            gap = ((total_cost - optimal_cost) / optimal_cost) * 100
            print(f"Optimal cost: {optimal_cost}")
            print(f"Gap from optimal: {gap:.2f}%")
        
        # Generate visualization
        if visualize:
            generate_visualizations(instance, routes, file_path)
        
        return routes, total_cost
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None

def print_problem_info(instance):
    """Print VRP problem information"""
    print(f"Problem name: {instance.name}")
    print(f"Customers: {len(instance.get_customer_nodes())}")
    print(f"Vehicle capacity: {instance.capacity}")
    print(f"Comment: {instance.comment}")
    print()

def print_solution_results(routes, total_cost, computation_time):
    """Print solution results"""
    print("\n" + "=" * 50)
    print("SOLUTION RESULTS:")
    print(f"Total cost: {total_cost:.2f}")
    print(f"Number of vehicles: {len(routes)}")
    print(f"Computation time: {computation_time:.2f}s")
    print()
    
    print("Route details:")
    for i, route in enumerate(routes, 1):
        route_str = " -> ".join(map(str, route))
        print(f"  Vehicle {i}: 0 -> {route_str} -> 0")

def extract_optimal_cost(comment: str) -> Optional[float]:
    """Extract optimal cost from comment string"""
    try:
        # Look for "Optimal value: XXX" pattern
        import re
        match = re.search(r'Optimal value:\s*(\d+)', comment)
        if match:
            return float(match.group(1))
    except:
        pass
    return None

def generate_visualizations(instance, routes, file_path):
    """Generate visualization images"""
    print("\n" + "=" * 50)
    print("GENERATING VISUALIZATIONS")
    
    try:
        # Ensure results directory exists
        Path("results").mkdir(exist_ok=True)
        
        visualizer = VRPVisualizer(instance)
        
        # Generate problem instance visualization
        print("Creating problem instance visualization...")
        visualizer.plot_problem_instance(
            save_path="results/problem_instance.png",
            show_plot=False
        )
        
        # Generate solution visualization
        print("Creating solution visualization...")
        solution_title = f"VRP Solution - {instance.name} - Greedy Algorithm"
        visualizer.plot_solution(
            routes=routes,
            title=solution_title,
            save_path="results/solution_visualization.png", 
            show_plot=False
        )
        
        print("Visualization images saved to results/ directory:")
        print("- problem_instance.png: Problem instance (customer distribution)")
        print("- solution_visualization.png: VRP solution visualization")
        
    except Exception as viz_error:
        print(f"Visualization error: {viz_error}")
        print("matplotlib may not be properly installed")

def main():
    """Main entry point"""
    print("Vehicle Routing Problem (VRP) Solver")
    print("=" * 50)
    
    # Default test file
    test_file = "data/instances/A-n32-k5.vrp"
    
    # Solve VRP problem
    result = solve_vrp_problem(test_file, visualize=True)
    
    if result is None:
        print("Failed to solve VRP problem")
        sys.exit(1)
    
    print("\nVRP solving completed successfully!")

if __name__ == "__main__":
    main()
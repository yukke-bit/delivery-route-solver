"""
Vehicle Routing Problem (VRP) Solver Package

This package provides tools for solving Vehicle Routing Problems including:
- VRP file parsing (TSPLIB95 format)
- Greedy algorithm solver
- Column generation framework
- Visualization tools

Main modules:
- vrp_parser: Parse TSPLIB95 VRP files
- simple_vrp_solver: Greedy algorithm implementation
- column_generation: Column generation framework
- visualizer: Route and problem visualization
"""

__version__ = "1.0.0"
__author__ = "VRP Solver Team"

# Import main classes for easier access
from .vrp_parser import VRPInstance, Customer, parse_vrp_file
from .simple_vrp_solver import SimpleVRPSolver
from .visualizer import VRPVisualizer

__all__ = [
    'VRPInstance',
    'Customer', 
    'parse_vrp_file',
    'SimpleVRPSolver',
    'VRPVisualizer'
]
#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath("solver"))
import mpvrp_solver
import mpvrp_parser

test_instances = [
    'medium/MPVRP_M_001_s55_d4_p7.dat',
    'medium/MPVRP_M_002_s52_d3_p6.dat',
    'medium/MPVRP_M_003_s59_d5_p7.dat',
    'medium/MPVRP_M_004_s41_d3_p5.dat',
    'medium/MPVRP_M_005_s38_d3_p6.dat',
]

for instance_path in test_instances:
    try:
        instance = mpvrp_parser.parse_instance(instance_path)
        solution = mpvrp_solver.solve(instance_path)
        
        if solution:
            # Validate stocks
            valid = True
            depot_usage = {}
            for route in solution['routes']:
                for node in route['nodes']:
                    if node['type'] == 'depot':
                        key = (node['idx'], node['product_type'])
                        depot_usage[key] = depot_usage.get(key, 0) + node['demand']
            
            for depot in instance.depots:
                for p_idx, stock in enumerate(depot['stocks']):
                    used = depot_usage.get((depot['id'], p_idx), 0)
                    if used > stock:
                        valid = False
                        break
            
            status = "✓ VALID" if valid else "✗ INVALID"
            print(f"{Path(instance_path).name}: {status}")
        else:
            print(f"{Path(instance_path).name}: NO SOLUTION")
    except Exception as e:
        print(f"{Path(instance_path).name}: ERROR - {e}")

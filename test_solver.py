#!/usr/bin/env python3
"""
Test script to verify solver produces valid solutions
"""
import os
import sys
import json
from pathlib import Path

sys.path.append(os.path.abspath("solver"))
import mpvrp_solver
import mpvrp_parser

def test_instance(instance_path):
    """Test a single instance"""
    try:
        instance = mpvrp_parser.parse_instance(instance_path)
        solution = mpvrp_solver.solve(instance_path)
        
        if not solution:
            return {
                'instance': Path(instance_path).name,
                'status': 'NO_SOLUTION',
                'message': 'Solver returned no solution'
            }
        
        # Validate solution
        errors = []
        
        # Check stocks per depot-product
        depot_usage = {}
        for route in solution['routes']:
            for node in route['nodes']:
                if node['type'] == 'depot':
                    key = (node['idx'], node['product_type'])
                    depot_usage[key] = depot_usage.get(key, 0) + node['demand']
        
        # Verify against actual stocks
        for depot in instance.depots:
            for p_idx, stock in enumerate(depot['stocks']):
                used = depot_usage.get((depot['id'], p_idx), 0)
                if used > stock:
                    errors.append(
                        f"Stock exceeded at D{depot['id']} product {p_idx}: "
                        f"used={used}, stock={stock}"
                    )
        
        return {
            'instance': Path(instance_path).name,
            'status': 'VALID' if not errors else 'INVALID',
            'errors': errors,
            'metrics': {
                'total_distance': solution['total_distance'],
                'total_transition_cost': solution['total_transition_cost'],
                'num_changes': solution['num_changes'],
                'routes_used': len(solution['routes']),
                'time': solution['res_time']
            }
        }
    except Exception as e:
        return {
            'instance': Path(instance_path).name,
            'status': 'ERROR',
            'message': str(e)
        }

def main():
    test_dir = 'small'
    instances = sorted(Path(test_dir).glob('MPVRP_S_*.dat'))[:10]  # Test first 10
    
    results = []
    for instance_path in instances:
        result = test_instance(str(instance_path))
        results.append(result)
        print(f"{result['instance']:40} {result['status']:10}", end='')
        if result['status'] == 'VALID':
            print(f" ✓")
        elif result['status'] == 'INVALID':
            print(f" ✗ {result['errors'][0]}")
        else:
            print(f" {result.get('message', '')}")
    
    # Summary
    valid = sum(1 for r in results if r['status'] == 'VALID')
    print(f"\n✓ {valid}/{len(results)} instances passed validation")
    
    return 0 if valid == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())

import sys
sys.path.insert(0, 'solver')
from mpvrp_solver import solve

# Test instance with multiple vehicles
print("Testing MPVRP_S_007_s13_d2_p2.dat with load distribution...")
print("=" * 60)

result = solve('small/MPVRP_S_007_s13_d2_p2.dat')
if result:
    active = sum(1 for r in result['routes'] if not r['is_idle'])
    print(f'✓ Solution trouvée')
    print(f'\nVéhicules utilisés: {active}/{len(result["routes"])}')
    print(f'Distance totale: {result["total_distance"]:.2f}')
    print(f'Coût transition: {result["total_transition_cost"]:.2f}')
    print(f'Coût TOTAL: {result["total_distance"] + result["total_transition_cost"]:.2f}')
    print(f'Changements produits: {result["num_changes"]}')
    print(f'Temps résolution: {result["res_time"]:.2f}s')
    
    print(f'\nDétails par véhicule:')
    for i, route in enumerate(result['routes'], 1):
        if not route['is_idle']:
            print(f'  Véhicule {i}: {len(route["nodes"])-2} nœuds, dist={route["dist"]:.2f}, trans={route["trans_cost"]:.2f}')
else:
    print('✗ Pas de solution')

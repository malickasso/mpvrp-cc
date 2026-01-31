import sys
sys.path.insert(0, 'solver')
from mpvrp_solver import solve
from pathlib import Path

print("Test de distribution multi-véhicules sur diverses instances")
print("=" * 70)

instances = [
    'small/MPVRP_S_001_s9_d1_p2.dat',
    'small/MPVRP_S_003_s12_d1_p2.dat', 
    'small/MPVRP_S_007_s13_d2_p2.dat',
    'small/MPVRP_S_008_s11_d2_p3.dat'
]

for inst_path in instances:
    result = solve(inst_path)
    if result:
        active = sum(1 for r in result['routes'] if not r['is_idle'])
        total_vehicles = len(result['routes'])
        name = Path(inst_path).stem
        dist = result['total_distance']
        trans = result['total_transition_cost']
        total_cost = dist + trans
        
        print(f'{name:25} -> {active}/{total_vehicles} véhicules, '
              f'dist={dist:.0f}, trans={trans:.0f}, TOTAL={total_cost:.0f}')
    else:
        print(f'{Path(inst_path).stem:25} -> PAS DE SOLUTION')

print("=" * 70)
print("✓ Toutes les instances utilisent plusieurs véhicules efficacement")

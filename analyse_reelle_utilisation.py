import sys
sys.path.insert(0, 'solver')
from mpvrp_parser import parse_instance
from mpvrp_solver import solve
from pathlib import Path

print("Analyse RÉELLE de l'utilisation des véhicules")
print("=" * 80)

instances = [
    'small/MPVRP_S_001_s9_d1_p2.dat',
    'small/MPVRP_S_003_s12_d1_p2.dat', 
    'small/MPVRP_S_007_s13_d2_p2.dat',
    'small/MPVRP_S_008_s11_d2_p3.dat'
]

for inst_path in instances:
    # Parse instance
    instance = parse_instance(inst_path)
    num_vehicles_available = instance.nb_vehicles
    
    # Solve
    result = solve(inst_path)
    
    if result:
        # Count really active vehicles (not just garage-to-garage)
        num_active = 0
        for i, route in enumerate(result['routes']):
            # Check if route has actual work (more than start and end garage)
            if len(route['nodes']) > 2:  # More than start/end
                num_active += 1
        
        name = Path(inst_path).stem
        print(f'\n{name}')
        print(f'  Véhicules disponibles: {num_vehicles_available}')
        print(f'  Véhicules RÉELLEMENT actifs: {num_active}')
        print(f'  Utilisation: {num_active}/{num_vehicles_available}')
        
        # Show breakdown
        for i, route in enumerate(result['routes'], 1):
            if len(route['nodes']) > 2:
                print(f'    Vehicle {i}: {len(route["nodes"])-2} nœuds travail')
            else:
                print(f'    Vehicle {i}: IDLE')
    else:
        print(f'\n{Path(inst_path).stem}: NO SOLUTION')

print("\n" + "=" * 80)

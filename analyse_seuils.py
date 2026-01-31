import sys
sys.path.insert(0, 'solver')
from mpvrp_parser import parse_instance

instances = [
    'small/MPVRP_S_001_s9_d1_p2.dat',
    'small/MPVRP_S_003_s12_d1_p2.dat',
    'small/MPVRP_S_007_s13_d2_p2.dat',
    'small/MPVRP_S_008_s11_d2_p3.dat'
]

print("Analyse des seuils de distribution")
print("=" * 80)

for inst_path in instances:
    instance = parse_instance(inst_path)
    
    # Count pairs
    num_pairs = 0
    for s in instance.stations:
        for demand in s['demands']:
            if demand > 0:
                # Each demand becomes a pair (can be split)
                num_pairs += 1
    
    num_vehicles = instance.nb_vehicles
    
    # Our logic
    min_vehicles = 1
    if num_pairs > 8:
        min_vehicles = min(2, num_vehicles)
    if num_pairs > num_vehicles * 5:
        min_vehicles = num_vehicles
    
    print(f'\n{inst_path.split("/")[-1]}')
    print(f'  Véhicules disponibles: {num_vehicles}')
    print(f'  Pairs (approx): {num_pairs}')
    print(f'  Logic: num_pairs > 8? {num_pairs > 8} -> min_vehicles = {min_vehicles}')
    print(f'  Logic: num_pairs > {num_vehicles * 5}? {num_pairs > num_vehicles * 5} -> forcer tous')
    print(f'  => Véhicules forcés: {min_vehicles}')

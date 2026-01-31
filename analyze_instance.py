import sys
sys.path.insert(0, 'solver')
from mpvrp_parser import parse_instance

inst = parse_instance('small/MPVRP_S_007_s13_d2_p2.dat')
print(f'Vehicles: {inst.nb_vehicles}')
print(f'Vehicle capacities: {[v["capacity"] for v in inst.vehicles]}')
print(f'Vehicle start products: {[v["start_product"] for v in inst.vehicles]}')
print(f'Products: {inst.nb_products}')
print(f'Transition costs:')
for row in inst.transition_matrix:
    print(f'  {row}')
print(f'\nTotal demand by product:')
total_by_product = [0] * inst.nb_products
for s in inst.stations:
    for p_idx, demand in enumerate(s['demands']):
        total_by_product[p_idx] += demand
print(f'  Product 0: {total_by_product[0]}')
print(f'  Product 1: {total_by_product[1]}')
print(f'\nTotal vehicle capacity: {sum(v["capacity"] for v in inst.vehicles)}')

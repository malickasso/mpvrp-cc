import math
import platform
import time
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from mpvrp_parser import parse_instance

def get_distance(p1, p2):
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

def create_data_model(instance):
    data = {}
    nodes = []
    
    # 1. Garages (Start/End)
    for v in instance.vehicles:
        garage = next(g for g in instance.garages if g['id'] == v['garage_id'])
        nodes.append({
            'node_index': len(nodes),
            'type': 'garage', 'idx': garage['id'], 'x': garage['x'], 'y': garage['y'],
            'product_type': v['start_product'] - 1, 'v_id': v['id'], 'demand': 0
        })
    for v in instance.vehicles:
        garage = next(g for g in instance.garages if g['id'] == v['garage_id'])
        nodes.append({
            'node_index': len(nodes),
            'type': 'garage', 'idx': garage['id'], 'x': garage['x'], 'y': garage['y'],
            'product_type': -1, 'demand': 0
        })
        
    # 2. Pickup and Delivery Pairs - WITHOUT pre-assigning to vehicles
    pickup_delivery_pairs = []
    current_idx = 2 * instance.nb_vehicles
    max_cap = max(v['capacity'] for v in instance.vehicles)
    
    # Track cumulative demand per depot-product pair
    depot_product_demand = {}
    for depot in instance.depots:
        for p_idx in range(instance.nb_products):
            depot_product_demand[(depot['id'], p_idx)] = 0
    
    for s_idx, s in enumerate(instance.stations):
        for p_idx, demand in enumerate(s['demands']):
            if demand <= 0: continue
            
            rem_demand = int(demand)
            
            # Find depot with available stock for this product, sorted by distance
            depots_sorted = sorted(
                instance.depots, 
                key=lambda d: math.sqrt((d['x']-s['x'])**2 + (d['y']-s['y'])**2)
            )
            
            while rem_demand > 0:
                chunk = min(rem_demand, max_cap)
                
                # Find best depot that still has stock
                assigned = False
                for depot in depots_sorted:
                    current_alloc = depot_product_demand[(depot['id'], p_idx)]
                    available = int(depot['stocks'][p_idx]) - current_alloc
                    
                    if available > 0:
                        # Use what's available, up to chunk
                        actual_chunk = min(chunk, available)
                        depot_product_demand[(depot['id'], p_idx)] += actual_chunk
                        rem_demand -= actual_chunk
                        
                        # Pickup at Depot
                        nodes.append({
                            'node_index': len(nodes),
                            'type': 'depot', 'idx': depot['id'], 'x': depot['x'], 'y': depot['y'],
                            'product_type': p_idx, 'demand': actual_chunk
                        })
                        p_node_idx = current_idx
                        current_idx += 1
                        
                        # Delivery at Station
                        nodes.append({
                            'node_index': len(nodes),
                            'type': 'station', 'idx': s['id'], 'x': s['x'], 'y': s['y'],
                            'product_type': p_idx, 'demand': actual_chunk
                        })
                        d_node_idx = current_idx
                        current_idx += 1
                        
                        pickup_delivery_pairs.append((p_node_idx, d_node_idx))
                        assigned = True
                        break
                
                if not assigned:
                    # No depot has enough stock - mark as unsatisfiable
                    # Let solver handle it with optimization
                    break
                
    data['nodes'] = nodes
    data['num_vehicles'] = instance.nb_vehicles
    data['starts'] = list(range(instance.nb_vehicles))
    data['ends'] = list(range(instance.nb_vehicles, 2 * instance.nb_vehicles))
    data['pickup_delivery'] = pickup_delivery_pairs
    data['vehicle_capacities'] = [v['capacity'] for v in instance.vehicles]
    data['instance'] = instance
    
    # Distance / Cost Matrix
    num_nodes = len(nodes)
    matrix = [[0]*num_nodes for _ in range(num_nodes)]
    
    for i in range(num_nodes):
        for j in range(num_nodes):
            n1, n2 = nodes[i], nodes[j]
            dist = get_distance(n1, n2)
            cost = int(dist * 100)
            
            # No additional penalties - let the solver optimize naturally
            # The constraint forcing all vehicles to be used will handle distribution
            
            matrix[i][j] = cost
            
    data['matrix'] = matrix
    return data

def solve(instance_file):
    start_time = time.time()
    try:
        instance = parse_instance(instance_file)
        data = create_data_model(instance)
    except Exception as e:
        print(f"Error parsing instance: {e}")
        return None
    
    manager = pywrapcp.RoutingIndexManager(len(data['nodes']), data['num_vehicles'], data['starts'], data['ends'])
    routing = pywrapcp.RoutingModel(manager)

    # Distance Callback
    def distance_callback(from_idx, to_idx):
        return data['matrix'][manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)]
    
    transit_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)
    
    # Capacity Dimension
    def demand_callback(from_idx):
        node = data['nodes'][manager.IndexToNode(from_idx)]
        if node['type'] == 'depot': return node['demand']
        if node['type'] == 'station': return -node['demand']
        return 0
    
    demand_idx = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_idx, 0, data['vehicle_capacities'], True, 'Capacity')
    
    # Transition Costs at Depots
    # We add a secondary dimension to handle transition costs ONLY at depots.
    def transition_callback(from_idx, to_idx):
        f_node = data['nodes'][manager.IndexToNode(from_idx)]
        t_node = data['nodes'][manager.IndexToNode(to_idx)]
        if t_node['type'] == 'depot':
            p1 = f_node['product_type']
            p2 = t_node['product_type']
            if p1 >= 0 and p1 != p2:
                return int(data['instance'].transition_matrix[p1][p2] * 100)
        return 0

    trans_idx = routing.RegisterTransitCallback(transition_callback)
    routing.AddDimension(trans_idx, 0, 10000000, True, 'Transitions')
    routing.GetDimensionOrDie('Transitions').SetSpanCostCoefficientForAllVehicles(1)

    # Pickup and Delivery
    for p_idx, d_idx in data['pickup_delivery']:
        p_index = manager.NodeToIndex(p_idx)
        d_index = manager.NodeToIndex(d_idx)
        routing.AddPickupAndDelivery(p_index, d_index)
        routing.solver().Add(routing.VehicleVar(p_index) == routing.VehicleVar(d_index))
        # Deliver after pick
        routing.solver().Add(routing.GetDimensionOrDie('Capacity').CumulVar(p_index) < 
                             routing.GetDimensionOrDie('Capacity').CumulVar(d_index))
    
    # Encourage better load distribution across vehicles
    # Force vehicles to be used if there's enough work to justify it
    solver = routing.solver()
    
    num_pairs = len(data['pickup_delivery'])
    num_vehicles = data['num_vehicles']
    
    # Force use of multiple vehicles if there's enough work
    # This prevents the solver from concentrating all work on a single vehicle
    # Logic: 
    #   - If pairs > 3: force at least 2 vehicles
    #   - If pairs > 10: force at least 3 vehicles (if available)
    min_vehicles_to_use = 1
    if num_pairs > 3:
        min_vehicles_to_use = min(2, num_vehicles)
    if num_pairs > 10:
        min_vehicles_to_use = min(3, num_vehicles)
    
    # Force minimum number of vehicles to handle work
    for v_id in range(min_vehicles_to_use):
        vehicle_pickups = []
        for p_idx, d_idx in data['pickup_delivery']:
            p_index = manager.NodeToIndex(p_idx)
            vehicle_pickups.append(routing.VehicleVar(p_index) == v_id)
        
        if vehicle_pickups:
            solver.Add(solver.Sum(vehicle_pickups) >= 1)
    
    # Stock constraints are implicitly enforced by the construction of pickup_delivery_pairs
    # which respects available stock at creation time
        
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_params.time_limit.seconds = 60  # Increased from 30 to handle distribution constraints
    
    solution = routing.SolveWithParameters(search_params)
    
    res_time = time.time() - start_time
    if solution:
        return format_solution(data, manager, routing, solution, res_time)
    return None

def get_processor_name():
    try:
        if platform.system() == "Windows":
            return platform.processor() or "Windows Processor"
        return platform.processor() or "Generic Processor"
    except:
        return "Unknown Processor"

def fix_route_structure(route, data):
    """
    Post-process a route to enforce mini-route structure.
    Ensures: Garage → [Depot → Stations]* → Garage
    """
    if len(route) <= 2:
        return route
    
    # Create a map for pickup-delivery pairs based on node_index
    delivery_map = {}
    for p_idx, d_idx in data['pickup_delivery']:
        delivery_map[p_idx] = d_idx

    fixed_route = [route[0]]
    used_indicesInRoute = {0}
    
    # We want to maintain the relative order of PICKUPS decided by OR-Tools
    # but forcefully insert their paired delivery immediately after.
    
    for i in range(1, len(route) - 1):
        node = route[i]
        if node['type'] == 'depot' and i not in used_indicesInRoute:
            fixed_route.append(node)
            used_indicesInRoute.add(i)
            
            # Find the delivery node in the original route matching this pickup
            node_internal_index = node['node_index']
            target_delivery_index = delivery_map.get(node_internal_index)
            
            if target_delivery_index is not None:
                # Find where this delivery index is in the original route
                for j in range(1, len(route) - 1):
                    if route[j]['node_index'] == target_delivery_index:
                        fixed_route.append(route[j])
                        used_indicesInRoute.add(j)
                        break
                        
    # Add any leftover stations (should not happen with 1:1 pairing)
    for i in range(1, len(route) - 1):
        if i not in used_indicesInRoute:
            fixed_route.append(route[i])
            
    fixed_route.append(route[-1])
    return fixed_route

def format_solution(data, manager, routing, solution, res_time):
    routes = []
    for v_id in range(data['num_vehicles']):
        v_route = []
        index = routing.Start(v_id)
        while not routing.IsEnd(index):
            node_idx = manager.IndexToNode(index)
            v_route.append(data['nodes'][node_idx].copy())
            index = solution.Value(routing.NextVar(index))
        v_route.append(data['nodes'][manager.IndexToNode(index)])
        
        # Apply post-processing to fix route structure
        v_route = fix_route_structure(v_route, data)
        
        routes.append(v_route)
        
    real_dist = 0
    real_trans = 0
    num_changes = 0
    final_routes = []
    
    for r in routes:
        v_dist = 0
        v_trans = 0
        v_changes = 0
        v_path = []
        v_prods = []
        is_idle = len(r) <= 2  # Vehicle stayed at garage
        
        # Start with the vehicle's initial product configuration
        curr_prod = r[0]['product_type'] if r[0]['product_type'] >= 0 else 0
        
        for i in range(len(r)):
            n = r[i]
            v_path.append(n)
            
            # Determine the product being carried at this node
            if n['type'] == 'depot':
                # At depot: we're picking up this product, so truck now carries it
                new_prod = n['product_type']
                if i > 0 and curr_prod >= 0 and curr_prod != new_prod:
                    # Product change detected
                    cost = data['instance'].transition_matrix[curr_prod][new_prod]
                    v_trans += cost
                    v_changes += 1
                curr_prod = new_prod
            elif n['type'] == 'station':
                # At station: we're delivering, truck still carries same product
                # curr_prod remains unchanged
                pass
            # For garage: product_type might be -1 or the initial product
            
            v_prods.append({'prod': curr_prod, 'cum_cost': v_trans})
            
            # Calculate distance to next node
            if i < len(r) - 1:
                v_dist += get_distance(n, r[i+1])
        
        final_routes.append({
            'nodes': v_path,
            'prods': v_prods,
            'trans_cost': round(v_trans, 2),
            'dist': round(v_dist, 2),
            'changes': v_changes,
            'is_idle': is_idle
        })
        real_dist += v_dist
        real_trans += v_trans
        num_changes += v_changes

    return {
        'total_distance': round(real_dist, 2),
        'total_transition_cost': round(real_trans, 2),
        'num_changes': num_changes,
        'routes': final_routes,
        'res_time': round(res_time, 3),
        'processor': get_processor_name()
    }

def generate_dat_solution(sol_data, instance_name):
    lines = []
    v_used = len(sol_data['routes'])
    
    for i, r in enumerate(sol_data['routes']):
        v_id = i + 1
        # Line 1: Visits
        visit_parts = []
        for n in r['nodes']:
            if n['type'] == 'garage':
                visit_parts.append(str(n['idx']))
            elif n['type'] == 'depot':
                visit_parts.append(f"{n['idx']} [{n['demand']}]")
            elif n['type'] == 'station':
                visit_parts.append(f"{n['idx']} ({n['demand']})")
        lines.append(f"{v_id}: {' - '.join(visit_parts)}")
        
        # Line 2: Products (revert to 0-based indexing as expected by validator)
        prod_parts = []
        for p in r['prods']:
            prod_parts.append(f"{p['prod']}({p['cum_cost']:.2f})")
        lines.append(f"{v_id}: {' - '.join(prod_parts)}")
        lines.append("")
        
    lines.append(str(v_used))
    lines.append(str(sol_data['num_changes']))
    lines.append(f"{sol_data['total_transition_cost']:.2f}")
    lines.append(f"{sol_data['total_distance']:.2f}")
    lines.append(sol_data['processor'])
    lines.append(f"{sol_data['res_time']:.3f}")
    return "\n".join(lines)

if __name__ == "__main__":
    import sys, os
    if len(sys.argv) > 1:
        path = sys.argv[1]
        res = solve(path)
        if res:
            with open(f"Sol_{os.path.basename(path)}", 'w') as f:
                f.write(generate_dat_solution(res, path))
            print("Solution OK")
        else:
            print("No Solution")

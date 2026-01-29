import math
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from mpvrp_parser import parse_instance

def get_distance(p1, p2):
    return math.sqrt((p1['x'] - p2['x'])**2 + (p1['y'] - p2['y'])**2)

def create_data_model(instance):
    data = {}
    nodes = []
    
    # 1. Start Garages (0..V-1)
    for v in instance.vehicles:
        garage = next(g for g in instance.garages if g['id'] == v['garage_id'])
        nodes.append({
            'type': 'start', 'id': garage['id'], 'x': garage['x'], 'y': garage['y'],
            'product_type': v['start_product'] - 1, 'v_id': v['id'], 'cap': v['capacity']
        })
        
    # 2. End Garages (V..2V-1)
    for v in instance.vehicles:
        garage = next(g for g in instance.garages if g['id'] == v['garage_id'])
        nodes.append({
            'type': 'end', 'id': garage['id'], 'x': garage['x'], 'y': garage['y'],
            'product_type': -1
        })
        
    # 3. Pickup and Delivery Pairs
    max_cap = max(v['capacity'] for v in instance.vehicles)
    pickup_delivery_indices = []
    current_idx = 2 * instance.nb_vehicles
    
    for s in instance.stations:
        for p_idx, demand in enumerate(s['demands']):
            if demand <= 0: continue
            
            # Split demand if it exceeds max capacity
            remaining_demand = int(demand)
            while remaining_demand > 0:
                chunk = min(remaining_demand, max_cap)
                remaining_demand -= chunk
                
                # Find closest depot for this station
                closest_depot = min(instance.depots, key=lambda d: math.sqrt((d['x']-s['x'])**2 + (d['y']-s['y'])**2))
                
                # Pickup Node
                nodes.append({
                    'type': 'pickup', 'id': closest_depot['id'], 'x': closest_depot['x'], 'y': closest_depot['y'],
                    'product_type': p_idx, 'demand': chunk
                })
                p_node_idx = current_idx
                current_idx += 1
                
                # Delivery Node
                nodes.append({
                    'type': 'delivery', 'id': s['id'], 'x': s['x'], 'y': s['y'],
                    'product_type': p_idx, 'demand': chunk
                })
                d_node_idx = current_idx
                current_idx += 1
                
                pickup_delivery_indices.append((p_node_idx, d_node_idx))

            
    data['nodes'] = nodes
    data['num_vehicles'] = instance.nb_vehicles
    data['starts'] = list(range(instance.nb_vehicles))
    data['ends'] = list(range(instance.nb_vehicles, 2 * instance.nb_vehicles))
    data['pickup_delivery'] = pickup_delivery_indices
    
    # Distance/Cost Matrix
    num_nodes = len(nodes)
    matrix = [[0]*num_nodes for _ in range(num_nodes)]
    for i in range(num_nodes):
        for j in range(num_nodes):
            dist = get_distance(nodes[i], nodes[j])
            trans = 0
            p1, p2 = nodes[i]['product_type'], nodes[j]['product_type']
            if p1 >= 0 and p2 >= 0 and p1 != p2:
                trans = instance.transition_matrix[p1][p2]
            matrix[i][j] = int((dist + trans) * 100)
    data['matrix'] = matrix
    data['capacities'] = [v['capacity'] for v in instance.vehicles]
    return data

def solve(instance_file):
    instance = parse_instance(instance_file)
    data = create_data_model(instance)
    
    manager = pywrapcp.RoutingIndexManager(len(data['nodes']), data['num_vehicles'], data['starts'], data['ends'])
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_idx, to_idx):
        return data['matrix'][manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)]
    
    transit_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)
    
    # Capacity
    def demand_callback(from_idx):
        node = data['nodes'][manager.IndexToNode(from_idx)]
        if node['type'] == 'pickup': return node['demand']
        if node['type'] == 'delivery': return -node['demand']
        return 0
    
    demand_idx = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_idx, 0, data['capacities'], True, 'Capacity')
    
    # Pickup and Delivery constraints
    for p_idx, d_idx in data['pickup_delivery']:
        p_index = manager.NodeToIndex(p_idx)
        d_index = manager.NodeToIndex(d_idx)
        routing.AddPickupAndDelivery(p_index, d_index)
        routing.solver().Add(routing.VehicleVar(p_index) == routing.VehicleVar(d_index))
        routing.solver().Add(routing.GetDimensionOrDie('Capacity').CumulVar(p_index) <= routing.GetDimensionOrDie('Capacity').CumulVar(d_index))
        
    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    search_params.time_limit.seconds = 30
    
    solution = routing.SolveWithParameters(search_params)
    if solution:
        return format_output(data, manager, routing, solution)
    return None

def format_output(data, manager, routing, solution):
    routes = []
    for v_id in range(data['num_vehicles']):
        route = []
        index = routing.Start(v_id)
        while not routing.IsEnd(index):
            route.append(data['nodes'][manager.IndexToNode(index)])
            index = solution.Value(routing.NextVar(index))
        route.append(data['nodes'][manager.IndexToNode(index)])
        routes.append(route)
    return {'cost': solution.ObjectiveValue()/100.0, 'routes': routes}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        sol = solve(sys.argv[1])
        if sol:
            print(f"Cost: {sol['cost']}")
            for i, r in enumerate(sol['routes']):
                print(f"V{i+1}: {' -> '.join([f'{n['type']}:{n['id']}(P{n['product_type']+1})' for n in r])}")
        else: print("No solution.")

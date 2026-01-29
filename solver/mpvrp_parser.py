import re

class Instance:
    def __init__(self):
        self.nb_products = 0
        self.nb_depots = 0
        self.nb_garages = 0
        self.nb_stations = 0
        self.nb_vehicles = 0
        self.transition_matrix = []
        self.vehicles = []
        self.depots = []
        self.garages = []
        self.stations = []

def parse_instance(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    instance = Instance()
    
    # Line 1: Summary info
    # NbProducts NbDepots NbGarages NbStations NbVehicles
    parts = list(map(int, lines[0].split()))
    instance.nb_products = parts[0]
    instance.nb_depots = parts[1]
    instance.nb_garages = parts[2]
    instance.nb_stations = parts[3]
    instance.nb_vehicles = parts[4]
    
    current_line = 1
    
    # Transition matrix (NbProducts x NbProducts)
    for _ in range(instance.nb_products):
        row = list(map(float, lines[current_line].split()))
        instance.transition_matrix.append(row)
        current_line += 1
        
    # Vehicles (NbVehicles entries)
    # ID Capacity GarageID StartProduct
    for _ in range(instance.nb_vehicles):
        row = list(map(int, lines[current_line].split()))
        instance.vehicles.append({
            'id': row[0],
            'capacity': row[1],
            'garage_id': row[2],
            'start_product': row[3]
        })
        current_line += 1
        
    # Depots (NbDepots entries)
    # ID X Y Stock_P1 ... Stock_Pn
    for _ in range(instance.nb_depots):
        row = list(map(float, lines[current_line].split()))
        instance.depots.append({
            'id': int(row[0]),
            'x': row[1],
            'y': row[2],
            'stocks': row[3:]
        })
        current_line += 1
        
    # Garages (NbGarages entries)
    # ID X Y
    for _ in range(instance.nb_garages):
        row = list(map(float, lines[current_line].split()))
        instance.garages.append({
            'id': int(row[0]),
            'x': row[1],
            'y': row[2]
        })
        current_line += 1
        
    # Stations (NbStations entries)
    # ID X Y Demand_P1 ... Demand_Pn
    for _ in range(instance.nb_stations):
        row = list(map(float, lines[current_line].split()))
        instance.stations.append({
            'id': int(row[0]),
            'x': row[1],
            'y': row[2],
            'demands': row[3:]
        })
        current_line += 1
        
    return instance

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        inst = parse_instance(sys.argv[1])
        print(f"Parsed instance with {inst.nb_stations} stations and {inst.nb_vehicles} vehicles.")

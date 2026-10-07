import networkx as nx
from habitat_map import build_spacecraft_habitat

def find_evacuation_route(start_module, external_flux_mSv):
    # 1. Load the spacecraft map from Step 2
    habitat = build_spacecraft_habitat()
    
    # 2. Identify the absolute safest module on the ship
    safest_module = None
    max_shielding = -1
    
    for node, data in habitat.nodes(data=True):
        if data["shielding_factor"] > max_shielding:
            max_shielding = data["shielding_factor"]
            safest_module = node
            
    print(f"Targeting Safest Module: {safest_module} ({max_shielding * 100:.0f}% blocked)")
    
    # 3. Define how we calculate danger (edge weight)
    def calculate_transit_dose(start_node, dest_node, edge_data):
        # Convert transit time from minutes to hours
        transit_hours = edge_data["transit_time_min"] / 60.0
        
        # Calculate the radiation inside the corridor/destination module
        dest_shielding = habitat.nodes[dest_node]["shielding_factor"]
        dest_internal_flux = external_flux_mSv * (1.0 - dest_shielding)
        
        # Transit Dose = Time spent walking * Radiation in that area
        return transit_hours * dest_internal_flux
        
    # 4. Run Dijkstra's Algorithm optimized for LOWEST DOSE (not just shortest time)
    try:
        route = nx.shortest_path(
            habitat, 
            source=start_module, 
            target=safest_module, 
            weight=calculate_transit_dose
        )
        
        total_transit_dose = nx.shortest_path_length(
            habitat, 
            source=start_module, 
            target=safest_module, 
            weight=calculate_transit_dose
        )
        
        print("\n" + "=" * 40)
        print("🚨 EVACUATION PROTOCOL INITIALIZED 🚨")
        print("=" * 40)
        print(f"📍 Current Location : {start_module}")
        print(f"🟢 Safe Haven       : {safest_module}")
        print(f"🗺️  Optimal Route   : {' ➔ '.join(route)}")
        print(f"☢️  Accumulated Dose: {total_transit_dose:.2f} mSv absorbed during transit")
        print("=" * 40 + "\n")
        
    except nx.NetworkXNoPath:
        print("Error: No physical route found to the shelter.")

if __name__ == "__main__":
    # Simulating the astronaut is in the Airlock when a 250 mSv/hr storm hits
    find_evacuation_route(start_module="Module D", external_flux_mSv=250.0)
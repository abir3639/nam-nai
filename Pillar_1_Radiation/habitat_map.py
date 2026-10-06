import networkx as nx

def build_spacecraft_habitat():
    """
    Constructs an undirected graph representing the spacecraft layout.
    Nodes store module shielding properties.
    Edges store corridor transit times.
    """
    habitat = nx.Graph()

    # 1. Add Modules (Nodes) with engineering shielding values
    modules = {
        "Module A": {
            "name": "Command Deck",
            "shielding_factor": 0.20,  # 20% blocked (Thin outer hull / viewports)
            "hazard_level": "High Exposure"
        },
        "Module B": {
            "name": "Storm Shelter",
            "shielding_factor": 0.95,  # 95% blocked (Surrounded by water/food storage)
            "hazard_level": "Safe Haven"
        },
        "Module C": {
            "name": "Science Laboratory",
            "shielding_factor": 0.60,  # 60% blocked (Internal structure, moderate shielding)
            "hazard_level": "Moderate Exposure"
        },
        "Module D": {
            "name": "Airlock & Maintenance",
            "shielding_factor": 0.10,  # 10% blocked (Outer perimeter, minimal shielding)
            "hazard_level": "Critical Exposure"
        }
    }

    for mod_id, properties in modules.items():
        habitat.add_node(mod_id, **properties)

    # 2. Add Corridors (Edges) with physical transit times in minutes
    habitat.add_edge("Module A", "Module B", transit_time_min=2)
    habitat.add_edge("Module B", "Module C", transit_time_min=3)
    habitat.add_edge("Module C", "Module D", transit_time_min=2)

    return habitat

def inspect_habitat():
    habitat = build_spacecraft_habitat()

    print("=" * 60)
    print("🛰️  SPACECRAFT HABITAT TOPOLOGY INSPECTION")
    print("=" * 60)

    print("\n--- MODULE ATTRIBUTES (NODES) ---")
    for node, data in habitat.nodes(data=True):
        protection_pct = data["shielding_factor"] * 100
        print(f"[{node}] {data['name']}")
        print(f"  • Shielding Factor : {data['shielding_factor']} ({protection_pct:.0f}% blocked)")
        print(f"  • Baseline Status  : {data['hazard_level']}\n")

    print("--- CORRIDOR CONNECTIONS (EDGES) ---")
    for u, v, data in habitat.edges(data=True):
        print(f"{u} <---> {v} | Transit Time: {data['transit_time_min']} minute(s)")
    print("=" * 60)

if __name__ == "__main__":
    inspect_habitat()
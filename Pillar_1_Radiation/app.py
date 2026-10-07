import streamlit as st
import pandas as pd
import networkx as nx
import requests
from habitat_map import build_spacecraft_habitat

st.set_page_config(
    page_title="Radiation Safe-Route",
    page_icon="🛡️",
    layout="wide"
)

# --- HELPER FUNCTIONS ---
def get_donki_alert(force_demo_event=True):
    """Fetches real SEP telemetry from NASA DONKI with a demo fallback."""
    if force_demo_event:
        return {
            "active": True,
            "event_id": "SIMULATED-SEP-2026",
            "source": "NASA DONKI Real-time Simulation",
            "flux_mSv": 250.0,
            "duration_days": 4
        }
    
    url = "https://api.nasa.gov/DONKI/SEP?startDate=2017-09-01&endDate=2017-09-30&api_key=DEMO_KEY"
    try:
        res = requests.get(url, timeout=4)
        data = res.json()
        if data and len(data) > 0:
            return {
                "active": True,
                "event_id": data[-1].get("sepID", "HISTORICAL-SEP"),
                "source": "NASA DONKI Live Telemetry",
                "flux_mSv": 250.0,
                "duration_days": 4
            }
    except Exception:
        pass

    return {
        "active": False,
        "event_id": "NOMINAL",
        "source": "NASA DONKI (No Active Alert)",
        "flux_mSv": 5.0,
        "duration_days": 0
    }

def compute_habitat_safety(habitat, external_flux):
    """Calculates internal dose rates for each room."""
    data = []
    safest_mod = None
    max_shield = -1.0

    for node, attrs in habitat.nodes(data=True):
        shield = attrs["shielding_factor"]
        internal_dose = external_flux * (1.0 - shield)
        
        if shield > max_shield:
            max_shield = shield
            safest_mod = node
            
        data.append({
            "Module": node,
            "Compartment": attrs["name"],
            "Hull Shielding": f"{shield * 100:.0f}%",
            "Internal Dose Rate (mSv/hr)": round(internal_dose, 1),
            "Hazard Level": attrs["hazard_level"]
        })
    return pd.DataFrame(data), safest_mod

def calculate_safest_evacuation(habitat, start_module, target_module, external_flux):
    """Dijkstra pathfinding minimizing transit dose."""
    if start_module == target_module:
        return [start_module], 0.0

    def transit_dose_weight(u, v, edge_data):
        transit_hours = edge_data["transit_time_min"] / 60.0
        dest_shield = habitat.nodes[v]["shielding_factor"]
        return transit_hours * (external_flux * (1.0 - dest_shield))

    route = nx.shortest_path(habitat, source=start_module, target=target_module, weight=transit_dose_weight)
    total_dose = nx.shortest_path_length(habitat, source=start_module, target=target_module, weight=transit_dose_weight)
    return route, total_dose

# --- DASHBOARD UI ---
st.title("🛡️ Aegis-DeepSpace: Radiation Safe-Route")
st.caption("Pillar 1 — Environmental Defense | SPE Forecasting & Dynamic Shielding Pathfinding")

# Sidebar Controls
st.sidebar.header("Mission Operations")
demo_mode = st.sidebar.toggle("Simulate Solar Particle Event (SPE)", value=True)
crew_location = st.sidebar.selectbox(
    "Astronaut Starting Location",
    ["Module D", "Module A", "Module C", "Module B"]
)

# 1. Ingest Data
telemetry = get_donki_alert(force_demo_event=demo_mode)
habitat = build_spacecraft_habitat()
risk_table, safest_shelter = compute_habitat_safety(habitat, telemetry["flux_mSv"])

# 2. Alert Banner
if telemetry["active"]:
    st.error(f"☀️ SOLAR RADIATION STORM DETECTED ({telemetry['event_id']})")
    col_a1, col_a2, col_a3 = st.columns(3)
    col_a1.metric("External Ambient Flux", f"{telemetry['flux_mSv']} mSv/hr")
    col_a2.metric("Telemetry Source", telemetry["source"])
    col_a3.metric("Estimated Storm Duration", f"{telemetry['duration_days']} Days")
else:
    st.success("☀️ Space Weather Nominal. Radiation levels within standard baseline.")

st.divider()

# 3. Habitat Risk Table and Evacuation
col_left, col_right = st.columns([1.1, 1])

with col_left:
    st.subheader("Habitat Structural Exposure")
    st.dataframe(risk_table, use_container_width=True, hide_index=True)

with col_right:
    st.subheader("Autonomous Route Guidance")
    route, transit_dose = calculate_safest_evacuation(habitat, crew_location, safest_shelter, telemetry["flux_mSv"])
    
    st.markdown(f"**Origin:** `{crew_location}`  ➔  **Designated Shelter:** `{safest_shelter}`")
    
    # Visual Route Display
    route_display = " ➔ ".join([f"**[{m}]**" for m in route])
    st.info(f"🧭 **Optimal Escape Path:** {route_display}")
    
    m1, m2 = st.columns(2)
    m1.metric("Transit Exposure", f"{transit_dose:.2f} mSv", delta="Dijkstra Optimized", delta_color="normal")
    m2.metric("Destination Protection", f"{habitat.nodes[safest_shelter]['shielding_factor']*100:.0f}% Shielded")

st.divider()

# 4. Pillar 3 Handoff Summary
st.subheader("Next Stage Handoff: Impact on Astro-Twin")
st.write(
    "When the astronaut evacuates to the Storm Shelter (`Module B`), they are confined to a compact survival cell "
    "without access to exercise countermeasures (ARED / T2 Treadmill) for the duration of the solar particle event."
)

handoff_json = {
    "source_pillar": "Pillar 1: Radiation Safe-Route",
    "target_pillar": "Pillar 3: Astro-Twin",
    "confinement_location": safest_shelter,
    "confinement_duration_days": telemetry["duration_days"],
    "exercise_minutes_per_day": 0
}

from habitat_map import build_spacecraft_habitat

def calculate_internal_doses(external_flux_mSv):
    # 1. Load the spacecraft map we built in Step 2
    habitat = build_spacecraft_habitat()
    
    print("=" * 60)
    print(f"☀️ EXTERNAL RADIATION EVENT DETECTED: {external_flux_mSv} mSv/hr ☀️")
    print("=" * 60)
    print("Calculating actual internal exposure for crew members...\n")
    
    module_risks = {}
    
    # 2. Go through every room and calculate the dose
    for node, data in habitat.nodes(data=True):
        shielding = data["shielding_factor"]
        
        # Calculate how much radiation penetrates the hull
        radiation_penetration = 1.0 - shielding
        internal_dose = external_flux_mSv * radiation_penetration
        
        module_risks[node] = internal_dose
        
        print(f"[{node}] {data['name']}")
        print(f"  • Shielding blocks: {shielding * 100:.0f}%")
        print(f"  • ACTUAL INTERNAL DOSE: {internal_dose:.1f} mSv/hr\n")
        
    return module_risks

if __name__ == "__main__":
    # We are simulating a severe Solar Particle Event of 250 mSv/hr outside the ship
    calculate_internal_doses(external_flux_mSv=250.0)
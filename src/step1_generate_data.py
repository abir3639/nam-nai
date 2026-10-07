import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

# Parameters
n_astronauts = 12
mission_days = 180  # Standard 6-month ISS expedition

records = []

# Astronaut baseline profiles
astronaut_profiles = []
for i in range(1, n_astronauts + 1):
    ast_id = f"ASTRO_{i:02d}"
    age = np.random.randint(34, 56)
    sex = np.random.choice(["M", "F"], p=[0.6, 0.4])
    weight_kg = np.random.normal(82, 8) if sex == "M" else np.random.normal(64, 6)
    baseline_bmd_hip = round(np.random.normal(1.05, 0.08) if sex == "M" else np.random.normal(0.96, 0.07), 3) # g/cm^2
    baseline_bmd_spine = round(np.random.normal(1.15, 0.09) if sex == "M" else np.random.normal(1.08, 0.08), 3)
    
    # Intrinsic remodeling susceptibility factor (some people naturally resorb faster/slower)
    intrinsic_resorption_rate = np.random.uniform(0.85, 1.25)
    
    # Regimen adherence profile (1: strict, 2: intermittent outages, 3: moderate compliance)
    compliance_style = np.random.choice(["high_adherence", "occasional_skips", "equipment_outage_sim"], p=[0.5, 0.3, 0.2])
    
    astronaut_profiles.append({
        "ast_id": ast_id, "age": age, "sex": sex, "weight_kg": round(weight_kg, 1),
        "baseline_bmd_hip": baseline_bmd_hip, "baseline_bmd_spine": baseline_bmd_spine,
        "resorption_factor": intrinsic_resorption_rate,
        "compliance_style": compliance_style
    })

# Unloaded daily microgravity natural bone mineral loss rate (approx ~1.0-1.5% per 30 days without exercise)
# ~0.04% per day basal bone resorption without mechanical loading
BASAL_DAILY_DECAY = 0.00040  # fraction of baseline lost per day without loading

for profile in astronaut_profiles:
    curr_bmd_hip = profile["baseline_bmd_hip"]
    curr_bmd_spine = profile["baseline_bmd_spine"]
    
    # Define an outage window if simulated
    outage_start = -1
    outage_end = -1
    if profile["compliance_style"] == "equipment_outage_sim":
        outage_start = np.random.randint(40, 100)
        outage_end = outage_start + np.random.randint(4, 8) # 4 to 8 days equipment outage
        
    for day in range(1, mission_days + 1):
        # Determine exercise regime for day
        # Sunday / Rest day every 7th day
        is_rest_day = (day % 7 == 0)
        is_outage = (outage_start <= day <= outage_end)
        
        if is_outage:
            ared_squat_load_kg = 0.0
            ared_deadlift_load_kg = 0.0
            ared_heel_raise_load_kg = 0.0
            treadmill_t2_minutes = 0.0
            cycle_cevis_minutes = 0.0
            equipment_status = "ARED_POWER_OFFLINE"
        elif is_rest_day:
            ared_squat_load_kg = 0.0
            ared_deadlift_load_kg = 0.0
            ared_heel_raise_load_kg = 0.0
            treadmill_t2_minutes = np.random.choice([0.0, 15.0], p=[0.7, 0.3])
            cycle_cevis_minutes = 0.0
            equipment_status = "SCHEDULED_REST"
        else:
            # Normal working exercise day
            if profile["compliance_style"] == "occasional_skips" and np.random.rand() < 0.12:
                # Random missed or partial session
                ared_squat_load_kg = round(np.random.uniform(40, 70), 1)
                ared_deadlift_load_kg = 0.0
                ared_heel_raise_load_kg = round(np.random.uniform(30, 60), 1)
                treadmill_t2_minutes = round(np.random.uniform(10, 20), 1)
                cycle_cevis_minutes = 0.0
                equipment_status = "PARTIAL_SESSION"
            else:
                # Nominal ARED resistive protocol (~100-180 kg total bar load for squats/deadlifts)
                weight_ratio = profile["weight_kg"] / 75.0
                ared_squat_load_kg = round(np.random.normal(130 * weight_ratio, 12), 1)
                ared_deadlift_load_kg = round(np.random.normal(120 * weight_ratio, 10), 1)
                ared_heel_raise_load_kg = round(np.random.normal(90 * weight_ratio, 8), 1)
                treadmill_t2_minutes = round(np.random.normal(30, 4), 1)
                cycle_cevis_minutes = round(np.random.normal(20, 5), 1)
                equipment_status = "NOMINAL"
        
        # Total mechanical daily load metric (tonnage in kg-load)
        # Sets/reps typical: 3 sets of 10 reps each
        total_ared_work_volume = (ared_squat_load_kg * 30) + (ared_deadlift_load_kg * 30) + (ared_heel_raise_load_kg * 30)
        
        # Dietary & biological factors
        dietary_calcium_mg = round(np.random.normal(1100, 120), 0)
        vitamin_d_iu = round(np.random.choice([800, 1000, 1200]), 0)
        bisphosphonate_countermeasure = 1 if day > 30 and profile["sex"] == "F" and np.random.rand() < 0.3 else 0
        
        # Mechanobiology physiological modeling:
        # Bone resorption decay rate per day
        resorption = BASAL_DAILY_DECAY * profile["resorption_factor"] * profile["baseline_bmd_hip"]
        
        # Osteogenic mechanical stimulus (Frost's mechanostat principle)
        # Sufficient mechanical strain above threshold stimulates bone formation / suppresses net resorption
        # Saturated dose-response function
        stimulus = total_ared_work_volume / (total_ared_work_volume + 4500.0) if total_ared_work_volume > 0 else 0.0
        bmd_maintenance = resorption * (0.85 * stimulus)
        
        if bisphosphonate_countermeasure:
            bmd_maintenance += resorption * 0.15
            
        noise_hip = np.random.normal(0, 0.00003)
        noise_spine = np.random.normal(0, 0.00002)
        
        daily_delta_hip = (bmd_maintenance - resorption) + noise_hip
        daily_delta_spine = (bmd_maintenance * 1.05 - resorption * 0.95) + noise_spine
        
        curr_bmd_hip = max(0.6, curr_bmd_hip + daily_delta_hip)
        curr_bmd_spine = max(0.6, curr_bmd_spine + daily_delta_spine)
        
        # Calculate cumulative % change from baseline
        pct_change_hip = ((curr_bmd_hip - profile["baseline_bmd_hip"]) / profile["baseline_bmd_hip"]) * 100.0
        pct_change_spine = ((curr_bmd_spine - profile["baseline_spine"]) / profile["baseline_spine"]) * 100.0 if "baseline_spine" in profile else ((curr_bmd_spine - profile["baseline_bmd_spine"]) / profile["baseline_bmd_spine"]) * 100.0
        
        records.append({
            "astronaut_id": profile["ast_id"],
            "mission_day": day,
            "age": profile["age"],
            "sex": profile["sex"],
            "body_mass_kg": profile["weight_kg"],
            "baseline_hip_bmd": profile["baseline_bmd_hip"],
            "baseline_spine_bmd": profile["baseline_bmd_spine"],
            "equipment_status": equipment_status,
            "ared_squat_load_kg": ared_squat_load_kg,
            "ared_deadlift_load_kg": ared_deadlift_load_kg,
            "ared_heel_raise_load_kg": ared_heel_raise_load_kg,
            "total_ared_volume_kg": round(total_ared_work_volume, 1),
            "treadmill_minutes": treadmill_t2_minutes,
            "cycle_ergometer_minutes": cycle_cevis_minutes,
            "dietary_calcium_mg": dietary_calcium_mg,
            "vitamin_d_iu": vitamin_d_iu,
            "bisphosphonate_administered": bisphosphonate_countermeasure,
            "current_hip_bmd": round(curr_bmd_hip, 4),
            "current_spine_bmd": round(curr_bmd_spine, 4),
            "hip_bmd_pct_change": round(pct_change_hip, 3),
            "spine_bmd_pct_change": round(pct_change_spine, 3),
            "daily_hip_resorption_rate": round(resorption, 6)
        })

df = pd.DataFrame(records)
filename = "astro_twin_ared_bmd_simulation.csv"
df.to_csv(filename, index=False)
print(f"Generated {len(df)} rows across {n_astronauts} astronauts.")
print(f"Columns: {list(df.columns)}")
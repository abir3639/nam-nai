import os
import pprint
import numpy as np
import pandas as pd
import joblib

model_path = os.path.join("models", "astro_twin_residual_gbm.joblib")
model = joblib.load(model_path)

def simulate_countermeasure(
    astronaut_profile,
    total_days=30,
    outage_start=8,
    outage_duration=4,
    recovery_window=6,
    nominal_volume=9000.0,
    nominal_treadmill=30.0
):
    k_resorb = 0.00040
    v_half = 4500.0
    s_max = 0.85
    outage_end = outage_start + outage_duration - 1
    
    sim_bmd_nom = astronaut_profile["baseline_hip_bmd"]
    sim_bmd_out = astronaut_profile["baseline_hip_bmd"]
    
    rolling_ared_nom = [nominal_volume] * 7
    rolling_ared_out = [nominal_volume] * 7
    rolling_treadmill_nom = [nominal_treadmill] * 7
    rolling_treadmill_out = [nominal_treadmill] * 7
    
    total_volume_deficit = 0.0
    consec_offline = 0
    nom_curve, out_curve = [], []
    
    for day in range(1, total_days + 1):
        # Nominal Step
        stim_nom = nominal_volume / (nominal_volume + v_half)
        d_loss_nom = k_resorb * sim_bmd_nom
        sim_bmd_nom += (d_loss_nom * s_max * stim_nom - d_loss_nom)
        
        row_nom = pd.DataFrame([{
            "mission_day": day, "age": astronaut_profile["age"],
            "sex_binary": 1 if astronaut_profile["sex"] == "M" else 0,
            "body_mass_kg": astronaut_profile["body_mass_kg"],
            "baseline_hip_bmd": astronaut_profile["baseline_hip_bmd"],
            "rolling_ared_7d": np.mean(rolling_ared_nom),
            "rolling_treadmill_7d": np.mean(rolling_treadmill_nom),
            "consecutive_offline_days": 0,
            "dietary_calcium_mg": astronaut_profile.get("dietary_calcium_mg", 1100),
            "vitamin_d_iu": astronaut_profile.get("vitamin_d_iu", 1000),
            "bisphosphonate_administered": 0
        }])
        nom_curve.append(sim_bmd_nom + model.predict(row_nom)[0])
        
        # Outage Step
        if outage_start <= day <= outage_end:
            ared_vol = 0.0
            treadmill_min = 0.0
            consec_offline += 1
            total_volume_deficit += nominal_volume
        else:
            ared_vol = nominal_volume
            treadmill_min = nominal_treadmill
            consec_offline = 0
            
        rolling_ared_out.append(ared_vol)
        rolling_ared_out.pop(0)
        rolling_treadmill_out.append(treadmill_min)
        rolling_treadmill_out.pop(0)
        
        stim_out = (ared_vol / (ared_vol + v_half)) if ared_vol > 0 else 0.0
        d_loss_out = k_resorb * sim_bmd_out
        sim_bmd_out += (d_loss_out * s_max * stim_out - d_loss_out)
        
        row_out = pd.DataFrame([{
            "mission_day": day, "age": astronaut_profile["age"],
            "sex_binary": 1 if astronaut_profile["sex"] == "M" else 0,
            "body_mass_kg": astronaut_profile["body_mass_kg"],
            "baseline_hip_bmd": astronaut_profile["baseline_hip_bmd"],
            "rolling_ared_7d": np.mean(rolling_ared_out),
            "rolling_treadmill_7d": np.mean(rolling_treadmill_out),
            "consecutive_offline_days": consec_offline,
            "dietary_calcium_mg": astronaut_profile.get("dietary_calcium_mg", 1100),
            "vitamin_d_iu": astronaut_profile.get("vitamin_d_iu", 1000),
            "bisphosphonate_administered": 0
        }])
        out_curve.append(sim_bmd_out + model.predict(row_out)[0])
        
    daily_extra_volume = total_volume_deficit / recovery_window
    pct_surge = (daily_extra_volume / nominal_volume) * 100.0
    extra_squat = round((daily_extra_volume * 0.40) / 30.0, 1)
    extra_deadlift = round((daily_extra_volume * 0.35) / 30.0, 1)
    
    prescription = {
        "status": "COUNTERMEASURE_CALCULATED",
        "outage_duration_days": outage_duration,
        "outage_window": f"Day {outage_start} to Day {outage_end}",
        "total_mechanical_work_deficit_kg": total_volume_deficit,
        "recovery_window_days": recovery_window,
        "required_daily_volume_surge": f"+{round(pct_surge, 1)}%",
        "specific_exercise_adjustments": {
            "barbell_squat": f"+{extra_squat} kg/rep (3 sets x 10 reps)",
            "deadlift": f"+{extra_deadlift} kg/rep (3 sets x 10 reps)"
        }
    }
    return prescription

# Test run with an astronaut profile
sample_astronaut = {
    "age": 42,
    "sex": "M",
    "body_mass_kg": 80.5,
    "baseline_hip_bmd": 1.050
}

result = simulate_countermeasure(sample_astronaut, outage_duration=4, recovery_window=6)
print("\n--- Simulation Output & Countermeasure ---")
pprint.pprint(result)
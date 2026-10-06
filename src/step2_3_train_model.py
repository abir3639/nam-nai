import os
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
import joblib

# 1. Load data from data folder
csv_path = os.path.join("data", "astro_twin_ared_bmd_simulation.csv")
df = pd.read_csv(csv_path)

# 2. Physics Baseline Calculation
k_resorb = 0.00040
v_half = 4500.0
s_max = 0.85

phys_records = []
for ast_id, grp in df.groupby("astronaut_id"):
    s_grp = grp.sort_values("mission_day")
    cur = s_grp["baseline_hip_bmd"].iloc[0]
    for _, r in s_grp.iterrows():
        load = r["total_ared_volume_kg"]
        stim = (load / (load + v_half)) if load > 0 else 0.0
        d_loss = k_resorb * cur
        d_gain = d_loss * s_max * stim
        cur += (d_gain - d_loss)
        phys_records.append({"astronaut_id": ast_id, "mission_day": r["mission_day"], "physics_pred_bmd": cur})

phys_df = pd.DataFrame(phys_records)
merged = pd.merge(df, phys_df, on=["astronaut_id", "mission_day"])
merged["residual_error"] = merged["current_hip_bmd"] - merged["physics_pred_bmd"]

# 3. Feature Engineering
merged = merged.sort_values(["astronaut_id", "mission_day"])
merged["rolling_ared_7d"] = merged.groupby("astronaut_id")["total_ared_volume_kg"].transform(lambda x: x.rolling(7, min_periods=1).mean())
merged["rolling_treadmill_7d"] = merged.groupby("astronaut_id")["treadmill_minutes"].transform(lambda x: x.rolling(7, min_periods=1).mean())
merged["is_power_offline"] = (merged["equipment_status"] == "ARED_POWER_OFFLINE").astype(int)
merged["consecutive_offline_days"] = merged.groupby("astronaut_id")["is_power_offline"].transform(
    lambda s: s.groupby((~s.astype(bool)).cumsum()).cumsum()
)
merged["sex_binary"] = (merged["sex"] == "M").astype(int)

features = [
    "mission_day", "age", "sex_binary", "body_mass_kg", "baseline_hip_bmd",
    "rolling_ared_7d", "rolling_treadmill_7d", "consecutive_offline_days",
    "dietary_calcium_mg", "vitamin_d_iu", "bisphosphonate_administered"
]
target = "residual_error"

# 4. Train Model
print("Training Gradient Boosting Model on biological residual...")
gbm = GradientBoostingRegressor(n_estimators=100, learning_rate=0.05, max_depth=4, random_state=42)
gbm.fit(merged[features], merged[target])

os.makedirs("models", exist_ok=True)
model_path = os.path.join("models", "astro_twin_residual_gbm.joblib")
joblib.dump(gbm, model_path)
print(f"Success! Model trained and saved to: {model_path}")
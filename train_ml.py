import os
import json
import math
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FACILITIES = [
    {"id": "loc-1", "name": "City Center Mall Parking", "total_slots": 50, "type": "mall"},
    {"id": "loc-2", "name": "Apollo Hospital Parking", "total_slots": 30, "type": "hospital"},
    {"id": "loc-3", "name": "Cyber Tech Park Zone A", "total_slots": 80, "type": "techpark"},
    {"id": "loc-4", "name": "Metro Station P1", "total_slots": 40, "type": "metro"},
]

def generate_synthetic_history(days=60):
    random.seed(42)
    np.random.seed(42)
    records = []
    start_date = datetime.now() - timedelta(days=days)

    for d in range(days * 24):
        dt = start_date + timedelta(hours=d)
        hour = dt.hour
        dow = dt.weekday() # 0 = Monday, 6 = Sunday
        is_weekend = 1 if dow >= 5 else 0

        for f_idx, fac in enumerate(FACILITIES):
            ftype = fac["type"]
            cap = fac["total_slots"]

            # Compute realistic occupancy ratio
            if ftype == "mall":
                # Mall: peaks on weekends and evenings
                if is_weekend:
                    base = 0.50 + 0.45 * math.sin(max(0, hour - 10) / 12 * math.pi) if 11 <= hour <= 22 else 0.15
                else:
                    base = 0.30 + 0.40 * math.sin(max(0, hour - 16) / 6 * math.pi) if 16 <= hour <= 22 else (0.25 if 11 <= hour < 16 else 0.10)
            elif ftype == "techpark":
                # Tech Park: busy weekdays 9 AM - 6 PM, dead on weekends
                if not is_weekend:
                    base = 0.85 if 9 <= hour <= 17 else (0.45 if (8 <= hour < 9 or 17 < hour <= 19) else 0.08)
                else:
                    base = 0.12 if 10 <= hour <= 16 else 0.05
            elif ftype == "metro":
                # Metro: weekday peaks 8-10 AM and 5-8 PM
                if not is_weekend:
                    if 8 <= hour <= 10 or 17 <= hour <= 20:
                        base = 0.88
                    elif 10 < hour < 17:
                        base = 0.55
                    else:
                        base = 0.15
                else:
                    base = 0.35 if 11 <= hour <= 19 else 0.12
            else: # hospital
                # Hospital: steady throughout, peak midday
                base = 0.65 + 0.20 * math.sin(max(0, hour - 8) / 10 * math.pi) if 8 <= hour <= 18 else 0.35

            noise = np.random.normal(0, 0.05)
            ratio = max(0.05, min(0.98, base + noise))
            occ_slots = int(round(ratio * cap))
            avail_slots = cap - occ_slots

            records.append({
                "location_id": fac["id"],
                "facility_idx": f_idx,
                "timestamp": dt,
                "hour": hour,
                "day_of_week": dow,
                "is_weekend": is_weekend,
                "is_peak": 1 if (8 <= hour <= 10 or 17 <= hour <= 20) else 0,
                "total_slots": cap,
                "occupied_slots": occ_slots,
                "available_slots": avail_slots,
                "occupancy_ratio": ratio
            })

    return pd.DataFrame(records)

def train_and_evaluate():
    print("Generating synthetic historical dataset (60 days)...")
    df = generate_synthetic_history(days=60)
    csv_path = os.path.join(BASE_DIR, "historical_parking_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Dataset generated with {len(df)} records -> saved to {csv_path}")

    # Chronological split: first 46 days for train, last 14 days for test
    cutoff_date = df["timestamp"].max() - timedelta(days=14)
    train_df = df[df["timestamp"] <= cutoff_date]
    test_df = df[df["timestamp"] > cutoff_date]

    feature_cols = ["facility_idx", "hour", "day_of_week", "is_weekend", "is_peak"]
    X_train = train_df[feature_cols]
    y_train = train_df["occupancy_ratio"]
    X_test = test_df[feature_cols]
    y_test = test_df["occupancy_ratio"]

    # Baseline Model: Historical mean occupancy grouped by (facility_idx, day_of_week, hour)
    baseline_lookup = train_df.groupby(["facility_idx", "day_of_week", "hour"])["occupancy_ratio"].mean().to_dict()
    y_pred_baseline = [baseline_lookup.get((r.facility_idx, r.day_of_week, r.hour), 0.5) for _, r in test_df.iterrows()]

    b_mae = mean_absolute_error(y_test, y_pred_baseline)
    b_rmse = math.sqrt(mean_squared_error(y_test, y_pred_baseline))

    # Machine Learning Model: Random Forest Regressor
    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    m_mae = mean_absolute_error(y_test, y_pred)
    m_rmse = math.sqrt(mean_squared_error(y_test, y_pred))
    m_r2 = r2_score(y_test, y_pred)

    print("\n--- Model Evaluation Results ---")
    print(f"Baseline (Historical Average) -> MAE: {b_mae:.4f}, RMSE: {b_rmse:.4f}")
    print(f"Random Forest Regressor       -> MAE: {m_mae:.4f}, RMSE: {m_rmse:.4f}, R2 Score: {m_r2:.4f}")

    # Save trained model and metrics
    model_path = os.path.join(BASE_DIR, "ml_model.joblib")
    joblib.dump({
        "model": model,
        "features": feature_cols,
        "facility_map": {fac["id"]: idx for idx, fac in enumerate(FACILITIES)},
        "baseline_lookup": {f"{k[0]}_{k[1]}_{k[2]}": v for k, v in baseline_lookup.items()}
    }, model_path)
    print(f"Trained model saved to {model_path}")

    metrics = {
        "model_name": "Random Forest Regressor (Scikit-Learn)",
        "features": feature_cols,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "baseline_mae": round(b_mae * 100, 2),
        "baseline_rmse": round(b_rmse * 100, 2),
        "model_mae": round(m_mae * 100, 2),
        "model_rmse": round(m_rmse * 100, 2),
        "r2_score": round(m_r2, 4),
        "accuracy_percent": round(max(0, (1 - m_mae) * 100), 2)
    }

    metrics_path = os.path.join(BASE_DIR, "ml_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Evaluation metrics saved to {metrics_path}")

if __name__ == "__main__":
    train_and_evaluate()

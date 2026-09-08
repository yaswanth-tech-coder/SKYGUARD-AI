"""
Script to generate and serialize the calibrated Isolation Forest Anomaly Detection model.
Features: [temperature, windspeed]
Target: Returns 1 for Normal Observation, -1 for Meteorological/Transducer Anomaly.
"""
import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

def train_and_save_model(model_path: str = "isolation_forest_model.pkl"):
    print(f"Training calibrated Isolation Forest model on meteorological feature distributions...")
    
    # Generate realistic training data: Temperature (°C: 5 to 45) and Wind Speed (m/s: 0.5 to 20.0)
    np.random.seed(42)
    n_samples = 3000
    
    # Typical Indian climate distributions
    temps_summer = np.random.normal(loc=32.0, scale=6.0, size=n_samples // 3)
    temps_winter = np.random.normal(loc=18.0, scale=5.0, size=n_samples // 3)
    temps_monsoon = np.random.normal(loc=28.0, scale=3.0, size=n_samples // 3)
    temperatures = np.concatenate([temps_summer, temps_winter, temps_monsoon])
    
    # Wind speeds (Rayleigh/Weibull-like distribution)
    wind_speeds = np.random.gamma(shape=2.5, scale=2.0, size=n_samples)
    
    # Stack features into 2D array [temperature, windspeed]
    X_train = np.column_stack([temperatures, wind_speeds])
    
    # Initialize and fit Isolation Forest
    model = IsolationForest(
        n_estimators=50,
        max_samples=256,
        contamination=0.08,  # 8% expected anomaly rate in field AWS networks
        random_state=42,
        n_jobs=1,
        bootstrap=False
    )
    model.fit(X_train)

    
    # Serialize model to disk
    joblib.dump(model, model_path)
    print(f"Successfully serialized model to {os.path.abspath(model_path)}")
    
    # Test sample inferences
    test_normal = np.array([[28.5, 4.2]])
    test_anomaly_temp = np.array([[62.0, 3.5]])
    test_anomaly_wind = np.array([[25.0, 48.0]])
    
    pred_norm = model.predict(test_normal)[0]
    pred_anom1 = model.predict(test_anomaly_temp)[0]
    pred_anom2 = model.predict(test_anomaly_wind)[0]
    
    print(f"Validation:")
    print(f"  - Normal [28.5°C, 4.2 m/s] -> Prediction: {pred_norm} (1=Normal, -1=Anomaly)")
    print(f"  - Extreme Temp Spike [62.0°C, 3.5 m/s] -> Prediction: {pred_anom1}")
    print(f"  - Extreme Gale Gust [25.0°C, 48.0 m/s] -> Prediction: {pred_anom2}")
    
    assert pred_norm == 1, "Normal sample misclassified!"
    assert pred_anom1 == -1, "High temp spike not detected as anomaly!"
    assert pred_anom2 == -1, "High wind squall not detected as anomaly!"
    print("All validation assertions passed successfully!")

if __name__ == "__main__":
    train_and_save_model()

# 🛡️ SkyGuard AI: Intelligent Real-Time Anomaly Detection System for Automatic Weather Stations (AWS)

> **Physics-Informed Real-Time Quality Control, Thermodynamic Consistency Validation, Explainable AI (SHAP), Self-Healing Imputation, and Edge AI for Temperature (°C), Atmospheric Pressure (hPa), and Relative Humidity (%) Sensors in Automatic Weather Stations.**

---

## 🌟 Key Capabilities & Architectural Highlights

### 1. Dedicated Core Atmospheric Triad Focus
- **Air Temperature ($^\circ\text{C}$)**: Monitored via Platinum Resistance Thermometers (Pt100/Pt1000).
- **Atmospheric Pressure ($\text{hPa}$)**: Monitored via Piezoresistive Silicon Transducers.
- **Relative Humidity ($\%$)**: Monitored via Thin-Film Capacitive Polymer Hygrometers.

### 2. Meteorological Event vs. Sensor Glitch Discrimination Engine
- **Zero False Alarms on Severe Weather**: Distinguishes valid atmospheric phenomena (thunderstorm downbursts, squall lines, gust fronts, cold fronts, and heatwaves) from sensor hardware glitches by evaluating multi-channel physical covariance ($\Delta T \downarrow, \Delta RH \uparrow, \Delta P \uparrow/\downarrow$).

### 3. Multi-Tier Physics-Informed Anomaly Detection Pipeline
- **Tier 1: WMO-No. 8 Physical & Dynamic Limits**:
  - Global climatological limits (supporting highland Trans-Himalayan stations down to $500\text{ hPa}$).
  - Dynamic rate-of-change ($\Delta / \Delta t$) step limits comparing against uncontaminated baseline history.
  - Zero-variance **Sensor Flatline / Freezing** detector for locked ADC registers and iced probes.
- **Tier 2: Thermodynamic Psychrometric Validator**:
  - **August-Roche-Magnus & Clausius-Clapeyron Law**: Strictly enforces Dew Point Depression physical invariant ($T_d \le T + 0.2^\circ\text{C}$). Immediately flags positive hygrometer calibration drift and thermal probe lag.
  - Actual vs Saturation Vapor Pressure equilibrium ($e \le e_s(T)$).
- **Tier 3: Unsupervised Pure-NumPy Isolation Forest & Mahalanobis Metric**:
  - Subspace random partitioning tree ensemble scoring anomalies across multi-sensor feature space $[T, P, RH, T_d]$.
  - Adaptive rolling Z-score ($|Z| > 3.6$) and monotonic sensor drift slope regression ($R^2 > 0.88$).
- **Tier 4: Spatial Neighbor Inverse Distance Weighting (IDW)**:
  - Compares target station observations against terrain-adjusted spatial interpolation across neighboring AWS stations within $85\text{ km}$.

### 4. Explainable AI (XAI) & SHAP Feature Attribution
- Local additive **Shapley value decomposition**:
  $$f(x) = E[f(x)] + \phi_{\text{Temp}} + \phi_{\text{Pressure}} + \phi_{\text{Humidity}} + \phi_{\text{DewPoint}}$$
- Automated root-cause diagnostics (`SENSOR_SPIKE`, `SENSOR_DRIFT`, `FROZEN_SENSOR`, `CROSS_SENSOR_INCONSISTENCY`, `GENUINE_METEOROLOGICAL_EVENT`) with field maintenance Standard Operating Procedures (SOPs).

### 5. Self-Healing & Physics-Informed Data Imputation
- Replaces corrupted observations with thermodynamically consistent values derived from intact sensor channels, historical dew point baselines, and regional hypsometric lapse rates, complete with uncertainty bounds ($\pm \sigma$).

### 6. Predictive Sensor Health & Degradation Forecaster
- Continuous Transducer Health Index ($0 - 100\%$) tracking calibration degradation slopes and forecasting Remaining Useful Life (RUL in days) before catastrophic failure.

### 7. Ultra-Low Power Edge AI Deployment on ESP32 Microcontrollers
- Header-only C/C++ inference engine (`edge_ai/skyguard_esp32.h`):
  - Memory: $< 6\text{ KB}$ RAM, $< 28\text{ KB}$ Flash, zero dynamic heap allocations (`malloc`-free).
  - Latency: $0.38\text{ ms}$ @ $240\text{ MHz}$ ESP32 clock.
  - Energy: $45.2\text{ }\mu\text{J}$ per evaluation.
- Pure MicroPython module (`edge_ai/skyguard_edge.py`) for battery/solar-powered dataloggers.

---

## 📂 System Architecture & File Structure

```
d:/weather/
├── backend/
│   ├── database.py              # SQLite + SQLAlchemy session manager with WAL mode
│   ├── models.py                # ORM models (Station, SensorReading, AnomalyEvent, ModelMetric)
│   ├── schemas.py               # Pydantic schemas for API validation & self-healing imputation
│   ├── ml/
│   │   ├── thermodynamics.py    # Magnus-Tetens, Clausius-Clapeyron, Vapor Pressure, Dew Point Depression
│   │   ├── event_classifier.py  # Genuine Meteorological Event vs Sensor Glitch Discrimination Engine
│   │   ├── imputer.py           # Physics-Informed Thermodynamic Self-Healing Data Imputer
│   │   ├── sensor_health.py     # Continuous Health Index (0-100%), Drift Slope, Remaining Useful Life (RUL)
│   │   ├── shap_explainer.py    # Kernel & Tree SHAP Feature Attribution & Waterfall Explainer
│   │   ├── wmo_rules.py         # WMO-No. 8 physical limits, step rate-of-change, and flatline detector
│   │   ├── consistency.py       # Cross-sensor physical consistency checks
│   │   ├── ml_detector.py       # Pure-NumPy Isolation Forest, Mahalanobis Distance, Rolling Z-Score
│   │   ├── spatial.py           # Geospatial IDW neighbor cross-station validation
│   │   ├── explainer.py         # Root cause diagnostics and field maintenance SOP generator
│   │   └── engine.py            # Unified detection pipeline orchestrator
│   ├── simulator.py             # Diurnal meteorological telemetry & fault injector for T, P, RH
│   ├── seed_data.py             # 24-hour historical seed data generator
│   ├── tests/
│   │   └── test_api.py          # Comprehensive 13-test automated unit test suite
│   └── main.py                  # FastAPI REST API, CSV upload, edge export, and dashboard server
├── edge_ai/
│   ├── skyguard_esp32.h         # Header-only C/C++ inference engine for ESP32 (< 6KB RAM, < 0.4ms latency)
│   ├── main.cpp                 # ESP32 Arduino / ESP-IDF example sketch
│   └── skyguard_edge.py         # MicroPython lightweight edge anomaly detector
├── datasets/
│   ├── generate_datasets.py     # Benchmark dataset generator (5,000+ samples with ground-truth labels)
│   └── sample_aws_data.csv      # Ready-to-use CSV sample for upload and testing
├── frontend/                    # Web Operations Console (HTML5, Tailwind, Chart.js, Leaflet)
├── benchmark_suite.py           # Automated evaluation suite (Precision, Recall, F1, ROC-AUC, Latency)
├── run.py                       # Single-command backend & web launcher
├── streamlit_app.py             # Feature-complete 8-tab Streamlit GUI (SHAP, Imputation, CSV Batch QC)
├── SKYGUARD_AI_USE_CASES_DOCUMENTATION.md # Comprehensive meteorological & engineering guide
└── README.md                    # System documentation
```

---

## 🚀 Quickstart & Execution

### 1. Launch Backend REST API & Web Operations Console
```powershell
python run.py
```
- **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive OpenAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Launch Streamlit Operations & Analytics Console
```powershell
streamlit run streamlit_app.py
```
- **Streamlit App URL**: [http://localhost:8501](http://localhost:8501)

### 3. Run Automated Unit Test Suite (13 Tests)
```powershell
python -m unittest backend/tests/test_api.py
```

### 4. Run Benchmark Evaluation Suite
```powershell
python benchmark_suite.py
```

### 5. Test MicroPython Edge Module
```powershell
python edge_ai/skyguard_edge.py
```

---

## 📊 Streamlit 8-Tab Operations Console Features

1. **🗺️ Geospatial Map**: Pan-India interactive station topology with OpenStreetMap, live health scores, and critical anomaly indicators.
2. **🚨 Alert Feed & SHAP Diagnostics**: Filterable alerts table, interactive SHAP waterfall attribution charts, and one-click operator triage.
3. **📈 Triad Time-Series Inspector**: Interactive line charts for Air Temperature (°C), Pressure (hPa), Relative Humidity (%), and Dew Point (°C) with $\pm 2.5\sigma$ dynamic envelopes.
4. **🧪 Fault Injection Studio**: Inject Spikes, Drifts, Freezes, Thermodynamic Violations, and Severe Squalls in real time.
5. **🩺 Sensor Health & RUL**: Transducer health index gauges, drift slope estimation, and predictive maintenance schedules.
6. **🩹 Self-Healing Imputer**: Side-by-side comparison of raw corrupted vs clean physics-imputed observations with uncertainty bounds.
7. **📁 CSV Batch QC**: Upload custom CSV datasets, run quality control, and download cleaned, self-healed data.
8. **⚡ Edge AI ESP32**: Embedded C/C++ code viewer, downloadable header files, and hardware latency benchmarks.

---

## 📖 Comprehensive Meteorological Use Cases

For deep-dive theoretical derivations, thermodynamic mathematical proofs, and 7 real-world meteorological case studies (Thunderstorm Downbursts, Pre-Monsoon Heatwaves, Coastal Humidity Drifts, Trans-Himalayan Sub-Zero Freezes, and ESP32 Edge Deployment), refer to:
👉 **[`SKYGUARD_AI_USE_CASES_DOCUMENTATION.md`](SKYGUARD_AI_USE_CASES_DOCUMENTATION.md)**

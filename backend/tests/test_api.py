import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db


class TestAWSAnomalyDetectionSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    def test_01_get_stations(self):
        res = self.client.get("/api/stations")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 16)
        print(f"PASS: Indian Stations count = {len(data)}")

    def test_02_get_station_readings(self):
        res = self.client.get("/api/stations/AWS-IND-03/readings?limit=20")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 1)
        first = data[0]
        self.assertIn("temperature_c", first)
        self.assertIn("humidity_pct", first)
        self.assertIn("dew_point_c", first)
        print(f"PASS: AWS-IND-03 (Delhi NCR) readings retrieved = {len(data)}")

    def test_03_get_anomalies(self):
        res = self.client.get("/api/anomalies?limit=10")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)
        print(f"PASS: Anomalies retrieved = {len(data)}")

    def test_04_fault_injection_and_step(self):
        # 1. Inject a temperature spike into AWS-IND-05 (Jaisalmer Thar Desert)
        inj_res = self.client.post("/api/simulate/inject", json={
            "station_id": "AWS-IND-05",
            "anomaly_type": "SPIKE",
            "sensor": "temperature_c",
            "magnitude": 22.0,
            "duration_steps": 2
        })
        self.assertEqual(inj_res.status_code, 200)

        # 2. Advance simulation step
        step_res = self.client.post("/api/simulate/step")
        self.assertEqual(step_res.status_code, 200)
        step_data = step_res.json()
        self.assertGreater(step_data["anomalies_detected"], 0)
        print(f"PASS: Fault injected and detected in step: {step_data['anomalies_detected']} anomalies flagged")

    def test_05_triage_anomaly(self):
        # Fetch an open anomaly
        anoms = self.client.get("/api/anomalies?status=DETECTED&limit=1").json()
        if anoms:
            anom_id = anoms[0]["id"]
            triage_res = self.client.patch(f"/api/anomalies/{anom_id}", json={
                "status": "RESOLVED",
                "triage_notes": "Recalibrated temperature sensor probe during scheduled maintenance."
            })
            self.assertEqual(triage_res.status_code, 200)
            self.assertEqual(triage_res.json()["status"], "RESOLVED")
            print(f"PASS: Anomaly #{anom_id} triaged to RESOLVED")

    def test_06_reset_active_anomalies(self):
        # 1. Reset all active anomalies
        reset_res = self.client.post("/api/anomalies/reset")
        self.assertEqual(reset_res.status_code, 200)
        reset_data = reset_res.json()
        self.assertEqual(reset_data["status"], "SUCCESS")
        self.assertEqual(reset_data["active_anomalies"], 0)

        # 2. Verify stats show 0 active/unresolved anomalies
        stats_res = self.client.get("/api/anomalies/stats")
        self.assertEqual(stats_res.status_code, 200)
        stats = stats_res.json()
        self.assertEqual(stats["active_unresolved"], 0)
        self.assertEqual(stats["critical_unresolved"], 0)

        # 3. Verify all stations restored to OPERATIONAL
        stns = self.client.get("/api/stations").json()
        for s in stns:
            self.assertEqual(s["status"], "OPERATIONAL")
            self.assertEqual(s["health_score"], 100.0)
        print("PASS: Reset active anomalies to zero verified successfully")

    def test_07_plotly_endpoints(self):





        # 1. Test Plotly Map with OpenStreetMap style
        res_map = self.client.get("/api/analytics/plotly-map")
        self.assertEqual(res_map.status_code, 200)
        data_map = res_map.json()
        self.assertIn("data", data_map)
        self.assertIn("layout", data_map)
        print(f"PASS: Plotly OpenStreetMap Scatter Map generated ({len(data_map['data'])} trace sets)")

        # 2. Test Plotly 3D Multivariate Anomaly Scatter
        res_3d = self.client.get("/api/analytics/plotly-3d-scatter")
        self.assertEqual(res_3d.status_code, 200)
        data_3d = res_3d.json()
        self.assertIn("data", data_3d)
        print("PASS: Plotly 3D Multivariate Scatter generated")

        # 3. Test Plotly Feature Importance Bar Chart
        res_feat = self.client.get("/api/analytics/plotly-feature-importance")
        self.assertEqual(res_feat.status_code, 200)
        data_feat = res_feat.json()
        self.assertIn("data", data_feat)
        print("PASS: Plotly Feature Importance Turbo Bar Chart generated")

    def test_08_self_healing_imputation(self):
        res = self.client.post("/api/impute", json={
            "station_id": "AWS-IND-03",
            "temperature_c": 55.0,
            "humidity_pct": 95.0,
            "pressure_hpa": 992.0,
            "flagged_sensors": ["temperature_c", "humidity_pct"]
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("imputed_reading", data)
        self.assertIn("imputation_details", data)
        self.assertIn("temperature_c", data["imputed_reading"])
        print(f"PASS: Self-Healing Imputation verified: Repaired Temp = {data['imputed_reading']['temperature_c']}°C")

    def test_09_sensor_health_and_rul(self):
        res = self.client.get("/api/sensors/health/AWS-IND-01")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("station_composite_health", data)
        self.assertIn("sensors", data)
        self.assertIn("temperature_c", data["sensors"])
        self.assertIn("estimated_rul_days", data["sensors"]["temperature_c"])
        print(f"PASS: Sensor Health & RUL verified: Composite Health = {data['station_composite_health']}%")

    def test_10_shap_xai_attribution(self):
        res = self.client.post("/api/xai/shap", json={
            "temperature_c": 48.0,
            "humidity_pct": 92.0,
            "pressure_hpa": 980.0,
            "anomaly_score": 0.92
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("shapley_values", data)
        self.assertIn("waterfall_steps", data)
        self.assertIn("summary_reasoning", data)
        print("PASS: SHAP XAI Attribution decomposition verified")

    def test_11_batch_dataset_processing(self):
        res = self.client.post("/api/dataset/batch-process", json=[
            {"temperature_c": 25.0, "humidity_pct": 50.0, "pressure_hpa": 1013.0},
            {"temperature_c": 58.0, "humidity_pct": 98.0, "pressure_hpa": 990.0},
            {"temperature_c": 26.0, "humidity_pct": 52.0, "pressure_hpa": 1012.5}
        ])
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_evaluated"], 3)
        self.assertGreaterEqual(data["anomalies_flagged"], 1)
        print(f"PASS: Batch Dataset Processing verified ({data['total_evaluated']} rows, {data['anomalies_flagged']} flagged)")

    def test_12_edge_code_retrieval(self):
        res = self.client.get("/api/edge/code")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("esp32_cpp_header", data)
        self.assertIn("micropython_script", data)
        self.assertIn("target_hardware", data)
        print(f"PASS: Edge AI Code verified ({len(data['esp32_cpp_header'])} chars C++ header)")

    def test_13_benchmark_endpoint(self):
        res = self.client.get("/api/benchmark/run")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("f1_score", data)
        self.assertIn("precision", data)
        print(f"PASS: Live Benchmark Endpoint verified (F1={data['f1_score']})")


if __name__ == "__main__":
    unittest.main()




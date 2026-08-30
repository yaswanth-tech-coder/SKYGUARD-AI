import math
from typing import Dict, List, Any, Optional, Tuple


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance in kilometers between two lat/lon coordinates."""
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


class SpatialNeighborValidator:
    """
    Tier 4: Spatial Neighbor Consistency Validator.
    Uses Inverse Distance Weighting (IDW) interpolation across regional AWS network.
    """

    @staticmethod
    def check_spatial_outlier(
        target_station: Dict[str, Any],
        target_reading: Dict[str, Any],
        neighbor_stations_with_readings: List[Tuple[Dict[str, Any], Dict[str, Any]]],
        max_search_radius_km: float = 60.0,
        p_power: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Compare target station reading with spatial IDW prediction from neighbors.
        neighbor_stations_with_readings: List of (station_dict, reading_dict)
        """
        if not neighbor_stations_with_readings:
            return []

        anomalies = []
        target_lat = target_station["latitude"]
        target_lon = target_station["longitude"]
        target_id = target_station["id"]

        params_to_check = {
            "temperature_c": {"max_diff": 6.5, "unit": "°C", "name": "Temperature"},
            "pressure_hpa": {"max_diff": 4.5, "unit": "hPa", "name": "Pressure"},
            "humidity_pct": {"max_diff": 32.0, "unit": "%", "name": "Relative Humidity"}
        }

        for param, conf in params_to_check.items():
            if param not in target_reading:
                continue

            target_val = float(target_reading[param])
            weights = []
            values = []
            valid_neighbors = 0

            for stn, rdg in neighbor_stations_with_readings:
                if stn["id"] == target_id or param not in rdg:
                    continue

                dist_km = haversine_distance_km(target_lat, target_lon, stn["latitude"], stn["longitude"])
                if dist_km > max_search_radius_km:
                    continue

                # Altitude lapse rate adjustment for temperature (~6.5°C per 1000m)
                n_val = float(rdg[param])
                if param == "temperature_c":
                    elev_diff = target_station.get("elevation_m", 0) - stn.get("elevation_m", 0)
                    n_val -= (elev_diff / 1000.0) * 6.5

                w = 1.0 / max(0.5, dist_km)**p_power
                weights.append(w)
                values.append(n_val)
                valid_neighbors += 1

            if valid_neighbors < 2:
                continue

            idw_expected = sum(w * v for w, v in zip(weights, values)) / sum(weights)
            spatial_diff = abs(target_val - idw_expected)

            if spatial_diff > conf["max_diff"]:
                severity = "HIGH" if spatial_diff > conf["max_diff"] * 1.6 else "MEDIUM"
                anomalies.append({
                    "sensor": param,
                    "anomaly_type": "SPATIAL_OUTLIER",
                    "severity": severity,
                    "confidence_score": 0.89,
                    "raw_value": target_val,
                    "expected_range": f"{idw_expected - 2.5:.1f} to {idw_expected + 2.5:.1f} {conf['unit']} (Spatial IDW)",
                    "ml_model": "Tier-4:IDW-SpatialNeighbor-Consistency",
                    "explanation": (
                        f"Spatial inconsistency detected on {conf['name']}: Station reports {target_val:.2f}{conf['unit']}, "
                        f"diverging by {spatial_diff:.2f}{conf['unit']} from regional neighborhood expected value "
                        f"({idw_expected:.2f}{conf['unit']} calculated across {valid_neighbors} neighboring AWS stations "
                        f"within {max_search_radius_km} km)."
                    )
                })

        return anomalies

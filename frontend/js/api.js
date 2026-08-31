/**
 * API Client for SkyGuard AI Automatic Weather Stations Anomaly Detection Platform
 * Supports both Live FastAPI Backend and Standalone Netlify Cloud Static Mode.
 */
const API = {
  baseUrl: (typeof window !== 'undefined' && (window.API_BASE_URL || localStorage.getItem('skyguard_api_url'))) || '',
  useClientFallback: false,

  // Embedded Static Data & Simulation Engine for Netlify
  _mockData: {
    stations: [
      { id: "AWS-IND-01", code: "SXR-HIMALAYA", name: "Srinagar Western Himalayas AWS", latitude: 34.0837, longitude: 74.7973, elevation_m: 1585.0, climate_zone: "Western Himalayan Alpine (J&K)", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.8, solar_charge_w: 16.2 },
      { id: "AWS-IND-02", code: "SML-PIRPANJAL", name: "Shimla Lesser Himalayas Ridge AWS", latitude: 31.1048, longitude: 77.1734, elevation_m: 2276.0, climate_zone: "Montane Subtropical (HP)", status: "OPERATIONAL", health_score: 96.1, battery_voltage: 12.5, solar_charge_w: 18.0 },
      { id: "AWS-IND-03", code: "DELHI-NCR", name: "National Capital NCR Urban AWS", latitude: 28.6139, longitude: 77.2090, elevation_m: 216.0, climate_zone: "Indo-Gangetic Plain Semi-Arid", status: "OPERATIONAL", health_score: 95.0, battery_voltage: 13.1, solar_charge_w: 22.4 },
      { id: "AWS-IND-04", code: "JPR-THAR", name: "Jaipur Thar Desert Edge AWS", latitude: 26.9124, longitude: 75.7873, elevation_m: 431.0, climate_zone: "Subtropical Arid Desert (Rajasthan)", status: "OPERATIONAL", health_score: 97.2, battery_voltage: 13.4, solar_charge_w: 24.1 },
      { id: "AWS-IND-05", code: "AMD-GULF", name: "Ahmedabad Sabarmati Basin AWS", latitude: 23.0225, longitude: 72.5714, elevation_m: 53.0, climate_zone: "Hot Semi-Arid Gujarat Plain", status: "OPERATIONAL", health_score: 96.8, battery_voltage: 12.9, solar_charge_w: 21.0 },
      { id: "AWS-IND-06", code: "MUM-KONKAN", name: "Mumbai Arabian Sea Maritime AWS", latitude: 19.0760, longitude: 72.8777, elevation_m: 14.0, climate_zone: "Tropical Monsoon Coastal (Konkan)", status: "OPERATIONAL", health_score: 94.5, battery_voltage: 12.4, solar_charge_w: 17.5 },
      { id: "AWS-IND-07", code: "BPL-VINDHYA", name: "Bhopal Central Highlands AWS", latitude: 23.2599, longitude: 77.4126, elevation_m: 527.0, climate_zone: "Central Highlands & Vindhyas (MP)", status: "OPERATIONAL", health_score: 99.0, battery_voltage: 13.0, solar_charge_w: 20.2 },
      { id: "AWS-IND-08", code: "MAHABALESHWAR", name: "Western Ghats Orographic AWS", latitude: 17.9237, longitude: 73.6586, elevation_m: 1353.0, climate_zone: "Western Ghats High Escarpment", status: "OPERATIONAL", health_score: 97.0, battery_voltage: 12.6, solar_charge_w: 15.8 },
      { id: "AWS-IND-09", code: "HYD-DECCAN", name: "Telangana Deccan Plateau AWS", latitude: 17.3850, longitude: 78.4867, elevation_m: 542.0, climate_zone: "Central Deccan Plateau (Telangana)", status: "OPERATIONAL", health_score: 96.0, battery_voltage: 12.7, solar_charge_w: 19.4 },
      { id: "AWS-IND-10", code: "BLR-MYSORE", name: "South Deccan Mysore Plateau AWS", latitude: 12.9716, longitude: 77.5946, elevation_m: 920.0, climate_zone: "South Deccan Plateau (Karnataka)", status: "OPERATIONAL", health_score: 98.5, battery_voltage: 12.8, solar_charge_w: 20.0 },
      { id: "AWS-IND-11", code: "CHENNAI-CORO", name: "Coromandel Coastal Cyclone AWS", latitude: 13.0827, longitude: 80.2707, elevation_m: 6.0, climate_zone: "Coromandel Coastal Belt (TN)", status: "OPERATIONAL", health_score: 95.8, battery_voltage: 12.9, solar_charge_w: 21.5 },
      { id: "AWS-IND-12", code: "KOCHI-MALABAR", name: "Malabar Tropical Monsoon AWS", latitude: 9.9312, longitude: 76.2673, elevation_m: 4.0, climate_zone: "Malabar Tropical Coast (Kerala)", status: "OPERATIONAL", health_score: 94.0, battery_voltage: 12.5, solar_charge_w: 16.0 },
      { id: "AWS-IND-13", code: "KOL-SUNDARBAN", name: "Kolkata Gangetic Delta AWS", latitude: 22.5726, longitude: 88.3639, elevation_m: 9.0, climate_zone: "Lower Gangetic Delta (WB)", status: "OPERATIONAL", health_score: 96.5, battery_voltage: 12.7, solar_charge_w: 18.5 },
      { id: "AWS-IND-14", code: "SHL-KHASI", name: "Cherrapunji Khasi Hills AWS", latitude: 25.2702, longitude: 91.7323, elevation_m: 1430.0, climate_zone: "Subtropical Monsoon Highlands", status: "OPERATIONAL", health_score: 97.5, battery_voltage: 12.4, solar_charge_w: 14.8 },
      { id: "AWS-IND-15", code: "GAU-BRAHMA", name: "Guwahati Brahmaputra Valley AWS", latitude: 26.1445, longitude: 91.7362, elevation_m: 55.0, climate_zone: "Brahmaputra Subtropical Valley", status: "OPERATIONAL", health_score: 97.0, battery_voltage: 12.8, solar_charge_w: 17.2 },
      { id: "AWS-IND-16", code: "IXZ-ANDAMAN", name: "Port Blair Bay of Bengal AWS", latitude: 11.6234, longitude: 92.7265, elevation_m: 16.0, climate_zone: "Tropical Maritime Island (A&N)", status: "OPERATIONAL", health_score: 95.0, battery_voltage: 12.6, solar_charge_w: 19.0 }
    ],
    anomalies: [
      {
        id: 1081,
        station_id: "AWS-IND-03",
        station_code: "DELHI-NCR",
        station_name: "National Capital NCR Urban AWS",
        timestamp: new Date().toISOString(),
        sensor: "temperature_c",
        anomaly_type: "SPIKE",
        severity: "HIGH",
        confidence_score: 0.94,
        raw_value: 53.50,
        expected_range: "19.50 to 31.50 °C",
        ml_model: "Tier-1:Dynamic-StepLimit",
        explanation: "Abrupt step jump of 25.00°C detected on temperature_c. Exceeds dynamic rate-of-change threshold.",
        status: "DETECTED",
        drift: "Transient Step Jump (Injected / Observed: 53.50 °C)",
        slope: "Instantaneous Step Rate-of-Change",
        root_cause: "ELECTROMAGNETIC_INTERFERENCE_OR_ADC_GLITCH",
        action: "Inspect and recalibrate temperature transducer",
        injected_value: "53.50 °C"
      },
      {
        id: 1082,
        station_id: "AWS-IND-04",
        station_code: "JPR-THAR",
        station_name: "Jaipur Thar Desert Edge AWS",
        timestamp: new Date(Date.now() - 900000).toISOString(),
        sensor: "humidity_pct",
        anomaly_type: "SENSOR_DRIFT",
        severity: "HIGH",
        confidence_score: 0.91,
        raw_value: 88.50,
        expected_range: "25.0 to 45.0 %",
        ml_model: "Tier-2:Magnus-DewPoint-Consistency",
        explanation: "Progressive linear drift on relative humidity. Magnus formula violation (Td > T).",
        status: "DETECTED",
        drift: "Progressive Drift (Injected / Observed: 88.50 %)",
        slope: "Monotonic Linear Drift (R² > 0.82)",
        root_cause: "CAPACITIVE_POLYMER_DEGRADATION",
        action: "Schedule laboratory salt chamber recalibration",
        injected_value: "88.50 %"
      },
      {
        id: 1083,
        station_id: "AWS-IND-06",
        station_code: "MUM-KONKAN",
        station_name: "Mumbai Arabian Sea Maritime AWS",
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        sensor: "wind_speed_ms",
        anomaly_type: "FROZEN_SENSOR",
        severity: "MEDIUM",
        confidence_score: 0.88,
        raw_value: 0.00,
        expected_range: "3.5 to 14.0 m/s",
        ml_model: "Tier-1:ZeroVariance-Flatline",
        explanation: "Zero variance flatline detected under active thermal gradient. Cup anemometer bearing seized.",
        status: "DETECTED",
        drift: "Static Constant (Injected / Observed: 0.00 m/s)",
        slope: "Zero Variance Flatline (σ < 1e-4)",
        root_cause: "MECHANICAL_BEARING_STALL_OR_ICING",
        action: "Replace cup anemometer bearing cartridge",
        injected_value: "0.00 m/s"
      }
    ],
    faults: []
  },

  async _fetchOrFallback(url, options = {}, fallbackFn) {
    if (!this.useClientFallback) {
      try {
        const res = await fetch(url, options);
        if (res.ok) return await res.json();
      } catch (err) {
        console.warn('Backend API connection unavailable, switching to Netlify Cloud Static Mode:', err);
        this.useClientFallback = true;
      }
    }
    return fallbackFn ? fallbackFn() : null;
  },

  _syncStationLiveReadings() {
    const now = new Date();
    const hour = now.getHours() + now.getMinutes() / 60.0;
    this._mockData.stations.forEach(stn => {
      // Find open active anomalies on this station
      const openAnoms = this._mockData.anomalies.filter(a => a.station_id === stn.id && a.status === 'DETECTED');
      const activeAnom = openAnoms[0] || null;

      // Base realistic diurnal readings
      let temp = 28.5 + 6.0 * Math.sin(Math.PI * (hour - 8) / 12.0) + (stn.elevation_m > 1000 ? -12.0 : (stn.elevation_m > 400 ? -4.0 : 0.0));
      let rh = Math.max(20, Math.min(95, 60.0 - (temp - 28.5) * 2.5));
      let press = 1013.25 - (stn.elevation_m * 0.11);
      let wind = 3.5 + Math.random() * 2.5;
      let solar = hour >= 6 && hour <= 18 ? Math.sin(Math.PI * (hour - 6) / 12.0) * 850 : 0.0;

      // If active anomaly exists, apply the faulty value
      if (activeAnom) {
        if (activeAnom.sensor === 'temperature_c') temp = activeAnom.raw_value;
        else if (activeAnom.sensor === 'humidity_pct') rh = activeAnom.raw_value;
        else if (activeAnom.sensor === 'pressure_hpa') press = activeAnom.raw_value;
        else if (activeAnom.sensor === 'wind_speed_ms') wind = activeAnom.raw_value;
        else if (activeAnom.sensor === 'solar_radiation_wm2') solar = activeAnom.raw_value;
      }

      stn.latest_reading = {
        station_id: stn.id,
        timestamp: now.toISOString(),
        temperature_c: parseFloat(temp.toFixed(2)),
        humidity_pct: parseFloat(rh.toFixed(1)),
        pressure_hpa: parseFloat(press.toFixed(2)),
        wind_speed_ms: parseFloat(wind.toFixed(2)),
        solar_radiation_wm2: parseFloat(solar.toFixed(1)),
        dew_point_c: parseFloat((temp - ((100 - rh) / 5)).toFixed(2)),
        battery_v: 12.6,
        is_anomaly: !!activeAnom,
        active_anomaly: activeAnom
      };
      stn.active_anomalies = openAnoms;
      stn.active_anomalies_count = openAnoms.length;
      stn.status = activeAnom ? (activeAnom.severity === 'CRITICAL' ? 'CRITICAL' : 'DEGRADED') : 'OPERATIONAL';
      stn.health_score = activeAnom ? (activeAnom.severity === 'CRITICAL' ? 64.0 : 78.5) : 98.4;
    });
  },

  async getStations() {
    this._syncStationLiveReadings();
    return this._fetchOrFallback(`${this.baseUrl}/api/stations`, {}, () => {
      this._syncStationLiveReadings();
      return this._mockData.stations;
    });
  },

  async getStationDetail(stationId) {
    this._syncStationLiveReadings();
    return this._fetchOrFallback(`${this.baseUrl}/api/stations/${stationId}`, {}, () => {
      this._syncStationLiveReadings();
      return this._mockData.stations.find(s => s.id === stationId) || this._mockData.stations[0];
    });
  },


  async getStationReadings(stationId, limit = 100) {
    return this._fetchOrFallback(`${this.baseUrl}/api/stations/${stationId}/readings?limit=${limit}`, {}, () => {
      const readings = [];
      const now = Date.now();
      const baseTemp = 28.5;
      for (let i = limit - 1; i >= 0; i--) {
        const ts = new Date(now - i * 15 * 60 * 1000);
        const hour = ts.getHours() + ts.getMinutes() / 60.0;
        const temp = baseTemp + 6.0 * Math.sin(Math.PI * (hour - 8) / 12.0) + (Math.random() - 0.5);
        const rh = Math.max(20, Math.min(95, 60.0 - (temp - baseTemp) * 3.0 + (Math.random() - 0.5) * 2));
        const press = 1013.25 + 1.5 * Math.cos(Math.PI * (hour - 9) / 6.0) + (Math.random() - 0.5) * 0.4;
        readings.push({
          station_id: stationId,
          timestamp: ts.toISOString(),
          temperature_c: parseFloat(temp.toFixed(2)),
          humidity_pct: parseFloat(rh.toFixed(1)),
          pressure_hpa: parseFloat(press.toFixed(2)),
          wind_speed_ms: parseFloat((3.5 + Math.random() * 3.0).toFixed(2)),
          solar_radiation_wm2: hour >= 6 && hour <= 18 ? parseFloat((Math.sin(Math.PI * (hour - 6) / 12.0) * 850).toFixed(1)) : 0.0,
          dew_point_c: parseFloat((temp - ((100 - rh) / 5)).toFixed(2)),
          battery_v: 12.6,
          is_anomaly: i === 0 && this._mockData.anomalies.some(a => a.station_id === stationId && a.status === 'DETECTED'),
          anomaly_score: i === 0 ? 0.95 : 0.02
        });
      }
      return readings;
    });
  },

  async getAnomalies(filters = {}) {
    const params = new URLSearchParams();
    if (filters.station_id) params.append('station_id', filters.station_id);
    if (filters.severity) params.append('severity', filters.severity);
    if (filters.status) params.append('status', filters.status);
    if (filters.anomaly_type) params.append('anomaly_type', filters.anomaly_type);
    if (filters.limit) params.append('limit', filters.limit);

    return this._fetchOrFallback(`${this.baseUrl}/api/anomalies?${params.toString()}`, {}, () => {
      return this._mockData.anomalies.filter(a => {
        if (filters.station_id && a.station_id !== filters.station_id) return false;
        if (filters.severity && a.severity !== filters.severity.toUpperCase()) return false;
        if (filters.status && a.status !== filters.status.toUpperCase()) return false;
        if (filters.anomaly_type && a.anomaly_type !== filters.anomaly_type) return false;
        return true;
      });
    });
  },

  async getAnomalyStats() {
    return this._fetchOrFallback(`${this.baseUrl}/api/anomalies/stats`, {}, () => {
      const active = this._mockData.anomalies.filter(a => a.status === 'DETECTED').length;
      const crit = this._mockData.anomalies.filter(a => a.status === 'DETECTED' && a.severity === 'CRITICAL').length;
      return {
        total_stations: this._mockData.stations.length,
        active_unresolved: active,
        critical_unresolved: crit,
        accuracy_rate: 98.8,
        f1_score: 0.948
      };
    });
  },

  async triageAnomaly(anomalyId, status, triageNotes = '') {
    return this._fetchOrFallback(`${this.baseUrl}/api/anomalies/${anomalyId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, triage_notes: triageNotes })
    }, () => {
      const target = this._mockData.anomalies.find(a => a.id === anomalyId);
      if (target) target.status = status;
      return { status: "UPDATED", anomaly_id: anomalyId, new_status: status };
    });
  },

  async resetActiveAnomalies() {
    return this._fetchOrFallback(`${this.baseUrl}/api/anomalies/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, () => {
      const count = this._mockData.anomalies.filter(a => a.status === 'DETECTED').length;
      this._mockData.anomalies.forEach(a => {
        if (a.status === 'DETECTED') a.status = 'RESOLVED';
      });
      this._mockData.stations.forEach(s => {
        s.status = 'OPERATIONAL';
        s.health_score = 100.0;
      });
      return { status: "SUCCESS", resetted_count: count, active_remaining: 0 };
    });
  },

  async injectFault(stationId, anomalyType, sensor, magnitude, durationSteps = 5) {
    return this._fetchOrFallback(`${this.baseUrl}/api/simulate/inject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        station_id: stationId,
        anomaly_type: anomalyType,
        sensor: sensor,
        magnitude: parseFloat(magnitude),
        duration_steps: parseInt(durationSteps)
      })
    }, () => {
      this._mockData.faults.push({ stationId, anomalyType, sensor, magnitude, durationSteps });
      return { status: "INJECTED", station_id: stationId };
    });
  },

  async stepSimulation() {
    return this._fetchOrFallback(`${this.baseUrl}/api/simulate/step`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, () => {
      let created = 0;
      if (this._mockData.faults.length > 0) {
        const fault = this._mockData.faults.shift();
        const stn = this._mockData.stations.find(s => s.id === fault.stationId) || this._mockData.stations[0];
        const units = { temperature_c: '°C', humidity_pct: '%', pressure_hpa: 'hPa', wind_speed_ms: 'm/s', solar_radiation_wm2: 'W/m²' };
        const unit = units[fault.sensor] || '';
        const base = fault.sensor === 'temperature_c' ? 28.5 : fault.sensor === 'humidity_pct' ? 55.0 : 1013.25;
        const faultyVal = (base + fault.magnitude).toFixed(2);

        this._mockData.anomalies.unshift({
          id: Math.floor(Math.random() * 90000) + 10000,
          station_id: stn.id,
          station_code: stn.code,
          station_name: stn.name,
          timestamp: new Date().toISOString(),
          sensor: fault.sensor,
          anomaly_type: fault.anomalyType,
          severity: Math.abs(fault.magnitude) > 20 ? "CRITICAL" : "HIGH",
          confidence_score: 0.96,
          raw_value: parseFloat(faultyVal),
          expected_range: `${base.toFixed(1)} ${unit}`,
          ml_model: "Tier-1:Dynamic-StepLimit",
          explanation: `Injected synthetic ${fault.anomalyType} fault with magnitude offset ${fault.magnitude > 0 ? '+' : ''}${fault.magnitude}${unit}.`,
          status: "DETECTED",
          drift: `${fault.anomalyType} (${faultyVal} ${unit})`,
          slope: "Instantaneous Step Rate-of-Change",
          root_cause: "SYNTHETIC_FAULT_INJECTION_STUDIO",
          action: "Inspect and recalibrate sensor transducer element",
          injected_value: `${faultyVal} ${unit}`
        });
        created = 1;
        stn.status = "CRITICAL";
        stn.health_score = 64.0;
      } else {
        // Natural live stream background anomaly generation (~35% chance per step)
        if (Math.random() < 0.35) {
          const randomStn = this._mockData.stations[Math.floor(Math.random() * this._mockData.stations.length)];
          const sampleFaults = [
            { sensor: 'temperature_c', type: 'SPIKE', mag: +(Math.random() * 8 + 18).toFixed(1), unit: '°C', base: 28.5, model: 'Tier-1:Dynamic-StepLimit', drift: 'Transient Step Jump', cause: 'THERMAL_SURGE_OR_ADC_GLITCH' },
            { sensor: 'humidity_pct', type: 'SENSOR_DRIFT', mag: +(Math.random() * 15 + 20).toFixed(1), unit: '%', base: 55.0, model: 'Tier-2:Magnus-DewPoint', drift: 'Progressive Drift', cause: 'CAPACITIVE_POLYMER_DEGRADATION' },
            { sensor: 'wind_speed_ms', type: 'FROZEN_SENSOR', mag: 0.0, unit: 'm/s', base: 4.5, model: 'Tier-1:ZeroVariance-Flatline', drift: 'Constant Flatline', cause: 'ANEMOMETER_BEARING_STALL' },
            { sensor: 'dew_point_c', type: 'CROSS_SENSOR_INCONSISTENCY', mag: 6.5, unit: '°C', base: 22.0, model: 'Tier-2:Magnus-Inconsistency', drift: 'Thermodynamic Inconsistency (Td > T)', cause: 'PSYCHROMETRIC_VIOLATION' }
          ];
          const chosen = sampleFaults[Math.floor(Math.random() * sampleFaults.length)];
          const faultyVal = chosen.type === 'FROZEN_SENSOR' ? '0.00' : (chosen.base + chosen.mag).toFixed(2);
          this._mockData.anomalies.unshift({
            id: Math.floor(Math.random() * 90000) + 10000,
            station_id: randomStn.id,
            station_code: randomStn.code,
            station_name: randomStn.name,
            timestamp: new Date().toISOString(),
            sensor: chosen.sensor,
            anomaly_type: chosen.type,
            severity: chosen.mag > 20 || chosen.type === 'SPIKE' ? 'CRITICAL' : 'HIGH',
            confidence_score: 0.94,
            raw_value: parseFloat(faultyVal),
            expected_range: `${chosen.base.toFixed(1)} ${chosen.unit}`,
            ml_model: chosen.model,
            explanation: `Live Stream AI Sentinel detected ${chosen.type} on ${chosen.sensor}.`,
            status: "DETECTED",
            drift: `${chosen.drift} (${faultyVal} ${chosen.unit})`,
            slope: "Real-time Telemetry Vector",
            root_cause: chosen.cause,
            action: "Inspect and recalibrate sensor transducer element",
            injected_value: `${faultyVal} ${chosen.unit}`
          });
          created = 1;
          randomStn.status = chosen.type === 'SPIKE' ? 'CRITICAL' : 'DEGRADED';
          randomStn.health_score = Math.max(30, randomStn.health_score - 15);
        }
      }
      return { status: "STEP_ADVANCED", anomalies_detected: created };
    });
  },


  async clearFaults(stationId = null) {
    return this._fetchOrFallback(`${this.baseUrl}/api/simulate/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(stationId ? { station_id: stationId } : {})
    }, () => {
      this._mockData.faults = [];
      return { status: "CLEARED" };
    });
  },

  async getModelMetrics() {
    return this._fetchOrFallback(`${this.baseUrl}/api/models/metrics`, {}, () => ({
      confusion_matrix: { true_positive: 384, false_positive: 14, false_negative: 28, true_negative: 8420, precision: 0.965, recall: 0.932, f1_score: 0.948 },
      feature_importance: [
        { feature: "Dew Point Depression (T - Td)", weight: 0.32, tier: "Tier-2: Thermodynamics" },
        { feature: "Instantaneous Rate-of-Change", weight: 0.26, tier: "Tier-1: WMO-No.8" },
        { feature: "Spatial IDW Consensus Deviation", weight: 0.21, tier: "Tier-4: Spatial" },
        { feature: "Isolation Forest Anomaly Score", weight: 0.14, tier: "Tier-3: ML" },
        { feature: "Nocturnal Solar Radiation Flux", weight: 0.07, tier: "Tier-2: Astronomical" }
      ],
      algorithm_stack: [
        { name: "Tier-1: Physical Bounds & Rate-of-Change", type: "Physics Limit Rulebook", latency_ms: 0.04 },
        { name: "Tier-2: Clausius-Clapeyron Thermodynamics", type: "Psychrometric Invariant", latency_ms: 0.08 },
        { name: "Tier-3: Pure-NumPy Isolation Forest", type: "Unsupervised Multivariate Ensemble", latency_ms: 0.28 },
        { name: "Tier-4: Spatial Inverse Distance Weighting", type: "Regional Neighborhood Consensus", latency_ms: 0.42 }
      ]
    }));
  },

  async getPlotlyMap() {
    return this._fetchOrFallback(`${this.baseUrl}/api/analytics/plotly-map`, {}, () => {
      const isLight = typeof document !== 'undefined' && document.body.classList.contains('light');
      return {
        data: [{
          type: "scattermapbox",
          lat: this._mockData.stations.map(s => s.latitude),
          lon: this._mockData.stations.map(s => s.longitude),
          mode: "markers+text",
          marker: { size: 14, color: "#06b6d4" },
          text: this._mockData.stations.map(s => s.name),
          textposition: "bottom right"
        }],
        layout: {
          mapbox: { style: isLight ? "open-street-map" : "carto-darkmatter", center: { lat: 22.5, lon: 79.5 }, zoom: 3.8 },
          margin: { l: 0, r: 0, t: 0, b: 0 }
        }
      };
    });
  },

  async getPlotly3dScatter() {
    return this._fetchOrFallback(`${this.baseUrl}/api/analytics/plotly-3d-scatter`, {}, () => ({
      data: [{
        type: "scatter3d",
        mode: "markers",
        x: [24, 28, 31, 22, 53.5, 30, 26],
        y: [55, 60, 45, 80, 88.5, 50, 65],
        z: [1013, 1012, 1010, 1015, 950, 1014, 1011],
        marker: { size: 5, color: ["#06b6d4", "#06b6d4", "#06b6d4", "#06b6d4", "#ef4444", "#06b6d4", "#06b6d4"] }
      }],
      layout: {
        scene: {
          xaxis: { title: "Air Temp (°C)" },
          yaxis: { title: "Humidity (%)" },
          zaxis: { title: "Pressure (hPa)" }
        },
        margin: { l: 0, r: 0, t: 0, b: 0 }
      }
    }));
  },

  async getPlotlyFeatureImportance() {
    return this._fetchOrFallback(`${this.baseUrl}/api/analytics/plotly-feature-importance`, {}, () => ({
      data: [{
        type: "bar",
        orientation: "h",
        y: ["Astronomical Solar", "Isolation Forest ML", "Spatial IDW", "Step Rate-of-Change", "Thermodynamic T-Td"],
        x: [0.07, 0.14, 0.21, 0.26, 0.32],
        marker: { color: ["#38bdf8", "#818cf8", "#c084fc", "#fb923c", "#f43f5e"] }
      }],
      layout: { margin: { l: 150, r: 20, t: 10, b: 30 } }
    }));
  }
};








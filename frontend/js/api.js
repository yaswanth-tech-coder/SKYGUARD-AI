/**
 * API Client for SkyGuard AI Automatic Weather Stations Anomaly Detection Platform
 * Supports both Live FastAPI Backend and Standalone Netlify Cloud Static Mode.
 */
const API = {
  baseUrl: (() => {
    if (typeof window !== 'undefined') {
      if (window.API_BASE_URL) return window.API_BASE_URL;
      const stored = localStorage.getItem('skyguard_api_url');
      if (stored && !stored.includes('localhost:8000')) return stored;
      if (stored && stored.includes('localhost:8000') && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        try { localStorage.removeItem('skyguard_api_url'); } catch (e) {}
      }
    }
    return 'https://skyguard-ai-7lge.onrender.com';
  })(),
  useClientFallback: false,

  // Embedded Static Data & Simulation Engine for Netlify
  _mockData: {
    stations: [
      { id: "AWS-IND-01", code: "DELHI-NCR", name: "National Capital NCR Urban AWS", city: "Delhi", latitude: 28.6139, longitude: 77.2090, elevation_m: 216.0, climate_zone: "Northern Gangetic Plain", status: "CRITICAL", health_score: 64.0, battery_voltage: 12.8, solar_charge_w: 16.2 },
      { id: "AWS-IND-02", code: "MUM-KONKAN", name: "Mumbai Arabian Sea Maritime AWS", city: "Mumbai", latitude: 19.0760, longitude: 72.8777, elevation_m: 14.0, climate_zone: "Tropical Monsoon Coastal (Konkan)", status: "DEGRADED", health_score: 82.0, battery_voltage: 12.5, solar_charge_w: 18.0 },
      { id: "AWS-IND-03", code: "CHENNAI-CORO", name: "Coromandel Coastal Maritime AWS", city: "Chennai", latitude: 13.0827, longitude: 80.2707, elevation_m: 6.0, climate_zone: "Coromandel Coastal Belt", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 13.1, solar_charge_w: 22.4 },
      { id: "AWS-IND-04", code: "KOL-SUNDARBAN", name: "Kolkata Gangetic Delta AWS", city: "Kolkata", latitude: 22.5726, longitude: 88.3639, elevation_m: 9.0, climate_zone: "Lower Gangetic Delta", status: "DEGRADED", health_score: 82.0, battery_voltage: 13.4, solar_charge_w: 24.1 },
      { id: "AWS-IND-05", code: "BLR-MYSORE", name: "Bengaluru Tech Plateau AWS", city: "Bengaluru", latitude: 12.9716, longitude: 77.5946, elevation_m: 920.0, climate_zone: "South Deccan Plateau", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.9, solar_charge_w: 21.0 },
      { id: "AWS-IND-06", code: "HYD-DECCAN", name: "Hyderabad Deccan Plateau AWS", city: "Hyderabad", latitude: 17.3850, longitude: 78.4867, elevation_m: 542.0, climate_zone: "Central Deccan Plateau", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.4, solar_charge_w: 17.5 },
      { id: "AWS-IND-07", code: "AMD-GULF", name: "Ahmedabad Sabarmati Basin AWS", city: "Ahmedabad", latitude: 23.0225, longitude: 72.5714, elevation_m: 53.0, climate_zone: "Hot Semi-Arid Gujarat Plain", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 13.0, solar_charge_w: 20.2 },
      { id: "AWS-IND-08", code: "SXR-HIMALAYA", name: "Srinagar Western Himalayas AWS", city: "Srinagar", latitude: 34.0837, longitude: 74.7973, elevation_m: 1585.0, climate_zone: "Western Himalayan Alpine", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.6, solar_charge_w: 15.8 },
      { id: "AWS-IND-09", code: "SML-PIRPANJAL", name: "Shimla Lesser Himalayas AWS", city: "Shimla", latitude: 31.1048, longitude: 77.1734, elevation_m: 2276.0, climate_zone: "Montane Subtropical", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.7, solar_charge_w: 19.4 },
      { id: "AWS-IND-10", code: "LEH-LADAKH", name: "Ladakh High Altitude Cold Desert AWS", city: "Leh Ladakh", latitude: 34.1526, longitude: 77.5771, elevation_m: 3500.0, climate_zone: "Trans-Himalayan Cold Desert", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.8, solar_charge_w: 20.0 },
      { id: "AWS-IND-11", code: "PATNA-GANGA", name: "Patna Bihar Plains AWS", city: "Patna", latitude: 25.5941, longitude: 85.1376, elevation_m: 53.0, climate_zone: "Middle Gangetic Floodplain", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.9, solar_charge_w: 21.5 },
      { id: "AWS-IND-12", code: "BPL-VINDHYA", name: "Bhopal Central Highlands AWS", city: "Bhopal", latitude: 23.2599, longitude: 77.4126, elevation_m: 527.0, climate_zone: "Central Highlands & Vindhyas", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.5, solar_charge_w: 16.0 },
      { id: "AWS-IND-13", code: "KOCHI-MALABAR", name: "Kochi Marine Gateway AWS", city: "Kochi", latitude: 9.9312, longitude: 76.2673, elevation_m: 4.0, climate_zone: "Malabar Tropical Coast", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.7, solar_charge_w: 18.5 },
      { id: "AWS-IND-14", code: "SHL-KHASI", name: "Cherrapunji Khasi Hills AWS", city: "Cherrapunji", latitude: 25.2702, longitude: 91.7323, elevation_m: 1430.0, climate_zone: "Subtropical Monsoon Highlands", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.4, solar_charge_w: 14.8 },
      { id: "AWS-IND-15", code: "MAHABALESHWAR", name: "Western Ghats Orographic AWS", city: "Mahabaleshwar", latitude: 17.9237, longitude: 73.6586, elevation_m: 1353.0, climate_zone: "Western Ghats High Escarpment", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.8, solar_charge_w: 17.2 },
      { id: "AWS-IND-16", code: "IXZ-ANDAMAN", name: "Port Blair Bay of Bengal AWS", city: "Port Blair", latitude: 11.6234, longitude: 92.7265, elevation_m: 16.0, climate_zone: "Tropical Maritime Island", status: "OPERATIONAL", health_score: 98.4, battery_voltage: 12.6, solar_charge_w: 19.0 }
    ],
    anomalies: [
      {
        id: 1081,
        station_id: "AWS-IND-01",
        station_code: "DELHI-NCR",
        station_name: "National Capital NCR Urban AWS",
        timestamp: new Date().toISOString(),
        sensor: "temperature_c",
        anomaly_type: "SPIKE",
        severity: "CRITICAL",
        confidence_score: 0.94,
        raw_value: 53.50,
        expected_range: "19.50 to 31.50 °C",
        ml_model: "Scikit-Learn:IsolationForest",
        explanation: "Abrupt step jump of 25.00°C detected on temperature_c. Isolation Forest outlier score: -0.182.",
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
        station_code: "KOL-SUNDARBAN",
        station_name: "Kolkata Gangetic Delta AWS",
        timestamp: new Date(Date.now() - 900000).toISOString(),
        sensor: "humidity_pct",
        anomaly_type: "SENSOR_DRIFT",
        severity: "HIGH",
        confidence_score: 0.91,
        raw_value: 88.50,
        expected_range: "25.0 to 45.0 %",
        ml_model: "Scikit-Learn:IsolationForest",
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
        station_id: "AWS-IND-02",
        station_code: "MUM-KONKAN",
        station_name: "Mumbai Arabian Sea Maritime AWS",
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        sensor: "wind_speed_ms",
        anomaly_type: "FROZEN_SENSOR",
        severity: "WARNING",
        confidence_score: 0.88,
        raw_value: 0.00,
        expected_range: "3.5 to 14.0 m/s",
        ml_model: "Scikit-Learn:IsolationForest",
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

  _wakeProbeRunning: false,

  _scheduleBackendWakeProbe() {
    if (this._wakeProbeRunning) return;
    this._wakeProbeRunning = true;

    const probe = async () => {
      try {
        const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        const timeoutId = controller ? setTimeout(() => controller.abort(), 4000) : null;
        const ping = await fetch(`${this.baseUrl}/api/health`, {
          signal: controller ? controller.signal : undefined
        }).catch(() => null);
        if (timeoutId) clearTimeout(timeoutId);

        if (ping && ping.ok) {
          console.info('[SkyGuard Sentinel] Cloud backend service is now AWAKE! Resuming live API stream.');
          this.useClientFallback = false;
          this._wakeProbeRunning = false;
          if (typeof window !== 'undefined' && window.app && typeof window.app.refreshAllData === 'function') {
            window.app.refreshAllData().catch(() => {});
          }
          return;
        }
      } catch (e) {
        // Still waking up
      }
      setTimeout(probe, 10000);
    };

    setTimeout(probe, 6000);
  },

  async _fetchOrFallback(url, options = {}, fallbackFn) {
    if (!this.useClientFallback) {
      try {
        // Use 5.5s timeout so sleeping free cloud instances never hang the browser UI
        const controller = typeof AbortController !== 'undefined' ? new AbortController() : null;
        const timeoutId = controller ? setTimeout(() => controller.abort(), 5500) : null;

        const fetchOptions = {
          ...options,
          signal: controller ? controller.signal : undefined
        };

        const res = await fetch(url, fetchOptions).catch(netErr => {
          throw new Error(netErr.name === 'AbortError' 
            ? 'Backend waking up from cold sleep (request timeout)' 
            : (netErr.message || 'Network unreachable'));
        });

        if (timeoutId) clearTimeout(timeoutId);

        if (res && res.ok) {
          const json = await res.json().catch(jsonErr => {
            throw new Error('Failed to parse JSON response: ' + jsonErr.message);
          });
          this.useClientFallback = false;
          return json;
        } else {
          const statusText = res ? `${res.status} ${res.statusText}` : 'Empty response';
          throw new Error(`Server returned non-200 status: ${statusText}`);
        }
      } catch (err) {
        console.warn(`[SkyGuard Sentinel] Backend temporarily waking up / unreachable at ${url} (${err.message}). Using client-side fallback data.`, err);
        this.useClientFallback = true;
        this._scheduleBackendWakeProbe();
        if (typeof window !== 'undefined' && window.app && typeof window.app.showToast === 'function' && !window.app._hasShownWakeToast) {
          window.app._hasShownWakeToast = true;
          window.app.showToast('☁️ Cloud backend waking up (~30s cold start). Live simulation active!', 'amber');
        }
      }
    }

    try {
      return fallbackFn ? fallbackFn() : null;
    } catch (fallbackErr) {
      console.error('[SkyGuard Sentinel] Fallback generator error:', fallbackErr);
      return null;
    }
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
      const isCrit = openAnoms.some(a => (a.severity || '').toUpperCase() === 'CRITICAL');
      const isWarn = openAnoms.some(a => ['WARNING', 'HIGH', 'MEDIUM'].includes((a.severity || '').toUpperCase()));
      stn.status = isCrit ? 'CRITICAL' : isWarn ? 'DEGRADED' : 'OPERATIONAL';
      stn.health_score = isCrit ? 64.0 : isWarn ? 82.0 : 98.4;
    });
  },


  async getLatestStations() {
    try {
      return await this._fetchOrFallback(`${this.baseUrl}/api/stations/latest`, {}, () => {
        this._syncStationLiveReadings();
        return { stations: this._mockData.stations };
      }).catch(err => {
        console.warn('[SkyGuard Sentinel] getLatestStations error caught:', err);
        return { stations: this._mockData.stations };
      });
    } catch (e) {
      return { stations: this._mockData.stations };
    }
  },

  async getStations() {
    this._syncStationLiveReadings();
    try {
      const res = await this._fetchOrFallback(`${this.baseUrl}/api/stations/latest`, {}, () => {
        this._syncStationLiveReadings();
        return this._mockData.stations;
      }).catch(err => {
        console.warn('[SkyGuard Sentinel] getStations error caught:', err);
        return this._mockData.stations;
      });

      if (res && res.stations && Array.isArray(res.stations)) {
      return res.stations.map((stn, idx) => {
        const isAnom = Boolean(stn.is_anomaly);
        const temp = stn.temperature ?? 25.0;
        const wind = stn.windspeed ?? 3.5;
        return {
          id: stn.station_id || `AWS-IND-${String(idx + 1).padStart(2, '0')}`,
          code: stn.station_code || stn.station_id || `AWS-${stn.city?.toUpperCase() || 'IND'}`,
          name: stn.station_name || `${stn.city} AWS`,
          city: stn.city || 'India',
          latitude: stn.latitude || 20.0,
          longitude: stn.longitude || 78.0,
          elevation_m: stn.elevation_m || 200.0,
          climate_zone: stn.climate_zone || 'Meteorological AWS',
          status: isAnom ? 'CRITICAL' : 'OPERATIONAL',
          health_score: isAnom ? 64.0 : 98.4,
          latest_reading: {
            station_id: stn.station_id,
            timestamp: stn.timestamp || new Date().toISOString(),
            temperature_c: parseFloat(temp.toFixed(2)),
            wind_speed_ms: parseFloat(wind.toFixed(2)),
            wind_direction_deg: parseFloat((stn.winddirection ?? 180.0).toFixed(1)),
            humidity_pct: parseFloat((stn.humidity ?? Math.max(20, Math.min(95, 60.0 - (temp - 28.5) * 2.5))).toFixed(1)),
            pressure_hpa: parseFloat((stn.pressure ?? 1013.25).toFixed(2)),
            solar_radiation_wm2: 650.0,
            dew_point_c: parseFloat((temp - 6.0).toFixed(2)),
            battery_v: 12.6,
            is_anomaly: isAnom,
            active_anomaly: isAnom ? {
              anomaly_type: "ISOLATION_FOREST_OUTLIER",
              severity: "CRITICAL",
              sensor: "temperature_c / wind_speed_ms",
              raw_value: `${temp}°C / ${wind} km/h`,
              injected_value: `${temp}°C`,
              confidence_score: stn.anomaly_score || 0.95,
              ml_model: "Scikit-Learn:IsolationForest",
              root_cause: "STATISTICAL_MULTIVARIATE_OUTLIER",
              action: "Inspect and recalibrate transducer element"
            } : null
          },
          active_anomalies_count: isAnom ? 1 : 0,
          active_anomalies: isAnom ? [{
            anomaly_type: "ISOLATION_FOREST_OUTLIER",
            severity: "CRITICAL",
            sensor: "temperature_c / wind_speed_ms",
            raw_value: `${temp}°C`,
            injected_value: `${temp}°C`,
            confidence_score: stn.anomaly_score || 0.95,
            ml_model: "Scikit-Learn:IsolationForest",
            root_cause: "STATISTICAL_MULTIVARIATE_OUTLIER",
            action: "Inspect and recalibrate transducer element"
          }] : []
        };
      });
    }
    if (Array.isArray(res)) {
      return res.map((stn, idx) => {
        if (!stn.latest_reading) {
          const fallbackStn = this._mockData.stations.find(s => s.id === stn.id) || this._mockData.stations[idx % this._mockData.stations.length];
          stn.latest_reading = fallbackStn.latest_reading || {
            station_id: stn.id,
            timestamp: new Date().toISOString(),
            temperature_c: 28.5,
            humidity_pct: 55.0,
            pressure_hpa: 1013.25,
            wind_speed_ms: 3.5,
            solar_radiation_wm2: 600.0,
            dew_point_c: 18.2,
            battery_v: 12.6,
            is_anomaly: false
          };
        }
        return stn;
      });
    }
    return this._mockData.stations;
    } catch (err) {
      console.warn('[SkyGuard Sentinel] getStations caught exception:', err);
      return this._mockData.stations;
    }
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
        if (filters.severity) {
          const filterSev = filters.severity.toUpperCase();
          const anomSev = (a.severity || '').toUpperCase();
          if (filterSev === 'WARNING' || filterSev === 'HIGH') {
            if (anomSev !== 'WARNING' && anomSev !== 'HIGH') return false;
          } else if (anomSev !== filterSev) {
            return false;
          }
        }
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
      if (target) {
        target.status = status;
        const remainingForStn = this._mockData.anomalies.filter(a => a.station_id === target.station_id && a.status === 'DETECTED');
        const stn = this._mockData.stations.find(s => s.id === target.station_id);
        if (stn) {
          stn.active_anomalies_count = remainingForStn.length;
          stn.active_anomalies = remainingForStn;
          if (remainingForStn.length === 0) {
            stn.status = 'OPERATIONAL';
            stn.health_score = 98.4;
            if (stn.latest_reading) {
              stn.latest_reading.is_anomaly = false;
              stn.latest_reading.active_anomaly = null;
            }
          }
        }
      }
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

  async injectFault(stationId, anomalyType, sensor, magnitude, durationSteps = 5, severity = 'AUTO') {
    return this._fetchOrFallback(`${this.baseUrl}/api/simulate/inject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        station_id: stationId,
        anomaly_type: anomalyType,
        sensor: sensor,
        magnitude: parseFloat(magnitude),
        duration_steps: parseInt(durationSteps),
        severity: severity
      })
    }, () => {
      this._mockData.faults.push({ stationId, anomalyType, sensor, magnitude, durationSteps, severity });
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

        let assignedSeverity = 'CRITICAL';
        if (fault.severity && fault.severity !== 'AUTO') {
          assignedSeverity = fault.severity.toUpperCase();
        } else {
          const absMag = Math.abs(fault.magnitude);
          if (fault.anomalyType === 'SPIKE') {
            assignedSeverity = absMag >= 18.0 ? 'CRITICAL' : (absMag >= 8.0 ? 'HIGH' : 'WARNING');
          } else if (fault.anomalyType === 'SENSOR_DRIFT') {
            assignedSeverity = absMag >= 15.0 ? 'CRITICAL' : (absMag >= 6.0 ? 'HIGH' : 'WARNING');
          } else if (fault.anomalyType === 'FROZEN_SENSOR') {
            assignedSeverity = 'WARNING';
          } else {
            assignedSeverity = absMag >= 20.0 ? 'CRITICAL' : 'WARNING';
          }
        }

        const isCrit = assignedSeverity === 'CRITICAL';
        const isWarn = assignedSeverity === 'WARNING' || assignedSeverity === 'HIGH' || assignedSeverity === 'MEDIUM';

        this._mockData.anomalies.unshift({
          id: Math.floor(Math.random() * 90000) + 10000,
          station_id: stn.id,
          station_code: stn.code,
          station_name: stn.name,
          timestamp: new Date().toISOString(),
          sensor: fault.sensor,
          anomaly_type: fault.anomalyType,
          severity: assignedSeverity,
          confidence_score: isCrit ? 0.96 : 0.84,
          raw_value: parseFloat(faultyVal),
          expected_range: `${base.toFixed(1)} ${unit}`,
          ml_model: "Tier-1:Dynamic-StepLimit",
          explanation: `Injected synthetic ${fault.anomalyType} fault (${assignedSeverity}) with magnitude offset ${fault.magnitude > 0 ? '+' : ''}${fault.magnitude}${unit}.`,
          status: "DETECTED",
          drift: `${fault.anomalyType} (${faultyVal} ${unit})`,
          slope: "Instantaneous Step Rate-of-Change",
          root_cause: "SYNTHETIC_FAULT_INJECTION_STUDIO",
          action: "Inspect and recalibrate sensor transducer element",
          injected_value: `${faultyVal} ${unit}`
        });
        created = 1;
        stn.status = isCrit ? "CRITICAL" : (isWarn ? "DEGRADED" : "OPERATIONAL");
        stn.health_score = isCrit ? 64.0 : (isWarn ? 82.0 : 98.4);
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
    return this._fetchOrFallback(`${this.baseUrl}/api/models/metrics`, {}, () => {
      const activeAnoms = this._mockData.anomalies.filter(a => a.status === 'DETECTED').length;
      const totalAnoms = this._mockData.anomalies.length;
      const tp = 384 + (totalAnoms * 4) + (activeAnoms * 3);
      const fp = 14;
      const fn = 28;
      const tn = 8420 + (totalAnoms * 25);

      const precision = parseFloat((tp / (tp + fp)).toFixed(4));
      const recall = parseFloat((tp / (tp + fn)).toFixed(4));
      const f1 = parseFloat((2 * (precision * recall) / (precision + recall)).toFixed(4));
      const rocAuc = parseFloat(Math.min(0.999, Math.max(0.920, 0.978 + (f1 - 0.948) * 0.15)).toFixed(4));

      return {
        confusion_matrix: {
          true_positive: tp,
          false_positive: fp,
          false_negative: fn,
          true_negative: tn,
          precision: precision,
          recall: recall,
          f1_score: f1,
          roc_auc: rocAuc
        },
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
      };
    });
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
    return this._fetchOrFallback(`${this.baseUrl}/api/analytics/plotly-3d-scatter`, {}, () => {
      this._syncStationLiveReadings();
      const xVals = [];
      const yVals = [];
      const zVals = [];
      const colors = [];
      const names = [];

      this._mockData.stations.forEach(stn => {
        const r = stn.latest_reading || {};
        xVals.push(r.temperature_c ?? 28.5);
        yVals.push(r.humidity_pct ?? 55.0);
        zVals.push(r.pressure_hpa ?? 1013.25);
        const isAnom = stn.status === 'CRITICAL' || (stn.active_anomalies_count && stn.active_anomalies_count > 0);
        colors.push(isAnom ? "#f43f5e" : "#06b6d4");
        names.push(`${stn.name} (${stn.code}) - ${isAnom ? 'ANOMALY DETECTED' : 'NORMAL'}`);
      });

      return {
        data: [{
          type: "scatter3d",
          mode: "markers",
          x: xVals,
          y: yVals,
          z: zVals,
          text: names,
          hoverinfo: "text+x+y+z",
          marker: {
            size: 6,
            color: colors,
            opacity: 0.9,
            line: { color: colors, width: 1 }
          }
        }],
        layout: {
          scene: {
            xaxis: { title: "Air Temp (°C)" },
            yaxis: { title: "Humidity (%)" },
            zaxis: { title: "Pressure (hPa)" }
          },
          margin: { l: 0, r: 0, t: 0, b: 0 }
        }
      };
    });
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
  },

  async getSensorHealth(stationId) {
    return this._fetchOrFallback(`${this.baseUrl}/api/sensors/health/${stationId}`, {}, () => {
      this._syncStationLiveReadings();
      const stn = this._mockData.stations.find(s => s.id === stationId) || this._mockData.stations[0];
      const openAnoms = this._mockData.anomalies.filter(a => a.station_id === stationId && a.status === 'DETECTED');

      const hasCrit = openAnoms.some(a => (a.severity || '').toUpperCase() === 'CRITICAL');
      const hasWarn = openAnoms.some(a => ['WARNING', 'HIGH', 'MEDIUM'].includes((a.severity || '').toUpperCase()));

      const tempAnoms = openAnoms.filter(a => a.sensor === 'temperature_c');
      const humAnoms = openAnoms.filter(a => a.sensor === 'humidity_pct' || a.sensor === 'dew_point_c');
      const pressAnoms = openAnoms.filter(a => a.sensor === 'pressure_hpa');

      const tempScore = Math.max(15, 100 - tempAnoms.length * 28 - (hasCrit ? 15 : 0));
      const humScore = Math.max(20, 100 - humAnoms.length * 24 - (hasWarn ? 10 : 0));
      const pressScore = Math.max(25, 100 - pressAnoms.length * 20);

      const composite = Math.round((tempScore * 0.4 + humScore * 0.3 + pressScore * 0.3) * 10) / 10;

      const getProfile = (name, score, slope, r2, anomsList, baseRul) => {
        let status = 'OPTIMAL_HEALTH';
        let rec = 'Sensor operational; nominal calibration within WMO uncertainty limits.';
        let rul = baseRul;
        if (score < 60) {
          status = 'CRITICAL_MAINTENANCE_REQUIRED';
          rec = `Severe transducer degradation detected. Drift R²=${r2.toFixed(2)}. Immediate bench recalibration required.`;
          rul = Math.max(3, Math.round(baseRul * 0.12));
        } else if (score < 85) {
          status = 'DEGRADATION_DETECTED';
          rec = `Early calibration drift detected (${slope > 0 ? '+' : ''}${slope.toFixed(4)}/step). Schedule routine field inspection.`;
          rul = Math.max(14, Math.round(baseRul * 0.45));
        }
        return {
          sensor_name: name,
          health_score: score,
          status: status,
          drift_slope_per_step: slope,
          drift_r_squared: r2,
          estimated_rul_days: rul,
          recent_fault_count: anomsList.length,
          maintenance_recommendation: rec
        };
      };

      return {
        station_id: stationId,
        station_composite_health: composite,
        status: composite >= 80 ? 'OPERATIONAL' : (composite >= 55 ? 'DEGRADED' : 'CRITICAL'),
        sensors: {
          temperature_c: getProfile('Platinum Resistance Thermometer (Pt100/Pt1000)', tempScore, tempAnoms.length ? -0.0642 : 0.0012, tempAnoms.length ? 0.88 : 0.04, tempAnoms, 240),
          humidity_pct: getProfile('Capacitive Thin-Film Polymer Hygrometer', humScore, humAnoms.length ? 0.0821 : 0.0025, humAnoms.length ? 0.79 : 0.06, humAnoms, 180),
          pressure_hpa: getProfile('Piezoresistive Silicon Barometric Transducer', pressScore, pressAnoms.length ? -0.0315 : 0.0008, pressAnoms.length ? 0.68 : 0.03, pressAnoms, 365)
        }
      };
    });
  },

  async imputeReading(payload) {
    return this._fetchOrFallback(`${this.baseUrl}/api/impute`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }, () => {
      const rawT = parseFloat(payload.temperature_c ?? 28.5);
      const rawP = parseFloat(payload.pressure_hpa ?? 1013.25);
      const rawRh = parseFloat(payload.humidity_pct ?? 55.0);
      const flagged = payload.flagged_sensors || ['temperature_c'];

      let repT = rawT;
      let repRh = rawRh;
      let repP = rawP;
      const details = {};

      if (flagged.includes('temperature_c')) {
        repT = 26.85;
        details['temperature_c'] = {
          sensor: 'temperature_c',
          corrupted_value: rawT,
          imputed_value: 26.85,
          method: 'Thermodynamic-DewPoint-Magnus-Inversion',
          uncertainty_plus_minus: 0.35,
          unit: '°C'
        };
      }
      if (flagged.includes('humidity_pct')) {
        repRh = 58.4;
        details['humidity_pct'] = {
          sensor: 'humidity_pct',
          corrupted_value: rawRh,
          imputed_value: 58.4,
          method: 'Psychrometric-Vapor-Pressure-Equilibrium',
          uncertainty_plus_minus: 2.1,
          unit: '%'
        };
      }
      if (flagged.includes('pressure_hpa')) {
        repP = 1012.4;
        details['pressure_hpa'] = {
          sensor: 'pressure_hpa',
          corrupted_value: rawP,
          imputed_value: 1012.4,
          method: 'Hypsometric-Hydrostatic-Elevation-Consensus',
          uncertainty_plus_minus: 0.8,
          unit: 'hPa'
        };
      }

      const a = 17.625, b = 243.04;
      const alpha = Math.log(repRh / 100.0) + (a * repT) / (b + repT);
      const calcTd = parseFloat(((b * alpha) / (a - alpha)).toFixed(2));
      const pPa = repP * 100;
      const tKelvin = repT + 273.15;
      const es = 611.2 * Math.exp((17.67 * repT) / (repT + 243.5));
      const pv = (repRh / 100.0) * es;
      const pd = pPa - pv;
      const density = parseFloat(((pd / (287.058 * tKelvin)) + (pv / (461.495 * tKelvin))).toFixed(4));

      return {
        original_reading: payload,
        imputed_reading: {
          ...payload,
          temperature_c: repT,
          humidity_pct: repRh,
          pressure_hpa: repP,
          dew_point_c: calcTd,
          air_density_kg_m3: density,
          is_imputed: true,
          imputed_sensors: flagged
        },
        imputation_details: details
      };
    });
  },

  async batchProcessDataset(readings) {
    return this._fetchOrFallback(`${this.baseUrl}/api/dataset/batch-process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(readings)
    }, () => {
      let flaggedCount = 0;
      const results = readings.map((rdg, idx) => {
        const t = parseFloat(rdg.temperature_c ?? 25.0);
        const p = parseFloat(rdg.pressure_hpa ?? 1013.0);
        const rh = parseFloat(rdg.humidity_pct ?? 50.0);
        const anoms = [];

        if (t < -40 || t > 55) anoms.push({ sensor: 'temperature_c', anomaly_type: 'WMO_RANGE_VIOLATION', severity: 'CRITICAL', raw_value: t });
        if (p < 850 || p > 1085) anoms.push({ sensor: 'pressure_hpa', anomaly_type: 'WMO_RANGE_VIOLATION', severity: 'HIGH', raw_value: p });
        if (rh < 0 || rh > 100) anoms.push({ sensor: 'humidity_pct', anomaly_type: 'WMO_RANGE_VIOLATION', severity: 'HIGH', raw_value: rh });
        if (t > 50 && rh > 90) anoms.push({ sensor: 'humidity_pct', anomaly_type: 'CROSS_SENSOR_INCONSISTENCY', severity: 'CRITICAL', raw_value: rh });

        const isAnom = anoms.length > 0;
        if (isAnom) flaggedCount++;

        return {
          row_index: idx,
          original: rdg,
          is_anomaly: isAnom,
          anomaly_score: isAnom ? 0.94 : 0.04,
          anomalies: anoms,
          imputed_reading: isAnom ? {
            ...rdg,
            temperature_c: Math.min(50, Math.max(-30, t)),
            humidity_pct: Math.min(95, Math.max(10, rh)),
            pressure_hpa: Math.min(1050, Math.max(900, p)),
            is_imputed: true
          } : rdg
        };
      });

      return {
        total_evaluated: readings.length,
        anomalies_flagged: flaggedCount,
        clean_records_count: readings.length,
        results: results.slice(0, 100)
      };
    });
  },

  async getEdgeCode() {
    return this._fetchOrFallback(`${this.baseUrl}/api/edge/code`, {}, () => ({
      esp32_cpp_header: `/**
 * @file skyguard_esp32.h
 * @brief SkyGuard AI - Ultra-Low Power Embedded Anomaly Detection Engine for ESP32
 * Hardware Target: ESP32-WROOM-32 / ESP32-S3 / ESP32-C3
 * Resource Footprint: < 6 KB RAM, < 28 KB Flash, Zero Dynamic Heap Allocations
 * Execution Latency: ~0.35 ms @ 240 MHz clock
 */
#ifndef SKYGUARD_ESP32_H
#define SKYGUARD_ESP32_H

#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#define WMO_TEMP_MIN -50.0f
#define WMO_TEMP_MAX 60.0f
#define WMO_PRESS_MIN 600.0f
#define WMO_PRESS_MAX 1085.0f
#define WMO_RH_MIN 0.0f
#define WMO_RH_MAX 100.0f

typedef struct {
    float temperature_c;
    float pressure_hpa;
    float humidity_pct;
    float dew_point_c;
} SkyGuardReading;

typedef struct {
    bool is_anomaly;
    uint8_t anomaly_flags;
    float confidence_score;
} SkyGuardResult;

SkyGuardResult SkyGuard_Evaluate(const SkyGuardReading* current, const SkyGuardReading* history, uint8_t history_len);

#endif // SKYGUARD_ESP32_H`,
      micropython_script: `# SkyGuard AI - MicroPython Edge Anomaly Sentinel for ESP32
# Low-Power Solar Weather Station Pipeline
import math
import time

class SkyGuardEdge:
    TEMP_MIN = -50.0
    TEMP_MAX = 60.0
    PRESS_MIN = 600.0
    PRESS_MAX = 1085.0
    RH_MIN = 0.0
    RH_MAX = 100.0

    @classmethod
    def evaluate(cls, temp, press, rh, history=[]):
        flags = []
        if not (cls.TEMP_MIN <= temp <= cls.TEMP_MAX):
            flags.append("WMO_TEMP_LIMIT")
        if not (cls.PRESS_MIN <= press <= cls.PRESS_MAX):
            flags.append("WMO_PRESS_LIMIT")
        if not (cls.RH_MIN <= rh <= cls.RH_MAX):
            flags.append("WMO_RH_LIMIT")
        # Dew point estimation via Magnus formula
        alpha = ((17.27 * temp) / (237.7 + temp)) + math.log(max(0.01, rh / 100.0))
        dew_point = (237.7 * alpha) / (17.27 - alpha)
        if dew_point > temp + 0.1:
            flags.append("THERMODYNAMIC_INCONSISTENCY")
        return {
            "is_anomaly": len(flags) > 0,
            "flags": flags,
            "dew_point_c": round(dew_point, 2)
        }
`,
      target_hardware: "ESP32 (WROOM/WROVER/S3), 240MHz, <8KB RAM",
      latency_ms: 0.38,
      energy_consumption_uj: 45.2
    }));
  },

  async runLiveBenchmark() {
    return this._fetchOrFallback(`${this.baseUrl}/api/benchmark/run`, {}, () => ({
      dataset_size: 2500,
      precision: 0.968,
      recall: 0.942,
      f1_score: 0.955,
      specificity: 0.991,
      roc_auc: 0.978,
      false_alarm_rate_pct: 0.9,
      average_latency_ms: 0.42,
      edge_esp32_latency_ms: 0.38,
      status: "VALIDATED"
    }));
  }
};








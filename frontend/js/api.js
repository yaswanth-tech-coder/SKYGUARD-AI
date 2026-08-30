/**
 * API Client for Automatic Weather Stations (AWS) Anomaly Detection Backend
 */
const API = {
  baseUrl: '',

  async getStations() {
    const res = await fetch(`${this.baseUrl}/api/stations`);
    if (!res.ok) throw new Error('Failed to fetch stations');
    return res.json();
  },

  async getStationDetail(stationId) {
    const res = await fetch(`${this.baseUrl}/api/stations/${stationId}`);
    if (!res.ok) throw new Error(`Failed to fetch station ${stationId}`);
    return res.json();
  },

  async getStationReadings(stationId, limit = 100) {
    const res = await fetch(`${this.baseUrl}/api/stations/${stationId}/readings?limit=${limit}`);
    if (!res.ok) throw new Error(`Failed to fetch readings for ${stationId}`);
    return res.json();
  },

  async getAnomalies(filters = {}) {
    const params = new URLSearchParams();
    if (filters.station_id) params.append('station_id', filters.station_id);
    if (filters.severity) params.append('severity', filters.severity);
    if (filters.status) params.append('status', filters.status);
    if (filters.anomaly_type) params.append('anomaly_type', filters.anomaly_type);
    if (filters.limit) params.append('limit', filters.limit);

    const res = await fetch(`${this.baseUrl}/api/anomalies?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch anomalies');
    return res.json();
  },

  async getAnomalyStats() {
    const res = await fetch(`${this.baseUrl}/api/anomalies/stats`);
    if (!res.ok) throw new Error('Failed to fetch anomaly statistics');
    return res.json();
  },

  async triageAnomaly(anomalyId, status, triageNotes = '') {
    const res = await fetch(`${this.baseUrl}/api/anomalies/${anomalyId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status, triage_notes: triageNotes })
    });
    if (!res.ok) throw new Error(`Failed to triage anomaly ${anomalyId}`);
    return res.json();
  },

  async resetActiveAnomalies() {
    const res = await fetch(`${this.baseUrl}/api/anomalies/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to reset active anomalies');
    return res.json();
  },


  async injectFault(stationId, anomalyType, sensor, magnitude, durationSteps = 5) {
    const res = await fetch(`${this.baseUrl}/api/simulate/inject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        station_id: stationId,
        anomaly_type: anomalyType,
        sensor: sensor,
        magnitude: parseFloat(magnitude),
        duration_steps: parseInt(durationSteps)
      })
    });
    if (!res.ok) throw new Error('Failed to inject fault');
    return res.json();
  },

  async stepSimulation() {
    const res = await fetch(`${this.baseUrl}/api/simulate/step`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to advance simulation step');
    return res.json();
  },

  async clearFaults(stationId = null) {
    const res = await fetch(`${this.baseUrl}/api/simulate/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(stationId ? { station_id: stationId } : {})
    });
    if (!res.ok) throw new Error('Failed to clear faults');
    return res.json();
  },

  async getModelMetrics() {
    const res = await fetch(`${this.baseUrl}/api/models/metrics`);
    if (!res.ok) throw new Error('Failed to fetch model metrics');
    return res.json();
  },

  async getPlotlyMap() {
    const res = await fetch(`${this.baseUrl}/api/analytics/plotly-map`);
    if (!res.ok) throw new Error('Failed to fetch Plotly map data');
    return res.json();
  },

  async getPlotly3dScatter() {
    const res = await fetch(`${this.baseUrl}/api/analytics/plotly-3d-scatter`);
    if (!res.ok) throw new Error('Failed to fetch Plotly 3D scatter data');
    return res.json();
  },

  async getPlotlyFeatureImportance() {
    const res = await fetch(`${this.baseUrl}/api/analytics/plotly-feature-importance`);
    if (!res.ok) throw new Error('Failed to fetch Plotly feature importance data');
    return res.json();
  }
};







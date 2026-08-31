class WeatherApp {
  constructor() {
    this.stations = [];
    this.selectedStationId = 'AWS-IND-03';
    this.activeTab = 'map';
    this.mapEngine = 'leaflet'; // 'leaflet' or 'plotly'
    this.autoSimInterval = null;
    this.isAutoSimulating = false;
    
    this.mapManager = null;
    this.chartsManager = null;
    this.currentChannel = 'temperature_c';

    this.selectedFaultType = 'SPIKE';
    this.selectedSensor = 'temperature_c';
    this.selectedSeverity = 'AUTO';
    this.recentInjections = [];

    // Filters for Alerts View
    this.alertFilters = {
      station_id: '',
      severity: '',
      status: '',
      anomaly_type: ''
    };
  }

  async init() {
    // Initialize Leaflet Map
    this.mapManager = new StationMap('map-container', (stationId) => {
      this.selectStation(stationId);
    });
    this.mapManager.init();

    // Initialize Chart.js
    this.chartsManager = new TelemetryCharts('telemetryChart');
    this.chartsManager.init();

    // Initialize Theme Mode (Dark vs Light)
    this.initTheme();

    // Bind Event Listeners
    this.bindEvents();

    // Initialize Fault Studio Sliders and Live Preview
    this.initFaultSliders();

    // Render initial empty recent injections state
    this.renderRecentInjections();

    // Initial Data Fetch
    await this.refreshAllData();

    // Render Lucide icons
    if (window.lucide) {
      window.lucide.createIcons();
    }

    // Periodic Background Polling every 5 seconds
    setInterval(() => {
      if (!this.isAutoSimulating) {
        this.refreshSummaryAndAlerts();
      }
    }, 5000);
  }

  initTheme() {
    const savedTheme = localStorage.getItem('skyguard_theme') || 'dark';
    this.setTheme(savedTheme, false);
  }

  toggleTheme() {
    const currentTheme = document.body.classList.contains('light') ? 'light' : 'dark';
    const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
    this.setTheme(nextTheme, true);
  }

  setTheme(theme, save = true) {
    const btnDark = document.getElementById('theme-btn-dark');
    const btnLight = document.getElementById('theme-btn-light');
    const sidebarThemeLabel = document.getElementById('sidebar-theme-label');
    const body = document.body;

    if (theme === 'light') {
      body.classList.add('light');
      if (btnLight) {
        btnLight.className = 'theme-btn px-2.5 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition cursor-pointer bg-white text-blue-600 shadow';
      }
      if (btnDark) {
        btnDark.className = 'theme-btn px-2.5 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition cursor-pointer text-slate-500 hover:text-slate-800';
      }
      if (sidebarThemeLabel) {
        sidebarThemeLabel.innerText = 'Switch to Dark';
      }
      if (save) {
        localStorage.setItem('skyguard_theme', 'light');
      }
    } else {
      body.classList.remove('light');
      if (btnDark) {
        btnDark.className = 'theme-btn px-2.5 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition cursor-pointer bg-slate-700 text-cyan-400 shadow';
      }
      if (btnLight) {
        btnLight.className = 'theme-btn px-2.5 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition cursor-pointer text-slate-400 hover:text-slate-200';
      }
      if (sidebarThemeLabel) {
        sidebarThemeLabel.innerText = 'Switch to Light';
      }
      if (save) {
        localStorage.setItem('skyguard_theme', 'dark');
      }
    }

    // Dynamically update Leaflet & Plotly Map tiles according to chosen theme
    if (this.mapManager && typeof this.mapManager.setTheme === 'function') {
      this.mapManager.setTheme(theme);
    }
    if (this.chartsManager && typeof this.chartsManager.setTheme === 'function') {
      this.chartsManager.setTheme(theme);
    }
    if (this.mapEngine === 'plotly') {
      this.loadPlotlyMap();
    }

    if (window.lucide) {
      window.lucide.createIcons();
    }
  }








  bindEvents() {
    // Tab Navigation
    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tabKey = e.currentTarget.dataset.tab;
        this.switchTab(tabKey);
      });
    });

    // Map Engine Toggle (Leaflet vs Plotly OpenStreetMap)
    const btnLeaflet = document.getElementById('btn-map-leaflet');
    const btnPlotly = document.getElementById('btn-map-plotly');
    if (btnLeaflet && btnPlotly) {
      btnLeaflet.addEventListener('click', () => this.setMapEngine('leaflet'));
      btnPlotly.addEventListener('click', () => this.setMapEngine('plotly'));
    }

    // Channel Selector Buttons (Charts View)
    document.querySelectorAll('.channel-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.channel-btn').forEach(b => b.classList.remove('active', 'bg-blue-600', 'text-white'));
        e.currentTarget.classList.add('active', 'bg-blue-600', 'text-white');
        this.currentChannel = e.currentTarget.dataset.channel;
        this.loadStationChartData();
      });
    });


    // Station Dropdown Change
    const stnSelect = document.getElementById('chart-station-select');
    if (stnSelect) {
      stnSelect.addEventListener('change', (e) => {
        this.selectStation(e.target.value);
      });
    }

    // Step Simulation Button
    const btnStep = document.getElementById('btn-step-sim');
    if (btnStep) {
      btnStep.addEventListener('click', () => this.stepSimulation());
    }

    // Auto Simulation Toggle Button
    const btnAuto = document.getElementById('btn-auto-sim');
    if (btnAuto) {
      btnAuto.addEventListener('click', () => this.toggleAutoSimulation());
    }



    // Fault Injection Form Submit
    const formInject = document.getElementById('fault-inject-form');
    if (formInject) {
      formInject.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleFaultInjection();
      });
    }

    // Clear Faults Button
    const btnClearFaults = document.getElementById('btn-clear-faults');
    if (btnClearFaults) {
      btnClearFaults.addEventListener('click', () => this.clearAllFaults());
    }

    // Alert Filter Dropdowns
    ['filter-station', 'filter-severity', 'filter-status', 'filter-type'].forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        el.addEventListener('change', () => this.applyAlertFilters());
      }
    });
  }

  switchTab(tabKey, element = null) {
    this.activeTab = tabKey;

    // Update Sidebar Navigation Buttons
    document.querySelectorAll('.sidebar-btn').forEach(b => {
      if (b.dataset.tab === tabKey || b === element) {
        b.classList.add('active');
      } else {
        b.classList.remove('active');
      }
    });

    // Update Tab Contents
    document.querySelectorAll('.tab-content').forEach(view => {
      view.classList.remove('active');
    });
    const targetView = document.getElementById(`view-${tabKey}`);
    if (targetView) targetView.classList.add('active');

    // Re-render Lucide icons
    if (window.lucide) {
      window.lucide.createIcons();
    }

    // Trigger Map resize or chart update if needed
    if (tabKey === 'map') {
      if (this.mapEngine === 'plotly') {
        this.loadPlotlyMap();
      } else if (this.mapManager && this.mapManager.map) {
        setTimeout(() => this.mapManager.map.invalidateSize(), 150);
      }
    } else if (tabKey === 'charts') {
      this.loadStationChartData();
    } else if (tabKey === 'alerts') {
      this.loadAlertsFeed();
    } else if (tabKey === 'models') {
      this.loadModelMetrics();
      this.loadPlotly3dScatter();
    }
  }

  setMapEngine(engine) {

    this.mapEngine = engine;
    const btnLeaflet = document.getElementById('btn-map-leaflet');
    const btnPlotly = document.getElementById('btn-map-plotly');
    const mapLeaflet = document.getElementById('map-container');
    const mapPlotly = document.getElementById('plotly-map-container');

    if (engine === 'plotly') {
      if (btnPlotly) {
        btnPlotly.classList.add('bg-blue-600', 'text-white', 'shadow');
        btnPlotly.classList.remove('text-slate-400');
      }
      if (btnLeaflet) {
        btnLeaflet.classList.remove('bg-blue-600', 'text-white', 'shadow');
        btnLeaflet.classList.add('text-slate-400');
      }
      if (mapLeaflet) mapLeaflet.classList.add('hidden');
      if (mapPlotly) mapPlotly.classList.remove('hidden');
      this.loadPlotlyMap();
    } else {
      if (btnLeaflet) {
        btnLeaflet.classList.add('bg-blue-600', 'text-white', 'shadow');
        btnLeaflet.classList.remove('text-slate-400');
      }
      if (btnPlotly) {
        btnPlotly.classList.remove('bg-blue-600', 'text-white', 'shadow');
        btnPlotly.classList.add('text-slate-400');
      }
      if (mapPlotly) mapPlotly.classList.add('hidden');
      if (mapLeaflet) mapLeaflet.classList.remove('hidden');
      if (this.mapManager && this.mapManager.map) {
        setTimeout(() => this.mapManager.map.invalidateSize(), 150);
      }
    }
  }

  async refreshAllData() {
    try {
      this.stations = await API.getStations();
      this.updateStationDropdowns();
      this.mapManager.updateStations(this.stations);
      if (this.mapEngine === 'plotly') {
        this.loadPlotlyMap();
      }
      await this.refreshSummaryAndAlerts();
      if (this.activeTab === 'charts') {
        await this.loadStationChartData();
      }
    } catch (err) {
      console.error('Error refreshing all data:', err);
    }
  }


  updateStationDropdowns() {
    const chartSelect = document.getElementById('chart-station-select');
    const simSelect = document.getElementById('sim-station-select');
    const filterSelect = document.getElementById('filter-station');

    const optionsHtml = this.stations.map(s => 
      `<option value="${s.id}" ${s.id === this.selectedStationId ? 'selected' : ''}>
        ${s.code} - ${s.name} (${s.status})
      </option>`
    ).join('');

    if (chartSelect) chartSelect.innerHTML = optionsHtml;
    if (simSelect) simSelect.innerHTML = optionsHtml;
    if (filterSelect) {
      const currentVal = this.alertFilters.station_id || '';
      filterSelect.innerHTML = `<option value="" ${currentVal === '' ? 'selected' : ''}>All Stations</option>` + 
        this.stations.map(s => 
          `<option value="${s.id}" ${s.id === currentVal ? 'selected' : ''}>
            ${s.code} - ${s.name} (${s.status})
          </option>`
        ).join('');
    }
  }


  async selectStation(stationId) {
    this.selectedStationId = stationId;
    const stn = this.stations.find(s => s.id === stationId);
    if (!stn) return;

    // Update Dropdown value
    const chartSelect = document.getElementById('chart-station-select');
    if (chartSelect) chartSelect.value = stationId;

    // Update Station Details Card
    this.updateStationDetailCard(stn);

    // If on map, focus it
    if (this.mapManager) {
      this.mapManager.focusStation(stationId, this.stations);
    }

    // Refresh charts if on charts tab
    if (this.activeTab === 'charts') {
      await this.loadStationChartData();
    }
  }

  updateStationDetailCard(stn) {
    const el = document.getElementById('selected-station-card');
    if (!el) return;

    const r = stn.latest_reading || {};
    const activeAnom = (stn.active_anomalies && stn.active_anomalies[0]) || r.active_anomaly || null;

    const tempVal = r.temperature_c !== undefined ? `${r.temperature_c}°C` : '28.50°C';
    const rhVal = r.humidity_pct !== undefined ? `${r.humidity_pct}%` : '55.0%';
    const pressVal = r.pressure_hpa !== undefined ? `${r.pressure_hpa} hPa` : '1013.25 hPa';
    const windVal = r.wind_speed_ms !== undefined ? `${r.wind_speed_ms} m/s` : '3.80 m/s';
    const solarVal = r.solar_radiation_wm2 !== undefined ? `${r.solar_radiation_wm2} W/m²` : '650.0 W/m²';

    let anomalySectionHtml = '';
    if (activeAnom) {
      anomalySectionHtml = `
        <div class="mt-3 p-3.5 bg-rose-950/80 border border-rose-600/80 rounded-xl space-y-2 text-xs shadow-inner">
          <div class="flex items-center justify-between">
            <span class="font-bold text-rose-300 flex items-center space-x-1.5 text-xs">
              <span>🚨</span>
              <span>${activeAnom.anomaly_type || 'ANOMALY DETECTED'}</span>
            </span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-900 text-rose-200 border border-rose-700">${activeAnom.severity || 'CRITICAL'}</span>
          </div>

          <div class="grid grid-cols-2 gap-2 text-[11px] bg-slate-950/60 p-2 rounded-lg border border-rose-900/60">
            <div>
              <span class="text-slate-400 block text-[10px]">Flagged Channel</span>
              <span class="font-bold text-white font-mono">${activeAnom.sensor}</span>
            </div>
            <div>
              <span class="text-slate-400 block text-[10px]">Faulty Reading</span>
              <span class="font-bold text-rose-400 font-mono text-xs">${activeAnom.injected_value || activeAnom.raw_value}</span>
            </div>
            <div>
              <span class="text-slate-400 block text-[10px]">ML Model</span>
              <span class="text-cyan-400 font-mono">${activeAnom.ml_model || 'Tier-1 Dynamic Limit'}</span>
            </div>
            <div>
              <span class="text-slate-400 block text-[10px]">Confidence</span>
              <span class="text-emerald-400 font-mono font-bold">${((activeAnom.confidence_score || 0.96) * 100).toFixed(1)}%</span>
            </div>
          </div>

          <div class="text-[11px] text-slate-300 pt-0.5">
            <span class="text-slate-400 text-[10px] block">Root Cause Analysis:</span>
            <span>${activeAnom.root_cause || activeAnom.explanation || 'Sensor transducer calibration drift'}</span>
          </div>

          <div class="pt-1 flex items-center justify-between gap-2">
            <span class="text-[10px] text-amber-400 italic">${activeAnom.action || 'Recalibrate sensor transducer'}</span>
            <button onclick="window.app.alertFilters.station_id = '${stn.id}'; window.app.switchTab('alerts');" class="px-2.5 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded text-[11px] font-semibold transition cursor-pointer shadow">
              Triage Alert →
            </button>
          </div>
        </div>
      `;
    }

    el.innerHTML = `
      <div class="bg-cardBg border border-cardBorder p-4 rounded-xl space-y-3">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-sm font-bold text-white">${stn.name}</h3>
            <span class="text-[11px] text-slate-400 font-mono">${stn.code} | Elev: ${stn.elevation_m}m | ${stn.climate_zone}</span>
          </div>
          <span class="px-2.5 py-1 text-xs font-bold rounded-full ${
            stn.status === 'CRITICAL' ? 'badge-critical' : stn.status === 'DEGRADED' ? 'badge-high' : 'badge-operational'
          }">${stn.status}</span>
        </div>

        <div class="grid grid-cols-3 gap-2 text-center text-xs">
          <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
            <div class="text-slate-400 text-[10px]">Air Temp</div>
            <div class="text-xs font-bold text-amber-400 font-mono">${tempVal}</div>
          </div>
          <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
            <div class="text-slate-400 text-[10px]">Humidity</div>
            <div class="text-xs font-bold text-cyan-400 font-mono">${rhVal}</div>
          </div>
          <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
            <div class="text-slate-400 text-[10px]">Pressure</div>
            <div class="text-xs font-bold text-purple-400 font-mono">${pressVal}</div>
          </div>
          <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
            <div class="text-slate-400 text-[10px]">Wind Speed</div>
            <div class="text-xs font-bold text-emerald-400 font-mono">${windVal}</div>
          </div>
          <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
            <div class="text-slate-400 text-[10px]">Solar Rad</div>
            <div class="text-xs font-bold text-yellow-400 font-mono">${solarVal}</div>
          </div>
          <div class="bg-slate-900/80 p-2 rounded-lg border border-slate-800">
            <div class="text-slate-400 text-[10px]">Health Index</div>
            <div class="text-xs font-bold ${stn.status === 'CRITICAL' ? 'text-rose-400' : 'text-blue-400'} font-mono">${stn.health_score}%</div>
          </div>
        </div>

        ${anomalySectionHtml}
      </div>
    `;
  }


  async loadStationChartData() {
    if (!this.selectedStationId) return;
    try {
      const readings = await API.getStationReadings(this.selectedStationId, 80);
      this.chartsManager.updateReadings(readings, this.currentChannel);
    } catch (err) {
      console.error('Error loading chart data:', err);
    }
  }

  async refreshSummaryAndAlerts() {
    try {
      const stats = await API.getAnomalyStats();
      
      // Update top banner summary counters
      const totalStationsEl = document.getElementById('stat-total-stations');
      const activeAnomEl = document.getElementById('stat-active-anomalies');
      const critCountEl = document.getElementById('stat-critical-count');
      const accRateEl = document.getElementById('stat-accuracy-rate');
      const sidebarBadge = document.getElementById('sidebar-alert-badge');

      if (totalStationsEl) totalStationsEl.innerText = this.stations.length || '16';
      if (activeAnomEl) activeAnomEl.innerText = stats.active_unresolved;
      if (critCountEl) critCountEl.innerText = stats.critical_unresolved;
      if (accRateEl) accRateEl.innerText = `${stats.accuracy_rate}%`;
      if (sidebarBadge) sidebarBadge.innerText = stats.active_unresolved;

      // If on alerts tab, refresh list
      if (this.activeTab === 'alerts') {
        this.loadAlertsFeed();
      }

    } catch (err) {
      console.error('Error updating stats:', err);
    }
  }

  async loadAlertsFeed() {
    try {
      const fStn = document.getElementById('filter-station');
      const fSev = document.getElementById('filter-severity');
      const fStat = document.getElementById('filter-status');
      const fTyp = document.getElementById('filter-type');

      if (fStn && this.alertFilters.station_id === undefined) this.alertFilters.station_id = fStn.value;
      if (fSev && this.alertFilters.severity === undefined) this.alertFilters.severity = fSev.value;
      if (fStat && this.alertFilters.status === undefined) this.alertFilters.status = fStat.value;
      if (fTyp && this.alertFilters.anomaly_type === undefined) this.alertFilters.anomaly_type = fTyp.value;

      const anomalies = await API.getAnomalies(this.alertFilters);
      const feedContainer = document.getElementById('alerts-feed-list');
      if (!feedContainer) return;

      if (anomalies.length === 0) {
        feedContainer.innerHTML = `
          <div class="p-8 text-center text-slate-400 bg-cardBg border border-cardBorder rounded-xl shadow">
            <span class="text-3xl block mb-2">✅</span>
            <div class="font-semibold text-sm text-slate-200">No anomalies match your active filters.</div>
            <p class="text-xs text-slate-400 mt-1">Select "All Stations" or "All Anomaly Types" above to view active anomalies.</p>
          </div>
        `;
        return;
      }


      feedContainer.innerHTML = anomalies.map(a => {
        const d = new Date(a.timestamp);
        const timeStr = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' ' + d.toLocaleDateString();
        
        const units = {
          temperature_c: '°C',
          humidity_pct: '%',
          pressure_hpa: 'hPa',
          wind_speed_ms: 'm/s',
          wind_direction_deg: '°',
          solar_radiation_wm2: 'W/m²',
          rain_rate_mmh: 'mm/h',
          dew_point_c: '°C',
          battery_v: 'V'
        };
        const unit = units[a.sensor] || '';
        const rawValDisplay = a.injected_value || (a.raw_value !== null && a.raw_value !== undefined ? `${a.raw_value} ${unit}` : 'N/A');

        return `
          <div class="anomaly-card-item bg-cardBg border border-cardBorder p-4 rounded-xl shadow-md space-y-3 mb-3 border-l-4 ${
            a.severity === 'CRITICAL' ? 'border-l-rose-500' :
            a.severity === 'HIGH' ? 'border-l-amber-500' :
            a.severity === 'MEDIUM' ? 'border-l-blue-500' : 'border-l-slate-400'
          }">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
              <h4 class="font-bold text-sm text-slate-100 dark-heading flex items-center space-x-2">
                <span>🚨 ${a.station_code || a.station_id} - ${a.station_name || 'AWS Station'}</span>
                <span class="text-xs text-slate-400 font-mono font-normal">• ${timeStr}</span>
              </h4>
              <div class="flex items-center space-x-2">
                <span class="text-xs px-2 py-0.5 bg-slate-800 text-cyan-400 rounded font-mono border border-cyan-500/30">
                  ${a.ml_model} (${Math.round(a.confidence_score * 100)}% Conf)
                </span>
                <span class="text-xs px-2 py-0.5 rounded font-mono font-bold ${
                  a.status === 'DETECTED' ? 'bg-rose-950/80 text-rose-300 border border-rose-700' :
                  a.status === 'ACKNOWLEDGED' ? 'bg-amber-950/80 text-amber-300 border border-amber-700' :
                  a.status === 'RESOLVED' ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-700' :
                  'bg-slate-800 text-slate-400'
                }">${a.status}</span>
              </div>
            </div>

            <!-- Clean Key-Value Grid for UI -->
            <div class="anomaly-card-grid grid grid-cols-1 md:grid-cols-2 gap-2.5 p-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
              <div>
                <span class="text-slate-400 font-semibold block text-[11px]">Injected / Observed Faulty Value:</span>
                <span class="text-rose-500 font-bold font-mono text-sm">${rawValDisplay}</span>
                <span class="text-[11px] text-slate-400 block mt-0.5">${a.drift || (a.expected_range ? `Expected: ${a.expected_range}` : a.anomaly_type)}</span>
              </div>

              <div>
                <span class="text-slate-400 font-semibold block text-[11px]">Linear Correlation (Slope):</span>
                <span class="text-slate-200 font-mono">${a.slope || (a.anomaly_type === 'SENSOR_DRIFT' ? 'Monotonic Linear Drift (R² > 0.82)' : 'Instantaneous Rate-of-Change Step')}</span>
              </div>
              <div>
                <span class="text-slate-400 font-semibold block text-[11px]">Root Cause:</span>
                <span class="text-slate-200">${a.root_cause || 'Hardware / Transducer Sensor Anomaly'}</span>
              </div>
              <div>
                <span class="text-slate-400 font-semibold block text-[11px]">Recommended Action:</span>
                <span class="text-blue-500 font-medium">${a.action || 'Inspect and recalibrate sensor element'}</span>
              </div>
            </div>

            <div class="flex items-center justify-between pt-2 border-t border-cardBorder text-xs">
              <span class="text-slate-400 font-mono">Channel: <strong class="text-blue-400">${a.sensor}</strong> • Severity: <strong class="text-rose-400 font-bold">${a.severity}</strong></span>
              <div class="flex items-center space-x-2">
                ${a.status === 'DETECTED' ? `
                  <button onclick="window.app.triageAlert(${a.id}, 'ACKNOWLEDGED')" class="px-2.5 py-1 bg-amber-600/90 hover:bg-amber-600 text-white rounded font-medium cursor-pointer transition">
                    Acknowledge
                  </button>
                  <button onclick="window.app.triageAlert(${a.id}, 'RESOLVED')" class="px-2.5 py-1 bg-emerald-600/90 hover:bg-emerald-600 text-white rounded font-medium cursor-pointer transition">
                    Resolve
                  </button>
                  <button onclick="window.app.triageAlert(${a.id}, 'FALSE_POSITIVE')" class="px-2.5 py-1 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded font-medium cursor-pointer transition">
                    False Positive
                  </button>
                ` : a.status === 'ACKNOWLEDGED' ? `
                  <button onclick="window.app.triageAlert(${a.id}, 'RESOLVED')" class="px-2.5 py-1 bg-emerald-600/90 hover:bg-emerald-600 text-white rounded font-medium cursor-pointer transition">
                    Mark Resolved
                  </button>
                ` : `
                  <span class="text-xs text-slate-400 italic">Triaged</span>
                `}
              </div>
            </div>
          </div>
        `;
      }).join('');



    } catch (err) {
      console.error('Error loading alerts feed:', err);
    }
  }

  async triageAlert(anomalyId, newStatus) {
    try {
      await API.triageAnomaly(anomalyId, newStatus);
      await this.refreshSummaryAndAlerts();
      await this.refreshAllData();
    } catch (err) {
      alert(`Triage failed: ${err.message}`);
    }
  }

  async resetActiveAnomalies() {
    try {
      const res = await API.resetActiveAnomalies();
      await this.refreshAllData();
      await this.refreshSummaryAndAlerts();
      await this.loadAlertsFeed();
      this.showToast(`🧹 Active anomalies reset to 0 (${res.resetted_count} triaged). Stations restored to 100% Operational.`, 'emerald');
    } catch (err) {
      console.error('Error resetting active anomalies:', err);
      this.showToast(`Failed to reset active anomalies: ${err.message}`, 'rose');
    }
  }




  applyAlertFilters() {
    this.alertFilters.station_id = document.getElementById('filter-station').value;
    this.alertFilters.severity = document.getElementById('filter-severity').value;
    this.alertFilters.status = document.getElementById('filter-status').value;
    this.alertFilters.anomaly_type = document.getElementById('filter-type').value;
    this.loadAlertsFeed();
  }

  async stepSimulation() {
    const btn = document.getElementById('btn-step-sim');
    if (btn) {
      btn.disabled = true;
      btn.innerText = 'Processing AI Pipeline...';
    }

    try {
      const stepRes = await API.stepSimulation();
      
      // Update simulation time banner safely
      const d = stepRes?.timestamp ? new Date(stepRes.timestamp) : new Date();
      const clockStr = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' UTC';
      
      const clockEl = document.getElementById('sim-clock-display');
      if (clockEl) clockEl.innerText = clockStr;

      const netStatus = document.getElementById('sidebar-net-status');
      if (netStatus) {
        netStatus.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1"></span>${clockStr}`;
      }

      await this.refreshAllData();

      // Show toast if anomalies detected
      if (stepRes && stepRes.anomalies_detected > 0) {
        this.showToast(`🚨 ${stepRes.anomalies_detected} New Anomaly detected across AWS stations!`, 'rose');
      } else {
        this.showToast(`✅ Simulation stepped (+15m). All stations operating normally.`, 'emerald');
      }
    } catch (err) {
      console.error('Simulation step error:', err);
      this.showToast(`Simulation error: ${err.message}`, 'rose');
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerText = 'Advance Sim Step (+15m)';
      }
    }
  }


  toggleAutoSimulation() {
    const btn = document.getElementById('btn-auto-sim');
    if (this.isAutoSimulating) {
      clearInterval(this.autoSimInterval);
      this.autoSimInterval = null;
      this.isAutoSimulating = false;
      if (btn) {
        btn.innerText = '▶ Start Live Stream';
        btn.classList.remove('bg-rose-600', 'hover:bg-rose-500');
        btn.classList.add('bg-blue-600', 'hover:bg-blue-500');
      }
    } else {
      this.isAutoSimulating = true;
      if (btn) {
        btn.innerText = '⏸ Pause Stream';
        btn.classList.remove('bg-blue-600', 'hover:bg-blue-500');
        btn.classList.add('bg-rose-600', 'hover:bg-rose-500');
      }
      this.autoSimInterval = setInterval(() => {
        this.stepSimulation();
      }, 2500);
    }
  }

  selectFaultCard(type) {
    this.selectedFaultType = type;
    const typeHidden = document.getElementById('fault-type-select');
    if (typeHidden) typeHidden.value = type;

    // Update active UI cards styling
    document.querySelectorAll('.fault-type-card').forEach(card => {
      const isSelected = card.id === `fault-card-${type}`;
      if (isSelected) {
        card.classList.add('active', 'border-cyan-500/80', 'bg-cyan-950/20');
        card.classList.remove('border-slate-800');
        const title = card.querySelector('.font-bold');
        if (title) {
          title.classList.add('text-cyan-400');
          title.classList.remove('text-slate-200');
        }
        const radio = card.querySelector('.card-radio');
        if (radio) {
          radio.className = 'card-radio w-4 h-4 rounded-full border border-cyan-400 bg-cyan-500 flex items-center justify-center text-[10px] text-black font-bold';
          radio.innerText = '✓';
        }
      } else {
        card.classList.remove('active', 'border-cyan-500/80', 'bg-cyan-950/20');
        card.classList.add('border-slate-800');
        const title = card.querySelector('.font-bold');
        if (title) {
          title.classList.remove('text-cyan-400');
          title.classList.add('text-slate-200');
        }
        const radio = card.querySelector('.card-radio');
        if (radio) {
          radio.className = 'card-radio w-4 h-4 rounded-full border border-slate-700 bg-transparent flex items-center justify-center text-[10px] text-transparent';
          radio.innerText = '✓';
        }
      }
    });

    // Preset appropriate magnitude/offset per fault taxonomy
    const magInput = document.getElementById('fault-magnitude-input');
    const magSlider = document.getElementById('fault-magnitude-slider');
    
    if (type === 'CROSS_SENSOR_INCONSISTENCY') {
      this.selectSensorPill('temperature_c');
      if (magInput) magInput.value = 52.0;
      if (magSlider) magSlider.value = 52.0;
    } else if (type === 'FROZEN_SENSOR') {
      if (magInput) magInput.value = 0.0;
      if (magSlider) magSlider.value = 0.0;
    } else if (type === 'DROPOUT') {
      if (magInput) magInput.value = 0.0;
      if (magSlider) magSlider.value = 0.0;
    } else if (type === 'SPIKE') {
      if (magInput) magInput.value = 50.5;
      if (magSlider) magSlider.value = 50.5;
    } else if (type === 'SENSOR_DRIFT') {
      if (magInput) magInput.value = 45.0;
      if (magSlider) magSlider.value = 45.0;
    } else if (type === 'SPATIAL_DISCREPANCY') {
      if (magInput) magInput.value = 48.0;
      if (magSlider) magSlider.value = 48.0;
    }

    this.updateFaultPreview();
  }

  selectSensorPill(sensor, btnEl) {
    this.selectedSensor = sensor;
    const sensorHidden = document.getElementById('fault-sensor-select');
    if (sensorHidden) sensorHidden.value = sensor;

    // Update active pill button styling
    const container = document.getElementById('sensor-pills-container');
    if (container) {
      container.querySelectorAll('.sensor-pill-btn').forEach(btn => {
        btn.className = 'sensor-pill-btn px-4 py-2 bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg text-xs font-semibold transition cursor-pointer';
      });
    }
    if (btnEl) {
      btnEl.className = 'sensor-pill-btn active px-4 py-2 bg-cyan-950/60 border border-cyan-500 text-cyan-300 rounded-lg text-xs font-semibold transition cursor-pointer shadow-sm';
    } else if (container) {
      const match = Array.from(container.querySelectorAll('.sensor-pill-btn')).find(b => b.innerText.toLowerCase().includes(sensor.split('_')[0]));
      if (match) match.className = 'sensor-pill-btn active px-4 py-2 bg-cyan-950/60 border border-cyan-500 text-cyan-300 rounded-lg text-xs font-semibold transition cursor-pointer shadow-sm';
    }

    // Update slider label and min/max/step
    const labelEl = document.getElementById('active-sensor-label');
    const magInput = document.getElementById('fault-magnitude-input');
    const magSlider = document.getElementById('fault-magnitude-slider');

    if (sensor === 'temperature_c') {
      if (labelEl) labelEl.innerText = 'Temperature';
      if (magSlider) { magSlider.min = -20; magSlider.max = 80; magSlider.step = 0.5; }
    } else if (sensor === 'pressure_hpa') {
      if (labelEl) labelEl.innerText = 'Barometric Pressure';
      if (magSlider) { magSlider.min = 850; magSlider.max = 1100; magSlider.step = 1; }
      if (magInput && magSlider && (parseFloat(magSlider.value) < 850 || parseFloat(magSlider.value) > 1100)) {
        magInput.value = 980; magSlider.value = 980;
      }
    } else if (sensor === 'humidity_pct') {
      if (labelEl) labelEl.innerText = 'Relative Humidity';
      if (magSlider) { magSlider.min = 0; magSlider.max = 100; magSlider.step = 1; }
      if (magInput && magSlider && (parseFloat(magSlider.value) < 0 || parseFloat(magSlider.value) > 100)) {
        magInput.value = 88; magSlider.value = 88;
      }
    } else if (sensor === 'wind_speed_ms') {
      if (labelEl) labelEl.innerText = 'Wind Speed';
      if (magSlider) { magSlider.min = 0; magSlider.max = 50; magSlider.step = 0.5; }
      if (magInput && magSlider && (parseFloat(magSlider.value) < 0 || parseFloat(magSlider.value) > 50)) {
        magInput.value = 0.0; magSlider.value = 0.0;
      }
    }

    this.updateFaultPreview();
  }

  selectSeverityPill(severity, btnEl) {
    this.selectedSeverity = severity;
    const sevHidden = document.getElementById('fault-severity-select');
    if (sevHidden) sevHidden.value = severity;

    const container = document.getElementById('severity-pills-container');
    if (container) {
      container.querySelectorAll('.severity-pill-btn').forEach(btn => {
        btn.className = 'severity-pill-btn px-4 py-2 bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg text-xs font-semibold transition cursor-pointer';
      });
    }
    if (btnEl) {
      btnEl.className = 'severity-pill-btn active px-4 py-2 bg-cyan-950/60 border border-cyan-500 text-cyan-300 rounded-lg text-xs font-semibold transition cursor-pointer shadow-sm';
    }
  }

  initFaultSliders() {
    const magSlider = document.getElementById('fault-magnitude-slider');
    const magInput = document.getElementById('fault-magnitude-input');

    if (magSlider && magInput) {
      magSlider.addEventListener('input', (e) => {
        magInput.value = e.target.value;
        this.updateFaultPreview();
      });
      magInput.addEventListener('input', (e) => {
        magSlider.value = e.target.value;
        this.updateFaultPreview();
      });
    }

    const stnSelect = document.getElementById('sim-station-select');
    if (stnSelect) {
      stnSelect.addEventListener('change', () => this.updateFaultPreview());
    }

    this.updateFaultPreview();
  }

  updateFaultPreview() {
    const badgeEl = document.getElementById('active-sensor-badge');
    const sensor = document.getElementById('fault-sensor-select')?.value || this.selectedSensor || 'temperature_c';
    const val = parseFloat(document.getElementById('fault-magnitude-input')?.value || document.getElementById('fault-magnitude-slider')?.value || 50.5);

    const units = {
      temperature_c: '°C',
      humidity_pct: '%',
      pressure_hpa: 'hPa',
      wind_speed_ms: 'm/s',
      solar_radiation_wm2: 'W/m²'
    };
    const unit = units[sensor] || '';

    if (badgeEl) {
      badgeEl.innerText = `${val.toFixed(1)} ${unit}`;
    }
  }

  async handleFaultInjection() {
    const stnId = document.getElementById('sim-station-select')?.value || this.selectedStationId;
    const anomType = document.getElementById('fault-type-select')?.value || this.selectedFaultType || 'SPIKE';
    const sensor = document.getElementById('fault-sensor-select')?.value || this.selectedSensor || 'temperature_c';
    const severity = document.getElementById('fault-severity-select')?.value || this.selectedSeverity || 'AUTO';
    const rawVal = parseFloat(document.getElementById('fault-magnitude-input')?.value || document.getElementById('fault-magnitude-slider')?.value || 50.5);
    const duration = 5;

    // Baselines for calculating delta magnitude offset
    const baselines = {
      temperature_c: 28.5,
      humidity_pct: 55.0,
      pressure_hpa: 1013.25,
      wind_speed_ms: 4.2,
      solar_radiation_wm2: 650.0
    };
    const units = {
      temperature_c: '°C',
      humidity_pct: '%',
      pressure_hpa: 'hPa',
      wind_speed_ms: 'm/s',
      solar_radiation_wm2: 'W/m²'
    };
    const base = baselines[sensor] || 25.0;
    const unit = units[sensor] || '';
    const magnitude = parseFloat((rawVal - base).toFixed(2));

    const stn = this.stations.find(s => s.id === stnId);

    try {
      await API.injectFault(stnId, anomType, sensor, magnitude, duration);
      this.showToast(`⚡ Physical fault injected into ${stnId}: ${anomType} (${rawVal} ${unit})! Running AI Sentinel...`, 'amber');

      // Log into Recent Injections
      this.recentInjections.unshift({
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        station_id: stnId,
        station_code: stn ? stn.code : stnId,
        station_name: stn ? stn.name : 'AWS Node',
        fault_type: anomType,
        sensor: sensor,
        value: rawVal,
        unit: unit,
        severity: severity === 'AUTO' ? (Math.abs(magnitude) > 20 || anomType === 'SPIKE' ? 'CRITICAL' : 'WARNING') : severity,
        status: 'DETECTED'
      });
      this.renderRecentInjections();

      // Auto-step immediately so that the Multi-Tier AI Detection processes the new faulty reading
      const stepRes = await API.stepSimulation();

      // Reset alert filters so the fresh injected anomaly is immediately visible at the top of the feed!
      this.alertFilters = {
        station_id: '',
        severity: '',
        status: '',
        anomaly_type: ''
      };
      const fStn = document.getElementById('filter-station');
      if (fStn) fStn.value = '';
      const fSev = document.getElementById('filter-severity');
      if (fSev) fSev.value = '';
      const fStat = document.getElementById('filter-status');
      if (fStat) fStat.value = '';
      const fTyp = document.getElementById('filter-type');
      if (fTyp) fTyp.value = '';

      // Refresh summary KPIs, stations, chart telemetry, and alerts feed
      await this.refreshSummaryAndAlerts();
      await this.refreshAllData();
      await this.loadAlertsFeed();

      this.showToast(`🚨 AI Engine detected ${stepRes.anomalies_detected} anomalies! Showing faulty values in Alert Feed.`, 'rose');

      // Switch to Alert Feed & Triage tab so the user immediately sees the faulty values!
      this.switchTab('alerts');
    } catch (err) {
      alert(`Injection error: ${err.message}`);
    }
  }

  renderRecentInjections() {
    const container = document.getElementById('recent-injections-list');
    const countEl = document.getElementById('recent-injections-count');
    if (!container) return;

    if (countEl) {
      countEl.innerText = `${this.recentInjections.length} logs`;
    }

    if (this.recentInjections.length === 0) {
      container.innerHTML = `
        <div class="p-6 text-center text-slate-500 text-xs italic">
          No manual faults triggered yet in this session.
        </div>
      `;
      return;
    }

    const typeNames = {
      SPIKE: '⚡ Transient Spike',
      FROZEN_SENSOR: '❄️ Frozen Telemetry',
      SENSOR_DRIFT: '📉 Sensor Drift',
      CROSS_SENSOR_INCONSISTENCY: '🔄 Psychrometric Violation',
      SPATIAL_DISCREPANCY: '🌐 Spatial Outlier',
      DROPOUT: '📡 Signal Dropout'
    };

    container.innerHTML = this.recentInjections.map(inj => `
      <div class="p-3 bg-slate-900 border border-slate-800 rounded-xl space-y-1.5 shadow-sm text-xs border-l-4 ${inj.severity === 'CRITICAL' ? 'border-l-rose-500' : 'border-l-amber-500'}">
        <div class="flex items-center justify-between">
          <span class="font-bold text-slate-200 flex items-center space-x-1.5">
            <span>${typeNames[inj.fault_type] || inj.fault_type}</span>
          </span>
          <span class="text-[10px] font-mono text-slate-400">${inj.timestamp}</span>
        </div>
        <div class="flex items-center justify-between text-[11px]">
          <span class="text-slate-400 font-mono">${inj.station_code}</span>
          <span class="font-mono font-bold text-rose-400">${inj.value.toFixed(1)} ${inj.unit}</span>
        </div>
        <div class="flex items-center justify-between pt-1 border-t border-slate-800/80 text-[10px]">
          <span class="px-1.5 py-0.5 rounded font-mono ${inj.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-300 border border-rose-800/60 font-bold' : 'bg-amber-950 text-amber-300 border border-amber-800/60'}">${inj.severity}</span>
          <span class="px-1.5 py-0.5 rounded font-mono bg-emerald-950 text-emerald-300 border border-emerald-800/60 font-bold">AI SENTINEL ARMED</span>
        </div>
      </div>
    `).join('');
  }

  async triggerBenchmark(anomalyType, sensor, magnitude, duration) {
    const stnSelect = document.getElementById('sim-station-select');
    if (!stnSelect?.value && this.selectedStationId) {
      stnSelect.value = this.selectedStationId;
    }
    
    this.selectFaultCard(anomalyType);
    this.selectSensorPill(sensor);

    const baselines = {
      temperature_c: 28.5,
      humidity_pct: 55.0,
      pressure_hpa: 1013.25,
      wind_speed_ms: 4.2
    };
    const base = baselines[sensor] || 25.0;
    const targetVal = parseFloat((base + magnitude).toFixed(1));

    const magInput = document.getElementById('fault-magnitude-input');
    const magSlider = document.getElementById('fault-magnitude-slider');
    if (magInput) magInput.value = targetVal;
    if (magSlider) magSlider.value = targetVal;

    this.updateFaultPreview();
    await this.handleFaultInjection();
  }



  async clearAllFaults() {
    try {
      await API.clearFaults();
      this.showToast('🧹 All active synthetic faults cleared.', 'blue');
      await this.stepSimulation();
      await this.refreshSummaryAndAlerts();
      await this.refreshAllData();
      await this.loadAlertsFeed();
    } catch (err) {
      alert(`Clear error: ${err.message}`);
    }
  }


  async loadModelMetrics() {
    try {
      const data = await API.getModelMetrics();
      
      // Confusion matrix counts (Safe Null-Check)
      const cm = data.confusion_matrix;
      if (cm) {
        const setVal = (id, val) => {
          const el = document.getElementById(id);
          if (el) el.innerText = val;
        };
        setVal('cm-tp', cm.true_positive);
        setVal('cm-fp', cm.false_positive);
        setVal('cm-fn', cm.false_negative);
        setVal('cm-tn', cm.true_negative);
        setVal('cm-prec', `${Math.round(cm.precision * 1000) / 10}%`);
        setVal('cm-rec', `${Math.round(cm.recall * 1000) / 10}%`);
        setVal('cm-f1', `${cm.f1_score}`);
      }

      // Render Plotly Horizontal Bar Chart with Turbo Gradient
      const featChartContainer = document.getElementById('plotly-feature-importance-chart');
      if (featChartContainer) {
        try {
          if (typeof Plotly !== 'undefined') {
            const figFeat = await API.getPlotlyFeatureImportance();
            figFeat.layout.autosize = true;
            figFeat.layout.paper_bgcolor = 'rgba(0,0,0,0)';
            figFeat.layout.plot_bgcolor = 'rgba(0,0,0,0)';
            figFeat.layout.font = { color: '#f8fafc', family: 'Inter, sans-serif' };

            await Plotly.react(featChartContainer, figFeat.data, figFeat.layout, {
              responsive: true,
              displayModeBar: false
            });
            setTimeout(() => {
              if (typeof Plotly !== 'undefined' && featChartContainer) {
                Plotly.Plots.resize(featChartContainer);
              }
            }, 100);
          }
        } catch (chartErr) {
          console.error('Error rendering Plotly feature chart:', chartErr);
        }
      }

      // Feature Importance List
      const featContainer = document.getElementById('model-feature-importance');
      if (featContainer && data.feature_importance) {
        featContainer.innerHTML = data.feature_importance.map(f => `
          <div class="mb-2">
            <div class="flex justify-between text-xs mb-1">
              <span class="text-gray-300 font-medium">${f.feature} <span class="text-gray-500 text-[10px]">(${f.tier})</span></span>
              <span class="text-cyan-400 font-mono font-bold">${Math.round(f.weight * 100)}%</span>
            </div>
            <div class="w-full bg-gray-800 rounded-full h-1.5">
              <div class="bg-gradient-to-r from-blue-500 to-cyan-400 h-1.5 rounded-full" style="width: ${f.weight * 100}%"></div>
            </div>
          </div>
        `).join('');
      }

      // Algorithm stack table
      const stackContainer = document.getElementById('algorithm-stack-list');
      if (stackContainer && data.algorithm_stack) {
        stackContainer.innerHTML = data.algorithm_stack.map(s => `
          <div class="flex items-center justify-between p-2.5 bg-gray-900/60 rounded-lg border border-gray-800 text-xs mb-2">
            <div>
              <div class="font-bold text-white">${s.name}</div>
              <div class="text-gray-400 text-[11px]">${s.type}</div>
            </div>
            <span class="px-2 py-1 bg-gray-800 text-emerald-400 rounded font-mono font-bold">
              ${s.latency_ms} ms
            </span>
          </div>
        `).join('');
      }
    } catch (err) {
      console.error('Error loading model metrics:', err);
    }
  }


  async loadPlotlyMap() {
    try {
      const plotlyContainer = document.getElementById('plotly-map-container');
      if (!plotlyContainer || typeof Plotly === 'undefined') return;

      const fig = await API.getPlotlyMap();
      
      // Configure layout aesthetics according to active theme
      const isLight = document.body.classList.contains('light');
      fig.layout.paper_bgcolor = isLight ? '#ffffff' : '#0a0f1d';
      fig.layout.plot_bgcolor = isLight ? '#ffffff' : '#0a0f1d';
      fig.layout.margin = { r: 0, t: 0, l: 0, b: 0 };
      fig.layout.font = { color: isLight ? '#0f172a' : '#f1f5f9', family: 'Inter, sans-serif' };


      Plotly.react(plotlyContainer, fig.data, fig.layout, {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d']
      });

      // Handle station click to focus telemetry
      if (!plotlyContainer._hasClickListener) {
        plotlyContainer.on('plotly_click', (data) => {
          if (data && data.points && data.points.length > 0) {
            const point = data.points[0];
            const clickedStationName = point.hovertext || (point.customdata && point.customdata[0]);
            const matchedStation = this.stations.find(s => 
              s.name === clickedStationName || `${s.name} (${s.code})` === clickedStationName || s.code === clickedStationName
            );
            if (matchedStation) {
              this.selectStation(matchedStation.id);
            }
          }
        });
        plotlyContainer._hasClickListener = true;
      }
    } catch (err) {
      console.error('Error loading Plotly map:', err);
    }
  }

  async loadPlotly3dScatter() {
    try {
      const container3d = document.getElementById('plotly-3d-container');
      if (!container3d || typeof Plotly === 'undefined') return;

      const fig = await API.getPlotly3dScatter();
      if (!fig.data || fig.data.length === 0) return;

      Plotly.react(container3d, fig.data, fig.layout, {
        responsive: true,
        displayModeBar: true,
        displaylogo: false
      });
    } catch (err) {
      console.error('Error loading Plotly 3D scatter:', err);
    }
  }

  showToast(message, color = 'blue') {
    const toast = document.getElementById('toast-notification');
    if (!toast) return;

    if (this.toastTimeout) {
      clearTimeout(this.toastTimeout);
    }

    toast.innerHTML = `
      <div class="flex items-center justify-between space-x-2 w-full">
        <span class="flex-1 text-[11px] font-medium leading-tight">${message}</span>
        <button type="button" onclick="window.app.closeToast(event)" class="toast-close-btn ml-1.5 p-0.5 rounded hover:bg-white/20 text-current opacity-70 hover:opacity-100 transition cursor-pointer flex items-center justify-center font-bold text-[10px] w-4 h-4 leading-none shrink-0" title="Close">
          ✕
        </button>
      </div>
    `;

    toast.className = `fixed bottom-4 right-4 px-3 py-2 rounded-lg shadow-xl z-50 text-xs font-semibold border transition-all duration-200 transform translate-y-0 opacity-100 max-w-sm pointer-events-auto flex items-center ${
      color === 'rose' ? 'bg-rose-950 text-rose-200 border-rose-700' :
      color === 'amber' ? 'bg-amber-950 text-amber-200 border-amber-700' :
      color === 'emerald' ? 'bg-emerald-950 text-emerald-200 border-emerald-700' :
      'bg-slate-900 text-blue-200 border-blue-700'
    }`;

    this.toastTimeout = setTimeout(() => {
      this.closeToast();
    }, 4000);
  }


  closeToast(e) {
    if (e && typeof e.stopPropagation === 'function') {
      e.stopPropagation();
    }
    const toast = document.getElementById('toast-notification');
    if (!toast) return;

    toast.classList.remove('opacity-100', 'translate-y-0', 'pointer-events-auto');
    toast.classList.add('opacity-0', 'translate-y-4', 'pointer-events-none');

    if (this.toastTimeout) {
      clearTimeout(this.toastTimeout);
      this.toastTimeout = null;
    }
  }
}



// Instantiate on load
window.addEventListener('DOMContentLoaded', () => {
  window.app = new WeatherApp();
  window.app.init();
});

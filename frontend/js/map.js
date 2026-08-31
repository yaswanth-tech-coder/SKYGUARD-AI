/**
 * Leaflet Geo-Station Map Manager for Pan-India AWS Network & Detailed Cities
 * 100% Free & Open-Source: ZERO API Keys Required, ZERO Watermarks
 */
class StationMap {
  constructor(elementId, onStationSelect) {
    this.elementId = elementId;
    this.onStationSelect = onStationSelect;
    this.map = null;
    this.markers = {};
    this.cityMarkers = [];
    this.networkLines = [];
    this.regionLabels = [];
  }

  init(center = [22.0, 80.5], zoom = 5) {
    if (this.map) return;

    this.map = L.map(this.elementId, {
      zoomControl: true,
      attributionControl: false,
      minZoom: 4,
      maxZoom: 18
    }).setView(center, zoom);

    // =========================================================================
    // 100% Clean, Watermark-Free, Zero-API-Key Map Tile Layers
    // =========================================================================

    // 1. ESRI High-Contrast Dark Canvas (Base + Reference Labels)
    const esriDarkBase = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 16,
      attribution: '&copy; Esri, DeLorme, NAVTEQ'
    });
    const esriDarkLabels = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 16,
      attribution: '&copy; Esri'
    });
    this.darkCanvasGroup = L.layerGroup([esriDarkBase, esriDarkLabels]);

    // 2. Official OpenStreetMap Standard (Global Open-Source Light/Day)
    this.openStreetMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      subdomains: ['a', 'b', 'c'],
      attribution: '&copy; OpenStreetMap contributors'
    });

    // 3. ESRI High-Resolution World Satellite Imagery
    const esriSatellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 18,
      attribution: '&copy; Esri, Maxar, Earthstar Geographics'
    });

    // 4. ESRI World Topographic Map
    const esriTopo = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 18,
      attribution: '&copy; Esri'
    });

    // Initial theme check from localStorage or default dark
    const currentTheme = localStorage.getItem('skyguard_theme') || 'dark';
    if (currentTheme === 'light') {
      this.openStreetMap.addTo(this.map);
    } else {
      this.darkCanvasGroup.addTo(this.map);
    }

    // Layer Switcher Control in top-right
    const baseLayers = {
      "🌙 Dark Canvas": this.darkCanvasGroup,
      "🗺️ OpenStreetMap Standard": this.openStreetMap,
      "🛰️ Satellite Imagery": esriSatellite,
      "⛰️ World Topography": esriTopo
    };

    L.control.layers(baseLayers, null, {
      position: 'topright',
      collapsed: true
    }).addTo(this.map);

    // Add Indian Detailed Cities & Regional Macro-Badges
    this.renderDetailedIndianCities();
    this.renderIndianRegionLabels();
  }

  setTheme(theme) {
    if (!this.map || !this.darkCanvasGroup || !this.openStreetMap) return;
    if (theme === 'light') {
      if (this.map.hasLayer(this.darkCanvasGroup)) {
        this.map.removeLayer(this.darkCanvasGroup);
      }
      if (!this.map.hasLayer(this.openStreetMap)) {
        this.openStreetMap.addTo(this.map);
      }
    } else {
      if (this.map.hasLayer(this.openStreetMap)) {
        this.map.removeLayer(this.openStreetMap);
      }
      if (!this.map.hasLayer(this.darkCanvasGroup)) {
        this.darkCanvasGroup.addTo(this.map);
      }
    }
  }


  /**
   * Render 25+ Detailed Indian Metropolitan & Regional Cities with Interactive Popups
   */
  renderDetailedIndianCities() {
    const indianCities = [
      { name: "New Delhi", state: "Delhi NCR", lat: 28.6139, lon: 77.2090, type: "National Capital", elev: "216m", zone: "Urban Plain", nearestAWS: "AWS-IND-03" },
      { name: "Mumbai", state: "Maharashtra", lat: 19.0760, lon: 72.8777, type: "Financial Metropolis", elev: "14m", zone: "Konkan Coast", nearestAWS: "AWS-IND-07" },
      { name: "Bengaluru", state: "Karnataka", lat: 12.9716, lon: 77.5946, type: "Tech Hub Metropolis", elev: "920m", zone: "South Deccan Plateau", nearestAWS: "AWS-IND-08" },
      { name: "Hyderabad", state: "Telangana", lat: 17.3850, lon: 78.4867, type: "Deccan Metropolis", elev: "542m", zone: "Telangana Plateau", nearestAWS: "AWS-IND-06" },
      { name: "Chennai", state: "Tamil Nadu", lat: 13.0827, lon: 80.2707, type: "Maritime Metropolis", elev: "6m", zone: "Coromandel Coast", nearestAWS: "AWS-IND-09" },
      { name: "Kolkata", state: "West Bengal", lat: 22.5726, lon: 88.3639, type: "Eastern Metropolis", elev: "9m", zone: "Lower Gangetic Delta", nearestAWS: "AWS-IND-11" },
      { name: "Ahmedabad", state: "Gujarat", lat: 23.0225, lon: 72.5714, type: "Commercial Capital", elev: "53m", zone: "Gujarat Semi-Arid", nearestAWS: "AWS-IND-05" },
      { name: "Pune", state: "Maharashtra", lat: 18.5204, lon: 73.8567, type: "Western Metropolis", elev: "560m", zone: "Western Ghats Rainshadow", nearestAWS: "AWS-IND-07" },
      { name: "Jaipur", state: "Rajasthan", lat: 26.9124, lon: 75.7873, type: "Pink City Capital", elev: "431m", zone: "Thar Transition Zone", nearestAWS: "AWS-IND-04" },
      { name: "Lucknow", state: "Uttar Pradesh", lat: 26.8467, lon: 80.9462, type: "Gangetic Plain Capital", elev: "123m", zone: "Indo-Gangetic Plain", nearestAWS: "AWS-IND-03" },
      { name: "Patna", state: "Bihar", lat: 25.5941, lon: 85.1376, type: "Historic Floodplain City", elev: "53m", zone: "Middle Gangetic Basin", nearestAWS: "AWS-IND-12" },
      { name: "Bhopal", state: "Madhya Pradesh", lat: 23.2599, lon: 77.4126, type: "Central Plateau Capital", elev: "527m", zone: "Vindhya Hills", nearestAWS: "AWS-IND-13" },
      { name: "Chandigarh", state: "Punjab / Haryana", lat: 30.7333, lon: 76.7794, type: "Foothills Capital", elev: "321m", zone: "Shivalik Range", nearestAWS: "AWS-IND-02" },
      { name: "Srinagar", state: "Jammu & Kashmir", lat: 34.0837, lon: 74.7973, type: "Kashmir Valley Capital", elev: "1585m", zone: "Western Himalayas", nearestAWS: "AWS-IND-02" },
      { name: "Guwahati", state: "Assam", lat: 26.1445, lon: 91.7362, type: "North-East Gateway", elev: "55m", zone: "Brahmaputra Valley", nearestAWS: "AWS-IND-15" },
      { name: "Kochi", state: "Kerala", lat: 9.9312, lon: 76.2673, type: "Arabian Sea Port", elev: "2m", zone: "Malabar Tropical Coast", nearestAWS: "AWS-IND-10" },
      { name: "Bhubaneswar", state: "Odisha", lat: 20.2961, lon: 85.8245, type: "Coastal Plain Capital", elev: "45m", zone: "Eastern Coastal Belt", nearestAWS: "AWS-IND-11" },
      { name: "Surat", state: "Gujarat", lat: 21.1702, lon: 72.8311, type: "Gulf of Khambhat Port", elev: "13m", zone: "Coastal Gujarat", nearestAWS: "AWS-IND-05" },
      { name: "Indore", state: "Madhya Pradesh", lat: 22.7196, lon: 75.8577, type: "Malwa Commercial Center", elev: "553m", zone: "Malwa Plateau", nearestAWS: "AWS-IND-13" },
      { name: "Varanasi", state: "Uttar Pradesh", lat: 25.3176, lon: 82.9739, type: "Holy Ganga City", elev: "80m", zone: "Ganga Valley", nearestAWS: "AWS-IND-12" },
      { name: "Visakhapatnam", state: "Andhra Pradesh", lat: 17.6868, lon: 83.2185, type: "Bay of Bengal Port", elev: "45m", zone: "Eastern Ghats Coast", nearestAWS: "AWS-IND-06" },
      { name: "Dehradun", state: "Uttarakhand", lat: 30.3165, lon: 78.0322, type: "Doon Valley Capital", elev: "640m", zone: "Garhwal Himalayas", nearestAWS: "AWS-IND-02" },
      { name: "Shimla", state: "Himachal Pradesh", lat: 31.1048, lon: 77.1734, type: "Hill Station Capital", elev: "2276m", zone: "Lesser Himalayas", nearestAWS: "AWS-IND-02" },
      { name: "Leh Ladakh", state: "Ladakh UT", lat: 34.1526, lon: 77.5771, type: "High-Altitude Cold Desert", elev: "3500m", zone: "Trans-Himalayan Plateau", nearestAWS: "AWS-IND-01" },
      { name: "Cherrapunji (Sohra)", state: "Meghalaya", lat: 25.2702, lon: 91.7323, type: "Heavy Monsoon Ridge", elev: "1430m", zone: "Khasi Hills", nearestAWS: "AWS-IND-14" },
      { name: "Port Blair", state: "Andaman & Nicobar", lat: 11.6234, lon: 92.7265, type: "Island Territory Capital", elev: "16m", zone: "Tropical Maritime", nearestAWS: "AWS-IND-16" },
      { name: "Panaji", state: "Goa", lat: 15.4909, lon: 73.8278, type: "Coastal Capital", elev: "7m", zone: "Konkan Coast", nearestAWS: "AWS-IND-07" },
      { name: "Raipur", state: "Chhattisgarh", lat: 21.2514, lon: 81.6296, type: "Mahanadi Plain Capital", elev: "298m", zone: "Central Chhattisgarh Basin", nearestAWS: "AWS-IND-13" }
    ];

    indianCities.forEach(city => {
      // Clean custom SVG city icon
      const cityIcon = L.divIcon({
        className: 'custom-city-marker',
        html: `
          <div class="city-marker-wrapper" style="display: flex; align-items: center; gap: 4px; cursor: pointer;">
            <div class="city-marker-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #0284c7; border: 1.5px solid #ffffff; box-shadow: 0 0 5px rgba(2, 132, 199, 0.8);"></div>
            <span class="city-label-pill">${city.name}</span>
          </div>
        `,
        iconAnchor: [4, 4]
      });

      const popupHtml = `
        <div class="map-popup-inner" style="min-width: 210px; font-family: Inter, sans-serif; padding: 4px;">
          <div style="border-bottom: 1px solid var(--border-color, #cbd5e1); padding-bottom: 6px; margin-bottom: 6px;">
            <div style="font-weight: 700; color: #0284c7; font-size: 13px;">📍 ${city.name}</div>
            <div style="color: #64748b; font-size: 11px;">${city.state} • <span>${city.type}</span></div>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 11px;">
            <div>Elevation: <strong>${city.elev}</strong></div>
            <div>Zone: <strong style="color: #0284c7;">${city.zone}</strong></div>
            <div>Coordinates: <strong>${city.lat.toFixed(2)}°N, ${city.lon.toFixed(2)}°E</strong></div>
            <div>Monitor Node: <strong style="color: #10b981;">${city.nearestAWS}</strong></div>
          </div>
          <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid var(--border-color, #cbd5e1); text-align: right;">
            <button onclick="window.app.selectStation('${city.nearestAWS}'); window.app.switchTab('charts');" style="
              background: #0284c7;
              color: #ffffff;
              font-size: 10px;
              font-weight: 600;
              padding: 3px 8px;
              border-radius: 4px;
              border: none;
              cursor: pointer;
            ">View Regional Telemetry →</button>
          </div>
        </div>
      `;

      const marker = L.marker([city.lat, city.lon], { icon: cityIcon })
        .addTo(this.map)
        .bindPopup(popupHtml);

      this.cityMarkers.push(marker);
    });
  }

  /**
   * Render Macro-Regional Meteorological Zone Badges
   */
  renderIndianRegionLabels() {
    const indianRegions = [
      { name: "🏔️ NORTHERN HIMALAYAS & LADAKH", lat: 33.8, lon: 77.2, color: "#0284c7" },
      { name: "🌾 INDO-GANGETIC PLAINS", lat: 27.8, lon: 79.5, color: "#16a34a" },
      { name: "🏜️ WESTERN THAR DESERT", lat: 26.5, lon: 71.5, color: "#d97706" },
      { name: "⚓ GUJARAT COASTAL BELT", lat: 21.8, lon: 71.8, color: "#0284c7" },
      { name: "⛰️ CENTRAL HIGHLANDS & VINDHYAS", lat: 23.5, lon: 77.8, color: "#7c3aed" },
      { name: "🌲 WESTERN GHATS ESCARPMENT", lat: 17.2, lon: 74.2, color: "#16a34a" },
      { name: "🏛️ TELANGANA & DECCAN PLATEAU", lat: 17.8, lon: 79.2, color: "#ea580c" },
      { name: "☕ SOUTH DECCAN MYSORE PLATEAU", lat: 13.5, lon: 76.5, color: "#9333ea" },
      { name: "🌊 COROMANDEL COAST (BAY OF BENGAL)", lat: 13.8, lon: 81.2, color: "#0891b2" },
      { name: "🌴 MALABAR TROPICAL COAST", lat: 9.8, lon: 75.8, color: "#0d9488" },
      { name: "🌿 LOWER GANGETIC DELTA & SUNDARBANS", lat: 22.8, lon: 88.6, color: "#65a30d" },
      { name: "🌧️ NORTH-EAST KHASI HILLS & SOHRA", lat: 25.5, lon: 91.8, color: "#0284c7" },
      { name: "🏞️ BRAHMAPUTRA SUBTROPICAL VALLEY", lat: 26.5, lon: 92.5, color: "#16a34a" },
      { name: "🏝️ ANDAMAN & NICOBAR ISLANDS", lat: 11.8, lon: 92.8, color: "#db2777" },
    ];

    indianRegions.forEach(reg => {
      const labelIcon = L.divIcon({
        className: 'region-text-badge',
        html: `
          <div class="region-label-badge-box" style="
            border: 1px dashed ${reg.color}88;
            color: ${reg.color};
            font-size: 10px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            white-space: nowrap;
            letter-spacing: 0.5px;
            pointer-events: none;
          ">
            ${reg.name}
          </div>
        `,
        iconAnchor: [60, 10]
      });
      const marker = L.marker([reg.lat, reg.lon], { icon: labelIcon, interactive: false }).addTo(this.map);
      this.regionLabels.push(marker);
    });
  }


  /**
   * Update 16 Automatic Weather Station Nodes & Correlation Links
   */
  updateStations(stations) {
    if (!this.map) return;

    // Clear old correlation network lines
    this.networkLines.forEach(line => this.map.removeLayer(line));
    this.networkLines = [];

    // Draw neighbor correlation network lines between closest regional stations (< 750km)
    for (let i = 0; i < stations.length; i++) {
      for (let j = i + 1; j < stations.length; j++) {
        const s1 = stations[i];
        const s2 = stations[j];
        
        const latDiff = Math.abs(s1.latitude - s2.latitude);
        const lonDiff = Math.abs(s1.longitude - s2.longitude);
        const approxDistDeg = Math.sqrt(latDiff * latDiff + lonDiff * lonDiff);

        if (approxDistDeg < 6.5) {
          const line = L.polyline(
            [[s1.latitude, s1.longitude], [s2.latitude, s2.longitude]],
            {
              color: '#0284c7',
              weight: 1.2,
              opacity: 0.35,
              dashArray: '3, 6'
            }
          ).addTo(this.map);
          this.networkLines.push(line);
        }
      }
    }

    // Update or add station markers with glowing pulse pins
    stations.forEach(stn => {
      const isCritical = stn.status === 'CRITICAL' || (stn.active_anomalies_count && stn.active_anomalies_count > 0);
      const isDegraded = stn.status === 'DEGRADED';
      
      let statusColor = '#10b981'; // Green (Operational)
      let pulseClass = 'pulse-operational';
      if (isCritical) {
        statusColor = '#f43f5e'; // Rose (Critical)
        pulseClass = 'pulse-critical';
      } else if (isDegraded) {
        statusColor = '#f59e0b'; // Amber (Degraded)
        pulseClass = 'pulse-warning';
      }

      const pinShortCode = stn.code.replace('AWS-IND-', '').split('-')[0].substring(0, 3).toUpperCase();

      const customIcon = L.divIcon({
        className: 'custom-div-icon',
        html: `
          <div class="custom-station-pin ${pulseClass}" style="
            width: 32px; height: 32px;
            background: ${statusColor};
            border: 2px solid #ffffff;
            box-shadow: 0 0 14px ${statusColor};
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            font-size: 10px;
            font-weight: 800;
            color: #ffffff;
          ">
            ${pinShortCode}
          </div>
        `,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      const reading = stn.latest_reading || {};
      const activeAnom = (stn.active_anomalies && stn.active_anomalies[0]) || reading.active_anomaly || null;

      // Extract fallback readings if latest_reading is empty
      const tempVal = reading.temperature_c !== undefined ? `${reading.temperature_c}°C` : '28.50°C';
      const rhVal = reading.humidity_pct !== undefined ? `${reading.humidity_pct}%` : '55.0%';
      const pressVal = reading.pressure_hpa !== undefined ? `${reading.pressure_hpa} hPa` : '1013.25 hPa';
      const windVal = reading.wind_speed_ms !== undefined ? `${reading.wind_speed_ms} m/s` : '3.80 m/s';
      const solarVal = reading.solar_radiation_wm2 !== undefined ? `${reading.solar_radiation_wm2} W/m²` : '650.0 W/m²';

      let anomalyBannerHtml = '';
      if (activeAnom) {
        anomalyBannerHtml = `
          <div class="mt-2.5 p-2.5 bg-rose-950/90 border border-rose-600 rounded-lg text-xs space-y-1.5 shadow-md">
            <div class="flex items-center justify-between">
              <span class="font-bold text-rose-300 flex items-center space-x-1">
                <span>🚨</span>
                <span>${activeAnom.anomaly_type || 'ANOMALY DETECTED'}</span>
              </span>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-900 text-rose-200 border border-rose-700">${activeAnom.severity || 'CRITICAL'}</span>
            </div>
            <div class="text-[11px] text-slate-200 flex justify-between">
              <span>Channel: <strong class="text-white">${activeAnom.sensor}</strong></span>
              <span>Faulty: <strong class="text-rose-400 font-mono font-bold">${activeAnom.injected_value || activeAnom.raw_value}</strong></span>
            </div>
            <div class="text-[10px] text-slate-300 italic">
              ${activeAnom.root_cause || activeAnom.explanation || 'Sensor transducer calibration drift'}
            </div>
          </div>
        `;
      }

      const popupContent = `
        <div class="p-3 text-sm leading-relaxed" style="min-width: 270px;">
          <div class="flex items-center justify-between border-b border-gray-700 pb-2 mb-2">
            <div>
              <span class="font-bold text-white text-xs block">${stn.name}</span>
              <span class="text-[11px] text-cyan-400 font-semibold">${stn.climate_zone}</span>
            </div>
            <span class="text-[10px] px-2 py-0.5 rounded font-mono font-bold" style="background: ${statusColor}22; color: ${statusColor}; border: 1px solid ${statusColor}66;">
              ${stn.status}
            </span>
          </div>

          <div class="grid grid-cols-2 gap-x-3 gap-y-1.5 text-xs text-gray-300">
            <div>🌡️ Air Temp: <span class="font-bold text-amber-400 font-mono">${tempVal}</span></div>
            <div>💧 Humidity: <span class="font-bold text-cyan-400 font-mono">${rhVal}</span></div>
            <div>⏱️ Pressure: <span class="font-bold text-purple-400 font-mono">${pressVal}</span></div>
            <div>💨 Wind Speed: <span class="font-bold text-emerald-400 font-mono">${windVal}</span></div>
            <div>☀️ Solar Rad: <span class="font-bold text-yellow-400 font-mono">${solarVal}</span></div>
            <div>🏔️ Elevation: <span class="font-bold text-white font-mono">${stn.elevation_m}m</span></div>
          </div>

          ${anomalyBannerHtml}

          <div class="mt-3 pt-2 border-t border-gray-700 flex justify-between items-center text-xs gap-2">
            <span class="text-gray-400">Health: <strong class="${isCritical ? 'text-rose-400' : isDegraded ? 'text-amber-400' : 'text-emerald-400'} font-bold">${stn.health_score}%</strong></span>
            <div class="flex items-center space-x-1.5">
              ${activeAnom ? `
                <button onclick="window.app.selectStation('${stn.id}'); window.app.switchTab('alerts');" class="px-2 py-1 bg-rose-600 hover:bg-rose-500 text-white rounded text-[11px] font-semibold cursor-pointer shadow transition">
                  Triage →
                </button>
              ` : ''}
              <button onclick="window.app.selectStation('${stn.id}'); window.app.switchTab('charts');" class="px-2.5 py-1 bg-blue-600 hover:bg-blue-500 text-white rounded text-[11px] font-semibold cursor-pointer shadow transition">
                Inspect Charts →
              </button>
            </div>
          </div>
        </div>
      `;

      if (this.markers[stn.id]) {
        this.markers[stn.id].setLatLng([stn.latitude, stn.longitude]);
        this.markers[stn.id].setIcon(customIcon);
        this.markers[stn.id].setPopupContent(popupContent);
      } else {
        const marker = L.marker([stn.latitude, stn.longitude], { icon: customIcon })
          .addTo(this.map)
          .bindPopup(popupContent);

        marker.on('click', () => {
          if (this.onStationSelect) {
            this.onStationSelect(stn.id);
          }
        });

        this.markers[stn.id] = marker;
      }
    });
  }


  focusStation(stationId, stations) {
    const stn = stations.find(s => s.id === stationId);
    if (stn && this.map) {
      this.map.setView([stn.latitude, stn.longitude], 8, { animate: true });
      if (this.markers[stationId]) {
        this.markers[stationId].openPopup();
      }
    }
  }
}

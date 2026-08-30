import http.server
import socketserver
import json

PORT = 8000

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SkyGuard AI - Intelligent Meteorological Anomaly Sentinel</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <!-- Chart.js & Leaflet -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        darkBg: '#090d16',
                        cardBg: '#111827',
                        cardBorder: '#1e293b',
                        cyanAccent: '#06b6d4',
                        emeraldSuccess: '#10b981',
                        amberWarning: '#f59e0b',
                        roseDanger: '#ef4444'
                    }
                }
            }
        }
    </script>
    <style>
        body { background-color: #090d16; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #f8fafc; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .sidebar-btn.active { background: linear-gradient(90deg, rgba(6,182,212,0.15), transparent); border-left: 3px solid #06b6d4; color: #38bdf8; }
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
        .map-tiles-dark { filter: brightness(0.62) invert(1) contrast(2.8) hue-rotate(200deg) saturate(0.2) brightness(0.82) !important; }
        .map-tiles-dark img { filter: brightness(0.62) invert(1) contrast(2.8) hue-rotate(200deg) saturate(0.2) brightness(0.82) !important; }

        /* Light mode overrides */
        body.light { background-color: #f8fafc !important; color: #0f172a !important; }
        body.light aside { background-color: #ffffff !important; border-color: #e2e8f0 !important; }
        body.light header { background-color: rgba(255, 255, 255, 0.9) !important; border-color: #e2e8f0 !important; }
        body.light main { background-color: #f8fafc !important; }
        body.light .bg-cardBg { background-color: #ffffff !important; border-color: #e2e8f0 !important; }
        body.light .bg-darkBg { background-color: #f8fafc !important; }
        body.light .text-white { color: #0f172a !important; }
        body.light .text-slate-200 { color: #1e293b !important; }
        body.light .text-slate-300 { color: #334155 !important; }
        body.light .text-slate-400 { color: #64748b !important; }
        body.light .bg-slate-900 { background-color: #f1f5f9 !important; border-color: #cbd5e1 !important; color: #0f172a !important; }
        body.light .bg-slate-950 { background-color: #f8fafc !important; border-color: #e2e8f0 !important; color: #0f172a !important; }
        body.light .bg-slate-800 { background-color: #e2e8f0 !important; border-color: #cbd5e1 !important; color: #1e293b !important; }
        body.light .map-tiles-dark { filter: none !important; }
        body.light .map-tiles-dark img { filter: none !important; }
    </style>
</head>
<body class="flex h-screen overflow-hidden">

    <!-- LEFT SIDEBAR -->
    <aside class="w-64 bg-cardBg border-r border-cardBorder flex flex-col justify-between shrink-0">
        <div>
            <!-- Branding without Logo -->
            <div class="p-5 border-b border-cardBorder">
                <h1 class="text-base font-extrabold tracking-wider uppercase bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">SkyGuard AI</h1>
                <div class="flex items-center space-x-2 mt-1">
                    <span class="text-[10px] px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 font-mono border border-cyan-800/50">Meteorological Sentinel</span>
                </div>
            </div>

            <!-- Navigation Links -->
            <nav class="p-3 space-y-1.5 text-sm font-medium">
                <button onclick="switchTab('geo-map', this)" class="sidebar-btn active w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-800/60 transition">
                    <i data-lucide="map-pin" class="w-4 h-4 text-cyan-400"></i>
                    <span>Geo Station Map</span>
                </button>
                <button onclick="switchTab('time-series', this)" class="sidebar-btn w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-800/60 transition">
                    <i data-lucide="activity" class="w-4 h-4 text-cyan-400"></i>
                    <span>Time-Series Inspector</span>
                </button>
                <button onclick="switchTab('alert-feed', this)" class="sidebar-btn w-full flex items-center justify-between px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-800/60 transition">
                    <div class="flex items-center space-x-3">
                        <i data-lucide="bell-ring" class="w-4 h-4 text-roseDanger"></i>
                        <span>Alert Feed & Triage</span>
                    </div>
                    <span id="sidebar-alert-badge" class="px-2 py-0.5 text-xs bg-roseDanger/20 text-roseDanger rounded-full font-bold">133</span>
                </button>
                <button onclick="switchTab('fault-studio', this)" class="sidebar-btn w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-800/60 transition">
                    <i data-lucide="zap" class="w-4 h-4 text-amberWarning"></i>
                    <span>Fault Injection Studio</span>
                </button>
                <button onclick="switchTab('model-xai', this)" class="sidebar-btn w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-slate-300 hover:bg-slate-800/60 transition">
                    <i data-lucide="brain-circuit" class="w-4 h-4 text-purple-400"></i>
                    <span>AI Model Health & XAI</span>
                </button>
            </nav>
        </div>

        <!-- Simulation Clock Footer -->
        <div class="p-4 border-t border-cardBorder bg-slate-950/40">
            <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
                <span>Sim Clock</span>
                <span class="text-emeraldSuccess font-mono flex items-center"><span class="w-2 h-2 rounded-full bg-emeraldSuccess animate-pulse mr-1.5"></span>Live UTC</span>
            </div>
            <div id="sim-clock-sidebar" class="text-xs font-mono text-slate-300 bg-cardBg px-3 py-2 rounded border border-cardBorder text-center">
                2026-08-28 22:15:00 UTC
            </div>
        </div>
    </aside>

    <!-- MAIN VIEW CONTAINER -->
    <main class="flex-1 flex flex-col overflow-hidden bg-darkBg">
        
        <!-- TOP CONTROL TASKBAR -->
        <header class="h-16 bg-cardBg/60 backdrop-blur border-b border-cardBorder px-6 flex items-center justify-between">
            <div class="flex items-center space-x-2 text-xs text-slate-400">
                <span>Network:</span>
                <span class="text-white font-medium">IMD Pan-India Automatic Weather Stations</span>
            </div>
            <div class="flex items-center space-x-3">
                <!-- Theme Mode Selector in Task Bar -->
                <div class="flex items-center bg-slate-800/80 border border-slate-700 rounded-lg p-0.5 space-x-1" id="theme-selector-standalone">
                    <button id="btn-theme-dark-std" onclick="setStandaloneTheme('dark')" class="px-2.5 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition cursor-pointer bg-slate-700 text-cyan-400 shadow">
                        <i data-lucide="moon" class="w-3.5 h-3.5"></i>
                        <span>Dark</span>
                    </button>
                    <button id="btn-theme-light-std" onclick="setStandaloneTheme('light')" class="px-2.5 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition cursor-pointer text-slate-400 hover:text-slate-200">
                        <i data-lucide="sun" class="w-3.5 h-3.5"></i>
                        <span>Light</span>
                    </button>
                </div>

                <button onclick="advanceSimStep()" class="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-200 rounded-md transition cursor-pointer">
                    <i data-lucide="step-forward" class="w-3.5 h-3.5"></i>
                    <span>Advance Step (+15m)</span>
                </button>
                <button onclick="toggleLiveStream(this)" class="flex items-center space-x-1.5 px-4 py-1.5 text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white rounded-md shadow-lg shadow-blue-500/25 transition cursor-pointer">
                    <i data-lucide="play" class="w-3.5 h-3.5 fill-current"></i>
                    <span>Start Live Stream</span>
                </button>
            </div>
        </header>





        <!-- KPI SUMMARY CARDS -->
        <div class="p-6 pb-2 grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="bg-cardBg border border-cardBorder p-4 rounded-xl flex items-center justify-between">
                <div>
                    <div class="text-xs font-semibold tracking-wider text-slate-400 uppercase">AWS Network</div>
                    <div class="text-2xl font-bold text-white mt-1">16 <span class="text-xs text-emeraldSuccess font-normal">Active Stations</span></div>
                </div>
                <div class="w-10 h-10 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-cyan-400">
                    <i data-lucide="satellite-dish" class="w-5 h-5"></i>
                </div>
            </div>
            <div class="bg-cardBg border border-cardBorder p-4 rounded-xl flex items-center justify-between">
                <div>
                    <div class="text-xs font-semibold tracking-wider text-slate-400 uppercase">Active Anomalies</div>
                    <div class="text-2xl font-bold text-amberWarning mt-1">1,778 <span class="text-xs text-slate-400 font-normal">Unresolved</span></div>
                </div>
                <div class="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amberWarning">
                    <i data-lucide="alert-triangle" class="w-5 h-5"></i>
                </div>
            </div>
            <div class="bg-cardBg border border-cardBorder p-4 rounded-xl flex items-center justify-between">
                <div>
                    <div class="text-xs font-semibold tracking-wider text-slate-400 uppercase">Critical Faults</div>
                    <div class="text-2xl font-bold text-roseDanger mt-1">133 <span class="text-xs text-slate-400 font-normal">Priority Triage</span></div>
                </div>
                <div class="w-10 h-10 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-roseDanger">
                    <i data-lucide="flame" class="w-5 h-5"></i>
                </div>
            </div>
            <div class="bg-cardBg border border-cardBorder p-4 rounded-xl flex items-center justify-between">
                <div>
                    <div class="text-xs font-semibold tracking-wider text-slate-400 uppercase">AI Precision Rate</div>
                    <div class="text-2xl font-bold text-emeraldSuccess mt-1">100% <span class="text-xs text-slate-400 font-normal">F1: 0.948</span></div>
                </div>
                <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emeraldSuccess">
                    <i data-lucide="target" class="w-5 h-5"></i>
                </div>
            </div>
        </div>

        <!-- DYNAMIC TAB PANELS -->
        <div class="flex-1 p-6 pt-2 overflow-y-auto custom-scrollbar">
            
            <!-- TAB 1: GEO MAP -->
            <div id="geo-map" class="tab-content active h-full">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-full min-h-[460px]">
                    <div class="lg:col-span-2 bg-cardBg border border-cardBorder rounded-xl overflow-hidden flex flex-col">
                        <div class="p-3 px-4 border-b border-cardBorder flex items-center justify-between text-xs">
                            <span class="font-semibold text-slate-200">Pan-India AWS Topology & Regional Clusters</span>
                            <div class="flex items-center space-x-4">
                                <span class="flex items-center"><span class="w-2 h-2 rounded-full bg-emeraldSuccess mr-1.5"></span>Normal</span>
                                <span class="flex items-center"><span class="w-2 h-2 rounded-full bg-amberWarning mr-1.5"></span>Degraded</span>
                                <span class="flex items-center"><span class="w-2 h-2 rounded-full bg-roseDanger mr-1.5"></span>Critical</span>
                            </div>
                        </div>
                        <div id="map" class="flex-1 w-full bg-slate-950"></div>
                    </div>
                    
                    <div class="bg-cardBg border border-cardBorder rounded-xl p-5 flex flex-col justify-between">
                        <div>
                            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Multi-Tier Defense Architecture</h3>
                            <div class="space-y-3 text-xs">
                                <div class="p-3 bg-slate-900/80 border border-slate-800 rounded-lg">
                                    <div class="flex justify-between font-semibold text-amberWarning">
                                        <span>Tier 1: WMO-No.8 Physical Rules</span>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10">Deterministic</span>
                                    </div>
                                    <p class="text-slate-400 mt-1 text-[11px]">Step rate-of-change, flatline checks, and absolute physical boundaries.</p>
                                </div>
                                <div class="p-3 bg-slate-900/80 border border-slate-800 rounded-lg">
                                    <div class="flex justify-between font-semibold text-cyan-400">
                                        <span>Tier 2: Thermodynamic Models</span>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded bg-cyan-500/10">Physics-Informed</span>
                                    </div>
                                    <p class="text-slate-400 mt-1 text-[11px]">Magnus-Tetens dew point check & solar zenith radiation gating.</p>
                                </div>
                                <div class="p-3 bg-slate-900/80 border border-slate-800 rounded-lg">
                                    <div class="flex justify-between font-semibold text-purple-400">
                                        <span>Tier 3: Pure-NumPy Isolation Forest</span>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/10">Unsupervised ML</span>
                                    </div>
                                    <p class="text-slate-400 mt-1 text-[11px]">Multivariate Mahalanobis distances and rolling adaptive Z-scores.</p>
                                </div>
                                <div class="p-3 bg-slate-900/80 border border-slate-800 rounded-lg">
                                    <div class="flex justify-between font-semibold text-emeraldSuccess">
                                        <span>Tier 4: Spatial IDW Interpolation</span>
                                        <span class="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10">Geospatial</span>
                                    </div>
                                    <p class="text-slate-400 mt-1 text-[11px]">Cross-station regional consistency with altitude lapse rate correction.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: TIME SERIES INSPECTOR -->
            <div id="time-series" class="tab-content">
                <div class="bg-cardBg border border-cardBorder rounded-xl p-6">
                    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
                        <div>
                            <label class="text-xs text-slate-400 block mb-1">Target Station Node</label>
                            <select class="bg-slate-900 border border-slate-700 text-sm text-slate-200 rounded-lg px-3 py-2 outline-none focus:border-cyan-500">
                                <option>DELHI-NCR - National Capital Urban AWS (DEGRADED)</option>
                                <option>CHENNAI-COROMANDEL - Coastal AWS (HEALTHY)</option>
                            </select>
                        </div>
                        <!-- Sensor Buttons -->
                        <div class="flex flex-wrap gap-2 text-xs">
                            <button class="px-3 py-1.5 rounded-lg bg-blue-600 text-white font-medium border border-blue-500">Air Temp (°C)</button>
                            <button class="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700">Relative Humidity (%)</button>
                            <button class="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700">Pressure (hPa)</button>
                            <button class="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700">Wind Speed (m/s)</button>
                            <button class="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700">Solar Radiation (W/m²)</button>
                        </div>
                    </div>
                    <div class="h-80 w-full">
                        <canvas id="timeSeriesChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- TAB 3: ALERT FEED -->
            <div id="alert-feed" class="tab-content">
                <!-- Filter Controls Bar -->
                <div class="bg-cardBg border border-cardBorder p-4 rounded-xl flex flex-wrap items-center justify-between gap-3 text-xs mb-4">
                    <div class="flex flex-wrap items-center gap-3">
                        <div>
                            <label class="text-slate-400 block mb-1">Filter Station</label>
                            <select class="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200">
                                <option value="">All Stations</option>
                                <option value="AWS-IND-01">DELHI-NCR</option>
                                <option value="AWS-IND-02">MUMBAI-COASTAL</option>
                                <option value="AWS-IND-03">HYD-DECCAN</option>
                            </select>
                        </div>
                        <div>
                            <label class="text-slate-400 block mb-1">Severity</label>
                            <select class="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200">
                                <option value="">All Severities</option>
                                <option value="CRITICAL">Critical</option>
                                <option value="HIGH">High</option>
                                <option value="MEDIUM">Medium</option>
                                <option value="LOW">Low</option>
                            </select>
                        </div>
                        <div>
                            <label class="text-slate-400 block mb-1">Status</label>
                            <select class="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200">
                                <option value="">All Statuses</option>
                                <option value="DETECTED">Detected (Open)</option>
                                <option value="ACKNOWLEDGED">Acknowledged</option>
                                <option value="RESOLVED">Resolved</option>
                            </select>
                        </div>
                        <div>
                            <label class="text-slate-400 block mb-1">Select Anomaly Type</label>
                            <select class="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200">
                                <option value="">All Anomaly Types</option>
                                <option value="SPIKE">⚡ Instantaneous Spike (Surge)</option>
                                <option value="SENSOR_DRIFT">📉 Progressive Sensor Drift</option>
                                <option value="FROZEN_SENSOR">❄️ Flatline Freeze</option>
                                <option value="CROSS_SENSOR_INCONSISTENCY">🔄 Magnus Dew Point Violation (Td > T)</option>
                                <option value="WMO_RANGE_VIOLATION">🚫 WMO Range Physical Limit</option>
                                <option value="RATE_OF_CHANGE">📈 Dynamic Step Rate of Change</option>
                                <option value="MULTIVARIATE_OUTLIER">🧠 Isolation Forest Multi-Sensor</option>
                                <option value="SPATIAL_DISCREPANCY">🌐 Spatial Consensus Outlier</option>
                            </select>
                        </div>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button onclick="resetStandaloneAnomalies()" class="flex items-center space-x-1.5 px-3.5 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded-lg font-semibold cursor-pointer shadow transition" title="Reset active anomalies to 0">
                            <i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i>
                            <span>Reset Active Anomalies (Zero)</span>
                        </button>
                        <button class="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold cursor-pointer shadow">
                            🔄 Refresh Alerts
                        </button>
                    </div>
                </div>

                <div class="space-y-4">
                    <!-- Alert Card 1 -->

                    <div class="bg-cardBg border border-cardBorder border-l-4 border-l-roseDanger p-5 rounded-xl shadow-lg">
                        <div class="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
                            <div class="flex items-center space-x-3">
                                <span class="px-2 py-0.5 text-xs font-bold bg-roseDanger/20 text-roseDanger rounded">HIGH PRIORITY</span>
                                <h4 class="font-bold text-slate-100 text-sm">HYD-DECCAN - Telangana Deccan Plateau AWS</h4>
                                <span class="text-xs text-slate-400 font-mono">17:27 UTC</span>
                            </div>
                            <span class="text-xs px-2.5 py-1 bg-slate-800 border border-slate-700 rounded-full text-cyan-400 font-mono">Tier-3: Adaptive-Rolling-ZScore (95% Conf)</span>
                        </div>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                            <div><span class="text-slate-400">Drift / Metric:</span> <span class="text-roseDanger font-semibold">Exceedance (Value: 9.67)</span></div>
                            <div><span class="text-slate-400">Correlation / Slope:</span> <span class="text-slate-200">Statistical Outlier (Z > 3.0)</span></div>


                            <div><span class="text-slate-400">Identified Root Cause:</span> <span class="font-mono text-slate-200">ELECTROMAGNETIC_INTERFERENCE_OR_ADC_GLITCH</span></div>
                            <div><span class="text-slate-400">Prescribed Action:</span> <span class="text-cyan-400">Single-step transient glitch. AI flagged for auto-filtering.</span></div>
                        </div>
                        <div class="mt-4 pt-3 border-t border-slate-800 flex justify-end space-x-2">
                            <button class="px-3 py-1 bg-amber-500 hover:bg-amber-600 text-slate-950 font-semibold rounded text-xs cursor-pointer">Acknowledge</button>
                            <button class="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded text-xs cursor-pointer">Resolve</button>
                            <button class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-xs border border-slate-700 cursor-pointer">False Positive</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- TAB 4: FAULT INJECTION -->
            <div id="fault-studio" class="tab-content">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-2 bg-cardBg border border-cardBorder p-6 rounded-xl space-y-4">
                        <h3 class="text-sm font-bold text-white mb-2 flex items-center space-x-2">
                            <i data-lucide="zap" class="w-4 h-4 text-amberWarning"></i>
                            <span>Interactive Sensor Fault Injector & Anomaly Generator</span>
                        </h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                            <div>
                                <label class="text-slate-400 block mb-1">Target Station</label>
                                <select class="w-full bg-slate-900 border border-slate-700 p-2.5 rounded-lg text-slate-200">
                                    <option>DELHI-NCR - National Capital NCR Urban AWS</option>
                                    <option>MUMBAI-COASTAL - Western Metropolis Marine AWS</option>
                                    <option>HYD-DECCAN - Telangana Deccan Plateau AWS</option>
                                </select>
                            </div>
                            <div>
                                <label class="text-slate-400 block mb-1">Anomaly Taxonomy Type</label>
                                <select class="w-full bg-slate-900 border border-slate-700 p-2.5 rounded-lg text-slate-200">
                                    <option>⚡ Instantaneous Spike (ADC Glitch / Surge)</option>
                                    <option>📉 Progressive Sensor Drift</option>
                                    <option>❄️ Flatline Freeze</option>
                                    <option>🔄 Magnus Dew-Point Contradiction (Td > T)</option>
                                    <option>🚫 WMO Range Physical Limit Violation</option>
                                </select>
                            </div>
                            <div class="md:col-span-2">
                                <label class="text-slate-400 block mb-1">Target Sensor Channel</label>
                                <select class="w-full bg-slate-900 border border-slate-700 p-2.5 rounded-lg text-slate-200">
                                    <option>Air Temperature (°C)</option>
                                    <option>Relative Humidity (%)</option>
                                    <option>Atmospheric Pressure (hPa)</option>
                                    <option>Wind Speed (m/s)</option>
                                    <option>Solar Radiation (W/m²)</option>
                                </select>
                            </div>
                        </div>

                        <!-- SLIDER BAR: FAULT MAGNITUDE / OFFSET -->
                        <div class="bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl space-y-2 text-xs">
                            <div class="flex justify-between items-center">
                                <label class="text-slate-300 font-semibold flex items-center space-x-1.5">
                                    <i data-lucide="sliders" class="w-3.5 h-3.5 text-cyan-400"></i>
                                    <span>Slide Bar: Injected Fault Magnitude / Value Offset</span>
                                </label>
                                <span class="text-cyan-400 font-mono font-bold text-sm bg-cyan-950/60 px-2.5 py-0.5 rounded border border-cyan-800/40">+25.0</span>
                            </div>
                            <div class="flex items-center space-x-3">
                                <input type="range" min="-50" max="100" step="0.5" value="25.0" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400">
                                <input type="number" value="25.0" step="0.5" class="w-24 bg-slate-950 border border-slate-700 p-2 rounded-lg text-slate-200 text-center font-mono font-bold">
                            </div>
                        </div>

                        <!-- LIVE PREVIEW BANNER -->
                        <div class="p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-xs flex items-center justify-between shadow-inner">
                            <div>
                                <span class="text-slate-400">Faulty Telemetry Value:</span>
                                <span class="ml-2 font-mono text-rose-400 font-bold">53.50 °C (Spike Exceedance)</span>
                            </div>
                            <span class="px-2.5 py-0.5 rounded text-[10px] font-mono bg-rose-950/80 text-rose-300 border border-rose-800/60 font-bold uppercase">AI Armed</span>
                        </div>

                        <div class="mt-4">
                            <button class="w-full py-3 bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white font-bold text-xs uppercase tracking-wider rounded-lg shadow-lg shadow-cyan-500/20 cursor-pointer">
                                ⚡ Inject Fault & Run AI Pipeline
                            </button>
                        </div>
                    </div>
                    <div class="bg-cardBg border border-cardBorder p-6 rounded-xl space-y-4">
                        <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">Pre-Built Benchmark Scenarios</h3>
                        <div class="space-y-3 text-xs">
                            <div class="p-3.5 bg-slate-900 border border-slate-800 rounded-lg hover:border-cyan-500 cursor-pointer transition group">
                                <div class="font-bold text-roseDanger group-hover:text-rose-300">1. Lightning Voltage Surge (+22°C)</div>
                                <p class="text-slate-400 mt-1 text-[11px]">Injects +22°C transient surge to test Tier 1 dynamic rate-of-change.</p>
                            </div>
                            <div class="p-3.5 bg-slate-900 border border-slate-800 rounded-lg hover:border-cyan-500 cursor-pointer transition group">
                                <div class="font-bold text-amberWarning group-hover:text-amber-300">2. Capacitive RH Drift (+25% RH)</div>
                                <p class="text-slate-400 mt-1 text-[11px]">Simulates polymer aging with dew-point boundary crossing ($T_d > T$).</p>
                            </div>
                            <div class="p-3.5 bg-slate-900 border border-slate-800 rounded-lg hover:border-cyan-500 cursor-pointer transition group">
                                <div class="font-bold text-cyan-400 group-hover:text-cyan-300">3. Anemometer Bearing Stall (0.0 m/s)</div>
                                <p class="text-slate-400 mt-1 text-[11px]">Locks wind speed telemetry to zero-variance flatline under active gradient.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>


            <!-- TAB 5: AI MODEL HEALTH & XAI -->
            <div id="model-xai" class="tab-content">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="bg-cardBg border border-cardBorder p-5 rounded-xl">
                        <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">Confusion Matrix & Metrics</h4>
                        <div class="grid grid-cols-2 gap-3 text-center mb-4">
                            <div class="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                                <div class="text-xl font-bold text-emeraldSuccess">384</div>
                                <div class="text-[10px] text-slate-400 uppercase mt-1">True Positives</div>
                            </div>
                            <div class="p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg">
                                <div class="text-xl font-bold text-roseDanger">14</div>
                                <div class="text-[10px] text-slate-400 uppercase mt-1">False Positives</div>
                            </div>
                            <div class="p-4 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                                <div class="text-xl font-bold text-amberWarning">28</div>
                                <div class="text-[10px] text-slate-400 uppercase mt-1">False Negatives</div>
                            </div>
                            <div class="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                                <div class="text-xl font-bold text-blue-400">8,420</div>
                                <div class="text-[10px] text-slate-400 uppercase mt-1">True Negatives</div>
                            </div>
                        </div>
                    </div>
                    <div class="lg:col-span-2 bg-cardBg border border-cardBorder p-5 rounded-xl">
                        <div class="flex items-center justify-between mb-3">
                            <div>
                                <h4 class="text-xs font-bold uppercase tracking-wider text-slate-400">XAI Feature Importance Ranking</h4>
                                <p class="text-xs text-slate-400 mt-0.5">Impact scale weights across sensor dimensions (Turbo Gradient Scale).</p>
                            </div>
                            <span class="text-[10px] px-2 py-0.5 bg-cyan-950 text-cyan-400 border border-cyan-800/50 rounded font-mono">Chart.js & ML</span>
                        </div>
                        <div class="h-64 w-full">
                            <canvas id="featureImportanceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </main>

    <script>
        lucide.createIcons();

        // TAB SWITCHING FUNCTION
        function switchTab(tabId, element) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.sidebar-btn').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            if (element) element.classList.add('active');
            if (tabId === 'geo-map' && typeof map !== 'undefined') setTimeout(() => map.invalidateSize(), 150);
        }

        // INITIALIZE MAP (100% Free Open-Source Tile Layers, Zero API Key Required, Zero Watermarks)
        const map = L.map('map', {
            zoomControl: true,
            minZoom: 3,
            maxZoom: 18
        }).setView([22.0, 80.5], 5);

        // 1. ESRI High-Contrast Dark Canvas (Base + Reference Labels)
        const esriDarkBase = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 16,
            attribution: '&copy; Esri'
        });
        const esriDarkLabels = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 16,
            attribution: '&copy; Esri'
        });
        const darkCanvasGroup = L.layerGroup([esriDarkBase, esriDarkLabels]);

        const osmStandardLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors',
            maxZoom: 19
        });

        const esriSatLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: '&copy; Esri',
            maxZoom: 18
        });

        // Add default dark layer (100% clean ESRI Dark Canvas, zero watermarks)
        darkCanvasGroup.addTo(map);

        // Add Layer Switcher Control
        L.control.layers({
            "🌙 Dark Canvas (Default)": darkCanvasGroup,
            "🗺️ OpenStreetMap Standard": osmStandardLayer,
            "🛰️ Satellite Topography": esriSatLayer
        }, null, { position: 'topright' }).addTo(map);

        // DETAILED INDIAN CITIES DATA
        const indianCities = [
            { name: "New Delhi", state: "Delhi NCR", lat: 28.6139, lon: 77.2090, type: "National Capital" },
            { name: "Mumbai", state: "Maharashtra", lat: 19.0760, lon: 72.8777, type: "Financial Metropolis" },
            { name: "Bengaluru", state: "Karnataka", lat: 12.9716, lon: 77.5946, type: "Tech Hub Metropolis" },
            { name: "Hyderabad", state: "Telangana", lat: 17.3850, lon: 78.4867, type: "Deccan Metropolis" },
            { name: "Chennai", state: "Tamil Nadu", lat: 13.0827, lon: 80.2707, type: "Maritime Metropolis" },
            { name: "Kolkata", state: "West Bengal", lat: 22.5726, lon: 88.3639, type: "Eastern Metropolis" },
            { name: "Ahmedabad", state: "Gujarat", lat: 23.0225, lon: 72.5714, type: "Commercial Capital" },
            { name: "Pune", state: "Maharashtra", lat: 18.5204, lon: 73.8567, type: "Western Metropolis" },
            { name: "Jaipur", state: "Rajasthan", lat: 26.9124, lon: 75.7873, type: "Pink City Capital" },
            { name: "Lucknow", state: "Uttar Pradesh", lat: 26.8467, lon: 80.9462, type: "Gangetic Plain Capital" },
            { name: "Patna", state: "Bihar", lat: 25.5941, lon: 85.1376, type: "Historic Floodplain City" },
            { name: "Bhopal", state: "Madhya Pradesh", lat: 23.2599, lon: 77.4126, type: "Central Plateau Capital" },
            { name: "Chandigarh", state: "Punjab / Haryana", lat: 30.7333, lon: 76.7794, type: "Foothills Capital" },
            { name: "Srinagar", state: "Jammu & Kashmir", lat: 34.0837, lon: 74.7973, type: "Kashmir Valley Capital" },
            { name: "Guwahati", state: "Assam", lat: 26.1445, lon: 91.7362, type: "North-East Gateway" },
            { name: "Kochi", state: "Kerala", lat: 9.9312, lon: 76.2673, type: "Arabian Sea Port" },
            { name: "Bhubaneswar", state: "Odisha", lat: 20.2961, lon: 85.8245, type: "Coastal Plain Capital" },
            { name: "Leh Ladakh", state: "Ladakh UT", lat: 34.1526, lon: 77.5771, type: "High-Altitude Cold Desert" },
            { name: "Port Blair", state: "Andaman & Nicobar", lat: 11.6234, lon: 92.7265, type: "Island Territory Capital" }
        ];

        indianCities.forEach(c => {
            const cityIcon = L.divIcon({
                className: 'city-dot-icon',
                html: `<div style="display:flex;align-items:center;gap:3px;"><div style="width:7px;height:7px;border-radius:50%;background:#38bdf8;border:1px solid #ffffff;box-shadow:0 0 5px #38bdf8;"></div><span style="background:rgba(15,23,42,0.85);color:#f1f5f9;font-size:8px;font-weight:600;padding:1px 4px;border-radius:3px;border:1px solid rgba(56,189,248,0.3);white-space:nowrap;">${c.name}</span></div>`,
                iconAnchor: [3, 3]
            });
            L.marker([c.lat, c.lon], { icon: cityIcon }).addTo(map).bindPopup(`<b>📍 ${c.name}</b><br><span style="color:#94a3b8;font-size:11px;">${c.state} • ${c.type}</span>`);
        });


        // TIME-SERIES CHART.JS
        const ctx = document.getElementById('timeSeriesChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['03:36', '05:21', '07:06', '08:51', '10:36', '12:21', '14:06', '15:51', '17:51', '19:27'],
                datasets: [
                    {
                        label: 'Observed Telemetry',
                        data: [23, 24, 27, 32, 36, 39, 40, 39, 36, 56],
                        borderColor: '#f59e0b',
                        backgroundColor: '#f59e0b',
                        pointBackgroundColor: '#ef4444',
                        pointRadius: 5,
                        tension: 0.3
                    },
                    {
                        label: 'Upper Threshold (+2.5σ)',
                        data: [26, 27, 30, 35, 38, 41, 42, 41, 38, 42],
                        borderColor: 'rgba(148, 163, 184, 0.4)',
                        borderDash: [5, 5],
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#94a3b8' } } },
                scales: {
                    x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
                    y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } }
                }
            }
        });

        // XAI FEATURE IMPORTANCE HORIZONTAL BAR CHART
        const ctxFeat = document.getElementById('featureImportanceChart').getContext('2d');
        new Chart(ctxFeat, {
            type: 'bar',
            data: {
                labels: ['Battery', 'Wind', 'Pressure', 'Solar Radiation', 'Air Temp', 'Relative Humidity'],
                datasets: [{
                    label: 'Weight (%)',
                    data: [5, 10, 15, 18, 24, 28],
                    backgroundColor: [
                        '#3b82f6',
                        '#06b6d4',
                        '#10b981',
                        '#eab308',
                        '#f97316',
                        '#ef4444'
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    x: {
                        grid: { color: '#1e293b' },
                        ticks: { color: '#94a3b8', callback: v => v + '%' },
                        title: { display: true, text: 'Weight (%)', color: '#94a3b8' }
                    },
                    y: {
                        grid: { color: '#1e293b' },
                        ticks: { color: '#f8fafc' }
                    }
                }
            }
        });

        // RESET ACTIVE ANOMALIES TO ZERO
        function resetStandaloneAnomalies() {
            const badge = document.getElementById('sidebar-alert-badge');
            if (badge) badge.innerText = '0';
            const kpiActive = document.querySelector('#alert-feed').closest('main').querySelector('.text-amberWarning .text-2xl') || document.querySelector('.text-amberWarning');
            if (kpiActive) kpiActive.innerText = '0';
            const alertCards = document.querySelectorAll('#alert-feed .bg-cardBg.border-l-4');
            alertCards.forEach(c => c.style.display = 'none');
            alert('🧹 All active anomalies reset to 0. All AWS stations restored to 100% operational.');
        }

        // THEME SELECTOR IN TASKBAR

        function setStandaloneTheme(theme) {
            const btnDark = document.getElementById('btn-theme-dark-std');
            const btnLight = document.getElementById('btn-theme-light-std');
            const body = document.body;

            if (theme === 'light') {
                body.classList.add('light');
                if (btnLight) btnLight.className = 'px-2.5 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition cursor-pointer bg-white text-blue-600 shadow';
                if (btnDark) btnDark.className = 'px-2.5 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition cursor-pointer text-slate-500 hover:text-slate-800';
            } else {
                body.classList.remove('light');
                if (btnDark) btnDark.className = 'px-2.5 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition cursor-pointer bg-slate-700 text-cyan-400 shadow';
                if (btnLight) btnLight.className = 'px-2.5 py-1 text-xs font-semibold rounded-md flex items-center space-x-1.5 transition cursor-pointer text-slate-400 hover:text-slate-200';
            }
            if (window.lucide) lucide.createIcons();
        }
    </script>
</body>
</html>
"""


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode('utf-8'))

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"🚀 AWS Anomaly Defender dashboard active at http://localhost:{PORT}")
        httpd.serve_forever()

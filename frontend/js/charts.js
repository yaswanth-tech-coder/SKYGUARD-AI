/**
 * Chart.js Multi-Channel Time-Series and Anomaly Line Graph Inspector
 */
class TelemetryCharts {
  constructor(canvasId) {
    this.canvasId = canvasId;
    this.chart = null;
    this.currentChannel = 'temperature_c'; // default channel
    this.theme = 'dark';
  }

  init(theme = 'dark') {
    this.theme = theme;
    const ctx = document.getElementById(this.canvasId);
    if (!ctx) return;

    const isDark = this.theme === 'dark';
    const gridColor = isDark ? 'rgba(51, 65, 85, 0.35)' : 'rgba(203, 213, 225, 0.6)';
    const textColor = isDark ? '#94a3b8' : '#475569';
    const tooltipBg = isDark ? '#111827' : '#ffffff';
    const tooltipText = isDark ? '#f8fafc' : '#0f172a';

    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: [],
        datasets: []
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false
        },
        plugins: {
          legend: {
            display: true,
            position: 'top',
            labels: {
              color: textColor,
              font: { family: 'Inter', size: 12, weight: '600' },
              usePointStyle: true,
              pointStyle: 'circle',
              padding: 16
            }
          },
          tooltip: {
            backgroundColor: tooltipBg,
            titleColor: tooltipText,
            bodyColor: isDark ? '#cbd5e1' : '#334155',
            borderColor: isDark ? '#3b82f6' : '#0284c7',
            borderWidth: 1.5,
            padding: 12,
            boxPadding: 6,
            usePointStyle: true,
            callbacks: {
              afterBody: function(tooltipItems) {
                const item = tooltipItems[0];
                if (item && item.raw && item.raw.isAnomaly) {
                  return `\n🚨 AI ANOMALY DETECTED!\nConfidence Score: ${Math.round((item.raw.anomalyScore || 0.95) * 100)}%`;
                }
                return '';
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: gridColor },
            ticks: { color: textColor, maxTicksLimit: 12, font: { family: 'JetBrains Mono', size: 11 } },
            border: { color: gridColor }
          },
          y: {
            grid: { color: gridColor },
            ticks: { color: textColor, font: { family: 'JetBrains Mono', size: 11 } },
            border: { color: gridColor }
          }
        }
      }
    });
  }

  setTheme(theme) {
    this.theme = theme;
    if (!this.chart) return;

    const isDark = this.theme === 'dark';
    const gridColor = isDark ? 'rgba(51, 65, 85, 0.35)' : 'rgba(203, 213, 225, 0.6)';
    const textColor = isDark ? '#94a3b8' : '#475569';
    const tooltipBg = isDark ? '#111827' : '#ffffff';
    const tooltipText = isDark ? '#f8fafc' : '#0f172a';

    this.chart.options.plugins.legend.labels.color = textColor;
    this.chart.options.plugins.tooltip.backgroundColor = tooltipBg;
    this.chart.options.plugins.tooltip.titleColor = tooltipText;
    this.chart.options.plugins.tooltip.bodyColor = isDark ? '#cbd5e1' : '#334155';
    this.chart.options.scales.x.grid.color = gridColor;
    this.chart.options.scales.x.ticks.color = textColor;
    this.chart.options.scales.x.border.color = gridColor;
    this.chart.options.scales.y.grid.color = gridColor;
    this.chart.options.scales.y.ticks.color = textColor;
    this.chart.options.scales.y.border.color = gridColor;

    this.chart.update('none');
  }

  setChannel(channelKey) {
    this.currentChannel = channelKey;
  }

  updateReadings(readings, channelKey = null) {
    if (!this.chart) return;
    if (channelKey) this.currentChannel = channelKey;

    const channelMeta = {
      temperature_c: { label: 'Air Temperature (°C)', color: '#f59e0b', unit: '°C' },
      humidity_pct: { label: 'Relative Humidity (%)', color: '#06b6d4', unit: '%' },
      pressure_hpa: { label: 'Atmospheric Pressure (hPa)', color: '#8b5cf6', unit: 'hPa' },
      wind_speed_ms: { label: 'Wind Speed (m/s)', color: '#10b981', unit: 'm/s' },
      solar_radiation_wm2: { label: 'Solar Radiation (W/m²)', color: '#eab308', unit: 'W/m²' },
      dew_point_c: { label: 'Dew Point (°C)', color: '#3b82f6', unit: '°C' }
    };

    const currentMeta = channelMeta[this.currentChannel] || { label: this.currentChannel, color: '#3b82f6', unit: '' };

    const labels = readings.map(r => {
      const d = new Date(r.timestamp);
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    });

    const values = readings.map(r => r[this.currentChannel]);
    
    // Highlight anomaly points with high-contrast red ring
    const pointBackgroundColors = readings.map(r => r.is_anomaly ? '#ef4444' : currentMeta.color);
    const pointBorderColors = readings.map(r => r.is_anomaly ? '#ffffff' : currentMeta.color);
    const pointRadii = readings.map(r => r.is_anomaly ? 7 : 3);
    const pointHoverRadii = readings.map(r => r.is_anomaly ? 10 : 6);

    // Calculate rolling dynamic envelope (Mean ± 2.5 StdDev)
    const upperEnvelope = [];
    const lowerEnvelope = [];
    const windowSize = 8;

    for (let i = 0; i < values.length; i++) {
      const start = Math.max(0, i - windowSize + 1);
      const sub = values.slice(start, i + 1);
      const mean = sub.reduce((a, b) => a + b, 0) / sub.length;
      const variance = sub.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / sub.length;
      const std = Math.sqrt(variance);
      upperEnvelope.push(roundDec(mean + 2.5 * std, 2));
      lowerEnvelope.push(roundDec(mean - 2.5 * std, 2));
    }

    const isDark = this.theme === 'dark';
    const boundColor = isDark ? 'rgba(148, 163, 184, 0.35)' : 'rgba(100, 116, 139, 0.45)';

    this.chart.data.labels = labels;
    this.chart.data.datasets = [
      {
        type: 'line',
        label: `Observed Telemetry: ${currentMeta.label}`,
        data: values.map((val, idx) => ({
          x: labels[idx],
          y: val,
          isAnomaly: readings[idx].is_anomaly,
          anomalyScore: readings[idx].anomaly_score
        })),
        borderColor: currentMeta.color,
        backgroundColor: currentMeta.color + '18',
        borderWidth: 2.5,
        pointBackgroundColor: pointBackgroundColors,
        pointBorderColor: pointBorderColors,
        pointBorderWidth: 2,
        pointRadius: pointRadii,
        pointHoverRadius: pointHoverRadii,
        tension: 0.35,
        fill: false
      },
      {
        type: 'line',
        label: 'Upper Threshold (+2.5σ)',
        data: upperEnvelope,
        borderColor: boundColor,
        borderWidth: 1.5,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false
      },
      {
        type: 'line',
        label: 'Lower Threshold (-2.5σ)',
        data: lowerEnvelope,
        borderColor: boundColor,
        borderWidth: 1.5,
        borderDash: [5, 5],
        pointRadius: 0,
        fill: false
      }
    ];

    this.chart.update('none');
  }
}

function roundDec(val, dec = 2) {
  return Number(Math.round(val + 'e' + dec) + 'e-' + dec);
}

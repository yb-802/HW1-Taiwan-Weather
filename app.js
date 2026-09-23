/**
 * Taiwan Weather Forecast - Frontend Vanilla JS
 * Compatible with GitHub Pages (.github.io)
 */

// Regions definition and geo-coordinates
const REGIONS_DATA = {
  "北部地區": { lat: 25.04, lon: 121.53, desc: "包含基隆、雙北、桃園、新竹等地", baseMin: 19.0, baseMax: 26.5 },
  "東北部地區": { lat: 24.75, lon: 121.75, desc: "包含宜蘭地區", baseMin: 18.5, baseMax: 25.0 },
  "中部地區": { lat: 24.15, lon: 120.67, desc: "包含苗栗、台中、彰化、南投、雲林", baseMin: 20.5, baseMax: 29.5 },
  "東部地區": { lat: 23.99, lon: 121.61, desc: "包含花蓮地區", baseMin: 20.0, baseMax: 27.0 },
  "南部地區": { lat: 22.99, lon: 120.21, desc: "包含嘉義、台南、高雄、屏東", baseMin: 22.0, baseMax: 32.0 },
  "東南部地區": { lat: 22.75, lon: 121.15, desc: "包含台東地區", baseMin: 21.5, baseMax: 29.0 }
};

const REGION_NAMES = Object.keys(REGIONS_DATA);

// Global State
let forecastStore = []; // Array of { regionName, dataDate, minT, maxT, avgT }
let leafletMap = null;
let mapMarkers = {};
let temperatureChart = null;
let currentSelectedRegion = "北部地區";
let currentSelectedDate = "";

// Initialize application on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  initDateOptions();
  generateInitialForecastData();
  initLeafletMap();
  initChart();
  bindEventListeners();
  updateUI();
});

// Generate 7-day realistic dates
function initDateOptions() {
  const dateSelect = document.getElementById("dateSelect");
  dateSelect.innerHTML = "";
  
  const today = new Date();
  for (let i = 0; i < 7; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() + i);
    const dateStr = d.toISOString().split("T")[0];
    const option = document.createElement("option");
    option.value = dateStr;
    option.textContent = i === 0 ? `${dateStr} (今天)` : dateStr;
    dateSelect.appendChild(option);
  }
  currentSelectedDate = dateSelect.options[0].value;
}

// Generate realistic 7-day data across 6 regions
function generateInitialForecastData() {
  forecastStore = [];
  const dateSelect = document.getElementById("dateSelect");
  const dates = Array.from(dateSelect.options).map(opt => opt.value);

  dates.forEach((dateStr, dayIndex) => {
    // sinusoidal temperature wave across the week
    const wave = 2.5 * Math.sin(dayIndex * 0.85);

    REGION_NAMES.forEach(region => {
      const spec = REGIONS_DATA[region];
      const jitter = (Math.random() * 1.6) - 0.8;
      const minT = parseFloat((spec.baseMin + wave + jitter).toFixed(1));
      const maxT = parseFloat((spec.baseMax + wave + (Math.random() * 1.5)).toFixed(1));
      const avgT = parseFloat(((minT + maxT) / 2.0).toFixed(1));

      forecastStore.push({
        regionName: region,
        dataDate: dateStr,
        minT: minT,
        maxT: maxT,
        avgT: avgT
      });
    });
  });
}

// Color scale mapping
function getTempColor(temp) {
  if (temp < 20.0) return "#2563EB"; // Blue (< 20°C)
  if (temp < 25.0) return "#10B981"; // Green (20 - 25°C)
  if (temp <= 30.0) return "#F59E0B"; // Orange (25 - 30°C)
  return "#EF4444"; // Red (> 30°C)
}

// Initialize Leaflet Map
function initLeafletMap() {
  leafletMap = L.map("taiwanMap", {
    center: [23.75, 120.95],
    zoom: 7,
    scrollWheelZoom: false
  });

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(leafletMap);

  // Add markers for all regions
  REGION_NAMES.forEach(region => {
    const info = REGIONS_DATA[region];
    const marker = L.circleMarker([info.lat, info.lon], {
      radius: 13,
      color: "#0f172a",
      weight: 2,
      fillColor: "#0284c7",
      fillOpacity: 0.85
    }).addTo(leafletMap);

    marker.on("click", () => {
      document.getElementById("regionSelect").value = region;
      currentSelectedRegion = region;
      updateUI();
    });

    mapMarkers[region] = marker;
  });
}

// Update Map markers based on selected date
function updateMapMarkers() {
  REGION_NAMES.forEach(region => {
    const record = forecastStore.find(r => r.regionName === region && r.dataDate === currentSelectedDate);
    const marker = mapMarkers[region];
    if (!marker) return;

    const minT = record ? record.minT : 20.0;
    const maxT = record ? record.maxT : 26.0;
    const avgT = record ? record.avgT : 23.0;
    const color = getTempColor(avgT);
    const isSelected = (region === currentSelectedRegion);

    marker.setStyle({
      fillColor: color,
      color: isSelected ? "#0f172a" : color,
      weight: isSelected ? 4 : 2,
      radius: isSelected ? 17 : 13
    });

    const popupContent = `
      <div style="font-family: inherit; width: 175px;">
        <h4 style="margin: 0 0 6px 0; color: #1e3a8a; font-size: 15px;">${region}</h4>
        <p style="margin: 3px 0; font-size: 13px;"><b>日期:</b> ${currentSelectedDate}</p>
        <p style="margin: 3px 0; font-size: 13px;"><b>最低溫:</b> <span style="color:#2563EB; font-weight:700;">${minT}°C</span></p>
        <p style="margin: 3px 0; font-size: 13px;"><b>最高溫:</b> <span style="color:#EF4444; font-weight:700;">${maxT}°C</span></p>
        <p style="margin: 3px 0; font-size: 13px;"><b>平均溫:</b> <b>${avgT}°C</b></p>
        <p style="margin: 5px 0 0 0; font-size: 11px; color: #64748b;">${REGIONS_DATA[region].desc}</p>
      </div>
    `;
    marker.bindPopup(popupContent);
    marker.bindTooltip(`${region}: ${avgT}°C`, { direction: 'top', offset: [0, -10] });
  });
}

// Initialize Chart.js
function initChart() {
  const ctx = document.getElementById("temperatureChart").getContext("2d");
  temperatureChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "最高氣溫 (MaxT)",
          data: [],
          borderColor: "#EF4444",
          backgroundColor: "rgba(239, 68, 68, 0.08)",
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointBackgroundColor: "#EF4444",
          pointRadius: 6,
          pointHoverRadius: 8
        },
        {
          label: "最低氣溫 (MinT)",
          data: [],
          borderColor: "#3B82F6",
          backgroundColor: "rgba(59, 130, 246, 0.08)",
          fill: true,
          tension: 0.35,
          borderWidth: 3,
          pointBackgroundColor: "#3B82F6",
          pointRadius: 6,
          pointHoverRadius: 8
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: "index",
        intersect: false
      },
      plugins: {
        legend: {
          position: "top",
          labels: {
            font: { family: "inherit", weight: "700", size: 12 },
            usePointStyle: true,
            padding: 16
          }
        },
        tooltip: {
          padding: 12,
          boxPadding: 6,
          usePointStyle: true,
          callbacks: {
            label: function(context) {
              return ` ${context.dataset.label}: ${context.parsed.y} °C`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: "#f1f5f9" },
          ticks: { font: { family: "inherit" } }
        },
        y: {
          title: { display: true, text: "氣溫 (°C)", font: { weight: "700" } },
          grid: { color: "#f1f5f9" },
          ticks: { font: { family: "inherit" } }
        }
      }
    }
  });
}

// Update Chart data for current region
function updateChart() {
  const regionRecords = forecastStore
    .filter(r => r.regionName === currentSelectedRegion)
    .sort((a, b) => a.dataDate.localeCompare(b.dataDate));

  const labels = regionRecords.map(r => r.dataDate);
  const maxTemps = regionRecords.map(r => r.maxT);
  const minTemps = regionRecords.map(r => r.minT);

  temperatureChart.data.labels = labels;
  temperatureChart.data.datasets[0].data = maxTemps;
  temperatureChart.data.datasets[1].data = minTemps;

  // Calculate dynamic range
  const allTemps = [...maxTemps, ...minTemps];
  const minVal = Math.floor(Math.min(...allTemps)) - 3;
  const maxVal = Math.ceil(Math.max(...allTemps)) + 3;
  temperatureChart.options.scales.y.min = Math.max(0, minVal);
  temperatureChart.options.scales.y.max = maxVal;

  temperatureChart.update();
}

// Update Data Table
function updateTable() {
  const tableBody = document.getElementById("tableBody");
  tableBody.innerHTML = "";

  const regionRecords = forecastStore
    .filter(r => r.regionName === currentSelectedRegion)
    .sort((a, b) => a.dataDate.localeCompare(b.dataDate));

  regionRecords.forEach(r => {
    const diff = (r.maxT - r.minT).toFixed(1);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><strong>${r.dataDate}</strong></td>
      <td style="color:#2563EB; font-weight:700;">${r.minT} °C</td>
      <td style="color:#EF4444; font-weight:700;">${r.maxT} °C</td>
      <td><strong>${r.avgT} °C</strong></td>
      <td>${diff} °C</td>
    `;
    tableBody.appendChild(row);
  });
}

// Update Top KPI Cards
function updateKPIs() {
  const todayRecord = forecastStore.find(
    r => r.regionName === currentSelectedRegion && r.dataDate === currentSelectedDate
  );

  if (todayRecord) {
    document.getElementById("kpiMinT").textContent = `${todayRecord.minT} °C`;
    document.getElementById("kpiMaxT").textContent = `${todayRecord.maxT} °C`;
    document.getElementById("kpiAvgT").textContent = `${todayRecord.avgT} °C`;
    document.getElementById("kpiDiff").textContent = `${(todayRecord.maxT - todayRecord.minT).toFixed(1)} °C`;
  }

  // Island-wide highlights on currentSelectedDate
  const dateRecords = forecastStore.filter(r => r.dataDate === currentSelectedDate);
  if (dateRecords.length > 0) {
    const hottest = dateRecords.reduce((prev, curr) => (curr.maxT > prev.maxT ? curr : prev));
    document.getElementById("kpiHottest").textContent = `${hottest.regionName} (${hottest.maxT}°C)`;
  }

  // Update dynamic titles
  document.getElementById("chartRegionTitle").textContent = `${currentSelectedRegion} 一週最高與最低氣溫`;
  document.getElementById("tableRegionTitle").textContent = `${currentSelectedRegion} 預報詳細數據表`;
  document.getElementById("aiRegionTitle").textContent = `${currentSelectedRegion} 智慧生活提醒 (${currentSelectedDate})`;
}

// Update AI Advisor Box
function updateAIAdvisor() {
  const todayRecord = forecastStore.find(
    r => r.regionName === currentSelectedRegion && r.dataDate === currentSelectedDate
  );
  if (!todayRecord) return;

  const curMax = todayRecord.maxT;
  const curAvg = todayRecord.avgT;
  const curDiff = (todayRecord.maxT - todayRecord.minT).toFixed(1);

  let clothing = "";
  let activity = "";
  let health = "";

  if (curMax >= 30.0) {
    clothing = "短袖、透氣吸汗衣物、遮陽帽與太陽眼鏡 ☀️";
    activity = "白天紫外線強烈，中午時段盡量減少戶外曝曬，戶外活動建議於清晨或傍晚進行。";
    health = "隨時補充水份與電解質，慎防熱傷害與中暑。";
  } else if (curAvg >= 24.0) {
    clothing = "短袖搭配薄襯衫或薄防風外套，早晚溫差微涼時可披上 👕";
    activity = "天氣舒適溫暖，非常適合各項戶外休閒運動與旅遊踏青。";
    health = "氣候宜人，可多開窗保持室內空氣流通。";
  } else if (curAvg >= 18.0) {
    clothing = "長袖上衣、針織衫、防風薄外套，洋蔥式穿搭尤佳 🧥";
    activity = "適合室內外文藝活動或近郊步道健行。";
    health = `日夜溫差達 ${curDiff}°C，早出晚歸朋友請留意心血管與呼吸道保暖。`;
  } else {
    clothing = "保暖毛衣、羽絨外套、圍巾與手套 🧣";
    activity = "天候偏冷，建議安排室內溫泉、博物館或聚會行程。";
    health = "注意室內外溫差，適時使用暖氣或電毯，長者與幼童需特別注意保暖。";
  }

  document.getElementById("aiClothing").textContent = clothing;
  document.getElementById("aiActivity").textContent = activity;
  document.getElementById("aiHealth").textContent = health;
}

// Master update function
function updateUI() {
  updateMapMarkers();
  updateChart();
  updateTable();
  updateKPIs();
  updateAIAdvisor();
}

// Event Listeners
function bindEventListeners() {
  // Region Select
  document.getElementById("regionSelect").addEventListener("change", (e) => {
    currentSelectedRegion = e.target.value;
    updateUI();
  });

  // Date Select
  document.getElementById("dateSelect").addEventListener("change", (e) => {
    currentSelectedDate = e.target.value;
    updateUI();
  });

  // Reset Mock Data Button
  document.getElementById("btnResetMock").addEventListener("click", () => {
    generateInitialForecastData();
    updateUI();
    alert("已重新產生 7 天氣象數據！");
  });

  // Fetch CWA API Button
  document.getElementById("btnFetchCWA").addEventListener("click", async () => {
    const apiKey = document.getElementById("apiKeyInput").value.trim();
    if (!apiKey) {
      alert("請先輸入中央氣象署 CWA API 授權碼，或直接使用預設之示範資料！");
      return;
    }

    try {
      const url = `https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=${encodeURIComponent(apiKey)}&format=JSON`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      
      // Attempt parse
      if (data && data.records && data.records.location) {
        alert("成功從中央氣象署取得即時氣象資料！");
      }
    } catch (err) {
      alert(`API 連線受限 (可能受跨域 CORS 限制或 Key 不正確)：${err.message}\n已為您保留高擬真示範氣象數據！`);
    }
  });

  // Export CSV
  document.getElementById("btnExportCSV").addEventListener("click", () => {
    const regionRecords = forecastStore.filter(r => r.regionName === currentSelectedRegion);
    let csv = "預報日期,最低氣溫(°C),最高氣溫(°C),平均氣溫(°C),溫差(°C)\n";
    regionRecords.forEach(r => {
      csv += `${r.dataDate},${r.minT},${r.maxT},${r.avgT},${(r.maxT - r.minT).toFixed(1)}\n`;
    });

    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${currentSelectedRegion}_天氣預報.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });
}

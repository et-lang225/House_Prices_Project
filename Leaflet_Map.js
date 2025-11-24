
const map = L.map('map').setView([37.8, -96], 4);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
}).addTo(map);

// Global store for the ZIP scores
let zipScores = {};
let minRank = Infinity;
let maxRank = -Infinity;


fetch("zip_scores.json")
  .then(res => {
    console.log("zip_scores fetch response:", res);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return res.json();
  })
  .then(data => {
    console.log("zip_scores.json data:", data); // check contents
    data.forEach(d => {
      const z = String(d.zip_code).padStart(5, "0");
      zipScores[z] = {
        ...d,
        rank: +d.rank,
        Predicted_Price: +d.Predicted_Price,
        Total_Pop: +d.Total_Pop,
        Homicide_Rate: +d.Homicide_Rate
      };

    if (zipScores[z].rank < minRank) minRank = zipScores[z].rank;
    if (zipScores[z].rank > maxRank) maxRank = zipScores[z].rank;
  });

    console.log("zipScores object:", zipScores); // verify keys and values
    loadZCTA();
  })
  .catch(err => console.error("Failed to load zip_scores.json:", err));



function loadZCTA() {
  fetch("us_zip_codes_wgs84.geojson")
    .then(res => res.json())
    .then(geojson => {
      L.geoJson(geojson, {
        style: feature => styleZCTA(feature),
        onEachFeature: (feature, layer) => popupZCTA(feature, layer)
      }).addTo(map);
    })
    .catch(err => console.error("Failed to load GeoJSON:", err));
}

function getZipFromFeature(feature) {
  // Use whichever property exists
  const rawZip =
    feature.properties.ZCTA5CE10 ??
    feature.properties.ZIP ??
    feature.properties.zip_code;

  // Convert to string and pad to 5 digits
  return String(rawZip).padStart(5, "0");
}

function styleZCTA(feature) {
  const zip = getZipFromFeature(feature);
  const stats = zipScores[zip];

  if (!stats) {
    console.log("No match for ZIP:", zip);
    return { fillColor: "#cccccc", weight: 1, color: "#333", fillOpacity: 0.5 };
  }

  return {
    fillColor: colorFromRank(stats.rank, minRank, maxRank),
    weight: 1,
    color: "#333",
    fillOpacity: 0.75
  };
}

// ================================
// 5. Popups for each ZIP
// ================================
function popupZCTA(feature, layer) {
  const zip = getZipFromFeature(feature);
  const s = zipScores[zip];

  if (!s) {
    layer.bindPopup(`<b>ZIP:</b> ${zip}<br>No score data available.`);
    return;
  }

  layer.bindPopup(`
    <b>ZIP Code:</b> ${zip}<br>
    <b>Rank:</b> ${s.rank}<br>
    <b>Predicted Price:</b> $${s.Predicted_Price.toLocaleString()}<br>
    <b>Total Population:</b> ${s.Total_Pop.toLocaleString()}<br>
    <b>Homicide Rate:</b> ${s.Homicide_Rate}
  `);
}

// ================================
// 6. Color Gradient Function (green → red)
// ================================
function colorFromRank(rank, minRank, maxRank) {
  // Handle case where min == max
  if (minRank === maxRank) return "hsl(120, 100%, 50%)"; // green fallback

  // Compute normalized t (0 → 1)
  const t = (rank - minRank) / (maxRank - minRank);

  // Green → Red using HSL
  const hue = 120 * (1 - t); // 120=green, 0=red
  return `hsl(${hue}, 100%, 50%)`;
}

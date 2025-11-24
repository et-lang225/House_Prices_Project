
const map = L.map('map').setView([37.8, -96], 4);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 18,
}).addTo(map);

// zipScores is defined in zip_scores.js
let minRank = Infinity;
let maxRank = -Infinity;

// Compute min/max ranks
for (const z in zipScores) {
  const r = zipScores[z].rank;
  if (r < minRank) minRank = r;
  if (r > maxRank) maxRank = r;
}

L.geoJson(zctaGeoJson, {
  style: feature => styleZCTA(feature),
  onEachFeature: (feature, layer) => popupZCTA(feature, layer)
}).addTo(map);



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


function colorFromRank(rank, minRank, maxRank) {

  if (minRank === maxRank) return "hsl(120, 100%, 50%)"; // green fallback

  const t = (rank - minRank) / (maxRank - minRank);

  const hue = 120 * (1 - t); // 120=green, 0=red
  return `hsl(${hue}, 100%, 50%)`;
}

const MAX_POINTS = 60;
const COLORS = { temperature: "#f97316", humidity: "#38bdf8", light: "#facc15" };

const cardsEl = document.getElementById("cards");
const logEl = document.getElementById("log");
const connEl = document.getElementById("conn");
const cards = {};
const datasets = {};

const chart = new Chart(document.getElementById("chart"), {
  type: "line",
  data: { labels: [], datasets: [] },
  options: {
    animation: false,
    scales: { y: { type: "logarithmic" } }, // sensors have very different ranges
    plugins: { legend: { labels: { color: "#e2e8f0" } } },
  },
});

function ensureSensor(name) {
  if (cards[name]) return;
  const el = document.createElement("div");
  el.className = "card";
  el.innerHTML = `<div class="label">${name}</div><div class="value">--</div>`;
  cardsEl.appendChild(el);
  cards[name] = el;

  const ds = { label: name, data: [], borderColor: COLORS[name], pointRadius: 2, tension: 0.3,
               pointBackgroundColor: [] };
  datasets[name] = ds;
  chart.data.datasets.push(ds);
}

function handle(r) {
  ensureSensor(r.sensor);
  const card = cards[r.sensor];
  card.querySelector(".value").textContent = `${r.value} ${r.unit}`;
  card.classList.toggle("anomaly", r.anomaly);

  const ds = datasets[r.sensor];
  ds.data.push(r.value);
  ds.pointBackgroundColor.push(r.anomaly ? "#ef4444" : COLORS[r.sensor]);
  if (r.sensor === "temperature") {
    chart.data.labels.push(new Date(r.timestamp).toLocaleTimeString());
  }
  if (ds.data.length > MAX_POINTS) { ds.data.shift(); ds.pointBackgroundColor.shift(); }
  if (chart.data.labels.length > MAX_POINTS) chart.data.labels.shift();
  chart.update();

  if (r.anomaly) {
    if (logEl.firstChild && logEl.firstChild.classList.contains("muted")) logEl.innerHTML = "";
    const li = document.createElement("li");
    li.textContent = `${new Date(r.timestamp).toLocaleTimeString()}  ${r.sensor}: ${r.value} ${r.unit} (${r.reason})`;
    logEl.prepend(li);
  }
}

function connect() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${location.host}/ws`);
  ws.onopen = () => { connEl.textContent = "connected"; connEl.className = "badge on"; };
  ws.onclose = () => { connEl.textContent = "disconnected"; connEl.className = "badge off"; setTimeout(connect, 2000); };
  ws.onmessage = (e) => handle(JSON.parse(e.data));
}
connect();

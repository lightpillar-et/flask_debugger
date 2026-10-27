const $ = (selector) => document.querySelector(selector);

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
  }[character]));
}

async function loadDashboard() {
  const query = new URLSearchParams();
  if ($("#method-filter").value) query.set("method", $("#method-filter").value);
  if ($("#url-filter").value) query.set("url", $("#url-filter").value);
  if ($("#status-filter").value) query.set("status", $("#status-filter").value);
  const [summary, requests, performance, errors] = await Promise.all([
    fetch("api/summary").then((response) => response.json()),
    fetch(`api/requests?${query}`).then((response) => response.json()),
    fetch("api/performance").then((response) => response.json()),
    fetch("api/errors").then((response) => response.json())
  ]);
  $("#total-requests").textContent = summary.total_requests;
  $("#successful-requests").textContent = summary.successful_requests;
  $("#error-requests").textContent = summary.error_requests;
  $("#average-duration").textContent = `${summary.average_duration_ms} ms`;
  $("#last-updated").textContent = `Updated ${new Date().toLocaleTimeString()}`;
  renderRequests(requests.requests);
  renderPerformance(performance);
  renderErrors(errors.errors);
}

function renderRequests(records) {
  $("#request-rows").innerHTML = records.length ? records.map((record) => `
    <tr data-id="${escapeHtml(record.id)}"><td><span class="method">${escapeHtml(record.method)}</span></td>
    <td class="url">${escapeHtml(record.url)}</td><td><span class="status status-${Math.floor(record.status_code / 100)}xx">${record.status_code}</span></td>
    <td>${record.duration_ms} ms</td><td>${escapeHtml(record.timestamp)}</td></tr>`).join("")
    : '<tr><td colspan="5" class="empty">No matching requests.</td></tr>';
  document.querySelectorAll("#request-rows tr[data-id]").forEach((row) => row.addEventListener("click", () => showDetail(row.dataset.id)));
}

function renderPerformance(data) {
  $("#performance-content").innerHTML = data.count ? `
    <div class="performance-stats"><span>Average <strong>${data.average_duration_ms} ms</strong></span><span>Fastest <strong>${data.min_duration_ms} ms</strong></span><span>Slowest <strong>${data.max_duration_ms} ms</strong></span></div>
    <div class="bars">${data.durations.slice(0, 20).reverse().map((item) => `<div class="bar" title="${escapeHtml(item.url)}: ${item.duration_ms} ms" style="height:${Math.max(8, Math.min(100, item.duration_ms))}%"></div>`).join("")}</div>` : "No performance data yet.";
}

function renderErrors(records) {
  $("#error-list").innerHTML = records.length ? records.slice(0, 8).map((record) => `<button class="error-item" data-id="${escapeHtml(record.id)}"><span class="status status-${Math.floor(record.status_code / 100)}xx">${record.status_code}</span><span>${escapeHtml(record.method)} ${escapeHtml(record.url)}</span></button>`).join("") : "No errors recorded.";
  document.querySelectorAll(".error-item").forEach((item) => item.addEventListener("click", () => showDetail(item.dataset.id)));
}

async function showDetail(id) {
  const record = await fetch(`api/requests/${encodeURIComponent(id)}`).then((response) => response.json());
  $("#modal-title").textContent = `${record.method} ${record.url}`;
  $("#modal-data").textContent = JSON.stringify(record, null, 2);
  $("#request-modal").classList.remove("hidden");
}

["method-filter", "url-filter", "status-filter"].forEach((id) => $(`#${id}`).addEventListener("input", loadDashboard));
$("#close-modal").addEventListener("click", () => $("#request-modal").classList.add("hidden"));
$("#request-modal").addEventListener("click", (event) => { if (event.target.id === "request-modal") event.target.classList.add("hidden"); });
loadDashboard();
setInterval(loadDashboard, 5000);

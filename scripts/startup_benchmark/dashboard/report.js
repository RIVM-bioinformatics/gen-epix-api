(() => {
  "use strict";
  const evidence = JSON.parse(document.getElementById("benchmark-data").textContent);
  const byId = (id) => document.getElementById(id);
  const config = {responsive: true, displaylogo: false, scrollZoom: true};
  const escaped = (value) => String(value ?? "").replace(/[&<>"']/g, (character) =>
    ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[character]));
  const format = (value) => value == null ? "Unavailable" : value.toFixed(3);
  const layout = (title) => ({
    title: {text: title}, font: {family: "system-ui, sans-serif", color: "#183044"},
    margin: {t: 55, r: 30, b: 65, l: 65}, height: 350,
    paper_bgcolor: "white", plot_bgcolor: "#f7fafc",
    legend: {orientation: "h", y: -0.25},
  });
  const thresholds = (axis) => [
    {value: evidence.statistics.target_seconds, label: "15s target", color: "#ba4a37"},
    {value: evidence.statistics.p95, label: "Overall p95", color: "#7952a1"},
  ].filter((item) => item.value != null).map((item) => axis === "y" ? {
    type: "line", xref: "paper", x0: 0, x1: 1, yref: "y", y0: item.value, y1: item.value,
    line: {color: item.color, dash: "dash"}, label: {text: item.label},
  } : {
    type: "line", yref: "paper", y0: 0, y1: 1, xref: "x", x0: item.value, x1: item.value,
    line: {color: item.color, dash: "dash"}, label: {text: item.label},
  });
  const populate = (id, values) => {
    for (const value of values) {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      byId(id).append(option);
    }
  };
  const table = (id, rows) => {
    const fragment = document.createDocumentFragment();
    for (const row of rows) {
      const tr = document.createElement("tr");
      for (const value of row) {
        const td = document.createElement("td");
        td.textContent = value ?? "Unavailable";
        tr.append(td);
      }
      fragment.append(tr);
    }
    byId(id).replaceChildren(fragment);
  };
  const sorted = (records, key, order) => [...records].sort((a, b) => {
    // Unknown durations stay last in both directions.
    if (a[key] == null && b[key] != null) return 1;
    if (b[key] == null && a[key] != null) return -1;
    const comparison = typeof a[key] === "number" ? a[key] - b[key] :
      String(a[key] ?? "").localeCompare(String(b[key] ?? ""));
    return (order === "asc" ? comparison : -comparison) ||
      (a.id ?? a.index) - (b.id ?? b.index);
  });

  const measured = evidence.records.filter((record) => record.kind === "measured");
  const successful = [];
  const measuredWithTrend = measured.map((record) => {
    if (record.status !== "success") return {...record, average: null};
    successful.push(record.seconds);
    return {...record, average: successful.length >= 5 ?
      successful.slice(-5).reduce((total, value) => total + value, 0) / 5 : null};
  });
  const indices = evidence.records.map((record) => record.index);
  const first = indices.length ? Math.min(...indices) : 0;
  const last = indices.length ? Math.max(...indices) : 0;
  const inRange = (record) => record.index >= Number(byId("run-min").value) &&
    record.index <= Number(byId("run-max").value);
  populate("kind", [...new Set(evidence.records.map((r) => r.kind))].sort());
  populate("status", [...new Set(evidence.records.map((r) => r.status))].sort());

  function attempts() {
    const records = evidence.records.filter((record) => inRange(record) &&
      (!byId("kind").value || record.kind === byId("kind").value) &&
      (!byId("status").value || record.status === byId("status").value));
    table("attempts", sorted(records, byId("attempt-sort").value, byId("attempt-order").value)
      .map((r) => [r.index, r.kind, r.status, format(r.seconds), r.cleanup, r.error ?? "—"]));
    byId("attempt-count").textContent = `${records.length} of ${evidence.records.length} attempts shown. Kind and status filters apply to this table.`;
  }

  function startup() {
    const records = measuredWithTrend.filter(inRange);
    const successes = records.filter((r) => r.status === "success");
    const unavailable = records.filter((r) => r.status !== "success");
    byId("startup-empty").hidden = successes.length > 0;
    byId("selected-count").textContent = `${successes.length} of ${successful.length} successful measured runs selected · ${unavailable.length} failed or unattempted. Overall statistics are unchanged.`;
    const chartLayout = {
      ...layout("Measured startup durations"), shapes: thresholds("y"),
      margin: {t: 55, r: unavailable.length ? 105 : 30, b: 65, l: 65},
      xaxis: {title: {text: "Original run number"}, dtick: records.length < 20 ? 1 : undefined},
      yaxis: {title: {text: "Seconds"}, rangemode: "tozero"},
      yaxis2: {overlaying: "y", side: "right", range: [-1, 12], tickvals: [0, 1],
        ticktext: ["Not attempted", "Failed"], showgrid: false, zeroline: false},
    };
    const traces = [{
      name: "Startup", type: "scatter", mode: "lines+markers", connectgaps: false,
      x: records.map((r) => r.index), y: records.map((r) => r.status === "success" ? r.seconds : null),
      line: {color: "#237ba0"}, hovertemplate: "Run %{x}<br>%{y:.3f} s<extra>Measured startup</extra>",
    }];
    if (byId("trend").checked) traces.push({
      name: "Five-sample average", type: "scatter", mode: "lines", connectgaps: false,
      x: records.map((r) => r.index), y: records.map((r) => r.average),
      line: {color: "#d68a28", dash: "dot"},
      hovertemplate: "Run %{x}<br>%{y:.3f} s<extra>Trailing average</extra>",
    });
    if (unavailable.length) traces.push({
      name: "Unavailable duration", type: "scatter", mode: "markers", yaxis: "y2",
      x: unavailable.map((r) => r.index), y: unavailable.map((r) => r.status === "not_attempted" ? 0 : 1),
      marker: {symbol: "x", color: "#ba4a37", size: 10},
      customdata: unavailable.map((r) => [escaped(r.status), escaped(r.error)]),
      hovertemplate: "Run %{x}<br>%{customdata[0]}<br>%{customdata[1]}<extra>No duration</extra>",
    });
    Plotly.react("startup-chart", traces, chartLayout, config);
    const bins = Math.max(1, Math.min(100, Math.round(Number(byId("bins").value) || 10)));
    Plotly.react("histogram", [{type: "histogram", x: successes.map((r) => r.seconds),
      nbinsx: bins, marker: {color: "#237ba0"}, name: "Successful measured runs",
      hovertemplate: "%{x} s<br>%{y} runs<extra></extra>"}], {
      ...layout("Successful measured durations"),
      xaxis: {title: {text: "Seconds"}}, yaxis: {title: {text: "Run count"}, dtick: 1},
    }, config);
    attempts();
  }

  let page = 0;
  const pageSize = 50;
  for (const [index, diagnostic] of evidence.imports.entries()) {
    const option = document.createElement("option");
    option.value = index;
    option.textContent = `Run ${diagnostic.run}`;
    byId("import-run").append(option);
  }
  byId("imports-empty").hidden = evidence.imports.length > 0;
  byId("imports-panel").hidden = evidence.imports.length === 0;

  function imports() {
    if (!evidence.imports.length) return;
    const diagnostic = evidence.imports[Number(byId("import-run").value)];
    const search = byId("module-search").value.toLowerCase();
    const metric = byId("import-sort").value;
    const records = sorted(diagnostic.records.filter((r) => r.module.toLowerCase().includes(search)),
      metric, byId("import-order").value);
    byId("import-interpretation").textContent = diagnostic.interpretation;
    const warnings = diagnostic.warnings.map((warning) => {
      const li = document.createElement("li"); li.textContent = warning; return li;
    });
    byId("import-warnings").replaceChildren(...warnings);
    byId("import-count").textContent = `${records.length} of ${diagnostic.records.length} import occurrences match. Repeated modules are separate occurrences.`;
    const top = records.slice(0, 20).reverse();
    Plotly.react("import-chart", [
      {name: "Self ms", type: "bar", orientation: "h", x: top.map((r) => r.self_us / 1000),
        y: top.map((r) => `${escaped(r.module)} (#${r.id})`), marker: {color: "#237ba0"},
        customdata: top.map((r) => escaped(r.chain.join(" → "))),
        hovertemplate: "%{y}<br>Self: %{x:.3f} ms<br>%{customdata}<extra></extra>"},
      {name: "Cumulative ms", type: "bar", orientation: "h", x: top.map((r) => r.cumulative_us / 1000),
        y: top.map((r) => `${escaped(r.module)} (#${r.id})`), marker: {color: "#7952a1"},
        hovertemplate: "%{y}<br>Cumulative: %{x:.3f} ms<extra>Do not sum</extra>"},
    ], {...layout("First 20 import occurrences by selected sort"), barmode: "group",
      height: Math.max(350, top.length * 38 + 120), margin: {t: 55, b: 65, l: 220, r: 25},
      xaxis: {title: {text: "Milliseconds"}}, yaxis: {automargin: true},
      annotations: records.length ? [] : [{text: "No import occurrences match", showarrow: false,
        xref: "paper", yref: "paper", x: 0.5, y: 0.5}],
    }, config);
    const pages = Math.max(1, Math.ceil(records.length / pageSize));
    page = Math.min(page, pages - 1);
    table("import-rows", records.slice(page * pageSize, (page + 1) * pageSize)
      .map((r) => [r.id, r.module, format(r.self_us / 1000), format(r.cumulative_us / 1000), r.chain.join(" → ")]));
    byId("page").textContent = `Page ${page + 1} of ${pages} · ${pageSize} occurrences per page`;
    byId("previous").disabled = page === 0;
    byId("next").disabled = page === pages - 1;
  }

  function reset() {
    byId("run-min").value = first; byId("run-max").value = last;
    byId("trend").checked = true; byId("bins").value = 10;
    byId("kind").value = ""; byId("status").value = "";
    byId("attempt-sort").value = "index"; byId("attempt-order").value = "asc";
    byId("import-run").value = "0"; byId("module-search").value = "";
    byId("import-sort").value = "self_us"; byId("import-order").value = "desc";
    page = 0; startup(); imports();
  }
  for (const id of ["run-min", "run-max", "bins", "trend"]) byId(id).addEventListener("input", startup);
  for (const id of ["kind", "status", "attempt-sort", "attempt-order"]) byId(id).addEventListener("change", attempts);
  for (const id of ["import-run", "module-search", "import-sort", "import-order"]) {
    byId(id).addEventListener("input", () => {page = 0; imports();});
  }
  byId("previous").addEventListener("click", () => {page--; imports();});
  byId("next").addEventListener("click", () => {page++; imports();});
  byId("reset").addEventListener("click", reset);
  reset();
})();

"""Generate a self-contained HTML dashboard without external assets or services."""

from __future__ import annotations

import json
from pathlib import Path

from .models import SkuAnalysis


def write_dashboard(path: str | Path, analyses: list[SkuAnalysis], summary: dict[str, object]) -> None:
    records = [analysis.as_record() for analysis in analyses]
    payload = json.dumps({"summary": summary, "rows": records}, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="ShelfSense retail sales and inventory decision dashboard">
<title>ShelfSense | Retail operations</title>
<style>
:root{color-scheme:light;--ink:#18231f;--muted:#66736d;--line:#e2e9e4;--paper:#f5f7f4;--card:#fff;--green:#176b52;--green-soft:#e4f2eb;--amber:#986313;--amber-soft:#fbf1dc;--red:#a43b35;--shadow:0 8px 28px rgba(29,55,43,.06)}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:14px/1.5 Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
.shell{max-width:1220px;margin:0 auto;padding:34px 28px 56px}.top{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-bottom:28px}.brand{display:flex;align-items:center;gap:13px}.mark{width:42px;height:42px;border-radius:13px;background:var(--green);display:grid;place-items:center;color:white;font-weight:800;font-size:19px;letter-spacing:-1px}.eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:.14em;color:var(--muted);font-weight:700}.brand h1{margin:1px 0 0;font-size:22px;letter-spacing:-.04em}.period{color:var(--muted);font-size:12px;text-align:right}.period strong{display:block;color:var(--ink);font-size:13px;font-weight:650}
.intro{display:flex;justify-content:space-between;align-items:end;gap:20px;margin:0 0 20px}.intro h2{margin:0;font-size:26px;letter-spacing:-.045em}.intro p{margin:5px 0 0;color:var(--muted)}.badge{border:1px solid #d7e5dc;background:#fafffc;color:var(--green);padding:7px 11px;border-radius:999px;font-size:11px;font-weight:700;white-space:nowrap}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin-bottom:16px}.card{background:var(--card);border:1px solid var(--line);border-radius:15px;box-shadow:var(--shadow)}.kpi{padding:17px 18px}.kpi-label{color:var(--muted);font-size:12px;font-weight:600}.kpi-value{margin-top:8px;font-size:25px;font-weight:750;letter-spacing:-.045em}.kpi-note{margin-top:3px;font-size:11px;color:var(--muted)}
.grid{display:grid;grid-template-columns:1.1fr .9fr;gap:14px;margin-bottom:16px}.panel{padding:19px 20px}.panel-head{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:16px}.panel h3{margin:0;font-size:14px;letter-spacing:-.01em}.sub{color:var(--muted);font-size:11px}.bars{display:grid;gap:13px}.bar-row{display:grid;grid-template-columns:24px 1fr 42px;gap:10px;align-items:center;font-size:12px}.bar-track{height:9px;background:#edf1ee;border-radius:20px;overflow:hidden}.bar-fill{height:100%;border-radius:20px;background:var(--green)}.bar-row:nth-child(2) .bar-fill{background:#8caa9b}.bar-row:nth-child(3) .bar-fill{background:#c4d4ca}.bar-count{text-align:right;color:var(--muted);font-variant-numeric:tabular-nums}
.insight{padding:14px 15px;border-radius:11px;background:#f6f8f6;color:var(--muted);font-size:12px}.insight strong{color:var(--ink)}.segment-list{display:flex;flex-wrap:wrap;gap:7px;margin:14px 0 0}.chip{padding:5px 8px;border:1px solid var(--line);border-radius:8px;font-size:11px;color:var(--muted)}
.table-panel{padding:19px 0 0}.table-head{padding:0 20px 14px;display:flex;justify-content:space-between;align-items:center;gap:12px}.table-head h3{margin:0;font-size:14px}.search{width:220px;max-width:45vw;border:1px solid var(--line);border-radius:9px;padding:8px 10px;font:inherit;font-size:12px;outline:none}.search:focus{border-color:#8bb7a1;box-shadow:0 0 0 3px #e4f2eb} .table-wrap{overflow-x:auto;border-top:1px solid var(--line)}table{width:100%;border-collapse:collapse;white-space:nowrap}th,td{text-align:left;padding:12px 15px;border-bottom:1px solid #edf1ee;font-size:12px}th{color:var(--muted);font-weight:650;background:#fbfcfb}td{font-variant-numeric:tabular-nums}tbody tr:hover{background:#fafcfb}.sku{font-weight:700;color:var(--ink)}.product{color:var(--muted);font-size:11px}.pill{display:inline-flex;align-items:center;padding:3px 7px;border-radius:6px;font-size:10px;font-weight:750}.reorder{color:var(--amber);background:var(--amber-soft)}.hold{color:var(--green);background:var(--green-soft)}.empty{padding:25px;text-align:center;color:var(--muted)}
.footer{margin-top:15px;display:flex;justify-content:space-between;gap:12px;color:var(--muted);font-size:10px}.footer strong{color:#45554d;font-weight:650}
@media(max-width:850px){.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}.grid{grid-template-columns:1fr}.intro{align-items:start;flex-direction:column}.period{text-align:left}}
@media(max-width:520px){.shell{padding:22px 14px 36px}.top{align-items:start;flex-direction:column}.period{text-align:left}.kpis{gap:8px}.kpi{padding:13px}.kpi-value{font-size:21px}.table-head{align-items:start;flex-direction:column}.search{width:100%;max-width:none}.footer{flex-direction:column}}
</style>
</head>
<body>
<main class="shell">
  <header class="top">
    <div class="brand"><div class="mark">S</div><div><div class="eyebrow">Operations intelligence</div><h1>ShelfSense</h1></div></div>
    <div class="period"><span>Observed sales window</span><strong id="period">—</strong></div>
  </header>
  <section class="intro"><div><h2>Inventory overview</h2><p>Commercial performance and replenishment signals in one place.</p></div><span class="badge">LOCAL REPORT · NO LIVE CONNECTION</span></section>
  <section class="kpis" id="kpis"></section>
  <section class="grid">
    <article class="card panel"><div class="panel-head"><h3>ABC segmentation</h3><span class="sub">SKU count by class</span></div><div class="bars" id="abc-bars"></div><div class="segment-list" id="xyz-chips"></div></article>
    <article class="card panel"><div class="panel-head"><h3>Decision snapshot</h3><span class="sub">Current inventory position</span></div><div class="insight" id="decision-insight"></div><div class="segment-list" id="decision-chips"></div></article>
  </section>
  <section class="card table-panel">
    <div class="table-head"><div><h3>Replenishment worklist</h3><div class="sub">SKUs at or below their calculated reorder point</div></div><input class="search" id="search" type="search" placeholder="Filter by SKU or product name" aria-label="Filter replenishment worklist"></div>
    <div class="table-wrap"><table><thead><tr><th>Product</th><th>Class</th><th>Position</th><th>Reorder point</th><th>Suggested qty</th><th>Est. value</th><th>Action</th></tr></thead><tbody id="reorder-rows"></tbody></table><div class="empty" id="empty" hidden>No matching replenishment rows.</div></div>
  </section>
  <footer class="footer"><span><strong>Model:</strong> weighted moving average · normal-approximation safety stock · EOQ</span><span>Decision support only. Validate supplier terms and forecasts before ordering.</span></footer>
</main>
<script>
const DATA = __PAYLOAD__;
const escapeHtml = value => String(value).replace(/[&<>\"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[character]));
const money = value => new Intl.NumberFormat(undefined,{minimumFractionDigits:2,maximumFractionDigits:2}).format(Number(value));
const number = value => new Intl.NumberFormat().format(Number(value));
const s = DATA.summary, rows = DATA.rows;
document.getElementById('period').textContent = `${s.period_start} — ${s.period_end} · ${s.observed_days} days`;
const kpis = [
  ['Sales revenue', money(s.revenue), `${number(s.units_sold)} units sold`],
  ['Gross profit', money(s.gross_profit), `${s.gross_margin_pct}% gross margin`],
  ['SKUs to reorder', number(s.skus_to_reorder), `${number(s.recommended_order_units)} units suggested`],
  ['Est. order value', money(s.estimated_replenishment_value), 'At observed average unit cost']
];
document.getElementById('kpis').innerHTML = kpis.map(([label,value,note])=>`<article class="card kpi"><div class="kpi-label">${label}</div><div class="kpi-value">${value}</div><div class="kpi-note">${note}</div></article>`).join('');
const abc = ['A','B','C'].map(cls=>({cls,count:rows.filter(r=>r.abc_class===cls).length}));
const maxCount = Math.max(1,...abc.map(x=>x.count));
document.getElementById('abc-bars').innerHTML = abc.map(x=>`<div class="bar-row"><strong>${x.cls}</strong><div class="bar-track"><div class="bar-fill" style="width:${x.count/maxCount*100}%"></div></div><span class="bar-count">${x.count} SKUs</span></div>`).join('');
const xyz = ['X','Y','Z','N'].map(cls=>`${cls}: ${rows.filter(r=>r.xyz_class===cls).length}`);
document.getElementById('xyz-chips').innerHTML = xyz.map(x=>`<span class="chip">${x}</span>`).join('');
const totalHold = rows.filter(r=>r.decision==='HOLD').length;
document.getElementById('decision-insight').innerHTML = `<strong>${s.skus_to_reorder} of ${s.sku_count} SKUs</strong> currently meet the reorder trigger. ${totalHold} SKUs are above the calculated threshold or have no observed demand. The suggested quantity includes the EOQ target, minimum order quantity and pack-size rounding.`;
document.getElementById('decision-chips').innerHTML = `<span class="chip">${totalHold} hold decisions</span><span class="chip">${s.transaction_lines} transaction lines</span><span class="chip">${s.forecast_method}</span>`;
const tbody = document.getElementById('reorder-rows');
const filtered = () => {
  const q = document.getElementById('search').value.trim().toLowerCase();
  const selected = rows.filter(r=>r.decision==='REORDER' && `${r.sku} ${r.product_name}`.toLowerCase().includes(q));
  tbody.innerHTML = selected.map(r=>`<tr><td><span class="sku">${escapeHtml(r.sku)}</span><br><span class="product">${escapeHtml(r.product_name)}</span></td><td>${r.abc_class} / ${r.xyz_class}</td><td>${number(r.inventory_position)}</td><td>${number(r.reorder_point)}</td><td><strong>${number(r.recommended_order_qty)}</strong></td><td>${money(r.estimated_order_value)}</td><td><span class="pill reorder">REORDER</span></td></tr>`).join('');
  document.getElementById('empty').hidden = selected.length !== 0;
};
document.getElementById('search').addEventListener('input',filtered);
filtered();
</script>
</body>
</html>
'''.replace("__PAYLOAD__", payload)
    Path(path).write_text(html, encoding="utf-8")

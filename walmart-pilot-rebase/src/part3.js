
// ═══ charts (inline SVG, no library) ════════════════════════════════════════
const CHARTS = {};
function niceTicks(lo, hi, n) {
  if (hi === lo) { hi = lo + 1; }
  const span = hi - lo, raw = span / n, mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const step = [1, 2, 2.5, 5, 10].map(k => k * mag).find(s => span / s <= n) || 10 * mag;
  const t0 = Math.floor(lo / step) * step, out = [];
  for (let v = t0; v <= hi + step * 0.5; v += step) out.push(+v.toFixed(10));
  return out;
}
const CVAR = c => c.startsWith('--') ? `var(${c})` : c;

// Shared-x line chart. series: [{name, color, ys, dash, area, width}], xs: shared x values.
function lineChart(o) {
  const W = o.w || 920, H = o.h || 300, pad = {l: 58, r: 18, t: 16, b: 30};
  const iw = W - pad.l - pad.r, ih = H - pad.t - pad.b;
  const xs = o.xs, n = xs.length;
  let lo = Infinity, hi = -Infinity;
  o.series.forEach(s => s.ys.forEach(v => { if (v != null && isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); } }));
  if (!isFinite(lo)) { lo = 0; hi = 1; }
  if (o.yZero !== false) lo = Math.min(lo, 0);
  if (o.yMax != null) hi = Math.max(hi, o.yMax);
  const ticks = niceTicks(lo, hi, o.yTicks || 5); lo = ticks[0]; hi = ticks[ticks.length - 1];
  const x0 = xs[0], x1 = xs[n - 1];
  const X = x => pad.l + (n > 1 ? (x - x0) / (x1 - x0) : 0.5) * iw, Y = v => pad.t + (1 - (v - lo) / (hi - lo)) * ih;
  let g = '';
  (o.bands || []).forEach(b => { const a = X(Math.max(b.x0, x0)), c = X(Math.min(b.x1, x1)); if (c > a) g += `<rect class="band" x="${a}" y="${pad.t}" width="${c - a}" height="${ih}"/>` + (b.label ? `<text class="band-lbl" x="${a + 6}" y="${pad.t + 12}">${esc(b.label)}</text>` : ''); });
  g += '<g class="grid">' + ticks.map(t => `<line x1="${pad.l}" x2="${W - pad.r}" y1="${Y(t)}" y2="${Y(t)}"/>`).join('') + '</g>';
  g += ticks.map(t => `<text x="${pad.l - 8}" y="${Y(t) + 4}" text-anchor="end">${esc(o.yFmt(t))}</text>`).join('');
  if (lo < 0 && hi > 0) g += `<line class="zero" x1="${pad.l}" x2="${W - pad.r}" y1="${Y(0)}" y2="${Y(0)}"/>`;
  const xt = o.xTicks || xs.filter((_, i) => i % Math.ceil(n / 8) === 0);
  g += xt.map(x => `<text x="${X(x)}" y="${H - 8}" text-anchor="middle">${esc(o.xLabel(x))}</text>`).join('');
  (o.vlines || []).forEach(v => { if (v.x >= x0 && v.x <= x1) g += `<line x1="${X(v.x)}" x2="${X(v.x)}" y1="${pad.t}" y2="${pad.t + ih}" stroke="${CVAR(v.color || '--muted')}" stroke-width="1" stroke-dasharray="3 3"/>` + (v.label ? `<text class="lbl" x="${X(v.x) + 5}" y="${pad.t + 12}">${esc(v.label)}</text>` : ''); });
  o.series.forEach(s => {
    let d = '', started = false, pts = [];
    s.ys.forEach((v, i) => { if (v == null || !isFinite(v)) { started = false; return; } const p = `${X(xs[i]).toFixed(1)} ${Y(v).toFixed(1)}`; d += (started ? 'L' : 'M') + p; started = true; pts.push([X(xs[i]), Y(v), i]); });
    if (s.area && pts.length > 1) g += `<path class="area" fill="${CVAR(s.color)}" d="${d}L${pts[pts.length - 1][0].toFixed(1)} ${Y(Math.max(lo, 0)).toFixed(1)}L${pts[0][0].toFixed(1)} ${Y(Math.max(lo, 0)).toFixed(1)}Z"/>`;
    g += `<path class="line" stroke="${CVAR(s.color)}" ${s.dash ? 'stroke-dasharray="6 4"' : ''} ${s.width ? `stroke-width="${s.width}"` : ''} d="${d}"/>`;
    if (s.endDot && pts.length) { const [px, py] = pts[pts.length - 1]; g += `<circle class="marker" cx="${px}" cy="${py}" r="4.5" fill="${CVAR(s.color)}"/>`; }
    if (s.dots) pts.forEach(([px, py]) => g += `<circle class="marker" cx="${px}" cy="${py}" r="3.5" fill="${CVAR(s.color)}"/>`);
  });
  (o.markers || []).forEach(m => { g += `<circle class="marker" cx="${X(m.x)}" cy="${Y(m.y)}" r="5" fill="${CVAR(m.color)}"/>` + (m.label ? `<text class="lbl" x="${X(m.x)}" y="${Y(m.y) - 10}" text-anchor="middle">${esc(m.label)}</text>` : ''); });
  g += `<line class="cross" id="${o.id}-x" x1="0" x2="0" y1="${pad.t}" y2="${pad.t + ih}"/>`;
  g += (o.series).map((s, si) => `<circle class="marker" id="${o.id}-d${si}" r="4.5" fill="${CVAR(s.color)}" opacity="0"/>`).join('');
  g += `<rect class="hit" x="${pad.l}" y="${pad.t}" width="${iw}" height="${ih}"/>`;
  CHARTS[o.id] = {type: 'line', xs, X, Y, series: o.series, xLabel: o.xLabel, tipX: o.tipX || o.xLabel, yFmt: o.tipFmt || o.yFmt, W, H, pad};
  const legend = o.legend === false ? '' : `<div class="legend">${o.series.map(s => `<span><i class="${s.dash ? 'dash' : ''}" style="border-color:${CVAR(s.color)}"></i>${esc(s.name)}</span>`).join('')}${(o.legendExtra || '')}</div>`;
  return `<div class="chart" data-chart="${o.id}"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(o.aria || '')}">${g}</svg><div class="tip" id="${o.id}-tip"></div></div>${legend}`;
}
// Grouped column chart. cats: labels; series: [{name, color, vals}]
function barChart(o) {
  const W = o.w || 920, H = o.h || 280, pad = {l: 58, r: 18, t: 16, b: 30};
  const iw = W - pad.l - pad.r, ih = H - pad.t - pad.b, nC = o.cats.length, nS = o.series.length;
  let lo = 0, hi = 0; o.series.forEach(s => s.vals.forEach(v => { if (v != null && isFinite(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); } }));
  const ticks = niceTicks(lo, hi, 5); lo = ticks[0]; hi = ticks[ticks.length - 1];
  const Y = v => pad.t + (1 - (v - lo) / (hi - lo)) * ih, slot = iw / nC, bw = Math.min(24, (slot * 0.7 - 2 * (nS - 1)) / nS);
  let g = '<g class="grid">' + ticks.map(t => `<line x1="${pad.l}" x2="${W - pad.r}" y1="${Y(t)}" y2="${Y(t)}"/>`).join('') + '</g>';
  g += ticks.map(t => `<text x="${pad.l - 8}" y="${Y(t) + 4}" text-anchor="end">${esc(o.yFmt(t))}</text>`).join('');
  g += `<line class="zero" x1="${pad.l}" x2="${W - pad.r}" y1="${Y(0)}" y2="${Y(0)}"/>`;
  const every = Math.ceil(nC / 12);
  o.cats.forEach((c, i) => { if (i % every === 0) g += `<text x="${pad.l + slot * (i + 0.5)}" y="${H - 8}" text-anchor="middle">${esc(c)}</text>`; });
  const groupW = nS * bw + (nS - 1) * 2;
  o.series.forEach((s, si) => s.vals.forEach((v, i) => {
    if (v == null || !isFinite(v)) return;
    const x = pad.l + slot * (i + 0.5) - groupW / 2 + si * (bw + 2), y0 = Y(0), y1 = Y(v), top = Math.min(y0, y1), h = Math.abs(y0 - y1), r = Math.min(4, bw / 2, h);
    const d = v >= 0
      ? `M${x} ${y0}V${top + r}Q${x} ${top} ${x + r} ${top}H${x + bw - r}Q${x + bw} ${top} ${x + bw} ${top + r}V${y0}Z`
      : `M${x} ${y0}V${y0 + h - r}Q${x} ${y0 + h} ${x + r} ${y0 + h}H${x + bw - r}Q${x + bw} ${y0 + h} ${x + bw} ${y0 + h - r}V${y0}Z`;
    g += `<path fill="${CVAR(s.color)}" d="${d}" data-i="${i}" data-s="${si}"/>`;
  }));
  g += `<rect class="hit" x="${pad.l}" y="${pad.t}" width="${iw}" height="${ih}"/>`;
  CHARTS[o.id] = {type: 'bar', cats: o.cats, series: o.series, slot, pad, W, H, yFmt: o.tipFmt || o.yFmt, X: i => pad.l + slot * (i + 0.5), Y};
  const legend = (o.legend === false || nS < 2) ? '' : `<div class="legend">${o.series.map(s => `<span><i class="sq" style="background:${CVAR(s.color)}"></i>${esc(s.name)}</span>`).join('')}</div>`;
  return `<div class="chart" data-chart="${o.id}"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(o.aria || '')}">${g}</svg><div class="tip" id="${o.id}-tip"></div></div>${legend}`;
}
function wireCharts(root) {
  root.querySelectorAll('.chart').forEach(el => {
    const id = el.dataset.chart, C = CHARTS[id]; if (!C) return;
    const svg = el.querySelector('svg'), tip = el.querySelector('.tip');
    const move = ev => {
      const r = svg.getBoundingClientRect(), mx = (ev.clientX - r.left) / r.width * C.W;
      let i;
      if (C.type === 'line') { let best = Infinity; C.xs.forEach((x, k) => { const d = Math.abs(C.X(x) - mx); if (d < best) { best = d; i = k; } }); }
      else i = clamp(Math.floor((mx - C.pad.l) / C.slot), 0, C.cats.length - 1);
      if (i == null) return;
      const px = C.X(C.type === 'line' ? C.xs[i] : i);
      let rows = '';
      C.series.forEach((s, si) => {
        const v = C.type === 'line' ? s.ys[i] : s.vals[i];
        if (C.type === 'line') { const dot = svg.querySelector('#' + id + '-d' + si); if (dot) { if (v == null || !isFinite(v)) dot.setAttribute('opacity', 0); else { dot.setAttribute('cx', px); dot.setAttribute('cy', C.Y(v)); dot.setAttribute('opacity', 1); } } }
        rows += `<div class="tr"><span><i style="background:${CVAR(s.color)}"></i>${esc(s.name)}</span><b>${v == null || !isFinite(v) ? '—' : esc(C.yFmt(v))}</b></div>`;
      });
      if (C.type === 'line') { const cx = svg.querySelector('#' + id + '-x'); cx.setAttribute('x1', px); cx.setAttribute('x2', px); cx.setAttribute('opacity', 1); }
      tip.innerHTML = `<div class="th">${esc(C.type === 'line' ? C.tipX(C.xs[i]) : C.cats[i])}</div>${rows}`;
      const left = px / C.W * r.width; tip.style.left = clamp(left, 90, r.width - 90) + 'px'; tip.style.top = (C.pad.t / C.H * r.height - 8) + 'px'; tip.style.opacity = 1;
    };
    const leave = () => { tip.style.opacity = 0; if (C.type === 'line') { svg.querySelector('#' + id + '-x').setAttribute('opacity', 0); C.series.forEach((_, si) => { const d = svg.querySelector('#' + id + '-d' + si); if (d) d.setAttribute('opacity', 0); }); } };
    svg.addEventListener('mousemove', move); svg.addEventListener('mouseleave', leave);
    svg.addEventListener('touchstart', e => move(e.touches[0]), {passive: true}); svg.addEventListener('touchmove', e => move(e.touches[0]), {passive: true});
  });
}

// ═══ view helpers ═══════════════════════════════════════════════════════════
const BASIS = {walmart: {label: 'Walmart reporting', short: 'Walmart', unit: 'visits', color: '--wm', ramp: ['--wm-lo', '--wm-mid', '--wm-hi'], cls: 'wm'},
               botify: {label: 'Botify GSC + BWT', short: 'Botify', unit: 'clicks', color: '--bt', ramp: ['--bt-lo', '--bt-mid', '--bt-hi'], cls: 'bt'}};
const fig = (title, sub, body, tools) => `<section class="fig"><div class="fig-head"><div><h2>${title}</h2>${sub ? `<p class="sub">${sub}</p>` : ''}</div>${tools ? `<div class="fig-tools">${tools}</div>` : ''}</div>${body}</section>`;
const seg = (key, opts, cur, cls) => `<div class="seg ${cls || ''}" role="group">${opts.map(([v, l]) => `<button type="button" data-set="${key}" data-v="${v}" aria-pressed="${String(cur) === String(v)}">${l}</button>`).join('')}</div>`;
const chip = (cls, t) => `<span class="chip ${cls}">${t}</span>`;
const dlt = x => `<span class="delta ${deltaCls(x)}">${spct(x)}</span>`;
const tierColor = (b, t) => BASIS[b].ramp[TIERS.indexOf(t)];
function weekPoints(daily, key, L) {   // daily rows → weekly sums (Sun–Sat), x = week end day
  const out = []; let cur = null;
  daily.forEach(p => { const dow = new Date(p.n * DAY).getUTCDay(); if (!cur || dow === 0) { cur = {n: p.n, v: 0, days: 0}; out.push(cur); } cur.v += p[key]; cur.n = p.n; cur.days++; });
  return out;
}
function monthRows(daily) {
  const out = [], idx = {};
  daily.forEach(p => { const y = yearOf(p.n), m = monthOf(p.n), k = y + '-' + m; if (!idx[k]) { idx[k] = {y, m, days: 0, ly: 0, base: 0, inc: 0, incRev: 0, ai: 0, aiRev: 0, baseGmv: 0, lyGmv: 0, held: 0}; out.push(idx[k]); }
    const r = idx[k]; r.days++; for (const key of ['ly', 'base', 'inc', 'incRev', 'ai', 'aiRev', 'baseGmv', 'lyGmv', 'held']) r[key] += p[key] || 0; });
  return out;
}

// ═══ Forecast tab ═══════════════════════════════════════════════════════════
function headlineTiles(D) {
  const single = b => TIERS.map(t => { const r = D[b === 'walmart' ? 'wm' : 'bt'][t], B = BASIS[b], aiOn = b === 'walmart' ? S.aeoInclude : S.includeAi;
    return `<div class="tile basis-${b}"><div class="tl"><span>${TIER_LABEL[t]} · incremental revenue</span>${chip(B.cls, B.short)}</div>
      <div class="tv num">${fmtUSD(r.totalRev)}</div>
      <div class="td num"><b>${fmtC(r.incVisits)}</b> incremental ${B.unit} · ${fmtUSD(r.searchRev)} search${aiOn ? ` + ${fmtUSD(r.aiRev)} AI` : ''}<br>
      Baseline ${dlt(r.baseYoy)} YoY → with Botify ${dlt(r.withUsYoy)} · exits at ${pct1(r.exit)} adoption</div></div>`; }).join('');
  if (S.basis !== 'compare') return `<div class="tiles">${single(S.basis)}</div>`;
  return `<div class="tiles">${TIERS.map(t => { const w = D.wm[t], f = D.bt[t], x = f.totalRev ? w.totalRev / f.totalRev : 0;
    return `<div class="tile basis-compare"><div class="tl"><span>${TIER_LABEL[t]} · incremental revenue</span><span class="num">${x.toFixed(1)}× Frank</span></div>
      <div class="pair"><div><div class="k"><span class="dot wm"></span>Walmart ledger</div><div class="v num">${fmtUSD(w.totalRev)}</div><div class="s num">${fmtC(w.incVisits)} visits · RPV ${fmtUSD2(w.rpv)}</div></div>
      <div><div class="k"><span class="dot bt"></span>Botify archive</div><div class="v num">${fmtUSD(f.totalRev)}</div><div class="s num">${fmtC(f.incVisits)} clicks · RPV ${fmtUSD2(f.rpv)}</div></div></div>
      <div class="td num">With Botify, YoY: Walmart ${dlt(w.withUsYoy)} · Botify ${dlt(f.withUsYoy)}</div></div>`; }).join('')}</div>`;
}
function ledgerTable(D) {
  const w = D.wm.mid, f = D.bt.mid, tOpt = S.wmTrend === 'custom' ? {label: 'Custom', v: S.wmTrendCustom / 100} : D.trendOpts[S.wmTrend];
  const rows = [
    ['What is counted', `SEO channel <b>PDP++ visits</b> (Walmart DMP export)`, `Google + Bing <b>clicks</b> (GSC US/web + BWT property totals)`],
    ['Baseline for the window', `${fmtC(w.baseVisits)} visits · last year’s aligned days × (1 ${D.trend >= 0 ? '+' : '−'} ${pct1(Math.abs(D.trend))})`, `${fmtC(f.baseVisits)} clicks · monthly actuals × (1 − 10.8% Google, − 4.2% Bing)`],
    ['Trend source', `${esc(tOpt.label)}: ${spct(tOpt.v)} · Walmart’s own export`, `GSC year-over-year on 299 days: ${spct(D.trends.google)} · accelerating to −17% recently`],
    ['Lift translation', S.liftMethod === 'ratio' ? `Frank’s clicks × ${D.vpc.ratio.toFixed(2)} visits per click (measured overlap)` : `Frank’s lift rate (${pct2(w.liftRate)} full-coverage, mid) × Walmart baseline × ramp`, `Frank’s levers verbatim: growth, indexation dial, Bing target`],
    ['Dollars per unit', `${fmtUSD2(w.rpv)} per visit · ${esc(D.rpvOpt.label)}`, `${fmtUSD2(f.rpv)} per click · AOV $${S.aov} × CR ${S.cr}% (contract frozen RPV)`],
    ['AI channel base', `${fmtC(D.aeoB.weeklyVisits)} AEO visits/week (28 days to ${fmtDateS(D.aeoB.to)}) · ${fmtUSD2(D.aeoRpv)} per visit`, `${fmtC(D.aiF.weeklyVisits)} OpenAI visits/week (2 scorecard weeks, May) × 1.11 ecosystem · ${fmtUSD2(D.aiF.rpv)} per visit`],
    ['Data currency', `Through ${fmtDate(LAST_WM)} · daily`, `GSC through ${fmtDate(LAST_GSC)} · Bing through ${fmtDate(LAST_BING)}`],
  ];
  return `<div class="tscroll"><table class="t"><thead><tr><th class="l">Ledger</th><th class="l"><span class="dot wm"></span>Walmart reporting</th><th class="l"><span class="dot bt"></span>Botify GSC + BWT (Frank)</th></tr></thead>
    <tbody>${rows.map(r => `<tr><td>${r[0]}</td><td class="l num">${r[1]}</td><td class="l num">${r[2]}</td></tr>`).join('')}</tbody></table></div>`;
}
function projectionFig(D) {
  const xs = D.wm.low.daily.map(p => p.n), xLabel = n => fmtDateS(isoOf(n));
  const ticks = xs.filter(n => { const d = new Date(n * DAY).getUTCDate(); return d === 1 || d === 15; });
  const mk = (b, t, dash) => ({name: `${BASIS[b].short} · ${TIER_LABEL[t]}`, color: S.basis === 'compare' ? BASIS[b].color : tierColor(b, t), ys: D[b === 'walmart' ? 'wm' : 'bt'][t].daily.map(p => p.cumTotal), dash, endDot: true, area: t === 'mid' && S.basis !== 'compare'});
  const series = S.basis === 'compare' ? [mk('walmart', S.tier), mk('botify', S.tier)] : TIERS.map(t => mk(S.basis, t));
  const vl = [{x: D.L + 30, label: 'Month 2'}, {x: D.L + 60, label: 'Month 3'}, {x: D.L + 90, label: 'Month 4'}].filter(v => v.x < D.H);
  return fig('Cumulative incremental revenue', `From launch ${fmtDate(S.launch)} to ${fmtDate(S.horizon)} (${D.span} days). Search and AI summed where the AI channel is included. Same ramp on both bases: three tranches, adoption steps at 30-day marks, so the corners are real.`,
    lineChart({id: 'proj', xs, xLabel, xTicks: ticks, tipX: n => fmtDate(isoOf(n)), yFmt: fmtUSD, series, vlines: vl, aria: 'Cumulative incremental revenue by tier'}),
    S.basis === 'compare' ? seg('tier', TIERS.map(t => [t, TIER_LABEL[t]]), S.tier) : '');
}
function pathFig(D) {
  const build = b => {
    const r = D[b === 'walmart' ? 'wm' : 'bt'][S.tier], B = BASIS[b];
    const ly = weekPoints(r.daily, 'ly', D.L), base = weekPoints(r.daily, 'base', D.L), inc = weekPoints(r.daily, 'inc', D.L), held = weekPoints(r.daily, 'held', D.L);
    const full = w => w.days === 7; const xs = base.map(w => w.n);
    const series = [];
    if (b === 'walmart') series.push({name: 'Last year, same weeks', color: '--ly', ys: ly.map((w, i) => full(w) ? w.v : null), dash: true});
    else series.push({name: 'Measured run-rate (held flat)', color: '--ly', ys: held.map((w, i) => full(w) ? w.v : null), dash: true});
    series.push({name: 'Baseline without Botify', color: b === 'walmart' ? '--wm-lo' : '--bt-lo', ys: base.map(w => full(w) ? w.v : null)});
    series.push({name: `With Botify · ${TIER_LABEL[S.tier]}`, color: B.color, ys: base.map((w, i) => full(w) ? w.v + inc[i].v : null), width: 2.5, endDot: true});
    const ticks = xs.filter((_, i) => i % 2 === 0);
    const half = S.basis === 'compare';
    return `<div><h3 style="font-size:15px;margin-bottom:8px"><span class="dot ${B.cls}"></span>${B.label} · weekly ${B.unit}</h3>${lineChart({id: 'path-' + b, xs, w: half ? 560 : 920, h: half ? 260 : 300, xLabel: n => fmtDateS(isoOf(n)), xTicks: ticks, tipX: n => 'Week ending ' + fmtDate(isoOf(n)), yFmt: fmtC, series, aria: 'Weekly baseline and with-Botify path'})}</div>`;
  };
  const body = S.basis === 'compare' ? `<div class="grid2">${build('walmart')}${build('botify')}</div>` : build(S.basis);
  return fig('The path through the window', `Weekly totals, Sunday to Saturday. The gap between the dashed line and the baseline is the trend assumption; the gap between the baseline and the top line is Botify. On Walmart’s ledger last year’s December was the biggest month in the export, so the baseline climbs into the holidays whatever the trend.`, body,
    seg('tier', TIERS.map(t => [t, TIER_LABEL[t]]), S.tier));
}
function monthlyTableFig(D) {
  const b = S.basis === 'compare' ? 'walmart' : S.basis, key = b === 'walmart' ? 'wm' : 'bt', B = BASIS[b];
  const rows = monthRows(D[key][S.tier].daily), lowR = monthRows(D[key].low.daily), highR = monthRows(D[key].high.daily);
  const tot = k => sum(rows.map(r => r[k]));
  const lyCol = b === 'walmart' ? 'Last year' : 'Run-rate';
  const html = rows.map((r, i) => {
    const lyv = b === 'walmart' ? r.ly : r.held, wu = r.base + r.inc;
    return `<tr><td>${MON[r.m - 1]} ${r.y}${r.days < dim(r.y, r.m) ? ` <span class="chip">${r.days}d</span>` : ''}</td><td class="num">${fmtC(lyv)}</td><td class="num">${fmtC(r.base)}</td>
      <td class="num">${fmtC(lowR[i].inc)}</td><td class="num ${B.cls}">${fmtC(r.inc)}</td><td class="num">${fmtC(highR[i].inc)}</td><td class="num">${fmtC(wu)}</td><td class="num">${dlt(lyv ? wu / lyv - 1 : null)}</td><td class="num">${fmtUSD(r.incRev)}</td></tr>`; }).join('');
  const T = D[key][S.tier], lyT = b === 'walmart' ? T.lyVisits : T.heldVisits;
  return fig(`Month by month · ${B.label}`, `Incremental ${B.unit} at each tier; the with-Botify and revenue columns follow the selected tier (${TIER_LABEL[S.tier]}). Revenue is search only here; AI is on its own card below.`,
    `<div class="tscroll"><table class="t"><thead><tr><th class="l">Month</th><th>${lyCol}</th><th>Baseline</th><th>Low</th><th>${TIER_LABEL[S.tier]}</th><th>High</th><th>With Botify</th><th>YoY</th><th>Search $</th></tr></thead>
    <tbody>${html}<tr class="total"><td>Window</td><td class="num">${fmtC(lyT)}</td><td class="num">${fmtC(T.baseVisits)}</td><td class="num">${fmtC(D[key].low.incVisits)}</td><td class="num ${B.cls}">${fmtC(T.incVisits)}</td><td class="num">${fmtC(D[key].high.incVisits)}</td><td class="num">${fmtC(T.withUs)}</td><td class="num">${dlt(T.withUsYoy)}</td><td class="num">${fmtUSD(T.searchRev)}</td></tr></tbody></table></div>`,
    S.basis === 'compare' ? chip('wm', 'Walmart ledger shown') : '');
}
function aeoFig(D) {
  const a = D.aeoB, wk = weeklySat({v: WM.aeo.visits, g: WM.aeo.gmv}, P.aeo.start, LAST_WM).filter(w => w.days === 7);
  const xs = wk.map(w => dayNum(w.end));
  const sc = FD.trajectory.ai.weeks.map(w => ({x: dayNum(w.ends), y: w.three_day.visits, color: '--bt', label: w.week.replace('FY27-', '') + ' scorecard'}));
  const chart = lineChart({id: 'aeo-wk', xs, xLabel: n => fmtDateS(isoOf(n)), xTicks: xs.filter((_, i) => i % 3 === 0), tipX: n => 'Week ending ' + fmtDate(isoOf(n)), yFmt: fmtC, w: 560, h: 260,
    series: [{name: 'Walmart AEO visits / week', color: '--wm', ys: wk.map(w => w.v), area: true, endDot: true}], markers: sc, vlines: [{x: D.L, label: 'Launch', color: '--muted'}],
    legendExtra: `<span><i class="sq" style="background:var(--bt)"></i>Frank’s two scorecard weeks (3-day attribution)</span>`, aria: 'Weekly AEO visits'});
  const tiles = TIERS.map(t => { const w = D.wm[t], f = D.bt[t]; return `<div><div class="k">${TIER_LABEL[t]} · incremental AI</div><div class="v num">${fmtUSD(w.aiRev)}</div><div class="s num">${fmtC(w.aiVisits)} visits · Frank: ${fmtUSD(f.aiRev)}</div></div>`; }).join('');
  return fig('AI channel (Walmart “AEO”)', `Walmart began reporting an AEO marketing vehicle on 1 May 2026. Its weekly visits match Frank’s two scorecard weeks to within 2%, which pins the export to the same 3-day attribution basis, so the 19 weeks here simply extend what he had. The channel has grown ${pct1(wk[wk.length - 1].v / wk[0].v - 1)} since its first full week; the step up in mid-August is unexplained in the export.`,
    `<div class="grid2"><div>${chart}</div>
     <div><div class="tile" style="box-shadow:none"><div class="tl">Baseline used · 28 days to ${fmtDateS(a.to)}</div><div class="tv num">${fmtC(a.weeklyVisits)}<small>visits / week</small></div>
       <div class="td num">GMV per visit ${fmtUSD2(a.rpv91)} · conversion ${pct1(a.cr91)} · AOV ${fmtUSD2(a.aov91)} (91 days). Frank’s scorecard basis: 1.45M/week, ${fmtUSD2(D.aiF.rpv)} per visit, AOV $101, CR 8.3%.</div>
       <div class="pair" style="grid-template-columns:repeat(3,1fr)">${tiles}</div>
       <div class="td">Lift ${TIERS.map(t => pct1(FD.trajectory.ai.lift[t])).join(' / ')} of the AI base at full adoption (Frank’s tiers), ${S.aeoRisk ? '× 0.8 risk haircut' : 'no risk haircut'}, ecosystem × ${S.aeoEco.toFixed(2)}, ${S.aeoTrend === 'linear' ? 'base growing at the trailing 8-week slope' : 'base held flat'}. No seasonality: none exists to measure.</div></div></div></div>`);
}
function actualsFig(D) {
  const A = D.actuals; if (!A) return '';
  return fig(`First ${A.days} days since launch · Walmart export`, `The only post-launch read available: the Botify archive stops ${fmtDate(LAST_GSC)}. At day ${A.days} the low ramp has 2% adoption on one tranche, so the model expects nothing visible yet; this is a sanity check on the baseline, not a verdict on the pilot. Whether SpeedWorkers was actually serving in this window is not something the export can tell.`,
    `<div class="tiles" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">
      <div class="tile" style="box-shadow:none"><div class="tl">SEO visits</div><div class="tv num">${fmtC(A.visits)}</div><div class="td num">${dlt(A.yoy)} vs same days last year · ${dlt(A.vsBase)} vs baseline</div></div>
      <div class="tile" style="box-shadow:none"><div class="tl">SEO GMV</div><div class="tv num">${fmtUSD(A.gmv)}</div><div class="td num">${dlt(A.gmvYoy)} YoY · ${fmtUSD2(A.gmv / A.visits)} per visit</div></div>
      <div class="tile" style="box-shadow:none"><div class="tl">Expected incremental so far</div><div class="tv num">${fmtC(A.expected.low)}<small>– ${fmtC(A.expected.high)}</small></div><div class="td num">visits, low to high · ${pct2(A.expected.high / A.visits)} of actual at most</div></div>
      <div class="tile" style="box-shadow:none"><div class="tl">AEO visits</div><div class="tv num">${fmtC(A.aeoV)}</div><div class="td num">${dlt(A.aeoBase ? A.aeoV / A.aeoBase - 1 : null)} vs the 28-day baseline run-rate · ${fmtUSD(A.aeoG)} GMV</div></div>
    </div>`);
}
function field(label, help, control, q) { return `<div class="field"><div class="fl"><span>${label}${q ? `<span class="qtag">Q${q}</span>` : ''}</span></div>${control}${help ? `<div class="fh">${help}</div>` : ''}</div>`; }
const sel = (key, opts, cur) => `<select data-key="${key}">${opts.map(([v, l]) => `<option value="${v}" ${String(cur) === String(v) ? 'selected' : ''}>${l}</option>`).join('')}</select>`;
const range = (key, min, max, step, cur, unit) => `<div class="row"><input type="range" data-key="${key}" min="${min}" max="${max}" step="${step}" value="${cur}"><span class="val num" style="min-width:56px;text-align:right">${cur}${unit || ''}</span></div>`;
const chk = (key, cur, label) => `<label class="chk"><input type="checkbox" data-key="${key}" ${cur ? 'checked' : ''}>${label}</label>`;
function inputsPanel(D) {
  const tOpts = Object.entries(D.trendOpts).map(([k, o]) => [k, `${o.label} (${spct(o.v)})`]).concat([['custom', 'Custom']]);
  const rOpts = Object.entries(D.rpvOpts).map(([k, o]) => [k, o.label]);
  return `<details class="inputs" ${S.inputsOpen ? 'open' : ''} id="inputs"><summary><span>Model inputs <span class="hint">· every assumption on this page is a control here; Q-tags point at the open questions</span></span></summary>
  <div class="inputs-body">
    <div class="wmh"><h4>Walmart ledger</h4>
      ${field('Baseline trend on last year’s window', D.trendOpts[S.wmTrend] ? D.trendOpts[S.wmTrend].note : 'Your figure.', sel('wmTrend', tOpts, S.wmTrend) + (S.wmTrend === 'custom' ? range('wmTrendCustom', -30, 30, 0.1, S.wmTrendCustom, '%') : ''), 2)}
      ${field('GMV per visit', D.rpvOpt.note, sel('rpvMethod', rOpts, S.rpvMethod), 3)}
      ${field('How Botify’s lift becomes Walmart visits', S.liftMethod === 'ratio' ? `Frank’s incremental clicks × ${D.vpc.ratio.toFixed(2)} visits per click, measured ${fmtDateS(D.vpc.from)}–${fmtDate(D.vpc.to)} where both archives overlap.` : 'Frank’s annual incremental clicks as a share of his own Google+Bing base, applied to Walmart’s baseline day by day. Keeps Walmart’s seasonality; drops Frank’s.', sel('liftMethod', [['proportional', 'Proportional lift rate'], ['ratio', 'Visits-per-click ratio']], S.liftMethod), 4)}
      ${field('AI channel', 'Walmart’s AEO export replaces the two scorecard weeks.', chk('aeoInclude', S.aeoInclude, 'Include AEO in the headline') + sel('aeoTrend', [['flat', 'Base held flat at trailing 28 days'], ['linear', `Base grows ${fmtC(D.aeoB.weeklySlope)} visits/week/week (trailing 8-week slope)`]], S.aeoTrend) + sel('aeoRpv', [['wm91', `Walmart AEO GMV per visit, 91 days (${fmtUSD2(D.aeoB.rpv91)})`], ['wm28', `Walmart AEO GMV per visit, 28 days (${fmtUSD2(D.aeoB.rpv28)})`], ['frank', `Frank’s scorecard RPV (${fmtUSD2(D.aiF.rpv)})`]], S.aeoRpv), 5)}
      ${field('AI risk and scope', 'Frank haircuts AI by 0.8 and scales OpenAI to the whole ecosystem by 1.11. If AEO already counts every AI referrer, the multiplier should stay at 1.', chk('aeoRisk', S.aeoRisk, 'Apply the 0.8 risk haircut') + range('aeoEco', 1, 1.5, 0.01, S.aeoEco, '×'), 6)}
    </div>
    <div class="bth"><h4>Botify archive (Frank’s levers, shared by both bases)</h4>
      ${field('Anonymized-query inclusion', 'Share of Google’s withheld-query impressions counted in the base. Frank’s dominant lever; 0% is the floor that survives any challenge.', range('anon', 0, 100, 5, S.anon, '%'))}
      ${field('Traffic growth, low → high', 'Non-branded impression growth at full coverage.', range('growthLo', 0, 30, 0.5, S.growthLo, '%') + range('growthHi', 0, 40, 0.5, S.growthHi, '%'))}
      ${field('Indexation dial, low → high', 'Share of the 434M crawled-not-indexed pages that get indexed. Frank’s least defensible number at 60%.', range('dialLo', 0, 80, 2.5, S.dialLo, '%') + range('dialHi', 0, 80, 2.5, S.dialHi, '%'))}
      ${field('New-page performance', 'Newly indexed pages perform at this share of an average page.', range('newPagePerf', 5, 100, 5, S.newPagePerf, '%'))}
      ${field('Contract RPV: AOV × conversion', `${fmtUSD2(S.aov * S.cr / 100)} per click. Walmart’s export over the 12 months to July 2026 gives AOV $74.69 and CR 4.30%, so the frozen figure is right for last year and low for today.`, range('aov', 50, 110, 0.1, S.aov, ' $') + range('cr', 2, 9, 0.1, S.cr, '%'), 3)}
      ${field('Engines and AI', '', chk('bing', S.bing, 'Include Bing traffic lever') + chk('includeAi', S.includeAi, 'Include AI in Frank’s headline') + sel('aiBasis', [['three_day_mean', '3-day attribution, mean of W16–W17'], ['three_day_w16', '3-day, W16 only'], ['three_day_latest', '3-day, W17 only'], ['same_session_mean', 'Same-session, mean']], S.aiBasis))}
      ${field('Frank’s baseline trends', 'Measured year-over-year on the GSC and Bing archives.', range('trendGoogle', -30, 10, 0.1, S.trendGoogle, '%') + range('trendBing', -30, 10, 0.1, S.trendBing, '%'))}
      ${field('Ramp', 'Tranches go live at equal intervals across the ramp weeks; each runs its own adoption curve.', range('rampWeeks', 0, 8, 1, S.rampWeeks, ' wk') + range('tranches', 1, 6, 1, S.tranches, ''))}
      <div class="field"><button type="button" class="tab" style="border:1px solid var(--rule);border-radius:8px;padding:8px 12px" data-set="__reset" data-v="1">Reset every input to defaults</button></div>
    </div>
  </div></details>`;
}
function viewForecast(D) {
  const cmp = S.basis === 'compare';
  return `<div class="stack">
    ${headlineTiles(D)}
    <div class="callout">${cmp
      ? `<strong>Same levers, about ${(D.wm.mid.totalRev / D.bt.mid.totalRev).toFixed(1)}× the dollars.</strong> Walmart counts ${D.vpc.ratio.toFixed(2)} SEO visits for every click in our archive and books ${fmtUSD2(D.wm.mid.rpv)} per visit against the frozen ${fmtUSD2(D.bt.mid.rpv)}. Its SEO channel is also ${spct(D.trendOpts.ttm.v)} year over year while GSC clicks are ${spct(D.trends.google)}. All three move the same direction.`
      : S.basis === 'walmart'
      ? `<strong>This is Frank’s lift on Walmart’s own numbers.</strong> Baseline is last year’s aligned window at ${spct(D.trend)}; each incremental visit is worth ${fmtUSD2(D.wm.mid.rpv)} (${esc(D.rpvOpt.label.toLowerCase())}). Switch to <em>Compare</em> to see what each of those choices does against the GSC build.`
      : `<strong>Frank’s model, unchanged.</strong> Reproduces his 13 Aug figures to the digit: ${fmtC(D.bt.low.incVisits)} / ${fmtC(D.bt.mid.incVisits)} / ${fmtC(D.bt.high.incVisits)} clicks to ${fmtDate(S.horizon)} at ${fmtUSD2(D.bt.low.rpv)} frozen RPV. Contract threshold 1.40M clicks, target 5.98M, stretch 13.65M by 20 Dec.`}</div>
    ${fig('Two ledgers, one window', 'What each basis counts, and where every number comes from. Rows in this table are the differences; everything else is shared.', ledgerTable(D))}
    ${projectionFig(D)}
    ${pathFig(D)}
    ${monthlyTableFig(D)}
    ${aeoFig(D)}
    ${actualsFig(D)}
    ${inputsPanel(D)}
  </div>`;
}

// ═══ Year-over-year tab ═════════════════════════════════════════════════════
const YMETRICS = {visits: ['SEO visits', fmtC], gmv: ['SEO net GMV', fmtUSD], orders: ['Authorized orders', fmtC], rpv: ['GMV per visit', fmtUSD2], cr: ['Conversion (orders ÷ visits)', pct2], aov: ['Average order value', fmtUSD2]};
function metricOf(r, k) { return k === 'rpv' ? (r.visits ? r.gmv / r.visits : null) : k === 'cr' ? (r.visits ? r.orders / r.visits : null) : k === 'aov' ? (r.orders ? r.gmv / r.orders : null) : r[k]; }
function viewYoy(D) {
  const mo = monthly({visits: WM.seo.visits, gmv: WM.seo.gmv, orders: WM.seo.orders}, P.seo.start, LAST_WM);
  const full = mo.filter(r => r.days === dim(r.y, r.m));
  const years = [2024, 2025, 2026], k = S.yoyMetric, [mLabel, mFmt] = YMETRICS[k];
  const byYear = years.map((y, yi) => ({name: String(y), color: ['--wm-lo', '--wm-mid', '--wm-hi'][yi], ys: Array.from({length: 12}, (_, i) => { const r = full.find(x => x.y === y && x.m === i + 1); return r ? metricOf(r, k) : null; }), width: y === 2026 ? 2.5 : 2, endDot: y === 2026}));
  const chartA = lineChart({id: 'yoy-a', xs: Array.from({length: 12}, (_, i) => i), xLabel: i => MON[i], xTicks: Array.from({length: 12}, (_, i) => i), tipX: i => MON[i], yFmt: mFmt, yZero: k !== 'rpv' && k !== 'aov' && k !== 'cr', series: byYear, aria: mLabel + ' by month and year'});
  // YoY by month, 364-day aligned, only where the aligned prior month is fully covered
  const yoyRows = full.map(r => { const a = `${r.y}-${String(r.m).padStart(2, '0')}-01`, b = `${r.y}-${String(r.m).padStart(2, '0')}-${String(r.days).padStart(2, '0')}`;
    const pa = isoOf(dayNum(a) - YOY), pb = isoOf(dayNum(b) - YOY); if (WM.seo.visits.count(pa, pb) < r.days) return null;
    const p = {visits: WM.seo.visits.sum(pa, pb), gmv: WM.seo.gmv.sum(pa, pb), orders: WM.seo.orders.sum(pa, pb)};
    const cur = metricOf(r, k), prev = metricOf(p, k); return {ym: MON[r.m - 1] + ' ' + String(r.y).slice(2), v: prev ? cur / prev - 1 : null, r, p}; }).filter(Boolean);
  const chartB = barChart({id: 'yoy-b', cats: yoyRows.map(r => r.ym), series: [{name: mLabel + ' YoY', color: '--wm', vals: yoyRows.map(r => r.v)}], yFmt: spct, h: 260, aria: mLabel + ' year over year by month'});
  // AEO weekly
  const wk = weeklySat({v: WM.aeo.visits, g: WM.aeo.gmv, o: WM.aeo.orders}, P.aeo.start, LAST_WM).filter(w => w.days === 7), xs = wk.map(w => dayNum(w.end));
  const chartC = lineChart({id: 'yoy-c', xs, xLabel: n => fmtDateS(isoOf(n)), xTicks: xs.filter((_, i) => i % 3 === 0), tipX: n => 'Week ending ' + fmtDate(isoOf(n)), yFmt: fmtC, w: 560, h: 240, series: [{name: 'AEO visits / week', color: '--wm', ys: wk.map(w => w.v), area: true, endDot: true}], aria: 'AEO weekly visits'});
  const chartD = lineChart({id: 'yoy-d', xs, xLabel: n => fmtDateS(isoOf(n)), xTicks: xs.filter((_, i) => i % 3 === 0), tipX: n => 'Week ending ' + fmtDate(isoOf(n)), yFmt: fmtUSD, w: 560, h: 240, series: [{name: 'AEO net GMV / week', color: '--wm-hi', ys: wk.map(w => w.g), area: true, endDot: true}], aria: 'AEO weekly GMV'});
  const t364 = yoyWindow(WM.seo.visits, D.preLaunch, 364), g364 = yoyWindow(WM.seo.gmv, D.preLaunch, 364), t91 = yoyWindow(WM.seo.visits, D.preLaunch, 91), g91 = yoyWindow(WM.seo.gmv, D.preLaunch, 91);
  const tbl = full.slice().reverse().map(r => { const yr = yoyRows.find(x => x.r === r); const yv = yr && yr.p.visits ? r.visits / yr.p.visits - 1 : null, yg = yr && yr.p.gmv ? r.gmv / yr.p.gmv - 1 : null;
    return `<tr><td>${MON[r.m - 1]} ${r.y}</td><td class="num">${fmtC(r.visits)}</td><td class="num">${dlt(yv)}</td><td class="num">${fmtUSD(r.gmv)}</td><td class="num">${dlt(yg)}</td><td class="num">${fmtC(r.orders)}</td><td class="num">${fmtUSD2(r.gmv / r.visits)}</td><td class="num">${pct2(r.orders / r.visits)}</td><td class="num">${fmtUSD2(r.gmv / r.orders)}</td></tr>`; }).join('');
  return `<div class="stack">
    <div class="tiles">
      <div class="tile basis-walmart"><div class="tl">SEO visits · trailing 12 months</div><div class="tv num">${fmtC(t364.recent)}</div><div class="td num">${dlt(t364.change)} vs the aligned prior year · to ${fmtDate(D.preLaunch)}</div></div>
      <div class="tile basis-walmart"><div class="tl">SEO net GMV · trailing 12 months</div><div class="tv num">${fmtUSD(g364.recent)}</div><div class="td num">${dlt(g364.change)} YoY · GMV per visit ${fmtUSD2(g364.recent / t364.recent)} (${spct(D.rpvOpts.lyTrend364.v)})</div></div>
      <div class="tile basis-walmart"><div class="tl">Trailing 13 weeks</div><div class="tv num">${dlt(t91.change)}<small>visits</small></div><div class="td num">GMV ${dlt(g91.change)} · GMV per visit ${fmtUSD2(g91.recent / t91.recent)} (${spct(D.rpvOpts.lyTrend91.v)}). Visits softened from May; dollars did not.</div></div>
      <div class="tile basis-walmart"><div class="tl">AEO · last full week</div><div class="tv num">${fmtC(wk[wk.length - 1].v)}<small>visits</small></div><div class="td num">${fmtUSD(wk[wk.length - 1].g)} GMV · ${fmtUSD2(wk[wk.length - 1].g / wk[wk.length - 1].v)} per visit · ${pct1(wk[wk.length - 1].v / wk[0].v - 1)} since the first full week in May</div></div>
    </div>
    ${fig('SEO channel by calendar month', 'Three years overlaid so seasonality and the year-over-year gap read together. 2024 starts in July (the export does); 2026 runs to 7 September.', chartA, seg('yoyMetric', Object.entries(YMETRICS).map(([k, v]) => [k, v[0].split(' (')[0]]), S.yoyMetric))}
    ${fig('Year over year, month by month', 'Each month against the same weekdays a year earlier (364-day alignment, Walmart’s own convention). Visits ran +13% to +22% from September 2025 to April 2026, then turned negative in May 2026, the month the AEO channel first appears in the export.', chartB)}
    <div class="grid2">${fig('AEO visits by week', 'Sunday to Saturday. The first full week is 3–9 May.', chartC)}${fig('AEO net GMV by week', 'GMV per AEO visit sits at 7.0–7.7 dollars, roughly twice the SEO channel.', chartD)}</div>
    ${fig('Monthly ledger · SEO channel', 'Full months only. Conversion is authorized orders over PDP++ visits.', `<div class="tscroll"><table class="t dense"><thead><tr><th class="l">Month</th><th>Visits</th><th>YoY</th><th>Net GMV</th><th>YoY</th><th>Orders</th><th>GMV / visit</th><th>Conv.</th><th>AOV</th></tr></thead><tbody>${tbl}</tbody></table></div>`)}
  </div>`;
}

// ═══ Data delta tab ═════════════════════════════════════════════════════════
function viewDelta(D) {
  // Monthly series over the overlap
  const from = '2024-10-01', to = LAST_WM;
  const mo = monthly({wm: WM.seo.visits, gsc: GSC.total, nb: GSC.nonbrand, br: GSC.brand, an: GSC.anon, bing: BING.clicks}, from, to);
  const cover = (ser, r) => ser.count(`${r.y}-${String(r.m).padStart(2, '0')}-01`, `${r.y}-${String(r.m).padStart(2, '0')}-${String(dim(r.y, r.m)).padStart(2, '0')}`) === dim(r.y, r.m);
  const fullM = mo.filter(r => r.days === dim(r.y, r.m));
  const yoyOf = (ser, r) => { const a = `${r.y}-${String(r.m).padStart(2, '0')}-01`, b = `${r.y}-${String(r.m).padStart(2, '0')}-${String(dim(r.y, r.m)).padStart(2, '0')}`; if (!cover(ser, r)) return null; const pa = isoOf(dayNum(a) - YOY), pb = isoOf(dayNum(b) - YOY); if (ser.count(pa, pb) < dim(r.y, r.m)) return null; const p = ser.sum(pa, pb); return p ? ser.sum(a, b) / p - 1 : null; };
  const yrows = fullM.filter(r => r.y >= 2025 && (r.y > 2025 || r.m >= 7)).map(r => ({lbl: MON[r.m - 1] + ' ' + String(r.y).slice(2), wm: yoyOf(WM.seo.visits, r), gsc: yoyOf(GSC.total, r), bing: yoyOf(BING.clicks, r)}));
  const xs1 = yrows.map((_, i) => i);
  const c1 = lineChart({id: 'd-yoy', xs: xs1, xLabel: i => yrows[i].lbl, xTicks: xs1, tipX: i => yrows[i].lbl, yFmt: spct, h: 300, series: [
    {name: 'Walmart SEO visits', color: '--wm', ys: yrows.map(r => r.wm), dots: true, width: 2.5}, {name: 'GSC clicks (US, web, all buckets)', color: '--bt', ys: yrows.map(r => r.gsc), dots: true}, {name: 'Bing clicks', color: '--third', ys: yrows.map(r => r.bing), dots: true}], aria: 'Year over year by source'});
  const rrows = fullM.filter(r => cover(GSC.total, r));
  const c2 = lineChart({id: 'd-ratio', xs: rrows.map((_, i) => i), xLabel: i => MON[rrows[i].m - 1] + ' ' + String(rrows[i].y).slice(2), xTicks: rrows.map((_, i) => i).filter(i => i % 2 === 0), tipX: i => MON[rrows[i].m - 1] + ' ' + rrows[i].y, yFmt: v => v.toFixed(1) + '×', w: 560, h: 280, yZero: false,
    series: [{name: 'Walmart visits per GSC click', color: '--wm', ys: rrows.map(r => r.gsc ? r.wm / r.gsc : null), dots: true, width: 2.5}, {name: 'Walmart visits per GSC + Bing click', color: '--wm-lo', ys: rrows.map(r => cover(BING.clicks, r) ? r.wm / (r.gsc + r.bing) : null), dash: true}], aria: 'Visits per click ratio'});
  const base = fullM.find(r => r.y === 2025 && r.m === 4);
  const irows = fullM.filter(r => r.y > 2025 || (r.y === 2025 && r.m >= 4));
  const c3 = lineChart({id: 'd-idx', xs: irows.map((_, i) => i), xLabel: i => MON[irows[i].m - 1] + ' ' + String(irows[i].y).slice(2), xTicks: irows.map((_, i) => i).filter(i => i % 2 === 0), tipX: i => MON[irows[i].m - 1] + ' ' + irows[i].y, yFmt: v => Math.round(v), w: 560, h: 280, yZero: false,
    series: [{name: 'Walmart SEO visits', color: '--wm', ys: irows.map(r => r.wm / base.wm * 100), width: 2.5}, {name: 'GSC clicks, all buckets', color: '--bt', ys: irows.map(r => cover(GSC.total, r) ? r.gsc / base.gsc * 100 : null)}, {name: 'GSC non-branded clicks', color: '--bt-lo', ys: irows.map(r => cover(GSC.total, r) ? r.nb / base.nb * 100 : null), dash: true}, {name: 'Bing clicks', color: '--third', ys: irows.map(r => cover(BING.clicks, r) ? r.bing / base.bing * 100 : null)}], aria: 'Indexed to April 2025'});
  // Frank's windows
  const fw = FD.trajectory.engines.google.yoy, wmF = yoyWindow(WM.seo.visits, fw.window_recent[1], 299);
  const winA = '2025-09-01', winB = '2025-12-20';
  const wmWin = WM.seo.visits.sum(winA, winB), gscWin = GSC.total.sum(winA, winB), bingWin = BING.clicks.sum(winA, winB);
  const winRows = [
    ['Frank’s trend window · 15 Oct → 9 Aug, this year vs last', fmtC(wmF.recent) + ' vs ' + fmtC(wmF.prior), dlt(wmF.change), fmtC(fw.recent.clicks) + ' vs ' + fmtC(fw.prior.clicks), dlt(fw.clicks)],
    ['Non-branded only (Frank’s lift scope)', '— no brand split in the export', '', fmtC(FD.trajectory.googleNonbrand.yoy.recent.clicks) + ' vs ' + fmtC(FD.trajectory.googleNonbrand.yoy.prior.clicks), dlt(FD.trajectory.googleNonbrand.yoy.clicks)],
    ['Measurement window last year · 1 Sep → 20 Dec 2025', fmtC(wmWin) + ' visits', '', fmtC(gscWin) + ' GSC + ' + fmtC(bingWin) + ' Bing clicks', (wmWin / (gscWin + bingWin)).toFixed(2) + '× visits per click'],
    ['Weekly ratio, Oct 2024 → Aug 2026', '', '', '', 'range 1.95× – 3.39×, drifting up'],
  ];
  // AEO vs scorecard
  const wkA = weeklySat({v: WM.aeo.visits, g: WM.aeo.gmv, o: WM.aeo.orders}, P.aeo.start, LAST_WM).filter(w => w.days === 7);
  const scRows = FD.trajectory.ai.weeks.map(w => { const k = wkA.find(x => x.end === w.ends); return `<tr><td class="nw">${esc(w.week.replace('FY27-', ''))} · week to ${fmtDateS(w.ends)}</td><td class="num bt">${fmtC(w.three_day.visits)}${w.three_day.attested ? '' : '*'}</td><td class="num wm">${k ? fmtC(k.v) : '—'}</td><td class="num">${k ? dlt(k.v / w.three_day.visits - 1) : ''}</td><td class="num bt">${fmtUSD(w.three_day.gmv)}</td><td class="num wm">${k ? fmtUSD(k.g) : '—'}</td><td class="num">${k ? dlt(k.g / w.three_day.gmv - 1) : ''}</td><td class="num bt">${fmtUSD2(w.three_day.gmv / w.three_day.visits)}</td><td class="num wm">${k ? fmtUSD2(k.g / k.v) : '—'}</td></tr>`; }).join('');
  const last4 = wkA.slice(-4), l4v = sum(last4.map(w => w.v)) / 4, l4g = sum(last4.map(w => w.g)) / 4;
  return `<div class="stack">
    <div class="callout"><strong>The two archives disagree on direction, not just level.</strong> On the 299 days Frank measured, Walmart’s SEO channel grew ${spct(wmF.change)} while GSC clicks fell ${spct(fw.clicks)}. Frank’s baseline therefore has Walmart’s organic <em>declining</em> into the pilot; Walmart’s own ledger has it roughly flat to up. The ratio between the two has drifted from about 2.1 visits per click in late 2024 to about 2.8 in 2026, which is the divergence expressed as a level.</div>
    ${fig('Year over year by source', 'Monthly, 364-day aligned, full months only. GSC has a comparable prior year from November 2025; Bing from April 2026.', c1)}
    <div class="grid2">
      ${fig('Walmart SEO visits per GSC click', 'A stable measurement gap would be a flat line. This one climbs, which means Walmart’s SEO channel is counting something GSC increasingly is not.', c2)}
      ${fig('Indexed to April 2025 = 100', 'Levels stripped away, so the trajectories can be read against each other. Non-branded Google, the scope Botify’s lift acts on, is the weakest line.', c3)}
    </div>
    ${fig('The windows that matter', 'Same dates, both sources.', `<div class="tscroll"><table class="t"><thead><tr><th class="l">Window</th><th class="l"><span class="dot wm"></span>Walmart SEO visits</th><th>YoY</th><th class="l"><span class="dot bt"></span>Botify archive clicks</th><th>YoY / ratio</th></tr></thead><tbody>${winRows.map(r => `<tr><td>${r[0]}</td><td class="l num">${r[1]}</td><td class="num">${r[2]}</td><td class="l num">${r[3]}</td><td class="num">${r[4]}</td></tr>`).join('')}</tbody></table></div>`)}
    ${fig('Why the SEO numbers differ', 'Candidate explanations, in the order I would test them. None of these is confirmed by the export itself; several are questions for Walmart.', `<div class="srcs">
      <div><b>Clicks are not visits.</b> GSC counts a click on a Google web result. Walmart counts a site session that reached a product page (PDP++). One click can seed several visits (return via history, app hand-off, tab restore); the ~2.5× gap is mostly this, but a stable definition would give a stable ratio.</div>
      <div><b>Channel scope.</b> GSC is Google web search only, US only, domain property. Walmart’s SEO vehicle is every organic referrer it classifies as search: Google, Bing, DuckDuckGo, Yahoo, and possibly Google Discover, image and shopping surfaces, and unattributed app deep links. Bing alone adds 7% to our archive; the rest we cannot see.</div>
      <div><b>Attribution basis.</b> The AEO match pins the export to Walmart’s 3-day attribution. If SEO visits are likewise attributed, a visit that arrived from search and returned within 3 days is SEO both times. GSC has no such memory.</div>
      <div><b>Reclassification on 1 May 2026.</b> SEO visits flipped from +14.5% YoY in April to −10.3% in May, the month AEO first appears. Removing AI referrals from SEO would lower SEO visits, but AEO’s 6M May visits explain only about a third of the swing. Something else moved too, and it is worth asking what.</div>
      <div><b>GSC counts fewer clicks than happen.</b> Frank noted both GSC tables return a fixed ~46k rows a day regardless of traffic, and that the anonymized bucket is 90% of impressions. Property-level totals are less affected than row-level ones, but a domain property still under-counts across subdomains and privacy-filtered queries.</div>
      <div><b>Bot and internal filtering.</b> Walmart filters bots from its analytics with its own rules; Google filters differently before it reports. The direction of that difference is not knowable from here.</div>
    </div>`)}
    ${fig('AI channel: Frank’s scorecard weeks against the export', 'Visits match within 2%, which fixes the export to the same 3-day basis. GMV in the export runs 14–16% below the scorecard, consistent with the export being net GMV (after cancellations and returns) where the scorecard quoted gross. * W17’s 3-day pair was derived by Frank from stated week-over-week deltas, not attested.',
      `<div class="tscroll"><table class="t"><thead><tr><th class="l">Week</th><th>Scorecard visits</th><th>Export visits</th><th>Δ</th><th>Scorecard GMV</th><th>Export GMV</th><th>Δ</th><th>Scorecard $/visit</th><th>Export $/visit</th></tr></thead><tbody>${scRows}
      <tr class="total"><td class="nw">Now · 4 weeks to ${fmtDateS(wkA[wkA.length - 1].end)}</td><td class="num">—</td><td class="num wm">${fmtC(l4v)}</td><td class="num">${dlt(l4v / D.aiF.weeklyVisits - 1)} vs Frank’s base</td><td class="num">—</td><td class="num wm">${fmtUSD(l4g)}</td><td></td><td class="num bt">${fmtUSD2(D.aiF.rpv)}</td><td class="num wm">${fmtUSD2(l4g / l4v)}</td></tr></tbody></table></div>
      <p class="note" style="margin-top:12px">The material change is not the level of any one week but that the channel has grown ${pct1(l4v / D.aiF.weeklyVisits - 1)} since Frank’s two weeks. His 1.11× ecosystem multiplier (OpenAI as 90% of AI referrals) may or may not apply: if Walmart’s AEO vehicle already counts every AI assistant, it should not. The export does not say.</p>`)}
  </div>`;
}

// ═══ Assumptions & questions tab ════════════════════════════════════════════
function viewAssumptions(D) {
  const Q = [
    ['Is the 1 September launch real, and is SpeedWorkers serving?', 'Frank’s deployment snapshot on 13 Aug read “connected, no bot traffic routed yet”. The export shows 7 post-launch days at +2.9% YoY visits. If routing began later, the launch date control should move and those days are pre-launch baseline.', 'Launch date, top bar'],
    ['Which trend should the Walmart baseline carry?', `The export supports +9.5% (12 months), −3.9% (13 weeks) or +6.2% (4 weeks). Frank’s GSC trend is −10.8%. The default here is the 13-week read because it spans a full quarter and post-dates the May break. One point of trend is about ${fmtC(D.wm.mid.lyVisits * 0.01)} visits over the window, versus ${fmtC(D.wm.low.incVisits)} incremental at the low tier.`, 'Baseline trend'],
    ['What is a visit worth: Walmart’s current GMV per visit, or the contract’s frozen $3.19?', `The addendum freezes RPV at AOV $74.10 × CR 4.3%. Walmart’s export gives $3.21 for the year to July 2026, so the frozen figure was right when set, but the trailing quarter is ${fmtUSD2(D.rpvOpts.t91flat.flat)} and Nov/Dec run 15–20% above the annual mean. The default grows last year’s month by the 12-month RPV change.`, 'GMV per visit; AOV × CR'],
    ['How should Botify’s click lift become Walmart visits?', `Proportional (default) applies Frank’s lift rate to Walmart’s base and inherits Walmart’s seasonality. The ratio method multiplies his clicks by the measured ${D.vpc.ratio.toFixed(2)} visits per click. They agree within a few percent at mid; the choice matters more for how the number is explained than for its size.`, 'Lift translation'],
    ['Does Walmart’s AEO vehicle count all AI assistants, or OpenAI only?', 'The visits match the OpenAI scorecard weeks to within 2%, which suggests AEO was OpenAI-only in May. If other assistants have since been added, part of the August step-up is scope, not growth, and the 1.11× ecosystem multiplier must stay at 1.', 'AI risk and scope'],
    ['Should the AEO base be held flat or allowed to keep growing?', `The channel doubled between late June and late August. Held flat is Frank’s posture and the default. The linear option continues the trailing 8-week slope (${fmtC(D.aeoB.weeklySlope)} visits/week/week), which roughly doubles the AI figure by December.`, 'AI channel'],
    ['Is the export’s “Net GMV” the number Walmart will judge revenue on?', 'It runs 14–16% below the gross GMV in the scorecards. If the pilot is scored on net, every dollar figure on the Walmart basis is already on that footing; if gross, they are 15% light.', 'No control; affects interpretation'],
    ['PDP++ or PDP visits?', 'The summary tabs use PDP++ and so does this page. The two differ by 0.1%, so it does not move a result, but the addendum should name one.', 'No control'],
    ['What happened on 1 May 2026?', 'SEO visits swung from +14.5% to −10.3% YoY in one month as AEO appeared. If Walmart re-classified traffic, the pre-May and post-May SEO series are not comparable and the 12-month trend option is overstated.', 'Baseline trend'],
    ['Which horizon is the headline: 20 December (contract close) or 31 December (decision)?', 'Frank moved goal-facing figures to the 20th. This page defaults to the 20th; the eleven extra days are peak season at peak adoption and add 16–23% to every tier.', 'Horizon, top bar'],
  ];
  const A = [
    ['Year-over-year alignment', '364 days back, so weekdays match. Identical to the Ly Dt column in the export.', 'Measured'],
    ['Zero-visit days', `SEO ${WM.seo.imputed.map(fmtDate).join(', ')} and AEO ${WM.aeo.imputed.map(fmtDate).join(', ')} report zero visits with non-zero GMV. Treated as export gaps and set to the mean of the neighbouring days. Raw values are kept for the tables.`, 'Assumption'],
    ['Pre-launch cut-off', `Every trend and rate is measured to ${fmtDate(D.preLaunch)}, the day before launch, so post-launch days never feed the baseline they are compared against.`, 'Method'],
    ['Walmart baseline', 'Last year’s aligned daily visits × (1 + trend). No separate seasonality index: last year’s days already carry the shape, including Walmart’s record December.', 'Method'],
    ['Frank’s baseline', 'Monthly Google + Bing totals for Aug 2025 – Jul 2026 indexed by calendar month × (1 + engine trend). His arithmetic, unchanged.', 'Method'],
    ['Lift levers', `Anonymized inclusion ${S.anon}%, growth ${S.growthLo}–${S.growthHi}%, indexation dial ${S.dialLo}–${S.dialHi}%, new-page performance ${S.newPagePerf}%, Bing targets from the workbook. Mid is the midpoint of every input.`, 'Frank’s defaults'],
    ['Ramp', `${S.tranches} tranches over ${S.rampWeeks} weeks; adoption steps at 30-day marks (low 2/8/22/40%, mid 11/26.5/46/65%, high 20/45/70/90%). Applied identically to search and AI on both bases.`, 'Frank’s defaults'],
    ['Visits per click', `${D.vpc.ratio.toFixed(3)}, from ${fmtC(D.vpc.visits)} Walmart SEO visits over ${fmtC(D.vpc.clicks)} GSC + Bing clicks, ${fmtDateS(D.vpc.from)} – ${fmtDate(D.vpc.to)}.`, 'Measured'],
    ['Frank’s base for the lift rate', `${fmtC(FRANK_BASE_CLICKS)} Google + Bing clicks, Aug 2025 – Jul 2026, his combined property total. Lift rates: ${TIERS.map(t => pct2(D.ann.clicks[t] / FRANK_BASE_CLICKS)).join(' / ')} at full adoption.`, 'Derived'],
    ['AEO baseline', `Trailing 28 days to ${fmtDate(D.aeoB.to)}: ${fmtC(D.aeoB.weeklyVisits)} visits/week. GMV per visit from the trailing 91 days. Frank’s two scorecard weeks are retained as the “Botify” basis for AI.`, 'Measured'],
    ['What is not modelled', 'Bing indexation, infrastructure savings, offline halo, strategic AI multipliers: all excluded by Frank for stated reasons, and excluded here. The +40M indexed pages, crawler compliance and share-of-voice tests in the addendum are not revenue and are not on this page.', 'Scope'],
  ];
  return `<div class="stack">
    ${fig('Open questions', 'Ranked by how much the answer moves the number. The tag names the control that changes with the answer, so each can be settled in the model the moment it is settled in the room.',
      `<div class="qlist">${Q.map((q, i) => `<div class="q"><div class="qn">Q${i + 1}</div><div><h4>${q[0]}</h4><p>${q[1]}</p></div><div class="qm">Control: <b>${q[2]}</b></div></div>`).join('')}</div>`)}
    ${fig('Assumptions and method', '', `<div class="tscroll"><table class="t"><thead><tr><th class="l">Item</th><th class="l">What this page does</th><th class="l">Grade</th></tr></thead><tbody>${A.map(a => `<tr><td>${a[0]}</td><td class="l" style="max-width:70ch">${a[1]}</td><td class="l">${chip(a[2] === 'Measured' ? 'ok' : a[2] === 'Assumption' ? 'warn' : '', a[2])}</td></tr>`).join('')}</tbody></table></div>`)}
    ${fig('Sources', '', `<div class="srcs">
      <div><b>DMP_SEO_9thJul24.xlsx</b> · Walmart internal reporting, marketing vehicle SEO, all divisions. Daily 9 Jul 2024 – 7 Sep 2026: Ty Net GMV, Auth Orders, PDP and PDP++ visits, with Ly columns 364 days back.</div>
      <div><b>AEO_1stMay26.xlsx</b> · Same report, marketing vehicle AEO. Daily 1 May – 7 Sep 2026. No prior-year columns (the vehicle is new).</div>
      <div><b>Frank’s framework</b> · framework.html DATA block and data/archive/daily.csv (GSC US/web by bucket, 664 days; Bing property total, 514 days); STATE.md, HANDOFF-TO-RYAN.md, CORRECTION-MEMO.md, REVIEW.md, 13 Aug 2026. Parity with forecast.py checked on the headline: 1,843,988 / 7,291,533 / 16,325,245 clicks to 31 Dec; $6.78M / $57.82M.</div>
      <div><b>Walmart Agentic Commerce Scorecards</b> W16 and W17 FY27 (Jie Li), as recorded in Frank’s data; not re-read here.</div>
    </div>`)}
  </div>`;
}

// ═══ shell ══════════════════════════════════════════════════════════════════
const TABS = [['forecast', 'Forecast'], ['yoy', 'Year over year'], ['delta', 'Data delta'], ['assumptions', 'Assumptions & questions']];
function renderShell() {
  document.getElementById('ctlbar').innerHTML = `
    <div class="ctl"><span class="lbl">Basis</span>${seg('basis', [['walmart', 'Walmart reporting'], ['botify', 'Botify GSC + BWT'], ['compare', 'Compare']], S.basis, 'basis')}</div>
    <div class="ctl"><span class="lbl">Horizon</span>${seg('horizon', [['2026-12-20', '20 Dec · close'], ['2026-12-31', '31 Dec · decision']], S.horizon)}</div>
    <div class="ctl"><label class="lbl" for="in-launch">Launch</label><input type="date" id="in-launch" data-key="launch" value="${S.launch}" min="2026-08-01" max="2026-12-01"></div>`;
  document.getElementById('tabs').innerHTML = TABS.map(([k, l]) => `<button class="tab" role="tab" data-set="tab" data-v="${k}" aria-selected="${S.tab === k}">${l}</button>`).join('');
}
function render() {
  renderShell();
  const D = derive(), view = document.getElementById('view');
  view.innerHTML = S.tab === 'yoy' ? viewYoy(D) : S.tab === 'delta' ? viewDelta(D) : S.tab === 'assumptions' ? viewAssumptions(D) : viewForecast(D);
  wireCharts(view);
  const det = document.getElementById('inputs'); if (det) det.addEventListener('toggle', () => { S.inputsOpen = det.open; persist(); });
}
const NUMKEYS = new Set(['wmTrendCustom', 'aeoEco', 'anon', 'growthLo', 'growthHi', 'dialLo', 'dialHi', 'newPagePerf', 'aov', 'cr', 'trendGoogle', 'trendBing', 'rampWeeks', 'tranches']);
document.addEventListener('click', e => {
  const b = e.target.closest('[data-set]'); if (!b) return;
  const k = b.dataset.set, v = b.dataset.v;
  if (k === '__reset') { const keep = {tab: S.tab, basis: S.basis, inputsOpen: true}; S = Object.assign({}, DEFAULTS, keep); persist(); render(); return; }
  S[k] = v; if (k === 'tab') window.scrollTo({top: 0}); persist(); render();
});
let raf = 0;
function onInput(e) {
  const el = e.target.closest('[data-key]'); if (!el) return;
  const k = el.dataset.key;
  if (el.type === 'checkbox') S[k] = el.checked;
  else if (NUMKEYS.has(k)) { S[k] = +el.value; if (k === 'growthLo' && S.growthLo > S.growthHi) S.growthHi = S.growthLo; if (k === 'growthHi' && S.growthHi < S.growthLo) S.growthLo = S.growthHi; if (k === 'dialLo' && S.dialLo > S.dialHi) S.dialHi = S.dialLo; if (k === 'dialHi' && S.dialHi < S.dialLo) S.dialLo = S.dialHi; }
  else { if (k === 'launch' && !/^\d{4}-\d{2}-\d{2}$/.test(el.value)) return; S[k] = el.value; }
  if (k === 'launch' && dayNum(S.launch) >= dayNum(S.horizon)) S.launch = '2026-12-01';
  S.inputsOpen = true; persist();
  if (el.type === 'range') { const v = el.parentElement.querySelector('.val'); if (v) v.textContent = el.value + (v.textContent.replace(/^[\d.\-]+/, '')); cancelAnimationFrame(raf); raf = requestAnimationFrame(render); }
  else render();
}
document.addEventListener('input', onInput);
document.addEventListener('change', e => { if (e.target.tagName === 'SELECT' || e.target.type === 'date') onInput(e); });
render();

import json, datetime as dt
SP = '/tmp/claude-0/-home-user-Botify/4b0b445d-dc93-5335-be9d-5864a937eee9/scratchpad/wm/'
S = json.load(open(SP + 'series.json')); YOY = json.load(open(SP + 'yoy.json'))
OUT_HTML = '/home/user/Botify/analysis/walmart-pilot-exec-brief.html'
DASH = ' stroke-dasharray="6 5"'
MONTHS = ["Sep", "Oct", "Nov", "Dec"]
WM   = [148.1, 161.2, 175.1, 208.8]; FLAT = [154.3, 163.6, 163.3, 173.5]; MEAS = [139.3, 147.7, 147.5, 156.8]
IDX_WM = [100.0, 105.3, 118.2, 136.4]; IDX_AC = [100.0, 102.7, 106.1, 109.2]
GOALS = [("2026-09-30", 8.7), ("2026-10-31", 18.4), ("2026-11-30", 30.9), ("2026-12-20", 45.3)]

def lines(series, ymin, ymax, ticks, W=760, H=250, L=56, Rm=210, T=18, B=44, yfmt=lambda t: f"{t}M", vfmt=lambda v: f"{v:.1f}M", title=""):
    pw = W - L - Rm; ph = H - T - B; xs = [L + i * pw / 3 for i in range(4)]
    y = lambda v: T + (ymax - v) / (ymax - ymin) * ph
    g = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img"><title>{title}</title>']
    for t in ticks:
        g += [f'<line class="grid" x1="{L}" x2="{L+pw}" y1="{y(t):.1f}" y2="{y(t):.1f}"/>', f'<text class="tick" x="{L-8}" y="{y(t)+4:.1f}" text-anchor="end">{yfmt(t)}</text>']
    for i, m in enumerate(MONTHS): g.append(f'<text class="tick" x="{xs[i]:.1f}" y="{T+ph+22}" text-anchor="middle">{m} 2026</text>')
    for name, vals, cls, dash in series:
        pts = " ".join(f"{xs[i]:.1f},{y(v):.1f}" for i, v in enumerate(vals))
        g.append(f'<polyline class="line {cls}"{DASH if dash else ""} points="{pts}"/>')
        g += [f'<circle class="dot {cls}" cx="{xs[i]:.1f}" cy="{y(v):.1f}" r="4"/>' for i, v in enumerate(vals)]
    lab = sorted([(y(v[-1]), n, v[-1], c) for n, v, c, _ in series]); placed = []
    for yy, n, v, c in lab:
        yy2 = yy if not placed or yy - placed[-1] >= 28 else placed[-1] + 28; placed.append(yy2)
        g += [f'<line class="leader" x1="{xs[-1]+6}" x2="{xs[-1]+14}" y1="{yy:.1f}" y2="{yy2:.1f}"/>',
              f'<text class="dlabel" x="{xs[-1]+18}" y="{yy2-3:.1f}">{n}</text>', f'<text class="dvalue {c}" x="{xs[-1]+18}" y="{yy2+11:.1f}">{vfmt(v)}</text>']
    return "\n".join(g) + '</svg>'

def yoy_bars(W=760, H=270, L=56, Rm=20, T=22, B=44):
    pw = W - L - Rm; ph = H - T - B; n = len(YOY); slot = pw / n; bw = slot * 0.62
    ymin, ymax = -22, 0
    y = lambda v: T + (ymax - v) / (ymax - ymin) * ph
    g = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img"><title>Google clicks, year over year, by month</title>']
    for t in (0, -5, -10, -15, -20):
        g += [f'<line class="grid" x1="{L}" x2="{L+pw}" y1="{y(t):.1f}" y2="{y(t):.1f}"/>', f'<text class="tick" x="{L-8}" y="{y(t)+4:.1f}" text-anchor="end">{t}%</text>']
    g.append(f'<line class="axis" x1="{L}" x2="{L+pw}" y1="{y(0):.1f}" y2="{y(0):.1f}"/>')
    for i, (ym, cur, prior, ch) in enumerate(YOY):
        x = L + i * slot + (slot - bw) / 2; v = ch * 100; top = y(0); hgt = y(v) - y(0)
        cls = "s-bad" if v < -14 else "s-claim"
        g.append(f'<rect class="bar {cls}" x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{hgt:.1f}" rx="0"/>')
        g.append(f'<text class="dvalue {cls}" x="{x+bw/2:.1f}" y="{y(v)+13:.1f}" text-anchor="middle">{v:.1f}%</text>')
        d = dt.date(int(ym[:4]), int(ym[5:]), 1)
        g.append(f'<text class="tick" x="{x+bw/2:.1f}" y="{T+ph+22}" text-anchor="middle">{d.strftime("%b %y")}</text>')
    return "\n".join(g) + '</svg>'

def cum_chart(W=760, H=280, L=56, Rm=210, T=18, B=44):
    pw = W - L - Rm; ph = H - T - B
    d0, d1 = dt.date(2026, 9, 1), dt.date(2026, 12, 20); span = (d1 - d0).days
    x = lambda d: L + (dt.date.fromisoformat(d) - d0).days / span * pw
    y = lambda v: T + (50 - v) / 50 * ph
    g = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img"><title>Cumulative incremental visits vs Walmart goals</title>']
    for t in (0, 10, 20, 30, 40, 50):
        g += [f'<line class="grid" x1="{L}" x2="{L+pw}" y1="{y(t):.1f}" y2="{y(t):.1f}"/>', f'<text class="tick" x="{L-8}" y="{y(t)+4:.1f}" text-anchor="end">{t}M</text>']
    for d, lab in (("2026-09-01", "Sep 1"), ("2026-09-30", "Sep 30"), ("2026-10-31", "Oct 31"), ("2026-11-30", "Nov 30"), ("2026-12-20", "Dec 20")):
        g.append(f'<text class="tick" x="{x(d):.1f}" y="{T+ph+22}" text-anchor="middle">{lab}</text>')
    for d, lab, dy in (("2026-09-17", "launch 9/17", 12), ("2026-09-24", "launch 9/24", 26)):
        g += [f'<line class="marker" x1="{x(d):.1f}" x2="{x(d):.1f}" y1="{T}" y2="{T+ph}"/>', f'<text class="tick" x="{x(d)+4:.1f}" y="{T+dy}">{lab}</text>']
    series = [("Our high case, launch Sep 1", "high_0901", "s-t1", False), ("Our high case, launch Sep 17", "high_0917", "s-t2", False),
              ("Our high case, launch Sep 24", "high_0924", "s-t3", False), ("Low case (contract tier), Sep 24", "low_0924", "s-t3", True)]
    ends = []
    for name, key, cls, dash in series:
        pts = S[key]; poly = f"{x('2026-09-01'):.1f},{y(0):.1f} {x(pts[0][0]):.1f},{y(0):.1f} " + " ".join(f"{x(d):.1f},{y(v/1e6):.1f}" for d, v in pts)
        g.append(f'<polyline class="line {cls}"{DASH if dash else ""} points="{poly}"/>'); ends.append((y(pts[-1][1] / 1e6), name, pts[-1][1] / 1e6, cls))
    step = f"{x('2026-09-01'):.1f},{y(0):.1f} "; py = y(0)
    for d, v in GOALS: step += f"{x(d):.1f},{py:.1f} {x(d):.1f},{y(v):.1f} "; py = y(v)
    g.append(f'<polyline class="line s-claim" stroke-dasharray="2 4" points="{step.strip()}"/>')
    for d, v in GOALS:
        xx, yy = x(d), y(v)
        g += [f'<rect class="dot s-claim" x="{xx-5:.1f}" y="{yy-5:.1f}" width="10" height="10" transform="rotate(45 {xx:.1f} {yy:.1f})"/>', f'<text class="dvalue s-claim" x="{xx:.1f}" y="{yy-9:.1f}" text-anchor="middle">{v}M</text>']
    ends.append((y(45.3), "Walmart's threshold", 45.3, "s-claim")); ends.sort(); placed = []
    for yy, n, v, c in ends:
        yy2 = yy if not placed or yy - placed[-1] >= 28 else placed[-1] + 28; placed.append(yy2)
        g += [f'<line class="leader" x1="{L+pw+6}" x2="{L+pw+14}" y1="{yy:.1f}" y2="{yy2:.1f}"/>', f'<text class="dlabel" x="{L+pw+18}" y="{yy2-3:.1f}">{n}</text>', f'<text class="dvalue {c}" x="{L+pw+18}" y="{yy2+11:.1f}">{v:.1f}M</text>']
    return "\n".join(g) + '</svg>'

c_yoy = yoy_bars()
c_base = lines([("Walmart's Annex A baseline", WM, "s-claim", False), ("If the decline simply stopped", FLAT, "s-t1", False), ("Their measured trend, −10.8%", MEAS, "s-t2", False)], 120, 215, [120, 140, 160, 180, 200], title="Monthly visits, Sep–Dec 2026")
c_shape = lines([("Annex A baseline", IDX_WM, "s-claim", False), ("Walmart's own search traffic, 2025", IDX_AC, "s-t2", False)], 95, 142, [100, 110, 120, 130, 140], yfmt=lambda t: str(t), vfmt=lambda v: f"{v:.0f}", title="Per-day index, September = 100")
c_cum = cum_chart()

def footer(n): return f'<div class="foot"><span>Botify · Walmart SpeedWorkers pilot · Internal</span><span>Annex A baseline &amp; §16.4 goals — {n} / 8</span></div>'

HTML = f'''<!doctype html><html><head><meta charset="utf-8"><title>Walmart Pilot — Baseline &amp; Goals Brief</title>
<style>
@page {{ size: Letter; margin: 0; }}
:root {{ --ink:#171B21; --ink2:#454D57; --muted:#727A85; --rule:#DCE0E6; --rule2:#EDF0F3; --claim:#B45309; --claim-tint:#FBEFE3; --t1:#00544C; --t2:#008C7E; --t3:#58BEB1; --teal-tint:#E3F3F1; --bad:#B3261E; --bad-tint:#FBE9E7; --grid:#E6E9EE;
  --serif:"Bitstream Charter","Charter",Georgia,serif; --sans:"Liberation Sans","Helvetica Neue",Arial,sans-serif; --mono:"DejaVu Sans Mono","Liberation Mono",monospace; }}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:#fff; color:var(--ink); font-family:var(--sans); font-size:10.5pt; line-height:1.42; -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
.pg {{ width:8.5in; height:11in; padding:0.5in 0.65in 0.55in; position:relative; overflow:hidden; break-after:page; page-break-after:always; }}
.pg:last-child {{ break-after:auto; page-break-after:auto; }}
.eyebrow {{ font-family:var(--mono); font-size:8pt; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); display:flex; gap:12px; }}
.eyebrow .tag {{ color:var(--claim); }}
.num {{ font-family:var(--serif); font-size:9pt; color:var(--muted); letter-spacing:.06em; text-transform:uppercase; margin-top:26px; }}
h1 {{ font-family:var(--serif); font-weight:normal; font-size:26pt; line-height:1.1; margin:8px 0 0; letter-spacing:-0.01em; }}
h1.big {{ font-size:34pt; margin-top:18px; }}
h2 {{ font-family:var(--serif); font-weight:normal; font-size:14pt; margin:14px 0 0; }}
p {{ margin:9px 0 0; color:var(--ink2); }}
p.lead {{ font-size:12pt; line-height:1.4; color:var(--ink); margin-top:10px; }}
b {{ color:var(--ink); }}
.prose {{ max-width:6.3in; }}
.kpis {{ display:grid; grid-template-columns:repeat(3,1fr); margin-top:20px; border-top:2px solid var(--ink); }}
.kpis > div {{ padding:14px 14px 16px 0; border-right:1px solid var(--rule); }} .kpis > div + div {{ padding-left:14px; }} .kpis > div:last-child {{ border-right:0; }}
.kpis .k {{ font-family:var(--mono); font-size:7.5pt; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }}
.kpis .n {{ font-family:var(--serif); font-size:27pt; line-height:1; margin-top:8px; }} .kpis .n.claim {{ color:var(--claim); }} .kpis .n.bad {{ color:var(--bad); }}
.kpis p {{ font-size:9pt; margin-top:7px; line-height:1.38; }}
.callout {{ margin-top:16px; padding:11px 14px; border-left:3px solid var(--bad); background:var(--bad-tint); }}
.callout p {{ margin:0; color:var(--ink); }} .callout p + p {{ margin-top:7px; }}
.callout.teal {{ border-color:var(--t2); background:var(--teal-tint); }}
figure {{ margin:12px 0 0; }}
figcaption {{ font-size:9.5pt; color:var(--ink2); margin-top:6px; }}
.chart {{ width:100%; height:auto; display:block; overflow:visible; }}
.chart text {{ font-family:var(--mono); font-size:9px; fill:var(--muted); }}
.chart .dlabel {{ fill:var(--ink2); font-family:var(--sans); font-size:10.5px; }} .chart .dvalue {{ font-size:10.5px; font-weight:bold; }}
.chart .grid {{ stroke:var(--grid); stroke-width:1; }} .chart .axis {{ stroke:var(--ink); stroke-width:1; }} .chart .marker {{ stroke:var(--rule); stroke-dasharray:3 3; }} .chart .leader {{ stroke:var(--rule); }}
.chart .line {{ fill:none; stroke-width:2; stroke-linejoin:round; stroke-linecap:round; }} .chart .dot {{ stroke:#fff; stroke-width:2; }}
.s-claim {{ stroke:var(--claim); fill:var(--claim); color:var(--claim); }} .s-t1 {{ stroke:var(--t1); fill:var(--t1); color:var(--t1); }} .s-t2 {{ stroke:var(--t2); fill:var(--t2); color:var(--t2); }} .s-t3 {{ stroke:var(--t3); fill:var(--t3); color:var(--t3); }} .s-bad {{ stroke:var(--bad); fill:var(--bad); color:var(--bad); }}
text.dvalue {{ stroke:none; }} rect.bar {{ stroke:none; }}
.legend {{ display:flex; gap:16px; flex-wrap:wrap; font-size:9pt; color:var(--ink2); margin-top:10px; }}
.legend span::before {{ content:""; display:inline-block; width:12px; height:3px; margin-right:6px; vertical-align:middle; background:currentColor; }}
.legend .dash::before {{ background:repeating-linear-gradient(90deg,currentColor 0 3px,transparent 3px 6px); }}
table {{ border-collapse:collapse; width:100%; font-variant-numeric:tabular-nums; font-size:9.8pt; margin-top:10px; }}
th,td {{ padding:5.5px 9px; text-align:right; border-bottom:1px solid var(--rule2); }}
th {{ font-weight:normal; color:var(--muted); font-family:var(--mono); font-size:8pt; letter-spacing:.04em; text-transform:uppercase; }}
th[scope=row], td:first-child, th:first-child {{ text-align:left; }} tbody th[scope=row] {{ color:var(--ink); font-family:var(--sans); font-size:9.8pt; text-transform:none; letter-spacing:0; }}
tr.total td, tr.total th {{ border-top:1px solid var(--ink); border-bottom:0; font-weight:bold; color:var(--ink); }}
td.claim {{ color:var(--claim); font-weight:bold; }} td.bad {{ color:var(--bad); font-weight:bold; }} td.teal {{ color:var(--t2); font-weight:bold; }}
.two {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-top:10px; }}
ul {{ margin:8px 0 0; padding-left:16px; color:var(--ink2); }} li {{ margin-top:6px; }}
ol.asks {{ margin:14px 0 0; padding-left:0; list-style:none; counter-reset:a; }}
ol.asks li {{ position:relative; padding:8px 0 8px 40px; border-top:1px solid var(--rule); color:var(--ink2); }}
ol.asks li::before {{ counter-increment:a; content:counter(a); position:absolute; left:0; top:9px; width:26px; height:26px; border:1px solid var(--ink); border-radius:50%; display:grid; place-items:center; font-family:var(--serif); font-size:12pt; color:var(--ink); }}
ol.asks li b {{ display:block; margin-bottom:2px; }}
.foot {{ position:absolute; left:0.65in; right:0.65in; bottom:0.4in; display:flex; justify-content:space-between; font-family:var(--mono); font-size:7.5pt; color:var(--muted); letter-spacing:.06em; text-transform:uppercase; border-top:1px solid var(--rule); padding-top:6px; }}
.src {{ font-size:8pt; color:var(--muted); margin-top:10px; line-height:1.35; }}
.answer {{ margin-top:12px; padding:10px 14px; border:1px solid var(--rule); }}
.answer p {{ margin:0; }} .answer p + p {{ margin-top:6px; }}
.answer .q {{ font-family:var(--serif); font-size:12pt; color:var(--ink); }}
</style></head><body>

<!-- 1 · cover / summary -->
<section class="pg">
  <div class="eyebrow"><span>Botify · Walmart SpeedWorkers pilot</span><span class="tag">Internal — for the executive team</span><span>8 September 2026</span></div>
  <div class="num">Executive brief</div>
  <h1 class="big">Walmart's baseline and goals, as drafted, describe a pilot that cannot pass.</h1>
  <p class="lead prose">Walmart's own search data shows organic traffic falling 11% year over year and accelerating. Their proposed baseline contains none of that decline and adds a holiday curve their traffic has never shown. Their goals then sit above the most optimistic outcome our model produces at any launch date.</p>
  <div class="kpis">
    <div><div class="k">Their organic search trend</div><div class="n bad">−19.8%</div><p>July 2026 Google clicks vs July 2025 — the worst month in a nine-month run where every month is down. Full period: −10.8%.</p></div>
    <div><div class="k">Baseline inflation · Sep–Dec</div><div class="n claim">+~100M</div><p>Annex A totals 693M visits. Their own run-rate, shape and trend give 591M. Even with zero decline: 655M.</p></div>
    <div><div class="k">Threshold vs our best case</div><div class="n bad">1.4–2.2×</div><p>Walmart wants 45.3M incremental visits. Our <i>high</i> case delivers 31M at a Sep 1 launch, 20M at Sep 24. The contract's low tier: 2–3M.</p></div>
  </div>
  <div class="callout">
    <p><b>Combined effect.</b> Measured against Annex A, actual traffic lands 80–100M visits below baseline before SpeedWorkers adds its first visit. The effective bar becomes roughly 130M incremental visits — four times our most optimistic model at the best launch date, six times at the realistic one.</p>
    <p>Every check in this brief uses Walmart's numbers: their visit counts for scale, their Search Console history for shape and trend, their scorecards for AI. Nothing here depends on Botify's forecast being right.</p>
  </div>
  <h2>The six angles</h2>
  <p class="prose">1 · Their traffic is declining and it is accelerating &nbsp;·&nbsp; 2 · The baseline ignores the decline &nbsp;·&nbsp; 3 · The baseline's shape is not organic search &nbsp;·&nbsp; 4 · What that does to the pilot's arithmetic &nbsp;·&nbsp; 5 · The goals against our model at real launch dates &nbsp;·&nbsp; 6 · What 45.3M means as growth &nbsp;·&nbsp; then what we recommend.</p>
  {footer(1)}
</section>

<!-- 2 · the trend -->
<section class="pg">
  <div class="num">Angle 1 · The reality of their trend</div>
  <h1>Walmart's organic search traffic is falling, and the fall is speeding up.</h1>
  <p class="lead prose">This is Walmart's own Google Search Console data for walmart.com (US, web), compared month by month against the same month a year earlier. Every month since November is down. The last three average −17%.</p>
  <figure>{c_yoy}<figcaption><b>Google clicks, year over year, by month.</b> Nine consecutive months of decline. Impressions are up 20% over the same span, so this is not lost demand — Walmart is being shown more and clicked less.</figcaption></figure>
  <div class="two">
    <div><table><thead><tr><th scope="col">Window</th><th scope="col">Google clicks</th><th scope="col">Year before</th><th scope="col">Change</th></tr></thead><tbody>
      <tr><th scope="row">Nov 2025 – Jul 2026</th><td>508.5M</td><td>572.0M</td><td class="bad">−11.1%</td></tr>
      <tr><th scope="row">May – Jul 2026</th><td>160.0M</td><td>193.1M</td><td class="bad">−17.1%</td></tr>
      <tr><th scope="row">Jul 2026 alone</th><td>53.1M</td><td>66.3M</td><td class="bad">−19.8%</td></tr>
      <tr><th scope="row">299 comparable days</th><td>559.9M</td><td>627.9M</td><td class="bad">−10.8%</td></tr>
    </tbody></table></div>
    <div class="callout teal" style="margin-top:14px"><p><b>Why it matters for the pilot.</b> Any honest "year-over-year run-rate" baseline for Sep–Dec 2026 must be lower than Sep–Dec 2025. Bing is down too (−4.2%). Nothing in this account is flat, and nothing suggests the trend reverses on its own before December.</p></div>
  </div>
  <p class="src">Source: Google Search Console, walmart.com US/Web, day grain, 2024-10-15 → 2026-08-09, from Frank's measurement-framework archive. Bing Webmaster Tools, 514 days to 2026-08-08.</p>
  {footer(2)}
</section>

<!-- 3 · the baseline ignores it -->
<section class="pg">
  <div class="num">Angle 2 · The baseline ignores the decline</div>
  <h1>Annex A contains no decline at all — and then some.</h1>
  <p class="lead prose">Annex A says it applies "a year-over-year run-rate methodology to Walmart's current performance." We rebuilt that projection from Walmart's own inputs. Their number is above it in every month, and the gap widens as the holidays approach.</p>
  <div class="legend"><span class="s-claim">Walmart's Annex A baseline</span><span class="s-t1">If the decline simply stopped</span><span class="s-t2">Their measured trend, −10.8%</span></div>
  <figure>{c_base}<figcaption><b>September is fine; December is not.</b> Annex A's September is within 4% of a no-decline projection. By December it is 20% above even that line and 33% above the measured trend.</figcaption></figure>
  <table><thead><tr><th scope="col">2026</th><th scope="col">Annex A</th><th scope="col">No decline</th><th scope="col">Measured trend</th><th scope="col">Annex A vs trend</th></tr></thead><tbody>
    <tr><th scope="row">September</th><td class="claim">148.1M</td><td>154.3M</td><td>139.3M</td><td>+6%</td></tr>
    <tr><th scope="row">October</th><td class="claim">161.2M</td><td>163.6M</td><td>147.7M</td><td>+9%</td></tr>
    <tr><th scope="row">November</th><td class="claim">175.1M</td><td>163.3M</td><td>147.5M</td><td class="bad">+19%</td></tr>
    <tr><th scope="row">December</th><td class="claim">208.8M</td><td>173.5M</td><td>156.8M</td><td class="bad">+33%</td></tr>
    <tr class="total"><th scope="row">Sep – Dec</th><td>693.2M</td><td>654.7M</td><td>591.3M</td><td class="bad">+17% · ~102M</td></tr>
  </tbody></table>
  <div class="answer">
    <p class="q">Are they ignoring the decline? Yes — and the September number shows how.</p>
    <p>Their September matches Walmart's <i>current</i> run-rate carried forward with no decline. From there the curve rises 41% into December. The growth embedded in the search portion of Annex A is <b>+6% year over year</b>, in a channel their own data puts at −11% to −20%. For Annex A to be true, Walmart would need 2.66 visits per search click; their own scorecards say 2.18–2.25.</p>
  </div>
  <p class="src">Method: Sep–Dec 2025 Google + Bing clicks by month × 2.252 visits per click (Walmart's own SEO visits ÷ our clicks, scorecard week ending 23 May 2026; the higher of two weeks), plus AI-assistant visits held flat at 1.45M/week. Bing held flat rather than at its measured −4.2%. Each choice favours Annex A.</p>
  {footer(3)}
</section>

<!-- 4 · the shape -->
<section class="pg">
  <div class="num">Angle 3 · The shape is not organic search</div>
  <h1>Their holiday curve is three times steeper than their search traffic has ever been.</h1>
  <p class="lead prose">This test needs no conversion between visits and clicks. Index every month to September and compare the shape of Annex A with the shape of Walmart's own organic search traffic in the same months last year.</p>
  <div class="legend"><span class="s-claim">Annex A baseline</span><span class="s-t2">Walmart's own search traffic, 2025</span></div>
  <figure>{c_shape}<figcaption><b>Per-day index, September = 100.</b> Annex A climbs to 136 by December; Walmart's organic search climbed to 109. The 2024 season looked like 2025, so this is not a one-year quirk.</figcaption></figure>
  <table><thead><tr><th scope="col">Ratio</th><th scope="col">Annex A</th><th scope="col">Walmart search, 2025</th><th scope="col">Walmart search, 2024</th></tr></thead><tbody>
    <tr><th scope="row">December ÷ November</th><td class="claim">1.19</td><td class="teal">1.06</td><td class="teal">1.07</td></tr>
    <tr><th scope="row">December ÷ September</th><td class="claim">1.41</td><td class="teal">1.13</td><td>n/a (archive starts Oct 2024)</td></tr>
    <tr><th scope="row">November ÷ September</th><td class="claim">1.18</td><td class="teal">1.06</td><td>n/a</td></tr>
  </tbody></table>
  <div class="answer">
    <p class="q">Where does a 41% Sep-to-Dec climb come from?</p>
    <p>Not from organic search. Walmart's holiday surge in search is real but modest, and it is mostly <i>branded</i> queries — which SpeedWorkers does not act on. A 41% climb is what total-site or all-channel traffic (paid, app, direct, email) does in Q4. If Annex A was built from that, it measures a channel the pilot does not touch, and the December number is not a baseline for this pilot at all.</p>
  </div>
  {footer(4)}
</section>

<!-- 5 · sets us up to fail -->
<section class="pg">
  <div class="num">Angle 4 · What the baseline does to the pilot's arithmetic</div>
  <h1>Measured against Annex A, we start 80–100M visits in the hole.</h1>
  <p class="lead prose">Incremental visits are defined as actual minus baseline. If Walmart's traffic simply follows its own trend — no SpeedWorkers effect at all — here is what the contract would record each month.</p>
  <table><thead><tr><th scope="col">2026</th><th scope="col">Where their traffic lands on trend</th><th scope="col">Annex A baseline</th><th scope="col">"Incremental" recorded, with zero SpeedWorkers effect</th></tr></thead><tbody>
    <tr><th scope="row">September</th><td>139.4M</td><td class="claim">148.1M</td><td class="bad">−8.7M</td></tr>
    <tr><th scope="row">October</th><td>147.5M</td><td class="claim">161.2M</td><td class="bad">−13.7M</td></tr>
    <tr><th scope="row">November</th><td>147.6M</td><td class="claim">175.1M</td><td class="bad">−27.5M</td></tr>
    <tr><th scope="row">December (full month)</th><td>156.6M</td><td class="claim">208.8M</td><td class="bad">−52.2M</td></tr>
    <tr class="total"><th scope="row">Sep 1 – Dec 20 (measurement window)</th><td>535.6M</td><td>619.1M</td><td class="bad">−83.5M</td></tr>
  </tbody></table>
  <div class="kpis" style="margin-top:22px">
    <div><div class="k">Deficit before we start</div><div class="n bad">−84M</div><p>Visits the contract would record as "lost" over the measurement window if SpeedWorkers did nothing and Walmart's traffic simply followed its trend. Counting all of September: −102M.</p></div>
    <div><div class="k">Walmart's stated threshold</div><div class="n claim">45.3M</div><p>Cumulative incremental visits by Dec 20. The baseline deficit alone is 1.8–2.3× this number.</p></div>
    <div><div class="k">Effective threshold</div><div class="n bad">~129M</div><p>What SpeedWorkers would actually have to generate for the contract to record 45.3M. Our high case: 31M (Sep 1) · 20M (Sep 24).</p></div>
  </div>
  <div class="callout"><p><b>The baseline error is larger than the entire goal.</b> Whether the pilot "passes" is decided almost entirely by the baseline, not by SpeedWorkers. A pilot that works perfectly — deployment healthy, render timeouts gone, indexation moving — still reads as a large negative number against Annex A. That is the failure mode Frank's framework was built to prevent, and it is exactly what this Annex reintroduces.</p></div>
  <p class="src">"On trend" = Sep–Dec 2025 actuals × (1 − 10.8%) for Google, Bing flat, at 2.252 visits per click, plus flat AI visits. Using the recent −17.1% trend the deficit is ~120M.</p>
  {footer(5)}
</section>

<!-- 6 · goals vs model -->
<section class="pg">
  <div class="num">Angle 5 · The goals against our own model</div>
  <h1>No tier of our forecast reaches any of Walmart's checkpoints at any launch date.</h1>
  <p class="lead prose">Frank's model reproduces the addendum's figures exactly. We re-ran it at a Sep 1, Sep 17 and Sep 24 launch, converted its clicks to visits at Walmart's own ratio, and added its AI-visit series — Walmart's unit and Walmart's channel definition.</p>
  <div class="legend"><span class="s-claim dash">Walmart's §16.4 goals</span><span class="s-t1">Our high case, launch Sep 1</span><span class="s-t2">High case, Sep 17</span><span class="s-t3">High case, Sep 24</span><span class="s-t3 dash">Low case (contract tier), Sep 24</span></div>
  <figure>{c_cum}</figure>
  <table><thead><tr><th scope="col">Cumulative incremental visits</th><th scope="col">Sep 30</th><th scope="col">Oct 31</th><th scope="col">Nov 30</th><th scope="col">Dec 20</th><th scope="col">Goal ÷ ours</th></tr></thead><tbody>
    <tr><th scope="row">Walmart's goal</th><td class="claim">8.7M</td><td class="claim">18.4M</td><td class="claim">30.9M</td><td class="claim">45.3M</td><td>—</td></tr>
    <tr><th scope="row">Our high case · launch Sep 1</th><td>2.6M</td><td>9.7M</td><td>21.0M</td><td>31.3M</td><td class="bad">1.4×</td></tr>
    <tr><th scope="row">Our high case · launch Sep 24</th><td>0.3M</td><td>4.0M</td><td>12.0M</td><td>20.3M</td><td class="bad">2.2×</td></tr>
    <tr><th scope="row">Our mid case · launch Sep 24</th><td>0.1M</td><td>1.5M</td><td>4.8M</td><td>8.5M</td><td class="bad">5.3×</td></tr>
    <tr><th scope="row">Contract low tier · launch Sep 24</th><td>0.01M</td><td>0.2M</td><td>0.7M</td><td>1.7M</td><td class="bad">27×</td></tr>
  </tbody></table>
  <div class="two">
    <div><p><b>The September checkpoint is impossible on any date.</b> 8.7M by Sep 30 means more incremental visits in the first 6–13 days of serving than our high case earns by Halloween. Month one of any deployment runs at 2–20% of full pace while search engines recrawl.</p></div>
    <div><p><b>The launch slip also loses the Full Scale gate.</b> 80% of pages must be served by Sep 30. At 250 URLs/s that is 40% on a Sep 17 launch and 18% on Sep 24. Adjustment Days relieve thresholds; nothing in the SOW restores a missed gate. Even relieved for the slip, 45.3M becomes 22.8M — still above our high case.</p></div>
  </div>
  {footer(6)}
</section>

<!-- 7 · what the goals represent -->
<section class="pg">
  <div class="num">Angle 6 · What 45.3M actually represents</div>
  <h1>They are asking for a year of best-case growth in twelve weeks, against a falling tide.</h1>
  <p class="lead prose">Three ways to size the ask, all on Walmart's own numbers.</p>
  <div class="kpis" style="margin-top:20px">
    <div><div class="k">As a lift on their whole organic base</div><div class="n claim">+10.6%</div><p>45.3M incremental visits on the ~429M organic + AI visits Walmart's trend gives for Sep 24 – Dec 20. In one quarter, during ramp-up, on a channel where SpeedWorkers touches only the non-branded 6%.</p></div>
    <div><div class="k">Against our annual high case</div><div class="n bad">≈ 1 year</div><p>At <i>full</i> coverage for a <i>full year</i>, our model lifts the base +4.0% (low), +7.5% (mid), +11.1% (high). Walmart's quarter-long ask equals the high case's entire annual output.</p></div>
    <div><div class="k">Against their decline</div><div class="n bad">71%</div><p>Walmart's Sep–Dec organic decline at −10.8% is ~63M visits. The goal asks the pilot to reverse 71% of a year's decline in one quarter. Our high case reverses 49% at a Sep 1 launch; the low tier, 5%.</p></div>
  </div>
  <h2>Put another way</h2>
  <table><thead><tr><th scope="col"></th><th scope="col">Walmart's own trend</th><th scope="col">Annex A implies</th><th scope="col">45.3M goal implies</th></tr></thead><tbody>
    <tr><th scope="row">Organic visits, Sep–Dec 2026 vs 2025</th><td class="bad">−11% (search) · recent −17%</td><td class="claim">+6% (search portion)</td><td>—</td></tr>
    <tr><th scope="row">Required swing vs trend</th><td>—</td><td class="claim">≈ 17 points</td><td class="claim">≈ 8–11 points more, on top</td></tr>
    <tr><th scope="row">What our model says the pilot moves the trend by</th><td colspan="3">Low ≈ 0.6 points · High ≈ 5 points, exiting the window at 40–90% adoption</td></tr>
  </tbody></table>
  <div class="callout"><p><b>The honest framing.</b> The pilot can succeed as a proof of mechanism — and Walmart's organic traffic can still be down year over year in December. Frank's framework was designed so that this is measured fairly against the trend without Botify. Annex A and §16.4 replace that with a baseline that assumes growth and a goal that assumes a year's work in a quarter.</p></div>
  <p class="src">Base in the window: Sep–Dec 2025 actuals on trend, pro-rated to Sep 24 – Dec 20. Model annual lifts from forecast.py annual_targets() on a 757.6M-click combined base. Decline in visits = 28.1M Google clicks × 2.252.</p>
  {footer(7)}
</section>

<!-- 8 · recommendation -->
<section class="pg">
  <div class="num">What we recommend</div>
  <h1>Do not sign Annex A or §16.4 as drafted. Ask four questions and propose the baseline we already built.</h1>
  <ol class="asks">
    <li><b>Ask for the Annex A worksheet.</b> Which base months, which year-over-year rate, and for which channel. Their own Search Console says −10.8%; the Annex implies +6%. If the curve came from all-channel traffic, it is the wrong channel for an organic pilot.</li>
    <li><b>Ask where the September-to-December curve comes from.</b> Their organic search does 1.13 Sep→Dec; the Annex does 1.41. This single question accounts for most of the 100M.</li>
    <li><b>Propose the countersigned baseline Frank already built.</b> Walmart's own organic + AI visits for 1 Sep – 20 Dec 2025 from their system of record, grown by the measured trend, frozen before go-live. Better still, the URL-hash holdout Frank is confirming with engineering: with a control group the projected baseline stops mattering.</li>
    <li><b>Re-anchor the goals to the go-live date and to our model's tiers.</b> Checkpoints launch-relative, the Target Full Scale Date moving with go-live, and the threshold set at the low tier the addendum already names — or Walmart states which tier of our forecast they believe they are signing. The 45.3M sits close to the original deck's high case, a figure we have since restated 30–40% lower.</li>
  </ol>
  <div class="two">
    <div><h2>What would change this reading</h2><ul>
      <li>Walmart analytics showing organic + AI visits Sep–Dec 2025 materially above 2.25× our click archive.</li>
      <li>A Walmart-side organic seasonal history with a Dec/Sep ratio near 1.4. Nothing in Search Console or Bing looks like that in either year we hold.</li>
      <li>Evidence the 2026 decline has reversed since 9 August. July was the worst reading in the series.</li>
    </ul></div>
    <div><h2>Caveats we carry openly</h2><ul>
      <li>Visits-per-click rests on two scorecard weeks in May; we used the higher, which favours Walmart.</li>
      <li>AI visits are held flat at 1.45M/week; the last reading was falling 19% week on week.</li>
      <li>Our model's own open items (indexation dial, anonymized attribution, unverified AOV/CR) bear on revenue, not on the visit figures here. The high case is the model's ceiling, not a claim.</li>
    </ul></div>
  </div>
  <p class="src">Sources: Google Search Console (walmart.com US/Web, 664 days to 9 Aug 2026); Bing Webmaster Tools (514 days to 8 Aug 2026); Walmart Agentic Commerce Scorecards W16–W17 FY27; Frank Vitovitch, Walmart Pilot Measurement Framework (forecast.py, STATE.md, correction memo, 13 Aug 2026); Annex A and §16.4 as received from Walmart, September 2026. Reproducible from the Botify repo: analysis/baseline_check.py and analysis/model/goals_check.py.</p>
  {footer(8)}
</section>
</body></html>'''
open(OUT_HTML, 'w').write(HTML); print(OUT_HTML, len(HTML))

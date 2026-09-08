from charts import *
OUT = '/home/user/Botify/analysis/walmart-pilot-brief.html'
WM=[148.1,161.2,175.1,208.8]; FLAT=[154.4,163.4,163.4,173.2]; MEAS=[139.4,147.5,147.6,156.6]; REC=[126.5,134.0,134.1,142.4]
c_yoy = yoy_bars(H=235)
c_base = lines([("Walmart's Annex A baseline", WM, "s-claim", False), ("If the decline stopped today", FLAT, "s-t1", False),
                ("Their 12-month trend, −10.8%", MEAS, "s-t2", False), ("Their last 3 months, −20%", REC, "s-t3", False)],
               115, 215, [120, 140, 160, 180, 200], H=205, title="Monthly organic + AI visits, Sep–Dec 2026")
c_cum = cum_chart(H=190)
STYLE = open('/home/user/Botify/analysis/walmart-pilot-exec-brief.html').read()
STYLE = STYLE[STYLE.index('<style>'):STYLE.index('</style>')+8]
STYLE = STYLE.replace('</style>', '.bar.partial{fill-opacity:.45} .grid3{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:10px} .mini th,.mini td{padding:4.5px 8px;font-size:9.3pt} .mini{margin-top:8px} .note{font-size:9pt;color:var(--ink2);margin-top:8px} h1{font-size:24pt} .kpis .n{font-size:26pt} .callout p{font-size:10pt} .pg p.lead{font-size:11pt;margin-top:8px} .pg .kpis{margin-top:14px} figure{margin-top:8px} .grid3{margin-top:6px} .note{margin-top:6px}</style>')
def footer(n): return f'<div class="foot"><span>Botify · Walmart SpeedWorkers pilot · Internal</span><span>Annex A baseline &amp; §16.4 goals — {n} / 3</span></div>'

HTML = f'''<!doctype html><html><head><meta charset="utf-8"><title>Walmart Pilot — Baseline &amp; Goals</title>{STYLE}</head><body>
<section class="pg">
  <div class="eyebrow"><span>Botify · Walmart SpeedWorkers pilot</span><span class="tag">Internal — executive brief</span><span>8 September 2026</span></div>
  <h1 style="margin-top:16px">Walmart's proposed baseline and goals are far outside what their own data supports.</h1>
  <p class="lead prose">Walmart's organic search traffic has fallen year over year for ten straight months and the decline is steepening. Their Annex A baseline contains none of that decline. Their §16.4 goal sits above the most optimistic outcome our model produces at any launch date.</p>
  <div class="kpis">
    <div><div class="k">Their trend · Aug 2026 vs Aug 2025</div><div class="n bad">−23.4%</div><p>Google clicks, walmart.com. Ten consecutive months down; the last three average −20%. First five days of September: −22%.</p></div>
    <div><div class="k">Baseline overstatement · Sep–Dec</div><div class="n claim">+102M</div><p>Annex A says 693M visits. Their own run-rate, seasonality and 12-month trend give 591M. On the last-3-month trend: 537M, a 156M gap.</p></div>
    <div><div class="k">Goal vs our most optimistic case</div><div class="n bad">1.4–2.2×</div><p>45.3M incremental visits by Dec 20. Our <i>high</i> case delivers 31M (Sep 1 launch) or 20M (Sep 24). The contract's low tier: 2–3M.</p></div>
  </div>
  <figure>{c_yoy}<figcaption><b>Google clicks, year over year, by month — Walmart's own Search Console data.</b> Impressions are up over the same period, so demand is not falling; Walmart is being shown more and clicked less. Nothing here suggests a reversal before December.</figcaption></figure>
  <div class="callout">
    <p><b>Annex A says it applies "a year-over-year run-rate" to current performance.</b> Applied to this channel, that produces a baseline <i>below</i> last year. Annex A instead embeds <b>+6% growth</b> in its search component and a September-to-December climb of 41% — three times what Walmart's organic search has ever done in Q4 (13% last year). September matches their current run-rate with zero decline; the inflation is all in November and December.</p>
  </div>
  {footer(1)}
</section>

<section class="pg">
  <div class="num">The baseline</div>
  <h1>Annex A vs. a baseline built from Walmart's own numbers.</h1>
  <p class="lead prose">Scale from Walmart's scorecards (2.25 visits per search click — the higher of two attested weeks), shape from their Sep–Dec 2025 search history, AI visits held flat. Only the trend varies.</p>
  <div class="legend"><span class="s-claim">Annex A baseline</span><span class="s-t1">If the decline stopped today</span><span class="s-t2">Their 12-month trend, −10.8%</span><span class="s-t3">Their last 3 months, −20%</span></div>
  <figure>{c_base}</figure>
  <div class="grid3">
    <div><table class="mini"><thead><tr><th scope="col">2026</th><th scope="col">Annex A</th><th scope="col">12-mo trend</th><th scope="col">Gap</th></tr></thead><tbody>
      <tr><th scope="row">Sep</th><td class="claim">148.1M</td><td>139.4M</td><td>+6%</td></tr>
      <tr><th scope="row">Oct</th><td class="claim">161.2M</td><td>147.5M</td><td>+9%</td></tr>
      <tr><th scope="row">Nov</th><td class="claim">175.1M</td><td>147.6M</td><td class="bad">+19%</td></tr>
      <tr><th scope="row">Dec</th><td class="claim">208.8M</td><td>156.6M</td><td class="bad">+33%</td></tr>
      <tr class="total"><th scope="row">Sep–Dec</th><td>693.2M</td><td>591.1M</td><td class="bad">+17%</td></tr>
    </tbody></table></div>
    <div><table class="mini"><thead><tr><th scope="col">Holiday shape</th><th scope="col">Annex A</th><th scope="col">Their search '25</th><th scope="col">'24</th></tr></thead><tbody>
      <tr><th scope="row">Dec ÷ Nov</th><td class="claim">1.19</td><td class="teal">1.06</td><td class="teal">1.07</td></tr>
      <tr><th scope="row">Dec ÷ Sep</th><td class="claim">1.41</td><td class="teal">1.13</td><td>—</td></tr>
      <tr><th scope="row">Growth embedded, YoY</th><td class="claim">+6%</td><td class="bad">−10.8%</td><td class="bad">−20% recent</td></tr>
      <tr><th scope="row">Visits per click required</th><td class="claim">2.66</td><td colspan="2">2.18–2.25 in their scorecards</td></tr>
    </tbody></table><p class="note">A 41% Q4 climb is what all-channel site traffic does. Organic search at Walmart does 13%, and the surge is branded queries SpeedWorkers doesn't act on.</p></div>
  </div>
  <div class="kpis" style="margin-top:14px">
    <div><div class="k">Recorded before we start</div><div class="n bad">−84M to −133M</div><p>"Incremental" visits the contract would record over Sep 1 – Dec 20 if SpeedWorkers did nothing and Walmart's traffic simply followed its trend (12-month vs last-3-month trend).</p></div>
    <div><div class="k">Walmart's threshold</div><div class="n claim">45.3M</div><p>The baseline deficit alone is 1.8–2.9× the entire goal. Whether the pilot "passes" is decided by the baseline, not by SpeedWorkers.</p></div>
    <div><div class="k">Effective bar</div><div class="n bad">129M–178M</div><p>What SpeedWorkers would actually have to generate for the contract to show 45.3M. Our high case: 31M at Sep 1, 20M at Sep 24.</p></div>
  </div>
  {footer(2)}
</section>

<section class="pg">
  <div class="num">The goals</div>
  <h1>No tier of our forecast reaches any checkpoint at any launch date.</h1>
  <p class="lead prose">Frank's model reproduces the addendum's figures exactly. Re-run at Sep 1, 17 and 24 launches, converted to visits at Walmart's own ratio, with AI visits added.</p>
  <div class="legend"><span class="s-claim dash">Walmart's §16.4 goals</span><span class="s-t1">Our high case, launch Sep 1</span><span class="s-t2">High case, Sep 17</span><span class="s-t3">High case, Sep 24</span><span class="s-t3 dash">Low case (contract tier), Sep 24</span></div>
  <figure>{c_cum}</figure>
  <table class="mini"><thead><tr><th scope="col">Cumulative incremental visits</th><th scope="col">Sep 30</th><th scope="col">Oct 31</th><th scope="col">Nov 30</th><th scope="col">Dec 20</th><th scope="col">Goal ÷ ours</th></tr></thead><tbody>
    <tr><th scope="row">Walmart's goal</th><td class="claim">8.7M</td><td class="claim">18.4M</td><td class="claim">30.9M</td><td class="claim">45.3M</td><td>—</td></tr>
    <tr><th scope="row">Our high case · launch Sep 1</th><td>2.6M</td><td>9.7M</td><td>21.0M</td><td>31.3M</td><td class="bad">1.4×</td></tr>
    <tr><th scope="row">Our high case · launch Sep 24</th><td>0.3M</td><td>4.0M</td><td>12.0M</td><td>20.3M</td><td class="bad">2.2×</td></tr>
    <tr><th scope="row">Our mid case · launch Sep 24</th><td>0.1M</td><td>1.5M</td><td>4.8M</td><td>8.5M</td><td class="bad">5.3×</td></tr>
    <tr><th scope="row">Contract low tier · launch Sep 24</th><td>0.01M</td><td>0.2M</td><td>0.7M</td><td>1.7M</td><td class="bad">27×</td></tr>
  </tbody></table>
  <div class="grid3">
    <div><p class="note"><b>The September checkpoint is impossible on any date.</b> 8.7M by Sep 30 is more than our high case earns by Halloween; month one of any deployment runs at 2–20% of full pace while engines recrawl. <b>The launch slip also loses the Full Scale gate</b> (80% served by Sep 30): 40% on a Sep 17 launch, 18% on Sep 24. Adjustment Days relieve thresholds but do not restore a missed gate — and even relieved, 45.3M becomes 22.8M, still above our high case.</p></div>
    <div><p class="note"><b>As growth:</b> 45.3M is a <b>+10.6% lift</b> on Walmart's entire organic + AI base in twelve weeks, during ramp-up, touching only the non-branded 6% of that base. At full coverage for a full year our model lifts the base +4% (low), +7.5% (mid), +11% (high). The ask equals the high case's <i>annual</i> output, delivered in one quarter, against a channel losing 11–20% a year.</p></div>
  </div>
  <div class="callout teal">
    <p><b>If 45.3M is actually a 12-month goal (Matt Kennedy's framing to Adrian), the number itself becomes reasonable.</b> Over the first twelve months from launch our model produces 22M (low), 71M (mid) and 147M (high) incremental visits — 45.3M sits between low and mid. But the document as written says "by the Measurement Close Date," the interim checkpoints are dated Sep 30 / Oct 31 / Nov 30 and cannot be annual, and the Annex A baseline problem is untouched. It needs to be corrected in the document, not in a text message.</p>
  </div>
  <p class="src">Sources: Google Search Console via Botify (walmart.com US/Web, daily, to 5 Sep 2026) · Bing Webmaster Tools · Walmart scorecards W16–W17 FY27 · Frank Vitovitch, forecast.py (13 Aug 2026) · Annex A and §16.4 as received from Walmart.</p>
  {footer(3)}
</section>
</body></html>'''
open(OUT,'w').write(HTML); print(OUT)

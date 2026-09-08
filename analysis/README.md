# Walmart pilot — Annex A baseline and §16.4 goal check

Pressure-test of the baseline (Annex A) and cumulative-visit goals (§16.4) Walmart proposed
for the SpeedWorkers pilot, against the search data Botify holds on walmart.com and Frank's
projection model. Report: `annex-a-baseline-audit.html`.

```
python3 analysis/baseline_check.py          # Annex A vs run-rate / shape / trend
python3 analysis/model/goals_check.py       # §16.4 goals vs forecast.py at Sep 1 / 17 / 24 launches
```

- `gsc_daily_2026-08-11.json` — Google Search Console, US/Web, day grain, 2024-10-15 → 2026-08-09,
  bucketed nonbrand / brand / anon. Copied from Frank's workspace (`data/raw/gsc_daily/`).
- `model/` — Frank Vitovitch's `forecast.py` and the 11 Aug 2026 snapshots it reads, unchanged,
  plus `goals_check.py`. Source: Drive folder *Walmart Pilot Measurement Framework*.

Headline (8 Sep 2026): Annex A is ~100M visits (+17%) above a baseline built on Walmart's own
scale, shape and measured trend, with the excess concentrated in Nov–Dec; the 45.3M threshold is
1.4–2.2× the model's high case depending on launch date, and 14–27× the governing low tier.

## Executive brief (3 pages)

`Walmart-Pilot-Baseline-and-Goals-Brief.pdf`, built by `build_short.py` + `charts.py` (headless Chromium
print-to-PDF of `walmart-pilot-brief.html`). `yoy.json` and `series.json` carry the chart data;
`gsc_recent_2026-09-05.json` holds the live Aug/Sep 2026 pull from the Botify MCP
(`walmart0/walmart-sw-demo`, `search_console_by_property_flat`, country=usa, search_type=WEB),
which matches Frank's archive to the click on the overlapping months.

Aug 2026 vs Aug 2025: −23.4% · Sep 1–5: −21.7% · last three months: −20.0%.

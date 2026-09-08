# Walmart pilot forecast, rebased on Walmart's reporting

`Walmart-Pilot-Rebase.html` (repo root) is the published artifact. It carries Frank's
SpeedWorkers pilot forecast on two bases, switchable at the top of the page:

- **Walmart reporting** — the DMP exports Walmart judges the pilot on: SEO marketing
  vehicle (daily, 9 Jul 2024 → 7 Sep 2026: Net GMV, Auth Orders, PDP++ visits) and
  the AEO vehicle (daily, 1 May → 7 Sep 2026). Frank's lift levers are applied to
  Walmart's baseline visits and priced at Walmart's own GMV per visit.
- **Botify GSC + BWT** — Frank's model ported verbatim from `framework.html`.
  Reproduces his 13 Aug headline to the digit (1,843,988 / 7,291,533 / 16,325,245
  clicks to 31 Dec; $6.78M / $57.82M; 1,418,146 clicks and $4.52M to 20 Dec).
- **Compare** — both, with the delta.

Tabs: Forecast · Year over year · Data delta (GSC/BWT archive vs Walmart SEO; scorecard
weeks vs Walmart AEO) · Assumptions & questions.

## Build

```
python3 src/build.py ../Walmart-Pilot-Rebase.html
```

`src/payload.json` is generated from the two Excel exports and Frank's
`data/archive/daily.csv` plus the `framework.html` DATA block; the raw exports are not
committed. `part1.html` is markup and CSS, `part2.js` the data access layer and both
models, `part3.js` charts and views.

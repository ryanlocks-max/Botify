"""Pressure-test Walmart's Annex A baseline against the search data we actually hold.

Sources (Frank's projection-model workspace, Drive folder 1ktN8NQHVb8G9QPxbwfeEVZQDksxivemF):
  data/raw/gsc_daily/2026-08-11.json   664 days of GSC, bucketed nonbrand/brand/anon, US/web
  data/raw/bing_daily/2026-08-11-514d.csv + data/derived/bing_2026-08-11.json (BWT walmart-global)
  derive_baseline.py                   Walmart Agentic Commerce Scorecards W16/W17 FY27

The chain has three links, and each one is measured rather than assumed:
  1. R  — visits per click. Calibrated on the two weeks where Walmart states its own
          SEO visit count, so the units question is settled with Walmart's own numbers.
  2. shape — month-to-month seasonality, taken from Walmart's own Sep-Dec search history.
  3. trend — year-over-year, measured on 299 comparable days of Google day-grain data.

Run: python3 analysis/baseline_check.py
"""
import collections, datetime, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GSC = os.path.join(HERE, "gsc_daily_2026-08-11.json")

# Annex A to the Statement of Work, "Baseline Visits"
ANNEX_A = {9: 148_100_000, 10: 161_200_000, 11: 175_100_000, 12: 208_800_000}

# Bing property-total clicks, rebuilt from the BWT pull's own monthly index and 12m total.
# The day-grain CSV agrees; the index is used so the reconstruction is auditable in one line.
BING_TOTAL_12M = 54_161_288                      # 2025-08-01 .. 2026-07-31
BING_SEASONALITY = {8: 1.0717, 9: 0.8802, 10: 0.9940, 11: 1.0709, 12: 1.2273, 1: 1.1521,
                    2: 0.8815, 3: 0.9667, 4: 0.9187, 5: 0.9263, 6: 0.9418, 7: 0.9688}
DAYS_IN_MONTH = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
                 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
BING_MONTH = {m: BING_SEASONALITY[m] * (BING_TOTAL_12M / 365.0) * DAYS_IN_MONTH[m]
              for m in range(1, 13)}

# Walmart's own attested SEO visit levels. Each scorecard states AI visits and AI's share
# of SEO visits in the same sentence, so SEO visits fall out of a ratio inside one basis.
SCORECARDS = [
    ("W16 FY27", "2026-05-17", 978_749, 1_600_000, 0.053),   # bing clicks, AI visits (3D), share
    ("W17 FY27", "2026-05-24", 926_709, 1_296_000, 0.046),
]

# Botify's own goal to the Dec 20 measurement close, in Google non-branded clicks (forecast.py)
GOALS = {"low": 1_418_146, "mid": 5_980_799, "high": 13_653_665}

# AI-assistant visits. Walmart says Annex A "Visits" include them. Two scorecard weeks
# (W16 1.600M, W17 1.296M, 3-day basis) -> mean 1.448M/wk. No seasonal history exists and
# the last reading was falling (-19% WoW, "decline continued"), so a flat 1.448M/wk is the
# generous assumption, not the cautious one.
AI_WEEKLY = 1_448_000

# Measured Google year-over-year, 299 comparable days from the day-grain archive
TREND_MEASURED = -0.108      # full comparable window
TREND_RECENT = -0.171        # May-Jul 2026, the last three months


def google_daily():
    rows = json.load(open(GSC))["results"]
    month, day = collections.Counter(), collections.Counter()
    for r in rows:
        month[r["d"][:7]] += r["clicks"]
        day[r["d"]] += r["clicks"]
    return month, day


def week(day, start):
    d0 = datetime.date.fromisoformat(start)
    return sum(day[(d0 + datetime.timedelta(days=i)).isoformat()] for i in range(7))


def calibrate_R(day):
    """Visits per click, from the only two weeks where Walmart states both sides."""
    out = []
    for label, start, bing, ai_visits, ai_share in SCORECARDS:
        seo_visits = ai_visits / ai_share
        clicks = week(day, start) + bing
        out.append((label, start, seo_visits, clicks, seo_visits / clicks))
    return out


def main():
    gmonth, gday = google_daily()
    anchors = calibrate_R(gday)

    print("1. R — visits per click, from Walmart's own scorecards")
    for label, start, visits, clicks, r in anchors:
        print(f"   {label}  wk of {start}   SEO visits {visits:>12,.0f}"
              f"   clicks {clicks:>10,}   R {r:.3f}")
    R = max(a[4] for a in anchors)     # the higher ratio is the one generous to Walmart
    print(f"   -> R = {R:.3f}  (higher of the two; a higher R makes Annex A look better)\n")

    g25 = {m: gmonth[f"2025-{m:02d}"] for m in (9, 10, 11, 12)}
    b25 = {m: BING_MONTH[m] for m in (9, 10, 11, 12)}

    print("2 & 3. Sep-Dec 2026 projected visits (search x R + flat AI) — Walmart's own shape, three trends")
    print(f"   {'':<5}{'Annex A':>12}{'flat YoY':>12}{'-10.8%':>12}{'-17.1%':>12}{'A vs flat':>12}")
    tot = dict(a=0.0, flat=0.0, meas=0.0, rec=0.0)
    for m in (9, 10, 11, 12):
        ai = AI_WEEKLY / 7 * DAYS_IN_MONTH[m]
        flat = (g25[m] + b25[m]) * R + ai
        meas = (g25[m] * (1 + TREND_MEASURED) + b25[m]) * R + ai
        rec = (g25[m] * (1 + TREND_RECENT) + b25[m]) * R + ai
        tot["a"] += ANNEX_A[m]; tot["flat"] += flat; tot["meas"] += meas; tot["rec"] += rec
        print(f"   {m:<5}{ANNEX_A[m]/1e6:>11.1f}M{flat/1e6:>11.1f}M{meas/1e6:>11.1f}M"
              f"{rec/1e6:>11.1f}M{ANNEX_A[m]/flat-1:>+11.1%}")
    print(f"   {'TOT':<5}{tot['a']/1e6:>11.1f}M{tot['flat']/1e6:>11.1f}M{tot['meas']/1e6:>11.1f}M"
          f"{tot['rec']/1e6:>11.1f}M{tot['a']/tot['flat']-1:>+11.1%}")

    print(f"\n   Annex A vs measured trend: {tot['a']/tot['meas']-1:+.1%}"
          f"  ({(tot['a']-tot['meas'])/1e6:,.0f}M visits of headroom)")
    print(f"   Annex A vs recent trend  : {tot['a']/tot['rec']-1:+.1%}"
          f"  ({(tot['a']-tot['rec'])/1e6:,.0f}M)")

    actual25 = sum(g25.values()) + sum(b25.values())
    ai_win = sum(AI_WEEKLY / 7 * DAYS_IN_MONTH[m] for m in (9, 10, 11, 12))
    print(f"\n   Growth embedded in Annex A: {((tot['a']-ai_win)/R)/actual25-1:+.1%} year over year"
          f" on the search part, against a channel measured at {TREND_MEASURED:+.1%}")
    print(f"   R that Annex A would require: {(tot['a']-ai_win)/(sum(g25.values())*(1+TREND_MEASURED)+sum(b25.values())):.2f}"
          f"  vs {min(a[4] for a in anchors):.2f}-{R:.2f} attested")

    print("\n4. Shape test — independent of R entirely (per-day, Sep = 100)")
    base_a, base_c = ANNEX_A[9] / 30, (g25[9] + b25[9]) / 30
    for m in (9, 10, 11, 12):
        a = (ANNEX_A[m] / DAYS_IN_MONTH[m]) / base_a * 100
        c = ((g25[m] + b25[m]) / DAYS_IN_MONTH[m]) / base_c * 100
        print(f"   month {m:<3} Annex A {a:>6.1f}   Walmart's own search actuals {c:>6.1f}")
    print(f"   Dec/Nov — Annex A {ANNEX_A[12]/ANNEX_A[11]:.3f}"
          f"   2025 actual {(g25[12]+b25[12])/(g25[11]+b25[11]):.3f}"
          f"   2024 actual {gmonth['2024-12']/gmonth['2024-11']:.3f}")

    print("\n5. The gap against the prize")
    for k, v in GOALS.items():
        print(f"   Botify goal ({k}) to Dec 20: {v:>11,} clicks = {v*R/1e6:>6.2f}M visits"
              f"   gap is {(tot['a']-tot['meas'])/(v*R):>5.1f}x it")


if __name__ == "__main__":
    main()

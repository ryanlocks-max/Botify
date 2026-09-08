"""Walmart's proposed §16.4 goals, tested against Frank's forecast.py.

Walmart proposes cumulative incremental VISITS (organic search + AI assistants):
  by Sep 30: 8.7M   by Oct 31: 18.4M   by Nov 30: 30.9M   final threshold: 45.3M
forecast.py produces incremental CLICKS (Google + Bing, non-branded) and incremental AI
visits separately. Clicks are converted to visits at R = 2.252 (Walmart's own SEO visits
per Google+Bing click, calibrated on scorecard W16 - the higher of the two attested weeks,
i.e. the reading most generous to Walmart). AI visits need no conversion.

  python3 goals_check.py
"""
import datetime as dt
import forecast as f

R = 2.252
WALMART_GOALS = {dt.date(2026, 9, 30): 8_700_000, dt.date(2026, 10, 31): 18_400_000,
                 dt.date(2026, 11, 30): 30_900_000, f.MEASUREMENT_CLOSE: 45_300_000}
LAUNCHES = [dt.date(2026, 9, 1), dt.date(2026, 9, 17), dt.date(2026, 9, 24)]
CLOSE = f.MEASUREMENT_CLOSE


def series_visits(tier, launch):
    """Cumulative incremental visits by date: search clicks x R + AI visits."""
    f.LAUNCH = launch
    search = f.weekly_series("clicks", tier, stride=1, end=CLOSE)
    ai = f.ai_series(tier, stride=1, end=CLOSE)
    ai_by = {d: v for d, v in ai}
    return {d: v * R + ai_by.get(d, 0.0) for d, v in search}, {d: v for d, v in search}, ai_by


def at(series, day):
    """Cumulative value on `day`; zero before launch."""
    keys = [d for d in series if d <= day]
    return series[max(keys)] if keys else 0.0


def main():
    print("Frank's model, converted to Walmart's unit (visits = clicks x %.3f + AI visits)\n" % R)
    print(f"{'launch':<12}{'tier':<6}{'Sep 30':>10}{'Oct 31':>10}{'Nov 30':>10}{'Dec 20':>10}"
          f"{'  search clk':>13}{'  AI visits':>12}")
    results = {}
    for launch in LAUNCHES:
        for tier in f.TIERS:
            vis, clk, ai = series_visits(tier, launch)
            row = [at(vis, d) for d in WALMART_GOALS]
            results[(launch, tier)] = row
            print(f"{launch.isoformat():<12}{tier:<6}" + "".join(f"{v/1e6:>9.2f}M" for v in row)
                  + f"{at(clk, CLOSE)/1e6:>12.2f}M{at(ai, CLOSE)/1e6:>11.2f}M")
        print()
    print(f"{'WALMART':<12}{'goal':<6}" + "".join(f"{v/1e6:>9.2f}M" for v in WALMART_GOALS.values()))

    print("\nWalmart goal as a multiple of Frank's HIGH case (the most optimistic tier)")
    for launch in LAUNCHES:
        hi = results[(launch, "high")]
        print(f"  launch {launch.isoformat()}: " +
              "  ".join(f"{d.strftime('%b %d')} {g/h if h else float('inf'):>5.1f}x"
                        for (d, g), h in zip(WALMART_GOALS.items(), hi)))

    print("\nSame, vs the LOW case (the tier the addendum sets pass/fail on)")
    for launch in LAUNCHES:
        lo = results[(launch, "low")]
        print(f"  launch {launch.isoformat()}: " +
              "  ".join(f"{d.strftime('%b %d')} {g/l if l else float('inf'):>6.1f}x"
                        for (d, g), l in zip(WALMART_GOALS.items(), lo)))

    print("\nFull Scale gate (>=80% of in-scope pages served by Sep 30, 250 URLs/s, 707M pages)")
    for launch in LAUNCHES:
        fs = f.full_scale_check(launch=launch)
        print(f"  launch {launch.isoformat()}: coverage at Sep 30 = {fs['coverage_at_target']:.1%}"
              f"  slack {fs['slack_days']:+.1f} days  -> {'MET' if fs['met'] else 'MISSED'}")

    print("\nIf Walmart's 45.3M were relieved by SOW s7.4 Adjustment Days for a launch slip")
    for launch in LAUNCHES[1:]:
        days = (launch - LAUNCHES[0]).days
        share = f._retention_share(days)
        print(f"  {days} Adjustment Days (launch {launch.isoformat()}): retained {share:.1%}"
              f" -> threshold {45_300_000*share/1e6:.1f}M visits; Frank high case delivers"
              f" {results[(launch,'high')][-1]/1e6:.1f}M, low {results[(launch,'low')][-1]/1e6:.1f}M")

    print("\nWhat R would Frank's high case need to reach 45.3M? (search clicks only)")
    for launch in LAUNCHES:
        f.LAUNCH = launch
        clk = f.weekly_series("clicks", "high", stride=1, end=CLOSE)[-1][1]
        ai = f.ai_series("high", stride=1, end=CLOSE)[-1][1]
        print(f"  launch {launch.isoformat()}: (45.3M - {ai/1e6:.2f}M AI) / {clk/1e6:.2f}M clicks"
              f" = R {(45_300_000-ai)/clk:.2f}   (attested 2.18-2.25)")


if __name__ == "__main__":
    main()

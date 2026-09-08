"""
Walmart pilot forecast — Sept 1 2026 launch, Dec 31 2026 decision.

Levels come from the workbook. Shapes come from live RealKeywords via the Botify
MCP (snapshots/<date>/derived_realkeywords.json). That split is deliberate:
RealKeywords is sampled, so it is reliable for ratios and unreliable for levels.

THE MODEL IS DUPLICATED IN framework.html so the sliders can recompute in the
browser. If you change the arithmetic here, change it there too.

Three things this version fixes:

1. Anonymized queries are their own bucket, not a baked-in gross-up. Botify
   represents them as keyword='n/a'; measured 89.75% of impressions on the live
   US walmart.com property (2026-08-11) and
   keywords=0 in every month. `ANONYMIZED_INCLUSION` is now an explicit control —
   the workbook's buried 0.3 haircut was an implicit 70%.

2. Seasonality is BUCKET-WEIGHTED. The old model applied non-branded seasonality
   to a base that is ~86% anonymized-attributed. Anonymized traffic has almost no
   holiday peak (Nov impressions index 0.94 vs non-branded 1.31), so the old
   shape borrowed a lift most of the base does not have. Weights follow the
   inclusion slider, so changing it changes both the base and its seasonal shape.

3. Anonymized can never reach a keyword target — no keyword text exists. Keyword
   seasonality therefore stays pure non-branded, and the inclusion slider leaves
   keyword figures untouched at every position.
"""
import glob, json, os
from datetime import date, timedelta

# ─────────────── controls ───────────────
LAUNCH, DECISION      = date(2026, 9, 1), date(2026, 12, 31)

# The contract stops counting BEFORE the decision is taken. SOW §4.2 sets a Measurement
# Close Date of 20 December; DECISION is 31 December. Those eleven days are peak season at
# peak coverage — the richest days in the whole window — so a goal set on the DECISION
# horizon overstates what is actually measurable by 23.1% at the low tier (1,843,988 vs
# 1,418,146 clicks), 18.0% at mid and 16.4% at high.
#
# Use MEASUREMENT_CLOSE for anything that becomes a THRESHOLD, a goal or a contractual
# figure. DECISION stays for narrative surfaces — the trajectory chart, the story about
# what the pilot is worth — because those report to the decision, not to the close.
# `goal_horizon()` exists so no call site has to remember which is which.
MEASUREMENT_CLOSE     = date(2026, 12, 20)

RAMP_WEEKS, TRANCHES  = 3, 3
ANONYMIZED_INCLUSION  = 0.70          # workbook parity (its 1 − 0.3 haircut)
GROWTH                = {"low": 0.07, "high": 0.20}
INDEXATION_DIAL       = {"low": 0.25, "high": 0.60}
# The workbook gives a low and a high and nothing between them. A mid band therefore has
# to be DERIVED, and the only defensible derivation is the midpoint of every input in the
# bundle — including the ramp, because the tiers are paired 1:1 and a mid target with an
# aggressive ramp would be exactly the 2x2 the model forbids. It is an interpolation, not
# a third scenario Walmart or the workbook supplied, and it is labelled as such.
TIERS = ("low", "mid", "high")


def _mid(d):
    return dict(d, mid=(d["low"] + d["high"]) / 2)
NEW_PAGE_PERFORMANCE  = 0.25
AOV, CR               = 74.1, 0.043
INCLUDE_BING          = True

# ─────────────── live shapes ───────────────
SNAPSHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "snapshots", "2026-08-11", "derived_realkeywords.json")
with open(SNAPSHOT) as f:
    DERIVED = json.load(f)

BING_SNAP = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "data", "derived", "bing_2026-08-11.json")
with open(BING_SNAP) as f:
    BING = json.load(f)
BING_SEAS = {m: {int(k): v for k, v in d.items()}
             for m, d in BING["seasonality"].items()}

NB_SEAS   = {m: {int(k): v for k, v in d.items()}
             for m, d in DERIVED["seasonality"]["nonbrand"].items()}
ANON_SEAS = {m: {int(k): v for k, v in d.items()}
             for m, d in DERIVED["seasonality"]["anon"].items()}
# live measured bases, used ONLY for the bucket weights (a ratio, not a level)
W_MEASURED = DERIVED["levels"]["nonbrand"]["impressions"]
W_ANON     = DERIVED["anon_attributed_to_nonbrand"]

# ─────────────── live measured levels ───────────────────────────────────────────
# These are READ FROM THE SNAPSHOT, not transcribed. The snapshot is US/WEB scoped
# (snapshots/<date>/derived_realkeywords.json, scope.country = "usa"), which is the
# only correct scope: AOV, CR and RPV are all US figures, so a global impression base
# priced with US economics overstates the result.
#
# THIS WENT WRONG ONCE, ON 2026-08-11. A fresh MCP query was run WITHOUT the country
# filter and its global figures were hardcoded here, over the top of a US-scoped
# baseline. The snapshot's own caveat had already warned about exactly this — "Workbook
# pull used countryFilter=all; this is country=usa. That explains the anonymized delta."
# Global overstated the anonymized bucket by 21.5%, and that bucket is ~60% of the
# annual number. Non-US is 20% of anonymized impressions and 18.6% of all impressions.
# Reading from DERIVED rather than pasting numbers is what stops it recurring.
#
# Caveat that survives the fix: this source is sampled, so it is stronger for ratios
# than for absolute levels. The forecast originally used workbook levels for that
# reason. Live levels are used now by explicit request, and they landed within 4-10%
# of the workbook's — but the sampling limitation is real and is stated in the
# artifact's provenance section.
_L = DERIVED["levels"]
_ALL_IMPR = sum(_L[k]["impressions"] for k in ("nonbrand", "brand", "anon"))
# The share of impressions where Google withholds the query. 89.75% on the US property.
# It was briefly written as 91.2% on 2026-08-11 — that was the GLOBAL figure, the same
# scope error as the levels below. Computed, never typed.
ANON_IMPR_SHARE = _L["anon"]["impressions"] / _ALL_IMPR
MEASURED_NONBRAND_IMPR = DERIVED["levels"]["nonbrand"]["impressions"]   # 2,953,187,750
_NONBRAND_CLICKS       = DERIVED["levels"]["nonbrand"]["clicks"]        # 45,878,716
ANON_ASSIGNED_IMPR     = DERIVED["anon_attributed_to_nonbrand"]         # 25,854,930,116
NONBRAND_CTR           = _NONBRAND_CLICKS / MEASURED_NONBRAND_IMPR      # 1.5535%
# Workbook predecessors, kept so the swap stays auditable:
#   MEASURED_NONBRAND_IMPR 3_097_123_307   ANON_ASSIGNED_IMPR 33_035_399_697
#   NONBRAND_CTR           0.01667490826
BING_TRAFFIC_CLKS      = {"low": 2_674_983,  "high": 7_642_810}    # workbook targets
BING_TRAFFIC_IMPR      = {"low": 387_078_179, "high": 1_105_937_655}
KEYWORDS               = {"low": 34_521, "high": 98_631}

# Bing baseline, MEASURED from data/raw/bing_daily/2026-08-11-514d.csv, trailing 365
# days to 2026-08-08. Not yet wired into a lever — Bing's targets above are still the
# workbook's. Recorded so the Bing lever can be rebased the same way Google now is.
BING_BASE_CLKS_TTM  = 54_004_757
BING_BASE_IMPR_TTM  = 7_912_003_217

# Indexation lever. POOL is CONFIRMED: GSC Page indexing for sc-domain:walmart.com on
# 2026-08-11 reports 273,000,000 indexed and 434,000,000 "Crawled – currently not
# indexed", which is this constant exactly. A further 180,000,000 sit in "Discovered –
# currently not indexed" and are NOT counted here, so this pool is the conservative
# subset of the addressable 614,000,000.
INDEXED_PAGES            = 273_000_000
POOL_CRAWLED_NOT_INDEXED = 434_000_000
# Both per-page rates are now measured non-brand volume ÷ INDEXED_PAGES rather than
# workbook constants. Absolute page counts cancel out of the lever anyway — it reduces
# to clicks × NEW_PAGE_PERFORMANCE × dial × POOL/INDEXED — so these two only set the
# unit, not the size of the answer.
CLICKS_PER_INDEXED_PAGE  = _NONBRAND_CLICKS / INDEXED_PAGES   # 0.1681; was 0.189
IMPR_PER_INDEXED_PAGE    = MEASURED_NONBRAND_IMPR / INDEXED_PAGES

# Index-coverage counts read off the two webmaster consoles on 2026-08-11. Only
# POOL_CRAWLED_NOT_INDEXED feeds a lever; the rest are recorded so the provenance
# section can state coverage on both engines without anyone retyping a number.
GSC_DISCOVERED_NOT_INDEXED = 180_000_000   # addressable, deliberately NOT in the pool
BING_INDEXED               = 411_000_000   # 1.5x Google's 273M
BING_SITEMAP_URLS          = 790_000_000   # declared across 346 sitemaps
BING_WARNINGS              = 166_000_000   # SEO warnings on indexed URLs — NOT a pool

RPV = AOV * CR

# ─────────────── provenance ─────────────────────────────────────────────────────
# One row per input the projection READS FROM AN OUTSIDE SYSTEM. `grade` is the honest
# evidence level, not a confidence score: measured = read from a system of record over a
# stated window; capture = a number a human read off a console screen on a date;
# reported = the client told us and we cannot audit it.
#
# Adjustable controls are deliberately absent — impression growth, indexation lift, new
# pages earn, cache ramp-up, AOV and CR all live in the flyout, so listing them here
# duplicated them and blurred the point of the section, which is provenance. Removed
# 2026-08-11 by request. They are still visible and still labelled as assumptions in
# the flyout, and the section's closing note points at them.
# Written in CLIENT-READABLE terms per CLAUDE.md — engine and property, never table or
# tool names. Keep the wording plain: this section exists to be checked, not admired.
SOURCES = [
    ("Google Search",
     [("Non-branded impressions",   f"{MEASURED_NONBRAND_IMPR:,}",
       "Google Search Console — walmart.com, all subdomains, Web",
       "12 months to 9 Aug 2026", "measured"),
      ("Non-branded click rate",    f"{NONBRAND_CTR:.4%}",
       "Google Search Console — same property and window",
       "12 months to 9 Aug 2026", "measured"),
      ("Share of queries withheld", f"{ANON_IMPR_SHARE:.2%} of impressions",
       "Google Search Console — apportioned by the non-branded share of named queries",
       "12 months to 9 Aug 2026", "measured"),
      ("Pages indexed",             f"{INDEXED_PAGES:,}",
       "Google Search Console — Page indexing report",
       "11 Aug 2026", "capture"),
      ("Pages crawled, not indexed", f"{POOL_CRAWLED_NOT_INDEXED:,}",
       "Google Search Console — Page indexing report. Drives the indexation lever",
       "11 Aug 2026", "capture"),
      ("Pages found, not yet crawled", f"{GSC_DISCOVERED_NOT_INDEXED:,}",
       "Google Search Console — addressable, but deliberately left out of the forecast",
       "11 Aug 2026", "capture")]),
    ("Bing",
     [("Clicks",      f"{BING_BASE_CLKS_TTM:,}",
       "Bing Webmaster Tools — daily export, refreshed weekly",
       "12 months to 8 Aug 2026", "measured"),
      ("Impressions", f"{BING_BASE_IMPR_TTM:,}",
       "Bing Webmaster Tools — same export",
       "12 months to 8 Aug 2026", "measured"),
      ("Pages indexed", f"{BING_INDEXED:,}",
       "Bing Webmaster Tools — 1.5x Google's count on the same site",
       "11 Aug 2026", "capture"),
      ("URLs declared in sitemaps", f"{BING_SITEMAP_URLS:,}",
       "Bing Webmaster Tools — across 346 sitemaps, so 52% of declared URLs are indexed",
       "11 Aug 2026", "capture")]),
    ("AI assistants",
     [("Weekly visits", "1,448,000",
       "Walmart's weekly Agentic Commerce scorecard, 3-day attribution",
       "FY27 W16–W17, 2 weeks", "reported"),
      ("Revenue per visit", "$8.37",
       "Same scorecards. Second week's 3-day figures derived from the first",
       "FY27 W16–W17, 2 weeks", "reported")]),
]


BASELINE_SNAP = sorted(glob.glob(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "derived", "baseline_*.json")))
with open(BASELINE_SNAP[-1]) as f:
    BASELINE = json.load(f)

# The client's own trajectory — what happens WITHOUT us. Trend is the MEASURED
# year-over-year where a comparable second year exists, and flat where it does not.
# Bing holds 365 days, so it has no second year and gets 0.0 rather than a borrowed
# figure. AI has two weekly observations, which is not a trend.
# Rounded to 0.1pp deliberately: the browser exposes this as a slider whose display
# carries one decimal, and a trend of -10.835% shown as "-10.8%" would mean the two
# tools quietly disagreed on the baseline. The number on screen is the number used.
def _measured_trend(engine):
    """Measured year-over-year where a comparable second period exists, flat where it
    does not — never a borrowed figure. Bing earned a real trend once its archive was
    backfilled to 514 days; before that it had no second year and sat at 0.0."""
    y = BASELINE["engines"].get(engine, {}).get("yoy")
    return round(y["clicks"], 3) if y else 0.0


TREND = {
    "google": _measured_trend("google"),
    "bing":   _measured_trend("bing"),
    "ai":     0.0,     # two weekly scorecards is not a trend
}
# 3D is Walmart's own AEO channel basis and the one every other channel in the scorecard is
# measured on. Verified against the scorecard's reported AOV ($101) and CR (8.3%) — see
# derive_baseline.py. `same_session_mean` is kept as the conservative floor.
AI_BASIS = "three_day_mean"
# None = exactly the months that HAVE a year-over-year counterpart, so the prior-year
# line spans every point on the chart instead of starting partway in. A fixed 12-month
# window looked complete but left Google's first three months (Aug-Oct 2025) with no
# comparison, because the archive's first complete month is Nov 2024. Capped at 12
# regardless: the prior-year series plots last year's value at THIS year's x position, so
# a longer history would show the same months twice.
HISTORY_MONTHS = None
HISTORY_CAP = 12      # observed_mean | observed_latest | workbook_3d
AI_ECOSYSTEM   = 1 / 0.90       # ChatGPT is ~90% of AI referral traffic (Similarweb)
AI_RISK        = 0.80           # applied ONCE. The workbook applies it twice.
AI_LIFT        = {"low": 0.03, "high": 0.06}
# ON by default, by decision. AI still rests on two volatile weekly scorecards — the
# thinnest evidence in the model — and the sum spans two measurement systems, so every
# figure carrying it is labelled and the search-only floor stays alongside it.
INCLUDE_AI     = True

# TWO DIFFERENT RAMPS, and conflating them is how a contract gets misread.
#
#   SERVING     — what share of in-scope pages is actually being served from cache.
#                 Botify controls it, it is a physical fact set by the rollout schedule
#                 and the cache fill rate, and it is NOT tiered: there is one answer.
#                 This is what SOW §4.2's Full Scale gate tests (>= 80%).
#                 See serving_ramp() / serving_coverage().
#
#   ADOPTION    — what share of the full-coverage annual run-rate is actually being
#                 EARNED at a point in time, i.e. how far search engines have recrawled,
#                 reindexed and re-ranked the pages already being served. Uncertain, so
#                 it IS tiered. This is the curve below, and it is what multiplies the
#                 target in weekly_series().
#
# The model's UI called this curve "cache coverage" and printed "exit coverage 40%",
# which reads as a serving figure against a contract that gates on serving >= 80%. It is
# not one. Renamed from RAMP on 2026-08-12 so the two can never be read as one quantity.
#
# Known artifact, small and honest: on days 0-1 the adoption curve is non-zero while
# almost nothing is cached yet, so adoption briefly exceeds serving. Worth ~nothing over
# a 121-day window and left alone rather than papered over.
ADOPTION_CURVE = {"conservative": [0.02, 0.08, 0.22, 0.40],
        "aggressive":   [0.20, 0.45, 0.70, 0.90]}
# Step-by-step midpoint of the two supplied curves.
ADOPTION_CURVE["moderate"] = [(a + b) / 2 for a, b in zip(ADOPTION_CURVE["conservative"], ADOPTION_CURVE["aggressive"])]
PAIR = {"low": "conservative", "mid": "moderate", "high": "aggressive"}   # 1:1, never a 2×2

# Every per-tier input gains its midpoint. Done here, once, so no call site has to know
# which dicts are tiered.
GROWTH             = _mid(GROWTH)
INDEXATION_DIAL    = _mid(INDEXATION_DIAL)
BING_TRAFFIC_CLKS  = _mid(BING_TRAFFIC_CLKS)
BING_TRAFFIC_IMPR  = _mid(BING_TRAFFIC_IMPR)
KEYWORDS           = _mid(KEYWORDS)
AI_LIFT            = _mid(AI_LIFT)


def bucket_weights(inclusion=None):
    """How much of the base is measured vs anonymized-attributed."""
    i = ANONYMIZED_INCLUSION if inclusion is None else inclusion
    anon = W_ANON * i
    total = W_MEASURED + anon
    return (W_MEASURED / total, anon / total) if total else (1.0, 0.0)


def seasonality(inclusion=None):
    """Google shape, bucket-weighted. Keywords stay pure non-branded because the
    anonymized bucket contains none."""
    w_nb, w_an = bucket_weights(inclusion)
    out = {}
    for metric in ("impressions", "clicks"):
        out[metric] = {m: w_nb * NB_SEAS[metric][m] + w_an * ANON_SEAS[metric][m]
                       for m in NB_SEAS[metric]}
    out["keywords"] = dict(NB_SEAS["keywords"])
    return out


def bing_seasonality():
    """Bing's own shape, from its daily property series. Bing is nearly flat on
    impressions (Nov 1.031) — its holiday effect is CTR, not volume — so borrowing
    Google's shape gave Bing a seasonal lift it has not earned."""
    return BING_SEAS


def annual_targets(inclusion=None):
    i = ANONYMIZED_INCLUSION if inclusion is None else inclusion
    base_impr = MEASURED_NONBRAND_IMPR + ANON_ASSIGNED_IMPR * i
    out = {"impressions": {}, "clicks": {}, "keywords": dict(KEYWORDS), "levers": {}}
    for t in TIERS:
        traffic_impr = base_impr * GROWTH[t]
        traffic_clks = traffic_impr * NONBRAND_CTR
        pages    = POOL_CRAWLED_NOT_INDEXED * INDEXATION_DIAL[t]
        idx_clks = pages * CLICKS_PER_INDEXED_PAGE * NEW_PAGE_PERFORMANCE
        idx_impr = pages * IMPR_PER_INDEXED_PAGE   * NEW_PAGE_PERFORMANCE
        # the traffic lever split by where its base came from — this is the
        # defensibility line: how much of the number is measured vs attributed
        measured_share = MEASURED_NONBRAND_IMPR / base_impr if base_impr else 1.0
        out["levers"][t] = {
            "traffic_measured":   traffic_clks * measured_share,
            "traffic_anonymized": traffic_clks * (1 - measured_share),
            "indexation":         idx_clks,
            "bing":               BING_TRAFFIC_CLKS[t] if INCLUDE_BING else 0.0,
        }
        out["clicks"][t]      = sum(out["levers"][t].values())
        out["impressions"][t] = traffic_impr + idx_impr + (
            BING_TRAFFIC_IMPR[t] if INCLUDE_BING else 0)
    return out


def _tranches():
    if RAMP_WEEKS <= 0:
        return [(LAUNCH, 1.0)]
    step = RAMP_WEEKS * 7 / TRANCHES
    return [(LAUNCH + timedelta(days=round(i * step)), 1.0 / TRANCHES)
            for i in range(TRANCHES)]


def adoption_fraction(tier, day, curve=None):
    """Launch-relative monthly step. A tranche contributes nothing before it is live.

    `curve` overrides which ramp the tier gets. Its only use is to isolate how much
    of the low/high spread is the ramp assumption, by running one scenario against
    the other's curve. The scenarios are otherwise paired 1:1 and never crossed.
    """
    return 0.0 if day < 0 else ADOPTION_CURVE[curve or PAIR[tier]][min(day // 30, 3)]


def weekly_series(metric, tier, inclusion=None, engine="both", curve=None,
                  stride=7, end=None):
    """Google and Bing are integrated separately so each carries its own seasonal
    shape, then summed. Keywords are Google-only (no Bing keyword target exists).

    `stride` is the emit interval in days; 7 gives the week-ends this is named for,
    1 gives every day. Charts want 1: the ramp steps are slope discontinuities, so
    the cumulative curve has real corners at them, and a weekly sample smears each
    corner across up to a week.

    `engine` selects which parts to accumulate — "both", "google" or "bing". The
    split is not a new model: it is the same two integrations this function has
    always run, returned separately instead of added. Google's part carries the
    traffic AND indexation levers; Bing's indexation lever is deliberately omitted
    from the model, so Bing is traffic only.
    """
    ann, seas, bseas = annual_targets(inclusion), seasonality(inclusion), bing_seasonality()
    bing_part = 0.0
    if INCLUDE_BING and metric in ("impressions", "clicks") and metric in bseas:
        bing_part = (BING_TRAFFIC_IMPR[tier] if metric == "impressions"
                     else BING_TRAFFIC_CLKS[tier])
    goog_base = (ann[metric][tier] - bing_part) / 365.0
    bing_base = bing_part / 365.0
    if engine == "google":
        bing_base = 0.0
    elif engine == "bing":
        goog_base = 0.0
    stop = end or DECISION
    pts, run, d = [], 0.0, LAUNCH
    while d <= stop:
        ramp = sum(w * adoption_fraction(tier, (d - st).days, curve)
                   for st, w in _tranches())
        g = seas[metric].get(d.month)
        if g:
            run += goog_base * g * ramp
        if bing_base:
            b = bseas[metric].get(d.month)
            if b:
                run += bing_base * b * ramp
        if (d - LAUNCH).days % stride == stride - 1 or d == stop:
            pts.append((d, run))
        d += timedelta(days=1)
    return pts


def cumulative(metric, tier, inclusion=None, engine="both", curve=None):
    return weekly_series(metric, tier, inclusion, engine, curve)[-1][1]


# ─────────────── the client's own trajectory (without us) ───────────────
def monthly_full(engine):
    """Every complete month held for this engine, keyed 'YYYY-MM'."""
    if engine == "ai":
        return {}
    if engine == "combined":
        return BASELINE["combined_monthly_full"]
    return BASELINE["engines"][engine]["monthlyFull"]


def prior_ym(ym):
    return "%04d-%s" % (int(ym[:4]) - 1, ym[5:7])


def yoy_series(engine):
    """Month-by-month year-over-year, oldest first, for every complete month that has a
    complete counterpart twelve months earlier.

    Empty for Bing and therefore for Combined: the ingested Bing pull covers 365 days
    from 2025-08-01, so no Bing month has a prior year to compare against. That is a
    collection gap, not a property of the data — the BWT source holds 514 days from
    2025-03-13, so a re-pull would buy roughly five comparable months.
    """
    md = monthly_full(engine)
    out = []
    for ym in sorted(md):
        p = prior_ym(ym)
        if p not in md:
            continue
        cur, prior = md[ym]["total"], md[p]["total"]
        out.append({"ym": ym, "prior_ym": p, "clicks": cur, "prior_clicks": prior,
                    "change": (cur / prior - 1) if prior else None})
    return out


def yoy_summary(engine, recent=3):
    """The year-to-date comparison, plus whether it is getting better or worse.

    `recent` vs the full period is the whole point: Walmart's Google decline averages
    -11.1% across nine months but the last three run -17.1%, so a single average hides
    an accelerating trend and understates the baseline it is used to project.
    """
    ser = yoy_series(engine)
    if not ser:
        return None
    def agg(rows):
        c = sum(r["clicks"] for r in rows)
        p = sum(r["prior_clicks"] for r in rows)
        return {"clicks": c, "prior_clicks": p, "change": (c / p - 1) if p else None}
    ytd = agg(ser)
    tail = agg(ser[-recent:]) if len(ser) >= recent else None
    return {"months": len(ser), "first": ser[0]["ym"], "last": ser[-1]["ym"],
            "ytd": ytd, "recent": tail, "recentN": recent,
            "accelerating": bool(tail and ytd["change"] is not None
                                 and tail["change"] is not None
                                 and tail["change"] < ytd["change"]),
            "series": ser}


def history(engine, n=None):
    """The trailing COMPLETE months of actual clicks, oldest first.

    Shown before the projection because without it the chart is unreadable: inside a
    Sep-Dec window the line rises on holiday seasonality and looks like growth, when
    the year-over-year trend is down 10.8%. With history the first point is Dec 2025
    actual and the last is Dec 2026 projected — the same calendar month at both ends,
    so the decline is the gap between them rather than something to be asserted.
    """
    if engine == "ai":
        return []      # two weekly scorecards are not a series
    # The FULL archive, not the 365-day window: the window is the widest span both
    # engines cover and is right for totals and seasonality, but it clips Google's
    # history to Aug 2025 onward and with it half the year-over-year comparison.
    md = monthly_full(engine)
    if not md:
        return []
    n = HISTORY_MONTHS if n is None else n
    if n is None:
        ser = yoy_series(engine)
        yms = ([r["ym"] for r in ser][-HISTORY_CAP:] if ser
               else sorted(md)[-HISTORY_CAP:])
    else:
        yms = sorted(md)[-n:]
    return [{"ym": ym, "year": int(ym[:4]), "month": int(ym[5:7]),
             "clicks": md[ym]["total"], "days": md[ym]["days"]} for ym in yms]


def held_monthly(engine, basis=None):
    """The measured monthly actuals, before any trend is applied — what they are
    running at today. The trend effect is baseline minus this, so it has to be
    window-scoped: over a Sep-Dec window the annual total is the wrong denominator.
    """
    if engine == "combined":
        g, b = held_monthly("google", basis), held_monthly("bing", basis)
        return {m: g.get(m, 0.0) + b.get(m, 0.0) for m in range(1, 13)}
    if engine == "ai":
        # basis is threaded explicitly rather than read off the module global, so the
        # JS port (which takes it as a parameter) cannot drift from this one.
        ann = ai_baseline(basis)["all_ai_annual_visits"]
        return {m: ann / 12.0 for m in range(1, 13)}
    mo = BASELINE["engines"][engine]["monthly"]
    return {int(m): v["total"] for m, v in mo.items()}


def baseline_monthly(engine, trend=None, basis=None):
    """Baseline clicks per calendar month, WITHOUT us.

    The measured monthly actual grown once by the engine's own trend. No
    seasonality index is applied on top: the actual monthly series already IS the
    seasonal shape, and multiplying by an index derived from that same series
    would count seasonality twice.
    """
    # Combined first: each engine carries its OWN measured trend, so there is no
    # single combined trend to look up. Averaging them would weight a 7% channel
    # equally with a 93% one.
    if engine == "combined":
        g = baseline_monthly("google", trend, basis)
        b = baseline_monthly("bing", trend, basis)
        return {m: g.get(m, 0.0) + b.get(m, 0.0) for m in range(1, 13)}
    t = TREND[engine] if trend is None else trend
    return {m: v * (1 + t) for m, v in held_monthly(engine, basis).items()}


def ai_baseline(basis=None):
    """Annual AI visits from the weekly scorecard observations.

    n is carried through deliberately. Two volatile weeks is not a baseline, and
    anything reading this figure needs to see how thin it is.
    """
    basis = basis or AI_BASIS
    obs = BASELINE["ai"]["weeks"]
    # basis: <three_day|same_session>_<mean|w16|latest>
    kind, _, which = basis.rpartition("_")
    kind = kind or "three_day"
    if which == "w16":
        rows = [obs[0]]
    elif which == "latest":
        rows = [obs[-1]]
    else:
        rows = obs
    v = sum(w[kind]["visits"] for w in rows) / len(rows)
    g = sum(w[kind]["gmv"] for w in rows) / len(rows)
    n = len(rows)
    openai_annual = v * 52.0
    all_ai = openai_annual * AI_ECOSYSTEM
    attested = all(w[kind].get("attested", True) for w in rows)
    return {"basis": basis, "kind": kind, "n": n, "attested": attested,
            "weekly_visits": v, "weekly_gmv": g,
            "rpv": g / v if v else 0.0,
            "openai_annual_visits": openai_annual,
            "all_ai_annual_visits": all_ai,
            # ONCE. The workbook's "Annual All-AI Visits" row already contains this
            # factor despite being labelled as ecosystem-scaling only, and then
            # haircuts it again — so its lift base is 0.64x, not 0.80x.
            "risk_adjusted_visits": all_ai * AI_RISK}


def ai_series(tier, basis=None, end=None, stride=7):
    """Our incremental AI visits over time.

    NO seasonality is applied: there is no AI seasonal history to measure, and
    borrowing the retail curve would be an assumption dressed as data. The ramp
    does apply — SpeedWorkers serves rendered pages to AI crawlers on the same
    coverage schedule.
    """
    stop = end or DECISION
    base = ai_baseline(basis)["risk_adjusted_visits"] * AI_LIFT[tier] / 365.0
    pts, run, d = [], 0.0, LAUNCH
    while d <= stop:
        run += base * sum(w * adoption_fraction(tier, (d - st).days) for st, w in _tranches())
        if (d - LAUNCH).days % stride == stride - 1 or d == stop:
            pts.append((d, run))
        d += timedelta(days=1)
    return pts


def ai_premium():
    """How much more a Walmart AI visit is worth than an SEO visit.

    Derived from the share figures, not the absolute ones: each scorecard states AI
    as a % of SEO visits AND as a % of SEO GMV in the same sentence, so their ratio
    is basis-independent even where the absolute numbers are contested. W16 gives
    11.2/5.3 = 2.11x, W17 gives 11.0/4.6 = 2.39x.
    """
    rs = [w["gmv_share_of_seo"] / w["visit_share_of_seo"]
          for w in BASELINE["ai"]["weeks"]
          if w.get("visit_share_of_seo") and w.get("gmv_share_of_seo")]
    return sum(rs) / len(rs) if rs else None


def revenue_split(tier, inclusion=None, basis=None, end=None):
    """Search revenue and AI revenue, kept APART.

    They are measured by different systems — our GSC/BWT click archive against
    Walmart's AEO visit channel, whose SEO visit count runs ~2x our click count. The
    two are summed only because Walmart itself reports AEO and SEO as sibling
    channels, and the sum is labelled as spanning two bases wherever it is shown.
    """
    search = weekly_series("clicks", tier, inclusion, "both", None, 7, end)[-1][1] * RPV
    visits = ai_series(tier, basis, end, 7)[-1][1]
    ai_rev = visits * ai_baseline(basis)["rpv"]
    return {"search": search, "ai": ai_rev, "ai_visits": visits,
            "total": search + (ai_rev if INCLUDE_AI else 0.0)}


def ai_annual(tier, basis=None):
    """Annual incremental AI visits and revenue at FULL coverage — the same basis the
    search levers are quoted on in annual_targets(), so the two can sit in one table."""
    b = ai_baseline(basis)
    visits = b["risk_adjusted_visits"] * AI_LIFT[tier]
    return {"visits": visits, "revenue": visits * b["rpv"], "rpv": b["rpv"]}


def lift_denominators(engine="google", inclusion=None):
    """The three possible denominators for "how big is our lift", and why only one is
    honest.

    The trajectory chart plots the lift against the client's PROPERTY TOTAL, because
    that is the only scope Bing has data for and the only one where a combined figure is
    legitimate. But the lift does not act on the property total — it acts on non-branded
    traffic including the anonymized share the forecast claims. Quoting the lift as a
    share of the total understates it; quoting it against named non-branded only
    overstates it absurdly. Both numbers are reported so neither can be used alone.
    """
    i = ANONYMIZED_INCLUSION if inclusion is None else inclusion
    eng = BASELINE["engines"].get(engine, {})
    total = eng.get("totals", {}).get("clicks", 0)
    named_nb = BASELINE["google_nonbrand"]["totals"]["clicks"] if engine == "google" else None
    anon = (BASELINE["engines"]["google"].get("anonClicks")
            if engine == "google" else None)
    matched = (named_nb + anon * DERIVED["nonbrand_share_of_named"] * i
               if named_nb is not None and anon is not None else None)
    return {"property_total": total, "named_nonbrand": named_nb, "matched": matched}


def annual_composition(tier, inclusion=None, basis=None):
    """Every component of the annual target on ONE unit — revenue.

    The levers are quoted in clicks and AI in visits, and those do not sum. Revenue
    does, which is the only way a single table can account for all of it. Native
    volume is carried alongside so nothing is silently converted.
    """
    ann = annual_targets(inclusion)
    out = []
    for key, label in (("traffic_measured", "Traffic — measured non-branded"),
                       ("traffic_anonymized", "Traffic — anonymized-attributed"),
                       ("indexation", "Indexation"),
                       ("bing", "Bing")):
        clicks = ann["levers"][tier][key]
        out.append({"key": key, "label": label, "unit": "clicks",
                    "volume": clicks, "revenue": clicks * RPV})
    if INCLUDE_AI:
        a = ai_annual(tier, basis)
        out.append({"key": "ai", "label": "AI assistants", "unit": "visits",
                    "volume": a["visits"], "revenue": a["revenue"]})
    total = sum(r["revenue"] for r in out)
    for r in out:
        r["share"] = r["revenue"] / total if total else 0.0
    return {"rows": out, "total_revenue": total,
            "search_revenue": sum(r["revenue"] for r in out if r["key"] != "ai"),
            "search_clicks": ann["clicks"][tier]}


def revenue_series(tier, component="total", inclusion=None, basis=None,
                   end=None, stride=7):
    """Cumulative revenue in DOLLARS over time, by component.

    Dollars are the one unit search and AI genuinely share. Clicks and visits are not
    comparable — Walmart's visit count runs ~2x our click count — but the money is,
    which is why every revenue surface routes through here rather than each chart
    multiplying its own clicks by its own RPV and quietly omitting AI.

    component: total | search | google | bing | ai
    """
    if component == "ai":
        pts = ai_series(tier, basis, end, stride)
        rpv = ai_baseline(basis)["rpv"]
        return [(d, v * rpv) for d, v in pts]
    if component in ("search", "google", "bing"):
        eng = "both" if component == "search" else component
        pts = weekly_series("clicks", tier, inclusion, eng, None, stride, end)
        return [(d, v * RPV) for d, v in pts]
    if component != "total":
        raise ValueError("unknown component %r" % component)
    search = revenue_series(tier, "search", inclusion, basis, end, stride)
    if not INCLUDE_AI:
        return search
    ai = revenue_series(tier, "ai", inclusion, basis, end, stride)
    # Same launch, end and stride, so the day grids align index for index.
    return [(d, v + ai[i][1]) for i, (d, v) in enumerate(search)]


def revenue_components(tier, inclusion=None, basis=None, end=None):
    """The stack, in the order it is drawn. AI is present only when included, so a
    chart built from this cannot show a band the headline does not count."""
    out = [("google", "Google"), ("bing", "Bing")]
    if INCLUDE_AI:
        out.append(("ai", "AI assistants"))
    return out


def trajectory(engine, tier, trend=None, basis=None):
    """Baseline vs with-Botify, per calendar month, over the PILOT WINDOW.

    Ends at DECISION, not a fixed year: the whole tab reports to one horizon, so a
    trajectory running eight months past the decision date would put the headline
    revenue figure and this chart on different clocks.

    Scope is property TOTAL for search engines. The Botify lift is non-branded
    only, so the deviation is a non-branded gain expressed against a total base —
    which is the honest way round, but it has to be said out loud.
    """
    end = DECISION
    base_mo = baseline_monthly(engine, trend, basis)
    held_mo = held_monthly(engine, basis)
    if engine == "ai":
        daily = ai_series(tier, basis, end, stride=1)
    else:
        eng = {"google": "google", "bing": "bing", "combined": "both"}[engine]
        daily = weekly_series("clicks", tier, None, eng, None, 1, end)
    inc_mo, prev = {}, 0.0
    for d, run in daily:
        inc_mo[d.month] = inc_mo.get(d.month, 0.0) + (run - prev)
        prev = run
    months, cur, seen = [], LAUNCH, set()
    while cur <= end:
        key = (cur.year, cur.month)
        if key not in seen:
            seen.add(key)
            months.append(key)
        cur += timedelta(days=1)
    return [{"year": y, "month": m,
             "held": held_mo.get(m, 0.0),
             "baseline": base_mo.get(m, 0.0),
             "incremental": inc_mo.get(m, 0.0)} for y, m in months]


# ─────────────── contract surface ───────────────────────────────────────────────
# Everything below emits on MEASUREMENT_CLOSE, not DECISION. These are the figures that
# become thresholds in Addendum 1, so they are deliberately separated from the narrative
# functions above — a goal is not the same object as a projection, and the eleven days
# between the two horizons are worth 23.1% of the low tier.

# ─────────────── cache build: the physical constraint on Full Scale ─────────────
# SOW §4.2 defines Full Scale as serving >= 80% of in-scope pages, tested at a fixed Target
# Full Scale Date. That is a THROUGHPUT question, not a modelling one, and the model was
# silent on it until Ryan's review.
#
# IN_SCOPE_PAGES IS NOT PINNED. §4.2 reads "TBD". The three readings differ by more than
# the constraint tolerates: 273M (Google's current index), 707M (index + crawled-not-
# indexed, the honest reading of "full US website"), ~1B (full-site cache). At 250/sec the
# break-even is 783M, so 707M works and 1B does not. Pin this before signature.
IN_SCOPE_PAGES        = 707_000_000
# 250 URLs/sec, confirmed by Frank 2026-08-12. NOT the 50/sec in PLAN.html §05 — that is the
# REFERENCE ACCOUNT's authorised rate, quoted there as a comparable, and both Ryan's review
# and my first pass wrongly treated it as Walmart's ceiling. It concluded Full Scale was
# impossible; at 250/sec it is achievable but tight.
CACHE_FILL_PER_SEC    = 250
FULL_SCALE_THRESHOLD  = 0.80
TARGET_FULL_SCALE     = date(2026, 9, 30)


# ─────────────── the agreement's own schedule, added 2026-08-13 ─────────────────
# Read from Addendum 1 §5.2/§5.3 (checkpoints) and §6.1 (serving ramp). These are CONTRACT
# FACTS, not model outputs, and they exist so the roadmap can show the dates Walmart is
# actually measured on instead of the round day-counts we invented.
#
# DO NOT WIRE THESE INTO THE FORECAST. §6.1's percentages are SERVING coverage — the share of
# in-scope pages being served, a physical fact of the rollout. ADOPTION_CURVE is a different
# quantity: how much of the benefit has arrived. The two read 88.6% and 2.0% on the same date
# (see STATE §6d), and the signed thresholds in §5.3 were generated by THIS model's adoption
# curve. Feeding the serving schedule into the ramp would move the model's outputs away from
# the numbers the addendum quotes.
#
# Checkpoints are fixed calendar dates — the agreement ties them to month ends and fixes the
# Measurement Close. Tranches are LAUNCH-RELATIVE, because T1 is the Go-Live Date, so a launch
# slip moves them (§6.3 shifts them again if the authorized fill rate is lower).
CHECKPOINTS = [date(2026, 9, 30), date(2026, 10, 31), date(2026, 11, 30)]

# (days after go-live, serving coverage, label). Values in the addendum are bracketed, meaning
# proposed and subject to confirmation at the Baseline Freeze — carried through as provisional.
SERVING_RAMP = [
    (0,  0.15, "T1"),
    (7,  0.40, "T2"),
    (14, 0.60, "T3"),
    (21, 0.80, "T4"),      # Full Scale threshold; determination window opens here
    (44, 0.975, "T5"),     # addendum says [95-100]%; see SERVING_RAMP_DISPLAY for T5
    (60, 1.00, "Cache complete"),   # before the Holiday Freeze Period begins 1 Nov
]
SERVING_RAMP_PROVISIONAL = True
# Where the addendum gives a RANGE rather than a value, the surface shows the range. The
# midpoint above exists so the schedule sorts and compares numerically; rendering it as "98%"
# claimed a precision the document does not have.
SERVING_RAMP_DISPLAY = {"T5": "95\u2013100%"}

# SOW §6. No configuration changes without Walmart's written approval, and it covers two of the
# four pilot months including peak. Fixed calendar dates, not launch-relative.
HOLIDAY_FREEZE = (date(2026, 11, 1), date(2027, 1, 10))


def cache_fill_per_day(rate=None):
    return (rate or CACHE_FILL_PER_SEC) * 86400


def serving_coverage(as_of, launch=None, rate=None, pages=None):
    """Share of in-scope pages physically in cache by `as_of`.

    Linear at a sustained rate, which is OPTIMISTIC: it assumes full throughput from hour
    one, no failed fetches and no re-fetch of churned pages. Treat the margin it reports
    as a ceiling, not an expectation.
    """
    d = (as_of - (launch or LAUNCH)).days
    if d < 0:
        return 0.0
    return min(1.0, cache_fill_per_day(rate) * d / (pages or IN_SCOPE_PAGES))


def full_scale_check(launch=None, rate=None, pages=None, target=None):
    """Is Full Scale reachable by the Target Full Scale Date, and by how much?

    The margin is in DAYS, because that is the unit the risk arrives in — launch slipping,
    a hold, a late dependency. A negative margin means the gate cannot be met at all.
    """
    launch = launch or LAUNCH
    target = target or TARGET_FULL_SCALE
    pages = pages or IN_SCOPE_PAGES
    need_days = FULL_SCALE_THRESHOLD * pages / cache_fill_per_day(rate)
    have_days = (target - launch).days
    return {"coverage_at_target": serving_coverage(target, launch, rate, pages),
            "days_needed": need_days, "days_available": have_days,
            "slack_days": have_days - need_days,
            "met": serving_coverage(target, launch, rate, pages) >= FULL_SCALE_THRESHOLD}


def launch_slip_sensitivity(max_slip=10, rate=None, pages=None, launch=None):
    """What each day of launch slip costs, on both mechanisms at once.

    A slip does two independent things and only one of them is compensated:
      * it eats cache-fill days against a FIXED Target Full Scale Date  -> a CLIFF, and
        §7.4 Adjustment Days do not restore a missed gate, only the thresholds;
      * it shortens the measurement window                             -> a slope, which
        Adjustment Days do relieve.
    Printing them together is the point: the goal relief can look adequate while the gate
    has already been lost.
    """
    # `launch` is explicit rather than read off the module global, because the browser has
    # no global to read — it has S.launch — and verify_parity.py mutates LAUNCH per case.
    # With the global, Python's slip rows followed the case while the JS port's did not,
    # which the suite caught as a 76-day disagreement in slack.
    base = launch or LAUNCH
    rows = []
    for slip in range(0, max_slip + 1):
        lz = base + timedelta(days=slip)
        fs = full_scale_check(launch=lz, rate=rate, pages=pages)
        rows.append({"slip": slip, "launch": lz,
                     "coverage_at_target": fs["coverage_at_target"],
                     "full_scale_met": fs["met"],
                     "slack_days": fs["slack_days"]})
    return rows


def serving_ramp(as_of, launch=None, rate=None, pages=None):
    """Share of in-scope pages being SERVED from cache at `as_of`.

    The contract-facing name for serving_coverage(). This is what Full Scale tests, and
    it is deliberately NOT tiered — how fast the cache fills is a fact, not a scenario.
    Do not confuse with ADOPTION_CURVE, which is how much of the benefit has arrived.
    """
    return serving_coverage(as_of, launch, rate, pages)


def goal_horizon():
    """The date a contractual figure is measured to. One place, so nothing has to
    remember that the contract stops counting eleven days before the decision."""
    return MEASUREMENT_CLOSE


def goal_quantum(tier="low", metric="clicks", inclusion=None):
    """The in-window total for `metric` at the MEASUREMENT CLOSE.

    `low` governs: the addendum sets its pass/fail bar at the conservative bundle, so the
    other tiers are reported as target and stretch rather than as commitments.
    """
    return weekly_series(metric, tier, inclusion, stride=1, end=goal_horizon())[-1][1]


def goal_table(inclusion=None):
    """Every goal-facing figure, per tier, on the close horizon.

    Reproduces the addendum's quantum: 1,418,146 / 5,980,799 / 13,653,665 clicks.
    """
    out = {}
    for t in TIERS:
        out[t] = {m: goal_quantum(t, m, inclusion) for m in ("clicks", "impressions", "keywords")}
        out[t]["revenue"] = revenue_series(t, "search", inclusion, end=goal_horizon())[-1][1]
    return out


# Cumulative Adjustment Days -> the share of the goal that is retained. SOW §7.4 reduces
# thresholds by a flat percentage per Adjustment Day; a flat rate is wrong in both
# directions, because the value of a pilot day is not constant. Day one costs 2.6% of the
# goal, day sixty costs 0.7% — the ramp is convex, so early days are worth far more.
#
# Calibrated by Ryan on the governing LOW tier with launch shifted and the close fixed.
# CAVEAT, and it must travel with the number: the calibration treats every Adjustment Day
# as a launch-shift day, which slightly over-relieves a hold in the MIDDLE of the window.
# That is defensible only because cache staleness and crawl-pattern re-establishment after
# an interruption are not modelled at all — the SOW's 2.5x post-Full-Scale multiplier is
# doing that job, and it has no empirical basis either. The reference account's actuals
# would ground both.
ADJUSTMENT_RETENTION = [(0, 1.000), (7, 0.816), (14, 0.661), (21, 0.533),
                        (30, 0.404), (45, 0.213), (60, 0.115)]


def _retention_share(cumulative_adjustment_days):
    """Share of the original goal surviving `d` Adjustment Days.

    Extracted from adjusted_thresholds() 2026-08-12 so the JS port has the same unit to
    be diffed against — this interpolation now also drives the Deployment tab's slip
    table, and an inline loop cannot be compared to anything.
    """
    d = max(0.0, float(cumulative_adjustment_days))
    pts = ADJUSTMENT_RETENTION
    if d >= pts[-1][0]:
        return pts[-1][1]
    for (d0, s0), (d1, s1) in zip(pts, pts[1:]):
        if d0 <= d <= d1:
            return s0 + (s1 - s0) * ((d - d0) / (d1 - d0)) if d1 > d0 else s0
    return pts[-1][1]


def adjusted_thresholds(cumulative_adjustment_days, inclusion=None):
    """Goal figures after `cumulative_adjustment_days` of Excused Delay.

    Linear interpolation between the calibration points; flat at the last point beyond 60
    days. The SOW requires Adjustment Days reported weekly, so this is what the weekly
    telemetry prints as the adjusted goal.
    """
    d = max(0.0, float(cumulative_adjustment_days))
    share = _retention_share(d)
    base = goal_table(inclusion)
    return {"adjustment_days": d, "retained": share,
            "goals": {t: {k: v * share for k, v in base[t].items()} for t in base}}


def data_payload():
    """The model's inputs as a JSON-ready dict — levels, bucket weights and shapes.

    This is the seam to the browser. `build_framework.py` injects it into
    framework.html so the JS port reads the SAME numbers rather than a
    hand-transcribed copy. Behaviour is duplicated; inputs are not.
    """
    return {
        "snapshot": DERIVED["snapshot_date"],
        "bingSnapshot": BING["snapshot_date"],
        "levels": {
            "measuredNonbrandImpr": MEASURED_NONBRAND_IMPR,
            "anonAssignedImpr": ANON_ASSIGNED_IMPR,
            "nonbrandCtr": NONBRAND_CTR,
            "bingClicks": BING_TRAFFIC_CLKS,
            "bingImpr": BING_TRAFFIC_IMPR,
            "keywords": KEYWORDS,
            "poolCrawledNotIndexed": POOL_CRAWLED_NOT_INDEXED,
            "imprPerIndexedPage": IMPR_PER_INDEXED_PAGE,
        },
        # live measured bases — used ONLY for the bucket weights (a ratio, not a level)
        "weights": {"measured": W_MEASURED, "anon": W_ANON},
        "seas": {
            "nonbrand": {k: {str(m): v for m, v in d.items()} for k, d in NB_SEAS.items()},
            "anon":     {k: {str(m): v for m, v in d.items()} for k, d in ANON_SEAS.items()},
            "bing":     {k: {str(m): v for m, v in d.items()} for k, d in BING_SEAS.items()},
        },
        "ramp": ADOPTION_CURVE,
        # ── the client's own trajectory, for the with-us / without-us view ──
        "trajectory": {
            "window": BASELINE["window"],
            "scope": BASELINE["scope"],
            "endsAt": "decision",
            "historyMonths": HISTORY_MONTHS,
            "history": {e: history(e) for e in ("google", "bing", "ai", "combined")},
            "monthlyFull": {e: monthly_full(e) for e in ("google", "bing", "combined")},
            "yoy": {e: yoy_summary(e) for e in ("google", "bing", "ai", "combined")},
            "engines": {
                "google": {
                    "label": "Google", "trend": TREND["google"],
                    "trendNote": "measured year-over-year, %d comparable days"
                                 % BASELINE["engines"]["google"]["yoy"]["days"],
                    "monthly": {m: v["total"] for m, v in BASELINE["engines"]["google"]["monthly"].items()},
                    "total": BASELINE["engines"]["google"]["totals"]["clicks"],
                    "yoy": BASELINE["engines"]["google"]["yoy"],
                    "scopeNote": "property total — non-branded + branded + anonymized",
                },
                # Bing's note and yoy are DERIVED, not hardcoded. They used to read
                # "flat — only 365 days held, so no comparable second year" with
                # yoy: None, which was true until the archive was backfilled to 514
                # days. After the backfill TREND["bing"] became a measured -4.2% while
                # this note still said flat, so the trajectory contradicted its own
                # slider, and a real year-over-year series was being thrown away.
                # Bing's comparable span is much shorter than Google's, so the note
                # states the day count and lets the reader weigh it.
                "bing": {
                    "label": "Bing", "trend": TREND["bing"],
                    "trendNote": (
                        "measured year-over-year, %d comparable days — a shorter span "
                        "than Google's %d, and it holds no holiday season"
                        % (BASELINE["engines"]["bing"]["yoy"]["days"],
                           BASELINE["engines"]["google"]["yoy"]["days"])
                        if BASELINE["engines"]["bing"].get("yoy")
                        else "flat — no comparable second year is held"),
                    "monthly": {m: v["total"] for m, v in BASELINE["engines"]["bing"]["monthly"].items()},
                    "total": BASELINE["engines"]["bing"]["totals"]["clicks"],
                    "yoy": BASELINE["engines"]["bing"].get("yoy"),
                    "scopeNote": "property total — Bing is not split by brand",
                },
                "ai": {
                    "label": "AI assistants", "trend": TREND["ai"],
                    "trendNote": "flat — two weekly observations is not a trend",
                    "monthly": None,
                    "total": None,
                    "yoy": None,
                    "scopeNote": "OpenAI-referred visits scaled to the full AI ecosystem",
                },
                "combined": {
                    "label": "Google + Bing", "trend": None,
                    "trendNote": "each engine carries its own trend",
                    "monthly": {str(m): v["total"] for m, v in BASELINE["combined"]["monthly"].items()},
                    "total": BASELINE["combined"]["totals"]["clicks"],
                    "yoy": None,
                    "scopeNote": "sum of the two property totals over the same 365 days",
                },
            },
            "ai": {
                "premium": ai_premium(),
                "includeByDefault": INCLUDE_AI,
                "weeks": BASELINE["ai"]["weeks"],
                "seoReference": BASELINE["ai"]["seo_reference"],
                "ecosystem": AI_ECOSYSTEM, "risk": AI_RISK, "lift": AI_LIFT,
                "caveats": BASELINE["ai"]["caveats"],
            },
            # What share of the total base the Botify lift actually acts on. The
            # deviation is a non-branded gain against a total base, and this is the
            # number that keeps that honest.
            "liftDenominators": {e: lift_denominators(e) for e in ("google",)},
            "nonbrandShareOfCombined":
                BASELINE["google_nonbrand"]["totals"]["clicks"]
                / BASELINE["combined"]["totals"]["clicks"],
            "googleNonbrand": {
                "total": BASELINE["google_nonbrand"]["totals"]["clicks"],
                "yoy": BASELINE["google_nonbrand"]["yoy"],
            },
            "caveats": BASELINE["caveats"],
        },
        "sources": [{"group": g,
                     "rows": [{"input": i, "value": v, "source": src,
                               "window": w, "grade": gr}
                              for i, v, src, w, gr in rows]}
                    for g, rows in SOURCES],
        # ── the cache build: the PHYSICAL constraint on Full Scale ──
        # Added 2026-08-12 so the Deployment tab can show it. This is the only part of the
        # contract the browser could not previously see, and it is the part the Deployment
        # stage is actually about — whether ≥80% of in-scope pages can be SERVED by the
        # Target Full Scale Date. Constants only; `verify_parity.py` diffs the ported
        # arithmetic against the functions above.
        "cache": {
            "inScopePages": IN_SCOPE_PAGES,
            "fillPerSec": CACHE_FILL_PER_SEC,
            "threshold": FULL_SCALE_THRESHOLD,
            "targetFullScale": TARGET_FULL_SCALE.isoformat(),
            # Stated on the surface, because §4.2 reads TBD and the reading decides whether
            # the gate is achievable at all.
            "inScopePinned": False,
            "breakEvenPages": int(cache_fill_per_day()
                                  * (TARGET_FULL_SCALE - LAUNCH).days / FULL_SCALE_THRESHOLD),
            # Ryan's §7.4 calibration, so the Deployment tab can put the threshold RELIEF
            # beside the gate. That juxtaposition is the finding: a slip relieves the goal
            # and nothing in the SOW restores a missed gate, so at 3 days the numbers look
            # adequate while Full Scale has already gone.
            "adjustmentRetention": [list(p) for p in ADJUSTMENT_RETENTION],
        },
        # The agreement's own dates, for the roadmap. Kept in their own block rather than
        # under "defaults" because nothing here is an input anyone may change — they are
        # terms. See the comment on SERVING_RAMP: these must not drive the forecast.
        "contract": {
            "checkpoints": [d.isoformat() for d in CHECKPOINTS],
            "servingRamp": [{"day": d, "coverage": c, "label": l}
                            for d, c, l in SERVING_RAMP],
            "servingRampProvisional": SERVING_RAMP_PROVISIONAL,
            "fullScaleTranche": "T4",
            "servingRampDisplay": SERVING_RAMP_DISPLAY,
            "freeze": [d.isoformat() for d in HOLIDAY_FREEZE],
            "fullScaleSustainDays": 7,
        },
        "defaults": {
            "launch": LAUNCH.isoformat(), "decision": DECISION.isoformat(),
            # The contract stops counting here, eleven days before the decision.
            "measurementClose": MEASUREMENT_CLOSE.isoformat(),
            "rampWeeks": RAMP_WEEKS, "tranches": TRANCHES,
            "anon": ANONYMIZED_INCLUSION,
            "growth": GROWTH, "dial": INDEXATION_DIAL,
            "newPagePerf": NEW_PAGE_PERFORMANCE,
            "clicksPerPage": CLICKS_PER_INDEXED_PAGE,
            "aov": AOV, "cr": CR, "bing": INCLUDE_BING,
            "aiBasis": AI_BASIS,
        },
    }


if __name__ == "__main__":
    w_nb, w_an = bucket_weights()
    ann = annual_targets()
    print(f"launch {LAUNCH} → decision {DECISION}  ({(DECISION-LAUNCH).days}d)"
          f"  ramp {RAMP_WEEKS}w/{TRANCHES}  Bing={'in' if INCLUDE_BING else 'out'}")
    print(f"anonymized inclusion {ANONYMIZED_INCLUSION:.0%}"
          f"  →  base is {w_nb:.1%} measured / {w_an:.1%} attributed")
    print(f"RPV ${RPV:.4f}   shapes from {DERIVED['snapshot_date']} RealKeywords\n")

    print("SEASONALITY (bucket-weighted)")
    seas = seasonality()
    for metric in ("impressions", "clicks", "keywords"):
        print("  %-12s %s" % (metric, "  ".join(
            f"{m}:{seas[metric][m]:.3f}" for m in sorted(seas[metric]))))

    print("\nANNUAL TARGETS")
    for t in TIERS:
        print(f"  {t:5} clicks {ann['clicks'][t]:>13,.0f}   impressions {ann['impressions'][t]:>15,.0f}"
              f"   revenue ${ann['clicks'][t]*RPV/1e6:,.1f}M")
        for k, v in ann["levers"][t].items():
            print(f"        {k:20} {v:>13,.0f}  ({v/ann['clicks'][t]:5.1%})")

    print("\nIN-WINDOW AT DECISION")
    for t in TIERS:
        for m in ("impressions", "clicks", "keywords"):
            v = cumulative(m, t)
            print(f"  {t:5} {m:12} {v:>16,.0f}  ({100*v/ann[m][t]:>5.1f}% of annual)")
        print(f"  {t:5} {'revenue':12} {'$'+format(cumulative('clicks',t)*RPV/1e6,',.2f')+'M':>16}")

    print("\nENGINE SPLIT AT DECISION — google + bing reconstructs the total exactly")
    for t in TIERS:
        tot = cumulative("clicks", t)
        goo = cumulative("clicks", t, None, "google")
        bng = cumulative("clicks", t, None, "bing")
        print(f"  {t:5} total ${tot*RPV/1e6:8,.2f}M"
              f"   google ${goo*RPV/1e6:8,.2f}M ({goo/tot:5.1%})"
              f"   bing ${bng*RPV/1e6:6,.2f}M ({bng/tot:5.1%})"
              f"   residual {abs(goo+bng-tot)/tot:.1e}")
    print("  Bing carries no indexation lever, so this is traffic vs traffic+indexation.")

    print("\nCACHE COVERAGE RAMP — the driver of the curve's shape")
    span = (DECISION - LAUNCH).days
    print("  tranche go-lives at launch + %s days"
          % [(st - LAUNCH).days for st, _ in _tranches()])
    for d in range(0, span + 1, 28):
        cov = {t: sum(w * adoption_fraction(t, (LAUNCH + timedelta(days=d) - st).days)
                      for st, w in _tranches()) for t in ("low", "high")}
        print(f"    day {d:3}   low {cov['low']:6.1%}   high {cov['high']:6.1%}")

    print("\nANONYMIZED SENSITIVITY — the dominant lever")
    print(f"  {'incl':>5} {'LOW rev':>10} {'HIGH rev':>11}  {'measured share of base':>24}")
    for i in (0.0, 0.3, 0.5, 0.7, 1.0):
        lo = cumulative("clicks", "low", i) * RPV
        hi = cumulative("clicks", "high", i) * RPV
        print(f"  {i:>5.0%} {'$'+format(lo/1e6,',.2f')+'M':>10} {'$'+format(hi/1e6,',.2f')+'M':>11}"
              f"  {bucket_weights(i)[0]:>23.1%}")

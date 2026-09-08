import json, datetime as dt
SP = __import__('os').path.dirname(__import__('os').path.abspath(__file__)) + '/'
S = json.load(open(SP + 'series.json')); YOY = json.load(open(SP + 'yoy.json'))
DASH = ' stroke-dasharray="6 5"'
MONTHS = ["Sep", "Oct", "Nov", "Dec"]
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
    ymin, ymax = -26, 0
    y = lambda v: T + (ymax - v) / (ymax - ymin) * ph
    g = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img"><title>Google clicks, year over year, by month</title>']
    for t in (0, -5, -10, -15, -20, -25):
        g += [f'<line class="grid" x1="{L}" x2="{L+pw}" y1="{y(t):.1f}" y2="{y(t):.1f}"/>', f'<text class="tick" x="{L-8}" y="{y(t)+4:.1f}" text-anchor="end">{t}%</text>']
    g.append(f'<line class="axis" x1="{L}" x2="{L+pw}" y1="{y(0):.1f}" y2="{y(0):.1f}"/>')
    for i, (ym, cur, prior, ch) in enumerate(YOY):
        x = L + i * slot + (slot - bw) / 2; v = ch * 100; top = y(0); hgt = y(v) - y(0)
        cls = "s-bad" if v < -14 else "s-claim"
        g.append(f'<rect class="bar {cls}{" partial" if ym.endswith("p") else ""}" x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{hgt:.1f}" rx="0"/>')
        g.append(f'<text class="dvalue {cls}" x="{x+bw/2:.1f}" y="{y(v)+13:.1f}" text-anchor="middle">{v:.1f}%</text>')
        partial = ym.endswith('p'); d = dt.date(int(ym[:4]), int(ym[5:7]), 1)
        lab = d.strftime("%b %y") + (" (1–5)" if partial else "")
        g.append(f'<text class="tick" x="{x+bw/2:.1f}" y="{T+ph+22}" text-anchor="middle">{lab}</text>')
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


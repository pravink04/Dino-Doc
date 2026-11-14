"""Numbers only: KPIs, period comparison, drivers, anomalies."""
import pandas as pd


def kpis(df):
    rev, cost, units = df.revenue.sum(), df.cost.sum(), df.units.sum()
    n = len(df)
    return {"revenue": rev, "profit": rev - cost, "margin": (rev - cost) / rev if rev else 0,
            "units": units, "price": rev / units if units else 0, "orders": n, "aov": rev / n if n else 0}


def compare(df, a, b):
    ka, kb = kpis(df[df.quarter == a]), kpis(df[df.quarter == b])
    change = {k: (kb[k] / ka[k] - 1 if ka[k] else 0) for k in ka}
    return ka, kb, change


def drivers(df, a, b):
    """Revenue change per region+product, split into volume and price/mix effects."""
    g = df.groupby(["quarter", "region", "product"])[["revenue", "units"]].sum().reset_index()
    A = g[g.quarter == a].set_index(["region", "product"])
    B = g[g.quarter == b].set_index(["region", "product"])
    out = pd.DataFrame({"rev_a": A.revenue, "rev_b": B.revenue, "u_a": A.units, "u_b": B.units}).fillna(0)
    out["change"] = out.rev_b - out.rev_a
    price_a = out.rev_a / out.u_a.replace(0, 1)
    out["volume_effect"] = (out.u_b - out.u_a) * price_a
    out["price_mix_effect"] = out.change - out.volume_effect
    out = out.sort_values("change").reset_index()
    out["segment"] = out.apply(lambda r: " · ".join(x for x in (r["region"], r["product"]) if x != "All") or "Total", axis=1)
    return out


def anomalies(df, threshold=0.25):
    """Flag months where a segment is >25% away from its previous 3-month average."""
    m = df.groupby([df.date.dt.to_period("M").astype(str).rename("month"), "region", "product"]).revenue.sum().reset_index()
    m = m.sort_values("month")
    m["avg3"] = m.groupby(["region", "product"]).revenue.transform(lambda s: s.shift(1).rolling(3).mean())
    m["dev"] = m.revenue / m.avg3 - 1
    return m[m.dev.abs() > threshold].sort_values("dev", key=lambda s: s.abs(), ascending=False)


def coverage(df, freq):
    """For each period, the share of its days that the data covers (a half-empty period is 'partial')."""
    lo, hi = df.date.min().normalize(), df.date.max().normalize()
    if (df.date.dt.day == 1).all():  # monthly data dated on the 1st: the last month is complete
        hi = hi + pd.offsets.MonthEnd(0)
    out = {}
    for p in df.date.dt.to_period(freq).unique():
        s, e = p.start_time.normalize(), p.end_time.normalize()
        out[str(p)] = ((min(e, hi) - max(s, lo)).days + 1) / ((e - s).days + 1)
    return out


def money(x, sym="₹"):
    """Short display format: Cr/L for rupees, M/K for other currencies."""
    a, sign = abs(x), "-" if x < 0 else ""
    if sym == "₹":
        return f"{sign}₹{a/1e7:.2f} Cr" if a >= 1e7 else f"{sign}₹{a/1e5:.2f} L" if a >= 1e5 else f"{sign}₹{a:,.0f}"
    return f"{sign}{sym}{a/1e6:.2f}M" if a >= 1e6 else f"{sign}{sym}{a/1e3:.1f}K" if a >= 1e3 else f"{sign}{sym}{a:,.0f}"
import pandas as pd
import plotly.express as px
import streamlit as st

import theme
from ai import ask_ai
from analysis import compare, drivers, anomalies, coverage, money
from feedback import analyze, THEMES
from loader import read_any, guess, clean_sales, clean_feedback, SALES_FIELDS, FB_FIELDS

st.set_page_config(page_title="Decision Intelligence", layout="wide")
theme.inject()
theme.hero()
theme.brand()


def mapper(raw, fields, key):
    """One dropdown per field, pre-filled with the auto-detected column. Change it if it is wrong."""
    cols = ["(none)"] + list(raw.columns)
    out = {}
    for field, label in fields.items():
        g = guess(raw, field)
        out[field] = st.selectbox(label, cols, index=cols.index(g) if g in cols else 0, key=f"{key}-{field}")
    return out


# ---------- 1. Load data (any column names) ----------
sales_file = st.sidebar.file_uploader("Sales file (CSV or Excel)", type=["csv", "xlsx"])
fb_file = st.sidebar.file_uploader("Feedback file (CSV or Excel)", type=["csv", "xlsx"])
freq = "Q" if st.sidebar.radio("Compare by", ["Quarter", "Month"]) == "Quarter" else "M"
dayfirst = st.sidebar.checkbox("Dates are DD/MM/YYYY")
sym = st.sidebar.text_input("Currency symbol", "₹")

raw = read_any(sales_file or "data/sales.csv")
with st.sidebar.expander("Sales column mapping", expanded=sales_file is not None):
    smap = mapper(raw, SALES_FIELDS, "s-" + (sales_file.name if sales_file else "sample"))
sales, notes = clean_sales(raw, smap, freq, dayfirst)
if sales is None:
    st.error(notes[0])
    st.stop()
for n in notes:
    st.sidebar.warning(n)
has_cost, has_units = smap["cost"] != "(none)", smap["units"] != "(none)"

# Which periods are complete? A period with only a few days of data gives fake "crashes".
cov = coverage(sales, freq)
periods = sorted(cov)
if len(periods) < 2:
    st.error("Only one period found in your data. Try 'Month' under 'Compare by', or upload data with more dates.")
    st.stop()
complete = [p for p in periods if cov[p] >= 0.9]
pick = complete if len(complete) >= 2 else periods
label = lambda p: p if cov[p] >= 0.9 else f"{p} (partial, {cov[p]:.0%})"
b = st.sidebar.selectbox("Current period", periods, index=periods.index(pick[-1]), format_func=label)
a = st.sidebar.selectbox("Compare with", periods, index=periods.index(pick[-2]), format_func=label)
st.sidebar.caption(f"{len(sales):,} rows · {sales.date.min():%d %b %Y} to {sales.date.max():%d %b %Y} · {len(complete)} complete periods")

# Feedback: never mix the built-in sample comments with your own sales file
if fb_file is not None or sales_file is None:
    fraw = read_any(fb_file or "data/feedback.csv")
    with st.sidebar.expander("Feedback column mapping", expanded=fb_file is not None):
        fmap = mapper(fraw, FB_FIELDS, "f-" + (fb_file.name if fb_file else "sample"))
    fb = analyze(clean_feedback(fraw, fmap, freq, b))
else:
    fb = analyze(pd.DataFrame({"quarter": [], "text": []}))

for p in dict.fromkeys([a, b]):
    if cov[p] < 0.9:
        st.warning(f"{p} has data for only {cov[p]:.0%} of its days, so comparisons with it are unreliable. Pick complete periods.")
if a == b:
    st.warning("Both periods are the same, so every change shows 0%.")

# ---------- 2. Analysis ----------
ka, kb, chg = compare(sales, a, b)
drv = drivers(sales, a, b)
mcov = coverage(sales, "M")
full = sales[sales.date.dt.to_period("M").astype(str).map(lambda m: mcov[m] >= 0.9)]  # only complete months
partial_months = sorted(m for m in mcov if mcov[m] < 0.9)
anom = anomalies(full) if full.date.dt.to_period("M").nunique() >= 4 else pd.DataFrame(columns=["month", "region", "product", "dev"])
fbb = fb[fb.quarter == b]
neg_themes = {t: int(fbb[fbb.label == "negative"][t].sum()) for t in THEMES}
worst, best = drv.iloc[0], drv.iloc[-1]


def f0(x):  # full number with symbol, so the AI cannot rescale it
    return ("-" if x < 0 else "") + f"{sym}{abs(x):,.0f}"


def seg_line(r, word):
    extra = f" (volume effect {f0(r['volume_effect'])}, price/mix effect {f0(r['price_mix_effect'])})" if has_units else ""
    return f"Biggest {word}: {r['segment']}, change {f0(r['change'])}{extra}."


L = [f"Period {b} compared with {a}. Currency symbol: {sym}. Use the numbers exactly as written.",
     f"Revenue {f0(kb['revenue'])} vs {f0(ka['revenue'])} ({chg['revenue']:+.1%}).",
     f"Orders {kb['orders']:,} ({chg['orders']:+.1%}); average order value {f0(kb['aov'])} ({chg['aov']:+.1%})."]
if has_cost:
    L.append(f"Profit {f0(kb['profit'])} ({chg['profit']:+.1%}). Margin {kb['margin']:.1%} vs {ka['margin']:.1%}.")
else:
    L.append("Cost data is NOT available: do not discuss profit or margin.")
if has_units:
    L.append(f"Units {kb['units']:,.0f} ({chg['units']:+.1%}); average price {f0(kb['price'])} ({chg['price']:+.1%}).")
L.append(seg_line(worst, "decline") if worst["change"] < 0 else "No segment declined.")
L.append(seg_line(best, "growth") if best["change"] > 0 else "No segment grew.")
L.append(f"Customer feedback in {b}: {fbb.label.value_counts().to_dict()}. Negative mentions by theme: {neg_themes}."
         if len(fbb) else "No customer feedback is available for this period.")
L.append("Anomalies in complete months (month, region, product, deviation): "
         f"{anom.head(5)[['month','region','product','dev']].round(2).to_dict('records') or 'none'}")
L.append(f"Data coverage: {a} {cov[a]:.0%}, {b} {cov[b]:.0%}. Data notes: {'; '.join(notes) or 'none'}")
facts = "\n".join(L)

# ---------- 3. Dashboard ----------
pts = (kb["margin"] - ka["margin"]) * 100
cards = [("💰", "Revenue", money(kb["revenue"], sym), f"{chg['revenue']:+.1%}", chg["revenue"] >= 0)]
if has_cost:
    cards += [("📈", "Profit", money(kb["profit"], sym), f"{chg['profit']:+.1%}", chg["profit"] >= 0),
              ("🎯", "Margin", f"{kb['margin']:.1%}", f"{pts:+.1f} pts", pts >= 0)]
else:
    cards += [("🧾", "Orders", f"{kb['orders']:,}", f"{chg['orders']:+.1%}", chg["orders"] >= 0),
              ("🛒", "Avg order value", money(kb["aov"], sym), f"{chg['aov']:+.1%}", chg["aov"] >= 0)]
if has_units:
    cards += [("📦", "Units", f"{kb['units']:,.0f}", f"{chg['units']:+.1%}", chg["units"] >= 0),
              ("🏷️", "Avg price", money(kb["price"], sym), f"{chg['price']:+.1%}", chg["price"] >= 0)]
theme.kpi_cards(cards)

t1, t2, t3, t4, t5 = st.tabs(["Executive summary", "Trends & anomalies", "What changed", "Customer feedback", "Scenarios"])

with t1:
    if st.button("Generate AI executive summary"):
        st.session_state.summary = ask_ai(facts + "\n\nWrite an executive summary: what happened, why, top 2 risks, top 2 opportunities, 3 recommendations.")
        st.toast("Summary ready", icon="✨")
    st.write(st.session_state.get("summary", "Click the button to generate the summary."))
    with st.expander("Facts sent to the AI"):
        st.text(facts)
    st.subheader("Ask the assistant")
    if q := st.chat_input("Why did revenue change?"):
        st.chat_message("user").write(q)
        st.chat_message("assistant").write(ask_ai(f"Facts:\n{facts}\n\nQuestion: {q}"))

with t2:
    monthly = full.groupby(full.date.dt.to_period("M").astype(str)).revenue.sum().reset_index()
    fig = px.line(monthly, x="date", y="revenue", title="Monthly revenue (complete months)")
    fig.update_traces(fill="tozeroy", fillcolor="rgba(34,211,238,.12)", line=dict(width=3))
    st.plotly_chart(theme.style(fig), width="stretch")
    if partial_months:
        st.caption(f"Left out because the month is incomplete: {', '.join(partial_months)}")
    st.dataframe(anom, width="stretch")

with t3:
    drv["direction"] = drv["change"].apply(lambda v: "Growth" if v >= 0 else "Decline")
    fig = px.bar(drv, x="change", y="segment", orientation="h", color="direction", title=f"Revenue change {a} → {b}",
                 color_discrete_map={"Growth": "#34d399", "Decline": "#f87171"})
    st.plotly_chart(theme.style(fig), width="stretch")
    cols = ["segment", "change"] + (["volume_effect", "price_mix_effect"] if has_units else [])
    st.dataframe(drv[cols].round(0), width="stretch")
    if not has_units:
        st.caption("No units column mapped, so the volume vs price split is not available.")

with t4:
    if fb.empty:
        st.info("No feedback loaded. Upload a feedback file (comment text, optional date) in the sidebar.")
    else:
        if fbb.empty:
            st.info(f"No comments matched {b}. Check the date/period mapping, or pick '(none)' to use all comments for {b}.")
        fig = px.histogram(fb, x="quarter", color="label", barmode="group", title="Sentiment by period",
                           color_discrete_map={"positive": "#34d399", "neutral": "#94a3b8", "negative": "#f87171"})
        st.plotly_chart(theme.style(fig), width="stretch")
        st.write("Negative mentions by theme:", neg_themes)

with t5:
    p = st.slider("Price change %", -20, 20, 0) / 100
    v = st.slider("Volume change %", -30, 30, 0) / 100
    k = st.slider("Unit cost change %", -15, 15, 0) / 100 if has_cost else 0
    elastic = st.checkbox("Price also changes volume (elasticity -1.2)")
    vol = (1 + v) * (1 - 1.2 * p if elastic else 1)
    rev = kb["revenue"] * (1 + p) * vol
    st.metric("Scenario revenue", money(rev, sym), f"{rev / kb['revenue'] - 1:+.1%}" if kb["revenue"] else "n/a")
    if has_cost:
        profit = rev - (kb["revenue"] - kb["profit"]) * vol * (1 + k)
        st.metric("Scenario profit", money(profit, sym), f"{profit / kb['profit'] - 1:+.1%}" if kb["profit"] else "n/a")
    else:
        st.caption("No cost column mapped, so only revenue is simulated.")
"""Reads any CSV/Excel file and maps its columns to the ones the dashboard needs."""
import re
import pandas as pd

SALES_FIELDS = {"date": "Date *", "revenue": "Revenue / sales amount *", "cost": "Cost (optional)",
                "units": "Units / quantity (optional)", "region": "Region (optional)", "product": "Product (optional)"}
FB_FIELDS = {"text": "Comment text *", "period": "Date / period (optional)"}

# Column-name hints. The first match wins; you can always change it in the sidebar.
SYN = {
    "date": ["date", "month", "period", "day", "time"],
    "revenue": ["revenue", "sales", "amount", "turnover", "income"],
    "cost": ["cost", "expense", "cogs"],
    "units": ["units", "quantity", "qty", "volume"],
    "region": ["region", "state", "city", "zone", "area", "location", "country", "branch", "store"],
    "product": ["product", "item", "category", "sku", "service"],
    "text": ["text", "comment", "feedback", "review", "message", "remark"],
    "period": ["quarter", "period", "date", "month"],
}


def read_any(src):
    """CSV (any separator, any encoding) or Excel -> DataFrame."""
    name = getattr(src, "name", str(src)).lower()
    if name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(src)
    else:
        for enc in ("utf-8", "latin-1"):
            try:
                if hasattr(src, "seek"):
                    src.seek(0)
                df = pd.read_csv(src, sep=None, engine="python", encoding=enc)
                break
            except UnicodeDecodeError:
                continue
    df.columns = [str(c).strip() for c in df.columns]
    return df


def guess(df, field):
    """Pick the most likely column for a field (exact name first, then 'contains')."""
    names = {c: c.lower() for c in df.columns}
    for c, n in names.items():
        if n in SYN[field]:
            return c
    for c, n in names.items():
        if any(s in n for s in SYN[field]):
            return c
    if field == "text":  # fall back to the column with the longest strings
        txt = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
        if txt:
            return max(txt, key=lambda c: df[c].astype(str).str.len().mean())
    return None


def num(s):
    """'₹1,20,000' -> 120000.0"""
    return pd.to_numeric(s.astype(str).str.replace(r"[^\d.\-]", "", regex=True), errors="coerce")


def parse_dates(s, dayfirst):
    return pd.to_datetime(s, errors="coerce", dayfirst=dayfirst, format="mixed")


def clean_sales(raw, m, freq, dayfirst=False):
    """Returns (clean DataFrame, notes). DataFrame is None if date or revenue is missing."""
    if m["date"] == "(none)" or m["revenue"] == "(none)":
        return None, ["Pick a date column and a revenue column in 'Sales column mapping'."]
    df = pd.DataFrame(index=raw.index)
    df["date"] = parse_dates(raw[m["date"]], dayfirst)
    df["revenue"] = num(raw[m["revenue"]])
    notes = []
    for f, msg in [("cost", "No cost column: profit and margin equal revenue, so ignore them."),
                   ("units", "No units column: volume vs price split is not available.")]:
        if m[f] == "(none)":
            df[f] = 0.0
            notes.append(msg)
        else:
            df[f] = num(raw[m[f]]).fillna(0)
    for f in ("region", "product"):
        df[f] = raw[m[f]].astype(str) if m[f] != "(none)" else "All"
    bad = df.date.isna().sum() + df.revenue.isna().sum()
    df = df.dropna(subset=["date", "revenue"])
    if df.empty:
        return None, ["No valid rows. Check the date and revenue columns (and the DD/MM/YYYY tick box)."]
    if bad:
        notes.append(f"{bad} rows had a bad date or revenue and were skipped.")
    df["quarter"] = df.date.dt.to_period(freq).astype(str)  # column name kept; holds quarter or month
    return df, notes


def period_label(x, freq):
    x = str(x).replace("-Q", "Q").strip()
    if re.fullmatch(r"\d{4}Q[1-4]", x):
        return x
    d = pd.to_datetime(x, errors="coerce")
    return str(d.to_period(freq)) if pd.notna(d) else x


def clean_feedback(raw, m, freq, default_period):
    """Comments with a period label. No period column: all comments go to the current period."""
    if m["text"] == "(none)":
        return pd.DataFrame({"quarter": [], "text": []})
    df = pd.DataFrame({"text": raw[m["text"]].astype(str).str.strip()})
    if m["period"] == "(none)":
        df["quarter"] = default_period
    else:
        df["quarter"] = raw[m["period"]].apply(lambda x: period_label(x, freq))
    return df[df.text.ne("") & df.text.ne("nan")].reset_index(drop=True)
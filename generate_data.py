"""Run once: creates data/sales.csv and data/feedback.csv (sample company)."""
import numpy as np, pandas as pd

rng = np.random.default_rng(7)
regions = {"North": 1.6e6, "South": 1.2e6, "East": 1.0e6, "West": 1.3e6}
products = {"Core": (1.0, 1000, 0.58), "Pro": (1.25, 1800, 0.52), "Lite": (0.7, 500, 0.68)}  # size, price, cost ratio

rows = []
for i, d in enumerate(pd.date_range("2025-01-01", periods=21, freq="MS")):
    season = 1 + 0.12 * np.sin((d.month - 3) / 12 * 2 * np.pi)
    for r, base in regions.items():
        for p, (size, price, cr) in products.items():
            rev = base * size * season * (1 + 0.018 * i) * rng.uniform(0.96, 1.04)
            pf = 1
            if r == "West" and p == "Pro" and i >= 18:   # planted problem: sales drop + discounting
                rev *= 0.6; cr += 0.05; pf = 0.92
            if r == "East" and i == 14:                  # planted one-month spike
                rev *= 1.45
            if r == "South" and p == "Lite" and i >= 18: # planted growth
                rev *= 1.3
            rows.append([d.date(), r, p, round(rev), round(rev * cr), round(rev / (price * pf))])
pd.DataFrame(rows, columns=["date", "region", "product", "revenue", "cost", "units"]).to_csv("data/sales.csv", index=False)

q2 = ["Delivery was fast and the Pro unit works great", "Good value for the price, support was helpful",
      "Setup was easy, love the app interface", "Quality is reliable, very happy with the Core plan",
      "A bit expensive but quality is excellent", "Support agent was friendly and quick",
      "Delivery was on time, smooth experience", "Interface is confusing for new users"]
q3 = ["Delivery delayed by two weeks, very frustrating", "Late shipping again, order arrived damaged",
      "Pro order delayed again and quality feels worse, expensive", "Support was slow and unresponsive, still waiting on refund",
      "Delivery delays in the West region, poor experience", "Great product but delivery is late",
      "Lite plan is good value, easy to use", "Love the new Lite pricing, best value",
      "Cancelled my Pro order after the delay", "App is easy and fast, happy with Lite",
      "Support was helpful and friendly", "Overpriced Pro, switching to a competitor"]
fb = [("2026Q2", t) for t in q2] + [("2026Q3", t) for t in q3]
pd.DataFrame(fb, columns=["quarter", "text"]).to_csv("data/feedback.csv", index=False)
print("Created data/sales.csv and data/feedback.csv")

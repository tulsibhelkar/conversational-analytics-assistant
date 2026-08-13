"""
generate_data.py
-----------------
Creates a synthetic but realistic retail sales dataset so the project can be
run end-to-end without needing to download anything from Kaggle.

If you already have a real dataset (e.g. Kaggle "Online Retail" / "Superstore"),
just drop it in as data/sales_data.csv with matching column names and skip
running this file.

Run:
    python data/generate_data.py
"""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

REGIONS = ["North", "South", "East", "West", "Central"]
CATEGORIES = {
    "Electronics": ["Wireless Earbuds", "Smartwatch", "Bluetooth Speaker", "Power Bank", "Laptop Stand"],
    "Home & Kitchen": ["Air Fryer", "Non-stick Pan Set", "Electric Kettle", "Mixer Grinder", "Table Lamp"],
    "Apparel": ["Cotton T-Shirt", "Running Shoes", "Denim Jacket", "Formal Shirt", "Backpack"],
    "Beauty": ["Face Serum", "Sunscreen SPF50", "Hair Dryer", "Lip Balm Set", "Perfume"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Cricket Bat", "Football", "Resistance Bands"],
}
SEGMENTS = ["New", "Returning", "Loyal"]

start_date = datetime(2023, 1, 1)
end_date = datetime(2025, 12, 31)
date_range_days = (end_date - start_date).days

n_rows = 4000
n_customers = 850

rows = []
for i in range(n_rows):
    order_date = start_date + timedelta(days=random.randint(0, date_range_days))
    category = random.choice(list(CATEGORIES.keys()))
    product = random.choice(CATEGORIES[category])
    region = random.choices(REGIONS, weights=[0.28, 0.18, 0.20, 0.22, 0.12])[0]
    segment = random.choices(SEGMENTS, weights=[0.4, 0.4, 0.2])[0]

    base_price = {
        "Electronics": (900, 4500),
        "Home & Kitchen": (400, 3200),
        "Apparel": (300, 2200),
        "Beauty": (150, 1500),
        "Sports": (250, 3000),
    }[category]
    unit_price = round(random.uniform(*base_price), 2)

    # slight seasonal bump around Oct-Dec (festive/holiday season)
    qty_boost = 1.4 if order_date.month in (10, 11, 12) else 1.0
    quantity = max(1, int(np.random.poisson(2) * qty_boost))

    # occasional discount, not every order
    discount_pct = random.choice([0, 0, 0, 5, 10, 15, 20])
    revenue = round(unit_price * quantity * (1 - discount_pct / 100), 2)

    rows.append({
        "order_id": f"ORD{100000 + i}",
        "order_date": order_date.strftime("%Y-%m-%d"),
        "customer_id": f"CUST{random.randint(1, n_customers):04d}",
        "customer_segment": segment,
        "region": region,
        "category": category,
        "product": product,
        "quantity": quantity,
        "unit_price": unit_price,
        "discount_pct": discount_pct,
        "revenue": revenue,
    })

df = pd.DataFrame(rows).sort_values("order_date").reset_index(drop=True)
df.to_csv("data/sales_data.csv", index=False)
print(f"Wrote {len(df)} rows to data/sales_data.csv")
print(df.head())

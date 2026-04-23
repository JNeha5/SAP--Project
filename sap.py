import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime, timedelta

np.random.seed(42)

# -----------------------------
# 1. DATA GENERATION
# -----------------------------

NUM_ORDERS = 300

materials = ['LAPTOP', 'DESK', 'MONITOR']
customers = [f'CUST{i}' for i in range(1, 51)]

def random_date(start):
    return start + timedelta(days=random.randint(0, 30))

base_date = datetime(2024, 1, 1)

# VBAK (Sales Order Header)
vbak = pd.DataFrame({
    'VBELN': [f'ORD{i:04d}' for i in range(NUM_ORDERS)],
    'AUDAT': [random_date(base_date) for _ in range(NUM_ORDERS)],
    'KUNNR': np.random.choice(customers, NUM_ORDERS)
})

# VBAP (Line Items)
vbap_list = []

for order in vbak['VBELN']:
    num_items = random.randint(1, 4)
    for _ in range(num_items):
        qty = random.randint(1, 5)
        price = random.randint(20000, 80000)
        vbap_list.append({
            'VBELN': order,
            'MATNR': random.choice(materials),
            'QTY': qty,
            'PRICE': price,
            'NETWR': qty * price
        })

vbap = pd.DataFrame(vbap_list)

# -----------------------------
# 2. DELIVERY DATA (LIKP)
# -----------------------------
likp_list = []

for _, row in vbak.iterrows():
    if random.random() < 0.86:  # 86% delivered
        lead_days = random.randint(3, 20)
        likp_list.append({
            'DELIV_ID': f'DEL{row.VBELN}',
            'VGBEL': row.VBELN,
            'WADAT_IST': row.AUDAT + timedelta(days=lead_days)
        })

likp = pd.DataFrame(likp_list)

# -----------------------------
# 3. BILLING DATA (VBRK)
# -----------------------------
vbrk_list = []

for _, row in likp.iterrows():
    if random.random() < 0.92:  # 92% invoiced
        vbrk_list.append({
            'BILL_ID': f'BIL{row.DELIV_ID}',
            'ZUONR': row.VGBEL,
            'FKDAT': row.WADAT_IST + timedelta(days=2)
        })

vbrk = pd.DataFrame(vbrk_list)

# -----------------------------
# 4. JOIN LOGIC (FIXED)
# -----------------------------

# Step 1: VBAK + VBAP (INNER)
df = pd.merge(vbak, vbap, on='VBELN', how='inner')

# Step 2: LEFT JOIN LIKP (Delivery)
df = pd.merge(
    df,
    likp,
    left_on='VBELN',
    right_on='VGBEL',
    how='left'
)

# Step 3: LEFT JOIN VBRK (Billing)
df = pd.merge(
    df,
    vbrk,
    left_on='VBELN',
    right_on='ZUONR',
    how='left'
)

# -----------------------------
# 5. KPI CALCULATIONS
# -----------------------------

# Total Order Value
total_order_value = df['NETWR'].sum()

# Billed Revenue
billed_df = df[df['FKDAT'].notna()]
billed_revenue = billed_df['NETWR'].sum()

# Unbilled AR
unbilled_ar = total_order_value - billed_revenue

# Lead Time
df['LEAD_TIME'] = (df['WADAT_IST'] - df['AUDAT']).dt.days

# Average Lead Time
lead_time_avg = df['LEAD_TIME'].mean()

# On-Time Delivery Rate (<= 7 days)
delivered_df = df[df['WADAT_IST'].notna()]
on_time_df = delivered_df[delivered_df['LEAD_TIME'] <= 7]

if len(delivered_df) > 0:
    on_time_rate = (len(on_time_df) / len(delivered_df)) * 100
else:
    on_time_rate = 0

# -----------------------------
# 6. PRINT KPI DASHBOARD
# -----------------------------

print("\n===== O2C KPI DASHBOARD =====")
print(f"Total Order Value     : ₹{total_order_value:,.2f}")
print(f"Billed Revenue        : ₹{billed_revenue:,.2f}")
print(f"Unbilled AR           : ₹{unbilled_ar:,.2f}")
print(f"Avg Lead Time         : {lead_time_avg:.2f} days")
print(f"On-Time Delivery Rate : {on_time_rate:.2f}%")

# -----------------------------
# 7. VISUALIZATIONS
# -----------------------------

# Revenue by Material
material_revenue = df.groupby('MATNR')['NETWR'].sum()

plt.figure()
material_revenue.plot(kind='bar')
plt.title("Revenue by Material")
plt.xlabel("Material")
plt.ylabel("Revenue")
plt.tight_layout()
plt.show()

# Lead Time Distribution
plt.figure()
df['LEAD_TIME'].dropna().hist(bins=10)
plt.title("Lead Time Distribution")
plt.xlabel("Days")
plt.ylabel("Frequency")
plt.tight_layout()
plt.show()

# Revenue Split
plt.figure()
plt.pie(
    [billed_revenue, unbilled_ar],
    labels=['Billed', 'Unbilled'],
    autopct='%1.1f%%'
)
plt.title("Revenue Split")
plt.show()

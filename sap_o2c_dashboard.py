import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import FuncFormatter
import matplotlib.gridspec as gridspec
import warnings

warnings.filterwarnings("ignore")
np.random.seed(42)

# =========================================================
# 1. SIMULATED SAP O2C DATA
# =========================================================

N_ORDERS = 300

# VBAK - Sales Order Header
vbak = pd.DataFrame({
    'VBELN': [f'SO{str(i).zfill(6)}' for i in range(1, N_ORDERS + 1)],
    'AUDAT': pd.to_datetime('2024-01-01') + pd.to_timedelta(
        np.random.randint(0, 365, N_ORDERS), unit='d'
    ),
    'KUNNR': np.random.choice([f'CUST{str(i).zfill(4)}' for i in range(1, 51)], N_ORDERS),
    'VKORG': np.random.choice(['1000', '2000', '3000'], N_ORDERS),
    'VTWEG': np.random.choice(['10', '20'], N_ORDERS),
    'NETWR_HDR': np.random.uniform(1000, 150000, N_ORDERS).round(2),
    'WAERK': 'INR'
})

# VBAP - Sales Order Items
MATERIALS = {
    'MAT-LAPTOP': ('Electronics', 45000),
    'MAT-MONITOR': ('Electronics', 18000),
    'MAT-KEYBOARD': ('Electronics', 2500),
    'MAT-CHAIR': ('Furniture', 12000),
    'MAT-DESK': ('Furniture', 25000),
    'MAT-HEADSET': ('Electronics', 5500),
    'MAT-WEBCAM': ('Electronics', 3200),
    'MAT-CABINET': ('Furniture', 8000),
}

vbap_rows = []
for _, order in vbak.iterrows():
    n_items = np.random.randint(1, 5)
    selected_mats = np.random.choice(list(MATERIALS.keys()), n_items, replace=False)
    for pos_idx, mat in enumerate(selected_mats, start=10):
        qty = np.random.randint(1, 20)
        base_price = MATERIALS[mat][1]
        netpr = round(base_price * np.random.uniform(0.90, 1.15), 2)
        netwr = round(qty * netpr, 2)

        vbap_rows.append({
            'VBELN': order['VBELN'],
            'POSNR': f'{pos_idx:04d}',
            'MATNR': mat,
            'MATKL': MATERIALS[mat][0],
            'KWMENG': qty,
            'NETPR': netpr,
            'NETWR_ITM': netwr
        })

vbap = pd.DataFrame(vbap_rows)

# LIKP - Delivery Header
delivered_orders = vbak.sample(frac=0.86, random_state=7)
likp = pd.DataFrame({
    'VBELN_DEL': [f'DL{str(i).zfill(6)}' for i in range(1, len(delivered_orders) + 1)],
    'VGBEL': delivered_orders['VBELN'].values,
    'LFDAT': delivered_orders['AUDAT'].values + pd.to_timedelta(
        np.random.randint(1, 15, len(delivered_orders)), unit='d'
    ),
    'WADAT_IST': delivered_orders['AUDAT'].values + pd.to_timedelta(
        np.random.randint(2, 28, len(delivered_orders)), unit='d'
    )
})

# VBRK - Billing Header
billed_orders = likp.sample(frac=0.92, random_state=13)
order_value_map = vbap.groupby('VBELN')['NETWR_ITM'].sum()

vbrk = pd.DataFrame({
    'VBELN_BILL': [f'BI{str(i).zfill(6)}' for i in range(1, len(billed_orders) + 1)],
    'ZUONR': billed_orders['VGBEL'].values,
    'FKDAT': billed_orders['WADAT_IST'].values + pd.to_timedelta(
        np.random.randint(1, 10, len(billed_orders)), unit='d'
    ),
    'NETWR_BILL': billed_orders['VGBEL'].map(order_value_map).values * np.random.uniform(0.95, 1.0, len(billed_orders))
})

# =========================================================
# 2. PIPELINE / JOIN LOGIC
# =========================================================

df = vbak.merge(vbap, on='VBELN', how='inner')
df = df.merge(
    likp[['VGBEL', 'LFDAT', 'WADAT_IST']],
    left_on='VBELN', right_on='VGBEL', how='left'
)
df = df.merge(
    vbrk[['ZUONR', 'FKDAT', 'NETWR_BILL']],
    left_on='VBELN', right_on='ZUONR', how='left'
)

df['ORDER_MONTH'] = df['AUDAT'].dt.to_period('M').astype(str)
df['LEAD_TIME_DAYS'] = (df['WADAT_IST'] - df['AUDAT']).dt.days
df['IS_DELIVERED'] = df['WADAT_IST'].notna()
df['IS_BILLED'] = df['FKDAT'].notna()

# =========================================================
# 3. KPI CALCULATION
# =========================================================

total_order_value = df['NETWR_ITM'].sum()
billed_revenue = vbrk['NETWR_BILL'].sum()
unbilled_exposure = total_order_value - billed_revenue
lead_times = df[df['LEAD_TIME_DAYS'].notna()]['LEAD_TIME_DAYS']
avg_lead_time = lead_times.mean()
on_time_rate = (lead_times <= 7).mean() * 100
delivery_rate = df['IS_DELIVERED'].mean() * 100

rev_by_mat = (
    df.groupby('MATNR')['NETWR_ITM']
    .sum()
    .sort_values(ascending=False)
    .head(8)
)

monthly = (
    df.groupby('ORDER_MONTH')
    .agg(
        Revenue=('NETWR_ITM', 'sum'),
        Orders=('VBELN', 'nunique')
    )
    .reset_index()
)

monthly['Revenue_M'] = monthly['Revenue'] / 1e6

# =========================================================
# 4. DASHBOARD STYLING
# =========================================================

BG = '#0D1117'
PANEL = '#161B22'
GRID = '#2A2F36'
TXT = '#E6EDF3'
MUTED = '#8B949E'
BLUE = '#58A6FF'
GREEN = '#3FB950'
YELLOW = '#D29922'
RED = '#F78166'

fig = plt.figure(figsize=(20, 14), dpi=160, facecolor=BG)
gs = gridspec.GridSpec(3, 12, figure=fig, hspace=0.55, wspace=0.5)

fig.suptitle(
    'SAP SD Order-to-Cash (O2C) Analytics Dashboard',
    fontsize=24, fontweight='bold', color=TXT
)

def draw_card(ax, title, value, subtitle="", color=BLUE):
    ax.set_facecolor(PANEL)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    rect = patches.FancyBboxPatch(
        (0, 0), 1, 1,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        linewidth=1.2, edgecolor=GRID, facecolor=PANEL,
        transform=ax.transAxes, clip_on=False
    )
    ax.add_patch(rect)

    ax.text(0.05, 0.72, title, color=MUTED, fontsize=11, fontweight='bold', transform=ax.transAxes)
    ax.text(0.05, 0.38, value, color=color, fontsize=20, fontweight='bold', transform=ax.transAxes)
    ax.text(0.05, 0.12, subtitle, color=TXT, fontsize=9, transform=ax.transAxes)

# =========================================================
# 5. KPI CARDS
# =========================================================

ax_kpi1 = fig.add_subplot(gs[0, 0:2])
draw_card(ax_kpi1, "Total Order Value", f"₹{total_order_value/1e7:.2f} Cr", "From VBAP item revenue", GREEN)

ax_kpi2 = fig.add_subplot(gs[0, 2:4])
draw_card(ax_kpi2, "Billed Revenue", f"₹{billed_revenue/1e7:.2f} Cr", "From VBRK billing value", BLUE)

ax_kpi3 = fig.add_subplot(gs[0, 4:6])
draw_card(ax_kpi3, "Unbilled Exposure", f"₹{unbilled_exposure/1e7:.2f} Cr", "Cash stuck in pipeline", RED)

ax_kpi4 = fig.add_subplot(gs[0, 6:8])
draw_card(ax_kpi4, "Avg Lead Time", f"{avg_lead_time:.1f} Days", "Order to goods issue", YELLOW)

ax_kpi5 = fig.add_subplot(gs[0, 8:10])
draw_card(ax_kpi5, "On-Time Delivery", f"{on_time_rate:.1f}%", "SLA threshold ≤ 7 days", GREEN if on_time_rate >= 70 else RED)

ax_kpi6 = fig.add_subplot(gs[0, 10:12])
draw_card(ax_kpi6, "Delivery Rate", f"{delivery_rate:.1f}%", "Orders delivered", BLUE)

# =========================================================
# 6. CHART 1 - REVENUE BY MATERIAL
# =========================================================

ax1 = fig.add_subplot(gs[1, 0:6])
ax1.set_facecolor(PANEL)

materials = rev_by_mat.index.str.replace('MAT-', '', regex=False)
values = rev_by_mat.values / 1e6

bars = ax1.barh(materials[::-1], values[::-1], color=BLUE, edgecolor='none')

for i, v in enumerate(values[::-1]):
    ax1.text(v + 0.05, i, f'₹{v:.2f}M', va='center', color=TXT, fontsize=10)

ax1.set_title('Revenue by Material', color=TXT, fontsize=14, fontweight='bold', pad=12)
ax1.set_xlabel('Revenue (₹ Millions)', color=MUTED)
ax1.tick_params(colors=TXT)
ax1.grid(axis='x', color=GRID, alpha=0.7)
for spine in ax1.spines.values():
    spine.set_color(GRID)

# =========================================================
# 7. CHART 2 - LEAD TIME DISTRIBUTION
# =========================================================

ax2 = fig.add_subplot(gs[1, 6:12])
ax2.set_facecolor(PANEL)

n, bins, patches_hist = ax2.hist(lead_times, bins=20, edgecolor=BG, alpha=0.9)

for patch, left in zip(patches_hist, bins[:-1]):
    if left <= 7:
        patch.set_facecolor(GREEN)
    elif left <= 14:
        patch.set_facecolor(YELLOW)
    else:
        patch.set_facecolor(RED)

ax2.axvline(avg_lead_time, color=TXT, linestyle='--', linewidth=1.6, label=f'Mean: {avg_lead_time:.1f}d')
ax2.axvline(7, color=GREEN, linestyle=':', linewidth=1.5, label='SLA: 7 days')

ax2.set_title('Order-to-Delivery Lead Time Distribution', color=TXT, fontsize=14, fontweight='bold', pad=12)
ax2.set_xlabel('Lead Time (Days)', color=MUTED)
ax2.set_ylabel('Order Count', color=MUTED)
ax2.tick_params(colors=TXT)
ax2.grid(axis='y', color=GRID, alpha=0.7)
for spine in ax2.spines.values():
    spine.set_color(GRID)

legend = ax2.legend(facecolor=PANEL, edgecolor=GRID, fontsize=9)
for text in legend.get_texts():
    text.set_color(TXT)

# =========================================================
# 8. CHART 3 - MONTHLY REVENUE TREND
# =========================================================

ax3 = fig.add_subplot(gs[2, 0:12])
ax3.set_facecolor(PANEL)

x = np.arange(len(monthly))
ax3.plot(x, monthly['Revenue_M'], marker='o', linewidth=2.5, color=BLUE, label='Revenue')
ax3.fill_between(x, monthly['Revenue_M'], color=BLUE, alpha=0.15)

rolling = monthly['Revenue_M'].rolling(3, min_periods=1).mean()
ax3.plot(x, rolling, linestyle='--', linewidth=2, color=RED, label='3-Month Rolling Avg')

ax3.set_xticks(x)
ax3.set_xticklabels(monthly['ORDER_MONTH'], rotation=45, ha='right', color=TXT)
ax3.set_title('Monthly Revenue Trend', color=TXT, fontsize=14, fontweight='bold', pad=12)
ax3.set_ylabel('Revenue (₹ Millions)', color=MUTED)
ax3.tick_params(colors=TXT)
ax3.grid(axis='y', color=GRID, alpha=0.7)
for spine in ax3.spines.values():
    spine.set_color(GRID)

ax3.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'₹{y:.1f}M'))

legend = ax3.legend(facecolor=PANEL, edgecolor=GRID, fontsize=9)
for text in legend.get_texts():
    text.set_color(TXT)

# =========================================================
# 9. FOOTER AND SAVE
# =========================================================

fig.text(
    0.5, 0.01,
    'Simulated SAP Tables: VBAK | VBAP | LIKP | VBRK   •   O2C Analytics Dashboard   •   Values in INR',
    ha='center', color=MUTED, fontsize=10
)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("sap_o2c_dashboard_final.png", dpi=300, bbox_inches='tight', facecolor=BG)
plt.show()

print("Dashboard saved successfully as: sap_o2c_dashboard_final.png")
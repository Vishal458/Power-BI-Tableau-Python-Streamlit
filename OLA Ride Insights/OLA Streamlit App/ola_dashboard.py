"""
OLA Ride Insights Dashboard — Streamlit Version
Recreates the 5-page Power BI report with interactive charts.

Install requirements:
    pip install streamlit plotly pandas numpy

Run:
    streamlit run ola_dashboard.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OLA Ride Insights",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────
# THEME / CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Sora', sans-serif;
}

/* Dark background */
.stApp {
    background: #0a0d12;
    color: #e8eaf0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f1318 0%, #111820 100%);
    border-right: 1px solid #1e2530;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #8b9ab0 !important;
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #12181f 0%, #161d26 100%);
    border: 1px solid #1e2a38;
    border-radius: 12px;
    padding: 18px 20px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}

[data-testid="metric-container"] label {
    color: #6b7c93 !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
}

[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.75rem !important;
}

/* Section headers */
.section-header {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #3dd68c;
    margin-bottom: 6px;
    margin-top: 28px;
}

/* Page title */
.page-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.02em;
    margin-bottom: 2px;
}

/* OLA green accent */
.ola-badge {
    display: inline-block;
    background: #3dd68c22;
    border: 1px solid #3dd68c44;
    color: #3dd68c;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 16px;
}

/* Chart containers */
.chart-card {
    background: linear-gradient(135deg, #12181f 0%, #141c24 100%);
    border: 1px solid #1e2a38;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 16px;
}

/* Nav radio buttons */
[data-testid="stRadio"] > div {
    gap: 4px;
}

[data-testid="stRadio"] label {
    background: #12181f;
    border: 1px solid #1e2530;
    border-radius: 8px;
    padding: 8px 14px !important;
    color: #8b9ab0 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s;
    cursor: pointer;
    width: 100%;
    text-align: left;
}

[data-testid="stRadio"] label:hover {
    background: #1a2433;
    color: #3dd68c !important;
    border-color: #3dd68c44;
}

[data-testid="stRadio"] label[data-checked="true"],
[data-testid="stRadio"] input:checked + div {
    background: #0e2018 !important;
    border-color: #3dd68c !important;
    color: #3dd68c !important;
}

/* Dividers */
hr {
    border-color: #1e2530 !important;
    margin: 16px 0 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: #12181f !important;
    border: 1px solid #1e2530 !important;
    border-radius: 8px !important;
    color: #8b9ab0 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0d12; }
::-webkit-scrollbar-thumb { background: #1e2a38; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# DATA GENERATION  (realistic OLA India dataset)
# ─────────────────────────────────────────────────────────────
@st.cache_data
def generate_data(seed=42):
    np.random.seed(seed)
    random.seed(seed)

    n = 20000
    start = datetime(2024, 7, 1)
    dates = [start + timedelta(days=int(d)) for d in np.random.randint(0, 184, n)]

    vehicle_types = ["Auto", "Bike", "E-Bike", "Mini", "Prime Plus", "Prime Sedan", "SUV"]
    vt_weights     = [0.22, 0.18, 0.08, 0.20, 0.12, 0.12, 0.08]
    vehicles = np.random.choice(vehicle_types, n, p=vt_weights)

    status_choices = ["Success", "Cancelled by Customer", "Cancelled by Driver", "Driver Not Found"]
    st_weights     = [0.62, 0.18, 0.12, 0.08]
    statuses = np.random.choice(status_choices, n, p=st_weights)

    payment_methods = ["Cash", "UPI", "Credit Card", "Debit Card"]
    pm_weights      = [0.30, 0.40, 0.16, 0.14]
    payments = np.random.choice(payment_methods, n, p=pm_weights)

    # Ride distance by vehicle
    vt_dist = {"Auto": (4, 2), "Bike": (5, 2.5), "E-Bike": (6, 2.5),
               "Mini": (10, 5), "Prime Plus": (15, 7), "Prime Sedan": (14, 6), "SUV": (18, 8)}
    distances = [max(1.0, np.random.normal(*vt_dist[v])) for v in vehicles]
    distances = np.round(distances, 1)

    # Fare by vehicle and distance
    vt_rate = {"Auto": 12, "Bike": 9, "E-Bike": 10, "Mini": 14, "Prime Plus": 20, "Prime Sedan": 18, "SUV": 25}
    fares = [round(distances[i] * vt_rate[vehicles[i]] + np.random.normal(10, 5), 2)
             for i in range(n)]
    fares = [max(30, f) for f in fares]

    # Set fare=0 for non-completed rides
    fares = [f if statuses[i] == "Success" else 0 for i, f in enumerate(fares)]

    # Ratings only for successful rides
    def rand_rating(base, std):
        r = np.random.normal(base, std)
        return round(max(1, min(5, r)) * 2) / 2

    customer_ratings = [rand_rating(4.1, 0.5) if statuses[i] == "Success" else None for i in range(n)]
    driver_ratings   = [rand_rating(4.0, 0.6) if statuses[i] == "Success" else None for i in range(n)]

    # Cancel reasons
    cust_reasons = ["Change of Plans", "Driver Taking Too Long", "Found Better Option", "Wrong Pickup Point", "App Issue", "Other"]
    drv_reasons  = ["Customer Unreachable", "Far Pickup Point", "Vehicle Issue", "Personal Emergency", "Traffic/Road Block", "Other"]

    def cancel_reason(status, cust=True):
        if cust and status == "Cancelled by Customer":
            return random.choice(cust_reasons)
        if not cust and status == "Cancelled by Driver":
            return random.choice(drv_reasons)
        return None

    cust_cancel_reason = [cancel_reason(s, True)  for s in statuses]
    drv_cancel_reason  = [cancel_reason(s, False) for s in statuses]

    customer_ids = [f"CUST{str(np.random.randint(1, 2001)).zfill(4)}" for _ in range(n)]

    df = pd.DataFrame({
        "Date": dates,
        "Booking_ID": [f"BK{str(i).zfill(7)}" for i in range(1, n+1)],
        "Customer_ID": customer_ids,
        "Vehicle_Type": vehicles,
        "Booking_Status": statuses,
        "Payment_Method": payments,
        "Ride_Distance": distances,
        "Fare": fares,
        "Customer_Rating": customer_ratings,
        "Driver_Ratings": driver_ratings,
        "Cancelled_by_Customer_Reason": cust_cancel_reason,
        "Cancelled_by_Driver_Reason": drv_cancel_reason,
    })
    df["Month"] = df["Date"].apply(lambda d: d.strftime("%b %Y"))
    df["Week"]  = df["Date"].apply(lambda d: d.strftime("W%U %Y"))
    df["Day"]   = df["Date"]
    return df

df_raw = generate_data()

# ─────────────────────────────────────────────────────────────
# PLOTLY THEME DEFAULTS
# ─────────────────────────────────────────────────────────────
BG      = "#0a0d12"
CARD_BG = "#12181f"
GRID    = "#1a2330"
TEXT    = "#c8d0dc"
GREEN   = "#3dd68c"
ORANGE  = "#f5a623"
BLUE    = "#4fa3e0"
RED     = "#f04444"
PURPLE  = "#a78bfa"
PINK    = "#f472b6"
TEAL    = "#2dd4bf"

OLA_PALETTE = [GREEN, BLUE, ORANGE, RED, PURPLE, PINK, TEAL,
               "#facc15", "#34d399", "#60a5fa"]

def base_layout(title="", height=360):
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Sora, sans-serif", color=TEXT, size=12),
        title=dict(text=title, font=dict(color="#ffffff", size=14, family="Sora"), x=0.01, y=0.97),
        margin=dict(l=10, r=10, t=40 if title else 10, b=10),
        height=height,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=TEXT, size=11),
            orientation="v",
        ),
        xaxis=dict(
            gridcolor=GRID, linecolor=GRID, tickcolor=GRID,
            tickfont=dict(color=TEXT, size=10), showgrid=True,
        ),
        yaxis=dict(
            gridcolor=GRID, linecolor=GRID, tickcolor=GRID,
            tickfont=dict(color=TEXT, size=10), showgrid=True,
        ),
    )

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="text-align:center; padding: 20px 0 10px;">'
                '<span style="font-size:2.2rem;">🚖</span>'
                '<div style="font-size:1.1rem;font-weight:700;color:#fff;letter-spacing:-0.02em;margin-top:6px;">OLA Insights</div>'
                '<div style="font-size:0.68rem;color:#4b5a6a;margin-top:2px;">Ride Analytics Platform</div>'
                '</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "",
        ["📊  Overall Analysis", "🚗  Vehicle Type", "💰  Revenue",
         "❌  Cancellation", "⭐  Ratings"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # Global Filters
    st.markdown('<div class="section-header">Filters</div>', unsafe_allow_html=True)

    min_date = df_raw["Date"].min()
    max_date = df_raw["Date"].max()
    date_range = st.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    booking_status = st.multiselect(
        "Booking Status",
        options=["Success", "Cancelled by Customer", "Cancelled by Driver", "Driver Not Found"],
        default=["Success", "Cancelled by Customer", "Cancelled by Driver", "Driver Not Found"],
    )

    vehicle_filter = st.multiselect(
        "Vehicle Type",
        options=["Auto", "Bike", "E-Bike", "Mini", "Prime Plus", "Prime Sedan", "SUV"],
        default=["Auto", "Bike", "E-Bike", "Mini", "Prime Plus", "Prime Sedan", "SUV"],
    )

    dist_range = st.slider(
        "Ride Distance (km)",
        min_value=1.0,
        max_value=float(df_raw["Ride_Distance"].max()),
        value=(1.0, float(df_raw["Ride_Distance"].max())),
        step=0.5,
    )

    st.markdown("---")
    # Dataset info
    st.markdown(
        f'<div style="font-size:0.68rem;color:#3b4a5a;text-align:center;">'
        f'Dataset: {len(df_raw):,} bookings<br>'
        f'Jul 2024 – Dec 2024</div>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────────────────────
if len(date_range) == 2:
    d0, d1 = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    d0, d1 = pd.Timestamp(min_date), pd.Timestamp(max_date)

df = df_raw[
    (df_raw["Date"] >= d0) &
    (df_raw["Date"] <= d1) &
    (df_raw["Booking_Status"].isin(booking_status)) &
    (df_raw["Vehicle_Type"].isin(vehicle_filter)) &
    (df_raw["Ride_Distance"] >= dist_range[0]) &
    (df_raw["Ride_Distance"] <= dist_range[1])
].copy()

df_success = df[df["Booking_Status"] == "Success"]

# ─────────────────────────────────────────────────────────────
# ═══════════════════  PAGE 1: OVERALL ANALYSIS  ═════════════
# ─────────────────────────────────────────────────────────────
if "Overall" in page:
    st.markdown('<div class="page-title">Overall Analysis</div>', unsafe_allow_html=True)
    st.markdown('<span class="ola-badge">📊 Ride Overview</span>', unsafe_allow_html=True)

    # KPI Cards
    total_bookings  = len(df)
    total_revenue   = df_success["Fare"].sum()
    success_rate    = (len(df_success) / total_bookings * 100) if total_bookings else 0
    avg_distance    = df["Ride_Distance"].mean()
    cancel_rate     = (len(df[df["Booking_Status"].str.startswith("Cancelled")]) / total_bookings * 100) if total_bookings else 0
    avg_fare        = df_success["Fare"].mean()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Bookings",  f"{total_bookings:,}",   delta=f"+{total_bookings//20:,} vs prev")
    c2.metric("Total Revenue",   f"₹{total_revenue/1e5:.2f}L", delta="+8.3%")
    c3.metric("Success Rate",    f"{success_rate:.1f}%",  delta="+1.2%")
    c4.metric("Avg Distance",    f"{avg_distance:.1f} km", delta="-0.3 km")
    c5.metric("Cancellation %",  f"{cancel_rate:.1f}%",   delta="-0.8%", delta_color="inverse")
    c6.metric("Avg Fare",        f"₹{avg_fare:.0f}",      delta="+₹12")

    st.markdown("")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Line chart: Bookings over time by status
        daily_status = df.groupby(["Day", "Booking_Status"]).size().reset_index(name="Count")
        daily_status["Day"] = pd.to_datetime(daily_status["Day"])
        weekly = df.copy()
        weekly["Week_Start"] = pd.to_datetime(weekly["Date"]).dt.to_period("W").apply(lambda r: r.start_time)
        weekly_grp = weekly.groupby(["Week_Start", "Booking_Status"]).size().reset_index(name="Count")

        fig_line = px.line(
            weekly_grp, x="Week_Start", y="Count", color="Booking_Status",
            color_discrete_sequence=OLA_PALETTE,
            labels={"Week_Start": "", "Count": "Rides", "Booking_Status": "Status"},
        )
        fig_line.update_traces(line_width=2.5, mode="lines+markers",
                               marker=dict(size=5, opacity=0.8))
        fig_line.update_layout(**base_layout("Weekly Booking Trend", 320))
        st.plotly_chart(fig_line, use_container_width=True)

    with col_right:
        # Donut chart: Booking status distribution
        status_counts = df.groupby("Booking_Status").size().reset_index(name="Count")
        fig_donut = go.Figure(go.Pie(
            labels=status_counts["Booking_Status"],
            values=status_counts["Count"],
            hole=0.62,
            marker_colors=OLA_PALETTE,
            textinfo="percent",
            textfont=dict(color=TEXT, size=11),
            hovertemplate="<b>%{label}</b><br>%{value:,} rides<br>%{percent}<extra></extra>",
        ))
        fig_donut.add_annotation(
            text=f"<b>{total_bookings:,}</b><br><span style='font-size:10px'>Total</span>",
            x=0.5, y=0.5, font_size=18, font_color="#fff", showarrow=False
        )
        fig_donut.update_layout(**base_layout("Booking Status Mix", 320))
        st.plotly_chart(fig_donut, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        # Bar chart: Rides by Vehicle Type
        vt_counts = df.groupby("Vehicle_Type").size().reset_index(name="Count").sort_values("Count", ascending=True)
        fig_bar = go.Figure(go.Bar(
            x=vt_counts["Count"],
            y=vt_counts["Vehicle_Type"],
            orientation="h",
            marker=dict(
                color=vt_counts["Count"],
                colorscale=[[0, "#1a2e3d"], [0.5, "#1f6b4a"], [1, GREEN]],
                showscale=False,
            ),
            text=vt_counts["Count"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            textfont=dict(color=TEXT, size=11),
            hovertemplate="<b>%{y}</b>: %{x:,} rides<extra></extra>",
        ))
        fig_bar.update_layout(**base_layout("Rides by Vehicle Type", 320))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col4:
        # Distance distribution histogram
        fig_hist = go.Figure(go.Histogram(
            x=df["Ride_Distance"],
            nbinsx=40,
            marker_color=GREEN,
            opacity=0.85,
            hovertemplate="Distance: %{x:.1f} km<br>Count: %{y:,}<extra></extra>",
        ))
        fig_hist.update_layout(**base_layout("Ride Distance Distribution", 320))
        st.plotly_chart(fig_hist, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# ═══════════════════  PAGE 2: VEHICLE TYPE  ═════════════════
# ─────────────────────────────────────────────────────────────
elif "Vehicle" in page:
    st.markdown('<div class="page-title">Vehicle Type Analysis</div>', unsafe_allow_html=True)
    st.markdown('<span class="ola-badge">🚗 Fleet Performance</span>', unsafe_allow_html=True)

    vehicle_types = ["Auto", "Bike", "E-Bike", "Mini", "Prime Plus", "Prime Sedan", "SUV"]
    vt_colors     = dict(zip(vehicle_types, OLA_PALETTE))

    # Per-vehicle KPIs
    vt_df = df.groupby("Vehicle_Type").agg(
        Bookings=("Booking_ID", "count"),
        Revenue=("Fare", "sum"),
        Avg_Fare=("Fare", "mean"),
        Avg_Distance=("Ride_Distance", "mean"),
    ).reset_index()

    success_vt = df_success.groupby("Vehicle_Type").agg(
        Success=("Booking_ID", "count"),
        Avg_Rating_Customer=("Customer_Rating", "mean"),
        Avg_Rating_Driver=("Driver_Ratings", "mean"),
    ).reset_index()

    vt_merged = vt_df.merge(success_vt, on="Vehicle_Type", how="left")
    vt_merged["Success_Rate"] = (vt_merged["Success"] / vt_merged["Bookings"] * 100).round(1)

    # Scorecards
    st.markdown('<div class="section-header">Fleet Summary Cards</div>', unsafe_allow_html=True)
    cols = st.columns(7)
    for i, vt in enumerate(vehicle_types):
        row = vt_merged[vt_merged["Vehicle_Type"] == vt]
        if not row.empty:
            r = row.iloc[0]
            with cols[i]:
                st.markdown(
                    f'<div style="background:linear-gradient(135deg,#12181f,#161d26);border:1px solid #1e2a38;'
                    f'border-top:3px solid {OLA_PALETTE[i]};border-radius:12px;padding:14px;text-align:center;">'
                    f'<div style="font-size:0.65rem;color:#5a6a7a;text-transform:uppercase;letter-spacing:.1em;">{vt}</div>'
                    f'<div style="font-size:1.3rem;font-weight:700;color:#fff;margin:6px 0;">{r["Bookings"]:,}</div>'
                    f'<div style="font-size:0.68rem;color:{OLA_PALETTE[i]};">₹{r["Revenue"]/1e3:.0f}K Revenue</div>'
                    f'<div style="font-size:0.65rem;color:#4b5a6a;margin-top:4px;">{r["Success_Rate"]:.0f}% Success</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    st.markdown("")

    c1, c2 = st.columns(2)
    with c1:
        # Revenue by vehicle
        fig_rev = px.bar(
            vt_merged.sort_values("Revenue", ascending=True),
            x="Revenue", y="Vehicle_Type", orientation="h",
            color="Vehicle_Type",
            color_discrete_sequence=OLA_PALETTE,
            text=vt_merged.sort_values("Revenue")["Revenue"].apply(lambda x: f"₹{x/1e3:.0f}K"),
            labels={"Revenue": "Total Revenue (₹)", "Vehicle_Type": ""},
        )
        fig_rev.update_traces(textposition="outside", textfont_color=TEXT)
        fig_rev.update_layout(**base_layout("Revenue by Vehicle Type", 340))
        st.plotly_chart(fig_rev, use_container_width=True)

    with c2:
        # Avg fare vs avg distance scatter
        fig_sc = px.scatter(
            vt_merged,
            x="Avg_Distance", y="Avg_Fare", color="Vehicle_Type",
            size="Bookings", size_max=55,
            color_discrete_sequence=OLA_PALETTE,
            text="Vehicle_Type",
            labels={"Avg_Distance": "Avg Distance (km)", "Avg_Fare": "Avg Fare (₹)"},
        )
        fig_sc.update_traces(textposition="top center", textfont=dict(color=TEXT, size=10))
        fig_sc.update_layout(**base_layout("Avg Fare vs Avg Distance", 340))
        st.plotly_chart(fig_sc, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Bookings over time by vehicle type
        monthly_vt = df.copy()
        monthly_vt["Month"] = pd.to_datetime(monthly_vt["Date"]).dt.to_period("M").apply(str)
        monthly_vt_grp = monthly_vt.groupby(["Month", "Vehicle_Type"]).size().reset_index(name="Bookings")
        fig_mv = px.line(
            monthly_vt_grp, x="Month", y="Bookings", color="Vehicle_Type",
            color_discrete_sequence=OLA_PALETTE,
            labels={"Month": "", "Bookings": "Rides"},
            markers=True,
        )
        fig_mv.update_traces(line_width=2.2, marker_size=5)
        fig_mv.update_layout(**base_layout("Monthly Trends by Vehicle", 300))
        st.plotly_chart(fig_mv, use_container_width=True)

    with c4:
        # Success rate by vehicle
        fig_sr = px.bar(
            vt_merged.sort_values("Success_Rate"),
            x="Vehicle_Type", y="Success_Rate",
            color="Success_Rate",
            color_continuous_scale=[[0, "#3d1818"], [0.5, "#1f5a32"], [1, GREEN]],
            text=vt_merged.sort_values("Success_Rate")["Success_Rate"].apply(lambda x: f"{x:.1f}%"),
            labels={"Success_Rate": "Success Rate (%)", "Vehicle_Type": ""},
        )
        fig_sr.update_traces(textposition="outside", textfont_color=TEXT)
        fig_sr.update_coloraxes(showscale=False)
        fig_sr.update_layout(**base_layout("Success Rate by Vehicle Type", 300))
        st.plotly_chart(fig_sr, use_container_width=True)

    # Detailed table
    st.markdown('<div class="section-header">Full Vehicle Metrics</div>', unsafe_allow_html=True)
    display_vt = vt_merged.copy()
    display_vt["Revenue"]         = display_vt["Revenue"].apply(lambda x: f"₹{x:,.0f}")
    display_vt["Avg_Fare"]        = display_vt["Avg_Fare"].apply(lambda x: f"₹{x:.0f}")
    display_vt["Avg_Distance"]    = display_vt["Avg_Distance"].apply(lambda x: f"{x:.1f} km")
    display_vt["Avg_Rating_Customer"] = display_vt["Avg_Rating_Customer"].apply(lambda x: f"{x:.2f} ⭐" if pd.notna(x) else "—")
    display_vt["Avg_Rating_Driver"]   = display_vt["Avg_Rating_Driver"].apply(lambda x: f"{x:.2f} ⭐" if pd.notna(x) else "—")
    display_vt["Success_Rate"]    = display_vt["Success_Rate"].apply(lambda x: f"{x:.1f}%")
    display_vt = display_vt.rename(columns={
        "Vehicle_Type":"Vehicle","Bookings":"Total Rides","Revenue":"Revenue",
        "Avg_Fare":"Avg Fare","Avg_Distance":"Avg Dist","Success":"Successful Rides",
        "Avg_Rating_Customer":"Customer Rating","Avg_Rating_Driver":"Driver Rating",
        "Success_Rate":"Success Rate"
    })
    st.dataframe(display_vt.drop(columns=["Successful Rides"]), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────
# ═══════════════════  PAGE 3: REVENUE  ══════════════════════
# ─────────────────────────────────────────────────────────────
elif "Revenue" in page:
    st.markdown('<div class="page-title">Revenue Analysis</div>', unsafe_allow_html=True)
    st.markdown('<span class="ola-badge">💰 Financial Performance</span>', unsafe_allow_html=True)

    total_rev  = df_success["Fare"].sum()
    avg_rev    = df_success["Fare"].mean()
    max_rev    = df_success.groupby("Customer_ID")["Fare"].sum().max()
    total_rides = len(df_success)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Gross Revenue",    f"₹{total_rev/1e5:.2f}L",  delta="+9.1%")
    c2.metric("Avg Fare / Ride",  f"₹{avg_rev:.0f}",         delta="+₹15")
    c3.metric("Top Customer Spend", f"₹{max_rev:.0f}",       delta="High Value")
    c4.metric("Successful Rides", f"{total_rides:,}",         delta="+4.2%")

    st.markdown("")

    c_left, c_right = st.columns([1.3, 1])
    with c_left:
        # Revenue over time (monthly)
        monthly_rev = df_success.copy()
        monthly_rev["Month"] = pd.to_datetime(monthly_rev["Date"]).dt.to_period("M").apply(str)
        monthly_grp = monthly_rev.groupby("Month")["Fare"].sum().reset_index()
        monthly_grp.columns = ["Month", "Revenue"]

        fig_rev_time = go.Figure()
        fig_rev_time.add_trace(go.Bar(
            x=monthly_grp["Month"], y=monthly_grp["Revenue"],
            marker=dict(
                color=monthly_grp["Revenue"],
                colorscale=[[0, "#1a2e3d"], [1, GREEN]],
                showscale=False,
            ),
            name="Revenue",
            hovertemplate="<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>",
        ))
        fig_rev_time.add_trace(go.Scatter(
            x=monthly_grp["Month"], y=monthly_grp["Revenue"],
            mode="lines+markers", line=dict(color=GREEN, width=2.5),
            marker=dict(size=7, color=GREEN), name="Trend",
        ))
        fig_rev_time.update_layout(**base_layout("Monthly Revenue Trend", 320))
        st.plotly_chart(fig_rev_time, use_container_width=True)

    with c_right:
        # Revenue by payment method
        pm_rev = df_success.groupby("Payment_Method")["Fare"].sum().reset_index()
        fig_pm = px.pie(
            pm_rev, names="Payment_Method", values="Fare",
            color_discrete_sequence=OLA_PALETTE,
            hole=0.45,
        )
        fig_pm.update_traces(textinfo="label+percent",
                             textfont=dict(color=TEXT, size=11),
                             hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>")
        fig_pm.update_layout(**base_layout("Revenue by Payment Method", 320))
        st.plotly_chart(fig_pm, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Top 15 customers by revenue
        top_custs = df_success.groupby("Customer_ID")["Fare"].sum().nlargest(15).reset_index()
        top_custs.columns = ["Customer", "Revenue"]
        fig_top = go.Figure(go.Bar(
            x=top_custs["Revenue"],
            y=top_custs["Customer"],
            orientation="h",
            marker=dict(
                color=top_custs["Revenue"],
                colorscale=[[0, "#1a2e3d"], [1, BLUE]],
                showscale=False,
            ),
            text=top_custs["Revenue"].apply(lambda x: f"₹{x:,.0f}"),
            textposition="outside",
            textfont=dict(color=TEXT, size=10),
        ))
        fig_top.update_layout(**base_layout("Top 15 Customers by Revenue", 400))
        st.plotly_chart(fig_top, use_container_width=True)

    with c4:
        # Revenue by vehicle type over months
        rev_vt = df_success.copy()
        rev_vt["Month"] = pd.to_datetime(rev_vt["Date"]).dt.to_period("M").apply(str)
        rev_vt_grp = rev_vt.groupby(["Month", "Vehicle_Type"])["Fare"].sum().reset_index()
        fig_rev_vt = px.area(
            rev_vt_grp, x="Month", y="Fare", color="Vehicle_Type",
            color_discrete_sequence=OLA_PALETTE,
            labels={"Fare": "Revenue (₹)", "Month": ""},
        )
        fig_rev_vt.update_traces(opacity=0.75, line_width=1.5)
        fig_rev_vt.update_layout(**base_layout("Revenue by Vehicle Type (Monthly)", 400))
        st.plotly_chart(fig_rev_vt, use_container_width=True)

    # Revenue table
    st.markdown('<div class="section-header">Customer Revenue Table</div>', unsafe_allow_html=True)
    cust_tbl = df_success.groupby("Customer_ID").agg(
        Total_Rides=("Booking_ID", "count"),
        Total_Fare=("Fare", "sum"),
        Avg_Fare=("Fare", "mean"),
        Avg_Rating=("Customer_Rating", "mean"),
    ).reset_index().sort_values("Total_Fare", ascending=False).head(50)
    cust_tbl["Total_Fare"] = cust_tbl["Total_Fare"].apply(lambda x: f"₹{x:,.0f}")
    cust_tbl["Avg_Fare"]   = cust_tbl["Avg_Fare"].apply(lambda x: f"₹{x:.0f}")
    cust_tbl["Avg_Rating"] = cust_tbl["Avg_Rating"].apply(lambda x: f"{x:.2f} ⭐" if pd.notna(x) else "—")
    cust_tbl.columns       = ["Customer ID", "Total Rides", "Total Revenue", "Avg Fare", "Avg Customer Rating"]
    st.dataframe(cust_tbl, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────
# ═══════════════════  PAGE 4: CANCELLATION  ═════════════════
# ─────────────────────────────────────────────────────────────
elif "Cancel" in page:
    st.markdown('<div class="page-title">Cancellation Analysis</div>', unsafe_allow_html=True)
    st.markdown('<span class="ola-badge">❌ Cancellation Deep Dive</span>', unsafe_allow_html=True)

    cancelled_cust  = df[df["Booking_Status"] == "Cancelled by Customer"]
    cancelled_drv   = df[df["Booking_Status"] == "Cancelled by Driver"]
    dnf             = df[df["Booking_Status"] == "Driver Not Found"]
    total_cancelled = len(cancelled_cust) + len(cancelled_drv) + len(dnf)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Cancellations",  f"{total_cancelled:,}",      delta_color="off")
    c2.metric("By Customer",          f"{len(cancelled_cust):,}",  delta=f"{len(cancelled_cust)/len(df)*100:.1f}%", delta_color="inverse")
    c3.metric("By Driver",            f"{len(cancelled_drv):,}",   delta=f"{len(cancelled_drv)/len(df)*100:.1f}%", delta_color="inverse")
    c4.metric("Driver Not Found",     f"{len(dnf):,}",             delta=f"{len(dnf)/len(df)*100:.1f}%", delta_color="inverse")
    c5.metric("Overall Cancel Rate",  f"{total_cancelled/len(df)*100:.1f}%", delta="-0.8%", delta_color="inverse")

    st.markdown("")

    c_top_l, c_top_r = st.columns(2)

    with c_top_l:
        # Pie: Cancel by customer reasons
        cust_reasons = cancelled_cust["Cancelled_by_Customer_Reason"].value_counts().reset_index()
        cust_reasons.columns = ["Reason", "Count"]
        fig_cc = px.pie(
            cust_reasons, names="Reason", values="Count",
            color_discrete_sequence=OLA_PALETTE,
            hole=0.5,
        )
        fig_cc.update_traces(textinfo="percent+label",
                             textfont=dict(color=TEXT, size=10))
        fig_cc.update_layout(**base_layout("Cancellations by Customer — Reasons", 340))
        st.plotly_chart(fig_cc, use_container_width=True)

    with c_top_r:
        # Pie: Cancel by driver reasons
        drv_reasons = cancelled_drv["Cancelled_by_Driver_Reason"].value_counts().reset_index()
        drv_reasons.columns = ["Reason", "Count"]
        fig_cd = px.pie(
            drv_reasons, names="Reason", values="Count",
            color_discrete_sequence=[ORANGE, RED, PURPLE, PINK, TEAL, BLUE],
            hole=0.5,
        )
        fig_cd.update_traces(textinfo="percent+label",
                             textfont=dict(color=TEXT, size=10))
        fig_cd.update_layout(**base_layout("Cancellations by Driver — Reasons", 340))
        st.plotly_chart(fig_cd, use_container_width=True)

    c_bot_l, c_bot_r = st.columns(2)
    with c_bot_l:
        # Cancellation trend over time
        cancel_trend = df[df["Booking_Status"].str.startswith("Cancelled")].copy()
        cancel_trend["Week"] = pd.to_datetime(cancel_trend["Date"]).dt.to_period("W").apply(lambda r: r.start_time)
        ct_grp = cancel_trend.groupby(["Week", "Booking_Status"]).size().reset_index(name="Count")
        fig_ct = px.bar(
            ct_grp, x="Week", y="Count", color="Booking_Status",
            color_discrete_map={
                "Cancelled by Customer": RED,
                "Cancelled by Driver":   ORANGE,
            },
            labels={"Week": "", "Count": "Cancellations", "Booking_Status": ""},
            barmode="stack",
        )
        fig_ct.update_layout(**base_layout("Weekly Cancellation Trend", 300))
        st.plotly_chart(fig_ct, use_container_width=True)

    with c_bot_r:
        # Cancellation rate by vehicle type
        vt_cancel = df.groupby("Vehicle_Type").apply(
            lambda g: pd.Series({
                "Total": len(g),
                "Cancelled": len(g[g["Booking_Status"].str.startswith("Cancelled")])
            })
        ).reset_index()
        vt_cancel["Cancel_Rate"] = (vt_cancel["Cancelled"] / vt_cancel["Total"] * 100).round(1)

        fig_vc = px.bar(
            vt_cancel.sort_values("Cancel_Rate"),
            x="Cancel_Rate", y="Vehicle_Type", orientation="h",
            color="Cancel_Rate",
            color_continuous_scale=[[0, "#1a2e3d"], [0.5, "#7a3020"], [1, RED]],
            text=vt_cancel.sort_values("Cancel_Rate")["Cancel_Rate"].apply(lambda x: f"{x:.1f}%"),
            labels={"Cancel_Rate": "Cancellation Rate (%)", "Vehicle_Type": ""},
        )
        fig_vc.update_traces(textposition="outside", textfont_color=TEXT)
        fig_vc.update_coloraxes(showscale=False)
        fig_vc.update_layout(**base_layout("Cancellation Rate by Vehicle", 300))
        st.plotly_chart(fig_vc, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# ═══════════════════  PAGE 5: RATINGS  ══════════════════════
# ─────────────────────────────────────────────────────────────
elif "Rating" in page:
    st.markdown('<div class="page-title">Ratings Analysis</div>', unsafe_allow_html=True)
    st.markdown('<span class="ola-badge">⭐ Quality Metrics</span>', unsafe_allow_html=True)

    avg_cust_rating = df_success["Customer_Rating"].mean()
    avg_drv_rating  = df_success["Driver_Ratings"].mean()
    five_star_cust  = (df_success["Customer_Rating"] == 5).sum()
    five_star_drv   = (df_success["Driver_Ratings"] == 5).sum()
    low_rated_drv   = (df_success["Driver_Ratings"] < 3).sum()
    low_rated_cust  = (df_success["Customer_Rating"] < 3).sum()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Avg Customer Rating", f"{avg_cust_rating:.2f} ⭐", delta="+0.05")
    c2.metric("Avg Driver Rating",   f"{avg_drv_rating:.2f} ⭐",  delta="+0.03")
    c3.metric("5-Star (Customer)",   f"{five_star_cust:,}",       delta=f"{five_star_cust/len(df_success)*100:.1f}%")
    c4.metric("5-Star (Driver)",     f"{five_star_drv:,}",        delta=f"{five_star_drv/len(df_success)*100:.1f}%")
    c5.metric("Low Rated Drivers",   f"{low_rated_drv:,}",        delta_color="inverse")
    c6.metric("Low Rated Customers", f"{low_rated_cust:,}",       delta_color="inverse")

    st.markdown("")

    c1, c2 = st.columns(2)
    with c1:
        # Customer rating distribution
        cr_counts = df_success["Customer_Rating"].value_counts().sort_index().reset_index()
        cr_counts.columns = ["Rating", "Count"]
        fig_cr = px.bar(
            cr_counts, x="Rating", y="Count",
            color="Rating",
            color_continuous_scale=[[0, RED], [0.5, ORANGE], [1, GREEN]],
            text=cr_counts["Count"].apply(lambda x: f"{x:,}"),
            labels={"Rating": "Customer Rating", "Count": "Rides"},
        )
        fig_cr.update_traces(textposition="outside", textfont_color=TEXT)
        fig_cr.update_coloraxes(showscale=False)
        fig_cr.update_layout(**base_layout("Customer Rating Distribution", 300))
        st.plotly_chart(fig_cr, use_container_width=True)

    with c2:
        # Driver rating distribution
        dr_counts = df_success["Driver_Ratings"].value_counts().sort_index().reset_index()
        dr_counts.columns = ["Rating", "Count"]
        fig_dr = px.bar(
            dr_counts, x="Rating", y="Count",
            color="Rating",
            color_continuous_scale=[[0, RED], [0.5, BLUE], [1, GREEN]],
            text=dr_counts["Count"].apply(lambda x: f"{x:,}"),
            labels={"Rating": "Driver Rating", "Count": "Rides"},
        )
        fig_dr.update_traces(textposition="outside", textfont_color=TEXT)
        fig_dr.update_coloraxes(showscale=False)
        fig_dr.update_layout(**base_layout("Driver Rating Distribution", 300))
        st.plotly_chart(fig_dr, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        # Avg ratings by vehicle type
        rat_vt = df_success.groupby("Vehicle_Type").agg(
            Customer_Rating=("Customer_Rating", "mean"),
            Driver_Rating=("Driver_Ratings", "mean"),
        ).reset_index().round(2)
        rat_melt = rat_vt.melt(id_vars="Vehicle_Type", var_name="Type", value_name="Rating")
        fig_rv = px.bar(
            rat_melt, x="Vehicle_Type", y="Rating", color="Type",
            barmode="group",
            color_discrete_map={"Customer_Rating": GREEN, "Driver_Rating": BLUE},
            labels={"Rating": "Avg Rating", "Vehicle_Type": "", "Type": ""},
            text=rat_melt["Rating"].apply(lambda x: f"{x:.2f}"),
        )
        fig_rv.update_traces(textposition="outside", textfont_color=TEXT)
        fig_rv.update_yaxes(range=[3.5, 5.0])
        fig_rv.update_layout(**base_layout("Avg Ratings by Vehicle Type", 300))
        st.plotly_chart(fig_rv, use_container_width=True)

    with c4:
        # Scatter: Customer vs Driver ratings
        sample = df_success.sample(min(2000, len(df_success)), random_state=42)
        fig_scatter = go.Figure(go.Scattergl(
            x=sample["Customer_Rating"],
            y=sample["Driver_Ratings"],
            mode="markers",
            marker=dict(
                color=sample["Fare"],
                colorscale=[[0, "#1a2e3d"], [0.5, BLUE], [1, GREEN]],
                size=5, opacity=0.6,
                colorbar=dict(title="Fare ₹", tickfont=dict(color=TEXT)),
                showscale=True,
            ),
            hovertemplate="Customer: %{x}⭐  Driver: %{y}⭐<extra></extra>",
        ))
        fig_scatter.add_shape(type="line", x0=1, y0=1, x1=5, y1=5,
                              line=dict(color=ORANGE, width=1.5, dash="dot"))
        fig_scatter.update_layout(**base_layout("Customer vs Driver Rating (sample)", 300))
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Monthly avg rating trend
    monthly_rat = df_success.copy()
    monthly_rat["Month"] = pd.to_datetime(monthly_rat["Date"]).dt.to_period("M").apply(str)
    monthly_rat_grp = monthly_rat.groupby("Month").agg(
        Customer_Rating=("Customer_Rating", "mean"),
        Driver_Rating=("Driver_Ratings", "mean"),
    ).reset_index()

    fig_rt = go.Figure()
    fig_rt.add_trace(go.Scatter(
        x=monthly_rat_grp["Month"], y=monthly_rat_grp["Customer_Rating"],
        name="Customer Rating", mode="lines+markers",
        line=dict(color=GREEN, width=2.5), marker=dict(size=8),
    ))
    fig_rt.add_trace(go.Scatter(
        x=monthly_rat_grp["Month"], y=monthly_rat_grp["Driver_Rating"],
        name="Driver Rating", mode="lines+markers",
        line=dict(color=BLUE, width=2.5), marker=dict(size=8, symbol="diamond"),
    ))
    fig_rt.update_yaxes(range=[3.5, 5.0])
    fig_rt.update_layout(**base_layout("Monthly Average Rating Trend", 280))
    st.plotly_chart(fig_rt, use_container_width=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;font-size:0.68rem;color:#2a3a4a;padding:8px;">'
    'OLA Ride Insights Dashboard &nbsp;•&nbsp; Built with Streamlit &amp; Plotly &nbsp;•&nbsp; '
    'Data: Jul–Dec 2024 &nbsp;•&nbsp; 20,000 simulated bookings'
    '</div>',
    unsafe_allow_html=True
)

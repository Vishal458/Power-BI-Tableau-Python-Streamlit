"""
Bird Species Observation Dashboard — Streamlit Version
Recreates the 2-page Power BI report with full interactivity.

Install:
    pip install streamlit plotly pandas numpy

Run:
    streamlit run bird_dashboard.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import random

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Bird Species Observation",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# THEME / CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

.stApp {
    background: #060c0a;
    color: #d4e8d8;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080f0c 0%, #0a1410 100%);
    border-right: 1px solid #162418;
}
[data-testid="stSidebar"] * { color: #6b8a72 !important; }
[data-testid="stSidebar"] .stMultiSelect span,
[data-testid="stSidebar"] .stSelectbox span { color: #c2d9c7 !important; }

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1a10 0%, #0f1f13 100%);
    border: 1px solid #1a2e1e;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
}
[data-testid="metric-container"] label {
    color: #4d7055 !important;
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #a8f0b8 !important;
    font-size: 1.7rem !important;
    font-weight: 800 !important;
    font-family: 'Fira Code', monospace !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.72rem !important;
}

.page-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #e8f5ea;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
    line-height: 1.2;
}
.page-subtitle {
    font-size: 0.72rem;
    color: #3a5c40;
    margin-bottom: 18px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

[data-testid="stRadio"] > div { gap: 5px; }
[data-testid="stRadio"] label {
    background: #0d1a10 !important;
    border: 1px solid #162418 !important;
    border-radius: 9px !important;
    padding: 9px 14px !important;
    color: #5a7860 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    width: 100%;
    transition: all 0.18s;
}
[data-testid="stRadio"] label:hover {
    background: #122016 !important;
    color: #a8f0b8 !important;
    border-color: #2a5c35 !important;
}

.sec-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #3a7a50;
    margin-top: 22px;
    margin-bottom: 6px;
}

hr { border-color: #162418 !important; margin: 14px 0 !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #060c0a; }
::-webkit-scrollbar-thumb { background: #1a2e1e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# DATA GENERATION
# ──────────────────────────────────────────────
@st.cache_data
def generate_bird_data(seed=7):
    np.random.seed(seed)
    random.seed(seed)

    species = [
        ("American Robin",          "Turdus migratorius"),
        ("Song Sparrow",            "Melospiza melodia"),
        ("Red-winged Blackbird",    "Agelaius phoeniceus"),
        ("Common Yellowthroat",     "Geothlypis trichas"),
        ("Eastern Meadowlark",      "Sturnella magna"),
        ("Bobolink",                "Dolichonyx oryzivorus"),
        ("Grasshopper Sparrow",     "Ammodramus savannarum"),
        ("Indigo Bunting",          "Passerina cyanea"),
        ("Yellow Warbler",          "Setophaga petechia"),
        ("Baltimore Oriole",        "Icterus galbula"),
        ("Cedar Waxwing",           "Bombycilla cedrorum"),
        ("Downy Woodpecker",        "Picoides pubescens"),
        ("Black-capped Chickadee",  "Poecile atricapillus"),
        ("House Finch",             "Haemorhous mexicanus"),
        ("American Goldfinch",      "Spinus tristis"),
        ("Dark-eyed Junco",         "Junco hyemalis"),
        ("White-throated Sparrow",  "Zonotrichia albicollis"),
        ("Hermit Thrush",           "Catharus guttatus"),
        ("Ovenbird",                "Seiurus aurocapilla"),
        ("Wood Thrush",             "Hylocichla mustelina"),
        ("Scarlet Tanager",         "Piranga olivacea"),
        ("Rose-breasted Grosbeak",  "Pheucticus ludovicianus"),
        ("American Kestrel",        "Falco sparverius"),
        ("Barn Swallow",            "Hirundo rustica"),
        ("Tree Swallow",            "Tachycineta bicolor"),
        ("Northern Harrier",        "Circus hudsonius"),
        ("Red-tailed Hawk",         "Buteo jamaicensis"),
        ("Great Blue Heron",        "Ardea herodias"),
        ("Killdeer",                "Charadrius vociferus"),
        ("Belted Kingfisher",       "Megaceryle alcyon"),
    ]

    habitat_types   = ["Forest", "Grassland", "Wetland", "Shrubland", "Agricultural", "Urban Edge"]
    habitat_weights = [0.25, 0.22, 0.18, 0.15, 0.12, 0.08]
    admin_units     = [
        ("Pennsylvania","PA"), ("New York","NY"), ("Virginia","VA"),
        ("Ohio","OH"), ("Michigan","MI"), ("Wisconsin","WI"),
        ("Minnesota","MN"), ("Maryland","MD"), ("West Virginia","WV"), ("North Carolina","NC"),
    ]
    id_methods  = ["Visual", "Vocalization", "Both Visual & Vocal", "Unknown"]
    id_weights  = [0.30, 0.42, 0.22, 0.06]
    sky_conds   = ["Clear", "Partly Cloudy", "Overcast", "Light Rain"]
    sky_weights = [0.42, 0.31, 0.18, 0.09]
    pif_stats   = ["Not on List", "Watch List", "Common Species in Steep Decline", "Yellow List"]
    pif_weights = [0.48, 0.25, 0.15, 0.12]
    stew_stats  = ["N/A", "High Responsibility", "Moderate Responsibility", "Low Responsibility"]
    stew_weights= [0.52, 0.20, 0.18, 0.10]
    sex_vals    = ["Male", "Female", "Unknown"]
    sex_weights = [0.38, 0.28, 0.34]
    loc_types   = ["Off-Road", "Roadside"]

    habitat_affinity = {
        "Forest":      ["Downy Woodpecker","Black-capped Chickadee","Ovenbird","Wood Thrush",
                         "Hermit Thrush","Scarlet Tanager","Rose-breasted Grosbeak"],
        "Grassland":   ["Eastern Meadowlark","Bobolink","Grasshopper Sparrow",
                         "American Kestrel","Northern Harrier","Killdeer"],
        "Wetland":     ["Red-winged Blackbird","Common Yellowthroat","Great Blue Heron",
                         "Belted Kingfisher","Barn Swallow","Tree Swallow"],
        "Shrubland":   ["Song Sparrow","Indigo Bunting","Yellow Warbler","American Robin","House Finch"],
        "Agricultural":["Bobolink","Eastern Meadowlark","American Kestrel","Song Sparrow","Killdeer"],
        "Urban Edge":  ["American Robin","House Finch","American Goldfinch","Cedar Waxwing","Baltimore Oriole"],
    }

    n = 6000
    rows = []
    all_names = [s[0] for s in species]

    for _ in range(n):
        habitat    = np.random.choice(habitat_types, p=habitat_weights)
        affinity   = habitat_affinity[habitat]
        weights    = [5 if nm in affinity else 1 for nm in all_names]
        total_w    = sum(weights)
        probs      = [w / total_w for w in weights]
        sp_idx     = np.random.choice(len(species), p=probs)
        common, scientific = species[sp_idx]

        admin_idx         = np.random.randint(len(admin_units))
        admin_unit, admin_code = admin_units[admin_idx]
        sky               = np.random.choice(sky_conds, p=sky_weights)
        sky_mult          = {"Clear": 1.3, "Partly Cloudy": 1.0, "Overcast": 0.8, "Light Rain": 0.5}[sky]
        total_birds_val   = max(1, int(np.random.negative_binomial(3, 0.45) * sky_mult))
        distance          = float(np.random.choice([0, 25, 50, 75, 100], p=[0.15, 0.25, 0.28, 0.20, 0.12]))
        interval          = int(np.random.choice([1, 2, 3, 4, 5, 6]))
        loc_type          = np.random.choice(loc_types, p=[0.60, 0.40])
        id_meth           = np.random.choice(id_methods, p=id_weights)
        pif               = np.random.choice(pif_stats, p=pif_weights)
        stew              = np.random.choice(stew_stats, p=stew_weights)
        sex               = np.random.choice(sex_vals, p=sex_weights)
        flyover           = np.random.choice(["Yes", "No"], p=[0.12, 0.88])

        rows.append({
            "common_name":                  common,
            "scientific_name":              scientific,
            "habitat_type":                 habitat,
            "admin_unit":                   admin_unit,
            "admin_unit_code":              admin_code,
            "sky":                          sky,
            "total_birds":                  total_birds_val,
            "distance":                     distance,
            "interval_length":              interval,
            "location_type":                loc_type,
            "id_method":                    id_meth,
            "pif_watchlist_status":         pif,
            "regional_stewardship_status":  stew,
            "sex":                          sex,
            "flyover_observed":             flyover,
        })

    return pd.DataFrame(rows)


df_raw = generate_bird_data()

# ──────────────────────────────────────────────
# COLOUR PALETTE
# ──────────────────────────────────────────────
BG     = "#060c0a"
GRID   = "#111e14"
TEXT   = "#8fb896"
WHITE  = "#e8f5ea"
G1     = "#a8f0b8"
G2     = "#4caf70"
AMBER  = "#f5c842"
TEAL   = "#3dd4c0"
BLUE   = "#5ba3d4"
RED    = "#f07070"
PURPLE = "#b08af0"
ORANGE = "#f0a050"
ROSE   = "#f07898"

PALETTE = [G1, TEAL, AMBER, BLUE, PURPLE, ORANGE, RED, ROSE,
           "#70d0f0", "#90e87a", "#f0d080", "#c890f0"]


def blayout(title="", h=340):
    """Base Plotly layout for dark forest theme."""
    d = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans, sans-serif", color=TEXT, size=11),
        margin=dict(l=8, r=8, t=40 if title else 12, b=8),
        height=h,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, size=10)),
        xaxis=dict(gridcolor=GRID, linecolor=GRID, tickcolor=GRID,
                   tickfont=dict(color=TEXT, size=10), showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=GRID, linecolor=GRID, tickcolor=GRID,
                   tickfont=dict(color=TEXT, size=10), showgrid=True, zeroline=False),
    )
    if title:
        d["title"] = dict(
            text=title,
            font=dict(color=WHITE, size=13, family="Plus Jakarta Sans"),
            x=0.01, y=0.97,
        )
    return d


def pie_layout(title="", h=300):
    d = blayout(title, h)
    d.pop("xaxis", None)
    d.pop("yaxis", None)
    return d


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:24px 0 12px;">'
        '<div style="font-size:2.6rem;">🦅</div>'
        '<div style="font-size:1.05rem;font-weight:800;color:#e8f5ea;letter-spacing:-0.02em;margin-top:6px;">'
        'Bird Observations</div>'
        '<div style="font-size:0.65rem;color:#2d4d34;margin-top:2px;letter-spacing:.08em;">'
        'SPECIES ANALYTICS PLATFORM</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown('<div class="sec-label">Navigation</div>', unsafe_allow_html=True)
    page = st.radio(
        "",
        ["🗺️  Distribution & Environment", "🔬  Species & Behavior"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown('<div class="sec-label">Filters</div>', unsafe_allow_html=True)

    all_habitats = sorted(df_raw["habitat_type"].unique().tolist())
    all_units    = sorted(df_raw["admin_unit"].unique().tolist())
    all_species  = sorted(df_raw["common_name"].unique().tolist())
    all_sky      = sorted(df_raw["sky"].unique().tolist())
    all_loc      = sorted(df_raw["location_type"].unique().tolist())

    sel_habitat = st.multiselect("Habitat Type",      options=all_habitats, default=all_habitats)
    sel_unit    = st.multiselect("State",             options=all_units,    default=all_units)
    sel_species = st.multiselect("Species",           options=all_species,  default=all_species)
    sel_sky     = st.multiselect("Sky Condition",     options=all_sky,      default=all_sky)
    sel_loc     = st.multiselect("Location Type",     options=all_loc,      default=all_loc)

    st.markdown("---")
    st.markdown(
        f'<div style="font-size:0.65rem;color:#1e3a24;text-align:center;">'
        f'Dataset: {len(df_raw):,} observations<br>'
        f'{df_raw["common_name"].nunique()} species · 10 states</div>',
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────
# APPLY FILTERS (with empty-guard)
# ──────────────────────────────────────────────
sel_habitat = sel_habitat or all_habitats
sel_unit    = sel_unit    or all_units
sel_species = sel_species or all_species
sel_sky     = sel_sky     or all_sky
sel_loc     = sel_loc     or all_loc

df = df_raw[
    df_raw["habitat_type"].isin(sel_habitat) &
    df_raw["admin_unit"].isin(sel_unit) &
    df_raw["common_name"].isin(sel_species) &
    df_raw["sky"].isin(sel_sky) &
    df_raw["location_type"].isin(sel_loc)
].copy()

if df.empty:
    st.warning("⚠️ No data matches the selected filters — showing the full dataset instead.")
    df = df_raw.copy()


# ══════════════════════════════════════════════════════════════
# PAGE 1 — DISTRIBUTION & ENVIRONMENTAL ANALYSIS
# ══════════════════════════════════════════════════════════════
if "Distribution" in page:
    st.markdown('<div class="page-title">Bird Distribution & Environmental Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">🗺️  Habitat · Geography · Weather Conditions</div>', unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────
    total_obs   = len(df)
    total_birds = int(df["total_birds"].sum())
    unique_spp  = df["common_name"].nunique()
    avg_birds   = df["total_birds"].mean()
    top_habitat = df.groupby("habitat_type")["total_birds"].sum().idxmax()
    top_state   = df.groupby("admin_unit")["total_birds"].sum().idxmax()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Observations", f"{total_obs:,}")
    c2.metric("Total Birds",        f"{total_birds:,}")
    c3.metric("Unique Species",     str(unique_spp))
    c4.metric("Avg Birds / Obs",    f"{avg_birds:.1f}")
    c5.metric("Top Habitat",        top_habitat)
    c6.metric("Top State",          top_state)

    st.markdown("")

    # ── Row 1: Habitat bar + State bar ────────
    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        hab = df.groupby("habitat_type")["total_birds"].sum().reset_index()
        hab.columns = ["Habitat", "Birds"]
        hab = hab.sort_values("Birds", ascending=False)

        fig = go.Figure(go.Bar(
            x=hab["Habitat"], y=hab["Birds"],
            marker=dict(
                color=hab["Birds"].tolist(),
                colorscale=[[0, "#0d2214"], [0.4, "#1f6b3a"], [1, G1]],
                showscale=False,
            ),
            text=[f"{v:,}" for v in hab["Birds"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=10),
            hovertemplate="<b>%{x}</b><br>%{y:,} birds<extra></extra>",
        ))
        fig.update_layout(**blayout("Total Birds by Habitat Type", 320))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        adm = df.groupby("admin_unit")["total_birds"].sum().reset_index()
        adm.columns = ["State", "Birds"]
        adm = adm.sort_values("Birds")

        fig2 = go.Figure(go.Bar(
            x=adm["Birds"], y=adm["State"],
            orientation="h",
            marker=dict(
                color=adm["Birds"].tolist(),
                colorscale=[[0, "#0d2214"], [0.5, "#257a40"], [1, TEAL]],
                showscale=False,
            ),
            text=[f"{v:,}" for v in adm["Birds"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=9),
            hovertemplate="<b>%{y}</b><br>%{x:,} birds<extra></extra>",
        ))
        fig2.update_layout(**blayout("Birds by State", 320))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: Interval line + Sky stacked bar ─
    col_c, col_d = st.columns(2)

    with col_c:
        intv = (
            df.groupby(["interval_length", "location_type"])
            .size()
            .reset_index(name="Observations")
            .sort_values("interval_length")
        )
        fig3 = go.Figure()
        loc_colors = {"Off-Road": G1, "Roadside": AMBER}
        for loc in sorted(intv["location_type"].unique()):
            sub = intv[intv["location_type"] == loc]
            col_c_color = loc_colors.get(loc, BLUE)
            fig3.add_trace(go.Scatter(
                x=sub["interval_length"].tolist(),
                y=sub["Observations"].tolist(),
                name=loc,
                mode="lines+markers",
                line=dict(color=col_c_color, width=2.5),
                marker=dict(size=8, color=col_c_color, line=dict(color=BG, width=1.5)),
                hovertemplate=f"<b>{loc}</b><br>Interval %{{x}} min — %{{y:,}} obs<extra></extra>",
            ))
        fig3.update_layout(**blayout("Observations by Interval Length & Location Type", 300))
        fig3.update_xaxes(title_text="Interval Length (min)", title_font=dict(color=TEXT, size=10))
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        sky_order = ["Clear", "Partly Cloudy", "Overcast", "Light Rain"]
        sky_hab = (
            df.groupby(["sky", "habitat_type"])["total_birds"]
            .sum()
            .reset_index()
        )
        sky_hab["sky"] = pd.Categorical(sky_hab["sky"], categories=sky_order, ordered=True)
        sky_hab = sky_hab.sort_values("sky")

        fig4 = px.bar(
            sky_hab, x="sky", y="total_birds", color="habitat_type",
            color_discrete_sequence=PALETTE,
            labels={"sky": "Sky Condition", "total_birds": "Birds", "habitat_type": "Habitat"},
            barmode="stack",
        )
        fig4.update_layout(**blayout("Birds by Sky Condition & Habitat", 300))
        fig4.update_traces(hovertemplate="<b>%{fullData.name}</b><br>%{y:,} birds<extra></extra>")
        st.plotly_chart(fig4, use_container_width=True)

    # ── Row 3: Species by interval line ───────
    st.markdown('<div class="sec-label">Top 6 Species — Bird Count by Interval Length</div>', unsafe_allow_html=True)

    top6 = df.groupby("common_name")["total_birds"].sum().nlargest(6).index.tolist()
    sp_intv = (
        df[df["common_name"].isin(top6)]
        .groupby(["interval_length", "common_name"])["total_birds"]
        .sum()
        .reset_index()
        .sort_values("interval_length")
    )
    fig5 = px.line(
        sp_intv, x="interval_length", y="total_birds", color="common_name",
        color_discrete_sequence=PALETTE,
        markers=True,
        labels={"interval_length": "Interval Length (min)", "total_birds": "Total Birds", "common_name": "Species"},
    )
    fig5.update_traces(line_width=2.2, marker_size=7)
    fig5.update_layout(**blayout("", 280))
    st.plotly_chart(fig5, use_container_width=True)

    # ── Summary table ─────────────────────────
    st.markdown('<div class="sec-label">Habitat × State Summary</div>', unsafe_allow_html=True)
    summary = (
        df.groupby(["habitat_type", "admin_unit"])
        .agg(
            Observations=("total_birds", "count"),
            Total_Birds=("total_birds", "sum"),
            Avg_Birds=("total_birds", "mean"),
            Species=("common_name", "nunique"),
        )
        .reset_index()
        .sort_values("Total_Birds", ascending=False)
        .head(30)
    )
    summary["Avg_Birds"] = summary["Avg_Birds"].round(1)
    summary.columns = ["Habitat", "State", "Observations", "Total Birds", "Avg Birds/Obs", "Species Count"]
    st.dataframe(summary, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
# PAGE 2 — SPECIES & BEHAVIOR ANALYSIS
# ══════════════════════════════════════════════════════════════
else:
    st.markdown('<div class="page-title">Species & Behavior Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">🔬  Species · ID Method · Conservation Status · Behaviour</div>', unsafe_allow_html=True)

    # ── KPIs ──────────────────────────────────
    total_obs   = len(df)
    total_birds = int(df["total_birds"].sum())
    unique_spp  = df["common_name"].nunique()
    flyover_pct = (df["flyover_observed"] == "Yes").sum() / total_obs * 100 if total_obs else 0
    watchlist_n = (df["pif_watchlist_status"] != "Not on List").sum()
    top_sp_raw  = df.groupby("common_name")["total_birds"].sum().idxmax()
    top_sp      = top_sp_raw[:18] + "…" if len(top_sp_raw) > 18 else top_sp_raw

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Birds",     f"{total_birds:,}")
    c2.metric("Unique Species",  str(unique_spp))
    c3.metric("Total Obs",       f"{total_obs:,}")
    c4.metric("Flyover Rate",    f"{flyover_pct:.1f}%")
    c5.metric("Watch-List Obs",  f"{watchlist_n:,}")
    c6.metric("Top Species",     top_sp)

    st.markdown("")

    # ── Row 1: Top species column + ID method bar ─
    col_a, col_b = st.columns([1.2, 1])

    with col_a:
        top12 = (
            df.groupby("common_name")["total_birds"]
            .sum()
            .nlargest(12)
            .reset_index()
        )
        top12.columns = ["Species", "Birds"]
        top12 = top12.sort_values("Birds", ascending=False)

        fig6 = go.Figure(go.Bar(
            x=top12["Species"].tolist(),
            y=top12["Birds"].tolist(),
            marker=dict(
                color=top12["Birds"].tolist(),
                colorscale=[[0, "#0d2214"], [0.5, G2], [1, G1]],
                showscale=False,
            ),
            text=[f"{v:,}" for v in top12["Birds"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=9),
            hovertemplate="<b>%{x}</b><br>%{y:,} birds<extra></extra>",
        ))
        fig6.update_layout(**blayout("Top 12 Species by Total Birds", 320))
        fig6.update_xaxes(tickangle=-35, tickfont=dict(size=9))
        st.plotly_chart(fig6, use_container_width=True)

    with col_b:
        idm = (
            df.groupby("id_method")["total_birds"]
            .sum()
            .reset_index()
        )
        idm.columns = ["ID Method", "Birds"]
        idm = idm.sort_values("Birds")

        bar_colors = [TEAL, G1, AMBER, BLUE][:len(idm)]
        fig7 = go.Figure(go.Bar(
            x=idm["Birds"].tolist(),
            y=idm["ID Method"].tolist(),
            orientation="h",
            marker_color=bar_colors,
            text=[f"{v:,}" for v in idm["Birds"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=10),
            hovertemplate="<b>%{y}</b><br>%{x:,} birds<extra></extra>",
        ))
        fig7.update_layout(**blayout("Birds by Identification Method", 320))
        st.plotly_chart(fig7, use_container_width=True)

    # ── Row 2: Three donuts/pies ───────────────
    col_c, col_d, col_e = st.columns(3)

    with col_c:
        fly_counts = df["flyover_observed"].value_counts()
        fly_labels = fly_counts.index.tolist()
        fly_values = fly_counts.values.tolist()

        fig8 = go.Figure(go.Pie(
            labels=fly_labels,
            values=fly_values,
            hole=0.58,
            marker=dict(colors=[RED, G1]),
            textinfo="percent+label",
            textfont=dict(color=TEXT, size=11),
            hovertemplate="<b>%{label}</b><br>%{value:,} obs (%{percent})<extra></extra>",
        ))
        fig8.add_annotation(
            text="Flyover", x=0.5, y=0.5,
            font=dict(color=WHITE, size=12, family="Plus Jakarta Sans"),
            showarrow=False,
        )
        fig8.update_layout(**pie_layout("Flyover Observed", 280))
        st.plotly_chart(fig8, use_container_width=True)

    with col_d:
        pif_counts = df["pif_watchlist_status"].value_counts()
        pif_labels = pif_counts.index.tolist()
        pif_values = pif_counts.values.tolist()

        pie_colors_pif = [G1, AMBER, RED, PURPLE][:len(pif_labels)]
        fig9 = go.Figure(go.Pie(
            labels=pif_labels,
            values=pif_values,
            hole=0.45,
            marker=dict(colors=pie_colors_pif),
            textinfo="percent",
            textfont=dict(color=TEXT, size=10),
            hovertemplate="<b>%{label}</b><br>%{value:,} obs (%{percent})<extra></extra>",
        ))
        fig9.update_layout(**pie_layout("PIF Watchlist Status", 280))
        st.plotly_chart(fig9, use_container_width=True)

    with col_e:
        rs_counts = df["regional_stewardship_status"].value_counts()
        rs_labels = rs_counts.index.tolist()
        rs_values = rs_counts.values.tolist()

        pie_colors_rs = [TEAL, BLUE, ORANGE, PURPLE][:len(rs_labels)]
        fig10 = go.Figure(go.Pie(
            labels=rs_labels,
            values=rs_values,
            hole=0.55,
            marker=dict(colors=pie_colors_rs),
            textinfo="percent",
            textfont=dict(color=TEXT, size=10),
            hovertemplate="<b>%{label}</b><br>%{value:,} obs (%{percent})<extra></extra>",
        ))
        fig10.add_annotation(
            text="Stewardship", x=0.5, y=0.5,
            font=dict(color=WHITE, size=11, family="Plus Jakarta Sans"),
            showarrow=False,
        )
        fig10.update_layout(**pie_layout("Regional Stewardship Status", 280))
        st.plotly_chart(fig10, use_container_width=True)

    # ── Row 3: Species × Habitat stacked + Distance dual ─
    col_f, col_g = st.columns(2)

    with col_f:
        top10_names = df.groupby("common_name")["total_birds"].sum().nlargest(10).index.tolist()
        sp_hab = (
            df[df["common_name"].isin(top10_names)]
            .groupby(["common_name", "habitat_type"])["total_birds"]
            .sum()
            .reset_index()
        )
        # order y-axis by total birds
        sp_order = (
            sp_hab.groupby("common_name")["total_birds"]
            .sum()
            .sort_values()
            .index.tolist()
        )
        fig11 = px.bar(
            sp_hab,
            x="total_birds", y="common_name",
            color="habitat_type",
            orientation="h",
            color_discrete_sequence=PALETTE,
            category_orders={"common_name": sp_order},
            labels={"total_birds": "Total Birds", "common_name": "", "habitat_type": "Habitat"},
            barmode="stack",
        )
        fig11.update_traces(
            hovertemplate="<b>%{y}</b> — %{fullData.name}<br>%{x:,} birds<extra></extra>"
        )
        fig11.update_layout(**blayout("Top Species by Habitat (stacked)", 340))
        st.plotly_chart(fig11, use_container_width=True)

    with col_g:
        dist_grp = (
            df.groupby("distance")
            .agg(Observations=("total_birds", "count"), Total_Birds=("total_birds", "sum"))
            .reset_index()
            .sort_values("distance")
        )
        dist_labels = [f"{int(v)}m" for v in dist_grp["distance"].tolist()]

        fig12 = go.Figure()
        fig12.add_trace(go.Bar(
            x=dist_labels,
            y=dist_grp["Total_Birds"].tolist(),
            name="Total Birds",
            marker_color=G2, opacity=0.85,
            hovertemplate="<b>%{x}</b><br>%{y:,} birds<extra></extra>",
            yaxis="y1",
        ))
        fig12.add_trace(go.Scatter(
            x=dist_labels,
            y=dist_grp["Observations"].tolist(),
            name="Observations",
            mode="lines+markers",
            line=dict(color=AMBER, width=2.2),
            marker=dict(size=7, color=AMBER),
            hovertemplate="<b>%{x}</b><br>%{y:,} obs<extra></extra>",
            yaxis="y2",
        ))
        base_l = blayout("Birds & Observations by Distance Band", 340)
        base_l["yaxis2"] = dict(
            overlaying="y", side="right",
            gridcolor="rgba(0,0,0,0)",
            tickfont=dict(color=AMBER, size=10),
            zeroline=False,
        )
        base_l["legend"] = dict(
            bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT, size=10),
            orientation="h", y=1.05,
        )
        fig12.update_layout(**base_l)
        st.plotly_chart(fig12, use_container_width=True)

    # ── Row 4: Sex pie + State observations bar ─
    col_h, col_i = st.columns([1, 1.2])

    with col_h:
        sex_counts = df["sex"].value_counts()
        sex_labels = sex_counts.index.tolist()
        sex_values = sex_counts.values.tolist()

        fig13 = go.Figure(go.Pie(
            labels=sex_labels,
            values=sex_values,
            hole=0.0,
            marker=dict(colors=[BLUE, ROSE, AMBER][:len(sex_labels)]),
            textinfo="percent+label",
            textfont=dict(color=TEXT, size=11),
            pull=[0.04] + [0] * (len(sex_labels) - 1),
            hovertemplate="<b>%{label}</b><br>%{value:,} obs (%{percent})<extra></extra>",
        ))
        fig13.update_layout(**pie_layout("Sex Distribution", 300))
        st.plotly_chart(fig13, use_container_width=True)

    with col_i:
        code_grp = df.groupby("admin_unit_code").size().reset_index(name="Observations")
        code_grp = code_grp.sort_values("Observations", ascending=False)

        fig14 = go.Figure(go.Bar(
            x=code_grp["admin_unit_code"].tolist(),
            y=code_grp["Observations"].tolist(),
            marker=dict(
                color=code_grp["Observations"].tolist(),
                colorscale=[[0, "#0d2214"], [0.5, TEAL], [1, G1]],
                showscale=False,
            ),
            text=[f"{v:,}" for v in code_grp["Observations"]],
            textposition="outside",
            textfont=dict(color=TEXT, size=10),
            hovertemplate="<b>%{x}</b><br>%{y:,} observations<extra></extra>",
        ))
        fig14.update_layout(**blayout("Observations by State Code", 300))
        st.plotly_chart(fig14, use_container_width=True)

    # ── Species summary table ──────────────────
    st.markdown('<div class="sec-label">Full Species Summary Table</div>', unsafe_allow_html=True)
    sp_tbl = (
        df.groupby(["common_name", "scientific_name"])
        .agg(
            Observations=("total_birds", "count"),
            Total_Birds=("total_birds", "sum"),
            Avg_Birds=("total_birds", "mean"),
            Habitats=("habitat_type", lambda x: ", ".join(sorted(x.unique()))),
            Flyover_Pct=("flyover_observed", lambda x: f"{(x == 'Yes').sum() / len(x) * 100:.0f}%"),
            Watchlist=("pif_watchlist_status", lambda x: x.mode().iloc[0] if len(x) > 0 else "—"),
        )
        .reset_index()
        .sort_values("Total_Birds", ascending=False)
    )
    sp_tbl["Avg_Birds"] = sp_tbl["Avg_Birds"].round(1)
    sp_tbl.columns = [
        "Common Name", "Scientific Name", "Obs", "Total Birds",
        "Avg/Obs", "Habitats", "Flyover %", "PIF Status",
    ]
    st.dataframe(sp_tbl, use_container_width=True, hide_index=True)


# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;font-size:0.65rem;color:#1a3022;padding:6px;">'
    'Bird Species Observation Dashboard &nbsp;·&nbsp; Built with Streamlit &amp; Plotly &nbsp;·&nbsp; '
    '6,000 synthetic survey records &nbsp;·&nbsp; 30 species · 10 states'
    '</div>',
    unsafe_allow_html=True,
)

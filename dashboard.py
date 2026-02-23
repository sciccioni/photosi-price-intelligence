"""
dashboard.py — PhotoSì Competitive Intelligence Dashboard
Streamlit app per visualizzare i dati di price monitoring pan-europeo.
Avvio: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG PAGINA
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PhotoSì · Price Intelligence",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — stile dark premium con accenti arancio/oro
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── GLOBAL ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0d0f;
    color: #e8e4dc;
}
.stApp { background: #0d0d0f; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141418 0%, #0f0f13 100%);
    border-right: 1px solid #2a2a35;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {
    color: #e8e4dc !important;
}

/* ── HEADERS ── */
h1, h2, h3, h4, h5 {
    font-family: 'Syne', sans-serif !important;
    color: #f5f0e8 !important;
    letter-spacing: -0.02em;
}

/* ── METRIC CARDS ── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a1a24 0%, #141420 100%);
    border: 1px solid #2d2d3d;
    border-radius: 16px;
    padding: 20px 24px !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #f4a028, #e87f12);
}
[data-testid="stMetricLabel"] p {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #8a8a9a !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    color: #f5f0e8 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 12px !important;
}

/* ── DATAFRAME ── */
[data-testid="stDataFrame"] {
    border: 1px solid #2d2d3d;
    border-radius: 12px;
    overflow: hidden;
}
.stDataFrame th {
    background: #1a1a24 !important;
    color: #f4a028 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

/* ── TABS ── */
[data-baseweb="tab-list"] {
    background: #141418;
    border-radius: 12px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #2a2a35;
}
[data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px !important;
    color: #8a8a9a !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 8px 18px !important;
    transition: all 0.2s ease;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(135deg, #f4a028, #e87f12) !important;
    color: #0d0d0f !important;
    font-weight: 600 !important;
}

/* ── SELECTS / MULTISELECTS ── */
[data-baseweb="select"] > div,
[data-baseweb="tag"] {
    background: #1a1a24 !important;
    border-color: #2d2d3d !important;
    color: #e8e4dc !important;
}
[data-baseweb="tag"] {
    background: #f4a028 !important;
    color: #0d0d0f !important;
    font-weight: 600 !important;
}

/* ── DIVIDER ── */
hr { border-color: #2d2d3d !important; }

/* ── CHART CONTAINERS ── */
.chart-container {
    background: linear-gradient(135deg, #141420 0%, #111117 100%);
    border: 1px solid #2d2d3d;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}

/* ── SECTION TITLES ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #2d2d3d;
}
.section-header h2 {
    font-size: 18px !important;
    font-weight: 700 !important;
    margin: 0 !important;
}
.pill {
    background: linear-gradient(135deg, #f4a028, #e87f12);
    color: #0d0d0f;
    font-family: 'Syne', sans-serif;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── INSIGHT CARDS ── */
.insight-card {
    background: #1a1a24;
    border: 1px solid #2d2d3d;
    border-left: 3px solid #f4a028;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    font-size: 14px;
    line-height: 1.6;
}
.insight-card strong { color: #f4a028; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #141418; }
::-webkit-scrollbar-thumb { background: #3a3a4a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #f4a028; }

/* ── UPLOAD AREA ── */
[data-testid="stFileUploader"] {
    background: #141420;
    border: 1px dashed #3a3a4a;
    border-radius: 12px;
}

/* ── RADIO ── */
[data-baseweb="radio"] span { color: #e8e4dc !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# PALETTE COMPETITOR — colori fissi per coerenza visiva
# ─────────────────────────────────────────────────────────────────────────────
COMPETITOR_COLORS = {
    "PhotoSì":     "#f4a028",
    "Cewe":        "#4a9eff",
    "Photobox":    "#ff6b6b",
    "Cheerz":      "#a78bfa",
    "Pixum":       "#34d399",
    "Saal Digital":"#f87171",
    "Albelli":     "#60a5fa",
    "Hofmann":     "#fb923c",
    "Bonusprint":  "#a3e635",
    "Ifolor":      "#e879f9",
    "Lalalab":     "#38bdf8",
    "Popsa":       "#fbbf24",
    "Journi":      "#6ee7b7",
    "Once Upon":   "#c084fc",
}

FLAG_MAP = {
    "IT": "🇮🇹", "DE": "🇩🇪", "FR": "🇫🇷", "ES": "🇪🇸",
    "GB": "🇬🇧", "NL": "🇳🇱", "CH": "🇨🇭", "BE": "🇧🇪",
}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#c8c4bc", size=12),
    title_font=dict(family="Syne, sans-serif", color="#f5f0e8", size=16),
    xaxis=dict(gridcolor="#2d2d3d", zerolinecolor="#2d2d3d", tickcolor="#6a6a7a"),
    yaxis=dict(gridcolor="#2d2d3d", zerolinecolor="#2d2d3d", tickcolor="#6a6a7a"),
    legend=dict(
        bgcolor="rgba(20,20,32,0.9)",
        bordercolor="#2d2d3d",
        borderwidth=1,
        font=dict(size=12, color="#c8c4bc"),
    ),
    hoverlabel=dict(
        bgcolor="#1a1a24",
        bordercolor="#2d2d3d",
        font=dict(family="DM Sans", color="#f5f0e8"),
    ),
    margin=dict(l=20, r=20, t=50, b=20),
)

# ─────────────────────────────────────────────────────────────────────────────
# CARICAMENTO DATI
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data(source) -> pd.DataFrame:
    if isinstance(source, str):
        df = pd.read_csv(source)
    else:
        df = pd.read_csv(source)
    # Normalizza colonne
    rename_map = {
        "prezzo_pulito": "prezzo_eur",
        "link_acquisto": "link",
    }
    df.rename(columns=rename_map, inplace=True)
    for col in ["prezzo_eur", "prezzo_originale"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Rimuovi outlier estremi (prezzi > 500€ probabilmente errati)
    if "prezzo_eur" in df.columns:
        df = df[df["prezzo_eur"].between(0.5, 500)]
    # Flag mercato
    df["flag"] = df["mercato"].map(FLAG_MAP).fillna("🌍")
    df["mercato_label"] = df["flag"] + " " + df["mercato"]
    return df

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 24px 0;">
        <div style="font-family:'Syne',sans-serif; font-size:22px; font-weight:800;
                    color:#f5f0e8; letter-spacing:-0.03em;">
            📸 PhotoSì
        </div>
        <div style="font-size:11px; color:#8a8a9a; letter-spacing:0.12em;
                    text-transform:uppercase; margin-top:4px;">
            Price Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📂 Carica Dati")
    uploaded = st.file_uploader("CSV di output", type=["csv"])

    DEFAULT_CSV = "cataloghi_shopping_multi_mercato.csv"
    if uploaded:
        df_raw = load_data(uploaded)
        st.success(f"✅ {len(df_raw):,} prodotti caricati")
    elif os.path.exists(DEFAULT_CSV):
        df_raw = load_data(DEFAULT_CSV)
        st.info(f"📄 Usando `{DEFAULT_CSV}`  \n{len(df_raw):,} record")
    else:
        st.warning("Nessun dato trovato. Carica un CSV o esegui prima lo script di raccolta.")
        st.stop()

    st.markdown("---")
    st.markdown("### 🎛️ Filtri")

    all_paesi = sorted(df_raw["mercato"].unique())
    sel_paesi = st.multiselect(
        "Mercati",
        options=all_paesi,
        default=all_paesi,
        format_func=lambda x: f"{FLAG_MAP.get(x, '🌍')} {x}",
    )

    all_comp = sorted(df_raw["competitor"].unique())
    sel_comp = st.multiselect("Competitor", options=all_comp, default=all_comp)

    min_p = float(df_raw["prezzo_eur"].min())
    max_p = float(df_raw["prezzo_eur"].max())
    price_range = st.slider(
        "Range prezzo (€)",
        min_value=min_p,
        max_value=max_p,
        value=(min_p, max_p),
        step=0.5,
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:11px;color:#555;text-align:center;'>"
        f"Aggiornato: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>",
        unsafe_allow_html=True,
    )

# Applica filtri
df = df_raw[
    df_raw["mercato"].isin(sel_paesi) &
    df_raw["competitor"].isin(sel_comp) &
    df_raw["prezzo_eur"].between(*price_range)
].copy()

# ─────────────────────────────────────────────────────────────────────────────
# HEADER PRINCIPALE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex; align-items:flex-end; justify-content:space-between;
            padding: 12px 0 28px 0; border-bottom: 1px solid #2d2d3d; margin-bottom: 32px;">
    <div>
        <h1 style="font-size:32px; font-weight:800; margin:0; letter-spacing:-0.04em;">
            Competitive Price Intelligence
        </h1>
        <p style="color:#8a8a9a; margin:6px 0 0 0; font-size:14px;">
            Monitoraggio prezzi photobook pan-europeo · EU + UK + CH
        </p>
    </div>
    <div style="text-align:right;">
        <span class="pill">Live Data</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric("📦 Prodotti", f"{len(df):,}")
with k2:
    st.metric("🏢 Competitor", f"{df['competitor'].nunique()}")
with k3:
    st.metric("🌍 Mercati", f"{df['mercato'].nunique()}")
with k4:
    avg = df["prezzo_eur"].mean()
    st.metric("💶 Prezzo Medio", f"€ {avg:.2f}")
with k5:
    # Confronto PhotoSì vs media mercato
    photosi_avg = df[df["competitor"] == "PhotoSì"]["prezzo_eur"].mean()
    others_avg  = df[df["competitor"] != "PhotoSì"]["prezzo_eur"].mean()
    if pd.notna(photosi_avg) and pd.notna(others_avg) and others_avg > 0:
        delta_pct = (photosi_avg - others_avg) / others_avg * 100
        st.metric(
            "📍 PhotoSì vs Mercato",
            f"€ {photosi_avg:.2f}",
            delta=f"{delta_pct:+.1f}%",
            delta_color="inverse",
        )
    else:
        st.metric("📍 PhotoSì vs Mercato", "N/D")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS PRINCIPALI
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview",
    "🗺️ Per Mercato",
    "🏢 Per Competitor",
    "🔍 Dettaglio Prodotti",
    "💡 Insights",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        # Boxplot prezzi per competitor
        st.markdown("#### 📊 Distribuzione Prezzi per Competitor")
        comp_order = (df.groupby("competitor")["prezzo_eur"]
                        .median()
                        .sort_values()
                        .index.tolist())
        color_seq = [COMPETITOR_COLORS.get(c, "#888") for c in comp_order]

        fig_box = go.Figure()
        for comp in comp_order:
            sub = df[df["competitor"] == comp]["prezzo_eur"]
            fig_box.add_trace(go.Box(
                y=sub,
                name=comp,
                marker_color=COMPETITOR_COLORS.get(comp, "#888"),
                line_color=COMPETITOR_COLORS.get(comp, "#888"),
                fillcolor=COMPETITOR_COLORS.get(comp, "#888") + "33",
                boxmean="sd",
                showlegend=False,
            ))
        fig_box.update_layout(
            **PLOT_LAYOUT,
            height=420,
            yaxis_title="Prezzo (€)",
            title="",
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with col_r:
        # Heatmap: competitor × mercato (prezzo medio)
        st.markdown("#### 🗺️ Heatmap Prezzo Medio")
        pivot = (df.groupby(["competitor", "mercato"])["prezzo_eur"]
                   .mean()
                   .round(2)
                   .unstack(fill_value=np.nan))

        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[f"{FLAG_MAP.get(c,'🌍')} {c}" for c in pivot.columns],
            y=pivot.index.tolist(),
            colorscale=[
                [0.0, "#0f3a5a"],
                [0.5, "#2563eb"],
                [1.0, "#f4a028"],
            ],
            text=pivot.values.round(1),
            texttemplate="€%{text}",
            textfont=dict(size=10, color="white"),
            hoverongaps=False,
            colorbar=dict(
                title="€",
                tickfont=dict(color="#c8c4bc"),
                title_font=dict(color="#c8c4bc"),
                bgcolor="rgba(0,0,0,0)",
            ),
        ))
        fig_heat.update_layout(
            **PLOT_LAYOUT,
            height=420,
            xaxis=dict(side="bottom", tickangle=-35, gridcolor="transparent"),
            yaxis=dict(gridcolor="transparent"),
            margin=dict(l=10, r=10, t=10, b=60),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    # Scatter: prezzo medio vs numero prodotti per competitor
    st.markdown("#### 🎯 Competitor Overview: Prezzo Medio vs Ampiezza Catalogo")
    agg = (df.groupby("competitor")
             .agg(prezzo_medio=("prezzo_eur", "mean"),
                  n_prodotti=("prodotto", "count"),
                  prezzo_min=("prezzo_eur", "min"),
                  prezzo_max=("prezzo_eur", "max"))
             .reset_index())

    fig_scatter = go.Figure()
    for _, row in agg.iterrows():
        color = COMPETITOR_COLORS.get(row["competitor"], "#888")
        is_photosi = row["competitor"] == "PhotoSì"
        fig_scatter.add_trace(go.Scatter(
            x=[row["prezzo_medio"]],
            y=[row["n_prodotti"]],
            mode="markers+text",
            name=row["competitor"],
            text=[row["competitor"]],
            textposition="top center",
            marker=dict(
                size=28 if is_photosi else 20,
                color=color,
                line=dict(width=3 if is_photosi else 1,
                          color="#ffffff" if is_photosi else color),
                opacity=1.0,
            ),
            textfont=dict(
                size=13 if is_photosi else 11,
                color="#f4a028" if is_photosi else "#c8c4bc",
                family="Syne, sans-serif",
            ),
            hovertemplate=(
                f"<b>{row['competitor']}</b><br>"
                f"Prezzo medio: €{row['prezzo_medio']:.2f}<br>"
                f"Prodotti: {int(row['n_prodotti'])}<br>"
                f"Range: €{row['prezzo_min']:.2f} – €{row['prezzo_max']:.2f}"
                "<extra></extra>"
            ),
        ))

    fig_scatter.update_layout(
        **PLOT_LAYOUT,
        height=400,
        xaxis_title="Prezzo Medio (€)",
        yaxis_title="N° Prodotti nel Catalogo",
        showlegend=False,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PER MERCATO
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### 🌍 Analisi per Mercato Geografico")

    # Bar chart: prezzo medio per paese raggruppato per competitor
    agg_mercato = (df.groupby(["mercato_label", "competitor"])["prezzo_eur"]
                     .mean()
                     .reset_index()
                     .sort_values("prezzo_eur"))

    fig_bar_m = px.bar(
        agg_mercato,
        x="mercato_label",
        y="prezzo_eur",
        color="competitor",
        barmode="group",
        color_discrete_map=COMPETITOR_COLORS,
        labels={"prezzo_eur": "Prezzo Medio (€)", "mercato_label": "Mercato"},
        height=420,
    )
    fig_bar_m.update_layout(**PLOT_LAYOUT, bargap=0.15, bargroupgap=0.06)
    st.plotly_chart(fig_bar_m, use_container_width=True)

    # Per ogni mercato, violin + top competitor più economico
    st.markdown("#### 🎻 Distribuzione per Singolo Mercato")
    paesi_disponibili = sorted(df["mercato"].unique())
    cols_m = st.columns(min(len(paesi_disponibili), 3))

    for i, paese in enumerate(paesi_disponibili):
        sub_p = df[df["mercato"] == paese]
        flag  = FLAG_MAP.get(paese, "🌍")

        with cols_m[i % 3]:
            st.markdown(f"**{flag} {paese}** — {len(sub_p)} prodotti")

            fig_v = go.Figure()
            for comp in sub_p["competitor"].unique():
                vals = sub_p[sub_p["competitor"] == comp]["prezzo_eur"]
                if len(vals) < 2:
                    continue
                color = COMPETITOR_COLORS.get(comp, "#888")
                fig_v.add_trace(go.Violin(
                    y=vals,
                    name=comp,
                    fillcolor=color + "44",
                    line_color=color,
                    box_visible=True,
                    meanline_visible=True,
                    showlegend=False,
                ))
            fig_v.update_layout(
                **PLOT_LAYOUT,
                height=280,
                margin=dict(l=10, r=10, t=20, b=10),
                yaxis_title="€",
            )
            st.plotly_chart(fig_v, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PER COMPETITOR
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    sel_c = st.selectbox(
        "🔍 Seleziona Competitor",
        options=sorted(df["competitor"].unique()),
        index=0 if "PhotoSì" not in df["competitor"].values
               else list(sorted(df["competitor"].unique())).index("PhotoSì"),
    )

    df_c = df[df["competitor"] == sel_c]
    color_c = COMPETITOR_COLORS.get(sel_c, "#4a9eff")

    # KPI competitor
    ck1, ck2, ck3, ck4 = st.columns(4)
    with ck1:
        st.metric("Prodotti", f"{len(df_c):,}")
    with ck2:
        st.metric("Prezzo Min", f"€ {df_c['prezzo_eur'].min():.2f}")
    with ck3:
        st.metric("Prezzo Medio", f"€ {df_c['prezzo_eur'].mean():.2f}")
    with ck4:
        st.metric("Prezzo Max", f"€ {df_c['prezzo_eur'].max():.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    col_cl, col_cr = st.columns([2, 3], gap="large")

    with col_cl:
        # Prezzi medi per mercato
        st.markdown(f"#### Prezzi per Mercato")
        agg_c = (df_c.groupby("mercato")["prezzo_eur"]
                      .agg(["mean", "min", "max", "count"])
                      .reset_index()
                      .sort_values("mean"))
        agg_c.columns = ["Mercato", "Media €", "Min €", "Max €", "Prodotti"]
        agg_c["Mercato"] = agg_c["Mercato"].map(
            lambda x: f"{FLAG_MAP.get(x,'🌍')} {x}")
        agg_c[["Media €","Min €","Max €"]] = agg_c[["Media €","Min €","Max €"]].round(2)
        st.dataframe(agg_c, use_container_width=True, hide_index=True,
                     height=min(400, 60 + 36*len(agg_c)))

    with col_cr:
        # Istogramma prezzi
        st.markdown(f"#### Distribuzione Prezzi")
        fig_hist = go.Figure(go.Histogram(
            x=df_c["prezzo_eur"],
            nbinsx=30,
            marker_color=color_c,
            opacity=0.85,
            name=sel_c,
        ))
        # Linea media
        mean_c = df_c["prezzo_eur"].mean()
        fig_hist.add_vline(
            x=mean_c,
            line_dash="dash",
            line_color="#ffffff",
            annotation_text=f"Media €{mean_c:.2f}",
            annotation_position="top right",
            annotation_font_color="#ffffff",
        )
        fig_hist.update_layout(
            **PLOT_LAYOUT, height=300,
            xaxis_title="Prezzo (€)",
            yaxis_title="N° Prodotti",
            showlegend=False,
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # Confronto vs altri competitor per mercato comune
    st.markdown("#### 📊 Confronto vs Competitor per Mercato")
    comuni = df[df["competitor"] != sel_c]["mercato"].unique()
    comuni = [m for m in comuni if m in df_c["mercato"].unique()]

    if comuni:
        agg_vs = (df[df["mercato"].isin(comuni)]
                    .groupby(["mercato", "competitor"])["prezzo_eur"]
                    .mean()
                    .reset_index())
        agg_vs["highlight"] = agg_vs["competitor"] == sel_c

        fig_vs = px.bar(
            agg_vs,
            x="mercato",
            y="prezzo_eur",
            color="competitor",
            barmode="group",
            color_discrete_map=COMPETITOR_COLORS,
            labels={"prezzo_eur": "Prezzo Medio (€)", "mercato": "Mercato"},
            height=380,
        )
        fig_vs.update_layout(**PLOT_LAYOUT)
        st.plotly_chart(fig_vs, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DETTAGLIO PRODOTTI
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### 🔍 Catalogo Completo Prodotti")

    # Filtri rapidi in-tab
    f1, f2, f3 = st.columns([2, 2, 3])
    with f1:
        filt_comp = st.multiselect("Competitor", df["competitor"].unique(),
                                    default=list(df["competitor"].unique())[:5],
                                    key="dt_comp")
    with f2:
        filt_paese = st.multiselect("Mercato", sorted(df["mercato"].unique()),
                                     default=list(sorted(df["mercato"].unique()))[:3],
                                     key="dt_paese")
    with f3:
        filt_q = st.text_input("🔎 Cerca nel titolo prodotto", "", key="dt_query")

    df_t = df[df["competitor"].isin(filt_comp) & df["mercato"].isin(filt_paese)]
    if filt_q:
        df_t = df_t[df_t["prodotto"].str.contains(filt_q, case=False, na=False)]

    # Ordina per prezzo
    df_t = df_t.sort_values("prezzo_eur")

    st.markdown(f"**{len(df_t):,} prodotti** corrispondenti ai filtri")

    # Tabella con colore condizionale per PhotoSì
    display_cols = ["competitor", "mercato_label", "prodotto",
                    "prezzo_originale", "valuta", "prezzo_eur"]
    if "link" in df_t.columns:
        display_cols.append("link")

    cols_show = [c for c in display_cols if c in df_t.columns]

    def highlight_photosi(row):
        if row.get("competitor") == "PhotoSì":
            return ["background-color: #2a1f0a; color: #f4a028; font-weight:600"] * len(row)
        return [""] * len(row)

    styled = (df_t[cols_show]
              .rename(columns={
                  "mercato_label": "Mercato", "competitor": "Competitor",
                  "prodotto": "Prodotto", "prezzo_originale": "Prezzo orig.",
                  "valuta": "Val.", "prezzo_eur": "€ EUR", "link": "Link"})
              .style.apply(highlight_photosi, axis=1)
              .format({"€ EUR": "€{:.2f}", "Prezzo orig.": "{:.2f}"}))

    st.dataframe(styled, use_container_width=True, height=480)

    # Download
    csv_dl = df_t.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "⬇️ Scarica questo subset CSV",
        data=csv_dl,
        file_name=f"price_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("#### 💡 Insights Automatici")

    insights = []

    # Insight 1: PhotoSì posizionamento prezzo
    photosi_data = df[df["competitor"] == "PhotoSì"]
    others_data  = df[df["competitor"] != "PhotoSì"]

    if not photosi_data.empty and not others_data.empty:
        avg_ps = photosi_data["prezzo_eur"].mean()
        avg_oth = others_data["prezzo_eur"].mean()
        delta = (avg_ps - avg_oth) / avg_oth * 100
        direction = "superiore" if delta > 0 else "inferiore"
        insights.append(
            f"<strong>Posizionamento di prezzo:</strong> PhotoSì ha un prezzo medio di "
            f"<strong>€{avg_ps:.2f}</strong>, {abs(delta):.1f}% <strong>{direction}</strong> "
            f"alla media del mercato (€{avg_oth:.2f})."
        )

    # Insight 2: competitor più economico per mercato
    for paese in df["mercato"].unique():
        sub = df[df["mercato"] == paese]
        cheapest = sub.groupby("competitor")["prezzo_eur"].mean().idxmin()
        cheapest_avg = sub.groupby("competitor")["prezzo_eur"].mean().min()
        flag = FLAG_MAP.get(paese, "🌍")
        insights.append(
            f"<strong>{flag} {paese}:</strong> Il competitor più economico è "
            f"<strong>{cheapest}</strong> con prezzo medio €{cheapest_avg:.2f}."
        )

    # Insight 3: mercato con prezzi più alti
    avg_by_market = df.groupby("mercato")["prezzo_eur"].mean()
    if not avg_by_market.empty:
        top_market = avg_by_market.idxmax()
        insights.append(
            f"<strong>Mercato premium:</strong> <strong>{FLAG_MAP.get(top_market,'🌍')} {top_market}</strong> "
            f"ha i prezzi medi più alti (€{avg_by_market[top_market]:.2f}), "
            f"potenzialmente indicando maggiore disponibilità a pagare."
        )

    # Insight 4: competitor con catalogo più ampio
    catalog_size = df.groupby("competitor")["prodotto"].count().sort_values(ascending=False)
    if not catalog_size.empty:
        leader = catalog_size.index[0]
        insights.append(
            f"<strong>Ampiezza catalogo:</strong> <strong>{leader}</strong> ha il catalogo "
            f"più ampio con <strong>{catalog_size[leader]}</strong> prodotti rilevati."
        )

    # Render insight cards
    for ins in insights:
        st.markdown(f'<div class="insight-card">{ins}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Radar chart: competitor vs dimensioni (prezzo medio, ampiezza catalogo, mercati coperti)
    st.markdown("#### 🎯 Radar Competitivo (normalizzato)")

    agg_radar = df.groupby("competitor").agg(
        prezzo_medio=("prezzo_eur", "mean"),
        n_prodotti=("prodotto", "count"),
        n_mercati=("mercato", "nunique"),
    ).reset_index()

    # Normalizza 0-1
    for col in ["prezzo_medio", "n_prodotti", "n_mercati"]:
        col_min = agg_radar[col].min()
        col_max = agg_radar[col].max()
        if col_max > col_min:
            agg_radar[f"{col}_norm"] = (agg_radar[col] - col_min) / (col_max - col_min)
        else:
            agg_radar[f"{col}_norm"] = 0.5

    categories = ["Prezzo Medio", "Ampiezza Catalogo", "Copertura Mercati"]

    fig_radar = go.Figure()
    for _, row in agg_radar.iterrows():
        color = COMPETITOR_COLORS.get(row["competitor"], "#888")
        vals = [
            row["prezzo_medio_norm"],
            row["n_prodotti_norm"],
            row["n_mercati_norm"],
        ]
        vals_closed = vals + [vals[0]]

        fig_radar.add_trace(go.Scatterpolar(
            r=vals_closed,
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor=color + "22",
            line=dict(color=color, width=2),
            name=row["competitor"],
            hovertemplate=f"<b>{row['competitor']}</b><br>%{{theta}}: %{{r:.2f}}<extra></extra>",
        ))

    fig_radar.update_layout(
        **PLOT_LAYOUT,
        height=480,
        polar=dict(
            bgcolor="rgba(20,20,30,0.8)",
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                tickfont=dict(color="#6a6a7a", size=10),
                gridcolor="#2d2d3d",
                linecolor="#2d2d3d",
            ),
            angularaxis=dict(
                tickfont=dict(color="#c8c4bc", size=12, family="Syne"),
                gridcolor="#2d2d3d",
                linecolor="#2d2d3d",
            ),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
        ),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="margin-top:40px;">
<div style="text-align:center; padding: 16px 0 8px 0;
            font-size:12px; color:#555; font-family:'DM Sans',sans-serif;">
    📸 <strong style="color:#8a8a9a;">PhotoSì Price Intelligence</strong> &nbsp;·&nbsp;
    Dati via Serper Shopping API &nbsp;·&nbsp;
    Prezzi normalizzati in EUR
</div>
""", unsafe_allow_html=True)

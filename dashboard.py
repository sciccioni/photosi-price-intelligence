"""
dashboard.py — PhotoSì Competitive Intelligence Dashboard
Avvio: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; background:#0d0d0f; color:#e8e4dc; }
.stApp { background:#0d0d0f; }
[data-testid="stSidebar"] { background:#141418; border-right:1px solid #2a2a35; }
[data-testid="stSidebar"] * { color:#e8e4dc !important; }
h1,h2,h3,h4,h5 { font-family:'Syne',sans-serif !important; color:#f5f0e8 !important; }
[data-testid="stMetric"] { background:#1a1a24; border:1px solid #2d2d3d; border-radius:16px; padding:20px !important; }
[data-testid="stMetricLabel"] p { font-size:11px !important; text-transform:uppercase; letter-spacing:0.1em; color:#8a8a9a !important; }
[data-testid="stMetricValue"] { font-family:'Syne',sans-serif !important; font-size:26px !important; font-weight:700 !important; color:#f5f0e8 !important; }
[data-baseweb="tab-list"] { background:#141418; border-radius:12px; padding:4px; border:1px solid #2a2a35; }
[data-baseweb="tab"] { background:transparent !important; color:#8a8a9a !important; font-family:'DM Sans',sans-serif !important; border-radius:8px !important; }
[aria-selected="true"][data-baseweb="tab"] { background:linear-gradient(135deg,#f4a028,#e87f12) !important; color:#0d0d0f !important; font-weight:600 !important; }
[data-baseweb="select"] > div { background:#1a1a24 !important; border-color:#2d2d3d !important; color:#e8e4dc !important; }
[data-baseweb="tag"] { background:#f4a028 !important; color:#0d0d0f !important; font-weight:600 !important; }
hr { border-color:#2d2d3d !important; }
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:#141418; }
::-webkit-scrollbar-thumb { background:#3a3a4a; border-radius:3px; }
.insight-card { background:#1a1a24; border:1px solid #2d2d3d; border-left:3px solid #f4a028; border-radius:12px; padding:16px 20px; margin-bottom:10px; font-size:14px; line-height:1.6; }
.insight-card strong { color:#f4a028; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# COSTANTI
# ─────────────────────────────────────────────────────────────────────────────
COMPETITOR_COLORS = {
    "PhotoSì":"#f4a028", "Cewe":"#4a9eff", "Photobox":"#ff6b6b",
    "Cheerz":"#a78bfa", "Pixum":"#34d399", "Saal Digital":"#f87171",
    "Albelli":"#60a5fa", "Hofmann":"#fb923c", "Bonusprint":"#a3e635",
    "Ifolor":"#e879f9", "Lalalab":"#38bdf8", "Popsa":"#fbbf24",
    "Journi":"#6ee7b7", "Once Upon":"#c084fc",
}

FLAG_MAP = {
    "IT":"🇮🇹", "DE":"🇩🇪", "FR":"🇫🇷", "ES":"🇪🇸",
    "GB":"🇬🇧", "NL":"🇳🇱", "CH":"🇨🇭", "BE":"🇧🇪",
}

def base_layout(h=420):
    """Layout Plotly base — SENZA xaxis/yaxis per evitare conflitti."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#c8c4bc", size=12),
        height=h,
        margin=dict(l=20, r=20, t=40, b=20),
        hoverlabel=dict(bgcolor="#1a1a24", bordercolor="#2d2d3d",
                        font=dict(family="DM Sans", color="#f5f0e8")),
        legend=dict(bgcolor="rgba(20,20,32,0.9)", bordercolor="#2d2d3d",
                    borderwidth=1, font=dict(size=12, color="#c8c4bc")),
    )

# ─────────────────────────────────────────────────────────────────────────────
# CARICAMENTO DATI
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data(source) -> pd.DataFrame:
    df = pd.read_csv(source)
    df.rename(columns={"prezzo_pulito": "prezzo_eur", "link_acquisto": "link"}, inplace=True)
    for col in ["prezzo_eur", "prezzo_originale"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["prezzo_eur"])
    df = df[df["prezzo_eur"].between(0.5, 500)]
    df["flag"] = df["mercato"].map(FLAG_MAP).fillna("🌍")
    df["mercato_label"] = df["flag"] + " " + df["mercato"]
    return df

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:8px 0 24px 0;">
        <div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#f5f0e8;">📸 PhotoSì</div>
        <div style="font-size:11px;color:#8a8a9a;letter-spacing:0.12em;text-transform:uppercase;margin-top:4px;">Price Intelligence</div>
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
        st.info(f"📄 {DEFAULT_CSV} · {len(df_raw):,} record")
    else:
        st.warning("Carica un CSV o esegui prima lo script di raccolta.")
        st.stop()

    st.markdown("---")
    st.markdown("### 🎛️ Filtri")

    all_paesi = sorted(df_raw["mercato"].unique())
    sel_paesi = st.multiselect("Mercati", options=all_paesi, default=all_paesi,
                                format_func=lambda x: f"{FLAG_MAP.get(x,'🌍')} {x}")

    all_comp = sorted(df_raw["competitor"].unique())
    sel_comp = st.multiselect("Competitor", options=all_comp, default=all_comp)

    min_p = float(df_raw["prezzo_eur"].min())
    max_p = float(df_raw["prezzo_eur"].max())
    price_range = st.slider("Range prezzo (€)", min_value=min_p, max_value=max_p,
                             value=(min_p, max_p), step=0.5)

    st.markdown("---")
    st.caption(f"Aggiornato: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# Applica filtri
df = df_raw[
    df_raw["mercato"].isin(sel_paesi) &
    df_raw["competitor"].isin(sel_comp) &
    df_raw["prezzo_eur"].between(*price_range)
].copy()

# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:12px 0 28px 0;border-bottom:1px solid #2d2d3d;margin-bottom:32px;">
    <h1 style="font-size:32px;font-weight:800;margin:0;letter-spacing:-0.04em;">Competitive Price Intelligence</h1>
    <p style="color:#8a8a9a;margin:6px 0 0 0;font-size:14px;">Monitoraggio prezzi photobook pan-europeo · EU + UK + CH</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# KPI
# ─────────────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1: st.metric("📦 Prodotti", f"{len(df):,}")
with k2: st.metric("🏢 Competitor", f"{df['competitor'].nunique()}")
with k3: st.metric("🌍 Mercati", f"{df['mercato'].nunique()}")
with k4: st.metric("💶 Prezzo Medio", f"€ {df['prezzo_eur'].mean():.2f}")
with k5:
    ps = df[df["competitor"] == "PhotoSì"]["prezzo_eur"].mean()
    ot = df[df["competitor"] != "PhotoSì"]["prezzo_eur"].mean()
    if pd.notna(ps) and pd.notna(ot) and ot > 0:
        delta = (ps - ot) / ot * 100
        st.metric("📍 PhotoSì vs Mercato", f"€ {ps:.2f}", delta=f"{delta:+.1f}%", delta_color="inverse")
    else:
        st.metric("📍 PhotoSì vs Mercato", "N/D")

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview", "🗺️ Per Mercato", "🏢 Per Competitor", "🔍 Prodotti", "💡 Insights"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        st.markdown("#### 📊 Distribuzione Prezzi per Competitor")
        comp_order = df.groupby("competitor")["prezzo_eur"].median().sort_values().index.tolist()
        fig_box = go.Figure()
        for comp in comp_order:
            sub = df[df["competitor"] == comp]["prezzo_eur"]
            color = COMPETITOR_COLORS.get(comp, "#888888")
            fig_box.add_trace(go.Box(
                y=sub, name=comp,
                marker_color=color,
                line_color=color,
                boxmean="sd",
                showlegend=False,
            ))
        fig_box.update_layout(**base_layout(420))
        fig_box.update_xaxes(showgrid=False, tickfont=dict(color="#c8c4bc"))
        fig_box.update_yaxes(gridcolor="#2d2d3d", tickfont=dict(color="#c8c4bc"), title_text="Prezzo (€)")
        st.plotly_chart(fig_box, use_container_width=True)

    with col_r:
        st.markdown("#### 🗺️ Heatmap Prezzo Medio")
        pivot = df.groupby(["competitor", "mercato"])["prezzo_eur"].mean().round(2).unstack(fill_value=np.nan)
        text_vals = np.where(np.isnan(pivot.values), "", pivot.values.round(1).astype(str))
        fig_heat = go.Figure(go.Heatmap(
            z=pivot.values,
            x=[f"{FLAG_MAP.get(c,'🌍')} {c}" for c in pivot.columns],
            y=list(pivot.index),
            colorscale=[[0.0, "#0f3a5a"], [0.5, "#2563eb"], [1.0, "#f4a028"]],
            text=text_vals,
            texttemplate="%{text}",
            textfont=dict(size=10, color="white"),
            hoverongaps=False,
            colorbar=dict(title="€", tickfont=dict(color="#c8c4bc"), title_font=dict(color="#c8c4bc")),
        ))
        fig_heat.update_layout(**base_layout(420))
        fig_heat.update_xaxes(tickangle=-35, showgrid=False, tickfont=dict(color="#c8c4bc"))
        fig_heat.update_yaxes(showgrid=False, tickfont=dict(color="#c8c4bc"))
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("#### 🎯 Prezzo Medio vs Ampiezza Catalogo")
    agg = df.groupby("competitor").agg(
        prezzo_medio=("prezzo_eur", "mean"),
        n_prodotti=("prodotto", "count"),
        prezzo_min=("prezzo_eur", "min"),
        prezzo_max=("prezzo_eur", "max"),
    ).reset_index()
    fig_scatter = go.Figure()
    for _, row in agg.iterrows():
        color = COMPETITOR_COLORS.get(row["competitor"], "#888888")
        is_ps = row["competitor"] == "PhotoSì"
        fig_scatter.add_trace(go.Scatter(
            x=[row["prezzo_medio"]], y=[row["n_prodotti"]],
            mode="markers+text", name=row["competitor"],
            text=[row["competitor"]], textposition="top center",
            marker=dict(size=28 if is_ps else 18, color=color,
                        line=dict(width=3 if is_ps else 1, color="#ffffff" if is_ps else color)),
            textfont=dict(size=13 if is_ps else 11,
                          color="#f4a028" if is_ps else "#c8c4bc", family="Syne, sans-serif"),
            hovertemplate=(f"<b>{row['competitor']}</b><br>"
                           f"Prezzo medio: €{row['prezzo_medio']:.2f}<br>"
                           f"Prodotti: {int(row['n_prodotti'])}<extra></extra>"),
            showlegend=False,
        ))
    fig_scatter.update_layout(**base_layout(400))
    fig_scatter.update_xaxes(gridcolor="#2d2d3d", tickfont=dict(color="#c8c4bc"), title_text="Prezzo Medio (€)")
    fig_scatter.update_yaxes(gridcolor="#2d2d3d", tickfont=dict(color="#c8c4bc"), title_text="N° Prodotti")
    st.plotly_chart(fig_scatter, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PER MERCATO
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### 🌍 Prezzo Medio per Mercato e Competitor")
    agg_m = df.groupby(["mercato_label", "competitor"])["prezzo_eur"].mean().reset_index()
    fig_bar = px.bar(
        agg_m, x="mercato_label", y="prezzo_eur", color="competitor",
        barmode="group", color_discrete_map=COMPETITOR_COLORS,
        labels={"prezzo_eur": "Prezzo Medio (€)", "mercato_label": "Mercato"},
        height=420,
    )
    fig_bar.update_layout(**base_layout(420))
    fig_bar.update_xaxes(showgrid=False, tickfont=dict(color="#c8c4bc"))
    fig_bar.update_yaxes(gridcolor="#2d2d3d", tickfont=dict(color="#c8c4bc"))
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("#### 🎻 Distribuzione per Singolo Mercato")
    paesi = sorted(df["mercato"].unique())
    cols_m = st.columns(min(len(paesi), 3))
    for i, paese in enumerate(paesi):
        sub_p = df[df["mercato"] == paese]
        with cols_m[i % 3]:
            st.markdown(f"**{FLAG_MAP.get(paese,'🌍')} {paese}** — {len(sub_p)} prodotti")
            fig_v = go.Figure()
            for comp in sub_p["competitor"].unique():
                vals = sub_p[sub_p["competitor"] == comp]["prezzo_eur"]
                if len(vals) < 2:
                    continue
                color = COMPETITOR_COLORS.get(comp, "#888888")
                fig_v.add_trace(go.Violin(
                    y=vals, name=comp, line_color=color,
                    box_visible=True, meanline_visible=True, showlegend=False,
                ))
            fig_v.update_layout(**base_layout(280))
            fig_v.update_xaxes(showgrid=False, tickfont=dict(color="#c8c4bc"))
            fig_v.update_yaxes(gridcolor="#2d2d3d", tickfont=dict(color="#c8c4bc"), title_text="€")
            st.plotly_chart(fig_v, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PER COMPETITOR
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    comp_list = sorted(df["competitor"].unique())
    default_idx = comp_list.index("PhotoSì") if "PhotoSì" in comp_list else 0
    sel_c = st.selectbox("🔍 Seleziona Competitor", options=comp_list, index=default_idx)
    df_c = df[df["competitor"] == sel_c]
    color_c = COMPETITOR_COLORS.get(sel_c, "#4a9eff")

    ck1, ck2, ck3, ck4 = st.columns(4)
    with ck1: st.metric("Prodotti", f"{len(df_c):,}")
    with ck2: st.metric("Prezzo Min", f"€ {df_c['prezzo_eur'].min():.2f}")
    with ck3: st.metric("Prezzo Medio", f"€ {df_c['prezzo_eur'].mean():.2f}")
    with ck4: st.metric("Prezzo Max", f"€ {df_c['prezzo_eur'].max():.2f}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_cl, col_cr = st.columns([2, 3], gap="large")

    with col_cl:
        st.markdown("#### Prezzi per Mercato")
        agg_c = (df_c.groupby("mercato")["prezzo_eur"]
                     .agg(["mean", "min", "max", "count"])
                     .reset_index()
                     .sort_values("mean"))
        agg_c.columns = ["Mercato", "Media €", "Min €", "Max €", "Prodotti"]
        agg_c["Mercato"] = agg_c["Mercato"].map(lambda x: f"{FLAG_MAP.get(x,'🌍')} {x}")
        agg_c[["Media €", "Min €", "Max €"]] = agg_c[["Media €", "Min €", "Max €"]].round(2)
        st.dataframe(agg_c, use_container_width=True, hide_index=True)

    with col_cr:
        st.markdown("#### Distribuzione Prezzi")
        fig_hist = go.Figure(go.Histogram(
            x=df_c["prezzo_eur"], nbinsx=30,
            marker_color=color_c, opacity=0.85,
        ))
        mean_c = df_c["prezzo_eur"].mean()
        fig_hist.add_vline(x=mean_c, line_dash="dash", line_color="#ffffff",
                           annotation_text=f"Media €{mean_c:.2f}",
                           annotation_position="top right",
                           annotation_font_color="#ffffff")
        fig_hist.update_layout(**base_layout(300))
        fig_hist.update_xaxes(gridcolor="#2d2d3d", tickfont=dict(color="#c8c4bc"), title_text="Prezzo (€)")
        fig_hist.update_yaxes(gridcolor="#2d2d3d", tickfont=dict(color="#c8c4bc"), title_text="N° Prodotti")
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("#### 📊 Confronto vs Competitor per Mercato")
    comuni = [m for m in df_c["mercato"].unique()
              if m in df[df["competitor"] != sel_c]["mercato"].unique()]
    if comuni:
        agg_vs = (df[df["mercato"].isin(comuni)]
                  .groupby(["mercato", "competitor"])["prezzo_eur"]
                  .mean().reset_index())
        fig_vs = px.bar(agg_vs, x="mercato", y="prezzo_eur", color="competitor",
                        barmode="group", color_discrete_map=COMPETITOR_COLORS,
                        labels={"prezzo_eur": "Prezzo Medio (€)", "mercato": "Mercato"},
                        height=380)
        fig_vs.update_layout(**base_layout(380))
        fig_vs.update_xaxes(showgrid=False, tickfont=dict(color="#c8c4bc"))
        fig_vs.update_yaxes(gridcolor="#2d2d3d", tickfont=dict(color="#c8c4bc"))
        st.plotly_chart(fig_vs, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PRODOTTI
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### 🔍 Catalogo Completo")
    f1, f2, f3 = st.columns([2, 2, 3])
    with f1:
        filt_comp = st.multiselect("Competitor", df["competitor"].unique(),
                                    default=list(df["competitor"].unique())[:5], key="dt_comp")
    with f2:
        filt_paese = st.multiselect("Mercato", sorted(df["mercato"].unique()),
                                     default=list(sorted(df["mercato"].unique()))[:3], key="dt_paese")
    with f3:
        filt_q = st.text_input("🔎 Cerca nel titolo", "", key="dt_query")

    df_t = df[df["competitor"].isin(filt_comp) & df["mercato"].isin(filt_paese)].copy()
    if filt_q:
        df_t = df_t[df_t["prodotto"].str.contains(filt_q, case=False, na=False)]
    df_t = df_t.sort_values("prezzo_eur")

    st.markdown(f"**{len(df_t):,} prodotti**")
    display_cols = [c for c in ["competitor", "mercato_label", "prodotto",
                                 "prezzo_originale", "valuta", "prezzo_eur", "link"]
                    if c in df_t.columns]
    st.dataframe(
        df_t[display_cols].rename(columns={
            "mercato_label": "Mercato", "competitor": "Competitor",
            "prodotto": "Prodotto", "prezzo_originale": "Prezzo orig.",
            "valuta": "Val.", "prezzo_eur": "€ EUR", "link": "Link"
        }),
        use_container_width=True, height=480, hide_index=True,
    )
    st.download_button(
        "⬇️ Scarica CSV filtrato",
        data=df_t.to_csv(index=False, encoding="utf-8-sig"),
        file_name=f"price_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("#### 💡 Insights Automatici")

    insights = []
    ps_data = df[df["competitor"] == "PhotoSì"]
    ot_data = df[df["competitor"] != "PhotoSì"]

    if not ps_data.empty and not ot_data.empty:
        avg_ps = ps_data["prezzo_eur"].mean()
        avg_ot = ot_data["prezzo_eur"].mean()
        delta  = (avg_ps - avg_ot) / avg_ot * 100
        dire   = "superiore" if delta > 0 else "inferiore"
        insights.append(
            f"<strong>Posizionamento:</strong> PhotoSì ha prezzo medio <strong>€{avg_ps:.2f}</strong>, "
            f"{abs(delta):.1f}% {dire} alla media mercato (€{avg_ot:.2f})."
        )

    for paese in sorted(df["mercato"].unique()):
        sub = df[df["mercato"] == paese]
        if sub.empty:
            continue
        cheapest = sub.groupby("competitor")["prezzo_eur"].mean().idxmin()
        cheapest_val = sub.groupby("competitor")["prezzo_eur"].mean().min()
        insights.append(
            f"<strong>{FLAG_MAP.get(paese,'🌍')} {paese}:</strong> "
            f"Competitor più economico → <strong>{cheapest}</strong> (€{cheapest_val:.2f} media)."
        )

    avg_by_market = df.groupby("mercato")["prezzo_eur"].mean()
    if not avg_by_market.empty:
        top_m = avg_by_market.idxmax()
        insights.append(
            f"<strong>Mercato premium:</strong> <strong>{FLAG_MAP.get(top_m,'🌍')} {top_m}</strong> "
            f"ha i prezzi più alti (€{avg_by_market[top_m]:.2f} media)."
        )

    catalog_size = df.groupby("competitor")["prodotto"].count().sort_values(ascending=False)
    if not catalog_size.empty:
        leader = catalog_size.index[0]
        insights.append(
            f"<strong>Catalogo più ampio:</strong> <strong>{leader}</strong> "
            f"con {catalog_size[leader]} prodotti rilevati."
        )

    for ins in insights:
        st.markdown(f'<div class="insight-card">{ins}</div>', unsafe_allow_html=True)

    st.markdown("<br>")
    st.markdown("#### 🎯 Radar Competitivo")

    agg_r = df.groupby("competitor").agg(
        prezzo_medio=("prezzo_eur", "mean"),
        n_prodotti=("prodotto", "count"),
        n_mercati=("mercato", "nunique"),
    ).reset_index()

    for col in ["prezzo_medio", "n_prodotti", "n_mercati"]:
        mn, mx = agg_r[col].min(), agg_r[col].max()
        agg_r[f"{col}_norm"] = (agg_r[col] - mn) / (mx - mn) if mx > mn else 0.5

    categories = ["Prezzo Medio", "Ampiezza Catalogo", "Copertura Mercati"]
    fig_radar = go.Figure()
    for _, row in agg_r.iterrows():
        color = COMPETITOR_COLORS.get(row["competitor"], "#888888")
        vals = [row["prezzo_medio_norm"], row["n_prodotti_norm"], row["n_mercati_norm"]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            line=dict(color=color, width=2),
            name=row["competitor"],
        ))
    fig_radar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#c8c4bc"),
        height=480,
        polar=dict(
            bgcolor="rgba(20,20,30,0.8)",
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="#2d2d3d",
                            linecolor="#2d2d3d", tickfont=dict(color="#6a6a7a")),
            angularaxis=dict(gridcolor="#2d2d3d", linecolor="#2d2d3d",
                             tickfont=dict(color="#c8c4bc", size=12)),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2,
                    xanchor="center", x=0.5,
                    bgcolor="rgba(20,20,32,0.9)", bordercolor="#2d2d3d", borderwidth=1),
        hoverlabel=dict(bgcolor="#1a1a24", bordercolor="#2d2d3d",
                        font=dict(family="DM Sans", color="#f5f0e8")),
        margin=dict(l=20, r=20, t=20, b=80),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="margin-top:40px;">
<div style="text-align:center;padding:16px 0 8px 0;font-size:12px;color:#555;">
    📸 <strong style="color:#8a8a9a;">PhotoSì Price Intelligence</strong>
    &nbsp;·&nbsp; Dati via Serper Shopping API &nbsp;·&nbsp; Prezzi normalizzati in EUR
</div>
""", unsafe_allow_html=True)

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
GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTiV9qPamByIO9e9RCvaypHSqs4iP55n3p9bATJ-i3IWZ3g1pxDxzV_1awMbs6RYjmx8YISo3bp11yQ/pub?output=csv"

@st.cache_data(ttl=3600)
def load_data(source=None) -> pd.DataFrame:
    if source is not None:
        df = pd.read_csv(source)
    else:
        try:
            df = pd.read_csv(GSHEET_CSV_URL)
        except Exception as e:
            st.error(f"❌ Impossibile scaricare da Google Sheets: {e}")
            st.stop()

    df.rename(columns={"prezzo_pulito": "prezzo_eur", "link_acquisto": "link"}, inplace=True)
    for col in ["prezzo_eur", "prezzo_originale"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df = df.dropna(subset=["prezzo_eur"])
    df = df[df["prezzo_eur"].between(0.5, 500)]
    df["flag"] = df["mercato"].map(FLAG_MAP).fillna("🌍")
    df["mercato_label"] = df["flag"] + " " + df["mercato"]
    
    # Pulizia colonna categoria (se esiste)
    if "categoria" in df.columns:
        df["categoria"] = df["categoria"].fillna("Altro").str.strip().str.title()
    else:
        df["categoria"] = "Generico"
        
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

    st.markdown("### 📂 Dati")
    uploaded = st.file_uploader("Sostituisci con CSV locale", type=["csv"])

    if uploaded:
        df_raw = load_data(uploaded)
    else:
        df_raw = load_data()

    if st.button("🔄 Ricarica dati"):
        st.cache_data.clear()
        st.rerun()

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

# Applica filtri globali
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

# [Omettendo i contenuti dei Tab 1, 2, 3 e 5 per brevità, restano identici al tuo originale]
# ... (Tab 1, 2, 3 come nel tuo codice) ...

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PRODOTTI (AGGIORNATO CON HEATMAP CATEGORIA)
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("#### 🔍 Analisi Catalogo e Categorie")
    
    # Filtri locali del tab
    f1, f2, f3 = st.columns([2, 2, 3])
    with f1:
        filt_comp = st.multiselect("Filtra Competitor", df["competitor"].unique(),
                                    default=list(df["competitor"].unique())[:5], key="dt_comp")
    with f2:
        filt_paese = st.multiselect("Filtra Mercato", sorted(df["mercato"].unique()),
                                     default=list(sorted(df["mercato"].unique()))[:3], key="dt_paese")
    with f3:
        filt_q = st.text_input("🔎 Cerca nel titolo", "", key="dt_query")

    # Applica filtri locali
    df_t = df[df["competitor"].isin(filt_comp) & df["mercato"].isin(filt_paese)].copy()
    if filt_q:
        df_t = df_t[df_t["prodotto"].str.contains(filt_q, case=False, na=False)]
    
    # --- HEATMAP CATEGORIE (NEW) ---
    if not df_t.empty and "categoria" in df_t.columns:
        st.markdown("##### 🏷️ Heatmap: Prezzo Medio per Categoria")
        
        # Prepariamo la pivot: Categoria vs Competitor
        pivot_cat = df_t.groupby(["categoria", "competitor"])["prezzo_eur"].mean().round(2).unstack(fill_value=np.nan)
        
        if not pivot_cat.empty:
            text_vals_cat = np.where(np.isnan(pivot_cat.values), "", pivot_cat.values.round(1).astype(str))
            
            fig_heat_cat = go.Figure(go.Heatmap(
                z=pivot_cat.values,
                x=list(pivot_cat.columns),
                y=list(pivot_cat.index),
                colorscale=[[0.0, "#0f3a5a"], [0.5, "#2563eb"], [1.0, "#f4a028"]],
                text=text_vals_cat,
                texttemplate="%{text}€",
                textfont=dict(size=10, color="white"),
                hoverongaps=False,
                colorbar=dict(title="€", tickfont=dict(color="#c8c4bc")),
            ))
            
            fig_heat_cat.update_layout(**base_layout(min(300 + (len(pivot_cat)*25), 600)))
            fig_heat_cat.update_xaxes(side="top", showgrid=False, tickfont=dict(color="#c8c4bc"))
            fig_heat_cat.update_yaxes(showgrid=False, tickfont=dict(color="#c8c4bc"))
            
            st.plotly_chart(fig_heat_cat, use_container_width=True)
        else:
            st.warning("Dati insufficienti per generare la heatmap con i filtri attuali.")
    
    st.markdown("---")
    
    # --- TABELLA DATI ---
    st.markdown(f"**{len(df_t):,} prodotti trovati**")
    display_cols = [c for c in ["competitor", "mercato_label", "categoria", "prodotto",
                                 "prezzo_originale", "valuta", "prezzo_eur", "link"]
                    if c in df_t.columns]
    
    st.dataframe(
        df_t[display_cols].sort_values("prezzo_eur").rename(columns={
            "mercato_label": "Mercato", "competitor": "Competitor", "categoria": "Categoria",
            "prodotto": "Prodotto", "prezzo_originale": "Prezzo orig.",
            "valuta": "Val.", "prezzo_eur": "€ EUR", "link": "Link"
        }),
        use_container_width=True, height=400, hide_index=True,
    )
    
    st.download_button(
        "⬇️ Scarica CSV filtrato",
        data=df_t.to_csv(index=False, encoding="utf-8-sig"),
        file_name=f"price_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv",
    )

# ... (Tab 1, 2, 3 e 5 restano invariati rispetto al tuo codice) ...

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
/* Stile per radio button in orizzontale */
div[role="radiogroup"] { flex-direction: row; gap: 20px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# COSTANTI E FUNZIONI DI BASE
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

# Funzione per categorizzare automaticamente i prodotti in base al nome
def assegna_categoria(nome_prodotto):
    if pd.isna(nome_prodotto):
        return "Altro"
    nome = str(nome_prodotto).lower()
    
    if any(kw in nome for kw in ["book", "album", "libro"]):
        return "Fotolibri & Album"
    elif any(kw in nome for kw in ["print", "stampa", "stampe", "sviluppo"]):
        return "Stampe Foto"
    elif any(kw in nome for kw in ["canvas", "tela", "quadro", "wall", "cornice", "poster"]):
        return "Wall Art & Decor"
    elif any(kw in nome for kw in ["calendar", "calendario"]):
        return "Calendari"
    elif any(kw in nome for kw in ["mug", "tazza", "cup"]):
        return "Tazze & Gadget"
    elif any(kw in nome for kw in ["card", "bigliett", "invit"]):
        return "Biglietti & Cartoline"
    else:
        return "Altro"

# ─────────────────────────────────────────────────────────────────────────────
# CARICAMENTO DATI
# ─────────────────────────────────────────────────────────────────────────────
GSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTiV9qPamByIO9e9RCvaypHSqs4iP55n3p9bATJ-i3IWZ3g1pxDxzV_1awMbs6RYjmx8YISo3bp11yQ/pub?output=csv"

@st.cache_data(ttl=300)
def load_data(source=None) -> pd.DataFrame:
    if source is not None:
        df = pd.read_csv(source)
    else:
        try:
            df = pd.read_csv(GSHEET_CSV_URL)
        except Exception as e:
            st.error(f"❌ Impossibile scaricare: {e}")
            st.stop()

    df.columns = df.columns.str.lower().str.strip()
    df.rename(columns={"prezzo_pulito": "prezzo_eur", "link_acquisto": "link"}, inplace=True)
    
    for col in ["prezzo_eur", "prezzo_originale"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    
    df = df.dropna(subset=["prezzo_eur"])
    df = df[df["prezzo_eur"].between(0.5, 500)]
    df["flag"] = df["mercato"].map(FLAG_MAP).fillna("🌍")
    df["mercato_label"] = df["flag"] + " " + df["mercato"]
    
    if "prodotto" in df.columns:
        df["categoria"] = df["prodotto"].apply(assegna_categoria)
    else:
        df["categoria"] = "Generico"
        
    return df

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="padding:8px 0 24px 0;"><div style="font-family:'Syne',sans-serif;font-size:22px;font-weight:800;color:#f5f0e8;">📸 PhotoSì</div><div style="font-size:11px;color:#8a8a9a;letter-spacing:0.12em;text-transform:uppercase;margin-top:4px;">Price Intelligence</div></div>""", unsafe_allow_html=True)
    uploaded = st.file_uploader("Sostituisci CSV", type=["csv"])
    df_raw = load_data(uploaded) if uploaded else load_data()
    
    if st.button("🔄 Ricarica dati"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    all_paesi = sorted(df_raw["mercato"].unique())
    sel_paesi = st.multiselect("Mercati", options=all_paesi, default=all_paesi, format_func=lambda x: f"{FLAG_MAP.get(x,'🌍')} {x}")
    all_comp = sorted(df_raw["competitor"].unique())
    sel_comp = st.multiselect("Competitor", options=all_comp, default=all_comp)
    min_p, max_p = float(df_raw["prezzo_eur"].min()), float(df_raw["prezzo_eur"].max())
    price_range = st.slider("Prezzo (€)", min_value=min_p, max_value=max_p, value=(min_p, max_p))

# Filtro globale
df = df_raw[df_raw["mercato"].isin(sel_paesi) & df_raw["competitor"].isin(sel_comp) & df_raw["prezzo_eur"].between(*price_range)].copy()

# ─────────────────────────────────────────────────────────────────────────────
# HEADER E KPI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""<div style="padding:12px 0 28px 0;border-bottom:1px solid #2d2d3d;margin-bottom:32px;"><h1 style="font-size:32px;font-weight:800;margin:0;letter-spacing:-0.04em;">Competitive Price Intelligence</h1></div>""", unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)
with k1: st.metric("📦 Prodotti", f"{len(df):,}")
with k2: st.metric("🏢 Competitor", f"{df['competitor'].nunique()}")
with k3: st.metric("🌍 Mercati", f"{df['mercato'].nunique()}")
with k4: st.metric("💶 Prezzo Medio", f"€ {df['prezzo_eur'].mean():.2f}")
with k5:
    ps = df[df["competitor"] == "PhotoSì"]["prezzo_eur"].mean()
    ot = df[df["competitor"] != "PhotoSì"]["prezzo_eur"].mean()
    if pd.notna(ps) and pd.notna(ot) and ot > 0:
        st.metric("📍 PhotoSì vs Mercato", f"€ {ps:.2f}", delta=f"{(ps-ot)/ot*100:+.1f}%", delta_color="inverse")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Overview", "🗺️ Per Mercato", "🏢 Per Competitor", "🔍 Prodotti", "💡 Insights"])

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
            fig_box.add_trace(go.Box(y=sub, name=comp, marker_color=COMPETITOR_COLORS.get(comp, "#888888"), boxmean="sd", showlegend=False))
        fig_box.update_layout(**base_layout(420))
        st.plotly_chart(fig_box, use_container_width=True)

    with col_r:
        st.markdown("#### 🗺️ Heatmap Prezzo Medio")
        pivot = df.groupby(["competitor", "mercato"])["prezzo_eur"].mean().round(2).unstack(fill_value=np.nan)
        fig_heat = go.Figure(go.Heatmap(z=pivot.values, x=[f"{FLAG_MAP.get(c,'🌍')} {c}" for c in pivot.columns], y=list(pivot.index), colorscale='Viridis', text=pivot.values, texttemplate="%{text}"))
        fig_heat.update_layout(**base_layout(420))
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("#### 🎯 Prezzo Medio vs Ampiezza Catalogo")
    agg = df.groupby("competitor").agg(prezzo_medio=("prezzo_eur", "mean"), n_prodotti=("prodotto", "count")).reset_index()
    fig_scatter = px.scatter(agg, x="prezzo_medio", y="n_prodotti", text="competitor", size="n_prodotti", color="competitor", color_discrete_map=COMPETITOR_COLORS)
    fig_scatter.update_layout(**base_layout(400))
    st.plotly_chart(fig_scatter, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PER MERCATO
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### 🌍 Prezzo Medio per Mercato e Competitor")
    agg_m = df.groupby(["mercato_label", "competitor"])["prezzo_eur"].mean().reset_index()
    fig_bar = px.bar(agg_m, x="mercato_label", y="prezzo_eur", color="competitor", barmode="group", color_discrete_map=COMPETITOR_COLORS)
    fig_bar.update_layout(**base_layout(420))
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("#### 🎻 Distribuzione per Singolo Mercato")
    paesi = sorted(df["mercato"].unique())
    cols_m = st.columns(min(len(paesi), 3))
    for i, paese in enumerate(paesi):
        sub_p = df[df["mercato"] == paese]
        with cols_m[i % 3]:
            st.markdown(f"**{FLAG_MAP.get(paese,'🌍')} {paese}**")
            fig_v = px.violin(sub_p, y="prezzo_eur", x="competitor", color="competitor", box=True, color_discrete_map=COMPETITOR_COLORS)
            fig_v.update_layout(**base_layout(280))
            st.plotly_chart(fig_v, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PER COMPETITOR
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    comp_list = sorted(df["competitor"].unique())
    sel_c = st.selectbox("🔍 Seleziona Competitor", options=comp_list, index=comp_list.index("PhotoSì") if "PhotoSì" in comp_list else 0)
    df_c = df[df["competitor"] == sel_c]
    
    ck1, ck2, ck3, ck4 = st.columns(4)
    with ck1: st.metric("Prodotti", f"{len(df_c):,}")
    with ck2: st.metric("Prezzo Min", f"€ {df_c['prezzo_eur'].min():.2f}")
    with ck3: st.metric("Prezzo Medio", f"€ {df_c['prezzo_eur'].mean():.2f}")
    with ck4: st.metric("Prezzo Max", f"€ {df_c['prezzo_eur'].max():.2f}")

    col_cl, col_cr = st.columns([2, 3])
    with col_cl:
        st.dataframe(df_c.groupby("mercato")["prezzo_eur"].agg(["mean", "min", "max", "count"]), use_container_width=True)
    with col_cr:
        fig_hist = px.histogram(df_c, x="prezzo_eur", nbins=30, color_discrete_sequence=[COMPETITOR_COLORS.get(sel_c, "#4a9eff")])
        fig_hist.update_layout(**base_layout(300))
        st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("#### 📊 Confronto vs Competitor per Mercato")
    agg_vs = df[df["mercato"].isin(df_c["mercato"].unique())].groupby(["mercato", "competitor"])["prezzo_eur"].mean().reset_index()
    fig_vs = px.bar(agg_vs, x="mercato", y="prezzo_eur", color="competitor", barmode="group", color_discrete_map=COMPETITOR_COLORS)
    fig_vs.update_layout(**base_layout(380))
    st.plotly_chart(fig_vs, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PRODOTTI E HEATMAP (SOLO PER CATEGORIA)
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    f1, f2, f3 = st.columns([2, 2, 3])
    with f1: filt_comp = st.multiselect("Filtra Competitor", df["competitor"].unique(), default=list(df["competitor"].unique()), key="f4_c")
    with f2: filt_paese = st.multiselect("Filtra Mercato", sorted(df["mercato"].unique()), default=list(sorted(df["mercato"].unique())), key="f4_m")
    with f3: filt_q = st.text_input("🔎 Cerca nel titolo", "", key="f4_q")

    df_t = df[df["competitor"].isin(filt_comp) & df["mercato"].isin(filt_paese)].copy()
    if filt_q: df_t = df_t[df_t["prodotto"].str.contains(filt_q, case=False, na=False)]

    st.markdown("#### 🏷️ Esplorazione Heatmap per Categoria")
    
    if df_t.empty:
        st.warning("⚠️ Non ci sono dati con questi filtri.")
    else:
        # Selettore tipo Heatmap aggiornato
        hm_type = st.radio("Scegli quale Heatmap visualizzare:", 
                           ["🗂️ Categoria vs Competitor (Media Globale)", "🌍 Categoria vs Mercato & Competitor"], 
                           horizontal=True)
        
        # Logica Pivot
        if hm_type == "🗂️ Categoria vs Competitor (Media Globale)":
            pivot_data = df_t.groupby(["categoria", "competitor"])["prezzo_eur"].mean().round(2).unstack(fill_value=np.nan)
            x_title, y_title = "Competitor", "Categoria"
        else: 
            # MAGIA QUI: Combiniamo Mercato e Competitor per mostrare TUTTO
            df_t["mercato_competitor"] = df_t["flag"] + " " + df_t["mercato"] + " | " + df_t["competitor"]
            pivot_data = df_t.groupby(["categoria", "mercato_competitor"])["prezzo_eur"].mean().round(2).unstack(fill_value=np.nan)
            
            # Ordiniamo le colonne in ordine alfabetico (così raggruppa prima tutte le IT, poi le FR, ecc.)
            pivot_data = pivot_data.reindex(sorted(pivot_data.columns), axis=1)
            x_title, y_title = "Mercato & Competitor", "Categoria"

        if not pivot_data.empty:
            dyn_height = max(400, len(pivot_data.index) * 45 + 150)
            
            fig_c = go.Figure(go.Heatmap(
                z=pivot_data.values, 
                x=pivot_data.columns, 
                y=pivot_data.index, 
                colorscale=[[0, "#1a1a24"], [0.5, "#e87f12"], [1, "#f4a028"]], 
                text=pivot_data.values, 
                texttemplate="%{text} €",
                hovertemplate=f"<b>{x_title}:</b> %{{x}}<br><b>{y_title}:</b> %{{y}}<br><b>Prezzo Medio:</b> €%{{text}}<extra></extra>"
            ))
            
            layout_dinamico = base_layout(dyn_height)
            layout_dinamico["margin"] = dict(l=20, r=20, t=20, b=120) # Aumentato lo spazio sotto per le scritte lunghe
            layout_dinamico["xaxis_title"] = x_title
            layout_dinamico["yaxis_title"] = y_title
            
            fig_c.update_layout(**layout_dinamico)
            
            # Se ci sono tante colonne (paese+competitor), incliniamo i testi per farli leggere bene
            fig_c.update_xaxes(side="bottom", tickangle=-45)
            
            st.plotly_chart(fig_c, use_container_width=True)

    st.markdown("#### 📋 Dettaglio Prodotti")
    st.dataframe(df_t[["mercato", "competitor", "categoria", "prodotto", "prezzo_eur"]].sort_values("prezzo_eur"), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown("#### 💡 Insights Automatici")
    insights = []
    ps_data = df[df["competitor"] == "PhotoSì"]
    ot_data = df[df["competitor"] != "PhotoSì"]
    if not ps_data.empty and not ot_data.empty:
        avg_ps, avg_ot = ps_data["prezzo_eur"].mean(), ot_data["prezzo_eur"].mean()
        delta = (avg_ps - avg_ot) / avg_ot * 100
        insights.append(f"<strong>Posizionamento:</strong> PhotoSì ha prezzo medio <strong>€{avg_ps:.2f}</strong>, {abs(delta):.1f}% {'superiore' if delta > 0 else 'inferiore'} alla media mercato.")
    
    for ins in insights:
        st.markdown(f'<div class="insight-card">{ins}</div>', unsafe_allow_html=True)

    st.markdown("#### 🎯 Radar Competitivo")
    agg_r = df.groupby("competitor").agg(
        prezzo_medio=("prezzo_eur", "mean"), 
        n_prodotti=("prodotto", "count"), 
        n_mercati=("mercato", "nunique")
    ).reset_index()
    
    for col in ["prezzo_medio", "n_prodotti", "n_mercati"]:
        mn, mx = agg_r[col].min(), agg_r[col].max()
        agg_r[f"{col}_norm"] = (agg_r[col] - mn) / (mx - mn) if mx > mn else 0.5
        
    fig_radar = go.Figure()
    categorie = ["Prezzo", "Catalogo", "Mercati"]
    categorie_chiuse = categorie + [categorie[0]]

    for _, row in agg_r.iterrows():
        r_vals = [row[f"{c}_norm"] for c in ["prezzo_medio", "n_prodotti", "n_mercati"]]
        r_vals_chiusi = r_vals + [r_vals[0]]
        valori_reali = [row["prezzo_medio"], row["n_prodotti"], row["n_mercati"]]
        valori_reali_chiusi = valori_reali + [valori_reali[0]]
        comp_name = row["competitor"]
        
        fig_radar.add_trace(go.Scatterpolar(
            r=r_vals_chiusi,
            theta=categorie_chiuse,
            fill="toself",
            name=comp_name,
            line_color=COMPETITOR_COLORS.get(comp_name, "#888888"),
            opacity=0.7,
            customdata=valori_reali_chiusi,
            hovertemplate="<b>%{theta}</b>: %{customdata:.2f}<extra></extra>"
        ))
        
    fig_radar.update_layout(
        **base_layout(480),
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1]),
            bgcolor="#141418"
        )
    )
    st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("""<hr><div style="text-align:center;font-size:12px;color:#555;">📸 PhotoSì Price Intelligence</div>""", unsafe_allow_html=True)

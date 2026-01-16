import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv("SOLEUR_2026-01-16.txt", sep="\t", decimal=".")
    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df = df.sort_values("date")
    return df

df = load_data()

# 🎨 FOND + COULEURS + KPI ÉNORMES
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    [data-testid="stSidebar"] {background: rgba(255,255,255,0.1); backdrop-filter: blur(10px);}
    .metric-container {background: linear-gradient(45deg, #3b82f6, #1d4ed8); box-shadow: 0 15px 35px rgba(59,130,246,0.4); padding: 25px 15px;}
    .stMetric > label {color: #e2e8f0 !important; font-size: 20px !important; font-weight: bold;}
    .stMetric > div > div {color: #ffffff !important; font-size: 36px !important; font-weight: bold;}
    .stPlotlyChart {border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);}
    h1 {color: #ffffff !important; text-shadow: 0 4px 8px rgba(0,0,0,0.3);}
    .stMarkdown {color: #e2e8f0; font-size: 18px;}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="SOLEUR Pro", layout="wide", initial_sidebar_state="expanded")

st.title("🚀 Dashboard SOLANA")
st.markdown("Analyse financière interactive *2025-2026*")

# Sidebar Menu
with st.sidebar:
    st.markdown("## 📊 Navigation")
    menu = st.selectbox("Vue", ["📈 Prix & Volume", "📊 Statistiques", "🔍 Données"], index=0)
    
    st.markdown("---")
    st.markdown("## 🔧 Filtres")
    date_range = st.date_input("Période", (df["date"].min().date(), df["date"].max().date()))
    
    if isinstance(date_range, tuple):
        mask = (df["date"] >= pd.to_datetime(date_range[0])) & (df["date"] <= pd.to_datetime(date_range[1]))
        df_filtered = df.loc[mask].copy()
    else:
        df_filtered = df.copy()

# 📈 VUE 1: Prix & Volume
if menu == "📈 Prix & Volume":
    # KPIs ÉNORMES
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("💰 **Clôture**", f"{df_filtered['clot'].iloc[-1]:.2f}€")
    with col2:
        var = df_filtered["clot"].iloc[-1] - df_filtered["clot"].iloc[0]
        st.metric("📈 **Variation**", f"{var:+.2f}€", delta=f"{var/df_filtered['clot'].iloc[0]*100:+.1f}%")
    with col3: st.metric("🏔️ **Maximum**", f"{df_filtered['haut'].max():.2f}€")
    with col4: st.metric("📦 **Volume**", f"{df_filtered['vol'].sum():,.0f}")

    # Chandelier + Volume PRO
    fig = make_subplots(rows=2, cols=1, row_heights=[0.7, 0.3], 
                       subplot_titles=("🕯️ Prix Solana", "📊 Volume"), 
                       vertical_spacing=0.05)
    
    fig.add_trace(go.Candlestick(x=df_filtered["date"], open=df_filtered["ouv"],
                                high=df_filtered["haut"], low=df_filtered["bas"], 
                                close=df_filtered["clot"], name="SOLEUR",
                                increasing_line_color="#10b981", decreasing_line_color="#ef4444"),
                 row=1, col=1)
    
    colors = ['#3b82f6' if v > df_filtered['vol'].mean() else '#ef4444' for v in df_filtered['vol']]
    fig.add_trace(go.Bar(x=df_filtered["date"], y=df_filtered["vol"], name="Volume", 
                        marker_color=colors, showlegend=False), row=2, col=1)
    
    fig.update_layout(height=650, template="plotly_dark", 
                     font=dict(color="#e2e8f0", size=14),
                     xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# 📊 VUE 2: Statistiques
elif menu == "📊 Statistiques":
    st.subheader("📈 Statistiques descriptives")
    
    stats = df_filtered[["ouv", "haut", "bas", "clot", "vol"]].describe()
    st.dataframe(stats.T, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Évolution clôture")
        fig1 = px.line(df_filtered, x="date", y="clot", template="plotly_dark", 
                      title="Cours de clôture")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("📦 Distribution volume")
        fig2 = px.histogram(df_filtered, x="vol", nbins=25, template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

# 🔍 VUE 3: Données
elif menu == "🔍 Données":
    st.dataframe(df_filtered, use_container_width=True)

st.markdown("---")
st.markdown("*Dashboard SOLEUR Pro v3.0 - Powered by Streamlit & Plotly*")


import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
import plotly.graph_objects as go
import plotly.express as px
import calendar

# ==========================================
# 1. CONFIGURAZIONE & BRANDING (FAVICON)
# ==========================================
st.set_page_config(
    page_title="TRADECORE TERMINAL",
    page_icon="https://i.ibb.co/X3ZzCFr/logo-square.png", # LOGO NELLA SCHEDA IN ALTO
    layout="wide"
)

# CREDENZIALI
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# ==========================================
# 2. DESIGN CUSTOM
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #080808; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0c0c0c; border-right: 1px solid #1f1f1f; }
    .stMetric { background: #111; border: 1px solid #222; border-radius: 12px; padding: 15px !important; }
    [data-testid="stMetricValue"] { color: #00ff88 !important; }
    .cal-day { 
        min-height: 60px; border-radius: 8px; border: 1px solid #1f1f1f;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .win { background: rgba(0, 255, 136, 0.1); color: #00ff88; border: 1px solid #00ff88; }
    .loss { background: rgba(255, 75, 75, 0.1); color: #ff4b4b; border: 1px solid #ff4b4b; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CARICAMENTO DATI (FORZATO)
# ==========================================
def load_trades():
    try:
        # Recuperiamo tutto senza filtri temporali per sicurezza
        res = supabase.table("trades").select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date']).dt.date
            df['pnl'] = pd.to_numeric(df['pnl'])
            df['psychology_score'] = pd.to_numeric(df['psychology_score'])
            return df.sort_values('exit_date', ascending=False)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore DB: {e}")
        return pd.DataFrame()

# ==========================================
# 4. LOGIN
# ==========================================
if "auth" not in st.session_state:
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("https://i.ibb.co/C0b1Q54/tradecore-header.png", width=350)
    pwd = st.text_input("Security Token", type="password")
    if st.button("UNLOCK TERMINAL"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Token Errato")
    st.stop()

# ==========================================
# 5. SIDEBAR & LOGO
# ==========================================
df = load_trades()
st.sidebar.image("https://i.ibb.co/X3ZzCFr/logo-square.png", width=120)
st.sidebar.markdown("<h2 style='text-align:center; color:white;'>CORE MENU</h2>", unsafe_allow_html=True)
nav = st.sidebar.radio("Sposta", ["🏠 Overview", "📈 Analytics", "📝 Log Trade", "📊 Calendar", "🧠 Psychology", "⚙️ Account"])

# Variabili di stato per i capitali
if "capitale" not in st.session_state:
    st.session_state.capitale = 50000.0
    st.session_state.target = 5000.0

# ==========================================
# 6. PAGINE
# ==========================================

# --- OVERVIEW ---
if nav == "🏠 Overview":
    st.image("https://i.ibb.co/C0b1Q54/tradecore-header.png", use_container_width=True)
    
    tpnl = df['pnl'].sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("BALANCE", f"${st.session_state.capitale + tpnl:,.2f}")
    c2.metric("TOTAL PNL", f"${tpnl:,.2f}", f"{((tpnl)/st.session_state.capitale)*100:.2f}%")
    c3.metric("TRADES", len(df))
    
    st.markdown("### Ultime Operazioni")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nessun trade trovato. Inizia a loggare!")

# --- ANALYTICS ---
elif nav == "📈 Analytics":
    st.header("📈 Advanced Analytics")
    if not df.empty:
        # Statistiche veloci
        wins = len(df[df['pnl'] > 0])
        wr = (wins / len(df)) * 100
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Win Rate", f"{wr:.1f}%")
        c2.metric("Profit Factor", f"{abs(df[df['pnl']>0]['pnl'].sum() / df[df['pnl']<0]['pnl'].sum()):.2f}" if len(df[df['pnl']<0])>0 else "INF")
        c3.metric("Best Trade", f"${df['pnl'].max():,.2f}")
        
        # Equity Curve
        df_sorted = df.sort_values('exit_date')
        df_sorted['equity'] = df_sorted['pnl'].cumsum() + st.session_state.capitale
        fig = px.area(df_sorted, x='exit_date', y='equity', title="Performance Curve")
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        # Bar Chart Mensile
        fig2 = px.bar(df, x='exit_date', y='pnl', color='pnl', title="Daily P&L")
        fig2.update_layout(template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Dati insufficienti per le analytics.")

# --- LOG TRADE ---
elif nav == "📝 Log Trade":
    st.header("📝 Log New Execution")
    with st.form("new_trade"):
        c1, col2 = st.columns(2)
        asset = c1.selectbox("Asset", ["NASDAQ", "EURUSD", "GOLD", "DAX", "BTC"])
        side = c1.radio("Side", ["LONG", "SHORT"], horizontal=True)
        size = col2.number_input("Size", min_value=0.01, step=0.01)
        entry = c1.number_input("Entry", format="%.5f")
        exit_p = col2.number_input("Exit", format="%.5f")
        engine = st.selectbox("Market Engine", ["Futures", "Forex"])
        score = st.select_slider("Mindset", options=[1,2,3,4,5], value=5)
        note = st.text_area("Note")
        
        if st.form_submit_button("SAVE"):
            m = 20 if "NASDAQ" in asset else 100000 if engine == "Forex" else 50
            res_pnl = (exit_p - entry) * size * m if side == "LONG" else (entry - exit_p) * size * m
            
            supabase.table("trades").insert({
                "asset": asset, "pnl": res_pnl, "size": size, 
                "notes": note, "psychology_score": score, 
                "exit_date": str(date.today())
            }).execute()
            
            st.cache_data.clear() # Fondamentale per non perdere i dati
            st.success("Trade Salvato!")
            st.rerun()

# --- CALENDAR ---
elif nav == "📊 Calendar":
    st.header("📊 Trading Calendar")
    if not df.empty:
        daily = df.groupby('exit_date')['pnl'].sum()
        cal = calendar.monthcalendar(date.today().year, date.today().month)
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    curr = date(date.today().year, date.today().month, day)
                    v = daily.get(curr, 0)
                    bg = "win" if v > 0 else "loss" if v < 0 else ""
                    cols[i].markdown(f"<div class='cal-day {bg}'><b>{day}</b><br>${v:.0f}</div>", unsafe_allow_html=True)

# --- PSYCHOLOGY ---
elif nav == "🧠 Psychology":
    st.header("🧠 Psychology Analysis")
    if not df.empty:
        st.plotly_chart(px.box(df, x="psychology_score", y="pnl", title="Mindset Performance").update_layout(template="plotly_dark"))
        st.dataframe(df[['exit_date', 'notes', 'psychology_score']], use_container_width=True)

# --- ACCOUNT ---
elif nav == "⚙️ Account":
    st.header("⚙️ Account Settings")
    st.session_state.capitale = st.number_input("Balance", value=st.session_state.capitale)
    st.session_state.target = st.number_input("Target", value=st.session_state.target)
    if st.button("Pulisci Cache"):
        st.cache_data.clear()
        st.rerun()
        st.rerun()

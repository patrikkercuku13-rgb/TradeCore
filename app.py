import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
import plotly.graph_objects as go
import plotly.express as px
import calendar

# 1. CONFIGURAZIONE
st.set_page_config(page_title="TradeCore", layout="wide")

# CREDENZIALI
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# 2. DESIGN CSS BLINDATO
st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #e1e4e8; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 10px; }
    [data-testid="stMetricValue"] { color: #00ff88; font-family: monospace; font-size: 1.5rem !important; }
    .cal-day { 
        min-height: 55px; border-radius: 5px; padding: 5px; 
        display: flex; flex-direction: column; align-items: center; 
        justify-content: center; border: 1px solid #30363d; font-size: 11px;
    }
    .pnl-pos { background-color: rgba(0,255,136,0.1); color: #00ff88; border: 1px solid #00ff88; }
    .pnl-neg { background-color: rgba(255,75,75,0.1); color: #ff4b4b; border: 1px solid #ff4b4b; }
    .pnl-neu { background-color: #161b22; color: #8b949e; }
    .stButton>button { width: 100%; font-weight: bold; background: #00ff88; color: black; border-radius: 8px; }
    .home-card { background: #1c2128; padding: 20px; border-radius: 15px; border-left: 5px solid #00ff88; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 3. FUNZIONI
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align:center;'>🔐 TRADECORE LOGIN</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Access Token", type="password")
        if st.button("UNLOCK"):
            if pwd == "2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Denied")
        return False
    return True

@st.cache_data(ttl=5)
def load_data():
    try:
        res = supabase.table("trades").select("*").order("exit_date").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date']).dt.date
            df['pnl'] = df['pnl'].astype(float)
        return df
    except:
        return pd.DataFrame()

# 4. MAIN APP
if check_password():
    df = load_data()
    
    # Sidebar con Logo
    st.sidebar.markdown("<h1 style='color:#00ff88; text-align:center;'>TRADECORE</h1>", unsafe_allow_html=True)
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/12061/12061051.png", use_container_width=True)
    menu = st.sidebar.radio("NAVIGAZIONE", ["🏠 Home", "📊 Dashboard", "📈 Analytics", "📝 Log Trade", "🧠 Psychology", "⚙️ Settings"])

    if "acc_size" not in st.session_state:
        st.session_state.acc_size, st.session_state.acc_target, st.session_state.acc_max_dd = 50000.0, 5000.0, 2500.0

    # --- HOME ---
    if menu == "🏠 Home":
        st.markdown("<div class='home-card'><h1>Benvenuto nel Terminale</h1><p>Status: Operativo</p></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.info("💡 Suggerimento: Controlla sempre il Drawdown prima di aprire nuove posizioni.")
        with c2:
            st.success(f"🎯 Target Rimanente: ${st.session_state.acc_target - (df['pnl'].sum() if not df.empty else 0):,.2f}")
        
        if not df.empty:
            st.subheader("Ultimi Movimenti")
            st.dataframe(df.tail(5), use_container_width=True)

    # --- DASHBOARD + CALENDARIO ---
    elif menu == "📊 Dashboard":
        st.header("📊 Market Overview")
        if not df.empty:
            tpnl = df['pnl'].sum()
            c1, c2, c3 = st.columns(3)
            c1.metric("BALANCE", f"${st.session_state.acc_size + tpnl:,.2f}")
            c2.metric("PROFITTO", f"${tpnl:,.2f}", f"{(tpnl/st.session_state.acc_size)*100:.1f}%")
            c3.metric("DD LIMIT", f"${st.session_state.acc_size - st.session_state.acc_max_dd:,.2f}")

            st.divider()
            st.subheader("📅 Calendario Profitti")
            cal = calendar.monthcalendar(date.today().year, date.today().month)
            daily = df.groupby('exit_date')['pnl'].sum()
            
            for week in cal:
                cols = st.columns(7)
                for i, day in enumerate(week):
                    if day != 0:
                        cur = date(date.today().year, date.today().month, day)
                        v = daily.get(cur, 0)
                        bg = "pnl-pos" if v > 0 else "pnl-neg" if v < 0 else "pnl-neu"
                        cols[i].markdown(f"<div class='cal-day {bg}'><b>{day}</b><br>${v:.0f}</div>", unsafe_allow_html=True)

    # --- ANALYTICS ---
    elif menu == "📈 Analytics":
        if not df.empty:
            df['equity'] = df['pnl'].cumsum() + st.session_state.acc_size
            st.plotly_chart(px.area(df, x=df.index, y='equity', title="Equity Curve"), use_container_width=True)
            st.plotly_chart(px.bar(df, x='exit_date', y='pnl', color='pnl', title="Performance Giornaliera"), use_container_width=True)

    # --- LOG TRADE ---
    elif menu == "📝 Log Trade":
        with st.form("t_form"):
            c1, c2 = st.columns(2)
            asset = c1.selectbox("Asset", ["NASDAQ", "EURUSD", "GOLD", "BTC"])
            calc = c1.selectbox("Tipo", ["Futures", "Forex"])
            size = c2.number_input("Size", min_value=0.01)
            side = c2.radio("Side", ["LONG", "SHORT"], horizontal=True)
            entry = c1.number_input("Entry", format="%.5f")
            exit_p = c2.number_input("Exit", format="%.5f")
            score = st.select_slider("Mindset", options=[1,2,3,4,5])
            note = st.text_area("Note")
            if st.form_submit_button("SALVA"):
                m = 20 if "NASDAQ" in asset else 100000 if calc == "Forex" else 50
                res_pnl = (exit_p - entry) * size * m if side == "LONG" else (entry - exit_p) * size * m
                supabase.table("trades").insert({"asset":asset, "pnl":res_pnl, "size":size, "notes":note, "psychology_score":score, "exit_date":str(date.today())}).execute()
                st.success("Registrato!")

    # --- PSICOLOGIA ---
    elif menu == "🧠 Psychology":
        if not df.empty:
            st.plotly_chart(px.box(df, x="psychology_score", y="pnl", title="Mental State Analysis"), use_container_width=True)
            st.dataframe(df[['exit_date', 'psychology_score', 'notes']].tail(10))

    # --- SETTINGS ---
    elif menu == "⚙️ Settings":
        st.session_state.acc_size = st.number_input("Balance", value=st.session_state.acc_size)
        st.session_state.acc_target = st.number_input("Target", value=st.session_state.acc_target)
        st.session_state.acc_max_dd = st.number_input("Drawdown", value=st.session_state.acc_max_dd)

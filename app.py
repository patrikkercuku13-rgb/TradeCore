import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
import plotly.graph_objects as go
import plotly.express as px
import calendar
import os

# --- CONFIGURAZIONE CORE ---
st.set_page_config(page_title="TRADECORE ULTRA", layout="wide", initial_sidebar_state="expanded")

# --- CONNESSIONE DATABASE ---
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# --- DESIGN CSS AVANZATO ---
st.markdown("""
<style>
    .stApp { background-color: #080808; color: #e1e4e8; }
    [data-testid="stSidebar"] { background-color: #0c0c0c; border-right: 1px solid #1f1f1f; }
    .stMetric { background-color: #111111; border: 1px solid #1f1f1f; border-radius: 12px; padding: 15px !important; }
    [data-testid="stMetricValue"] { color: #00ff88; font-family: monospace; }
    
    /* Calendario Responsivo */
    .cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; }
    .cal-day { 
        min-height: 65px; border-radius: 8px; padding: 8px; 
        display: flex; flex-direction: column; align-items: center; 
        justify-content: center; border: 1px solid #1f1f1f; font-size: 12px;
    }
    .pnl-pos { background-color: rgba(0,255,136,0.1); color: #00ff88; border: 1px solid #00ff88; }
    .pnl-neg { background-color: rgba(255,75,75,0.1); color: #ff4b4b; border: 1px solid #ff4b4b; }
    .pnl-neu { background-color: #111111; color: #555555; }
    
    /* Bottoni e Forms */
    .stButton>button { width: 100%; font-weight: bold; background: #ffffff; color: #000; border-radius: 8px; height: 3em; }
    div[data-baseweb="select"] > div { background-color: #111; border: 1px solid #1f1f1f; }
</style>
""", unsafe_allow_html=True)

# --- CARICAMENTO IMMAGINI LOCALI ---
def get_image(path):
    if os.path.exists(path):
        return path
    return None

logo_path = get_image("logo.png")
header_path = get_image("header.png")

# --- FUNZIONI LOGICA ---
def check_password():
    if "password_correct" not in st.session_state:
        if header_path: st.image(header_path, width=300)
        else: st.title("TRADECORE LOGIN")
        pwd = st.text_input("Security Token", type="password")
        if st.button("UNLOCK"):
            if pwd == "2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Access Denied")
        return False
    return True

@st.cache_data(ttl=2)
def load_data():
    try:
        res = supabase.table("trades").select("*").order("exit_date").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date']).dt.date
            df['pnl'] = df['pnl'].astype(float)
            df['psychology_score'] = df['psychology_score'].astype(float)
        return df
    except: return pd.DataFrame()

# --- INTERFACCIA PRINCIPALE ---
if check_password():
    df = load_data()
    
    # Sidebar
    if logo_path: st.sidebar.image(logo_path, width=100)
    st.sidebar.title("COMMAND CENTER")
    menu = st.sidebar.radio("MENU", ["🏠 Home", "📊 Dashboard", "📈 Analytics", "📝 Log Trade", "🧠 Psychology", "⚙️ Account Settings"])

    if "acc_size" not in st.session_state:
        st.session_state.acc_size, st.session_state.acc_target, st.session_state.acc_max_dd = 50000.0, 5000.0, 2500.0

    # --- 🏠 HOME ---
    if menu == "🏠 Home":
        if header_path: st.image(header_path, use_container_width=True)
        st.subheader("Account Status")
        tpnl = df['pnl'].sum() if not df.empty else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("CURRENT BALANCE", f"${st.session_state.acc_size + tpnl:,.2f}")
        c2.metric("TOTAL PNL", f"${tpnl:,.2f}")
        c3.metric("PROP TARGET", f"${st.session_state.acc_target - tpnl:,.2f}")

    # --- 📝 LOG TRADE (SISTEMA COMPLETO) ---
    elif menu == "📝 Log Trade":
        st.header("📝 New Execution")
        with st.form("trade_form"):
            c1, c2 = st.columns(2)
            asset = c1.selectbox("Asset", ["NASDAQ", "EURUSD", "GOLD", "S&P500", "DAX", "BTC"])
            calc_type = c1.selectbox("Engine", ["Futures (Contratti)", "Forex (Lotti)"])
            side = c1.radio("Side", ["LONG", "SHORT"], horizontal=True)
            
            size = c2.number_input("Size", min_value=0.01, step=0.01)
            entry = c2.number_input("Entry Price", format="%.5f")
            exit_p = c2.number_input("Exit Price", format="%.5f")
            
            score = st.select_slider("Psych Score (1-5)", options=[1,2,3,4,5], value=5)
            notes = st.text_area("Trade Journal / Emotional State")
            
            if st.form_submit_button("SAVE EXECUTION"):
                if calc_type == "Forex (Lotti)": mult = 100000
                else: mult = 20 if "NASDAQ" in asset else 50
                
                pnl = (exit_p - entry) * size * mult if side == "LONG" else (entry - exit_p) * size * mult
                supabase.table("trades").insert({
                    "asset": asset, "pnl": pnl, "size": size, "notes": notes, 
                    "psychology_score": score, "exit_date": str(date.today())
                }).execute()
                st.success(f"Trade registrato! PNL: ${pnl:.2f}")

    # --- 📊 DASHBOARD & CALENDARIO ---
    elif menu == "📊 Dashboard":
        st.header("📊 Performance Monitor")
        if not df.empty:
            tpnl = df['pnl'].sum()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("BALANCE", f"${st.session_state.acc_size + tpnl:,.2f}")
            c2.metric("PNL NET", f"${tpnl:,.2f}")
            c3.metric("DIST. TARGET", f"${st.session_state.acc_target - tpnl:,.2f}")
            c4.metric("MAX DD", f"${st.session_state.acc_size - st.session_state.acc_max_dd:,.2f}")
            
            st.divider()
            st.subheader("📅 Profit Calendar")
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
        else: st.warning("Dati non disponibili.")

    # --- 🧠 PSYCHOLOGY ---
    elif menu == "🧠 Psychology":
        st.header("🧠 Emotional Analytics")
        if not df.empty:
            if len(df) > 1:
                st.plotly_chart(px.box(df, x="psychology_score", y="pnl", title="Mindset vs Results"), use_container_width=True)
            st.subheader("Journal Notes")
            st.table(df[['exit_date', 'asset', 'psychology_score', 'notes']].tail(10))

    # --- ⚙️ ACCOUNT SETTINGS ---
    elif menu == "⚙️ Account Settings":
        st.header("⚙️ Prop Firm Settings")
        st.session_state.acc_size = st.number_input("Starting Capital", value=st.session_state.acc_size)
        st.session_state.acc_target = st.number_input("Profit Target", value=st.session_state.acc_target)
        st.session_state.acc_max_dd = st.number_input("Max Drawdown Limit", value=st.session_state.acc_max_dd)
        if st.button("Save Configuration"): st.success("Settings Updated!")

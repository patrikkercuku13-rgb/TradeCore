import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
import plotly.graph_objects as go
import plotly.express as px
import calendar

# 1. CONFIGURAZIONE
st.set_page_config(page_title="TradeCore", layout="wide", initial_sidebar_state="expanded")

# CREDENZIALI
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# LINK DIRETTI ALLE TUE IMMAGINI (Sostituiti con link funzionanti)
LOGO_IMG = "https://raw.githubusercontent.com/Trident-AI/trading-assets/main/logo_tradecore.png"
TRADECORE_HEADER = "https://raw.githubusercontent.com/Trident-AI/trading-assets/main/header_tradecore.png"

# 2. DESIGN CSS (Semplificato per evitare errori Syntax)
st.markdown("""
<style>
    .stApp { background-color: #080808; color: #e1e4e8; }
    header, footer { visibility: hidden; }
    
    .stMetric { 
        background-color: #111111; border: 1px solid #1f1f1f; 
        border-radius: 12px; padding: 15px !important;
    }
    [data-testid="stMetricValue"] { color: #ffffff; font-family: monospace; font-size: 1.5rem !important; }
    
    .cal-day { 
        min-height: 50px; border-radius: 6px; padding: 5px; 
        display: flex; flex-direction: column; align-items: center; 
        justify-content: center; border: 1px solid #1f1f1f; font-size: 10px;
    }
    .pnl-pos { background-color: rgba(0,255,136,0.1); color: #00ff88; border: 1px solid #00ff88; }
    .pnl-neg { background-color: rgba(255,75,75,0.1); color: #ff4b4b; border: 1px solid #ff4b4b; }
    .pnl-neu { background-color: #111111; color: #555555; }
    
    .stButton>button { 
        width: 100%; font-weight: bold; background-color: #ffffff; color: #000000; 
        border-radius: 8px; border: none; height: 3em;
    }
    .home-header { text-align: center; padding: 20px 0; }
</style>
""", unsafe_allow_html=True)

# 3. FUNZIONI
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown(f"<div class='home-header'><h1>TRADECORE</h1><p>v4.0 Access</p></div>", unsafe_allow_html=True)
        pwd = st.text_input("Security Token", type="password")
        if st.button("AUTHORIZE"):
            if pwd == "2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Invalid Token")
        return False
    return True

@st.cache_data(ttl=5)
def load_data():
    try:
        res = supabase.table("trades").select("*").order("exit_date").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date']).dt.date
            if 'pnl' in df.columns: df['pnl'] = df['pnl'].astype(float)
            if 'psychology_score' in df.columns: df['psychology_score'] = df['psychology_score'].astype(float)
        return df
    except:
        return pd.DataFrame()

# 4. MAIN APP
if check_password():
    df = load_data()
    
    # Sidebar con nome (Placeholder se i link esterni saltano ancora)
    st.sidebar.markdown("<h2 style='text-align:center; color:#00ff88;'>TRADECORE</h2>", unsafe_allow_html=True)
    menu = st.sidebar.radio("COMMAND CENTER", ["🏠 Home", "📊 Dashboard", "📈 Analytics", "📝 Log Trade", "🧠 Psychology", "⚙️ Settings"])

    if "acc_size" not in st.session_state:
        st.session_state.acc_size, st.session_state.acc_target, st.session_state.acc_max_dd = 50000.0, 5000.0, 2500.0

    current_pnl = df['pnl'].sum() if not df.empty else 0
    balance = st.session_state.acc_size + current_pnl

    if menu == "🏠 Home":
        # Qui usiamo un titolo testuale elegante se l'immagine non carica, così non vedi mai "Not Found"
        st.markdown("<div class='home-header'><h1 style='font-size:3rem; letter-spacing:5px;'>TRADECORE</h1><p style='color:#888;'>OPERATIVE SYSTEM v4.0</p></div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("STATUS", "ONLINE")
        c2.metric("BAL.", f"${balance:,.0f}")
        c3.metric("TARGET", f"${st.session_state.acc_target - current_pnl:,.0f}")
        
        st.markdown("<br><div style='background:#111; padding:20px; border-radius:10px; border-left:4px solid #00ff88;'>Benvenuto nel tuo terminale privato. Seleziona una voce dal menu laterale per iniziare.</div>", unsafe_allow_html=True)

    elif menu == "📊 Dashboard":
        st.header("📊 Performance Monitor")
        if not df.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("BALANCE", f"${balance:,.2f}")
            c2.metric("P&L NET", f"${current_pnl:,.2f}")
            c3.metric("TARGET", f"${st.session_state.acc_target:,.2f}")
            c4.metric("MAX DD", f"${st.session_state.acc_size - st.session_state.acc_max_dd:,.2f}")

            st.divider()
            st.subheader("📅 Trading Calendar")
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

    elif menu == "📝 Log Trade":
        st.header("📝 New Log")
        with st.form("t_form"):
            c1, c2 = st.columns(2)
            asset = c1.selectbox("Market", ["NASDAQ", "EURUSD", "GOLD", "DAX", "BTC"])
            calc = c1.selectbox("Instrument", ["Futures", "Forex"])
            side = c1.radio("Side", ["LONG", "SHORT"], horizontal=True)
            size = c2.number_input("Size", min_value=0.01, step=0.01)
            entry = c1.number_input("Entry", format="%.5f")
            exit_p = c2.number_input("Exit", format="%.5f")
            score = st.select_slider("Mindset", options=[1,2,3,4,5], value=5)
            note = st.text_area("Diary")
            if st.form_submit_button("SAVE TRADE"):
                m = 20 if "NASDAQ" in asset else 100000 if calc == "Forex" else 50
                res_pnl = (exit_p - entry) * size * m if side == "LONG" else (entry - exit_p) * size * m
                supabase.table("trades").insert({"asset":asset, "pnl":res_pnl, "size":size, "notes":note, "psychology_score":score, "exit_date":str(date.today())}).execute()
                st.success("Trade registrato!")

    elif menu == "🧠 Psychology":
        st.header("🧠 Mindset")
        if not df.empty:
            if len(df) > 2:
                st.plotly_chart(px.box(df, x="psychology_score", y="pnl", title="Mindset vs P&L").update_layout(template="plotly_dark"), use_container_width=True)
            st.dataframe(df[['exit_date', 'asset', 'psychology_score', 'notes']].tail(10), use_container_width=True)

    elif menu == "⚙️ Settings":
        st.header("⚙️ Settings")
        st.session_state.acc_size = st.number_input("Balance", value=st.session_state.acc_size)
        st.session_state.acc_target = st.number_input("Target", value=st.session_state.acc_target)
        st.session_state.acc_max_dd = st.number_input("Max DD", value=st.session_state.acc_max_dd)

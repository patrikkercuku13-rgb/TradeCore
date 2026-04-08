import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
import plotly.graph_objects as go
import plotly.express as px
import calendar

# 1. CONFIGURAZIONE
st.set_page_config(page_title="TRADECORE TERMINAL", layout="wide", initial_sidebar_state="expanded")

# CREDENZIALI
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# LINK IMMAGINI (Hostate temporaneamente)
LOGO_IMG = "https://i.ibb.co/X3ZzCFr/logo-square.png"
TRADECORE_HEADER = "https://i.ibb.co/C0b1Q54/tradecore-header.png"

# 2. DESIGN CSS (Blindato & Mobile Friendly)
st.markdown("""
<style>
    /* Sfondo Ultra Dark e Font */
    .stApp { background-color: #080808; color: #e1e4e8; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    /* Hide Streamlit Header/Footer */
    header, footer { visibility: hidden; }
    
    /* Metriche Premium */
    .stMetric { 
        background-color: #111111; border: 1px solid #1f1f1f; 
        border-radius: 12px; padding: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] { color: #ffffff; font-family: monospace; font-size: 1.6rem !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #888888; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 1px; }
    
    /* Calendario Mobile-First */
    .cal-day { 
        min-height: 55px; border-radius: 6px; padding: 4px; 
        display: flex; flex-direction: column; align-items: center; 
        justify-content: center; border: 1px solid #1f1f1f; font-size: 10px;
    }
    @media (max-width: 768px) {
        .cal-day { min-height: 45px; font-size: 9px; }
        [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
    }
    .pnl-pos { background-color: rgba(0,255,136,0.08); color: #00ff88; border: 1px solid #00ff88; }
    .pnl-neg { background-color: rgba(255,75,75,0.08); color: #ff4b4b; border: 1px solid #ff4b4b; }
    .pnl-neu { background-color: #111111; color: #555555; }
    
    /* Bottoni e Input */
    .stButton>button { 
        width: 100%; font-weight: bold; background-color: #ffffff; color: #000000; 
        border-radius: 6px; border: none; height: 3em;
        transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #cccccc; transform: translateY(-1px); }
    div[data-baseweb="input"] { background-color: #111111; border: 1px solid #1f1f1f; border-radius: 6px; }
    
    /* Home Page Splash */
    .home-header { text-align: center; padding: 40px 0; }
    .home-stats { background: #111111; padding: 20px; border-radius: 15px; border: 1px solid #1f1f1f; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# 3. FUNZIONI
def check_password():
    if "password_correct" not in st.session_state:
        # Splash screen di login ispirata al design
        st.markdown(f"<div class='home-header'><img src='{TRADECORE_HEADER}' width='250'></div>", unsafe_allow_html=True)
        pwd = st.text_input("Security Token", type="password")
        st.write("")
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
    
    # Sidebar Professional con Logo Dinamico
    st.sidebar.markdown(f"<div style='text-align:center; padding: 10px 0;'><img src='{LOGO_IMG}' width='80'></div>", unsafe_allow_html=True)
    menu = st.sidebar.radio("COMMAND CENTER", ["🏠 Home", "📊 Dashboard", "📈 Analytics", "📝 Log Trade", "🧠 Psychology", "⚙️ Settings"])

    if "acc_size" not in st.session_state:
        st.session_state.acc_size, st.session_state.acc_target, st.session_state.acc_max_dd = 50000.0, 5000.0, 2500.0

    current_pnl = df['pnl'].sum() if not df.empty else 0
    balance = st.session_state.acc_size + current_pnl

    # --- HOME (Nuova Schermata Splash) ---
    if menu == "🏠 Home":
        st.markdown(f"<div class='home-header'><img src='{TRADECORE_HEADER}' width='200'><p style='color:#888;'>v4.0 | Operativo</p></div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("STATUS", "ONLINE", delta="Secured")
        c2.metric("BAL.", f"${balance:,.0f}")
        c3.metric("TO TARGET", f"${st.session_state.acc_target - current_pnl:,.0f}")
        
        st.markdown("<div class='home-stats'>⚡ <b>Quick Action:</b> Vai su 'Log Trade' per registrare una nuova operazione o 'Dashboard' per il calendario.</div>", unsafe_allow_html=True)

    # --- DASHBOARD & CALENDARIO ---
    elif menu == "📊 Dashboard":
        st.header("📊 Performance Monitor")
        if not df.empty:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("BALANCE", f"${balance:,.2f}")
            c2.metric("P&L NET", f"${current_pnl:,.2f}", f"{(current_pnl/st.session_state.acc_size)*100:.1f}%")
            c3.metric("DIST. TARGET", f"${st.session_state.acc_target - current_pnl:,.2f}")
            c4.metric("DD LIMIT", f"${st.session_state.acc_size - st.session_state.acc_max_dd:,.2f}")

            prog = min(max(current_pnl / st.session_state.acc_target, 0.0), 1.0)
            st.progress(prog)

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
        else:
            st.info("Inizia a registrare trade per attivare il monitor.")

    # --- ANALYTICS ---
    elif menu == "📈 Analytics":
        st.header("📈 Deep Stats")
        if not df.empty:
            df['equity'] = df['pnl'].cumsum() + st.session_state.acc_size
            
            st.plotly_chart(px.line(df, x=df.index, y='equity', title="Account Value", color_discrete_sequence=['#ffffff']).update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)'), use_container_width=True)
            
            col1, col2 = st.columns(2)
            wr = (len(df[df['pnl'] > 0]) / len(df)) * 100
            col1.metric("Win Rate", f"{wr:.1f}%")
            col2.plotly_chart(px.bar(df, x='exit_date', y='pnl', color='pnl', color_continuous_scale=['#ff4b4b', '#00ff88'], title="Daily Performance").update_layout(template="plotly_dark"), use_container_width=True)

    # --- LOG TRADE ---
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
            
            score = st.select_slider("Mindset (1-5)", options=[1,2,3,4,5], value=5)
            note = st.text_area("Diary")
            
            if st.form_submit_button("EXECUTE"):
                m = 20 if "NASDAQ" in asset else 100000 if calc == "Forex" else 50
                res_pnl = (exit_p - entry) * size * m if side == "LONG" else (entry - exit_p) * size * m
                
                new_trade = {"asset":asset, "pnl":res_pnl, "size":size, "notes":note, "psychology_score":score, "exit_date":str(date.today())}
                supabase.table("trades").insert(new_trade).execute()
                st.success("Trade Secured.")

    # --- PSICOLOGIA (Blindata) ---
    elif menu == "🧠 Psychology":
        st.header("🧠 Mindset Analytics")
        if not df.empty and 'psychology_score' in df.columns:
            if len(df) > 2 and not df['psychology_score'].isnull().all():
                st.plotly_chart(px.box(df, x="psychology_score", y="pnl", title="Mindset vs P&L", color_discrete_sequence=['#ffffff']).update_layout(template="plotly_dark"), use_container_width=True)
            else:
                st.info("📈 Inserisci almeno 3 trade con score psicologico per attivare l'analisi box-plot.")
            st.divider()
            st.dataframe(df[['exit_date', 'asset', 'psychology_score', 'notes']].tail(20), use_container_width=True)
        else:
            st.info("Nessun dato psicologico disponibile.")

    # --- SETTINGS ---
    elif menu == "⚙️ Settings":
        st.header("⚙️ Configuration")
        st.session_state.acc_size = st.number_input("Starting Balance ($)", value=st.session_state.acc_size)
        st.session_state.acc_target = st.number_input("Profit Target ($)", value=st.session_state.acc_target)
        st.session_state.acc_max_dd = st.number_input("Max Drawdown ($)", value=st.session_state.acc_max_dd)
        if st.button("Save Settings"): st.success("Settings Updated.")

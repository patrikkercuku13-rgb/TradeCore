import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
import plotly.express as px
import calendar
import base64

# --- CONFIGURAZIONE SCHEDA BROWSER ---
st.set_page_config(page_title="TRADECORE", page_icon="🎯", layout="wide")

# --- CONNESSIONE DATABASE ---
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# --- CSS PERSONALIZZATO (DARK & GREEN) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #1f1f1f; }
    .stMetric { background: #111; border: 1px solid #222; border-radius: 12px; padding: 15px !important; }
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-family: monospace; }
    .cal-day { 
        min-height: 70px; border-radius: 8px; border: 1px solid #1f1f1f;
        display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 11px;
    }
    .win { background: rgba(0, 255, 136, 0.15); color: #00ff88; border: 1px solid #00ff88; }
    .loss { background: rgba(255, 75, 75, 0.15); color: #ff4b4b; border: 1px solid #ff4b4b; }
    .brand-title { font-size: 2.8rem; font-weight: 900; letter-spacing: 6px; color: #00ff88; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- FUNZIONE CARICAMENTO DATI (FORZATA) ---
def get_data_live():
    try:
        # Richiesta diretta senza cache
        res = supabase.table("trades").select("*").execute()
        df_db = pd.DataFrame(res.data)
        if not df_db.empty:
            df_db['exit_date'] = pd.to_datetime(df_db['exit_date']).dt.date
            df_db['pnl'] = pd.to_numeric(df_db['pnl'])
            df_db['psychology_score'] = pd.to_numeric(df_db['psychology_score'])
            return df_db.sort_values('exit_date', ascending=False)
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- LOGIN ---
if "logged_in" not in st.session_state:
    st.markdown("<div class='brand-title'>TRADECORE</div>", unsafe_allow_html=True)
    pw = st.text_input("Security Token", type="password")
    if st.button("AUTHORIZE"):
        if pw == "2026":
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# --- NAVIGAZIONE ---
df = get_data_live()
st.sidebar.markdown("<div style='color:#00ff88; font-weight:900; font-size:20px; text-align:center;'>TRADECORE</div>", unsafe_allow_html=True)
nav = st.sidebar.radio("NAV", ["🏠 HOME", "📊 DASHBOARD", "📈 ANALYTICS", "📝 LOG TRADE", "🧠 PSYCHOLOGY", "⚙️ SETTINGS"])

if "starting_bal" not in st.session_state:
    st.session_state.starting_bal = 50000.0

# ==========================================
# PAGINE
# ==========================================

if nav == "🏠 HOME":
    st.markdown("<div class='brand-title'>TRADECORE</div>", unsafe_allow_html=True)
    total_pnl = df['pnl'].sum() if not df.empty else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("ACCOUNT", f"${st.session_state.starting_bal + total_pnl:,.2f}")
    c2.metric("TOTAL P&L", f"${total_pnl:,.2f}", f"{(total_pnl/st.session_state.starting_bal)*100:.2f}%")
    c3.metric("EXECUTIONS", len(df))
    
    st.subheader("Last Entries")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data found in Supabase. Go to 'LOG TRADE' to start.")

elif nav == "📊 DASHBOARD":
    st.header("📅 Trading Calendar")
    if not df.empty:
        daily_res = df.groupby('exit_date')['pnl'].sum()
        cal = calendar.monthcalendar(date.today().year, date.today().month)
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    curr_d = date(date.today().year, date.today().month, day)
                    pnl_val = daily_res.get(curr_d, 0)
                    status = "win" if pnl_val > 0 else "loss" if pnl_val < 0 else ""
                    cols[i].markdown(f"<div class='cal-day {status}'><b>{day}</b><br>${pnl_val:.0f}</div>", unsafe_allow_html=True)
    else:
        st.warning("Log trades to see the calendar.")

elif nav == "📈 ANALYTICS":
    st.header("📈 Performance Stats")
    if not df.empty:
        df_sorted = df.sort_values('exit_date')
        df_sorted['equity'] = df_sorted['pnl'].cumsum() + st.session_state.starting_bal
        
        st.plotly_chart(px.line(df_sorted, x='exit_date', y='equity', title="Equity Curve").update_layout(template="plotly_dark"), use_container_width=True)
        
        c1, c2 = st.columns(2)
        wr = (len(df[df['pnl'] > 0]) / len(df)) * 100
        c1.metric("Win Rate", f"{wr:.1f}%")
        c2.metric("Avg Trade", f"${df['pnl'].mean():,.2f}")
    else:
        st.error("Not enough data.")

elif nav == "📝 LOG TRADE":
    st.header("📝 New Execution")
    with st.form("add_trade", clear_on_submit=True):
        c1, c2 = st.columns(2)
        asset = c1.selectbox("Asset", ["NASDAQ", "EURUSD", "GOLD", "DAX", "BTC"])
        side = c1.radio("Side", ["LONG", "SHORT"], horizontal=True)
        size = c2.number_input("Size", value=1.0, step=0.1)
        entry = c1.number_input("Entry Price", format="%.5f")
        exit_p = c2.number_input("Exit Price", format="%.5f")
        engine = st.selectbox("Mode", ["Futures", "Forex"])
        score = st.select_slider("Mindset", options=[1,2,3,4,5], value=5)
        note = st.text_area("Journal")
        
        if st.form_submit_button("SAVE TO CLOUD"):
            mult = 20 if "NASDAQ" in asset else 100000 if engine == "Forex" else 50
            final_pnl = (exit_p - entry) * size * mult if side == "LONG" else (entry - exit_p) * size * mult
            
            supabase.table("trades").insert({
                "asset": asset, "pnl": final_pnl, "size": size, 
                "notes": note, "psychology_score": score, 
                "exit_date": str(date.today())
            }).execute()
            st.success("SUCCESS! Trade saved.")
            st.rerun()

elif nav == "🧠 PSYCHOLOGY":
    st.header("🧠 Psychology Analysis")
    if not df.empty:
        st.plotly_chart(px.box(df, x="psychology_score", y="pnl").update_layout(template="plotly_dark"))
    else:
        st.info("Log more trades.")

elif nav == "⚙️ SETTINGS":
    st.header("⚙️ Settings")
    st.session_state.starting_bal = st.number_input("Initial Balance", value=st.session_state.starting_bal)
    if st.button("FORZA REFRESH DATI"):
        st.rerun()

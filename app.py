import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
import plotly.graph_objects as go
import plotly.express as px
import calendar
import base64

# ==========================================
# 1. CONFIGURAZIONE & BRANDING
# ==========================================
st.set_page_config(
    page_title="TRADECORE TERMINAL",
    page_icon="🎯", 
    layout="wide"
)

# CREDENZIALI SUPABASE
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# ==========================================
# 2. DESIGN CUSTOM (DARK MODE & MOBILE)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #1f1f1f; }
    .stMetric { background: #111; border: 1px solid #222; border-radius: 12px; padding: 15px !important; }
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-family: 'Courier New', monospace; }
    
    /* Calendario */
    .cal-day { 
        min-height: 60px; border-radius: 8px; border: 1px solid #1f1f1f;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .win { background: rgba(0, 255, 136, 0.1); color: #00ff88; border: 1px solid #00ff88; }
    .loss { background: rgba(255, 75, 75, 0.1); color: #ff4b4b; border: 1px solid #ff4b4b; }
    
    /* Logo Header Custom */
    .header-box { text-align: center; padding: 20px; border-bottom: 1px solid #1f1f1f; margin-bottom: 20px; }
    .brand-text { font-size: 2.5rem; font-weight: 900; letter-spacing: 5px; color: #00ff88; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. MOTORE DATI (RECUPERO TOTALE)
# ==========================================
def load_all_trades_no_cache():
    try:
        # Recupero forzato senza cache per evitare di "perdere" trade
        res = supabase.table("trades").select("*").execute()
        df_res = pd.DataFrame(res.data)
        if not df_res.empty:
            df_res['exit_date'] = pd.to_datetime(df_res['exit_date']).dt.date
            df_res['pnl'] = pd.to_numeric(df_res['pnl'])
            df_res['psychology_score'] = pd.to_numeric(df_res['psychology_score'])
            return df_res.sort_values('exit_date', ascending=False)
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore caricamento dati: {e}")
        return pd.DataFrame()

# ==========================================
# 4. ACCESSO
# ==========================================
if "auth_status" not in st.session_state:
    st.markdown("<div class='header-box'><div class='brand-text'>TRADECORE</div></div>", unsafe_allow_html=True)
    psw = st.text_input("Security Token", type="password")
    if st.button("UNLOCK"):
        if psw == "2026":
            st.session_state.auth_status = True
            st.rerun()
        else:
            st.error("Token Errato")
    st.stop()

# ==========================================
# 5. NAVIGAZIONE
# ==========================================
df = load_all_trades_no_cache()
st.sidebar.markdown("<div class='brand-text' style='font-size:1.2rem; text-align:center;'>TRADECORE</div>", unsafe_allow_html=True)
nav = st.sidebar.radio("NAVIGAZIONE", ["🏠 Overview", "📈 Analytics", "📝 Log Trade", "📊 Calendar", "🧠 Psychology", "⚙️ Settings"])

if "base_bal" not in st.session_state:
    st.session_state.base_bal = 50000.0

# ==========================================
# 6. PAGINE
# ==========================================

# --- OVERVIEW ---
if nav == "🏠 Overview":
    st.markdown("<div class='header-box'><div class='brand-text'>TRADECORE</div></div>", unsafe_allow_html=True)
    
    tpnl = df['pnl'].sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("BALANCE", f"${st.session_state.base_bal + tpnl:,.2f}")
    c2.metric("TOTAL PNL", f"${tpnl:,.2f}", f"{(tpnl/st.session_state.base_bal)*100:.2f}%")
    c3.metric("EXECUTIONS", len(df))
    
    st.subheader("Journal Storico")
    if not df.empty:
        # Tabella interattiva e selezionabile
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nessun trade nel database. Vai a 'Log Trade' per inserire i dati.")

# --- ANALYTICS ---
elif nav == "📈 Analytics":
    st.header("📈 Analisi Performance")
    if not df.empty:
        # Metriche
        wins = len(df[df['pnl'] > 0])
        wr = (wins / len(df)) * 100
        pf = abs(df[df['pnl']>0]['pnl'].sum() / df[df['pnl']<0]['pnl'].sum()) if len(df[df['pnl']<0]) > 0 else 1.0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Win Rate", f"{wr:.1f}%")
        c2.metric("Profit Factor", f"{pf:.2f}")
        c3.metric("Max Gain", f"${df['pnl'].max():,.2f}")
        
        # Equity Curve
        df_ev = df.sort_values('exit_date')
        df_ev['equity'] = df_ev['pnl'].cumsum() + st.session_state.base_bal
        st.plotly_chart(px.line(df_ev, x='exit_date', y='equity', title="Equity Curve").update_layout(template="plotly_dark"), use_container_width=True)
        
        # Volume per Asset
        st.plotly_chart(px.pie(df, names='asset', values='size', title="Esposizione per Asset").update_layout(template="plotly_dark"), use_container_width=True)
    else:
        st.warning("Esegui dei trade per sbloccare le statistiche.")

# --- LOG TRADE ---
elif nav == "📝 Log Trade":
    st.header("📝 Nuova Operazione")
    with st.form("entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        asset = c1.selectbox("Asset", ["NASDAQ", "EURUSD", "GOLD", "DAX", "BTC"])
        side = c1.radio("Side", ["LONG", "SHORT"], horizontal=True)
        engine = c1.selectbox("Market", ["Futures", "Forex"])
        
        size = c2.number_input("Size", min_value=0.01, step=0.01, value=1.0)
        entry = c2.number_input("Entry Price", format="%.5f")
        exit_p = c2.number_input("Exit Price", format="%.5f")
        
        score = st.select_slider("Stato Mentale", options=[1,2,3,4,5], value=5)
        note = st.text_area("Note e Journaling")
        
        if st.form_submit_button("REGISTRA TRADE"):
            # Calcolo PnL
            m = 20 if "NASDAQ" in asset else 100000 if engine == "Forex" else 50
            res_pnl = (exit_p - entry) * size * m if side == "LONG" else (entry - exit_p) * size * m
            
            # Inserimento DB
            supabase.table("trades").insert({
                "asset": asset, "pnl": res_pnl, "size": size, 
                "notes": note, "psychology_score": score, 
                "exit_date": str(date.today())
            }).execute()
            
            st.success("Trade salvato correttamente!")
            st.balloons()

# --- CALENDAR ---
elif nav == "📊 Calendar":
    st.header("📊 Calendario Profitti")
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
    st.header("🧠 Psicologia e Mindset")
    if not df.empty:
        st.plotly_chart(px.box(df, x="psychology_score", y="pnl", title="Mindset vs PnL").update_layout(template="plotly_dark"), use_container_width=True)
        st.write("### Note Recenti")
        st.table(df[['exit_date', 'notes', 'psychology_score']].head(10))

# --- SETTINGS ---
elif nav == "⚙️ Settings":
    st.header("⚙️ Impostazioni")
    st.session_state.base_bal = st.number_input("Capitale Iniziale ($)", value=st.session_state.base_bal)
    if st.button("Svuota Memoria App (Fix Trade)"):
        st.cache_data.clear()
        st.rerun()

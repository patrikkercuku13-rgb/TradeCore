import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
import plotly.graph_objects as go
import plotly.express as px
import calendar

# ==========================================
# 1. CONFIGURAZIONE & BRANDING
# ==========================================
# Il logo apparirà nella scheda in alto del browser
st.set_page_config(
    page_title="TRADECORE TERMINAL",
    page_icon="https://i.ibb.co/X3ZzCFr/logo-square.png",
    layout="wide"
)

# CREDENZIALI SUPABASE
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# ==========================================
# 2. DESIGN & STILE (CSS)
# ==========================================
st.markdown("""
<style>
    .stApp { background-color: #080808; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0c0c0c; border-right: 1px solid #1f1f1f; }
    .stMetric { background: #111; border: 1px solid #222; border-radius: 12px; padding: 15px !important; }
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-family: 'Courier New', monospace; }
    
    /* Calendario Professional */
    .cal-day { 
        min-height: 70px; border-radius: 8px; padding: 10px; 
        display: flex; flex-direction: column; align-items: center; 
        justify-content: center; border: 1px solid #1f1f1f; font-size: 13px;
    }
    .win { background: rgba(0, 255, 136, 0.1); color: #00ff88; border: 1px solid #00ff88; }
    .loss { background: rgba(255, 75, 75, 0.1); color: #ff4b4b; border: 1px solid #ff4b4b; }
    .neutral { background: #111; color: #555; }
    
    /* Tabella */
    .stDataFrame { border: 1px solid #222; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. MOTORE DATI
# ==========================================
@st.cache_data(ttl=2)
def fetch_data():
    try:
        res = supabase.table("trades").select("*").execute()
        df_raw = pd.DataFrame(res.data)
        if not df_raw.empty:
            df_raw['exit_date'] = pd.to_datetime(df_raw['exit_date']).dt.date
            df_raw['pnl'] = pd.to_numeric(df_raw['pnl'])
            df_raw['psychology_score'] = pd.to_numeric(df_raw['psychology_score'])
            return df_raw.sort_values('exit_date')
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore connessione: {e}")
        return pd.DataFrame()

# ==========================================
# 4. LOGICA ACCESSO
# ==========================================
if "authenticated" not in st.session_state:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.image("https://i.ibb.co/C0b1Q54/tradecore-header.png", width=400)
    token = st.text_input("Security Token", type="password")
    if st.button("UNLOCK SYSTEM"):
        if token == "2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Token non valido.")
    st.stop()

# ==========================================
# 5. NAVIGAZIONE SIDEBAR
# ==========================================
df = fetch_data()
st.sidebar.image("https://i.ibb.co/X3ZzCFr/logo-square.png", width=120)
st.sidebar.markdown("---")
nav = st.sidebar.radio("COMMAND CENTER", ["🏠 Overview", "📈 Analytics", "📝 Log Trade", "📊 Dashboard", "🧠 Psychology", "⚙️ Settings"])

if "balance" not in st.session_state:
    st.session_state.balance = 50000.0
    st.session_state.target = 5000.0

# ==========================================
# 6. PAGINE
# ==========================================

# --- OVERVIEW ---
if nav == "🏠 Overview":
    st.image("https://i.ibb.co/C0b1Q54/tradecore-header.png", use_container_width=True)
    
    net_pnl = df['pnl'].sum() if not df.empty else 0
    current_bal = st.session_state.balance + net_pnl
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CURRENT BALANCE", f"${current_bal:,.2f}")
    c2.metric("NET PNL", f"${net_pnl:,.2f}", f"{(net_pnl/st.session_state.balance)*100:.2f}%")
    c3.metric("TRADES", len(df))
    c4.metric("TARGET LEFT", f"${st.session_state.target - net_pnl:,.2f}")
    
    st.markdown("### Recenti")
    if not df.empty:
        st.dataframe(df.sort_values('exit_date', ascending=False), use_container_width=True)
    else:
        st.info("Nessun dato presente. Vai su 'Log Trade'.")

# --- ANALYTICS (TORNARE AL TOP) ---
elif nav == "📈 Analytics":
    st.header("📈 Deep Performance Analytics")
    if not df.empty:
        # Calcoli Statistici
        wins = df[df['pnl'] > 0]
        losses = df[df['pnl'] <= 0]
        win_rate = (len(wins) / len(df)) * 100
        avg_win = wins['pnl'].mean() if not wins.empty else 0
        avg_loss = losses['pnl'].mean() if not losses.empty else 0
        pf = abs(wins['pnl'].sum() / losses['pnl'].sum()) if not losses.empty and losses['pnl'].sum() != 0 else 0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Win Rate", f"{win_rate:.1f}%")
        c2.metric("Profit Factor", f"{pf:.2f}")
        c3.metric("Avg Win", f"${avg_win:,.2f}")
        c4.metric("Avg Loss", f"${avg_loss:,.2f}")
        
        st.divider()
        
        # Grafico Equity
        df['equity'] = df['pnl'].cumsum() + st.session_state.balance
        fig_equity = px.area(df, x='exit_date', y='equity', title="Equity Curve Globale",
                            color_discrete_sequence=['#00ff88'])
        fig_equity.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_equity, use_container_width=True)
        
        # Asset Performance
        asset_pnl = df.groupby('asset')['pnl'].sum().reset_index()
        fig_asset = px.bar(asset_pnl, x='asset', y='pnl', title="Profitto per Asset",
                          color='pnl', color_continuous_scale='RdYlGn')
        fig_asset.update_layout(template="plotly_dark")
        st.plotly_chart(fig_asset, use_container_width=True)
    else:
        st.warning("Dati insufficienti per generare le analisi.")

# --- LOG TRADE ---
elif nav == "📝 Log Trade":
    st.header("📝 Registra Esecuzione")
    with st.form("trade_entry"):
        col1, col2 = st.columns(2)
        asset = col1.selectbox("Asset", ["NASDAQ", "EURUSD", "GOLD", "S&P500", "DAX", "BTC"])
        engine = col1.selectbox("Calcolo", ["Futures", "Forex"])
        side = col1.radio("Direzione", ["LONG", "SHORT"], horizontal=True)
        
        size = col2.number_input("Size (Lotti/Contratti)", min_value=0.01, step=0.01, value=1.0)
        entry = col2.number_input("Prezzo Entrata", format="%.5f")
        exit_p = col2.number_input("Prezzo Uscita", format="%.5f")
        
        score = st.select_slider("Stato Mentale", options=[1,2,3,4,5], value=5)
        note = st.text_area("Journaling / Note")
        
        if st.form_submit_button("SALVA TRADE"):
            # Calcolo PNL
            mult = 20 if "NASDAQ" in asset else 100000 if engine == "Forex" else 50
            res_pnl = (exit_p - entry) * size * mult if side == "LONG" else (entry - exit_p) * size * mult
            
            supabase.table("trades").insert({
                "asset": asset, "pnl": res_pnl, "size": size, 
                "notes": note, "psychology_score": score, 
                "exit_date": str(date.today())
            }).execute()
            
            st.cache_data.clear()
            st.success(f"Trade Registrato! PNL: ${res_pnl:.2f}")
            st.balloons()

# --- DASHBOARD (CALENDARIO) ---
elif nav == "📊 Dashboard":
    st.header("📅 Calendario Operativo")
    if not df.empty:
        daily_pnl = df.groupby('exit_date')['pnl'].sum()
        cal = calendar.monthcalendar(date.today().year, date.today().month)
        
        # Header Giorni
        days_header = st.columns(7)
        for i, d in enumerate(["LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"]):
            days_header[i].markdown(f"<p style='text-align:center; color:#888;'>{d}</p>", unsafe_allow_html=True)
            
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    curr_date = date(date.today().year, date.today().month, day)
                    val = daily_pnl.get(curr_date, 0)
                    bg_class = "win" if val > 0 else "loss" if val < 0 else "neutral"
                    cols[i].markdown(f"<div class='cal-day {bg_class}'><b>{day}</b><br>${val:.0f}</div>", unsafe_allow_html=True)

# --- PSICOLOGIA ---
elif nav == "🧠 Psychology":
    st.header("🧠 Analisi Comportamentale")
    if not df.empty:
        st.plotly_chart(px.box(df, x="psychology_score", y="pnl", title="Mindset vs Performance",
                             color_discrete_sequence=['#00ff88']).update_layout(template="plotly_dark"))
        st.markdown("### Ultime Note Diario")
        st.table(df[['exit_date', 'asset', 'notes', 'psychology_score']].tail(10))

# --- SETTINGS ---
elif nav == "⚙️ Settings":
    st.header("⚙️ Parametri Account")
    st.session_state.balance = st.number_input("Capitale Prop Firm ($)", value=st.session_state.balance)
    st.session_state.target = st.number_input("Obiettivo Profitto ($)", value=st.session_state.target)
    
    if st.button("RESET DATABASE CACHE"):
        st.cache_data.clear()
        st.rerun()

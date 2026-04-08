import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client, Client
import plotly.express as px
import calendar

# 1. SETUP CORE
st.set_page_config(page_title="TRADECORE TERMINAL", page_icon="🎯", layout="wide")

# CONNESSIONE SUPABASE
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# 2. DESIGN CSS (Ispirato ai tuoi screenshot)
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #ffffff; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #1f1f1f; }
    
    /* Metriche stile Terminale */
    .stMetric { background: #0f0f0f; border: 1px solid #1f1f1f; border-radius: 8px; padding: 20px !important; }
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 1.8rem !important; font-weight: 700; }
    
    /* Calendario */
    .cal-day { 
        min-height: 80px; border: 1px solid #1f1f1f; border-radius: 6px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .win { background: rgba(0, 255, 136, 0.1); border: 1px solid #00ff88; color: #00ff88; }
    .loss { background: rgba(255, 75, 75, 0.1); border: 1px solid #ff4b4b; color: #ff4b4b; }
    
    /* Branding */
    .brand-header { font-size: 3.5rem; font-weight: 900; color: #00ff88; text-align: center; letter-spacing: 10px; padding: 40px 0; text-shadow: 0 0 20px rgba(0,255,136,0.3); }
</style>
""", unsafe_allow_html=True)

# 3. MOTORE DATI (Con Diagnosi)
def fetch_trades():
    try:
        res = supabase.table("trades").select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            # Convertiamo i nomi colonne in minuscolo per evitare errori di battitura nel DB
            df.columns = [c.lower() for c in df.columns]
            
            # Fix date e numeri
            date_col = 'exit_date' if 'exit_date' in df.columns else df.columns[0]
            df[date_col] = pd.to_datetime(df[date_col]).dt.date
            if 'pnl' in df.columns:
                df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
            return df, None
        return pd.DataFrame(), "Database collegato ma vuoto."
    except Exception as e:
        return pd.DataFrame(), f"Errore di connessione: {str(e)}"

# 4. LOGIN SISTEMA
if "authorized" not in st.session_state:
    st.markdown("<div class='brand-header'>TRADECORE</div>", unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            token = st.text_input("SECURITY TOKEN", type="password")
            if st.button("AUTHORIZE ACCESS"):
                if token == "2026":
                    st.session_state.authorized = True
                    st.rerun()
    st.stop()

# 5. CARICAMENTO EFFETTIVO
df, error_msg = fetch_trades()

# 6. SIDEBAR
st.sidebar.markdown("<h1 style='color:#00ff88; text-align:center;'>TRADECORE</h1>", unsafe_allow_html=True)
menu = st.sidebar.radio("SISTEMA", ["🏠 OVERVIEW", "📈 ANALYTICS", "📊 CALENDARIO", "📝 LOG TRADE", "⚙️ SETTINGS"])

if "bal_iniziale" not in st.session_state:
    st.session_state.bal_iniziale = 50000.0

# ==========================================
# PAGINE
# ==========================================

if menu == "🏠 OVERVIEW":
    st.markdown("<div class='brand-header'>TRADECORE</div>", unsafe_allow_html=True)
    
    if error_msg: st.warning(error_msg)
    
    pnl_totale = df['pnl'].sum() if not df.empty and 'pnl' in df.columns else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("ACCOUNT BALANCE", f"${st.session_state.bal_iniziale + pnl_totale:,.2f}")
    col2.metric("NET PROFIT", f"${pnl_totale:,.2f}")
    col3.metric("TOTAL TRADES", len(df))
    
    st.divider()
    st.subheader("Ultime Esecuzioni")
    if not df.empty:
        st.dataframe(df.head(10), use_container_width=True)

elif menu == "📈 ANALYTICS":
    st.header("📈 Performance Analytics")
    if not df.empty and 'pnl' in df.columns:
        # Equity Curve
        df_sorted = df.sort_values(df.columns[0]) # ordina per data
        df_sorted['equity'] = df_sorted['pnl'].cumsum() + st.session_state.bal_iniziale
        
        st.plotly_chart(px.line(df_sorted, x=df_sorted.columns[0], y='equity', 
                               title="Equity Curve").update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)'), 
                        use_container_width=True)
        
        # Win Rate
        wins = len(df[df['pnl'] > 0])
        wr = (wins / len(df)) * 100
        st.metric("Win Rate", f"{wr:.1f}%")
    else:
        st.info("Dati insufficienti per i grafici.")

elif menu == "📊 CALENDARIO":
    st.header("📅 Calendario Profitti")
    if not df.empty:
        # Troviamo la colonna data corretta
        d_col = 'exit_date' if 'exit_date' in df.columns else df.columns[0]
        daily_pnl = df.groupby(d_col)['pnl'].sum()
        
        cal = calendar.monthcalendar(date.today().year, date.today().month)
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    curr_date = date(date.today().year, date.today().month, day)
                    val = daily_pnl.get(curr_date, 0)
                    cl = "win" if val > 0 else "loss" if val < 0 else ""
                    cols[i].markdown(f"<div class='cal-day {cl}'><b>{day}</b><br>${val:.0f}</div>", unsafe_allow_html=True)

elif menu == "📝 LOG TRADE":
    st.header("📝 Nuova Registrazione")
    with st.form("trade_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        asset = c1.selectbox("Market", ["NASDAQ", "EURUSD", "GOLD", "DAX", "BTC"])
        side = c1.radio("Side", ["LONG", "SHORT"], horizontal=True)
        size = c2.number_input("Size", value=1.0)
        entry = c1.number_input("Entry Price", format="%.5f")
        exit_p = c2.number_input("Exit Price", format="%.5f")
        tipo = st.selectbox("Engine", ["Futures", "Forex"])
        note = st.text_area("Journal")
        
        if st.form_submit_button("REGISTRA"):
            mult = 20 if "NASDAQ" in asset else 100000 if tipo == "Forex" else 50
            pnl_final = (exit_p - entry) * size * mult if side == "LONG" else (entry - exit_p) * size * mult
            
            supabase.table("trades").insert({
                "asset": asset, "pnl": pnl_final, "size": size, 
                "notes": note, "exit_date": str(date.today()), "psychology_score": 5
            }).execute()
            st.success(f"Trade registrato! PNL: ${pnl_final:.2f}")
            st.rerun()

elif menu == "⚙️ SETTINGS":
    st.header("⚙️ Settings")
    st.session_state.bal_iniziale = st.number_input("Capitale Iniziale", value=st.session_state.bal_iniziale)
    if st.button("PULISCI CACHE DATI"):
        st.rerun()

import streamlit as st
import pandas as pd
from datetime import datetime, date
from supabase import create_client, Client
import plotly.express as px
import calendar

# 1. SETUP & CREDENTIALS
st.set_page_config(page_title="TradeCore", layout="wide")

URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# 2. CSS MOBILE-OPTIMIZED (Niente immagini esterne che spariscono)
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #ffffff; }
    
    /* Logo Digitale in CSS */
    .brand-logo { 
        font-size: 2.2rem; font-weight: 900; letter-spacing: -1px;
        background: linear-gradient(90deg, #00ff88, #00d4ff);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding: 20px 0;
    }

    /* Card per i dati su mobile */
    .trade-card {
        background: #111; border-radius: 10px; padding: 15px;
        margin-bottom: 10px; border-left: 4px solid #00ff88;
    }

    /* Pulsanti enormi per dita */
    .stButton>button { 
        height: 3.5rem; border-radius: 10px; font-size: 1.1rem;
        background: #ffffff; color: #000; font-weight: bold; border: none;
    }

    /* Calendario che non si rompe */
    .cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 2px; }
    .cal-day { 
        min-height: 45px; font-size: 10px; border-radius: 4px;
        display: flex; align-items: center; justify-content: center;
        background: #111; border: 1px solid #222;
    }
    .win { border-color: #00ff88; color: #00ff88; background: rgba(0,255,136,0.05); }
    .loss { border-color: #ff4b4b; color: #ff4b4b; background: rgba(255,75,75,0.05); }
</style>
""", unsafe_allow_html=True)

# 3. LOGICA LOGIN
if "auth" not in st.session_state:
    st.markdown("<div class='brand-logo'>TRADECORE</div>", unsafe_allow_html=True)
    pwd = st.text_input("Security Token", type="password")
    if st.button("UNLOCK TERMINAL"):
        if pwd == "2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Access Denied")
    st.stop()

# 4. CARICAMENTO DATI
@st.cache_data(ttl=5)
def get_data():
    try:
        res = supabase.table("trades").select("*").order("exit_date").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

df = get_data()
if not df.empty:
    df['exit_date'] = pd.to_datetime(df['exit_date']).dt.date
    df['pnl'] = df['pnl'].astype(float)

# 5. MENU MOBILE
menu = st.sidebar.selectbox("VAI A:", ["🏠 Home", "📝 Log Trade", "📊 Dashboard", "⚙️ Settings"])

if "acc_size" not in st.session_state:
    st.session_state.acc_size = 50000.0

# --- HOME ---
if menu == "🏠 Home":
    st.markdown("<div class='brand-logo'>TRADECORE</div>", unsafe_allow_html=True)
    total_pnl = df['pnl'].sum() if not df.empty else 0
    
    st.metric("CURRENT BALANCE", f"${st.session_state.acc_size + total_pnl:,.2f}")
    
    st.subheader("Ultime Esecuzioni")
    if not df.empty:
        for _, row in df.tail(3).iterrows():
            color = "#00ff88" if row['pnl'] > 0 else "#ff4b4b"
            st.markdown(f"""
            <div class='trade-card' style='border-color:{color}'>
                <b>{row['asset']}</b> | {row['exit_date']}<br>
                <span style='color:{color}'>PNL: ${row['pnl']:.2f}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nessun trade registrato.")

# --- LOG TRADE ---
elif menu == "📝 Log Trade":
    st.subheader("Registra Operazione")
    with st.form("mobile_form"):
        asset = st.selectbox("Market", ["NASDAQ", "EURUSD", "GOLD", "DAX"])
        side = st.radio("Direzione", ["LONG", "SHORT"], horizontal=True)
        entry = st.number_input("Entry", format="%.5f")
        exit_p = st.number_input("Exit", format="%.5f")
        size = st.number_input("Size", value=1.0)
        calc = st.selectbox("Strumento", ["Futures", "Forex"])
        
        if st.form_submit_button("SALVA TRADE"):
            m = 20 if "NASDAQ" in asset else 100000 if calc == "Forex" else 50
            pnl = (exit_p - entry) * size * m if side == "LONG" else (entry - exit_p) * size * m
            supabase.table("trades").insert({
                "asset": asset, "pnl": pnl, "size": size, 
                "exit_date": str(date.today()), "psychology_score": 5
            }).execute()
            st.success("Salvato! Torna alla Home.")

# --- DASHBOARD ---
elif menu == "📊 Dashboard":
    st.subheader("Performance Mensile")
    if not df.empty:
        cal = calendar.monthcalendar(date.today().year, date.today().month)
        daily = df.groupby('exit_date')['pnl'].sum()
        
        # Calendario compatto per mobile
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    curr = date(date.today().year, date.today().month, day)
                    val = daily.get(curr, 0)
                    style = "win" if val > 0 else "loss" if val < 0 else ""
                    cols[i].markdown(f"<div class='cal-day {style}'>{day}</div>", unsafe_allow_html=True)
    
    st.divider()
    if not df.empty:
        fig = px.line(df, x=df.index, y=df['pnl'].cumsum(), title="Equity Curve")
        fig.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

# --- SETTINGS ---
elif menu == "⚙️ Settings":
    st.session_state.acc_size = st.number_input("Balance Iniziale", value=st.session_state.acc_size)
    if st.button("RESET CACHE"):
        st.cache_data.clear()
        st.rerun()
     

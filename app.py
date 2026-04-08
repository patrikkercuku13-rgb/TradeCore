import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, date, timedelta
import calendar
import time

# ==========================================
# 1. SETUP TERMINALE & DESIGN
# ==========================================
st.set_page_config(
    page_title="TRADECORE V16.1 | STABLE",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #050708; color: #e0e0e0; }
    div[data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #1f2328; }
    .stMetric { background: #0d1117; border: 1px solid #30363d; padding: 15px; border-radius: 10px; }
    .cal-day {
        width: 55px; height: 55px; border-radius: 50%;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: bold; margin: 5px; font-size: 0.9em;
    }
    .pnl-pos { background: linear-gradient(135deg, #238636, #2ea043); color: white; border: 2px solid #3fb950; }
    .pnl-neg { background: linear-gradient(135deg, #da3633, #f85149); color: white; border: 2px solid #ff7b72; }
    .pnl-neu { background: #161b22; color: #8b949e; border: 1px solid #30363d; }
    .pnl-val { font-size: 0.6em; font-weight: normal; margin-top: 2px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONNESSIONE DATABASE
# ==========================================
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"

@st.cache_resource
def get_client():
    return create_client(URL, KEY)

db = get_client()

def load_data():
    try:
        res = db.table("trades").select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date'], errors='coerce')
            df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# ==========================================
# 3. BARRA LATERALE
# ==========================================
with st.sidebar:
    st.title("🚀 TRADECORE V16.1")
    page = st.radio("NAVIGAZIONE", ["📊 DASHBOARD", "📅 CALENDARIO", "📝 LOG ESECUZIONE", "🗄️ ARCHIVIO DATI", "💰 RISK CALC"])
    st.divider()
    if st.button("RE-SYNC DATA"):
        st.cache_resource.clear()
        st.rerun()

df_main = load_data()

# ==========================================
# 4. LOG ESECUZIONE
# ==========================================
if page == "📝 LOG ESECUZIONE":
    st.title("Professional Execution Log")
    with st.form("ultimate_form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            asset = st.selectbox("Asset", ["MNQ", "NQ", "MES", "ES", "MYM", "M2K", "BTCUSD", "GOLD", "EURUSD"])
            direction = st.radio("Side", ["Long", "Short"], horizontal=True)
        with col2:
            entry = st.number_input("Entry Price", format="%.2f", step=0.25, min_value=0.0, max_value=10000000.0)
            exit_p = st.number_input("Exit Price", format="%.2f", step=0.25, min_value=0.0, max_value=10000000.0)
        with col3:
            contracts = st.number_input("Contracts", value=1.0, min_value=0.01, step=0.01)
            multiplier = st.number_input("Point Value ($)", value=2.0)
        with col4:
            dt = st.date_input("Date", date.today())
            session = st.selectbox("Session", ["Asia", "London Open", "NY Morning", "NY Afternoon", "After Hours"])

        st.divider()
        c_tech, c_psy = st.columns(2)
        with c_tech:
            setup = st.selectbox("Setup Type", ["FVG Inversion", "Liquidity Sweep", "MSS / Shift", "Silver Bullet", "Unicorn", "Turtle Soup", "Order Block", "Breaker"])
            tf = st.selectbox("Timeframe", ["15s", "1m", "5m", "15m", "1h", "4h", "Daily"])
        with c_psy:
            emo = st.selectbox("Dominant Emotion", ["Calm/Flow", "FOMO", "Greed", "Fear", "Revenge", "Patience"])
            disc = st.radio("Discipline", ["Perfect", "Minor Rule Break", "Full Tilt"], horizontal=True)
        notes = st.text_area("Trade Journal")

        if st.form_submit_button("LOCK TRADE INTO VAULT"):
            diff = (exit_p - entry) if direction == "Long" else (entry - exit_p)
            pnl_calc = round(float(diff * contracts * multiplier), 2)
            payload = {
                "asset": asset, "direction": direction, "entry_price": float(entry),
                "exit_price": float(exit_p), "pnl": pnl_calc, "setup": setup,
                "session": session, "exit_date": str(dt), "notes": notes,
                "timeframe": tf, "contracts": float(contracts), "emotion": emo,
                "psychology": "Flow", "discipline": disc
            }
            db.table("trades").insert(payload).execute()
            st.balloons()
            st.success(f"SUCCESS! P&L: ${pnl_calc:,.2f}")
            time.sleep(1)
            st.rerun()

# ==========================================
# 5. DASHBOARD
# ==========================================
elif page == "📊 DASHBOARD":
    st.title("Market Analytics")
    if not df_main.empty:
        c1, c2, c3, c4 = st.columns(4)
        net = df_main['pnl'].sum()
        c1.metric("NET P&L", f"${net:,.2f}")
        c2.metric("TOTAL TRADES", len(df_main))
        wr = (len(df_main[df_main['pnl'] > 0]) / len(df_main)) * 100
        c3.metric("WIN RATE", f"{wr:.1f}%")
        avg = df_main['pnl'].mean()
        c4.metric("AVG TRADE", f"${avg:,.2f}")
        df_sorted = df_main.sort_values('exit_date')
        df_sorted['equity'] = df_sorted['pnl'].cumsum()
        st.line_chart(df_sorted.set_index('exit_date')['equity'])
    else:
        st.info("Nessun trade registrato.")

# ==========================================
# 6. CALENDARIO
# ==========================================
elif page == "📅 CALENDARIO":
    st.title("Daily Performance")
    if not df_main.empty:
        df_main['d_only'] = df_main['exit_date'].dt.date
        daily = df_main.groupby('d_only')['pnl'].sum().to_dict()
        m_idx = st.selectbox("Mese", range(1, 13), index=datetime.now().month-1)
        cal = calendar.monthcalendar(2026, m_idx)
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    curr_date = date(2026, m_idx, day)
                    val = daily.get(curr_date, None)
                    style = "pnl-neu"
                    txt = ""
                    if val is not None:
                        style = "pnl-pos" if val > 0 else "pnl-neg"
                        txt = f"${val:.0f}"
                    cols[i].markdown(f'<div class="cal-day {style}">{day}<div class="pnl-val">{txt}</div></div>', unsafe_allow_html=True)

# ==========================================
# 7. ARCHIVIO & RISK
# ==========================================
elif page == "🗄️ ARCHIVIO DATI":
    st.title("Trade History")
    if not df_main.empty:
        st.dataframe(df_main.sort_values('exit_date', ascending=False), use_container_width=True)
        del_id = st.number_input("ID Trade da cancellare", step=1)
        if st.button("DELETE"):
            db.table("trades").delete().eq("id", del_id).execute()
            st.rerun()

elif page == "💰 RISK CALC":
    st.title("Risk Management")
    bal = st.number_input("Account Balance ($)", value=10000.0)
    risk_p = st.slider("Risk %", 0.1, 5.0, 1.0)
    sl_points = st.number_input("Stop Loss (Points)", value=20.0)
    val_point = st.number_input("Multiplier ($)", value=2.0)
    
    if sl_points > 0:
        risk_usd = bal * (risk_p/100)
        pos_size = risk_usd / (sl_points * val_point)
        st.metric("Suggested Contracts", f"{pos_size:.2f}")
        st.write(f"Stai rischiando ${risk_usd:,.2f} per questa operazione.")
        # ==========================================
# 8. SECURITY & CUSTOM BRANDING (HIDE STREAMLIT)
# ==========================================

# 1. Funzione per nascondere il menu Streamlit e il footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* Questo serve per rendere l'app più pulita */
            .stApp { margin-top: -20px; }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 2. Sistema di Login Semplice
def check_password():
    """Restituisce True se l'utente ha inserito la password corretta."""
    def password_entered():
        if st.session_state["password"] == "IL_TUO_TRADECORE_2026": # CAMBIA QUESTA PASSWORD
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Rimuove la password dallo stato per sicurezza
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Schermata iniziale di Login
        st.markdown("<h1 style='text-align: center;'>🔐 TRADECORE ACCESS</h1>", unsafe_allow_html=True)
        st.text_input("Inserisci il codice di accesso", type="password", on_change=password_entered, key="password")
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 Password errata. Riprova.")
        return False
    else:
        return True

# 3. Come usare il login nel codice principale
# Avvolgeremo tutto il resto del codice dentro un:
# if check_password():
#     ... qui va tutto il resto della tua app ...

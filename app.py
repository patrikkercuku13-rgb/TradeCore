import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURAZIONE PAGINA (STILE TRADECORE) ---
st.set_page_config(page_title="TradeCore | Pro Dashboard", layout="wide", page_icon="📈")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div.stButton > button { background-color: white; color: black; border-radius: 5px; font-weight: bold; width: 100%; border: none; }
    div.stButton > button:hover { background-color: #dcdcdc; }
    .stMetric { background-color: #1a1c23; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    [data-testid="stSidebar"] { background-color: #1a1c23; border-right: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONNESSIONE SUPABASE ---
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
try:
    supabase: Client = create_client(URL, KEY)
except:
    st.error("Errore di connessione al database. Controlla le chiavi.")

# --- 3. FUNZIONI CORE ---
def fetch_trades():
    try:
        res = supabase.table('trades').select("*").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame()

def save_trade(asset, profit, pips, contracts, psychology, notes):
    try:
        supabase.table('trades').insert({
            "asset": asset, "profit": profit, "pips": pips, 
            "contracts": contracts, "psychology": psychology, "notes": notes
        }).execute()
        st.toast("🚀 Trade registrato con successo!", icon="🔥")
        st.rerun()
    except Exception as e:
        st.error(f"Errore: {e}")

# --- 4. LOGICA DASHBOARD & IMPOSTAZIONI ---
df = fetch_trades()

# Gestione Saldo Iniziale (Settings)
if 'initial_balance' not in st.session_state:
    st.session_state.initial_balance = 5000.0

# --- 5. INTERFACCIA PRINCIPALE ---
st.title("TRADECORE")
st.caption("THE TRADER'S VAULT • v1.2")

# Calcoli
if not df.empty:
    df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0)
    total_pl = df['profit'].sum()
    current_bal = st.session_state.initial_balance + total_pl
    win_rate = (len(df[df['profit'] > 0]) / len(df)) * 100 if len(df) > 0 else 0
else:
    total_pl, current_bal, win_rate = 0, st.session_state.initial_balance, 0

# Metriche Superiori
m1, m2, m3, m4 = st.columns(4)
m1.metric("CURRENT BALANCE", f"€{current_bal:,.2f}")
m2.metric("TOTAL P/L", f"€{total_pl:,.2f}", delta=f"{total_pl:,.2f}")
m3.metric("WIN RATE", f"{win_rate:.1f}%")
m4.metric("EXECUTIONS", len(df) if not df.empty else 0)

st.divider()

# --- 6. TABS (GRAFICI, JOURNAL, SETTINGS) ---
tab_chart, tab_journal, tab_settings = st.tabs(["📈 PERFORMANCE", "📜 JOURNAL", "⚙️ SETTINGS"])

with tab_chart:
    if not df.empty:
        df['equity'] = st.session_state.initial_balance + df['profit'].cumsum()
        fig = px.line(df, y='equity', title='Equity Growth

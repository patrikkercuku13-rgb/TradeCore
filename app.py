import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CONFIGURAZIONE SUPABASE ---
URL: str = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="TradeCore | Professional Dashboard", layout="wide")

# CSS per il look Bianco e Nero (Dark Mode)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div.stButton > button { background-color: white; color: black; border-radius: 5px; font-weight: bold; width: 100%; }
    .stMetric { background-color: #1a1c23; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONI DATABASE ---
def fetch_trades():
    response = supabase.table('trades').select("*").order('created_at').execute()
    return pd.DataFrame(response.data)

def save_trade(asset, profit, pips, contracts, psychology, notes):
    supabase.table('trades').insert({
        "asset": asset, "profit": profit, "pips": pips, 
        "contracts": contracts, "psychology": psychology, "notes": notes
    }).execute()
    st.rerun()

# --- HEADER ---
col_logo, col_title = st.columns([1, 4])
with col_title:
    st.title("TRADECORE")
    st.caption("Professional Equity & Psychology Tracker")

# --- CARICAMENTO DATI ---
df = fetch_trades()
initial_balance = 5000.0  # Puoi renderlo variabile nelle impostazioni

# --- CALCOLI DASHBOARD ---
if not df.empty:
    total_profit = df['profit'].sum()
    current_balance = initial_balance + total_profit
    win_rate = (len(df[df['profit'] > 0]) / len(df)) * 100
    total_trades = len(df)
else:
    total_profit, current_balance, win_rate, total_trades = 0, initial_balance, 0, 0

# --- METRICHE PRINCIPALI ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Current Balance", f"€{current_balance:,.2f}")
m2.metric("Total P/L", f"€{total_profit:,.2f}", delta=f"{total_profit:,.2f}")
m3.metric("Win Rate", f"{win_rate:.1f}%")
m4.metric("Trades Executed", total_trades)

st.divider()

# --- SIDEBAR: REGISTRAZIONE OPERAZIONE ---
with st.sidebar:
    st.header("⚡ New Execution")
    asset = st.selectbox("Asset", ["NAS100", "EURUSD", "GOLD", "BTCUSD"])
    prof = st.number_input("Profit/Loss (€)", value=0.0)
    pips = st.number_input("Points / Pips", value=0.0)
    lots = st.number_input("Contracts / Lots", value=0.1)
    
    st.subheader("🧠 Psychology")
    psy = st.select_slider("Mindset State", options=["Tough", "Mixed", "Focused", "God Mode"])
    note = st.text_area("Trade Review", placeholder="Entrata su IFVG...")
    
    if st.button("SAVE TO CLOUD"):
        save_trade(asset, prof, pips, lots, psy, note)

# --- GRAFICI E STORICO ---
tab1, tab2, tab3 = st.tabs(["📈 Equity Curve", "📜 Journal", "⚙️ Settings"])

with tab1:
    if not df.empty:
        df['equity'] = initial_balance + df['profit'].cumsum()
        fig = px.line(df, x=df.index, y='equity', title='Performance Growth',
                     color_discrete_sequence=['white'], template="plotly_dark")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available. Record your first trade to see the curve.")

with tab2:
    if not df.empty:
        # Formattazione tabella per renderla figa
        st.dataframe(df[['created_at', 'asset', 'profit', 'pips', 'contracts', 'psychology', 'notes']].sort_values(by='created_at', ascending=False), 
                     use_container_width=True)
    else:
        st.write("Your journal is empty.")

with tab3:
    st.subheader("Account Settings")
    new_balance = st.number_input("Starting Capital", value=initial_balance)
    st.button("Update Account Settings (Coming Soon)")
       

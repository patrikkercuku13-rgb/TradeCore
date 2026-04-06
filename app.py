import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="TradeCore | Pro Dashboard", layout="wide")

# --- 2. CONNESSIONE SUPABASE ---
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# --- 3. FUNZIONI DATABASE ---
def fetch_trades():
    try:
        # Prendiamo tutto senza ordinamento per ora, così non crasha
        response = supabase.table('trades').select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Errore caricamento dati: {e}")
        return pd.DataFrame()

def save_trade(asset, profit, pips, contracts, psychology, notes):
    try:
        supabase.table('trades').insert({
            "asset": asset, "profit": profit, "pips": pips, 
            "contracts": contracts, "psychology": psychology, "notes": notes
        }).execute()
        st.success("🔥 Trade salvato con successo!")
        st.rerun()
    except Exception as e:
        st.error(f"Errore nel salvataggio: {e}")

# --- 4. LOGICA DASHBOARD ---
df = fetch_trades()
initial_balance = 5000.0

if not df.empty:
    # Assicuriamoci che 'profit' sia numerico
    df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0)
    total_profit = df['profit'].sum()
    current_balance = initial_balance + total_profit
    win_rate = (len(df[df['profit'] > 0]) / len(df)) * 100 if len(df) > 0 else 0
else:
    total_profit, current_balance, win_rate = 0, initial_balance, 0

# --- 5. INTERFACCIA ---
st.title("TRADECORE 🚀")
m1, m2, m3 = st.columns(3)
m1.metric("Balance", f"€{current_balance:,.2f}")
m2.metric("P/L Totale", f"€{total_profit:,.2f}")
m3.metric("Win Rate", f"{win_rate:.1f}%")

st.divider()

# SIDEBAR PER INSERIMENTO
with st.sidebar:
    st.header("⚡ New Execution")
    asset = st.selectbox("Asset", ["NAS100", "EURUSD", "GOLD", "BTCUSD"])
    prof = st.number_input("Profit/Loss (€)", value=0.0)
    pips_val = st.number_input("Points / Pips", value=0.0)
    lots = st.number_input("Contracts / Lots", value=0.1)
    psy = st.select_slider("Mindset", options=["Tough", "Mixed", "Focused", "God Mode"])
    note = st.text_area("Note", placeholder="Es: Entrata su IFVG")
    
    if st.button("SAVE TO CLOUD"):
        save_trade(asset, prof, pips_val, lots, psy, note)

# GRAFICI
if not df.empty:
    df['equity'] = initial_balance + df['profit'].cumsum()
    fig = px.line(df, y='equity', title='Equity Curve', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df, use_container_width=True)
else:
    st.info("Inizia registrando il tuo primo trade dalla barra laterale!")

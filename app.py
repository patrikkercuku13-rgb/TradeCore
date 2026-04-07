import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, date
import calendar
import time
import plotly.graph_objects as go

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="TRADECORE V14", layout="wide")

URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"

@st.cache_resource
def get_client():
    return create_client(URL, KEY)

client = get_client()

# --- FUNZIONE RECUPERO DATI SICURA ---
def load_data():
    try:
        res = client.table("trades").select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            # Forza la creazione delle colonne se mancano per evitare il KeyError
            expected_cols = ['exit_date', 'pnl', 'asset', 'direction', 'setup']
            for col in expected_cols:
                if col not in df.columns:
                    df[col] = None
            
            df['exit_date'] = pd.to_datetime(df['exit_date'], errors='coerce')
            df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
            return df
        return pd.DataFrame(columns=['exit_date', 'pnl', 'asset', 'direction', 'setup', 'notes'])
    except:
        return pd.DataFrame()

df_main = load_data()

# --- NAVIGAZIONE ---
st.sidebar.title("TRADECORE V14")
page = st.sidebar.radio("SISTEMA", ["DASHBOARD", "CALENDARIO", "LOG ESECUZIONE", "ARCHIVIO"])

# --- LOG ESECUZIONE (IL TUO PUNTO DI INSERIMENTO) ---
if page == "LOG ESECUZIONE":
    st.title("Inserimento Trade")
    with st.form("trade_form"):
        c1, c2 = st.columns(2)
        asset = c1.text_input("Asset", "MNQ")
        direction = c2.selectbox("Direzione", ["Long", "Short"])
        
        c3, c4 = st.columns(2)
        entry = c3.number_input("Entrata", format="%.2f")
        exit_p = c4.number_input("Uscita", format="%.2f")
        
        c5, c6 = st.columns(2)
        multiplier = c5.number_input("Moltiplicatore", value=2.0)
        contracts = c6.number_input("Contratti", value=1.0)
        
        dt = st.date_input("Data", date.today())
        
        if st.form_submit_button("SALVA TRADE"):
            pnl = (exit_p - entry) * contracts * multiplier if direction == "Long" else (entry - exit_p) * contracts * multiplier
            payload = {
                "asset": asset, "direction": direction, "entry_price": entry, 
                "exit_price": exit_p, "pnl": pnl, "exit_date": str(dt)
            }
            client.table("trades").insert(payload).execute()
            st.success("Salvato! Vai in Archivio.")
            time.sleep(1)
            st.rerun()

# --- ARCHIVIO (QUI C'ERA L'ERRORE - ORA FISSATO) ---
elif page == "ARCHIVIO":
    st.title("Database Trade")
    if not df_main.empty and 'exit_date' in df_main.columns:
        # Ordiniamo solo se ci sono dati, altrimenti mostriamo la tabella così com'è
        df_display = df_main.sort_values('exit_date', ascending=False)
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("L'archivio è vuoto. Inserisci un trade per vederlo qui.")

# --- DASHBOARD & CALENDARIO (VERSIONE SEMPLIFICATA PER TEST) ---
elif page == "DASHBOARD":
    st.title("Analisi Performance")
    if not df_main.empty:
        st.metric("P&L Totale", f"$ {df_main['pnl'].sum():.2f}")
    else:
        st.write("Dati insufficienti.")

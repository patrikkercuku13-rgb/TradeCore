import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Prop Performance Hub", layout="wide")

# Inizializzazione variabili di sessione
if 'trades' not in st.session_state: st.session_state.trades = []
if 'account_setup' not in st.session_state: 
    st.session_state.account_setup = {"balance": 25000.0, "target": 1500.0, "max_drawdown": 1250.0, "type": "Prop Firm"}

def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker)
        return round(data.history(period="1d")['Close'].iloc[-1], 5)
    except: return 0.0

# --- SIDEBAR: GESTIONE CONTO ---
st.sidebar.title("💳 Account Setup")
with st.sidebar.expander("Configura Sfida", expanded=True):
    acc_type = st.selectbox("Tipo Conto", ["Prop Firm", "Live", "Demo"])
    balance = st.number_input("Capitale Iniziale ($)", value=25000.0)
    target_prof = st.number_input("Target Profitto ($)", value=1500.0)
    max_dd = st.number_input("Max Drawdown ($)", value=1250.0)
    
    if st.button("Aggiorna Impostazioni Conto"):
        st.session_state.account_setup = {
            "balance": balance, "target": target_prof, "max_drawdown": max_dd, "type": acc_type
        }
        st.success("Conto configurato!")

# --- NAVIGAZIONE ---
page = st.sidebar.radio("Vai a:", ["🏠 Dashboard", "📝 Journal", "🧠 Psychology"])

# --- PAGINA DASHBOARD (LA TUA RICHIESTA) ---
if page == "🏠 Dashboard":
    st.title(f"📊 {st.session_state.account_setup['type']} Dashboard")
    
    initial_balance = st.session_state.account_setup['balance']
    target = st.session_state.account_setup['target']
    max_dd_limit = st.session_state.account_setup['max_drawdown']
    
    # Calcolo dati attuali
    df = pd.DataFrame(st.session_state.trades)
    current_pnl = df["PnL"].sum() if not df.empty else 0.0
    current_balance = initial_balance + current_pnl
    
    # 1. METRICHE PRINCIPALI
    c1, c2, c3 = st.columns(3)
    c1.metric("Bilancio Attuale", f"$ {current_balance:.2f}", f"{current_pnl:.2f}")
    
    # Calcolo Target
    missing_target = target - current_pnl
    perc_target = (current_pnl / target) * 100 if current_pnl > 0 else 0
    c2.metric("Mancanza al Target", f"$ {max(0, missing_target):.2f}", f"{min(100, perc_target):.1f}% Completato")
    
    # Calcolo Drawdown
    # Nota: semplificato sul capitale iniziale. Le prop usano spesso il "Trailing", lo affineremo.
    current_dd = initial_balance - current_balance if current_balance < initial_balance else 0
    remaining_dd = max_dd_limit - current_dd
    c3.metric("Margine Drawdown", f"$ {max(0, remaining_dd):.2f}", f"Limite: ${max_dd_limit}", delta_color="inverse")

    # 2. SUGGERIMENTO RISCHIO (RISK MANAGEMENT)
    st.divider()
    st.subheader("🛡️ Risk Management Advice")
    risk_col1, risk_col

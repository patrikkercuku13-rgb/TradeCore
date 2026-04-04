import streamlit as st
import pandas as pd
import yfinance as yf

# CONFIGURAZIONE PRO
st.set_page_config(page_title="Prop Performance Hub", layout="wide")

# INIZIALIZZAZIONE SESSIONE (DATABASE TEMPORANEO)
if 'trades' not in st.session_state: st.session_state.trades = []
if 'daily_recaps' not in st.session_state: st.session_state.daily_recaps = []
if 'account_setup' not in st.session_state: 
    st.session_state.account_setup = {"balance": 25000.0, "target": 1500.0, "max_drawdown": 1250.0, "type": "Prop Firm"}

# FUNZIONE PREZZI LIVE
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker)
        return round(data.history(period="1d")['Close'].iloc[-1], 5)
    except: return 0.0

# --- SIDEBAR: ACCOUNT SETUP & NAVIGAZIONE ---
st.sidebar.title("💳 Account Setup")
with st.sidebar.expander("Configura Challenge", expanded=False):
    acc_type = st.selectbox("Tipo Conto", ["Prop Firm", "Live", "Demo"])
    balance = st.number_input("Capitale Iniziale ($)", value=st.session_state.account_setup["balance"])
    target_prof = st.number_input("Target Profitto ($)", value=st.session_state.account_setup["target"])
    max_dd = st.number_input("Max Drawdown ($)", value=st.session_state.account_setup["max_drawdown"])
    if st.button("Aggiorna Conto"):
        st.session_state.account_setup = {"balance": balance, "target": target_prof, "max_drawdown": max_dd, "type": acc_type}

st.sidebar.divider()
page = st.sidebar.radio("Vai a:", ["🏠 Dashboard", "📝 Journal", "🧠 Psychology"])

# --- 1. PAGINA DASHBOARD ---
if page == "🏠 Dashboard":
    st.title(f"📊 {st.session_state.account_setup['type']} Analytics")
    
    setup = st.session_state.account_setup
    df = pd.DataFrame(st.session_state.trades)
    current_pnl = df["PnL"].sum() if not df.empty else 0.0
    current_balance = setup['balance'] + current_pnl
    
    # Metriche Superiori
    c1, c2, c3 = st.columns(3)
    c1.metric("Bilancio Attuale", f"$ {current_balance:.2f}", f"{current_pnl:.2f}")
    
    miss_target = setup['target'] - current_pnl
    perc_t = (current_pnl / setup['target']) * 100 if current_pnl > 0 else 0
    c2.metric("Manca al Target", f"$ {max(0, miss_target):.2f}", f"{min(100, perc_t):.1f}%")
    
    drawdown_att = setup['balance'] - current_balance if current_balance < setup['balance'] else 0
    margine_dd = setup['max_drawdown'] - drawdown_att
    c3.metric("Margine Drawdown", f"$ {max(0, margine_dd):.2f}", f"Tot: ${setup['max_drawdown']}", delta_color="inverse")

    # Grafico Equity Reale
    st.subheader("📈 Equity Curve (Bilancio Reale)")
    if not df.empty:
        equity_list = [setup['balance']] + (setup['balance'] + df["PnL"].cumsum()).tolist()
        st.line_chart(equity_list)
    else:
        st.info("Nessun trade registrato. La linea partirà dal tuo bilancio iniziale.")

# --- 2. PAGINA JOURNAL (CON CALCOLO TICK/PIPS) ---
elif page == "📝 Journal":
    st.title("📓 Trade Log & Calculator")
    
    with st.form("trade_pro"):
        col1, col2, col3 = st.columns(3)
        asset_type = col1.selectbox("Tipo", ["Futures", "CFD / Forex"])
        ticker = col2.text_input("Ticker (NQ=F, EURUSD=X)", "NQ=F")
        direction = col3.radio("Direzione", ["Long", "Short"], horizontal=True)
        
        live_p = get_live_price(ticker)
        st.write(f"Prezzo Live: **{live_p}**")
        
        c_in, c_out, c_size = st.columns(3)
        p_in = c_in.number_input("Entrata", value=live_p, format="%.5f")
        p_out = c_out.number_input("Uscita", format="%.5f")
        
        if asset_type == "Futures":
            size = c_size.number_input("Contratti", value=1, step=1)
            tick_val = 20 # Nasdaq Mini
        else:
            size = c_size.number_input("Lotti", value=0.1, step=0.01)
            tick_val = 10 # Forex Standard

        if st.form_submit_button("Registra Trade"):
            diff = (p_out - p_in) if direction == "Long" else (p_in - p_out)
            
            if asset_type == "Futures":
                pnl = diff * tick_val * size
            else:
                pnl = (diff * 10000) * size * (tick_val / 10)
            
            st.session_state.trades.append({
                "Asset": ticker, "Dir": direction, "Size": size, "PnL": round(pnl, 2), "Tipo": asset_type
            })
            st.success(f"Registrato! PnL: ${pnl:.2f}")

# --- 3. PAGINA PSYCHOLOGY (MOOD & RECAP) ---
elif page == "🧠 Psychology":
    st.title("🧠 Psychology & Mood")
    st.subheader("Come ti senti oggi?")
    
    m1, m2, m3 = st.columns(3)
    if m1.button("🔴 TOUGH DAY (⛈️)"): st.session_state.last_m = "Tough Day"
    if m2.button("🟡 MIXED (☁️)"): st.session_state.last_m = "Mixed"
    if m3.button("🟢 GOOD DAY (☀️)"): st.session_state.last_m = "Good Day"
    
    curr_mood = st.session_state.get('last_m', 'Seleziona mood')
    st.write(f"Stato attuale: **{curr_mood}**")
    
    recap = st.text_area("Scrivi il tuo Daily Recap...")
    if st.button("Salva Recap"):
        st.session_state.daily_recaps.append({"Mood": curr_mood, "Nota": recap})
        st.balloons()
        st.success("Salva!")
        
    if st.session_state.daily_recaps:
        st.table(pd.DataFrame(st.session_state.daily_recaps).iloc[::-1])

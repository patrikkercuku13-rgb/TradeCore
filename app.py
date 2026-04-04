import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Prop Performance Hub", layout="wide")

if 'trades' not in st.session_state: st.session_state.trades = []
if 'daily_recaps' not in st.session_state: st.session_state.daily_recaps = []

def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker)
        return round(data.history(period="1d")['Close'].iloc[-1], 5)
    except: return 0.0

# --- NAVIGAZIONE ---
st.sidebar.title("🎛️ Navigation")
page = st.sidebar.radio("Vai a:", ["🏠 Dashboard", "📝 Journal", "🧠 Daily Psychology", "🔔 Alerts & Setup"])

# --- PAGINA DASHBOARD ---
if page == "🏠 Dashboard":
    st.title("📊 Prop Analytics")
    if st.session_state.trades:
        df = pd.DataFrame(st.session_state.trades)
        c1, c2, c3 = st.columns(3)
        total_pnl = df["PnL"].sum()
        c1.metric("Total PnL", f"$ {total_pnl:.2f}")
        winrate = (len(df[df['PnL'] > 0]) / len(df)) * 100
        c2.metric("Winrate", f"{winrate:.1f}%")
        c3.metric("Trades", len(df))
        st.subheader("Equity Curve")
        st.line_chart(df["PnL"].cumsum())
        st.subheader("Storico Trade")
        st.dataframe(df.iloc[::-1], use_container_width=True)

# --- PAGINA JOURNAL (VERSIONE PRO) ---
elif page == "📝 Journal":
    st.title("📓 Professional Trade Log")
    
    with st.form("trade_pro"):
        col1, col2 = st.columns(2)
        asset_type = col1.selectbox("Tipo Strumento", ["Futures", "CFD / Forex"])
        ticker = col2.text_input("Ticker (es: NQ=F, EURUSD=X)", "NQ=F")
        
        live_p = get_live_price(ticker)
        st.write(f"Prezzo Live attuale: **{live_p}**")
        
        c_in, c_out = st.columns(2)
        p_in = c_in.number_input("Prezzo Entrata", value=live_p, format="%.5f")
        p_out = c_out.number_input("Prezzo Uscita", format="%.5f")
        
        direction = st.radio("Direzione", ["Long", "Short"], horizontal=True)
        
        # LOGICA DINAMICA LOTTI / CONTRATTI
        if asset_type == "Futures":
            size = st.number_input("Numero di Contratti", value=1, step=1)
            tick_value = 20 # Valore punto NQ Mini. Per Micro metti 2.
        else:
            size = st.number_input("Numero di Lotti", value=0.1, step=0.01)
            tick_value = 10 # Valore standard Pip per 1 lotto Forex

        submit = st.form_submit_button("Registra Operazione")
        
        if submit:
            # CALCOLO PNL
            if direction == "Long":
                diff = p_out - p_in
            else:
                diff = p_in - p_out
            
            if asset_type == "Futures":
                pnl_finale = diff * tick_value * size
            else:
                # Calcolo semplificato Forex: (Prezzo * 10000 per i pips) * size * 10$
                pnl_finale = (diff * 10000) * size * (tick_value / 10) 
            
            st.session_state.trades.append({
                "Asset": ticker, 
                "Tipo": asset_type,
                "Dir": direction,
                "Size": size,
                "PnL": round(pnl_finale, 2)
            })
            st.success(f"Trade {direction} salvato! PnL: ${pnl_finale:.2f}")

# --- PAGINA PSYCHOLOGY ---
elif page == "🧠 Daily Psychology":
    st.title("🧠 Psychology & Mood")
    # ... (Il codice del mood che abbiamo fatto prima va qui)

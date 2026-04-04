import streamlit as st
import pandas as pd
import yfinance as yf # La libreria magica per i prezzi

st.set_page_config(page_title="Prop Performance Hub", layout="wide")

if 'trades' not in st.session_state:
    st.session_state.trades = []

# --- FUNZIONE RECUPERO PREZZI LIVE ---
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker)
        # Prendiamo l'ultima chiusura disponibile
        price = data.history(period="1d")['Close'].iloc[-1]
        return round(price, 5)
    except:
        return 0.0

# --- NAVIGAZIONE ---
st.sidebar.title("🎛️ Navigation")
page = st.sidebar.radio("Vai a:", ["🏠 Dashboard", "📝 Journal", "🔔 Alerts & Setup"])

if page == "🏠 Dashboard":
    st.title("📊 Prop Analytics")
    # ... (stesso codice di prima per la dashboard)

elif page == "📝 Journal":
    st.title("📓 Trading Journal")
    
    with st.form("inserimento_trade"):
        st.subheader("Nuovo Trade")
        
        # INPUT TICKER
        ticker_input = st.text_input("Inserisci Ticker (es: NQ=F, EURUSD=X, AAPL)", "NQ=F")
        
        # TASTO PER AGGIORNARE IL PREZZO
        current_market_price = get_live_price(ticker_input)
        st.write(f"🏷️ Prezzo attuale di mercato: **{current_market_price}**")
        
        col_a, col_b = st.columns(2)
        prezzo_in = col_a.number_input("Tuo Prezzo Entrata", value=current_market_price, format="%.5f")
        prezzo_out = col_b.number_input("Tuo Prezzo Uscita", format="%.5f")
        
        note = st.text_area("Note sul trade")
        submit = st.form_submit_button("Registra Trade")
        
        if submit:
            # Calcolo semplificato (poi lo affineremo per lotti/contratti)
            pnl = (prezzo_out - prezzo_in) * 20 
            st.session_state.trades.append({"Asset": ticker_input, "PnL": pnl, "Note": note})
            st.success("Trade salvato!")

elif page == "🔔 Alerts & Setup":
    st.title("⚙️ Setup")
    st.write("Configura qui i tuoi parametri...")

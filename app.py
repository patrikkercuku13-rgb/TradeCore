import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Prop Performance Hub", layout="wide")

# Inizializzazione sessioni per non perdere i dati durante la navigazione
if 'trades' not in st.session_state: st.session_state.trades = []
if 'daily_recaps' not in st.session_state: st.session_state.daily_recaps = []

# --- FUNZIONE PREZZI LIVE ---
def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker)
        return round(data.history(period="1d")['Close'].iloc[-1], 5)
    except: return 0.0

# --- SIDEBAR ---
st.sidebar.title("🎛️ Navigation")
page = st.sidebar.radio("Vai a:", ["🏠 Dashboard", "📝 Journal", "🧠 Daily Psychology", "🔔 Alerts & Setup"])

# --- PAGINA 1: DASHBOARD ---
if page == "🏠 Dashboard":
    st.title("📊 Prop Analytics")
    if st.session_state.trades:
        df = pd.DataFrame(st.session_state.trades)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total PnL", f"$ {df['PnL'].sum():.2f}")
        winrate = (len(df[df['PnL'] > 0]) / len(df)) * 100
        c2.metric("Winrate", f"{winrate:.1f}%")
        c3.metric("Trades", len(df))
        st.line_chart(df["PnL"].cumsum())

# --- PAGINA 2: JOURNAL ---
elif page == "📝 Journal":
    st.title("📓 Trade Log")
    with st.form("trade_form"):
        ticker = st.text_input("Ticker (es: NQ=F, EURUSD=X)", "NQ=F")
        live_p = get_live_price(ticker)
        st.write(f"Prezzo Live: **{live_p}**")
        p_in = st.number_input("Entrata", value=live_p, format="%.5f")
        p_out = st.number_input("Uscita", format="%.5f")
        if st.form_submit_button("Salva Trade"):
            pnl = (p_out - p_in) * 20 # Da personalizzare poi
            st.session_state.trades.append({"Asset": ticker, "PnL": pnl})
            st.success("Trade registrato!")

# --- PAGINA 3: DAILY PSYCHOLOGY (LA TUA IDEA!) ---
elif page == "🧠 Daily Psychology":
    st.title("🌩️ Daily Recap & Mood")
    st.subheader("Com'è andata oggi psicologicamente?")
    
    col1, col2, col3 = st.columns(3)
    
    # Sistema a pulsanti per il Mood
    with col1:
        if st.button("🔴 TOUGH DAY \n (⛈️ Tempesta)"):
            st.session_state.last_mood = "Tough Day"
            st.error("Oggi è stata dura. Respira e stacca i monitor.")
            
    with col2:
        if st.button("🟡 MIXED \n (☁️ Nuvola)"):
            st.session_state.last_mood = "Mixed"
            st.warning("Giornata così e così. Analizza gli errori.")
            
    with col3:
        if st.button("🟢 GOOD DAY \n (☀️ Sole)"):
            st.session_state.last_mood = "Good Day"
            st.success("Grande focus! Continua così.")

    st.divider()
    
    # Spazio per il Recap Lungo
    recap_text = st.text_area("Scrivi il tuo Daily Recap (Note lunghe, errori, lezioni imparate...)", height=200)
    
    if st.button("Salva Recap Giornaliero"):
        mood = st.session_state.get('last_mood', 'Non dichiarato')
        st.session_state.daily_recaps.append({"Data": pd.Timestamp.now(), "Mood": mood, "Note": recap_text})
        st.balloons()
        st.success("Recap salvato nel database!")

    # Storico dei Recap
    if st.session_state.daily_recaps:
        st.subheader("📖 Storico dei tuoi Recap")
        st.table(pd.DataFrame(st.session_state.daily_recaps).iloc[::-1])

# --- PAGINA 4: ALERTS ---
elif page == "🔔 Alerts & Setup":
    st.title("⚙️ Setup")
    st.info("Configurazioni notifiche in arrivo...")

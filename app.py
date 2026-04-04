import streamlit as st
import pandas as pd

# Configurazione Pagina Stile Pro
st.set_page_config(page_title="Prop Performance Hub", layout="wide", initial_sidebar_state="expanded")

# Inizializzazione Database Temporaneo
if 'trades' not in st.session_state:
    st.session_state.trades = []
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# --- SIDEBAR DI NAVIGAZIONE ---
st.sidebar.title("🎛️ Navigation")
page = st.sidebar.radio("Vai a:", ["🏠 Dashboard", "📝 Journal", "🔔 Alerts & Setup"])

# --- PAGINA 1: DASHBOARD ---
if page == "🏠 Dashboard":
    st.title("📊 Prop Analytics")
    if not st.session_state.trades:
        st.info("Nessun dato disponibile. Inserisci i tuoi primi trade nel Journal!")
    else:
        df = pd.DataFrame(st.session_state.trades)
        # Metriche stile Prop Firm
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total PnL", f"$ {df['PnL'].sum():.2f}")
        winrate = (len(df[df['PnL'] > 0]) / len(df)) * 100
        c2.metric("Winrate", f"{winrate:.1f}%")
        c3.metric("Profit Factor", "1.5") # Lo calcoleremo meglio dopo
        c4.metric("Trades", len(df))
        
        st.subheader("Equity Curve")
        st.line_chart(df["PnL"].cumsum())

# --- PAGINA 2: JOURNAL ---
elif page == "📝 Journal":
    st.title("📓 Trading Journal")
    
    with st.expander("✅ Trading Checklist (Obbligatoria)", expanded=True):
        c1, c2 = st.columns(2)
        check1 = c1.checkbox("Ho seguito il trend?")
        check2 = c1.checkbox("Rischio/Rendimento corretto?")
        check3 = c2.checkbox("Setup confermato?")
        check4 = c2.checkbox("Emozioni sotto controllo?")

    with st.form("inserimento_trade"):
        st.subheader("Nuovo Trade")
        col_a, col_b, col_c = st.columns(3)
        asset = col_a.text_input("Strumento (es. MNQ, EURUSD)")
        prezzo_in = col_b.number_input("Entrata", format="%.5f")
        prezzo_out = col_c.number_input("Uscita", format="%.5f")
        
        note = st.text_area("Daily Recap / Note sul trade")
        
        submit = st.form_submit_button("Registra Trade")
        
        if submit:
            if not (check1 and check2 and check3 and check4):
                st.error("Devi completare tutta la checklist prima di registrare!")
            else:
                pnl = (prezzo_out - prezzo_in) * 20 # Esempio per NQ
                st.session_state.trades.append({"Asset": asset, "PnL": pnl, "Note": note})
                st.success("Trade salvato con successo!")

# --- PAGINA 3: ALERTS & SETUP ---
elif page == "🔔 Alerts & Setup":
    st.title("⚙️ Configurazioni & Notifiche")
    st.session_state.user_type = st.selectbox("Cosa tradi principalmente?", ["Futures (Nasdaq/ES)", "Forex", "Azioni"])
    
    st.subheader("Configura Alert")
    if st.checkbox("Attiva notifiche 15min prima dell'apertura"):
        st.success(f"Notifiche attivate per il mercato {st.session_state.user_type}!")
        if st.session_state.user_type == "Futures (Nasdaq/ES)":
            st.write("⏰ Riceverai un alert alle 15:15 (Sessione USA)")
        else:
            st.write("⏰ Riceverai un alert alle 08:45 (Sessione London)")

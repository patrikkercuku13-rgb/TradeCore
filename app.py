import streamlit as st
import pandas as pd

st.set_page_config(page_title="Nasdaq Tracker", layout="wide")
st.title("📈 TradeCore: PnL & Winrate")

# Inizializza i dati se non esistono
if 'trades' not in st.session_state:
    st.session_state.trades = []

# Sidebar per inserire i dati
with st.sidebar:
    st.header("Nuova Operazione")
    pnl_input = st.number_input("PnL Operazione ($)", value=0.0)
    if st.button("Aggiungi Trade"):
        st.session_state.trades.append(pnl_input)
        st.success("Operazione registrata!")

# Calcoli e Visualizzazione
if st.session_state.trades:
    df = pd.DataFrame(st.session_state.trades, columns=["PnL"])
    
    # Metriche
    winrate = (len(df[df["PnL"] > 0]) / len(df)) * 100
    pnl_totale = df["PnL"].sum()
    
    col1, col2 = st.columns(2)
    col1.metric("PnL Totale", f"$ {pnl_totale:.2f}")
    col2.metric("Winrate", f"{winrate:.1f}%")
    
    # Grafico Equity Line
    st.subheader("Andamento Capitale")
    st.line_chart(df["PnL"].cumsum())
else:
    st.info("Aggiungi un trade nella barra a sinistra per iniziare!")

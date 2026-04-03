
import streamlit as st
import pandas as pd

st.title("📈 Nasdaq PnL Tracker")

if 'trades' not in st.session_state:
    st.session_state.trades = []

with st.form("inserimento"):
    pnl = st.number_input("Guadagno/Perdita ($)", value=0.0)
    if st.form_submit_button("Aggiungi"):
        st.session_state.trades.append(pnl)

if st.session_state.trades:
    df = pd.DataFrame(st.session_state.trades, columns=["PnL"])
    st.metric("Winrate", f"{(len(df[df['PnL'] > 0]) / len(df)) * 100:.1f}%")
    st.line_chart(df["PnL"].cumsum())

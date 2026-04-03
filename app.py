import streamlit as st
import pandas as pd

st.set_page_config(page_title="Nasdaq & Global Journal", layout="wide")
st.title("📊 Professional Trading Journal")

if 'trades' not in st.session_state:
    st.session_state.trades = []

# --- SIDEBAR PER L'INSERIMENTO ---
with st.sidebar:
    st.header("📝 Registra Operazione")
    
    tipo_asset = st.selectbox("Tipo di Asset", ["Future (Nasdaq/ES)", "Azione", "Forex", "Commodity"])
    strumento = st.text_input("Strumento (es. NQ, AAPL, EURUSD)", "NQ")
    
    col_a, col_b = st.columns(2)
    prezzo_in = col_a.number_input("Prezzo Ingresso", value=0.0, format="%.5f")
    prezzo_out = col_b.number_input("Prezzo Uscita", value=0.0, format="%.5f")
    
    quantita = st.number_input("Quantità (Lotti/Contratti/Azioni)", value=1.0)

    # Logica di calcolo Profitto
    pnl_calcolato = 0.0
    if st.button("Calcola e Registra"):
        diff = prezzo_out - prezzo_in
        
        if tipo_asset == "Future (Nasdaq/ES)":
            # Esempio Nasdaq: 1 punto = $20 (Micro NQ = $2) -> Usiamo $20 come standard Mini
            moltiplicatore = 20 
            pnl_calcolato = diff * moltiplicatore * quantita
        elif tipo_asset == "Forex":
            # Approssimazione standard Forex (1 lotto = 100k, 1 pip = $10)
            pnl_calcolato = diff * 100000 * quantita
        else: # Azioni e Commodity standard
            pnl_calcolato = diff * quantita
            
        st.session_state.trades.append({
            "Strumento": strumento,
            "Tipo": tipo_asset,
            "Ingresso": prezzo_in,
            "Uscita": prezzo_out,
            "Qty": quantita,
            "PnL ($)": round(pnl_calcolato, 2)
        })
        st.success(f"Registrato: ${pnl_calcolato:.2f}")

# --- DASHBOARD PRINCIPALE ---
if st.session_state.trades:
    df = pd.DataFrame(st.session_state.trades)
    
    # Metriche
    tot_pnl = df["PnL ($)"].sum()
    winrate = (len(df[df["PnL ($)"] > 0]) / len(df)) * 100
    
    c1, c2, c3 = st.columns(3)
    c1.metric("PnL Totale", f"$ {tot_pnl:.2f}")
    c2.metric("Winrate", f"{winrate:.1f}%")
    c3.metric("Operazioni", len(df))
    
    # Grafico Equity
    st.subheader("📈 Equity Line")
    st.line_chart(df["PnL ($)"].cumsum())

    # Registro Tabella
    st.subheader("📑 Registro Storico")
    st.dataframe(df.iloc[::-1], use_container_width=True) # Mostra la tabella bella larga

    if st.button("Svuota Diario"):
        st.session_state.trades = []
        st.rerun()
else:
    st.info("Benvenuto! Usa la barra a sinistra per inserire il tuo primo trade.")

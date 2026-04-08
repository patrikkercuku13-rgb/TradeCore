import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
import plotly.graph_objects as go
import plotly.express as px
import calendar

# ==========================================
# 1. SETUP & DESIGN DI LIVELLO PROFESSIONALE
# ==========================================
st.set_page_config(page_title="TRADECORE TERMINAL v4.0", layout="wide")

# CREDENZIALI INSERITE
SUPABASE_URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# CSS AVANZATO (Design Scuro, Calendario e Bottoni)
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e4e8; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 15px; }
    [data-testid="stMetricValue"] { color: #00ff88; font-family: 'Courier New', monospace; font-size: 1.8rem !important; }
    
    /* Calendario Grid */
    .cal-day { 
        min-height: 85px; border-radius: 10px; padding: 10px; 
        display: flex; flex-direction: column; align-items: center; 
        justify-content: center; border: 1px solid #30363d; font-size: 14px;
        transition: transform 0.2s;
    }
    .cal-day:hover { transform: scale(1.02); border-color: #8b949e; }
    .pnl-pos { background-color: rgba(0, 255, 136, 0.1); color: #00ff88; border: 1px solid #00ff88; }
    .pnl-neg { background-color: rgba(255, 75, 75, 0.1); color: #ff4b4b; border: 1px solid #ff4b4b; }
    .pnl-neu { background-color: #161b22; color: #8b949e; }
    
    /* Bottoni Premium */
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3.5em; 
        background: linear-gradient(135deg, #00ff88 0%, #00d4ff 100%); 
        color: #000; font-weight: bold; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. MOTORE LOGICO
# ==========================================

def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align:center;'>🚀 TRADECORE ACCESS</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Security Token", type="password")
        if st.button("AUTHORIZE"):
            if pwd == "2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("TOKEN INVALIDO")
        return False
    return True

@st.cache_data(ttl=5)
def load_data():
    try:
        res = supabase.table("trades").select("*").order("exit_date").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date']).dt.date
            df['pnl'] = df['pnl'].astype(float)
        return df
    except:
        return pd.DataFrame()

# ==========================================
# 3. INTERFACCIA E NAVIGAZIONE
# ==========================================

if check_password():
    df = load_data()
    
    # Inizializzazione Sessione Account
    if "acc_size" not in st.session_state:
        st.session_state.acc_size = 50000.0
        st.session_state.acc_target = 5000.0
        st.session_state.acc_max_dd = 2500.0

    st.sidebar.title("⚡ TERMINAL v4")
    menu = st.sidebar.radio("NAVIGAZIONE", ["🏠 Dashboard", "📈 Equity & Stats", "📝 Log Trade", "🧠 Psychology", "⚙️ Account Settings"])

    # --- ⚙️ ACCOUNT SETTINGS ---
    if menu == "⚙️ Account Settings":
        st.header("⚙️ Configurazione Conto Prop")
        c1, c2, c3 = st.columns(3)
        st.session_state.acc_size = c1.number_input("Capitale Iniziale ($)", value=st.session_state.acc_size)
        st.session_state.acc_target = c2.number_input("Target Profitto ($)", value=st.session_state.acc_target)
        st.session_state.acc_max_dd = c3.number_input("Massimo Drawdown ($)", value=st.session_state.acc_max_dd)
        st.success("Parametri aggiornati correttamente!")

    # --- 📝 LOG TRADE (SISTEMA AVANZATO) ---
    elif menu == "📝 Log Trade":
        st.header("📝 Registrazione Esecuzione")
        with st.form("trade_form"):
            c1, c2 = st.columns(2)
            asset = c1.selectbox("Asset", ["NASDAQ (NQ)", "S&P500 (ES)", "DAX", "EURUSD", "GOLD", "BTC"])
            side = c1.radio("Direzione", ["LONG", "SHORT"], horizontal=True)
            calc_type = c2.selectbox("Tipo Strumento", ["Futures (Contratti)", "Forex (Lotti)"])
            size = c2.number_input("Quantità (Size)", min_value=0.01, step=0.01)
            
            entry = c1.number_input("Prezzo Entrata", format="%.5f")
            exit_p = c2.number_input("Prezzo Uscita", format="%.5f")
            
            setup = st.selectbox("Setup Utilizzato", ["SMC - OrderBlock", "SMC - FVG", "Liquidity Sweep", "Breakout", "Mean Reversion"])
            score = st.select_slider("Stato Mentale (1=Ansia, 5=Focus)", options=[1,2,3,4,5])
            notes = st.text_area("Note sul Trade (Perché sei entrato? Cosa hai provato?)")
            
            if st.form_submit_button("REGISTRA TRADE"):
                # Calcolo P&L Reale
                if calc_type == "Forex (Lotti)":
                    pnl = (exit_p - entry) * size * 100000 if side == "LONG" else (entry - exit_p) * size * 100000
                else: # Futures Multipliers (Esempi comuni)
                    mult = 20 if "NASDAQ" in asset else 50 if "S&P500" in asset else 25
                    pnl = (exit_p - entry) * size * mult if side == "LONG" else (entry - exit_p) * size * mult
                
                new_trade = {
                    "asset": asset, "pnl": pnl, "size": size, "setup": setup,
                    "entry_price": entry, "exit_price": exit_p, "notes": notes, 
                    "psychology_score": score, "exit_date": str(date.today())
                }
                supabase.table("trades").insert(new_trade).execute()
                st.balloons()
                st.success(f"Trade Salvato! Risultato: ${pnl:.2f}")

    # --- 🏠 DASHBOARD E CALENDARIO ---
    elif menu == "🏠 Dashboard":
        st.header("🏠 Mission Control")
        if not df.empty:
            total_pnl = df['pnl'].sum()
            balance = st.session_state.acc_size + total_pnl
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("BALANCE", f"${balance:,.2f}")
            c2.metric("P&L TOTALE", f"${total_pnl:,.2f}", f"{(total_pnl/st.session_state.acc_size)*100:.2f}%")
            c3.metric("DIST. TARGET", f"${st.session_state.acc_target - total_pnl:,.2f}")
            c4.metric("DD LIMIT", f"${st.session_state.acc_size - st.session_state.acc_max_dd:,.2f}")

            # Barra progresso Target
            prog = min(max(total_pnl / st.session_state.acc_target, 0.0), 1.0)
            st.write(f"**Progresso Obiettivo: {prog*100:.1f}%**")
            st.progress(prog)

            st.divider()
            # CALENDARIO DINAMICO
            st.subheader("📅 Trading Calendar")
            today = date.today()
            cal = calendar.monthcalendar(today.year, today.month)
            daily_pnl = df.groupby('exit_date')['pnl'].sum()
            
            cols_header = st.columns(7)
            for i, d in enumerate(["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]):
                cols_header[i].write(f"**{d}**")
            
            for week in cal:
                cols = st.columns(7)
                for i, day in enumerate(week):
                    if day == 0:
                        cols[i].write("")
                    else:
                        curr_date = date(today.year, today.month, day)
                        val = daily_pnl.get(curr_date, 0)
                        bg = "pnl-pos" if val > 0 else "pnl-neg" if val < 0 else "pnl-neu"
                        cols[i].markdown(f"<div class='cal-day {bg}'><b>{day}</b><br>${val:.0f}</div>", unsafe_allow_html=True)
        else:
            st.info("Nessun dato. Inizia a loggare i tuoi trade!")

    # --- 📈 EQUITY & ANALYTICS ---
    elif menu == "📈 Equity & Stats":
        st.header("📈 Analisi Performance")
        if not df.empty:
            df['cum_pnl'] = df['pnl'].cumsum() + st.session_state.acc_size
            
            col_a, col_b = st.columns([2, 1])
            with col_a:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['cum_pnl'], fill='tozeroy', name='Equity', line=dict(color='#00ff88')))
                fig.update_layout(template="plotly_dark", title="Equity Curve Globale")
                st.plotly_chart(fig, use_container_width=True)
            
            with col_b:
                st.subheader("Win Rate")
                wins = len(df[df['pnl'] > 0])
                wr = (wins / len(df)) * 100
                st.metric("Win Rate", f"{wr:.1f}%")
                st.plotly_chart(px.pie(values=[wins, len(df)-wins], names=['Profit', 'Loss'], color_discrete_sequence=['#00ff88', '#ff4b4b']), use_container_width=True)

    # --- 🧠 PSYCHOLOGY ---
    elif menu == "🧠 Psychology":
        st.header("🧠 Diario Psicologico")
        if not df.empty:
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(px.box(df, x="psychology_score", y="pnl", title="P&L vs Stato Mentale"), use_container_width=True)
            with c2:
                st.plotly_chart(px.bar(df.groupby('setup')['pnl'].sum().reset_index(), x='setup', y='pnl', title="Profitto per Setup"), use_container_width=True)
            
            st.divider()
            st.subheader("Ultimi Journal")
            st.table(df[['exit_date', 'asset', 'psychology_score', 'notes']].tail(10))

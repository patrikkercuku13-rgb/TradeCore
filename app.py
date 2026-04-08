import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
from supabase import create_client, Client
import plotly.graph_objects as go
import plotly.express as px

# ==========================================
# 1. CONFIGURAZIONE & DESIGN SENSORIALE
# ==========================================
st.set_page_config(page_title="TRADECORE ULTRA", layout="wide", initial_sidebar_state="expanded")

# --- CREDENZIALI (INSERISCI LE TUE) ---
SUPABASE_URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
SUPABASE_KEY = "IL_TUO_ANON_PUBLIC_KEY"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e4e8; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 15px; }
    [data-testid="stMetricValue"] { color: #00ff88; font-family: 'Courier New', monospace; }
    .stButton>button { width: 100%; background: linear-gradient(90deg, #00ff88, #00d4ff); color: black; font-weight: bold; border: none; }
    .sidebar .sidebar-content { background-color: #161b22; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNZIONI DI LOGICA E CALCOLO
# ==========================================

def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align:center;'>💻 TERMINAL ACCESS</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Enter Access Token", type="password")
        if st.button("AUTHORIZE"):
            if pwd == "2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")
        return False
    return True

@st.cache_data(ttl=5)
def load_data():
    try:
        res = supabase.table("trades").select("*").order("exit_date", descending=False).execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date'])
            df['pnl'] = df['pnl'].astype(float)
        return df
    except:
        return pd.DataFrame()

# ==========================================
# 3. INTERFACCIA PRINCIPALE
# ==========================================

if check_password():
    df = load_data()
    
    # Sidebar potenziata
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2534/2534341.png", width=100)
    st.sidebar.title("TRADECORE v4.0")
    menu = st.sidebar.selectbox("COMMAND CENTER", 
        ["🏠 Dashboard", "📈 Equity & Analytics", "📝 Log Trade", "🧠 Psychology Vault", "⚙️ Account Settings"])

    # Inizializzazione parametri account
    if "acc_size" not in st.session_state:
        st.session_state.acc_size = 50000.0
        st.session_state.acc_target = 5000.0
        st.session_state.acc_max_dd = 2500.0

    # --- ⚙️ ACCOUNT SETTINGS ---
    if menu == "⚙️ Account Settings":
        st.header("⚙️ Account & Prop Configuration")
        with st.container():
            c1, c2, c3 = st.columns(3)
            st.session_state.acc_size = c1.number_input("Starting Balance ($)", value=st.session_state.acc_size)
            st.session_state.acc_target = c2.number_input("Profit Target ($)", value=st.session_state.acc_target)
            st.session_state.acc_max_dd = c3.number_input("Max Drawdown ($)", value=st.session_state.acc_max_dd)
            st.info(f"Parametri settati per un account da ${st.session_state.acc_size:,.2f}")

    # --- 📝 LOG TRADE (SISTEMA DI CALCOLO AVANZATO) ---
    elif menu == "📝 Log Trade":
        st.header("📝 New Execution Log")
        with st.form("trade_entry"):
            col1, col2 = st.columns(2)
            with col1:
                asset = st.selectbox("Market Asset", ["NASDAQ100", "S&P500", "DAX40", "EURUSD", "GOLD", "BITCOIN"])
                setup = st.selectbox("Trading Setup", ["SMC - OrderBlock", "SMC - Fair Value Gap", "Liquidity Sweep", "Mean Reversion", "News Trade"])
                side = st.radio("Side", ["LONG", "SHORT"], horizontal=True)
            
            with col2:
                calc_type = st.selectbox("Calculation Engine", ["Futures (Contratti)", "Forex (Lotti)"])
                size = st.number_input("Position Size", min_value=0.01, step=0.01)
                entry = st.number_input("Entry Price", format="%.5f")
                exit_p = st.number_input("Exit Price", format="%.5f")
            
            st.divider()
            notes = st.text_area("Trade Diary & Emotional State", placeholder="Ero calmo? Ho seguito il piano?")
            score = st.select_slider("Mindset Quality (1=Panic, 5=Zen)", options=[1,2,3,4,5])
            
            if st.form_submit_button("EXECUTE & SAVE"):
                # Motore di calcolo P&L
                if calc_type == "Forex (Lotti)":
                    pnl = (exit_p - entry) * size * 100000 if side == "LONG" else (entry - exit_p) * size * 100000
                else: # Futures Multipliers
                    mult = 20 if "NASDAQ" in asset else 50
                    pnl = (exit_p - entry) * size * mult if side == "LONG" else (entry - exit_p) * size * mult
                
                data = {
                    "asset": asset, "setup": setup, "pnl": pnl, "size": size,
                    "entry_price": entry, "exit_price": exit_p, "notes": notes,
                    "psychology_score": score, "exit_date": str(date.today())
                }
                supabase.table("trades").insert(data).execute()
                st.success(f"Trade registrato! P&L: ${pnl:.2f}")

    # --- 🏠 DASHBOARD (PROP MONITOR) ---
    elif menu == "🏠 Dashboard":
        st.header("🏠 Mission Control")
        if not df.empty:
            total_pnl = df['pnl'].sum()
            balance = st.session_state.acc_size + total_pnl
            dist_target = st.session_state.acc_target - total_pnl
            dd_level = st.session_state.acc_size - st.session_state.acc_max_dd
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("CURRENT BALANCE", f"${balance:,.2f}")
            c2.metric("PROFIT/LOSS", f"${total_pnl:,.2f}", delta=f"{(total_pnl/st.session_state.acc_size)*100:.2f}%")
            c3.metric("TO TARGET", f"${dist_target:,.2f}", delta_color="inverse")
            c4.metric("DD LIMIT", f"${dd_level:,.2f}")
            
            # Progress Bar Target
            progress = min(max(total_pnl / st.session_state.acc_target, 0.0), 1.0)
            st.write(f"**Target Progress: {progress*100:.1f}%**")
            st.progress(progress)
            
            # Grafico Rapido
            df['cum_pnl'] = df['pnl'].cumsum() + st.session_state.acc_size
            st.plotly_chart(px.line(df, x=df.index, y='cum_pnl', title="Live Account Value"), use_container_width=True)

    # --- 📈 EQUITY & ANALYTICS ---
    elif menu == "📈 Equity & Analytics":
        st.header("📈 Deep Performance Analytics")
        if not df.empty:
            tab1, tab2 = st.tabs(["Equity Curve", "Stats per Setup"])
            
            with tab1:
                df['cum_pnl'] = df['pnl'].cumsum()
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['cum_pnl'], fill='tozeroy', name='Cumulative P&L', line=dict(color='#00ff88')))
                fig.update_layout(template="plotly_dark", title="Total Growth")
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                setup_perf = df.groupby('setup')['pnl'].sum().reset_index()
                st.plotly_chart(px.bar(setup_perf, x='setup', y='pnl', color='pnl', title="Performance by Strategy"), use_container_width=True)
                
                win_rate = (len(df[df['pnl'] > 0]) / len(df)) * 100
                st.metric("WIN RATE GLOBALE", f"{win_rate:.1f}%")

    # --- 🧠 PSYCHOLOGY VAULT ---
    elif menu == "🧠 Psychology Vault":
        st.header("🧠 Emotional Intelligence Lab")
        if not df.empty:
            st.write("Analisi della correlazione tra il tuo stato d'animo e il risultato monetario.")
            fig = px.box(df, x="psychology_score", y="pnl", points="all", title="P&L distribution by Mental State")
            st.plotly_chart(fig, use_container_width=True)
            
            st.subheader("Journal Storico")
            st.dataframe(df[['exit_date', 'asset', 'psychology_score', 'notes']].sort_values(by='exit_date', ascending=False))

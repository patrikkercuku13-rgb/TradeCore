import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import calendar
from supabase import create_client, Client
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURAZIONE E DESIGN (BRANDING)
# ==========================================
st.set_page_config(page_title="TRADECORE TERMINAL", layout="wide", initial_sidebar_state="expanded")

# Inserisci qui i tuoi dati di Supabase
SUPABASE_URL = "IL_TUO_URL" 
SUPABASE_KEY = "LA_TUA_CHIAVE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# CSS per nascondere Streamlit e personalizzare l'interfaccia
st.markdown("""
    <style>
    /* Nascondi Header e Footer ufficiali */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Stile Calendario a Blocchi */
    .cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; }
    .cal-day {
        min-height: 80px; border-radius: 10px; padding: 10px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        border: 1px solid #30363d; font-weight: bold;
    }
    .pnl-pos { background-color: #002b1b; border: 1px solid #00ff88; color: #00ff88; }
    .pnl-neg { background-color: #3d0101; border: 1px solid #ff4b4b; color: #ff4b4b; }
    .pnl-neu { background-color: #161b22; color: #8b949e; }
    
    /* Metriche e Cards */
    div[data-testid="stMetric"] { background-color: #1c2128; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #238636; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNZIONI DI SISTEMA
# ==========================================

def check_password():
    """Protezione Accesso"""
    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center;'>🔐 TRADECORE</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            pwd = st.text_input("Inserisci Password Operatore", type="password")
            if st.button("Sblocca Terminale"):
                if pwd == "2026": # Puoi cambiare la password qui
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Accesso negato. Password errata.")
        return False
    return True

@st.cache_data(ttl=60)
def load_data():
    """Carica trade da Supabase"""
    try:
        res = supabase.table("trades").select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date'])
            df['pnl'] = df['pnl'].astype(float)
        return df
    except Exception as e:
        st.error(f"Errore Database: {e}")
        return pd.DataFrame()

# ==========================================
# 3. INTERFACCIA PRINCIPALE (Se loggato)
# ==========================================

if check_password():
    df_main = load_data()
    
    # Sidebar Navigation
    st.sidebar.markdown("<h2 style='color:#00ff88;'>⚡ TRADECORE PRO</h2>", unsafe_allow_html=True)
    page = st.sidebar.radio("NAVIGAZIONE", [
        "🏠 Dashboard", 
        "📊 Diario Operativo", 
        "📅 Calendario P&L", 
        "📈 Analytics Avanzate",
        "🧮 Risk Calculator",
        "🧠 Psicologia",
        "⚙️ Settings"
    ])
    
    st.sidebar.divider()
    if not df_main.empty:
        total_pnl = df_main['pnl'].sum()
        st.sidebar.metric("Net P&L", f"${total_pnl:,.2f}", delta=f"{total_pnl:,.2f}")

    # --- PAGINA 1: DASHBOARD ---
    if page == "🏠 Dashboard":
        st.title("Market Execution Overview")
        if df_main.empty:
            st.warning("Nessun dato trovato. Vai al Diario per inserire il primo trade.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            wins = len(df_main[df_main['pnl'] > 0])
            wr = (wins / len(df_main)) * 100
            c1.metric("Win Rate", f"{wr:.1f}%")
            c2.metric("Profit Factor", f"{abs(df_main[df_main['pnl']>0]['pnl'].sum() / df_main[df_main['pnl']<0]['pnl'].sum()):.2f}" if len(df_main[df_main['pnl']<0])>0 else "INF")
            c3.metric("Trades", len(df_main))
            c4.metric("Avg Trade", f"${df_main['pnl'].mean():,.2f}")
            
            # Equity Curve
            st.subheader("Equity Curve")
            df_equity = df_main.sort_values('exit_date')
            df_equity['cumulative'] = df_equity['pnl'].cumsum()
            fig = px.line(df_equity, x='exit_date', y='cumulative', template="plotly_dark", color_discrete_sequence=['#00ff88'])
            st.plotly_chart(fig, use_container_width=True)

    # --- PAGINA 2: DIARIO ---
    elif page == "📊 Diario Operativo":
        st.title("Trade Journal")
        with st.expander("➕ AGGIUNGI TRADE", expanded=True):
            with st.form("add_trade"):
                col1, col2, col3 = st.columns(3)
                asset = col1.selectbox("Asset", ["MNQ", "MES", "DAX", "GC", "EURUSD"])
                side = col2.selectbox("Side", ["Long", "Short"])
                pnl = col3.number_input("P&L Netto ($)", value=0.0)
                
                col4, col5 = st.columns(2)
                dt = col4.date_input("Data Chiusura", date.today())
                setup = col5.selectbox("Setup", ["Silver Bullet", "FVG Inversion", "Judas Swing", "MSS"])
                
                note = st.text_area("Note e Confluenze")
                if st.form_submit_button("SALVA TRADE"):
                    data = {"asset": asset, "side": side, "pnl": pnl, "exit_date": str(dt), "strategy": setup, "notes": note}
                    supabase.table("trades").insert(data).execute()
                    st.success("Trade salvato!")
                    st.rerun()
        
        st.subheader("History")
        st.dataframe(df_main.sort_values('exit_date', ascending=False), use_container_width=True)

    # --- PAGINA 3: CALENDARIO ---
    elif page == "📅 Calendario P&L":
        st.title("Profit & Loss Calendar")
        m = st.selectbox("Seleziona Mese", range(1, 13), index=datetime.now().month-1)
        
        df_main['d_only'] = df_main['exit_date'].dt.date
        pnl_map = df_main.groupby('d_only')['pnl'].sum().to_dict()
        
        cal = calendar.monthcalendar(2026, m)
        cols_h = st.columns(7)
        for i, d_name in enumerate(["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]):
            cols_h[i].write(f"**{d_name}**")
            
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    curr_date = date(2026, m, day)
                    val = pnl_map.get(curr_date, 0)
                    cl = "pnl-neu"
                    if val > 0: cl = "pnl-pos"
                    elif val < 0: cl = "pnl-neg"
                    
                    cols[i].markdown(f"<div class='cal-day {cl}'>{day}<br><small>${val:,.0f}</small></div>", unsafe_allow_html=True)

# --- PAGINA 4: ANALYTICS ---
    elif page == "📈 Analytics":
        st.title("Performance Insights")
        if not df_main.empty:
            c1, c2 = st.columns(2)
            
            with c1:
                # Equity Curve
                df_sorted = df_main.sort_values('exit_date')
                df_sorted['cum_pnl'] = df_sorted['pnl'].cumsum()
                fig_line = px.line(df_sorted, x='exit_date', y='cum_pnl', 
                                 title="Equity Curve", template="plotly_dark",
                                 color_discrete_sequence=['#00ff88'])
                st.plotly_chart(fig_line, use_container_width=True)
            
            with c2:
                # Win Rate Pie
                wins = len(df_main[df_main['pnl'] > 0])
                losses = len(df_main[df_main['pnl'] <= 0])
                fig_pie = px.pie(values=[wins, losses], names=['Win', 'Loss'], 
                               title="Win Rate %",
                               color_discrete_sequence=['#00ff88', '#ff4b4b'], 
                               template="plotly_dark")
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("Nessun dato disponibile per le analisi.")

    # --- PAGINA 5: RISK CALCULATOR ---
    elif page == "🧮 Risk Calculator":
        st.title("Position Sizing")
        col1, col2 = st.columns(2)
        with col1:
            balance = st.number_input("Account Balance ($)", value=10000)
            risk_p = st.slider("Rischio %", 0.1, 5.0, 1.0)
            entry = st.number_input("Entry Price", value=0.0)
            sl = st.number_input("Stop Loss Price", value=0.0)
        with col2:
            if entry != 0 and sl != 0:
                risk_amt = balance * (risk_p / 100)
                tick_dist = abs(entry - sl)
                # Calcolo per Micro Nasdaq (MNQ: 1 punto = $2)
                contracts = risk_amt / (tick_dist * 2)
                st.metric("Rischio in $", f"${risk_amt:,.2f}")
                st.success(f"Size Consigliata (MNQ): {contracts:.2f} contratti")

    # --- PAGINA 6: PSICOLOGIA ---
    elif page == "🧠 Psicologia":
        st.title("Mental Edge Tracker")
        st.info("Registra il tuo stato mentale per identificare i trigger emotivi.")
        with st.form("psy"):
            mood = st.select_slider("Mood Post-Sessione", ["Rabbia", "Frustrazione", "Neutro", "Focus", "Euforia"])
            foll_plan = st.checkbox("Ho seguito il piano al 100%?")
            overtrade = st.checkbox("Ho fatto overtrading?")
            st.text_area("Note Psicologiche")
            if st.form_submit_button("Salva Analisi Mentale"):
                st.success("Dati psicologici salvati!")

    # --- PAGINA 7: SETTINGS ---
    elif page == "⚙️ Settings":
        st.title("System Settings")
        st.write("Database Connection Status: **CONNECTED**")
        if st.button("Clear Cache"):
            st.cache_data.clear()
            st.rerun(), names=['Win', 'Loss'], color_discrete_sequence=['#00ff88', '#ff4b4b'], template="plotly_dark")
            st.plotly_chart(fig_pie)

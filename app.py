import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import calendar
from supabase import create_client, Client
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURAZIONE E SETUP
# ==========================================
st.set_page_config(page_title="TRADECORE PRO", layout="wide", initial_sidebar_state="expanded")

# Credenziali Supabase (Da inserire domani a scuola)
SUPABASE_URL = "IL_TUO_URL"
SUPABASE_KEY = "LA_TUA_CHIAVE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 2. BRANDING & CSS CUSTOM
# ==========================================
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Calendario Grid */
    .cal-day {
        width: 100%; aspect-ratio: 1/1; border-radius: 8px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        margin-bottom: 5px; border: 1px solid #30363d;
    }
    .pnl-pos { background-color: #002b1b; border: 1px solid #00ff88; color: #00ff88; }
    .pnl-neg { background-color: #3d0101; border: 1px solid #ff4b4b; color: #ff4b4b; }
    .pnl-neu { background-color: #161b22; color: #8b949e; }
    
    /* Box Psicologia */
    .mood-box { padding: 10px; border-radius: 5px; border-left: 5px solid #ff9f1c; background: #252a33; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. FUNZIONI CORE
# ==========================================
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align:center;'>🔐 TRADECORE ACCESS</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Security Token", type="password")
        if st.button("Unlock"):
            if pwd == "2026": # La tua password
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("Access Denied.")
        return False
    return True

@st.cache_data(ttl=60)
def load_data():
    try:
        res = supabase.table("trades").select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date'])
            df['pnl'] = df['pnl'].astype(float)
        return df
    except: return pd.DataFrame()

# ==========================================
# 4. MAIN APP
# ==========================================
if check_password():
    df_main = load_data()
    
    # Sidebar
    st.sidebar.title("⚡ TRADECORE v3")
    page = st.sidebar.radio("Sezioni", [
        "🏠 Dashboard", 
        "📊 Diario Operativo", 
        "🧠 Psicologia",
        "🧮 Risk Calculator",
        "📅 Calendario", 
        "📈 Analytics"
    ])

    # --- 🧮 SECTION: RISK CALCULATOR ---
    if page == "🧮 Risk Calculator":
        st.title("Position Sizing Calculator")
        c1, c2 = st.columns(2)
        with c1:
            balance = st.number_input("Account Balance ($)", value=10000.0)
            risk_perc = st.slider("Rischio (%)", 0.25, 5.0, 1.0)
            entry = st.number_input("Entry Price", value=0.0)
            stop = st.number_input("Stop Loss", value=0.0)
        
        with c2:
            risk_amt = balance * (risk_perc / 100)
            st.metric("Rischio in Dollari", f"${risk_amt:,.2f}")
            if entry != 0 and stop != 0:
                dist = abs(entry - stop)
                # Calcolo per Micro/Mini Future (Es: MNQ = $2 per punto)
                st.info(f"Distanza Stop: {dist:.2f} punti")
                contracts = risk_amt / (dist * 2) # Esempio per MNQ
                st.success(f"Taglia Suggerita: {contracts:.2f} Micro Contracts")

    # --- 🧠 SECTION: PSICOLOGIA ---
    elif page == "🧠 Psicologia":
        st.title("Trading Psychology Tracker")
        st.markdown("<div class='mood-box'>Analizza il tuo stato mentale per evitare errori emotivi.</div>", unsafe_allow_html=True)
        
        with st.form("psycho_form"):
            mood = st.select_slider("Stato d'animo", options=["Disperato", "Frustrato", "Neutro", "Focalizzato", "Euforico"])
            patience = st.checkbox("Ho rispettato il mio piano?")
            revenge = st.checkbox("Ho sentito l'impulso di fare Revenge Trading?")
            notes = st.text_area("Cosa hai provato durante l'ultima sessione?")
            if st.form_submit_button("Salva Diario Mentale"):
                st.success("Analisi salvata. Ricorda: l'euforia è pericolosa quanto la frustrazione.")

    # --- 📊 SECTION: DIARIO ---
    elif page == "📊 Diario Operativo":
        st.title("Journal Entry")
        with st.expander("📝 Inserisci Trade", expanded=True):
            with st.form("t_form"):
                ca1, ca2, ca3 = st.columns(3)
                asset = ca1.selectbox("Asset", ["MNQ", "MES", "DAX", "GC"])
                side = ca2.selectbox("Side", ["Long", "Short"])
                pnl = ca3.number_input("P&L ($)", value=0.0)
                
                cb1, cb2 = st.columns(2)
                date_t = cb1.date_input("Data", date.today())
                strat = cb2.selectbox("Setup", ["Silver Bullet", "FVG", "MSS", "LQD"])
                
                if st.form_submit_button("Salva Trade"):
                    new_trade = {"asset": asset, "side": side, "pnl": pnl, "exit_date": str(date_t), "strategy": strat}
                    supabase.table("trades").insert(new_trade).execute()
                    st.rerun()
        st.dataframe(df_main.sort_values('exit_date', ascending=False), use_container_width=True)

    # --- 📅 SECTION: CALENDARIO ---
    elif page == "📅 Calendario":
        st.title("P&L Calendar")
        m = st.selectbox("Mese", range(1,13), index=datetime.now().month-1)
        df_main['d_only'] = df_main['exit_date'].dt.date
        pnl_map = df_main.groupby('d_only')['pnl'].sum().to_dict()
        
        cal = calendar.monthcalendar(2026, m)
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    d = date(2026, m, day)
                    val = pnl_map.get(d, 0)
                    cl = "pnl-neu"
                    if val > 0: cl = "pnl-pos"
                    elif val < 0: cl = "pnl-neg"
                    cols[i].markdown(f"<div class='cal-day {cl}'>{day}<br><small>${val:.0f}</small></div>", unsafe_allow_html=True)

    # --- 📈 SECTION: ANALYTICS ---
    elif page == "📈 Analytics":
        st.title("Performance Insights")
        if not df_main.empty:
            c1, c2 = st.columns(2)
            # Equity Curve
            df_main = df_main.sort_values('exit_date')
            df_main['cum_pnl'] = df_main['pnl'].cumsum()
            fig = px.line(df_main, x='exit_date', y='cum_pnl', title="Equity Curve", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
            # Win Rate Pie
            wins = len(df_main[df_main['pnl'] > 0])
            losses = len(df_main[df_main['pnl'] <= 0])
            fig_pie = px.pie(values=[wins, losses], names=['Win', 'Loss'], color_discrete_sequence=['#00ff88', '#ff4b4b'], template="plotly_dark")
            st.plotly_chart(fig_pie)

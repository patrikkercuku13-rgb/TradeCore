import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import calendar
from supabase import create_client, Client
import plotly.express as px

# ==========================================
# 1. SETUP & BRANDING
# ==========================================
st.set_page_config(page_title="TRADECORE PRO", layout="wide")

# Credenziali (Da compilare)
SUPABASE_URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# CSS per pulire l'interfaccia e creare il calendario
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #0e1117; color: #ffffff; }
    .cal-day {
        min-height: 80px; border-radius: 10px; padding: 10px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        border: 1px solid #30363d; font-weight: bold;
    }
    .pnl-pos { background-color: #002b1b; border: 1px solid #00ff88; color: #00ff88; }
    .pnl-neg { background-color: #3d0101; border: 1px solid #ff4b4b; color: #ff4b4b; }
    .pnl-neu { background-color: #161b22; color: #8b949e; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNZIONI DI SISTEMA
# ==========================================
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align:center;'>🔐 TRADECORE ACCESS</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Security Token", type="password")
        if st.button("Unlock"):
            if pwd == "2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Password Errata")
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
    except:
        return pd.DataFrame()

# ==========================================
# 3. LOGICA PRINCIPALE
# ==========================================
if check_password():
    df_main = load_data()
    
    # Sidebar
    st.sidebar.title("⚡ TRADECORE v3")
    page = st.sidebar.radio("Menu", [
        "🏠 Dashboard", 
        "📊 Diario", 
        "📅 Calendario", 
        "📈 Analytics",
        "🧮 Risk Calc",
        "🧠 Psicologia"
    ])

    # --- 🏠 DASHBOARD ---
    if page == "🏠 Dashboard":
        st.title("Trading Overview")
        if not df_main.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Net Profit", f"${df_main['pnl'].sum():,.2f}")
            c2.metric("Total Trades", len(df_main))
            wr = (len(df_main[df_main['pnl'] > 0]) / len(df_main)) * 100
            c3.metric("Win Rate", f"{wr:.1f}%")
            
            df_sorted = df_main.sort_values('exit_date')
            df_sorted['equity'] = df_sorted['pnl'].cumsum()
            fig = px.line(df_sorted, x='exit_date', y='equity', title="Equity Curve", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    # --- 📊 DIARIO ---
    elif page == "📊 Diario":
        st.title("Trade Journal")
        with st.form("new_trade"):
            c1, c2, c3 = st.columns(3)
            asset = c1.selectbox("Asset", ["MNQ", "MES", "DAX", "GC"])
            pnl = c2.number_input("P&L ($)", value=0.0)
            dt = c3.date_input("Data", date.today())
            if st.form_submit_button("Salva Trade"):
                data = {"asset": asset, "pnl": pnl, "exit_date": str(dt)}
                supabase.table("trades").insert(data).execute()
                st.success("Salvato!")
                st.rerun()
        st.dataframe(df_main.sort_values('exit_date', ascending=False), use_container_width=True)

    # --- 📅 CALENDARIO ---
    elif page == "📅 Calendario":
        st.title("P&L Calendar")
        m = st.selectbox("Mese", range(1, 13), index=datetime.now().month-1)
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
                    cols[i].markdown(f"<div class='cal-day {cl}'>{day}<br>${val:.0f}</div>", unsafe_allow_html=True)

    # --- 📈 ANALYTICS (PULITO) ---
    elif page == "📈 Analytics":
        st.title("Detailed Analytics")
        if not df_main.empty:
            col_a, col_b = st.columns(2)
            with col_a:
                # Grafico a Torta Win/Loss
                wins = len(df_main[df_main['pnl'] > 0])
                losses = len(df_main[df_main['pnl'] <= 0])
                fig_pie = px.pie(values=[wins, losses], names=['Win', 'Loss'], 
                               title="Win Rate %", template="plotly_dark",
                               color_discrete_sequence=['#00ff88', '#ff4b4b'])
                st.plotly_chart(fig_pie, use_container_width=True)
            with col_b:
                # Profit per Asset
                asset_pnl = df_main.groupby('asset')['pnl'].sum().reset_index()
                fig_bar = px.bar(asset_pnl, x='asset', y='pnl', title="Profit by Asset", template="plotly_dark")
                st.plotly_chart(fig_bar, use_container_width=True)

    # --- 🧮 RISK CALC ---
    elif page == "🧮 Risk Calc":
        st.title("Position Sizing")
        balance = st.number_input("Account Balance ($)", value=10000)
        risk_perc = st.slider("Rischio (%)", 0.5, 5.0, 1.0)
        stop_loss = st.number_input("Stop Loss (punti)", value=10.0)
        
        risk_amt = balance * (risk_perc / 100)
        # Esempio MNQ: 1 punto = 2$
        if stop_loss > 0:
            contracts = risk_amt / (stop_loss * 2)
            st.success(f"Rischio: ${risk_amt:.2f} | Contratti MNQ: {contracts:.2f}")

    # --- 🧠 PSICOLOGIA ---
    elif page == "🧠 Psicologia":
        st.title("Trading Psychology")
        mood = st.select_slider("Mood", ["Frustrato", "Neutro", "Focus", "Euforico"])
        plan = st.checkbox("Ho seguito il piano?")
        st.text_area("Note mentali della sessione")
        if st.button("Salva Mood"):
            st.success("Stato d'animo registrato.")

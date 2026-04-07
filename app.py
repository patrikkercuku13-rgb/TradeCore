import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, date, timedelta
import calendar
import time

# ==========================================
# 1. CORE ENGINE & UI DESIGN
# ==========================================
st.set_page_config(
    page_title="TRADECORE V15.2 | PRO TERMINAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estetica High-End Terminal
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono&display=swap');
    
    .main { background-color: #050708; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    div[data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #1f2328; }
    
    .stMetric {
        background: linear-gradient(145deg, #0d1117, #161b22);
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    .cal-wrapper { display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-start; }
    .cal-day {
        width: 60px; height: 60px; border-radius: 50%;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 700; font-size: 0.9em; transition: 0.3s;
    }
    .pnl-pos { background: linear-gradient(135deg, #238636 0%, #2ea043 100%); color: white; border: 2px solid #3fb950; }
    .pnl-neg { background: linear-gradient(135deg, #da3633 0%, #f85149 100%); color: white; border: 2px solid #ff7b72; }
    .pnl-neu { background-color: #161b22; color: #8b949e; border: 1px solid #30363d; }
    .pnl-sub { font-size: 0.55em; font-weight: 400; margin-top: 2px; font-family: 'JetBrains Mono'; }

    .stTextInput input, .stNumberInput input, .stSelectbox div {
        background-color: #0d1117 !important; color: #00ff88 !important; border: 1px solid #30363d !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE CONNECTION
# ==========================================
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"

@st.cache_resource
def get_client():
    return create_client(URL, KEY)

db = get_client()

def load_data_vault():
    try:
        res = db.table("trades").select("*").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date'], errors='coerce')
            df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
            # Fix colonne per coerenza database
            cols = ['setup', 'session', 'psychology', 'emotion', 'discipline', 'notes', 'contracts', 'direction', 'asset', 'entry_price', 'exit_price']
            for c in cols:
                if c not in df.columns: df[c] = "N/A"
            return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #00ff88;'>TRADECORE V15.2</h2>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("SISTEMA OPERATIVO", [
        "📊 DASHBOARD",
        "📅 CALENDARIO P&L",
        "📝 LOG ESECUZIONE",
        "🧠 PSICOLOGIA",
        "📈 ANALISI STRATEGICA",
        "💰 RISK CALCULATOR",
        "🗄️ ARCHIVIO DATI",
        "⚙️ SETTINGS"
    ])
    st.divider()
    st.caption("Database Status: Online")

df_main = load_data_vault()

# ==========================================
# 4. PAGINA: LOG ESECUZIONE (FIX INDENTAZIONE & CALCOLO)
# ==========================================
if page == "📝 LOG ESECUZIONE":
    st.title("Execution Entry Terminal")
    st.markdown("Registra l'operazione. Il sistema calcolerà automaticamente il P&L in base ai punti.")
    
    with st.form("trade_form_v15_2", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            asset = st.selectbox("Asset", ["MNQ", "MES", "NQ", "ES", "MYM", "M2K", "BTCUSD", "GOLD", "EURUSD"])
            direction = st.radio("Side", ["Long", "Short"], horizontal=True)
        with col2:
            entry = st.number_input("Entry Price", format="%.2f", step=0.25)
            exit_p = st.number_input("Exit Price", format="%.2f", step=0.25)
        with col3:
            contracts = st.number_input("Contracts", value=1.0, step=0.1)
            multiplier = st.number_input("Point Value ($)", value=2.0, help="MNQ=2, MES=5, NQ=20, ES=50")
        with col4:
            dt = st.date_input("Exit Date", date.today())
            session = st.selectbox("Session", ["Asia", "London Open", "NY Morning", "NY Lunch", "NY Afternoon"])

        st.divider()
        st.subheader("Context & Strategy")
        s1, s2, s3 = st.columns(3)
        with s1:
            setup = st.selectbox("Primary Setup", ["FVG Inversion", "Liquidity Sweep", "MSS / Shift", "Silver Bullet", "Unicorn", "Turtle Soup", "Order Block", "Breaker Block"])
        with s2:
            tf = st.selectbox("Timeframe", ["1s", "15s", "1m", "5m", "15m", "1h", "4h", "D"])
        with s3:
            rr = st.number_input("Planned R:R", value=2.0)

        st.divider()
        st.subheader("Psychology Review")
        p1, p2, p3 = st.columns(3)
        with p1: psy = st.select_slider("Mindset", ["Tired", "Anxious", "Neutral", "Focused", "Flow"])
        with p2: emo = st.selectbox("Emotion", ["Calm", "FOMO", "Greed", "Patience", "Fear", "Revenge"])
        with p3: disc = st.radio("Discipline", ["Perfect", "Minor Violation", "Major Violation"], horizontal=True)
        
        notes = st.text_area("Trade Journal / Mistakes / Lessons")

        # IL PULSANTE È DENTRO IL FORM (Indentato correttamente)
        submit = st.form_submit_button("COMMIT TO VAULT")
        
        if submit:
            # Calcolo P&L Reale (Punti * Contratti * ValorePunto)
            diff = (exit_p - entry) if direction == "Long" else (entry - exit_p)
            pnl_final = round(float(diff * contracts * multiplier), 2)
            
            payload = {
                "asset": asset, "direction": direction, "entry_price": float(entry), 
                "exit_price": float(exit_p), "pnl": pnl_final, "setup": setup, 
                "session": session, "exit_date": str(dt), "psychology": psy, 
                "emotion": emo, "discipline": disc, "notes": notes, 
                "timeframe": tf, "contracts": float(contracts)
            }
            
            try:
                db.table("trades").insert(payload).execute()
                st.balloons()
                st.success(f"✅ REGISTRATO: ${pnl_final:,.2f}")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Errore Database: {e}")

# ==========================================
# 5. PAGINA: DASHBOARD
# ==========================================
elif page == "📊 DASHBOARD":
    st.title("Performance Intelligence")
    if not df_main.empty:
        net = df_main['pnl'].sum()
        wins = df_main[df_main['pnl'] > 0]
        losses = df_main[df_main['pnl'] < 0]
        wr = (len(wins) / len(df_main)) * 100 if len(df_main) > 0 else 0
        pf = abs(wins['pnl'].sum() / losses['pnl'].sum()) if not losses.empty else 1.0
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("NET P&L", f"${net:,.2f}")
        c2.metric("WIN RATE", f"{wr:.1f}%")
        c3.metric("PROFIT FACTOR", f"{pf:.2f}")
        c4.metric("TOTAL TRADES", len(df_main))

        # Equity Curve
        df_sorted = df_main.sort_values('exit_date')
        df_sorted['equity'] = df_sorted['pnl'].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_sorted['exit_date'], y=df_sorted['equity'], fill='tozeroy', line=dict(color='#00ff88', width=3)))
        fig.update_layout(template="plotly_dark", title="Cumulative Equity Growth", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Benvenuto nel Terminale. Vai al Log per iniziare.")

# ==========================================
# 6. PAGINA: CALENDARIO (STILE PIKKIT)
# ==========================================
elif page == "📅 CALENDARIO P&L":
    st.title("Monthly Journal")
    if not df_main.empty:
        df_main['d_only'] = df_main['exit_date'].dt.date
        daily_pnl = df_main.groupby('d_only')['pnl'].sum().to_dict()
        
        now = datetime.now()
        month_idx = st.selectbox("Mese", range(1, 13), index=now.month-1)
        cal = calendar.monthcalendar(now.year, month_idx)
        
        st.subheader(f"{calendar.month_name[month_idx]} {now.year}")
        
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    dt_obj = date(now.year, month_idx, day)
                    p = daily_pnl.get(dt_obj, None)
                    cls = "pnl-neu"
                    txt = ""
                    if p is not None:
                        cls = "pnl-pos" if p > 0 else "pnl-neg"
                        txt = f"{p:+.0f}"
                    cols[i].markdown(f'<div class="cal-day {cls}">{day}<div class="pnl-sub">{txt}</div></div>', unsafe_allow_html=True)
    else:
        st.warning("Nessun dato per il calendario.")

# ==========================================
# 7. PSICOLOGIA & STRATEGIA
# ==========================================
elif page == "🧠 PSICOLOGIA":
    st.title("Behavioral Analysis")
    if not df_main.empty:
        col1, col2 = st.columns(2)
        fig1 = px.bar(df_main.groupby('emotion')['pnl'].sum().reset_index(), x='emotion', y='pnl', color='pnl', title="PnL by Dominant Emotion", template="plotly_dark")
        col1.plotly_chart(fig1, use_container_width=True)
        fig2 = px.box(df_main, x='psychology', y='pnl', title="PnL Distribution by Mindset", template="plotly_dark")
        col2.plotly_chart(fig2, use_container_width=True)

elif page == "📈 ANALISI STRATEGICA":
    st.title("Quantitative Efficiency")
    if not df_main.empty:
        col1, col2 = st.columns(2)
        fig1 = px.pie(df_main, names='setup', values='pnl', title="PnL Distribution by Setup", hole=0.5, template="plotly_dark")
        col1.plotly_chart(fig1, use_container_width=True)
        fig2 = px.bar(df_main.groupby('session')['pnl'].sum().reset_index(), x='session', y='pnl', color='pnl', title="Performance by Market Session")
        col2.plotly_chart(fig2, use_container_width=True)

# ==========================================
# 8. RISK CALCULATOR
# ==========================================
elif page == "💰 RISK CALCULATOR":
    st.title("Position Sizing Tool")
    c1, c2 = st.columns(2)
    with c1:
        balance = st.number_input("Account Balance ($)", value=10000.0)
        risk_p = st.slider("Risk per Trade (%)", 0.1, 5.0, 1.0)
    with c2:
        stop_pts = st.number_input("Stop Loss (Points)", value=20.0)
        pt_val = st.number_input("Multiplier ($)", value=2.0)
    
    if stop_pts > 0:
        risk_usd = balance * (risk_p / 100)
        size = risk_usd / (stop_pts * pt_val)
        st.metric("Suggested Size (Contracts)", f"{size:.2f}")
        st.info(f"Rischio Totale per questo trade: ${risk_usd:,.2f}")

# ==========================================
# 9. ARCHIVIO & SETTINGS
# ==========================================
elif page == "🗄️ ARCHIVIO DATI":
    st.title("Full Trade Archive")
    if not df_main.empty:
        st.dataframe(df_main.sort_values('exit_date', ascending=False), use_container_width=True)
        st.divider()
        del_id = st.number_input("Inserisci ID da eliminare", step=1)
        if st.button("DELETE PERMANENTLY"):
            db.table("trades").delete().eq("id", del_id).execute()
            st.success("Record eliminato.")
            time.sleep(1)
            st.rerun()

elif page == "⚙️ SETTINGS":
    st.title("System Configuration")
    st.write(f"Supabase Connection: Active")
    st.write(f"Project ID: aurjuibhbuinxzirpjkt")
    if st.button("Re-Sync Terminal"):
        st.cache_resource.clear()
        st.rerun()

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
    page_title="TRADECORE V15.0 | PROFESSIONAL TERMINAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom per look High-End
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono&display=swap');
    
    .main { background-color: #050708; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    div[data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #1f2328; }
    
    /* Glossy Metrics */
    .stMetric {
        background: linear-gradient(145deg, #0d1117, #161b22);
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    /* Calendario Cerchi Dinamici */
    .cal-wrapper { display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-start; }
    .cal-day {
        width: 60px; height: 60px; border-radius: 50%;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 700; font-size: 0.9em; transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .pnl-pos { background: linear-gradient(135deg, #238636 0%, #2ea043 100%); color: white; border: 2px solid #3fb950; box-shadow: 0 0 10px rgba(46, 160, 67, 0.3); }
    .pnl-neg { background: linear-gradient(135deg, #da3633 0%, #f85149 100%); color: white; border: 2px solid #ff7b72; box-shadow: 0 0 10px rgba(248, 81, 73, 0.3); }
    .pnl-neu { background-color: #161b22; color: #8b949e; border: 1px solid #30363d; }
    .pnl-sub { font-size: 0.6em; font-weight: 400; margin-top: 2px; font-family: 'JetBrains Mono'; }

    /* Estetica Input */
    .stTextInput input, .stNumberInput input, .stSelectbox div {
        background-color: #0d1117 !important; color: #00ff88 !important; border: 1px solid #30363d !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DATABASE CONNECTION (BLINDATA)
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
            # Riempimento colonne mancanti per vecchi record
            for c in ['setup', 'session', 'psychology', 'emotion', 'discipline', 'notes', 'contracts', 'direction', 'asset']:
                if c not in df.columns: df[c] = "N/A"
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore caricamento: {e}")
        return pd.DataFrame()

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>CORE V15</h2>", unsafe_allow_html=True)
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
    st.caption("Database: Connected")

df_main = load_data_vault()

# ==========================================
# 4. PAGINA: LOG ESECUZIONE (SETUP IERI)
# ==========================================

if st.form_submit_button("COMMIT TO VAULT"):
    # Calcoliamo la differenza di punti assoluta
    # Esempio: 18000 - 17930 = 70 punti
    point_diff = (exit_p - entry) if direction == "Long" else (entry - exit_p)
    
    # Calcolo Finale: Punti * Contratti * Valore per Punto
    # Assicurati che 'multiplier' sia 2 per MNQ o 5 per MES (non 0.02!)
    pnl_val = float(point_diff * contracts * multiplier)
    
    # Arrotondamento per evitare errori di virgola (es. 0.1400000001)
    pnl_val = round(pnl_val, 2)
    
    payload = {
        "asset": asset, 
        "direction": direction, 
        "entry_price": float(entry), 
        "exit_price": float(exit_p),
        "pnl": pnl_val, # Ora salva il valore corretto (es. -140.00)
        "setup": setup, 
        "session": session, 
        "exit_date": str(dt),
        "psychology": psy, 
        "emotion": emo, 
        "discipline": disc, 
        "notes": notes,
        "timeframe": tf, 
        "contracts": float(contracts)
    }
    
    try:
        db.table("trades").insert(payload).execute()
        st.success(f"✅ TRADE REGISTRATO: {pnl_val:,.2f} USD")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Errore: {e}")
# ==========================================
# 5. PAGINA: DASHBOARD ANALYTICS
# ==========================================
elif page == "📊 DASHBOARD":
    st.title("Market Analytics")
    if not df_main.empty:
        # Metriche
        net = df_main['pnl'].sum()
        wr = (len(df_main[df_main['pnl'] > 0]) / len(df_main)) * 100
        pf = abs(df_main[df_main['pnl'] > 0]['pnl'].sum() / df_main[df_main['pnl'] < 0]['pnl'].sum()) if any(df_main['pnl'] < 0) else 1
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("NET P&L", f"${net:,.2f}")
        c2.metric("WIN RATE", f"{wr:.1f}%")
        c3.metric("PROFIT FACTOR", f"{pf:.2f}")
        c4.metric("TRADES", len(df_main))

        # Equity Curve
        df_sorted = df_main.sort_values('exit_date')
        df_sorted['equity'] = df_sorted['pnl'].cumsum()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_sorted['exit_date'], y=df_sorted['equity'], fill='tozeroy', line=dict(color='#00ff88')))
        fig.update_layout(template="plotly_dark", title="Equity Growth")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nessun dato disponibile.")

# ==========================================
# 6. PAGINA: CALENDARIO P&L (CERCHI PIKKIT)
# ==========================================
elif page == "📅 CALENDARIO P&L":
    st.title("Monthly Performance Calendar")
    if not df_main.empty:
        df_main['d_only'] = df_main['exit_date'].dt.date
        daily_pnl = df_main.groupby('d_only')['pnl'].sum().to_dict()
        
        now = datetime.now()
        month_idx = st.selectbox("Seleziona Mese", range(1, 13), index=now.month-1)
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
        st.info("Logga il tuo primo trade per vedere il calendario.")

# ==========================================
# 7. PAGINA: PSICOLOGIA & QUANT
# ==========================================
elif page == "🧠 PSICOLOGIA":
    st.title("Behavioral Analysis")
    if not df_main.empty:
        col1, col2 = st.columns(2)
        fig1 = px.bar(df_main.groupby('emotion')['pnl'].sum().reset_index(), x='emotion', y='pnl', title="PnL vs Emotion", template="plotly_dark")
        col1.plotly_chart(fig1, use_container_width=True)
        fig2 = px.box(df_main, x='psychology', y='pnl', title="PnL vs Mindset", template="plotly_dark")
        col2.plotly_chart(fig2, use_container_width=True)

elif page == "📈 ANALISI STRATEGICA":
    st.title("Strategy Efficiency")
    if not df_main.empty:
        col1, col2 = st.columns(2)
        fig1 = px.pie(df_main, names='setup', values='pnl', title="Setup Distribution", hole=0.4)
        col1.plotly_chart(fig1, use_container_width=True)
        fig2 = px.bar(df_main.groupby('session')['pnl'].sum().reset_index(), x='session', y='pnl', title="PnL by Session")
        col2.plotly_chart(fig2, use_container_width=True)

# ==========================================
# 8. RISK CALCULATOR
# ==========================================
elif page == "💰 RISK CALCULATOR":
    st.title("Position Sizing")
    b = st.number_input("Account Balance", value=10000.0)
    rp = st.slider("Risk %", 0.1, 5.0, 1.0)
    sl = st.number_input("Stop Loss (Points)", value=20.0)
    vp = st.number_input("Point Value ($)", value=2.0)
    
    if sl > 0:
        risk_usd = b * (rp/100)
        size = risk_usd / (sl * vp)
        st.metric("Suggested Contracts", f"{size:.2f}")
        st.write(f"Rischio Totale: ${risk_usd:,.2f}")

# ==========================================
# 9. ARCHIVIO & SETTINGS
# ==========================================
elif page == "🗄️ ARCHIVIO DATI":
    st.title("Full Archive")
    if not df_main.empty:
        # Pulizia prima della visualizzazione per evitare crash
        df_view = df_main.copy()
        df_view = df_view.sort_values('exit_date', ascending=False)
        st.dataframe(df_view, use_container_width=True)
        
        st.divider()
        del_id = st.number_input("Delete ID", step=1)
        if st.button("DELETE PERMANENTLY"):
            db.table("trades").delete().eq("id", del_id).execute()
            st.success("Deleted.")
            st.rerun()

elif page == "⚙️ SETTINGS":
    st.title("Terminal Configuration")
    st.write(f"Supabase Status: Connected")
    st.write(f"Total Database Rows: {len(df_main)}")
    if st.button("Clear App Cache"):
        st.cache_resource.clear()
        st.rerun()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, date, timedelta
import calendar
import time

# --- 1. CONFIGURAZIONE SISTEMA ---
st.set_page_config(
    page_title="TRADECORE V11.0 | ULTIMATE TERMINAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CREDENZIALI E CONNESSIONE ---
# Sostituisci qui se non usi i Secrets di Streamlit
SUPABASE_URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"

@st.cache_resource
def init_db():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    db = init_db()
except Exception as e:
    st.error(f"Connessione fallita: {e}")
    st.stop()

# --- 3. ENGINE ESTETICO (CSS CUSTOM) ---
st.markdown("""
    <style>
    /* Global Styles */
    .main { background-color: #050708; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    div[data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #1f2328; }
    
    /* Glossy Metrics */
    .stMetric {
        background: linear-gradient(145deg, #0d1117, #161b22);
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* Calendario Pro */
    .calendar-day {
        width: 100%; aspect-ratio: 1/1; border-radius: 14px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1.2em; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
    }
    .calendar-day:hover { transform: translateY(-5px); filter: brightness(1.3); }
    .pnl-positive { background: linear-gradient(135deg, #238636 0%, #2ea043 100%); color: white; border: 1px solid #3fb950; box-shadow: 0 0 20px rgba(46, 160, 67, 0.4); }
    .pnl-negative { background: linear-gradient(135deg, #da3633 0%, #f85149 100%); color: white; border: 1px solid #ff7b72; box-shadow: 0 0 20px rgba(248, 81, 73, 0.4); }
    .pnl-neutral { background-color: #161b22; color: #8b949e; border: 1px solid #30363d; }
    .pnl-label { font-size: 0.65em; margin-top: 5px; font-weight: 400; font-family: 'JetBrains Mono', monospace; }

    /* Custom Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #1f6feb 0%, #0d419d 100%);
        color: white; border: none; border-radius: 10px; padding: 12px; font-weight: bold;
        transition: 0.4s; width: 100%;
    }
    .stButton>button:hover { box-shadow: 0 0 25px rgba(31, 111, 235, 0.5); transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# --- 4. DATA ENGINE ---
def get_vault_data():
    try:
        res = db.table("trades").select("*").order("exit_date").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date'])
            df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
            # Auto-Recovery per dati mancanti
            cols = ['asset', 'direction', 'setup', 'session', 'psychology', 'emotion', 'discipline', 'notes']
            for c in cols:
                if c not in df.columns: df[c] = "N/A"
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

def save_to_vault(payload):
    db.table("trades").insert(payload).execute()

# --- 5. LOGICA SIDEBAR ---
with st.sidebar:
    st.markdown("# TRADECORE `V11`")
    st.divider()
    page = st.radio("SISTEMA OPERATIVO", [
        "DASHBOARD ANALYTICS",
        "CALENDARIO P&L",
        "LOG ESECUZIONE",
        "VAULT PSICOLOGICO",
        "QUANTI ANALYSIS",
        "DATABASE STORICO",
        "API AUTOMATION"
    ])
    st.divider()
    st.info(f"Connesso a: {SUPABASE_URL.split('//')[1].split('.')[0]}")

df_main = get_vault_data()

# --- 6. PAGINE ---

if page == "DASHBOARD ANALYTICS":
    st.title("Market Intelligence Terminal")
    if not df_main.empty:
        # Calcoli Avanzati
        total_pnl = df_main['pnl'].sum()
        win_rate = (len(df_main[df_main['pnl'] > 0]) / len(df_main)) * 100
        avg_trade = df_main['pnl'].mean()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("NET PROFIT", f"${total_pnl:,.2f}")
        c2.metric("WIN RATE", f"{win_rate:.1f}%")
        c3.metric("EXPECTANCY", f"${avg_trade:,.2f}")
        c4.metric("MAX DD", f"-${abs(df_main['pnl'].min()):,.2f}")

        # Equity Curve
        df_main = df_main.sort_values('exit_date')
        df_main['equity'] = df_main['pnl'].cumsum()
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(x=df_main['exit_date'], y=df_main['equity'], fill='tozeroy', 
                                    line=dict(color='#00ff88', width=4), name="Equity Line"))
        fig_eq.update_layout(template="plotly_dark", height=500, margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig_eq, use_container_width=True)
    else:
        st.warning("Carica la prima operazione per sbloccare la dashboard.")

elif page == "CALENDARIO P&L":
    st.title("Visual Performance Calendar")
    if not df_main.empty:
        df_main['d_only'] = df_main['exit_date'].dt.date
        daily = df_main.groupby('d_only')['pnl'].sum().to_dict()
        
        now = datetime.now()
        cal = calendar.monthcalendar(now.year, now.month)
        
        st.subheader(f"{calendar.month_name[now.month]} {now.year}")
        h = st.columns(7)
        for i, d in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
            h[i].markdown(f"<center><small style='color:gray'>{d}</small></center>", unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    dt_obj = date(now.year, now.month, day)
                    p = daily.get(dt_obj, None)
                    cls = "pnl-neutral"
                    txt = ""
                    if p is not None:
                        cls = "pnl-positive" if p > 0 else "pnl-negative"
                        txt = f"{p:+.0f}"
                    cols[i].markdown(f'<div class="calendar-day {cls}">{day}<div class="pnl-label">{txt}</div></div>', unsafe_allow_html=True)
        st.write("")
    else:
        st.info("Nessun dato per generare il calendario.")

elif page == "LOG ESECUZIONE":
    st.title("Secure Execution Log")
    with st.form("trade_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            asset = st.text_input("Asset", "NAS100")
            side = st.selectbox("Side", ["Long", "Short"])
            size = st.number_input("Contracts", min_value=0.01)
        with col2:
            entry = st.number_input("Entry", format="%.5f")
            exit_p = st.number_input("Exit", format="%.5f")
            pt_val = st.number_input("Point Value", value=20.0)
        with col3:
            setup = st.selectbox("Setup", ["FVG Inversion", "Liquidity Sweep", "MSS", "Silver Bullet"])
            session = st.selectbox("Session", ["London", "NY Morning", "NY Afternoon"])
            exit_date = st.date_input("Date", date.today())
        
        st.divider()
        st.subheader("Psychology & Discipline")
        p1, p2, p3 = st.columns(3)
        mind = p1.select_slider("Mindset", ["Poor", "Neutral", "Focused", "Peak"])
        emo = p2.selectbox("Emotion", ["Calm", "Anxiety", "Fear", "Greed", "Patience"])
        disc = p3.radio("Discipline", ["Perfect", "Minor Violation", "Major Violation"])
        notes = st.text_area("Notes / Lessons")
        
        if st.form_submit_button("COMMIT TO VAULT"):
            pnl_calc = (exit_p - entry) * size * pt_val if side == "Long" else (entry - exit_p) * size * pt_val
            data = {
                "asset": asset, "direction": side, "entry_price": entry, "exit_price": exit_p,
                "pnl": pnl_calc, "setup": setup, "session": session, "exit_date": str(exit_date),
                "psychology": mind, "emotion": emo, "discipline": disc, "notes": notes
            }
            save_to_vault(data)
            st.success("Sincronizzazione completata.")
            time.sleep(1)
            st.rerun()

elif page == "VAULT PSICOLOGICO":
    st.title("Psychological Intelligence")
    if not df_main.empty:
        l1, l2 = st.columns(2)
        f_emo = px.bar(df_main.groupby('emotion')['pnl'].sum().reset_index(), x='emotion', y='pnl', 
                       title="PnL per Stato Emotivo", template="plotly_dark", color='pnl')
        l1.plotly_chart(f_emo, use_container_width=True)
        
        f_disc = px.box(df_main, x='discipline', y='pnl', title="Impatto della Disciplina", template="plotly_dark")
        l2.plotly_chart(f_disc, use_container_width=True)
        
        st.subheader("Mental Performance Heatmap")
        heatmap = df_main.groupby(['psychology', 'emotion'])['pnl'].mean().unstack().fillna(0)
        st.write(heatmap)

elif page == "QUANTI ANALYSIS":
    st.title("Quantitative Strategy Analysis")
    if not df_main.empty:
        q1, q2 = st.columns(2)
        f_setup = px.sunburst(df_main, path=['setup', 'direction'], values='pnl', title="Mappa Strategica PnL")
        q1.plotly_chart(f_setup, use_container_width=True)
        
        f_session = px.bar(df_main.groupby('session')['pnl'].sum().reset_index(), x='session', y='pnl', title="PnL per Sessione Oraria")
        q2.plotly_chart(f_session, use_container_width=True)

elif page == "DATABASE STORICO":
    st.title("Archive Records")
    st.dataframe(df_main.sort_values('exit_date', ascending=False), use_container_width=True)
    id_del = st.number_input("Elimina ID", step=1)
    if st.button("DELETE PERMANENTLY"):
        db.table("trades").delete().eq("id", id_del).execute()
        st.rerun()

elif page == "API AUTOMATION":
    st.title("External Integration")
    st.info("Modulo per il collegamento diretto a TradingView via Webhook.")
    st.code(f"WEBHOOK_URL: https://api.tradecore.io/v11/{SUPABASE_URL.split('//')[1].split('.')[0]}")
    st.text_input("Broker API Key (Encrypted)", type="password")
    st.button("Test Connection")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, date
import calendar
import time

# --- 1. CONFIGURAZIONE ULTIMATE ---
st.set_page_config(
    page_title="TRADECORE V10.0 | PROFESSIONAL TERMINAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ENGINE ESTETICO (CSS COMPLETO) ---
st.markdown("""
    <style>
    .main { background-color: #050708; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    div[data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #1f2328; }
    
    /* Metriche Dashboard */
    .stMetric {
        background-color: #0d1117;
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* Calendario Stile Screenshot */
    .calendar-day {
        width: 100%; aspect-ratio: 1/1; border-radius: 12px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1.1em; transition: 0.2s;
    }
    .pnl-positive { background: linear-gradient(145deg, #238636, #2ea043); color: white; border: 1px solid #3fb950; box-shadow: 0 0 15px rgba(46, 160, 67, 0.3); }
    .pnl-negative { background: linear-gradient(145deg, #da3633, #f85149); color: white; border: 1px solid #ff7b72; box-shadow: 0 0 15px rgba(248, 81, 73, 0.3); }
    .pnl-neutral { background-color: #161b22; color: #8b949e; border: 1px solid #30363d; }
    .pnl-label { font-size: 0.6em; margin-top: 4px; font-weight: 400; font-family: 'Monaco', monospace; }

    /* Form e Input */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #0d1117 !important; color: white !important; border: 1px solid #30363d !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONNESSIONE DATABASE ---
SUPABASE_URL = "IL_TUO_URL"
SUPABASE_KEY = "LA_TUA_KEY"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

db = init_connection()

# --- 4. ENGINE RECUPERO DATI (CON AUTO-RECOVERY) ---
def get_trades_from_vault():
    try:
        res = db.table("trades").select("*").order("exit_date").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            # Pulizia e Conversione
            df['exit_date'] = pd.to_datetime(df['exit_date'])
            df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
            
            # Recupero Colonne Mancanti (Dati di ieri)
            required_cols = ['asset', 'direction', 'setup', 'session', 'psychology', 'emotion', 'discipline', 'notes']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = "N/A (Legacy)"
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore Database: {e}")
        return pd.DataFrame()

# --- 5. LOGICA SIDEBAR ---
with st.sidebar:
    st.markdown("## TRADECORE `v10.0`")
    st.divider()
    page = st.radio("SISTEMA", [
        "📊 DASHBOARD CORE", 
        "📅 CALENDARIO P&L", 
        "📝 LOG ESECUZIONE", 
        "🧠 ANALISI PSICOLOGICA", 
        "📈 ANALISI AVANZATA", 
        "🗄️ DATABASE INTEGRALE",
        "⚙️ API & SETTINGS"
    ])
    st.divider()
    st.caption("Terminal Status: Operational")

df_main = get_trades_from_vault()

# --- 6. DASHBOARD CORE ---
if page == "📊 DASHBOARD CORE":
    st.title("Market Execution Dashboard")
    if not df_main.empty:
        # Calcolo Metriche
        total_pnl = df_main['pnl'].sum()
        win_rate = (len(df_main[df_main['pnl'] > 0]) / len(df_main)) * 100
        df_main = df_main.sort_values('exit_date')
        df_main['equity'] = df_main['pnl'].cumsum()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TOTAL P&L", f"${total_pnl:,.2f}")
        c2.metric("WIN RATE", f"{win_rate:.1f}%")
        c3.metric("TRADES", len(df_main))
        c4.metric("MAX DRAWDOWN", f"-${abs(df_main['pnl'].min()):,.2f}")

        # Equity Curve
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(x=df_main['exit_date'], y=df_main['equity'], fill='tozeroy', line=dict(color='#00ff88', width=3)))
        fig_equity.update_layout(template="plotly_dark", height=400, title="Equity Growth")
        st.plotly_chart(fig_equity, use_container_width=True)
    else:
        st.info("Database pronto. Inizia a inserire le operazioni per vedere le analisi.")

# --- 7. CALENDARIO P&L (STILE RICHIESTO) ---
elif page == "📅 CALENDARIO P&L":
    st.title("PnL Visual Calendar")
    if not df_main.empty:
        df_main['date_only'] = df_main['exit_date'].dt.date
        daily_pnl = df_main.groupby('date_only')['pnl'].sum().to_dict()
        
        now = datetime.now()
        cal = calendar.monthcalendar(now.year, now.month)
        
        st.markdown(f"### {calendar.month_name[now.month]} {now.year}")
        cols_h = st.columns(7)
        for i, d in enumerate(["LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"]):
            cols_h[i].markdown(f"<center><small>{d}</small></center>", unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    curr_d = date(now.year, now.month, day)
                    val = daily_pnl.get(curr_d, None)
                    style = "pnl-neutral"
                    lbl = ""
                    if val is not None:
                        style = "pnl-positive" if val > 0 else "pnl-negative"
                        lbl = f"{val:+.0f}"
                    cols[i].markdown(f'<div class="calendar-day {style}">{day}<div class="pnl-label">{lbl}</div></div>', unsafe_allow_html=True)
        st.write("")

# --- 8. LOG ESECUZIONE (PSICOLOGIA INCLUSA) ---
elif page == "📝 LOG ESECUZIONE":
    st.title("New Trade Entry")
    with st.form("main_entry", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        asset = c1.text_input("Asset", value="MNQ1!")
        direction = c2.selectbox("Side", ["Long", "Short"])
        size = c3.number_input("Lots", min_value=0.01)
        
        c4, c5, c6 = st.columns(3)
        entry = c4.number_input("Entry Price", format="%.5f")
        exit_p = c5.number_input("Exit Price", format="%.5f")
        pt_val = c6.number_input("Point Value", value=20.0)
        
        st.divider()
        st.subheader("Context & Psychology")
        c7, c8, c9 = st.columns(3)
        setup = c7.selectbox("Setup", ["FVG", "Liquidity Sweep", "MSS", "Silver Bullet"])
        session = c8.selectbox("Session", ["London", "NY Morning", "NY Afternoon"])
        exit_date = c9.date_input("Date", date.today())
        
        mindset = st.select_slider("Mindset", options=["Poor", "Neutral", "Focused", "Peak Performance"])
        emotion = st.selectbox("Primary Emotion", ["Calm", "Anxiety", "Fear", "Greed", "Patience"])
        discipline = st.radio("Did you follow the plan?", ["Yes", "No - FOMO", "No - Revenge", "No - Early Exit"])
        notes = st.text_area("Trade Review / Mistakes")
        
        if st.form_submit_button("SAVE TRADE"):
            pnl_val = (exit_p - entry) * size * pt_val if direction == "Long" else (entry - exit_p) * size * pt_val
            payload = {
                "asset": asset, "direction": direction, "entry_price": entry, "exit_price": exit_p,
                "pnl": pnl_val, "setup": setup, "session": session, "exit_date": str(exit_date),
                "psychology": mindset, "emotion": emotion, "discipline": discipline, "notes": notes
            }
            db.table("trades").insert(payload).execute()
            st.success("Trade salvato.")
            time.sleep(1)
            st.rerun()

# --- 9. ANALISI PSICOLOGICA & AVANZATA (DOPPIA PROFONDITA') ---
elif page == "🧠 ANALISI PSICOLOGICA":
    st.title("Trading Psychology Insights")
    if not df_main.empty:
        col1, col2 = st.columns(2)
        fig1 = px.bar(df_main.groupby('emotion')['pnl'].sum().reset_index(), x='emotion', y='pnl', title="PnL vs Emotion", template="plotly_dark")
        col1.plotly_chart(fig1, use_container_width=True)
        fig2 = px.box(df_main, x='discipline', y='pnl', title="PnL Distribution vs Discipline", template="plotly_dark")
        col2.plotly_chart(fig2, use_container_width=True)

elif page == "📈 ANALISI AVANZATA":
    st.title("Advanced Quantitative Analysis")
    if not df_main.empty:
        col1, col2 = st.columns(2)
        fig3 = px.pie(df_main, names='setup', values='pnl', title="PnL by Setup Strategy", template="plotly_dark")
        col1.plotly_chart(fig3, use_container_width=True)
        fig4 = px.bar(df_main.groupby('session')['pnl'].sum().reset_index(), x='session', y='pnl', title="PnL by Session", template="plotly_dark")
        col2.plotly_chart(fig4, use_container_width=True)

# --- 10. DATABASE INTEGRALE ---
elif page == "🗄️ DATABASE INTEGRALE":
    st.title("Full Archive Vault")
    st.dataframe(df_main.sort_values('exit_date', ascending=False), use_container_width=True)
    id_del = st.number_input("Delete ID", step=1)
    if st.button("DELETE PERMANENTLY"):
        db.table("trades").delete().eq("id", id_del).execute()
        st.rerun()

# --- 11. API & SETTINGS ---
elif page == "⚙️ API & SETTINGS":
    st.title("Automation & Connection")
    st.info("Integrazione API MetaTrader/TradingView prevista per il Giorno 5.")

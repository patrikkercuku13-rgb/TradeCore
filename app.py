import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, date, timedelta
import calendar
import time

# --- CONFIGURAZIONE DI ALTO LIVELLO ---
st.set_page_config(
    page_title="TRADECORE V9.0 | PROFESSIONAL TERMINAL",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ENGINE ESTETICO (CSS CUSTOM) ---
st.markdown("""
    <style>
    /* Sfondo e Testi */
    .main { background-color: #050708; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    
    /* Sidebar Design */
    div[data-testid="stSidebar"] {
        background-color: #0a0c10;
        border-right: 1px solid #1f2328;
    }

    /* Container delle Metriche */
    .stMetric {
        background-color: #0d1117;
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* Calendario PnL Professional */
    .calendar-container { padding: 10px; background: #0d1117; border-radius: 15px; border: 1px solid #30363d; }
    .calendar-day {
        width: 100%; aspect-ratio: 1/1; border-radius: 12px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1.2em; transition: all 0.2s ease-in-out;
    }
    .calendar-day:hover { transform: scale(1.05); filter: brightness(1.2); }
    .pnl-positive { background: linear-gradient(145deg, #238636, #2ea043); color: white; border: 1px solid #3fb950; box-shadow: 0 0 15px rgba(46, 160, 67, 0.4); }
    .pnl-negative { background: linear-gradient(145deg, #da3633, #f85149); color: white; border: 1px solid #ff7b72; box-shadow: 0 0 15px rgba(248, 81, 73, 0.4); }
    .pnl-neutral { background-color: #161b22; color: #8b949e; border: 1px solid #30363d; }
    .pnl-label { font-size: 0.6em; font-family: 'Monaco', monospace; margin-top: 4px; font-weight: 400; }
    
    /* Bottoni e Input */
    .stButton>button {
        width: 100%; border-radius: 8px; background: linear-gradient(90deg, #1f6feb, #0d419d);
        color: white; font-weight: bold; border: none; padding: 10px; transition: 0.3s;
    }
    .stButton>button:hover { box-shadow: 0 0 20px rgba(31, 111, 235, 0.6); transform: translateY(-2px); }
    </style>
""", unsafe_allow_html=True)

# --- CONNESSIONE E GESTIONE DATI ---
SUPABASE_URL = "LA_TUA_URL"
SUPABASE_KEY = "LA_TUA_KEY"

@st.cache_resource
def init_connection():
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Errore di connessione al Database: {e}")
        return None

db = init_connection()

def get_trades_from_vault():
    try:
        res = db.table("trades").select("*").order("exit_date").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date'])
            df['pnl'] = df['pnl'].astype(float)
        return df
    except:
        return pd.DataFrame()

# --- MODULI ANALITICI ---

def calculate_advanced_metrics(df):
    if df.empty: return {}
    total_trades = len(df)
    winning_trades = len(df[df['pnl'] > 0])
    losing_trades = len(df[df['pnl'] < 0])
    win_rate = (winning_trades / total_trades) * 100
    
    gross_profit = df[df['pnl'] > 0]['pnl'].sum()
    gross_loss = abs(df[df['pnl'] < 0]['pnl'].sum())
    profit_factor = gross_profit / gross_loss if gross_loss != 0 else gross_profit
    
    avg_win = df[df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
    avg_loss = df[df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
    risk_reward_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
    
    df = df.sort_values('exit_date')
    df['equity'] = df['pnl'].cumsum()
    df['peak'] = df['equity'].cummax()
    df['drawdown'] = df['peak'] - df['equity']
    max_dd = df['drawdown'].max()
    
    return {
        "wr": win_rate, "pf": profit_factor, "rr": risk_reward_ratio,
        "max_dd": max_dd, "avg_trade": df['pnl'].mean(), "total_pnl": df['pnl'].sum()
    }

# --- NAVIGATION ---
with st.sidebar:
    st.markdown("## TRADECORE `v9.0`")
    st.divider()
    page = st.radio("SISTEMA", [
        "📊 DASHBOARD CORE", 
        "📅 CALENDARIO PERFORMANCE", 
        "📝 ESECUZIONE TRADE", 
        "🧠 ANALISI PSICOLOGICA", 
        "📈 ANALISI AVANZATA", 
        "🗄️ DATABASE INTEGRALE",
        "⚙️ API & SETTINGS"
    ])
    st.divider()
    if db: st.success("Database Connection: ACTIVE")
    else: st.error("Database Connection: OFFLINE")

df_main = get_trades_from_vault()

# --- 1. DASHBOARD CORE ---
if page == "📊 DASHBOARD CORE":
    st.title("Market Execution Terminal")
    if not df_main.empty:
        m = calculate_advanced_metrics(df_main)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TOTAL P&L", f"${m['total_pnl']:,.2f}")
        c2.metric("WIN RATE", f"{m['wr']:.1f}%")
        c3.metric("PROFIT FACTOR", f"{m['pf']:.2f}")
        c4.metric("MAX DRAWDOWN", f"-${m['max_dd']:,.2f}")

        # Equity Curve Principale
        st.subheader("Accumulated Performance")
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            x=df_main['exit_date'], y=df_main['equity'],
            fill='tozeroy', line=dict(color='#00ff88', width=3),
            name="Equity"
        ))
        fig_equity.update_layout(template="plotly_dark", height=450, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_equity, use_container_width=True)
    else:
        st.info("Nessun dato presente. Inizia caricando un'operazione nel Log Esecuzione.")

# --- 2. CALENDARIO PERFORMANCE ---
elif page == "📅 CALENDARIO PERFORMANCE":
    st.title("Interactive PnL Calendar")
    if not df_main.empty:
        df_main['date_only'] = df_main['exit_date'].dt.date
        daily_pnl = df_main.groupby('date_only')['pnl'].sum().to_dict()
        
        # Selezione Mese
        now = datetime.now()
        col_m1, col_m2 = st.columns([1, 4])
        sel_month = col_m1.selectbox("Mese", list(range(1, 13)), index=now.month-1)
        
        cal = calendar.monthcalendar(now.year, sel_month)
        st.markdown(f"### {calendar.month_name[sel_month]} {now.year}")
        
        days_header = st.columns(7)
        for i, d in enumerate(["LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"]):
            days_header[i].markdown(f"<center><small>{d}</small></center>", unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    curr_d = date(now.year, sel_month, day)
                    val = daily_pnl.get(curr_d, None)
                    style = "pnl-neutral"
                    lbl = ""
                    if val is not None:
                        style = "pnl-positive" if val > 0 else "pnl-negative"
                        lbl = f"{val:+.0f}"
                    cols[i].markdown(f'<div class="calendar-day {style}">{day}<div class="pnl-label">{lbl}</div></div>', unsafe_allow_html=True)
            st.write("")
    else:
        st.warning("Dati insufficienti per generare il calendario.")

# --- 3. ESECUZIONE TRADE ---
elif page == "📝 ESECUZIONE TRADE":
    st.title("Execution Entry Vault")
    with st.form("trade_entry_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            asset = st.text_input("Asset Symbol", "MNQ1!")
            direction = st.selectbox("Side", ["Long", "Short"])
            size = st.number_input("Lots/Contracts", min_value=0.01, step=0.01)
        with f2:
            entry = st.number_input("Entry Price", format="%.5f")
            exit_p = st.number_input("Exit Price", format="%.5f")
            pt_val = st.number_input("Multiplier (Point Value)", value=20.0)
        with f3:
            setup = st.selectbox("Strategy Setup", ["FVG Inversion", "Silver Bullet", "Liquidity Sweep", "MSS/BMS", "Turtle Soup"])
            session = st.selectbox("Market Session", ["London Open", "NY Morning", "NY Afternoon", "Asia"])
            exit_date_sel = st.date_input("Execution Date", date.today())

        st.divider()
        st.subheader("Psychological Logging")
        p1, p2, p3 = st.columns(3)
        mindset = p1.select_slider("Pre-Trade Mindset", options=["Low Focus", "Neutral", "Good", "High Flow", "Over-Excited"])
        emotion = p2.selectbox("Primary Emotion", ["Calm", "Anxiety", "Greed", "Fear", "Patience"])
        discipline = p3.radio("Discipline Score", ["Perfect Execution", "Minor Error", "Major Violation (FOMO/Revenge)"])
        
        notes = st.text_area("Execution Notes (Why did you take this trade?)")
        
        if st.form_submit_button("COMMIT TO PERMANENT RECORD"):
            # Calcolo PnL
            raw_pnl = (exit_p - entry) * size * pt_val if direction == "Long" else (entry - exit_p) * size * pt_val
            payload = {
                "asset": asset, "direction": direction, "entry_price": entry, "exit_price": exit_p,
                "pnl": raw_pnl, "setup": setup, "session": session, "exit_date": str(exit_date_sel),
                "psychology": mindset, "emotion": emotion, "discipline": discipline, "notes": notes
            }
            db.table("trades").insert(payload).execute()
            st.success("Operazione registrata con successo nel database.")
            time.sleep(1)
            st.rerun()

# --- 4. ANALISI PSICOLOGICA ---
elif page == "🧠 ANALISI PSICOLOGICA":
    st.title("Trading Psychology Intelligence")
    if not df_main.empty:
        col_psy1, col_psy2 = st.columns(2)
        
        # Correlazione Emozione / PnL
        fig_emo = px.bar(df_main.groupby('emotion')['pnl'].sum().reset_index(), 
                         x='emotion', y='pnl', color='pnl', title="PnL by Primary Emotion",
                         template="plotly_dark", color_continuous_scale="RdYlGn")
        col_psy1.plotly_chart(fig_emo, use_container_width=True)
        
        # Impatto della Disciplina
        fig_disc = px.box(df_main, x='discipline', y='pnl', color='discipline',
                          title="Profit Distribution by Discipline", template="plotly_dark")
        col_psy2.plotly_chart(fig_disc, use_container_width=True)
        
        # Mindset Performance Heatmap
        st.subheader("Mindset vs Success Rate")
        mindset_perf = df_main.groupby('psychology')['pnl'].agg(['sum', 'count']).reset_index()
        st.dataframe(mindset_perf, use_container_width=True)
    else:
        st.info("Logga almeno 5 trade per vedere i pattern psicologici.")

# --- 5. ANALISI AVANZATA ---
elif page == "📈 ANALISI AVANZATA":
    st.title("Advanced Quantitative Analysis")
    if not df_main.empty:
        tab1, tab2, tab3 = st.tabs(["Strategy Efficiency", "Time Analysis", "Risk Analysis"])
        
        with tab1:
            col_st1, col_st2 = st.columns(2)
            fig_setup = px.sunburst(df_main, path=['setup', 'direction'], values='pnl', 
                                    color='pnl', color_continuous_scale='RdYlGn', title="Strategy Performance Map")
            col_st1.plotly_chart(fig_setup, use_container_width=True)
            
            # Win Rate per Setup
            setup_wr = df_main.groupby('setup').apply(lambda x: (len(x[x['pnl']>0])/len(x))*100).reset_index(name='Win Rate %')
            col_st2.bar_chart(setup_wr.set_index('setup'))

        with tab2:
            fig_session = px.bar(df_main.groupby('session')['pnl'].sum().reset_index(), 
                                 x='session', y='pnl', title="Profit by Market Session", template="plotly_dark")
            st.plotly_chart(fig_session, use_container_width=True)

        with tab3:
            # Calcolo Drawdown
            df_main['peak'] = df_main['equity'].cummax()
            df_main['drawdown_val'] = df_main['peak'] - df_main['equity']
            fig_dd = px.area(df_main, x='exit_date', y='drawdown_val', title="Drawdown Exposure Over Time",
                             color_discrete_sequence=['#ff4b4b'], template="plotly_dark")
            st.plotly_chart(fig_dd, use_container_width=True)

# --- 6. DATABASE INTEGRALE ---
elif page == "🗄️ DATABASE INTEGRALE":
    st.title("Portfolio Database Vault")
    st.markdown("Visualizzazione cruda di tutti i record storici salvati nel cloud.")
    
    # Filtri
    search = st.text_input("Filtra per Asset (es. NQ)")
    if search:
        df_display = df_main[df_main['asset'].str.contains(search, case=False)]
    else:
        df_display = df_main
        
    st.dataframe(df_display.sort_values('exit_date', ascending=False), use_container_width=True)
    
    st.divider()
    st.subheader("Admin Operations")
    id_to_del = st.number_input("ID del record da eliminare", step=1)
    if st.button("ELIMINA RECORD PERMANENTEMENTE"):
        db.table("trades").delete().eq("id", id_to_del).execute()
        st.warning(f"Record {id_to_del} rimosso. Ricaricando...")
        time.sleep(1)
        st.rerun()

# --- 7. SETTINGS API ---
elif page == "⚙️ API & SETTINGS":
    st.title("Terminal Configuration")
    col_set1, col_set2 = st.columns(2)
    with col_set1:
        st.subheader("Broker API (Coming Soon)")
        st.text_input("API Access Key", type="password")
        st.text_input("API Secret Key", type="password")
        st.selectbox("Data Provider", ["MetaTrader 5", "Interactive Brokers", "Rithmic", "Tradovate"])
    with col_set2:
        st.subheader("Webhook Automation")
        st.code("https://api.tradecore.io/v9/webhook/your-unique-id")
        st.info("Usa questo URL nei tuoi Alert di TradingView per loggare i trade automaticamente.")

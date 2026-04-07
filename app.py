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
# 1. CONFIGURAZIONE CORE & ESTETICA (CSS)
# ==========================================
st.set_page_config(
    page_title="TRADECORE V13.0 | THE VAULT",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Design futuristico stile Bloomberg/Terminal
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&display=swap');
    
    .main { background-color: #050708; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    div[data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #1f2328; }
    
    /* Metriche High-End */
    .stMetric {
        background: linear-gradient(145deg, #0d1117, #161b22);
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    }
    
    /* Calendario Cerchi (Stile Richiesto) */
    .calendar-container { padding: 20px; }
    .calendar-day {
        width: 100%; aspect-ratio: 1/1; border-radius: 50%;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1.15em; transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer; position: relative;
    }
    .calendar-day:hover { transform: scale(1.1); filter: brightness(1.2); z-index: 10; }
    .pnl-positive { background: linear-gradient(135deg, #238636 0%, #2ea043 100%); color: white; border: 2px solid #3fb950; box-shadow: 0 0 15px rgba(46, 160, 67, 0.4); }
    .pnl-negative { background: linear-gradient(135deg, #da3633 0%, #f85149 100%); color: white; border: 2px solid #ff7b72; box-shadow: 0 0 15px rgba(248, 81, 73, 0.4); }
    .pnl-neutral { background-color: #161b22; color: #8b949e; border: 1px solid #30363d; }
    .pnl-label { font-size: 0.55em; margin-top: 3px; font-weight: 400; font-family: 'JetBrains Mono', monospace; }

    /* Input Styling */
    .stTextInput input, .stNumberInput input, .stSelectbox div {
        background-color: #0d1117 !important; color: #00ff88 !important; border: 1px solid #30363d !important;
    }
    
    /* Bottoni */
    .stButton>button {
        background: linear-gradient(90deg, #1f6feb 0%, #0d419d 100%);
        color: white; border: none; border-radius: 8px; font-weight: bold; height: 50px;
        box-shadow: 0 4px 15px rgba(31, 111, 235, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONNESSIONE & DATABASE ENGINE
# ==========================================
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"

@st.cache_resource
def connect_vault():
    return create_client(URL, KEY)

try:
    client = connect_vault()
except:
    st.error("DATABASE OFFLINE - Controlla la connessione")

def get_full_data():
    try:
        res = client.table("trades").select("*").order("exit_date").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date'])
            df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
            # Fix per colonne mancanti (legacy data)
            cols = ['asset', 'direction', 'setup', 'session', 'psychology', 'emotion', 'discipline', 'notes', 'timeframe', 'contracts']
            for c in cols:
                if c not in df.columns: df[c] = "N/A"
            return df
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"Sincronizzazione fallita: {e}")
        return pd.DataFrame()

# ==========================================
# 3. LOGICA DI CALCOLO AVANZATA
# ==========================================
def calculate_performance(df):
    if df.empty: return None
    
    wins = df[df['pnl'] > 0]['pnl']
    losses = df[df['pnl'] < 0]['pnl']
    
    total_net = df['pnl'].sum()
    win_rate = (len(wins) / len(df)) * 100
    profit_factor = wins.sum() / abs(losses.sum()) if not losses.empty else wins.sum()
    avg_win = wins.mean() if not wins.empty else 0
    avg_loss = losses.mean() if not losses.empty else 0
    expectancy = (win_rate/100 * avg_win) + ((1-win_rate/100) * avg_loss)
    
    # Drawdown
    df['equity'] = df['pnl'].cumsum()
    df['peak'] = df['equity'].cummax()
    df['dd'] = df['peak'] - df['equity']
    max_dd = df['dd'].max()
    
    return {
        "net": total_net, "wr": win_rate, "pf": profit_factor,
        "expectancy": expectancy, "max_dd": max_dd, "trades": len(df)
    }

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #00ff88;'>TRADECORE V13</h1>", unsafe_allow_html=True)
    st.divider()
    page = st.radio("SISTEMA OPERATIVO", [
        "📊 DASHBOARD ANALYTICS",
        "📅 CALENDARIO P&L",
        "📝 LOG ESECUZIONE",
        "🧠 PSICOLOGIA & DIARIO",
        "📈 STRATEGY QUANT",
        "💰 RISK MANAGEMENT",
        "🗄️ ARCHIVIO DATABASE",
        "⚙️ TERMINAL SETTINGS"
    ])
    st.divider()
    st.caption("Server Status: Secured")
    st.caption(f"Ref: {URL.split('//')[1].split('.')[0]}")

df_main = get_full_data()

# ==========================================
# 5. PAGINA: DASHBOARD ANALYTICS
# ==========================================
if page == "📊 DASHBOARD ANALYTICS":
    st.title("Market Execution Intelligence")
    if not df_main.empty:
        m = calculate_performance(df_main)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("TOTAL NET PROFIT", f"${m['net']:,.2f}")
        c2.metric("WIN RATE", f"{m['wr']:.1f}%")
        c3.metric("PROFIT FACTOR", f"{m['pf']:.2f}")
        c4.metric("MAX DRAWDOWN", f"-${m['max_dd']:,.2f}")

        # Grafico Equity Curve
        st.subheader("Accumulated Performance Line")
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=df_main['exit_date'], y=df_main['equity'],
            fill='tozeroy', line=dict(color='#00ff88', width=3),
            hovertemplate="Data: %{x}<br>Equity: $%{y:,.2f}<extra></extra>"
        ))
        fig_eq.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig_eq, use_container_width=True)
        
        # Metriche Secondarie
        st.divider()
        sc1, sc2, sc3 = st.columns(3)
        sc1.write(f"**Expectancy:** ${m['expectancy']:,.2f} per trade")
        sc2.write(f"**Total Volume:** {df_main['contracts'].astype(float).sum():,.2f} Units")
        sc3.write(f"**Best Trade:** ${df_main['pnl'].max():,.2f}")
    else:
        st.info("In attesa di dati... Inserisci il primo trade nel Log Esecuzione.")

# ==========================================
# 6. PAGINA: CALENDARIO P&L
# ==========================================
elif page == "📅 CALENDARIO P&L":
    st.title("Performance Visualization")
    if not df_main.empty:
        df_main['d_only'] = df_main['exit_date'].dt.date
        daily_sum = df_main.groupby('d_only')['pnl'].sum().to_dict()
        
        now = datetime.now()
        col_m1, col_m2 = st.columns([2, 5])
        month_idx = col_m1.selectbox("Seleziona Mese", range(1, 13), index=now.month-1)
        
        cal = calendar.monthcalendar(now.year, month_idx)
        st.subheader(f"{calendar.month_name[month_idx]} {now.year}")
        
        # Header Giorni
        days_header = st.columns(7)
        for i, d in enumerate(["LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"]):
            days_header[i].markdown(f"<center><small style='color: #8b949e;'>{d}</small></center>", unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day != 0:
                    dt = date(now.year, month_idx, day)
                    val = daily_sum.get(dt, None)
                    
                    bg_style = "pnl-neutral"
                    lbl = ""
                    if val is not None:
                        bg_style = "pnl-positive" if val > 0 else "pnl-negative"
                        lbl = f"{val:+.0f}"
                    
                    cols[i].markdown(f"""
                        <div class="calendar-day {bg_style}">
                            {day}
                            <div class="pnl-label">{lbl}</div>
                        </div>
                    """, unsafe_allow_html=True)
        st.write("")
    else:
        st.warning("Database vuoto.")

# ==========================================
# 7. PAGINA: LOG ESECUZIONE (RIPRISTINATO COMPLETO)
# ==========================================
elif page == "📝 LOG ESECUZIONE":
    st.title("Execution Entry Terminal")
    with st.form("heavy_trade_form", clear_on_submit=True):
        # Sezione 1: Asset e Direzione
        st.subheader("1. Market Data")
        r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
        asset = r1_c1.selectbox("Asset Class", ["MNQ (Nasdaq)", "MES (S&P500)", "MYM (Dow)", "M2K (Russell)", "BTC/USD", "EUR/USD", "GOLD"])
        direction = r1_c2.radio("Direction", ["Long", "Short"], horizontal=True)
        contracts = r1_c3.number_input("Units / Contracts", value=1.0, step=0.1)
        multiplier = r1_c4.number_input("Point Value ($)", value=2.0)

        # Sezione 2: Prezzi e Date
        st.subheader("2. Prices & Execution")
        r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
        entry_p = r2_c1.number_input("Entry Price", format="%.5f")
        exit_p = r2_c2.number_input("Exit Price", format="%.5f")
        exit_date_val = r2_c3.date_input("Exit Date", date.today())
        session = r2_c4.selectbox("Session", ["Asia", "London Open", "NY Morning", "NY Lunch", "NY Afternoon"])

        # Sezione 3: Strategia (Ieri)
        st.subheader("3. Strategy & Technicals")
        r3_c1, r3_c2, r3_c3 = st.columns(3)
        setup = r3_c1.selectbox("Setup Primario", [
            "FVG Inversion", "Liquidity Sweep", "MSS / Shift", "Silver Bullet", 
            "Unicorn", "Turtle Soup", "Order Block Rejection", "Breaker Block"
        ])
        tf = r3_c2.selectbox("Timeframe", ["1s", "15s", "1m", "5m", "15m", "1h", "4h", "D"])
        rr = r3_c3.number_input("Planned R:R", value=2.0)

        # Sezione 4: Psicologia
        st.subheader("4. Psychological Review")
        r4_c1, r4_c2, r4_c3 = st.columns(3)
        psy = r4_c1.select_slider("Mindset", ["Tired", "Anxious", "Neutral", "Focused", "Flow"])
        emo = r4_c2.selectbox("Dominant Emotion", ["Calm", "FOMO", "Greed", "Patience", "Fear", "Revenge"])
        disc = r4_c3.radio("Discipline", ["Perfect", "Minor Violation", "Major Violation"])
        
        notes = st.text_area("Trade Journal & Lessons Learned")

        if st.form_submit_button("LOCK TRADE INTO VAULT"):
            # Calcolo PnL Matematico
            pnl_res = (exit_p - entry_p) * contracts * multiplier if direction == "Long" else (entry_p - exit_p) * contracts * multiplier
            
            payload = {
                "asset": asset, "direction": direction, "entry_price": entry_p, "exit_price": exit_p,
                "pnl": pnl_res, "setup": setup, "session": session, "exit_date": str(exit_date_val),
                "psychology": psy, "emotion": emo, "discipline": disc, "notes": notes,
                "timeframe": tf, "contracts": contracts
            }
            
            try:
                client.table("trades").insert(payload).execute()
                st.success(f"Trade registrato! PnL: ${pnl_res:,.2f}")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"ERRORE: Controlla se le colonne esistono su Supabase. Dettaglio: {e}")

# ==========================================
# 8. PAGINA: PSICOLOGIA & ANALISI AVANZATA
# ==========================================
elif page == "🧠 PSICOLOGIA & DIARIO":
    st.title("Trading Psychology Intelligence")
    if not df_main.empty:
        col_p1, col_p2 = st.columns(2)
        
        # Analisi Emozioni
        fig_emo = px.bar(df_main.groupby('emotion')['pnl'].sum().reset_index(), 
                         x='emotion', y='pnl', color='pnl', title="PnL per Emozione Dominante", template="plotly_dark")
        col_p1.plotly_chart(fig_emo, use_container_width=True)
        
        # Analisi Disciplina
        fig_disc = px.pie(df_main, names='discipline', values='pnl', title="Profitto per Livello di Disciplina", template="plotly_dark", hole=0.5)
        col_p2.plotly_chart(fig_disc, use_container_width=True)
        
        st.divider()
        st.subheader("Mental Health Heatmap")
        st.write("Le tue performance basate sul mindset pre-trade:")
        psy_perf = df_main.groupby('psychology')['pnl'].agg(['sum', 'count', 'mean']).reset_index()
        st.dataframe(psy_perf, use_container_width=True)
    else:
        st.info("Nessun dato psicologico disponibile.")

elif page == "📈 STRATEGY QUANT":
    st.title("Quantitative Strategy Analysis")
    if not df_main.empty:
        q1, q2 = st.columns(2)
        
        # Setup Efficiency
        fig_setup = px.sunburst(df_main, path=['setup', 'direction'], values='pnl', 
                                color='pnl', color_continuous_scale='RdYlGn', title="Efficiency Map")
        q1.plotly_chart(fig_setup, use_container_width=True)
        
        # Session Analytics
        fig_sess = px.bar(df_main.groupby('session')['pnl'].sum().reset_index(), 
                          x='session', y='pnl', color='pnl', title="Profitto per Sessione di Mercato")
        q2.plotly_chart(fig_sess, use_container_width=True)

# ==========================================
# 9. PAGINA: RISK MANAGEMENT
# ==========================================
elif page == "💰 RISK MANAGEMENT":
    st.title("Position Sizing & Risk Control")
    c_r1, c_r2 = st.columns(2)
    
    with c_r1:
        balance = st.number_input("Account Balance ($)", value=10000.0)
        risk_perc = st.slider("Risk per Trade (%)", 0.1, 5.0, 1.0)
        risk_usd = balance * (risk_perc / 100)
        st.metric("Risk Amount", f"${risk_usd:,.2f}")
    
    with c_r2:
        stop_pts = st.number_input("Stop Loss Points", value=20.0)
        val_point = st.number_input("Contract Value per Point ($)", value=2.0)
        
        if stop_pts > 0:
            suggested_size = risk_usd / (stop_pts * val_point)
            st.metric("Suggested Contracts", f"{suggested_size:.2f}")
            st.warning(f"Usa massimo {int(suggested_size)} contratti per rispettare il {risk_perc}% di rischio.")

# ==========================================
# 10. ARCHIVIO & SETTINGS
# ==========================================
elif page == "🗄️ ARCHIVIO DATABASE":
    st.title("Full Archive Vault")
    st.dataframe(df_main.sort_values('exit_date', ascending=False), use_container_width=True)
    
    st.divider()
    id_del = st.number_input("Inserisci ID Trade per eliminazione", step=1)
    if st.button("ELIMINA RECORD DEFINITIVAMENTE"):
        client.table("trades").delete().eq("id", id_del).execute()
        st.success(f"Trade {id_del} eliminato.")
        time.sleep(1)
        st.rerun()

elif page == "⚙️ TERMINAL SETTINGS":
    st.title("System Configuration")
    st.write(f"**Connected to:** {URL}")
    st.write(f"**API Status:** Active")
    st.write(f"**Rows in DB:** {len(df_main)}")
    if st.button("Re-Sync Database"):
        st.cache_resource.clear()
        st.rerun()

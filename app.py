import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from supabase import create_client, Client
from datetime import datetime, date, timedelta
import calendar
import time

# --- 1. SETUP AMBIENTE ---
st.set_page_config(page_title="TRADECORE V12.0 | PROFESSIONAL", layout="wide", initial_sidebar_state="expanded")

SUPABASE_URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"

@st.cache_resource
def init_db():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

db = init_db()

# --- 2. ENGINE ESTETICO AVANZATO ---
st.markdown("""
    <style>
    .main { background-color: #050708; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    div[data-testid="stSidebar"] { background-color: #0a0c10; border-right: 1px solid #1f2328; }
    
    /* Container Dashboard */
    .stMetric {
        background: linear-gradient(145deg, #0d1117, #161b22);
        border: 1px solid #30363d;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }

    /* Calendario Pro (Stile Richiesto) */
    .calendar-day {
        width: 100%; aspect-ratio: 1/1; border-radius: 14px;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1.1em; transition: 0.2s;
    }
    .pnl-positive { background: linear-gradient(135deg, #238636 0%, #2ea043 100%); color: white; border: 1px solid #3fb950; }
    .pnl-negative { background: linear-gradient(135deg, #da3633 0%, #f85149 100%); color: white; border: 1px solid #ff7b72; }
    .pnl-neutral { background-color: #161b22; color: #8b949e; border: 1px solid #30363d; }
    .pnl-label { font-size: 0.6em; margin-top: 4px; font-weight: 400; font-family: 'Courier New', monospace; }

    /* Input Fields */
    input { background-color: #0d1117 !important; color: white !important; border: 1px solid #30363d !important; border-radius: 8px !important; }
    .stSelectbox div { background-color: #0d1117 !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. GESTIONE DATI ---
def fetch_vault():
    try:
        res = db.table("trades").select("*").order("exit_date").execute()
        df = pd.DataFrame(res.data)
        if not df.empty:
            df['exit_date'] = pd.to_datetime(df['exit_date'])
            df['pnl'] = pd.to_numeric(df['pnl'], errors='coerce').fillna(0)
            return df
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- 4. INTERFACCIA E NAVIGAZIONE ---
with st.sidebar:
    st.markdown("## TRADECORE `V12`")
    st.divider()
    page = st.radio("SISTEMA", [
        "📊 DASHBOARD", "📅 CALENDARIO P&L", "📝 LOG ESECUZIONE", 
        "📈 ANALISI TECNICA", "🧠 PSICOLOGIA", "🗄️ DATABASE", "⚙️ SETTINGS"
    ])

df_main = fetch_vault()

# --- 5. LOG ESECUZIONE (RIPRISTINATO E POTENZIATO) ---
if page == "📝 LOG ESECUZIONE":
    st.title("Secure Execution Vault")
    st.markdown("Inserisci i dettagli millimetrici dell'operazione.")

    with st.form("ultra_trade_form", clear_on_submit=True):
        # Prima Riga: Dati Mercato
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            asset = st.selectbox("Asset Class", ["MNQ (Nasdaq)", "MES (S&P500)", "MYM (Dow)", "M2K (Russell)", "BTC/USD", "EUR/USD", "GOLD"])
            side = st.radio("Direction", ["Long", "Short"], horizontal=True)
        with c2:
            entry = st.number_input("Entry Price", format="%.5f", help="Prezzo di esecuzione")
            exit_p = st.number_input("Exit Price", format="%.5f", help="Prezzo di chiusura")
        with c3:
            contracts = st.number_input("Contracts/Lots", min_value=0.01, step=0.01, value=1.0)
            multiplier = st.number_input("Point Value ($)", value=2.0, help="Es: 2$ per MNQ, 5$ per MES")
        with c4:
            exit_date = st.date_input("Exit Date", date.today())
            session = st.selectbox("Market Session", ["Asia", "London Open", "NY Morning", "NY Lunch", "NY Afternoon", "After Hours"])

        st.divider()
        
        # Seconda Riga: Analisi Tecnica (Dettagliata come ieri)
        st.subheader("Technical Setup & Confluences")
        s1, s2, s3 = st.columns(3)
        with s1:
            primary_setup = st.selectbox("Primary Setup", [
                "FVG Inversion", "Liquidity Sweep (Internal)", "Liquidity Sweep (External)", 
                "MSS / Market Structure Shift", "Silver Bullet (ICT)", "Unicorn Setup", 
                "Order Block Rejection", "Breaker Block", "Turtle Soup"
            ])
            timeframe = st.selectbox("Execution TF", ["15s", "1m", "5m", "15m", "1h", "4h", "Daily"])
        with s2:
            confluences = st.multiselect("Confluences", [
                "PD Array", "Oversold/Overbought", "Killzone Time", "SMT Divergence", 
                "Premium/Discount Array", "Daily Bias Aligned", "News Driven", "High Volume Node"
            ])
        with s3:
            rr_planned = st.number_input("Planned R:R", min_value=0.0, value=2.0)
            stop_dist = st.number_input("Stop Distance (Ticks/Points)", min_value=0.0)

        st.divider()

        # Terza Riga: Psicologia e Diario
        st.subheader("Psychological & Discipline Review")
        p1, p2, p3 = st.columns(3)
        with p1:
            mindset = st.select_slider("Pre-Trade Mindset", options=["Tired", "Anxious", "Neutral", "Focused", "Flow State"])
        with p2:
            emotion = st.selectbox("Dominant Emotion", ["Calm", "Fear of Missing Out", "Greed", "Patience", "Anger/Revenge"])
        with p3:
            discipline = st.radio("Discipline Level", ["Followed Plan", "Early Exit", "Moved Stop", "Overleveraged", "Averaging Down"])
        
        notes = st.text_area("Trade Journal (Analisi post-trade e sensazioni)")
        
        if st.form_submit_button("LOCK DATA IN CLOUD"):
            # Calcolo PnL Matematico
            if side == "Long":
                calculated_pnl = (exit_p - entry) * contracts * multiplier
            else:
                calculated_pnl = (entry - exit_p) * contracts * multiplier
            
            payload = {
                "asset": asset, "direction": side, "entry_price": entry, "exit_price": exit_p,
                "pnl": calculated_pnl, "setup": primary_setup, "session": session, 
                "exit_date": str(exit_date), "psychology": mindset, "emotion": emotion, 
                "discipline": discipline, "notes": notes, "timeframe": timeframe, "rr_ratio": rr_planned
            }
            
            try:
                db.table("trades").insert(payload).execute()
                st.success(f"TRADE REGISTRATO: Profitto/Perdita di ${calculated_pnl:,.2f}")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Errore durante il salvataggio: {e}")

# --- 6. DASHBOARD & ANALYTICS (TUTTE LE FUNZIONI DI IERI + NUOVE) ---
elif page == "📊 DASHBOARD":
    st.title("Performance Intelligence")
    if not df_main.empty:
        # Metriche in alto
        m1, m2, m3, m4 = st.columns(4)
        net_pnl = df_main['pnl'].sum()
        wr = (len(df_main[df_main['pnl'] > 0]) / len(df_main)) * 100
        pf = abs(df_main[df_main['pnl'] > 0]['pnl'].sum() / df_main[df_main['pnl'] < 0]['pnl'].sum()) if not df_main[df_main['pnl'] < 0].empty else 0
        
        m1.metric("NET P&L", f"${net_pnl:,.2f}")
        m2.metric("WIN RATE", f"{wr:.1f}%")
        m3.metric("PROFIT FACTOR", f"{pf:.2f}")
        m4.metric("TOTAL TRADES", len(df_main))

        # Equity Curve
        df_main = df_main.sort_values('exit_date')
        df_main['equity'] = df_main['pnl'].cumsum()
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(x=df_main['exit_date'], y=df_main['equity'], fill='tozeroy', line=dict(color='#00ff88', width=3)))
        fig_eq.update_layout(template="plotly_dark", height=450, title="Cumulative Equity Curve")
        st.plotly_chart(fig_eq, use_container_width=True)
    else:
        st.info("Nessun trade nel database.")

# --- 7. CALENDARIO P&L (STILE RICHIESTO) ---
elif page == "📅 CALENDARIO P&L":
    st.title("Daily PnL Calendar")
    if not df_main.empty:
        df_main['d_only'] = df_main['exit_date'].dt.date
        daily = df_main.groupby('d_only')['pnl'].sum().to_dict()
        
        now = datetime.now()
        cal = calendar.monthcalendar(now.year, now.month)
        
        st.subheader(f"{calendar.month_name[now.month]} {now.year}")
        cols_h = st.columns(7)
        for i, d in enumerate(["LUN", "MAR", "MER", "GIO", "VEN", "SAB", "DOM"]):
            cols_h[i].markdown(f"<center><small>{d}</small></center>", unsafe_allow_html=True)

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

# --- 8. ANALISI TECNICA & PSICOLOGICA ---
elif page == "📈 ANALISI TECNICA":
    st.title("Strategy Efficiency")
    if not df_main.empty:
        col_t1, col_t2 = st.columns(2)
        fig_setup = px.bar(df_main.groupby('setup')['pnl'].sum().reset_index(), x='setup', y='pnl', title="PnL by Setup", template="plotly_dark", color='pnl')
        col_t1.plotly_chart(fig_setup, use_container_width=True)
        
        fig_session = px.pie(df_main, names='session', values='pnl', title="PnL Distribution by Session", template="plotly_dark")
        col_t2.plotly_chart(fig_session, use_container_width=True)

elif page == "🧠 PSICOLOGIA":
    st.title("Behavioral Analysis")
    if not df_main.empty:
        col_p1, col_p2 = st.columns(2)
        fig_mind = px.box(df_main, x='psychology', y='pnl', title="PnL vs Mindset", template="plotly_dark")
        col_p1.plotly_chart(fig_mind, use_container_width=True)
        
        fig_disc = px.bar(df_main.groupby('discipline')['pnl'].count().reset_index(), x='discipline', y='pnl', title="Discipline Frequency", template="plotly_dark")
        col_p2.plotly_chart(fig_disc, use_container_width=True)

# --- 9. DATABASE & SETTINGS ---
elif page == "🗄️ DATABASE":
    st.title("Full Trade Archive")
    st.dataframe(df_main.sort_values('exit_date', ascending=False), use_container_width=True)
    
elif page == "⚙️ SETTINGS":
    st.title("System Configuration")
    st.write("Database Status: Connected")
    st.write(f"Supabase Project ID: {SUPABASE_URL.split('//')[1].split('.')[0]}")

import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. UI & COSMETIC SETTINGS (PREMIUM DARK)
# ==========================================
st.set_page_config(page_title="TradeCore | Elite Terminal", layout="wide", page_icon="📉")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #000000; color: #ffffff; }
    .main { background-color: #000000; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #1f1f1f; min-width: 300px; }
    
    /* Metric Cards */
    .stMetric { 
        background-color: #0a0a0a; 
        padding: 25px; 
        border-radius: 12px; 
        border: 1px solid #1f1f1f;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    
    /* Buttons */
    div.stButton > button { 
        background-color: #ffffff; 
        color: #000000; 
        border-radius: 4px; 
        font-weight: 800; 
        width: 100%; 
        height: 3.5em;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: none;
    }
    div.stButton > button:hover { background-color: #cccccc; cursor: pointer; }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 30px; background-color: transparent; }
    .stTabs [data-baseweb="tab"] { 
        color: #666; 
        font-weight: 700; 
        font-size: 18px;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] { color: #ffffff !important; border-bottom: 2px solid #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CLOUD CORE (SUPABASE)
# ==========================================
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase = create_client(URL, KEY)

def load_all_records():
    try:
        res = supabase.table('trades').select("*").order('created_at').execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

# ==========================================
# 3. GLOBAL STATE
# ==========================================
df = load_all_records()
if 'init_cap' not in st.session_state: st.session_state.init_cap = 5000.0

# ==========================================
# 4. NAVIGATION SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3594/3594449.png", width=50)
    st.title("TRADECORE")
    st.caption("PROFESSIONAL VAULT v4.0")
    st.markdown("---")
    
    nav = st.radio("NAVIGATION", ["DASHBOARD", "LOG TRADE", "PSYCHOLOGY", "DAILY RECAP", "SETTINGS"])
    
    st.markdown("---")
    # Real-time mini metrics in sidebar
    if not df.empty:
        t_df = df.dropna(subset=['net_profit'])
        net = t_df['net_profit'].sum()
        st.metric("NET BALANCE", f"€{st.session_state.init_cap + net:,.2f}", delta=f"€{net:,.2f}")
    
    st.info("System: Online\nData: Encrypted")

# ==========================================
# MODULE: DASHBOARD (The Visual Engine)
# ==========================================
if nav == "DASHBOARD":
    st.header("📊 PERFORMANCE ANALYTICS")
    t_df = df.dropna(subset=['net_profit']) if not df.empty else pd.DataFrame()

    if not t_df.empty:
        # Top Row Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("EXECUTIONS", len(t_df))
        wr = (len(t_df[t_df['net_profit'] > 0]) / len(t_df)) * 100
        c2.metric("WIN RATE", f"{wr:.1f}%")
        c3.metric("AVG PROFIT", f"€{t_df['net_profit'].mean():,.2f}")
        
        pos = t_df[t_df['net_profit'] > 0]['net_profit'].sum()
        neg = abs(t_df[t_df['net_profit'] < 0]['net_profit'].sum())
        pf = round(pos / neg, 2) if neg != 0 else "MAX"
        c4.metric("PROFIT FACTOR", pf)

        st.divider()

        # Equity Curve Large
        t_df['equity'] = st.session_state.init_cap + t_df['net_profit'].cumsum()
        fig = px.area(t_df, y='equity', title="EQUITY EVOLUTION", template="plotly_dark")
        fig.update_traces(line_color='#ffffff', fillcolor='rgba(255,255,255,0.1)')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)

        # Asset Distribution
        st.subheader("ASSET PERFORMANCE")
        asset_perf = t_df.groupby('asset')['net_profit'].sum().reset_index()
        fig_bar = px.bar(asset_perf, x='asset', y='net_profit', template="plotly_dark", color='net_profit', color_continuous_scale='Greys')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("NO DATA DETECTED. PLEASE LOG YOUR FIRST TRADE.")

# ==========================================
# MODULE: LOG TRADE (The Terminal)
# ==========================================
elif nav == "LOG TRADE":
    st.header("⚡ EXECUTION TERMINAL")
    
    assets = [
        "NAS100", "US30", "SPX500", "GER40", "GOLD", "EURUSD", "GBPUSD", "USDJPY", 
        "BTCUSD", "ETHUSD", "SOLUSD", "OIL_WTI", "NAT_GAS", "SILVER"
    ]

    with st.form("trade_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            asset = st.selectbox("Asset Instrument", assets)
            side = st.radio("Market Side", ["LONG", "SHORT"], horizontal=True)
            st.markdown("---")
            size_type = st.radio("Size Type", ["LOTS", "CONTRACTS"], horizontal=True)
            size_val = st.number_input(f"Volume ({size_type})", value=0.1, step=0.01)
            
        with col2:
            entry = st.number_input("Entry Price", format="%.5f")
            exit_p = st.number_input("Exit Price", format="%.5f")
            setup = st.text_input("Setup/Strategy", placeholder="IFVG / MSS / Breaker")
            
        with col3:
            gross = st.number_input("Gross Profit/Loss (€)", value=0.0, step=1.0)
            comm = st.number_input("Commissions (€)", value=0.0, step=0.1)
            st.markdown("### NET RESULT")
            st.title(f"€{gross - comm:.2f}")

        st.divider()
        note = st.text_area("Execution Notes", placeholder="Why did you take this setup?")

        if st.form_submit_button("LOCK TRADE INTO VAULT"):
            payload = {
                "asset": asset, "side": side, "entry_price": entry, "exit_price": exit_p,
                "lots": size_val if size_type == "LOTS" else None,
                "contracts": size_val if size_type == "CONTRACTS" else None,
                "gross_profit": gross, "commissions": comm,
                "net_profit": gross - comm, "setup_type": setup, "mood_notes": note
            }
            supabase.table('trades').insert(payload).execute()
            st.success("TRADE SECURED IN CLOUD")
            st.rerun()

# ==========================================
# MODULE: PSYCHOLOGY (Mindset)
# ==========================================
elif nav == "PSYCHOLOGY":
    st.header("🧠 MINDSET TRACKER")
    with st.form("psy_form"):
        mood = st.select_slider("Session Mood", options=["REVENGE", "TOUGH", "CALM", "FOCUSED", "GOD MODE"], value="CALM")
        psy_notes = st.text_area("How are you feeling?", placeholder="Focus on emotions, not numbers...")
        if st.form_submit_button("SAVE EMOTIONAL STATE"):
            supabase.table('trades').insert({
                "psychology_score": mood, "mood_notes": psy_notes, "asset": "PSY_LOG"
            }).execute()
            st.success("Mindset Logged")
            st.rerun()
    
    if not df.empty:
        st.divider()
        psy_df = df.dropna(subset=['psychology_score'])
        st.subheader("HISTORY")
        st.dataframe(psy_df[['created_at', 'psychology_score', 'mood_notes']].iloc[::-1], use_container_width=True)

# ==========================================
# MODULE: DAILY RECAP
# ==========================================
elif nav == "DAILY RECAP":
    st.header("📅 DAILY PERFORMANCE REVIEW")
    with st.form("day_form"):
        score = st.slider("Rate Today's Discipline (1-10)", 1, 10, 5)
        summary = st.text_area("Key Lesson of the Day", placeholder="What will you do better tomorrow?")
        if st.form_submit_button("CLOSE TRADING DAY"):
            supabase.table('trades').insert({
                "daily_score": score, "daily_summary": summary, "asset": "DAILY_RECAP"
            }).execute()
            st.success("Day Logged")
            st.rerun()

# ==========================================
# MODULE: SETTINGS
# ==========================================
elif nav == "SETTINGS":
    st.header("⚙️ CONFIGURATION")
    st.session_state.init_cap = st.number_input("Starting Capital (€)", value=st.session_state.init_cap)
    if st.button("RESET SYSTEM VIEW"): st.rerun()

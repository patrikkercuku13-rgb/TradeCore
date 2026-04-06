import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. ARCHITECTURAL UI CONFIG (PREMIUM DARK)
# ==========================================
st.set_page_config(
    page_title="TRADECORE | Magnum Opus v6.0",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for High-End Terminal Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace; background-color: #000000; color: #ffffff; }
    .main { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #1f1f1f; }
    
    /* Metric Cards Styling */
    .stMetric { 
        background-color: #0a0a0a; 
        padding: 25px; 
        border-radius: 4px; 
        border: 1px solid #1f1f1f;
        transition: 0.3s;
    }
    .stMetric:hover { border-color: #00ff41; }
    
    /* Button Aesthetics */
    div.stButton > button { 
        background-color: #ffffff; color: #000; border-radius: 2px; 
        font-weight: 800; text-transform: uppercase; letter-spacing: 2px;
        transition: 0.4s; border: none; height: 3.8em; width: 100%;
    }
    div.stButton > button:hover { background-color: #00ff41; box-shadow: 0 0 20px rgba(0,255,65,0.4); }
    
    /* Progress Bar */
    .stProgress > div > div > div > div { background-color: #00ff41; }
    
    /* Dataframe Styling */
    [data-testid="stTable"] { background-color: #0a0a0a; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINE & CLOUD SYNC
# ==========================================
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase = create_client(URL, KEY)

@st.cache_data(ttl=5)
def load_vault_data():
    try:
        res = supabase.table('trades').select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

# Initialize Session Global Variables
if 'balance' not in st.session_state: st.session_state.balance = 50000.0
if 'acc_mode' not in st.session_state: st.session_state.acc_mode = "Funded"
if 'target' not in st.session_state: st.session_state.target = 3000.0
if 'max_dd' not in st.session_state: st.session_state.max_dd = 2500.0

df_raw = load_vault_data()

# ==========================================
# 3. SIDEBAR COMMAND CENTER
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='letter-spacing: 6px; color: #00ff41;'>CORE</h1>", unsafe_allow_html=True)
    st.caption(f"OS VERSION 6.0 | ACCOUNT: {st.session_state.acc_mode.upper()}")
    st.divider()
    
    nav = st.radio("SQUADRON MODULES", 
                   ["DASHBOARD", "EXECUTION TERMINAL", "ADVANCED ANALYTICS", "PSYCHOLOGY", "DAILY RECAP", "PORTFOLIO MANAGER"])
    
    st.divider()
    if not df_raw.empty:
        # Strict Filtering for Financial Metrics
        trades_only = df_raw[df_raw['net_profit'].notna() & (~df_raw['asset'].isin(['PSY_SYSTEM', 'DAY_SYSTEM', 'MINDSET_LOG', 'DAILY_RECAP']))]
        net_pnl = trades_only['net_profit'].sum()
        current_eq = st.session_state.balance + net_pnl
        
        st.metric("TOTAL EQUITY", f"€{current_eq:,.2f}", delta=f"€{net_pnl:,.2f}")
        
        if st.session_state.acc_mode == "Funded":
            prog_ratio = (net_pnl / st.session_state.target)
            st.progress(min(max(prog_ratio, 0.0), 1.0))
            st.write(f"Target: {prog_ratio*100:.1f}%")
    
    st.markdown("---")
    st.caption("CONNECTION: ENCRYPTED ✅")

# ==========================================
# MODULE 1: DASHBOARD (The Oversight)
# ==========================================
if nav == "DASHBOARD":
    st.header("📈 PERFORMANCE MONITOR")
    t_df = df_raw[df_raw['net_profit'].notna() & (~df_raw['asset'].isin(['PSY_SYSTEM', 'DAY_SYSTEM', 'MINDSET_LOG', 'DAILY_RECAP']))]

    if not t_df.empty:
        # High-Speed Stats
        m1, m2, m3, m4 = st.columns(4)
        wins = len(t_df[t_df['net_profit'] > 0])
        total_executions = len(t_df)
        win_rate = (wins / total_executions * 100) if total_executions > 0 else 0
        
        m1.metric("WIN RATE", f"{win_rate:.1f}%")
        m2.metric("PROFIT FACTOR", round(t_df[t_df['net_profit']>0]['net_profit'].sum() / abs(t_df[t_df['net_profit']<0]['net_profit'].sum()), 2) if not t_df[t_df['net_profit']<0].empty else "MAX")
        m3.metric("EXECUTIONS", total_executions)
        m4.metric("AVG RISK/TRADE", f"{t_df['risk_pct'].mean():.2f}%")

        st.divider()
        
        # Area Equity Chart
        t_df = t_df.sort_values('created_at', ascending=True)
        t_df['equity_line'] = st.session_state.balance + t_df['net_profit'].cumsum()
        
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(x=t_df['created_at'], y=t_df['equity_line'], fill='tozeroy', line_color='#00ff41', name='Equity'))
        fig_equity.update_layout(title="EQUITY EVOLUTION (LIVE)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_equity, use_container_width=True)
        
        # Recent List
        st.subheader("LATEST ENTRIES")
        st.dataframe(t_df.sort_values('created_at', ascending=False).head(5), use_container_width=True)
    else:
        st.info("NO TRADE DATA DETECTED. INITIALIZE TERMINAL.")

# ==========================================
# MODULE 2: EXECUTION TERMINAL (The Engine)
# ==========================================
elif nav == "EXECUTION TERMINAL":
    st.header("⚡ COMMAND TERMINAL")
    
    asset_catalog = [
        "NAS100", "US30", "SPX500", "GER40", "UK100", 
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD",
        "GOLD", "SILVER", "OIL_WTI", "BTCUSD", "ETHUSD", "SOLUSD"
    ]

    with st.form("master_exec_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.subheader("Asset & Size")
            asset = st.selectbox("Market", asset_catalog)
            side = st.radio("Direction", ["LONG", "SHORT"], horizontal=True)
            unit_type = st.radio("Unit", ["Lots", "Contracts", "Mini Contracts"], horizontal=True)
            # Lots use Decimals, Contracts use Integers
            if unit_type == "Lots":
                vol = st.number_input("Volume (Decimal)", value=0.10, step=0.01, format="%.2f")
            else:
                vol = st.number_input("Volume (Integer)", value=1, step=1)
                
        with c2:
            st.subheader("Price Levels")
            entry_p = st.number_input("Entry Price", format="%.5f")
            exit_p = st.number_input("Exit Price", format="%.5f")
            stop_l = st.number_input("Stop Loss", format="%.5f")
            tick_val = st.number_input("Point Value (€)", value=1.0, help="Value of 1 point movement per 1 lot/contract")

        with c3:
            st.subheader("Financials")
            # Logic for Auto-Calculation
            if side == "LONG":
                gross_p = (exit_p - entry_p) * vol * tick_val
                risk_money = abs(entry_p - stop_l) * vol * tick_val if stop_l != 0 else 0
            else:
                gross_p = (entry_p - exit_p) * vol * tick_val
                risk_money = abs(stop_l - entry_p) * vol * tick_val if stop_l != 0 else 0
            
            commission = st.number_input("Broker Fees (€)", value=0.0, step=0.1)
            final_net = gross_p - commission
            
            st.markdown(f"### NET: <span style='color:#00ff41;'>€{final_net:.2f}</span>", unsafe_allow_html=True)
            r_pct = (risk_money / st.session_state.balance * 100) if st.session_state.balance > 0 else 0
            st.caption(f"Risk Amount: €{risk_money:.2f} ({r_pct:.2f}%)")

        st.divider()
        st.subheader("Context")
        setup_type = st.text_input("Setup Name", placeholder="e.g., FVG + Liquidity")
        trade_notes = st.text_area("Execution Journal", placeholder="Details about entry feeling...")

        if st.form_submit_button("LOCK TRADE INTO CLOUD"):
            submission = {
                "asset": asset, "side": side, "entry_price": entry_p, "exit_price": exit_p,
                "lots": vol if unit_type == "Lots" else None,
                "contracts": int(vol) if unit_type == "Contracts" else None,
                "mini_contracts": int(vol) if unit_type == "Mini Contracts" else None,
                "gross_profit": gross_p, "commissions": commission, "net_profit": final_net,
                "risk_pct": r_pct, "setup_type": setup_type, "mood_notes": trade_notes
            }
            supabase.table('trades').insert(submission).execute()
            st.success("DATA ENCRYPTED & SAVED")
            st.rerun()

# ==========================================
# MODULE 3: ADVANCED ANALYTICS (Data Deep Dive)
# ==========================================
elif nav == "ADVANCED ANALYTICS":
    st.header("🧬 DATA INTELLIGENCE")
    t_df = df_raw[df_raw['net_profit'].notna() & (~df_raw['asset'].isin(['PSY_SYSTEM', 'DAY_SYSTEM', 'MINDSET_LOG', 'DAILY_RECAP']))]
    
    if not t_df.empty:
        row1_1, row1_2 = st.columns(2)
        with row1_1:
            st.plotly_chart(px.pie(t_df, names='asset', values='net_profit', title="PROFIT BY ASSET", hole=0.4, template="plotly_dark"), use_container_width=True)
        with row1_2:
            st.plotly_chart(px.bar(t_df, x='side', y='net_profit', color='side', title="LONG VS SHORT PERFORMANCE", template="plotly_dark"), use_container_width=True)
        
        st.divider()
        
        row2_1, row2_2 = st.columns([2, 1])
        with row2_1:
            st.subheader("STRATEGY WIN-RATE ANALYSIS")
            strat_perf = t_df.groupby('setup_type')['net_profit'].sum().reset_index()
            st.plotly_chart(px.bar(strat_perf, x='setup_type', y='net_profit', color='net_profit', template="plotly_dark"), use_container_width=True)
        with row2_2:
            st.subheader("COMMISSION IMPACT")
            total_comm = t_df['commissions'].sum()
            st.metric("TOTAL FEES PAID", f"€{total_comm:,.2f}")
            st.caption("Fees vs Net Ratio: " + f"{total_comm/abs(t_df['net_profit'].sum())*100:.2f}%")
    else:
        st.warning("AWAITING DATABASE POPULATION...")

# ==========================================
# MODULE 4: PSYCHOLOGY (Mindset Vault)
# ==========================================
elif nav == "PSYCHOLOGY":
    st.header("🧠 PSYCHOLOGICAL JOURNAL")
    with st.form("psy_log_form", clear_on_submit=True):
        m_mood = st.select_slider("Current State", options=["REVENGE", "TOUGH", "CALM", "FOCUSED", "GOD MODE"], value="CALM")
        m_notes = st.text_area("Detailed Mental Scan", placeholder="Describe emotions, distractions, or flow state...")
        if st.form_submit_button("RECORD MINDSET"):
            supabase.table('trades').insert({"psychology_score": m_mood, "mood_notes": m_notes, "asset": "PSY_SYSTEM"}).execute()
            st.success("MINDSET SECURED")
            st.rerun()
            
    if not df_raw.empty:
        st.divider()
        psy_data = df_raw[df_raw['asset'] == 'PSY_SYSTEM'].head(10)
        st.table(psy_data[['created_at', 'psychology_score', 'mood_notes']])

# ==========================================
# MODULE 5: DAILY RECAP (Discipline)
# ==========================================
elif nav == "DAILY RECAP":
    st.header("📅 DAILY PERFORMANCE RECAP")
    with st.form("daily_form", clear_on_submit=True):
        d_score = st.slider("Discipline Level (1-10)", 1, 10, 5)
        d_summary = st.text_area("Key Takeaways", placeholder="What did you learn from the markets today?")
        if st.form_submit_button("CLOSE TRADING DAY"):
            supabase.table('trades').insert({"daily_score": d_score, "daily_summary": d_summary, "asset": "DAY_SYSTEM"}).execute()
            st.success("DAY LOGGED")
            st.rerun()

# ==========================================
# MODULE 6: PORTFOLIO MANAGER (Vault Control)
# ==========================================
elif nav == "PORTFOLIO MANAGER":
    st.header("⚙️ VAULT CONFIGURATION")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.session_state.acc_mode = st.radio("ACCOUNT ARCHITECTURE", ["Personal", "Funded"], horizontal=True)
        st.session_state.balance = st.number_input("INITIAL BALANCE (€)", value=st.session_state.balance)
    
    with col_p2:
        if st.session_state.acc_mode == "Funded":
            st.session_state.target = st.number_input("PROFIT TARGET (€)", value=st.session_state.target)
            st.session_state.max_dd = st.number_input("MAX DRAWDOWN (€)", value=st.session_state.max_dd)
            
    st.divider()
    if st.button("RE-CALIBRATE SYSTEM"):
        st.balloons()
        st.rerun()

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption(f"TRADECORE MASTERPIECE V6.0 | SYSTEM TIME: {datetime.now().strftime('%H:%M:%S')} | CLOUD: SUPABASE")

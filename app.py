import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. ARCHITECTURAL UI CONFIG (TOTAL BLACK)
# ==========================================
st.set_page_config(
    page_title="TRADECORE | Master Terminal",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace; background-color: #000000; color: #ffffff; }
    .main { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #1f1f1f; }
    .stMetric { background-color: #0a0a0a; padding: 20px; border-radius: 8px; border: 1px solid #222; }
    div.stButton > button { 
        background-color: #ffffff; color: #000; border-radius: 2px; 
        font-weight: 800; text-transform: uppercase; letter-spacing: 2px;
        transition: 0.4s; border: none; height: 3.5em;
    }
    div.stButton > button:hover { background-color: #00ff41; color: #000; box-shadow: 0 0 15px #00ff41; }
    .stProgress > div > div > div > div { background-color: #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CORE ENGINE & CLOUD SYNC
# ==========================================
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase = create_client(URL, KEY)

@st.cache_data(ttl=10)
def fetch_vault():
    try:
        res = supabase.table('trades').select("*").order('created_at').execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

# Global State Management
if 'balance' not in st.session_state: st.session_state.balance = 50000.0
if 'acc_mode' not in st.session_state: st.session_state.acc_mode = "Funded"
if 'p_target' not in st.session_state: st.session_state.p_target = 3000.0
if 'm_drawdown' not in st.session_state: st.session_state.m_drawdown = 2500.0

df_raw = fetch_vault()

# ==========================================
# 3. NAVIGATION & SIDEBAR COMMANDS
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='letter-spacing: 5px;'>TRADECORE</h1>", unsafe_allow_html=True)
    st.caption(f"CONNECTED AS: {st.session_state.acc_mode.upper()} OPERATOR")
    st.divider()
    
    module = st.radio("COMMAND CENTER", 
                      ["DASHBOARD", "EXECUTION LOG", "ANALYTICS", "PSYCHOLOGY", "DAILY RECAP", "PORTFOLIO"])
    
    st.divider()
    # Live Accounting in Sidebar
    if not df_raw.empty:
        trades_only = df_raw.dropna(subset=['net_profit'])
        pnl = trades_only['net_profit'].sum()
        current = st.session_state.balance + pnl
        st.metric("TOTAL EQUITY", f"€{current:,.2f}", delta=f"{pnl:,.2f}")
        
        if st.session_state.acc_mode == "Funded":
            prog = (pnl / st.session_state.p_target)
            st.caption(f"Target: €{st.session_state.p_target:,.2f}")
            st.progress(min(max(prog, 0.0), 1.0))
            st.write(f"Objective: {prog*100:.1f}%")

# ==========================================
# MODULE 1: DASHBOARD (Visual Intelligence)
# ==========================================
if module == "DASHBOARD":
    st.header("💎 PERFORMANCE OVERVIEW")
    t_df = df_raw.dropna(subset=['net_profit']) if not df_raw.empty else pd.DataFrame()

    if not t_df.empty:
        # High Level Stats
        k1, k2, k3, k4 = st.columns(4)
        wr = (len(t_df[t_df['net_profit'] > 0]) / len(t_df)) * 100
        k1.metric("WIN RATE", f"{wr:.1f}%")
        k2.metric("PROFIT FACTOR", round(t_df[t_df['net_profit']>0]['net_profit'].sum() / abs(t_df[t_df['net_profit']<0]['net_profit'].sum()), 2) if not t_df[t_df['net_profit']<0].empty else "INF")
        k3.metric("AVG RRR", f"{t_df['risk_pct'].mean():.2f}% Per Trade")
        k4.metric("TOTAL NET", f"€{t_df['net_profit'].sum():,.2f}")

        st.divider()
        # Main Equity Curve
        t_df['cum_pnl'] = st.session_state.balance + t_df['net_profit'].cumsum()
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(y=t_df['cum_pnl'], mode='lines+markers', name='Equity', line=dict(color='#00ff41', width=3), fill='tozeroy', fillcolor='rgba(0,255,65,0.05)'))
        fig_equity.update_layout(title="MASTER EQUITY CURVE", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_equity, use_container_width=True)
    else:
        st.info("NO TRADES LOGGED. ACCESS THE 'EXECUTION LOG' TO BEGIN.")

# ==========================================
# MODULE 2: EXECUTION LOG (The Terminal)
# ==========================================
elif module == "EXECUTION LOG":
    st.header("⚡ TRADE EXECUTION TERMINAL")
    
    asset_list = ["NAS100", "US30", "SPX500", "GER40", "GOLD", "SILVER", "EURUSD", "GBPUSD", "USDJPY", "BTCUSD", "ETHUSD", "SOLUSD"]
    
    with st.form("terminal_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            asset = st.selectbox("Market Asset", asset_list)
            side = st.radio("Action", ["LONG", "SHORT"], horizontal=True)
            st.markdown("---")
            size_mode = st.radio("Unit Type", ["Contracts", "Mini Contracts", "Lots"], horizontal=True)
            size_val = st.number_input(f"Enter {size_mode}", value=1 if size_mode != "Lots" else 0.10, step=1 if size_mode != "Lots" else 0.01)
        
        with f2:
            ent = st.number_input("Entry Level", format="%.5f")
            ext = st.number_input("Exit Level", format="%.5f")
            setup = st.text_input("Strategy/Setup", placeholder="IFVG, MSS, Liquidity Sweep")
            risk = st.number_input("Risk Applied (%)", value=0.5, step=0.1)

        with f3:
            gross = st.number_input("Gross P/L (€)", value=0.0, step=10.0)
            comm = st.number_input("Commission Cost (€)", value=0.0, step=0.1)
            net_val = gross - comm
            st.markdown("### EXPECTED NET")
            color = "#00ff41" if net_val >= 0 else "#ff4b4b"
            st.markdown(f"<h1 style='color:{color};'>€{net_val:.2f}</h1>", unsafe_allow_html=True)

        note = st.text_area("Execution Journal", placeholder="Context of the trade...")
        
        if st.form_submit_button("SUBMIT TO VAULT"):
            p = {
                "asset": asset, "side": side, "entry_price": ent, "exit_price": ext,
                "contracts": int(size_val) if size_mode == "Contracts" else None,
                "mini_contracts": int(size_val) if size_mode == "Mini Contracts" else None,
                "lots": size_val if size_mode == "Lots" else None,
                "gross_profit": gross, "commissions": comm, "net_profit": net_val,
                "risk_pct": risk, "setup_type": setup, "mood_notes": note,
                "account_tag": st.session_state.acc_mode
            }
            supabase.table('trades').insert(p).execute()
            st.balloons()
            st.rerun()

    if not df_raw.empty:
        st.divider()
        st.subheader("RECENT ACTIVITY")
        st.dataframe(df_raw.dropna(subset=['net_profit']).sort_values('created_at', ascending=False), use_container_width=True)

# ==========================================
# MODULE 3: ANALYTICS (Deep Insight)
# ==========================================
elif module == "ANALYTICS":
    st.header("🧬 ADVANCED DATA ANALYTICS")
    t_df = df_raw.dropna(subset=['net_profit']) if not df_raw.empty else pd.DataFrame()
    
    if not t_df.empty:
        a1, a2 = st.columns(2)
        with a1:
            asset_pie = px.pie(t_df, names='asset', values='net_profit', title="PROFIT BY ASSET", template="plotly_dark", hole=0.4)
            st.plotly_chart(asset_pie, use_container_width=True)
        with a2:
            side_bar = px.bar(t_df, x='side', y='net_profit', title="SIDE PERFORMANCE", color='side', template="plotly_dark")
            st.plotly_chart(side_bar, use_container_width=True)
        
        st.divider()
        st.subheader("STRATEGY EFFICIENCY")
        strat_df = t_df.groupby('setup_type')['net_profit'].sum().reset_index()
        fig_strat = px.bar(strat_df, x='setup_type', y='net_profit', template="plotly_dark", color='net_profit')
        st.plotly_chart(fig_strat, use_container_width=True)
    else:
        st.warning("INSUFFICIENT DATA FOR ANALYSIS")

# ==========================================
# MODULE 4: PSYCHOLOGY (The Human Factor)
# ==========================================
elif module == "PSYCHOLOGY":
    st.header("🧠 PSYCHOLOGICAL JOURNAL")
    with st.form("psy_log"):
        mood = st.select_slider("Session Mindset", options=["REVENGE", "TOUGH", "CALM", "FOCUSED", "GOD MODE"], value="CALM")
        thought = st.text_area("Inner Monologue", placeholder="Fear, greed, or discipline? Explain...")
        if st.form_submit_button("LOG STATE"):
            supabase.table('trades').insert({"psychology_score": mood, "mood_notes": thought, "asset": "PSY_SYSTEM"}).execute()
            st.success("MINDSET RECORDED")
            st.rerun()
    
    if not df_raw.empty:
        psy_data = df_raw.dropna(subset=['psychology_score'])
        st.divider()
        st.table(psy_data[['created_at', 'psychology_score', 'mood_notes']].iloc[::-1].head(10))

# ==========================================
# MODULE 5: DAILY RECAP
# ==========================================
elif module == "DAILY RECAP":
    st.header("📅 DAILY PERFORMANCE RECAP")
    with st.form("day_log"):
        score = st.slider("Discipline Score", 1, 10, 5)
        lesson = st.text_area("Key Lesson Learned", placeholder="What will you change tomorrow?")
        if st.form_submit_button("CLOSE TRADING DAY"):
            supabase.table('trades').insert({"daily_score": score, "daily_summary": lesson, "asset": "DAY_SYSTEM"}).execute()
            st.success("DAY LOGGED")
            st.rerun()

# ==========================================
# MODULE 6: PORTFOLIO (Management)
# ==========================================
elif module == "PORTFOLIO":
    st.header("⚙️ PORTFOLIO COMMAND")
    
    st.session_state.acc_mode = st.radio("ACCOUNT TYPE", ["Personal", "Funded"], horizontal=True)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.session_state.balance = st.number_input("STARTING EQUITY (€)", value=st.session_state.balance)
        if st.session_state.acc_mode == "Funded":
            st.session_state.p_target = st.number_input("PROFIT TARGET (€)", value=st.session_state.p_target)
    with col_p2:
        if st.session_state.acc_mode == "Funded":
            st.session_state.m_drawdown = st.number_input("MAX DRAWDOWN (€)", value=st.session_state.m_drawdown)
    
    if st.button("CALIBRATE SYSTEM"):
        st.success("VAULT RECONFIGURED")
        st.rerun()

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption(f"TRADECORE V5.0 | {datetime.now().strftime('%H:%M:%S')} | ENCRYPTED CLOUD CONNECTION")

import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. PAGE CONFIG
st.set_page_config(page_title="TradeCore | Professional Vault", layout="wide")

# CSS for Dark Mode and Sidebar Navigation
st.markdown("""
    <style>
    .main { background-color: #000000; color: white; }
    [data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #222; }
    .stMetric { background-color: #111; border: 1px solid #222; padding: 20px; border-radius: 10px; }
    div.stButton > button { background-color: white; color: black; font-weight: bold; border-radius: 4px; border: none; }
    div.stButton > button:hover { background-color: #ddd; }
    </style>
    """, unsafe_allow_html=True)

# 2. DATABASE CONNECTION
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase = create_client(URL, KEY)

# 3. DATA ENGINE
def load_data():
    try:
        res = supabase.table('trades').select("*").order('created_at').execute()
        return pd.DataFrame(res.data)
    except: return pd.DataFrame()

df = load_data()
if 'start_cap' not in st.session_state: st.session_state.start_cap = 5000.0

# 4. SIDEBAR NAVIGATION
with st.sidebar:
    st.title("TRADECORE")
    st.caption("Elite Trading OS v3.2")
    st.divider()
    
    menu = st.radio("SELECT MODULE", 
                    ["DASHBOARD", "LOG TRADE", "PSYCHOLOGY", "DAILY RECAP", "SETTINGS"])
    
    st.divider()
    if not df.empty:
        trade_df = df.dropna(subset=['net_profit'])
        net_pl = trade_df['net_profit'].sum()
        st.metric("TOTAL NET P/L", f"€{net_pl:,.2f}", delta=f"{net_pl:,.2f}")
        st.metric("ACCOUNT BALANCE", f"€{st.session_state.start_cap + net_pl:,.2f}")

# ==========================================
# MODULE 1: DASHBOARD
# ==========================================
if menu == "DASHBOARD":
    st.header("📈 PERFORMANCE ANALYTICS")
    trade_df = df.dropna(subset=['net_profit']) if not df.empty else pd.DataFrame()

    if not trade_df.empty:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("EXECUTIONS", len(trade_df))
        m2.metric("WIN RATE", f"{(len(trade_df[trade_df['net_profit'] > 0]) / len(trade_df)) * 100:.1f}%")
        m3.metric("AVG TRADE", f"€{trade_df['net_profit'].mean():,.2f}")
        
        pos = trade_df[trade_df['net_profit'] > 0]['net_profit'].sum()
        neg = abs(trade_df[trade_df['net_profit'] < 0]['net_profit'].sum())
        pf = round(pos / neg, 2) if neg != 0 else "MAX"
        m4.metric("PROFIT FACTOR", pf)

        st.divider()
        trade_df['equity'] = st.session_state.start_cap + trade_df['net_profit'].cumsum()
        fig = px.line(trade_df, y='equity', title="EQUITY CURVE", template="plotly_dark", color_discrete_sequence=['white'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("RECENT TRADES")
        st.dataframe(trade_df.sort_values('created_at', ascending=False).head(10), use_container_width=True)
    else:
        st.info("The vault is empty. Go to 'LOG TRADE' to start.")

# ==========================================
# MODULE 2: LOG TRADE
# ==========================================
elif menu == "LOG TRADE":
    st.header("⚡ EXECUTION TERMINAL")
    
    # Lista Asset Espansa
    asset_list = [
        "NAS100", "US30", "SPX500", "GER40", "UK100", "JP225", # Indices
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "USDCHF", "EURGBP", # Forex Major
        "GOLD", "SILVER", "OIL_WTI", "NAT_GAS", # Commodities
        "BTCUSD", "ETHUSD", "SOLUSD", "XRPUSD" # Crypto
    ]

    with st.form("trade_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            asset = st.selectbox("Instrument", asset_list)
            side = st.selectbox("Side", ["LONG", "SHORT"])
            # Aggiunta scelta tra Lots e Contracts
            size_type = st.radio("Size Type", ["Lots", "Contracts"], horizontal=True)
            size_val = st.number_input(f"Enter {size_type}", value=0.10, step=0.01)
        with c2:
            entry = st.number_input("Entry Price", format="%.5f")
            exit_p = st.number_input("Exit Price", format="%.5f")
            setup = st.text_input("Setup Name", placeholder="IFVG, Breaker, etc.")
        with c3:
            gross = st.number_input("Gross P/L (€)", value=0.0)
            comm = st.number_input("Commissions (€)", value=0.0)
            st.markdown("### Total Net")
            st.write(f"€{gross - comm:.2f}")

        if st.form_submit_button("SUBMIT TRADE"):
            data = {
                "asset": asset, "side": side, "entry_price": entry, "exit_price": exit_p,
                "lots": size_val if size_type == "Lots" else None,
                "contracts": size_val if size_type == "Contracts" else None,
                "gross_profit": gross, "commissions": comm,
                "net_profit": gross - comm, "setup_type": setup
            }
            supabase.table('trades').insert(data).execute()
            st.success(f"Trade on {asset} Secured!")
            st.rerun()

# ==========================================
# MODULE 3: PSYCHOLOGY (Mantenedo tutto)
# ==========================================
elif menu == "PSYCHOLOGY":
    st.header("🧠 MINDSET TRACKER")
    with st.form("psy_form", clear_on_submit=True):
        mood = st.select_slider("Current State", options=["REVENGE", "TOUGH", "CALM", "FOCUSED", "GOD MODE"])
        notes = st.text_area("Trading Session Notes", placeholder="How do you feel right now?")
        if st.form_submit_button("SAVE MINDSET"):
            supabase.table('trades').insert({
                "psychology_score": mood,
                "mood_notes": notes,
                "asset": "MINDSET_LOG"
            }).execute()
            st.success("Mindset recorded!")
            st.rerun()

    if not df.empty:
        st.divider()
        st.subheader("PSYCHOLOGY HISTORY")
        psy_df = df.dropna(subset=['psychology_score'])
        st.table(psy_df[['created_at', 'psychology_score', 'mood_notes']].iloc[::-1].head(10))

# ==========================================
# MODULE 4: DAILY RECAP (Mantenedo tutto)
# ==========================================
elif menu == "DAILY RECAP":
    st.header("📅 END OF DAY REVIEW")
    with st.form("daily_form", clear_on_submit=True):
        d_score = st.slider("Daily Performance Score (1-10)", 1, 10, 5)
        d_summary = st.text_area("What did you learn today?")
        if st.form_submit_button("FINISH DAY"):
            supabase.table('trades').insert({
                "daily_score": d_score,
                "daily_summary": d_summary,
                "asset": "DAILY_RECAP"
            }).execute()
            st.success("Daily Recap Logged!")
            st.rerun()

    if not df.empty:
        st.divider()
        st.subheader("RECENT RECAPS")
        recap_df = df.dropna(subset=['daily_score'])
        st.table(recap_df[['created_at', 'daily_score', 'daily_summary']].iloc[::-1].head(5))

# ==========================================
# MODULE 5: SETTINGS (Mantenedo tutto)
# ==========================================
elif menu == "SETTINGS":
    st.header("⚙️ SYSTEM CONFIG")
    st.session_state.start_cap = st.number_input("Initial Capital", value=st.session_state.start_cap)
    if st.button("RESET SESSION"): st.rerun()

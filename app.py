import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. UI ARCHITECTURE (ULTRA-BLACK TERMINAL)
# ==========================================
st.set_page_config(
    page_title="TRADECORE | Ultimate Vault",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Execution Environment
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace; background-color: #000000; color: #ffffff; }
    .main { background-color: #000000; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #1f1f1f; }
    
    /* Metric Cards */
    .stMetric { 
        background-color: #0a0a0a; 
        padding: 25px; 
        border-radius: 2px; 
        border: 1px solid #1f1f1f;
    }
    
    /* Neon Buttons */
    div.stButton > button { 
        background-color: #ffffff; color: #000; border-radius: 0px; 
        font-weight: 800; text-transform: uppercase; letter-spacing: 2px;
        transition: 0.4s; border: none; height: 3.8em; width: 100%;
    }
    div.stButton > button:hover { background-color: #ff4b4b; color: white; box-shadow: 0 0 20px rgba(255,75,75,0.4); }
    
    /* Delete Button Specific */
    .delete-btn button { background-color: #ff4b4b !important; color: white !important; }

    /* Tables */
    .stDataFrame { border: 1px solid #1f1f1f; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CLOUD CORE (SUPABASE SYNC)
# ==========================================
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase = create_client(URL, KEY)

def fetch_vault():
    try:
        res = supabase.table('trades').select("*").order('created_at', desc=True).execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Cloud Connection Error: {e}")
        return pd.DataFrame()

# Initialize Global Settings
if 'balance' not in st.session_state: st.session_state.balance = 50000.0
if 'acc_mode' not in st.session_state: st.session_state.acc_mode = "Funded"
if 'target' not in st.session_state: st.session_state.target = 3000.0

df_raw = fetch_vault()

# ==========================================
# 3. SIDEBAR COMMAND CENTER
# ==========================================
with st.sidebar:
    st.markdown("<h1 style='letter-spacing: 5px; color: #ffffff;'>TRADECORE</h1>", unsafe_allow_html=True)
    st.caption(f"OS V7.0 | ACTIVE SESSION")
    st.divider()
    
    nav = st.radio("SQUADRON MODULES", 
                   ["DASHBOARD", "EXECUTION LOG", "ANALYTICS", "PSYCHOLOGY", "PORTFOLIO", "DATABASE MANAGER"])
    
    st.divider()
    if not df_raw.empty:
        # Filter for Real Trades Only (Calculations)
        t_only = df_raw[df_raw['net_profit'].notna() & (~df_raw['asset'].isin(['PSY_SYSTEM', 'DAY_SYSTEM', 'MINDSET_LOG']))]
        net_pnl = t_only['net_profit'].sum()
        
        st.metric("CURRENT EQUITY", f"€{st.session_state.balance + net_pnl:,.2f}", delta=f"€{net_pnl:,.2f}")
        
        if st.session_state.acc_mode == "Funded":
            prog = (net_pnl / st.session_state.target)
            st.progress(min(max(prog, 0.0), 1.0))
            st.write(f"Objective Progress: {prog*100:.1f}%")
    
    st.divider()
    st.caption("SERVER: NORTH-EUROPE-1")
    st.caption(f"SYNC TIME: {datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# MODULE 1: DASHBOARD
# ==========================================
if nav == "DASHBOARD":
    st.header("📊 PERFORMANCE OVERVIEW")
    t_df = df_raw[df_raw['net_profit'].notna() & (~df_raw['asset'].isin(['PSY_SYSTEM', 'DAY_SYSTEM']))]

    if not t_df.empty:
        c1, c2, c3, c4 = st.columns(4)
        wins = len(t_df[t_df['net_profit'] > 0])
        total = len(t_df)
        wr = (wins / total * 100) if total > 0 else 0
        
        c1.metric("REAL WIN RATE", f"{wr:.1f}%")
        c2.metric("PROFIT FACTOR", round(t_df[t_df['net_profit']>0]['net_profit'].sum() / abs(t_df[t_df['net_profit']<0]['net_profit'].sum()), 2) if not t_df[t_df['net_profit']<0].empty else "MAX")
        c3.metric("TRADES LOGGED", total)
        c4.metric("AVG NET/TRADE", f"€{t_df['net_profit'].mean():,.2f}")

        st.divider()
        t_df = t_df.sort_values('created_at', ascending=True)
        t_df['equity'] = st.session_state.balance + t_df['net_profit'].cumsum()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=t_df['created_at'], y=t_df['equity'], fill='tozeroy', line_color='#ffffff', name='Equity'))
        fig.update_layout(title="EQUITY CURVE", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("NO DATA IN VAULT. PLEASE EXECUTE LOGGING.")

# ==========================================
# MODULE 2: EXECUTION LOG (Auto-Calc)
# ==========================================
elif nav == "EXECUTION LOG":
    st.header("⚡ TERMINAL EXECUTION")
    
    with st.form("exec_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            asset = st.selectbox("Instrument", ["NAS100", "US30", "GER40", "GOLD", "EURUSD", "BTCUSD", "ETHUSD"])
            side = st.radio("Side", ["LONG", "SHORT"], horizontal=True)
            u_type = st.radio("Unit", ["Lots", "Contracts", "Mini Contracts"], horizontal=True)
            u_val = st.number_input("Volume", value=0.10 if u_type == "Lots" else 1.0, step=0.01 if u_type == "Lots" else 1.0)
            
        with col2:
            ent = st.number_input("Entry Price", format="%.5f")
            ext = st.number_input("Exit Price", format="%.5f")
            sl = st.number_input("Stop Loss", format="%.5f")
            pt_val = st.number_input("Point Value (€)", value=1.0)

        with col3:
            # Mathematical Calculation Engine
            if side == "LONG":
                gross = (ext - ent) * u_val * pt_val
                r_money = abs(ent - sl) * u_val * pt_val if sl != 0 else 0
            else:
                gross = (ent - ext) * u_val * pt_val
                r_money = abs(sl - ent) * u_val * pt_val if sl != 0 else 0
            
            fees = st.number_input("Commissions (€)", value=0.0)
            net = gross - fees
            st.metric("CALCULATED NET", f"€{net:.2f}")
            r_pct = (r_money / st.session_state.balance * 100) if st.session_state.balance > 0 else 0
            st.caption(f"Risk: €{r_money:.2f} ({r_pct:.2f}%)")

        st.divider()
        setup = st.text_input("Setup Name")
        notes = st.text_area("Notes")

        if st.form_submit_button("SUBMIT TO CLOUD"):
            data = {
                "asset": asset, "side": side, "entry_price": ent, "exit_price": ext,
                "lots": u_val if u_type == "Lots" else None,
                "contracts": int(u_val) if u_type != "Lots" else None,
                "net_profit": net, "risk_pct": r_pct, "setup_type": setup, "mood_notes": notes
            }
            supabase.table('trades').insert(data).execute()
            st.success("TRADE LOCKED")
            st.rerun()

# ==========================================
# MODULE 3: ANALYTICS
# ==========================================
elif nav == "ANALYTICS":
    st.header("🧬 ADVANCED DATA")
    t_df = df_raw[df_raw['net_profit'].notna() & (~df_raw['asset'].isin(['PSY_SYSTEM', 'DAY_SYSTEM']))]
    
    if not t_df.empty:
        a1, a2 = st.columns(2)
        with a1:
            st.plotly_chart(px.pie(t_df, names='asset', values='net_profit', title="Profit by Asset", hole=0.4, template="plotly_dark"), use_container_width=True)
        with a2:
            st.plotly_chart(px.bar(t_df, x='setup_type', y='net_profit', color='net_profit', title="Strategy Performance", template="plotly_dark"), use_container_width=True)
    else:
        st.warning("DATABASE EMPTY")

# ==========================================
# MODULE 4: PSYCHOLOGY
# ==========================================
elif nav == "PSYCHOLOGY":
    st.header("🧠 MINDSET")
    with st.form("psy"):
        mood = st.select_slider("Mood", ["REVENGE", "TOUGH", "CALM", "FOCUSED", "GOD MODE"], value="CALM")
        txt = st.text_area("Mental State Summary")
        if st.form_submit_button("LOG MINDSET"):
            supabase.table('trades').insert({"psychology_score": mood, "mood_notes": txt, "asset": "PSY_SYSTEM"}).execute()
            st.rerun()

# ==========================================
# MODULE 5: PORTFOLIO
# ==========================================
elif nav == "PORTFOLIO":
    st.header("⚙️ SYSTEM CONFIG")
    st.session_state.acc_mode = st.radio("Type", ["Personal", "Funded"], horizontal=True)
    st.session_state.balance = st.number_input("Balance (€)", value=st.session_state.balance)
    if st.session_state.acc_mode == "Funded":
        st.session_state.target = st.number_input("Target (€)", value=st.session_state.target)
    if st.button("SAVE CONFIG"): st.rerun()

# ==========================================
# MODULE 6: DATABASE MANAGER (The Purge)
# ==========================================
elif nav == "DATABASE MANAGER":
    st.header("🗑️ SYSTEM CLEANUP")
    st.warning("DANGER ZONE: Deleting records is permanent.")
    
    if not df_raw.empty:
        # Display simplified table for selection
        display_df = df_raw[['id', 'created_at', 'asset', 'side', 'net_profit']].copy()
        st.dataframe(display_df, use_container_width=True)
        
        st.divider()
        delete_id = st.number_input("Enter ID to Delete", step=1, value=0)
        
        if st.button("DELETE RECORD PERMANENTLY"):
            if delete_id > 0:
                try:
                    supabase.table('trades').delete().eq('id', delete_id).execute()
                    st.error(f"Record #{delete_id} Purged from Cloud.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.info("Please enter a valid ID from the table above.")
    else:
        st.info("NO RECORDS TO DELETE.")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption(f"TRADECORE MASTERPIECE V7.0 | ARCHITECTURE: 330+ LINES | DB: SUPABASE")

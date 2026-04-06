import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. INITIAL CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="TradeCore | The Professional Trader's Vault",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Black & White Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
    .main { background-color: #000000; color: #ffffff; }
    .stMetric { 
        background-color: #111111; 
        padding: 25px; 
        border-radius: 12px; 
        border: 1px solid #222; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div.stButton > button { 
        background-color: #ffffff; 
        color: #000000; 
        border-radius: 8px; 
        font-weight: 800; 
        padding: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #cccccc; border: none; }
    .sidebar .sidebar-content { background-color: #0a0a0a; }
    .stProgress > div > div > div > div { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. DATABASE CONNECTION (SUPABASE)
# ==========================================
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"

try:
    supabase: Client = create_client(URL, KEY)
except Exception as e:
    st.error(f"CRITICAL ERROR: Database Connection Failed. {e}")

# ==========================================
# 3. CORE FUNCTIONS
# ==========================================
def load_all_data():
    try:
        res = supabase.table('trades').select("*").order('created_at', descending=False).execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.warning(f"Database table might be empty or syncing... {e}")
        return pd.DataFrame()

def commit_trade(data_dict):
    try:
        supabase.table('trades').insert(data_dict).execute()
        st.balloons()
        st.toast("TRADE LOGGED IN THE VAULT", icon="✅")
        return True
    except Exception as e:
        st.error(f"Failed to save trade: {e}")
        return False

# ==========================================
# 4. SESSION STATE & SETTINGS
# ==========================================
if 'starting_cap' not in st.session_state:
    st.session_state.starting_cap = 5000.0

# ==========================================
# 5. SIDEBAR - THE TRADING DESK
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3594/3594449.png", width=60) # Placeholder per il tuo logo
    st.title("TRADECORE")
    st.markdown("---")
    
    st.header("⚡ NEW EXECUTION")
    with st.form("trade_form", clear_on_submit=True):
        asset = st.selectbox("Instrument", ["NAS100", "US30", "GER40", "GOLD", "EURUSD", "BTCUSD"])
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            profit = st.number_input("P/L Realized (€)", value=0.0, step=10.0)
            pips = st.number_input("Pips / Points", value=0.0)
        with col_form2:
            lots = st.number_input("Size / Lots", value=0.1, step=0.1)
            timeframe = st.selectbox("Timeframe", ["M1", "M5", "M15", "H1", "H4", "D1"])
            
        setup = st.text_input("Setup Type", placeholder="e.g. IFVG, Breaker, MSS")
        
        st.markdown("### 🧠 PSYCHOLOGY")
        psy_score = st.select_slider("State of Mind", options=["REVENGE", "TOUGH", "CALM", "FOCUSED", "GOD MODE"], value="CALM")
        review = st.text_area("Post-Trade Review", placeholder="How did you feel? Why did you enter?")
        
        submitted = st.form_submit_button("LOCK TRADE")
        if submitted:
            trade_data = {
                "asset": asset, "profit": profit, "pips": pips, 
                "contracts": lots, "psychology": psy_score, 
                "notes": review, "setup_type": setup, "timeframe": timeframe
            }
            if commit_trade(trade_data):
                st.rerun()

    st.markdown("---")
    st.info("System Status: Online & Encrypted")

# ==========================================
# 6. MAIN DASHBOARD LOGIC
# ==========================================
df = load_all_data()

# Calculations
if not df.empty:
    df['profit'] = pd.to_numeric(df['profit'])
    net_profit = df['profit'].sum()
    current_bal = st.session_state.starting_cap + net_profit
    win_count = len(df[df['profit'] > 0])
    total_count = len(df)
    win_rate = (win_count / total_count) * 100
    avg_trade = df['profit'].mean()
else:
    net_profit, current_bal, win_rate, total_count, avg_trade = 0.0, st.session_state.starting_cap, 0.0, 0, 0.0

# Header Metrics
st.markdown(f"## 🛠️ Operational Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("ACCOUNT BALANCE", f"€{current_bal:,.2f}")
m2.metric("NET PERFORMANCE", f"€{net_profit:,.2f}", delta=f"{net_profit:,.2f}")
m3.metric("WIN RATE", f"{win_rate:.1f}%")
m4.metric("AVG TRADE", f"€{avg_trade:,.2f}")

st.markdown("---")

# ==========================================
# 7. MULTI-SECTION TABS
# ==========================================
tab_perf, tab_journal, tab_analytics, tab_settings = st.tabs([
    "📊 PERFORMANCE", "📝 JOURNAL", "🧬 ANALYTICS", "⚙️ SETTINGS"
])

with tab_perf:
    if not df.empty:
        col_chart, col_stats = st.columns([3, 1])
        
        with col_chart:
            # Equity Curve Calculation
            df['equity'] = st.session_state.starting_cap + df['profit'].cumsum()
            fig = px.line(df, y='equity', title='EQUITY GROWTH CURVE', 
                         template="plotly_dark", color_discrete_sequence=['#ffffff'])
            fig.update_traces(line=dict(width=4))
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Number of Executions",
                yaxis_title="Capital (€)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_stats:
            st.markdown("### 🏆 Streaks")
            st.write(f"**Total Trades:** {total_count}")
            st.write(f"**Best Trade:** €{df['profit'].max():,.2f}")
            st.write(f"**Worst Trade:** €{df['profit'].min():,.2f}")
            st.progress(win_rate/100)
            st.caption(f"Win Rate Accuracy: {win_rate:.0f}%")
    else:
        st.info("The vault is empty. Please log your first execution from the sidebar.")

with tab_journal:
    st.subheader("Historical Records")
    if not df.empty:
        # Displaying the Journal with Psychology icons
        df_display = df.sort_values(by='created_at', ascending=False)
        st.dataframe(df_display[['created_at', 'asset', 'profit', 'setup_type', 'psychology', 'notes']], 
                     use_container_width=True)
    else:
        st.write("No trades found.")

with tab_analytics:
    st.subheader("Deep Data Analysis")
    if not df.empty:
        col_an1, col_an2 = st.columns(2)
        with col_an1:
            asset_dist = px.pie(df, names='asset', values='profit', title='Profit Distribution by Asset', template="plotly_dark")
            st.plotly_chart(asset_dist, use_container_width=True)
        with col_an2:
            psy_dist = px.bar(df, x='psychology', y='profit', title='Profit vs Mindset', template="plotly_dark", color_discrete_sequence=['#ffffff'])
            st.plotly_chart(psy_dist, use_container_width=True)
    else:
        st.info("Awaiting more data for deep analysis.")

with tab_settings:
    st.subheader("Vault Configuration")
    col_set1, col_set2 = st.columns(2)
    with col_set1:
        st.session_state.starting_cap = st.number_input("Starting Capital (€)", value=st.session_state.starting_cap)
        st.write("Updating this will recalibrate your entire Equity Curve.")
    with col_set2:
        st.write("### Account Identity")
        st.write("User: Master Trader")
        st.write(f"Account ID: {URL.split('//')[1].split('.')[0]}")
    
    if st.button("SAVE CONFIGURATION"):
        st.success("Configuration updated successfully.")
        st.rerun()

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption("TradeCore Architecture • Developed for Elite Performance")

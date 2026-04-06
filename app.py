import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. CONFIGURAZIONE INTERFACCIA PRO
# ==========================================
st.set_page_config(
    page_title="TradeCore | Elite Dashboard",
    page_icon="📈",
    layout="wide"
)

# CSS per look Total Black e scritte bianche
st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stMetric { 
        background-color: #0a0a0a; 
        padding: 20px; 
        border-radius: 10px; 
        border: 1px solid #333; 
    }
    div.stButton > button { 
        background-color: #ffffff; 
        color: #000000; 
        border-radius: 4px; 
        font-weight: bold; 
        width: 100%;
        border: none;
    }
    div.stButton > button:hover { background-color: #cccccc; }
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { color: #888; font-weight: bold; }
    .stTabs [aria-selected="true"] { color: #fff; border-bottom-color: #fff; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CONNESSIONE SUPABASE
# ==========================================
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"

@st.cache_resource
def init_connection():
    return create_client(URL, KEY)

supabase = init_connection()

# ==========================================
# 3. FUNZIONI DATI
# ==========================================
def get_trades():
    try:
        # Recupero dati ordinati per data
        query = supabase.table('trades').select("*").order('created_at').execute()
        return pd.DataFrame(query.data)
    except Exception:
        return pd.DataFrame()

def push_trade(payload):
    try:
        supabase.table('trades').insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Errore invio: {e}")
        return False

# ==========================================
# 4. LOGICA DI SESSIONE
# ==========================================
if 'balance_init' not in st.session_state:
    st.session_state.balance_init = 5000.0

df = get_trades()

# Calcolo metriche in tempo reale
if not df.empty:
    df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0)
    net_profit = df['profit'].sum()
    current_bal = st.session_state.balance_init + net_profit
    win_rate = (len(df[df['profit'] > 0]) / len(df)) * 100
    trades_count = len(df)
else:
    net_profit, current_bal, win_rate, trades_count = 0.0, st.session_state.balance_init, 0.0, 0

# ==========================================
# 5. LAYOUT DASHBOARD
# ==========================================
st.title("TRADECORE SYSTEM")
st.caption(f"LIVE CLOUD CONNECTION | {datetime.now().strftime('%d %B %Y')}")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("TOTAL EQUITY", f"€{current_bal:,.2f}")
col_m2.metric("NET P/L", f"€{net_profit:,.2f}", delta=f"{net_profit:,.2f}")
col_m3.metric("WIN RATE", f"{win_rate:.1f}%")
col_m4.metric("EXECUTIONS", trades_count)

st.divider()

# ==========================================
# 6. SIDEBAR: TERMINALE DI IMMISSIONE
# ==========================================
with st.sidebar:
    st.header("⚡ EXECUTION UNIT")
    with st.form("trade_entry", clear_on_submit=True):
        market = st.selectbox("Market Asset", ["NAS100", "US30", "GER40", "GOLD", "EURUSD", "BTCUSD"])
        
        c1, c2 = st.columns(2)
        with c1:
            p_val = st.number_input("Profit/Loss (€)", step=1.0)
            pip_val = st.number_input("Pips/Points", step=0.1)
        with c2:
            lot_val = st.number_input("Lots Size", value=0.1, step=0.01)
            tf_val = st.selectbox("Timeframe", ["M1", "M5", "M15", "H1", "H4", "D1"])
        
        setup_name = st.text_input("Setup Details", placeholder="e.g. IFVG + MSS")
        
        st.markdown("### 🧠 PSYCHOLOGY")
        mood = st.select_slider("State of Mind", options=["REVENGE", "TOUGH", "CALM", "FOCUSED", "GOD MODE"], value="CALM")
        comment = st.text_area("Trade Notes", placeholder="Descrivi il feeling dell'operazione...")
        
        if st.form_submit_button("LOCK DATA INTO CLOUD"):
            payload = {
                "asset": market, "profit": p_val, "pips": pip_val,
                "contracts": lot_val, "timeframe": tf_val, "setup_type": setup_name,
                "psychology": mood, "notes": comment
            }
            if push_trade(payload):
                st.toast("DATA ENCRYPTED & SAVED", icon="🛡️")
                st.rerun()

# ==========================================
# 7. SEZIONI ANALITICHE (TABS)
# ==========================================
t_growth, t_journal, t_data, t_settings = st.tabs(["📊 GROWTH", "📜 JOURNAL", "🧬 ANALYTICS", "⚙️ SETTINGS"])

with t_growth:
    if not df.empty:
        df['equity_line'] = st.session_state.balance_init + df['profit'].cumsum()
        fig_growth = px.line(df, y='equity_line', title='CAPITAL EVOLUTION', 
                            template="plotly_dark", color_discrete_sequence=['#ffffff'])
        fig_growth.update_traces(line=dict(width=3))
        st.plotly_chart(fig_growth, use_container_width=True)
    else:
        st.info("Inizia caricando il tuo trade da +142 dalla sidebar laterale.")

with t_journal:
    st.subheader("Historical Logbook")
    if not df.empty:
        # Visualizzazione pulita invertita (ultimo in alto)
        st.dataframe(df[['created_at', 'asset', 'profit', 'setup_type', 'psychology', 'notes']].iloc[::-1], use_container_width=True)
    else:
        st.write("No records found in database.")

with t_data:
    if not df.empty:
        ca1, ca2 = st.columns(2)
        with ca1:
            st.subheader("Profit by Asset")
            fig_asset = px.bar(df.groupby('asset')['profit'].sum().reset_index(), x='asset', y='profit', template="plotly_dark")
            st.plotly_chart(fig_asset, use_container_width=True)
        with ca2:
            st.subheader("Psychology Impact")
            fig_psy = px.box(df, x='psychology', y='profit', template="plotly_dark")
            st.plotly_chart(fig_psy, use_container_width=True)
    else:
        st.info("Awaiting more data for deep analysis.")

with t_settings:
    st.subheader("Vault Configuration")
    st.session_state.balance_init = st.number_input("Starting Capital (€)", value=st.session_state.balance_init)
    st.markdown(f"**Database Status:** Connected to `{URL.split('//')[1]}`")
    if st.button("Refresh Connection"):
        st.rerun()

# ==========================================
# 8. FOOTER
# ==========================================
st.markdown("---")
st.caption("TradeCore Architecture | v1.7 | Developed for Elite Performance")

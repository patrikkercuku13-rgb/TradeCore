import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. CONFIGURAZIONE ESTETICA (TOTAL BLACK)
# ==========================================
st.set_page_config(
    page_title="TradeCore | The Professional Vault",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stMetric { 
        background-color: #0a0a0a; 
        padding: 20px; 
        border-radius: 10px; 
        border: 1px solid #222; 
    }
    div.stButton > button { 
        background-color: #ffffff; 
        color: #000000; 
        border-radius: 5px; 
        font-weight: bold; 
        width: 100%;
        height: 3em;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { color: #888; }
    .stTabs [data-baseweb="tab"]:hover { color: #fff; }
    .stTabs [aria-selected="true"] { color: #fff; border-bottom-color: #fff; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CONNESSIONE DATABASE
# ==========================================
URL = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"

@st.cache_resource
def get_supabase():
    return create_client(URL, KEY)

supabase = get_supabase()

# ==========================================
# 3. FUNZIONI OPERATIVE (FIXED ORDER)
# ==========================================
def load_data():
    try:
        # CORREZIONE: rimosso 'descending', aggiunto 'desc' nel metodo corretto
        res = supabase.table('trades').select("*").order('created_at').execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        return pd.DataFrame()

def save_to_db(payload):
    try:
        supabase.table('trades').insert(payload).execute()
        return True
    except Exception as e:
        st.error(f"Errore Database: {e}")
        return False

# ==========================================
# 4. LOGICA DI CALCOLO & SESSIONE
# ==========================================
if 'capitale_iniziale' not in st.session_state:
    st.session_state.capitale_iniziale = 5000.0

df = load_data()

# Processamento Dati
if not df.empty:
    df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0)
    total_pl = df['profit'].sum()
    current_balance = st.session_state.capitale_iniziale + total_pl
    win_rate = (len(df[df['profit'] > 0]) / len(df)) * 100
    avg_win = df[df['profit'] > 0]['profit'].mean() if not df[df['profit'] > 0].empty else 0
else:
    total_pl, current_balance, win_rate, avg_win = 0, st.session_state.capitale_iniziale, 0, 0

# ==========================================
# 5. HEADER & METRICHE PRO
# ==========================================
st.title("TRADECORE ENGINE")
st.caption("CONNECTED TO SUPABASE CLOUD • VERSION 1.6")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("EQUITY", f"€{current_balance:,.2f}")
with m2:
    st.metric("NET P/L", f"€{total_pl:,.2f}", delta=f"{total_pl:,.2f}")
with m3:
    st.metric("WIN RATE", f"{win_rate:.1f}%")
with m4:
    st.metric("AVG WIN", f"€{avg_win:,.2f}")

st.divider()

# ==========================================
# 6. SIDEBAR: INSERIMENTO PROFESSIONALE
# ==========================================
with st.sidebar:
    st.header("⚡ EXECUTION DESK")
    with st.form("input_form"):
        asset = st.selectbox("Asset", ["NAS100", "US30", "GER40", "GOLD", "EURUSD", "BTCUSD"])
        col1, col2 = st.columns(2)
        with col1:
            p_l = st.number_input("Profit/Loss (€)", step=1.0)
            pips = st.number_input("Pips/Points", step=0.1)
        with col2:
            lots = st.number_input("Lots", value=0.1, step=0.01)
            tf = st.selectbox("TF", ["M1", "M5", "M15", "H1", "H4", "D1"])
            
        setup = st.text_input("Setup Name", placeholder="es. IFVG + MSS")
        
        st.subheader("🧠 PSYCHOLOGY")
        psy = st.select_slider("Mood", options=["REVENGE", "TOUGH", "CALM", "FOCUSED", "GOD MODE"], value="CALM")
        notes = st.text_area("Review", placeholder="Perché hai preso questo trade?")
        
        if st.form_submit_button("COMMIT TRADE"):
            new_data = {
                "asset": asset, "profit": p_l, "pips": pips, 
                "contracts": lots, "timeframe": tf, "setup_type": setup,
                "psychology": psy, "notes": notes
            }
            if save_to_db(new_data):
                st.success("DATA SECURED")
                st.rerun()

# ==========================================
# 7. SEZIONI ANALITICHE (TABS)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["📈 GROWTH", "📝 JOURNAL", "📊 DATA", "⚙️ SETTINGS"])

with tab1:
    if not df.empty:
        df['equity_curve'] = st.session_state.capitale_iniziale + df['profit'].cumsum()
        fig = px.line(df, y='equity_curve', title='CAPITAL GROWTH OVER TIME',
                     color_discrete_sequence=['#ffffff'], template="plotly_dark")
        fig.update_layout(xaxis_title="Trades", yaxis_title="Balance (€)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Inizia registrando il tuo trade da +142 nella sidebar!")

with tab2:
    st.subheader("Trading Journal")
    if not df.empty:
        # Visualizziamo i dati in modo pulito
        journal_df = df[['created_at', 'asset', 'profit', 'setup_type', 'psychology', 'notes']].iloc[::-1]
        st.table(journal_df)
    else:
        st.write("Ancora nessun record.")

with tab3:
    st.subheader("Performance Metrics")
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            asset_stats = df.groupby('asset')['profit'].sum().reset_index()
            fig_bar = px.bar(asset_stats, x='asset', y='profit', title="Profit by Asset", color='

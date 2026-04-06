import streamlit as st
from supabase import create_client, Client
import datetime

# 1. DATABASE CONNECTION
URL: str = "https://aurjuibhbuinxzirpjkt.supabase.co"
KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1cmp1aWJoYnVpbnh6aXJwamt0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU0ODE0MjEsImV4cCI6MjA5MTA1NzQyMX0.xSZBDGACcF6yDpkvuKQZottdKINFM0JM3iuRrI987lE"
supabase: Client = create_client(URL, KEY)

# 2. PAGE CONFIG & DARK THEME
st.set_page_config(page_title="TradeCore | Professional Edge", page_icon="🔲", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    .stButton>button { background-color: #ffffff; color: #000000; border-radius: 5px; width: 100%; font-weight: bold; border: none; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>textarea { background-color: #111111; color: white; border: 1px solid #333333; }
    .stSelectbox>div>div>div { background-color: #111111; color: white; }
    h1, h2, h3 { color: #ffffff !important; font-family: 'Inter', sans-serif; }
    .stMetric { background-color: #111111; padding: 15px; border-radius: 10px; border: 1px solid #222222; }
    </style>
    """, unsafe_allow_safe_area=True)

# --- HEADER ---
col_l, col_r = st.columns([1, 5])
with col_l:
    st.write("# 🔲")
with col_r:
    st.title("TRADECORE")
    st.write(f"Today is: **{datetime.date.today().strftime('%A, %d %B %Y')}** | *Rule your edge. Master your risk.*")

st.divider()

# --- SIDEBAR: CALCULATOR ---
with st.sidebar:
    st.header("🧮 Risk Calculator")
    balance = st.number_input("Account Balance ($)", value=50000.0, step=1000.0)
    risk_pct = st.slider("Risk per Trade (%)", 0.1, 5.0, 1.0)
    stop_loss = st.number_input("Stop Loss (Points/Pips)", value=10.0, step=1.0)
    
    risk_dollars = balance * (risk_pct / 100)
    # Calcolo lotti semplificato (es. Nasdaq 1$ per punto per lotto)
    suggested_lots = risk_dollars / (stop_loss if stop_loss > 0 else 1)
    
    st.metric("Risk Amount", f"${risk_dollars:.2f}")
    st.metric("Suggested Lots", f"{suggested_lots:.2f}")
    st.info("Ensure lot size matches your broker's contract specification.")

# --- MAIN INTERFACE: 3 COLUMNS ---
tab1, tab2 = st.tabs(["📈 Trade Logger", "📊 Performance Review"])

with tab1:
    col_input, col_psycho = st.columns([1, 1], gap="large")

    with col_input:
        st.subheader("Step 1: Execution Details")
        with st.form("trade_form", clear_on_submit=True):
            asset = st.selectbox("Asset Class", ["NAS100 (Nasdaq)", "EURUSD", "GOLD (XAUUSD)", "S&P 500", "BTCUSD"])
            p_l = st.number_input("Realized P/L ($)", value=0.0, step=10.0)
            setup = st.text_input("Setup Name (e.g., IFVG, Silver Bullet, Liquidity Sweep)")
            
            st.write("---")
            st.subheader("Step 2: Mental State")
            mood = st.select_slider("Daily Mental Weather", 
                                   options=["Stormy ⛈️", "Cloudy ☁️", "Neutral 😐", "Clear Sky 🌤️", "Peak Performance ⚡"])
            
            # THE PSYCHO QUESTIONS (The core of our work)
            st.write("**Self-Reflection Questions:**")
            q1 = st.checkbox("Did I follow my Trading Plan 100%?")
            q2 = st.checkbox("Did I wait for my actual setup (no FOMO)?")
            q3 = st.checkbox("Am I revenge trading or over-leveraging?")
            
            error_type = st.selectbox("If you failed, why?", 
                                     ["N/A", "FOMO", "Early Exit", "Late Entry", "Over-leverage", "Lack of Patience"])
            
            notes = st.text_area("Final Thoughts / Trade Review")
            
            submit = st.form_submit_button("LOCK TRADE INTO CLOUD")

    with col_psycho:
        st.subheader("🧠 TradeCore Insights")
        if p_l > 0:
            st.success(f"Great job! You secured **${p_l}**. Keep the discipline.")
        elif p_l < 0:
            st.error(f"Loss of **${abs(p_l)}**. Remember: A stop loss is just a business expense.")
        
        st.write("---")
        st.write("### Your Psychology Summary Today")
        st.write(f"**Current Mood:** {mood}")
        status = "Disciplined ✅" if q1 and q2 else "Plan Violated ⚠️"
        st.write(f"**Execution Status:** {status}")
        
        if error_type != "N/A":
            st.warning(f"**Focus Area:** You identified '{error_type}' as a weakness today. Fix it for the next session.")

# --- DATABASE LOGIC ---
if submit:
    # Aggreghiamo i dati psicologici per il database
    psycho_summary = f"Mood: {mood} | Plan: {q1} | Patience: {q2} | Error: {error_type}"
    
    trade_data = {
        "asset": asset,
        "profit": p_l,
        "notes": f"[{setup}] {notes} || {psycho_summary}"
    }
    
    try:
        supabase.table("trades").insert(trade_data).execute()
        st.toast("Data synced with Supabase successfully!", icon='✅')
        if p_l > 0:
            st.balloons()
    except Exception as e:
        st.error(f"Sync Error: {e}")

with tab2:
    st.subheader("History & Equity Curve (Live Data)")
    try:
        response = supabase.table("trades").select("*").order("id", desc=True).execute()
        data = response.data
        
        if data:
            for t in data:
                with st.expander(f"{t['asset']} | P/L: ${t['profit']} | {t['id']} "):
                    st.write(f"**Details:** {t['notes']}")
                    # Qui potremmo aggiungere un tasto per eliminare il trade se sbagliato
        else:
            st.info("The database is empty. Log your first trade above!")
    except:
        st.warning("Connecting to cloud... please wait.")

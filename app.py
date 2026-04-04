import streamlit as st
import pandas as pd
import yfinance as yf

# PROFESSIONAL CONFIG
st.set_page_config(page_title="Alpha Trader Hub", layout="wide")

# SESSION STATE INITIALIZATION
if 'trades' not in st.session_state: st.session_state.trades = []
if 'daily_recaps' not in st.session_state: st.session_state.daily_recaps = []
if 'account_setup' not in st.session_state: 
    st.session_state.account_setup = {"balance": 25000.0, "target": 1500.0, "max_drawdown": 1250.0, "type": "Prop Firm"}

def get_live_price(ticker):
    try:
        data = yf.Ticker(ticker)
        return round(data.history(period="1d")['Close'].iloc[-1], 5)
    except: return 0.0

# --- SIDEBAR: ACCOUNT SETUP ---
st.sidebar.title("💳 Account Settings")
acc_type = st.sidebar.selectbox("Account Type", ["Prop Firm", "Live", "Demo"])

with st.sidebar.expander("Configure Account", expanded=True):
    balance = st.number_input("Initial Balance ($)", value=st.session_state.account_setup["balance"])
    
    # Only show Target and DD for Prop Firms
    if acc_type == "Prop Firm":
        target_prof = st.number_input("Profit Target ($)", value=1500.0)
        max_dd = st.number_input("Max Drawdown ($)", value=1250.0)
    else:
        target_prof = 0.0
        max_dd = 0.0
        
    if st.sidebar.button("Update Account"):
        st.session_state.account_setup = {
            "balance": balance, "target": target_prof, "max_drawdown": max_dd, "type": acc_type
        }
        st.success("Account Updated!")

st.sidebar.divider()
page = st.sidebar.radio("Navigation", ["🏠 Dashboard", "📝 Trade Log", "🧠 Psychology"])

# --- 1. DASHBOARD PAGE ---
if page == "🏠 Dashboard":
    st.title(f"📊 {st.session_state.account_setup['type']} Analytics")
    
    setup = st.session_state.account_setup
    df = pd.DataFrame(st.session_state.trades)
    current_pnl = df["Net_PnL"].sum() if not df.empty else 0.0
    current_balance = setup['balance'] + current_pnl
    
    # Top Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Balance", f"$ {current_balance:.2f}", f"{current_pnl:.2f}")
    
    if setup['type'] == "Prop Firm":
        # Prop Firm Specific Metrics
        miss_target = setup['target'] - current_pnl
        perc_t = (current_pnl / setup['target']) * 100 if current_pnl > 0 else 0
        c2.metric("Target Remaining", f"$ {max(0, miss_target):.2f}", f"{min(100, perc_t):.1f}% Done")
        
        drawdown_val = setup['balance'] - current_balance if current_balance < setup['balance'] else 0
        margine_dd = setup['max_drawdown'] - drawdown_val
        c3.metric("Drawdown Margin", f"$ {max(0, margine_dd):.2f}", f"Limit: ${setup['max_drawdown']}", delta_color="inverse")
    else:
        # Live/Demo Metrics
        winrate = (len(df[df['Net_PnL'] > 0]) / len(df)) * 100 if not df.empty else 0
        c2.metric("Winrate", f"{winrate:.1f}%")
        c3.metric("Total Trades", len(df))

    # Equity Curve
    st.subheader("📈 Real-Time Equity Curve")
    if not df.empty:
        equity_list = [setup['balance']] + (setup['balance'] + df["Net_PnL"].cumsum()).tolist()
        st.line_chart(equity_list)
    else:
        st.info("No trades recorded yet. The curve starts at your initial balance.")

# --- 2. TRADE LOG PAGE (ENHANCED) ---
elif page == "📝 Trade Log":
    st.title("📓 Professional Trade Log")
    
    with st.form("trade_entry"):
        col_m1, col_m2, col_m3 = st.columns(3)
        asset_cat = col_m1.selectbox("Asset Class", ["Futures", "CFD / Forex"])
        ticker = col_m2.text_input("Ticker (e.g. NQ=F, EURUSD=X)", "NQ=F")
        direction = col_m3.selectbox("Direction", ["Long", "Short"])
        
        live_p = get_live_price(ticker)
        st.write(f"Current Market Price: **{live_p}**")
        
        c_in, c_out, c_fee = st.columns(3)
        p_in = c_in.number_input("Entry Price", value=live_p, format="%.5f")
        p_out = c_out.number_input("Exit Price", format="%.5f")
        commissions = c_fee.number_input("Commissions ($)", value=0.0, step=0.1)
        
        # DYNAMIC INPUTS BASED ON ASSET CLASS
        if asset_cat == "Futures":
            f_type = st.radio("Contract Type", ["Standard (Full)", "Micro"], horizontal=True)
            size = st.number_input("Number of Contracts", value=1, step=1) # Integer for Futures
            tick_val = 20 if f_type == "Standard (Full)" else 2 # e.g. NQ=20, MNQ=2
        else:
            # CFD / Forex Logic
            size = st.number_input("Lots", value=0.10, step=0.01, format="%.2f") # Float for CFD
            tick_val = 10 # Standard Pip value for 1 Lot
            
        if st.form_submit_button("Submit Trade"):
            # PnL Calculation
            price_diff = (p_out - p_in) if direction == "Long" else (p_in - p_out)
            
            if asset_cat == "Futures":
                gross_pnl = price_diff * tick_val * size
            else:
                # Forex Pips calculation
                gross_pnl = (price_diff * 10000) * size * (tick_val / 10)
            
            net_pnl = gross_pnl - commissions
            
            st.session_state.trades.append({
                "Asset": ticker, 
                "Dir": direction, 
                "Size": size, 
                "Gross_PnL": round(gross_pnl, 2),
                "Commissions": commissions,
                "Net_PnL": round(net_pnl, 2),
                "Type": asset_cat
            })
            st.success(f"Trade Logged! Net PnL: ${net_pnl:.2f}")

# --- 3. PSYCHOLOGY PAGE ---
elif page == "🧠 Psychology":
    st.title("🧠 Psychology & Discipline")
    st.subheader("Daily Market Mood")
    
    m1, m2, m3 = st.columns(3)
    if m1.button("🔴 TOUGH DAY (⛈️)"): st.session_state.last_mood = "Tough Day"
    if m2.button("🟡 MIXED (☁️)"): st.session_state.last_mood = "Mixed"
    if m3.button("🟢 GOOD DAY (☀️)"): st.session_state.last_mood = "Good Day"
    
    current_mood = st.session_state.get('last_mood', 'Not Set')
    st.write(f"Current Mindset: **{current_mood}**")
    
    recap_notes = st.text_area("Write your Daily Recap (Notes, Mistakes, Lessons)...", height=150)
    
    if st.button("Save Daily Recap"):
        st.session_state.daily_recaps.append({
            "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "Mood": current_mood, 
            "Notes": recap_notes
        })
        st.balloons()
        st.success("Recap Saved!")
        
    if st.session_state.daily_recaps:
        st.table(pd.DataFrame(st.session_state.daily_recaps).iloc[::-1])
        

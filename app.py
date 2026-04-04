import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# PROFESSIONAL CONFIG
st.set_page_config(page_title="Alpha Trader Hub", layout="wide")

# SESSION STATE INITIALIZATION
if 'trades' not in st.session_state: st.session_state.trades = []
if 'daily_recaps' not in st.session_state: st.session_state.daily_recaps = []
if 'account_setup' not in st.session_state: 
    st.session_state.account_setup = {"balance": 25000.0, "target": 1500.0, "max_drawdown": 1250.0, "type": "Prop Firm"}

def get_live_price(ticker):
    try:
        # Use a localized method for reliability
        data = yf.Ticker(ticker)
        # Fetching only the latest close price efficiently
        price = data.history(period="1d")['Close'].iloc[-1]
        return round(price, 5)
    except: return 0.0

# --- SIDEBAR: ACCOUNT SETUP ---
st.sidebar.title("💳 Account Settings")
acc_type = st.sidebar.selectbox("Account Type", ["Prop Firm", "Live", "Demo"], index=0)

with st.sidebar.expander("Configure Account", expanded=True):
    balance = st.number_input("Initial Balance ($)", value=st.session_state.account_setup["balance"], step=100.0)
    
    # Only show Target and DD for Prop Firms
    if acc_type == "Prop Firm":
        target_prof = st.number_input("Profit Target ($)", value=1500.0, step=10.0)
        max_dd = st.number_input("Max Drawdown ($)", value=1250.0, step=10.0)
    else:
        target_prof = 0.0
        max_dd = 0.0
        
    if st.sidebar.button("Update Account"):
        # Resetting trades if balance changes to keep the graph accurate (optional)
        # st.session_state.trades = []
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
    initial_balance = setup['balance']
    df = pd.DataFrame(st.session_state.trades)
    
    current_pnl = df["Net_PnL"].sum() if not df.empty else 0.0
    current_balance = initial_balance + current_pnl
    
    # Top Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Balance", f"$ {current_balance:.2f}", f"${current_pnl:.2f} (Total PnL)")
    
    if setup['type'] == "Prop Firm":
        # Prop Firm Specific Metrics
        miss_target = setup['target'] - current_pnl
        perc_t = (current_pnl / setup['target']) * 100 if current_pnl > 0 else 0
        c2.metric("Target Remaining", f"$ {max(0, miss_target):.2f}", f"{min(100, perc_t):.1f}% Done")
        
        # Drawdown calculation based on initial balance floor
        drawdown_floor = initial_balance - setup['max_drawdown']
        margine_dd = current_balance - drawdown_floor
        
        c3.metric("Drawdown Margin Left", f"$ {max(0, margine_dd):.2f}", f"Floor: ${drawdown_floor:.2f}", delta_color="inverse")
    else:
        # Live/Demo Metrics
        winrate = (len(df[df['Net_PnL'] > 0]) / len(df)) * 100 if not df.empty else 0
        c2.metric("Winrate", f"{winrate:.1f}%")
        c3.metric("Total Trades", len(df))

    # --- EQUITY CURVE (ANCHORED TO BALANCE) ---
    st.subheader("📈 Absolute Equity Curve (Actual Balance)")
    
    if not df.empty:
        # 1. Create a Series of Net PnL
        pnl_series = df["Net_PnL"]
        # 2. Calculate the Cumulative PnL
        cumulative_pnl = pnl_series.cumsum()
        # 3. Add the Initial Balance to every cumulative point
        actual_equity = initial_balance + cumulative_pnl
        
        # 4. Create the final plot data, starting exactly at Initial Balance
        plot_data = pd.concat([pd.Series([initial_balance]), actual_equity], ignore_index=True)
        
        # Plotting the Line Chart
        st.line_chart(plot_data)
        
        # 5. Display detailed trades for verification
        st.subheader("Logged Trades")
        st.dataframe(df[["Asset", "Dir", "Size", "Net_PnL", "Timestamp"]].iloc[::-1], use_container_width=True)
        
    else:
        # Default state with no trades
        st.info("No trades logged yet. Below is your starting capital.")
        # Make a simple graph showing just the starting balance over a 'placeholder' time
        st.line_chart([initial_balance, initial_balance])

# --- 2. TRADE LOG PAGE ---
elif page == "📝 Trade Log":
    st.title("📓 Professional Trade Log")
    
    with st.form("trade_entry"):
        col_m1, col_m2, col_m3 = st.columns(3)
        asset_cat = col_m1.selectbox("Asset Class", ["Futures", "CFD / Forex"])
        ticker = col_m2.text_input("Ticker (e.g. MNQ=F, EURUSD=X)", "MNQ=F")
        direction = col_m3.selectbox("Direction", ["Long", "Short"])
        
        live_p = get_live_price(ticker)
        st.write(f"Current Market Price: **{live_p}**")
        
        c_in, c_out, c_fee = st.columns(3)
        p_in = c_in.number_input("Entry Price", value=live_p, format="%.5f")
        p_out = c_out.number_input("Exit Price", format="%.5f")
        commissions = c_fee.number_input("Commissions ($)", value=1.0, step=0.1)
        
        # DYNAMIC INPUTS BASED ON ASSET CLASS
        if asset_cat == "Futures":
            f_type = st.radio("Contract Type", ["Standard (Full)", "Micro"], index=1, horizontal=True) # Default MNQ
            size = st.number_input("Number of Contracts", value=1, step=1) # Integer for Futures
            tick_val = 20 if f_type == "Standard (Full)" else 2 # e.g. NQ=20, MNQ=2
        else:
            # CFD / Forex Logic
            size = st.number_input("Lots", value=0.01, step=0.01, format="%.2f") # Float for CFD
            tick_val = 10 # Standard Pip value for 1 Lot
            
        submit_button = st.form_submit_button("Submit Trade")
        
        if submit_button:
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
                "Net_PnL": round(net_pnl, 2),
                "Type": asset_cat,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.success(f"Trade Logged! Net PnL: ${net_pnl:.2f}")

# --- 3. PSYCHOLOGY PAGE ---
elif page == "🧠 Psychology":
    st.title("🧠 Market Mindset")
    # ... (Keeping the Psychology section same as last version)
    st.subheader("Mental Recap")
    m1, m2, m3 = st.columns(3)
    if m1.button("🔴 TOUGH DAY (⛈️)"): st.session_state.last_mood = "Tough Day"
    if m2.button("🟡 MIXED (☁️)"): st.session_state.last_mood = "Mixed"
    if m3.button("🟢 GOOD DAY (☀️)"): st.session_state.last_mood = "Good Day"
    current_mood = st.session_state.get('last_mood', 'Not Set')
    st.write(f"Mindset: **{current_mood}**")
    recap_notes = st.text_area("Write your Daily Recap...", height=150)
    if st.button("Save Recap"):
        st.session_state.daily_recaps.append({
            "Date": pd.Timestamp.now().strftime("%Y-%m-%d"),
            "Mood": current_mood, 
            "Notes": recap_notes
        })
        st.balloons(); st.success("Saved!")
    if st.session_state.daily_recaps:
        st.table(pd.DataFrame(st.session_state.daily_recaps).iloc[::-1])

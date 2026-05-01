import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Page Config
st.set_page_config(page_title="Stock Intrinsic Value & Peer Comparison Tool", layout="wide")
st.title("📈 Stock Analysis & Intrinsic Value Calculator")

# Function to fetch stock data
@st.cache_data
def get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except:
        return None

# Function to calculate Graham Intrinsic Value
def calculate_graham_value(eps, bvps):
    if eps and bvps and eps > 0 and bvps > 0:
        return np.sqrt(22.5 * eps * bvps)
    return "N/A"

# Sidebar Inputs
st.sidebar.header("🔍 Stock Search")
# Indian stocks in Yahoo Finance need '.NS' (NSE) or '.BO' (BSE) suffix
main_ticker = st.sidebar.text_input("Enter Main Stock Ticker (e.g., DEEPAKNTR.NS):", "DEEPAKNTR.NS").upper()
peer_tickers = st.sidebar.text_input("Enter Peer Tickers (comma separated):", "TATACHEM.NS, SRF.NS, IRFC.NS").upper()

if main_ticker:
    info = get_stock_data(main_ticker)
    
    if info:
        st.header(f"Company: {info.get('longName', main_ticker)}")
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        
        # Fundamental Metrics
        eps = info.get('trailingEps', 0)
        bvps = info.get('bookValue', 0)
        pe_ratio = info.get('trailingPE', 0)
        pb_ratio = info.get('priceToBook', 0)
        roe = info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0
        debt_eq = info.get('debtToEquity', 0)
        
        intrinsic_value = calculate_graham_value(eps, bvps)
        
        # Display Main Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Price", f"₹{current_price}")
        
        if isinstance(intrinsic_value, float):
            margin_of_safety = ((intrinsic_value - current_price) / intrinsic_value) * 100
            col2.metric("Intrinsic Value (Graham)", f"₹{intrinsic_value:.2f}")
            col3.metric("Margin of Safety", f"{margin_of_safety:.2f}%")
            
            if current_price < intrinsic_value:
                st.success(f"✅ The stock is UNDERVALUED. It is trading below its Intrinsic Value of ₹{intrinsic_value:.2f}.")
            else:
                st.warning(f"⚠️ The stock is OVERVALUED. It is trading above its Intrinsic Value of ₹{intrinsic_value:.2f}.")
        else:
            col2.metric("Intrinsic Value", "N/A")
            st.info("Intrinsic value cannot be calculated (EPS or Book Value is negative/missing).")

        # Ratios
        st.subheader("📊 Fundamental Ratios")
        r_col1, r_col2, r_col3, r_col4 = st.columns(4)
        r_col1.metric("P/E Ratio", round(pe_ratio, 2) if pe_ratio else "N/A")
        r_col2.metric("P/B Ratio", round(pb_ratio, 2) if pb_ratio else "N/A")
        r_col3.metric("ROE (%)", f"{round(roe, 2)}%" if roe else "N/A")
        r_col4.metric("Debt to Equity", round(debt_eq, 2) if debt_eq else "N/A")

        st.markdown("---")
        
        # Peer Comparison
        st.subheader("⚖️ Peer Comparison")
        peers = [t.strip() for t in peer_tickers.split(",")]
        all_tickers = [main_ticker] + peers
        
        comparison_data = []
        for t in all_tickers:
            peer_info = get_stock_data(t)
            if peer_info:
                p_eps = peer_info.get('trailingEps', 0)
                p_bvps = peer_info.get('bookValue', 0)
                p_price = peer_info.get('currentPrice', peer_info.get('regularMarketPrice', 0))
                p_iv = calculate_graham_value(p_eps, p_bvps)
                
                comparison_data.append({
                    "Ticker": t,
                    "Price (₹)": p_price,
                    "Intrinsic Value (₹)": round(p_iv, 2) if isinstance(p_iv, float) else "N/A",
                    "P/E Ratio": round(peer_info.get('trailingPE', 0), 2) if peer_info.get('trailingPE') else "N/A",
                    "P/B Ratio": round(peer_info.get('priceToBook', 0), 2) if peer_info.get('priceToBook') else "N/A",
                    "ROE (%)": round((peer_info.get('returnOnEquity', 0) or 0) * 100, 2),
                    "Debt/Equity": round(peer_info.get('debtToEquity', 0), 2) if peer_info.get('debtToEquity') else "N/A"
                })
                
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)

    else:
        st.error("Could not fetch data. Please check the Ticker symbol (Make sure to add '.NS' for NSE stocks).")
          

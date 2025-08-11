"""Stock data fetching module using yfinance."""

import yfinance as yf
import pandas as pd
import streamlit as st
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import requests
from config.settings import DEFAULT_PERIOD, MIN_DATA_POINTS, ERROR_MESSAGES


class StockDataFetcher:
    """Class for fetching and processing stock data."""
    
    def __init__(self):
        self.cache = {}
        
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def fetch_stock_data(_self, symbol: str, period: str = DEFAULT_PERIOD) -> Optional[pd.DataFrame]:
        """
        Fetch historical stock data.
        
        Args:
            symbol: Stock symbol (e.g., "2881.TW")
            period: Time period for data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            DataFrame with stock data or None if failed
        """
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            
            if data.empty:
                st.error(ERROR_MESSAGES["no_data"])
                return None
                
            if len(data) < MIN_DATA_POINTS:
                st.warning(ERROR_MESSAGES["insufficient_data"])
                
            # Clean column names
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            
            return data
            
        except requests.exceptions.RequestException:
            st.error(ERROR_MESSAGES["network_error"])
            return None
        except Exception as e:
            st.error(f"數據獲取錯誤: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def fetch_stock_info(_self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch stock information and metadata.
        
        Args:
            symbol: Stock symbol (e.g., "2881.TW")
            
        Returns:
            Dictionary with stock info or None if failed
        """
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Extract key information
            stock_info = {
                'longName': info.get('longName', 'N/A'),
                'shortName': info.get('shortName', 'N/A'),
                'currency': info.get('currency', 'TWD'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'marketCap': info.get('marketCap'),
                'previousClose': info.get('previousClose'),
                'dayHigh': info.get('dayHigh'),
                'dayLow': info.get('dayLow'),
                'volume': info.get('volume'),
                'averageVolume': info.get('averageVolume'),
                'trailingPE': info.get('trailingPE'),
                'dividendRate': info.get('dividendRate'),
                'dividendYield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh'),
                'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow')
            }
            
            return stock_info
            
        except Exception as e:
            st.error(f"股票資訊獲取錯誤: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def fetch_dividend_history(_self, symbol: str, years: int = 5) -> Optional[pd.DataFrame]:
        """
        Fetch dividend history for the stock.
        
        Args:
            symbol: Stock symbol (e.g., "2881.TW")
            years: Number of years of dividend history
            
        Returns:
            DataFrame with dividend history or None if failed
        """
        try:
            stock = yf.Ticker(symbol)
            
            # Get dividend data for specified years
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365 * years)
            
            dividends = stock.dividends
            if dividends.empty:
                return None
                
            # Filter by date range
            dividend_data = dividends[
                (dividends.index >= start_date) & 
                (dividends.index <= end_date)
            ]
            
            if dividend_data.empty:
                return None
                
            # Convert to DataFrame with better formatting
            df = dividend_data.to_frame('Dividend')
            df.index.name = 'Date'
            df['Year'] = df.index.year
            df['Quarter'] = df.index.quarter
            
            return df.sort_index(ascending=False)
            
        except Exception as e:
            st.error(f"配息資料獲取錯誤: {str(e)}")
            return None
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest stock price.
        
        Args:
            symbol: Stock symbol (e.g., "2881.TW")
            
        Returns:
            Latest price or None if failed
        """
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="1d")
            
            if data.empty:
                return None
                
            return data['Close'].iloc[-1]
            
        except Exception as e:
            st.error(f"即時價格獲取錯誤: {str(e)}")
            return None
    
    def get_price_change(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Get price change information.
        
        Args:
            symbol: Stock symbol (e.g., "2881.TW")
            
        Returns:
            Dictionary with price change info or None if failed
        """
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period="5d")
            
            if len(data) < 2:
                return None
                
            current_price = data['Close'].iloc[-1]
            previous_price = data['Close'].iloc[-2]
            
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100
            
            return {
                'current_price': current_price,
                'previous_price': previous_price,
                'change': change,
                'change_percent': change_percent
            }
            
        except Exception as e:
            st.error(f"價格變化資料獲取錯誤: {str(e)}")
            return None
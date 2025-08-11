"""Technical indicators calculation module."""

import pandas as pd
import numpy as np
import streamlit as st
from typing import Optional, Dict, List, Tuple
from config.settings import MA_SHORT, MA_LONG


class TechnicalIndicators:
    """Class for calculating technical indicators."""
    
    @staticmethod
    def calculate_moving_averages(data: pd.DataFrame, short_window: int = MA_SHORT, 
                                long_window: int = MA_LONG) -> pd.DataFrame:
        """
        Calculate moving averages.
        
        Args:
            data: Stock price DataFrame
            short_window: Short-term MA period (default: 5)
            long_window: Long-term MA period (default: 20)
            
        Returns:
            DataFrame with moving averages added
        """
        df = data.copy()
        
        df[f'MA{short_window}'] = df['Close'].rolling(window=short_window).mean()
        df[f'MA{long_window}'] = df['Close'].rolling(window=long_window).mean()
        
        return df
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate RSI (Relative Strength Index).
        
        Args:
            data: Stock price DataFrame
            period: RSI calculation period (default: 14)
            
        Returns:
            DataFrame with RSI added
        """
        df = data.copy()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, 
                                std_dev: int = 2) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: Stock price DataFrame
            period: Moving average period (default: 20)
            std_dev: Standard deviation multiplier (default: 2)
            
        Returns:
            DataFrame with Bollinger Bands added
        """
        df = data.copy()
        
        df['BB_Middle'] = df['Close'].rolling(window=period).mean()
        bb_std = df['Close'].rolling(window=period).std()
        
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * std_dev)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * std_dev)
        
        return df
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, 
                      signal: int = 9) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            data: Stock price DataFrame
            fast: Fast EMA period (default: 12)
            slow: Slow EMA period (default: 26)
            signal: Signal line EMA period (default: 9)
            
        Returns:
            DataFrame with MACD added
        """
        df = data.copy()
        
        ema_fast = df['Close'].ewm(span=fast).mean()
        ema_slow = df['Close'].ewm(span=slow).mean()
        
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=signal).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        return df
    
    @staticmethod
    def detect_golden_cross(data: pd.DataFrame, short_window: int = MA_SHORT, 
                           long_window: int = MA_LONG) -> List[pd.Timestamp]:
        """
        Detect golden cross signals (short MA crosses above long MA).
        
        Args:
            data: Stock price DataFrame with MAs
            short_window: Short-term MA period
            long_window: Long-term MA period
            
        Returns:
            List of dates where golden cross occurred
        """
        df = data.copy()
        
        if f'MA{short_window}' not in df.columns or f'MA{long_window}' not in df.columns:
            df = TechnicalIndicators.calculate_moving_averages(df, short_window, long_window)
        
        # Detect crossover points
        df['Signal'] = np.where(df[f'MA{short_window}'] > df[f'MA{long_window}'], 1, 0)
        df['Signal_Change'] = df['Signal'].diff()
        
        golden_crosses = df[df['Signal_Change'] == 1].index.tolist()
        
        return golden_crosses
    
    @staticmethod
    def detect_death_cross(data: pd.DataFrame, short_window: int = MA_SHORT, 
                          long_window: int = MA_LONG) -> List[pd.Timestamp]:
        """
        Detect death cross signals (short MA crosses below long MA).
        
        Args:
            data: Stock price DataFrame with MAs
            short_window: Short-term MA period
            long_window: Long-term MA period
            
        Returns:
            List of dates where death cross occurred
        """
        df = data.copy()
        
        if f'MA{short_window}' not in df.columns or f'MA{long_window}' not in df.columns:
            df = TechnicalIndicators.calculate_moving_averages(df, short_window, long_window)
        
        # Detect crossover points
        df['Signal'] = np.where(df[f'MA{short_window}'] > df[f'MA{long_window}'], 1, 0)
        df['Signal_Change'] = df['Signal'].diff()
        
        death_crosses = df[df['Signal_Change'] == -1].index.tolist()
        
        return death_crosses
    
    @staticmethod
    def calculate_support_resistance(data: pd.DataFrame, window: int = 20) -> Dict[str, float]:
        """
        Calculate support and resistance levels.
        
        Args:
            data: Stock price DataFrame
            window: Window for calculating levels
            
        Returns:
            Dictionary with support and resistance levels
        """
        df = data.tail(window)
        
        # Simple support/resistance calculation
        support = df['Low'].min()
        resistance = df['High'].max()
        
        # More sophisticated calculation using pivots
        highs = df['High'].rolling(window=5, center=True).max()
        lows = df['Low'].rolling(window=5, center=True).min()
        
        pivot_highs = df[df['High'] == highs]['High'].tolist()
        pivot_lows = df[df['Low'] == lows]['Low'].tolist()
        
        if pivot_highs:
            resistance = np.mean(sorted(pivot_highs, reverse=True)[:3])
        if pivot_lows:
            support = np.mean(sorted(pivot_lows)[:3])
        
        return {
            'support': support,
            'resistance': resistance,
            'current_price': df['Close'].iloc[-1]
        }
    
    @staticmethod
    def calculate_volatility(data: pd.DataFrame, period: int = 20) -> float:
        """
        Calculate price volatility (standard deviation).
        
        Args:
            data: Stock price DataFrame
            period: Period for volatility calculation
            
        Returns:
            Volatility as standard deviation
        """
        returns = data['Close'].pct_change().dropna()
        volatility = returns.rolling(window=period).std().iloc[-1]
        
        return volatility * np.sqrt(252)  # Annualized volatility
    
    @staticmethod
    def get_trend_analysis(data: pd.DataFrame) -> Dict[str, str]:
        """
        Analyze current trend based on multiple indicators.
        
        Args:
            data: Stock price DataFrame with indicators
            
        Returns:
            Dictionary with trend analysis
        """
        df = data.copy()
        
        # Add MAs if not present
        if 'MA5' not in df.columns or 'MA20' not in df.columns:
            df = TechnicalIndicators.calculate_moving_averages(df)
        
        latest = df.iloc[-1]
        
        # Price vs MAs
        if latest['Close'] > latest['MA20'] > latest['MA5']:
            trend = "強烈上升趋势"
        elif latest['Close'] > latest['MA20']:
            trend = "上升趋势"
        elif latest['Close'] < latest['MA20'] < latest['MA5']:
            trend = "強烈下降趋势"
        elif latest['Close'] < latest['MA20']:
            trend = "下降趋势"
        else:
            trend = "橫盤整理"
        
        # Volume analysis
        avg_volume = df['Volume'].tail(20).mean()
        current_volume = latest['Volume']
        
        if current_volume > avg_volume * 1.5:
            volume_trend = "成交量放大"
        elif current_volume < avg_volume * 0.5:
            volume_trend = "成交量萎縮"
        else:
            volume_trend = "成交量正常"
        
        return {
            'price_trend': trend,
            'volume_trend': volume_trend
        }
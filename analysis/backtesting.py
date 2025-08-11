"""Backtesting module for trading strategies."""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from analysis.indicators import TechnicalIndicators


class SimpleBacktester:
    """Simple backtesting engine for trading strategies."""
    
    def __init__(self, initial_capital: float = 100000):
        """
        Initialize backtester.
        
        Args:
            initial_capital: Starting capital in TWD
        """
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0  # Number of shares
        self.trades = []
        
    def golden_cross_strategy(self, data: pd.DataFrame, 
                            short_window: int = 5, long_window: int = 20) -> Dict:
        """
        Backtest golden cross strategy.
        
        Strategy:
        - Buy when MA5 crosses above MA20 (Golden Cross)
        - Sell when MA5 crosses below MA20 (Death Cross)
        
        Args:
            data: Stock price DataFrame
            short_window: Short MA period
            long_window: Long MA period
            
        Returns:
            Dictionary with backtest results
        """
        df = data.copy()
        df = TechnicalIndicators.calculate_moving_averages(df, short_window, long_window)
        
        self._reset()
        
        # Generate signals
        df['Signal'] = np.where(df[f'MA{short_window}'] > df[f'MA{long_window}'], 1, 0)
        df['Signal_Change'] = df['Signal'].diff()
        
        portfolio_value = []
        
        for i in range(len(df)):
            row = df.iloc[i]
            current_price = row['Close']
            
            # Buy signal (Golden Cross)
            if row['Signal_Change'] == 1 and self.position == 0:
                shares_to_buy = int(self.capital / current_price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    self.capital -= cost
                    self.position = shares_to_buy
                    
                    self.trades.append({
                        'date': row.name,
                        'action': 'BUY',
                        'price': current_price,
                        'shares': shares_to_buy,
                        'cost': cost
                    })
            
            # Sell signal (Death Cross)
            elif row['Signal_Change'] == -1 and self.position > 0:
                proceeds = self.position * current_price
                self.capital += proceeds
                
                self.trades.append({
                    'date': row.name,
                    'action': 'SELL',
                    'price': current_price,
                    'shares': self.position,
                    'proceeds': proceeds
                })
                
                self.position = 0
            
            # Calculate portfolio value
            current_portfolio_value = self.capital + (self.position * current_price)
            portfolio_value.append(current_portfolio_value)
        
        # Final sell if still holding
        if self.position > 0:
            final_price = df['Close'].iloc[-1]
            proceeds = self.position * final_price
            self.capital += proceeds
            
            self.trades.append({
                'date': df.index[-1],
                'action': 'SELL',
                'price': final_price,
                'shares': self.position,
                'proceeds': proceeds
            })
            
            self.position = 0
        
        df['Portfolio_Value'] = portfolio_value
        
        return self._calculate_performance(df)
    
    def ma_crossover_with_volume_strategy(self, data: pd.DataFrame) -> Dict:
        """
        MA crossover strategy with volume confirmation.
        
        Strategy:
        - Buy on golden cross with above-average volume
        - Sell on death cross or 10% stop loss
        
        Args:
            data: Stock price DataFrame
            
        Returns:
            Dictionary with backtest results
        """
        df = data.copy()
        df = TechnicalIndicators.calculate_moving_averages(df, 5, 20)
        
        # Calculate average volume
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
        
        self._reset()
        
        df['Signal'] = np.where(df['MA5'] > df['MA20'], 1, 0)
        df['Signal_Change'] = df['Signal'].diff()
        
        portfolio_value = []
        entry_price = None
        
        for i in range(len(df)):
            row = df.iloc[i]
            current_price = row['Close']
            
            # Buy signal with volume confirmation
            if (row['Signal_Change'] == 1 and 
                row['Volume'] > row['Volume_MA'] * 1.2 and 
                self.position == 0):
                
                shares_to_buy = int(self.capital / current_price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    self.capital -= cost
                    self.position = shares_to_buy
                    entry_price = current_price
                    
                    self.trades.append({
                        'date': row.name,
                        'action': 'BUY',
                        'price': current_price,
                        'shares': shares_to_buy,
                        'cost': cost
                    })
            
            # Sell signals
            elif self.position > 0:
                should_sell = False
                sell_reason = ""
                
                # Death cross
                if row['Signal_Change'] == -1:
                    should_sell = True
                    sell_reason = "Death Cross"
                
                # Stop loss (10%)
                elif entry_price and current_price < entry_price * 0.9:
                    should_sell = True
                    sell_reason = "Stop Loss"
                
                if should_sell:
                    proceeds = self.position * current_price
                    self.capital += proceeds
                    
                    self.trades.append({
                        'date': row.name,
                        'action': 'SELL',
                        'price': current_price,
                        'shares': self.position,
                        'proceeds': proceeds,
                        'reason': sell_reason
                    })
                    
                    self.position = 0
                    entry_price = None
            
            current_portfolio_value = self.capital + (self.position * current_price)
            portfolio_value.append(current_portfolio_value)
        
        df['Portfolio_Value'] = portfolio_value
        
        return self._calculate_performance(df)
    
    def _reset(self):
        """Reset backtester to initial state."""
        self.capital = self.initial_capital
        self.position = 0
        self.trades = []
    
    def _calculate_performance(self, df: pd.DataFrame) -> Dict:
        """
        Calculate performance metrics.
        
        Args:
            df: DataFrame with portfolio values
            
        Returns:
            Dictionary with performance metrics
        """
        if df.empty or 'Portfolio_Value' not in df.columns:
            return {}
        
        final_value = df['Portfolio_Value'].iloc[-1]
        total_return = (final_value - self.initial_capital) / self.initial_capital * 100
        
        # Buy and hold comparison
        initial_price = df['Close'].iloc[0]
        final_price = df['Close'].iloc[-1]
        buy_hold_return = (final_price - initial_price) / initial_price * 100
        
        # Calculate daily returns
        df['Daily_Return'] = df['Portfolio_Value'].pct_change()
        daily_returns = df['Daily_Return'].dropna()
        
        # Risk metrics
        volatility = daily_returns.std() * np.sqrt(252) * 100  # Annualized
        sharpe_ratio = 0
        if volatility > 0:
            risk_free_rate = 0.01  # Assume 1% risk-free rate
            excess_return = total_return / 100 - risk_free_rate
            sharpe_ratio = excess_return / (volatility / 100)
        
        # Maximum drawdown
        running_max = df['Portfolio_Value'].expanding().max()
        drawdown = (df['Portfolio_Value'] - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Win rate
        winning_trades = sum(1 for trade in self.trades[1::2] 
                           if len(self.trades) > 1 and 
                           trade['proceeds'] > self.trades[self.trades.index(trade)-1]['cost'])
        total_trades = len(self.trades) // 2
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'buy_hold_return': buy_hold_return,
            'excess_return': total_return - buy_hold_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'trades': self.trades,
            'portfolio_data': df[['Close', 'Portfolio_Value', 'MA5', 'MA20']].copy()
        }
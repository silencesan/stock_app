"""Main Streamlit application for Taiwan Stock Analysis Tool."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.stock_data import StockDataFetcher
from analysis.indicators import TechnicalIndicators
from analysis.backtesting import SimpleBacktester
from utils.helpers import (
    validate_stock_symbol, get_stock_name, format_currency, 
    calculate_percentage_change, format_percentage
)
from config.settings import TAIWAN_BANK_STOCKS, CHART_THEME, CHART_HEIGHT


def main():
    """Main application function."""
    st.set_page_config(
        page_title="台股銀行股分析工具",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📈 台股銀行股分析工具")
    st.markdown("---")
    
    # Initialize data fetcher
    fetcher = StockDataFetcher()
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 設定")
        
        # Stock selection
        st.subheader("股票選擇")
        
        # Dropdown for bank stocks
        bank_options = ["請選擇"] + [f"{code} - {name}" for code, name in TAIWAN_BANK_STOCKS.items()]
        selected_bank = st.selectbox("選擇銀行股", bank_options)
        
        # Manual input
        manual_symbol = st.text_input(
            "或手動輸入股票代碼", 
            placeholder="例如: 2881.TW 或 2881",
            help="支援台股代碼，如 2881.TW 或 2881"
        )
        
        # Determine which symbol to use
        stock_symbol = None
        if manual_symbol:
            is_valid, cleaned_symbol = validate_stock_symbol(manual_symbol)
            if is_valid:
                stock_symbol = cleaned_symbol
            else:
                st.error("請輸入有效的股票代碼格式")
        elif selected_bank != "請選擇":
            stock_code = selected_bank.split(" - ")[0]
            stock_symbol = f"{stock_code}.TW"
        
        # Time period
        st.subheader("時間範圍")
        period_options = {
            "1個月": "1mo",
            "3個月": "3mo", 
            "6個月": "6mo",
            "1年": "1y",
            "2年": "2y",
            "5年": "5y"
        }
        selected_period = st.selectbox("選擇時間範圍", list(period_options.keys()), index=3)
        period = period_options[selected_period]
        
        # Analysis options
        st.subheader("分析選項")
        show_ma = st.checkbox("顯示移動平均線", value=True)
        show_volume = st.checkbox("顯示成交量", value=True)
        show_rsi = st.checkbox("顯示RSI指標", value=False)
        show_bollinger = st.checkbox("顯示布林通道", value=False)
    
    # Main content
    if stock_symbol:
        stock_name = get_stock_name(stock_symbol)
        if stock_name:
            st.subheader(f"📊 {stock_name} ({stock_symbol})")
        else:
            st.subheader(f"📊 {stock_symbol}")
        
        # Fetch data
        with st.spinner("正在獲取股票數據..."):
            stock_data = fetcher.fetch_stock_data(stock_symbol, period)
            stock_info = fetcher.fetch_stock_info(stock_symbol)
        
        if stock_data is not None and not stock_data.empty:
            # Display key metrics
            display_key_metrics(stock_data, stock_info)
            
            # Calculate indicators
            if show_ma:
                stock_data = TechnicalIndicators.calculate_moving_averages(stock_data)
            if show_rsi:
                stock_data = TechnicalIndicators.calculate_rsi(stock_data)
            if show_bollinger:
                stock_data = TechnicalIndicators.calculate_bollinger_bands(stock_data)
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📈 股價走勢", "💰 配息資訊", "🔄 策略回測", "📊 技術分析"])
            
            with tab1:
                display_price_chart(stock_data, show_ma, show_volume, show_rsi, show_bollinger)
            
            with tab2:
                display_dividend_info(fetcher, stock_symbol)
            
            with tab3:
                display_backtesting_results(stock_data)
            
            with tab4:
                display_technical_analysis(stock_data)
        else:
            st.error("無法獲取股票數據，請檢查代碼是否正確或稍後再試。")
    else:
        # Welcome message
        st.markdown("""
        ### 歡迎使用台股銀行股分析工具！ 👋
        
        **功能特色：**
        - 📈 即時股價走勢圖表
        - 📊 技術指標分析 (MA5/MA20, RSI, 布林通道)
        - 💰 歷史配息資訊
        - 🔄 交易策略回測
        - 📱 響應式設計，支援各種設備
        
        **使用方式：**
        1. 在左側選擇銀行股或手動輸入股票代碼
        2. 選擇分析時間範圍
        3. 勾選想要顯示的技術指標
        4. 查看詳細分析結果
        
        **支援的銀行股：**
        """)
        
        # Display supported bank stocks
        cols = st.columns(4)
        bank_list = list(TAIWAN_BANK_STOCKS.items())
        for i, (code, name) in enumerate(bank_list):
            with cols[i % 4]:
                st.write(f"**{code}** - {name}")


def display_key_metrics(data: pd.DataFrame, info: dict):
    """Display key financial metrics."""
    latest = data.iloc[-1]
    previous = data.iloc[-2] if len(data) > 1 else latest
    
    price_change = latest['Close'] - previous['Close']
    price_change_pct = calculate_percentage_change(previous['Close'], latest['Close'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "當前股價",
            format_currency(latest['Close']),
            delta=f"{price_change:+.2f} ({format_percentage(price_change_pct)})"
        )
    
    with col2:
        st.metric("成交量", f"{latest['Volume']:,.0f}")
    
    with col3:
        if info and info.get('fiftyTwoWeekHigh'):
            st.metric("52週最高", format_currency(info['fiftyTwoWeekHigh']))
        else:
            st.metric("區間最高", format_currency(data['High'].max()))
    
    with col4:
        if info and info.get('fiftyTwoWeekLow'):
            st.metric("52週最低", format_currency(info['fiftyTwoWeekLow']))
        else:
            st.metric("區間最低", format_currency(data['Low'].min()))


def display_price_chart(data: pd.DataFrame, show_ma: bool, show_volume: bool, 
                       show_rsi: bool, show_bollinger: bool):
    """Display price chart with indicators."""
    
    # Determine subplot configuration
    subplot_titles = ["股價走勢"]
    rows = 1
    row_heights = [0.7]
    
    if show_volume:
        subplot_titles.append("成交量")
        rows += 1
        row_heights.append(0.2)
    
    if show_rsi:
        subplot_titles.append("RSI")
        rows += 1
        row_heights.append(0.1)
    
    # Create subplots
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=rows, cols=1,
        subplot_titles=subplot_titles,
        vertical_spacing=0.02,
        row_heights=row_heights
    )
    
    # Main price chart
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="股價"
        ),
        row=1, col=1
    )
    
    # Moving averages
    if show_ma and 'MA5' in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MA5'],
                mode='lines',
                name='MA5',
                line=dict(color='orange', width=1)
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MA20'],
                mode='lines',
                name='MA20',
                line=dict(color='blue', width=1)
            ),
            row=1, col=1
        )
    
    # Bollinger Bands
    if show_bollinger and 'BB_Upper' in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['BB_Upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color='gray', width=1, dash='dash'),
                showlegend=False
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['BB_Lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color='gray', width=1, dash='dash'),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ),
            row=1, col=1
        )
    
    current_row = 2
    
    # Volume
    if show_volume:
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(data['Close'], data['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name="成交量",
                marker_color=colors,
                opacity=0.7
            ),
            row=current_row, col=1
        )
        current_row += 1
    
    # RSI
    if show_rsi and 'RSI' in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='purple', width=2)
            ),
            row=current_row, col=1
        )
        
        # Add RSI reference lines
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     opacity=0.5, row=current_row, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     opacity=0.5, row=current_row, col=1)
    
    # Update layout
    fig.update_layout(
        title="股價走勢圖",
        template=CHART_THEME,
        height=CHART_HEIGHT,
        showlegend=True,
        xaxis_rangeslider_visible=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def display_dividend_info(fetcher: StockDataFetcher, symbol: str):
    """Display dividend information."""
    st.subheader("💰 配息資訊")
    
    with st.spinner("正在獲取配息數據..."):
        dividend_data = fetcher.fetch_dividend_history(symbol, years=5)
    
    if dividend_data is not None and not dividend_data.empty:
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_dividends = dividend_data['Dividend'].sum()
            st.metric("5年總配息", format_currency(total_dividends))
        
        with col2:
            avg_dividend = dividend_data.groupby('Year')['Dividend'].sum().mean()
            st.metric("年均配息", format_currency(avg_dividend))
        
        with col3:
            recent_dividend = dividend_data.groupby('Year')['Dividend'].sum().iloc[0]
            st.metric("最近年度配息", format_currency(recent_dividend))
        
        # Dividend chart
        yearly_dividends = dividend_data.groupby('Year')['Dividend'].sum().reset_index()
        yearly_dividends = yearly_dividends.sort_values('Year')
        
        fig = px.bar(
            yearly_dividends, 
            x='Year', 
            y='Dividend',
            title="年度配息趨勢",
            template=CHART_THEME
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed dividend table
        st.subheader("詳細配息記錄")
        display_data = dividend_data.copy()
        display_data['Date'] = display_data.index.strftime('%Y-%m-%d')
        display_data = display_data[['Date', 'Dividend', 'Year', 'Quarter']]
        display_data.columns = ['除息日', '股息(元)', '年份', '季度']
        
        st.dataframe(display_data, use_container_width=True)
        
    else:
        st.info("該股票暫無配息記錄或數據獲取失敗")


def display_backtesting_results(data: pd.DataFrame):
    """Display backtesting results."""
    st.subheader("🔄 策略回測")
    
    # Strategy selection
    strategy = st.selectbox(
        "選擇回測策略",
        ["黃金交叉策略", "MA交叉+成交量確認策略"]
    )
    
    initial_capital = st.number_input(
        "初始資金 (TWD)", 
        min_value=10000, 
        max_value=10000000,
        value=100000,
        step=10000
    )
    
    if st.button("開始回測"):
        with st.spinner("正在進行策略回測..."):
            backtester = SimpleBacktester(initial_capital)
            
            if strategy == "黃金交叉策略":
                results = backtester.golden_cross_strategy(data)
            else:
                results = backtester.ma_crossover_with_volume_strategy(data)
        
        if results:
            # Performance metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "總報酬率",
                    f"{results['total_return']:.2f}%",
                    delta=f"{results['excess_return']:.2f}% vs 買進持有"
                )
            
            with col2:
                st.metric("最終資產", format_currency(results['final_value']))
            
            with col3:
                st.metric("交易次數", f"{results['total_trades']} 次")
            
            with col4:
                st.metric("勝率", f"{results['win_rate']:.1f}%")
            
            # Additional metrics
            col5, col6, col7 = st.columns(3)
            
            with col5:
                st.metric("年化波動率", f"{results['volatility']:.2f}%")
            
            with col6:
                st.metric("夏普比率", f"{results['sharpe_ratio']:.2f}")
            
            with col7:
                st.metric("最大回撤", f"{results['max_drawdown']:.2f}%")
            
            # Portfolio value chart
            if 'portfolio_data' in results:
                portfolio_df = results['portfolio_data']
                
                fig = go.Figure()
                
                # Portfolio value
                fig.add_trace(go.Scatter(
                    x=portfolio_df.index,
                    y=portfolio_df['Portfolio_Value'],
                    mode='lines',
                    name='策略資產價值',
                    line=dict(color='blue', width=2)
                ))
                
                # Buy and hold comparison
                initial_price = portfolio_df['Close'].iloc[0]
                buy_hold_values = (portfolio_df['Close'] / initial_price) * initial_capital
                
                fig.add_trace(go.Scatter(
                    x=portfolio_df.index,
                    y=buy_hold_values,
                    mode='lines',
                    name='買進持有',
                    line=dict(color='gray', width=1, dash='dash')
                ))
                
                # Mark buy/sell points
                for trade in results['trades']:
                    if trade['action'] == 'BUY':
                        fig.add_trace(go.Scatter(
                            x=[trade['date']],
                            y=[portfolio_df.loc[trade['date'], 'Portfolio_Value']],
                            mode='markers',
                            marker=dict(color='green', size=10, symbol='triangle-up'),
                            name='買進' if 'BUY_ADDED' not in locals() else '',
                            showlegend='BUY_ADDED' not in locals()
                        ))
                        locals()['BUY_ADDED'] = True
                    else:
                        fig.add_trace(go.Scatter(
                            x=[trade['date']],
                            y=[portfolio_df.loc[trade['date'], 'Portfolio_Value']],
                            mode='markers',
                            marker=dict(color='red', size=10, symbol='triangle-down'),
                            name='賣出' if 'SELL_ADDED' not in locals() else '',
                            showlegend='SELL_ADDED' not in locals()
                        ))
                        locals()['SELL_ADDED'] = True
                
                fig.update_layout(
                    title="策略績效比較",
                    template=CHART_THEME,
                    height=500,
                    yaxis_title="資產價值 (TWD)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Trade history
            if results['trades']:
                st.subheader("交易記錄")
                trades_df = pd.DataFrame(results['trades'])
                trades_df['date'] = pd.to_datetime(trades_df['date']).dt.strftime('%Y-%m-%d')
                
                st.dataframe(trades_df, use_container_width=True)


def display_technical_analysis(data: pd.DataFrame):
    """Display technical analysis summary."""
    st.subheader("📊 技術分析")
    
    # Calculate additional indicators
    data_with_indicators = TechnicalIndicators.calculate_moving_averages(data)
    data_with_indicators = TechnicalIndicators.calculate_rsi(data_with_indicators)
    
    # Current trend analysis
    trend_analysis = TechnicalIndicators.get_trend_analysis(data_with_indicators)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("趨勢分析")
        st.write(f"**價格趨勢:** {trend_analysis['price_trend']}")
        st.write(f"**成交量趨勢:** {trend_analysis['volume_trend']}")
    
    with col2:
        st.subheader("支撐阻力位")
        support_resistance = TechnicalIndicators.calculate_support_resistance(data)
        
        st.write(f"**支撐位:** {format_currency(support_resistance['support'])}")
        st.write(f"**阻力位:** {format_currency(support_resistance['resistance'])}")
        st.write(f"**當前價格:** {format_currency(support_resistance['current_price'])}")
    
    # Golden/Death cross detection
    st.subheader("交叉信號")
    
    golden_crosses = TechnicalIndicators.detect_golden_cross(data_with_indicators)
    death_crosses = TechnicalIndicators.detect_death_cross(data_with_indicators)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.write("**最近黃金交叉:**")
        if golden_crosses:
            latest_golden = golden_crosses[-1].strftime('%Y-%m-%d')
            st.success(f"📈 {latest_golden}")
        else:
            st.write("無記錄")
    
    with col4:
        st.write("**最近死亡交叉:**")
        if death_crosses:
            latest_death = death_crosses[-1].strftime('%Y-%m-%d')
            st.error(f"📉 {latest_death}")
        else:
            st.write("無記錄")


if __name__ == "__main__":
    main()
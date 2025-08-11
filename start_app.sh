#!/bin/bash

# 台股銀行股分析工具啟動腳本

echo "🚀 正在啟動台股銀行股分析工具..."

# 設定環境變數
export PATH="$HOME/.local/bin:$PATH"

# 切換到專案目錄
cd "$(dirname "$0")"

# 激活虛擬環境
source .venv/bin/activate

# 檢查套件是否安裝
echo "📦 檢查套件安裝狀態..."
python -c "import streamlit, yfinance, pandas, plotly; print('✅ 所有必要套件已安裝')" || {
    echo "❌ 套件缺失，正在安裝..."
    uv pip install streamlit yfinance pandas plotly
}

echo "📈 啟動 Streamlit 應用程式..."
echo "🌐 應用程式將在瀏覽器中打開: http://localhost:8501"
echo "⏹️  按 Ctrl+C 停止應用程式"

# 啟動應用程式
streamlit run app.py
"""Configuration settings for the stock analysis app."""

# Taiwan Bank Stock Symbols
TAIWAN_BANK_STOCKS = {
    "2880": "華南金",
    "2881": "富邦金", 
    "2882": "國泰金",
    "2883": "開發金",
    "2884": "玉山金",
    "2885": "元大金",
    "2886": "兆豐金",
    "2887": "台新金",
    "2888": "新光金",
    "2889": "國票金",
    "2890": "永豐金",
    "2891": "中信金",
    "2892": "第一金"
}

# Technical Analysis Settings
MA_SHORT = 5
MA_LONG = 20

# Chart Settings
CHART_THEME = "plotly_white"
CHART_HEIGHT = 600

# Data Settings
DEFAULT_PERIOD = "1y"  # 1 year
MIN_DATA_POINTS = 50   # Minimum data points required for analysis

# Error Messages
ERROR_MESSAGES = {
    "invalid_symbol": "請輸入有效的股票代碼 (例如: 2881.TW)",
    "no_data": "無法取得股票資料，請確認代碼是否正確",
    "insufficient_data": "資料不足，無法進行分析",
    "network_error": "網路連線錯誤，請稍後再試"
}
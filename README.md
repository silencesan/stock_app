# 台股銀行股分析工具 📈

一個基於 Streamlit 和 Python 的台股銀行股分析工具，支援即時股價查詢、技術指標分析、配息資訊和策略回測功能。

## 🌟 功能特色

- **📊 即時股價分析**: 支援台股銀行股即時價格查詢
- **📈 技術指標**: MA5/MA20移動平均線、RSI、布林通道等指標
- **💰 配息資訊**: 歷史配息記錄和年度配息趨勢分析
- **🔄 策略回測**: 黃金交叉和量價確認策略回測
- **📱 響應式設計**: 適配各種螢幕尺寸的現代化界面

## 🚀 快速開始

### 本地運行

1. **複製專案**
```bash
git clone <your-repo-url>
cd stock_app
```

2. **建立虛擬環境**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate  # Windows
```

3. **安裝依賴**
```bash
pip install -r requirements.txt
```

4. **運行應用程式**
```bash
streamlit run app.py
```

5. **在瀏覽器中打開** `http://localhost:8501`

## 📦 支援的銀行股

| 股票代碼 | 公司名稱 | 股票代碼 | 公司名稱 |
|---------|---------|---------|---------|
| 2880 | 華南金 | 2886 | 兆豐金 |
| 2881 | 富邦金 | 2887 | 台新金 |
| 2882 | 國泰金 | 2888 | 新光金 |
| 2883 | 開發金 | 2889 | 國票金 |
| 2884 | 玉山金 | 2890 | 永豐金 |
| 2885 | 元大金 | 2891 | 中信金 |
|         |         | 2892 | 第一金 |

## 🛠 技術棧

- **前端**: Streamlit
- **資料獲取**: yfinance
- **資料處理**: pandas, numpy
- **視覺化**: plotly
- **技術指標**: pandas-ta
- **部署**: Streamlit Community Cloud

## 📊 主要功能模組

### 1. 股價走勢分析
- K線圖顯示
- 移動平均線 (MA5/MA20)
- 成交量分析
- RSI 指標
- 布林通道

### 2. 配息分析
- 歷史配息記錄
- 年度配息趨勢
- 配息統計摘要

### 3. 策略回測
- 黃金交叉策略
- MA交叉+成交量確認策略
- 績效分析與比較
- 交易記錄詳情

### 4. 技術分析
- 趨勢分析
- 支撐阻力位
- 交叉信號偵測

## 🌐 雲端部署

### 部署到 Streamlit Community Cloud

1. **上傳到 GitHub**: 將專案上傳至 GitHub 儲存庫
2. **連接 Streamlit Cloud**: 
   - 前往 [share.streamlit.io](https://share.streamlit.io)
   - 登入並連接 GitHub 帳戶
   - 選擇儲存庫和分支
   - 設定主檔案為 `app.py`
3. **部署**: 點擊 Deploy 完成部署

## 📁 專案結構

```
stock_app/
├── app.py                 # 主應用程式
├── requirements.txt       # 套件依賴清單
├── README.md             # 專案說明文件
├── .streamlit/
│   └── config.toml       # Streamlit 設定
├── data/
│   └── stock_data.py     # 股票數據獲取模組
├── analysis/
│   ├── indicators.py     # 技術指標計算
│   └── backtesting.py    # 回測功能
├── utils/
│   └── helpers.py        # 輔助函數
└── config/
    └── settings.py       # 設定檔
```

## ⚙️ 設定說明

### 技術指標參數
- **MA短期**: 5日移動平均線
- **MA長期**: 20日移動平均線
- **RSI週期**: 14日
- **布林通道**: 20日中線，2倍標準差

### 回測參數
- **初始資金**: 可自訂（預設10萬元）
- **交易成本**: 暫不計算（可後續加入）
- **停損機制**: 10%停損（量價策略）

## 📈 使用說明

1. **選擇股票**: 可從下拉選單選擇銀行股或手動輸入股票代碼
2. **設定時間範圍**: 支援1個月到5年的歷史資料
3. **選擇指標**: 勾選想要顯示的技術指標
4. **查看分析**: 切換不同頁籤查看各種分析結果
5. **策略回測**: 選擇策略並設定初始資金進行回測

## 🔧 客製化開發

如需添加新功能或修改現有功能，請參考：

- `config/settings.py`: 修改基本設定
- `analysis/indicators.py`: 添加新的技術指標
- `analysis/backtesting.py`: 開發新的交易策略
- `app.py`: 修改使用者介面和互動邏輯

## 📝 注意事項

- 本工具僅供教育和研究用途，不構成投資建議
- 股市有風險，投資需謹慎
- 資料來源為 Yahoo Finance，可能存在延遲或誤差
- 回測結果不代表未來表現

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改進這個專案！

## 📄 授權

此專案採用 MIT 授權條款。

---

如有問題或建議，請透過 GitHub Issues 與我們聯繫。
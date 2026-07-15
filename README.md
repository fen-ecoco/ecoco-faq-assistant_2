# ECOCO FAQ Assistant 2.0

ECOCO 內部常見問題集管理系統，提供簡易的本地端介面，用於管理和編輯客服常用問答 (FAQ)。

---

## 🌐 線上版本

**雲端網址：** https://ecoco-faq-assistant-2.onrender.com

> 免費方案長時間未使用會進入休眠，首次載入可能需等待 30～60 秒。

---

## 🚀 功能總覽

### 核心功能
- ✅ 新增 / 編輯 / 刪除常見問題
- ✅ 全文搜尋（主題、分類、內容）
- ✅ V1 標準回覆 + V2 備用英文 雙版本管理
- ✅ 一鍵複製回覆內容
- ✅ 複製整列資料（Google Sheet 格式）

### 側邊欄導覽
- 📋 **全部** — 顯示所有 FAQ
- 🔍 **主題 / 項目 / 版本** — 點選後顯示快速篩選按鈕（Chips）
- 🤖 **智能比對** — 貼上用戶訊息，自動找出最相關問答
- 🔥 **熱門** — 依複製次數自動排行，點擊跳至對應卡片

### 匯出 / 匯入功能
| 按鈕 | 說明 |
|------|------|
| 📥 **匯入** | 上傳 CSV 批次新增 FAQ |
| 📄 **CSV** | 匯出所有 FAQ 為 CSV 檔案 |
| 📊 **Excel** | 匯出所有 FAQ 為 XLS 檔案 |
| 📕 **PDF** | 匯出為排版好的 PDF（含 ECOCO 品牌樣式） |

### 其他
- ⬆️ **TOP 置頂鍵** — 頁面右下角，捲動超過 300px 自動出現
- 🔄 **雲端同步** — 使用 `sync_from_render.py` 將雲端資料同步至本機

---

## 🗂️ 專案結構

```
ecoco-faq-assistant_2/
├── ecoco_persistent_faq.html   # 前端主頁面（React + Tailwind）
├── faq_server.py               # FastAPI 後端（支援 PostgreSQL）
├── requirements.txt            # Python 套件清單
├── render.yaml                 # Render 部署設定
├── init_data.py                # 初始資料匯入腳本
├── sync_from_render.py         # 雲端 → 本機同步腳本
├── 啟動ECOCO知識庫.bat         # 本機一鍵啟動（Windows）
└── README.md
```

---

## ⚙️ 本機啟動方式

```bash
pip install -r requirements.txt
python faq_server.py
```
瀏覽器開啟：http://127.0.0.1:7777

---

## ☁️ 雲端部署（Render + Supabase）

### 環境變數
| Key | Value |
|-----|-------|
| `DATABASE_URL` | Supabase PostgreSQL Connection Pooler URI（port 6543） |

---

## 🔄 資料同步

```bash
# 同步雲端新資料到本機（保留本機既有資料）
python sync_from_render.py

# 完全用雲端資料取代本機
python sync_from_render.py --reset
```

---

## 📋 CSV 匯入欄位格式

| 欄位 | 必填 |
|------|------|
| 主題 | ✅ |
| 主項目 | |
| 小項目 | |
| 細項 | |
| 標準回覆(V1) | |
| 備用英文(V2) | |

---

## 🎨 ECOCO VI 色票

| 色彩 | HEX |
|------|-----|
| Orange | `#FF5000` |
| Deep Blue | `#060E9F` |
| Yellow | `#FFCE00` |
| Light Blue | `#8EB9C9` |
| Beige | `#FAE0B8` |
| Aqua | `#0076A9` |

---

## 📝 更新紀錄

### v2.2（2026/07）
- 優化右下角 TOP 置頂鍵：頁面下捲超過 300px 自動顯示深藍色圓形按鈕，支援平滑回頂，滑鼠懸停變更為橘色
- 新增 Excel 批次匯入功能（搜尋列旁「匯入」按鈕）：支援標準三步驟（下載範本 → 上傳 CSV → 預覽確認後批次新增）
- 批次匯入規格優化：支援主題、主項目、小項目、細項、V1、V2 共六欄位，相容 Excel 另存之「CSV UTF-8」格式
- 前端新增更新日期功能：配合後端 `faq_server.py` 的 `modified_date` 欄位，前端新增顯示更新日，並於送出資料時自動帶入當天日期

### v2.1（2026/03）
- 升級 AI 客服為後端真實呼叫大語言模型架構（擺脫前端靜態模擬）
- 後端新增 `POST /api/ai_chat` 專屬端點，正式串接 `google-generativeai` 套件
- 導入 `gemini-1.5-flash` 模型，並注入 ECOCO 點數回饋平台專業客服 Prompt 提示詞
- 前端全面串接後端 API，支援動態產生建議回覆、新增讀取中動畫
- 強化前端錯誤處理，當未設定 API Key 或連線失敗時顯示明確的 ❌ 錯誤提示
- `requirements.txt` 新增依賴套件，確保 Render 雲端部署自動安裝

### v2.0（2026/03）
- 新增左側導覽欄（全部／主題／項目／版本／智能比對／熱門）
- 新增快速篩選 Chips
- 新增智能比對功能
- 新增熱門問題排行（依複製次數自動排列）
- 新增匯出 CSV / Excel / PDF
- 新增 Excel / CSV 批次匯入
- 新增右下角 TOP 置頂鍵
- 後端改用 PostgreSQL（Supabase）永久儲存
- API_URL 改為 `window.location.origin`，雲端直接可用
- 新增雲端同步腳本 `sync_from_render.py`

### v1.0（2026/03）
- 基礎 FAQ 新增 / 編輯 / 刪除
- 全文搜尋、V1 / V2 雙版本回覆
- SQLite 本機資料庫

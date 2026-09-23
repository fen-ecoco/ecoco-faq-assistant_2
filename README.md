# ECOCO FAQ Assistant 2.0

ECOCO 內部常見問題集管理系統，提供簡易的本地端與雲端介面，用於管理和編輯客服常用問答 (FAQ)。

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
- ✅ 建立日 / 更新日 自動記錄

### 側邊欄導覽
- 📋 **全部** — 顯示所有 FAQ
- 🔍 **主題 / 項目 / 版本** — 點選後顯示可收合的快速篩選按鈕（Chips）
- 🤖 **智能比對** — 貼上用戶訊息，自動找出最相關問答
- 🔥 **熱門** — 依複製次數自動排行
- 🤖 **AI 客服** — 輸入用戶問題，由 Gemini AI 生成建議回覆
- 📦 **封存區** — 封存不常用問答，隨時可解封存

### 匯出 / 匯入功能
| 按鈕 | 說明 |
|------|------|
| 📥 **匯入** | 上傳 CSV 批次新增 FAQ（支援儲存格內換行） |
| 📄 **CSV** | 匯出所有 FAQ 為 CSV 檔案 |
| 📊 **Excel** | 匯出所有 FAQ 為 XLS 檔案 |
| 📕 **PDF** | 匯出為排版好的 PDF（含 ECOCO 品牌樣式） |

### 其他
- ⬆️ **TOP 置頂鍵** — 頁面右下角，捲動超過 300px 自動出現
- 📑 **分頁功能** — 支援 1 / 10 / 50 / 100 / 500 / 1000 筆/頁
- 🔄 **雲端同步** — 使用 `sync_from_render.py` 將雲端資料同步至本機

---

## 🗂️ 專案結構

```
ecoco-faq-assistant_2/
├── ecoco_persistent_faq.html   # 前端主頁面（React + Tailwind）
├── faq_server.py               # FastAPI 後端（支援 SQLite 本機 / PostgreSQL 雲端）
├── requirements.txt            # Python 套件清單
├── render.yaml                 # Render 雲端部署設定
├── init_data.py                # 初始資料匯入腳本
├── migrate_to_render.py        # 本機 → 雲端資料搬移腳本
├── sync_from_render.py         # 雲端 → 本機同步腳本
├── 啟動ECOCO知識庫.bat         # 本機一鍵啟動（Windows）
├── .gitignore                  # 排除敏感檔案與暫存檔
└── README.md
```

---

## ⚙️ 本機啟動方式

### 快速啟動
直接執行：
```
啟動ECOCO知識庫.bat
```
會自動安裝套件、清除佔用的 Port 7777、啟動伺服器並開啟瀏覽器。

### 手動啟動
```bash
pip install -r requirements.txt
python faq_server.py
```
瀏覽器開啟：http://127.0.0.1:7777

### AI 客服功能（本機）
需設定 Gemini API 金鑰（永久設定）：
```powershell
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "你的API金鑰", "User")
```
金鑰取得：https://aistudio.google.com/app/apikey

---

## ☁️ 雲端部署（Render + Supabase）

### Render 環境變數
| Key | Value |
|-----|-------|
| `DATABASE_URL` | Supabase PostgreSQL Connection Pooler URI（port 6543） |
| `GEMINI_API_KEY` | Google Gemini API 金鑰 |

---

## 🔒 安全性注意事項

- **API Key 絕對不要上傳 GitHub** — 已加入 `.gitignore` 排除 `.env` 檔案
- 本機資料庫 `ecoco_faq.db` 已加入 `.gitignore`，不會上傳
- Log 檔 `server_debug.log` 已加入 `.gitignore`
- 若不小心上傳了敏感資訊，請立即至 Google AI Studio 重新產生 API Key

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

| 欄位 | 必填 | 說明 |
|------|------|------|
| 主題 | ✅ | FAQ 主分類 |
| 主項目 | | 次分類 |
| 小項目 | | 版本或細分類 |
| 細項 | | 用戶問題描述 |
| 標準回覆(V1) | | 官方標準回覆（支援儲存格內換行） |
| 備用英文(V2) | | 英文版或備用語句 |

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

### v2.5（2026/07）
- 新增 AI 客服功能（Gemini 2.5 Flash）
- 修正 faq_server.py UTF-8 編碼宣告問題
- 新增 .gitignore 防止敏感資訊上傳
- 啟動腳本新增自動開啟瀏覽器、自動清除佔用 Port、自動安裝 google-generativeai
- 新增分頁功能（1 / 10 / 50 / 100 / 500 / 1000 筆/頁）
- Chip 篩選列改為收合式設計
- 新增建立日 / 更新日顯示
- 修正 CSV 多行儲存格匯入解析問題

### v2.0（2026/03）
- 新增左側導覽欄（全部／主題／項目／版本／智能比對／熱門／封存區）
- 新增快速篩選 Chips
- 新增智能比對功能
- 新增熱門問題排行（依複製次數自動排列）
- 新增匯出 CSV / Excel / PDF
- 新增 Excel / CSV 批次匯入
- 新增右下角 TOP 置頂鍵
- 後端改用 PostgreSQL（Supabase）永久儲存
- 新增雲端同步腳本 `sync_from_render.py`

### v1.0（2026/03）
- 基礎 FAQ 新增 / 編輯 / 刪除
- 全文搜尋、V1 / V2 雙版本回覆
- SQLite 本機資料庫

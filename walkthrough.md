# AI 客服後端串接完成 (Gemini API)

我已經成功將 AI 客服模組從「前端靜態模擬」升級為「後端真實呼叫大語言模型 (Gemini)」的架構了！

## 🚀 完成了什麼？

1. **後端支援 (faq_server.py)**
   - 建立了專屬的 `POST /api/ai_chat` 端點。
   - 已經串接 `google-generativeai` 套件，並設定好專屬的 Prompt 指令（「你是一位專業的 ECOCO (點數回饋平台) 客服助手...基於官方網站、官方粉絲團以及公開資訊...」）。
   - 現在，模型 (`gemini-1.5-flash`) 會真正根據 ECOCO 的背景與您輸入的問題，動態運算並產生適合客服情境的回覆文字。

2. **前端串接 (ecoco_persistent_faq.html)**
   - AI 客服面板的「產生建議回覆」按鈕，現在會真正打 API 給後端伺服器。
   - 在產生期間保留了友善的讀取中動畫。
   - 強化了錯誤處理：如果伺服器未設定 API Key，或者發生連線問題，前端面板會直接給出明確的「❌ 錯誤提示」，指引您去設定。

3. **套件管理 (requirements.txt)**
   - 已加入了 `google-generativeai` 套件，確保在 Render 部署時會自動安裝所需依賴。

---

## ⚠️ 您接下來需要做的事 (重要)

> [!CAUTION]
> 目前您的伺服器 (包含本機與 Render 上) 尚未設定 Gemini 的 API 金鑰。如果現在點擊「產生建議回覆」，前端將會顯示錯誤訊息，請您進行以下步驟：

### 步驟 1：取得免費 API Key
請前往 **[Google AI Studio](https://aistudio.google.com/)**，登入您的 Google 帳號，並點擊左側的「Get API key」來建立一組新的 API Key。

### 步驟 2：設定 Render 伺服器
1. 登入您的 Render 儀表板，進入 `ecoco-faq-assistant-2` 專案。
2. 前往 **Environment** (環境變數) 頁籤。
3. 點擊 **Add Environment Variable**，新增一筆：
   - **Key:** `GEMINI_API_KEY`
   - **Value:** (貼上您剛剛拿到的 API 金鑰)
4. 儲存後，Render 會自動重新部署。部署完成後，線上的 AI 客服就能夠正常產生真實的內容了！

### 步驟 3：在本機測試 (選用)
如果您想在自己的電腦上先測試，請在啟動 `faq_server.py` 之前，在終端機先執行：
*(Windows Powershell)*
```powershell
$env:GEMINI_API_KEY="您的API金鑰"
python faq_server.py
```

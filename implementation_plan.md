# AI 客服後端串接與真實生成功能

目前 AI 客服的功能為前端靜態的示範文字。為了讓 AI 能夠根據 ECOCO 官網與粉專資訊提供真正有用的建議回覆，我們需要將 AI 產生邏輯移至後端，並串接真實的語言模型 (LLM) API。

## User Review Required

> [!IMPORTANT]
> 要達成這個功能，我們需要串接真實的 AI 服務。在此提案中，我預計為您串接 **Google Gemini API** (因為它能支援搜尋與最新資料，且有免費額度可以使用)。
> **您需要做的事：**
> 1. 您是否同意使用 Gemini？（或是您更偏好 OpenAI/ChatGPT？）
> 2. 如果同意，您需要前往 [Google AI Studio](https://aistudio.google.com/) 申請一組 `GEMINI_API_KEY`，後續需要將它設定在您的 Render 環境變數中。

## Proposed Changes

### 後端 (Backend)

#### [MODIFY] [requirements.txt](file:///C:/Users/fen/.gemini/antigravity/skills/ecoco-faq-assistant/requirements.txt)
- 新增 `google-generativeai` 套件。

#### [MODIFY] [faq_server.py](file:///C:/Users/fen/.gemini/antigravity/skills/ecoco-faq-assistant/faq_server.py)
- 新增 `POST /api/ai_chat` 端點。
- 寫入接收前端問題並呼叫 Gemini API 的邏輯。
- 我們會設定一段系統 Prompt，明確告訴 AI 它是 ECOCO 的客服助手，並指引它以客服的口吻以及它對 ECOCO 的知識來生成回覆。
- 若環境中未設定 `GEMINI_API_KEY`，則回傳提醒字眼，請使用者去設定。

### 前端 (Frontend)

#### [MODIFY] [ecoco_persistent_faq.html](file:///C:/Users/fen/.gemini/antigravity/skills/ecoco-faq-assistant/ecoco_persistent_faq.html)
- 移除目前 `handleAiSubmit` 裡的 `setTimeout` 假回覆機制。
- 改為使用 `fetch` 打 API 到後端的 `/api/ai_chat`，將使用者的提問送出，並接收真實的 AI 建議。
- 加入錯誤處理 (例如：當後端提示尚未設定 API Key 時，在畫面上友善提醒您)。

## Verification Plan

### Manual Verification
1. 實作完成後，我會請您在本地或 Render 補上 API Key，接著測試前端的 AI 面板，輸入如「點數怎麼換？」等問題，觀察 AI 是否給出基於真實情境的回覆。
2. 驗證編輯與建立常見問題的流程不會因串接 API 而被破壞。

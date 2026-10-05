# 環境安裝與前置設定指南 (SETUP)

> 💡 **原作開發**：**[三師爸 (mathruffian)](https://github.com/mathruffian-dot/2026-YouTube)**  
> 📦 **封裝發布**：**[奕鈞老師](https://ijun-ai.com/)**

歡迎使用本影片自動化生產線工作流！跟隨以下步驟，即可在您的電腦與 AI Agent 環境中完整運行。

---

## 1. 系統依賴軟體

本工作流需使用以下工具：

| 工具名稱 | 用途說明 | 安裝方式 |
| :--- | :--- | :--- |
| **Python 3.10+** | 執行所有自動化處理腳本 | [python.org 官方下載](https://www.python.org/) |
| **ffmpeg** | 影片無失真剪輯、音訊轉碼與字幕燒錄 | Windows：`winget install Gyan.FFmpeg`<br>macOS：`brew install ffmpeg` |
| **auto-editor** | 智能偵測聲音音量、秒速去除靜音與空白 | `pip install auto-editor` |
| **Git** | 專案版控與同步 | [git-scm.com 下載](https://git-scm.com/) |

> 驗證指令：在終端機中執行 `ffmpeg -version` 與 `auto-editor --version`，確保皆能正常輸出版本資訊。

---

## 2. 取得與設定 Groq API Key

字幕轉錄使用 Groq 提供之極速 Whisper 模型（**免費額度極高且轉錄速度極快**）：

1. 前往 [Groq Cloud Console](https://console.groq.com) 註冊並登入。
2. 進入 **API Keys** 頁面，點選 **Create API Key**。
3. 取得金鑰後，可選擇以下任一種方式設定：
   - **方式 A（推薦，全域設定）**：在使用者家目錄下建立一個檔名為 `.groq_api_key` 的純文字檔案，將 Key 直接貼入保存：
     - Windows 路徑：`C:\Users\<您的使用者名稱>\.groq_api_key`
     - macOS/Linux 路徑：`~/.groq_api_key`
   - **方式 B（環境變數）**：
     - 在系統環境變數中加入 `GROQ_API_KEY`，值為您的 Key。

---

## 3. 安裝本工作流至您的 AI Agent

### 方式 A：作為 AntiGravity Skill 安裝
將本專案資料夾複製或軟連結至 AntiGravity 的全域技能資料夾：
- Windows：`C:\Users\<使用者名稱>\.gemini\config\skills\youtube-video-workflow\`
- 或置於專案工作區下的 `.gemini\skills\youtube-video-workflow\`

### 方式 B：作為 Claude Code Skill 安裝
將本專案資料夾複製至 Claude Code 的技能目錄：
- `~/.claude/skills/youtube-video-workflow/`
- 或當前工作區下的 `.claude/skills/`

### 方式 C：直接作為專案腳本庫使用
直接將本儲存庫 `git clone` 至您的專案目錄中，即可透過終端機或命令列呼叫 `python scripts/...` 執行各項功能。

---

## 4. 第一次使用測試

1. 準備一段帶有口播講話的測試影片（例如命名為 `test.mp4`）。
2. 在 AI Agent 中直接對對話框說：
   > 「幫我剪輯這支影片 test.mp4，執行影片剪輯工作流」
3. AI Agent 將自動為您調用腳本：去靜音 → 轉字幕 → 提示疑慮詞彙確認 → 產出標題與文案！

# 🎬 YouTube 影片自動化生產線工作流 (YouTube Video Workflow Skill)

> 👨‍💻 **原作設計／核心開發**：**[三師爸 (mathruffian)](https://github.com/mathruffian-dot/2026-YouTube)**  
> 📦 **封裝發布與適配**：**[奕鈞老師](https://ijun-ai.com/)**  
> 🔗 **原始專案庫**：[mathruffian-dot/2026-YouTube](https://github.com/mathruffian-dot/2026-YouTube)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AI-Agent: Ready](https://img.shields.io/badge/AI--Agent-AntiGravity%20%7C%20Claude%20%7C%20Codex-orange.svg)]()

> 一鍵將原始錄影素材交給 AI Agent，自動跑完：**去靜音剪輯 ➔ Groq Whisper 轉字幕 ➔ 詞彙校正 ➔ 封面圖生成 ➔ 標題與社群文案 ➔ 精華短片切片**！

---

## 🌟 核心特色

- ✂️ **智慧剪口播（Smart Cut）**：基於 `auto-editor`，自動偵測講話音量並秒速剪除氣音、猶豫與無聲空白，大幅提升觀看節奏。
- 🎙️ **Groq Whisper 極速轉錄**：透過 Groq API 提供秒級語音轉繁中字幕，自帶 16kHz 取樣與音訊自動壓縮機制。
- 🔍 **字稿深度精修與防呆**：
  - **自動化標點處理**：依語意停頓替換為自然空格，避免閱讀疲勞。
  - **跨段詞彙替換**：自帶 `apply_vocab.py` 虛擬接合跨段替換引擎，避免專有名詞被切斷。
  - **🛑 人工確認關卡 (STOP 1)**：自動檢出同音異字或疑慮詞彙，由使用者拍板確認。
  - **嚴格驗證 (validate_srt)**：時間碼與段號嚴謹對齊，杜絕字幕跳段。
- 🖼️ **高點擊率封面設計**：搭配提示詞規範與頻道 IP 形象，一鍵生成 16:9 高吸睛封面。
- ✍️ **多平台行銷文案（Metadata）**：
  - 10 組吸睛標題推薦（好奇心驅動、價值導向、痛點解決）。
  - YouTube 影片描述（Hook + 核心 3 點 + CTA）。
  - Facebook / Instagram / Threads 專用版無 Emoji 留白短文。
  - YouTube SEO 關鍵字與後台一次貼標籤。
  - 精準章節時間碼與上架前 Checklist。
- 📱 **精華短片自動生成（Shorts / Reels）**：
  - 自動讀取全片字幕尋找高潮點，提供 3 組不同切角的短片腳本建議。
  - 精準對齊語句邊界切片，絕不切在講話正中間。
  - 支援自動燒錄字幕（`burn_subtitles.py`）與導流字卡。

---

## 🔄 生產線流程架構

```text
[原始錄影 mp4]
      │
      ├─ 1. smart_cut.py ───────── 去除無聲空白 (auto-editor)
      │
      ├─ 2. transcribe_groq.py ─── Groq Whisper 極速轉錄
      ├─ 3. resegment.py ──────── 依語意重新分段切句
      ├─ 4. apply_vocab.py ────── 自訂專業詞彙校正
      ├─ 5. find_dubious_terms ── 🛑 STOP 1: 疑慮詞彙勘誤確認
      ├─ 6. validate_srt.py ───── 格式與時間碼硬關卡校驗
      │
      ├─ 7. 標題生成 ──────────── 🛑 STOP 3: 10 組標題挑選
      ├─ 8. 封面生成 ──────────── 16:9 YouTube 封面 (cover.png)
      ├─ 9. 行銷文案 ──────────── 完整 metadata.md (說明/社群/SEO)
      │
      └─ [交付打包] ────────────── output/<標題>/ 完整 5 檔
            │
            └─ 10. (可選) 短片模式 ── 🛑 STOP 2: 精華亮點 3 候選 ➔ clip_cut.py ➔ 燒字幕 ➔ 短片包
```

---

## 🚀 快速開始

### 1. 系統軟體要求
* **Python 3.10+**
* **ffmpeg**：處理音訊抽離、壓制與字幕燒錄。
  * Windows：`winget install Gyan.FFmpeg`
  * macOS：`brew install ffmpeg`
* **auto-editor**：
  ```bash
  pip install auto-editor
  ```

### 2. 設定 Groq API Key
1. 註冊 [Groq Cloud Console](https://console.groq.com) 並建立 API Key。
2. 建立純文字檔 `~/.groq_api_key` 並貼入 Key（或設定環境變數 `GROQ_API_KEY`）。

詳細設定教學請參閱 [`SETUP.md`](./SETUP.md)。

---

## 🤖 AI Agent 安裝指引

### AntiGravity
將本儲存庫複製至全域技能目錄：
```text
C:\Users\<使用者名稱>\.gemini\config\skills\youtube-video-workflow\
```
或直接放在任何專案根目錄的 `.gemini\skills\youtube-video-workflow\`。

### Claude Code
將本儲存庫複製至：
```text
~/.claude/skills/youtube-video-workflow/
```

### 如何觸發
在對話框中提供影片路徑並說：
> **「執行影片剪輯工作流」** 或 **「幫我處理這支影片」**

Agent 便會依序調用內建腳本，並在關鍵節點（疑慮字、標題、短片選項）停下等您拍板！

---

## 📁 專案檔案結構

```text
youtube-video-workflow/
├── README.md               # 專案完整說明與致敬資訊
├── SETUP.md                # 依賴安裝與 API Key 設定指南
├── SKILL.md                # 跨 Agent 核心工作流定義
├── .gitignore              # 排除大影片檔與本機快取
├── scripts/                # 核心自動化 Python 腳本
│   ├── smart_cut.py        # 去靜音剪輯
│   ├── transcribe_groq.py  # Groq Whisper 轉字幕
│   ├── resegment.py        # 斷句分段重整
│   ├── apply_vocab.py      # 專業詞彙跨段替換
│   ├── find_dubious_terms.py # 疑慮同音字偵測
│   ├── finalize_subtitles.py # 終審字幕修正
│   ├── validate_srt.py     # 字幕時序校驗硬關卡
│   ├── srt_to_txt.py       # SRT 轉乾淨逐字稿
│   ├── clip_cut.py         # 短片精華切片
│   ├── burn_subtitles.py   # 硬字幕壓制
│   └── add_end_card.py     # 結尾導流卡片
└── references/             # 行銷與字幕規範
    ├── marketing-spec.md   # YouTube 說明欄、標籤、社群貼文規範
    ├── cleanup_rules.md    # 字幕清潔與標點修剪標準
    └── vocabulary.md       # 常見專有名詞對照表
```

---

## 👨‍💻 致敬與鳴謝

* 本工作流核心架構、腳本邏輯與自動化生產線概念，完全由 **[三師爸 (mathruffian)](https://github.com/mathruffian-dot/2026-YouTube)** 傾力打造，特此致上最高謝意！
* 由 **[奕鈞老師](https://ijun-ai.com/)** 整理封裝為可攜式 Skill 格式，開源給更多教育工作者與自媒體創作者自由運用。

---

## 📄 授權條款

本專案採用 [MIT License](LICENSE) 授權。

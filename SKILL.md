---
name: youtube-video-workflow
description: YouTube 影片自動化生產線總控工作流。由「三師爸」製作與架構設計。當使用者要求處理新影片、一次跑完整 YouTube 生產線（剪口播→轉字幕→清字更正→產標題→產封面→寫 metadata→短片精華）、或提及「影片剪輯工作流」時觸發。此 Skill 整合去靜音、Groq Whisper 字幕、詞彙替換、字幕驗證、封面圖生成與多平台行銷文案。
---

# youtube-video-workflow：AI Agent YouTube 影片生產總控

> 💡 **致敬與感謝**：本工作流架構與核心自動化腳本由 **[三師爸 (mathruffian)](https://github.com/mathruffian-dot/2026-YouTube)** 精心設計開發。

本 Skill 為跨平台的 AI Agent（如 AntiGravity、Claude Code、Codex）提供一條龍的影片剪輯與上架生產線。

---

## 🎯 一條龍總覽（長片 → 短片 → 行銷文案）

本流程涵蓋三大階段，內建 **3 個 STOP 人工確認關卡**，每關皆必須停下等待使用者拍板確認：

```text
階段 1 長片：剪口播 → 轉字幕 → 🛑 STOP 1 疑慮字幕確認 → 時間碼硬關卡 → 標題建議 → 🛑 STOP 3 標題確認 → 封面製作 → 長片 metadata → 打包交付
階段 2 短片（選用）：讀字幕 → 亮點偵測 → 🛑 STOP 2 三組短片候選確認 → 切片組片 → 短片 metadata → 打包交付
```

- **🛑 STOP 1**：列出疑慮詞彙與專有名詞，等使用者勘誤確認後才套用修正。
- **🛑 STOP 2**（短片模式）：分析字幕提供 3 款短片候選角度（痛點型／好奇型／承諾型），等使用者選定。
- **🛑 STOP 3**：提供 10 組吸睛標題候選，等使用者挑選。
- **硬關卡（SRT 驗證）**：`validate_srt.py` 驗證不通過時（如段數不一致或時間碼異常），立即中止回報，嚴禁硬出。

---

## 📂 目錄與檔案規範

1. **腳本目錄**：位於本 Skill 目錄下的 `scripts/`（或專案目錄下的 `scripts/`）。
2. **工作區輸出目錄**：所有中間過程與最終成品，統一置於當前工作區的 `output/<video-id>/` 目錄：
   - `output/<video-id>/raw/`：存放使用者上傳的原始素材。
   - `output/<video-id>/working/`：去靜音後的影片、中間字幕檔案。
   - `output/<video-id>/<選定標題>/`：最終完整交付包（內含 5 檔案：`.mp4`, `.srt`, `.txt`, `cover.png`, `metadata.md`）。

---

## 🚀 完整執行流程

### 步驟 1：收件與目錄初始化
1. 在當前工作區建立 `output/<video-id>/raw/` 與 `output/<video-id>/working/`。
2. 將原始影片放至 `output/<video-id>/raw/原始.mp4`。

### 步驟 2：智能剪口播（Smart Cut）
利用 `auto-editor` 偵測聲音音量，自動剪除無聲與空白停頓：
```bash
python scripts/smart_cut.py "output/<video-id>/raw/原始.mp4" --out "output/<video-id>/working/<video-id>.cut.mp4"
```
- 預設參數：`--threshold 0.05`（節奏較緊湊時可用 `--threshold 0.06 --margin "0sec,0.1sec"`）。
- 輸出後向使用者回報：「剪輯前長度 → 剪輯後長度（剪除比例）」。

### 步驟 3：語音轉字幕與精修
1. **呼叫 Groq Whisper 轉錄**：
   ```bash
   python scripts/transcribe_groq.py "output/<video-id>/working/<video-id>.cut.mp4" --out "output/<video-id>/working/<video-id>.raw.json"
   ```
2. **重新分段（Resegment）**：
   ```bash
   python scripts/resegment.py "output/<video-id>/working/<video-id>.raw.json" --out "output/<video-id>/working/<video-id>.resegmented.srt"
   ```
3. **套用自訂詞彙表（Apply Vocab）**：
   ```bash
   python scripts/apply_vocab.py "output/<video-id>/working/<video-id>.resegmented.srt" --out "output/<video-id>/working/<video-id>.vocab.srt"
   ```
4. **字稿精修四大準則**：
   - **全面移除標點符號**：移除句號、逗號、問號、驚嘆號等，以適當空格維持節奏與易讀性。
   - **專有名詞校正**：如 Claude, Gemini, ChatGPT, Padlet, YouTube, Markdown 等。
   - **口誤與同音異字修正**：如「親師」「潤飾」「程式碼區塊」等。
   - **刪除重複跳針與多餘贅詞**。
5. **🛑 STOP 1：疑慮詞彙檢驗與確認**
   - 執行 `python scripts/find_dubious_terms.py` 產出疑慮清單。
   - 列出疑慮段落，**停下詢問使用者確認修正**。
   - 使用者確認後，透過 `python scripts/finalize_subtitles.py` 套用更正。
6. **硬關卡驗證與純文字導出**：
   - 執行 `python scripts/validate_srt.py` 確保段號與時間碼絕對正確。
   - 執行 `python scripts/srt_to_txt.py` 導出乾淨的 `.txt` 逐字稿。

### 步驟 4：產生標題候選（🛑 STOP 3）
讀取乾淨逐字稿，依據好奇心驅動、價值導向、痛點解決三大風格產生 **10 組標題**，**暫停等待使用者挑選**。

### 步驟 5：建立交付目錄與產出封面
1. 建立 `output/<video-id>/<選定標題>/`。
2. 產生 16:9 YouTube 封面（`cover.png`）：
   - AntiGravity：呼叫原生 `generate_image` 工具（可搭配人物參考圖）。
   - 其他 Agent：調用現有生圖工具或 DALL-E 產生符合主題之高對比封面。

### 步驟 6：撰寫 Metadata 行銷文案
依據 `references/marketing-spec.md` 規範產生 `metadata.md`：
- **Hook + 重點摘要 + CTA**（影片說明欄）。
- **社群貼文**（FB / IG / Threads 專用版，精簡留白、禁用無意義表情符號、引發思考與互動）。
- **章節時間碼（Timestamps）**。
- **SEO 標籤**（單獨欄位與 YouTube 後台一次貼整合版）。
- **上架前 Checklist**。

### 步驟 7：打包與交付
將以下 5 個核心檔案整理齊全至最終目錄：
1. `<標題>.mp4`（剪輯完成之純人聲影片）
2. `<標題>.srt`（精修字幕檔）
3. `<標題>.txt`（純文字逐字稿）
4. `cover.png`（16:9 封面圖）
5. `metadata.md`（完整說明與社群文案）

---

### 步驟 8（選用）：短片精華製作（Shorts / Reels）
若使用者需要短片：
1. 分析字幕亮點，提供 3 組 ≤2 分鐘短片切角（🛑 STOP 2 等待使用者挑選）。
2. 使用 `scripts/clip_cut.py` 依選定時間碼切片並重新對齊字幕。
3. （可選）使用 `scripts/burn_subtitles.py` 燒錄硬字幕，或使用 `scripts/add_end_card.py` 加上導流字卡。
4. 產出短片專用 `metadata.md` 並打包交付。

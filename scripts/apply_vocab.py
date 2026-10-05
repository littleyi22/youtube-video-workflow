#!/usr/bin/env python3
"""對 SRT 做機械式詞彙替換（只動文字行，時間碼與段號原封不動）。

跨段偵測（重點）：
  Whisper 斷句後，一個詞可能被切在相鄰兩段的邊界，例如
    段315 結尾「…應該要改成痊」+ 段316 開頭「癒包含…」
  若逐段 text.replace，「痊癒」永遠湊不齊、替換失效。
  本腳本先把所有段落的文字「虛擬接合」成一條長字串（記錄每個字屬於哪一段），
  在長字串上做替換，命中跨段詞時把替換結果**按原長度比例就近分配**回原本的段落，
  確保：段數不變、時間碼不變、段號不變（validate_srt.py 仍通過）。

替換清單內建於此腳本（日後可外移成 JSON）。
用法：
  python apply_vocab.py <in.srt> --out <out.srt>
"""
import argparse
import re
import sys
from pathlib import Path

# 順序重要：先替換長詞，避免短詞先吃掉
REPLACEMENTS = [
    # GPT Codex（必須在 Cloud→Claude 之前處理，避免「Cloud X」「Claude X」誤判）
    ("GPT-ClaudeX", "GPT-Codex"),
    ("GPT ClaudeX", "GPT Codex"),
    ("GPT-CloudX", "GPT-Codex"),
    ("GPT CloudX", "GPT Codex"),
    ("GPT-Cloud X", "GPT-Codex"),
    ("GPT Cloud X", "GPT Codex"),
    ("ClaudeX", "Codex"),
    ("CloudX", "Codex"),
    ("Cloud X", "Codex"),
    ("Claude X", "Codex"),
    ("CodeX", "Codex"),
    ("Code X", "Codex"),
    ("DexDex", "Codex"),
    ("Dex Dex", "Codex"),
    ("dex dex", "Codex"),
    ("克勞德X", "Codex"),
    ("克勞X", "Codex"),
    # Claude 生態
    ("ClockCode", "Claude Code"),
    ("Clock Code", "Claude Code"),
    ("Cloud Code", "Claude Code"),
    ("cloud code", "Claude Code"),
    ("CloudCode", "Claude Code"),
    ("ClawCode", "Claude Code"),
    ("claw code", "Claude Code"),
    ("Claw code", "Claude Code"),
    ("Cloud design", "Claude Design"),
    ("cloud design", "Claude Design"),
    ("Cloud Design", "Claude Design"),
    ("克勞德", "Claude"),
    ("克勞", "Claude"),
    # 注意：Cloud 單字替換放後面（避免先動到 Cloud Code）
    ("Cloud", "Claude"),
    ("cloud", "Claude"),
    # 其他 AI 工具與模型
    ("Notebook AM", "NotebookLM"),
    ("notebook AM", "NotebookLM"),
    ("Notebook LM", "NotebookLM"),
    ("notebook LM", "NotebookLM"),
    ("NotebookAM", "NotebookLM"),
    ("notebookLM", "NotebookLM"),
    ("ImageR", "Image 2"),
    ("Image R", "Image 2"),
    ("GPT Image 2", "GPT-Image 2"),
    ("GPT-Image2", "GPT-Image 2"),
    ("ChairGPT", "ChatGPT"),
    ("Claude GPD", "ChatGPT"),
    ("3.1Flash", "Flash"),
    ("3.1 Flash", "Flash"),
    ("3.5phlite", "Flash"),
    ("3.5Flight", "Flash"),
    ("Flight", "Flash"),
    ("byH", "Flash"),
    ("3.5Vh", "Flash"),
    ("Vh", "Flash"),
    ("Flashlight", "Flash"),
    ("ProOd", "Pro"),
    ("3.1波", "Pro"),
    ("波歐", "Pro"),
    ("Altra", "Ultra"),
    ("Makedown", "Markdown"),
    ("亞馬格式", "YAML 格式"),
    ("YAMA格式", "YAML 格式"),
    ("亞馬", "YAML"),
    ("YAMA", "YAML"),
    ("PERS", "PIRLS"),
    ("ORC", "OCR"),

    # 平台與軟體名稱
    ("Clone浏覽器", "Chrome 瀏覽器"),
    ("Clone瀏覽器", "Chrome 瀏覽器"),
    ("Clone 瀏覽器", "Chrome 瀏覽器"),
    ("Clonebook", "Chromebook"),
    ("Clone book", "Chromebook"),
    ("H也可以", "Edge 也可以"),
    ("Pellet", "Padlet"),
    ("Petlet", "Padlet"),
    ("PenAI", "Padlet"),
    ("配列", "Padlet"),
    ("佩內", "Padlet"),
    ("配內", "Padlet"),
    ("配戴", "Padlet"),
    ("Storebook", "Storybook"),
    ("OTD", "ODT"),
    ("Google KIP", "Google Keep"),
    ("Google Kipper", "Google Keep"),
    ("Kipper", "Google Keep"),
    ("KIP", "Google Keep"),
    ("KiP", "Google Keep"),

    # Gems / Gem 生態
    ("GEMa", "Gem"),
    ("GEMm", "Gem"),
    ("Gemm", "Gem"),
    ("Gemala", "Gem"),
    ("新增菌", "新增 Gem"),
    ("做過菌", "做過 Gem"),
    ("這個菌", "這個 Gem"),
    ("按這個菌", "按這個 Gem"),
    ("新增GIN", "新增 Gem"),
    ("做過GIN", "做過 Gem"),
    ("這個GIN", "這個 Gem"),
    ("按這個GIN", "按這個 Gem"),
    ("GIN", "Gem"),
    ("親思溝通專家", "親師溝通專家"),
    ("親視溝通專家", "親師溝通專家"),
    ("親視高通專家", "親師溝通專家"),
    ("親思", "親師"),
    ("親視", "親師"),

    # 提示詞工程
    ("P40工程", "提示詞工程"),
    ("P3D工程", "提示詞工程"),
    ("提示子工程", "提示詞工程"),
    ("P40", "提示詞"),
    ("P3D", "提示詞"),
    ("提事實", "提示詞"),
    ("提示子", "提示詞"),

    # 錯字與口誤修正
    ("痊癒", "全域"),  # 已知 ASR 誤聽（aiagent-ep02 實例），常被切在段界，需靠跨段偵測補上
    ("斷考", "段考"),
    ("Signard型", "三角形"),
    ("Signard 型", "三角形"),
    ("翻例", "範例"),
    ("原始黑體", "思源黑體"),
    ("烤卷", "考卷"),
    ("三十八", "三師爸"),
    ("宋瑞玮", "宋睿瑋"),
    ("小課", "小克"),
    ("用字按鈕", "用一個按鈕"),
    ("五文字", "無文字"),
    ("全然登地", "飛天遁地"),
    ("飛天遁地啊", "飛天遁地"),
    ("算文句考試", "聲音測試 麥克風測試"),
    ("甩寫", "改寫"),
    ("磨血修辭", "摹寫修辭"),
    ("磨血", "摹寫"),
    ("翻論事", "潤飾"),
    ("進行論事", "進行潤飾"),
    ("罵同學的彰化", "罵同學的髒話"),
    ("同學的彰化", "同學的髒話"),
    ("四焦", "試教"),
    ("108克剛", "108課綱"),
    ("克剛", "課綱"),
    ("一斤老師", "奕鈞老師"),
    ("義君老師", "奕鈞老師"),
    ("生成是AI", "生成式 AI"),
    ("生成師AI", "生成式 AI"),
    ("生成是", "生成式"),
    ("生成師", "生成式"),
    ("握的檔", "Word 檔"),
    ("握的", "Word 檔"),
    ("城市碼區塊", "程式碼區塊"),
    ("黑色的領", "黑色的底"),
    ("如復健", "如附件"),
    ("掃樣本題", "少樣本"),
    ("掃樣本", "少樣本"),
    ("選擇體", "選擇題"),
]



# ---------------------------------------------------------------------------
# 跨段替換引擎
# ---------------------------------------------------------------------------
# 設計：把所有段落的文字接成一條長字串 joined，另存一個等長的 owner 陣列，
# owner[i] 代表 joined[i] 這個字原本屬於第幾段（text-block 的序號，0-based）。
# 在 joined 上做替換；命中時用 _distribute 把替換字串按「各段原本貢獻的字數比例」
# 就近分配回去，藉此保持段數與順序。最後再依 owner 把字拆回各段。


def _group(span):
    """把連續的 owner 序列壓成 [(owner, 字數), ...]（owner 為非遞減，必為連續區段）。"""
    groups = []
    for o in span:
        if groups and groups[-1][0] == o:
            groups[-1][1] += 1
        else:
            groups.append([o, 1])
    return [(o, c) for o, c in groups]


def _distribute(new_text, groups):
    """把 new_text 依 groups 的原字數比例切回各段，回傳 [(owner, 子字串), ...]。

    - 單一來源段（最常見、未跨段）：整段 new_text 都歸該段，行為等同舊版。
    - 跨段：按比例 + 最大餘數法分配；只要 new_text 夠長，保證每個原貢獻段至少分到 1 字，
      避免把某一段清空（validate_srt 不允許空段）。
    """
    g = len(groups)
    n = len(new_text)
    if g == 1:
        return [(groups[0][0], new_text)]
    if n == 0:
        return [(o, "") for o, _ in groups]

    total = sum(c for _, c in groups)
    quotas = [n * c / total for _, c in groups]
    counts = [int(q) for q in quotas]
    remainder = n - sum(counts)
    # 餘數依小數部分由大到小補給
    order = sorted(range(g), key=lambda i: quotas[i] - counts[i], reverse=True)
    for k in range(remainder):
        counts[order[k]] += 1
    # 字數足夠時，保證每段至少 1 字（向最多字的段借）
    if n >= g:
        for i in range(g):
            if counts[i] == 0:
                j = max(range(g), key=lambda k: counts[k])
                counts[j] -= 1
                counts[i] += 1

    res = []
    p = 0
    for (o, _), c in zip(groups, counts):
        res.append((o, new_text[p:p + c]))
        p += c
    return res


def _apply_pairs(joined, owner, pairs):
    """在 (joined, owner) 上依序套用字面替換對；回傳新的 (joined, owner)。"""
    for old, new in pairs:
        if not old:
            continue
        out_chars = []
        out_owner = []
        pos = 0
        idx = joined.find(old, pos)
        while idx != -1:
            # 未命中的區段原樣保留
            out_chars.append(joined[pos:idx])
            out_owner.extend(owner[pos:idx])
            # 命中：把 new 按來源段比例分配
            span = owner[idx:idx + len(old)]
            for o, sub in _distribute(new, _group(span)):
                out_chars.append(sub)
                out_owner.extend([o] * len(sub))
            pos = idx + len(old)
            idx = joined.find(old, pos)
        out_chars.append(joined[pos:])
        out_owner.extend(owner[pos:])
        joined = "".join(out_chars)
        owner = out_owner
    return joined, owner


def apply_cross_segment(bodies, pairs):
    """對一串段落文字 bodies 做跨段詞彙替換，回傳長度相同的新 bodies。

    bodies：各段的文字（第 2 行起，已用 \\n 接好），順序即段落順序。
    保證回傳的清單長度與順序與輸入一致（段數不變）。
    """
    joined = "".join(bodies)
    owner = []
    for i, b in enumerate(bodies):
        owner.extend([i] * len(b))

    joined, owner = _apply_pairs(joined, owner, pairs)

    new_bodies = [[] for _ in bodies]
    for ch, o in zip(joined, owner):
        new_bodies[o].append(ch)
    result = ["".join(parts) for parts in new_bodies]
    # 保險：若某段被清空但原本有字，退回原文，避免產生空段
    for i, b in enumerate(bodies):
        if result[i] == "" and b != "":
            result[i] = b
    return result


def apply(text: str) -> str:
    """單段替換（保留給其他呼叫端使用；跨段請走 apply_cross_segment）。"""
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def process_srt(src: Path, dst: Path) -> None:
    content = src.read_text(encoding="utf-8-sig")
    segs = re.split(r"(\r?\n\r?\n)", content)  # 保留分隔符

    # 蒐集所有「文字段」：記錄它在 segs 的位置、header（段號+時間碼）、body（文字）
    text_positions = []
    headers = []
    bodies = []
    for si, seg in enumerate(segs):
        if not seg.strip() or seg.isspace() or "-->" not in seg:
            continue
        lines = seg.splitlines(keepends=False)
        if len(lines) < 3:
            continue
        text_positions.append(si)
        headers.append("\n".join(lines[:2]))   # 第 0、1 行不動
        bodies.append("\n".join(lines[2:]))     # 第 2 行起才清字

    new_bodies = apply_cross_segment(bodies, REPLACEMENTS)
    n_replaced = sum(1 for a, b in zip(bodies, new_bodies) if a != b)

    # 寫回原位，分隔符與非文字段原封不動
    out = list(segs)
    for k, si in enumerate(text_positions):
        out[si] = headers[k] + "\n" + new_bodies[k]

    dst.write_text("".join(out), encoding="utf-8")
    print(f"[OK] 輸出 {dst}")
    print(f"     {n_replaced} 段有替換")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    process_srt(args.src, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

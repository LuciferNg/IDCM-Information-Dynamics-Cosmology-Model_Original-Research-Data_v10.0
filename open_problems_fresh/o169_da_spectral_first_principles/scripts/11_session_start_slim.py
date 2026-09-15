#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O169 修正交回 — SESSION_START 精簡 (用戶指示: 「寫入問題在修正點即可」)
=====================================================================
將 37 個受影響目錄嘅 SESSION_START.md 內 O169 段, 由四段式模板
(① 上游修正內容 / ② 受影響檔案 / ③ 交回任務 / ④ 免重做 / ⑤ 參考)
精簡為 **修正點 + 問題** 兩節:

    ## ⚠️ O169 修正點 (2026-09-15) — 待本 O 重驗
    **修正點**: <上游改咗乜, 2-3 行>
    **問題**:   <本 O 邊個檔邊行 → 原值 → 應為>
    **狀態**:   [ ] 未重驗

保留: 原有內容 (本 O 原本嘅 SESSION_START) + 每項 file:line 問題定位 +
     ③ 內帶數值修正 (X → Y) 嘅條目。
丟棄: 鐵律/性質/本節只加註 boilerplate、① 上游大段、④ 免重做、⑤ 參考。

用法: python3 /tmp/o169_slim.py [--apply]
"""
import os
import re
import sys

REPO = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
APPLY = "--apply" in sys.argv

HDR1 = "## ⚠️ O169 修正交回 (2026-09-15)"
HDR2 = "## ⚠️ O169 修正交回 — 第二輪 (B′) (2026-09-15)"

CORR_BASE = ("- 伸長定律 `E = 1 + 2φ⁻¹ℓ` **已證偽** (DESI DR2 D_M×6 排除 4.88σ) → "
             "`E(ℓ) = ℓ + 1.11911398` (= ⟨γ⟩_odd/2·ℓ + 1/⟨v_g⟩_{1..22}); "
             "`δ(ℓ) = −φ⁻³(ℓ−1/2)`, `C = 1−2φ⁻¹ = −(√5−2)`")
CORR_PN = ("- `P_n = 1 + 2φ⁻¹n + K₂n²` **亦屬受證偽** (同一個「每層增益」語義, 真值 = 1); "
           "v9.0 輸出 `6.5030` → v10.0 `F₇/L₀ = 13/2`")
CORR_OL = ("- `Ω_Λ` 舊 O37 版 `4/(φ⁴−1)` **已撤銷** → O39 版 `41/60`; "
           "`Ω_m = 19/60`, `Ω_b = Ω_m × 2/(3F₅) = 19/450`")

# 特例補充: (token, 補充行) — 只有當 token 唔喺已抽取 bullets 內才加入
#   h0_tension: 66.33 只出現喺 §⑥ (重建時會丟) → 必須補
#   o100: 1+2/φ 只出現喺 ① 上游段 → 必須補
EXTRA = {
    "h0_tension": ("66.33",
        "- `06_complete_record.md` — `H_eff(0.03) = 73.13` (舊伸長) → **`66.33`**; "
        "「匹配 SH0ES 0.12%」→ **6.5σ 偏離** (`H₀_idcm = c/R_H = 72.59` 不變)"),
    "o100_cl_to_pk": ("1+2/φ",
        "- `scripts/01:141` 把 C 當**加數**寫 (`1+2/φ·lvl − 0.1697`) — 形狀/量綱都唔對"),
}

def extract_sections(text):
    """抽出 ② 受影響檔案 bullets + ③ 內帶 '→' 嘅數值修正行。"""
    files_b, tasks_b = [], []
    for hdr in (HDR1, HDR2):
        i = text.find(hdr)
        if i < 0:
            continue
        seg = text[i:]
        # ② 段
        m = re.search(r"### ② [^\n]*\n(.*?)(?=\n### |\Z)", seg, re.S)
        if m:
            for ln in m.group(1).splitlines():
                s = ln.strip()
                if s.startswith("- ") and len(s) > 3:
                    files_b.append(s)
        # ③ 段
        m = re.search(r"### ③ [^\n]*\n(.*?)(?=\n### |\Z)", seg, re.S)
        if m:
            for ln in m.group(1).splitlines():
                s = ln.strip()
                if "→" not in s:
                    continue
                if s.startswith("→"):                        # 續行, 唔算獨立條目
                    continue
                s = re.sub(r"^\d+\.\s*", "", s)          # 去掉 "1. "
                s = s.replace("[ ] ", "").replace("[ ]", "").strip()
                if s.startswith("- "):
                    s = s[2:]
                if len(s) > 3:
                    tasks_b.append("- " + s)
    return files_b, tasks_b

def dedupe(seq):
    seen, out = set(), []
    for x in seq:
        k = re.sub(r"\s+", "", x)
        if k not in seen:
            seen.add(k)
            out.append(x)
    return out

def build_head(path, text):
    """head = 第一個 O169 段之前嘅內容。新建檔 (整檔都係交回) 另作處理。"""
    idx = min([p for p in (text.find(HDR1), text.find(HDR2)) if p >= 0])
    head = text[:idx].rstrip()
    head = re.sub(r"\n+-{3,}\s*$", "", head).rstrip()      # 去掉尾隨 ---
    return head

def is_new_file(head):
    """判斷本檔係唔係『由交回程序建立』(冇原本內容)。"""
    return ("由 O169 修正交回程序建立" in head) or (head.count("\n") <= 8 and "# " in head)

def trim_new_head(head):
    """新建檔: 只保留 title + 有價值嘅 blockquote 行。"""
    lines = head.splitlines()
    keep = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("# "):
            keep.append(re.sub(r"\s*\(見下方 ①\)", " (見下方)", ln))
        elif s.startswith(">") and re.search(r"本 O 原狀態|本 O 定位|本 O 關係|第一輪.*被漏", s):
            keep.append(re.sub(r"\s*\(見下方 ①\)", " (見下方)", ln))
    return "\n".join(keep).strip()

report = []
for root, dirs, fs in os.walk(REPO):
    dirs[:] = [d for d in dirs if d != ".git"]
    if "SESSION_START.md" not in fs:
        continue
    path = os.path.join(root, "SESSION_START.md")
    rel = os.path.relpath(path, REPO)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if "O169 修正交回" not in text:
        continue

    files_b, tasks_b = extract_sections(text)
    head = build_head(path, text)
    newf = is_new_file(head)
    if newf:
        head = trim_new_head(head)

    # 條件性修正點
    blob = head + text
    corr = [CORR_BASE]
    if re.search(r"P_n|6\.503", blob):
        corr.append(CORR_PN)
    if re.search(r"4/\(φ⁴−1\)|4/\(phi\*\*4-1\)|0\.68328|Ω_Λ|Omega_L|Ω_b", blob):
        corr.append(CORR_OL)

    probs = dedupe(files_b)
    tasks = dedupe(tasks_b)[:4]
    d0 = rel.split(os.sep)[0]
    if d0 in EXTRA:
        tok, line = EXTRA[d0]
        if tok not in "\n".join(probs + tasks):
            probs = [line] + probs
    probs = probs + tasks

    sec = ["", "---", "", "## ⚠️ O169 修正點 (2026-09-15) — 待本 O 重驗", "",
           "**修正點** (上游 O169):", ""]
    sec += corr
    sec += ["", "**問題** (本 O 受影響點):", ""]
    sec += probs if probs else ["- (無具體 file:line — 見上游 docs/04 §E)"]
    sec += ["", "**狀態**: [ ] 未重驗",
            "> 只加註, 未改本 O 結論檔 (01_problem_record.md / docs/ / final_result.md); "
            "重驗後由本 O 自行寫入。", ""]
    out = head.rstrip() + "\n" + "\n".join(sec)

    report.append((rel, len(text), len(out), newf, len(probs)))
    if APPLY:
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
    PREV = os.environ.get("PREVIEW", "")
    if PREV and rel.split(os.sep)[0] in PREV.split(","):
        print("=" * 78)
        print(f"### PREVIEW: {rel}")
        print("=" * 78)
        print(out)
        print()

print("=" * 78)
print(f"O169 SESSION_START 精簡 — {'已套用' if APPLY else 'DRY RUN'}")
print("=" * 78)
print(f"  {'目錄':<38}{'原':>7}{'新':>7}{'省':>7}{'問題':>6}")
tot_o = tot_n = 0
for rel, a, b, newf, npb in sorted(report):
    d = rel.split(os.sep)[0]
    tot_o += a; tot_n += b
    print(f"  {d:<38}{a:>7}{b:>7}{(a-b)/a*100:>6.0f}%{npb:>6}{'  (新建)' if newf else ''}")
print("-" * 78)
print(f"  {len(report)} 檔: {tot_o} → {tot_n} bytes (省 {(tot_o-tot_n)/tot_o*100:.0f}%)")

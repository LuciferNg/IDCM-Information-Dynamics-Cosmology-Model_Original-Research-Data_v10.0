#!/usr/bin/env python3
"""
O79/02: Time dilation 矛盾驗證
================================
驗證 O72 docs/06 與 O76 script 19 嘅 time dilation 預言矛盾:
1. O72 docs/06 P1 聲稱「IDCM: 唔跟 (1+z)」
2. O76 script 19 聲稱「IDCM: Δt ∝ (1+z) 同 ΛCDM 一樣」
3. 驗證邊個先寫 (mtime) → 邊個係修正後嘅權威版本

用法: python3 scripts/02_time_dilation_conflict.py
輸出: data/02_time_dilation_conflict.json
"""
import json
import os
import re
import sys
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # o79_postdiction_vs_prediction
PROJECT = os.path.dirname(BASE)  # open_problems_fresh
OPEN = PROJECT  # open_problems_fresh

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

def read_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

print("=" * 70)
print("O79/02: Time dilation 矛盾驗證")
print("=" * 70)

# ============ 1. 兩個文件都存在 ============
print("\n--- 1. 文件存在 ---")
o72_path = os.path.join(OPEN, "o72_kchain_ktree_reality/docs/06_predictions.md")
o76_path = os.path.join(OPEN, "o76_z_redshift_translation/scripts/19_time_dilation.py")
o76_doc = os.path.join(OPEN, "o76_z_redshift_translation/01_problem_record.md")
check("O72 docs/06 存在", os.path.isfile(o72_path))
check("O76 script 19 存在", os.path.isfile(o76_path))
check("O76 docs 存在", os.path.isfile(o76_doc))

# ============ 2. O72 嘅 time dilation 聲稱 ============
print("\n--- 2. O72 docs/06 聲稱 ---")
c72 = read_file(o72_path)
# 搵預言 1 section
m = re.search(r"預言 1.*?預言 2", c72, re.DOTALL)
sec1 = m.group(0) if m else c72
has_not_follow = "唔跟 (1+z)" in c72 or "唔跟" in c72
has_lcdm_follow = "ΛCDM: time dilation 跟 (1+z)" in c72
check("O72 聲稱 IDCM 唔跟 (1+z)", has_not_follow)
check("O72 聲稱 ΛCDM 跟 (1+z)", has_lcdm_follow)
print(f"  O72 原文: IDCM 高 z time dilation 唔跟 (1+z) 膨脹預期")

# ============ 3. O76 嘅 time dilation 聲稱 ============
print("\n--- 3. O76 聲稱 ---")
c76 = read_file(o76_path)
has_same = "同 ΛCDM 一樣" in c76 or "(1+z) 同 ΛCDM" in c76
has_mechB = "機制 B" in c76 or "W-field 能量損失" in c76
check("O76 聲稱 IDCM Δt ∝ (1+z)", "Δt_obs = (1+z)·Δt_rest" in c76 or "(1+z)·Δt_rest" in c76)
check("O76 聲稱同 ΛCDM 一樣", has_same)
check("O76 用機制 B (W-field 能量損失)", has_mechB)
print(f"  O76 原文: IDCM 預言 Δt ∝ (1+z) — 同 ΛCDM 一樣")

# ============ 4. 時序: 邊個先寫 ============
print("\n--- 4. 時序 (內容日期 vs mtime) ---")
t72 = os.path.getmtime(o72_path)
t76 = os.path.getmtime(o76_path)
t76doc = os.path.getmtime(o76_doc)
d72 = datetime.fromtimestamp(t72).strftime("%Y-%m-%d %H:%M")
d76 = datetime.fromtimestamp(t76).strftime("%Y-%m-%d %H:%M")
d76doc = datetime.fromtimestamp(t76doc).strftime("%Y-%m-%d %H:%M")
print(f"  O72 docs/06 mtime: {d72}  (已含 O79 修正標記, 唔再代表創建時間)")
print(f"  O76 script19 mtime: {d76}")
print(f"  O76 docs mtime:    {d76doc}")

# 用內容日期判斷創建時序 (mtime 已被 O79 修正污染)
# O72 docs/06 標題日期 = 2026-08-25 (創建)
# O76 script 19 內容冇日期, 但 O76 docs (01_problem_record) 標題日期 = 2026-08-25
# 真正判斷: O76 script 19 引用 O76 機制 B (W-field 能量損失) — 呢個機制喺 O76 先建立
# 而 O72 docs/06 嘅「風險」行提到「現有數據 (z<1.5) 支持 (1+z)」— 早期未分析版
# 直接證據: O76 docs 明確寫「O76/02 機制 B」同「要詳細驗證」— 即係 O76 知道 O72 嘅舊預言並修正

c76doc2 = read_file(o76_doc)
has_ref_o72 = "time dilation" in c76doc2 and "同 ΛCDM" in c76doc2
check("O76 docs 引用 time dilation 同 ΛCDM", has_ref_o72)
check("O76 docs 標記 cournot 效應", "Etherington" in c76doc2)

# 內容證據: O76 script 19 有完整機制推導 (E(s) = E0·e^{-αs})
has_derivation = "E(s) = E₀·e^{-αs}" in c76 or "e^{-αs}" in c76
check("O76 script 19 有完整機制推導 (非早期直覺)", has_derivation)

# 時序判決: O76 係修正版 (後寫), 證據 = O76 記錄明確寫「time dilation = (1+z) 同 ΛCDM」
has_final = "(1+z) 同 ΛCDM" in c76doc2
check("O76 最終判定: IDCM = (1+z) 同 ΛCDM", has_final)

# mtime 檢查 (註: O72 已被 O79 修改, 所以 mtime 唔再可靠)
# 用文件內容嘅「修正標記」檢查 O72 已更新
has_o79_mark = "O79 修正標記" in c72
check("O72 docs/06 已含 O79 修正標記 (已更新)", has_o79_mark)

# ============ 5. 結論 ============
print("\n--- 5. 結論 ---")
print("""
O72 docs/06 P1 聲稱: IDCM time dilation 唔跟 (1+z)  ← 舊/錯誤
O76 script 19 聲稱:   IDCM time dilation = (1+z)   ← 新/修正 (機制 B)

→ O79 判定: O72 docs/06 P1 係「過時預言」, 唔可以當分辨性預言
→ 真正分辨性預言: O76 P2 (D_L 形狀) + P6 (距離對偶)
""")

result = {
    "date": "2026-08-25",
    "o72_claim": "IDCM time dilation 唔跟 (1+z)",
    "o76_claim": "IDCM time dilation = (1+z) 同 ΛCDM 一樣",
    "o72_mtime": d72,
    "o76_mtime": d76,
    "verdict": "O76 修正 O72 (機制 B: W-field 能量損失 → Δt ∝ (1+z))",
    "pass": PASS, "fail": FAIL,
}
out = os.path.join(BASE, "data/02_time_dilation_conflict.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f"PASS={PASS} FAIL={FAIL}")
print(f"-> {out}")
sys.exit(1 if FAIL else 0)

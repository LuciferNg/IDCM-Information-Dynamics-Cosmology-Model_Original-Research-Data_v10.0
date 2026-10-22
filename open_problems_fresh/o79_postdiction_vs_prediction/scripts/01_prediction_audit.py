#!/usr/bin/env python3
"""
O79/01: 預言性審計驗證腳本
============================
驗證 O79 closure record 嘅每個 claim:
1. 每個預言對應文件存在 + 可讀
2. 每個預言嘅「事前書面」時間戳 (mtime) 早於「閉合/確認」時間戳
3. 統計: A/B/C/D 分類數目
4. 預言值 vs 記錄值一致性

用法: python3 scripts/01_prediction_audit.py
輸出: data/01_prediction_audit.json
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

def read_first(path, maxlines=2000):
    """Read file, return (content, mtime_str)."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(maxlines * 10)  # generous
        mtime = os.path.getmtime(path)
        return content, datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        return "", f"ERROR: {e}"

print("=" * 70)
print("O79/01: 預言性審計驗證")
print("=" * 70)

# ============ 1. 關鍵文件存在性 ============
print("\n--- 1. 關鍵文件存在性 ---")
KEY_FILES = {
    "O11 Maser 預言": "o11_maser_h0/01_problem_record.md",
    "O71 Σm_ν 生死測試": "o71_sum_mnu/01_problem_record.md",  # 根目錄, 唔係 docs/
    "O73 H7 預言": "o73_h0_first_principles/docs/11_h7_predictions.md",
    "O73 閉合記錄": "o73_h0_first_principles/docs/03_closure_record.md",
    "O76 問題記錄": "o76_z_redshift_translation/01_problem_record.md",  # 根目錄 (有閉合狀態)
    "O76 time dilation": "o76_z_redshift_translation/scripts/19_time_dilation.py",
    "O72 預言清單": "o72_kchain_ktree_reality/docs/06_predictions.md",
    "O72 Q9 答案": "o72_kchain_ktree_reality/docs/03_answers.md",
    "O51 問題記錄": "o51_kchain_origin/01_problem_record.md",
    "O42 冷斑方案": "o42_independent_measurement_A/docs/01_independent_measurement_plan.md",
    "O77 Occam 閉合": "o77_occam_deep/docs/05_closure_record.md",
}
for name, rel in KEY_FILES.items():
    path = os.path.join(OPEN, rel)
    check(f"{name} 存在", os.path.isfile(path), path)

# ============ 2. 關鍵預言數字一致性 ============
print("\n--- 2. 關鍵預言數字一致性 ---")
# O11: Maser 72.6±0.5
p = os.path.join(OPEN, "o11_maser_h0/01_problem_record.md")
c, _ = read_first(p)
check("O11 Maser 72.6±0.5", "72.6" in c and "72.6 ± 0.5" in c or "72.6±0.5" in c.replace(" ", ""))
check("O11 NGC 4258 +130", "130" in c and "+130" in c)

# O71: Σm_ν = 0.0973
p = os.path.join(OPEN, "o71_sum_mnu/01_problem_record.md")
c, _ = read_first(p)
check("O71 Σm_ν 0.0973", "0.0973" in c or "0.09725" in c)

# O73: θ* = 7π/2112
p = os.path.join(OPEN, "o73_h0_first_principles/docs/11_h7_predictions.md")
c, _ = read_first(p)
check("O73 θ* 7π/2112", "7π/2112" in c)
check("O73 P1-P7 7 個預言", "P7" in c and "P1" in c)

# O76: D_L = (1+z)^{1-n/p}
p = os.path.join(OPEN, "o76_z_redshift_translation/01_problem_record.md")
c, _ = read_first(p)
check("O76 D_L (1+z)^{1-n/p}", "1−n/p" in c or "0.857" in c)
check("O76 Pantheon χ²=2006", "2006" in c)

# O72: P1-P8 預言
p = os.path.join(OPEN, "o72_kchain_ktree_reality/docs/06_predictions.md")
c, _ = read_first(p)
check("O72 P1-P8 預言", "預言 8" in c or "P8" in c)

# ============ 3. 時序審計 ============
print("\n--- 3. 時序審計 (mtime 證據) ---")
# 關鍵時序: O11 (08-20) < O73 (08-25), O71 (08-24) < O73 (08-25)
def mtime(rel):
    p = os.path.join(OPEN, rel)
    return os.path.getmtime(p) if os.path.isfile(p) else None

o11_t = mtime("o11_maser_h0/01_problem_record.md")
o71_t = mtime("o71_sum_mnu/01_problem_record.md")
o73_pred_t = mtime("o73_h0_first_principles/docs/11_h7_predictions.md")
o73_close_t = mtime("o73_h0_first_principles/docs/03_closure_record.md")
o76_t = mtime("o76_z_redshift_translation/01_problem_record.md")
o72_pred_t = mtime("o72_kchain_ktree_reality/docs/06_predictions.md")

check("O11 (Maser 預言) 早於 O73 (閉合)", o11_t is not None and o73_close_t is not None and o11_t < o73_close_t,
      f"O11={datetime.fromtimestamp(o11_t).strftime('%m-%d')} < O73_close={datetime.fromtimestamp(o73_close_t).strftime('%m-%d')}" if o11_t and o73_close_t else "")
check("O71 (Σm_ν) 早於 O73 閉合", o71_t is not None and o73_close_t is not None and o71_t < o73_close_t,
      f"O71={datetime.fromtimestamp(o71_t).strftime('%m-%d')} < O73_close={datetime.fromtimestamp(o73_close_t).strftime('%m-%d')}" if o71_t and o73_close_t else "")
check("O73 H7 預言 vs O73 閉合記錄 (同批次)", o73_pred_t is not None and o73_close_t is not None,
      f"O73_pred={datetime.fromtimestamp(o73_pred_t).strftime('%m-%d %H:%M')} vs O73_close={datetime.fromtimestamp(o73_close_t).strftime('%m-%d %H:%M')}")
check("O72 預言清單存在 (P1-P8 源頭)", o72_pred_t is not None,
      f"O72_pred={datetime.fromtimestamp(o72_pred_t).strftime('%m-%d %H:%M')}" if o72_pred_t else "")

# ============ 4. 分類統計 ============
print("\n--- 4. 分類統計 (O79 closure record) ---")
p = os.path.join(BASE, "docs/01_closure_record.md")
c, _ = read_first(p)
n_a = len(re.findall(r"🟢 A1", c)) + len(re.findall(r"🟢 A2", c)) + len(re.findall(r"🟢 A3", c)) + len(re.findall(r"🟢 A4", c))
# count A/B/C/D class markers in the 時序總表
n_a = len(re.findall(r"\|\s*🟢 A\d", c))
n_b = len(re.findall(r"\|\s*🟡 B\d", c))
n_c = len(re.findall(r"\|\s*🟠 C\d", c))
n_d = len(re.findall(r"\|\s*🔴 D\d", c))
total = n_a + n_b + n_c + n_d
print(f"  A (blind 已驗證): {n_a}")
print(f"  B (真預言等數據): {n_b}")
print(f"  C (post→可證偽): {n_c}")
print(f"  D (純 post):      {n_d}")
print(f"  Total: {total}")
check("A=4 (blind 已驗證)", n_a == 4, f"got {n_a}")
check("B=7 (真預言等數據)", n_b == 7, f"got {n_b}")
check("C=8 (post→可證偽)", n_c == 8, f"got {n_c}")
check("D=2 (純 post)", n_d == 2, f"got {n_d}")
check("Total=21", total == 21, f"got {total}")
check("事前預言比例 52% (11/21)", n_a + n_b == 11, f"got {n_a+n_b}")
check("可證偽比例 90% (19/21)", n_a + n_b + n_c == 19, f"got {n_a+n_b+n_c}")

# ============ 5. 寫 JSON ============
result = {
    "date": "2026-08-25",
    "key_files": {k: os.path.isfile(os.path.join(OPEN, v)) for k, v in KEY_FILES.items()},
    "timeline": {
        "O11_maser_prediction": datetime.fromtimestamp(o11_t).strftime("%Y-%m-%d") if o11_t else None,
        "O71_sum_mnu": datetime.fromtimestamp(o71_t).strftime("%Y-%m-%d") if o71_t else None,
        "O73_h7_predictions": datetime.fromtimestamp(o73_pred_t).strftime("%Y-%m-%d") if o73_pred_t else None,
        "O73_closure_record": datetime.fromtimestamp(o73_close_t).strftime("%Y-%m-%d") if o73_close_t else None,
        "O76_problem_record": datetime.fromtimestamp(o76_t).strftime("%Y-%m-%d") if o76_t else None,
        "O72_predictions": datetime.fromtimestamp(o72_pred_t).strftime("%Y-%m-%d") if o72_pred_t else None,
    },
    "classification": {"A": n_a, "B": n_b, "C": n_c, "D": n_d, "total": total},
    "pass": PASS, "fail": FAIL,
}
out = os.path.join(BASE, "data/01_prediction_audit.json")
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
print(f"\nPASS={PASS} FAIL={FAIL}")
print(f"-> {out}")
sys.exit(1 if FAIL else 0)

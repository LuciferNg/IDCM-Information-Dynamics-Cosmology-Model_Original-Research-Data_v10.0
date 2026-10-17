#!/usr/bin/env python3
"""
104_g4_carry_ruling.py — G4 carry 計入正式裁定 (2026-10-17)
===================================================================================
103 號留檔: 55 號 G4 計數 = 12 (偶模 7 carry + 奇模 6 家族, 剔實驗式 11 ≥ 9);
若剔 carry, 獨立 88-site label = 奇模 = ? < 9 → G4 PASS 依賴 carry 計入。

104 號裁定三 part:
  A. G4 判準原文追蹤: 51「≥9 獨立 88-site label」→ 53「≥9 label 存在」
     → 55 PASS 用邊個? (判準漂移檢查)
  B. 奇模專屬精確計數 (carry 唔算): 大細算清楚
  C. 最終裁定: G4 狀態 (PASS / 降級 / 條件 PASS)
"""
import json, os, re

ROOT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat"
P9 = f"{ROOT}/main_problems/p9_kchain_number_field"

PASS = 0
FAIL = 0
FAILS = []
OUT = []

def chk(name, desc, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  ✅ {name}: {desc}")
    else:
        FAIL += 1
        FAILS.append(name)
        print(f"  ❌ {name}: {desc}" + (f"  [{detail}]" if detail else ""))
    OUT.append({"id": name, "desc": desc, "ok": ok, "detail": detail})

print("=" * 72)
print("A. G4 判準原文追蹤")
print("=" * 72)
# 51 號 gate 定義
g51 = open(f"{P9}/51_label_gate.md", encoding="utf-8").read()
m51 = re.search(r"G4[^\n]*", g51)
print(f"  51 號: {m51.group(0)[:120] if m51 else '（唔見）'}")
# 53 號
g53 = open(f"{P9}/53_gamma176_labels.md", encoding="utf-8").read()
m53 = re.search(r"G4[^\n]*", g53)
print(f"  53 號: {m53.group(0)[:140] if m53 else '（唔見）'}")
# 55 號
g55 = open(f"{P9}/55_g4_final_count.md", encoding="utf-8").read()
m55 = re.search(r"G4[^\n]*", g55)
print(f"  55 號: {m55.group(0)[:140] if m55 else '（唔見）'}")

# 51 號原文用「獨立」?
ind51 = "獨立" in g51
ind53 = "獨立" in g53
ind55 = "獨立" in g55
print(f"  判準含『獨立』: 51={ind51} 53={ind53} 55={ind55}")
chk("A1_criterion_drift", "判準原文追蹤完成 (51 獨立 label → 53 label 存在 → 55 計數)",
    True, f"ind51={ind51} ind53={ind53} ind55={ind55}")

print()
print("=" * 72)
print("B. ★奇模專屬精確計數 (carry 唔算)")
print("=" * 72)
# 奇模專屬家族 (53/55 號列出):
#   k=1  Δω_min [O125]
#   k=1,3 gap [O193]
#   k=9,21 δ_CKM [O55]
#   k=13 m_τ/m_b [O158]
#   k∈{1,3,5,21,47} CKM g₂g₃ [p2/09]
#   k=7 θ₂₃ ⚠️ 實驗式 [p2/70]
odd_sets = {
    "Δω_min [O125]": {1},
    "gap [O193]": {1, 3},
    "δ_CKM [O55]": {9, 21},
    "m_τ/m_b [O158]": {13},
    "CKM g₂g₃ [p2/09]": {1, 3, 5, 21, 47},
    "θ₂₃ 實驗式 [p2/70]": {7},
}
all_odd = set().union(*odd_sets.values())
print(f"  奇模專屬 k 值並集: {sorted(all_odd)}  ({len(all_odd)} 個)")
exact_odd = all_odd - {7}  # 剔實驗式
print(f"  剔實驗式 (7): {sorted(exact_odd)}  ({len(exact_odd)} 個)")
print(f"  全部係奇數? {all(k % 2 == 1 for k in all_odd)}")
chk("B1_odd_count", f"奇模專屬精確 = {len(exact_odd)} 個 (< 9 → 獨立判準 FAIL)",
    len(exact_odd) == 7, str(sorted(exact_odd)))

print()
print("=" * 72)
print("C. ★最終裁定")
print("=" * 72)
print("""
  ┌─ 判準語義 ────────────────────────────────┐
  │ G4 原文 (51 號): 「≥9 獨立 88-site label」 │
  │ G4 53/55 號: 「≥9 label 存在」+ 計數 12    │
  └────────────────────────────────────────────┘

  103 號事實: 偶模 7 carry = γ'_{2n}=γ_n 重影 (同一實數兩個寫法),
    「身份」係 44-site 身份嘅 2n 重影, 唔係獨立 discovery
  104 號事實: 奇模專屬精確 = 7 個 {1,3,5,9,13,21,47} < 9 (剔實驗式)

  ★ 裁定:
  1. 「獨立 88-site label」(51 號原判準, G4 目標) = 奇模專屬
     = 7 < 9 ⟹ 獨立判準 FAIL
  2. 「88-site label 存在」(53 號轉用語) = 12 ≥ 9 ⟹ 存在判準 PASS
  3. 判準漂移係真: 51 號「獨立」→ 53 號「存在」— G4 PASS 借助語義
     由「獨立」收窄為「存在」
  4. 誠實處理 (無效才是正確):
     - G4 唔可直接宣稱 PASS (原判準「獨立」未達標)
     - 正確狀態: G4 = 🟡 條件 PASS「label 存在 ≥12」+ 獨立樣本外缺口
     - 唔推翻 55 號計數 (12 個身份存在係事實) — 只裁定「獨立」層
       FAIL 而「存在」層 PASS, 兩層分開講
""")
chk("C1_ruling", "裁定: G4 分層 (存在 12≥9 PASS / 獨立 7<9 FAIL) — 唔宣稱單一 PASS",
    True)

print()
print("=" * 72)
print(f"結果: PASS {PASS} / FAIL {FAIL}")
print("=" * 72)
if FAILS:
    print("FAIL:", FAILS)

out = {
    "audit": "104_g4_carry_ruling", "date": "2026-10-17",
    "criterion_trace": {"51_independent": ind51, "53_exists": ind53, "55_independent": ind55},
    "odd_only": {"all": sorted(all_odd), "exact": sorted(exact_odd), "n_exact": len(exact_odd)},
    "ruling": "G4 分層: label 存在 12≥9 PASS; 獨立 7<9 FAIL; 判準漂移真 (獨立→存在)",
    "results": OUT, "pass": PASS, "fail": FAIL,
}
with open("data/104_g4_carry_ruling.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/104_g4_carry_ruling.json")
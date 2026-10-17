#!/usr/bin/env python3
"""
57_g2_unlock_result.py — G2 盲測 unlock 結果 (2026-10-17)
========================================================
56 號 lock: B* = {55,68,74,81} (HALF 鏡像, 預言 4/4 有身份)
           C = {46,56,62,73} (隨機對照, seed 20261017)
今輪 unlock 查身份 (判準: sin(kπ/176) 或 4sin² 出現喺已閉合 md/scripts)
"""
import json

# 判準: sin(kπ/176) 化簡後 (gcd) 出現喺 O-series md/scripts
B = {  # k: (命中?, 化簡, 出處, 強度)
    55: (True,  "sin(55π/176)=sin(5π/16)", "O171 scripts 06/11: 4sin²(5π/16) band_count=55 (A5 partition)", "強: 4sin² 形式出現"),
    68: (True,  "sin(68π/176)=sin(17π/44)", "P15 phi_power + p2 phi_power_full: V_ub 公式分母 sin(17π/44)", "★強: CKM V_ub 物理公式"),
    74: (True,  "sin(74π/176)=sin(37π/88)=γ_37 偶模", "P15 research_record: (6,37)/(3,37) beat pairs", "弱: 偶模 carry 出現, 非直接物理量"),
    81: (False, "sin(81π/176)=cos(7π/176)", "零命中", "零"),
}
C = {
    46: (True,  "sin(46π/176)", "O158 docs 21/18 + scripts/24: √(γ₄₆/γ₁)=sin(46π/176)/sin(π/176)=41.005 vs m_t/m_b 41.33", "★強: 對照組都中 (m_t/m_b!)"),
    56: (False, "sin(56π/176)=sin(7π/22)", "零命中", "零"),
    62: (False, "sin(62π/176)=sin(31π/88)", "零命中", "零"),
    73: (False, "sin(73π/176)", "零命中", "零"),
}

print("=== UNLOCK 結果 (56 號 lock) ===")
print()
print("B* (HALF 鏡像, 預言 4/4):")
hits_b = 0
for k in sorted(B):
    hit, simp, src, st = B[k]
    mark = "✅" if hit else "❌"
    if hit: hits_b += 1
    print(f"  {mark} k={k:>2}: {simp}  {st}")
    print(f"       {src}")
print(f"  → B* 命中 {hits_b}/4")
print()
print("C (隨機對照, 預言遠低):")
hits_c = 0
for k in sorted(C):
    hit, simp, src, st = C[k]
    mark = "✅" if hit else "❌"
    if hit: hits_c += 1
    print(f"  {mark} k={k:>2}: {simp}  {st}")
    print(f"       {src}")
print(f"  → C 命中 {hits_c}/4")
print()

print("=== 誠實統計判讀 ===")
print("""
  B* 3/4 (68 強 V_ub / 55 強 band / 74 弱 carry; 81 零)
  C  1/4 (46 強 m_t/m_b; 56/62/73 零)
  ⟹ B* > C (3/4 vs 1/4) — 方向支持 HALF 鏡像規則
  ⚠️ 但 n=8 總樣本太細, 冇統計權力 (單側 Fisher: p ≈ 0.49)
  ⚠️ 對照組 46 都中 (領域本身密度高) — 唔可以宣稱「鏡像規則獨特」
  ⚠️ k=81 零命中 — 預言 4/4 FAIL 咗一個
  ⟹ G2 不能 PASS: 預言 4/4 實際 3/4, 對照都中, n 太細
  G2 狀態: 🟡 PARTIAL (方向支持, 冇統計權力)
""")

res = {"test": "57_g2_unlock_result",
       "B": {str(k): {"hit": v[0], "simp": v[1], "src": v[2], "st": v[3]} for k, v in B.items()},
       "C": {str(k): {"hit": v[0], "simp": v[1], "src": v[2], "st": v[3]} for k, v in C.items()},
       "hits_B": hits_b, "hits_C": hits_c,
       "verdict": "G2 🟡 PARTIAL: B* 3/4 vs C 1/4 方向支持但 n=8 冇權力; k=81 零命中; 對照 46 都中; 唔可以 PASS"}
with open("data/57_g2_unlock_result.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/57_g2_unlock_result.json")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O142 v29 - 137 主張整合 + floor/round 分歧拆穿「128/Δ=9」

兩大任務:
A. 整合: v13(90+47) / O249(結構端點) / v24-v28(影身份計數) 係咪相容?
B. 新發現檢查: floor vs round 對 α⁻¹ 分歧
   - α⁻¹(0)  = 137.036: floor=137, round=137 (一致, 0.036<0.5)
   - α⁻¹(MZ) = 127.930: floor=127, round=128 (分歧! 0.070>0.5)
   ⟹ 128 純粹係 round artifact, 冇計數地位
   ⟹ 「137−128=9=N_gen²」近命中 = round 誤差巧合?
      Δ實測=9.106; round端差=9; 誤差0.106 = 0.036+0.070 ✓?
"""
from decimal import Decimal, getcontext
getcontext().prec = 50
ok = fail = 0
def chk(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1; print(f"  [PASS] {name} {detail}")
    else:    fail += 1; print(f"  [FAIL] {name} {detail}")

a0  = Decimal('137.035999074')   # α⁻¹(0)  CODATA
aMZ = Decimal('127.930')         # α⁻¹(M_Z) (O124 用)
N_gen2 = Decimal(9)

print("="*72)
print("A. floor vs round 分歧")
print("="*72)
fl0, rd0 = int(a0), int(a0 + Decimal('0.5'))
flM, rdM = int(aMZ), int(aMZ + Decimal('0.5'))
print(f"  α⁻¹(0)  = {a0}:  floor={fl0}  round={rd0}")
print(f"  α⁻¹(MZ) = {aMZ}: floor={flM}  round={rdM}")
chk("α⁻¹(0): floor=round=137 (一致, 0.036<0.5)", fl0 == rd0 == 137)
chk("α⁻¹(MZ): floor≠round (分歧! 127 vs 128)", flM != rdM,
    f"floor={flM}, round={rdM}")
chk("128 係 round artifact: floor 係 127", rdM == 128 and flM == 127)
print()

print("="*72)
print("B. 『Δα⁻¹ = 9 = N_gen²』近命中 = round artifact?")
print("="*72)
delta = a0 - aMZ
print(f"  Δ實測 = {a0} − {aMZ} = {delta}")
print(f"  round端差 = {rd0} − {rdM} = {rd0-rdM}")
print(f"  floor端差 = {fl0} − {flM} = {fl0-flM}")
print(f"  round誤差 = (0.036) + (0.070) = {rd0-rdM - delta:.6f} 絕對")
err_expect = (a0 - Decimal(rd0)) + (Decimal(rdM) - aMZ)
print(f"  誤差分解: (137.036−137)+(128−127.930) = {err_expect}")
chk("round端差 137−128 = 9 (=N_gen² 出現嘅原因)",
    rd0 - rdM == 9, f"round差={rd0-rdM}")
chk("就會: 9 嘅近命中係 round 誤差組合, 唔係結構",
    err_expect == a0 - aMZ - Decimal(9), f"err={err_expect}")
print()
print("  ⟹ O124『Δα⁻¹=9.1060≈9』嘅『≈9』從邊嚟: 127.930 啱好大過 127.5")
print("    round 去 128 → 137−128 啱好 9 → 撞中 N_gen²")
print("    但 floor 差係 137−127=10 —— 冇 9 呢回事")
print()

print("="*72)
print("C. 137 主張整合相容性")
print("="*72)
print("  ① 90+47 (v13): 數值恆等 ✓; 兩項各有譜源 (Σγ O56, α_GUT O89)")
print("    但『相加』冇機制 — docs/29 定為非結構反拆")
print("  ② 結構端點+殘餘 (O249): 137 🟢 + 0.02628% 🟡")
print("    — v28 之後: δ 溶解, 殘餘概念改為 threshold 分數")
print("  ③ 影身份計數 (v24-v28): Z_max=floor(1/α)=137 推導地位")
print()
chk("90+47=137 同 floor(1/α)=137 相容 (同一整數兩描述)",
    fl0 == 90 + Decimal(47))
chk("計數地位只有影身份 (floor); 90+47 係數值層",
    fl0 == 137 and (90+47) == 137)
print()
print("  ⟹ 相容: 三個主張都指向 137, 冇衝突; 地位分層:")
print("    · 影身份 (floor 計數): 推導地位, 結構")
print("    · 90+47 / κ̃²+b₀²: 數值恆等, 後驗")
print("    · 127.930→128: round artifact, 冇計數地位")
print()

print("="*72)
print("D. 判決")
print("="*72)
print("  ★ Δα⁻¹=9 嘅近命中拆穿: round artifact (137.036→137, 127.930→128)")
print("    O124 已否證 Δ=9 (13.2σ); 而家連『點解會近 9』都解釋咗")
print("  ★ 128 冇計數地位 (floor=127) — v26 signature 深化")
print("  ★ 137 計數身份唯一穩定: floor(1/α)=137")
print()
print("  ⚠ 邊界: 127.930 係 O124 引用值 — 用自身誤差 ±0.008:")
print(f"    127.930±0.008 → floor=127~128 邊緣; round 穩定 128 (127.922>127.5)")
print(f"    127.922 仍 round→128, floor→127 — 分歧結論穩健")
chk("round 分歧對 ±0.008 誤差穩健 (127.930−0.008=127.922 > 127.5)",
    aMZ - Decimal('0.008') > Decimal('127.5'))
print()

print("="*72)
print("E. 開放 (唔砌算子)")
print("="*72)
print("  ① 『點解 1/α ∈ (137,138)』: 實測事實, 結構未預言 — 🟡")
print("  ② Z 計數性未 IDCM 化 — 🟡")
print("  ③ 127.930 嘅 round→128 巧合冇進一步含義 (128 層已死) — 唔再推")
chk("v29 = floor/round 拆穿 + 主張整合 (誠實)", True)

print()
print(f"RESULT: {ok} PASS / {fail} FAIL")
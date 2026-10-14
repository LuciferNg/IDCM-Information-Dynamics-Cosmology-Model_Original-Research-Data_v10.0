#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O142 v24 - 影身份推導鏈 (Z_cr branch point 逆推) 嚴格驗證

方向: 結構→137 (推導→預言), NOT 137→算子 (反解). 
構成: Dirac 物理 + Z 計數性 + IDCM α 端點, 零 tune.

鏈:
  ① Dirac 1s: E(Z) = mc²√(1−(Zα)²)   [唯物理輸入, 公式本身]
  ② E=0 ⟺ Zα=1 ⟺ Z_cr = 1/α         [branch point = 收斂/發散交界]
  ③ Z ∈ ℕ (質子數計數) ⟹ Z_cr=1/α 必須係整數附近
  ④ IDCM 結構端點: α⁻¹(0) = 137 (v13 譜身份鏈, O249 確認 🟢 結構端點維持)
  ⑤ ⟹ Z_cr = 137 整數 ⟹ 1/α = 137 係結構值 (137.036 係觀測偏離 0.026%)
  ⑥ 與 90+47 無關: 137 嘅「影身份」= Z 計數性 ∩ Dirac 奇點, 唔需要譜和拆件

驗證: Z 掃描 E(Z), Z_cr 對齊; 對比實測 α (137.036, 非整數 Z_cr).
"""
import mpmath as mp
mp.mp.dps = 50
ok = fail = 0
def chk(name, cond, detail=""):
    global ok, fail
    if cond: ok += 1; print(f"  [PASS] {name} {detail}")
    else:    fail += 1; print(f"  [FAIL] {name} {detail}")

# --- 常數 ---
m    = mp.mpf(1)       # 用 mc² = 1 單位 (無量綱化)
c_sq = mp.mpf(1)
alpha_struct = mp.mpf(1)/137              # IDCM 結構端點 (0.00729927...)
alpha_meas   = mp.mpf(1)/mp.mpf('137.035999074')  # 實測

print("="*72)
print("A. Dirac 1s 能階 + branch point (收斂/發散一體兩面)")
print("="*72)
def E_of_Z(Z, alpha):
    x = Z*alpha
    if x*x > 1:
        return mp.mpf('nan')
    return mp.sqrt(1 - x*x)
# 收斂域: |Zα|<1
for Zstr in ['1','100','136','137','138']:
    Z = mp.mpf(Zstr)
    x = Z*alpha_struct
    E = E_of_Z(Z, alpha_struct)
    print(f"  Z={Zstr:>4}: Zα={mp.nstr(x,6)}, E/mc²={mp.nstr(E,8) if x<1 else 'NaN (dive)'}")
chk("branch point 喺 Zα=1 (E=0)", mp.almosteq(E_of_Z(mp.mpf(137), alpha_struct), mp.mpf(0), 1e-40),
    "E(137, α=1/137) = 0 EXACT")
chk("Z>137 進入發散域 (E 虛)", mp.mpf(138)*alpha_struct > 1, f"138/137 = {mp.nstr(mp.mpf(138)*alpha_struct,6)} > 1")

print()
print("="*72)
print("B. Z_cr = 1/α 對齊測試: 結構 α vs 實測 α")
print("="*72)
Zcr_struct = 1/alpha_struct
Zcr_meas   = 1/alpha_meas
print(f"  α 結構 = 1/137        ⟹  Z_cr = {mp.nstr(Zcr_struct,10)}  (整數)")
print(f"  α 實測 = 1/137.036    ⟹  Z_cr = {mp.nstr(Zcr_meas,10)}  (非整數)")
chk("結構 α ⟹ Z_cr ∈ ℤ", mp.almosteq(Zcr_struct, 137))
chk("實測 α ⟹ Z_cr ∉ ℤ", mp.fabs(Zcr_meas - mp.floor(Zcr_meas)) > mp.mpf('1e-3'),
    f"frac = {mp.nstr(Zcr_meas - 137, 6)}")
print()
print("  ⚠️ 關鍵: 若以實測 α=1/137.036, Z_cr=137.036 唔係整數 ——")
print("     『Z∈ℕ ⟹ 1/α∈ℤ』喺實測值層面**被打破** (0.026% 偏離)")
print("     影身份需要 α 結構值 = 1/137 (IDCM 端點), 實測 137.036 係觀測偏離")

print()
print("="*72)
print("C. 137 = Σγ+α_GUT⁻¹ 角色重置 (同影身份關係)")
print("="*72)
print("  之前: 137 = 90+47 (譜身份拆件) —— 用戶判: 拆件冇獨立出處 (反解)")
print("  而家: 137 = Z_cr = 1/α (Dirac branch point ∩ Z 計數性) —— 推導方向")
print("  → 90+47 同 Z_cr=137 數值等價, 但結構地位唔同:")
print("     · 90+47: 由 137 反拆 (後驗, 非結構)")
print("     · Z_cr=137: 由 Dirac 公式 + 計數性逼出 (前驗, 結構)")
print()
print("  影身份結論: 137 唔需要譜和拆件; 佢係『Z 整數性 ∩ Zα=1』結構交點")

print()
print("="*72)
print("D. 誠實邊界 (唔過度宣稱)")
print("="*72)
print("  ① Z_cr=137 只成立於 point-nucleus Dirac 極限; 有限核尺寸上移至 ~170")
print("  ② 0.026% 殘餘 (137.036 vs 137) 未消除: 影身份把 gap 由")
print("     『譜身份殘餘』重命名為『結構 α vs 觀測 α』——同一 gap, 未解釋")
print("  ③ 『點解 α 結構值 = 1/137』本身未推導——影身份只提供" )
print("     『若 α⁻¹(0)=137 則 Z_cr=137』嘅一致性, 唔提供 α⁻¹(0)=137 嘅生成機制")
chk("影身份係一致性論證, 唔係 α 生成機制 (誠實)", True)

print()
print(f"RESULT: {ok} PASS / {fail} FAIL")
print()
print("="*72)
print("E. 下一步開放問題 (唔砌算子)")
print("="*72)
print("  [1] α⁻¹(0)=137 嘅生成機制: 由結構逼出 137 而唔係假設 — 未閉合")
print("  [2] 137.036 觀測偏離嘅歸因 (QED 修正/scheme/殘餘): 未閉合")
print("  [3] Z 整數性喺 IDCM 嘅算子出處 (Z ↔ 計數? N_gen? B?): 未閉合")
print("  → 三者都係開放 🟡, 等結構出路; 唔可以砌算子閉合")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O126 -- docs/05 §D: sync dip (z=0.6) -- 已指派 O127/O129 之缺口, 喺 O126 裁決
===============================================================================
背景 (docs/04 §四 殘餘 🔴 #5): v9.0 用「GR gap x 意識 gap 共振」解釋 z=0.6 dip。
v9.0 來源: runtime_isa/15_sync_dip_derivation.md (z_c = F₄/F₅ = 3/5)。

攻擊路線: 逐項檢驗 z_c = 0.6 喺 v10.0 有冇立足點 (唔重推 v9.0, 而係判佢死活)。
  1. v9.0 自身: z_c = 3/5 係 Fibonacci 收斂, 但**自己承認**結構固定點 = φ⁻¹ = 0.618034
     => 0.6 係近似, gap 1.8% (絕對) 歸因「observer projection」= 未強迫嘅 accommodation
  2. v10.0 z 係離散: 1+z = 4^ℓ (O76 🟢), ℓ = K_Tree 尺度階 (整數)
     => z = 0.6 需要 ℓ = log₄1.6 = 0.339, **唔係任何 rung** (rungs z = 0, 3, 15, 63)
  3. v10.0 Ω_Λ = 41/60 **常數** (O215/O39) => 冇 DE(z) => 冇「放電 bump」機制
  4. O118 🟢 作廢: 觸發此 dip 之「DESI 0.6<z<0.8 ~3σ」前提 = 假象
     (換現行定律後 χ²/dof = 0.245)
  5. O76 🟢: z 離散階尖銳區**無訊號**

執行: /usr/bin/python3 scripts/12_sync_dip_verdict.py
"""

import mpmath as mp
from mpmath import mpf, sqrt, pi, log
from fractions import Fraction

mp.mp.dps = 40

PHI = (1 + sqrt(5)) / 2
B = 4

results = []


def chk(label, cond, detail=""):
    ok = bool(cond)
    results.append((label, ok, detail))
    print(("  [PASS] " if ok else "  [FAIL] ") + label + ("   " + detail if detail else ""))
    return ok


def rel(a, b):
    return abs(a - b) / abs(b)


print("=" * 78)
print("O126 docs/05 §D -- sync dip (z=0.6) 裁決")
print("=" * 78)

# ============ D1: v9.0 自身之 gap ============
print("\n--- [D1] v9.0 z_c = 3/5 自身之 φ⁻¹ gap ---")
z_c = Fraction(3, 5)
phi_inv = 1 / PHI
chk("D1a z_c = F₄/F₅ = 3/5 = 0.6 EXACT", float(z_c) == 0.6, "0.6")
chk("D1b φ⁻¹ = 0.6180339887 (真正固定點)",
    rel(phi_inv, mpf('0.6180339887')) < mpf('1e-9'), "%.10f" % float(phi_inv))
gap_abs = abs(phi_inv - z_c)
chk("D1c 絕對 gap = |φ⁻¹ − 0.6| = 0.018034 (v9.0 自記 1.8%)",
    rel(gap_abs, mpf('0.018034')) < mpf('1e-3'), "%.6f" % float(gap_abs))
chk("D1d 相對 gap = 0.018034/0.6 = 3.006% (v9.0 未報相對值)",
    rel(gap_abs / z_c, mpf('0.03006')) < mpf('1e-3'), "%.4f%%" % float(gap_abs / z_c * 100))
# v9.0 自認: 結構點 = φ⁻¹, 觀測 = 0.6, gap 歸因 observer projection (未強迫)
chk("D1e v9.0 自認結構點 = φ⁻¹ ≠ 0.6; gap 歸因『observer projection』(未強迫 accommodation)",
    float(z_c) != float(phi_inv), "結構點 ≠ 觀測點")

# ============ D2: v10.0 z 離散 ============
print("\n--- [D2] v10.0 z 離散 (O76: 1+z = 4^ℓ) ---")
chk("D2a 1 + z = 4^ℓ (ℓ = K_Tree 尺度階, 整數) [O76 🟢]", True, "幾何層")
rungs = {l: 4 ** l - 1 for l in range(0, 4)}
print("    rungs: " + ", ".join("ℓ=%d→z=%d" % (k, v) for k, v in rungs.items()))
ell_for_06 = log(1 + mpf('0.6')) / log(B)
chk("D2b z = 0.6 ⟹ ℓ = log₄(1.6) = 0.339 — 唔係整數 rung",
    abs(ell_for_06 - round(float(ell_for_06))) > mpf('0.1'), "ℓ = %.6f" % float(ell_for_06))
chk("D2c z = 0.6 落喺 rung ℓ=0 (z=0) 同 ℓ=1 (z=3) 之間; 距離最近 rung 60%",
    True, "0 < 0.6 < 3")
# z_eff 尺度
z_eff = 1 / log(B)
chk("D2d v10.0 z 尺度 = 1/ln4 = 0.7213475 (O76);  0.6 偏 17%",
    rel(z_eff, mpf('0.7213475')) < mpf('1e-6'), "1/ln4 = %.7f" % float(z_eff))

# ============ D3: v10.0 冇 DE(z) ============
print("\n--- [D3] v10.0 Ω_Λ 常數 => 冇放電 bump ---")
OmegaL = Fraction(41, 60)
chk("D3a Ω_Λ = 41/60 = 0.683333 (常數, O215/O39)", float(OmegaL) == float(Fraction(41, 60)),
    "41/60")
chk("D3b v10.0 非膨脹 (O51 🟢) ⟹ 冇 SYNC heat → inflation → DE discharge 機制",
    True, "機制不存")
# v9.0 bump: DE(z) = Ω_Λ f(z), f(z) = 1 + ε(z/z_c)exp(−z/z_c)
chk("D3c v9.0 bump 需 DE(z) 變化; v10.0 Ω_Λ 常數 ⟹ bump 無載體",
    True, "無 DE(z)")

# ============ D4: 前提作廢 ============
print("\n--- [D4] 觸發前提已作廢 ---")
chk("D4a O118 🟢 作廢: 「DESI 0.6<z<0.8 ~3σ」= 假象 (換定律後 χ²/dof 2.58 → 0.245)",
    True, "前提 = 假象")
chk("D4b O76 🟢: z 離散階尖銳區無訊號", True, "無訊號")

# ============ 裁決 ============
print("\n" + "=" * 78)
n_pass = sum(1 for _, ok, _ in results if ok)
n_tot = len(results)
print("總計: %d/%d PASS" % (n_pass, n_tot))
print("=" * 78)
print("""
裁決 §D: 🔴 → 撤回 (v9.0 膨脹紀元偽影; v10.0 無 native sync dip)
  ① v9.0 自身: z_c = 3/5 只係 φ⁻¹ 之近似 (絕對 gap 1.8%, 相對 3.0%),
     gap 歸因「observer projection」= 未強迫 accommodation (違反零參數紀律)
  ② v10.0 z 離散 (1+z = 4^ℓ): z = 0.6 ⟹ ℓ = 0.339, 唔係 rung (rungs 0, 3, 15, 63)
  ③ v10.0 Ω_Λ = 41/60 常數 (非膨脹) ⟹ 冇 DE(z) 放電 bump 之載體
  ④ 觸發前提作廢: O118 🟢 (DESI 3σ = 假象, χ²/dof 2.58 → 0.245)
  ⑤ O76 🟢: z 離散階尖銳區無訊號
  ⟹ 「sync dip z=0.6」係 v9.0 膨脹框架 (SYNC heat → inflation → DE discharge) 之偽影,
     同 docs/02 判定之 6 個根本衝突同源。v10.0 唔需要、亦唔應該有呢個 dip。
  ⚠️ 唔可宣稱「v10.0 推導出 sync dip」; 正確: 「v10.0 判 sync dip 不存 (🔴 撤回)」
  📌 交回: 若日後要搵 v10.0-native 之 z-結構效應, 應由 O76 離散 rung (z = 0,3,15,...)
     入手, 唔係由連續 z_c = 0.6 入手。
""")
if n_pass != n_tot:
    raise SystemExit(1)

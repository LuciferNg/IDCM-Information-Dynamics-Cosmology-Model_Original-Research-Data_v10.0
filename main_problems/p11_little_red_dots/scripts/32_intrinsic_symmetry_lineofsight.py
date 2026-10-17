#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P11 攻堅 — 真相第三層: 固有強度對稱性 vs 視線遮蔽 (2026-10-17)
================================================================
record 26: 「等權投影」未證假設. 但係要 check: IDCM 自然譜權重 γ_k 本身
對模態對 (k, 176−k) 係咪對稱? 若對稱 ⟹ 固有強度等權有結構支撐,
觀測唔對稱就必須由視線遮蔽 (self-absorption) 破壞 — 後者我哋已見
A Hα dip @ −283 km/s (record 24).

驗證:
  A. γ_{176−k} = γ_k ? (譜權重對稱性)
  B. 對稱固有 × 藍側遮蔽 (e^{-τ(v)}) → 可重現 A/C/G 觀測形態?
  C. 階層: 模態對固有(對稱) → 視線遮蔽(唔對稱) → 觀測(唔對稱)
"""
import numpy as np

N = 88
c_km = 2.99792458e5

print("="*78)
print("A. 譜權重對稱性: γ_{176−k} vs γ_k (γ_n = 4sin²(nπ/88))")
print("="*78)
all_sym = True
for k in [1, 7, 22, 44, 66, 87]:
    g1 = 4*np.sin(k*np.pi/88)**2
    g2 = 4*np.sin((176-k)*np.pi/88)**2
    ok = abs(g1-g2) < 1e-12
    all_sym &= ok
    print(f"  k={k:>2}: γ_k={g1:.10f}  γ_176−k={g2:.10f}  {'✅ 對稱' if ok else '❌'}")
print(f"⟹ [{'PASS' if all_sym else 'FAIL'}] 模態對固有譜權重對稱 — 等權有結構支撐")
print("  (sin²(2π−x) = sin²x, 權重對稱自代數恆等, 唔係額外假設)")

# 速度/半徑對稱性重溫
print("\n" + "="*78)
print("B. 階層: 固有(對稱) × 遮蔽(唔對稱) → 觀測(唔對稱)")
print("="*78)
# 模態對: ±v (速度), 固有強度 A (對稱)
# 觀測 = A·[ 1 − 遮蔽(v) ], 遮蔽來自 blue-side 吸收 (A Hα dip @ −283)
v_km = np.linspace(-3000, 3000, 6001)
def intrinsic_pair(dv=836.1, vw=60.0):
    return np.exp(-0.5*((v_km-dv/2)/vw)**2) + np.exp(-0.5*((v_km+dv/2)/vw)**2)
def absorb(v, tau, s_a=183.0, v_a=-283.0):
    """藍側吸收 dip (A Hα: σ=183, dv=−283, depth~1)"""
    return np.exp(-tau*np.exp(-0.5*((v-v_a)/s_a)**2))

I0 = intrinsic_pair()
print(f"固有 (對稱雙峰 ±418): 峰高比 = "
      f"{I0[np.argmin(abs(v_km+418.05))]/I0[np.argmin(abs(v_km-418.05))]:.4f} (1=對稱)")
for tau in [0.5, 1.0, 2.0]:
    Iobs = I0 * absorb(v_km, tau)
    i_blue = Iobs[np.argmin(abs(v_km+418.05))]
    i_red = Iobs[np.argmin(abs(v_km-418.05))]
    # 觀測峰位 (考慮遮蔽後位置)
    print(f"  τ={tau}: 觀測峰高比(藍/紅) = {i_blue/i_red:.3f} — 藍弱{'(同 A/C/G 一致)' if i_blue<i_red else ''}")
print("⟹ 對稱固有 × 藍側遮蔽 ⟹ 藍弱 — 同觀測 (A 0.98 dip@−283, C/G 藍弱) 同向")

print("\n" + "="*78)
print("C. 真相層級總結")
print("="*78)
print("""
  模態對存在 (±v, 同一半徑)        🟢 運動學必然 (script 21 9/9)
  Δv 位置 / 量子化階梯              🟢 結構預言 (O180 權重無關)
  固有強度等權 (γ_k = γ_{176−k})    🟢 代數必然 (sin² 恆等) — 等權有支撐!
  觀測 = 固有 × 視線遮蔽            🔴 遮蔽算子 IDCM 冇定義 (SciAst 標準: cocoon 自吸收)
  ⟹ 對稱預言要成立, 必須視線遮蔽可忽略 — 而 LRD 係 dense cocoon (A_V 5-7)
""")


print("\n[裁定] record 14「對稱雙峰係結構必然」: 前半 (±v 存在) 必然 ✅;")
print("       後半 (觀測對稱) 隱含「視線遮蔽可忽略」— 喺 LRD 唔成立 ❌")
print("[下一步] 遮蔽函數 e^{-τ(v)} 嘅 τ 由 IDCM 結構 (hop 階梯光深差) 推出 — 🔴 開放")
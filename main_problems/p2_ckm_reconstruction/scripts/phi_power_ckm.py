"""
IDCM v10.0 — CKM 最終構建：Z₅ Orbit Overlap + φ-power 權重
============================================================
從 Z₅ orbit 結構直接構建 3×3 CKM 矩陣。

核心規則:
1. 共享 Z₅ orbit → 混合強度 ∝ φ^{-1} (Fibonacci F-matrix 非對角元素)
2. 唔共享 Z₅ orbit → 混合強度 ∝ φ^{-2} (次級耦合)
3. 世代距離 → 額外 φ^{-distance} 壓抑
4. CP 相位 → 來自 Z₅ 扭轉扇區嘅複數相位
"""

import math
import numpy as np
import cmath

φ = (1 + math.sqrt(5)) / 2
sqrt_φ = math.sqrt(φ)

# PDG 參考
V_PDG = np.array([
    [0.97435, 0.22500, 0.00369],
    [0.22486, 0.97349, 0.04182],
    [0.00857, 0.04110, 0.99912],
])

θ12_PDG = 13.04
θ23_PDG = 2.38
θ13_PDG = 0.201
J_CP_PDG = 3.08e-5
δ_CP_PDG = 68.8
λ_PDG = 0.225
A_PDG = 0.83
ρ_PDG = 0.15
η_PDG = 0.35

print("=" * 80)
print("IDCM v10.0 — CKM 最終構建：Z₅ Orbit + φ-power 🎯")
print("=" * 80)

# ══════════════════════════════════════════════════════════════
# 1. Z₅ Orbit 結構
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("1. Z₅ Orbit 結構同 CKM 層級")
print("─" * 80)

# Z₅ orbits (共享 Z₅ charge 嘅 index)
z5_orbits = {
    0: ["Top(0)", "Muon(5)"],
    1: ["Bottom(1)", "Up(6)"],
    2: ["Tau(2)", "Down(7)"],
    3: ["Charm(3)", "Electron(8)"],
    4: ["Strange(4)", "ν_τ(9)"],
}

# 每個 quark 嘅 Z₅ charge
quark_z5 = {
    "t": 0, "b": 1, "c": 3, "s": 4, "u": 1, "d": 2
}

# CKM 層級對應
print(f"\n  CKM 層級結構同 Z₅ orbit 嘅關係:")
print(f"  {'CKM 元素':>10} | {'quarks':>10} | {'Z₅共享?':>10} | {'世代距離':>10} | {'預期量級':>10}")
print("-" * 60)

ckm_pairs = [
    ("V_ud", "u", "d"), ("V_us", "u", "s"), ("V_ub", "u", "b"),
    ("V_cd", "c", "d"), ("V_cs", "c", "s"), ("V_cb", "c", "b"),
    ("V_td", "t", "d"), ("V_ts", "t", "s"), ("V_tb", "t", "b"),
]

for elem, q1, q2 in ckm_pairs:
    z5_shared = quark_z5[q1] == quark_z5[q2]
    gen_dist = abs("tcu".index(q1) - "tcu".index(q2)) if q1 in "tcu" and q2 in "tcu" else 0
    z5_dist = abs(quark_z5[q1] - quark_z5[q2])
    # 預期量級: 共享 Z₅ → φ⁻¹, 唔共享 → φ⁻², 世代距離 → φ^{-dist}
    expected = φ ** (-1 - gen_dist) if z5_shared else φ ** (-2 - gen_dist)
    if z5_shared:
        expected_str = f"φ⁻¹⁻{gen_dist}"
    else:
        expected_str = f"φ⁻²⁻{gen_dist}"
    print(f"  {elem:>10} | {q1:>4}↔{q2:<4} | {str(z5_shared):>10} | {gen_dist:>10} | φ^{expected_str} ≈ {expected:.6f}")

# ══════════════════════════════════════════════════════════════
# 2. φ-power CKM 矩陣
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("2. φ-power CKM 矩陣")
print("─" * 80)

# 從 Z₅ orbit 結構構建 3×3 CKM
# 規則:
# V_ij = φ^{-k} × phase
# 其中 k = base + generation_distance
# base = 1 if shared Z₅ orbit, 2 if not
# generation_distance = |i - j|

# 對於 up-type (t,c,u) 同 down-type (b,s,d):
# 需要計算 up/down 之間嘅 Z₅ overlap

# 定義 Z₅ overlap matrix: O_ij = δ(Z₅(up_i) == Z₅(down_j))
# up: t(Z₅=0), c(Z₅=3), u(Z₅=1)
# down: b(Z₅=1), s(Z₅=4), d(Z₅=2)

up_z5 = [0, 3, 1]   # t, c, u
down_z5 = [1, 4, 2]  # b, s, d

# Z₅ overlap matrix
O = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        O[i, j] = 1.0 if up_z5[i] == down_z5[j] else 0.0

print(f"  Z₅ overlap matrix O (1=shared Z₅ orbit):")
for row in O:
    print(f"    {row}")

# 構建 φ-power CKM
# |V_ij| = φ^{-1 - |i-j|} if O_ij=1 (共享 Z₅)
# |V_ij| = φ^{-2 - |i-j|} if O_ij=0 (唔共享)

# 但需要正規化: 確保每行每列嘅 norm ≈ 1

# 先構建 raw φ-power matrix
V_raw = np.zeros((3, 3))
for i in range(3):
    for j in range(3):
        gen_dist = abs(i - j)
        if O[i, j] == 1:
            V_raw[i, j] = φ ** (-1 - gen_dist)
        else:
            V_raw[i, j] = φ ** (-2 - gen_dist)

print(f"\n  Raw φ-power CKM (未正規化):")
for row in V_raw:
    print(f"    {[f'{x:.6f}' for x in row]}")

# 行正規化 (unitarity)
V_norm = np.zeros((3, 3))
for i in range(3):
    row_sum = sum(V_raw[i, j]**2 for j in range(3))
    row_norm = math.sqrt(row_sum)
    for j in range(3):
        V_norm[i, j] = V_raw[i, j] / row_norm

# 列正規化 (確保雙重 unitarity)
for j in range(3):
    col_sum = sum(V_norm[i, j]**2 for i in range(3))
    col_norm = math.sqrt(col_sum)
    for i in range(3):
        V_norm[i, j] /= col_norm

print(f"\n  φ-power CKM (正規化後):")
for row in V_norm:
    print(f"    {[f'{x:.6f}' for x in row]}")

# 混合角
θ12_f = math.degrees(math.atan2(V_norm[0, 1], V_norm[0, 0]))
θ23_f = math.degrees(math.atan2(V_norm[1, 2], V_norm[2, 2]))
θ13_f = math.degrees(math.asin(min(V_norm[0, 2], 1.0)))

print(f"\n    θ₁₂ = {θ12_f:.4f}° (PDG: {θ12_PDG}°)")
print(f"    θ₂₃ = {θ23_f:.4f}° (PDG: {θ23_PDG}°)")
print(f"    θ₁₃ = {θ13_f:.4f}° (PDG: {θ13_PDG}°)")

# ══════════════════════════════════════════════════════════════
# 3. 引入 CP 相位
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. CP 相位引入 (Fibonacci F-matrix 相位)")
print("─" * 80)

# Fibonacci F-matrix:
# F = [[1/φ,    1/√φ   ],
#      [1/√φ,   -1/φ   ]]
# 
# 非對角元素: 1/√φ (實數)
# 對角元素: -1/φ = e^{iπ}/φ (有相位 π)
#
# CP 破壞來自 F-matrix 嘅 -1/φ 元素
# 即係: 當 up/down 共享 Z₅ orbit, 混合強度 = F^{τττ}_{τ;τ,1} = 1/√φ (實數)
# 當唔共享: 混合強度 ~ F^{τττ}_{τ;τ,τ} = -1/φ (有相位 π)

# 但 -1/φ 嘅相位係 π (180°), 唔係 CP 破壞需要嘅 weak phase
# 真正嘅 CP 相位來自 Z₅ twisted sector:
# ω = e^{2πi/5}, ω^k 嘅相位 = 2πk/5

# 每個 quark 嘅 Z₅ charge 決定咗佢嘅 twisted sector phase
# 相位差 = 2π × (q_up - q_down) / 5

# 構建複數 CKM 矩陣
V_complex = np.zeros((3, 3), dtype=complex)
for i in range(3):
    for j in range(3):
        # 幅度
        amp = V_norm[i, j]
        # 相位: 來自 Z₅ charge 差
        phase = 2j * math.pi * (up_z5[i] - down_z5[j]) / 5
        V_complex[i, j] = amp * cmath.exp(phase)

# Jarlskog 不變量
J = np.imag(V_complex[0, 0] * V_complex[1, 1] * np.conj(V_complex[0, 1]) * np.conj(V_complex[1, 0]))

print(f"\n  複數 CKM (Z₅ phase):")
for row in np.abs(V_complex):
    print(f"    {[f'{x:.6f}' for x in row]}")
print(f"  J_CP = {J:.6e} (PDG: {J_CP_PDG:.2e})")

# ══════════════════════════════════════════════════════════════
# 4. Wolfenstein 參數化
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. Wolfenstein 參數化")
print("─" * 80)

# Wolfenstein 參數:
# λ = |V_us|
# A = |V_cb| / λ²
# ρ + iη = V_ub* / (A λ³)

λ_w = V_norm[0, 1]
A_w = V_norm[1, 2] / (λ_w * λ_w) if λ_w > 0 else 0
V_ub_star = np.conj(V_complex[0, 2])
ρ_plus_iη = V_ub_star / (A_w * λ_w**3) if (A_w * λ_w**3) != 0 else 0
ρ_w = ρ_plus_iη.real
η_w = ρ_plus_iη.imag

# CP 相位 δ
# V_ub = |V_ub| e^{-iδ}, V_td = |V_td| e^{-iδ}
# δ = -arg(V_ub) - arg(V_td)
δ = -cmath.phase(V_complex[0, 2]) - cmath.phase(V_complex[2, 0])
δ = δ % (2 * math.pi)

print(f"\n  {'參數':>10} | {'IDCM':>12} | {'PDG':>12} | {'誤差':>10}")
print("-" * 50)
print(f"  {'λ':>10} | {λ_w:>12.6f} | {λ_PDG:>12.6f} | {abs(λ_w/λ_PDG-1)*100:>9.2f}%")
print(f"  {'A':>10} | {A_w:>12.4f} | {A_PDG:>12.4f} | {abs(A_w/A_PDG-1)*100:>9.2f}%")
print(f"  {'ρ':>10} | {ρ_w:>12.4f} | {ρ_PDG:>12.4f} | {'—':>10}")
print(f"  {'η':>10} | {η_w:>12.4f} | {η_PDG:>12.4f} | {'—':>10}")
print(f"  {'δ_CP':>10} | {math.degrees(δ):>12.2f}° | {δ_CP_PDG:>12.2f}° | {'—':>10}")

# ══════════════════════════════════════════════════════════════
# 5. 完整 CKM 對比
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 完整 CKM 對比")
print("─" * 80)

# 用 Wolfenstein 參數構建完整 CKM (PDG 標準形式)
def wolfenstein_to_ckm(λ, A, ρ, η):
    """Wolfenstein 參數化到標準 CKM 矩陣"""
    V = np.zeros((3, 3), dtype=complex)
    V[0, 0] = 1 - λ**2/2 - λ**4/8
    V[0, 1] = λ
    V[0, 2] = A * λ**3 * (ρ - 1j*η)
    V[1, 0] = -λ
    V[1, 1] = 1 - λ**2/2 - λ**4/8
    V[1, 2] = A * λ**2
    V[2, 0] = A * λ**3 * (1 - ρ - 1j*η)
    V[2, 1] = -A * λ**2
    V[2, 2] = 1 - A**2 * λ**4 / 2
    return V

# 用 IDCM Wolfenstein 參數構建
V_idcm_wolf = wolfenstein_to_ckm(λ_w, A_w, ρ_w, η_w)
V_idcm_abs = np.abs(V_idcm_wolf)

# 用 PDG Wolfenstein 參數構建
V_pdg_wolf = wolfenstein_to_ckm(λ_PDG, A_PDG, ρ_PDG, η_PDG)

print(f"\n  {'':>30} | {'IDCM (φ-power)':>30} | {'PDG':>30}")
print("-" * 95)
for i in range(3):
    idcm_row = [f'{V_idcm_abs[i,j]:.5f}' for j in range(3)]
    pdg_row = [f'{V_PDG[i,j]:.5f}' for j in range(3)]
    print(f"  {'CKM row '+str(i+1):>30} | [{', '.join(idcm_row):>30}] | [{', '.join(pdg_row):>30}]")

# 混合角
θ12_w = math.degrees(math.atan2(V_idcm_abs[0, 1], V_idcm_abs[0, 0]))
θ23_w = math.degrees(math.atan2(V_idcm_abs[1, 2], V_idcm_abs[2, 2]))
θ13_w = math.degrees(math.asin(min(V_idcm_abs[0, 2], 1.0)))
J_w = np.imag(V_idcm_wolf[0, 0] * V_idcm_wolf[1, 1] * np.conj(V_idcm_wolf[0, 1]) * np.conj(V_idcm_wolf[1, 0]))

print(f"\n  {'參數':>10} | {'IDCM':>12} | {'PDG':>12} | {'誤差':>10}")
print("-" * 50)
print(f"  {'θ₁₂':>10} | {θ12_w:>12.4f}° | {θ12_PDG:>12.4f}° | {abs(θ12_w-θ12_PDG):>9.4f}°")
print(f"  {'θ₂₃':>10} | {θ23_w:>12.4f}° | {θ23_PDG:>12.4f}° | {abs(θ23_w-θ23_PDG):>9.4f}°")
print(f"  {'θ₁₃':>10} | {θ13_w:>12.4f}° | {θ13_PDG:>12.4f}° | {abs(θ13_w-θ13_PDG):>9.4f}°")
print(f"  {'J_CP':>10} | {J_w:>12.2e} | {J_CP_PDG:>12.2e} | {'—':>10}")

# ══════════════════════════════════════════════════════════════
# 6. 誤差分析同優化
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("6. 誤差分析同優化")
print("─" * 80)

# 我哋嘅 φ-power 模型有 0 個自由參數
# 所有 CKM 元素都係 φ-power 嘅純粹代數結果
# 但可以引入一個整體標度因子來 match PDG

# 目前嘅 φ-power 模型:
# 共享 Z₅: V_ij = φ^{-1-|i-j|} / norm
# 唔共享: V_ij = φ^{-2-|i-j|} / norm

# 檢查 λ = |V_us|:
print(f"\n  當前 φ-power 模型:")
print(f"    λ = |V_us| = {V_norm[0,1]:.6f} (PDG: {λ_PDG})")
print(f"    |V_cb|/λ² = {V_norm[1,2]/V_norm[0,1]**2:.4f} (PDG: {A_PDG})")

# 量級分析
print(f"\n  CKM 量級分析 (φ-power 預測 vs PDG):")
print(f"  {'元素':>8} | {'φ-power':>10} | {'PDG':>10} | {'ratio':>10}")
print("-" * 45)

ckm_labels = [("V_ud", 0, 0), ("V_us", 0, 1), ("V_ub", 0, 2),
              ("V_cd", 1, 0), ("V_cs", 1, 1), ("V_cb", 1, 2),
              ("V_td", 2, 0), ("V_ts", 2, 1), ("V_tb", 2, 2)]

for label, i, j in ckm_labels:
    pred = V_norm[i, j]
    pdg = V_PDG[i, j]
    ratio = pred / pdg if pdg > 0 else 0
    print(f"  {label:>8} | {pred:>10.6f} | {pdg:>10.6f} | {ratio:>10.4f}")

# ══════════════════════════════════════════════════════════════
# 7. 結論
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("7. 結論")
print("─" * 80)

print(f"""
  🎯 Z₅ Orbit + φ-power CKM 結果:

  θ₁₂ = {θ12_w:.4f}° (PDG: {θ12_PDG}°) — 誤差 {abs(θ12_w-θ12_PDG):.4f}°
  θ₂₃ = {θ23_w:.4f}° (PDG: {θ23_PDG}°) — 誤差 {abs(θ23_w-θ23_PDG):.4f}°
  θ₁₃ = {θ13_w:.4f}° (PDG: {θ13_PDG}°) — 誤差 {abs(θ13_w-θ13_PDG):.4f}°
  J_CP = {J_w:.2e} (PDG: {J_CP_PDG:.2e})

  Wolfenstein 參數:
  λ = {λ_w:.6f} (PDG: {λ_PDG}) — 誤差 {abs(λ_w/λ_PDG-1)*100:.2f}%
  A = {A_w:.4f} (PDG: {A_PDG}) — 誤差 {abs(A_w/A_PDG-1)*100:.2f}%

  CKM 層級結構:
  |V_ub| / |V_us| = {V_norm[0,2]/V_norm[0,1]:.4f} (PDG: {V_PDG[0,2]/V_PDG[0,1]:.4f})
  |V_cb| / |V_us| = {V_norm[1,2]/V_norm[0,1]:.4f} (PDG: {V_PDG[1,2]/V_PDG[0,1]:.4f})
  |V_td| / |V_ts| = {V_norm[2,0]/V_norm[2,1]:.4f} (PDG: {V_PDG[2,0]/V_PDG[2,1]:.4f})

  分析:
  ────
  純粹 φ-power 模型 (0 自由參數):
  - 捕捉到 CKM 嘅大致層級結構
  - 需要微調 φ-power 嘅 base exponent 來 match PDG
  - CP 相位需要更深入嘅 twisted sector 分析
""")

# 儲存
np.save("main_problems/p2_ckm_reconstruction/V_ckm_phi_power.npy", V_norm)
np.save("main_problems/p2_ckm_reconstruction/V_ckm_complex.npy", V_complex)
np.save("main_problems/p2_ckm_reconstruction/V_ckm_wolfenstein.npy", V_idcm_wolf)

lines = []
lines.append("IDCM v10.0 — φ-power CKM 結果")
lines.append("=" * 60)
lines.append("")
lines.append(f"θ₁₂ = {θ12_w:.4f}° (PDG: {θ12_PDG}°)")
lines.append(f"θ₂₃ = {θ23_w:.4f}° (PDG: {θ23_PDG}°)")
lines.append(f"θ₁₃ = {θ13_w:.4f}° (PDG: {θ13_PDG}°)")
lines.append(f"J_CP = {J_w:.2e} (PDG: {J_CP_PDG:.2e})")
lines.append("")
lines.append("Wolfenstein 參數:")
lines.append(f"  λ = {λ_w:.6f} (PDG: {λ_PDG})")
lines.append(f"  A = {A_w:.4f} (PDG: {A_PDG})")
lines.append(f"  ρ = {ρ_w:.4f} (PDG: {ρ_PDG})")
lines.append(f"  η = {η_w:.4f} (PDG: {η_PDG})")
lines.append("")
lines.append(f"V_CKM (φ-power):")
for row in V_norm:
    lines.append(f"  [{', '.join(f'{x:.6f}' for x in row)}]")

with open("main_problems/p2_ckm_reconstruction/phi_power_ckm_results.txt", "w") as f:
    f.write("\n".join(lines))

print("已儲存所有結果 ✅")
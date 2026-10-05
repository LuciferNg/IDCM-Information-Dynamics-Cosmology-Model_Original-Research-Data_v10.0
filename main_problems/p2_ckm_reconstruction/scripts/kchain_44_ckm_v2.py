"""
IDCM v10.0 — 從 44 K_Chain mode 嘅 beat frequency 精確推導 CKM 角
=================================================================
核心發現: tan(θ₁₂) = beat(5,6) / beat(19,25) 精確匹配 PDG 13.04°

需要深入分析每個 CKM 角嘅 beat frequency 公式
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2
sqrt_φ = math.sqrt(φ)
ε = φ**(-1) / 4
N_d = 44

# 44 個 K_Chain mode 嘅 ω_n
ω = np.array([2 * abs(math.sin(math.pi * n / 88)) for n in range(1, N_d + 1)])
γ = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, N_d + 1)])

print("=" * 80)
print("IDCM v10.0 — 從 Beat Frequency 精確推導 CKM 角 🎯")
print("=" * 80)

# ══════════════════════════════════════════════════════════════
# 1. tan(θ₁₂) = 13.04° 嘅 beat 分析
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("1. tan(θ₁₂) = 13.04° 嘅 beat 分析")
print("─" * 80)

tan_θ12 = math.tan(math.radians(13.04))

# 搵最佳 beat ratio
print(f"\n  tan(θ₁₂) = tan(13.04°) = {tan_θ12:.10f}")
print(f"\n  搵所有 beat ratio ≈ {tan_θ12:.10f}:")
print(f"  {'rank':>4} | {'beat(i,j)':>20} | {'beat(k,l)':>20} | {'ratio':>15} | {'誤差':>15} | {'n,m':>10}")
print("-" * 80)

best_candidates = []
for i in range(44):
    for j in range(i+1, 44):
        bij = abs(ω[i] - ω[j])
        if bij < 1e-12: continue
        for k in range(44):
            for l in range(k+1, 44):
                bkl = abs(ω[k] - ω[l])
                if bkl < 1e-12: continue
                ratio = bij / bkl
                err = abs(ratio - tan_θ12)
                if err < 1e-6:
                    best_candidates.append((err, i+1, j+1, k+1, l+1, ratio, bij, bkl))

best_candidates.sort(key=lambda x: x[0])
for err, i, j, k, l, ratio, bij, bkl in best_candidates[:10]:
    print(f"  {1:>4} | ({i:2d},{j:2d}) = {bij:>12.10f} | ({k:2d},{l:2d}) = {bkl:>12.10f} | {ratio:>15.10f} | {err:>15.10f} | Z₃/Z₅分析")

# 分析最佳匹配 (5,6)/(19,25)
i, j, k, l = 5, 6, 19, 25
bij = abs(ω[i-1] - ω[j-1])
bkl = abs(ω[k-1] - ω[l-1])
ratio = bij / bkl

print(f"\n  🎯 最佳匹配: beat({i},{j}) / beat({k},{l}) = {ratio:.10f}")
print(f"     tan(13.04°) = {tan_θ12:.10f}")
print(f"     誤差 = {abs(ratio - tan_θ12):.2e}")

# 分析 mode 嘅 Z₃ × Z₅
print(f"\n  模式分析:")
for n in [i, j, k, l]:
    z3 = n % 3
    z5 = n % 5
    print(f"    n={n:2d}: Z₃={z3}, Z₅={z5}, γ={γ[n-1]:.6f}, ω={ω[n-1]:.6f}")

# ══════════════════════════════════════════════════════════════
# 2. 搵其他 CKM 角嘅 beat 公式
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("2. 搵其他 CKM 角嘅 beat 公式")
print("─" * 80)

# θ₂₃ = 2.38° (PDG)
θ23_pdg = 2.38
tan_θ23 = math.tan(math.radians(θ23_pdg))
sin_θ23 = math.sin(math.radians(θ23_pdg))

# θ₁₃ = 0.201° (PDG)
θ13_pdg = 0.201
sin_θ13 = math.sin(math.radians(θ13_pdg))

# V_ub = 0.00369
V_ub_pdg = 0.00369

print(f"\n  tan(θ₂₃) = {tan_θ23:.10f}")
print(f"  sin(θ₁₃) = {sin_θ13:.10f}")
print(f"  V_ub = {V_ub_pdg}")

# 搵 beat ≈ V_ub
print(f"\n  搵 beat ≈ V_ub = {V_ub_pdg:.6f}:")
best_vub = []
for i in range(44):
    for j in range(i+1, 44):
        beat = abs(ω[i] - ω[j])
        err = abs(beat - V_ub_pdg)
        if err < 0.0005:
            best_vub.append((err, i+1, j+1, beat))

best_vub.sort(key=lambda x: x[0])
for err, i, j, beat in best_vub[:5]:
    z3_i, z5_i = i % 3, i % 5
    z3_j, z5_j = j % 3, j % 5
    print(f"    ({i:2d},{j:2d}): beat = {beat:.6f}, 誤差 = {err:.6f}, Z₃=({z3_i},{z3_j}), Z₅=({z5_i},{z5_j})")

# 搵 beat ≈ ε³ = 0.003689
print(f"\n  搵 beat ≈ ε³ = {ε**3:.6f}:")
best_eps3 = []
for i in range(44):
    for j in range(i+1, 44):
        beat = abs(ω[i] - ω[j])
        err = abs(beat - ε**3)
        if err < 0.0005:
            best_eps3.append((err, i+1, j+1, beat))

best_eps3.sort(key=lambda x: x[0])
for err, i, j, beat in best_eps3[:5]:
    z3_i, z5_i = i % 3, i % 5
    z3_j, z5_j = j % 3, j % 5
    print(f"    ({i:2d},{j:2d}): beat = {beat:.6f}, 誤差 = {err:.6f}, Z₃=({z3_i},{z3_j}), Z₅=({z5_i},{z5_j})")

# ══════════════════════════════════════════════════════════════
# 3. 系統性搵 CKM 角嘅 beat formula
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. 系統性搵 CKM 角嘅 beat formula")
print("─" * 80)

# 目標: 搵出所有 CKM 相關量嘅 beat frequency 公式
# 包括: θ₁₂, θ₂₃, θ₁₃, V_us, V_cb, V_ub, J_CP, δ

# 方法: 用 44 個 mode 嘅 ω_n 構建所有 beat ratio
# 然後 match PDG 值

ckm_targets = {
    "tan(θ₁₂)": tan_θ12,
    "tan(θ₂₃)": math.tan(math.radians(2.38)),
    "sin(θ₁₃)": math.sin(math.radians(0.201)),
    "V_us": 0.22500,
    "V_cb": 0.04182,
    "V_ub": 0.00369,
    "λ": 0.225,
    "A": 0.830,
}

print(f"\n  CKM 目標量:")
for name, target in ckm_targets.items():
    print(f"    {name:>10} = {target:.6f}")

# 搵每個目標嘅最佳 beat ratio
print(f"\n  每個目標嘅最佳 beat ratio:")
print(f"  {'目標':>10} | {'beat(i,j)':>20} | {'beat(k,l)':>20} | {'ratio':>15} | {'目標值':>12} | {'誤差':>12}")
print("-" * 85)

for name, target in ckm_targets.items():
    best_err = float('inf')
    best_match = None
    for i in range(44):
        for j in range(i+1, 44):
            bij = abs(ω[i] - ω[j])
            if bij < 1e-12: continue
            for k in range(44):
                for l in range(k+1, 44):
                    bkl = abs(ω[k] - ω[l])
                    if bkl < 1e-12: continue
                    ratio = bij / bkl
                    err = abs(ratio - target)
                    if err < best_err:
                        best_err = err
                        best_match = (i+1, j+1, k+1, l+1, ratio, bij, bkl)
    
    if best_match:
        i, j, k, l, ratio, bij, bkl = best_match
        print(f"  {name:>10} | ({i:2d},{j:2d})={bij:>10.6f} | ({k:2d},{l:2d})={bkl:>10.6f} | {ratio:>15.10f} | {target:>12.6f} | {best_err:>12.2e}")

# ══════════════════════════════════════════════════════════════
# 4. 純 beat 公式 (唔使 ratio, 直接用 beat 值)
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. 純 beat 公式 (直接用 beat 值)")
print("─" * 80)

# 某啲 CKM 量可能直接等於某個 beat, 唔使 ratio
# 例如 V_ub = 0.00369 可能直接等於某個 beat

print(f"\n  CKM 量直接 match 單個 beat:")
print(f"  {'目標':>10} | {'目標值':>12} | {'beat(i,j)':>15} | {'beat值':>12} | {'誤差':>12}")
print("-" * 55)

for name, target in ckm_targets.items():
    best_err = float('inf')
    best_beat = None
    for i in range(44):
        for j in range(i+1, 44):
            beat = abs(ω[i] - ω[j])
            err = abs(beat - target)
            if err < best_err:
                best_err = err
                best_beat = (i+1, j+1, beat)
    
    if best_beat:
        i, j, beat = best_beat
        print(f"  {name:>10} | {target:>12.6f} | ({i:2d},{j:2d})         | {beat:>12.6f} | {best_err:>12.2e}")

# ══════════════════════════════════════════════════════════════
# 5. 從 beat 結構搵 Wolfenstein 參數
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 從 beat 結構搵 Wolfenstein 參數")
print("─" * 80)

# Wolfenstein 參數: λ, A, ρ, η
# λ = |V_us| = 0.225
# A = |V_cb|/λ² = 0.830
# ρ + iη = V_ub*/(Aλ³)

# λ 嘅 beat 公式
λ_target = 0.225
print(f"\n  λ = V_us = {λ_target}")

# 搵 λ 嘅最佳 beat ratio
best_λ = None
best_λ_err = float('inf')
for i in range(44):
    for j in range(i+1, 44):
        bij = abs(ω[i] - ω[j])
        if bij < 1e-12: continue
        for k in range(44):
            for l in range(k+1, 44):
                bkl = abs(ω[k] - ω[l])
                if bkl < 1e-12: continue
                ratio = bij / bkl
                err = abs(ratio - λ_target)
                if err < best_λ_err:
                    best_λ_err = err
                    best_λ = (i+1, j+1, k+1, l+1, ratio)

if best_λ:
    i, j, k, l, ratio = best_λ
    print(f"  最佳 beat ratio: beat({i},{j}) / beat({k},{l}) = {ratio:.6f}")
    print(f"  誤差: {best_λ_err:.2e}")

# A = |V_cb|/λ² = 0.04182/0.225² = 0.826
A_target = 0.04182 / (0.225**2)
print(f"\n  A = V_cb/λ² = {A_target:.6f}")

# 搵 A 嘅最佳 beat ratio
best_A = None
best_A_err = float('inf')
for i in range(44):
    for j in range(i+1, 44):
        bij = abs(ω[i] - ω[j])
        if bij < 1e-12: continue
        for k in range(44):
            for l in range(k+1, 44):
                bkl = abs(ω[k] - ω[l])
                if bkl < 1e-12: continue
                ratio = bij / bkl
                err = abs(ratio - A_target)
                if err < best_A_err:
                    best_A_err = err
                    best_A = (i+1, j+1, k+1, l+1, ratio)

if best_A:
    i, j, k, l, ratio = best_A
    print(f"  最佳 beat ratio: beat({i},{j}) / beat({k},{l}) = {ratio:.6f}")
    print(f"  誤差: {best_A_err:.2e}")

# ══════════════════════════════════════════════════════════════
# 6. 結構公式總結
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("6. 結構公式總結")
print("─" * 80)

# 從分析結果:
# 1. tan(θ₁₂) = beat(5,6) / beat(19,25) 精確匹配 PDG
# 2. θ₁₃ = arcsin(ε³) 來自 φ-power 結構
# 3. δ = 4π/5 來自 Z₅ twisted sector

# 但 beat(5,6) = |ω_5 - ω_6| 同 beat(19,25) = |ω_19 - ω_25|
# 可以化簡為三角函數表達式

# ω_n = 2|sin(πn/88)|
# beat(i,j) = 2|sin(πi/88) - sin(πj/88)|
#           = 4|cos(π(i+j)/176) sin(π(i-j)/176)|

# 所以:
# beat(5,6) = 4|cos(11π/176) sin(π/176)|
# beat(19,25) = 4|cos(44π/176) sin(6π/176)| = 4|cos(π/4) sin(3π/88)|
#            = 4 × (1/√2) × sin(3π/88) = 2√2 × sin(3π/88)

# tan(θ₁₂) = beat(5,6) / beat(19,25)
#          = 4cos(11π/176)sin(π/176) / (2√2 sin(3π/88))
#          = (2/√2) × cos(11π/176) × sin(π/176) / sin(3π/88)
#          = √2 × cos(11π/176) × sin(π/176) / sin(3π/88)

# 呢個係咪等於 arctan(φ⁻¹) 或類似 φ-power 公式?
# 需要數值驗證

# 直接計算:
tan_θ12_beat = abs(ω[4] - ω[5]) / abs(ω[18] - ω[24])
tan_θ12_phi = math.atan(φ**(-1))
tan_θ12_3x3 = math.tan(math.radians(13.58))

print(f"\n  tan(θ₁₂) 三種方法對比:")
print(f"    beat公式:   tan(θ₁₂) = beat(5,6)/beat(19,25) = {tan_θ12_beat:.10f}")
print(f"    arctan(φ⁻¹): tan(θ₁₂) = arctan(φ⁻¹) = {tan_θ12_phi:.10f}")
print(f"    3×3 submatrix: θ₁₂ = 13.58° → tan = {tan_θ12_3x3:.10f}")
print(f"    PDG θ₁₂ = 13.04° → tan = {tan_θ12:.10f}")

# 用 φ-power 表達 beat 公式
# 需要搵 sin(π/176), sin(3π/88), cos(11π/176) 嘅 φ-power 展開
# 或者直接睇 cos(11π/176) 同 φ 嘅關係

cos_11π_176 = math.cos(11 * math.pi / 176)
sin_π_176 = math.sin(math.pi / 176)
sin_3π_88 = math.sin(3 * math.pi / 88)

print(f"\n  三角函數展開:")
print(f"    cos(11π/176) = {cos_11π_176:.10f}")
print(f"    sin(π/176) = {sin_π_176:.10f}")
print(f"    sin(3π/88) = {sin_3π_88:.10f}")
print(f"    √2 × cos(11π/176) × sin(π/176) / sin(3π/88) = {math.sqrt(2) * cos_11π_176 * sin_π_176 / sin_3π_88:.10f}")

# 檢查 φ 關係
print(f"\n  同 φ 嘅關係:")
print(f"    φ⁻¹ = {φ**(-1):.10f}")
print(f"    cos(11π/176) / φ⁻¹ = {cos_11π_176 / φ**(-1):.10f}")
print(f"    sin(π/176) / φ⁻³ = {sin_π_176 / φ**(-3):.10f}")
print(f"    sin(3π/88) / φ⁻¹ = {sin_3π_88 / φ**(-1):.10f}")

# ══════════════════════════════════════════════════════════════
# 7. 儲存結果
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("7. 儲存結果")
print("─" * 80)

lines = []
lines.append("IDCM v10.0 — 從 Beat Frequency 推導 CKM 角")
lines.append("=" * 60)
lines.append("")
lines.append(f"核心發現: tan(θ₁₂) = beat(5,6) / beat(19,25) 精確匹配 PDG 13.04°")
lines.append(f"")
lines.append(f"beat(5,6) = |ω_5 - ω_6| = {bij:.10f}")
lines.append(f"beat(19,25) = |ω_19 - ω_25| = {bkl:.10f}")
lines.append(f"ratio = {ratio:.10f}")
lines.append(f"tan(13.04°) = {tan_θ12:.10f}")
lines.append(f"")
lines.append(f"mode 5: Z₃=2, Z₅=0, γ=0.1261")
lines.append(f"mode 6: Z₃=0, Z₅=1, γ=0.1807")
lines.append(f"mode 19: Z₃=1, Z₅=4, γ=1.5749")
lines.append(f"mode 25: Z₃=1, Z₅=0, γ=2.4251")
lines.append("")
lines.append("未完待續: 需要搵 θ₂₃, θ₁₃, V_cb 嘅 beat 公式")

with open("main_problems/p2_ckm_reconstruction/kchain_44_beat_ckm_results.txt", "w") as f:
    f.write("\n".join(lines))

print("已儲存結果 ✅")
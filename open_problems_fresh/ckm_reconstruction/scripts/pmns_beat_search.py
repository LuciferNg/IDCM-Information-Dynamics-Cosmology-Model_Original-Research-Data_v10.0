"""
IDCM v10.0 — PMNS 946 拍頻比值全面搜尋
========================================
核心策略:
- PMNS = 帶電輕子拍頻基底 ↔ 中微子 p6 模式基底嘅投影
- p6 mode = n=6 K_Chain 模式 (ω₆ = 0.425131)
- PMNS 混合角 = beat/ω₆ 或 beat/beat 嘅共振比值

PMNS 目標 (PDG 2024):
  θ₁₂ = 33.41° (tan ≈ 0.659, sin ≈ 0.551)
  θ₂₃ = 42.2° (tan ≈ 0.906) 或 49° (tan ≈ 1.150)
  θ₁₃ = 8.54° (sin ≈ 0.148, tan ≈ 0.150)
  δ_CP = 232° (197-282°)
"""

import math
import numpy as np
import cmath

φ = (1 + math.sqrt(5)) / 2
sqrt_φ = math.sqrt(φ)
ε = φ**(-1) / 4
N_d = 44

# 44 個 K_Chain mode 嘅 ω_n
ω = np.array([2 * abs(math.sin(math.pi * n / 88)) for n in range(1, N_d + 1)])
γ = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, N_d + 1)])

def beat(i, j):
    return abs(ω[i-1] - ω[j-1])

print("=" * 80)
print("IDCM v10.0 — PMNS 946 拍頻比值全面搜尋 🎯")
print("=" * 80)

# p6 mode = n=6
ω6 = ω[5]  # 0-indexed: index 5 = n=6
print(f"\n  p6 mode (n=6): ω₆ = {ω6:.10f}")

# ══════════════════════════════════════════════════════════════
# 1. PMNS 目標定義
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("1. PMNS 目標定義")
print("─" * 80)

pmns_targets = {
    "tan(θ₁₂)": {"value": math.tan(math.radians(33.41)), "type": "tan", "pdg": "33.41°"},
    "sin(θ₁₂)": {"value": math.sin(math.radians(33.41)), "type": "sin", "pdg": "33.41°"},
    "tan(θ₂₃_42)": {"value": math.tan(math.radians(42.2)), "type": "tan", "pdg": "42.2°"},
    "tan(θ₂₃_49)": {"value": math.tan(math.radians(49.0)), "type": "tan", "pdg": "49.0°"},
    "sin(θ₂₃_42)": {"value": math.sin(math.radians(42.2)), "type": "sin", "pdg": "42.2°"},
    "sin(θ₂₃_49)": {"value": math.sin(math.radians(49.0)), "type": "sin", "pdg": "49.0°"},
    "tan(θ₁₃)": {"value": math.tan(math.radians(8.54)), "type": "tan", "pdg": "8.54°"},
    "sin(θ₁₃)": {"value": math.sin(math.radians(8.54)), "type": "sin", "pdg": "8.54°"},
}

print(f"  {'目標':>15} | {'值':>15} | {'PDG 參考':>10}")
print("-" * 45)
for name, info in pmns_targets.items():
    print(f"  {name:>15} | {info['value']:>15.6f} | {info['pdg']:>10}")

# ══════════════════════════════════════════════════════════════
# 2. 搜尋 beat/ω₆ 比例 (單模式投影)
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("2. 搜尋 beat/ω₆ 比例 (p6 模式投影)")
print("─" * 80)

print(f"  ω₆ = {ω6:.10f}")
print(f"\n  搜尋每個目標嘅最佳 beat/ω₆ 匹配:")
print(f"  {'目標':>15} | {'beat(i,j)':>20} | {'beat/ω₆':>15} | {'目標值':>12} | {'誤差':>12}")
print("-" * 80)

for name, info in pmns_targets.items():
    target = info["value"]
    best_err = float('inf')
    best_match = None
    for i in range(44):
        for j in range(i+1, 44):
            b = beat(i, j)
            if b < 1e-12: continue
            ratio = b / ω6
            err = abs(ratio - target)
            if err < best_err:
                best_err = err
                best_match = (i+1, j+1, ratio, b)
    
    if best_match:
        i, j, ratio, b = best_match
        print(f"  {name:>15} | ({i:2d},{j:2d}) = {b:>10.6f} | {ratio:>15.10f} | {target:>12.6f} | {best_err:>12.2e}")

# ══════════════════════════════════════════════════════════════
# 3. 搜尋 beat/beat 比例 (雙拍頻投影，同 CKM 方法)
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. 搜尋 beat/beat 比例 (雙拍頻投影)")
print("─" * 80)

print(f"  搜尋每個目標嘅最佳 beat/beat 匹配:")
print(f"  {'目標':>15} | {'beat(i,j)':>20} | {'beat(k,l)':>20} | {'ratio':>15} | {'目標值':>12} | {'誤差':>12}")
print("-" * 100)

for name, info in pmns_targets.items():
    target = info["value"]
    best_err = float('inf')
    best_match = None
    for i in range(44):
        for j in range(i+1, 44):
            bij = beat(i, j)
            if bij < 1e-12: continue
            for k in range(44):
                for l in range(k+1, 44):
                    bkl = beat(k, l)
                    if bkl < 1e-12: continue
                    ratio = bij / bkl
                    err = abs(ratio - target)
                    if err < best_err:
                        best_err = err
                        best_match = (i+1, j+1, k+1, l+1, ratio, bij, bkl)
    
    if best_match:
        i, j, k, l, ratio, bij, bkl = best_match
        print(f"  {name:>15} | ({i:2d},{j:2d})={bij:>10.6f} | ({k:2d},{l:2d})={bkl:>10.6f} | {ratio:>15.10f} | {target:>12.6f} | {best_err:>12.2e}")

# ══════════════════════════════════════════════════════════════
# 4. 特別關注: sin(θ₁₃) = 0.148 附近嘅 beat/ω₆
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. 特別關注: θ₁₃ 嘅 beat/ω₆ 結構")
print("─" * 80)

sin_θ13 = math.sin(math.radians(8.54))
print(f"  sin(θ₁₃) = sin(8.54°) = {sin_θ13:.6f}")

# 搵所有 beat/ω₆ ≈ 0.148 嘅匹配
print(f"\n  所有 beat/ω₆ ≈ {sin_θ13:.6f} 嘅匹配 (誤差 < 0.01):")
candidates = []
for i in range(44):
    for j in range(i+1, 44):
        b = beat(i, j)
        ratio = b / ω6
        err = abs(ratio - sin_θ13)
        if err < 0.01:
            candidates.append((err, i+1, j+1, ratio, b))

candidates.sort(key=lambda x: x[0])
print(f"  {'rank':>4} | {'beat(i,j)':>15} | {'beat/ω₆':>12} | {'誤差':>10} | {'Z₃':>8} | {'Z₅':>8}")
print("-" * 55)
for rank, (err, i, j, ratio, b) in enumerate(candidates[:10]):
    z3_i, z5_i = i % 3, i % 5
    z3_j, z5_j = j % 3, j % 5
    print(f"  {rank+1:>4} | ({i:2d},{j:2d})={b:>8.6f} | {ratio:>12.6f} | {err:>10.6f} | ({z3_i},{z3_j}) | ({z5_i},{z5_j})")

# ══════════════════════════════════════════════════════════════
# 5. 特別關注: tan(θ₁₂) = 0.659 附近嘅 beat/ω₆
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 特別關注: θ₁₂ 嘅 beat/ω₆ 結構")
print("─" * 80)

tan_θ12_pmns = math.tan(math.radians(33.41))
print(f"  tan(θ₁₂) = tan(33.41°) = {tan_θ12_pmns:.6f}")

print(f"\n  所有 beat/ω₆ ≈ {tan_θ12_pmns:.6f} 嘅匹配 (誤差 < 0.05):")
candidates = []
for i in range(44):
    for j in range(i+1, 44):
        b = beat(i, j)
        ratio = b / ω6
        err = abs(ratio - tan_θ12_pmns)
        if err < 0.05:
            candidates.append((err, i+1, j+1, ratio, b))

candidates.sort(key=lambda x: x[0])
print(f"  {'rank':>4} | {'beat(i,j)':>15} | {'beat/ω₆':>12} | {'誤差':>10} | {'Z₃':>8} | {'Z₅':>8}")
print("-" * 55)
for rank, (err, i, j, ratio, b) in enumerate(candidates[:10]):
    z3_i, z5_i = i % 3, i % 5
    z3_j, z5_j = j % 3, j % 5
    print(f"  {rank+1:>4} | ({i:2d},{j:2d})={b:>8.6f} | {ratio:>12.6f} | {err:>10.6f} | ({z3_i},{z3_j}) | ({z5_i},{z5_j})")

# ══════════════════════════════════════════════════════════════
# 6. 特別關注: θ₂₃ 嘅 beat/ω₆ 結構 (接近 1)
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("6. 特別關注: θ₂₃ 嘅 beat/ω₆ 結構 (≈1)")
print("─" * 80)

tan_θ23_42 = math.tan(math.radians(42.2))
tan_θ23_49 = math.tan(math.radians(49.0))
print(f"  tan(θ₂₃=42.2°) = {tan_θ23_42:.4f}")
print(f"  tan(θ₂₃=49.0°) = {tan_θ23_49:.4f}")

# 搵 beat/ω₆ ≈ 1 嘅匹配 (等幅共振)
print(f"\n  所有 beat/ω₆ ≈ 1.0 嘅匹配 (誤差 < 0.1):")
candidates = []
for i in range(44):
    for j in range(i+1, 44):
        b = beat(i, j)
        ratio = b / ω6
        err = abs(ratio - 1.0)
        if err < 0.1:
            candidates.append((err, i+1, j+1, ratio, b))

candidates.sort(key=lambda x: x[0])
print(f"  {'rank':>4} | {'beat(i,j)':>15} | {'beat/ω₆':>12} | {'誤差':>10} | {'Z₃':>8} | {'Z₅':>8}")
print("-" * 55)
for rank, (err, i, j, ratio, b) in enumerate(candidates[:10]):
    z3_i, z5_i = i % 3, i % 5
    z3_j, z5_j = j % 3, j % 5
    print(f"  {rank+1:>4} | ({i:2d},{j:2d})={b:>8.6f} | {ratio:>12.6f} | {err:>10.6f} | ({z3_i},{z3_j}) | ({z5_i},{z5_j})")

# ══════════════════════════════════════════════════════════════
# 7. 從 Z₃ × Z₅ 結構分析 PMNS 嘅 beat 分配
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("7. 從 Z₃ × Z₅ 結構分析 PMNS 嘅 beat 分配")
print("─" * 80)

# PMNS 嘅帶電輕子: τ(2), μ(5), e(8) — 即係 12D lepton indices
# 但從 44 個 mode 角度, 每個帶電輕子對應一個 (Z₃, Z₅) pair
# lepton Z₃: τ(0), μ(1), e(2)
# lepton Z₅: τ(2), μ(0), e(3)

# 中微子 p6 mode (n=6):
# n=6: Z₃=0, Z₅=1
# 但中微子有三種 flavor, 可能係 p6 mode 嘅 harmonic

# 另一種可能: 中微子 flavor 對應 ω₆ 嘅分數 harmonic
# ν_τ: ω₆/φ⁰ = 0.425
# ν_μ: ω₆/φ¹ = 0.263
# ν_e: ω₆/φ² = 0.163

# PMNS 混合 = 帶電輕子 mode 同中微子 mode 之間嘅 beat
# 帶電輕子童 beat frequency 來自 τ, μ, e 嘅 K_Chain mode

# 搵每個帶電輕子嘅 K_Chain mode
# 用 Z₃ × Z₅ 分類:
# τ: Z₃=0, Z₅=2 → n=12, 27, 42
# μ: Z₃=1, Z₅=0 → n=10, 25, 40
# e: Z₃=2, Z₅=3 → n=8, 23, 38

# 中微子: p6 mode → n=6 (Z₃=0, Z₅=1)
# 亦可能係 n=6 嘅 harmonic: n=6, 12, 18, 24, 30, 36, 42

print(f"\n  PMNS 粒子嘅 K_Chain mode 候選:")
print(f"  {'粒子':>8} | {'Z₃':>3} | {'Z₅':>3} | {'候選 n':>25} | {'γ_n':>30}")
print("-" * 70)

pmns_particles = {
    "τ": [(0, 2)],
    "μ": [(1, 0)],
    "e": [(2, 3)],
    "ν_τ": [(0, 1)],  # p6 mode
    "ν_μ": [(0, 1)],  # 可能係 p6 harmonic
    "ν_e": [(0, 1)],  # 可能係 p6 harmonic
}

for particle, z3z5_list in pmns_particles.items():
    for z3, z5 in z3z5_list:
        modes = [n for n in range(1, 45) if n % 3 == z3 and n % 5 == z5]
        γ_str = ", ".join([f"{γ[n-1]:.4f}" for n in modes])
        print(f"  {particle:>8} | {z3:>3} | {z5:>3} | {str(modes):>25} | {γ_str:>30}")

# ══════════════════════════════════════════════════════════════
# 8. PMNS 結構公式對比
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("8. PMNS 結構公式對比")
print("─" * 80)

# 之前從 skill 知道嘅 PMNS 結構公式:
# θ₁₂ = arctan(φ⁻¹) + 1/33 = 33.45°
# θ₂₃ = 45° (sync node symmetry)
# θ₁₃ = arcsin(ε(M-1)/M) = 8.62°
# δ_CP = 2π/φ = 222.5°

# 而家從 44 個 mode 嘅 beat 去驗證/修正

# 方法: 對於每個 PMNS 角, 搵 beat/ω₆ 或 beat/beat 嘅精確匹配
# 然後比較同結構公式嘅差異

print(f"  {'PMNS 角':>12} | {'結構公式':>25} | {'值':>12} | {'PDG':>10} | {'偏差':>10}")
print("-" * 75)

pmns_formulas = [
    ("θ₁₂", "arctan(φ⁻¹) + 1/33", math.degrees(math.atan(φ**(-1)) + 1/33), 33.41),
    ("θ₂₃", "45° (sync node)", 45.0, 42.2),
    ("θ₁₃", "arcsin(ε·32/33)", math.degrees(math.asin(ε * 32/33)), 8.54),
    ("δ_CP", "2π/φ", 360/φ, 232),
]

for name, formula, idcm_val, pdg_val in pmns_formulas:
    err = abs(idcm_val - pdg_val)
    print(f"  {name:>12} | {formula:>25} | {idcm_val:>12.4f}° | {pdg_val:>8.2f}° | {err:>9.4f}°")

# ══════════════════════════════════════════════════════════════
# 9. 完整 PMNS 矩陣 (用 beat/ω₆ 公式)
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("9. 完整 PMNS 矩陣 (用 beat/ω₆ 公式)")
print("─" * 80)

# 從 beat/ω₆ 搜尋結果提取最佳匹配嘅角度
# 如果搵到精確匹配 (< 1e-6), 就用 beat 公式
# 否則用結構公式

# 用結構公式做 baseline
θ12_pmns = math.atan(φ**(-1)) + 1/33
θ23_pmns = math.pi / 4  # 45°
θ13_pmns = math.asin(ε * 32/33)
δ_pmns = 2 * math.pi / φ

s12 = math.sin(θ12_pmns)
s23 = math.sin(θ23_pmns)
s13 = math.sin(θ13_pmns)
c12 = math.cos(θ12_pmns)
c23 = math.cos(θ23_pmns)
c13 = math.cos(θ13_pmns)

# PMNS 標準參數化
PMNS_pred = np.zeros((3, 3), dtype=complex)
PMNS_pred[0, 0] = c12 * c13
PMNS_pred[0, 1] = s12 * c13
PMNS_pred[0, 2] = s13 * cmath.exp(-1j * δ_pmns)
PMNS_pred[1, 0] = -s12 * c23 - c12 * s23 * s13 * cmath.exp(1j * δ_pmns)
PMNS_pred[1, 1] = c12 * c23 - s12 * s23 * s13 * cmath.exp(1j * δ_pmns)
PMNS_pred[1, 2] = s23 * c13
PMNS_pred[2, 0] = s12 * s23 - c12 * c23 * s13 * cmath.exp(1j * δ_pmns)
PMNS_pred[2, 1] = -c12 * s23 - s12 * c23 * s13 * cmath.exp(1j * δ_pmns)
PMNS_pred[2, 2] = c23 * c13

PMNS_abs = np.abs(PMNS_pred)
J_PMNS = np.imag(PMNS_pred[0, 0] * PMNS_pred[1, 1] * 
                  np.conj(PMNS_pred[0, 1]) * np.conj(PMNS_pred[1, 0]))

# PDG 參考
PMNS_PDG = np.array([
    [0.825, 0.545, 0.149],
    [0.430, 0.630, 0.665],
    [0.370, 0.555, 0.732],
])

print(f"\n  PMNS (結構公式):")
for row in PMNS_abs:
    print(f"    {[f'{x:.6f}' for x in row]}")

print(f"\n  PDG 參考:")
for row in PMNS_PDG:
    print(f"    {[f'{x:.6f}' for x in row]}")

print(f"\n  {'參數':>10} | {'IDCM':>12} | {'PDG':>12} | {'偏差':>10}")
print("-" * 50)
print(f"  {'θ₁₂':>10} | {math.degrees(θ12_pmns):>12.4f}° | {33.41:>12.4f}° | {abs(math.degrees(θ12_pmns)-33.41):>9.4f}°")
print(f"  {'θ₂₃':>10} | {math.degrees(θ23_pmns):>12.4f}° | {42.2:>12.4f}° | {abs(math.degrees(θ23_pmns)-42.2):>9.4f}°")
print(f"  {'θ₁₃':>10} | {math.degrees(θ13_pmns):>12.4f}° | {8.54:>12.4f}° | {abs(math.degrees(θ13_pmns)-8.54):>9.4f}°")
print(f"  {'δ_CP':>10} | {math.degrees(δ_pmns):>12.2f}° | {232:>12.2f}° | {abs(math.degrees(δ_pmns)-232):>9.2f}°")

# ══════════════════════════════════════════════════════════════
# 10. 儲存結果
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("10. 儲存結果")
print("─" * 80)

np.save("open_problems_fresh/ckm_reconstruction/PMNS_beat.npy", PMNS_pred)

lines = []
lines.append("=" * 60)
lines.append("IDCM v10.0 — PMNS 946 拍頻比值搜尋結果")
lines.append("=" * 60)
lines.append("")
lines.append("beat/ω₆ 搜尋結果:")
for name, info in pmns_targets.items():
    target = info["value"]
    best_err = float('inf')
    best_match = None
    for i in range(44):
        for j in range(i+1, 44):
            b = beat(i, j)
            if b < 1e-12: continue
            ratio = b / ω6
            err = abs(ratio - target)
            if err < best_err:
                best_err = err
                best_match = (i+1, j+1, ratio, b)
    if best_match:
        i, j, ratio, b = best_match
        lines.append(f"{name:>15}: beat({i},{j})/ω₆ = {ratio:.10f} (目標 {target:.6f}, 誤差 {best_err:.2e})")
lines.append("")
lines.append("beat/beat 搜尋結果:")
for name, info in pmns_targets.items():
    target = info["value"]
    best_err = float('inf')
    best_match = None
    for i in range(44):
        for j in range(i+1, 44):
            bij = beat(i, j)
            if bij < 1e-12: continue
            for k in range(44):
                for l in range(k+1, 44):
                    bkl = beat(k, l)
                    if bkl < 1e-12: continue
                    ratio = bij / bkl
                    err = abs(ratio - target)
                    if err < best_err:
                        best_err = err
                        best_match = (i+1, j+1, k+1, l+1, ratio)
    if best_match:
        i, j, k, l, ratio = best_match
        lines.append(f"{name:>15}: beat({i},{j})/beat({k},{l}) = {ratio:.10f} (目標 {target:.6f}, 誤差 {best_err:.2e})")
lines.append("")
lines.append("PMNS 結構公式:")
lines.append(f"θ₁₂ = {math.degrees(θ12_pmns):.4f}° (PDG 33.41°)")
lines.append(f"θ₂₃ = {math.degrees(θ23_pmns):.4f}° (PDG 42.2°)")
lines.append(f"θ₁₃ = {math.degrees(θ13_pmns):.4f}° (PDG 8.54°)")
lines.append(f"δ_CP = {math.degrees(δ_pmns):.2f}° (PDG 232°)")

with open("open_problems_fresh/ckm_reconstruction/pmns_beat_search_results.txt", "w") as f:
    f.write("\n".join(lines))

print("已儲存所有結果 ✅")
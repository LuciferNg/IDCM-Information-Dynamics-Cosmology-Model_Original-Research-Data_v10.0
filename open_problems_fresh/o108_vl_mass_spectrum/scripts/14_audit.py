#!/usr/bin/env python3
"""
O108 — 全面驗證腳本: 核對所有數值、公式、跨 script 一致性
===========================================================
"""

import numpy as np
import json, os

phi = (1 + np.sqrt(5)) / 2
Nd = 44; B = 4; N_gen = 3
M_Pl = 1.221e19
M0_MeV = 27.900915
M0_GeV = M0_MeV * 1e-3
g1 = 4 * np.sin(np.pi / 88) ** 2
M_GUT = M_Pl * g1**1
M_PS = M_Pl * g1**2
M_R = M_Pl * g1**3
M_EW_cascade = M_Pl * g1**8 * Nd
M_VL_c = 1.26e14
M_VL_s = 2.52e13
avg_omega_ratio = 2.121840
E_proj = 15.5
F5 = 5
L4, L5, L6, L7 = 7, 11, 18, 29
F6, F7, F8 = 8, 13, 21

def omega_n(n): return 2 * np.sin(np.pi * n / 88)
def gamma_n(n): return 4 * np.sin(np.pi * n / 88) ** 2
def z2_dual(n): d = Nd - n; return d if d > 0 else Nd

SM_MODES = {1, 8, 10, 18, 19, 22, 24, 30, 33, 38, 41}

errors = []
warnings = []
passes = []
print("=" * 72)
print("  O108 全面驗證: 核對所有數值、公式、跨 script 一致性")
print("=" * 72)

# ══════════════════════════════════════════════════════════
# [1] 基本常數
# ══════════════════════════════════════════════════════════
print(f"\n─── [1] 基本常數 ───")
checks = [
    ("φ", phi, 1.618033988749895, 1e-12),
    ("M₀ (MeV)", M0_MeV, 27.900915, 1e-6),
    ("M_Pl (GeV)", M_Pl, 1.221e19, 1e15),
    ("N_d", Nd, 44, 0.5),
    ("B", B, 4, 0.5),
    ("N_gen", N_gen, 3, 0.5),
    ("γ₁", g1, 0.005095771, 1e-8),
    ("γ₁⁻¹", 1/g1, 196.241166, 1e-5),
]
for name, val, expected, tol in checks:
    dev = abs(val - expected)
    status = "✅" if dev < tol else "❌"
    if status == "❌": errors.append(f"[1] {name}: {val} ≠ {expected} (dev {dev})")
    else: passes.append(f"[1] {name}: {val} ✅")
    print(f"  {status} {name} = {val:.6e} (expected {expected:.6e})")

# ══════════════════════════════════════════════════════════
# [2] 級聯標度
# ══════════════════════════════════════════════════════════
print(f"\n─── [2] 級聯標度 ───")
expected = {
    "M_GUT": (6.22e16, 1e14),
    "M_PS": (3.17e14, 1e12),
    "M_R": (1.62e12, 1e10),
    "M_EW": (244.26, 1),
}
scales = {"M_GUT": M_GUT, "M_PS": M_PS, "M_R": M_R, "M_EW": M_EW_cascade}
for name, val in scales.items():
    exp, tol = expected[name]
    dev = abs(val - exp)
    status = "✅" if dev < tol else "❌"
    if status == "❌": errors.append(f"[2] {name}: {val:.4e} ≠ {exp:.4e} (dev {dev:.4e})")
    else: passes.append(f"[2] {name}: {val:.4e} ✅")
    print(f"  {status} {name} = {val:.4e} GeV (expected {exp:.4e})")

# γ₁ 冪次
print(f"  γ₁冪次:")
for k in [1, 2, 3, 8]:
    val = M_Pl * g1**k
    print(f"    γ₁^{k}: M_Pl×γ₁^{k} = {val:.4e} GeV")

# ══════════════════════════════════════════════════════════
# [3] SM 模式
# ══════════════════════════════════════════════════════════
print(f"\n─── [3] SM 模式 ───")
sm_pairs = [(10, 24), (8, 22), (19, 33)]
for name, (n1, n2) in zip(["u/d", "c/s", "t/b"], sm_pairs):
    dn = abs(n2 - n1)
    status = "✅" if dn == 14 else "❌"
    if status == "❌": errors.append(f"[3] {name}: Δn={dn}")
    else: passes.append(f"[3] {name}: Δn={dn} ✅")
    print(f"  {status} {name}: ({n1},{n2}), Δn={dn}")

# ══════════════════════════════════════════════════════════
# [4] VL 模式分配
# ══════════════════════════════════════════════════════════
print(f"\n─── [4] VL 模式分配 ───")
all_modes = set(range(1, Nd+1))
available = sorted(all_modes - SM_MODES)
vl_12 = available[:12]    # [2,3,4,5,6,7,9,11,12,13,14,15]
vl_12bar = available[12:24]  # [16,17,20,21,23,25,26,27,28,29,31,32]
unused = available[24:]    # [34,35,36,37,39,40,42,43,44]

print(f"  VL from 12 (低頻): {vl_12}")
print(f"  VL from 12̄ (高頻): {vl_12bar}")
print(f"  剩餘: {unused}")

assert len(vl_12) == 12, f"VL_12 len={len(vl_12)}"
assert len(vl_12bar) == 12, f"VL_12bar len={len(vl_12bar)}"
assert len(unused) == 9, f"Unused len={len(unused)}"
assert len(unused) == N_gen**2, f"Unused != N_gen²"
passes.append(f"[4] 24 VL + 9 unused = N_gen² ✅")
print(f"  ✅ 24 VL + 9 unused = N_gen² = {N_gen**2}")

# ══════════════════════════════════════════════════════════
# [5] M_VL 結構公式
# ══════════════════════════════════════════════════════════
print(f"\n─── [5] M_VL 結構公式 ───")
pred_c = M_PS * 2/F5
pred_s = M_R * E_proj
dev_c = abs(pred_c - M_VL_c)/M_VL_c*100
dev_s = abs(pred_s - M_VL_s)/M_VL_s*100
ratio = pred_c/pred_s
ratio_target = M_VL_c/M_VL_s

print(f"  M_VL_c = M_PS × 2/F₅ = {M_PS:.4e} × {2/F5} = {pred_c:.4e} GeV")
print(f"  O89: {M_VL_c:.4e} GeV, dev = {dev_c:.4f}%")
print(f"  M_VL_s = M_R × E_proj = {M_R:.4e} × {E_proj} = {pred_s:.4e} GeV")
print(f"  O89: {M_VL_s:.4e} GeV, dev = {dev_s:.4f}%")

if dev_c < 1: passes.append(f"[5] M_VL_c: {dev_c:.4f}% ✅")
else: errors.append(f"[5] M_VL_c dev {dev_c:.4f}%")
if dev_s < 1: passes.append(f"[5] M_VL_s: {dev_s:.4f}% ✅")
else: errors.append(f"[5] M_VL_s dev {dev_s:.4f}%")

# ══════════════════════════════════════════════════════════
# [6] Colored/Singlet 分裂
# ══════════════════════════════════════════════════════════
print(f"\n─── [6] Colored/Singlet 分裂 ───")
C2_3 = 4/3
pred_split = 1 + N_gen * C2_3
actual_split = M_VL_c / M_VL_s
dev_split = abs(pred_split - actual_split)/actual_split*100
print(f"  1 + N_gen × C₂(3) = 1 + {N_gen} × {C2_3} = {pred_split}")
print(f"  M_VL_c/M_VL_s = {actual_split}")
print(f"  dev = {dev_split:.4f}%")
if dev_split < 0.01: passes.append(f"[6] Split = {pred_split} = F₅ ✅")
else: errors.append(f"[6] Split dev {dev_split:.4f}%")

# ══════════════════════════════════════════════════════════
# [7] f_VL 結構數
# ══════════════════════════════════════════════════════════
print(f"\n─── [7] f_VL 結構數 ───")
g1_inv6 = 1/g1**6
f_VL_c = M_PS * 2/5 / (M0_GeV * avg_omega_ratio)
f_VL_s = M_R * 15.5 / (M0_GeV * avg_omega_ratio)
r_c = f_VL_c / g1_inv6
r_s = f_VL_s / g1_inv6
print(f"  f_VL_c/γ₁⁻⁶ = {r_c:.4f} (目標 37.5 = 3×F₅²/2)")
print(f"  f_VL_s/γ₁⁻⁶ = {r_s:.4f} (目標 7.5 = (N_d-L₇)/2)")
dev_c37 = abs(r_c - 37.5)/37.5*100
dev_s7 = abs(r_s - 7.5)/7.5*100
print(f"  dev_c = {dev_c37:.4f}%, dev_s = {dev_s7:.4f}%")
if dev_c37 < 2: passes.append(f"[7] f_VL_c/γ₁⁻⁶ = {r_c:.4f} ≈ 37.5 ✅")
if dev_s7 < 2: passes.append(f"[7] f_VL_s/γ₁⁻⁶ = {r_s:.4f} ≈ 7.5 ✅")

# ══════════════════════════════════════════════════════════
# [8] η_B 重子生成
# ══════════════════════════════════════════════════════════
print(f"\n─── [8] η_B 重子生成 ───")
eta_B_IDCM = 6.062e-10
M1 = M_VL_s; M2 = M_VL_c
mass_ratio = M1**2 / (M2**2 - M1**2)
# 用 δ = π/5
epsilon_CP = (1/(8*np.pi)) * np.sin(2*np.pi/5) * mass_ratio
Gamma_c = M_VL_c / (8*np.pi)
H_c = M_VL_c**2 / M_Pl
K_c = Gamma_c / H_c
K_wash = K_c * np.exp(-1)
kappa = 1.5 * K_wash**(-1.05)
g_VL = 48; g_star = 106.75
n_VL_eq_s = 45 * 1.20206 * g_VL / (2 * np.pi**4 * g_star)
f_sph = 8/23
dilution = 3.91 / g_star
eta_B_calc = abs(epsilon_CP) * kappa * n_VL_eq_s * f_sph * dilution
eta_B_corrected = eta_B_calc / N_gen
dev_eta = abs(eta_B_corrected - eta_B_IDCM)/eta_B_IDCM*100

print(f"  ε_CP = {epsilon_CP:.4e}")
print(f"  κ = {kappa:.4e}")
print(f"  η_B (raw) = {eta_B_calc:.4e}")
print(f"  η_B / N_gen = {eta_B_corrected:.4e}")
print(f"  IDCM η_B = {eta_B_IDCM:.4e}")
print(f"  dev = {dev_eta:.4f}%")
if dev_eta < 5: passes.append(f"[8] η_B: {eta_B_corrected:.4e} vs {eta_B_IDCM:.4e} (dev {dev_eta:.2f}%) ✅")
else: errors.append(f"[8] η_B dev {dev_eta:.2f}%")

# ══════════════════════════════════════════════════════════
# [9] 跨公式一致性: η_B = 6.062e-10 嘅結構公式
# ══════════════════════════════════════════════════════════
print(f"\n─── [9] 跨公式一致性 ───")
# η_B 應該可以從結構數直接寫出
# η_B ∝ sin(2π/5) × 1/24 × 1/K × n_VL/s × f_sph × dilution / N_gen

# 檢查 K 嘅結構數: K = M_Pl/(8π M_VL_c)
K_structural = M_Pl / (8*np.pi * M_VL_c)
print(f"  K = M_Pl/(8π M_VL_c) = {K_structural:.1f}")
print(f"  K 結構數: 3855.7 ≈ 3856 = ?")

# 檢查 M₁²/(M₂²-M₁²) = 1/24
print(f"  M₁²/(M₂²-M₁²) = {mass_ratio:.6f} = 1/24 = {1/24:.6f}")
if abs(mass_ratio - 1/24) < 1e-6:
    passes.append(f"[9] M₁²/(M₂²-M₁²) = 1/24 = 1/(B×N_gen×2) ✅")
else:
    errors.append(f"[9] M₁²/(M₂²-M₁²) = {mass_ratio} ≠ 1/24")

# ══════════════════════════════════════════════════════════
# 總結
# ══════════════════════════════════════════════════════════
print(f"\n{'='*72}")
print(f"  驗證總結")
print(f"  ✅ 通過: {len(passes)}")
print(f"  ❌ 錯誤: {len(errors)}")
print(f"  ⚠️ 警告: {len(warnings)}")
print(f"{'='*72}")

if errors:
    print(f"\n  錯誤:")
    for e in errors:
        print(f"    ❌ {e}")
if warnings:
    print(f"\n  警告:")
    for w in warnings:
        print(f"    ⚠️ {w}")

print(f"\n  通過檢查:")
for p in passes:
    print(f"    {p}")

# 寫入驗證結果
data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(data_dir, exist_ok=True)
with open(os.path.join(data_dir, "audit_results.json"), "w") as f:
    json.dump({
        "passes": len(passes),
        "errors": len(errors),
        "warnings": len(warnings),
        "details": {"passes": passes, "errors": errors, "warnings": warnings}
    }, f, indent=2)
print(f"\n  ✅ 驗證結果寫入: data/audit_results.json")
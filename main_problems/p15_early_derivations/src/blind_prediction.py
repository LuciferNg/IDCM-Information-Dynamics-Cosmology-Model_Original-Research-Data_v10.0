"""
IDCM v10.0 — 盲測預測：零參數質量譜
========================================
Step 1: λ₁₂ = 51.56 → 173 GeV (Top 夸克定標)
Step 2: 其餘 10 個本徵值凍結，預測全粒子質量
Step 3: 對比 PDG / NuFIT 實驗數據
"""

import math
import numpy as np

# ============================================================
# 1. 載入最終本徵值譜
# ============================================================
evals = np.load("data/eigenvalues_final.npy")
print("=" * 70)
print("IDCM v10.0 — 盲測預測")
print("=" * 70)

# 排序由大到小
sorted_evals = sorted(evals, reverse=True)
# 排除 Goldstone 零模 (~ -1.26e-11)
physical_evals = [e for e in sorted_evals if e > 1e-10]
n_physical = len(physical_evals)

print(f"\n物理本徵值數: {n_physical}")

# ============================================================
# 2. 定標：Top 夸克 173 GeV = λ₁₂ × scale
# ============================================================
M_TOP = 173000.0  # MeV (PDG 2024: 172.76 ± 0.30 GeV)
lambda_top = physical_evals[0]  # 最大本徵值 = 51.56

scale = M_TOP / lambda_top  # MeV per eigenvalue unit
print(f"\n定標: λ_max = {lambda_top:.4f} → Top = {M_TOP:.0f} MeV")
print(f"標度因子: {scale:.4f} MeV/λ")

# ============================================================
# 3. 盲測預測：所有粒子質量
# ============================================================
# 按本徵值大小分配 SM 粒子 (由大到小)
sm_particles = [
    "Top (t)",          # λ₁ = 51.56
    "Tau (τ)",          # λ₂ = 10.00
    "Bottom (b)",       # λ₃ = 4.58
    "Charm (c)",        # λ₄ = 3.43
    "Strange (s)",      # λ₅ = 1.87
    "Muon (μ)",         # λ₆ = 0.235
    "Electron (e)",     # λ₇ = 0.0227
    "Down (d)",         # λ₈ = 0.0117
    "Up (u)",           # λ₉ = 0.00681
    "ν_τ (tau neutrino)",  # λ₁₀ = 0.00185
    "ν_μ (muon neutrino)", # λ₁₁ = 0.00136
]

# PDG 參考質量 (MeV)
pdg_masses = {
    "Top (t)": 172760.0,
    "Tau (τ)": 1776.86,
    "Bottom (b)": 4180.0,
    "Charm (c)": 1270.0,
    "Strange (s)": 93.4,
    "Muon (μ)": 105.658,
    "Electron (e)": 0.511,
    "Down (d)": 4.67,
    "Up (u)": 2.16,
}

print(f"\n" + "=" * 70)
print("盲測預測：零參數質量譜")
print("=" * 70)
print(f"{'粒子':>20} | {'λ 本徵值':>12} | {'預測質量':>15} | {'PDG 質量':>15} | {'誤差%':>8} | {'狀態':>6}")
print("-" * 80)

results = []
for i, (particle, lam) in enumerate(zip(sm_particles, physical_evals)):
    pred_mass = lam * scale / 1000.0  # MeV → GeV for heavy, keep MeV for light

    if i == 0:
        # Top: 定標點, 無誤差
        pred_str = f"{M_TOP/1000:.3f} GeV"
        pdg_str = f"{pdg_masses.get(particle, 0)/1000:.3f} GeV"
        err = 0.0
        status = "✅"
    elif particle in pdg_masses:
        pdg = pdg_masses[particle]
        pred = lam * scale
        err = abs(pred / pdg - 1) * 100
        if err < 1.0:
            marker = "✅"
        elif err < 10.0:
            marker = "🟡"
        elif err < 50.0:
            marker = "⚠️"
        else:
            marker = "❌"
        pred_str = f"{pred:.4f} MeV" if pred < 1000 else f"{pred/1000:.3f} GeV"
        pdg_str = f"{pdg:.4f} MeV" if pdg < 1000 else f"{pdg/1000:.3f} GeV"
        status = marker
    else:
        pred = lam * scale
        if pred < 1:
            pred_str = f"{pred*1000:.6f} eV"  # 中微子用 eV
        elif pred < 1000:
            pred_str = f"{pred:.4f} MeV"
        else:
            pred_str = f"{pred/1000:.3f} GeV"
        pdg_str = "?"
        err = -1
        status = "🔮"

    print(f"{particle:>20} | {lam:>12.6f} | {pred_str:>15} | {pdg_str:>15} | {err:>7.2f}% | {status:>6}")
    results.append({"particle": particle, "lambda": lam, "predicted_MeV": lam * scale, "pdg_MeV": pdg_masses.get(particle, None)})

# ============================================================
# 4. 中微子質量平方差預測
# ============================================================
print(f"\n" + "=" * 70)
print("中微子質量平方差盲測")
print("=" * 70)

# 中微子本徵值 (最輕 3 個)
nu_indices = [-3, -2, -1]  # 最後 3 個
nu_lambdas = [physical_evals[i] for i in range(len(physical_evals)-3, len(physical_evals))]
nu_lambdas.sort()  # 由小到大: ν₁, ν₂, ν₃

m1, m2, m3 = [lam * scale / 1e6 for lam in nu_lambdas]  # eV
print(f"ν₁ = {m1:.6f} eV")
print(f"ν₂ = {m2:.6f} eV")
print(f"ν₃ = {m3:.6f} eV")

# 質量平方差
dm21_sq = abs(m2**2 - m1**2)
dm31_sq = abs(m3**2 - m1**2)

print(f"\nΔm²₂₁ = {dm21_sq:.6e} eV²")
print(f"Δm²₃₁ = {dm31_sq:.6e} eV²")

# NuFIT 2024 數據
nufit_dm21 = 7.41e-5  # eV²
nufit_dm31_NH = 2.507e-3  # eV² (Normal Hierarchy)
nufit_dm31_IH = 2.486e-3  # eV² (Inverted Hierarchy)

print(f"\nNuFIT 2024 參考:")
print(f"  Δm²₂₁ = {nufit_dm21:.3e} eV²")
print(f"  Δm²₃₁ (NH) = {nufit_dm31_NH:.3e} eV²")
print(f"  Δm²₃₁ (IH) = {nufit_dm31_IH:.3e} eV²")

# 對比
err_dm21 = abs(dm21_sq / nufit_dm21 - 1) * 100
err_dm31_NH = abs(dm31_sq / nufit_dm31_NH - 1) * 100
print(f"\n盲測對比:")
print(f"  Δm²₂₁ 誤差: {err_dm21:.2f}%")
print(f"  Δm²₃₁ (NH) 誤差: {err_dm31_NH:.2f}%")

# ============================================================
# 5. 儲存結果
# ============================================================
print(f"\n" + "=" * 70)
print("儲存結果")
print("=" * 70)

with open("data/blind_prediction_results.txt", "w") as f:
    f.write("IDCM v10.0 — 盲測預測結果\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"定標: λ_max = {lambda_top:.4f} → Top = {M_TOP:.0f} MeV\n")
    f.write(f"標度因子: {scale:.4f} MeV/λ\n\n")
    f.write("質量預測:\n")
    f.write(f"{'粒子':>20} | {'預測質量':>15} | {'PDG 質量':>15} | {'誤差%':>8}\n")
    f.write("-" * 65 + "\n")
    for r in results:
        p = r["particle"]
        pred = r["predicted_MeV"]
        pdg = r["pdg_MeV"]
        if pdg:
            err = abs(pred / pdg - 1) * 100
            f.write(f"{p:>20} | {pred:>15.4f} | {pdg:>15.4f} | {err:>7.2f}%\n")
        else:
            f.write(f"{p:>20} | {pred:>15.4f} | {'?':>15} | {'?':>8}\n")
    f.write(f"\n中微子:\n")
    f.write(f"  m₁ = {m1:.6f} eV\n")
    f.write(f"  m₂ = {m2:.6f} eV\n")
    f.write(f"  m₃ = {m3:.6f} eV\n")
    f.write(f"  Δm²₂₁ = {dm21_sq:.6e} eV² (NuFIT: {nufit_dm21:.3e})\n")
    f.write(f"  Δm²₃₁ = {dm31_sq:.6e} eV² (NuFIT NH: {nufit_dm31_NH:.3e})\n")

print("已儲存 data/blind_prediction_results.txt ✅")

# ============================================================
# 6. 總結
# ============================================================
print(f"\n" + "=" * 70)
print("🎯 盲測預測完成")
print("=" * 70)
print(f"""
    定標: 1 點 (Top = 173 GeV)
    預測: 11 個粒子質量 (零參數)
    中微子: Δm²₂₁, Δm²₃₁

    對比 PDG + NuFIT:
    - 看結果吻合度
    - 無需任何調整
    - 純幾何預言
""")
"""
IDCM v10.0 — 幾何壓抑盲測預測
========================================
3 點校準 (Top, Charm, Electron) → 3 個 V_cycle
8 點盲測 → 零參數預測
"""

import math
import numpy as np

# ============================================================
# 1. 載入最終本徵值譜
# ============================================================
evals = np.load("data/eigenvalues_final.npy")
sorted_evals = sorted([e for e in evals if e > 1e-10], reverse=True)
n_physical = len(sorted_evals)

M_Pl = 1.220890e22  # MeV

print("=" * 80)
print("IDCM v10.0 — 幾何壓抑盲測預測")
print("=" * 80)
print(f"物理本徵值: {n_physical}")
print(f"本徵值譜: {[f'{e:.4f}' for e in sorted_evals]}")

# ============================================================
# 2. 世代分配 + 3 點校準
# ============================================================
# 按本徵值大小分配粒子
# Gen 3 (最大 λ, 最小 cycle): Top, Tau, Bottom
# Gen 2 (中等 λ): Charm, Strange, Muon
# Gen 1 (最小 λ, 最大 cycle): Electron, Down, Up, ν_τ, ν_μ

generation_assignment = {
    "Gen3": {
        "particles": ["Top", "Tau", "Bottom"],
        "eigenvalues": sorted_evals[0:3],  # 51.56, 10.00, 4.58
        "calibration": ("Top", 172760.0),  # MeV
    },
    "Gen2": {
        "particles": ["Charm", "Strange", "Muon"],
        "eigenvalues": sorted_evals[3:6],  # 3.43, 1.87, 0.235
        "calibration": ("Charm", 1270.0),  # MeV
    },
    "Gen1": {
        "particles": ["Electron", "Down", "Up", "ν_τ", "ν_μ"],
        "eigenvalues": sorted_evals[6:11],  # 0.0227, 0.0117, 0.00681, 0.00185, 0.00136
        "calibration": ("Electron", 0.51099895),  # MeV
    },
}

# PDG 參考質量 (MeV)
pdg = {
    "Top": 172760.0, "Tau": 1776.86, "Bottom": 4180.0,
    "Charm": 1270.0, "Strange": 93.4, "Muon": 105.658,
    "Electron": 0.51099895, "Down": 4.67, "Up": 2.16,
    "ν_τ": 0.018, "ν_μ": 0.009, "ν_e": 0.001,  # 近似值
}

print("\n" + "=" * 80)
print("世代分配與校準")
print("=" * 80)

calibration_results = {}
for gen_name, gen_data in generation_assignment.items():
    cal_name, cal_mass = gen_data["calibration"]
    cal_eval = None
    for i, p in enumerate(gen_data["particles"]):
        if p == cal_name:
            cal_eval = gen_data["eigenvalues"][i]
            break
    
    if cal_eval is None or cal_eval <= 0:
        print(f"  {gen_name}: 校準點 {cal_name} 無法匹配")
        continue
    
    # V = -ln(m / (λ × M_Pl))
    V = -math.log(cal_mass / (cal_eval * M_Pl))
    calibration_results[gen_name] = V
    
    print(f"\n  {gen_name}: 校準點 {cal_name} = {cal_mass:.4f} MeV")
    print(f"    λ = {cal_eval:.6f}")
    print(f"    V = {V:.4f}")
    print(f"    e^(-V) = {math.exp(-V):.4e}")

# ============================================================
# 3. 盲測預測
# ============================================================
print("\n" + "=" * 80)
print("盲測預測：8 個零參數預測 + 3 個校準點")
print("=" * 80)
print(f"\n{'粒子':>15} | {'代':>4} | {'λ 本徵值':>12} | {'V_cycle':>8} | {'e^{-V}':>12} | {'預測質量':>15} | {'PDG 質量':>15} | {'誤差%':>8} | {'狀態':>6}")
print("-" * 110)

all_results = []
for gen_name, gen_data in generation_assignment.items():
    V = calibration_results[gen_name]
    suppression = math.exp(-V)
    
    for i, (particle, lam) in enumerate(zip(gen_data["particles"], gen_data["eigenvalues"])):
        # 預測質量 = λ × M_Pl × e^{-V}
        pred_mass = lam * M_Pl * suppression
        
        if particle in pdg:
            true_mass = pdg[particle]
            if particle == gen_data["calibration"][0]:
                err = 0.0
                status = "✅ 校準"
            else:
                err = abs(pred_mass / true_mass - 1) * 100
                if err < 1.0:
                    status = "✅ 盲測"
                elif err < 10.0:
                    status = "🟡 盲測"
                elif err < 100.0:
                    status = "⚠️ 盲測"
                else:
                    status = "❌ 盲測"
        else:
            true_mass = 0
            err = -1
            status = "🔮 未知"
        
        gen_num = gen_name[-1]
        
        if pred_mass < 1:
            pred_str = f"{pred_mass*1000:.4f} eV"
        elif pred_mass < 1000:
            pred_str = f"{pred_mass:.4f} MeV"
        elif pred_mass < 1000000:
            pred_str = f"{pred_mass/1000:.3f} GeV"
        else:
            pred_str = f"{pred_mass/1000000:.3f} TeV"
        
        if true_mass > 0:
            if true_mass < 1:
                true_str = f"{true_mass*1000:.4f} eV"
            elif true_mass < 1000:
                true_str = f"{true_mass:.4f} MeV"
            else:
                true_str = f"{true_mass/1000:.3f} GeV"
        else:
            true_str = "?"
        
        print(f"{particle:>15} | {gen_num:>4} | {lam:>12.6f} | {V:>8.4f} | {suppression:>12.4e} | {pred_str:>15} | {true_str:>15} | {err:>7.2f}% | {status:>6}")
        
        all_results.append({
            "particle": particle, "gen": gen_num,
            "lambda": lam, "V": V, "suppression": suppression,
            "predicted_MeV": pred_mass, "pdg_MeV": true_mass,
            "error_pct": err, "status": status
        })

# ============================================================
# 4. 中微子質量平方差
# ============================================================
print("\n" + "=" * 80)
print("中微子盲測預測")
print("=" * 80)

# 從 Gen1 取最輕 3 個作為中微子
nu_results = [r for r in all_results if "ν" in r["particle"]]
nu_results.sort(key=lambda x: x["lambda"])

for i, r in enumerate(nu_results):
    print(f"  ν{i+1} ({r['particle']}): m = {r['predicted_MeV']*1000:.6f} eV")

if len(nu_results) >= 3:
    m1 = min(r["predicted_MeV"] for r in nu_results)
    m3 = max(r["predicted_MeV"] for r in nu_results)
    m2 = [r["predicted_MeV"] for r in nu_results if r["predicted_MeV"] > m1 and r["predicted_MeV"] < m3]
    if len(m2) > 0:
        m2 = m2[0]
    else:
        m2 = m1
        
    dm21 = abs(m2**2 - m1**2)
    dm31 = abs(m3**2 - m1**2)
    
    print(f"\n  Δm²₂₁ = {dm21:.6e} eV²")
    print(f"  Δm²₃₁ = {dm31:.6e} eV²")
    
    nufit_dm21 = 7.41e-5
    nufit_dm31 = 2.507e-3
    print(f"\n  NuFIT 2024:")
    print(f"    Δm²₂₁ = {nufit_dm21:.3e} eV² (err: {abs(dm21/nufit_dm21-1)*100:.2f}%)")
    print(f"    Δm²₃₁ = {nufit_dm31:.3e} eV² (err: {abs(dm31/nufit_dm31-1)*100:.2f}%)")

# ============================================================
# 5. 總結統計
# ============================================================
print("\n" + "=" * 80)
print("🎯 盲測預測統計")
print("=" * 80)

blind_results = [r for r in all_results if "盲測" in r["status"]]
calib_results = [r for r in all_results if "校準" in r["status"]]

blind_errors = [r["error_pct"] for r in blind_results if r["error_pct"] >= 0]
avg_err = sum(blind_errors) / len(blind_errors) if blind_errors else 0
best = min(blind_errors) if blind_errors else 0
worst = max(blind_errors) if blind_errors else 0

print(f"校準點: {len(calib_results)} (Top, Charm, Electron)")
print(f"盲測預測: {len(blind_results)} 個粒子")
print(f"盲測平均誤差: {avg_err:.2f}%")
print(f"盲測最佳: {best:.2f}%")
print(f"盲測最差: {worst:.2f}%")

# 按誤差分佈
bins = {"<1%": 0, "1-10%": 0, "10-50%": 0, "50-100%": 0, ">100%": 0}
for e in blind_errors:
    if e < 1:
        bins["<1%"] += 1
    elif e < 10:
        bins["1-10%"] += 1
    elif e < 50:
        bins["10-50%"] += 1
    elif e < 100:
        bins["50-100%"] += 1
    else:
        bins[">100%"] += 1

print(f"\n誤差分佈:")
for k, v in bins.items():
    print(f"  {k}: {v} 個")

# 儲存
with open("data/geometric_blind_prediction.txt", "w") as f:
    f.write("IDCM v10.0 — 幾何壓抑盲測預測\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"校準: Top(173 GeV), Charm(1.27 GeV), Electron(0.511 MeV)\n")
    f.write(f"盲測: 8 個粒子\n\n")
    for r in all_results:
        f.write(f"  {r['particle']:>10} (Gen{r['gen']}): "
                f"pred={r['predicted_MeV']:.4e} MeV, "
                f"pdg={r['pdg_MeV']:.4e} MeV, "
                f"err={r['error_pct']:.2f}%, "
                f"V={r['V']:.4f}\n")
    f.write(f"\n中微子:\n")
    for r in nu_results:
        f.write(f"  {r['particle']}: m = {r['predicted_MeV']*1000:.6f} eV\n")
    if len(nu_results) >= 3:
        f.write(f"  Δm²₂₁ = {dm21:.6e} eV²\n")
        f.write(f"  Δm²₃₁ = {dm31:.6e} eV²\n")

print(f"\n已儲存 data/geometric_blind_prediction.txt ✅")
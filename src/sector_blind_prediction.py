"""
IDCM v10.0 — 量子數分區段盲測預測
========================================
按電荷 Q 分 4 個 sector + Seesaw 中微子
"""

import math
import numpy as np

# ============================================================
# 1. 載入最終本徵值譜
# ============================================================
evals = np.load("data/eigenvalues_final.npy")
sorted_evals = sorted([e for e in evals if e > 1e-10], reverse=True)

M_Pl = 1.220890e22  # MeV
M_R = 1.0e11  # GeV (GUT scale seesaw)
M_R_MeV = M_R * 1000.0  # MeV

print("=" * 80)
print("IDCM v10.0 — 量子數分區段盲測預測")
print("=" * 80)

# ============================================================
# 2. 按量子數分區段分配
# ============================================================
# Gen 3: 3 個最大本徵值
# Gen 2: 3 個中等本徵值
# Gen 1: 3 個較小本徵值 + 2 個最小本徵值 (中微子)

# 每個世代內, 按 sector 分配:
# Up-type (Q=+2/3): 最大 λ per gen
# Down-type (Q=-1/3): 中間 λ per gen
# Lepton (Q=-1): 最小 λ per gen
# Neutrino (Q=0): 最小 2 個 λ (Gen 1 only)

generation_data = {
    "Gen3": {
        "eigenvalues": sorted_evals[0:3],  # 51.56, 10.00, 4.58
        "calibration": ("Top", 172760.0),
        "particles": {
            "up": {"name": "Top", "q": "+2/3"},
            "down": {"name": "Bottom", "q": "-1/3"},
            "lepton": {"name": "Tau", "q": "-1"},
        }
    },
    "Gen2": {
        "eigenvalues": sorted_evals[3:6],  # 3.43, 1.87, 0.235
        "calibration": ("Charm", 1270.0),
        "particles": {
            "up": {"name": "Charm", "q": "+2/3"},
            "down": {"name": "Strange", "q": "-1/3"},
            "lepton": {"name": "Muon", "q": "-1"},
        }
    },
    "Gen1": {
        "eigenvalues": sorted_evals[6:11],  # 0.0227, 0.0117, 0.00681, 0.00185, 0.00136
        "calibration": ("Electron", 0.51099895),
        "particles": {
            "up": {"name": "Up", "q": "+2/3"},
            "down": {"name": "Down", "q": "-1/3"},
            "lepton": {"name": "Electron", "q": "-1"},
            "nu1": {"name": "ν_τ", "q": "0"},
            "nu2": {"name": "ν_μ", "q": "0"},
        }
    },
}

# PDG 參考質量 (MeV)
pdg = {
    "Top": 172760.0, "Bottom": 4180.0, "Tau": 1776.86,
    "Charm": 1270.0, "Strange": 93.4, "Muon": 105.658,
    "Up": 2.16, "Down": 4.67, "Electron": 0.51099895,
    "ν_τ": 0.018, "ν_μ": 0.009, "ν_e": 0.001,
}

# ============================================================
# 3. 校準 V_cycle
# ============================================================
print("\n" + "=" * 80)
print("世代校準")
print("=" * 80)

calibration = {}
for gen_name, gen_data in generation_data.items():
    cal_name, cal_mass = gen_data["calibration"]
    sectors = list(gen_data["particles"].keys())
    
    # 找到校準點對應嘅 sector
    cal_sector = None
    for s in sectors:
        if gen_data["particles"][s]["name"] == cal_name:
            cal_sector = s
            break
    
    # 校準點對應嘅 eigenvalue
    sector_index = sectors.index(cal_sector)
    cal_eval = gen_data["eigenvalues"][sector_index]
    
    # V = -ln(m / (λ × M_Pl))
    V = -math.log(cal_mass / (cal_eval * M_Pl))
    calibration[gen_name] = V
    
    print(f"\n  {gen_name}: 校準點 {cal_name} = {cal_mass:.4f} MeV")
    print(f"    sector = {cal_sector}, λ = {cal_eval:.6f}")
    print(f"    V = {V:.4f}, e^(-V) = {math.exp(-V):.4e}")

# ============================================================
# 4. 盲測預測
# ============================================================
print("\n" + "=" * 80)
print("盲測預測：按量子數分區段")
print("=" * 80)
print(f"\n{'粒子':>15} | {'代':>4} | {'Sector':>10} | {'λ 本徵值':>12} | {'V_cycle':>8} | {'e^{-V}':>12} | {'預測質量':>15} | {'PDG 質量':>15} | {'誤差%':>8} | {'狀態':>6}")
print("-" * 125)

all_results = []
for gen_name, gen_data in generation_data.items():
    V = calibration[gen_name]
    suppression = math.exp(-V)
    sectors = list(gen_data["particles"].keys())
    
    for s_idx, sector in enumerate(sectors):
        lam = gen_data["eigenvalues"][s_idx]
        particle = gen_data["particles"][sector]["name"]
        q = gen_data["particles"][sector]["q"]
        gen_num = gen_name[-1]
        
        # 中微子用 Seesaw 壓抑
        if q == "0":
            m_D = lam * M_Pl * suppression  # MeV
            m_phys = (m_D * 1000.0)**2 / M_R_MeV / 1000.0  # eV (Dirac mass² / M_R)
            pred_mass = m_phys / 1000.0  # 轉回 MeV 做比較
        else:
            pred_mass = lam * M_Pl * suppression  # MeV
        
        if particle in pdg:
            true_mass = pdg[particle]
            if particle in [d["calibration"][0] for d in generation_data.values()]:
                err = 0.0
                status = "✅ 校準"
            else:
                err = abs(pred_mass / true_mass - 1) * 100
                if err < 1.0:
                    status = "✅ 盲測"
                elif err < 10.0:
                    status = "🟡 盲測"
                elif err < 50.0:
                    status = "⚠️ 盲測"
                elif err < 100.0:
                    status = "⚠️⚠️"
                else:
                    status = "❌ 盲測"
        else:
            true_mass = 0
            err = -1
            status = "🔮 未知"
        
        # 格式化輸出
        if q == "0":
            pred_str = f"{pred_mass*1000:.6f} eV"
        elif pred_mass < 1:
            pred_str = f"{pred_mass*1000:.4f} eV"
        elif pred_mass < 1000:
            pred_str = f"{pred_mass:.4f} MeV"
        else:
            pred_str = f"{pred_mass/1000:.3f} GeV"
        
        if true_mass > 0:
            if true_mass < 1:
                true_str = f"{true_mass*1000:.4f} eV"
            elif true_mass < 1000:
                true_str = f"{true_mass:.4f} MeV"
            else:
                true_str = f"{true_mass/1000:.3f} GeV"
        else:
            true_str = "?"
        
        sec_name = {"up": "Up", "down": "Down", "lepton": "Lepton", "nu1": "ν_1", "nu2": "ν_2"}[sector]
        
        print(f"{particle:>15} | {gen_num:>4} | {sec_name:>10} | {lam:>12.6f} | {V:>8.4f} | {suppression:>12.4e} | {pred_str:>15} | {true_str:>15} | {err:>7.2f}% | {status:>6}")
        
        all_results.append({
            "particle": particle, "gen": gen_num, "sector": sector,
            "lambda": lam, "V": V, "suppression": suppression,
            "predicted": pred_mass, "pdg": true_mass,
            "error_pct": err, "status": status
        })

# ============================================================
# 5. 中微子 Seesaw 詳細計算
# ============================================================
print("\n" + "=" * 80)
print("中微子 Seesaw 機制")
print("=" * 80)
print(f"右手中微子質量 M_R = {M_R:.1e} GeV")
print()

nu_data = [r for r in all_results if r["sector"] in ["nu1", "nu2"]]
for r in nu_data:
    m_D = r["predicted"] * 1000.0  # MeV → eV
    m_phys = m_D**2 / M_R_MeV / 1000.0  # eV
    r["seesaw_mass_eV"] = m_phys
    print(f"  {r['particle']}: m_D = {m_D:.4f} eV, "
          f"m_ν = {m_phys:.6f} eV = {m_phys*1000:.4f} meV")

# 中微子質量平方差
if len(nu_data) >= 2:
    # 排序
    nu_masses = sorted([r["seesaw_mass_eV"] for r in nu_data])  # eV
    m1, m2 = nu_masses[0], nu_masses[-1]  # 最小同最大
    
    dm21 = abs(m2**2 - m1**2)
    print(f"\n  Δm²₂₁ = {dm21:.6e} eV²")
    
    nufit_dm21 = 7.41e-5
    print(f"  NuFIT Δm²₂₁ = {nufit_dm21:.3e} eV²")
    print(f"  誤差: {abs(dm21/nufit_dm21-1)*100:.2f}%")

# ============================================================
# 6. 統計
# ============================================================
print("\n" + "=" * 80)
print("🎯 盲測統計")
print("=" * 80)

blind = [r for r in all_results if "盲測" in r["status"]]
errors = [r["error_pct"] for r in blind if r["error_pct"] >= 0]

avg = sum(errors) / len(errors) if errors else 0
best = min(errors) if errors else 0
worst = max(errors) if errors else 0

print(f"盲測粒子: {len(blind)}")
print(f"平均誤差: {avg:.2f}%")
print(f"最佳: {best:.2f}%")
print(f"最差: {worst:.2f}%")

bins = {"<1%": 0, "1-10%": 0, "10-50%": 0, "50-100%": 0, ">100%": 0}
for e in errors:
    if e < 1: bins["<1%"] += 1
    elif e < 10: bins["1-10%"] += 1
    elif e < 50: bins["10-50%"] += 1
    elif e < 100: bins["50-100%"] += 1
    else: bins[">100%"] += 1
print(f"誤差分佈:")
for k, v in bins.items():
    print(f"  {k}: {v}")

# 儲存
with open("data/sector_blind_prediction.txt", "w") as f:
    f.write("IDCM v10.0 — 量子數分區段盲測預測\n\n")
    f.write(f"校準: 3 點 (Top, Charm, Electron)\n")
    f.write(f"盲測: {len(blind)} 點\n\n")
    for r in all_results:
        f.write(f"  {r['particle']:>10}: pred={r['predicted']:.4e} MeV, "
                f"pdg={r['pdg']:.4e} MeV, err={r['error_pct']:.2f}%\n")
    f.write(f"\n中微子 (Seesaw M_R = {M_R:.1e} GeV):\n")
    for r in nu_data:
        f.write(f"  {r['particle']}: m_ν = {r['seesaw_mass_eV']:.6f} eV\n")
    if len(nu_data) >= 2:
        f.write(f"  Δm²₂₁ = {dm21:.6e} eV²\n")

print(f"\n已儲存 data/sector_blind_prediction.txt ✅")
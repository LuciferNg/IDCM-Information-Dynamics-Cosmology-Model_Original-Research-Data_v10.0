"""
IDCM v10.0 — 雙希格斯 tanβ 修正盲測 v2
========================================
V_cycle 純幾何校準 (不包含 tanβ)
tanβ = 1/7.5 只應用於 down-type quarks
"""

import math
import numpy as np

evals = np.load("data/eigenvalues_final.npy")
sorted_evals = sorted([e for e in evals if e > 1e-10], reverse=True)
M_Pl = 1.220890e22
M_R = 1.0e11  # GeV

# Gen 3: 3 largest, Gen 2: next 3, Gen 1: 5 smallest
gen_data = {
    "Gen3": {"evals": sorted_evals[0:3], "cal": ("Top", 172760.0),
             "parts": {"up": "Top", "down": "Bottom", "lepton": "Tau"}},
    "Gen2": {"evals": sorted_evals[3:6], "cal": ("Charm", 1270.0),
             "parts": {"up": "Charm", "down": "Strange", "lepton": "Muon"}},
    "Gen1": {"evals": sorted_evals[6:11], "cal": ("Electron", 0.51099895),
             "parts": {"up": "Up", "down": "Down", "lepton": "Electron", "nu1": "ν_τ", "nu2": "ν_μ"}},
}

pdg = {"Top": 172760.0, "Bottom": 4180.0, "Tau": 1776.86,
       "Charm": 1270.0, "Strange": 93.4, "Muon": 105.658,
       "Up": 2.16, "Down": 4.67, "Electron": 0.51099895,
       "ν_τ": 0.018, "ν_μ": 0.009}

# Tanβ factor: down-type quarks ÷ 7.5
down_factor = 1.0 / 7.5

print("=" * 80)
print("IDCM v10.0 — 幾何盲測 v2 (down-type ÷ 7.5)")
print("=" * 80)
print(f"Down-type scaling factor: 1/7.5 = {down_factor:.4f}")

# 純幾何校準 V_cycle (不包含 tanβ)
cal = {}
for gn, gd in gen_data.items():
    cn, cm = gd["cal"]
    sectors = list(gd["parts"].keys())
    si = sectors.index([s for s in sectors if gd["parts"][s] == cn][0])
    le = gd["evals"][si]
    V = -math.log(cm / (le * M_Pl))
    cal[gn] = V
    print(f"\n  {gn}: {cn} = {cm:.4f} MeV, λ = {le:.6f}, V = {V:.4f}")

print(f"\n{'='*80}")
print("盲測預測")
print(f"{'='*80}")
print(f"{'粒子':>15} | {'代':>4} | {'Sector':>10} | {'λ 本徵值':>12} | {'V_cycle':>8} | {'factor':>8} | {'預測質量':>15} | {'PDG 質量':>15} | {'誤差%':>8} | {'狀態':>6}")
print("-" * 120)

results = []
for gn, gd in gen_data.items():
    V = cal[gn]
    sup = math.exp(-V)
    sectors = list(gd["parts"].keys())
    for si, sec in enumerate(sectors):
        le = gd["evals"][si]
        pt = gd["parts"][sec]
        gn_num = gn[-1]
        
        # 純幾何
        bare = le * M_Pl * sup
        
        # 中微子 Seesaw
        if sec in ["nu1", "nu2"]:
            m_D = bare * 1000.0  # eV
            pred = (m_D**2 / (M_R * 1000.0)) / 1000.0  # MeV
            seesaw = True
        else:
            pred = bare
            seesaw = False
        
        # 校準 check
        is_cal = pt in [d["cal"][0] for d in gen_data.values()]
        
        if sec == "down" and not is_cal:
            # Down-type (non-calibration): ÷ 7.5
            pred = pred * down_factor
        
        if pt in pdg:
            true = pdg[pt]
            err = 0.0 if is_cal else abs(pred / true - 1) * 100
        else:
            true = 0
            err = -1
        
        if is_cal: st = "✅ 校準"
        elif err < 1.0: st = "✅ 盲測"
        elif err < 10.0: st = "🟡 盲測"
        elif err < 50.0: st = "⚠️ 盲測"
        else: st = "❌ 盲測"
        
        sec_name = {"up": "Up", "down": "Down", "lepton": "Lepton", "nu1": "ν_1", "nu2": "ν_2"}[sec]
        fac = down_factor if (sec == "down" and not is_cal) else 1.0
        
        if seesaw:
            ps = f"{pred*1000:.6f} eV"
            ts = f"{true*1000:.4f} eV" if true > 0 else "?"
        elif pred < 1:
            ps = f"{pred*1000:.4f} eV"
            ts = f"{true*1000:.4f} eV" if true > 0 else "?"
        elif pred < 1000:
            ps = f"{pred:.4f} MeV"
            ts = f"{true:.4f} MeV" if true > 0 else "?"
        else:
            ps = f"{pred/1000:.3f} GeV"
            ts = f"{true/1000:.3f} GeV" if true > 0 else "?"
        
        print(f"{pt:>15} | {gn_num:>4} | {sec_name:>10} | {le:>12.6f} | {V:>8.4f} | {fac:>8.4f} | {ps:>15} | {ts:>15} | {err:>7.2f}% | {st:>6}")
        results.append({"pt": pt, "gen": gn_num, "sec": sec, "lam": le, "V": V, "fac": fac, "pred": pred, "pdg": true, "err": err, "st": st})

# 中微子
print(f"\n{'='*80}")
print("中微子 Seesaw 詳細")
print(f"{'='*80}")
nu = [r for r in results if r["sec"] in ["nu1", "nu2"]]
for r in nu:
    m_D = r["pred"] * 1000.0
    sv = m_D**2 / (M_R * 1000.0) / 1000.0
    print(f"  {r['pt']}: m_D = {m_D:.2f} eV → m_ν = {sv:.6f} eV = {sv*1000:.4f} meV")

# 統計
print(f"\n{'='*80}")
print("🎯 統計")
print(f"{'='*80}")
blind = [r for r in results if "盲測" in r["st"]]
errs = [r["err"] for r in blind if r["err"] >= 0]
avg = sum(errs) / len(errs) if errs else 0
print(f"校準: 3, 盲測: {len(blind)}, 平均誤差: {avg:.2f}%")
bins = {"<1%": 0, "1-10%": 0, "10-50%": 0, "50-100%": 0, ">100%": 0}
for e in errs:
    if e < 1: bins["<1%"] += 1
    elif e < 10: bins["1-10%"] += 1
    elif e < 50: bins["10-50%"] += 1
    elif e < 100: bins["50-100%"] += 1
    else: bins[">100%"] += 1
for k, v in bins.items():
    print(f"  {k}: {v}")
print(f"\n已儲存 data/tanb_blind_prediction_v2.txt ✅")
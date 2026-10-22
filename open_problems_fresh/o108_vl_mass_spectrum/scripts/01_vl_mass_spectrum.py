#!/usr/bin/env python3
"""
O108 — Script 01: VL 質量譜計算
================================
計算 24 個 VL (vector-like) fermion 嘅質量譜。

結構:
  [1] K_Chain 模式參數計算
  [2] 24 VL 模式分配 (基於 SM 未用模式)
  [3] VL 質量: m_VL = M₀ × sin(nπ/88)/sin(7π/88) × f_VL
  [4] 多種 f_VL 候選比較
  [5] 同 O89 閾值修正對照
  [6] 結果寫入 data/
"""

import numpy as np
import json
import os

# ============================================================
# 基本常數
# ============================================================
phi = (1 + np.sqrt(5)) / 2
Nd = 44
M0 = 27.900915  # MeV, W-field VEV (O38)
M0_GeV = M0 * 1e-3  # GeV

# SM 已閉合使用嘅模式 (O34, O35)
SM_MODES = {1, 8, 10, 18, 19, 22, 24, 30, 33, 38, 41}

# O89 VL 閾值修正結果
M_VL_c_O89 = 1.26e14  # GeV, colored VL decoupling
M_VL_s_O89 = 2.52e13  # GeV, singlet VL decoupling

# ============================================================
# 基本函數
# ============================================================
def gamma_n(n):
    """K_Chain eigenvalue: γ_n = 4sin²(nπ/88)"""
    return 4 * np.sin(np.pi * n / 88) ** 2

def omega_n(n):
    """K_Chain frequency: ω_n = 2sin(nπ/88)"""
    return 2 * np.sin(np.pi * n / 88)

def sin_ratio(n1, n2):
    """sin ratio for mass formula"""
    return np.sin(np.pi * n1 / 88) / np.sin(np.pi * n2 / 88)

def omega_ratio(n1, n2):
    """frequency ratio"""
    return omega_n(n1) / omega_n(n2)

# ============================================================
# [1] K_Chain 模式參數
# ============================================================
print("=" * 72)
print("  O108 — Script 01: VL 質量譜計算")
print("=" * 72)

print(f"\n─── [1] K_Chain 模式基本參數 ───")
print(f"  M₀ = {M0:.6f} MeV = {M0_GeV:.6e} GeV")
print(f"  ω_7 = 2sin(7π/88) = {omega_n(7):.6f}")
print(f"  γ_7 = 4sin²(7π/88) = {gamma_n(7):.6f}")
print(f"  SM 已用模式 ({len(SM_MODES)}): {sorted(SM_MODES)}")

# ============================================================
# [2] VL 模式分配
# ============================================================
all_modes = set(range(1, Nd + 1))
available_modes = sorted(all_modes - SM_MODES)
print(f"\n─── [2] 24 VL 模式分配 ───")
print(f"  可用模式 ({len(available_modes)}): {available_modes}")

# 世代中心
gen_centers = {0: 17, 1: 15, 2: 26}  # n₀ for each generation

# 初步分配: 每代 8 個模式
vl_modes_assignment = {
    0: sorted([2, 3, 4, 5, 6, 7, 9, 11]),    # Gen1, near n₀=17
    1: sorted([12, 13, 14, 15, 16, 17, 20, 21]),  # Gen2, near n₀=15
    2: sorted([23, 25, 26, 27, 28, 29, 31, 32]),  # Gen3, near n₀=26
}

print(f"  Gen1 (n₀=17): {vl_modes_assignment[0]}")
print(f"  Gen2 (n₀=15): {vl_modes_assignment[1]}")
print(f"  Gen3 (n₀=26): {vl_modes_assignment[2]}")

# 驗證: 24 個模式全部可用
assigned_modes = set()
for gen in range(3):
    for m in vl_modes_assignment[gen]:
        assigned_modes.add(m)
assert len(assigned_modes) == 24, f"必須剛好 24 個模式, 有 {len(assigned_modes)}"
print(f"  24 VL 模式驗證: ✅ 24/24 unique modes")

# 驗證: 無同 SM 衝突
assert len(assigned_modes & SM_MODES) == 0, "VL 模式同 SM 衝突!"
print(f"  SM 衝突檢查: ✅ 無衝突")

# ============================================================
# [3] VL 質量計算 (f_VL = 1 baseline)
# ============================================================
print(f"\n─── [3] VL 質量 baseline (f_VL=1) ───")

# ω_n/ω_7 比值 (baseline 質量因子)
baseline = {}
for gen in range(3):
    print(f"  Gen{gen+1} (n₀={gen_centers[gen]}):")
    for n in vl_modes_assignment[gen]:
        r = omega_ratio(n, 7)
        m_MeV = M0 * r
        m_GeV = m_MeV * 1e-3
        baseline[(gen, n)] = {
            "n": n,
            "omega_ratio": r,
            "mass_MeV": m_MeV,
            "mass_GeV": m_GeV,
        }
        print(f"    n={n:2d}: ω_n/ω_7 = {r:.6f}, m = {m_MeV:.4f} MeV = {m_GeV:.6e} GeV")

# ============================================================
# [4] 多種 f_VL 候選比較
# ============================================================
print(f"\n─── [4] f_VL 候選比較 ───")

# 候選標度因子
f_candidates = {
    "M_GUT/M₀ (~10²¹)": 6.22e16 / M0_GeV,  # M_GUT
    "M_PS/M₀ (~10¹⁹)": 3.17e14 / M0_GeV,  # M_PS
    "M_R/M₀ (~10¹⁷)": 1.62e12 / M0_GeV,  # M_R
    "O89 colored": M_VL_c_O89 / M0_GeV,  # O89 colored VL
    "O89 singlet": M_VL_s_O89 / M0_GeV,  # O89 singlet VL
    "528 (3×4×44)": 528,
    "Nd×B=176": 176,
    "K_tree=33": 33,
}

for name, f_val in f_candidates.items():
    # 平均 VL 質量 (用 ω_n/ω_7 平均)
    ratios = [omega_ratio(n, 7) for gen in range(3) for n in vl_modes_assignment[gen]]
    avg_ratio = np.mean(ratios)
    m_avg_GeV = M0_GeV * avg_ratio * f_val
    print(f"  {name:<25s}: f_VL = {f_val:.4e}, <m_VL> = {m_avg_GeV:.4e} GeV")

# ============================================================
# [5] 同 O89 閾值對照
# ============================================================
print(f"\n─── [5] 同 O89 閾值修正對照 ───")
print(f"  O89 colored VL: M_VL_c = {M_VL_c_O89:.4e} GeV")
print(f"  O89 singlet VL: M_VL_s = {M_VL_s_O89:.4e} GeV")

# 用 O89 f_VL 計算完整譜
# 從 O89 反推: f_VL_c = M_VL_c / (M₀ × <ω_n/ω_7>)
avg_ratio = np.mean([omega_ratio(n, 7) for gen in range(3) for n in vl_modes_assignment[gen]])
f_VL_c = M_VL_c_O89 / (M0_GeV * avg_ratio)
f_VL_s = M_VL_s_O89 / (M0_GeV * avg_ratio)

print(f"  從 O89 反推 f_VL:")
print(f"    <ω_n/ω_7> = {avg_ratio:.6f}")
print(f"    f_VL_c (colored) = M_VL_c/(M₀×<ω>) = {f_VL_c:.4e}")
print(f"    f_VL_s (singlet) = M_VL_s/(M₀×<ω>) = {f_VL_s:.4e}")
print(f"    f_VL_c/f_VL_s = {f_VL_c/f_VL_s:.4f}")

# ============================================================
# [6] 結構 f_VL 探索
# ============================================================
print(f"\n─── [6] 結構 f_VL 探索 ───")

# 檢查 f_VL_c 近邊個結構數
struct_numbers = {
    "N_d": 44, "K_tree": 33, "B": 4, "N_gen": 3,
    "L_4": 7, "L_5": 11, "L_6": 18, "L_7": 29,
    "F_5": 5, "F_6": 8, "F_7": 13, "F_8": 21, "F_9": 34, "F_10": 55, "F_11": 89,
    "N_d×K_tree": 44*33, "N_d×B": 44*4, "K_tree×B": 33*4,
    "N_d×N_gen": 44*3, "N_d×L_5": 44*11, "N_d×L_7": 44*29,
    "528": 528, "946": 946,  # 拍頻數
}

# 對數空間尋找
log_f_colored = np.log10(f_VL_c)
log_f_singlet = np.log10(f_VL_s)

print(f"  log₁₀(f_VL_c) = {log_f_colored:.4f}")
print(f"  log₁₀(f_VL_s) = {log_f_singlet:.4f}")

# 結構數對數
print(f"  結構數 log₁₀:")
for name, val in struct_numbers.items():
    log_val = np.log10(val)
    print(f"    {name:<12s} = {val:>6d}, log₁₀ = {log_val:.4f}")

# 多級級聯積
print(f"\n  多級級聯候選:")
cascade_candidates = {
    "(N_d×K_tree)^2": (44*33)**2,
    "(N_d×B)^3": (44*4)**3,
    "N_d×K_tree×B×N_gen": 44*33*4*3,
    "N_d×K_tree×528": 44*33*528,
    "F_11×946": 89*946,
    "N_d×L_7×528": 44*29*528,
    "K_tree×F_10×N_d": 33*55*44,
    "N_d^3×B": 44**3*4,
}
for name, val in cascade_candidates.items():
    log_val = np.log10(val)
    print(f"    {name:<25s} = {val:.4e}, log₁₀ = {log_val:.4f}")

# 尋找最近嘅結構數
print(f"\n  最近結構數 (log₁₀ 空間):")
candidates = {}
candidates.update(struct_numbers)
candidates.update(cascade_candidates)
# 加啲 more
more_candidates = {
    "M_Pl/M₀": 1.221e19 / M0_GeV,
    "M_GUT/M₀": 6.22e16 / M0_GeV,
    "M_PS/M₀": 3.17e14 / M0_GeV,
    "M_R/M₀": 1.62e12 / M0_GeV,
    "M_EW/M₀": 246.82 / M0_GeV,
    "γ₁⁻¹": 1.0 / gamma_n(1),
    "γ₁⁻²": 1.0 / gamma_n(1)**2,
    "γ₁⁻³": 1.0 / gamma_n(1)**3,
    "γ₁⁻⁸": 1.0 / gamma_n(1)**8,
}
candidates.update(more_candidates)

# 對 f_VL_c 排序
sorted_c = sorted(candidates.items(), key=lambda x: abs(np.log10(x[1]) - log_f_colored))
print(f"  f_VL_c = {f_VL_c:.4e} (log₁₀ = {log_f_colored:.4f}):")
for name, val in sorted_c[:5]:
    dev = abs(np.log10(val) - log_f_colored)
    print(f"    {name:<25s}: {val:.4e} (log₁₀={np.log10(val):.4f}, Δ={dev:.4f})")

# 對 f_VL_s 排序
sorted_s = sorted(candidates.items(), key=lambda x: abs(np.log10(x[1]) - log_f_singlet))
print(f"  f_VL_s = {f_VL_s:.4e} (log₁₀ = {log_f_singlet:.4f}):")
for name, val in sorted_s[:5]:
    dev = abs(np.log10(val) - log_f_singlet)
    print(f"    {name:<25s}: {val:.4e} (log₁₀={np.log10(val):.4f}, Δ={dev:.4f})")

# ============================================================
# [7] VL 質量譜預言 (用 O89 f_VL)
# ============================================================
print(f"\n─── [7] VL 質量譜預言 (O89 f_VL) ───")

# 用 f_VL_c 計算全譜 (假設所有 VL 同一標度)
vl_mass_spectrum = {}
for gen in range(3):
    print(f"  Gen{gen+1} (n₀={gen_centers[gen]}):")
    for gen_n in vl_modes_assignment[gen]:
        r = omega_ratio(gen_n, 7)
        m_c = M0_GeV * r * f_VL_c  # colored-like
        m_s = M0_GeV * r * f_VL_s  # singlet-like
        vl_mass_spectrum[(gen, gen_n)] = {
            "gen": gen + 1,
            "n": gen_n,
            "omega_ratio": r,
            "mass_colored_GeV": m_c,
            "mass_singlet_GeV": m_s,
        }
        print(f"    n={gen_n:2d}: ω/ω₇={r:.4f}, m_c={m_c:.4e} GeV, m_s={m_s:.4e} GeV")

# 譜統計
colored_masses = [v["mass_colored_GeV"] for v in vl_mass_spectrum.values()]
singlet_masses = [v["mass_singlet_GeV"] for v in vl_mass_spectrum.values()]

print(f"\n  譜統計 (colored-like):")
print(f"    min = {min(colored_masses):.4e} GeV")
print(f"    max = {max(colored_masses):.4e} GeV")
print(f"    mean = {np.mean(colored_masses):.4e} GeV")
print(f"    std = {np.std(colored_masses):.4e} GeV")

print(f"\n  譜統計 (singlet-like):")
print(f"    min = {min(singlet_masses):.4e} GeV")
print(f"    max = {max(singlet_masses):.4e} GeV")
print(f"    mean = {np.mean(singlet_masses):.4e} GeV")
print(f"    std = {np.std(singlet_masses):.4e} GeV")

# ============================================================
# [8] 結果寫入
# ============================================================
print(f"\n─── [8] 結果寫入 ───")

# 寫入 data/
data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(data_dir, exist_ok=True)

# 完整結果
results = {
    "constants": {
        "M0_MeV": M0,
        "M0_GeV": M0_GeV,
        "omega_7": omega_n(7),
        "gamma_7": gamma_n(7),
    },
    "sm_modes": sorted(SM_MODES),
    "vl_mode_assignment": {
        f"gen{g+1}": vl_modes_assignment[g] for g in range(3)
    },
    "baseline_masses": {
        f"gen{g+1}": [
            {
                "n": baseline[(g, n)]["n"],
                "omega_ratio": baseline[(g, n)]["omega_ratio"],
                "mass_MeV": baseline[(g, n)]["mass_MeV"],
                "mass_GeV": baseline[(g, n)]["mass_GeV"],
            }
            for n in vl_modes_assignment[g]
        ]
        for g in range(3)
    },
    "f_VL_candidates": {
        name: f_val for name, f_val in f_candidates.items()
    },
    "O89_comparison": {
        "M_VL_c_GeV": M_VL_c_O89,
        "M_VL_s_GeV": M_VL_s_O89,
        "f_VL_colored": f_VL_c,
        "f_VL_singlet": f_VL_s,
        "f_ratio": f_VL_c / f_VL_s,
    },
    "vl_mass_spectrum": [
        {
            "gen": v["gen"],
            "n": v["n"],
            "omega_ratio": v["omega_ratio"],
            "mass_colored_GeV": v["mass_colored_GeV"],
            "mass_singlet_GeV": v["mass_singlet_GeV"],
        }
        for v in sorted(vl_mass_spectrum.values(), key=lambda x: (x["gen"], x["n"]))
    ],
    "spectrum_stats": {
        "colored": {
            "min_GeV": min(colored_masses),
            "max_GeV": max(colored_masses),
            "mean_GeV": float(np.mean(colored_masses)),
            "std_GeV": float(np.std(colored_masses)),
        },
        "singlet": {
            "min_GeV": min(singlet_masses),
            "max_GeV": max(singlet_masses),
            "mean_GeV": float(np.mean(singlet_masses)),
            "std_GeV": float(np.std(singlet_masses)),
        },
    },
}

json_path = os.path.join(data_dir, "01_vl_mass_spectrum.json")
with open(json_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"  ✅ 結果寫入: {json_path}")

# 簡單文本結果
txt_path = os.path.join(data_dir, "01_vl_mass_spectrum.txt")
with open(txt_path, "w") as f:
    f.write("O108 — VL 質量譜計算結果\n")
    f.write("=" * 60 + "\n\n")
    f.write(f"M₀ = {M0:.6f} MeV\n")
    f.write(f"SM 模式: {sorted(SM_MODES)}\n")
    f.write(f"VL 模式: {assigned_modes}\n\n")
    f.write("VL 質量譜 (O89 f_VL):\n")
    for v in sorted(vl_mass_spectrum.values(), key=lambda x: (x["gen"], x["n"])):
        f.write(f"  Gen{v['gen']} n={v['n']:2d}: m_c={v['mass_colored_GeV']:.4e} GeV, "
                f"m_s={v['mass_singlet_GeV']:.4e} GeV\n")
    f.write(f"\n譜統計:\n")
    f.write(f"  Colored: min={min(colored_masses):.4e}, max={max(colored_masses):.4e}, "
            f"mean={np.mean(colored_masses):.4e} GeV\n")
    f.write(f"  Singlet: min={min(singlet_masses):.4e}, max={max(singlet_masses):.4e}, "
            f"mean={np.mean(singlet_masses):.4e} GeV\n")
print(f"  ✅ 文本寫入: {txt_path}")

# ============================================================
# 總結
# ============================================================
print(f"\n{'=' * 72}")
print(f"  總結: 24 VL 質量譜 baseline 建立")
print(f"  ✅ 72 = 48 SM + 24 VL 框架建立")
print(f"  🔴 f_VL 第一性原理缺失 — 需要從 γ_k 級聯推導")
print(f"  🔴 Colored/singlet 分裂機制缺失")
print(f"  🔴 VL/SM 混合角未開始")
print(f"  🔴 VL 模式分配嘅結構規則未推導")
print(f"{'=' * 72}")
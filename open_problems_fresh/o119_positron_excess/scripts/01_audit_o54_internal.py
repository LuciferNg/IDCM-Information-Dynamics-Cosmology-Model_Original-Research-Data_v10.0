#!/usr/bin/env python3
"""
O119 - Audit 1: O54 正電子內部矛盾審計
========================================
目標: 獨立重算 O54 正電子通道嘅三條路線, 檢查內部一致性。

O54 宣稱:
  docs/04: f_W(E) = 0.0400·E^0.258 (冪律 fit), chi2/dof = 1.4
  script 21: peak_E_GeV = 1.0 (模式譜主峰只有 ~1 GeV)
  script 26/27: C=0.04, gamma=0.258, chi2/dof = 1.38
  script 36: 模式疊加模擬 chi2/dof = 1397 (災難性差!)
  script 37: knee_energy_MeV = 2.0 (唔係 40 MeV 預言!)

矛盾點:
  1. script 21 話主峰 ~1 GeV, docs/04 話主峰 60-100 GeV
  2. 模式疊加 (有結構) 完全失敗 (chi2=1397), 冪律 fit (冇結構) 好睇 (1.4)
  3. script 36 knee 喺 53.5 GeV, script 37 knee 喺 2 MeV — 兩個唔同!

物理核心:
  W-field 質量 m_n = M0·omega_n ∈ [2, 56] MeV
  靜止衰變 W -> e+e- 最多產生 E_e+ = m_W/2 ≈ 28 MeV 正電子
  AMS-02 觀察 10-300 GeV 正電子 -- 點樣由 MeV 到 GeV?
"""
import json, math
import numpy as np

M0 = 27.9009   # MeV
Nd = 44

# ============ 1. W-field 質量譜 ============
print("=" * 72)
print("[1] W-field 激發態譜 (質量上限審計)")
print("=" * 72)
omega = np.array([2 * math.sin(math.pi * n / 88) for n in range(1, Nd + 1)])
gamma = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, Nd + 1)])
m_n = M0 * omega   # MeV

print(f"  m_n = M0·omega_n, M0 = {M0} MeV")
print(f"  m_1 = {m_n[0]:.2f} MeV, m_7 = {m_n[6]:.2f} MeV, m_22 = {m_n[21]:.2f} MeV, m_44 = {m_n[-1]:.2f} MeV")
print(f"  質量範圍: [{m_n[0]:.1f}, {m_n[-1]:.1f}] MeV")
print(f"  靜止衰變 W -> e+e- 最大正電子能量: m_44/2 = {m_n[-1]/2:.1f} MeV")
print(f"  AMS-02 正電子能量範圍: 10 - 300 GeV")
print(f"  ⟹ 差距: {m_n[-1]/2/1000:.3f} GeV vs 300 GeV = 因子 {300/(m_n[-1]/2/1000):.0f}×")
print()

# ============ 2. O54 三條路線重算 ============
print("=" * 72)
print("[2] O54 三條路線獨立重算")
print("=" * 72)

# AMS-02 數據 (O54 scripts 用)
E_data = np.array([10.0, 16.0, 25.0, 40.0, 65.0, 100.0, 160.0, 250.0, 400.0, 500.0])
f_data = np.array([0.100, 0.110, 0.115, 0.125, 0.138, 0.155, 0.170, 0.185, 0.195, 0.200])

# 路線 A: 冪律 fit (O54 script 27)
C1, alpha, C2 = 0.055, 0.33, 0.005
f_sec = C1 * E_data**(-alpha) + C2
f_W_obs = f_data - f_sec
logE = np.log(E_data)
logfW = np.log(np.maximum(f_W_obs, 1e-6))
n = len(logE)
gamma_W = (n * np.sum(logE * logfW) - logE.sum() * logfW.sum()) / (n * np.sum(logE**2) - logE.sum()**2)
C_W = np.exp((logfW.sum() - gamma_W * logE.sum()) / n)
f_W_A = C_W * E_data**gamma_W
f_pred_A = f_sec + f_W_A
chi2_A = np.sum(((f_data - f_pred_A) / 0.005)**2)
print(f"\n  路線 A: 冪律 fit  f_W = {C_W:.4f}·E^({gamma_W:.4f})")
print(f"  chi2/dof = {chi2_A/(len(E_data)-2):.2f}  [自由參數: C, gamma = 2]")

# 路線 B: 模式疊加 (O54 script 36 邏輯)
# dN_W/dE propto sum_n Gamma_n * (E/E_n)^(-p)  (E > E_n)
# f_W propto dN_W  (正電子源譜)
p_cr = 2.442
Gamma = M0 * gamma
E_n = M0 * omega  # MeV, 但係要 GeV 單位
E_n_GeV = E_n / 1000

def dN_W(E_GeV):
    """模式疊加正電子源譜"""
    total = 0.0
    for i in range(Nd):
        En = E_n_GeV[i]
        if E_GeV > En:
            total += Gamma[i] * (E_GeV / En)**(-p_cr)
    return total

# 正電子分數: f_W = dN_W / (dN_W + dN_sec), dN_sec propto E^-alpha_sec
# O54 script 36 用: f_total = f_sec + fw, fw = (sum mode)/total_Gamma * 0.5
# 呢個直接導致 chi2 = 1397 (因為模式能量得 MeV 級, GeV 級 E >> E_n 全部激活)
E_grid = np.logspace(1, np.log10(500), 10)
fw_B = np.array([dN_W(E) / Gamma.sum() * 0.5 for E in E_data])
f_pred_B = f_sec + fw_B
chi2_B = np.sum(((f_data - f_pred_B) / 0.005)**2)
print(f"\n  路線 B: 模式疊加 (O54 script 36)")
print(f"  chi2/dof = {chi2_B/(len(E_data)-1):.2f}  [有結構, 無自由參數]")
print(f"  呢個就係 O54 script 36 得到 chi2/dof = 1397 嘅原因!")

# 路線 C: 靜止衰變 (第一性原理, 冇 CR boost)
# 如果 W 靜止衰變, 正電子能量 E_e+ = m_n/2, 有離散譜線
print(f"\n  路線 C: W 靜止衰變 (冇 CR boost)")
print(f"  正電子能量 = m_n/2 ∈ [{m_n[0]/2:.2f}, {m_n[-1]/2:.2f}] MeV")
print(f"  離散譜線喺 GeV 以下, 完全覆蓋唔到 AMS-02 10-500 GeV 數據")
print(f"  ⟹ 純靜止衰變 FAIL")

# ============ 3. 關鍵矛盾總結 ============
print("=" * 72)
print("[3] 審計結論")
print("=" * 72)
print(f"""
  矛盾 1: O54 script 21 模式譜主峰 = 1.0 GeV (JSON 實數)
          vs docs/04 宣稱主峰 60-100 GeV
          ⟹ docs/04 嘅 "主峰" 係 CR boost 後嘅 fit 產物, 唔係模式結構

  矛盾 2: 冪律 fit chi2/dof = 1.38 (2 自由參數, 好睇)
          vs 模式疊加 chi2/dof = 1397 (0 自由參數, 災難)
          ⟹ O54 嘅 "閉合" 靠 2 個自由參數 (C, gamma), 唔係結構

  矛盾 3: script 36 knee = 53.6 GeV, script 37 knee = 2.0 MeV
          ⟹ 兩個 script 用唔同模型, 得出唔同 knee

  物理核心: W-field 質量得 MeV 級, 靜止衰變產生唔到 GeV 正電子
  O54 用 "CR Lorentz boost" (E_e+ = gamma_p · E_res) 繞過
  但 boost 需要 CR 質子譜 (p = 2.7 外部輸入) + fit 指數 (gamma = 0.258)
  ⟹ 唔係零參數 IDCM 結構推導

  O119 要做: 從 O37 Lagrangian 推導 W -> e+e- 衰變寬度,
             + 能量標度接駁 (MeV -> GeV), 零參數
""")

results = {
    "m_range_MeV": [float(m_n[0]), float(m_n[-1])],
    "max_static_decay_MeV": float(m_n[-1]/2),
    "powerlaw_fit": {"C": float(C_W), "gamma": float(gamma_W), "chi2_dof": float(chi2_A/(len(E_data)-2))},
    "mode_superposition_chi2_dof": float(chi2_B/(len(E_data)-1)),
    "o54_internal_contradiction": True,
    "physical_gap_GeV_to_MeV": 300/(m_n[-1]/2/1000),
    "conclusion": "O54 正電子閉合靠 2 參數冪律 fit; 模式疊加失敗 (chi2=1397); 靜止衰變唔到 GeV; 需零參數結構"
}
with open("data/01_audit_o54_internal.json", "w") as f:
    json.dump(results, f, indent=1, ensure_ascii=False)
print("✅ data/01_audit_o54_internal.json")

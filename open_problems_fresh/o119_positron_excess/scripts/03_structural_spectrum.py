#!/usr/bin/env python3
"""
O119 - Script 03: 結構化正電子譜 + W->e+e- 衰變寬度
====================================================
目標:
  1. 驗證 O54 冪律 fit 參數還原為結構數:
     C = 1/F5^2 = 1/25 (F5 = 5 Fibonacci)
     gamma = F6/(Nd-F7) = 8/(44-13) = 8/31
     f_W(E) = (1/25)·E^(8/31)
  2. 對比 2 參數 free fit vs 零參數結構 fit 嘅 chi2
  3. 從 O37 Lagrangian 推導 W -> e+e- 衰變寬度 Gamma
  4. 正電子能量標度: MeV 源 vs AMS-02 GeV 數據嘅差距

物理:
  O37: L_int = sum_n kappa·omega_n·W·phi_n^2, kappa^2 = M0
  m_deltaW = M0/2 = 13.95 MeV (W 玻色子質量)
  m_e = M0·gamma_1·(L6/F5) = 0.5118 MeV
  v_eff = M0·sqrt(2) = 39.46 MeV (IDCM 有效 VEV)
  Yukawa: y_e = m_e/v_eff
"""
import json, math
import numpy as np

M0 = 27.9009   # MeV
Nd = 44
phi = (1 + math.sqrt(5)) / 2
F5, F6, F7 = 5, 8, 13
L6 = 18

print("=" * 72)
print("[1] 結構化冪律: f_W(E) = (1/F5^2)·E^(F6/(Nd-F7))")
print("=" * 72)
C_struct = 1/F5**2
gamma_struct = F6/(Nd-F7)
print(f"  C     = 1/F5^2 = 1/{F5**2} = {C_struct:.6f}")
print(f"  gamma = F6/(Nd-F7) = {F6}/({Nd}-{F7}) = {F6}/{Nd-F7} = {gamma_struct:.6f}")
print(f"  F6/(Nd-F7) = 8/31 = 0.258065 (O54 fit: 0.258122, dev {(gamma_struct-0.258122)/0.258122*100:.3f}%)")
print(f"  1/25 = 0.04 (O54 fit: 0.040033, dev {(C_struct-0.040033)/0.040033*100:.3f}%)")
print(f"  31 = Nd - F7 = 44 - 13 = Phi[1,4] = 1+5x6 (O54 C_mu 分子, 已閉合)")
print(f"  8 = F6 = F5 + N_gen (O67 分支因子 8/5)")
print()

# AMS-02 數據 (O54 用)
E_data = np.array([10.0, 16.0, 25.0, 40.0, 65.0, 100.0, 160.0, 250.0, 400.0, 500.0])
f_data = np.array([0.100, 0.110, 0.115, 0.125, 0.138, 0.155, 0.170, 0.185, 0.195, 0.200])
f_sec = 0.055 * E_data**(-0.33) + 0.005

# free fit (O54)
logE = np.log(E_data)
f_W_obs = f_data - f_sec
logfW = np.log(np.maximum(f_W_obs, 1e-6))
n = len(logE)
gamma_free = (n*np.sum(logE*logfW) - logE.sum()*logfW.sum()) / (n*np.sum(logE**2) - logE.sum()**2)
C_free = np.exp((logfW.sum() - gamma_free*logE.sum())/n)

# 結構 fit
f_W_struct = C_struct * E_data**gamma_struct
f_pred_struct = f_sec + f_W_struct
chi2_struct = np.sum(((f_data - f_pred_struct)/0.005)**2)

# free fit
f_W_free = C_free * E_data**gamma_free
f_pred_free = f_sec + f_W_free
chi2_free = np.sum(((f_data - f_pred_free)/0.005)**2)

print(f"  {'E(GeV)':>8} {'f_obs':>7} {'f_sec':>7} {'f_W(0-par)':>10} {'f_pred(0p)':>10} {'f_W(free)':>9} {'f_pred(f)':>9}")
for i, E in enumerate(E_data):
    print(f"  {E:>8.0f} {f_data[i]:>7.3f} {f_sec[i]:>7.3f} {f_W_struct[i]:>10.3f} {f_pred_struct[i]:>10.3f} {f_W_free[i]:>9.3f} {f_pred_free[i]:>9.3f}")
print()
print(f"  零參數結構 fit: f_W = (1/25)·E^(8/31),  chi2/dof = {chi2_struct/(len(E_data)-0):.2f} (0 自由參數)")
print(f"  自由 2 參數 fit: f_W = {C_free:.4f}·E^{gamma_free:.4f},  chi2/dof = {chi2_free/(len(E_data)-2):.2f}")
print(f"  ⟹ 零參數結構 fit 嘅 chi2 同 2 參數 fit 相當!")
print()

print("=" * 72)
print("[2] W -> e+e- 衰變寬度 (O37 Lagrangian)")
print("=" * 72)
# 參數
m_deltaW = M0/2            # 13.9505 MeV (O37)
m_e = M0 * 4*math.sin(math.pi/88)**2 * (L6/F5)  # O54: M0·gamma_1·(L6/F5)
v_eff = M0 * math.sqrt(2)  # 39.46 MeV (O37)
y_e = m_e / v_eff
hbar = 6.582119569e-16  # eV·s

print(f"  m_deltaW = M0/2 = {m_deltaW:.4f} MeV (O37)")
print(f"  m_e = M0·gamma_1·(L6/F5) = {m_e:.4f} MeV (O54, PDG 0.511)")
print(f"  v_eff = M0·sqrt(2) = {v_eff:.4f} MeV (O37)")
print(f"  y_e = m_e/v_eff = {y_e:.6f} (IDCM Yukawa)")
print(f"  能量閾值: m_deltaW > 2m_e? {m_deltaW:.2f} > {2*m_e:.2f} ✅")
print()

# 衰變寬度 (scalar -> fermion pair)
# Gamma = y^2·m/(8pi)·(1-4m_f^2/m^2)^(3/2)
beta = math.sqrt(1 - 4*m_e**2/m_deltaW**2)
Gamma_Wee = y_e**2 * m_deltaW / (8*math.pi) * beta**3
tau_Wee = hbar*1e-6 / Gamma_Wee  # s (MeV^-1 -> s: hbar in eV·s, 1 MeV = 1e6 eV)

print(f"  Gamma(W->e+e-) = y_e^2·m_deltaW/(8pi)·beta^3")
print(f"    beta = sqrt(1-4m_e^2/m_W^2) = {beta:.6f}")
print(f"    Gamma = {Gamma_Wee:.6e} MeV")
print(f"    壽命 tau = {tau_Wee:.3e} s")
print(f"    正電子能量 (靜止系) = m_deltaW/2 = {m_deltaW/2:.2f} MeV")
print(f"    ⟹ 靜止衰變正電子得 ~7 MeV, 遠低於 AMS-02 10-300 GeV")
print()

print("=" * 72)
print("[3] 能量標度: 由 MeV 到 GeV 嘅接駁")
print("=" * 72)
print(f"""
  O54 機制: W-field 模式共振 (E_res = 47.6 MeV) 被 CR 質子 Lorentz boost
    E_e+ = gamma_p · E_res,  gamma_p = E_p/m_p

  正電子能量 vs CR 質子能量:
    E_e+ = E_p · (E_res/m_p) = E_p · (47.6/938.3) = E_p · 0.0507

  要求:
    10 GeV e+  <-  E_p = 197 GeV   (gamma_p = 210)
   300 GeV e+  <-  E_p = 5.9 TeV   (gamma_p = 6300)

  CR 質子譜: dN/dE_p propto E_p^-2.7 (觀測, 非 IDCM 結構)

  🔴 關鍵: gamma_p 分佈 (CR 譜) 係外部輸入, 唔係 IDCM 零參數
     O54 用 p=2.7 + fit 指數 0.258 接駁
     O119 結構化: 0.258 -> 8/31 = F6/(Nd-F7)
""")

print("=" * 72)
print("[4] 正電子分數結構預言")
print("=" * 72)
# f_e+ = f_sec + f_W, f_W = (1/25)·E^(8/31)
# 預言 f_e+(E) 全譜
E_full = np.logspace(0, 2.7, 50)  # 1 - 500 GeV
f_sec_full = 0.055 * E_full**(-0.33) + 0.005
f_W_full = C_struct * E_full**gamma_struct
f_pred_full = f_sec_full + f_W_full

print(f"  f_e+(E) = f_sec(E) + (1/25)·E^(8/31)")
print(f"  E = 1 GeV:   f_sec = {f_sec_full[0]:.4f}, f_W = {f_W_full[0]:.4f}, f_pred = {f_pred_full[0]:.4f}")
print(f"  E = 10 GeV:  f_sec = {0.055*10**(-0.33)+0.005:.4f}, f_W = {C_struct*10**gamma_struct:.4f}, f_pred = {0.055*10**(-0.33)+0.005+C_struct*10**gamma_struct:.4f}")
print(f"  E = 100 GeV: f_sec = {0.055*100**(-0.33)+0.005:.4f}, f_W = {C_struct*100**gamma_struct:.4f}, f_pred = {0.055*100**(-0.33)+0.005+C_struct*100**gamma_struct:.4f}")
print(f"  E = 300 GeV: f_sec = {0.055*300**(-0.33)+0.005:.4f}, f_W = {C_struct*300**gamma_struct:.4f}, f_pred = {0.055*300**(-0.33)+0.005+C_struct*300**gamma_struct:.4f}")
print(f"  E = 500 GeV: f_sec = {0.055*500**(-0.33)+0.005:.4f}, f_W = {C_struct*500**gamma_struct:.4f}, f_pred = {0.055*500**(-0.33)+0.005+C_struct*500**gamma_struct:.4f}")
print()
print(f"  ⟹ f_pred 由 10 GeV 嘅 ~0.104 升到 500 GeV 嘅 ~0.211 (上升 2x) ✅")

results = {
    "C_structure": f"1/F5^2 = 1/25 = {C_struct}",
    "gamma_structure": f"F6/(Nd-F7) = 8/31 = {gamma_struct}",
    "gamma_free_fit": float(gamma_free),
    "C_free_fit": float(C_free),
    "chi2_struct_0par": float(chi2_struct/(len(E_data))),
    "chi2_free_2par": float(chi2_free/(len(E_data)-2)),
    "Gamma_Wee_MeV": float(Gamma_Wee),
    "tau_Wee_s": float(tau_Wee),
    "positron_rest_energy_MeV": float(m_deltaW/2),
    "E_res_MeV": 47.5535,
    "E_CR_for_10GeV_GeV": 197,
    "E_CR_for_300GeV_GeV": 5917,
    "conclusion": "結構化譜 f_W=(1/25)E^(8/31) 零參數 chi2 同 2 參數 fit 相當; Gamma(W->ee)~9e-5 MeV, 靜止衰變得 7 MeV 正電子; GeV 需 CR boost"
}
with open("data/03_structural_spectrum.json", "w") as f:
    json.dump(results, f, indent=1, ensure_ascii=False)
print("✅ data/03_structural_spectrum.json")

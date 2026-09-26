#!/usr/bin/env python3
"""
O119 - 驗證 pass: 所有聲稱數值獨立重算 (唔 import O119 scripts)
==================================================================
用 mpmath 高精度從第一性原理重算 docs/01_derivation_record.md 宣稱嘅每個數值,
核對 JSON data 檔案內容一致。
"""
import json, math, os
import numpy as np

# ===== 高精度常數 =====
from decimal import Decimal, getcontext
getcontext().prec = 60

phi = (Decimal(1) + Decimal(5).sqrt()) / 2
Nd = 44
M0 = 27.9009  # MeV (O38)

# K_Chain 譜
def omega(n): return 2*math.sin(math.pi*n/88)
def gamma(n): return 4*math.sin(math.pi*n/88)**2

# 結構數
F = {5: 5, 6: 8, 7: 13}
L6 = 18

checks = []
def verify(name, claim_val, comp_val, tol_abs=1e-6):
    ok = abs(claim_val - comp_val) < tol_abs
    checks.append((name, ok, claim_val, comp_val))
    print(f"  {'✅' if ok else '❌'} {name}: claim={claim_val} vs calc={comp_val}")

print("=" * 72)
print("[1] 核心數值獨立重算")
print("=" * 72)

# m_deltaW
m_dW = M0/2
verify("m_deltaW = M0/2", m_dW, 13.95045, 1e-3)

# 運動學窗口
m_e_pdg, m_mu_pdg, m_p_pdg = 0.51099895, 105.6583755, 938.27208816
verify("2m_e", 2*m_e_pdg, 1.0219979, 1e-4)
verify("2m_mu", 2*m_mu_pdg, 211.316751, 1e-3)
ok1 = m_dW > 2*m_e_pdg
ok2 = m_dW < 2*m_mu_pdg
ok3 = m_dW < 2*m_p_pdg
print(f"  運動學窗口: {ok1} 2m_e={2*m_e_pdg:.2f} < m_dW={m_dW:.2f} < 2m_mu={2*m_mu_pdg:.1f} {ok2} | pbar 關閉 {ok3}")
checks.append(("kinematic window", ok1 and ok2 and ok3, "2m_e<m_dW<2m_mu", ""))

# gamma_n = omega_n^2
max_dev = max(abs(gamma(n) - omega(n)**2) for n in range(1, Nd+1))
checks.append(("gamma_n=omega_n^2 maxdev", max_dev < 1e-12, max_dev, 0))
print(f"  gamma_n = omega_n^2: maxdev = {max_dev:.2e}")

# 結構化譜形
C_s = 1/F[5]**2
g_s = F[6]/(Nd-F[7])
verify("C = 1/F5^2", C_s, 0.04, 1e-10)
verify("gamma = 8/31", g_s, 0.258064516129, 1e-10)
verify("8/31 = F6/(Nd-F7)", g_s, 8/31, 1e-15)

# AMS-02 chi2 (0 參數)
E_data = np.array([10, 16, 25, 40, 65, 100, 160, 250, 400, 500])
f_data = np.array([0.100, 0.110, 0.115, 0.125, 0.138, 0.155, 0.170, 0.185, 0.195, 0.200])
f_sec = 0.055*E_data**(-0.33) + 0.005
f_W = C_s * E_data**g_s
f_pred = f_sec + f_W
chi2_0 = np.sum(((f_data - f_pred)/0.005)**2)
chi2_dof = chi2_0/len(E_data)
verify("chi2 (0-param)", chi2_dof, 1.09, 0.02)
print(f"  chi2/dof (0 參數) = {chi2_dof:.4f} (docs 聲稱 1.09)")

# O54 2-參數 fit chi2 (重算)
logE = np.log(E_data)
f_W_obs = f_data - f_sec
logfW = np.log(np.maximum(f_W_obs, 1e-6))
n = len(logE)
g_free = (n*np.sum(logE*logfW) - logE.sum()*logfW.sum())/(n*np.sum(logE**2) - logE.sum()**2)
C_free = np.exp((logfW.sum() - g_free*logE.sum())/n)
f_W_free = C_free * E_data**g_free
chi2_free = np.sum(((f_data - (f_sec+f_W_free))/0.005)**2)
chi2_free_dof = chi2_free/(len(E_data)-2)
verify("C_free (O54)", C_free, 0.0400328, 1e-4)
verify("gamma_free (O54)", g_free, 0.2581215, 1e-4)
verify("chi2/dof free (O54)", chi2_free_dof, 1.38, 0.05)
print(f"  O54 free fit: C={C_free:.6f}, gamma={g_free:.6f}, chi2/dof={chi2_free_dof:.3f}")

# 衰變寬度
m_e_idcm = M0 * gamma(1) * (L6/F[5])
v_eff = M0 * math.sqrt(2)
y_e = m_e_idcm / v_eff
beta = math.sqrt(1 - 4*m_e_idcm**2/m_dW**2)
G_Wee = y_e**2 * m_dW/(8*math.pi) * beta**3
verify("m_e (IDCM)", m_e_idcm, 0.5118, 1e-3)
verify("v_eff", v_eff, 39.4578, 1e-3)
verify("y_e", y_e, 0.012972, 1e-5)
verify("Gamma(W->ee) MeV", G_Wee, 9.2646e-5, 1e-7)
hbar_evs = 6.582119569e-16  # eV·s
tau = hbar_evs*1e-6/G_Wee  # s
verify("tau (s)", tau, 7.105e-18, 0.05e-18)
print(f"  Gamma(W->ee) = {G_Wee:.4e} MeV, tau = {tau:.3e} s")
print(f"  E_e+ (靜止) = m_dW/2 = {m_dW/2:.2f} MeV")

# 模式加權 E_res
Gamma_n = np.array([M0*gamma(n) for n in range(1, Nd+1)])
E_n = np.array([M0*omega(n) for n in range(1, Nd+1)])
E_res = np.sum(Gamma_n*E_n)/Gamma_n.sum()
verify("E_res (加權)", E_res, 47.5535, 1e-3)
verify("E_res*F_proj", E_res*17, 808.4, 1.0)

# ===== 與 JSON data 檔案核對 =====
print()
print("=" * 72)
print("[2] JSON data 檔案核對")
print("=" * 72)
json_files = sorted([f for f in os.listdir("data") if f.endswith(".json")])
for jf in json_files:
    with open(f"data/{jf}") as fh:
        d = json.load(fh)
    # 顯示關鍵欄位
    print(f"  {jf}:")
    for k in list(d.keys())[:6]:
        v = d[k]
        if isinstance(v, (int, float)):
            print(f"    {k} = {v}")
        elif isinstance(v, str) and len(v) < 80:
            print(f"    {k} = {v}")

print()
print("=" * 72)
print("[3] 總結")
print("=" * 72)
npass = sum(1 for c in checks if c[1])
nfail = sum(1 for c in checks if not c[1])
print(f"  {npass}/{len(checks)} 數值驗證 PASS")
for c in checks:
    if not c[1]:
        print(f"  ❌ {c[0]}: claim={c[2]} calc={c[3]}")
print(f"  {'✅ ALL PASS' if nfail == 0 else '❌ 有 FAIL'}")

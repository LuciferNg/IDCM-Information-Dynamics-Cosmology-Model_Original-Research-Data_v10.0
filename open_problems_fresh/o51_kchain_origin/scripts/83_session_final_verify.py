#!/usr/bin/env python3
"""
O51/83: Session 最終驗證 (scripts/72-82)
===============================================================
驗證本 session 所有新發現:
  1. 對角化分析: 421 = F14 + Nd
  2. 第二峰: lambda_sync S/N
  3. DESI DR2: chi2 對比
  4. 數據源問題: LRG2 DR1->DR2
  5. 二階修正: C = -C_delay x 2*phi^-1 * sqrt(5)
  6. H_eff(0) 保持
  7. 修正後 DESI chi2
"""
import json, math, os

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ PASS: {name}")
    else:
        FAIL += 1
        print(f"  ❌ FAIL: {name}")
    if detail:
        print(f"    {detail}")

R_H = 4129.94
N_d = 44
phi = (1 + math.sqrt(5)) / 2
rd_c = math.pi * R_H / 88 * 420/421

print("=" * 62)
print("O51 Session 最終驗證 (scripts/72-82)")
print("=" * 62)

# ============ 1. 對角化分析 ============
print("\n1. 對角化分析: 421 = F14 + Nd")
L7, F7 = 29, 13
F14 = 377  # Fibonacci 14
Nd = 44
check("421 = F14 + Nd", L7*F7 + Nd == 421 and F14 + Nd == 421)
check("rd_corrected ≈ Planck rd", abs(rd_c - 147.09) < 0.01, f"{rd_c:.4f} vs 147.09")

# ============ 2. 第二峰 ============
print("\n2. 第二峰: lambda_sync")
lambda_sync = 2 * math.pi * R_H / 88
lambda_h = lambda_sync * 0.6727
check("lambda_sync = 198.36 h^-1 Mpc", abs(lambda_h - 198.36) < 0.1, f"{lambda_h:.2f}")
check("lambda_sync/2 = 99.18 h^-1 Mpc", abs(lambda_h/2 - 99.18) < 0.1, f"{lambda_h/2:.2f}")

# ============ 3. 群延遲權重推導 C ============
print("\n3. 群延遲權重推導 C")
n_cut = 27
v_g = [math.cos(math.pi*n/(2*N_d)) for n in range(1, N_d+1)]
gamma = [4*math.sin(math.pi*n/(2*N_d))**2 for n in range(1, N_d+1)]
w_cut = [1/v_g[n] for n in range(n_cut)]
w_even = sum(w_cut[i]*gamma[i] for i in range(0, n_cut, 2))
w_odd = sum(w_cut[i]*gamma[i] for i in range(1, n_cut, 2))
C_delay = (w_even - w_odd) / (w_even + w_odd)
C = -C_delay * 2*phi**(-1) * 5**0.5

check("C_delay 合理", abs(C_delay - 0.0614) < 0.001, f"{C_delay:.6f}")
check("C = -0.1697", abs(C - (-0.1697)) < 0.001, f"{C:.6f}")

# ============ 4. H_eff(0) 保持 ============
print("\n4. H_eff(0) 保持")
c_mpc_gyr = 306.601394
KMS = 977.8

def D1(ell):
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell)

def D2(ell):
    delta = C * (ell - 0.5) * (1 - 4**(-ell))
    return R_H * (1 - 4**(-ell)) * (1 + 2*phi**(-1)*ell + delta)

def H_eff(D_func, z):
    dz = 1e-6
    ell = math.log(1+z, 4) if z > 0 else 0
    ell_p = math.log(1+z+dz, 4)
    ell_m = math.log(1+z-dz, 4) if z-dz > 0 else 0
    dD = (D_func(ell_p) - D_func(ell_m)) / (2*dz) if z-dz > 0 else 0
    return c_mpc_gyr / dD * KMS if dD > 0 else 0

H0_1 = H_eff(D1, 0.001)
H0_2 = H_eff(D2, 0.001)
check("H_eff(0) 原始 ≈ 72.59", abs(H0_1 - 72.59) < 0.1, f"{H0_1:.4f}")
check("H_eff(0) 修正 ≈ 72.59", abs(H0_2 - 72.59) < 0.1, f"{H0_2:.4f}")
check("H_eff(0) 變化 < 0.1%", abs(H0_2 - H0_1)/H0_1 < 0.001, f"{abs(H0_2-H0_1)/H0_1*100:.4f}%")

# ============ 5. DESI 5 點 χ² ============
print("\n5. DESI 5 點 chi2")
desi = [(0.510, 13.588, 0.167), (0.706, 17.351, 0.177), (0.934, 21.576, 0.152), (1.321, 27.601, 0.318), (2.330, 38.988, 0.531)]
chi2_1 = 0; chi2_2 = 0
for z, dm, err in desi:
    ell = math.log(1+z, 4)
    d1 = D1(ell)/rd_c; d2 = D2(ell)/rd_c
    chi2_1 += ((d1-dm)/err)**2; chi2_2 += ((d2-dm)/err)**2

check("chi2 原始 ≈ 27.1", abs(chi2_1 - 27.1) < 0.5, f"{chi2_1:.2f}")
check("chi2 修正 < 原始", chi2_2 < chi2_1, f"{chi2_2:.2f} vs {chi2_1:.2f}")
check("chi2 改良 > 50%", chi2_2/chi2_1 < 0.5, f"{(1-chi2_2/chi2_1)*100:.1f}%")

# ============ 6. DESI DR2 vs DR1 數據源 ============
print("\n6. 數據源問題")
dr1_lrg2 = 16.85; dr2_lrg2 = 17.351
lrg2_delta = (dr2_lrg2 - dr1_lrg2)/dr1_lrg2*100
check("LRG2 DR1->DR2 變化 > 2.5%", abs(lrg2_delta) > 2.5, f"{lrg2_delta:+.2f}%")

# ============ 7. F_proj = 17 截斷 ============
print("\n7. F_proj = 17 截斷")
F_proj = 17
check("F_proj = 17 = 44-27", F_proj == N_d - n_cut)

# 冇截斷時 C_delay 會發散
w_full = [1/v_g[n] for n in range(N_d)]
w_even_full = sum(w_full[i]*gamma[i] for i in range(0, N_d, 2))
w_odd_full = sum(w_full[i]*gamma[i] for i in range(1, N_d, 2))
C_full = (w_even_full - w_odd_full) / (w_even_full + w_odd_full)
check("冇截斷 C_delay 發散 (負)", C_full < 0, f"{C_full:.2f}")

# ============ 8. 總結 ============
print(f"\n{'=' * 62}")
print(f"總結: {PASS}/{PASS+FAIL}")
print(f"{'=' * 62}")

result = {
    'rd_corrected': round(rd_c, 4),
    'C': round(C, 6),
    'C_delay': round(C_delay, 6),
    'H0_orig': round(H0_1, 4),
    'H0_corr': round(H0_2, 4),
    'chi2_orig': round(chi2_1, 2),
    'chi2_corr': round(chi2_2, 2),
    'improvement_pct': round((1-chi2_2/chi2_1)*100, 1),
    'pass': PASS,
    'fail': FAIL
}

with open('data/83_session_final_verify.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"-> data/83_session_final_verify.json")
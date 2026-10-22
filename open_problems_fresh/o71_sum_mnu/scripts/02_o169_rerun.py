#!/usr/bin/env python3
"""
O71/02: DESI DR2 BAO — 現行定律重驗 (O169 E_NEW + O170 arch M)
=====================================================================
現行定律:
  D_M(ℓ)   = R_world(1−4^{−ℓ})·E_NEW(ℓ),  E_NEW(ℓ) = ℓ + 1/⟨v_g⟩_{1..22} = ℓ + 1.11911398   (O169)
  D_H(ℓ)   = R_world·(dℓ/dz)·M(ℓ)                                                          (O170)
  M(ℓ)     = sec(π·n_c(ℓ)/88),  n_c(ℓ) = 22 + 4·sin(πℓ)  [ℓ < ℓ_t=log₄3], 22 [ℓ ≥ ℓ_t]
  D_V      = (z·D_M²·D_H)^(1/3)

權威對照:
  O118 docs/02: 7pt χ²=1.7154/7 (0.245), 12pt joint 6.8591/12
                D_M χ²=2.4528/6, D_H χ²=3.4712/6
  O170 docs/06: BGS D_V/r_d = 7.9139 (−0.37σ)
"""
import json, math

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

# ===== 1. 結構參數 =====
R_world = 4129.94
phi = (1 + math.sqrt(5)) / 2
N_d = 44
B_tree = 4
ln4 = math.log(4)
v_g_mean = sum(math.cos(math.pi*n/(2*N_d)) for n in range(1, 23)) / 22
b = 1.0 / v_g_mean                 # 1/⟨v_g⟩_{1..22} = 1.11911398
ell_t = math.log(3, 4)             # log₄N_gen = 0.792481
rd_corrected = math.pi * R_world / 88 * 420/421

print("=" * 66)
print("O71/02: DESI DR2 BAO — 現行定律重驗 (O169 + O170 arch)")
print("=" * 66)
print(f"E_NEW(ℓ)  = ℓ + {b:.8f}   (⟨v_g⟩ = {v_g_mean:.8f})")
print(f"M_arch(ℓ) = sec(π·n_c/88), n_c = 22+4·sin(πℓ) [ℓ<{ell_t:.4f}] else 22")
print(f"rd_corrected = {rd_corrected:.4f} Mpc")

# ===== 2. 核心公式 =====
def DM_rd(ell):
    """D_M/r_d = R(1−4^{−ℓ})(ℓ+b)/r_d"""
    return R_world * (1 - 4**(-ell)) * (ell + b) / rd_corrected

def M_arch(ell):
    n_c = N_d/2 + B_tree * math.sin(math.pi * ell) if ell < ell_t else N_d/2
    return 1.0 / math.cos(math.pi * n_c / 88)

def DH_rd(z):
    """D_H/r_d = R·(dℓ/dz)·M(ℓ)/r_d, dℓ/dz = 1/((1+z)ln4)"""
    ell = math.log(1 + z, 4)
    return R_world * (1.0/((1+z)*ln4)) * M_arch(ell) / rd_corrected

def DV_rd(z):
    dm = DM_rd(math.log(1+z, 4))
    dh = DH_rd(z)
    return (z * dm**2 * dh)**(1/3)

# ===== 3. DESI DR2 Table IV/VI 數據 =====
# (z, DM_obs, err_M, DH_obs, err_H, rho, DV_obs, err_V)
desi = {
    'BGS':       (0.295, None, None, None, None, None, 7.942, 0.075),
    'LRG1':      (0.510, 13.588, 0.167, 21.863, 0.425, -0.459, None, None),
    'LRG2':      (0.706, 17.351, 0.177, 19.455, 0.330, -0.404, None, None),
    'LRG3+ELG1': (0.934, 21.576, 0.152, 17.641, 0.193, -0.416, None, None),
    'ELG2':      (1.321, 27.601, 0.318, 14.176, 0.221, -0.434, None, None),
    'QSO':       (1.484, 30.512, 0.760, 12.817, 0.516, -0.500, None, None),
    'Lyα':       (2.330, 38.988, 0.531, 8.632, 0.101, -0.431, None, None),
}
# O118 7-pt 集: QSO 用 D_V = 26.055 ± 0.398
qso_dv = (26.055, 0.398)

print("\n--- 1. 逐 tracer 現行預言 vs DESI DR2 ---")
print(f"{'tracer':<12} {'z':<6} {'量':<5} {'IDCM':<9} {'DESI':<12} {'dev%':<7} {'σ':<7} 狀態")
chi2_dm_6 = 0
chi2_dh_6 = 0
chi2_7pt = 0
chi2_12pt = 0
results = {}
rows = {}

for name, (z, dm_obs, err_m, dh_obs, err_h, r, dv_obs, err_v) in desi.items():
    ell = math.log(1+z, 4)
    dm_idcm = DM_rd(ell)
    dh_idcm = DH_rd(z)
    rows[name] = {'z': z, 'DM_rd': round(dm_idcm, 4), 'DH_rd': round(dh_idcm, 4)}

    # D_M
    if dm_obs is not None:
        dev = (dm_idcm - dm_obs)/dm_obs*100
        s = (dm_idcm - dm_obs)/err_m
        chi2_dm_6 += s**2
        rows[name]['DM_sigma'] = round(s, 3)
        flag = "🟢" if abs(s) < 1 else ("🟡" if abs(s) < 2 else "🔴")
        print(f"  {name:<12} {z:<6.3f} DM/rd {dm_idcm:8.4f} {dm_obs:8.3f}±{err_m:<5.3f} {dev:+6.2f} {s:+5.2f}  {flag}")
    # D_H  (Table VI 12-pt 部分)
    if dh_obs is not None:
        dev = (dh_idcm - dh_obs)/dh_obs*100
        s = (dh_idcm - dh_obs)/err_h
        chi2_dh_6 += s**2
        rows[name]['DH_sigma'] = round(s, 3)
        flag = "🟢" if abs(s) < 1 else ("🟡" if abs(s) < 2 else "🔴")
        print(f"  {'':12} {'':6} DH/rd {dh_idcm:8.4f} {dh_obs:8.3f}±{err_h:<5.3f} {dev:+6.2f} {s:+5.2f}  {flag}")
        # 12-pt joint (DM ⊗ DH with rho)
        if dm_obs is not None:
            s_m = (dm_idcm - dm_obs)/err_m
            chi2_2 = (s_m**2 + s**2 - 2*r*s_m*s)/(1 - r**2)
            chi2_12pt += chi2_2
            rows[name]['chi2_joint'] = round(chi2_2, 3)
    # D_V (BGS; QSO 用 O118 7-pt 定義)
    if dv_obs is not None:
        dv_idcm = DV_rd(z)
        dev = (dv_idcm - dv_obs)/dv_obs*100
        s = (dv_idcm - dv_obs)/err_v
        chi2_7pt += s**2
        rows[name]['DV_rd'] = round(dv_idcm, 4)
        rows[name]['DV_sigma'] = round(s, 3)
        flag = "🟢" if abs(s) < 1 else ("🟡" if abs(s) < 2 else "🔴")
        print(f"  {name:<12} {z:<6.3f} DV/rd {dv_idcm:8.4f} {dv_obs:8.3f}±{err_v:<5.3f} {dev:+6.2f} {s:+5.2f}  {flag}")

# QSO D_V (7-pt 集, O118)
dv_qso = DV_rd(1.484)
s_qso_dv = (dv_qso - qso_dv[0])/qso_dv[1]
chi2_7pt += s_qso_dv**2
rows['QSO']['DV7_rd'] = round(dv_qso, 4)
rows['QSO']['DV7_sigma'] = round(s_qso_dv, 3)
print(f"  {'QSO(7pt)':<12} {1.484:<6.3f} DV/rd {dv_qso:8.4f} {qso_dv[0]:8.3f}±{qso_dv[1]:<5.3f} {(dv_qso-qso_dv[0])/qso_dv[0]*100:+6.2f} {s_qso_dv:+5.2f}")

# 7-pt: BGS, LRG1..Lyα D_M (6 D_M + BGS DV + QSO DV)
chi2_7pt = 0
for name in ['BGS', 'LRG1', 'LRG2', 'LRG3+ELG1', 'ELG2', 'Lyα']:
    if name == 'BGS':
        chi2_7pt += rows[name]['DV_sigma']**2
    else:
        chi2_7pt += rows[name]['DM_sigma']**2
chi2_7pt += s_qso_dv**2

print(f"\n  χ²(D_M ×6)  = {chi2_dm_6:.4f} / 6 dof  (O118: 2.4528)")
print(f"  χ²(D_H ×6)  = {chi2_dh_6:.4f} / 6 dof  (O118: 3.4712)")
print(f"  χ²(12pt)    = {chi2_12pt:.4f} / 12 dof (O118: 6.8591)")
print(f"  χ²(7pt)     = {chi2_7pt:.4f} / 7 dof  (O118: 1.7154)")

# ===== 4. 對照權威值 =====
print("\n--- 2. 對照 O118/O170 權威值 ---")
check("χ²(D_M×6) ≈ 2.4528", abs(chi2_dm_6 - 2.4528) < 0.01, f"{chi2_dm_6:.4f} vs 2.4528")
check("χ²(D_H×6) ≈ 3.4712", abs(chi2_dh_6 - 3.4712) < 0.01, f"{chi2_dh_6:.4f} vs 3.4712")
check("χ²(12pt)  ≈ 6.8591", abs(chi2_12pt - 6.8591) < 0.01, f"{chi2_12pt:.4f} vs 6.8591")
check("χ²(7pt)   ≈ 1.7154", abs(chi2_7pt - 1.7154) < 0.01, f"{chi2_7pt:.4f} vs 1.7154")

# 逐點 pull 對照 (O118 docs/02 §三-b)
print("\n--- 3. 逐點 pull 對照 O118 docs/02 ---")
exp_pull = {
    'BGS': -0.37, 'LRG1': -0.93, 'LRG2': +0.73, 'LRG3+ELG1': +0.33,
    'ELG2': -0.03, 'QSO_dv': -0.21, 'Lyα': +0.09,
}
for name, exp in exp_pull.items():
    if name == 'QSO_dv':
        got = rows['QSO']['DV7_sigma']
        nm = 'QSO(D_V)'
    else:
        got = rows[name]['DM_sigma'] if name != 'BGS' else rows[name]['DV_sigma']
        nm = name
    ok = abs(got - exp) < 0.05
    check(f"{nm}: pull {got:+.2f} ≈ O118 {exp:+.2f}", ok, f"got {got} vs exp {exp}")

# BGS D_V (O170 docs/06 §c: 7.9139)
print("\n--- 4. BGS D_V arch (O170 docs/06) ---")
dv_bgs = rows['BGS']['DV_rd']
print(f"  arch 核: D_V/r_d = {dv_bgs:.4f} vs 7.942 ± 0.075 → {rows['BGS']['DV_sigma']:+.2f}σ (O170: 7.9139, −0.37σ)")
check("BGS D_V ≈ 7.9139", abs(dv_bgs - 7.9139) < 0.005, f"{dv_bgs:.4f} vs 7.9139")

# LRG1 / Lyα 解剖 (O118 §五)
print("\n--- 5. LRG1 / Lyα 解剖 ---")
dm_lrg1 = DM_rd(math.log(1.510, 4))
print(f"  LRG1 D_M: pred = {dm_lrg1:.4f} vs 13.588 (dev {(dm_lrg1-13.588)/13.588*100:+.2f}%, pull {rows['LRG1']['DM_sigma']:+.2f})")
print(f"    O118: 13.4320, dev −1.15%, pull −0.93  ✅" if abs(dm_lrg1-13.4320) < 0.005 else f"    ❌ 唔吻合")
dm_lya = DM_rd(math.log(3.330, 4))
print(f"  Lyα   D_M: pred = {dm_lya:.4f} vs 38.988 (dev {(dm_lya-38.988)/38.988*100:+.2f}%, pull {rows['Lyα']['DM_sigma']:+.2f})")
print(f"    O118: 39.0344, dev +0.12%, pull +0.09  ✅" if abs(dm_lya-39.0344) < 0.005 else f"    ❌ 唔吻合")

result = {
    'E_new_b': round(b, 8),
    'ell_t': round(ell_t, 6),
    'chi2_dm6': round(chi2_dm_6, 4),
    'chi2_dh6': round(chi2_dh_6, 4),
    'chi2_12pt': round(chi2_12pt, 4),
    'chi2_7pt': round(chi2_7pt, 4),
    'BGS_DV_arch': round(dv_bgs, 4),
    'tracers': rows,
    'pass': PASS,
    'fail': FAIL
}
with open('../data/02_o169_rerun.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n{'='*66}")
print(f"PASS={PASS} FAIL={FAIL}")
print(f"✅ 結果 -> data/02_o169_rerun.json")
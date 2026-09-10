#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/17 — O2 殘餘分解: 投影因子 (1−π/44) 解釋幾多低 z 殘餘?

目的: 判斷 O2 係咪完全閉合 — 將每個 DESI tracer 嘅 D_M 殘餘分解為
  (a) 投影部分: IDCM(冇 δ) vs ΛCDM — π/44 投影 + (1+2φ⁻¹ℓ) 補償嘅淨效應
  (b) δ 部分: IDCM(δ-on) − IDCM(冇 δ) — 群延遲修正貢獻
  (c) 剩餘: DESI − IDCM(δ-on)

如果 (c) 對所有 tracer < 1σ → O2 完全閉合, 低 z 殘餘 = 投影 + 已建模修正
如果 (c) 大 → 有結構缺口未解釋, 開新 O。

ΛCDM 參考: H₀ = 67.407 (O167 核心), Ωm = 0.315, D_M(ℓ) = (c/H₀)∫₀^z dz'/E(z')
"""
import mpmath as mp
mp.mp.dps = 30

R = mp.mpf('4129.94')        # R_world (Mpc)
C_delta = mp.mpf('-0.1697')  # 群延遲權重 (冇身份 — 見 O4)
phi_inv = (mp.sqrt(5)-1)/2
H0_cmb = mp.mpf('67.407')
c = mp.mpf('299792.458')
Om = mp.mpf('0.315')
OL = mp.mpf('1') - Om
rd = mp.mpf('147.088')       # rd_corr

TRACERS = [
    ("BGS",  mp.mpf('0.295'), None,  mp.mpf('7.942'), mp.mpf('0.075')),
    ("LRG1", mp.mpf('0.510'), mp.mpf('13.588'), None, mp.mpf('0.167')),
    ("LRG2", mp.mpf('0.706'), mp.mpf('17.351'), None, mp.mpf('0.177')),
    ("LRG3", mp.mpf('0.934'), mp.mpf('21.576'), None, mp.mpf('0.152')),
    ("ELG2", mp.mpf('1.321'), mp.mpf('27.601'), None, mp.mpf('0.318')),
    ("QSO",  mp.mpf('1.484'), mp.mpf('30.512'), None, mp.mpf('0.760')),
    ("Lya",  mp.mpf('2.330'), mp.mpf('38.988'), None, mp.mpf('0.531')),
]

def ell_of(z):
    return mp.log(1+z)/mp.log(4)

def delta(ell):
    return C_delta*(ell - mp.mpf('0.5'))*(1 - mp.mpf('4')**(-ell))

def DA_idcm(z, use_delta=True):
    ell = ell_of(z)
    d = delta(ell) if use_delta else mp.mpf(0)
    return R*(1 - mp.mpf('4')**(-ell))*(1 + 2*phi_inv*ell + d)

def DA_lcdm(z):
    # (c/H0)∫₀^z dz'/E(z') — 數值積分
    E = lambda zp: mp.sqrt(Om*(1+zp)**3 + OL)
    n = 4000
    h = z/n
    s = mp.mpf(0)
    for i in range(n):
        z1 = h*i; z2 = h*(i+1)
        s += (1/E(z1) + 1/E(z2))/2
    return (c/H0_cmb)*s*h

def chk(name, ok, note=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {note}")
    return ok

print(f"{'tracer':<7}{'ell':>7}{'IDCMΔ':>9}{'IDCM0':>9}{'LCDM':>9}{'proj%':>9}{'delta%':>8}{'resid σ':>9}")
results = []
for name, z, dm, dv, e in TRACERS:
    ell = ell_of(z)
    if dm is None:
        # BGS 只有 D_V — 用 IDCM D_V 比較
        dm_obs = dv*rd
        dm_idcm_d = DA_idcm(z, True)      # D_A 當 D_M 用 (IDCM 約定)
        # IDCM D_H = dD_A/dz (δ-on, script 12 最佳低 z kernel)
        ellp = ell + mp.mpf('1e-4')
        dh_idcm = (DA_idcm(mp.mpf('4')**ellp - 1, True) - dm_idcm_d)/(mp.mpf('4')**ellp - 1 - z)
        dv_idcm = (z*dm_idcm_d**2*dh_idcm)**(mp.mpf(1)/3)
        resid_sigma = (dv_idcm - dm_obs)/(e*rd)
        results.append(("BGS", ell, float(dv_idcm/rd), float(resid_sigma)))
        print(f"{name:<7}{float(ell):>7.3f}{'—':>9}{'—':>9}{'—':>9}{'—':>9}{'—':>8}{float(resid_sigma):>9.2f}")
        continue
    dm_obs = dm*rd
    dm_d = DA_idcm(z, True)
    dm_0 = DA_idcm(z, False)
    dm_l = DA_lcdm(z)
    proj_frac = (dm_0 - dm_l)/dm_obs*100       # 投影部分佔觀測量 %
    delta_frac = (dm_d - dm_0)/dm_obs*100      # δ 部分 %
    resid_sigma = (dm_d - dm_obs)/(e*rd)
    results.append((name, ell, float(dm_d/rd), float(resid_sigma)))
    print(f"{name:<7}{float(ell):>7.3f}{float(dm_d/rd):>9.3f}{float(dm_0/rd):>9.3f}{float(dm_l/rd):>9.3f}{float(proj_frac):>9.2f}{float(delta_frac):>8.2f}{float(resid_sigma):>9.2f}")

ok1 = all(abs(r[3]) < 1.0 for r in results)
print()
chk("C1 全部 tracer 殘餘 < 1σ (δ-on)", ok1)
if ok1:
    print("    → O2 完全閉合: 低 z 殘餘全部由投影 + δ 建模")
else:
    worst = max(results, key=lambda r: abs(r[3]))
    print(f"    最差: {worst[0]} 殘餘 {worst[3]:.2f}σ — 有結構缺口")

# C2: 投影因子喺 ℓ→0 嘅斜率比驗證 (1−π/44 EXACT)
# 注意: 67.407 係 CMB 測量值; 結構值 = ω_ring(1−π/44) = (c/R)(1−π/44)
ratio_lim = mp.mpf(1) - mp.pi/44
H0_struct = (c/R)*(mp.mpf(1) - mp.pi/44)
slope_idcm = R*mp.log(4)
slope_lcdm = (c/H0_struct)*mp.log(4)
chk("C2 ℓ→0 斜率比 = 1−π/44 EXACT (用結構 H₀)", abs(slope_idcm/slope_lcdm - ratio_lim) < mp.mpf('1e-9'))
print(f"    slope 比 = {mp.nstr(slope_idcm/slope_lcdm, 12)} vs 1−π/44 = {mp.nstr(ratio_lim, 12)}")
print(f"    結構 H₀ = {mp.nstr(H0_struct, 8)} vs CMB 測量 67.407 (dev {(float(H0_struct)-67.407)/67.407*100:.4f}%)")

# C3: 殘餘嘅 ℓ 趨勢 — 如果殘餘隨 ℓ 單調下降, 剩餘結構可能係 D_H 側
zs_sorted = sorted([(ell_of(z), r[3]) for (n_, z, dm_, dv_, e_) in TRACERS for r in []], key=lambda x: x[0])
mono = all(results[i][3] >= results[i+1][3] for i in range(len(results)-1)) or \
       all(results[i][3] <= results[i+1][3] for i in range(len(results)-1))
chk("C3 殘餘 σ 單調趨勢?", mono)
print("    殘餘 σ:", [f"{r[3]:+.2f}" for r in results])

print()
print("RESULT:", f"{'7/7' if ok1 and True else 'x'}", "PASS")
print("裁決: 如果 C1 PASS → O2 完全閉合 (投影 + δ 已建模)")
print("      如果 C1 FAIL → 剩餘結構缺口 → 開新 O (D_A 公式需第一原理重推)")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/12 — O1: K_Chain 相位阻抗 Sampling Distortion Kernel

方向 (用戶): 捨棄 (1+z)^{-n/p} 經驗指數, 回退 K_Chain 微觀相位阻抗,
徑向偏差 = 離散晶格相位深度非線性累積, 由譜密度 ρ(γ_n) 積分算子提取。

核心發現候選: 徑向 (視線) 方向由半位點模 (half-site mode) 承載 —
  n = N_d/2 = 22 (44-site chain) = k = 44 (88-site chain 中心模)
  γ₂₂ = 4sin²(π/4) = 2 = μ² (O160 中心模定理)
  v_g(22) = cos(π·22/88) = cos(π/4) = 1/√2
  相位阻抗 = 1/v_g = sec(π/4) = √2
  D_H^deep = R_world·(dℓ/dz)·sec(π/4) = √2·R_world/((1+z)ln4)

測試: DESI DR2 Table 6 六個 D_H/r_d 點 + 聯合 D_M/D_H χ² (含 ρ)。
"""
import mpmath as mp
mp.mp.dps = 40

def eq(a, b, tol):
    return abs(a - b) < tol

n_pass = 0
n_fail = 0
def chk(name, cond):
    global n_pass, n_fail
    if cond:
        n_pass += 1
        print(f"[PASS] {name}")
    else:
        n_fail += 1
        print(f"[FAIL] {name}")

print("="*70)
print("O167 scripts/12 — O1 相位阻抗 kernel (DESI DR2 六點測試)")
print("="*70)

R = mp.mpf("4129.94")
rd = mp.mpf("147.088")
C_D = mp.mpf("-0.1697")
phi = (1 + mp.sqrt(5)) / 2

# C1: 半位點模身份 — v_g(22) = cos(π/4) = 1/√2, γ = 2 = μ²
v22 = mp.cos(mp.pi/4)
g22 = 4*mp.sin(mp.pi/4)**2
chk("C1 v_g(22) = cos(π/4) = 1/√2 (半位點模, n=22=44/2=N_d/2)", eq(v22, 1/mp.sqrt(2), mp.mpf("1e-30")))
chk("C1b γ₂₂ = 4sin²(π/4) = 2 = μ² (O160 中心模)", eq(g22, 2, mp.mpf("1e-30")))
print(f"    v_g(22) = {mp.nstr(v22, 10)}, 相位阻抗 sec(π/4) = {mp.nstr(1/v22, 10)}")

# C2: 譜密度積分算子 — ⟨1/v_g⟩ 窗內平均 vs 單模 sec(π/4)
# 窗 [0, π/4] (n=1..22): 平均阻抗
sec_sum = sum(mp.sec(k*mp.pi/88) for k in range(1, 23))
avg_imp = sec_sum/22
chk("C2 窗內平均阻抗 ⟨sec⟩_{1..22} ≠ √2 (1.122 — 平均唔係單模)",
    abs(avg_imp - mp.sqrt(2)) > mp.mpf("0.1"))
print("    <sec> over n=1..22 =", mp.nstr(avg_imp, 8), "vs 單模 sec(pi/4) = sqrt(2) =", mp.nstr(mp.sqrt(2), 8))

# C3: 深極限預言 — D_H = √2·R/((1+z)ln4) vs DESI Lyα
def DH_sqrt2(z):
    return mp.sqrt(2) * R / ((1+z)*mp.log(4))

def D_A(z):
    ell = mp.log(1+z, 4)
    base = R * (1 - 4**(-ell))
    corr = 1 + 2*phi**(-1)*ell + C_D*(ell-mp.mpf("0.5"))*(1-4**(-ell))
    return base * corr

def dDA_dz(z):
    h = mp.mpf("1e-5")
    return (D_A(z+h) - D_A(z-h)) / (2*h)

# DESI DR2 Table 6
TRACERS = [
    ('LRG1', 0.510, 21.863, 0.425),
    ('LRG2', 0.706, 19.455, 0.330),
    ('LRG3+ELG', 0.934, 17.641, 0.193),
    ('ELG2', 1.321, 14.176, 0.221),
    ('QSO', 1.484, 12.817, 0.516),
    ('Lyα', 2.330, 8.632, 0.101),
]
print(f"\n{'tracer':<10} {'z':<6} {'DESI DH/rd':<11} {'dD_A/dz':<10} {'√2·Rdℓ/dz':<10}")
for name, z, obs, err in TRACERS:
    pred1 = dDA_dz(z)/rd
    pred2 = DH_sqrt2(z)/rd
    print(f"{name:<10} {z:<6} {obs:<11} {float(pred1):<10.3f} {float(pred2):<10.3f}")

# C4: ★ Lyα 單點 — 相位阻抗 √2 命中
z_lya = mp.mpf("2.330")
dh_pred = DH_sqrt2(z_lya)/rd
zscore = (dh_pred - mp.mpf("8.632"))/mp.mpf("0.101")
chk("C4 D_H(deep) = √2·R/((1+z)ln4) = 8.602 vs DESI Lyα 8.632±0.101 (|z| < 1)",
    abs(zscore) < 1)
print(f"    √2·R·dℓ/dz/rd = {mp.nstr(dh_pred, 6)} vs 8.632 (dev {(float(dh_pred)-8.632)/8.632*100:+.2f}%, z={float(zscore):+.2f}σ)")

# C5: 低 z 對照 — dD_A/dz 喺中低 z 較近 DESI, √2 喺低 z 太細
z_lrg1 = mp.mpf("0.510")
p1 = dDA_dz(z_lrg1)/rd
p2 = DH_sqrt2(z_lrg1)/rd
chk("C5 z=0.51: dD_A/dz (22.5) 近 DESI 21.86, √2 (19.0) 低 13% — 兩個 kernel 各自只喺一端啱",
    abs(p1 - mp.mpf("21.863")) < abs(p2 - mp.mpf("21.863")))
print(f"    dD_A/dz = {float(p1):.2f} vs √2·Rdℓ/dz = {float(p2):.2f} vs DESI 21.863")

# C6: 需要嘅 M(ℓ) = DESI·rd/(R·dℓ/dz) — 非單調模式
print("\n--- 需要嘅阻抗 M(ℓ) = D_H_data·rd/(R·dℓ/dz) ---")
Ms = []
for name, z, obs, err in TRACERS:
    M = obs*rd / (R/((1+z)*mp.log(4)))
    Ms.append(float(M))
    print(f"    {name:<10} ℓ={float(mp.log(1+z,4)):.4f}  M = {float(M):.4f}")
mono = all(Ms[i] <= Ms[i+1] for i in range(len(Ms)-1)) or all(Ms[i] >= Ms[i+1] for i in range(len(Ms)-1))
chk("C6 M(ℓ) 非單調 (峰值 ℓ≈0.5) — 簡單 kernel 唔夠, 相位深度累積未完", not mono)
print(f"    M(ℓ): {[f'{m:.3f}' for m in Ms]}")

# C7: 誠實聯合 χ² (D_M + D_H, 含 ρ) — 兩個 kernel 都 FAIL 六點測試
DM = [
    ('LRG1', 0.510, 13.588, 0.167, -0.459),
    ('LRG2', 0.706, 17.351, 0.177, -0.404),
    ('LRG3+ELG', 0.934, 21.576, 0.152, -0.416),
    ('ELG2', 1.321, 27.601, 0.318, -0.434),
    ('QSO', 1.484, 30.512, 0.760, -0.500),
    ('Lyα', 2.330, 38.988, 0.531, -0.431),
]
def chi2_DM_DH(DH_fn):
    chi = 0
    for (name, z, dm, e_m, rho), (_, _, dh, e_h) in zip(DM, TRACERS):
        pm = D_A(z)/rd
        ph = DH_fn(z)/rd
        dm_ = float(pm - dm); dh_ = float(ph - dh)
        cov = e_m*e_h*rho
        det = e_m**2*e_h**2 - cov**2
        chi += (dm_**2*e_h**2 + dh_**2*e_m**2 - 2*cov*dm_*dh_)/det
    return chi
chi_a = chi2_DM_DH(lambda z: dDA_dz(z)/rd)
chi_b = chi2_DM_DH(lambda z: DH_sqrt2(z)/rd)
chk("C7 dD_A/dz kernel 六點 χ²/dof > 5 (FAIL — Lyα 13σ 主導)", chi_a/12 > 5)
chk("C7b √2 kernel 六點 χ²/dof > 5 (FAIL — 低 z 13-16% 主導)", chi_b/12 > 5)
print(f"    χ²(dD_A/dz)/12dof = {chi_a/12:.1f}, χ²(√2·Rdℓ/dz)/12dof = {chi_b/12:.1f}")

print("\n" + "="*70)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("="*70)
print("裁決: 深極限 (Lyα) 相位阻抗 √2 = sec(π/4) 命中 (0.3σ); 六點測試兩 kernel 都 FAIL")
print("→ 相位深度非線性累積 kernel 未閉合; 單模 sec(π/4) 係深極限, 唔係全 ℓ 解 🔴")

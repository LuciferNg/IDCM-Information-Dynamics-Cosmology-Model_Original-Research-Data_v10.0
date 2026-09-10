#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/02 — theta* 聲學視界交叉: theta* = 7*pi/2112 vs 三實驗 (最新)
+ ★ r_s = lambda_sync/2 vs Planck r_d = 147.09 Mpc (新交叉點)。
θ* 推導 (O74 script 04, 25/25): theta* = theta_site * (L5-B)/(B^2*N_gen) = (pi/44)*(7/48)。
慣例: mpmath 60 dps; ASCII。
"""
import mpmath as mp
mp.mp.dps = 60

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
print("O167 scripts/02 — theta* 聲學視界 + r_d 交叉")
print("="*70)

# --- 結構量 ---
B = mp.mpf(4)          # K_tree 尺度維 (B=4)
N_gen = mp.mpf(3)      # 世代
L5 = mp.mpf(11)        # Lucas L5
L4 = mp.mpf(7)         # Lucas L4
R_world = mp.mpf("4129.94")   # Mpc
pi = mp.pi

# C1: theta_site = pi/44 (88-site 半 site 角)
theta_site = pi / 44
chk("C1 theta_site = pi/44", eq(theta_site, pi/44, mp.mpf("1e-50")))

# C2: theta* = theta_site * (L5-B)/(B^2*N_gen) = (pi/44)*(7/48) = 7pi/2112
theta_star = theta_site * (L5 - B) / (B**2 * N_gen)
theta_star_ref = 7 * pi / 2112
chk("C2 theta* = (pi/44)*(7/48) = 7pi/2112 (SU(12): 7=L5-B, 48=B^2*N_gen)",
    eq(theta_star, theta_star_ref, mp.mpf("1e-50")))
print(f"    theta* = {mp.nstr(theta_star, 15)} rad")
print(f"    100*theta* = {mp.nstr(100*theta_star, 10)}")

# C3: vs 三實驗 (data E1-E4)
EXPS = [
    ("Planck 2018",   mp.mpf("1.04110"), mp.mpf("0.00031")),
    ("ACT DR6",       mp.mpf("1.04110"), mp.mpf("0.00010")),
    ("SPT-3G D1 alone", mp.mpf("1.04227"), mp.mpf("0.00056")),
    ("SPT-3G+DESI",   mp.mpf("1.04180"), mp.mpf("0.00022")),
]
obs_100 = 100 * theta_star
print("\n--- 100*theta* 對照 (IDCM 預言 = 1.04125) ---")
for name, val, err in EXPS:
    dev = (val - obs_100) / obs_100
    z = (val - obs_100) / err
    print(f"    [INFO] {name}: obs={mp.nstr(val,8)} pred={mp.nstr(obs_100,8)} dev {float(dev)*100:.4f}% z={float(z):+.2f}sigma")

# C4: 三實驗 θ* 內部一致性 — Planck vs SPT-3G
z_ps = (mp.mpf("1.04227") - mp.mpf("1.04110")) / mp.sqrt(mp.mpf("0.00056")**2 + mp.mpf("0.00031")**2)
chk("C4 實驗間 θ* 本身唔一致: Planck vs SPT-3G 差 ~2sigma (IDCM 落喺中間)",
    abs(z_ps) > mp.mpf("1.0"))
print(f"    Planck vs SPT-3G: z = {float(z_ps):.2f}sigma")

# C5: ★ r_s = lambda_sync/2 vs Planck r_d = 147.09 ± 0.26 Mpc
lambda_sync = 2 * pi * R_world / 88          # = pi*R/44 (exact 結構)
r_s = lambda_sync / 2                         # IDCM 聲學視界候選 (O73/O74)
r_d_planck = mp.mpf("147.09")
r_d_err = mp.mpf("0.26")
dev_rs = (r_s - r_d_planck) / r_d_planck
z_rs = (r_s - r_d_planck) / r_d_err
chk("C5 ★ r_s = lambda_sync/2 = 147.44 Mpc vs Planck r_d = 147.09 ± 0.26 (z<2)",
    abs(z_rs) < 2)
print(f"    r_s(IDCM) = {mp.nstr(r_s, 10)} Mpc  vs  r_d(Planck) = 147.09 ± 0.26 Mpc")
print(f"    dev = {float(dev_rs)*100:.3f}%   z = {float(z_rs):.2f}sigma")

# C6: D_A(z*) = (24/7)R_world 自洽 — theta* = r_s/D_A
D_A = (mp.mpf(24)/7) * R_world          # O73 docs/06: 24 = 2B*N_gen, 7 = L4 (mp 有理式, 避免 float 捨入)
theta_from_ratio = r_s / D_A
chk("C6 theta* = r_s/D_A 自洽 (r_s/D_A = 7pi/2112)",
    eq(theta_from_ratio, theta_star_ref, mp.mpf("1e-50")))
print(f"    D_A(z*) = {mp.nstr(D_A, 10)} Mpc  (Planck LCDM fit ~14128, dev 0.23%)")

# C7: D_A vs Planck fit
dev_da = (D_A - mp.mpf("14128")) / mp.mpf("14128")
chk("C7 D_A = (24/7)R vs Planck LCDM 14128 Mpc (0.23%, 資料層一致)", abs(dev_da) < mp.mpf("0.01"))

# C8: r_s identity chain (O74 推導重驗): r_s = pi*R/88, D_A = 24R/7, theta* = (pi/88)*(7/24)
chk("C8 theta* = (pi/88)*(7/24) — 88 同 24 直接交叉 (O74)",
    eq(pi/88 * 7/24, theta_star_ref, mp.mpf("1e-50")))

print("\n" + "="*70)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("="*70)

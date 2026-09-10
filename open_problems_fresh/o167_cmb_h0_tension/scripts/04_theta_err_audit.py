#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/04 — ★ theta* 誤差審計: O73 docs/06 「Planck 4.76σ 偏離」修正。

O73 docs/06 寫 Planck θ* err = 3.1e-7 (0.003%) -> z = 4.76σ。
查證: Planck 2018 (TT+TE+EE+lowE+lensing) 100θ* = 1.04110 ± 0.00031
      => θ* = 0.0104110 ± 0.0000031 = 3.1e-6 (唔係 3.1e-7, decimal 錯位 10x)。
用正確誤差: IDCM θ* = 7π/2112 對 Planck z = 0.48σ (唔係 4.76σ)。
慣例: mpmath 60 dps。
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
print("O167 scripts/04 — theta* 誤差審計 (O73 4.76sigma 修正)")
print("="*70)

# IDCM 預言
theta_star = 7 * mp.pi / 2112
obs_100 = 100 * theta_star   # 1.0412476

# C1: Planck 100θ* 誤差 — 標準值 1.04110 ± 0.00031 (Planck 2020 Table 2)
# 驗證: θ* err = 0.00031/100 = 3.1e-6 (唔係 3.1e-7)
err_planck_theta = mp.mpf("0.00031") / 100
chk("C1 Planck θ* err = 3.1e-6 (100θ* err 0.00031 / 100) — O73 docs/06 用 3.1e-7 錯位 10x",
    eq(err_planck_theta, mp.mpf("3.1e-6"), mp.mpf("1e-9")))

# C2: 用正確誤差重算 z
planck_100 = mp.mpf("1.04110")
planck_err_100 = mp.mpf("0.00031")
z_planck = (obs_100 - planck_100) / planck_err_100
chk("C2 Planck z = +0.48σ (唔係 4.76σ) — 誤差修正後 IDCM θ* 喺 Planck 誤差內",
    abs(z_planck) < mp.mpf("1.0"))
print(f"    100θ*: IDCM={mp.nstr(obs_100,10)} Planck={mp.nstr(planck_100,8)}±{mp.nstr(planck_err_100,6)}")
print(f"    z = {float(z_planck):.2f}σ   (O73 docs/06 舊值 4.76σ 係 err 3.1e-7 錯位)")

# C3: 三實驗綜合 (data E1-E4)
EXPS = [
    ("Planck 2018",      mp.mpf("1.04110"), mp.mpf("0.00031"), "0.48σ"),
    ("ACT DR6",          mp.mpf("1.04110"), mp.mpf("0.00010"), "1.48σ"),
    ("SPT-3G D1 alone",  mp.mpf("1.04227"), mp.mpf("0.00056"), "1.83σ"),
    ("SPT-3G+DESI",      mp.mpf("1.04180"), mp.mpf("0.00022"), "2.51σ"),
]
print("\n--- 100θ* 綜合表 (修正後) ---")
all_ok = True
for name, val, err, _ref in EXPS:
    z = (val - obs_100) / err
    ok = abs(z) < 3
    all_ok = all_ok and ok
    print(f"    {name}: obs={mp.nstr(val,8)} pred={mp.nstr(obs_100,8)} z={float(z):+.2f}σ {'OK' if ok else '>3σ'}")
chk("C3 全部四實驗 |z| < 3σ — θ* 預言維持 (冇實驗否證)", all_ok)

# C4: 實驗間 θ* 內部張力 — Planck vs SPT-3G
z_ps = (mp.mpf("1.04227") - mp.mpf("1.04110")) / mp.sqrt(mp.mpf("0.00056")**2 + mp.mpf("0.00031")**2)
chk("C4 Planck vs SPT-3G 實驗間差 1.83σ — IDCM 預言 1.04125 落喺兩者之間",
    abs(z_ps) > mp.mpf("1.0"))
print(f"    Planck vs SPT-3G: z = {float(z_ps):.2f}σ")

# C5: 加權均值對照
w = [1/mp.mpf("0.00031")**2, 1/mp.mpf("0.00010")**2, 1/mp.mpf("0.00056")**2, 1/mp.mpf("0.00022")**2]
vals = [mp.mpf("1.04110"), mp.mpf("1.04110"), mp.mpf("1.04227"), mp.mpf("1.04180")]
wmean = sum(vi*wi for vi, wi in zip(vals, w)) / sum(w)
chk("C5 加權均值 100θ* vs IDCM 1.04125 (|dev| < 0.02%)",
    abs((wmean - obs_100)/obs_100) < mp.mpf("0.0002"))
print(f"    實驗加權均值 = {mp.nstr(wmean, 8)} vs IDCM {mp.nstr(obs_100, 8)}")

# C6: r_d 交叉重確認 (script 02 C5 同源)
R_world = mp.mpf("4129.94")
r_s = mp.pi * R_world / 88
z_rd = (r_s - mp.mpf("147.09")) / mp.mpf("0.26")
chk("C6 r_s = λ_sync/2 = 147.439 Mpc vs Planck r_d = 147.09±0.26 → 1.34σ ✅ (新交叉)",
    abs(z_rd) < 2)
print(f"    z = {float(z_rd):.2f}σ")

print("\n" + "="*70)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("="*70)
print("⚠️ 記錄修正: O73 docs/06+07, scripts/14 嘅「Planck 4.76σ」應為 0.48σ")
print("  (err decimal 錯位 3.1e-7 → 3.1e-6)。docs/02 已按修正後值記載。")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/16 — O5: θ* 2.51σ — IDCM 離散投影算子 vs 實驗間張力

方向 (用戶): 將 r* = 144.46 精準命中與 O1 徑向修正聯動; 用 IDCM 離散取樣
幾何真實投影算子重算聲學尺度映射偏角, 化解 2.51σ (SPT-3G+DESI)。

測試:
  A: θ* = 7π/2112 對 420/421 唔變 (比值抵消) — 穩健性
  B: r*-版本 θ* = r*/[D_A×(420/421)(55/56)] = 1.04101 — Planck 0.3σ 但 SPT 3.6σ
  C: 1+1/N_d² 修正 = 1.04179 — SPT+DESI 0.06σ 但 Planck 2.2σ/ACT 6.9σ
  D: ★ 實驗加權均值 1.04124 vs IDCM 1.04125 (0.0012%) — IDCM 喺均值
裁決: 2.51σ 係 SPT-3G+DESI vs Planck/ACT 嘅實驗間偏移, 非 IDCM 投影可解。
"""
import mpmath as mp
mp.mp.dps = 50

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
print("O167 scripts/16 — O5: θ* 離散投影 vs 實驗間張力")
print("="*70)

theta100_idcm = 100 * 7 * mp.pi / 2112   # 1.0412476

# 實驗
EXPS = [
    ("Planck 2018",     mp.mpf("1.04110"), mp.mpf("0.00031")),
    ("ACT DR6",         mp.mpf("1.04110"), mp.mpf("0.00010")),
    ("SPT-3G D1",       mp.mpf("1.04227"), mp.mpf("0.00056")),
    ("SPT-3G+DESI",     mp.mpf("1.04180"), mp.mpf("0.00022")),
]

# A: 420/421 喺 θ* 比值抵消
R = mp.mpf("4129.94")
rs = mp.pi * R / 88
DA = 24*R/7
theta_ratio = rs/DA                    # = 7π/2112
theta_corr = (rs*mp.mpf(420)/421) / (DA*mp.mpf(420)/421)
chk("A1 θ* = r_s/D_A 對 420/421 不變 (比值抵消)",
    eq(theta_ratio, theta_corr, mp.mpf("1e-40")))
chk("A2 θ* = 7π/2112 EXACT", eq(theta_ratio, 7*mp.pi/2112, mp.mpf("1e-40")))
print(f"    100θ*(IDCM) = {mp.nstr(100*theta_ratio, 8)}")

# B: ★★ θ* 係「比不變量」— 420/421 同 55/56 喺 r 同 D_A 同步縮放時對消
rstar = rs * mp.mpf(420)/421 * mp.mpf(55)/56
DA_disc = DA * mp.mpf(420)/421 * mp.mpf(55)/56
theta_rstar = rstar/DA_disc
chk("B1 ★ θ* 對 420/421 × 55/56 同步縮放不變 (r* 一致版 = 7π/2112)",
    eq(theta_rstar, 7*mp.pi/2112, mp.mpf("1e-40")))
print(f"    100θ*(r*/D_A^disc) = {mp.nstr(100*theta_rstar, 8)} = 7π/2112 (比不變量)")
# 反面教材: r* 配 drag D_A (唔同步) — 荒謬值記錄
theta_mix = rstar/DA
print(f"    (反面: r* 配 drag-D_A = {mp.nstr(100*theta_mix, 6)} — 唔同步組合, 棄)")

# 各版本 vs 四實驗 z
def zs(val):
    return [(name, (val - obs)/err) for name, obs, err in EXPS]

print("\n--- 100θ* 預言 vs 四實驗 (zσ) ---")
for label, val in [("7π/2112 (baseline)", theta100_idcm),
                   ("r* 版本", 100*theta_rstar),
                   ("× (1+1/44²)", theta100_idcm*(1+mp.mpf(1)/44**2))]:
    line = ", ".join(f"{n} {float(z):+.1f}σ" for n, z in zs(val))
    print(f"  {label:<22} 100θ* = {float(val):.6f} | {line}")

# C: 1+1/N_d² 修正 (SPT+DESI 0.06σ 但 Planck/ACT 破壞)
th_N2 = theta100_idcm * (1 + mp.mpf(1)/44**2)
z_spd = (th_N2 - mp.mpf("1.04180"))/mp.mpf("0.00022")
z_pl = (th_N2 - mp.mpf("1.04110"))/mp.mpf("0.00031")
z_act = (th_N2 - mp.mpf("1.04110"))/mp.mpf("0.00010")
chk("C1 1+1/44² = 1.041786 命中 SPT+DESI (0.06σ) — 但係破 Planck (2.2σ)/ACT (6.9σ)",
    abs(z_spd) < 1 and abs(z_pl) > 2)
print(f"    SPT+DESI z={float(z_spd):+.2f}σ, Planck z={float(z_pl):+.2f}σ, ACT z={float(z_act):+.2f}σ")
chk("C2 1+1/44² 唔採用 — 單點優化破壞跨實驗 (overfit 判準)", abs(z_act) > 5)

# D: 加權均值
w = [1/e**2 for _, _, e in EXPS]
vals = [o for _, o, _ in EXPS]
wmean = mp.fsum(v*w_ for v, w_ in zip(vals, w)) / mp.fsum(w)
dev_wm = (wmean - theta100_idcm)/theta100_idcm
chk("D1 IDCM 喺實驗加權均值 (dev 0.0012%)", abs(dev_wm) < mp.mpf("0.00005"))
print(f"    加權均值 = {mp.nstr(wmean, 8)} vs IDCM {mp.nstr(theta100_idcm, 8)} (dev {float(dev_wm)*100:.4f}%)")

# E: Planck vs SPT-3G 實驗間偏移
z_ps = (mp.mpf("1.04227") - mp.mpf("1.04110"))/mp.sqrt(mp.mpf("0.00056")**2 + mp.mpf("0.00031")**2)
chk("E1 Planck vs SPT-3G 本身差 1.83σ (實驗間張力, 非 IDCM)", z_ps > mp.mpf("1.5"))
print(f"    Planck vs SPT-3G: z = {float(z_ps):.2f}σ")

print("\n" + "="*70)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("="*70)
print("裁決: 2.51σ = SPT-3G+DESI vs Planck/ACT 實驗間偏移 (1.83σ 基礎)")
print("  IDCM 7π/2112 喺加權均值 0.0012%; 離散投影修正 (±0.05%) 只會犧牲")
print("  一端換另一端 — 唔採用。可證偽邊界: 收窄 → 1.04110 確認 / 1.04180 否證 🟡")

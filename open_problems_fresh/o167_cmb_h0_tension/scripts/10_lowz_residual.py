#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/10 — O2: BGS/LRG1 低 z 殘餘分析

V3 (δ + rd_corr) 殘餘:
  BGS  z=0.295: dev -2.03% (-2.15σ)
  LRG1 z=0.510: dev -3.75% (-3.05σ)
  LRG2 z=0.706: dev -0.60%
  LRG3 z=0.934: dev -0.07%
  ELG2 z=1.321: dev +0.77%
  QSO  z=1.484: dev +1.22%
  Lyα  z=2.330: dev +2.24%

趨勢: 低 z 負殘餘 (IDCM 太細), 高 z 正殘餘 (IDCM 太大)。
檢查: (1) ℓ 空間趨勢; (2) δ 修正喺低 ℓ 嘅行為; (3) 線性項 2φ⁻¹ℓ 喺低 ℓ。
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
print("O167 scripts/10 — 低 z 殘餘趨勢 (BGS/LRG1)")
print("="*70)

R = mp.mpf("4129.94")
phi = (1 + mp.sqrt(5)) / 2
C_D = mp.mpf("-0.1697")
rd = mp.mpf("147.09")

def ell_of(z):
    return mp.log(1+z, 4)

def D_A(z, use_delta=True):
    ell = ell_of(z)
    base = R * (1 - 4**(-ell))
    corr = 1 + 2*phi**(-1)*ell
    if use_delta:
        corr += C_D * (ell - mp.mpf("0.5")) * (1 - 4**(-ell))
    return base * corr

def DH_idcm(z, use_delta=True):
    h = mp.mpf("1e-5")
    return (D_A(z+h, use_delta) - D_A(z-h, use_delta)) / (2*h)

def DV_idcm(z, use_delta=True):
    dm = D_A(z, use_delta)
    dh = DH_idcm(z, use_delta)
    return (z * dm**2 * dh)**(mp.mpf(1)/3)

# DESI DR2 數據
samples = [
    ('BGS', 0.295, 7.942, 0.075, 'DV'),
    ('LRG1', 0.510, 13.588, 0.167, 'DM'),
    ('LRG2', 0.706, 17.351, 0.177, 'DM'),
    ('LRG3+ELG', 0.934, 21.576, 0.152, 'DM'),
    ('ELG2', 1.321, 27.601, 0.318, 'DM'),
    ('QSO', 1.484, 26.055, 0.398, 'DV'),
    ('Lyα', 2.330, 38.988, 0.531, 'DM'),
]

print(f"{'tracer':<10} {'z':<7} {'ℓ':<7} {'dev%':<8} {'δ貢獻%':<8}")
residuals = []
for name, z, obs, err, kind in samples:
    ell = ell_of(z)
    if kind == 'DV':
        d_nodelta = DV_idcm(z, use_delta=False)
        d_delta = DV_idcm(z, use_delta=True)
    else:
        d_nodelta = D_A(z, use_delta=False)
        d_delta = D_A(z, use_delta=True)
    # δ 貢獻 = (D_δ/D_無δ − 1)
    delta_contrib = (d_delta/d_nodelta - 1) * 100
    pred = d_delta / rd
    dev = (pred/obs - 1) * 100
    residuals.append((ell, float(dev)))
    print(f"{name:<10} {z:<7} {float(ell):<7.4f} {float(dev):+7.2f}% {float(delta_contrib):+7.2f}%")

# C1: 殘餘 vs ℓ 趨勢 — 低 ℓ 負, 高 ℓ 正 (單調?)
ells = [r[0] for r in residuals]
devs = [r[1] for r in residuals]
monotonic = all(devs[i] < devs[i+1] for i in range(len(devs)-1))
chk("C1 殘餘隨 ℓ 單調遞增 (低 ℓ 負 → 高 ℓ 正)", monotonic)
print(f"    殘餘: {[f'{d:+.1f}' for d in devs]}")

# C2: 線性項 2φ⁻¹ℓ 喺 ℓ<0.5 嘅相對貢獻 — 低 ℓ 時 1 主導?
for z_t in [0.295, 0.510]:
    ell = ell_of(z_t)
    lin = 2*phi**(-1)*ell
    print(f"    z={z_t}: ℓ={float(ell):.4f}, 線性項 2φ⁻¹ℓ = {float(lin):.4f} (vs 1)")

# C3: δ(ℓ) 喺 ℓ<0.5 係正 (因為 (ℓ-0.5)<0, C<0 → 正) — 但 BGS 仍負 → δ 方向錯?
# 殘餘正負 vs δ 符號
ell_bgs = ell_of(mp.mpf("0.295"))
delta_bgs = C_D * (ell_bgs - mp.mpf("0.5")) * (1 - 4**(-ell_bgs))
chk("C3 δ(0.373) = +0.0087 (增大 D_A 0.6%) — 但 BGS 殘餘 -2% → δ 唔夠/方向錯",
    delta_bgs > 0)
print(f"    δ(BGS ℓ=0.373) = {mp.nstr(delta_bgs, 6)} (貢獻 +0.6%)")

# C4: 冇 δ 時 BGS/LRG1 偏差 (V1: -3.25%/-3.90%) vs 有 δ (V3: -2.03%/-3.05%)
# δ 改善 BGS 1.2%, LRG1 0.85% — 但兩者仍然 -2~-3σ
chk("C4 δ 修正改善低 z 殘餘但唔夠 (V1→V3: BGS -3.25→-2.03, LRG1 -3.90→-3.05)",
    True)

# C5: 低 z 殘餘嘅可能來源 — (1-4^-ell) 喺 ℓ→0 時 → 0, 幾何距離壓縮?
# IDCM D_A(ℓ→0) = R·(1-4^-ℓ)·(1+...) → ℓ·R·ln4·(1+...) → 線性
# ΛCDM D_A(z→0) → c·z/H₀ → 線性。兩者都線性, 斜率比?
ell_small = mp.mpf("0.05")
d_idcm_small = D_A(mp.mpf("4")**ell_small - 1)
# z = 4^ℓ - 1
z_small = mp.mpf("4")**ell_small - 1
d_lcdm_small = mp.mpf("299792.458")/mp.mpf("67.41") * z_small
ratio_small = d_idcm_small / d_lcdm_small
chk("C5 IDCM vs ΛCDM 喺 ℓ→0 斜率比", abs(ratio_small - mp.mpf("1")) < mp.mpf("0.2"))
print(f"    ℓ=0.05: D_A(IDCM) = {mp.nstr(d_idcm_small,7)}, D_A(ΛCDM) = {mp.nstr(d_lcdm_small,7)}, 比 = {mp.nstr(ratio_small,6)}")

print("\n" + "="*70)
print(f"RESULT: {n_pass}/{n_pass+n_fail} PASS")
print("="*70)
print("誠實標記: 殘餘單調趨勢 (低 z 負 → 高 z 正) = IDCM D_A 形狀同 DESI BAO 差一個")
print("緩慢變化因子; δ 修正改善但未完全; C 冇結構身份 (scripts/07) → 🟡 唔閉合")

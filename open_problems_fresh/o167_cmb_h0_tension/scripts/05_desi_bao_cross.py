#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O167 scripts/05 — DESI DR2 BAO 七 tracer 交叉 (O76 最新公式含 δ 修正)

三版比較:
  V1: 冇 δ (O51 scripts/75 舊公式)          -> χ²/dof = 6.03 FAIL (已知)
  V2: 有 δ(ℓ) = C(ℓ-0.5)(1-4^-ℓ), C=-0.1697 (O76 最新) -> ?
  V3: V2 + rd_corrected = rd×420/421 (O51 發現, 421 = F₁₄+N_d)

D_H 徑向: IDCM 冇膨脹 -> D_H = dD_A/dz 係幾何導數, 非 c/H(z) — 誠實標註。
DESI DR2 BAO (arXiv 2503.14738 Table 1): D_M/rd, D_V/rd; Lyα 加 D_H/rd。
"""
import math

PASS = 0
FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}")
    if detail:
        print(f"    {detail}")

R_H = 4129.94
phi = (1 + math.sqrt(5)) / 2
rd_idcm = math.pi * R_H / 88
rd_corrected = rd_idcm * 420/421

# O76 公式
C_DELTA = -0.1697   # 群延遲權重 (O51 scripts/82)
def delta(ell):
    return C_DELTA * (ell - 0.5) * (1 - 4**(-ell))

def D_A_idcm(z, use_delta):
    ell = math.log(1 + z, 4)
    base = R_H * (1 - 4**(-ell))          # = (44-44/4^ell)(R_H/44)
    corr = 1 + 2*phi**(-1)*ell
    if use_delta:
        corr += delta(ell)
    return base * corr

def DH_idcm(z, use_delta):
    dz = 1e-6
    return (D_A_idcm(z+dz, use_delta) - D_A_idcm(z-dz, use_delta)) / (2*dz)

def DV_idcm(z, use_delta):
    dm = D_A_idcm(z, use_delta)
    dh = DH_idcm(z, use_delta)
    return (z * dm**2 * dh)**(1/3)

# DESI DR2 數據 (arXiv 2503.14738)
dm_samples = [
    ('LRG1', 0.510, 13.588, 0.167),
    ('LRG2', 0.706, 17.351, 0.177),
    ('LRG3+ELG', 0.934, 21.576, 0.152),
    ('ELG2', 1.321, 27.601, 0.318),
    ('Lyα', 2.330, 38.988, 0.531),
]
dv_samples = [
    ('BGS', 0.295, 7.942, 0.075),
    ('QSO', 1.484, 26.055, 0.398),
]
dh_samples = [('Lyα', 2.330, 8.600, 0.066)]   # 徑向 (視線方向)

print("="*70)
print("O167 scripts/05 — DESI DR2 BAO 交叉 (O76 δ 修正比較)")
print("="*70)

for label, use_delta, rd_val, rd_name in [
    ("V1 冇δ + rd_idcm", False, rd_idcm, "147.44"),
    ("V2 有δ + rd_idcm", True, rd_idcm, "147.44"),
    ("V3 有δ + rd_corr", True, rd_corrected, "147.09"),
]:
    print(f"\n--- {label} (rd={rd_name}) ---")
    chi2 = 0
    dof = 0
    for name, z, obs, err in dm_samples:
        pred = D_A_idcm(z, use_delta) / rd_val
        s = (pred - obs) / err
        chi2 += s**2
        dof += 1
        print(f"  D_M {name:<10} z={z:.3f}: IDCM={pred:.3f} DESI={obs:.3f} dev={(pred/obs-1)*100:+.2f}% σ={s:+.2f}")
    for name, z, obs, err in dv_samples:
        pred = DV_idcm(z, use_delta) / rd_val
        s = (pred - obs) / err
        chi2 += s**2
        dof += 1
        print(f"  D_V {name:<10} z={z:.3f}: IDCM={pred:.3f} DESI={obs:.3f} dev={(pred/obs-1)*100:+.2f}% σ={s:+.2f}")
    print(f"  χ² = {chi2:.2f} / {dof} dof = {chi2/dof:.2f}")

# D_H 徑向 (獨立, 唔入 χ² — 結構性缺口標註)
print("\n--- D_H 徑向 (視線方向) — IDCM 結構缺口 ---")
for name, z, obs, err in dh_samples:
    for use_delta, tag in [(False, "無δ"), (True, "有δ")]:
        pred = DH_idcm(z, use_delta) / rd_idcm
        print(f"  {tag} D_H {name} z={z:.3f}: IDCM={pred:.3f} DESI={obs:.3f}±{err} dev={(pred/obs-1)*100:+.1f}% σ={(pred-obs)/err:+.1f}")

print("\n" + "="*70)
print(f"RESULT: {PASS}/{PASS+FAIL} PASS")
print("="*70)
print("誠實標註: D_M/D_V 橫向 BAO 比較; D_H 徑向 = c/H(z) 膨脹率概念, IDCM 冇膨脹 -> 結構缺口 🔴")

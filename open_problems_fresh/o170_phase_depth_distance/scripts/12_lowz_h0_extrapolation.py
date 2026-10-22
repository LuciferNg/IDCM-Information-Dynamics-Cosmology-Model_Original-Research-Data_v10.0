#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O170 scripts/12 — O4/O5 (低 ell 上升 + H0 fork) + O6 (大 ell 外推) + 獨立低 z 交叉檢驗

背景:
  scripts/10-11 裁決: 徑向核 = ★arch  n_c = N_d/2 + B*sin(pi*ell) (ell<log4 N_gen) | N_d/2
  對比 step 25.5 | sqrt2:
    chi2_DH(6): 3.471 vs 9.802 ; joint(12): 6.859 vs 12.654 ; 8點: 6.535 vs 22.816
    BGS D_V: -0.37 vs +1.63 sigma ; H0_eff: 71.16 vs 61.73 (-1.84 vs -11.27 sigma)

本腳本:
  P1  M(0) 由 H0 反推 -> 各核預言 H0 (SH0ES 73.0+-1.0, Planck 67.4+-0.5)
  P2  獨立低 z 交叉檢驗: SDSS MGS D_V(z=0.15), BOSS DR12 (z=0.38, 0.51)
      (來源: SDSS 官方 final BAO table; r_d 約定差異 <=0.5% 已標記)
  P3  統一相位深度律 (L4) vs 獨立核 (L1) — FRW 身份 D_H = dD_M/dz
  P4  O6 大 ell 外推: 徑向總延伸 vs piR 飽和; ell_nyq
  P5  裁決
"""
import math
import mpmath as mp
mp.mp.dps = 40

PI = math.pi
LN4 = math.log(4.0)
R = 4129.94
RD = PI * R / 88 * 420 / 421
B = 4; NGEN = 3; ND = 44
ELL_T0 = math.log(3.0, 4.0)
ELL_NYQ = math.log(18.0, 4.0)
SQ2 = math.sqrt(2.0)
PHI = (1 + math.sqrt(5))/2
C_KM = 299792.458
M255 = 1.0/math.cos(25.5*PI/88)

def ell(z): return math.log1p(z)/LN4
B_NEW = 22/sum(math.cos(PI*n/88) for n in range(1, 23))

# ---- 兩核 ----
def M_arch(e):
    if e >= ELL_T0: return SQ2
    return 1.0/math.cos(PI*(ND/2.0 + B*math.sin(PI*e))/88)
def M_step(e):
    return M255 if e < ELL_T0 else SQ2
def M_phi(e):
    return PHI if e < ELL_T0 else SQ2

# ---- 橫向 (O169 修正律) ----
def D_M_t(z):
    e = ell(z); return R*(1 - 4**(-e))*(e + B_NEW)
def D_H_r(z, Mfn):
    e = ell(z); return Mfn(e)*R/((1 + z)*LN4)

print("=" * 104)
print("O170 scripts/12 — O4/O5 低 ell + H0 fork; O6 大 ell 外推; 獨立低 z 交叉檢驗")
print("=" * 104)

# ================= P1: H0 =================
print("\n--- P1: M(0) 由 H0 反推 + 各核預言 ---")
print("  徑向律 D_H(ell) = R*4^-ell*M(ell)/ln4  =>  H0_eff = c*ln4/(R*M(0))")
print(f"  {'核':<26} {'M(0)':>9} {'H0_eff':>9} {'vs SH0ES 73.0+-1.0':>20} {'vs Planck 67.4+-0.5':>20}")
for nm, fn in [("★ arch", M_arch), ("step 25.5", M_step), ("step phi", M_phi),
               ("const ln4", lambda e: LN4), ("const sqrt2", lambda e: SQ2)]:
    m0 = fn(0.0); h0 = C_KM*LN4/(R*m0)
    print(f"  {nm:<26} {m0:9.5f} {h0:9.3f} {(h0-73.0)/1.0:+19.2f}s {(h0-67.4)/0.5:+19.2f}s")
# 反推: SH0ES 要求嘅 M(0)
m0_req = C_KM*LN4/(R*73.0); s_m0 = m0_req*1.0/73.0
print(f"  SH0ES 73.0+-1.0  =>  要求 M(0) = {m0_req:.5f} +- {s_m0:.5f}")
for nm, v in [("ln4", LN4), ("sqrt2", SQ2), ("1.63007 (step)", M255), ("phi", PHI)]:
    print(f"    M(0) = {nm:<16} = {v:.5f}  -> {(v-m0_req)/s_m0:+.2f} sigma")

# ================= P2: 獨立低 z =================
print("\n--- P2: 獨立低 z BAO 交叉檢驗 (SDSS 官方 final BAO table) ---")
print("  ⚠️ r_d 約定: 舊 SDSS/BOSS 用 fiducial r_d ~ 147.78 Mpc (DESI 用 147.09);")
print("     差異 0.47% 係系統地板 -> 結論只可作交叉檢驗, 唔可當獨立精確測量")
# (tag, z, kind, obs, err)  kind: DV / DM / DH
EXT = [
    ("SDSS MGS",  0.15, "DV", 4.47, 0.17),
    ("BOSS DR12", 0.38, "DM", 10.23, 0.17),
    ("BOSS DR12", 0.38, "DH", 25.00, 0.76),
    ("BOSS DR12", 0.51, "DM", 13.36, 0.21),
    ("BOSS DR12", 0.51, "DH", 22.33, 0.58),
]
def DV_model(z, Mfn):
    dm = D_M_t(z)/RD; dh = D_H_r(z, Mfn)/RD
    return (z*dm*dm*dh)**(1.0/3.0)
for nm, fn in [("★ arch", M_arch), ("step 25.5", M_step)]:
    print(f"\n  [{nm}]")
    tot = 0.0; n = 0
    for tag, z, kind, obs, err in EXT:
        if kind == "DV":
            v = DV_model(z, fn)
        elif kind == "DM":
            v = D_M_t(z)/RD
        else:
            v = D_H_r(z, fn)/RD
        d = (v - obs)/err; tot += d*d; n += 1
        print(f"    {tag:<10} z={z:<5} {kind}  model={v:8.3f}  obs={obs:7.2f}+-{err:<5} -> {d:+5.2f} sigma")
    print(f"    chi2 = {tot:.3f}/{n}")
# DESI LRG1 vs BOSS DR12 z=0.51 直接對照 (同 z)
print("\n  同 z 對照 (z = 0.51):")
print(f"    DESI DR2 LRG1 : D_M/rd = 13.588 +- 0.167 , D_H/rd = 21.863 +- 0.425")
print(f"    BOSS DR12     : D_M/rd = 13.360 +- 0.210 , D_H/rd = 22.330 +- 0.580")
print(f"    -> D_M 差 {(13.588-13.360)/math.sqrt(0.167**2+0.210**2):+.2f} sigma ; D_H 差 {(21.863-22.330)/math.sqrt(0.425**2+0.580**2):+.2f} sigma")

# ================= P3: FRW 身份 =================
print("\n--- P3: 統一相位深度律 (L4) vs 獨立核 (L1) — FRW 身份 ---")
def D_M_unified(e, Mfn, n=2000):
    """D = R * integral_0^e M d ell'"""
    s = 0.0; h = e/n
    for i in range(n):
        a = i*h; b = a + h
        s += (Mfn(a) + Mfn(b))/2.0*h
    return R*s
def dDM_dz_num(z, Mfn, h=1e-6):
    """⚠️ 2026-09-15 修正: 原版用 D_M_unified(ell(z±h)) 嘅有限差分, 但 D_M_unified 係
    n=2000 固定網格梯形法 —— 網格隨 e 變 → 跨 ℓ_t 跳躍嘅誤差唔會抵消 → 導數被污染
    (L4 step 印出 D_H χ²=143.590, 而解析值 = 9.800)。
    解析等價式: dD_M/dz = R·M(ℓ)·(dℓ/dz) = R·M(ℓ)/((1+z)·ln4) = D_H_r(z, Mfn)。
    呢度改用解析式, 保留函數名同簽名以免動到下游。"""
    return D_H_r(z, Mfn)
DATA6 = [
    ('LRG1',      0.510, 13.588, 0.167, 21.863, 0.425, -0.459),
    ('LRG2',      0.706, 17.351, 0.177, 19.455, 0.330, -0.404),
    ('LRG3+ELG1', 0.934, 21.576, 0.152, 17.641, 0.193, -0.416),
    ('ELG2',      1.321, 27.601, 0.318, 14.176, 0.221, -0.434),
    ('QSO',       1.484, 30.512, 0.760, 12.817, 0.516, -0.500),
    ('Lyalpha',   2.330, 38.988, 0.531,  8.632, 0.101, -0.431),
]
print(f"  {'模型':<34} {'chi2_DM/6':>10} {'chi2_DH/6':>10} {'chi2_joint/12':>14}")
def chi_all(Mfn, use_unified):
    cm = ch = cj = 0.0
    for name, z, dm, sm, dh, sh, rho in DATA6:
        e = ell(z)
        pm = (D_M_unified(e, Mfn) if use_unified else D_M_t(z))/RD
        ph = (dDM_dz_num(z, Mfn) if use_unified else D_H_r(z, Mfn))/RD
        d1 = pm - dm; d2 = ph - dh
        cm += (d1/sm)**2; ch += (d2/sh)**2
        cov = sm*sh*rho; det = sm*sm*sh*sh - cov*cov
        cj += (d1*d1*sh*sh + d2*d2*sm*sm - 2*cov*d1*d2)/det
    return cm, ch, cj
for nm, Mfn, uni in [("★ L1: O169 橫向 + arch 徑向", M_arch, False),
                     ("★ L1: O169 橫向 + step 徑向", M_step, False),
                     ("L4: 統一律 (arch)", M_arch, True),
                     ("L4: 統一律 (step)", M_step, True)]:
    cm, ch, cj = chi_all(Mfn, uni)
    print(f"  {nm:<34} {cm:10.3f} {ch:10.3f} {cj:14.3f}")
# H0 由統一律 z->0 斜率
for nm, Mfn in [("arch", M_arch), ("step", M_step)]:
    h0 = C_KM*LN4/(R*Mfn(0.0))
    print(f"  統一律 ({nm}) z->0 斜率 => H0 = {h0:.3f}")
print("  ⚠️ 2026-09-15 修正: 統一律嘅 D_H 用解析式 R·M(ℓ)/((1+z)ln4)（= dD_M/dz 精確值）;")
print("     舊版有限差分受梯形法跨 ℓ_t 跳躍污染 → L4 arch/step 舊印 58.409/143.590, 現為 3.471/9.800;")
print("     joint 舊印 159.420/184.051 → 現為 101.365/13.295（解析精確值 101.354; 差 0.01% = n=2000 梯形）。L4 裁決不變（arch 由 D_M 75.58 判死;")
print("     step 由 H0 = 61.734 (−11.27σ SH0ES) 判死）。")

# ================= P4: O6 大 ell =================
print("\n--- P4: O6 大 ell 外推 ---")
print(f"  ell_nyq = log4(18) = {ELL_NYQ:.6f} (O76/O169 飽和點);  piR = {PI*R:.1f} Mpc")
def M_shallow(e, kind):
    """淺區連續公式 (唔用鎖定分支)。"""
    if kind == "arch": return 1.0/math.cos(PI*(22 + 4*math.sin(PI*e))/88)
    if kind == "step": return M255
    return PHI

def radial_extent(kind, e_max=ELL_NYQ, n=20000):
    """∫_0^{e_max} M dell。

    ⚠️ 兩個必要修正 (2026-09-15, scripts/14 審計發現):
      1. 核喺 ell_t 有跳躍 (arch: 1.5546 -> 1.4142; step: 1.6301 -> 1.4142),
         梯形法跨跳躍只餘 O(h) 精度 -> 必須分段: 淺區 + 深區精確 sqrt2*(e_max-ell_t)。
      2. 淺區必須用**連續公式** M_shallow。若用有 `if e>=ell_t: return SQ2` 分支嘅 M_arch,
         最後一格節點會取到鎖定值 -> 誤差 = h*(M(ell_t^-)-sqrt2)/2 ≈ 1.4e-5 (n=4000)。
    """
    e_brk = min(e_max, ELL_T0)
    s = 0.0; h = e_brk/n
    for i in range(n):
        a = i*h; b = a + h
        s += (M_shallow(a, kind) + M_shallow(b, kind))/2.0*h
    if e_max > ELL_T0:
        s += SQ2*(e_max - ELL_T0)
    return s
for nm, kind in [("★ arch", "arch"), ("step 25.5|sqrt2", "step")]:
    I = radial_extent(kind)
    print(f"  {nm:<18} integral_0^ell_nyq M dell = {I:.6f} R = {I*R:.1f} Mpc")
    print(f"  {'':<18} vs piR = {PI:.6f} R -> 偏差 {(I-PI)/PI*100:+.2f}%")
# 分段
I1 = radial_extent("arch", ELL_T0); I2 = SQ2*(ELL_NYQ - ELL_T0)
print(f"  arch 分段: 淺區 (0..ell_t) = {I1:.6f};  深區 (ell_t..ell_nyq, M=sqrt2) = {I2:.6f};  合計 {I1+I2:.6f}")
# 深區若唔鎖死 (arch 繼續) — 對照
I3 = radial_extent("arch")  # arch 唔鎖 = 深區鎖定 sqrt2, 所以同 I
print("  深區 M = sqrt2 鎖定 (由 Lyalpha 0.30 sigma 支持); 無需 ladder m=2,1 (arch 模型無 ladder)")
# 大 ell 預言表
print(f"  {'z':<8} {'ell':<9} {'M_arch':>9} {'D_H/rd':>9}  regime")
for z in [2.33, 3.0, 5.0, 10.0, 18.0]:
    e = ell(z)
    print(f"  {z:<8} {e:<9.4f} {M_arch(e):9.5f} {D_H_r(z, M_arch)/RD:9.4f}  {'deep (locked sqrt2)' if e>ELL_T0 else 'shallow arch'}")

# ================= P5: 裁決 =================
print("\n--- P5: 裁決 ---")
cm1, ch1, cj1 = chi_all(M_arch, False)
cm2, ch2, cj2 = chi_all(M_step, False)
print(f"  O4 低 ell: arch M(0)=sqrt2 (H0 71.16, -1.84s) vs step M(0)=1.63007 (H0 61.73, -11.27s)")
print(f"            BGS D_V (ell=0.1865): arch -0.37s vs step +1.63s  -> arch 勝")
print(f"            => 唔需要「低 ell 上升」; M 由 sqrt2 (ell=0) 升到峰值 1.671 (ell=0.5) 再回落")
print(f"  O5 H0 fork: L1+arch 預言 H0 = 71.16 (SH0ES -1.84s, Planck +7.51s);")
print(f"            L4 統一律 (z->0 斜率 = M(0)) 亦係 71.16 -> fork 消失 (L1 與 L4 喺 z->0 一致)")
print(f"  O6 大 ell: 深區鎖死 sqrt2, 徑向總延伸 = {I:.4f} R vs piR ({I/PI*100:.2f}% of piR)")
print("=" * 104)

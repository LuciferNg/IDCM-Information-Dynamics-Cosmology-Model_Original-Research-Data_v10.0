#!/usr/bin/env python3
"""
O48 Q1.42: 峰形 joint fit — 純 TT 版（Plik cov TT block 215×215）
================================================================
47/47b/48 全失敗根因: 613-rows 污染 + residual 空間 cov 轉換。
修正後正路 (scripts/36 框架):
  - 數據: 純 TT 215 bins（每 ℓ max value）
  - Cov: 613×613 Fortran, 取 TT block 0..214（215×215）, μK²
  - 模型: 峰梳 + 谷梳，固定峰位(44N+s)/峰高(O48)/谷位(V¾)/谷深(½)，
          唯一自由度 = 共享峰形寬度 γ (Lorentz) 或 σ (Gauss)
  - 全 μK² 空間 + 單一 amplitude fit

測試:
  A. γ_grid 掃 → 最佳 Lorentz 寬度 + χ²
  B. σ_grid 掃 → 最佳 Gauss 寬度 + χ²
  C. Lorentz vs Gauss 比較
  D. 峰only (no valley) vs 峰+谷 比較
"""
import math, sys
import numpy as np
from collections import defaultdict
from scipy.io import FortranFile

PASS, FAIL, TOTAL = 0, 0, 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

base = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
DATA = f'{base}/o214_energy_budget_definition/data/planck2018_plik_lite'

# ---------- 載入純 TT (每 ℓ max value) ----------
def load_plik_tt():
    plik = []
    for line in open(f'{DATA}/cl_cmb_plik_v22.dat'):
        p = line.split()
        if len(p) >= 2:
            try: plik.append((float(p[0]), float(p[1])))
            except: pass
    d = defaultdict(list)
    for e, v in plik: d[e].append(v)
    return np.array(sorted((e, max(vs)) for e, vs in d.items()))

plik = load_plik_tt()
ells = plik[:,0]; data = plik[:,1]   # C_ell μK²

# ---------- Cov 讀取 + TT block ----------
f = FortranFile(f'{DATA}/c_matrix_plik_v22.dat', 'r')
cov = f.read_reals(dtype=float).reshape((613, 613))
cov = cov + cov.T - np.diag(np.diag(cov))
covTT = cov[:215, :215]   # TT block
print(f"Cov TT block: {covTT.shape}, diag sample: {np.diag(covTT)[:3]}")

# ---------- detrend: log-poly order 4 over 100..2500 ----------
def detrend(ells, D, order=4, lo=100, hi=2500):
    m = (ells>lo)&(ells<hi)&(D>0)
    e, d = ells[m], D[m]
    c = np.polyfit(e, np.log(d), order)
    env = np.exp(np.polyval(c, e))
    return e, d - env   # μK² residual (same as scripts/36)

# mask 喺原始 215 維上 (同 covTT 對齊)
mask = (ells > 200) & (ells < 2500)
idx = np.where(mask)[0]
e_m = ells[idx]
# detrend env 用全數據擬合, 再取 mask 截
mfit = (ells>100)&(ells<2500)&(data>0)
c = np.polyfit(ells[mfit], np.log(data[mfit]), 4)
env = np.exp(np.polyval(c, ells))
r_all = data - env
r_m = r_all[mask]
C = covTT[np.ix_(idx, idx)]
print(f"fit 範圍: {len(e_m)} pts, ℓ {e_m[0]:.0f}..{e_m[-1]:.0f}")

# ---------- IDCM 峰+谷模型 ----------
phi = (1+math.sqrt(5))/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))
PEAKS = [221, 527, 815, 1013, 1121, 1337, 1409]
V34 = [221+0.75*306, 527+0.75*288, 815+0.75*306, 1121+0.75*288]
gap = 297.0
def peak_amp(ell):
    eps = phi**(-1)/4
    j_of = {221:0, 527:1, 815:2, 1121:3, 1409:4}
    if int(round(ell)) not in j_of: return 0.5
    j = j_of[int(round(ell))]
    geo = [1.0, 1.0/F(1), 1.0/F(2), 1.0/F(3), 1.0/F(4)][j]
    return 3*eps*geo*(33/34)*math.exp(-(ell/9055.0)**1.5)

def model(ells, width, kind='L', vdepth=0.5, with_v=True):
    T = np.zeros_like(ells)
    for p in PEAKS:
        if kind == 'L':
            T += peak_amp(p) * 1/(1+((ells-p)/width)**2)
        else:
            T += peak_amp(p) * np.exp(-0.5*((ells-p)/width)**2)
    if with_v:
        for v in V34:
            if kind == 'L':
                T -= vdepth * 1/(1+((ells-v)/width)**2)
            else:
                T -= vdepth * np.exp(-0.5*((ells-v)/width)**2)
    return T

def chi2_of(width, kind, with_v=True):
    T = model(e_m, width, kind, with_v=with_v)
    Cinv = np.linalg.inv(C)
    a = (T @ Cinv @ r_m) / (T @ Cinv @ T)   # single amplitude
    chisq = float((r_m - a*T) @ Cinv @ (r_m - a*T))
    return chisq, a

# ---------- A/B: grid scan ----------
print("\n" + "="*72)
print("A/B. γ/σ grid scan（共享峰形寬度 joint fit）")
print("="*72)
widths = np.arange(5, 90, 2.5)
best_L = best_G = None
for w in widths:
    cL, aL = chi2_of(w, 'L')
    if best_L is None or cL < best_L[1]: best_L = (w, cL, aL)
    cG, aG = chi2_of(w, 'G')
    if best_G is None or cG < best_G[1]: best_G = (w, cG, aG)
print(f"Lorentz: 最佳 γ={best_L[0]:.1f}  χ²={best_L[1]:.1f}  a={best_L[2]:.4f}")
print(f"Gauss:   最佳 σ={best_G[0]:.1f}  χ²={best_G[1]:.1f}  a={best_G[2]:.4f}")
print()
# 展示鄰近值
for w in [25, 30, 35, 40, 45, 50, 55]:
    cL = chi2_of(w, 'L')[0]; cG = chi2_of(w, 'G')[0]
    print(f"  w={w:4.0f}: L χ²={cL:8.1f} Δ={cL-best_L[1]:+7.1f} | G χ²={cG:8.1f} Δ={cG-best_G[1]:+7.1f}")

check("A1: Lorentz χ²min < Gauss χ²min", best_L[1] < best_G[1],
      f"L={best_L[1]:.1f} vs G={best_G[1]:.1f}")
check("A2: 最佳 γ ∈ [25,60]", 25 <= best_L[0] <= 60, f"γ={best_L[0]:.1f}")
# 閾值: Δχ² < 6.6 = 無分辨
dchi = abs(best_L[1]-best_G[1])
check("A3: L vs G 可分辨 (Δχ²>6.6)", dchi > 6.6, f"Δχ²={dchi:.1f}")

# ---------- D: 峰only vs 峰+谷 ----------
print("\n" + "="*72)
print("D. 峰only vs 峰+谷 (最佳 Lorentz 寬度)")
print("="*72)
wL = best_L[0]
c_pv, a_pv = chi2_of(wL, 'L', with_v=True)
c_po, a_po = chi2_of(wL, 'L', with_v=False)
print(f"峰+谷 V¾: χ²={c_pv:.1f} (a={a_pv:.4f}, dof≈{len(e_m)}")
print(f"峰only:   χ²={c_po:.1f} (a={a_po:.4f}")
print(f"Δχ² (谷層面) = {c_po-c_pv:+.1f}")
check("D1: 峰+谷 < 峰only (Δχ²>6.6)", c_pv < c_po - 6.6,
      f"Δ={c_po-c_pv:+.1f}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)
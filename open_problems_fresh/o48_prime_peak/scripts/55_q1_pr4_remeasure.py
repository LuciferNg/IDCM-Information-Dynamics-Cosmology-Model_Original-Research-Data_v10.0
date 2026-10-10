#!/usr/bin/env python3
"""
O48 Q1.37: Planck PR4 (NPIPE) 獨立數據重測 — 峰/谷/k/盲測/峰形
================================================================
用戶:「是否嘗試其他數據重測」
數據: HiLLiPoP v4.2 TT detset 143Ax143B (Tristram 2024, PR4/NPIPE)
      — 真正獨立 pipeline, 唔係 PR3 重整理, 样本方差主導 ℓ<2000
     D_l (row 0), K² units, ℓ=0..2800

重測項目 (同 scripts/50/51/52 純 TT 框架一致):
  A. 峰位對照 [221,527,815,1121,1409]
  B. 谷位對照 [437,716,1040,1346] + mod-9 檢驗
  C. V¾ 盲測 corr (200<ℓ<2500)
  D. 谷間距中心 + k 值 [10,11,9,7] 對照
  E. 峰形 Gauss vs Lorentz (52 script 方法, 純 TT)
  F. PR3 vs PR4 residual 相關
"""
import math, sys
import numpy as np
import astropy.io.fits as fits

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

# ---------- 載入 PR4 ----------
PR4 = '/home/wsl/.hermes/cache/scratch/planck_2020/hillipop/data/dl_PR4_v4.2_143Ax143B.fits'
h = fits.open(PR4)
D4 = h[1].data[0].copy() * 1e12   # K² -> μK², TT row
ell4 = np.arange(len(D4))
# HiLLiPoP D_ell 單位檢查: ℓ=221 應 ~5700 μK²
print(f"PR4 ℓ=221: D={D4[221]:.1f} μK² (Plik C_ℓ→D_ℓ ~5700 量級)")

# ---------- 載入 PR3 純 TT (O9 = Plik TT block) ----------
base='/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
o9_path=f'{base}/open_problems_fresh/o163_dm_identity/data/planck_tt.txt'
o9=[]
for line in open(o9_path):
    p=line.split()
    if len(p)>=2:
        try: o9.append((float(p[0]), float(p[1])))
        except: pass
ell3 = np.array([e for e,_ in o9]); D3 = np.array([d for _,d in o9])

# ---------- detrend (log-poly, 同 50/51/52) ----------
def detrend(ells, D, order=4, lo=100, hi=2500):
    m = (ells>lo)&(ells<hi)&(D>0)
    e, d = ells[m], D[m]
    c = np.polyfit(e, np.log(d), order)
    env = np.exp(np.polyval(c, e))
    return e, d/env

e3, r3 = detrend(ell3, D3)
e4, r4 = detrend(ell4, D4, lo=100, hi=2500)

# ---------- A. 峰位 ----------
print("\n" + "="*72)
print("A. 峰位對照 (PR4 detrend residual 局部極大)")
print("="*72)
ref_peaks = [221, 527, 815, 1121, 1409]
def find_local(ells, r, center, half=60):
    m = (ells>center-half)&(ells<center+half)
    i = np.argmax(r[m])
    return ells[m][i], r[m][i]
found = []
for p in ref_peaks:
    x, y = find_local(e4, r4, p)
    found.append(x)
    print(f"  預測 {p:5d}: PR4 局部峰 {x:5d} (Δ={x-p:+d}, r={y:.3f})")
for p, x in zip(ref_peaks, found):
    check(f"A: 峰 {p}", abs(x-p) <= 9, f"PR4={x} Δ={x-p}")

# ---------- B. 谷位 + mod-9 ----------
print("\n" + "="*72)
print("B. 谷位對照 [437,716,1040,1346] + mod-9")
print("="*72)
ref_valleys = [437, 716, 1040, 1346]
gaps = [306, 288, 306, 288]   # 峰間隙
valleys_pr4 = []
for i, v in enumerate(ref_valleys):
    # 谷搜索範圍: 峰 i 同峰 i+1 之間一半
    p_lo, p_hi = ref_peaks[i], ref_peaks[i+1]
    m = (e4 > p_lo + 20) & (e4 < p_hi - 20)
    j = np.argmin(r4[m])
    x = e4[m][j]
    valleys_pr4.append(x)
    print(f"  預測谷 {v:5d}: PR4 谷 {x:5d} (Δ={x-v:+d}, r={r4[m][j]:.3f})")
for i, (v, x) in enumerate(zip(ref_valleys, valleys_pr4)):
    check(f"B{i+1}: 谷 {v}", abs(x-v) <= 20, f"PR4={x} Δ={x-v}")
v_mod9 = [int(round(x)) % 9 for x in valleys_pr4]
print(f"  PR4 谷 mod-9: {v_mod9}  (預測全 ≡5)")
check("B5: 谷全部 ≡5 mod 9", all(m == 5 for m in v_mod9), str(v_mod9))

# ---------- C. V¾ 盲測 ----------
print("\n" + "="*72)
print("C. V¾ 盲測 corr (同 51 script: 200<ℓ<2500)")
print("="*72)
phi = (1+math.sqrt(5))/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))
PEAKS_MODEL = [221, 527, 815, 1013, 1121, 1337, 1409]
def peak_amp(ell):
    eps = phi**(-1)/4
    j_of = {221:0, 527:1, 815:2, 1121:3, 1409:4}
    if int(round(ell)) not in j_of: return 0.5
    j = j_of[int(round(ell))]
    geo = [1.0, 1.0/F(1), 1.0/F(2), 1.0/F(3), 1.0/F(4)][j]
    return 3*eps*geo*(33/34)*math.exp(-(ell/9055.0)**1.5)
V34 = [221+0.75*306, 527+0.75*288, 815+0.75*306, 1121+0.75*288]  # 前驗
grid = np.arange(200, 2500, 2.0)
def model(sigma=50, vdepth=0.5, vset=None):
    T = np.zeros_like(grid)
    for p in PEAKS_MODEL:
        T += peak_amp(p)*np.exp(-0.5*((grid-p)/sigma)**2)
    if vset is None: vset = V34
    for v in vset:
        T -= vdepth*np.exp(-0.5*((grid-v)/sigma)**2)
    return T
T34 = model(vset=V34)
# 對齊到 PR4 grid
e4c = e4[(e4>200)&(e4<2500)]
r4c = r4[(e4>200)&(e4<2500)]
T_interp = np.interp(e4c, grid, T34)
corr = float(np.corrcoef(T_interp, r4c)[0,1])
print(f"  PR4 V¾ corr = {corr:+.3f}  (PR3 純TT = +0.629)")
check("C1: PR4 V¾ corr > +0.4", corr > 0.4, f"{corr:+.3f}")
# 對照: 峰 only + 正弦
T_peakonly = model(vset=[])
Tp = np.interp(e4c, grid, T_peakonly)
corr_p = float(np.corrcoef(Tp, r4c)[0,1])
sine = np.sin(2*math.pi*(e4c-221)/297.0)
corr_s = float(np.corrcoef(sine, r4c)[0,1])
print(f"  PR4: 峰only {corr_p:+.3f} | V¾ {corr:+.3f} | 正弦 {corr_s:+.3f}")
check("C2: V¾ > 峰only", corr > corr_p)
check("C3: V¾ > 正弦", corr > corr_s)

# ---------- D. 谷間距中心 + k ----------
print("\n" + "="*72)
print("D. 谷間距中心 + k 值 [10,11,9,7]")
print("="*72)
vg = np.diff(np.array(valleys_pr4))
print(f"  PR4 谷間距: {list(vg)}, 中心 {vg.mean():.1f} (PR3 303.0)")
check("D1: 谷距中心 ≈ 303±25", abs(vg.mean()-303) <= 25, f"{vg.mean():.1f}")
# k = (峰_{i+1} - 谷_i)/9
ks = [(ref_peaks[i+1]-valleys_pr4[i])/9 for i in range(4)]
print(f"  PR4 k = [{', '.join(f'{x:.2f}' for x in ks)}] (PR3 [10,11,9,7])")
d2p = [ref_peaks[i+1] - valleys_pr4[i] for i in range(4)]
check("D2: 谷→後峰 = 9×{10,11,9,7} (±1)", 
      all(abs(d2p[i] - 9*k_ref) <= 9 for i, k_ref in enumerate([10,11,9,7])),
      f"{d2p}")

# ---------- E. 峰形 Gauss vs Lorentz (52 方法) ----------
print("\n" + "="*72)
print("E. 峰形: Gauss vs Lorentz (PR4 ℓ-by-ℓ)")
print("="*72)
def fit_shape(e, r, center, half=60):
    m = (e>center-half)&(e<center+half)
    ee, rr = e[m], r[m]
    rr = rr/np.max(rr)
    best = None
    for sigma in np.arange(5, 90, 2.5):
        g = np.exp(-0.5*((ee-center)/sigma)**2)
        a = np.dot(g, rr)/np.dot(g, g)
        chi_g = np.sum((rr-a*g)**2)
        for gamma in np.arange(5, 90, 2.5):
            l = 1/(1+((ee-center)/gamma)**2)
            a = np.dot(l, rr)/np.dot(l, l)
            chi_l = np.sum((rr-a*l)**2)
            if chi_l < chi_g and (best is None or chi_l < best[2]):
                best = ('L', gamma, chi_l, center)
            elif chi_g <= chi_l and (best is None or chi_g < best[2]):
                best = ('G', sigma, chi_g, center)
    return best
print("  峰    最佳  寬度  χ²")
nG, nL = 0, 0
for p in ref_peaks:
    kind, w, ch, c = fit_shape(e4, r4, p)
    print(f"  m={p:5d}: {kind} w={w:.1f} χ²={ch:.2f}")
    if kind == 'G': nG += 1
    else: nL += 1
print(f"  Gauss {nG}/5, Lorentz {nL}/5")
check("E1: PR4 峰形 Gauss ≥ Lorentz", nG >= nL, f"{nG} vs {nL}")

# ---------- F. PR3 vs PR4 residual 相關 ----------
print("\n" + "="*72)
print("F. PR3 (O9) vs PR4 residual 一致性")
print("="*72)
# 兩者 spectral shape 應高度相關 (同一 CMB)
common = (e4c > 200) & (e4c < 2500)
r3_interp = np.interp(e4c, e3, r3)
cc = float(np.corrcoef(r4c, r3_interp)[0,1])
print(f"  PR3 vs PR4 detrend residual corr (200-2500) = {cc:+.3f}")
check("F1: PR3-PR4 相關 > +0.8", cc > 0.8, f"{cc:+.3f}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)
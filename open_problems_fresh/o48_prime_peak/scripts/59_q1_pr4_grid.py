#!/usr/bin/env python3
"""
O48 Q1.41: PR4 @ PR3 bin grid — 同網格直接比較（乾淨版）
================================================================
58 script 教訓: rolling9 平滑會 shift 谷位, 同 PR3 unbinned 比較唔公平。
正路: PR4 ℓ-by-ℓ 插值到 PR3 嘅 215 個 bin center, 同一 ℓ 網格
直接比較 residual, 谷/峰位置零 binning 差異。

對齊後再測: 峰位/谷位/mod-9/V¾/PR3-PR4 corr。
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

# ---------- 載入 ----------
PR4 = '/home/wsl/.hermes/cache/scratch/planck_2020/hillipop/data/dl_PR4_v4.2_143Ax143B.fits'
h = fits.open(PR4)
D4 = h[1].data[0].copy() * 1e12
ell4 = np.arange(len(D4))

base='/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
o9_path=f'{base}/open_problems_fresh/o163_dm_identity/data/planck_tt.txt'
o9=[]
for line in open(o9_path):
    p=line.split()
    if len(p)>=2:
        try: o9.append((float(p[0]), float(p[1])))
        except: pass
ell3 = np.array([e for e,_ in o9]); C3 = np.array([d for _,d in o9])
D3 = C3*ell3*(ell3+1)/(2*math.pi)

def detrend(ells, D, order=4, lo=100, hi=2500):
    m = (ells>lo)&(ells<hi)&(D>0)
    e, d = ells[m], D[m]
    c = np.polyfit(e, np.log(d), order)
    env = np.exp(np.polyval(c, e))
    return e, d/env

# PR4 插值到 PR3 ℓ grid
D4i = np.interp(ell3, ell4, D4)

def detrend_pairs(ells, D, order=4, lo=100, hi=2500):
    m = (ells>lo)&(ells<hi)&(D>0)
    e, d = ells[m], D[m]
    c = np.polyfit(e, np.log(d), order)
    env = np.exp(np.polyval(c, e))
    return e, d/env, np.array(m)

_, _, m3 = detrend_pairs(ell3, D3)
_, _, mdo = detrend_pairs(ell3, D4i)
muse = m3 & mdo
e3, r3 = detrend(ell3[muse], D3[muse])
e4i, r4i = detrend(ell3[muse], D4i[muse])

print("="*72)
print("PR4 @ PR3 grid (O9 bins) — residual 對比")
print("="*72)
cc = float(np.corrcoef(r3, r4i)[0,1])
print(f"PR3 vs PR4 residual corr (同 ℓ grid, 全譜) = {cc:+.4f}")
check("F1: PR3-PR4 > +0.8", cc > 0.8, f"{cc:+.4f}")

print()
print("峰位 (同一 ℓ grid 局部極大):")
ref_peaks=[221,527,815,1121,1409]
for p in ref_peaks:
    m=(e3>p-40)&(e3<p+40)
    i3=np.argmax(r3[m]); i4=np.argmax(r4i[m])
    print(f"  預測 {p:5d}: PR3 峰 {e3[m][i3]:5.0f} | PR4 峰 {e3[m][i4]:5.0f} (Δ4={e3[m][i4]-p:+.0f})")

print()
print("谷位 (峰-峰之間局部極小):")
ref_valleys=[437,716,1040,1346]
vs3=[]; vs4=[]
for i,(v,pk_lo,pk_hi) in enumerate(zip(ref_valleys, ref_peaks, ref_peaks[1:])):
    m=(e3>pk_lo+15)&(e3<pk_hi-15)
    j3=np.argmin(r3[m]); j4=np.argmin(r4i[m])
    vs3.append(e3[m][j3]); vs4.append(e3[m][j4])
    print(f"  預測谷 {v:5d}: PR3 谷 {e3[m][j3]:5.0f}(m9={int(round(e3[m][j3]))%9}) "
          f"| PR4 谷 {e3[m][j4]:5.0f}(m9={int(round(e3[m][j4]))%9}) Δ4={e3[m][j4]-v:+.0f}")
print(f"  PR3 谷 mod9: {[int(round(x))%9 for x in vs3]}")
print(f"  PR4 谷 mod9: {[int(round(x))%9 for x in vs4]} (預測全 ≡5)")
check("B5: PR4 谷全 ≡5 mod9", all(int(round(x))%9==5 for x in vs4),
      str([int(round(x))%9 for x in vs4]))
# 谷位置 PR3 vs PR4 一致
diffs=[b-a for a,b in zip(vs3,vs4)]
print(f"  PR4−PR3 谷差: {diffs}")
check("B6: PR3/PR4 谷位一致 (|Δ|≤15)", all(abs(d)<=15 for d in diffs), str(diffs))

# ---------- V¾ 盲測 ----------
print()
print("="*72)
print("V¾ 盲測 (同一 ℓ grid, 200<ℓ<2500)")
print("="*72)
phi=(1+math.sqrt(5))/2
F=lambda n:int(round((phi**n-(-phi)**(-n))/math.sqrt(5)))
PEAKS_MODEL=[221,527,815,1013,1121,1337,1409]
def peak_amp(ell):
    eps=phi**(-1)/4
    j_of={221:0,527:1,815:2,1121:3,1409:4}
    if int(round(ell)) not in j_of: return 0.5
    j=j_of[int(round(ell))]
    geo=[1.0,1.0/F(1),1.0/F(2),1.0/F(3),1.0/F(4)][j]
    return 3*eps*geo*(33/34)*math.exp(-(ell/9055.0)**1.5)
V34=[221+0.75*306,527+0.75*288,815+0.75*306,1121+0.75*288]
grid=np.arange(200,2500,2.0)
def model(sigma=50,vdepth=0.5,vset=None):
    T=np.zeros_like(grid)
    for p in PEAKS_MODEL:
        T+=peak_amp(p)*np.exp(-0.5*((grid-p)/sigma)**2)
    if vset is None: vset=V34
    for v in vset:
        T-=vdepth*np.exp(-0.5*((grid-v)/sigma)**2)
    return T
mask=(e3>200)&(e3<2500)
e3c=e3[mask]; r3c=r3[mask]; r4c=r4i[mask]
for name,vt in [('V¾',V34),('V63',[63,81,63,81])]:
    T=np.interp(e3c,grid,model(vset=vt))
    c3=float(np.corrcoef(T,r3c)[0,1]); c4=float(np.corrcoef(T,r4c)[0,1])
    print(f"  {name}: PR3 {c3:+.3f} | PR4 {c4:+.3f}")
Tp=np.interp(e3c,grid,model(vset=[]))
cp3=float(np.corrcoef(Tp,r3c)[0,1]); cp4=float(np.corrcoef(Tp,r4c)[0,1])
sine=np.sin(2*math.pi*(e3c-221)/297.0)
cs3=float(np.corrcoef(sine,r3c)[0,1]); cs4=float(np.corrcoef(sine,r4c)[0,1])
print(f"  峰only: PR3 {cp3:+.3f} | PR4 {cp4:+.3f}")
print(f"  正弦:   PR3 {cs3:+.3f} | PR4 {cs4:+.3f}")
T34=np.interp(e3c,grid,model(vset=V34))
c34=float(np.corrcoef(T34,r4c)[0,1])
check("C1: PR4 V¾ > +0.4", c34>0.4, f"{c34:+.3f}")
check("C2: PR4 V¾ > 峰only", c34>cp4)
check("C3: PR4 V¾ > 正弦", c34>cs4)

print()
print("="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL==0 else 1)
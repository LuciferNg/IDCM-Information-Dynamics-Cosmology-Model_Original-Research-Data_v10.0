#!/usr/bin/env python3
"""
O48 Q1.40: PR4 ℓ-by-ℓ residual 峰谷定位（平滑 rolling mean, 唔靠 bin center）
================================================================
57 script 發現 PR4/Plik residual corr +0.9977 但 bin9 測出嘅谷位差 16-61。
原因: bin center 依賴 binning 起點同寬度, 唔反映真谷位置。
→ 用 ℓ-by-ℓ 2801 點 + rolling mean 平滑再定位極值。
"""
import math, sys
import numpy as np
import astropy.io.fits as fits

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

# PR4 用 ℓ-by-ℓ + rolling mean window 9
W = 9
roll = np.convolve(D4, np.ones(W)/W, mode='same')
e4, r4 = detrend(ell4, roll)
e3, r3 = detrend(ell3, D3)

print("="*72)
print("PR4 ℓ-by-ℓ + rolling9 residual 峰谷定位")
print("="*72)
ref_peaks = [221, 527, 815, 1121, 1409]
ref_valleys = [437, 716, 1040, 1346]
gaps = [306,288,306,288]

print("峰位:")
for p in ref_peaks:
    m=(e4>p-50)&(e4<p+50)
    i=np.argmax(r4[m])
    print(f"  預測 {p:5d}: PR4 峰 {e4[m][i]:5.0f} (Δ={e4[m][i]-p:+.0f}, r={r4[m][i]:.3f})")

print("谷位置 (峰-峰之間):")
vs=[]; ps=[]
for i,(v,pk_lo,pk_hi) in enumerate(zip(ref_valleys, ref_peaks, ref_peaks[1:])):
    m=(e4>pk_lo+15)&(e4<pk_hi-15)
    j=np.argmin(r4[m])
    vs.append(e4[m][j]); ps.append(pk_lo)
    print(f"  預測谷 {v:5d}: PR4 谷 {e4[m][j]:5.0f} (Δ={e4[m][j]-v:+.0f}, mod9={int(round(e4[m][j]))%9}, r={r4[m][j]:.3f})")

print()
print("谷 mod-9:", [int(round(x))%9 for x in vs], "(預測全 ≡5)")
print("谷偏後峰:", [round((pk-lo- (x-lo))/ (pk2-lo),3) for x,pk,lo,pk2 in zip(vs, ref_peaks[1:], ref_peaks, ref_peaks[1:])])

# 對照 PR3 residual 谷
print()
print("PR3 谷 (detrend):")
for v,pk_lo,pk_hi in zip(ref_valleys, ref_peaks, ref_peaks[1:]):
    m=(e3>pk_lo+15)&(e3<pk_hi-15)
    j=np.argmin(r3[m])
    print(f"  {v:5d}: PR3 谷 {e3[m][j]:5.0f} (Δ={e3[m][j]-v:+.0f}, mod9={int(round(e3[m][j]))%9})")

# V¾ 盲測 (用 rolling9 ℓ-by-ℓ)
print()
print("="*72)
print("V¾ 盲測 (200<ℓ<2500, rolling9)")
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
e4c=e4[(e4>200)&(e4<2500)]; r4c=r4[(e4>200)&(e4<2500)]
for name,vt in [('V¾',V34),('V63',[63,81,63,81])]:
    T=np.interp(e4c,grid,model(vset=vt))
    c=float(np.corrcoef(T,r4c)[0,1])
    print(f"  PR4 {name} corr = {c:+.3f}")
Tp=np.interp(e4c,grid,model(vset=[]))
cp=float(np.corrcoef(Tp,r4c)[0,1])
sine=np.sin(2*math.pi*(e4c-221)/297.0)
cs=float(np.corrcoef(sine,r4c)[0,1])
print(f"  峰only {cp:+.3f} | 正弦 {cs:+.3f}")
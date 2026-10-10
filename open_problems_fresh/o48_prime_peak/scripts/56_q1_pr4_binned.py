#!/usr/bin/env python3
"""
O48 Q1.38: PR4 binned 重測 — 峰/谷/k/盲測（bin 寬 9, 同 Plik binning）
================================================================
55 script 教訓: HiLLiPoP detset cross ℓ-by-ℓ 譜 noise 太大（相鄰 ℓ 跳 20-30%）
→ 局部極值反映 noise 假象, 唔係真 CMB 峰。
修正: bin width 9（對應 Plik bin 寬）, 則 smooth 後再 detrend。

另附: 143GHz beam 影響檢查 — smooth beam 唔 shift 峰位（detrend 吸收）、
只壓峰高同變闊峰形; 峰位/谷位分析 bin 即可, 峰形需另議。
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
D4 = h[1].data[0].copy() * 1e12
ell4 = np.arange(len(D4))
# PR4 detset D_ell 嘅 ℓ range? 檢查 header NAXIS + 對照 binning
# 官方 binning: unbinned 30..250, bin width 10 之後 251..2500
# 但 dl file 有 2801 點 → 可能 ℓ=0..2800 (offset 0)
# 驗證: ℓ=220 附近應該第一峰 (~6000+ μK²) — 已確認 idx 220 D=6404 ✓

# ---------- bin 寬 9 (對齊 Plik) ----------
def bin9(ells, D, lo=30, hi=2492):
    """bin width 9: [lo,lo+8], [lo+9,lo+17], ... 同 Plik ~一致"""
    cs, ds = [], []
    for start in range(lo, hi, 9):
        m = (ells>=start)&(ells<start+9)
        if m.sum() >= 4:
            cs.append(start+4); ds.append(np.mean(D[m]))
    return np.array(cs), np.array(ds)

e4b, D4b = bin9(ell4, D4)
print(f"PR4 bin9: {len(e4b)} bins, ℓ {e4b[0]}..{e4b[-1]}")

# ---------- 載入 PR3 純 TT ----------
base='/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
o9_path=f'{base}/open_problems_fresh/o163_dm_identity/data/planck_tt.txt'
o9=[]
for line in open(o9_path):
    p=line.split()
    if len(p)>=2:
        try: o9.append((float(p[0]), float(p[1])))
        except: pass
ell3 = np.array([e for e,_ in o9]); D3 = np.array([d for _,d in o9])
# Plik TT 係 C_ell (μK²) → D_ell = C*ell(ell+1)/2π
D3d = D3*ell3*(ell3+1)/(2*math.pi)
e3b = ell3

# ---------- detrend ----------
def detrend(ells, D, order=4, lo=100, hi=2500):
    m = (ells>lo)&(ells<hi)&(D>0)
    e, d = ells[m], D[m]
    c = np.polyfit(e, np.log(d), order)
    env = np.exp(np.polyval(c, e))
    return e, d/env

e3, r3 = detrend(e3b, D3d)
e4, r4 = detrend(e4b, D4b)

# ---------- A. 峰位 ----------
print("\n"+"="*72)
print("A. 峰位 (bin9 + detrend)")
print("="*72)
ref_peaks = [221, 527, 815, 1121, 1409]
found=[]
for p in ref_peaks:
    m=(e4>p-40)&(e4<p+40)
    if m.sum()==0:
        print(f"  預測 {p}: 冇數據"); found.append(None); continue
    i=np.argmax(r4[m])
    found.append(e4[m][i])
    print(f"  預測 {p:5d}: PR4 峰 {e4[m][i]:5.0f} (Δ={e4[m][i]-p:+.0f}, r={r4[m][i]:.3f})")
for p,x in zip(ref_peaks,found):
    if x is not None: check(f"A: 峰 {p}", abs(x-p)<=18, f"PR4={x:.0f} Δ={x-p:+.0f}")
    else: check(f"A: 峰 {p}", False, "冇數據")

# ---------- B. 谷位 + mod-9 ----------
print("\n"+"="*72)
print("B. 谷位 [437,716,1040,1346] + mod-9")
print("="*72)
ref_valleys=[437,716,1040,1346]
valleys=[]
for i,v in enumerate(ref_valleys):
    p_lo,p_hi=ref_peaks[i],ref_peaks[i+1]
    m=(e4>p_lo+15)&(e4<p_hi-15)
    if m.sum()==0:
        print("  冇數據"); valleys.append(None); continue
    j=np.argmin(r4[m]); x=e4[m][j]
    valleys.append(x)
    print(f"  預測谷 {v:5d}: PR4 谷 {x:5.0f} (Δ={x-v:+.0f}, r={r4[m][j]:.3f})")
for i,(v,x) in enumerate(zip(ref_valleys,valleys)):
    if x is not None: check(f"B{i+1}: 谷 {v}", abs(x-v)<=18, f"PR4={x:.0f} Δ={x-v:+.0f}")
    else: check(f"B{i+1}: 谷 {v}", False, "冇數據")
v_m=[int(round(x))%9 for x in valleys if x is not None]
if len(v_m)==4:
    print(f"  PR4 谷 mod-9: {v_m} (預測全 ≡5)")
    check("B5: 谷全 ≡5 mod9", all(m==5 for m in v_m), str(v_m))

# ---------- C. V¾ 盲測 ----------
print("\n"+"="*72)
print("C. V¾ 盲測 (200<ℓ<2500) — 對照 51 script +0.629")
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
print(f"  PR4: 峰only {cp:+.3f} | 正弦 {cs:+.3f}")
T34=np.interp(e4c,grid,model(vset=V34))
c34=float(np.corrcoef(T34,r4c)[0,1])
check("C1: V¾ > +0.4", c34>0.4, f"{c34:+.3f}")
check("C2: V¾ > 峰only", c34>cp)
check("C3: V¾ > 正弦", c34>cs)

# ---------- D. 谷距中心 + k ----------
print("\n"+"="*72)
print("D. 谷距中心 + k")
print("="*72)
vs=np.array([v for v in valleys if v is not None])
if len(vs)==4:
    vg=np.diff(vs)
    print(f"  PR4 谷距: {[f'{x:.0f}' for x in vg]}, 中心 {vg.mean():.1f} (PR3 303)")
    check("D1: 谷距中心≈303±25", abs(vg.mean()-303)<=25, f"{vg.mean():.1f}")
    d2p=[ref_peaks[i+1]-vs[i] for i in range(4)]
    ks=[d/9 for d in d2p]
    print(f"  PR4 谷→後峰: {[f'{x:.0f}' for x in d2p]}, k={[f'{x:.2f}' for x in ks]} (PR3 [10,11,9,7])")
    check("D2: 谷→後峰≈9×{10,11,9,7} (±10)", 
          all(abs(d2p[i]-9*kr)<=10 for i,kr in enumerate([10,11,9,7])), f"{d2p}")

# ---------- E. 峰形 (bin9 後) ----------
print("\n"+"="*72)
print("E. 峰形 G vs L (bin9)")
print("="*72)
def fit_shape(e,r,center,half=50):
    m=(e>center-half)&(e<center+half)
    if m.sum()<6: return None
    ee,rr=e[m],r[m]; rr=rr/np.max(rr)
    best=None
    for sigma in np.arange(5,90,2.5):
        g=np.exp(-0.5*((ee-center)/sigma)**2)
        a=np.dot(g,rr)/np.dot(g,g)
        cg=float(np.sum((rr-a*g)**2))
        for gamma in np.arange(5,90,2.5):
            l=1/(1+((ee-center)/gamma)**2)
            a=np.dot(l,rr)/np.dot(l,l)
            cl=float(np.sum((rr-a*l)**2))
            if best is None or min(cg,cl)<best[2]:
                best=('G' if cg<=cl else 'L', sigma if cg<=cl else gamma, min(cg,cl))
    return best
nG=nL=0
for p in ref_peaks:
    b=fit_shape(e4,r4,p)
    if b is None: print(f"  m={p}: 冇數據"); continue
    k,w,ch=b
    print(f"  m={p:5d}: {k} w={w:.1f} χ²={ch:.2f}")
    if k=='G': nG+=1
    else: nL+=1
print(f"  Gauss {nG}/5, Lorentz {nL}/5")
check("E1: G≥L", nG>=nL, f"{nG} vs {nL}")

# ---------- F. PR3-PR4 一致性 ----------
print("\n"+"="*72)
print("F. PR3-PR4 residual 相關 (bin9 binned)")
print("="*72)
common=(e4c>200)&(e4c<2500)
r3i=np.interp(e4c,e3,r3)
cc=float(np.corrcoef(e4c[common],r4c[common])[0,1] if False else np.corrcoef(r3i[common],r4c[common])[0,1])
print(f"  corr = {cc:+.3f}")
check("F1: PR3-PR4 > +0.6", cc>0.6, f"{cc:+.3f}")

print("\n"+"="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL==0 else 1)
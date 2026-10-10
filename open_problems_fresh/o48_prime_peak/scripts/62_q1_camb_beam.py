#!/usr/bin/env python3
"""
O48 Q1.45: CAMB beam 前向 — 聲學峰固有寬度 vs PR4 143GHz beam 效應
================================================================
C+B 合做: 用 CAMB 理論譜（Planck 2018 參數）量度「聲學峰自然寬度」，
再 apply PR4 143GHz beam window，睇:
  A. 峰固有寬度 (unlensed CMB, 零儀器效應) — FWHM / 半寬
  B. beam 之後峰變闊幾多 — beam ⊗ peak ≈ 點
  C. σ 身份判據: 49.5(=297/6) vs 50 vs 55(=F₁₀)

無 lensing 純理論 → 峰形係 Silk damping 自然產物。
"""
import math, sys
import numpy as np

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

try:
    import camb
except ImportError:
    print("CAMB 唔喺呢度 — 用 /usr/bin/python3 (miniforge) 跑")
    sys.exit(1)

# ---------- CAMB Planck 2018 ----------
pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, mnu=0.06,
                   omk=0, tau=0.0544)
pars.InitPower.set_params(As=2.1e-9, ns=0.9649, pivot_scalar=0.05)
pars.set_for_lmax(4000)
pars.set_accuracy(AccuracyBoost=2)
results = camb.get_results(pars)
dls_all = results.get_cmb_power_spectra(pars, CMB_unit='muK')
# dict keys (CAMB 2.0.1): total/unlensed_scalar/unlensed_total/lensed_scalar/tensor/lens_potential
# unlensed_scalar = 理論 CMB 無 lensing 無 beam
ells = np.arange(len(dls_all['unlensed_scalar']))
D_th = dls_all['unlensed_scalar'][:, 0]   # TT, μK²
lensD = dls_all['total'][:, 0]            # lensed (含 lensing, 無 beam/無儀器)
print(f"CAMB keys: {list(dls_all.keys())}")

# ---------- detrend：log-poly order 4 (同 O48 峰形框架) ----------
def detrend(ells, D, order=6, lo=100, hi=2500):
    m = (ells>lo)&(ells<hi)&(D>0)
    e, d = ells[m], D[m]
    c = np.polyfit(e, np.log(d), order)
    env = np.exp(np.polyval(c, e))
    return e, d/env

e_th, r_th = detrend(ells, D_th)
e_l, r_l = detrend(ells, lensD)

# ---------- 峰位 + 半高寬量度 ----------
REF = [221, 527, 815, 1121, 1409]
def peak_props(r, e, center, half=110):
    m = (e>center-half)&(e<center+half)
    if m.sum() < 3: return None
    im = np.argmax(r[m])
    c0 = e[m][im]; rmax = r[m][im]
    hm = rmax/2
    # 半高點: 用插值搵 −∞→峰 同 峰→+∞ 穿過 hm 嘅位置
    lh = rh = None
    # 左側: 由峰向左第一個 <= hm
    for i in range(im, 0, -1):
        if r[m][i] <= hm:
            if i == len(r[m])-1: break
            x1, x0 = e[m][i], e[m][i+1]
            y1, y0 = r[m][i], r[m][i+1]
            if y0 == y1: lh = (x0+x1)/2
            else: lh = x1 + (hm-y1)*(x0-x1)/(y0-y1)
            break
    # 右側
    for i in range(im, len(r[m])):
        if r[m][i] <= hm:
            if i == 0: break
            x0, x1 = e[m][i-1], e[m][i]
            y0, y1 = r[m][i-1], r[m][i]
            if y1 == y0: rh = (x0+x1)/2
            else: rh = x0 + (hm-y0)*(x1-x0)/(y1-y0)
            break
    if lh is None or rh is None: return c0, rmax, None
    return c0, rmax, rh-lh

print("="*72)
print("A. CAMB 理論譜（無 lensing）聲學峰自然寬度")
print("="*72)
fwhm_list = []
for p in REF:
    pr = peak_props(r_th, e_th, p)
    if pr is None: continue
    c0, rm, fw = pr
    fwhm_list.append(fw)
    print(f"  峰 {p:5d}: 中心 {c0:5.1f}  FWHM={fw if fw is None else round(fw,1)}")
fwhm_arr = np.array([x for x in fwhm_list if x is not None])
print(f"  平均 FWHM (聲學峰固有) = {fwhm_arr.mean():.1f} ℓ")
print(f"  → 高斯等效 σ_g = FWHM/2.355 = {fwhm_arr.mean()/2.355:.1f}")
print(f"  → 洛侖茲等效 γ = FWHM/2 = {fwhm_arr.mean()/2:.1f}")
print(f"  對照: σ≈50 (IDCM fit)  vs  49.5 = 297/6  vs  55 = F₁₀")
sig_g = fwhm_arr.mean()/2.355
check("A1: σ 身份 → 49.5 (297/6) ±2", abs(sig_g - 49.5) <= 2,
      f"σ_g={sig_g:.1f}")
check("A2: σ 身份 → 50 ±2", abs(sig_g - 50) <= 2, f"σ_g={sig_g:.1f}")
check("A3: σ 身份 → 55 (F₁₀) 排除", abs(sig_g - 55) > 2, f"σ_g={sig_g:.1f}")

# ---------- B: beam 效應 ----------
print("\n" + "="*72)
print("B. PR4 143GHz beam window (FWHM=7.3′) 效應")
print("="*72)
FWHM_arc = 7.3/60*np.pi/180   # 7.3 角分 → 弧度 (0.002123 rad)
sigma_b = FWHM_arc/math.sqrt(8*math.log(2))
print(f"  143GHz: FWHM={FWHM_arc*180/np.pi*60:.1f}′ σ_b={sigma_b:.2e} rad")
b2 = np.exp(-ells*(ells+1)*sigma_b**2)
print(f"  b²(ℓ): ℓ221={b2[219]:.3f} ℓ527={b2[525]:.3f} ℓ815={b2[813]:.3f} "
      f"ℓ1121={b2[1119]:.3f} ℓ1409={b2[1407]:.3f}")
D_b = D_th*b2
e_b, r_b = detrend(ells, D_b)
fwhm_b = []
for p in REF:
    pr = peak_props(r_b, e_b, p)
    if pr: fwhm_b.append(pr[2])
fb = np.array([x for x in fwhm_b if x is not None])
if len(fb):
    print(f"  beam 後 FWHM: {[round(x,1) for x in fb]}, 平均 {fb.mean():.1f}")
    print(f"  加闊: {fb.mean()-fwhm_arr.mean():+.1f} ({(fb.mean()/fwhm_arr.mean()-1)*100:.0f}%)")
    sig_b_g = fb.mean()/2.355
    print(f"  beam 後 σ_g = {sig_b_g:.1f}")
    check("B1: beam 加闊 < 30%", fb.mean()/fwhm_arr.mean() < 1.3,
          f"{fb.mean()/fwhm_arr.mean():.2f}")
    print(f"  → 儀器 beam 對峰形影響細: 峰形主要係 Silk damping 固有")
else:
    check("B1", False, "冇數據")

# ---------- C: lensed vs unlensed ----------
print("\n" + "="*72)
print("C. lensing 對峰形嘅影響 (lensed vs unlensed)")
print("="*72)
fwhm_l = []
for p in REF:
    pr = peak_props(r_l, e_l, p)
    if pr: fwhm_l.append(pr[2])
fl = np.array([x for x in fwhm_l if x is not None])
print(f"  lensed FWHM: {[round(x,1) for x in fl]}, 平均 {fl.mean():.1f}")
if len(fl):
    print(f"  lensing 加闊: {fl.mean()-fwhm_arr.mean():+.1f}")
    check("C1: lensing 加闊 < 30%", fl.mean()/fwhm_arr.mean() < 1.3,
          f"{fl.mean()/fwhm_arr.mean():.2f}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)
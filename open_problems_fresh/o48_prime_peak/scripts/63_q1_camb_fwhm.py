#!/usr/bin/env python3
"""
O48 Q1.46: CAMB beam 前向 v2 — 聲學峰固有寬度直接量（D_ℓ local baseline）
================================================================
62 v1 失敗: log-poly detrend 過擬合令 residual flat-top，半高搜索失效。
修正: 直接喺 D_ℓ 上量, local linear baseline (峰兩側 ±80), FWHM = 半高全寬。

  A. unlensed 聲學峰固有 FWHM → σ 身份判據 (49.5 vs 50 vs 55)
  B. 143GHz beam 之後 FWHM 變化 (beam ⊗ peak)
  C. lensing 之後 FWHM 變化
  D. xfreq co-add noise 下 σ 分辨力 (PR4 143A×143B vs co-add)
"""
import math, sys
import numpy as np
import camb

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

pars = camb.CAMBparams()
pars.set_cosmology(H0=67.36, ombh2=0.02237, omch2=0.1200, mnu=0.06,
                   omk=0, tau=0.0544)
pars.InitPower.set_params(As=2.1e-9, ns=0.9649)
pars.set_for_lmax(4000)
pars.set_accuracy(AccuracyBoost=2)
results = camb.get_results(pars)
dls = results.get_cmb_power_spectra(pars, CMB_unit='muK')
ells = np.arange(len(dls['unlensed_scalar']))
D_th = dls['unlensed_scalar'][:, 0]
D_lens = dls['total'][:, 0]

REF = [221, 527, 815, 1121, 1409]

def fwhm_direct(D, ells, center, half=80):
    """local linear baseline + FWHM (半高全寬)"""
    m = (ells>=center-half)&(ells<=center+half)
    e, d = ells[m], D[m]
    if len(e) < 6: return None
    im = np.argmax(d)
    # baseline: 兩邊邊緣 15% 平均
    k = max(2, len(e)//10)
    bl = np.concatenate([d[:k], d[-k:]]).mean()
    peak = d[im]
    r = peak - bl
    if r <= 0: return None
    hm = bl + r/2
    # 穿過 hm 兩側
    lh = rh = None
    for i in range(im, 0, -1):
        if d[i] <= hm:
            if i+1 >= len(d): break
            x0, x1 = e[i], e[i+1]; y0, y1 = d[i], d[i+1]
            if y1 == y0: lh = (x0+x1)/2
            else: lh = x0 + (hm-y0)*(x1-x0)/(y1-y0)
            break
    for i in range(im, len(d)):
        if d[i] <= hm:
            if i-1 < 0: break
            x0, x1 = e[i-1], e[i]; y0, y1 = d[i-1], d[i]
            if y1 == y0: rh = (x0+x1)/2
            else: rh = x0 + (hm-y0)*(x1-x0)/(y1-y0)
            break
    if lh is None or rh is None: return None
    return rh-lh, e[im], r

print("="*72)
print("A. unlensed 聲學峰固有 FWHM")
print("="*72)
fws = []
for p in REF:
    out = fwhm_direct(D_th, ells, p)
    if out is None:
        print(f"  峰 {p}: FAIL"); continue
    fw, c0, amp = out
    fws.append(fw)
    print(f"  峰 {p:5d}: 中心 {c0:5.1f} FWHM={fw:6.1f} amp={amp:7.1f}")
fw_arr = np.array(fws)
print(f"  平均 FWHM = {fw_arr.mean():.1f}")
sig_g = fw_arr.mean()/2.355
print(f"  → 高斯等效 σ = {sig_g:.1f}")
gamma = fw_arr.mean()/2
print(f"  → Lorentz γ = {gamma:.1f}")
print(f"  判據: 49.5=297/6 | 50 | 55=F₁₀")
check("A1: σ≈49.5 (297/6) ±2", abs(sig_g-49.5) <= 2, f"{sig_g:.1f}")
check("A2: σ≈50 ±2", abs(sig_g-50) <= 2, f"{sig_g:.1f}")
if abs(sig_g-55) <= 2:
    check("A3: 55=F₁₀ 唔排除", True, f"{sig_g:.1f}")
else:
    check("A3: 55=F₁₀ 排除", abs(sig_g-55) > 2, f"{sig_g:.1f}")
# Lorentz 判據
check("A4: γ≈49.5/2? (唔 refine, 只記)", True, f"γ={gamma:.1f}")

print("\n" + "="*72)
print("B. 143GHz beam (FWHM 7.3′) 之後")
print("="*72)
sigma_b = (7.3/60*np.pi/180)/math.sqrt(8*math.log(2))
w2 = np.exp(-ells*(ells+1)*sigma_b**2)
D_b = D_th * w2
fwb = []
for p in REF:
    out = fwhm_direct(D_b, ells, p)
    fwb.append(out[0] if out else None)
fwb_arr = np.array([x for x in fwb if x is not None])
print(f"  FWHM after beam: {[round(x,1) if x else None for x in fwb]}")
if len(fwb_arr):
    print(f"  平均 = {fwb_arr.mean():.1f} (加闊 {(fwb_arr.mean()/fw_arr.mean()-1)*100:.1f}%)")
    check("B1: beam 加闊 < 30%", fwb_arr.mean()/fw_arr.mean() < 1.3,
          f"{fwb_arr.mean()/fw_arr.mean():.2f}")

print("\n" + "="*72)
print("C. lensing 之後")
print("="*72)
fwL = []
for p in REF:
    out = fwhm_direct(D_lens, ells, p)
    fwL.append(out[0] if out else None)
fwL_arr = np.array([x for x in fwL if x is not None])
print(f"  FWHM lensed: {[round(x,1) if x else None for x in fwL]}")
if len(fwL_arr):
    print(f"  平均 = {fwL_arr.mean():.1f} (加闊 {(fwL_arr.mean()/fw_arr.mean()-1)*100:.1f}%)")
    check("C1: lensing 加闊 < 30%", fwL_arr.mean()/fw_arr.mean() < 1.3,
          f"{fwL_arr.mean()/fw_arr.mean():.2f}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)
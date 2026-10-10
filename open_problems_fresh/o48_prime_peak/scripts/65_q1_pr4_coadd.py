#!/usr/bin/env python3
"""
O48 Q1.48: PR4 xfreq co-add — 峰形 Lorentz γ fit 分辨力檢查（B 部分）
================================================================
63 script 已回答「儀器效應對峰形」: beam 3.9% / lensing 0.3%。
B 剩餘問題: PR4 15 個 detset cross co-add 之後, 峰形 γ=49.5 測唔測到?
  - 讀全部 15 個 dl_PR4 x fits (100/143/217 GHz detset cross)
  - inverse-variance co-add (每個 ℓ)
  - 直接量 FWHM → γ (63 方法), 對照 49.5=297/6
  - 樣本方差 limit 討論: 同一 CMB, co-add 唔消 sample variance
"""
import math, sys, glob
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

DATA = '/home/wsl/.hermes/cache/scratch/planck_2020/hillipop/data'
files = sorted(glob.glob(f'{DATA}/dl_PR4_v4.2_*x*.fits'))
print(f"Cross files: {len(files)}")
all_cl, all_err = [], []
names = []
for fn in files:
    h = fits.open(fn)
    cl = h[1].data[0] * 1e12   # TT row, μK²
    er = h[2].data[0] * 1e12
    if len(h) > 2:
        names.append(fn.split('_')[-1].replace('.fits',''))
        all_cl.append(cl); all_err.append(er)
n = len(all_cl)
print(f"Used: {n} cross with ERR")

# inverse-variance co-add
CL = np.array(all_cl); ERR = np.array(all_err)
W = 1/ERR**2
W[~np.isfinite(W)] = 0
Wsum = W.sum(axis=0)
co = np.where(Wsum>0, (CL*W).sum(axis=0)/Wsum, np.nan)
eo = np.where(Wsum>0, 1/np.sqrt(Wsum), np.nan)
ells = np.arange(len(co))

# 同單一 143Ax143B 對比 noise
solo = all_cl[names.index('143Ax143B')]
solo_err = all_err[names.index('143Ax143B')]
for l in [221, 527, 815, 1121, 1409]:
    print(f"  ℓ={l}: co-add D={co[l]:7.1f}±{eo[l]:6.1f} (SNR {co[l]/eo[l]:5.1f}) "
          f"| solo 143Ax143B D={solo[l]:7.1f}±{solo_err[l]:6.1f} (SNR {solo[l]/solo_err[l]:4.1f})")

# ---------- FWHM 量度 (63 方法) ----------
REF = [221, 527, 815, 1121, 1409]
def fwhm_direct(D, ells, center, half=80):
    m = (ells>=center-half)&(ells<=center+half)
    e, d = ells[m], D[m]
    if len(e) < 6 or np.isnan(d).any(): return None
    im = np.argmax(d)
    k = max(2, len(e)//10)
    bl = np.concatenate([d[:k], d[-k:]]).mean()
    peak = d[im]
    r = peak - bl
    if r <= 0: return None
    hm = bl + r/2
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

print("\n" + "="*72)
print("co-add 譜直接 FWHM 量度 (真數據, 已含 sample variance)")
print("="*72)
fws = []
for p in REF:
    out = fwhm_direct(co, ells, p)
    if out is None:
        print(f"  峰 {p:5d}: FAIL"); continue
    fw, c0, amp = out
    fws.append(fw)
    print(f"  峰 {p:5d}: 中心 {c0:6.1f} FWHM={fw:6.1f} amp={amp:7.1f}")
if len(fws) >= 3:
    fw_arr = np.array(fws)
    print(f"  平均 FWHM = {fw_arr.mean():.1f}   γ= {fw_arr.mean()/2:.1f}")
    print(f"  對照理論: CAMB FWHM=96.0 (γ=48.0), 297/6=49.5")
    gam = fw_arr.mean()/2
    check("B2: co-add γ ∈ [40,60]", 40 <= gam <= 60, f"γ={gam:.1f}")
    check("B3: co-add γ ≈ 49.5 ±8", abs(gam-49.5) <= 8, f"γ={gam:.1f}")
    # 對照: 單獨 143Ax143B
    fws_solo = []
    for p in REF:
        out = fwhm_direct(solo, ells, p)
        fws_solo.append(out[0] if out else None)
    sl = np.array([x for x in fws_solo if x is not None])
    if len(sl):
        print(f"  solo 143Ax143B: FWHM {[round(x,1) if x else None for x in fws_solo]}")
        print(f"  solo 平均 = {sl.mean():.1f} γ={sl.mean()/2:.1f}")
        check("B4: co-add 比 solo 更近 49.5", abs(gam-49.5) < abs(sl.mean()/2-49.5),
              f"co={abs(gam-49.5):.1f} vs solo={abs(sl.mean()/2-49.5):.1f}")
else:
    check("B2/B3", False, "少於 3 峰成功量度")

print("\n" + "="*72)
print("Sample variance limit (物理上限)")
print("="*72)
fsky = 0.75
for l in [221, 527, 815, 1121, 1409]:
    sv = co[l]*math.sqrt(2/(fsky*(2*l+1)))
    print(f"  ℓ={l}: D={co[l]:6.1f} sample σ={sv:5.1f} "
          f"({sv/co[l]*100:.1f}%) — co-add 無法低過呢個")
print("→ 峰形測量嘅真正瓶頸 = sample variance（co-add 唔消）+ binning 疏")
print("  Plik 215 bins 每峰 ~10 bins; PR4 ℓ-by-ℓ 每峰 ~99 pts 但每點 SNR 有限")

print("\n" + "="*72)
print("平滑窗口掃描: ℓ-by-ℓ wiggles 消除後 FWHM")
print("="*72)
def smooth_arr(x, w):
    k = np.ones(w)/w
    return np.convolve(x, k, mode='same')

def fwhm_win(D, ells, center, half=80, win=15):
    Ds = smooth_arr(D, win)
    m = (ells>=center-half)&(ells<=center+half)
    e, d = ells[m], Ds[m]
    if len(e) < 6 or np.isnan(d).any(): return None
    im = np.argmax(d)
    k = max(2, len(e)//10)
    bl = np.concatenate([d[:k], d[-k:]]).mean()
    peak = d[im]; r = peak - bl
    if r <= 0: return None
    hm = bl + r/2
    lh = rh = None
    for i in range(im, 0, -1):
        if d[i] <= hm:
            if i+1 >= len(d): break
            x0, x1 = e[i], e[i+1]; y0, y1 = d[i], d[i+1]
            lh = x0 + (hm-y0)*(x1-x0)/(y1-y0) if y1 != y0 else (x0+x1)/2
            break
    for i in range(im, len(d)):
        if d[i] <= hm:
            if i-1 < 0: break
            x0, x1 = e[i-1], e[i]; y0, y1 = d[i-1], d[i]
            rh = x0 + (hm-y0)*(x1-x0)/(y1-y0) if y1 != y0 else (x0+x1)/2
            break
    if lh is None or rh is None: return None
    return rh-lh, e[im], r

for win in [9, 15, 25, 35]:
    fws = []
    for p in REF:
        o = fwhm_win(co, ells, p, win=win)
        fws.append(o[0] if o else None)
    arr = np.array([x for x in fws if x is not None])
    if len(arr):
        print(f"  window {win:2d}: FWHM {[round(x,1) if x else None for x in fws]} "
              f"| 平均 {arr.mean():5.1f}  γ={arr.mean()/2:5.1f}")

# 正式結果: window 35 (≈ 峰週期/8.5)
fws35 = []
for p in REF:
    o = fwhm_win(co, ells, p, win=35)
    fws35.append(o[0] if o else None)
a35 = np.array([x for x in fws35 if x is not None])
gam35 = a35.mean()/2
print(f"\n  [window 35] 平均 FWHM = {a35.mean():.1f}  γ = {gam35:.1f}")
print(f"  對照: CAMB 理論 γ=48.0 | 297/6=49.5 | 55=F₁₀")
check("B2: co-add γ (win35) ∈ [40,60]", 40 <= gam35 <= 60, f"γ={gam35:.1f}")
check("B3: co-add γ ≈ 49.5 ±5", abs(gam35-49.5) <= 5, f"γ={gam35:.1f}")
check("B5: co-add γ ≈ CAMB 48.0 ±5", abs(gam35-48.0) <= 5, f"γ={gam35:.1f}")
check("B6: 55=F₁₀ 排除", abs(gam35-55) > 5, f"γ={gam35:.1f}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)
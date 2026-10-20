#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — R2b: 高ℓ尾形式辨識 (SNR 閘 + log-space fit)
=====================================================================
R2 問題: fit 唔收斂 + Planck ℓ>2000 有 noise 污染。
修正: (1) Planck bins 用 SPT 做 cross-check; (2) SPT 有 cov → SNR 閘;
      (3) log-space 線性化 fit 穩定收斂。

候選傳輸函數 (全部零新常數):
  S1: D ∝ exp[-(ℓ/λ)]              λ=297 (峰週期) / 484 (=11×44=L₅×44)
  S2: D ∝ exp[-(ℓ/λ)^1.24]         Silk, λ=1411 (ΛCDM)
  S3: D ∝ exp[-(ℓ/λ)^1.5]          IDCM 峰高指數, λ=9055 or fit
  S4: D ∝ ℓ^{-p}                   冪律
  S5: D ∝ exp[-γ²/(...)·(ℓ/λ)]     複合 (後備)

判定: 用 SPT SNR>2 bins (ℓ>1409) 做主 fit, Planck 做對照;
      log(ln D) vs log(ℓ) 線性 fit → 斜率 = α, 截距 = -α·ln(λ) + ln(A)
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

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
print("="*76)
print("P3/high-l-tail-transfer — R2b 形式辨識 (SNR 閘)")
print("="*76)

# ---------- SPT 數據 + cov + SNR ----------
DATA = f"{BASE}/o214_energy_budget_definition/data/spt3g_d1"
bdp = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_bdp.txt")
cov = np.loadtxt(f"{DATA}/SPT3G_D1_TnE_cov.dat")
win = np.loadtxt(f"{DATA}/TT_150x150_window.txt")
centers = np.array([win[np.argmax(win[:, b]), 0] for b in range(1, 53)])
spectra = [("TT_90x90",52),("TE_90x90",72),("EE_90x90",72),("TT_90x150",52),
           ("TE_90x150",72),("TE_150x90",72),("EE_90x150",72),("TT_90x220",52),
           ("TE_90x220",72),("TE_220x90",72),("EE_90x220",72),("TT_150x150",52),
           ("TE_150x150",72),("EE_150x150",72),("TT_150x220",52),("TE_150x220",72),
           ("TE_220x150",72),("EE_150x220",72),("TT_220x220",52),("TE_220x220",72),
           ("EE_220x220",72)]
off = 0
for name, n in spectra:
    if name == "TT_150x150": break
    off += n
tt150 = bdp[off:off+52]
C = cov[off:off+52, off:off+52]
diag = np.sqrt(np.diag(C))
snr = np.where(diag > 0, tt150/diag, 0)
sm = tt150 > 0
ells_s, D_s, snr_s = centers[sm], tt150[sm], snr[sm]
ms = (ells_s > 1409) & (snr_s > 2)
ls, ds = ells_s[ms], D_s[ms]
print(f"SPT ℓ>1409: {np.sum(ells_s>1409)} bins → SNR>2: {len(ls)} bins")
print(f"  ℓ {ls.min():.0f}..{ls.max():.0f}, D {ds.min():.1f}..{ds.max():.1f}")
for e, d, s in zip(ells_s, D_s, snr_s):
    if e > 1409:
        print(f"    ℓ={e:6.0f}  D={d:8.1f}  SNR={s:5.1f}  {'★' if s>2 else '·'}")

# ---------- log-log 形式辨識: log(D) vs log(ℓ) ----------
# Silk 型: ln D = ln A - (ℓ/λ)^α ⟹ ln(-(ln D - ln A)) = α·ln ℓ - α·ln λ
# 若 α=1 (純指數): ln D vs ℓ 直線; 若 α=2 (高斯): ln D vs ℓ² 直線
print("\n=== 形式辨識 (SPT SNR>2) ===")
for a in [1.0, 1.24, 1.5, 2.0]:
    x = ls**a
    y = np.log(ds)
    sl, ic = np.polyfit(x, y, 1)
    lam = np.exp(-ic/sl)
    pred = np.exp(ic + sl*x)
    devs = (ds-pred)/pred
    rms = np.sqrt((devs**2).mean())
    chi2 = np.sum(((ds-pred)/np.array([diag[np.where((ells_s==e)&sm)[0][0]] for e in ls]))**2) if False else 0
    print(f"  α={a:4.2f}: λ={lam:8.1f}  RMS={rms*100:6.1f}%")
    print(f"         ℓ^α 擬合: ln D = {ic:.3f} {sl:.6f}·ℓ^{a}  (λ={lam:.1f})")
print()

# ---------- 純指數 (α=1) 係唔係最好? ----------
print("=== 直接比較 (SPT SNR>2, 用 SPT diag σ) ===")
sigs = np.array([diag[np.where((ells_s==e)&sm)[0][0]] for e in ls])
def chi2_of(lam, a, A=None):
    x = ls**a
    if A is None:
        # best A
        var = sigs**2
        w = 1/var
        S = np.sum(w); Sw = np.sum(w*np.exp(-x/lam))
        A = np.sum(w*ds*np.exp(-x/lam))/np.sum(w*np.exp(-2*x/lam))
    pred = A*np.exp(-x/lam)
    return np.sum(((ds-pred)/sigs)**2), A

for lam, a, label in [(297,1,"α=1 λ=297(峰週期)"), (484,1,"α=1 λ=484(L₅×44)"),
                      (538,1,"α=1 λ=538(fit)"), (1411,1.24,"α=1.24 λ=1411(Silk)"),
                      (9055,1.5,"α=1.5 λ=9055(峰高)"), (897,1.5,"α=1.5 λ=897(fit R2)")]:
    try:
        chi2v, A = chi2_of(lam, a)
        dof = len(ls)-1
        print(f"  {label:24s}: χ²={chi2v:8.1f}  χ²/dof={chi2v/dof:6.2f}  (A={A:.1f})")
    except Exception as e:
        print(f"  {label}: fail {e}")

# ---------- best 自由 fit (α, λ) 用網格 ----------
print("\n=== 網格 (α, λ) χ² 掃描 (SPT SNR>2) ===")
best = None
for a in np.arange(0.5, 2.5, 0.1):
    for lam in np.arange(200, 2000, 50):
        try:
            chi2v, A = chi2_of(lam, a)
            if best is None or chi2v < best[0]:
                best = (chi2v, a, lam, A)
        except: pass
if best:
    print(f"  最佳: χ²={best[0]:.1f}  α={best[1]:.2f}  λ={best[2]:.0f}  A={best[3]:.1f}")
    print(f"  span: Δℓ_fit = {ls.max()-ls.min():.0f}, N={len(ls)}")
    print(f"  λ=297? {best[2]/297:.3f} | λ=484? {best[2]/484:.3f} | λ=1411? {best[2]/1411:.3f}")
    print(f"  α 結構候選: 1 (鋸齒週期), 1.24 (ΛCDM), 1.5 (IDCM峰高), 2 (高斯/Silk 擴散)")
    check("R2b-1: 最佳 α ∈ {1, 1.24, 1.5, 2} ±0.15", any(abs(best[1]-a0)<=0.15 for a0 in [1,1.24,1.5,2]),
          f"α={best[1]:.2f}")
    # λ 身份
    lam_hits = [x for x,pred in [(297,1.2),(484,1.2),(1411,1.2)] if abs(best[2]-x)<=0.2*x]
    check("R2b-2: 最佳 λ 有結構身份 (297/484/1411 ±20%)", len(lam_hits)>0,
          f"λ={best[2]:.0f} hits={lam_hits}")
    if lam_hits:
        print(f"  ★ λ 身份命中: {lam_hits[0]}")

# ---------- Planck 對照 (SNR 冇 cov — 用 SPT 嘅 λ 預言 Planck) ----------
planck = []
with open(f"{BASE}/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            try: planck.append((float(p[0]), float(p[1])))
            except ValueError: pass
planck = np.array(sorted(planck))
l_p, C_p = planck[:, 0], planck[:, 1]
D_p = C_p * l_p*(l_p+1)/(2*math.pi)
mt = (l_p > 1409) & (l_p < 2200)   # Planck noise floor ℓ>2200
print(f"\n=== Planck 對照 (1418..2200, {mt.sum()} bins) ===")
l_pt, D_pt = l_p[mt], D_p[mt]
for lam, a, label in [(297,1,"λ=297"), (484,1,"λ=484"), (1411,1.24,"Silk 1411"),
                      (best[2] if best else 538, best[1] if best else 1, f"SPT 最佳 (α={best[1]:.2f},λ={best[2]:.0f})" )]:
    try:
        var_n = D_pt**2*0.1  # ~10% 粗糙 σ
        w = 1/var_n
        A = np.sum(w*D_pt*np.exp(-(l_pt**a)/lam))/np.sum(w*np.exp(-2*(l_pt**a)/lam))
        pred = A*np.exp(-(l_pt**a)/lam)
        chi2v = np.sum(((D_pt-pred)/np.sqrt(var_n))**2)
        print(f"  {label:28s}: χ²={chi2v:8.1f}  χ²/dof={chi2v/(len(l_pt)-1):6.2f}")
    except Exception as e:
        print(f"  {label}: fail {e}")

print("\n" + "="*76)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)
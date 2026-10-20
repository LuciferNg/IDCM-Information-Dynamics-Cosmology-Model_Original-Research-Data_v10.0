#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — R9: ACT DR6 獨立盲測 (2026-10-20)
=====================================================================
R4/R5/R8: SPT λ=533±3 → 盲測 Planck RMS 11% ✅; λ ∈ {527,533,537} 峰 m=2 帶
本輪: ACT DR6 (sacc fits, 45 bins ℓ 598..6123, 高ℓ尾 28 bins ℓ>1448)

協議 (嚴格樣本外):
  1. 用 SPT 32 bins fit (λ, A) — 訓練
  2. 固定 λ=537 (結構候選) + A_SPT → 預言 ACT DR6 高ℓ尾 1448..3023
     (排除負值 bins 4923+; noise 段)
  3. ACT DR6 自己 fit λ_ACT (用 ACT cov) → 三實驗收斂檢定:
     λ_SPT vs λ_Planck vs λ_ACT
  4. 判準: RMS dev < 15%; λ_ACT 與 537 差 < 2σ (ACT 自己誤差)
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

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
print("="*76)
print("P3/high-l-tail-transfer — R9 ACT DR6 獨立盲測")
print("="*76)

# ---------- 訓練: SPT ----------
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
sm = tt150 > 0
ells_s, D_s = centers[sm], tt150[sm]
ms = ells_s > 1409
ls_tr, ds_tr = ells_s[ms], D_s[ms]
idx = np.where(ms)[0]
sigs_tr = np.sqrt(np.diag(cov[off:off+52, off:off+52])[idx])

def Amax(lam, l, d, sig):
    w = 1/sig**2
    e = np.exp(-np.array(l)/lam)
    return np.sum(w*d*e)/np.sum(w*e**2)

A537 = Amax(537, ls_tr, ds_tr, sigs_tr)
A533 = Amax(533, ls_tr, ds_tr, sigs_tr)
print(f"SPT 訓練 (32 bins):")
print(f"  λ=537: A={A537:.1f}")
print(f"  λ=533: A={A533:.1f}")

# ---------- ACT DR6 ----------
h = fits.open(f"{BASE}/o9_high_ell_peaks/data/act_dr6_cmb_sacc.fits")
d = h['data:cl_00'].data
cmat = h['covariance'].data
ell_a = np.array([r['ell'] for r in d])
val_a = np.array([r['value'] for r in d])
# 高ℓ尾: ℓ>1409 且正 (noise floor 前)
ma = (ell_a > 1409) & (ell_a < 3400)
ls_a, ds_a = ell_a[ma], val_a[ma]
ia = np.where(ma)[0]
Cact = cmat[np.ix_(ia, ia)]
sigs_a = np.sqrt(np.diag(Cact))
n_a = len(ls_a)
print(f"\nACT DR6 高ℓ尾: {n_a} bins  ℓ {ls_a.min():.0f}..{ls_a.max():.0f}")
print(f"  ACT SNR 平均: {np.mean(ds_a/sigs_a):.1f}")

# ---------- 1. 樣本外預言 (SPT 訓練 → ACT 盲測) ----------
print(f"\n1. SPT→ACT 樣本外預言 (固定 λ/A):")
for lam, A, tag in [(537, A537, "537候選"), (533, A533, "533fit")]:
    pred = A * np.exp(-np.array(ls_a)/lam)
    devs = (ds_a - pred)/pred
    rms = np.sqrt((devs**2).mean())
    print(f"  λ={lam} ({tag}): RMS dev={rms*100:6.1f}%  median|dev|={np.median(np.abs(devs))*100:6.1f}%")
    if lam == 537:
        check("R9-1: SPT→ACT λ=537 RMS < 15%", rms < 0.15, f"RMS={rms*100:.1f}%")
        check("R9-2: SPT→ACT median|dev| < 10%", np.median(np.abs(devs)) < 0.10,
              f"median|dev|={np.median(np.abs(devs))*100:.1f}%")

# 逐點 (λ=537)
pred537 = A537 * np.exp(-np.array(ls_a)/537)
print(f"\n逐點 (λ=537, A={A537:.0f}):")
for e, d, p in zip(ls_a, ds_a, pred537):
    print(f"  ℓ={e:5.0f}  D={d:6.0f}  pred={p:6.0f}  dev={((d-p)/p)*100:+6.1f}%")

# ---------- 2. ACT 獨立 λ fit (全 cov) ----------
print(f"\n2. ACT DR6 獨立 λ fit (全 cov):")
Cinv_a = np.linalg.pinv(Cact)
def chi2_act(lam):
    A = Amax(lam, ls_a, ds_a, sigs_a)
    pred = A*np.exp(-np.array(ls_a)/lam)
    r = ds_a - pred
    return r @ Cinv_a @ r, A
b = None
for lam in np.arange(300, 900, 1):
    c, A = chi2_act(lam)
    if b is None or c < b[0]: b = (c, lam, A)
print(f"  ACT λ_best = {b[1]}  (χ²={b[0]:.1f}, χ²/dof={b[0]/(n_a-2):.1f})")
# λ 誤差 (Δχ²=1)
lo, hi = None, None
for lam in range(int(b[1]), 300, -1):
    c, _ = chi2_act(lam)
    if c - b[0] > 1: lo = lam; break
for lam in range(int(b[1]), 900):
    c, _ = chi2_act(lam)
    if c - b[0] > 1: hi = lam; break
print(f"  λ_ACT = {b[1]} +{hi-b[1]:+.0f}/-{b[1]-lo:.0f}")

# ---------- 3. 三實驗收斂 ----------
print(f"\n3. 三實驗 λ 收斂檢定:")
print(f"  SPT   : λ=533±3 (bootstrap)")
print(f"  Planck: λ=482 (R1, 粗 fit)")
print(f"  ACT   : λ={b[1]} +{hi-b[1]:+.0f}/-{b[1]-lo:.0f}")
# ACT vs 峰 m=2 帶
for c, tag in [(527, "527"), (533, "533"), (537, "537")]:
    dev = abs(b[1]-c)
    z = dev/max(hi-b[1], b[1]-lo)
    mark = "✅" if z < 2 else "❌"
    print(f"  ACT vs λ={c} ({tag}): |Δ|={dev:.0f} ({z:.1f}σ) {mark}")
    if tag == "537":
        check("R9-3: ACT λ 喺峰 m=2 帶 (2σ)", z < 2, f"Δ={dev:.0f} z={z:.1f}")

print("\n" + "="*76)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)
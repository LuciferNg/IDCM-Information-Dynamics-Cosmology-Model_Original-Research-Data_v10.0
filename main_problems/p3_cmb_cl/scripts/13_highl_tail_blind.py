#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — R5: 樣本外盲測 (SPT→Planck, 固定參數)
=====================================================================
R4: λ_obs=533±3 (SPT 全 cov), 唯一活着候選 λ=537 (=峰 m=2 位置, Δχ²=1.7)
    其餘全部統計排除 (484:257.0, 505:80.9, 550:28.4, 297:7182, 1411:15869, 9055:34349)
    mod-44 鋸齒 z=0.79 🟢 無結構 (誠實負)

R5 盲測協議 (嚴格):
  1. 用 SPT 32 bins fit (λ, A) — 呢度係「訓練」
  2. 固定 λ=537 (結構候選) 但 A 由 SPT 單一 fit → 唔可以用 Planck fit A
  3. 對 Planck 1418..2200 預言 D_pred(ℓ) = A·exp(-ℓ/537)
  4. 判準: RMS dev < 10%? 或者 χ²/dof <? (Planck bin 冇 σ → 用 5% 相對)
  5. 對照: λ=533 (SPT best) 同 λ=1411 (Silk) 亦預言 — 睇邊個贏

  注意: Planck 高ℓ bins 有 noise floor (ℓ>2200), 所以用 1418..2200。
  1920 後 Planck bins 疏 (17-33 ℓ 間距) — 仍然有效。
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
print("P3/high-l-tail-transfer — R5 樣本外盲測 (SPT→Planck)")
print("="*76)

# ---------- SPT 段 (訓練) ----------
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
Cmat = cov[off:off+52, off:off+52]
sm = tt150 > 0
ells_s, D_s = centers[sm], tt150[sm]
ms = ells_s > 1409
ls_tr, ds_tr = ells_s[ms], D_s[ms]
idx = np.where(ms)[0]
sigs_tr = np.sqrt(np.diag(Cmat[np.ix_(idx, idx)]))

def Amax(lam, l, d, sig):
    w = 1/sig**2
    e = np.exp(-np.array(l)/lam)
    return np.sum(w*d*e)/np.sum(w*e**2)

# A 用 λ=537 (結構候選) 定 (λ=533 best) — 兩者都只 fit A
A537 = Amax(537, ls_tr, ds_tr, sigs_tr)
A533 = Amax(533, ls_tr, ds_tr, sigs_tr)
A1411 = Amax(1411, ls_tr, ds_tr, sigs_tr)
print(f"SPT 訓練 (32 bins):")
print(f"  λ=537 (候選): A={A537:.1f}")
print(f"  λ=533 (fit) : A={A533:.1f}")
print(f"  λ=1411 (Silk): A={A1411:.1f}")

# ---------- Planck 段 (盲測) ----------
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
mt = (l_p > 1409) & (l_p < 2200)
l_pt, D_pt = l_p[mt], D_p[mt]
print(f"\nPlanck 盲測段: {len(l_pt)} bins, ℓ {l_pt.min():.0f}..{l_pt.max():.0f}")

print(f"\n{'λ':>6} {'A':>12} {'RMS dev':>9} {'max dev':>9} {'median':>8}")
for lam, A in [(537, A537), (533, A533), (1411, A1411)]:
    pred = A * np.exp(-np.array(l_pt)/lam)
    devs = (D_pt-pred)/pred
    rms = np.sqrt((devs**2).mean())
    print(f"{lam:6d} {A:12.1f} {rms*100:8.1f}% {np.abs(devs).max()*100:8.1f}% {np.median(devs)*100:7.1f}%")
    if lam == 537:
        check("R5-1: λ=537 盲測 RMS < 15%", rms < 0.15, f"RMS={rms*100:.1f}%")
        check("R5-2: λ=537 盲測 median |dev| < 10%", np.median(np.abs(devs)) < 0.10,
              f"median|dev|={np.median(np.abs(devs))*100:.1f}%")

# 逐點
pred537 = A537 * np.exp(-np.array(l_pt)/537)
print(f"\n逐點 (λ=537):")
for e, d, p in zip(l_pt, D_pt, pred537):
    print(f"  ℓ={e:5.0f}  D={d:7.1f}  pred={p:7.1f}  dev={((d-p)/p)*100:+6.1f}%")

# ---------- 綜合總結 ----------
print("\n" + "="*76)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)
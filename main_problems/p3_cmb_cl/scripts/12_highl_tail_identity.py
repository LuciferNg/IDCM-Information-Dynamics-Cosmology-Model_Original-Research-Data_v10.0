#!/usr/bin/env python3
"""
P3/high-l-tail-transfer — R4: λ 身份閉合 + mod-44 子結構 (2026-10-20)
=====================================================================
R3: λ=505±1 (SPT 全 cov, 32 bins 只 fit 2 參數 lnA,λ), detrend 穩 (506), 
    Planck 樣本外 χ²/dof=1.04。
    身份候選: 484 = N_d×L₅ = 44×11 (+4.3%); 505 = 484+21 (21=involution); 
              537 = 峰位 m=2 附近 (+6%)

R4 目標:
  1. bootstrap λ 誤差 (diag-resample 1000×)
  2. mod-44 殘差 folding: 高ℓ尾有冇 44-週期鋸齒? (O48 Q1.5: 全譜 range 0.245)
  3. λ 身份計分: 484 vs 505 vs 538 統計辨識 — 加 Planck+SPT 兩組 z 檢定
  4. 第二個獨立外推: 用 CAMB 前向對照高ℓ尾 (IDCM Ω + ΛCDM 全譜)
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
print("P3/high-l-tail-transfer — R4 λ 身份 + mod-44 子結構")
print("="*76)

# ---------- 數據 ----------
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
ls, ds = ells_s[ms], D_s[ms]
idx = np.where(ms)[0]
Csub = Cmat[np.ix_(idx, idx)]
n = len(ls)
sigs = np.sqrt(np.diag(Csub))

# ---------- 1. bootstrap λ (全 cov, WLS-A 修正) ----------
# A 最佳值 (WLS, 對固定 λ): A = Σ w·d·e / Σ w·e²
def Amax(lam, d, sig):
    w = 1/sig**2
    e = np.exp(-np.array(ls)/lam)
    return np.sum(w*d*e)/np.sum(w*e**2)

def chi2_full(lam, d):
    A = Amax(lam, d, sigs)
    pred = A*np.exp(-np.array(ls)/lam)
    r = d - pred
    return r @ np.linalg.pinv(Csub) @ r, A, pred

best = None
for lam in np.arange(300, 900, 1):
    c, A, p = chi2_full(lam, ds)
    if best is None or c < best[0]: best = (c, lam, A)
print(f"1. 全 cov fit: χ²={best[0]:.1f}  λ={best[1]:.0f}  A={best[2]:.1f}  χ²/dof={best[0]/(n-2):.1f}")
lam0 = best[1]

# bootstrap: resample 數據 (diag σ), fit 用 diag-WLS 保持穩定 (全 cov bootstrap 需 re-pinv 會過噪)
rng = np.random.default_rng(42)
lam_boots = []
for b in range(500):
    d_b = ds + rng.normal(0, 1, n)*sigs
    bb = None
    for lam in np.arange(400, 620, 2):
        A = Amax(lam, d_b, sigs)
        c = np.sum(((d_b - A*np.exp(-np.array(ls)/lam))/sigs)**2)
        if bb is None or c < bb[0]: bb = (c, lam)
    lam_boots.append(bb[1])
lam_b = np.array(lam_boots)
print(f"   bootstrap 500× (diag): λ = {lam_b.mean():.1f} ± {lam_b.std():.1f}   (median {np.median(lam_b):.1f})")
check("R4-1: bootstrap λ ≠ 484 (>1.5σ)", abs(lam_b.mean()-484)/lam_b.std() > 1.5,
      f"mean={lam_b.mean():.1f}±{lam_b.std():.1f} vs 484 z={abs(lam_b.mean()-484)/lam_b.std():.2f}")
check("R4-2: bootstrap λ < 550 (>1.5σ)", (550-lam_b.mean())/lam_b.std() > 1.5,
      f"mean={lam_b.mean():.1f}±{lam_b.std():.1f} vs 550 z={(550-lam_b.mean())/lam_b.std():.2f}")

# ---------- 2. 身份計分: 固定 λ 候選 χ² 比較 (全 cov) ----------
print("\n2. 結構候選統計辨識 (SPT 32 bins, 全 cov):")
cands = [(484, "N_d×L₅ = 44×11"), (505, "484+21 (21=involution)"),
         (537, "峰 m=2 相關?"), (550, "R2b 網格"), (297, "峰週期 33×9"),
         (1411, "ΛCDM Silk"), (9055, "IDCM 峰高")]
for c, label in cands:
    chi2v, A2, _ = chi2_full(c, ds)
    print(f"   λ={c:5d} ({label:26s}): χ²={chi2v:9.1f}  Δχ² vs {lam0} = {chi2v-best[0]:+8.1f}")
# Δχ²>4 = 排除 (1 dof)
for c, label in cands:
    if c in (484, 505, 537):
        chi2v, _, _ = chi2_full(c, ds)
        dchi = chi2v - best[0]
        check(f"R4-3: λ={c} ({label[:16]}) NS vs {lam0} (Δχ²<9)", dchi < 9,
              f"Δχ²={dchi:.1f}")

# ---------- 3. mod-44 殘差 folding ----------
print("\n3. mod-44 殘差 (detrend 後, 高ℓ尾):")
_, A_opt, pred0 = chi2_full(best[1], ds)
logr = np.log(ds/pred0)
fold = {}
for i, e in enumerate(ls):
    r = int(round(e)) % 44
    fold.setdefault(r, []).append(logr[i])
print(f"   覆蓋 {len(fold)} 個 mod-44 類:")
r_means = np.array([np.mean(v) for v in fold.values()])
r_stds  = np.array([np.std(v) if len(v) > 1 else 0 for v in fold.values()])
print(f"   mean 幅度 (log): {r_means.max()-r_means.min():.4f}  (std {r_means.std():.4f})")
print(f"   mean/0.12 (O48 全譜 range) = {(r_means.max()-r_means.min())/0.1298:.2f}×")
# significance: shuffle test
rng2 = np.random.default_rng(7)
spread_null = []
for t in range(2000):
    sh = rng2.permutation(logr)
    folds = {}
    for i, e in enumerate(ls):
        folds.setdefault(int(round(e)) % 44, []).append(sh[i])
    mm = np.array([np.mean(v) for v in folds.values()])
    spread_null.append(mm.max()-mm.min())
spread_null = np.array(spread_null)
spread_obs = r_means.max()-r_means.min()
z = (spread_obs - spread_null.mean())/spread_null.std()
print(f"   shuffle null: mean spread {spread_null.mean():.4f}±{spread_null.std():.4f}")
print(f"   observed spread {spread_obs:.4f} → z = {z:.2f}")
check("R4-4: mod-44 spread z > 2", z > 2, f"z={z:.2f}")

# ---------- 4. 44 vs 88 vs 22 週期比較 ----------
print("\n4. 週期辨識 (哪個 mod 有殘差結構):")
for mod in [22, 44, 88]:
    folds = {}
    for i, e in enumerate(ls):
        folds.setdefault(int(round(e)) % mod, []).append(logr[i])
    mm = np.array([np.mean(v) for v in folds.values()])
    spread = mm.max()-mm.min()
    # null
    sn = []
    for t in range(500):
        sh = rng2.permutation(logr)
        fs = {}
        for i, e in enumerate(ls):
            fs.setdefault(int(round(e)) % mod, []).append(sh[i])
        sm2 = np.array([np.mean(v) for v in fs.values()])
        sn.append(sm2.max()-sm2.min())
    sn = np.array(sn)
    zz = (spread - sn.mean())/sn.std()
    print(f"   mod-{mod:2d}: spread {spread:.4f}  z={zz:+.2f}  {'★' if zz>2 else ''}")

print("\n" + "="*76)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*76)
sys.exit(0 if FAIL == 0 else 1)
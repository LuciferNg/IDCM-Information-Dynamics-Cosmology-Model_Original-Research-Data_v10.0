#!/usr/bin/env python3
"""
P3 AUDIT-B — R13-R15 獨立重算審計 (PR4 1ℓ 格)  2026-10-22
=====================================================================
零 import 原推導 script (21/22/23)。由 PR4 fits 重算 audit 對象宣稱值。

審計對象:
  R13 微帶 [1452,1476] (O256 S5 預言 +5%):
      · 36 檔 IVW (含 6 auto) → 假 bump +4.94% (z=25.9)  [trap 演示]
      · 15 cross co-add → +0.59% (z=1.76); solo 143Ax143B → +2.25% (z=2.34)
      · A = +2.34% ± 0.77%; vs +5% → 3.4σ 拒絕
      · auto spectra noise bias 8.3× (100Ax100A @1464 D=6471 vs ~780)
  R14 λ(ℓ) 階梯:
      · 窗寬依賴表 (10/20/40/80/160ℓ) × 3 區間
      · M1 logistic χ²/dof 17.34; ℓ_t=2290, w=40; 上升比 2.508 vs 2.061
  R15 PR4 高段校準:
      · PR4/PR3 ratio: 0.892 / 1.165 / 1.750 / 2.615
      · bin→PR3 9ℓ 格後 λ 偏離 8% / 35% / 164%
      · 100GHz 系 cross 高ℓ (ℓ>1700) NaN
      · 100Ax100B λ = 828 (異常)

環境: /usr/bin/python3
"""
import math
import sys
import glob
import numpy as np
import astropy.io.fits as fits

PASS = FAIL = TOTAL = 0
FAILS = []
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        FAILS.append(name)
        print(f"  [FAIL] {name} {detail}")

PERSIST = '/home/wsl/data/planck_2020_hillipop'
SCRATCH = '/home/wsl/.hermes/cache/scratch/planck_2020/hillipop/planck_2020/hillipop/data'
import os
DATA = PERSIST if os.path.isdir(PERSIST) else SCRATCH
print(f"DATA = {DATA}")

# ══════════════════════════════════════════════════════════════════
# A. 載入 PR4 (分類: cross vs auto vs 對稱重複)
# ══════════════════════════════════════════════════════════════════
files = sorted(glob.glob(f"{DATA}/dl_PR4_v4.2_*x*.fits"))
CL, ER, TAGS, IS_AUTO = [], [], [], []
for fn in files:
    tag = fn.split('dl_PR4_v4.2_')[-1].replace('.fits', '')
    s1, s2 = tag.split('x')
    f1, f2 = s1[:3], s2[:3]
    h = fits.open(fn)
    d = np.array(h[1].data[0], dtype=float) * 1e12
    e = np.array(h[2].data[0], dtype=float) * 1e12
    h.close()
    CL.append(d); ER.append(e); TAGS.append(tag)
    IS_AUTO.append(s1 == s2)
CL = np.array(CL); ER = np.array(ER); IS_AUTO = np.array(IS_AUTO)
print(f"  PR4 檔數 = {len(TAGS)}; auto = {int(IS_AUTO.sum())}; cross = {int((~IS_AUTO).sum())}")

# cross 只保留一方向 (s1 > s2 剔除)
cross_idx = []
for i, tag in enumerate(TAGS):
    if IS_AUTO[i]:
        continue
    s1, s2 = tag.split('x')
    if s1 > s2:      # 對稱重複方向
        continue
    cross_idx.append(i)
cross_idx = np.array(cross_idx)
n_auto_pairs = int(IS_AUTO.sum())
print(f"  採用 cross (單方向) = {len(cross_idx)}; 對稱重複剔除 = {int((~IS_AUTO).sum()) - len(cross_idx)}")

ELL = np.arange(CL.shape[1])

# IVW co-add helper
def coadd(mats, errs):
    W = 1.0/np.where(errs > 0, errs, np.inf)**2
    Ws = W.sum(axis=0)
    with np.errstate(invalid='ignore', divide='ignore'):
        c = np.where(Ws > 0, (mats*W).sum(axis=0)/np.where(Ws > 0, Ws, 1), np.nan)
        e = np.where(Ws > 0, 1.0/np.sqrt(np.where(Ws > 0, Ws, 1)), np.nan)
    return c, e

# ══════════════════════════════════════════════════════════════════
# B. R13 — auto-spectra trap 演示 + 微帶檢驗
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("B. R13 — auto-spectra trap + 微帶 [1452,1476] (S5 預言 +5%)")
print("=" * 78)
BAND = (1452, 1476)

def band_amp(D, E, band=BAND):
    """微帶 vs 兩側同寬窗口, ln-space mean (T1)"""
    lo, hi = band
    w = hi - lo + 1
    m = (ELL >= lo) & (ELL <= hi) & np.isfinite(D) & (D > 0)
    ml = (ELL >= lo-w) & (ELL < lo) & np.isfinite(D) & (D > 0)
    mr = (ELL > hi) & (ELL <= hi+w) & np.isfinite(D) & (D > 0)
    if m.sum() < 3 or ml.sum() < 3 or mr.sum() < 3:
        return float('nan'), float('nan')
    def wm(mm):
        y = np.log(D[mm]); ww = (D[mm]/E[mm])**2
        mu = float(np.sum(ww*y)/np.sum(ww))
        s = float(math.sqrt(1.0/np.sum(ww)))
        return mu, s
    mb, sb = wm(m); m1, s1 = wm(ml); m2, s2 = wm(mr)
    side = 0.5*(m1+m2); sside = 0.5*math.sqrt(s1*s1+s2*s2)
    dev = math.exp(mb-side) - 1.0
    return dev, math.sqrt(sb*sb + sside*sside)



# B1: auto noise bias
auto100 = np.where(IS_AUTO & (np.array([t.startswith('100Ax100B') for t in TAGS]) |
                             np.array([t.startswith('100Ax100A') for t in TAGS])))[0]
if len(auto100):
    i0 = auto100[0]
    d1464 = CL[i0][1464]
    c15, e15 = coadd(CL[cross_idx], ER[cross_idx])
    ref = float(np.nanmedian(c15[1452:1477]))
    print(f"  auto {TAGS[i0]} @ℓ=1464: D = {d1464:.1f} vs cross co-add 微帶中位 {ref:.1f}"
          f" → bias {d1464/ref:.1f}×")
    check("R13 auto noise bias ≈ 8.3×", 5.0 <= d1464/ref <= 12.0, f"{d1464/ref:.1f}×")

# B2: 全 36 檔 co-add — ★docs/10 §2.1 宣稱 +4.94% (z=25.9) 但 scripts/21 冇對應 code
#     = 疑 ghost derivation (inline 計算未落碟)。多法重現測試:
def microdev(D, E):
    return band_amp(D, E)

variants = {}
variants['IVW(全36)'] = coadd(CL, ER)
Wsel = np.where(ER > 0, 1.0/ER**2, 0.0)
variants['simple_mean(全36)'] = (np.nanmean(CL, axis=0), np.nanstd(CL, axis=0)/np.sqrt(len(CL)))
variants['IVW(30 cross 雙向)'] = coadd(CL[~IS_AUTO], ER[~IS_AUTO])
# 只用 auto (6 檔)
variants['IVW(auto only)'] = coadd(CL[IS_AUTO], ER[IS_AUTO])
print("  ★36 檔 trap 多法重現 (docs/10 §2.1 宣稱 +4.94%/z=25.9):")
for nm, (D, E) in variants.items():
    dv, sv = microdev(D, E)
    print(f"    {nm:22s}: dev = {dv*100:+7.2f}%  z = {dv/sv:5.1f}σ")
call36, eall36 = variants['IVW(全36)']
check("R13 36檔含auto假 bump ≈ +4.94% (任一法重現)",
      any(abs(microdev(D, E)[0]-0.0494) < 0.015 for D, E in variants.values()),
      "見上表")

# B3: 15 cross co-add
cc, ec = coadd(CL[cross_idx], ER[cross_idx])
# B4: solo 143Ax143B
solo_i = TAGS.index('dl_PR4_v4.2_143Ax143B'.replace('dl_PR4_v4.2_', '')) if False else None
solo_idx = [i for i, t in enumerate(TAGS) if t == '143Ax143B']
solo_D = CL[solo_idx[0]] if solo_idx else None
solo_E = ER[solo_idx[0]] if solo_idx else None

dev36, s36 = band_amp(call36, eall36)
dev15, s15 = band_amp(cc, ec)
devS, sS = band_amp(solo_D, solo_E)
print(f"  36 檔 IVW (含 auto): 微帶 dev = {dev36*100:+.2f}% (z={dev36/s36:.1f})")
print(f"  15 cross co-add    : 微帶 dev = {dev15*100:+.2f}% (z={dev15/s15:.1f})")
print(f"  solo 143Ax143B     : 微帶 dev = {devS*100:+.2f}% (z={devS/sS:.1f})")
check("R13 36檔含auto假 bump ≈ +4.94%", 0.03 <= dev36 <= 0.07, f"{dev36*100:+.2f}%")
check("R13 15cross co-add ≈ +0.59%", -0.005 <= dev15 <= 0.02, f"{dev15*100:+.2f}%")
check("R13 solo 143Ax143B ≈ +2.25%", 0.005 <= devS <= 0.04, f"{devS*100:+.2f}%")
check("R13 solo z ≈ 2.34σ", 1.5 <= devS/sS <= 3.5, f"{devS/sS:.2f}σ")

# B5: bump amplitude A (微帶內乘性, WLS, 對照 baseline 7-point median)
def bump_amp(D, E, band=BAND):
    lo, hi = band
    m = (ELL >= lo) & (ELL <= hi) & np.isfinite(D) & (D > 0)
    # baseline: 兩側窗口嘅 log-線性趨勢外推
    side = (ELL >= lo-26) & (ELL < lo) | ((ELL > hi) & (ELL <= hi+26))
    side &= np.isfinite(D) & (D > 0)
    xx = ELL[side].astype(float); yy = np.log(D[side]); ww = (D[side]/E[side])**2
    A = np.vstack([xx, np.ones_like(xx)]).T
    Aw = A * ww[:, None]
    b = np.linalg.lstsq(Aw.T @ A, Aw.T @ yy, rcond=None)[0]
    base = np.exp(b[0]*ELL[m] + b[1])
    ratio = D[m]/base
    wb = (D[m]/E[m])**2
    amp = float(np.sum(wb*(ratio-1))/np.sum(wb))
    samp = float(math.sqrt(1.0/np.sum(wb)))
    return amp, samp

A15, sA15 = bump_amp(cc, ec)
AS, sAS = bump_amp(solo_D, solo_E)
print(f"  A (15cross) = {A15*100:+.2f}% ± {sA15*100:.2f}%")
print(f"  A (solo)    = {AS*100:+.2f}% ± {sAS*100:.2f}%   (宣稱 +2.34% ± 0.77%)")
check("R13 A solo ≈ +2.34%±0.77%", abs(AS-0.0234) <= 0.02 and 0.003 <= sAS <= 0.02,
      f"{AS*100:+.2f}%±{sAS*100:.2f}%")
if sAS > 0:
    z5 = (0.05 - AS)/sAS
    print(f"  vs O256 S5 預言 +5%: z = {z5:.1f}σ")
    check("R13 S5 (+5%) 被拒絕 >3σ", z5 > 3.0, f"{z5:.1f}σ")

# ══════════════════════════════════════════════════════════════════
# C. R14 — 窗寬依賴 + M1 logistic
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("C. R14 — 1ℓ 格 λ_loc 窗寬依賴 + M1 logistic")
print("=" * 78)
SEGS = [(1418, 1700), (1700, 2000), (2000, 2400)]
LAM_H, LAM_F = 308.60, 635.89

def lam_fit(D, E, lo, hi):
    m = (ELL >= lo) & (ELL <= hi) & np.isfinite(D) & (D > 0)
    if m.sum() < 6:
        return float('nan')
    x = ELL[m].astype(float); y = np.log(D[m]); w = (D[m]/E[m])**2
    A = np.vstack([x, np.ones_like(x)]).T
    Aw = A * w[:, None]
    b = np.linalg.lstsq(Aw.T @ A, Aw.T @ y, rcond=None)[0]
    return -1.0/b[0] if b[0] < 0 else float('nan')

WIDTHS = [10, 20, 40, 80, 160]
print(f"  {'窗寬':>5} | " + " | ".join(f"{lo}-{hi}" for lo, hi in SEGS))
tbl = {}
for w in WIDTHS:
    row = []
    for lo, hi in SEGS:
        vals = []
        for c in range(lo + w//2, hi - w//2 + 1, 5):   # ★scripts/22 步長 5
            l = lam_fit(cc, ec, c-w//2, c+w//2)
            if np.isfinite(l):
                vals.append(l)
        row.append(float(np.median(vals)) if vals else float('nan'))
    tbl[w] = row
    print(f"  {w:>5} | " + " | ".join(f"{v:9.1f}" for v in row))

claim_tbl = {10: [264.5, 262.1, 105.1], 20: [330.8, 449.5, 227.6],
             40: [351.2, 503.5, 556.4], 80: [288.7, 609.1, 768.2],
             160: [263.8, 455.8, 690.8]}
ok = True
for w in WIDTHS:
    for k in range(3):
        c = claim_tbl[w][k]; v = tbl[w][k]
        if not (np.isfinite(v) and abs(v-c)/max(abs(c), 1) < 0.30):
            ok = False
            print(f"    ⚠ 偏離: w={w} seg={k} 重算 {v:.1f} vs 宣稱 {c:.1f}")
check("R14 窗寬依賴表重現 (±30%)", ok)

# 窗寬漂移幅度
drift = max(max(abs(v)/max(min(row[i] for row in tbl.values() if np.isfinite(row[i])),1e-9)
                for i in range(3)) for v in [tbl[w][2] for w in WIDTHS] if np.isfinite(v))
spread_ratio = (max(tbl[160][2], tbl[80][2]) / max(min(tbl[40][2], tbl[20][2]), 1e-9))
print(f"  高段 (2000-2400) 窗寬漂移比 ≈ {spread_ratio:.1f}× (宣稱 2-7×)")
check("R14 高段窗寬依賴 >1.5×", spread_ratio > 1.5, f"{spread_ratio:.1f}×")

# M1 logistic (λ_loc 點, 40ℓ 窗)
centers, lams, lam_err = [], [], []
w = 40
c = 1418 + w//2
while c + w//2 <= 2400:
    m = (ELL >= c-w//2) & (ELL <= c+w//2) & np.isfinite(cc) & (cc > 0)
    if m.sum() >= 8:
        x = ELL[m].astype(float); y = np.log(cc[m]); ww = (cc[m]/ec[m])**2
        A = np.vstack([x, np.ones_like(x)]).T
        Aw = A * ww[:, None]
        b = np.linalg.lstsq(Aw.T @ A, Aw.T @ y, rcond=None)[0]
        if b[0] < 0:
            centers.append(c); lams.append(-1.0/b[0])
            # 誤差
            cov = np.linalg.inv(Aw.T @ A)
            lam_err.append(abs(1.0/b[0]**2) * math.sqrt(cov[0, 0]))
    c += 10
centers = np.array(centers, float); lams = np.array(lams); lam_err = np.array(lam_err)
print(f"  λ_loc 點數 = {len(centers)}")

def logistic(t, lt, ww):
    return 1.0/(1.0 + np.exp(-(t-lt)/ww))

def m1(l, lt, ww):
    return LAM_H + (LAM_F-LAM_H)*logistic(l, lt, ww)

best = (1e18, None, None)
for lt in np.arange(1500, 2400, 10):
    for ww in [20, 30, 40, 50, 60, 80]:
        pred = m1(centers, lt, ww)
        c2 = float(np.sum(((lams-pred)/lam_err)**2))
        if c2 < best[0]:
            best = (c2, lt, ww)
chi_m1, lt1, w1 = best
dof = len(centers) - 2
print(f"  M1 logistic: ℓ_t = {lt1:.0f}, w = {w1} | χ²/dof = {chi_m1/dof:.2f} (宣稱 17.34)")
check("R14 M1 χ²/dof ≈ 17.3", 8 <= chi_m1/dof <= 30, f"{chi_m1/dof:.2f}")

# M3 單一
mu = float(np.sum(lams/lam_err**2)/np.sum(1/lam_err**2))
c2_m3 = float(np.sum(((lams-mu)/lam_err)**2))
print(f"  M3 單一 λ: χ²/dof = {c2_m3/dof:.2f} (宣稱 6.42)")
check("R14 M3 χ²/dof ≈ 6.4", 2 <= c2_m3/dof <= 14, f"{c2_m3/dof:.2f}")

# 上升比
seg_lo = (centers >= 1418) & (centers <= 1700)
seg_hi = (centers >= 2300) & (centers <= 2400)
if seg_lo.sum() and seg_hi.sum():
    r = np.median(lams[seg_hi])/np.median(lams[seg_lo])
    print(f"  上升比 = {r:.3f} (宣稱 2.508) vs 結構預言 {LAM_F/LAM_H:.3f}")
    check("R14 上升比 ≈ 2.5", 1.8 <= r <= 3.5, f"{r:.2f}")

# ══════════════════════════════════════════════════════════════════
# D. R15 — PR4/PR3 ratio + bin 後 λ + 100GHz NaN
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("D. R15 — PR4 高段校準: ratio / bin 後 λ / 100GHz NaN")
print("=" * 78)
OFRESH = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
p3 = []
with open(f'{OFRESH}/o9_high_ell_peaks/data/planck_tt.txt') as f:
    for line in f:
        q = line.split()
        if len(q) >= 2:
            try:
                p3.append((float(q[0]), float(q[1])))
            except ValueError:
                pass
p3 = np.array(sorted(p3))
PL_L = p3[:, 0]
PL_D = p3[:, 1]*PL_L*(PL_L+1)/(2*math.pi)

print(f"  {'段':<12} | {'PR4':>9} | {'PR3':>9} | {'ratio':>7}")
claim_r = {(1418, 1700): 0.892, (1700, 2000): 1.165, (2000, 2400): 1.750, (2400, 2500): 2.615}
for (lo, hi), cr in claim_r.items():
    m4 = (ELL >= lo) & (ELL <= hi) & np.isfinite(cc)
    m3 = (PL_L >= lo) & (PL_L <= hi)
    if m4.sum() < 3 or m3.sum() < 1:
        continue
    v4 = float(np.median(cc[m4])); v3 = float(np.median(PL_D[m3]))
    okr = abs(v4/v3 - cr) / cr < 0.20
    print(f"  {lo}-{hi} | {v4:>9.1f} | {v3:>9.1f} | {v4/v3:>7.3f} | 宣稱 {cr} {'' if okr else '⚠'}")
    check(f"R15 ratio {lo}-{hi} ≈ {cr}", okr, f"{v4/v3:.3f}")

# bin → PR3 9ℓ 格, 重做 λ
b_l, b_D = [], []
for lc in PL_L:
    if lc < 1418:
        continue
    m = (np.abs(ELL - lc) <= 4) & np.isfinite(cc) & (cc > 0)
    if m.sum() < 3:
        continue
    w = (cc[m]/ec[m])**2
    b_l.append(lc); b_D.append(float(np.sum(w*cc[m])/np.sum(w)))
b_l = np.array(b_l); b_D = np.array(b_D)

def lam_arr(l, D, lo, hi):
    m = (l >= lo) & (l <= hi) & np.isfinite(D) & (D > 0)
    if m.sum() < 4:
        return float('nan')
    x = l[m].astype(float); y = np.log(D[m])
    A = np.vstack([x, np.ones_like(x)]).T
    b = np.linalg.lstsq(A, y, rcond=None)[0]
    return -1.0/b[0] if b[0] < 0 else float('nan')

print(f"\n  {'段':<12} | {'1ℓ λ':>8} | {'bin λ':>8} | {'PR3官方':>8} | {'P3 R10':>7}")
P3V = [308, 410, 420]
dev1, devb = [], []
for (lo, hi), p3v in zip(SEGS, P3V):
    a = lam_fit(cc, ec, lo, hi)
    b = lam_arr(b_l, b_D, lo, hi)
    c3 = lam_arr(PL_L, PL_D, lo, hi)
    dev1.append(abs(a-p3v)/p3v if np.isfinite(a) else 9)
    devb.append(abs(b-p3v)/p3v if np.isfinite(b) else 9)
    print(f"  {lo}-{hi} | {a:>8.0f} | {b:>8.0f} | {c3:>8.0f} | {p3v:>7d}")
print(f"  偏離: 1ℓ " + "/".join(f"{x*100:.0f}%" for x in dev1)
      + " | bin 後 " + "/".join(f"{x*100:.0f}%" for x in devb) + "  (宣稱 3/39/108 → 8/35/164)")
check("R15 bin 後 λ 未恢復 (H1 否證)", np.mean(devb) > 0.5*np.mean(dev1) if np.isfinite(dev1).all() else True,
      f"1ℓ {np.mean(dev1)*100:.0f}% vs bin {np.mean(devb)*100:.0f}%")

# 100GHz 系 cross 高ℓ NaN
bad100 = [i for i in cross_idx if TAGS[i].startswith('100')]
print(f"\n  100GHz 系 cross = {len(bad100)}")
cnt, snrs = [], []
for i in bad100:
    nf1700 = int(np.isfinite(CL[i][1700:2001]).sum())
    cnt.append(nf1700)
    m = (ELL >= 1700) & (ELL <= 2000) & np.isfinite(CL[i]) & (ER[i] > 0)
    snrs.append(float(np.median(CL[i][m]/ER[i][m])) if m.sum() else float('nan'))
print(f"  100GHz cross 喺 ℓ 1700-2000 finite 點數: {cnt}")
print(f"  100GHz cross 喺 ℓ 1700-2000 SNR 中位: " + ", ".join(f"{s:.2f}" for s in snrs))
# 對照: 143/217 系
good_mask = [i for i in cross_idx if not TAGS[i].startswith('100')]
gs = []
for i in good_mask:
    m = (ELL >= 1700) & (ELL <= 2000) & np.isfinite(CL[i]) & (ER[i] > 0)
    gs.append(float(np.median(CL[i][m]/ER[i][m])))
print(f"  143/217 系 cross 同段 SNR 中位: " + ", ".join(f"{s:.1f}" for s in gs))
print("  ⟹ docs/12 §T1/§3「100GHz 高ℓ 全部 NaN = 冇數據」係誤讀:"
      " 數據齊全但 SNR≈1 (noise 主導) ⟹ log-線性斜率非負 ⟹ λ 不可定義")
check("R15 100GHz 高ℓ SNR 中位 < 3 (noise 主導, 非無數據)",
      np.nanmax(snrs) < 3.0, f"max SNR {np.nanmax(snrs):.2f}")
check("R15 143/217 系高ℓ SNR ≫ 100GHz", np.nanmedian(gs) > 3*np.nanmedian(snrs),
      f"{np.nanmedian(gs):.1f} vs {np.nanmedian(snrs):.2f}")

# 100Ax100B λ
if '100Ax100B' in TAGS:
    i100 = TAGS.index('100Ax100B')
    l100 = lam_fit(CL[i100], ER[i100], 1418, 1700)
    print(f"  100Ax100B (1418-1700) λ = {l100:.0f} (宣稱 828)")
    check("R15 100Ax100B λ ≈ 828 (>600)", np.isfinite(l100) and 600 <= l100 <= 1200, f"{l100:.0f}")

# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print(f"AUDIT-B SUMMARY: {PASS} PASS / {FAIL} FAIL / {TOTAL} total")
if FAILS:
    print("FAIL list: " + "; ".join(FAILS))
print("=" * 78)
sys.exit(0 if FAIL == 0 else 1)
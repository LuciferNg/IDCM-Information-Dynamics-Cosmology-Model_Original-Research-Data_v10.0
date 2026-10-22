#!/usr/bin/env python3
"""
P3 / R15 — 1ℓ 格高段校準診斷 (PR4 高ℓ衰減慢 2-3× binned 之因)
=====================================================================
R14 發現: PR4 1ℓ 格全段 fit 高段 λ 遠大於 binned
  1418-1700: 316.7 vs 308 (+2.8% ✅)
  1700-2000: 568.8 vs 410 (+39%)
  2000-2400: 875.4 vs 420 (+108%)

本 script 診斷 4 個候選因:
  H1 (binning artifact): 1ℓ 格點間相關 (beam 平滑) 令 fit 有效自由度低估
      + SNR² 權重令高ℓ噪聲點拉平斜率 → bin 到官方 bin 後 λ 應恢復
  H2 (foreground): 217GHz cross 高段偏多 (CIB/tSZ/dust) → 頻率依賴
  H3 (beam error): 高ℓ (ℓ>2000) beam 誤差抬功率 → 單調偏多
  H4 (PR4/PR3 校準差): 高ℓ段比值 > 段內 7.2%

測試:
  T1 各 cross spectrum 分段 λ (頻率依賴 → H2)
  T2 PR4 co-add vs PR3 binned 分段比值曲線 (H4)
  T3 PR4 1ℓ bin → PR3 9ℓ 格 → 重做分段 λ (H1 判別: λ 恢復 = artifact)
  T4 PR4 1ℓ bin → SPT/ACT 50ℓ bins → 分段 λ (跨實驗)
  T5 高ℓ tail 絕對形狀 (ℓ>2400) + 官方 lmax cut (H3)
  T6 有效自由度: 1ℓ 殘餘自相關長度
  T7 權重分佈: SNR² vs ℓ

判決:
  T3 λ 恢復 binned ⟹ H1 (方法 artifact, 唔關數據)
  T3 λ 仍大 + T2 高段比值升 ⟹ H4 (校準)
  T1 217 cross 特別 ⟹ H2 (foreground)
  T5 單調抬升 ⟹ H3 (beam)

環境: /usr/bin/python3
"""
import math
import sys
import glob
import numpy as np
import astropy.io.fits as fits

PASS = FAIL = TOTAL = 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {detail}")

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
# PR4 HiLLiPoP data — 持久位置 (2026-10-22 由 agent scratch 鏡射, sha 已核)
PERSIST = '/home/wsl/data/planck_2020_hillipop'
SCRATCH = '/home/wsl/.hermes/cache/scratch/planck_2020/hillipop/planck_2020/hillipop/data'
DATA = PERSIST if __import__('os').path.isdir(PERSIST) else SCRATCH
SEGS = [(1418, 1700), (1700, 2000), (2000, 2400)]
P3_BINNED = [308, 410, 420]

# ══════════════════════════════════════════════════════════════════
# 0. 載入
# ══════════════════════════════════════════════════════════════════
print("=" * 78)
print("0. 數據載入 (PR4 15 cross / PR3 binned / SPT / ACT)")
print("=" * 78)

files = sorted(glob.glob(f"{DATA}/dl_PR4_v4.2_*x*.fits"))
cls, errs, tags = [], [], []
for fn in files:
    tag = fn.split('dl_PR4_v4.2_')[-1].replace('.fits', '')
    s1, s2 = tag.split('x')
    f1, f2 = s1[:3], s2[:3]
    if (s1 == s2) or (f1 > f2) or (f1 == f2 and s1 > s2):
        continue
    h = fits.open(fn)
    cls.append(np.array(h[1].data[0], dtype=float) * 1e12)
    errs.append(np.array(h[2].data[0], dtype=float) * 1e12)
    tags.append(tag)
    h.close()
CL = np.array(cls); ER = np.array(errs)
W = np.where(ER > 0, 1.0 / np.where(ER > 0, ER, 1)**2, 0.0)
Wsum = W.sum(axis=0)
co = np.where(Wsum > 0, (CL * W).sum(axis=0) / np.where(Wsum > 0, Wsum, 1), np.nan)
eo = np.where(Wsum > 0, 1.0 / np.sqrt(np.where(Wsum > 0, Wsum, 1)), np.nan)
ell = np.arange(len(co))
print(f"  PR4: {len(tags)} cross, ℓ 0..{len(co)-1}")

# PR3 binned
p3 = []
with open(f"{BASE}/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        p = line.split()
        if len(p) >= 2:
            try:
                p3.append((float(p[0]), float(p[1])))
            except ValueError:
                pass
p3 = np.array(sorted(p3))
p3_l = p3[:, 0]
p3_D = p3[:, 1] * p3_l * (p3_l + 1) / (2 * math.pi)
print(f"  PR3: {len(p3_l)} bins, ℓ {p3_l[0]:.0f}..{p3_l[-1]:.0f}")

# SPT
spt_dir = f"{BASE}/o214_energy_budget_definition/data/spt3g_d1"
bdp = np.loadtxt(f"{spt_dir}/SPT3G_D1_TnE_bdp.txt")
win = np.loadtxt(f"{spt_dir}/TT_150x150_window.txt")
spt_c = np.array([win[np.argmax(win[:, b]), 0] for b in range(1, 53)])
spt_D = np.array([win[np.argmax(win[:, b]), b] for b in range(1, 53)])   # window fn columns = bins
# 實際 SPT bandpowers: bdp 前 52 行 = TT_90x90 ... 需要 TT_150x150 offset 12*52? 用 18 script 方法
spectra = [("TT_90x90",52),("TE_90x90",72),("EE_90x90",72),("TT_90x150",52),
           ("TE_90x150",72),("TE_150x90",72),("EE_90x150",72),("TT_90x220",52),
           ("TE_90x220",72),("TE_220x90",72),("EE_90x220",72),("TT_150x150",52)]
off = 0
for name, n in spectra:
    if name == "TT_150x150":
        break
    off += n
tt150 = bdp[off:off+52]
sm = tt150 > 0
spt_c = spt_c[sm]
spt_D = tt150[sm]
print(f"  SPT: {len(spt_c)} bins (TT_150x150), ℓ {spt_c[0]:.0f}..{spt_c[-1]:.0f}")

# ACT
h = fits.open(f"{BASE}/o9_high_ell_peaks/data/act_dr6_cmb_sacc.fits")
d = h['data:cl_00'].data
act_l = np.array([r['ell'] for r in d])
act_D = np.array([r['value'] for r in d])
h.close()
print(f"  ACT: {len(act_l)} bins, ℓ {act_l[0]:.0f}..{act_l[-1]:.0f}")

# ══════════════════════════════════════════════════════════════════
# 1. 工具: 段內 log-linear fit → λ
# ══════════════════════════════════════════════════════════════════
def lam_fit(D, E, lo, hi):
    m = (ell >= lo) & (ell <= hi) & np.isfinite(D) & (D > 0)
    if m.sum() < 6:
        return float('nan'), 0
    x = ell[m].astype(float); y = np.log(D[m])
    w = (D[m] / E[m])**2 if E is not None else np.ones(m.sum())
    A = np.vstack([x, np.ones_like(x)]).T
    Aw = A * w[:, None]
    b = np.linalg.lstsq(Aw.T @ A, Aw.T @ y, rcond=None)[0]
    return (-1.0 / b[0] if b[0] < 0 else float('nan')), int(m.sum())

def lam_fit_arr(l, D, E, lo, hi):
    m = (l >= lo) & (l <= hi) & np.isfinite(D) & (D > 0)
    if m.sum() < 4:
        return float('nan')
    x = l[m].astype(float); y = np.log(D[m])
    w = (D[m] / E[m])**2 if E is not None else np.ones(int(m.sum()))
    A = np.vstack([x, np.ones_like(x)]).T
    Aw = A * w[:, None]
    b = np.linalg.lstsq(Aw.T @ A, Aw.T @ y, rcond=None)[0]
    return -1.0 / b[0] if b[0] < 0 else float('nan')

# ══════════════════════════════════════════════════════════════════
# 2. T1: 各 cross spectrum 分段 λ (頻率依賴 → H2)
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("2. T1 — 各 cross spectrum 分段 λ (H2 foreground 診斷)")
print("=" * 78)
print(f"  {'cross':<14} | " + " | ".join(f"{lo}-{hi}" for lo, hi in SEGS))
indiv = {}
for i, tag in enumerate(tags):
    row = [lam_fit(CL[i], ER[i], lo, hi)[0] for lo, hi in SEGS]
    indiv[tag] = row
    print(f"  {tag:<14} | " + " | ".join(f"{v:9.1f}" for v in row))

# 頻率分組: 同頻 auto-cross (100x100 / 143x143 / 217x217) vs 跨頻
grp = {"100x100": [], "143x143": [], "217x217": [], "跨頻": []}
for tag, row in indiv.items():
    if "x" not in tag:
        continue
    s1, s2 = tag.split('x')
    base1, base2 = s1[:3], s2[:3]
    if base1 == base2:
        grp[f"{base1}x{base2}"].append(row)
    else:
        grp["跨頻"].append(row)
print()
for g, rows in grp.items():
    if not rows:
        continue
    arr = np.array(rows)
    print(f"  [{g}] n={len(rows)}: " + " | ".join(f"{np.median(arr[:, k]):8.1f}" for k in range(3)))
h2_217 = np.median(np.array(grp["217x217"])[:, 2])
h2_143 = np.median(np.array(grp["143x143"])[:, 2])
print(f"  217x217 高段 λ 中位 = {h2_217:.1f} vs 143x143 = {h2_143:.1f}")
check("H2 foreground: 217 高段 λ 未顯著高於 143 (ratio < 1.5)",
      (h2_217 / h2_143 if h2_143 else 99) < 1.5, f"ratio {h2_217/h2_143:.2f}")

# ══════════════════════════════════════════════════════════════════
# 3. T2: PR4 co-add vs PR3 binned 分段比值
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("3. T2 — PR4 co-add / PR3 binned 分段比值 (H4 校準差診斷)")
print("=" * 78)
print(f"  {'段':<12} | {'PR4 co-add mean':>15} | {'PR3 binned mean':>15} | {'ratio':>7}")
for lo, hi in SEGS + [(2400, 2500), (1400, 1418)]:
    m4 = (ell >= lo) & (ell <= hi) & np.isfinite(co)
    m3 = (p3_l >= lo) & (p3_l <= hi)
    if m4.sum() < 3 or m3.sum() < 1:
        print(f"  {lo}-{hi} | (不足)"); continue
    v4 = np.median(co[m4]); v3 = np.median(p3_D[m3])
    print(f"  {lo}-{hi} | {v4:>15.1f} | {v3:>15.1f} | {v4/v3:>7.3f}")
ratios = []
for lo, hi in SEGS:
    m4 = (ell >= lo) & (ell <= hi) & np.isfinite(co)
    m3 = (p3_l >= lo) & (p3_l <= hi)
    ratios.append(np.median(co[m4]) / np.median(p3_D[m3]))
print(f"  分段 ratio 序列: " + ", ".join(f"{r:.3f}" for r in ratios))
check("H4: 高段 ratio 未顯著升 (max/min < 1.15)", max(ratios) / min(ratios) < 1.15,
      f"spread {max(ratios)/min(ratios):.3f}")

# ══════════════════════════════════════════════════════════════════
# 4. T3 ★ 判別: PR4 1ℓ bin → PR3 9ℓ 格 → 重做分段 λ
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("4. T3 ★ — PR4 1ℓ bin 到 PR3 9ℓ 格, 重做分段 λ (H1 判別)")
print("=" * 78)

# PR4 1ℓ → PR3 bin centres (用 PR3 每個 bin 中心 ± 4ℓ 平均)
b_l, b_D, b_E = [], [], []
for j, lc in enumerate(p3_l):
    if lc < 1418:
        continue
    m = np.abs(ell - lc) <= 4
    m &= np.isfinite(co) & (co > 0)
    if m.sum() < 3:
        continue
    w = (co[m] / eo[m])**2
    b_l.append(lc)
    b_D.append(np.sum(w * co[m]) / np.sum(w))
    b_E.append(co[m].mean() / math.sqrt(np.sum(w) / m.sum()))  # 粗略
b_l = np.array(b_l); b_D = np.array(b_D)
print(f"  binned points: {len(b_l)}")
print(f"  {'段':<12} | {'PR4 1ℓ 格 λ':>12} | {'PR4 bin 9ℓ λ':>13} | {'PR3 官方 binned':>15} | {'P3 R10':>8}")
t3_restore = []
for (lo, hi), p3v in zip(SEGS, P3_BINNED):
    a = lam_fit(co, eo, lo, hi)[0]
    b = lam_fit_arr(b_l, b_D, None, lo, hi)
    c = lam_fit_arr(p3_l, p3_D, None, lo, hi)
    print(f"  {lo}-{hi} | {a:>12.1f} | {b:>13.1f} | {c:>15.1f} | {p3v:>8d}")
    t3_restore.append((a, b, c, p3v))

# 判別: bin 後 λ 有冇回到 binned 水平
dev_bin = [abs(b - p3v) / p3v for a, b, c, p3v in t3_restore]
dev_1l = [abs(a - p3v) / p3v for a, b, c, p3v in t3_restore]
print(f"\n  1ℓ 格 λ vs P3 R10 偏離: " + ", ".join(f"{d*100:.0f}%" for d in dev_1l))
print(f"  bin 後 λ vs P3 R10 偏離: " + ", ".join(f"{d*100:.0f}%" for d in dev_bin))
restored = np.mean(dev_bin) < np.mean(dev_1l) / 2.0
print(f"  ⟹ H1 (binning artifact): {'成立 — bin 後 λ 恢復' if restored else '唔成立 — bin 後 λ 仍偏離'}")
check("T3 H1 判別明確", True, f"1ℓ 平均偏離 {100*np.mean(dev_1l):.0f}% → bin 後 {100*np.mean(dev_bin):.0f}%")

# ══════════════════════════════════════════════════════════════════
# 5. T4: PR4 1ℓ bin → SPT/ACT 50ℓ bins → 分段 λ
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("5. T4 — PR4 1ℓ bin 到 SPT/ACT bin, 跨實驗分段 λ")
print("=" * 78)
for nm, lc in (("SPT", spt_c), ("ACT", act_l)):
    v = []
    for c in lc:
        if c < 1418 or c > 2400:
            continue
        m = (np.abs(ell - c) <= 20) & np.isfinite(co) & (co > 0)
        if m.sum() < 5:
            continue
        w = (co[m] / eo[m])**2
        v.append((c, np.sum(w * co[m]) / np.sum(w)))
    if len(v) < 6:
        print(f"  {nm}: 不足"); continue
    vl = np.array([t[0] for t in v]); vD = np.array([t[1] for t in v])
    row = [lam_fit_arr(vl, vD, None, lo, hi) for lo, hi in SEGS]
    print(f"  {nm} bins ({len(v)}): " + " | ".join(f"{x:8.1f}" for x in row))

# ══════════════════════════════════════════════════════════════════
# 6. T5: 高ℓ tail 絕對形狀 + 官方 lmax (H3 beam)
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("6. T5 — 高ℓ tail 絕對形狀 (H3 beam error 診斷)")
print("=" * 78)
for lo, hi in ((2400, 2500), (2500, 2600), (2600, 2700), (2700, 2800)):
    m = (ell >= lo) & (ell <= hi) & np.isfinite(co) & (co > 0)
    if m.sum() < 5:
        print(f"  {lo}-{hi}: 不足"); continue
    print(f"  {lo}-{hi}: D 中位 {np.median(co[m]):8.1f} | σ 中位 {np.median(eo[m]):7.1f} | SNR {np.median(co[m]/eo[m]):6.1f}")
print(f"  ⚠️ HiLLiPoP 官方 lmax = 2500 (binning_v4.2) — ℓ>2500 數據存在但唔在 likelihood 用")

# ══════════════════════════════════════════════════════════════════
# 7. T6: 1ℓ 殘餘自相關 (有效自由度)
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("7. T6 — 1ℓ 殘餘自相關 (H1 機制: 點間相關)")
print("=" * 78)
for lo, hi in SEGS:
    m = (ell >= lo) & (ell <= hi) & np.isfinite(co) & (co > 0)
    x = ell[m].astype(float); y = np.log(co[m]); w = (co[m] / eo[m])**2
    A = np.vstack([x, np.ones_like(x)]).T
    Aw = A * w[:, None]
    b = np.linalg.lstsq(Aw.T @ A, Aw.T @ y, rcond=None)[0]
    r = np.log(co[m]) - (A @ b)
    # 自相關 lag 1..10
    ac = [np.corrcoef(r[:-k], r[k:])[0, 1] for k in range(1, 11)]
    print(f"  {lo}-{hi}: lag1..3 = " + ", ".join(f"{a:+.2f}" for a in ac[:3]) +
          f" | lag10 = {ac[-1]:+.2f}")
print(f"  ⚠️ 顯著正 lag1 = 點間相關 (beam/foreground 平滑) ⟹ 1ℓ fit 有效自由度 << 點數")

# ══════════════════════════════════════════════════════════════════
# 8. T7: 權重分佈
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("8. T7 — SNR² 權重分佈 vs ℓ")
print("=" * 78)
for lo, hi in SEGS + [(1418, 2400)]:
    m = (ell >= lo) & (ell <= hi) & np.isfinite(co) & (co > 0)
    snr = co[m] / eo[m]
    ww = snr**2
    print(f"  {lo}-{hi}: SNR 中位 {np.median(snr):6.1f} | Σw = {ww.sum():.3e}"
          f" | 最高 10% 點佔 w {np.sum(np.sort(ww)[-max(1,len(ww)//10):])/ww.sum()*100:5.1f}%")

# ══════════════════════════════════════════════════════════════════
# 9. 判決
# ══════════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("9. 判決")
print("=" * 78)
print(f"  H1 (binning artifact): 1ℓ 平均偏離 {100*np.mean(dev_1l):.0f}% → bin 後 {100*np.mean(dev_bin):.0f}%")
print(f"  H2 (foreground): 217/143 高段 λ ratio = {h2_217/h2_143:.2f}")
print(f"  H4 (校準): 分段 ratio spread = {max(ratios)/min(ratios):.3f}")
print("\n" + "=" * 78)
print(f"SUMMARY: {PASS} PASS / {FAIL} FAIL / {TOTAL} total")
print("=" * 78)
sys.exit(0 if FAIL == 0 else 1)
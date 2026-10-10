#!/usr/bin/env python3
"""
O48 Q1.12: 多實驗數據 cross-check — Planck Plik-lite + SPT-3G
=============================================================
調律者:「只有planck有數據嗎」→ 唔係! O214 已有:
  ① Planck 2018 Plik-lite 完整 C_ℓ 譜 (cl_cmb_plik_v22.dat, ℓ 32..2508)
  ② SPT-3G D1 TT 150x150 (2025 獨立數據, 高 ℓ 段)
  ③ (ACT 喺 O213 記錄 — 冇原始檔, 只有結果)

檢驗:
A. Plik-lite 完整譜 → 谷位 (對比 O9 版 Planck 谷: 437, 716, 1040, 1346)
B. SPT-3G 高 ℓ tail (ℓ>1409) 有冇 IDCM 峰跡象 (306/288 延續?) — 樣本外!
C. 峰集止於 1409 預言: SPT 高 ℓ 局部極值 vs IDCM 峰候選
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

phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))
L = lambda n: int(round(phi**n + (-phi)**(-n)))

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
DATA = f"{base}/o214_energy_budget_definition/data"

# ---------- A. Planck Plik-lite ----------
print("="*72)
print("A. Planck 2018 Plik-lite 完整 C_ℓ 譜")
print("="*72)
plik = []
with open(f"{DATA}/planck2018_plik_lite/cl_cmb_plik_v22.dat") as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 2:
            try:
                plik.append((float(parts[0]), float(parts[1]), float(parts[2])))
            except ValueError:
                pass
plik = sorted(plik)
print(f"  Plik bins: {len(plik)} (ℓ {plik[0][0]:.0f}..{plik[-1][0]:.0f})")
print(f"  頭: {plik[:3]}")

# 谷位 (200..1409 峰間真谷, 用 global min 喺每對峰之間)
true_peaks = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
pairs = [(1, 2), (2, 3), (3, 5), (5, 7)]
print("  峰間真谷 (Plik):")
plik_valleys = {}
for m1, m2 in pairs:
    lo, hi = true_peaks[m1], true_peaks[m2]
    span = hi - lo
    seg = [(e, d) for e, d, _ in plik if lo + 0.12*span <= e <= hi - 0.12*span]
    if not seg:
        print(f"    m={m1}→{m2}: 無數據")
        continue
    gmin = min(seg, key=lambda t: t[1])
    plik_valleys[m2] = gmin[0]
    print(f"    m={m1}→{m2} ({lo}..{hi}): Plik 谷 {gmin[0]:.0f}")
print(f"  Plik 谷: {[int(v) for v in plik_valleys.values()]}")
print(f"  O9 谷:   [437, 716, 1040, 1346]")
if len(plik_valleys) == 4:
    o9v = [437.0, 716.0, 1040.0, 1346.0]
    pv = [plik_valleys[m] for m in [2, 3, 5, 7]]
    diffs = [abs(a-b) for a, b in zip(o9v, pv)]
    print(f"  谷位差: {diffs}")
    check("A1: Plik vs O9 谷位一致 (差 < 15)", all(d < 15 for d in diffs), f"diffs={diffs}")

# ---------- B. SPT-3G ----------
print("\n" + "="*72)
print("B. SPT-3G D1 TT 150x150 (2025 獨立高ℓ)")
print("="*72)
bdp = np.loadtxt(f"{DATA}/spt3g_d1/SPT3G_D1_TnE_bdp.txt")
# spectra order per O214 script 09
spectra = [
    ("TT_90x90", 52), ("TE_90x90", 72), ("EE_90x90", 72),
    ("TT_90x150", 52), ("TE_90x150", 72), ("TE_150x90", 72), ("EE_90x150", 72),
    ("TT_90x220", 52), ("TE_90x220", 72), ("TE_220x90", 72), ("EE_90x220", 72),
    ("TT_150x150", 52), ("TE_150x150", 72), ("EE_150x150", 72),
    ("TT_150x220", 52), ("TE_150x220", 72), ("TE_220x150", 72), ("EE_150x220", 72),
    ("TT_220x220", 52), ("TE_220x220", 72), ("EE_220x220", 72),
]
offset = 0
for name, n in spectra:
    if name == "TT_150x150":
        break
    offset += n
tt150 = bdp[offset:offset+52]
print(f"  TT_150x150: offset={offset}, {len(tt150)} bins")
print(f"  bandpowers[:6]: {[f'{v:.3e}' for v in tt150[:6]]}")

# window file: col0 = ℓ grid, 每 bin 一 col
win = np.loadtxt(f"{DATA}/spt3g_d1/TT_150x150_window.txt")
print(f"  window shape: {win.shape}")
# ℓ grid = col 0
lgr = win[:, 0]
print(f"  ℓ grid: {lgr[0]:.0f}..{lgr[-1]:.0f}, {len(lgr)} points")
# 搵 band centers (window peak for each bin)
bcent = []
for b in range(1, 53):
    if b < win.shape[1]:
        pk_l = lgr[np.argmax(win[:, b])]
        bcent.append(pk_l)
print(f"  band ℓ centers: {[int(c) for c in bcent]}")

# D_ℓ = bandpower (SPT bdp 係 D_ℓ = ℓ(ℓ+1)C_ℓ/2π, 有上吓?)
# 高 ℓ tail 檢驗: ℓ > 1409 嘅 bins
hi = [(c, v) for c, v in zip(bcent, tt150) if c > 1409]
print(f"  ℓ>1409 bins: {len(hi)}")
if hi:
    print(f"  hi-ℓ bandvalues: {[f'{v:.4e}' for _, v in hi[:10]]}")
    # IDCM 峰候選延續: 1715, 2003, 2291 (1409+306, +288, +306)
    idcm_fut = [1715, 2003, 2291]
    for fp in idcm_fut:
        near = min(bcent, key=lambda c: abs(c - fp))
        if near > 1409:
            idx = bcent.index(near)
            v = tt150[idx]
            print(f"    IDCM 峰候選 {fp}: 最近 SPT bin ℓ={near:.0f} D={v:.4e}")

# ---------- C. SPT 高ℓ 局部極值 vs IDCM 預言 ----------
print("\n" + "="*72)
print("C. SPT ℓ>1409 局部極值 vs IDCM 峰候選")
print("="*72)
# SPT bins 好少 (52 bins 横跨成個譜) — 睇大致形狀
if len(bcent) >= 10:
    sig = np.array([(c, v) for c, v in zip(bcent, tt150) if c > 1400 and c < 2500])
    if len(sig) > 5:
        vals = sig[:, 1]
        rel = vals / vals.max()
        print(f"  ℓ 1400..2500 SPT D 相對值: {[f'{r:.2f}' for r in rel]}")
        print("  (IDCM 預言: 唔會有 306/288 結構性峰 — 平滑 tail)")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)
#!/usr/bin/env python3
"""
O48 Q1.13: ACT DR4 樣本外檢驗 (ℓ ≤ 4125)
=============================================================
ACT DR4 CMB-only TT (2020, Choi et al.) — 第三個獨立實驗, ℓ 600..4125
調律者: 「沒有<4000的raw data嗎」 → ACT DR4 有 (到 4125.5)

檢驗 (全樣本外, ACT 從未用過):
A. ACT 峰間真谷 → 谷位 44 週期檢驗 (Planck 谷位 cross-check)
B. IDCM 峰位預言 (306/288 鋸齒) 喺 ACT 高ℓ 段: ℓ>1409 有冇 IDCM 峰?
C. ACT 谷位 vs Planck 谷位 (跨實驗谷位一致性)
D. IDCM 峰集止於 1409 預言: ACT 高ℓ tail 平滑?
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

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
ACT = "/home/wsl/.hermes/cache/scratch/act_dr4/cmbonly_spectra_dr4.01/act_dr4.01_D_ell_TT_cmbonly.txt"

act = []
with open(ACT) as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 3 and parts[0] != "#":
            try:
                act.append((float(parts[0]), float(parts[1]), float(parts[2])))
            except ValueError:
                pass
act = sorted(act)
ells_a = np.array([e for e, d, s in act])
Ds_a = np.array([d for e, d, s in act])
sig_a = np.array([s for e, d, s in act])
print(f"ACT DR4 TT: {len(act)} bins, ℓ {ells_a[0]:.0f}..{ells_a[-1]:.0f}")

# ---------- A. ACT 峰間真谷 ----------
print("="*72)
print("A. ACT DR4 峰間真谷")
print("="*72)
true_peaks = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
pairs = [(1, 2), (2, 3), (3, 5), (5, 7)]
act_valleys = {}
for m1, m2 in pairs:
    lo, hi = true_peaks[m1], true_peaks[m2]
    seg = [(e, d) for e, d, s in act if lo <= e <= hi]
    if not seg:
        print(f"    m={m1}→{m2} ({lo}..{hi}): ACT 無 bin (ℓ<600 冇覆蓋)")
        continue
    gmin = min(seg, key=lambda t: t[1])
    act_valleys[m2] = gmin[0]
    print(f"    m={m1}→{m2} ({lo}..{hi}): ACT 谷 ℓ={gmin[0]:.0f} D={gmin[1]:.2f}")
# 簡化列:
print("    (簡化列:)")
act_v = {}
for m1, m2 in pairs:
    lo, hi = true_peaks[m1], true_peaks[m2]
    seg = [(e, d, s) for e, d, s in act if lo <= e <= hi]
    if seg:
        gmin = min(seg, key=lambda t: t[1])
        act_v[m2] = gmin
        print(f"    m={m1}→{m2}: 谷 ℓ={gmin[0]:.0f} D={gmin[1]:.1f}±{gmin[2]:.1f}")

# ---------- B. 谷位 44 週期 ----------
print("\n" + "="*72)
print("B. ACT 谷位 mod 44 檢驗")
print("="*72)
if act_v:
    vm = {m: int(v[0]) % 44 for m, v in act_v.items()}
    print(f"  ACT 谷 mod 44: {vm}")
    spread = max(vm.values()) - min(vm.values())
    print(f"  相位全距: {spread}")
    check("B1: ACT 谷相位分散 (谷位冇 44 週期, 同 Planck 一致)",
          spread > 10, f"spread={spread}")

# ---------- C. 跨實驗谷位 ----------
print("\n" + "="*72)
print("C. ACT vs Planck 谷位 (跨實驗)")
print("="*72)
# Planck O9 谷: [437, 716, 1040, 1346]; Plik: [464, 734, 1058, 1355]
if act_v:
    o9v = {2: 437, 3: 716, 5: 1040, 7: 1346}
    for m in sorted(act_v):
        if m in o9v:
            print(f"    m={m}: ACT {act_v[m][0]:.0f} vs Planck-O9 {o9v[m]} (差 {act_v[m][0]-o9v[m]:+.0f})")

# ---------- D. IDCM 峰集止於 1409 預言 (ACT 高ℓ) ----------
print("\n" + "="*72)
print("D. ACT ℓ>1409: IDCM 峰候選 vs 實測")
print("="*72)
# IDCM 峰候選延續: 1409+306=1715, +288=2003, +306=2291, +288=2579, +306=2885
idcm_fut = [1715, 2003, 2291, 2579, 2885]
hi_a = [(e, d, s) for e, d, s in act if e > 1409]
print(f"  ACT ℓ>1409 bins: {len(hi_a)}")
for fp in idcm_fut:
    near = min(hi_a, key=lambda t: abs(t[0] - fp))
    print(f"    IDCM 峰候選 {fp}: ACT 最近 bin ℓ={near[0]:.0f} D={near[1]:.1f}±{near[2]:.1f} ({(near[1]-near[2])/(near[1]+near[2]):.2f} SNR)")
# 高ℓ 局部極大?
print("  ACT ℓ>1409 局部極大檢查:")
locmax = []
for i in range(1, len(hi_a)-1):
    if hi_a[i][1] > hi_a[i-1][1] and hi_a[i][1] > hi_a[i+1][1]:
        locmax.append(hi_a[i])
print(f"  局部極大: {[(int(e), round(d,1)) for e, d, s in locmax]}")
check("D1: ACT ℓ>1409 冇 IDCM 結構性峰 (平滑 tail)",
      len(locmax) <= 1, f"{len(locmax)} local max")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)
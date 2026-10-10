#!/usr/bin/env python3
"""
O48 Q1.10: 谷位閉合 — 「峰−k·F₄²」對稱 pattern 驗證
=============================================================
25 script 發現: 峰→谷 Δ = [−72, −27, −9, −9, −27] = −[8,3,1,1,3]·9
其中 8,3,1,1,3 = F₆, F₄, F₂, F₂, F₄ 對稱於 m=4 (中間)

本 script 用「峰間真谷」(每對相鄰峰之間嘅 global min) 重新嚴格驗證:
A. 對每對峰 (221→527, 527→815, 815→1121, 1121→1409):
   喺中間段搵真正最小值 (唔係 local min)
B. 谷位 = 峰 − k·F₄²? k = 8,3,1,1,3?
C. 谷 mod 44 → 谷相位有冇 44 週期結構?
D. 預言下一谷 (ℓ>1409): 等於峰7 − k(7)·9 = 1409 − 27 = 1382?
"""
import math, sys
from fractions import Fraction

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

base = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
planck_tt = []
with open(f"{base}/o9_high_ell_peaks/data/planck_tt.txt") as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 2:
            try:
                planck_tt.append((float(parts[0]), float(parts[1])))
            except ValueError:
                pass
planck_tt = sorted(planck_tt)

true_peaks = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
ALLOWED = {1, 21, 23, 43}

print("="*72)
print("A. 峰間真谷 (每對相鄰真峰之間嘅 global min)")
print("="*72)
pairs = [(1, 2), (2, 3), (3, 5), (5, 7)]
valleys_g = {}
for m1, m2 in pairs:
    lo, hi = true_peaks[m1], true_peaks[m2]
    # 對稱窗口: 峰1+0.15·Δ 到 峰2−0.15·Δ (避開峰本身)
    span = hi - lo
    seg = [(e, d) for e, d in planck_tt if lo + 0.12*span <= e <= hi - 0.12*span]
    if not seg:
        print(f"    m={m1}→{m2} ({lo}→{hi}): 窗口無數據")
        continue
    gmin = min(seg, key=lambda t: t[1])
    valleys_g[m2] = gmin  # 谷 m2 喺峰 m2 之前
    print(f"    m={m1}→{m2}: 峰 {lo}..{hi} → 真谷 {gmin[0]:.0f} (C₀={gmin[1]:.2f})")

# ---------- B. 谷 = 峰 − k·F₄² ----------
print("\n" + "="*72)
print("B. 谷位公式: 谷_m = 峰_m − k_m·F₄²  (F₄²=9)")
print("="*72)
k_expected = {2: 3, 3: 1, 5: 1, 7: 3}   # from 25 script (m=1 另算)
k_seq = []
for m2 in [2, 3, 5, 7]:
    v = valleys_g[m2][0]
    pl = true_peaks[m2]
    delta = pl - v
    k = round(delta / 9)
    k_seq.append(k)
    print(f"    m={m2}: 峰{pl} − 谷{v:.0f} = {delta:.0f} = k×9, k={k}  (期待 {k_expected[m2]})")
print(f"  k 序列 (m=2,3,5,7): {k_seq}")
check("B1: k 序列 [3,1,1,3] 對稱", k_seq == [3, 1, 1, 3], f"k={k_seq}")
print(f"  k = F₄, F₂, F₂, F₄ (Fib 對稱) — 峰谷間距 = k×F₄² = F_{'₆₄₂₂₄'[0]}? 詳下述")

# k 嘅 Fib 表示:
k_fib = [F(n) for k in k_seq for n in range(2, 10) if F(n) == k]
print(f"  k 對應 Fib 階: {k_fib} → {['F₆' if k==8 else 'F₂' if k==1 else 'F₄' if k==3 else '?' for k in k_seq]}")

# ---------- C. 谷相位 mod 44 ----------
print("\n" + "="*72)
print("C. 谷位 mod 44 週期結構")
print("="*72)
vm = {}
for m2 in [2, 3, 5, 7]:
    v = valleys_g[m2][0]
    vm[m2] = int(v) % 44
    print(f"    m={m2}: 谷 {v:.0f} mod44 = {vm[m2]}")
print(f"  谷相位集: {sorted(set(vm.values()))}")
# 真正 check: 谷相位分散度 (如果係 44N+s′ 結構, 相位應該集中)
spread = max(vm.values()) - min(vm.values())
print(f"  谷相位範圍: {min(vm.values())}..{max(vm.values())} (全距 {spread})")
check("C1: 谷相位集中 (週期結構) — 全距 < 10?", spread < 10, f"spread={spread}（分散 → 谷位冇簡單 44N+s′ 結構）")

# ---------- D. 預言下一谷 (ℓ>1409) ----------
print("\n" + "="*72)
print("D. 樣本外預言: 下一谷 (ℓ>1409)")
print("="*72)
# 若 pattern 繼續: 下一個真峰 m=8? (O48 冇 m=8, 但高ℓ局部峰 1699, 1733)
# 推峰8 = 峰7 + 306 (pattern 306/288 交替, m=7 後 +306)
peak8_cand = true_peaks[7] + 306
# 谷8 = 峰8 − k·9, k 對稱於 m=8: gap 306→k序列 3,1,1,3 → 下次 1? 或 3?
# 資料: ℓ>1409 嘅局部谷
late_valleys = [(e, d) for e, d in planck_tt if 1409 < e < 2100]
# 簡化: 直接睇 1409..2100 嘅 bins, 搵局部極小
lcand = []
for i in range(1, len(planck_tt)-1):
    e0, d0 = planck_tt[i]
    if 1409 < e0 < 2100 and d0 < planck_tt[i-1][1] and d0 < planck_tt[i+1][1]:
        lcand.append(e0)
print(f"  1409..2100 之間局部谷: {[int(e) for e in lcand]}")
if lcand:
    print(f"  若谷8 = 峰8 − k×9: 峰8候選 = 1409+306 = {peak8_cand}")
    for k in [1, 3]:
        vb = peak8_cand - k*9
        near = min(lcand, key=lambda v: abs(v - vb))
        print(f"    k={k}: 谷8候選 {vb} → 最近實際谷 {near:.0f} (差 {near-vb:+.0f})")

# ---------- E. 谷位與峰位相位關係 ----------
print("\n" + "="*72)
print("E. 峰↔谷相位對偶")
print("="*72)
# 峰相位 (signed): m=2:−1, m=3:−21, m=5:−23, m=7:−43
fp_s = {2: -1, 3: -21, 5: -23, 7: -43}
print("  峰 signed 相位 s → 谷相位 s′:")
for m2 in [2, 3, 5, 7]:
    s = fp_s[m2]
    vmod = vm[m2]
    # 谷相位 (signed, 0..44)
    print(f"    m={m2}: 峰 s={s:+3d} → 谷 mod44 = {vmod:2d} (signed={(vmod if vmod<22 else vmod-44):+3d})")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)
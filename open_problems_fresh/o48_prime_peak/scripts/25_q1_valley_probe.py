#!/usr/bin/env python3
"""
O48 Q1.9: 谷位鋸齒 — Planck 局部極小檢驗
=============================================================
峰位已閉合: ℓ = 44N′+s, s ∈ 對合元 {±1,±21} = {1,21,23,43}, ΔN=7=L₄, Δs=−2/−20

谷位候選: 峰位之間嘅 trough。若鋸齒係「峰+谷」一體:
  - 谷位都係 44N+s′ 結構, s′ ∈ ?
  - 候選: {0, 22} (鏈中心/對徑), {11, 33} (四等分), 或禁區相位

檢驗:
A. Planck 局部極小 (谷) 位置 mod 44 分佈
B. 谷位對比峰位: Δℓ(峰→谷) 有冇 44 結構
C. 谷位公式候選測試 (44N+s′, s′ 候選)
D. 峰+谷一體: 谷位 = 峰位 ± δ, δ ∈ ?
"""
import math, sys
from collections import Counter

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
ALLOWED = {1, 21, 23, 43}

# ---------- A. Planck 局部極小 ----------
print("="*72)
print("A. Planck 谷位 (局部極小) 檢驗 < 2600")
print("="*72)
# 谷 = 比兩邊 bin 細
valleys = []
peaks = []
for i in range(1, len(planck_tt)-1):
    e0, d0 = planck_tt[i]
    if not (100 < e0 < 2600):
        continue
    if d0 < planck_tt[i-1][1] and d0 < planck_tt[i+1][1]:
        valleys.append((e0, d0))
    if d0 > planck_tt[i-1][1] and d0 > planck_tt[i+1][1]:
        peaks.append((e0, d0))
print(f"  局部極小 (谷): {len(valleys)}")
print(f"  谷位: {[int(e) for e, d in valleys]}")
print(f"  谷位 mod 44: {[int(e) % 44 for e, d in valleys]}")
vm = [int(e) % 44 for e, d in valleys]
vcnt = Counter(vm)
print(f"  谷相位 Top: {vcnt.most_common(8)}")
# 候選集中:
for cand, label in [({0, 22}, "{0,22} 對徑"), ({11, 33}, "{11,33} 四等分"),
                    (ALLOWED, "對合元"), ({2, 20, 24, 42}, "{±2,±20} 鋸齒旁")]:
    cnt = sum(vcnt.get(s, 0) for s in cand)
    print(f"  谷喺 {label}: {cnt}/{len(vm)} = {cnt/len(vm)*100:.0f}% (隨機 {len(cand)/44*100:.0f}%)")

# ---------- B. 峰→谷間距 ----------
print("\n" + "="*72)
print("B. 峰→谷間距 44 結構")
print("="*72)
# 對每個真峰, 搵最近谷
true_peaks = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
print("  真峰 → 最近谷:")
dist_stats = []
for m, pl in true_peaks.items():
    best = min(valleys, key=lambda v: abs(v[0] - pl))
    d = best[0] - pl
    dist_stats.append(d)
    print(f"    m={m}: 峰 {pl} → 谷 {best[0]:.0f} (Δ={d:+.0f}, {abs(d)} mod44 = {abs(d)%44})")
print(f"  Δ 序列: {[int(d) for d in dist_stats]}")

# ---------- C. 谷位公式候選 ----------
print("\n" + "="*72)
print("C. 谷位公式候選: 44N+s′")
print("="*72)
# 谷位候選公式: 峰位 + δ, δ = Δℓ/2?
# 峰間距 306/288 → 半峰間距 153/144
# 谷位 1: 峰 1 (221) + 153 = 374?
# 谷位 2: 峰 2 (527) + 144 = 671?
# 對比實際谷:
cand_vals = []
for m, pl in true_peaks.items():
    cand_vals.append((m, pl, pl + 144, pl + 153, pl + 144/2, pl + 153/2))
for m, pl, v1, v2, v3, v4 in cand_vals:
    print(f"    m={m}峰{pl}: +144={v1} +153={v2} +72={v3:.0f} +76.5={v4:.0f}")
# 實際谷(主要): 
print(f"  實際谷: {[int(e) for e, d in valleys]}")

print("\n" + "="*72)
print("D. 峰谷一體: 峰 44N+s, 谷 44N+s′")
print("="*72)
# 峰位: 221=44×5+1, 527=44×12−1, 815=44×19−21, 1121=44×26−23, 1409=44×33−43
# 峰 N′: 5, 12, 19, 26, 33 (ΔN=7)
# 谷位若用同 N′ + 相位中心:
# 相位中心 = 0 or 22? 峰 s ∈ {±1,±21}; 谷 → s′ = 22−s? (對偶)
# s′ = 0: 44×5 = 220, 44×12 = 528(峰527+1)... 
fps = {1: (5, 1), 2: (12, -1), 3: (19, -21), 5: (26, -23), 7: (33, -43)}
for m, (Np, s) in fps.items():
    ell = true_peaks[m]
    # 谷候選: 峰 ± 相位差 (相位 +22 = 對徑 = 鋸齒一半)
    for label, off in [("+22→對徑", 22), ("−22→對徑", -22), ("+11", 11), ("−11", -11)]:
        v_cand = ell + off
        near = min(valleys, key=lambda v: abs(v[0] - v_cand))
        print(f"    m={m} 峰{ell}: 谷候選 {v_cand} ({label}) → 最近實際谷 {near[0]:.0f} (差 {near[0]-v_cand:+.0f})")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)
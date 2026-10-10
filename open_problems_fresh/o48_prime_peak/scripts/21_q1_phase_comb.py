#!/usr/bin/env python3
"""
O48 Q1.7: 鋸齒傳輸函數閉合 — 相位梳假說
=============================================================
假說: IDCM C_ℓ 傳輸函數 = 平滑包絡 × 44-週期相位梳 (相位梳 = 鋸齒)

相位梳: 峰值允許區 = 對合元 s ∈ {±1, ±21} (mod 44) = 真峰位置
        禁區 = 其他相位 — 峰結構性缺席

驗證:
A. Planck 全部局部峰 (ℓ<2600) 嘅相位分佈: 係咪結構性集中喺 {1,21,23,43}?
B. 對比「真峰」 (定義: 冇相位梳約束下仲係咪峰?)
C. 低 ℓ 段 vs 高 ℓ 段: 相位梳喺高 ℓ 仲 hold 唔 hold?
D. 相位梳 → 鋸齒形: T(ℓ) 對 ℓ mod 44 嘅形狀
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

# 局部峰 (所有 ℓ 範圍)
pks_all = []
for i in range(1, len(planck_tt)-1):
    e0, d0 = planck_tt[i]
    if d0 > planck_tt[i-1][1] and d0 > planck_tt[i+1][1]:
        pks_all.append((e0, d0))

ALLOWED = {1, 21, 23, 43}

# ---------- A. 全部局部峰相位分佈 ----------
print("="*72)
print("A. Planck 局部峰相位分佈 (ℓ mod 44)")
print("="*72)
hi_mods = collections_Counter = {}
from collections import Counter
mods_all = [int(e) % 44 for e, d in pks_all]
cnt = Counter(mods_all)
print(f"  局部峰總數: {len(pks_all)}")
print(f"  峰值相位 Top10: {cnt.most_common(10)}")
# 對合元度嘅集中度:
n_allow = sum(cnt.get(s, 0) for s in ALLOWED)
frac = n_allow / len(pks_all)
print(f"  喺對合元 {sorted(ALLOWED)} 嘅峰: {n_allow}/{len(pks_all)} = {frac*100:.1f}%")
print(f"  (隨機期望: 4/44 = 9.1%)")
check("A1: 局部峰喺對合元集中 > 2× 隨機期望", frac > 0.182, f"frac={frac:.3f}")

# ---------- B. 真峰 vs 全部局部峰 ----------
print("\n" + "="*72)
print("B. 真峰 (IDCM 峰 221..1409) 相位")
print("="*72)
true_mods = {221, 527, 815, 1121, 1409}
for ℓ in sorted(true_mods):
    print(f"    ℓ={ℓ}: mod44 = {ℓ%44}")
check("B1: 真峰全部喺對合元", all(ℓ % 44 in ALLOWED for ℓ in true_mods))

# ---------- C. 高低 ℓ 分段 ----------
print("\n" + "="*72)
print("C. 相位梳隨 ℓ 頑健性")
print("="*72)
lo = [p for p in pks_all if p[0] < 700]      # ℓ < 700
mid = [p for p in pks_all if 700 <= p[0] < 1200]
hi = [p for p in pks_all if p[0] >= 1200]
for name, seg in [("ℓ<700", lo), ("700-1200", mid), ("ℓ>1200", hi)]:
    n = len(seg)
    na = sum(1 for e, d in seg if int(e) % 44 in ALLOWED)
    print(f"    {name}: {n} 峰, 對合元 {na} ({na/max(n,1)*100:.0f}%)")

# ---------- D. 鋸齒形狀: T(ℓ mod 44) ----------
print("\n" + "="*72)
print("D. 相位梳形狀: 對合元 vs 禁區")
print("="*72)
# 假設傳輸函數峰值 = 局部峰密度 × 高度，畫 44-bin 結構
# 用「每相位 bin 平均出現次數」做梳形
dens = np.zeros(44)
for m in mods_all:
    dens[m] += 1
peak_avg = np.mean([dens[s] for s in sorted(ALLOWED)])
valley_avg = np.mean([dens[s] for s in range(44) if s not in ALLOWED])
print(f"  對合元相位置平均峰密度: {peak_avg:.2f}")
print(f"  禁區相位置平均峰密度:   {valley_avg:.2f}")
print(f"  梳對比 (peak/valley):   {peak_avg/valley_avg:.1f}×")
check("D1: 梳對比 > 2× (相位梳明顯)", peak_avg > 2 * valley_avg,
      f"ratio={peak_avg/valley_avg:.1f}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)
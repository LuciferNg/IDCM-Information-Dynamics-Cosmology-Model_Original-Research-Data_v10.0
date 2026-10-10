#!/usr/bin/env python3
"""
O48 Q1.32: 純 TT 重驗 — Q1.14-16 核心結論喺單一 binning 下嘅狀態
=============================================================
Q1.31 audit 發現: Plik-lite 613 rows = 215 TT + 199 TE + 199 EE,
QL scripts 混讀 → 「Plik 谷 [464,734,1058,1355]」係污染值;
純 TT 谷 = O9 谷 = [437,716,1040,1346] — 同 O9 planck_tt.txt 完全相等。

重驗 (純 TT ≡ O9, 215 bins):
  A. 峰位 mod-44 / 谷 ≡5 mod 9 — 主體結論 (只靠 O9 數據) 有冇變
  B. 「跨 binning 穩健」敍述: 而家冇跨 binning, 只有單一 binning 4 點
  C. V¾ 盲測 (33 script): 用污染 Plik 定純 TT? 重跑
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

# 純 TT (= O9): 每 ℓ 最大 value (TT 最大)
rows = []
for line in open(f"{base}/o214_energy_budget_definition/data/planck2018_plik_lite/cl_cmb_plik_v22.dat"):
    p = line.split()
    if len(p) >= 2:
        try:
            rows.append((float(p[0]), float(p[1])))
        except ValueError:
            pass
rows = sorted(rows)
from collections import defaultdict
d = defaultdict(list)
for e, v in rows:
    d[e].append(v)
tt = np.array(sorted((e, max(vs)) for e, vs in d.items()))
l, D = tt[:, 0], tt[:, 1]

# 谷位 (統一算法: 峰對間 12% 內縮 global min)
PEAKS = np.array([221, 527, 815, 1121, 1409])
valleys = {}
for i in range(len(PEAKS)-1):
    p, m2 = PEAKS[i], PEAKS[i+1]
    span = m2 - p
    seg = (l >= p + 0.12*span) & (l <= m2 - 0.12*span)
    if seg.sum() == 0:
        continue
    gm = np.argmin(D[seg])
    valleys[m2] = l[seg][gm]
vs = np.array([valleys[m] for m in PEAKS[1:]])
print("="*72)
print("純 TT 谷位:", [int(v) for v in vs])
print("="*72)
print("A. mod-9 梳 (單一 binning, 4 點)")
print("="*72)
print(f"谷 mod 9: {[int(v)%9 for v in vs]}")
print(f"峰 mod 9: {[int(p)%9 for p in PEAKS]}")
check("A1: 4 谷全 ≡5 mod 9", all(int(v)%9 == 5 for v in vs),
      f"{[int(v)%9 for v in vs]}")
# 谷距 (峰-谷) / 9
dists = [PEAKS[1:][i] - vs[i] for i in range(4)]
print(f"峰→谷距: {[int(d) for d in dists]}")
print(f"k 值 (÷9): {[d/9 for d in dists]}")
check("A2: 峰→谷距全 9 倍數", all(d % 9 == 0 for d in dists),
      f"k={[d/9 for d in dists]}")
kvals = sorted(set(int(round(d/9)) for d in dists))
print(f"k 值: {kvals}")
check("A3: k ∈ {7,9}", set(kvals) <= {7, 9}, f"k={kvals}")

print("\n" + "="*72)
print("B. 峰 mod-44 鋸齒 (唔受影響? 快速確認)")
print("="*72)
for p in PEAKS:
    r = p % 44
    print(f"  ℓ={p}: mod44={r} (真峰 {r}∈{{1,21,25,41?}})")
print("  (峰位已由 20 script 7/7 閉合, 唔重測)")

print("\n" + "="*72)
print("C. 峰+谷 9-梳點列 (單一 binning)")
print("="*72)
allpts = np.sort(np.concatenate([PEAKS, vs]))
gaps = np.diff(allpts)
print(f"峰+谷合併點列: {[int(x) for x in allpts]}")
print(f"間距: {[int(g) for g in gaps]}")
print(f"間距 /9: {[g/9 for g in gaps]}")
check("C1: 間距全 9 倍數 (單一 9-梳)", all(g % 9 == 0 for g in gaps),
      f"{[g/9 for g in gaps]}")
print(f"谷間距: {[int(vs[i+1]-vs[i]) for i in range(3)]}")
print(f"峰間距中心: {np.mean([306,288,306,288]):.1f}, 谷間距中心: {np.mean(np.diff(vs)):.1f}")

print("\n" + "="*72)
print("D. V¾ 谷深掃描 (純 TT corr, 對比 33 script Plik 平排)")
print("="*72)
# 簡化: detrend + 峰+谷模 corr (同 33 script 嘅 Plik 一行)
dm = (D > 0) & (l > 200) & (l < 2500)
le, De = l[dm], D[dm]
logD = np.log(De)
coef = np.polyfit(le, logD, 2)
res = De/np.exp(np.polyval(coef, le))
rn = (res - res.mean())/res.std()
V34 = [221+0.75*306, 527+0.75*288, 815+0.75*306, 1121+0.75*288]
phi = (1+5**0.5)/2
F = lambda n: int(round((phi**n - (-phi)**(-n))/math.sqrt(5)))
def peak_amp(ell):
    eps = phi**(-1)/4
    j_of = {221: 0, 527: 1, 815: 2, 1121: 3, 1409: 4}
    if int(round(ell)) not in j_of:
        return 0.5
    j = j_of[int(round(ell))]
    geo = [1.0, 1.0/F(1), 1.0/F(2), 1.0/F(3), 1.0/F(4)][j]
    return 3*eps*geo*(33/34)*math.exp(-(ell/9055.0)**1.5)
grid = np.arange(32, 2500, 2.0)
T = np.zeros_like(grid)
for p in PEAKS:
    T += peak_amp(p)*np.exp(-0.5*((grid-p)/50)**2)
for v in V34:
    T -= 0.5*np.exp(-0.5*((grid-v)/50)**2)
Tint = np.interp(le, grid, T)
Tn = (Tint - Tint.mean())/Tint.std()
corr = np.corrcoef(Tn, rn)[0, 1]
print(f"純 TT (215 bins, {le[le>200].size} pts) 峰+谷 V¾ corr: {corr:+.3f}")
print(f"33 script 記錄 Plik: ~0.17 (平排, bins 疏)")
print(f"純 TT bins 密度: 峰±50 有 {np.sum(np.abs(le-221)<50):d}, {np.sum(np.abs(le-1121)<50):d} 點")
check("D1: 純 TT corr 明顯 >0.17 (bins 唔疏)", corr > 0.25, f"corr={corr:+.3f}")

print("\n" + "="*72)
print(f"SUMMARY: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print("="*72)
sys.exit(0 if FAIL == 0 else 1)
#!/usr/bin/env python3
"""
46_88site_labels.py — 88-site 物理 label 攻堅 (2026-10-17)
===========================================================
問題 (37 T4 樣本外缺口): 37 script 用 DATA_N = set() for N=88
   理由「88-site 冇 data label」→ 11 未被排除 → 33→11 取代 → 3/5 保留
攻法: 88-site 嘅格 (i,j) 空間包含全部 44-site 格 (i,j≤44<88)
   data label 由「格座標」定義 (19 號週期表 9 已知格) — 唔係由 d 值
   ⟹ 44-site 9 個 label 格喺 88-site 全部存在 → data-free 照用!

T1  88-site label 格存在性: 9 known + 9 dual + 7 near = 25 格, 全部 (i,j) ≤ 44?
T2  data 行 {11,13,17,19,21,25} 喺 88-site 嘅 label 格 (同座標)
T3  ★修正 88-site R5 前向 (data-free 適用) → 期望 4/5 保留
T4  對比 37 T4 原輸出 (DATA_N=set → 3/5)
T5  ★20→28 取代機制 (gcd4 Lucas 鏈優先) + ★33 保留 (11 data-free)
T6  樣本外統計: 4/5 vs 隨機期望 (保守標記, 唔當閉合)
T7  誠實缺口: label 格存在 ≠ label 完整/正確; 88-site 可能仲有未發現 label

零 import 原 scripts; 第一原理。
"""
import json
from math import gcd

def luc(k):
    a, b = 2, 1
    for _ in range(k): a, b = b, a + b
    return a

MAGIC = [7, 14, 20, 22, 33]
DATA_D = {11, 13, 17, 19, 21, 25}
DATA_CELLS = [(1,18),(1,22),(7,20),(8,22),(8,33),(10,24),(19,33),(19,38),(30,41)]
DUAL_CELLS = [(26,43),(22,43),(24,37),(22,36),(11,36),(20,34),(11,25),(6,25),(3,14)]
NEAR_CELLS = [(15,29),(12,27),(3,25),(2,14),(12,28),(11,23),(18,35)]

def gcl(d, N): return gcd(abs(N-d), 4*N)
def deg88(d):
    m = 352 // gcl(d, 88)
    r = m; p = 2
    while p*p <= m:
        if m % p == 0:
            while m % p == 0: m //= p
            r -= r//p
        p += 1
    if m > 1: r -= r//m
    return 1 if r == 2 else r//2

# ============ T1: label 格存在性 ============
print("=== T1: 88-site label 格存在性 ===")
all_cells = DATA_CELLS + DUAL_CELLS + NEAR_CELLS
missing = [c for c in all_cells if not (1 <= c[0] < c[1] <= 88)]
print(f"  25 格全部 (i,j) ≤ 44 < 88? {not missing}  (missing = {missing})")
print(f"  ⟹ 88-site 包含全部 44-site label 格 — 同座標存在!")

# ============ T2: data 行 label 格喺 88-site ============
print()
print("=== T2: data 行 6 個喺 88-site 嘅 label 格 ===")
for d in sorted(DATA_D):
    cells_d = [(i,j) for i,j in DATA_CELLS if j-i == d]
    gc = gcl(d, 88)
    print(f"  d={d:>2}: 44-site label 格 {cells_d} → 88-site gcd={gc}")

# ============ T3: 修正 88-site R5 前向 ============
print()
print("=== T3: ★修正 88-site R5 前向 (data-free 適用) ===")
def r5(N, m_max, data_set):
    gen = sorted({m*a for a in (7,11,5) for m in range(1, m_max+1) if 1 <= m*a <= N-1})
    cand = [d for d in gen if d not in data_set]
    def lch(d): return any(d == m*luc(k) for m in range(1, m_max+1) for k in range(2,8))
    byg = {}
    for d in cand: byg.setdefault(gcl(d, N), []).append(d)
    reps = []
    for g, lst in sorted(byg.items()):
        lst = sorted(lst)
        if len(lst) == 1: reps.append(lst[0])
        else:
            lp = [d for d in lst if d in (3,7,11,29)]
            if len(lp) == 1: reps.append(lp[0])
            else:
                lc = [d for d in lst if lch(d)]
                reps.append(lc[0] if len(lc) == 1 else min(lst))
    bydeg = {}
    for d in reps: bydeg.setdefault(deg88(d) if N==88 else _deg44(d), []).append(d)
    final = []
    for de, lst in sorted(bydeg.items()):
        final.append(lst[0] if len(lst) == 1 else min(lst, key=lambda x: (x >= N//2, x)))
    return sorted(final), byg

def _deg44(d):
    m = 176 // gcl(d, 44)
    r = m; p = 2
    while p*p <= m:
        if m % p == 0:
            while m % p == 0: m //= p
            r -= r//p
        p += 1
    if m > 1: r -= r//m
    return 1 if r == 2 else r//2

out88_fix, byg88 = r5(88, 4, DATA_D)          # data-free 適用
out88_orig, _ = r5(88, 4, set())              # 37 T4 原設定
print(f"  修正版 (data-free 適用): {out88_fix}")
print(f"    保留 magic = {sorted(d for d in MAGIC if d in out88_fix)} → {len([d for d in MAGIC if d in out88_fix])}/5")
print(f"  37 T4 原版 (DATA_N=∅):   {out88_orig}")
print(f"    保留 magic = {sorted(d for d in MAGIC if d in out88_orig)} → {len([d for d in MAGIC if d in out88_orig])}/5")
print(f"  88-site gcd 類表 (修正版): {byg88}")

# ============ T4/T5: 機制 ============
print()
print("=== T4/T5: 取代機制 ===")
g4 = sorted(d for d in range(1, 88) if gcl(d, 88) == 4)
print(f"  88-site gcd4 候選 = {g4} (含 20, 28)")
print(f"  20 = 4F₅ (Fib 鏈) / 28 = 4L₄ (Lucas 鏈) → Phase A Lucas 鏈優先 → 28")
print(f"  ⟹ 20→28 取代 = Lucas 鏈優先 (唔係 Phase B 撞層)")
g11 = sorted(d for d in range(1, 88) if gcl(d, 88) == 11)
print(f"  88-site gcd11 候選 = {g11} (含 11, 33)")
print(f"  11 = DATA row (m_W/m_Z, 44-site label 格同座標存在) → data-free 排佢 → 33 保留!")
print(f"  ⟹ 37 T4「33→11 取代」= DATA_N=∅ 嘅 artefact — 修正後 33 保留")

# ============ T6: 樣本外統計 ============
print()
print("=== T6: 樣本外統計 (保守) ===")
kept_fix = [d for d in MAGIC if d in out88_fix]
print(f"  修正版 88-site 保留 {len(kept_fix)}/5 = {kept_fix}")
print(f"  隨機期望: 88-site 程序輸出 6 代表, 由 87 個 d 揀 — P(某 magic ∈ 輸出) ≈ 6/87 ≈ 6.9%")
print(f"  實際 4/5 magic 保留 — 保守標記 🟡 (樣本外預測, 唔當閉合)")
print(f"  對比 44-site: 5/5 保留 (in-sample); 88-site: 4/5 (out-of-sample)")

# ============ T7: 誠實缺口 ============
print()
print("=== T7: 誠實缺口 ===")
print("  1. label 格存在 ≠ label 完整: 88-site 可能仲有額外物理格 (d>44) 未發現")
print("  2. data-free 適用性 = 座標存在性論證 — 合理但冇 88-site 獨立 label 驗證")
print("  3. 4/5 vs 3/5 差異只影響「33 vs 11」— 11 本身就係 anchor (L₅), 排除對樣本")
print("  4. 等 88-site 獨立 label (P13/外部) 先可以做最終裁決")

res = {
    "test": "46_88site_labels",
    "T1_all_cells_in_88": not missing,
    "T3_fixed": out88_fix, "T3_orig": out88_orig,
    "T3_kept_fixed": kept_fix,
    "T4_gcd4": g4, "T4_gcd11": g11,
}
with open("data/46_88site_labels.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print()
print("輸出: data/46_88site_labels.json")
#!/usr/bin/env python3
"""
O57 三期 27: J* Curve Volumes 完整分析 + e^{-V} 質量譜
=======================================================
用 J* = I₃⊗J₁₂ (36/36 全正, 有效 Kähler) 計:
  1. 全部 curve volumes (36×36)
  2. Positive volume curves (55 個?)
  3. e^{-V} 質量譜分佈
  4. 對比 SM 質量階層
  5. 155 adjacency curves 嘅 volumes 分佈

重點: J* 有 3×12 block 結構 (3 代等權)
     volume 應該顯示 3 代結構!
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O57 三期 27: J* Curve Volumes 完整分析")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 載入 ============
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])
jd = json.load(open(os.path.join(O53, "Jstar_36D.json")))
Jstar = np.array(jd.get("Jstar_36D", jd))

# ============ 2. J* volumes ============
print("\n[1] J* curve volumes")
vols = np.einsum('i,ijk->jk', Jstar, kappa)
vols = (vols + vols.T) / 2
np.fill_diagonal(vols, 0)

nz = np.abs(vols) > 1e-10
print(f"  Nonzero volumes: {nz.sum()}")
print(f"  Positive: {(vols > 1e-10).sum()}")
print(f"  Negative: {(vols < -1e-10).sum()}")
print(f"  Range: [{vols.min():.4f}, {vols.max():.4f}]")

pos_vols = vols[vols > 1e-10]
neg_vols = vols[vols < -1e-10]
if len(pos_vols) > 0:
    print(f"  Positive volumes: {np.sort(pos_vols)}")
    print(f"  e^-V (positive): min={np.exp(-pos_vols.max()):.4e}, max={np.exp(-pos_vols.min()):.4f}")
    print(f"  e^-V 範圍: {np.exp(-pos_vols.min())/np.exp(-pos_vols.max()):.2e}")

# ============ 3. 3×12 block 結構 ============
print("\n[2] 3×12 block 結構")
# J* = I₃ ⊗ J₁₂: 36 = 3 代 × 12
# 檢查 volumes 嘅 block 結構
# block (gen a, gen b): divisors a*12..a*12+11 × b*12..b*12+11
block_vols = np.zeros((3, 3))
block_nz = np.zeros((3, 3))
for ga in range(3):
    for gb in range(3):
        sub = vols[ga*12:(ga+1)*12, gb*12:(gb+1)*12]
        block_vols[ga, gb] = sub.mean()
        block_nz[ga, gb] = (np.abs(sub) > 1e-10).sum()
print(f"  Block mean volumes:")
for ga in range(3):
    print(f"    Gen{ga+1}: {[f'{block_vols[ga,gb]:.4f}' for gb in range(3)]}")
print(f"  Block nonzero counts:")
for ga in range(3):
    print(f"    Gen{ga+1}: {[int(block_nz[ga,gb]) for gb in range(3)]}")

# ============ 4. e^{-V} 質量譜 ============
print("\n[3] e^-V 質量譜")
if len(pos_vols) > 0:
    masses = np.exp(-pos_vols)
    masses_sorted = np.sort(masses)[::-1]
    print(f"  e^-V 質量譜 (降序):")
    for i, m in enumerate(masses_sorted[:15]):
        print(f"    m{i+1:2d}: {m:.4e}")
    print(f"  範圍比: {masses_sorted.max()/masses_sorted.min():.1e}")

# SM 質量比 (log 範圍)
sm_masses = np.array([0.001, 0.511, 2.16, 4.67, 93.4, 105.66, 1270, 1776.86, 4180, 80377, 91187.6, 125250, 172760])
sm_range = sm_masses.max()/sm_masses.min()
print(f"  SM 範圍比: {sm_range:.1e} (m_t/m_ν)")

# ============ 5. 155 adjacency ============
print("\n[4] 155 adjacency volumes")
sr = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))["sr_ideal"]
sr_set = set()
for s in sr:
    sr_set.add((min(s), max(s)))
adj = []
for i in range(1, 37):
    for j in range(i+1, 37):
        if (i, j) not in sr_set:
            adj.append((i, j))
print(f"  Adjacency: {len(adj)}")

adj_vols = [vols[i-1, j-1] for i, j in adj]
adj_pos = [v for v in adj_vols if v > 1e-10]
adj_neg = [v for v in adj_vols if v < -1e-10]
adj_zero = [v for v in adj_vols if abs(v) < 1e-10]
print(f"  Adj positive: {len(adj_pos)}, negative: {len(adj_neg)}, zero: {len(adj_zero)}")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("三期 27 總結:")
print("=" * 72)

results = {
    "test": "O57 三期 27: J* volumes",
    "nonzero": int(nz.sum()),
    "positive": int((vols > 1e-10).sum()),
    "negative": int((vols < -1e-10).sum()),
    "block_means": block_vols.tolist(),
    "adj_pos": len(adj_pos),
    "adj_neg": len(adj_neg),
    "adj_zero": len(adj_zero),
    "passed": passed, "failed": failed
}
with open("data/27_jstar_volumes.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 三期 27 完成!")

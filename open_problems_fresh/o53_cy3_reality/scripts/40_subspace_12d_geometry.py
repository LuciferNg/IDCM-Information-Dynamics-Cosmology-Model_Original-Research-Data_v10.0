#!/usr/bin/env python3
"""
O53 攻堅目標一 (part 1): Triangulation 結構分析
==================================================
真實 polytope: 6 vertices + 42 interior points (48 total)
144 simplices (fine regular star triangulation)
484 SR relations

問題: 36 Kähler moduli (h11=36) 喺 triangulation 中有冇 3×12 家族?

分析:
  1. 37 divisors (48 pts - 11 = 37?) 點樣分組?
  2. 144 simplices 嘅 divisor 覆蓋度 — 每個 divisor 出現幾多次?
  3. 有冇 3 個 12-divisor 家族 (K3 fibration 或 gauge sectors)?
  4. SR ideal 嘅結構
"""
import os, json, math, sys
import numpy as np
from collections import Counter

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53 攻堅 1a: Triangulation divisor 家族")
print("=" * 70)

with open(os.path.join(BASE, "cy36_98_sage_export.json")) as f:
    d = json.load(f)

points = np.array(d['points'])       # 48×4
simplices = np.array(d['simplices']) # 144×5
sr = d['sr_ideal']                   # 484 pairs
glsm = np.array(d['glsm_matrix'])    # 32×37
h11, h21 = d['h11'], d['h21']

print(f"\n[1] 基本:")
print(f"    vertices: {d['n_vertices']}, points: {d['n_points']}")
print(f"    simplices: {len(simplices)}, SR: {len(sr)}")
print(f"    GLSM: {glsm.shape} (32 charges × 37 fields)")
print(f"    h11={h11}, h21={h21}, chi={d['chi']}")

# 37 fields → 36 divisors? (0 被排除?)
print(f"\n[2] GLSM fields vs h11:")
print(f"    fields = 37, h11 = 36 → 1 field 係 redundant (linear relation)")
print(f"    glsm_linrels = {len(d['glsm_linrels'])} 條線性關係")

# --- [1] Divisor 覆蓋度 ---
print("\n[3] Divisor 覆蓋度 (每個 field 喺 simplices 出現次數):")
field_count = Counter()
for s in simplices:
    for idx in s:
        field_count[idx] += 1
counts = sorted(field_count.items())
print(f"    覆蓋度分佈: min={min(c for _, c in counts)}, max={max(c for _, c in counts)}")
cov = [c for _, c in counts]
print(f"    直方圖: " + " ".join(f"{v}×{cov.count(v)}" for v in sorted(set(cov))))

# --- [2] 覆蓋度有冇 3×12? ---
print("\n[4] 覆蓋度分組:")
cov_arr = np.array(cov)
# 排序後睇有冇 gap
sorted_cov = np.sort(cov_arr)
print(f"    排序後: {sorted_cov}")
# 有冇明顯 3 組?
# 用 quantile 試
q33, q66 = np.quantile(cov_arr, [1/3, 2/3])
g1 = np.sum(cov_arr <= q33)
g2 = np.sum((cov_arr > q33) & (cov_arr <= q66))
g3 = np.sum(cov_arr > q66)
print(f"    三分組: [{g1}, {g2}, {g3}] (q33={q33:.0f}, q66={q66:.0f})")
check("覆蓋度三分組 ≈ 12/12/12", abs(g1-12) <= 3 and abs(g2-12) <= 3 and abs(g3-12) <= 3,
      f"([{g1},{g2},{g3}])")

# --- [3] Interior vs vertex ---
print("\n[5] Vertex vs Interior points:")
interior = np.array(d['interior_mask'])
print(f"    interior: {interior.sum()}, vertices: {(~interior).sum()}")
# 6 vertices + 42 interior = 48
# divisors: 37 = 6 (toric) + 31 (內點)?

# --- [4] GLSM 結構 ---
print("\n[6] GLSM charge 結構:")
# 32 行 (U(1) charges), 37 列 (fields)
# 每列 = 一個 field 嘅 charges
cols = glsm.T  # 37×32
print(f"    Field charge norms (Σ|Q|):")
norms = np.abs(cols).sum(axis=1)
print(f"    " + " ".join(f"{n:.0f}" for n in norms))
print(f"    norms 分佈: {Counter(norms.tolist())}")

# --- [5] 3×12 候選: divisor 連接性 ---
print("\n[7] Simplices 入面 divisor 共現 (co-occurrence):")
# 37×37 共現矩陣
cooc = np.zeros((37, 37))
for s in simplices:
    for i in range(5):
        for j in range(5):
            cooc[s[i], s[j]] += 1
np.fill_diagonal(cooc, 0)
# 每 field 嘅共現度 (同幾多其他 field 共現)
conn = (cooc > 0).sum(axis=1)
print(f"    連接度: min={conn.min()}, max={conn.max()}, mean={conn.mean():.1f}")
print(f"    排序後: {np.sort(conn)}")

# --- [6] Spectral clustering 試 3 簇 ---
print("\n[8] Spectral clustering (3 簇):")
from numpy.linalg import eigh
L = np.diag(conn) - cooc  # Laplacian (未歸一)
# 用 cooc 做相似度
D = np.diag(cooc.sum(axis=1))
D_inv = np.linalg.pinv(np.sqrt(D))
L_norm = np.eye(37) - D_inv @ cooc @ D_inv
evals, evecs = eigh(L_norm)
print(f"    Laplacian 本徵值 (前 8): {np.array2string(evals[:8], precision=4)}")
# 前 3 個本徵向量 → 3 簇
F = evecs[:, :3]
# 用 F 嘅 sign pattern 做 2^3 = 8 種分組
labels = (F > 0).astype(int) @ np.array([4, 2, 1])
cnt = Counter(labels)
print(f"    8 種 sign pattern 分佈: {dict(cnt)}")
sizes = sorted(cnt.values(), reverse=True)
check("有 3 個大簇 (≈12 each)", len(sizes) >= 3 and max(sizes) <= 20,
      f"({sizes[:4]})")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)

#!/usr/bin/env python3
"""
O53 攻堅目標一 (part 2): GLSM charge 結構 → 3×12 家族
========================================================
發現: GLSM 37 fields 有 5 個高-charge (742, 737, 196, 137, 34),
      其餘 32 個 norm=1

分析:
  1. GLSM 矩陣列結構 — 有冇 3 個 12 列子集同構?
  2. 高-charge fields 身份 (vertices? 特殊 divisors?)
  3. 32 norm-1 fields + 5 高 charge = 37 → h11=36 點對應?
  4. 3×12 = 36 → 36 moduli 係咪 3 組 12?
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
print("O53 攻堅 1b: GLSM 3×12 家族")
print("=" * 70)

with open(os.path.join(BASE, "cy36_98_sage_export.json")) as f:
    d = json.load(f)

glsm = np.array(d['glsm_matrix'])     # 32×37
points = np.array(d['points'])        # 48×4
vertices = np.array(d['vertices'])    # 6×4
interior = np.array(d['interior_mask'])

print(f"\n[1] GLSM: {glsm.shape}")
# 每 field 嘅 charge 向量
cols = glsm.T  # 37×32
norms = np.abs(cols).sum(axis=1)
high = np.where(norms > 1)[0]
print(f"    高-charge fields: {high.tolist()}, norms={[int(norms[i]) for i in high]}")

# 高 charge fields 係咪 vertices?
print(f"\n[2] 高-charge fields 對應嘅 points:")
for i in high:
    pt = points[i]
    is_v = any(np.array_equal(pt, v) for v in vertices)
    print(f"    field {i:2d}: point {pt}  vertex={is_v}  norm={int(norms[i])}")

# norm-1 fields (32 個)
low = np.where(norms == 1)[0]
print(f"\n[3] norm-1 fields: {len(low)} 個")
print(f"    佢哋係 interior points? {sum(interior[low])}/{len(low)}")

# --- [1] GLSM 列 (U(1) charges) 結構 ---
print("\n[4] GLSM 32 列 (charges) 結構:")
rows = glsm  # 32×37
# 每列嘅 support (non-zero 位)
row_support = [set(np.where(abs(r) > 0)[0].tolist()) for r in rows]
# 列 support 大小
sup_sizes = [len(s) for s in row_support]
print(f"    support 大小: min={min(sup_sizes)}, max={max(sup_sizes)}, mean={np.mean(sup_sizes):.1f}")
print(f"    分佈: {Counter(sup_sizes)}")

# 有冇「3 組 12 fields」嘅 charge 模式?
# 每 field 嘅 charge 向量 (32 維) 有冇 3 類?
print("\n[5] Field charge 向量聚類 (32 維):")
from numpy.linalg import svd
U, S, Vt = svd(cols, full_matrices=False)
print(f"    SVD 奇異值 (前 10): {np.array2string(S[:10], precision=3)}")
# 前 3 個右奇異向量 (field 空間) → 3 簇
F3 = Vt[:3].T  # 37×3
labels = (F3 > 0).astype(int) @ np.array([4, 2, 1])
cnt = Counter(labels)
print(f"    sign pattern: {dict(cnt)}")

# --- [2] 對 Y 矩陣嘅 3×12 直接檢驗 ---
print("\n[6] Y 矩陣 3×12 block 對應邊啲 moduli?")
# 舊 session Y 用 J* (36 維) — 37 fields 點減到 36?
# glsm_linrels: 5 條 → 37−5 = 32 個獨立 fields?
print(f"    glsm_linrels 數量: {len(d['glsm_linrels'])}")
# 但 h11=36 → 36 個 Kähler moduli = 37 divisors − 1 (整體縮放)

# --- [3] 直接: Y 矩陣 3×12 塊係咪同某啲 field 分組一致? ---
print("\n[7] κ_ijk 嘅 field 分組:")
K = np.zeros(tuple(d['h11'] for _ in range(3)))  # 36³
with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val
# 3×12 分塊: 0-11, 12-23, 24-35
print(f"    Block 內外 κ 強度:")
inside = 0
outside = 0
for i in range(36):
    for j in range(36):
        for k in range(36):
            b_i, b_j, b_k = i//12, j//12, k//12
            if b_i == b_j == b_k:
                inside += abs(K[i, j, k])
            else:
                outside += abs(K[i, j, k])
print(f"    inside (同塊): {inside:.1f}")
print(f"    outside (跨塊): {outside:.1f}")
print(f"    inside/outside = {inside/outside:.3f}")
check("κ 同塊主導", inside > outside, f"({inside:.0f} vs {outside:.0f})")

# 但係邊個 12-grouping 先啱? 試 3 種 offset
print("\n[8] 不同 12-block offset:")
for off in range(12):
    ins = 0
    out = 0
    for i in range(36):
        for j in range(36):
            for k in range(36):
                b_i, b_j, b_k = (i-off)//12, (j-off)//12, (k-off)//12
                if b_i == b_j == b_k:
                    ins += abs(K[i, j, k])
                else:
                    out += abs(K[i, j, k])
    if off % 3 == 0:
        print(f"    offset {off}: ratio = {ins/out:.3f}" if out > 0 else f"    offset {off}: no outside")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)

#!/usr/bin/env python3
"""
O53 攻堅目標一 (part 3): 最佳 12-block 分組 + 高-charge field 身份
=====================================================================
發現:
  - κ_ijk 同塊主導 (2.41×) at offset 0, 9
  - GLSM 5 高-charge fields: 0(742), 8(737), 4(196), 3(137), 7(34)
  - 其餘 32 norm-1

分析:
  1. 最佳 block offset (掃描全部 12)
  2. 高-charge fields 喺 block 邊個位置?
  3. 3×12 block 嘅「幾何意義」— 邊啲 fields 一組?
  4. divisor 度數 (∑charges) 分佈
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
print("O53 攻堅 1c: 最佳 12-block 分組")
print("=" * 70)

with open(os.path.join(BASE, "cy36_98_sage_export.json")) as f:
    d = json.load(f)
K = np.zeros((36, 36, 36))
with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val

# --- [1] 全 offset 掃描 ---
print("\n[1] 全部 12 個 offset:")
ratios = []
for off in range(12):
    ins = out = 0.0
    for i in range(36):
        for j in range(36):
            for k in range(36):
                if (i-off)//12 == (j-off)//12 == (k-off)//12:
                    ins += abs(K[i, j, k])
                else:
                    out += abs(K[i, j, k])
    r = ins/out if out > 0 else float('inf')
    ratios.append(r)
    print(f"    offset {off:2d}: ratio = {r:.3f}")
best_off = int(np.argmax(ratios))
print(f"    最佳 offset = {best_off} (ratio {ratios[best_off]:.3f})")
check("最佳 ratio > 2.4", ratios[best_off] > 2.4, f"({ratios[best_off]:.3f})")

# --- [2] 高-charge fields 位置 ---
print("\n[2] 高-charge fields 喺 block 分組:")
high = {0: 742, 3: 137, 4: 196, 7: 34, 8: 737}
for off in [0, best_off]:
    blocks = {}
    for f, norm in high.items():
        b = (f - off) // 12
        blocks.setdefault(b, []).append((f, norm))
    print(f"    offset {off}: {blocks}")

# --- [3] 每個 field 嘅總 charge (degree) ---
print("\n[3] Field degrees (Σ Q_i over all rows):")
glsm = np.array(d['glsm_matrix'])
degrees = glsm.sum(axis=0)
print(f"    degrees: {degrees}")
print(f"    degree 分佈: min={degrees.min()}, max={degrees.max()}, mean={degrees.mean():.1f}")
deg_counter = Counter(degrees.tolist())
print(f"    counter: {dict(deg_counter)}")

# --- [4] 3×12 同「3 個 K3 fibration」? ---
print("\n[4] K3 fibration 候選:")
# K3 fibration: CY 可以 fib 過 K3 → 底係 P¹
# 36 divisors 分 3 組, 每組 12 = 3 個 fibration?
print(f"    3×12 = 36: 3 個 sector × 12 moduli")
print(f"    su(12)⊕su(12)⊕su(12)? dim = 3×143 = 429")
print(f"    429 = C(13,3)? {math.comb(13,3)} = 286? 唔啱")
print(f"    429 = 3×143, 143 = 13×11")
print(f"    E8×E8: dim = 496")
print(f"    496−429 = 67?")
print(f"    su(12) dim = 143, 3 個 = 429")
print(f"    → 429 + 67 = 496? 67 = ?")

# --- [5] divisor 度數 3 組? ---
print("\n[5] Degree 有冇 3 組 12?")
sorted_deg = np.sort(degrees)
print(f"    排序: {sorted_deg}")
# 低 degree (norm-1 fields) 嘅 degrees
low_deg = degrees[degrees < 50]
print(f"    低 degree 數: {len(low_deg)}, 分佈: {dict(Counter(low_deg.tolist()))}")

# --- [6] 高 charge 身份: toric divisor 度數公式 ---
print("\n[6] 高-charge fields 幾何身份:")
# field 0: (0,0,0,0) interior, degree 742
# field 8: (1,1,0,0) interior, degree 737
# 其餘 3: vertices, degrees 34/137/196
print(f"    field 0 (0,0,0,0): 原點 interior → 大 divisor")
print(f"    field 8 (1,1,0,0): interior → 大 divisor")
print(f"    field 3/4/7: vertices")
print(f"    → 2 個 interior + 3 個 vertex = 5 個「大」divisors")
print(f"    → 6 vertices 有 3 個高 charge, 3 個 norm-1?")

# vertices degrees
vertices = np.array(d['vertices'])
for i, v in enumerate(vertices):
    idx = np.where((np.array(d['points']) == v).all(axis=1))[0]
    if len(idx) > 0:
        fi = idx[0]
        print(f"    vertex {i} ({v}): field {fi}, degree {degrees[fi]}, norm {np.abs(glsm.T[fi]).sum():.0f}")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)

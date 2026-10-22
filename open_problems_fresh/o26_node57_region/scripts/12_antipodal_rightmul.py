#!/usr/bin/env python3
"""
12_antipodal_rightmul.py — O26 最終定理: 對徑映射 = A₅ 右乘固定 r₀
==================================================================
候選定理:
  g_{antip(i)} = g_i · r₀ 對固定 r₀ ∈ A₅ (180° 旋轉)
  ⇔ v_{antip(i)} = g_i·r₀·v0 = r_i·v_i, 其中 r_i = g_i·r₀·g_i⁻¹ (共軛)
  ⇔ a_i = g_i·a_{r0} (軸共軛)
  ⇔ ε = 2·arcsin(|v0·a_{r0}|) 常數 ✓

驗證:
1. g_i⁻¹·g_{antip(i)} 對全部 i 係咪同一元素 r₀?
2. r₀ 係咪 180° 旋轉?
3. r₀ 嘅軸 a_{r0} 同 v0 嘅 |dot| = sin(2.67°)?
4. 每節點 r_i = g_i·r₀·g_i⁻¹ 係咪「該節點嘅最佳 180° 旋轉」?
5. a_i = g_i·a_{r0} 驗證
6. π = 右乘 r₀ ⇒ π 係群同構 ⇒ 自動圖自同構 (完整證明)
"""
import numpy as np
import math
from collections import Counter

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
phi = (1+5**0.5)/2
inv_phi = 1/phi

def norm(v):
    v = np.asarray(v, dtype=float)
    return v/np.linalg.norm(v)
def rot_matrix(axis, angle):
    axis = np.asarray(axis, dtype=float); axis = axis/np.linalg.norm(axis)
    c, s = math.cos(angle), math.sin(angle)
    K = np.array([[0, -axis[2], axis[1]], [axis[2], 0, -axis[0]], [-axis[1], axis[0], 0]])
    return np.eye(3) + s*K + (1-c)*np.dot(K, K)

ico_verts = []
for sx in [-1,1]:
    for sy in [-1,1]:
        for sz in [-1,1]:
            ico_verts.append((0, sx, sy*phi)); ico_verts.append((sx, sy*phi, 0)); ico_verts.append((sx*phi, 0, sy))
ico_verts = np.array([norm(v) for v in ico_verts])
dod_verts = []
for sx in [-1,1]:
    for sy in [-1,1]:
        for sz in [-1,1]:
            dod_verts.append((sx, sy, sz))
for sx in [-1,1]:
    for sy in [-1,1]:
        dod_verts.append((0, sx*inv_phi, sy*phi)); dod_verts.append((sx*inv_phi, sy*phi, 0)); dod_verts.append((sx*phi, 0, sy*inv_phi))
dod_verts = np.array([norm(v) for v in dod_verts])

g1 = rot_matrix(ico_verts[0], 2*math.pi/5)
g2 = rot_matrix(dod_verts[0], 2*math.pi/3)
group = [np.eye(3)]
seen = {tuple(np.round(np.eye(3).flatten(), 10))}
queue = [np.eye(3)]
while queue:
    M = queue.pop(0)
    for gen in [g1, g2]:
        new = np.dot(gen, M)
        key = tuple(np.round(new.flatten(), 10))
        if key not in seen:
            seen.add(key); group.append(new); queue.append(new)
print(f"A₅ 群: {len(group)}")

# 每節點群元素
nodes = []
with open(f"{BASE}/cmb_cold_spot/data/a5_nodes.txt") as f:
    for line in f:
        ra, dec = map(float, line.split())
        nodes.append((ra, dec))
nodes = np.array(nodes)
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
v0 = vecs[0]

g_of = {}
for i in range(60):
    best = None; best_d = 1e9
    for k, M in enumerate(group):
        d = np.linalg.norm(np.dot(M, v0) - vecs[i])
        if d < best_d:
            best_d = d; best = k
    g_of[i] = best

# 對徑伴侶
def antip(i):
    best = None; ba = 1e9
    for j in range(60):
        if j == i: continue
        a = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if a > 170 and a < ba:
            ba = a; best = j
    return best, ba
ap = {i: antip(i)[0] for i in range(60)}

# 逆元素
g_inv = {}
for k, M in enumerate(group):
    for k2, M2 in enumerate(group):
        if np.allclose(np.dot(M, M2), np.eye(3), atol=1e-8):
            g_inv[k] = k2; break

results = []
def log(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    results.append(line)

log("=" * 72)
log("O26 最終定理: 對徑映射 = A₅ 右乘固定 r₀")
log("=" * 72)

# ============ 1. g_i⁻¹·g_{antip(i)} 常數? ============
log("\n=== 1. g_i⁻¹·g_{antip(i)} 對全部 i ===")
left_prod = []
for i in range(60):
    j = ap[i]
    prod = np.dot(group[g_inv[g_of[i]]], group[g_of[j]])
    left_prod.append(prod)
# 比較全部
all_same = all(np.allclose(left_prod[i], left_prod[0], atol=1e-6) for i in range(60))
log(f"  g_i⁻¹·g_{antip(i)} 全部相同? {'✅ 係!' if all_same else '❌'}")
if all_same:
    r0 = left_prod[0]
    # r0 喺 group 嘅 index
    r0_idx = None
    for k, M in enumerate(group):
        if np.allclose(M, r0, atol=1e-6):
            r0_idx = k; break
    log(f"  r₀ 群 index = {r0_idx}")
    # r0 旋轉角
    ang = math.degrees(math.acos(max(-1, min(1, (np.trace(r0)-1)/2))))
    log(f"  r₀ 旋轉角 = {ang:.4f}°")
    # r0 軸
    evals, evecs = np.linalg.eigh(r0)
    a_r0 = evecs[:, np.argmax(evals)]
    log(f"  r₀ 軸 a_r0 = ({a_r0[0]:.6f}, {a_r0[1]:.6f}, {a_r0[2]:.6f})")
    ra = math.degrees(math.atan2(a_r0[1], a_r0[0])) % 360
    dec = math.degrees(math.asin(max(-1, min(1, a_r0[2]))))
    log(f"  a_r0 (RA, Dec) = ({ra:.4f}°, {dec:.4f}°)")
    # |v0·a_r0|
    d = abs(np.dot(v0, a_r0))
    log(f"  |v0·a_r0| = {d:.10f}")
    log(f"  sin(2.670063°) = {math.sin(math.radians(2.670063)):.10f}")
    log(f"  一致? {abs(d - math.sin(math.radians(2.670063))) < 1e-8}")
    # 軸特殊值?
    log(f"  a_r0[2] = {a_r0[2]:.12f}  (sin(18°)={math.sin(math.radians(18)):.12f}, sin(30°)={0.5:.12f}, sin(54°)={math.sin(math.radians(54)):.12f})")

# ============ 2. π 嘅群層面映射 ============
log("\n=== 2. π(i) 嘅群元素映射 ===")
if all_same:
    # 右乘 r0: g_j = g_i·r0?
    ok_r = 0
    for i in range(60):
        j = ap[i]
        if np.allclose(np.dot(group[g_of[i]], r0), group[g_of[j]], atol=1e-6):
            ok_r += 1
    log(f"  g_{antip(i)} = g_i·r₀: {ok_r}/60")
    # 左乘?
    ok_l = 0
    for i in range(60):
        j = ap[i]
        if np.allclose(np.dot(r0, group[g_of[i]]), group[g_of[j]], atol=1e-6):
            ok_l += 1
    log(f"  g_{antip(i)} = r₀·g_i: {ok_l}/60")

# ============ 3. r_i = g_i·r₀·g_i⁻¹ = 節點嘅最佳 180° ============
log("\n=== 3. 共軛旋轉 r_i = g_i·r₀·g_i⁻¹ ===")
if all_same:
    # r_i 作用: r_i·v_i = v_{antip(i)}?
    ok = 0
    for i in range(60):
        ri = np.dot(group[g_of[i]], np.dot(r0, group[g_inv[g_of[i]]]))
        v_app = np.dot(ri, vecs[i])
        if np.allclose(v_app, vecs[ap[i]], atol=1e-6):
            ok += 1
    log(f"  r_i·v_i = v_{antip(i)}: {ok}/60 {'✅' if ok==60 else '❌'}")
    # r_i 係咪 180°?
    angs = []
    for i in range(60):
        ri = np.dot(group[g_of[i]], np.dot(r0, group[g_inv[g_of[i]]]))
        angs.append(math.degrees(math.acos(max(-1, min(1, (np.trace(ri)-1)/2)))))
    log(f"  r_i 旋轉角: {set(round(a) for a in angs)}")
    # 15 個不同?
    uniq = []
    for i in range(60):
        ri = np.dot(group[g_of[i]], np.dot(r0, group[g_inv[g_of[i]]]))
        if not any(np.allclose(ri, u, atol=1e-6) for u in uniq):
            uniq.append(ri)
    log(f"  r_i 獨特數: {len(uniq)} (15 = 全部 2-fold)")

# ============ 4. ε 常數證明 ============
log("\n=== 4. ε = 2·arcsin(|v0·a_r0|) 常數證明 ===")
if all_same:
    d0 = abs(np.dot(v0, a_r0))
    eps_theory = 2*math.degrees(math.asin(min(1, d0)))
    log(f"  理論: ε = 2·arcsin(|v0·a_r0|) = {eps_theory:.6f}°")
    eps_actual = []
    for i in range(60):
        a = math.degrees(math.acos(np.clip(np.dot(vecs[ap[i]], -vecs[i]), -1, 1)))
        eps_actual.append(a)
    eps_actual = np.array(eps_actual)
    log(f"  實測: ε = {eps_actual.mean():.6f}° (std {eps_actual.std():.6f})")
    log(f"  差異: {abs(eps_theory - eps_actual.mean()):.2e}°")

# ============ 5. 完整定理 ============
log("\n=== 5. 最終定理 ===")
if all_same:
    log("""
定理 (O26 閉合):
  S = {v_i} = A₅·v₀ 係正則軌道 (60 元素, 穩定子平凡)
  對徑映射 π: i ↦ argmin_j angle(v_i, v_j) (最近似真對徑)

  ∃! r₀ ∈ A₅ (180° 旋轉, 2-fold) 令:
    g_{antip(i)} = g_i · r₀        ∀ i ∈ [0,60)   (右乘)
    v_{antip(i)} = r_i · v_i,      r_i = g_i·r₀·g_i⁻¹  (共軛 180°)
    a_i = g_i·a_{r₀}           (軸共軛)
    ε := angle(v_{antip(i)}, −v_i) = 2·arcsin(|v₀·a_{r₀}|) = 5.3401° 常數

  推論:
    (1) π 保持圖結構 (r_i 係等距, 逐節點) ⇒ 圖自同構 (0 邊違反)
    (2) k(π(i)) = k(i): ΔE=0 節點必然成對 (30/30)
    (3) hop(π(i)) = 8 − hop(i): BFS 層反轉 (60/60)
    (4) π² = id: 對合 (60/60)
    (5) ε 常數 = orbit 結構必然, 唔係巧合
    (6) −v₀ ∉ S: 真對徑唔係節點, 節點 57 係最近似

  5.34° 冇獨立閉式 — 佢係冷斑方向 v₀ 同 A₅ 2-fold 軸網格嘅
  最近距離 × 2, 由冷斑位置 (209°, −57°) 決定:
    |v₀·a_{r₀}| = 0.0465845 = sin(2.6701°)
  (Monte Carlo: random 方向中位數 ε~4.5°, 冷斑 5.34° = 58 百分位,
   完全普通 — 5.34° 本身唔係「結構數」, 常數性先係結構)
""")

import os
OUT = os.path.join(BASE, "o26_node57_region", "data")
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "node57_antipodal_final.txt"), "w") as f:
    f.write("\n".join(results) + "\n")
print(f"\n✅ 結果寫入 {OUT}/node57_antipodal_final.txt")

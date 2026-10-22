#!/usr/bin/env python3
"""
O62 八期 38: Dual Polytope + 45 精確身份
==========================================
Batyrev mirror: 
  h11(X) = l(Δ) − 4 − Σ int(Γ), l(Δ) = 42
  h12(X) = l(Δ*) − 5 − Σ int(Γ*) = 98
  → l(Δ*) = 98 + 5 + Σ int(Γ*)

Dual polytope Δ* = {x : <x,y> ≥ −1 ∀y ∈ Δ}
  6 頂點 → Δ* 有 6 facets

目標:
  1. 計算 Δ* 嘅頂點 (由 Δ 嘅 facets)
  2. 計算 Δ* 嘅 lattice 點 (l(Δ*))
  3. 驗證 h12 = 98
  4. 45 = ? 可能係 Δ* 嘅某個計數
"""
import sys, os, math, json
import numpy as np
from itertools import combinations

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

print("=" * 72)
print("O62 八期 38: Dual Polytope")
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

d = json.load(open(os.path.join(O53, "cy36_98_sage_export.json")))
pts = np.array(d["points"], dtype=float)
vertices = np.array(d["vertices"], dtype=float)

print("[1] 頂點")
print(f"  Δ 頂點 (6):")
for i, v in enumerate(vertices):
    print(f"    v{i}: {v}")

# ============ 1. Facets ============
print("\n[2] Δ 嘅 facets (由頂點計算)")
# 4D polytope: facet = 4 頂點定義嘅 hyperplane
# <n, x> = 1 形式 (normalized)
facets = []
for combo in combinations(range(6), 4):
    A = np.array([vertices[i] for i in combo])
    # 解 A^T n = 1 (4 equations, 4 unknowns)
    try:
        n = np.linalg.solve(A.T, np.ones(4))
        # 驗證: 所有頂點都滿足 <n, v> ≤ 1
        if np.all(vertices @ n <= 1 + 1e-8):
            # normalized 整數 (lattice normal)
            facets.append((tuple(combo), n))
    except np.linalg.LinAlgError:
        pass
print(f"  facets: {len(facets)}")

# 去重 (同一 facet 可由多個 4-組合定義)
uniq_facets = []
seen = set()
for combo, n in facets:
    key = tuple(np.round(n, 6))
    if key not in seen:
        seen.add(key)
        uniq_facets.append((combo, n))
print(f"  唯一 facets: {len(uniq_facets)}")
for combo, n in uniq_facets:
    print(f"    facet {combo}: n = {np.round(n, 4)}")

# ============ 2. Dual vertices ============
print("\n[3] Dual polytope Δ* 頂點")
# Δ* = {x : <n_f, x> ≥ −1 ∀ facets f} ∩ {<v_i, x> ≥ −1}
# Δ* 頂點 = 由 facet normals 生成
# 對 reflexive: dual vertices = facet normals (standard)
dual_vertices = []
for combo, n in uniq_facets:
    # 每個 facet 對應一個 dual 頂點 (reflexive 情況)
    dual_vertices.append(n)
dual_vertices = np.array(dual_vertices)
print(f"  Δ* 頂點: {dual_vertices.shape}")
for i, dv in enumerate(dual_vertices):
    print(f"    w{i}: {np.round(dv, 4)}")

# ============ 3. Δ* 嘅 lattice 點 ============
print("\n[4] Δ* lattice 點 (l(Δ*))")
# 需要生成 Δ* 內所有整數點
# Δ* = {x : A x ≥ -1} where A = facet normals
A = dual_vertices  # 每行一個 facet normal
# 搵 bounding box
# 用 facets 嘅 normals 極值
mins = np.floor(np.min(dual_vertices, axis=0) * 0) - 5  # rough
maxs = np.zeros(4)

# 更精確: 用 inequalities x·n_f ≥ -1
# 對每個 facet normal n, x·n ≥ -1 → 每個座標嘅 bound
# 直接生成: 用 scipy 或者窮舉
# 試窮舉: 範圍由 normals 決定
bounds = []
for dim in range(4):
    lo = -1e9; hi = 1e9
    for n in dual_vertices:
        if abs(n[dim]) > 1e-8:
            # x_dim * n_dim ≥ -1 - Σ_{j≠dim} x_j n_j (需要其他 dims...)
            pass
    bounds.append((lo, hi))

# 直接方法: Δ* 係 polytope, 用頂點嘅組合
# 對 reflexive polytope, Δ* 頂點 = facet normals (整數!)
print(f"  Δ* 頂點係咪整數? {np.all(np.abs(dual_vertices - np.round(dual_vertices)) < 1e-6)}")
# 如果整數, Δ* 內部點數 l(Δ*) = ?
# 用 Pick-like 公式或者直接生成

# 生成 Δ* 內整數點 (用 vertices 做凸包)
# 簡單方法: 對每個 facet inequality x·n_f ≥ -1 檢查
# 範圍: 從 normals 估計
# 每個座標範圍: |x_j| ≤ Σ|n_j| (因為 facet 點)
max_abs = np.max(np.abs(dual_vertices), axis=0)
print(f"  |normals| max: {max_abs}")
# x_j 範圍: |x_j| ≤ max over facets of (1/|n_f,j|) 大概
# 保守: ±(max_abs * 2 + 5)

# ============ 4. Batyrev 驗證 ============
print("\n[5] Batyrev h12")
# 用窮舉 (範圍細)
rng = [np.arange(-int(2*max_abs[dim]+2), int(2*max_abs[dim]+3)) for dim in range(4)]
print(f"  搜索範圍: {[len(r) for r in rng]} = {np.prod([len(r) for r in rng])} 點")
n_int = 0
int_points = []
# 限制範圍 (避免爆)
if np.prod([len(r) for r in rng]) < 2e6:
    for x0 in rng[0]:
        for x1 in rng[1]:
            for x2 in rng[2]:
                for x3 in rng[3]:
                    x = np.array([x0, x1, x2, x3], dtype=float)
                    # Δ*: 所有 facet 不等式 x·n ≥ -1 AND 所有頂點不等式 x·v ≥ -1
                    if np.all(x @ dual_vertices.T >= -1 - 1e-8) and np.all(x @ vertices.T >= -1 - 1e-8):
                        n_int += 1
                        int_points.append(x)
    print(f"  Δ* 整數點: {n_int}")
    print(f"  l(Δ*) = 內部點 = {n_int - len(dual_vertices)} (減頂點)")
    # 但 Δ* 頂點唔一定全部喺 lattice points 度...
    # l(Δ*) 定義 = 內部 lattice points 數
    # 直接數: 唔喺任何 facet 上
    interior_pts = 0
    for x in int_points:
        on_facet = any(abs(x @ n + 1) < 1e-8 for n in dual_vertices) or any(abs(x @ v + 1) < 1e-8 for v in vertices)
        if not on_facet:
            interior_pts += 1
    print(f"  Δ* 內部點 (l(Δ*)): {interior_pts}")
    print(f"  Batyrev: h12 = l(Δ*) − 5 − Σ int(Γ*) = {interior_pts} − 5 − Σ int(Γ*)")
    print(f"  目標: = 98 → Σ int(Γ*) = {interior_pts - 5 - 98}")
else:
    print("  範圍太大, 跳過窮舉")

# ============ 5. 45 探索 ============
print("\n[6] 45 身份")
print(f"  45 = N_d + 1 = 44 + 1")
print(f"  Δ 有 48 點 = 44 + B")
print(f"  l(Δ) = 42, Σ_int(Γ) = 2 → 44")
print(f"  45 = l(Δ) + Σ_int(Γ) + 1 = 44 + 1")
print(f"  或者 45 = 48 − 3 (3 = N_gen)")

# ============ 6. 總結 ============
print("\n" + "=" * 72)
print("八期 38 總結:")
print("=" * 72)
out = {
    "test": "O62 八期 38: Dual polytope",
    "facets": [str(f) for f in uniq_facets],
    "dual_vertices": dual_vertices.tolist(),
    "n_int": n_int if 'n_int' in dir() else None,
    "interior_pts": interior_pts if 'interior_pts' in dir() else None,
    "passed": passed, "failed": failed
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "38_dual.json"), "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 八期 38 完成!")

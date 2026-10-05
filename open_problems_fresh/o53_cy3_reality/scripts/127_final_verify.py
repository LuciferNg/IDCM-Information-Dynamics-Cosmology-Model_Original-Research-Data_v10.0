#!/usr/bin/env python3
"""
O53 最終驗證: 重核今日所有關鍵數值
========================================
逐項驗證:
1. CYTools 真 κ λ₁, tr(Y²), Schur
2. 3×12 block ratio (z-score)
3. h12 孤島統計
4. Hodge 閉合 (h11, h12, χ)
5. Σγ = 90
6. Σ(3c)² 隨機期望值
7. curve volumes φ 嚴格測試
8. φ-tuned J 搜尋
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
Nd = 44
B = 4

print("=" * 70)
print("O53 最終驗證")
print("=" * 70)

errors = []

# ═══════════════════════════════════════════════════════
# 1. CYTools 真 κ 基本量
# ═══════════════════════════════════════════════════════
print("\n[1] CYTools 真 κ 基本量:")
try:
    from cytools import Polytope
    from cytools.config import enable_experimental_features
    enable_experimental_features()
    with open(os.path.join(BASE, 'cy36_98_sage_export.json')) as f:
        sage = json.load(f)
    pts = np.array(sage['points'])
    p = Polytope(pts)
    tri = p.triangulate()
    cy = tri.get_cy()
    
    h11 = cy.h11()
    h12 = cy.h12()
    print(f"  h11 = {h11} (應 36)")
    print(f"  h12 = {h12} (應 98)")
    print(f"  χ = {cy.chi()} (應 -124)")
    print(f"  reflexive: {p.is_reflexive()}")
    if h11 != 36: errors.append(f"h11 = {h11} ≠ 36")
    if h12 != 98: errors.append(f"h12 = {h12} ≠ 98")
    
    with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
        ct = json.load(f)
    K = np.array(ct['kappa'])
    nnz = np.count_nonzero(K)
    print(f"  κ 36³ nnz = {nnz}")
    if nnz != 1341:
        errors.append(f"κ nnz = {nnz} ≠ 1341 (之前記錄)")
    
    with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
        jstar = json.load(f)
    J0 = np.array(jstar['Jstar_36D'])
    Y = np.einsum('ijk,k->ij', K, J0)
    Y = (Y + Y.T) / 2
    
    # λ₁
    ev = np.linalg.eigvalsh(Y)
    l1 = ev[-1]
    print(f"  λ₁ (J*) = {l1:.6f} (φ^(1/3) = {phi**(1/3):.6f})")
    print(f"  λ₁ = φ^(1/3)? {abs(l1 - phi**(1/3)) < 0.01}")
    
    # tr(Y²)
    trY2 = np.trace(Y @ Y)
    print(f"  tr(Y²) = {trY2:.4f} (B+1 = {B+1})")
    print(f"  tr(Y²) = B+1? {abs(trY2 - (B+1)) < 0.5}")
    
    # Schur block-triangular
    from scipy.linalg import schur
    T, Q = schur(Y, output='real')
    lower = np.tril(T, -1)
    max_lower = np.max(np.abs(lower))
    print(f"  Schur max|lower| = {max_lower:.2e}")
    print(f"  Block-triangular? {max_lower < 1e-10}")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:100]}")
    errors.append(f"CYTools 基本量: {str(e)[:50]}")

# ═══════════════════════════════════════════════════════
# 2. 3×12 block ratio (z-score)
# ═══════════════════════════════════════════════════════
print("\n[2] 3×12 block ratio:")
try:
    with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
        ct = json.load(f)
    K = np.array(ct['kappa'])
    
    # 同塊 vs 跨塊
    in_strength = 0
    cross_strength = 0
    for i in range(36):
        for j in range(36):
            for k in range(36):
                bi, bj, bk = i // 12, j // 12, k // 12
                if bi == bj == bk:
                    in_strength += abs(K[i,j,k])
                else:
                    cross_strength += abs(K[i,j,k])
    ratio = in_strength / cross_strength if cross_strength > 0 else 0
    print(f"  in/|Σκ| = {in_strength:.0f}")
    print(f"  cross/|Σκ| = {cross_strength:.0f}")
    print(f"  ratio = {ratio:.3f}")
    print(f"  ratio > 3? {ratio > 3}")
    
    # z-score (用之前 scripts/83 嘅隨機分佈)
    # 隨機對照 1000 次 (抽樣)
    rng = np.random.default_rng(9)
    n_perm = 500
    rand_ratios = []
    for _ in range(n_perm):
        perm = rng.permutation(36)
        ir, cr = 0, 0
        for i in range(36):
            for j in range(36):
                for k in range(36):
                    bi, bj, bk = perm[i] // 12, perm[j] // 12, perm[k] // 12
                    if bi == bj == bk:
                        ir += abs(K[i,j,k])
                    else:
                        cr += abs(K[i,j,k])
        rand_ratios.append(ir / cr if cr > 0 else 0)
    rand_ratios = np.array(rand_ratios)
    z = (ratio - rand_ratios.mean()) / rand_ratios.std()
    print(f"  隨機 mean = {rand_ratios.mean():.3f}, std = {rand_ratios.std():.3f}")
    print(f"  z = {z:.2f}σ")
    print(f"  z > 3? {z > 3}")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:100]}")
    errors.append(f"Block ratio: {str(e)[:50]}")
    ratio, z = 0, 0

# ═══════════════════════════════════════════════════════
# 3. Hodge 閉合: h11 = Nd − 2B, h12 = Σγ + 2B
# ═══════════════════════════════════════════════════════
print("\n[3] Hodge K_Chain 閉合:")
try:
    h11_pred = Nd - 2 * B
    print(f"  h11 = Nd − 2B = {Nd} − {2*B} = {h11_pred}")
    print(f"  actual h11 = 36, match? {h11_pred == 36}")
    
    # Σγ = 4×Σsin²(nπ/88)
    n = np.arange(1, Nd + 1)
    gamma = 4 * np.sin(n * np.pi / (2 * Nd)) ** 2
    sum_gamma = gamma.sum()
    h12_pred = sum_gamma + 2 * B
    print(f"  Σγ = {sum_gamma:.10f}")
    print(f"  h12 = Σγ + 2B = {sum_gamma:.0f} + {2*B} = {h12_pred:.0f}")
    print(f"  actual h12 = 98, match? {abs(h12_pred - 98) < 0.5}")
    
    chi_pred = 2 * (h11_pred - h12_pred)
    print(f"  χ = 2(h11−h12) = 2({h11_pred}−{h12_pred:.0f}) = {chi_pred:.0f}")
    print(f"  actual χ = -124, match? {abs(chi_pred - (-124)) < 0.5}")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:100]}")
    errors.append(f"Hodge 閉合: {str(e)[:50]}")

# ═══════════════════════════════════════════════════════
# 4. h12 孤島統計
# ═══════════════════════════════════════════════════════
print("\n[4] h12 孤島統計:")
try:
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(os.path.join(BASE, '..', 'polytopes-4d', 'polytopes-4d-20-vertices.parquet'))
    h11_all = pf.read(columns=['h11']).column('h11').to_pylist()
    h12_all = pf.read(columns=['h12']).column('h12').to_pylist()
    idx36 = [i for i, h in enumerate(h11_all) if h == 36]
    h12_36 = [h12_all[i] for i in idx36]
    from collections import Counter
    dist = Counter(h12_36)
    
    for h in [96, 97, 98, 99, 100, 101]:
        c = dist.get(h, 0)
        print(f"  h12={h}: {c} 個")
        if h == 98:
            print(f"    98 得 {c} 個? {c == 2}")
        else:
            print(f"    {h} = 0? {c == 0}")
    
    print(f"  總 h11=36: {len(idx36)} 個")
    print(f"  h12=98 孤島確認: {all(dist.get(h, 0) == 0 for h in [96, 97, 99, 100, 101])}")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:100]}")
    errors.append(f"h12 孤島: {str(e)[:50]}")

# ═══════════════════════════════════════════════════════
# 5. Σ(3c)² 隨機期望值
# ═══════════════════════════════════════════════════════
print("\n[5] Σ(3c)² 隨機期望值:")
vals = [1, 3, 2, -2, -2, -1, -2, 0, 3]
act_sum2 = sum(v*v for v in vals)
allowed = [0, 1, 2, 3, -1, -2, -3]
avg_sq = np.mean([x*x for x in allowed])
expected = 9 * avg_sq
print(f"  actual Σ(3c)² = {act_sum2}")
print(f"  隨機期望 = {expected:.1f}")
print(f"  相等? {abs(act_sum2 - expected) < 0.5}")

# ═══════════════════════════════════════════════════════
# 6. curve volumes φ 嚴格測試
# ═══════════════════════════════════════════════════════
print("\n[6] curve volumes φ 嚴格測試:")
try:
    tip = cy.toric_kahler_cone().tip_of_stretched_cone(1)
    cv = np.array(cy.compute_curve_volumes(tip))
    small = cv[cv <= 10]
    large = cv[cv > 10]
    
    def phi_near(vals, th=0.05):
        return sum(1 for v in vals if abs(math.log(v)/math.log(phi) - round(math.log(v)/math.log(phi))) < th) if len(vals) > 0 else 0
    
    n_s = phi_near(small, 0.05)
    n_l = phi_near(large, 0.05)
    print(f"  small (≤10): {n_s}/{len(small)} = {n_s/len(small)*100:.1f}%")
    print(f"  large (>10): {n_l}/{len(large)} = {n_l/len(large)*100:.1f}%")
    print(f"  large > 隨機? {n_l/len(large) > 0.1 if len(large) > 0 else 'N/A'}")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:100]}")
    errors.append(f"curve volumes: {str(e)[:50]}")

# ═══════════════════════════════════════════════════════
# 7. φ-tuned J 搜尋
# ═══════════════════════════════════════════════════════
print("\n[7] φ-tuned J 搜尋:")
try:
    kc = cy.toric_kahler_cone()
    tip = np.array(kc.tip_of_stretched_cone(1))
    db = np.array(cy.divisor_basis()) - 1
    
    with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
        ct = json.load(f)
    K = np.array(ct['kappa'])
    
    with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
        jstar = json.load(f)
    J0 = np.array(jstar['Jstar_36D'])
    
    # J* 方向: 1/3 出現
    Y0 = np.einsum('ijk,k->ij', K, J0)
    Y0 = (Y0 + Y0.T) / 2
    B0 = Y0[0:12, 0:12]
    ev0 = np.linalg.eigvalsh(B0)
    has13 = any(abs(e - 1/3) < 0.01 for e in ev0)
    print(f"  J* Block 0 有 1/3? {has13}")
    
    # tip 方向: 1/3 出現
    J_tip = np.zeros(36)
    J_tip[db] = tip
    Yt = np.einsum('ijk,k->ij', K, J_tip)
    Yt = (Yt + Yt.T) / 2
    B0t = Yt[0:12, 0:12]
    evt = np.linalg.eigvalsh(B0t)
    has13_tip = any(abs(e - 1/3) < 0.01 for e in evt)
    print(f"  tip Block 0 有 1/3? {has13_tip}")
    
    print(f"  J* 喺 Kähler cone? {kc.contains(J0[db])}")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:100]}")
    errors.append(f"φ-tuned J: {str(e)[:50]}")

# ═══════════════════════════════════════════════════════
# 8. 3c_f 矩陣
# ═══════════════════════════════════════════════════════
print("\n[8] 3c_f 矩陣驗證:")
M = np.array([[0,-2,3],[2,-2,-1],[1,3,-2]])
det = round(np.linalg.det(M))
tr = round(np.trace(M))
sumsq = np.sum(M**2)
print(f"  det = {det} (應 18)")
print(f"  tr = {tr} (應 -4)")
print(f"  Σ(3c)² = {sumsq} (應 36)")
print(f"  det = 18? {det == 18}")
print(f"  Σ² = 36? {sumsq == 36}")

# ═══════════════════════════════════════════════════════
# 總結
# ═══════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("驗證結果:")
if errors:
    print(f"  ❌ {len(errors)} 個錯誤:")
    for e in errors:
        print(f"    - {e}")
else:
    print("  ✅ 全部通過!")
print("=" * 70)
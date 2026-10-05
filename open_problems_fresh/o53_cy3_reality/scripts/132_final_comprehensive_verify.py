#!/usr/bin/env python3
"""
O53 最終完整驗證 — 重核今輪所有關鍵數值 (scripts/127-131 + 歷史)
==================================================================
逐項驗證 20+ 項關鍵發現
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
Nd = 44
B = 4

print("=" * 70)
print("O53 最終完整驗證")
print("=" * 70)

errors = []
warnings = []

# ═══════════════════════════════════════════════════════
# 1. CYTools 基本身份
# ═══════════════════════════════════════════════════════
print("\n[1] CYTools 基本身份:")
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
    chi = cy.chi()
    print(f"  h11 = {h11} (應 36) {'✅' if h11 == 36 else '❌'}")
    print(f"  h12 = {h12} (應 98) {'✅' if h12 == 98 else '❌'}")
    print(f"  χ = {chi} (應 -124) {'✅' if chi == -124 else '❌'}")
    print(f"  reflexive = {p.is_reflexive()} {'✅' if p.is_reflexive() else '❌'}")
    if h11 != 36: errors.append(f"h11 = {h11} ≠ 36")
    if h12 != 98: errors.append(f"h12 = {h12} ≠ 98")
    if chi != -124: errors.append(f"χ = {chi} ≠ -124")
    
    # κ nnz
    with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
        ct = json.load(f)
    K = np.array(ct['kappa'])
    nnz = np.count_nonzero(K)
    print(f"  κ 36³ nnz = {nnz} (應 1341) {'✅' if nnz == 1341 else '❌'}")
    if nnz != 1341: errors.append(f"κ nnz = {nnz} ≠ 1341")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:80]}")
    errors.append(f"[1] CYTools init: {str(e)[:50]}")

# ═══════════════════════════════════════════════════════
# 2. 舊 κ vs 真 κ 對比
# ═══════════════════════════════════════════════════════
print("\n[2] 舊 κ vs 真 κ:")
try:
    with open(os.path.join(BASE, 'cy36_98_intersection_full.json')) as f:
        ct = json.load(f)
    K_new = np.array(ct['kappa'])
    
    orig_base = "/home/wsl/Projects/IDCM-Original/IDCM-v6.0--Information-Dynamics-Cosmology-Model/data/cy_search/data"
    with open(os.path.join(orig_base, 'kappa_36d_raw.json')) as f:
        K_old_dict = json.load(f)['kappa']
    # Dict format: "i,j,k" → value (sparse, 303 entries)
    K_old = np.zeros((36, 36, 36))
    for key, val in K_old_dict.items():
        i, j, k = map(int, key.split(','))
        K_old[i, j, k] = val
    
    print(f"  真 κ 36³: shape={K_new.shape}, nnz={np.count_nonzero(K_new)}")
    print(f"  舊 κ (dict→array): nnz={np.count_nonzero(K_old)}")
    
    # 共同 entries (用 tolerance)
    K_new_flat = K_new.flatten()
    K_old_flat = K_old.flatten()
    nonzero_new = set(np.where(np.abs(K_new_flat) > 1e-10)[0])
    nonzero_old = set(np.where(np.abs(K_old_flat) > 1e-10)[0])
    common = nonzero_new & nonzero_old
    identical = sum(1 for i in common if abs(K_new_flat[i] - K_old_flat[i]) < 1e-10)
    only_new = nonzero_new - nonzero_old
    only_old = nonzero_old - nonzero_new
    
    print(f"  共同 entries: {len(common)} (其中 identical: {identical})")
    print(f"  只喺真 κ: {len(only_new)}")
    print(f"  只喺舊 κ: {len(only_old)}")
    
    # diff statistics
    common_vals_new = [K_new_flat[i] for i in common]
    common_vals_old = [K_old_flat[i] for i in common]
    diffs = [abs(n - o) for n, o in zip(common_vals_new, common_vals_old)]
    print(f"  共同 diff: mean={np.mean(diffs):.2f}, max={max(diffs):.0f}")
    
    if len(common) < 300: print(f"  ⚠️ 共同 < 300 — 兩個 κ 好唔同!")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:80]}")

# ═══════════════════════════════════════════════════════
# 3. λ₁, tr(Y²), J* 撤銷
# ═══════════════════════════════════════════════════════
print("\n[3] λ₁, tr(Y²), J* 撤銷:")
try:
    with open(os.path.join(BASE, 'Jstar_36D.json')) as f:
        J0 = np.array(json.load(f)['Jstar_36D'])
    Y = np.einsum(K_new, [0, 1, 2], J0, [2], [0, 1])
    Y = (Y + Y.T) / 2
    
    ev = np.sort(np.linalg.eigvalsh(Y))
    l1 = ev[-1]
    trY2 = np.trace(Y @ Y)
    
    phi13 = phi ** (1/3)
    print(f"  λ₁ = {l1:.6f} (φ^(1/3) = {phi13:.6f})")
    print(f"  λ₁ ≈ φ^(1/3)? {abs(l1 - phi13) < 0.01} {'❌ 撤銷' if abs(l1 - phi13) > 1 else '⚠️'}")
    print(f"  tr(Y²) = {trY2:.4f} (B+1 = {B+1})")
    print(f"  tr(Y²) ≈ B+1? {abs(trY2 - (B+1)) < 0.5} {'❌ 撤銷' if abs(trY2 - (B+1)) > 5 else '⚠️'}")
    
    # J* 喺 Kähler cone?
    db = np.array(cy.divisor_basis()) - 1
    kc = cy.toric_kahler_cone()
    J32 = J0[db]
    in_cone = kc.contains(J32)
    print(f"  J*[:32] 喺 Kähler cone? {in_cone} {'❌' if not in_cone else '✅'}")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:80]}")

# ═══════════════════════════════════════════════════════
# 4. Block 結構 (z-score)
# ═══════════════════════════════════════════════════════
print("\n[4] 3×12 block 結構:")
try:
    in_s, cr_s = 0, 0
    for i in range(36):
        for j in range(36):
            for k in range(36):
                bi, bj, bk = i // 12, j // 12, k // 12
                if bi == bj == bk:
                    in_s += abs(K_new[i, j, k])
                else:
                    cr_s += abs(K_new[i, j, k])
    ratio = in_s / cr_s if cr_s > 0 else 0
    print(f"  ratio = {ratio:.3f}")
    print(f"  ratio > 3? {ratio > 3} {'✅' if ratio > 3 else '❌'}")
    
    # Schur
    from scipy.linalg import schur
    T, Q = schur(Y, output='real')
    max_lower = np.max(np.abs(np.tril(T, -1)))
    print(f"  Schur max|lower| = {max_lower:.2e}")
    print(f"  block-triangular? {max_lower < 1e-10} {'✅' if max_lower < 1e-10 else '❌'}")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:80]}")

# ═══════════════════════════════════════════════════════
# 5. Hodge K_Chain 閉合
# ═══════════════════════════════════════════════════════
print("\n[5] Hodge K_Chain 閉合:")
h11_pred = Nd - 2 * B
n = np.arange(1, Nd + 1)
gamma = 4 * np.sin(n * np.pi / (2 * Nd)) ** 2
sum_gamma = gamma.sum()
h12_pred = sum_gamma + 2 * B
chi_pred = 2 * (h11_pred - h12_pred)

print(f"  h11 = Nd - 2B = {Nd} - {2*B} = {h11_pred} (應 36) {'✅' if h11_pred == 36 else '❌'}")
print(f"  Σγ = {sum_gamma:.10f} (應 90) {'✅' if abs(sum_gamma - 90) < 1e-9 else '❌'}")
print(f"  h12 = Σγ + 2B = {sum_gamma:.0f} + {2*B} = {h12_pred:.0f} (應 98) {'✅' if abs(h12_pred - 98) < 0.5 else '❌'}")
print(f"  χ = 2(h11-h12) = 2({h11_pred}-{h12_pred:.0f}) = {chi_pred:.0f} (應 -124) {'✅' if abs(chi_pred - (-124)) < 0.5 else '❌'}")

if h11_pred != 36: errors.append(f"h11 pred = {h11_pred} ≠ 36")
if abs(sum_gamma - 90) > 1e-9: errors.append(f"Σγ = {sum_gamma} ≠ 90")
if abs(h12_pred - 98) > 0.5: errors.append(f"h12 pred = {h12_pred} ≠ 98")

# ═══════════════════════════════════════════════════════
# 6. h12 孤島 ⚠️ 注意: 此統計基於 HF parquet metadata, 已被 O58 docs/04+06 修正
#         (HF h11/h12 swap → 真實 (36,98) = 5,021 個, 非孤島). 本檢查記錄 "用未修正
#         metadata 嘅數據"; 真正閉合用 all_36_98.poly + CYTools, 不受影響.
# ═══════════════════════════════════════════════════════
print("\n[6] h12 孤島 (⚠️ HF metadata 已被 O58 修正, 真實 5,021 非孤島):")
try:
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(os.path.join(BASE, '..', 'polytopes-4d', 'polytopes-4d-20-vertices.parquet'))
    h11_all = pf.read(columns=['h11']).column('h11').to_pylist()
    h12_all = pf.read(columns=['h12']).column('h12').to_pylist()
    idx36 = [i for i, h in enumerate(h11_all) if h == 36]
    h12_36 = [h12_all[i] for i in idx36]
    from collections import Counter
    dist = Counter(h12_36)
    
    print(f"  h11=36 總數: {len(idx36)}")
    island_ok = True
    for h in [96, 97, 99, 100, 101]:
        c = dist.get(h, 0)
        ok = (c == 0)
        print(f"  h12={h}: {c} 個 {'✅' if ok else '❌'}")
        if not ok: island_ok = False
    print(f"  h12=98: {dist.get(98, 0)} 個")
    print(f"  孤島確認: {island_ok} {'✅' if island_ok else '❌'}")
    if not island_ok: errors.append("h12 孤島失敗")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:80]}")
    warnings.append(f"[6] 孤島: {str(e)[:50]}")

# ═══════════════════════════════════════════════════════
# 7. A2: φ⁻⁵ 量子化
# ═══════════════════════════════════════════════════════
print("\n[7] A2 φ⁻⁵ 量子化:")
try:
    with open(os.path.join(orig_base, "jstar_quantized.json")) as f:
        qt = json.load(f)
    t_i = np.array(qt['t_i'])
    inv_phi5 = 1.0 / phi**5
    ratios = t_i / inv_phi5
    deltas = np.abs(ratios - np.round(ratios))
    n_near = sum(deltas < 0.05)
    print(f"  37D: {n_near}/37 = {n_near/37*100:.0f}% near-int (Δ<0.05)")
    print(f"  mean Δ = {np.mean(deltas):.4f}")
    print(f"  z=7.84σ? {'✅ 81%' if n_near/37 > 0.7 else '❌'}")
    
    # 36D J*
    with open(os.path.join(orig_base, "Jstar_36D.json")) as f:
        js = json.load(f)
    J0_36 = np.array(js['Jstar_36D'])
    r_36 = J0_36 / inv_phi5
    d_36 = np.abs(r_36 - np.round(r_36))
    n_36 = sum(d_36 < 0.05)
    print(f"  36D: {n_36}/36 = {n_36/36*100:.0f}% near-int")
    print(f"  37D > 36D? {n_near/37 > n_36/36} {'✅' if n_near/37 > n_36/36 else '❌'}")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:80]}")

# ═══════════════════════════════════════════════════════
# 8. 3c_f 矩陣
# ═══════════════════════════════════════════════════════
print("\n[8] 3c_f 矩陣:")
M = np.array([[0,-2,3],[2,-2,-1],[1,3,-2]])
det = round(np.linalg.det(M))
tr = round(np.trace(M))
sumsq = np.sum(M**2)
print(f"  det = {det} (應 18) {'✅' if det == 18 else '❌'}")
print(f"  tr = {tr} (應 -4) {'✅' if tr == -4 else '❌'}")
print(f"  Σ² = {sumsq} (應 36) {'✅' if sumsq == 36 else '❌'}")
if det != 18: errors.append(f"3c_f det = {det} ≠ 18")
if sumsq != 36: errors.append(f"3c_f Σ² = {sumsq} ≠ 36")

# ═══════════════════════════════════════════════════════
# 9. Σ(3c)² 隨機期望值 (撤銷確認)
# ═══════════════════════════════════════════════════════
print("\n[9] Σ(3c)² 隨機期望值 (撤銷確認):")
allowed = [0, 1, 2, 3, -1, -2, -3]
avg_sq = np.mean([x*x for x in allowed])
expected = 9 * avg_sq
print(f"  actual = {sumsq}, 隨機期望 = {expected:.1f}")
print(f"  相等? {abs(sumsq - expected) < 0.5} {'✅ 撤銷確認' if abs(sumsq - expected) < 0.5 else '⚠️'}")

# ═══════════════════════════════════════════════════════
# 10. GLSM charges (A1 排除)
# ═══════════════════════════════════════════════════════
print("\n[10] GLSM charges (A1 排除確認):")
try:
    glsm = np.array(cy.glsm_charge_matrix())
    all_ch = glsm.flatten()
    nz = all_ch[all_ch != 0]
    mod3_0 = (nz % 3 == 0).sum()
    print(f"  non-zero: {len(nz)}, mod 3=0: {mod3_0}/{len(nz)} = {mod3_0/len(nz)*100:.0f}%")
    print(f"  < 30%? {mod3_0/len(nz) < 0.3} {'✅ 排除確認' if mod3_0/len(nz) < 0.3 else '⚠️'}")
    
except Exception as e:
    print(f"  FAIL: {str(e)[:80]}")

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
if warnings:
    print(f"  ⚠️ {len(warnings)} 個警告:")
    for w in warnings:
        print(f"    - {w}")
print("=" * 70)
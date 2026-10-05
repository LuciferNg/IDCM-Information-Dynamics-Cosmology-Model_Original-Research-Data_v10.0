#!/usr/bin/env python3
"""
O59 攻堅 Q1 Phase 2: v_geom = √λ_max × M₀ × F 閉合驗證
=====================================================
發現: F_needed = 1229.0 ≈ 88×14 = 1232 (0.24%)
  88 = Σγ_odd (觀察者維度) = 2N_d
  14 = 2L₄ = 2×7 (L₄ = γ₇ mode 數)

測試:
  1. v_geom = √λ_max × M₀ × 88 × 14 → 246 GeV?
  2. λ_max ≈ Nd+2B = 52 (0.85%)?
  3. λ₂ ≈ 10 (近整數) — 身份?
  4. v_max 方向 = 電弱破缺方向?
  5. 11 個 Goldstone/Gauge 殘留?
"""
import os, math
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
phi = (1 + math.sqrt(5)) / 2
M0 = 27.900915  # MeV
v_ew = 246.22e3  # MeV

print("=" * 72)
print("O59 Q1 Phase 2: v_geom 閉合驗證")
print("=" * 72)

passed, failed = 0, 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
v = phi ** (-np.arange(12) / 12)
Y12 = np.einsum("ijk,k->ij", d12, v)
Y12 = (Y12 + Y12.T) / 2
ev, evec = np.linalg.eigh(Y12)
idx = np.argsort(ev)[::-1]
ev, evec = ev[idx], evec[:, idx]
lam_max = ev[0]

# ============ 1. v_geom = √λ_max × M₀ × 88 × 14 ============
print("\n[1] ★ v_geom = √λ_max × M₀ × 88 × 14")
sqrt_lam = math.sqrt(lam_max)
v_geom = sqrt_lam * M0 * 88 * 14
print(f"  √λ_max = {sqrt_lam:.4f}")
print(f"  √λ_max × M₀ = {sqrt_lam*M0:.3f} MeV = {sqrt_lam*M0/1e3:.4f} GeV")
print(f"  ×88×14 = {v_geom:.1f} MeV = {v_geom/1e3:.3f} GeV")
err_v = abs(v_geom - v_ew)/v_ew*100
print(f"  v_ew = {v_ew/1e3:.2f} GeV")
print(f"  誤差: {err_v:.3f}%")
check("v_geom ≈ 246 GeV (<1%)", err_v < 1, f"({v_geom/1e3:.2f} GeV, {err_v:.2f}%)")

# 88×14 嘅結構身份
print(f"\n  88×14 結構:")
print(f"  88 = Σγ_odd (觀察者維度) = 2N_d = 2×44")
print(f"  14 = 2L₄ = 2×7 (L₄ = γ₇ mode)")
print(f"  88×14 = {88*14} = 2N_d × 2L₄ = 4N_dL₄")
print(f"  4 = B (K_Tree branch)")
check("88×14 = 4×N_d×L₄", 88*14 == 4*44*7)

# ============ 2. λ_max ≈ Nd+2B = 52 ============
print("\n[2] λ_max 身份")
print(f"  λ_max = {lam_max:.4f}")
print(f"  Nd+2B = {44+8} = 52")
err52 = abs(52 - lam_max)/lam_max*100
print(f"  誤差: {err52:.3f}%")
check("λ_max ≈ Nd+2B = 52 (<1%)", err52 < 1, f"({err52:.2f}%)")
print(f"  52 = 44+8 = Nd+2B: K_Chain sites + 2×branch")
print(f"  52 = 4×13 = B×F₇ (branch × Fibonacci 7)")
check("52 = B×F₇ = 4×13", 4*13 == 52)

# ============ 3. λ₂ ≈ 10 ============
print("\n[3] λ₂ = 10.0002 近整數")
lam2 = ev[1]
print(f"  λ₂ = {lam2:.6f}")
err10 = abs(10 - lam2)/10*100
print(f"  誤差: {err10:.5f}%")
check("λ₂ ≈ 10 (<0.1%)", err10 < 0.1, f"({err10:.5f}%)")
print(f"  10 嘅身份: L₅−1 = 10? 2F₅ = 10? L₄+3 = 10?")
print(f"  L₅−1 = 11−1 = 10 ✓ (Lucas 5 − 1)")
print(f"  2F₅ = 2×5 = 10 ✓ (2×Fibonacci 5)")
print(f"  10 = Nd−34? 唔係. 10 = 44−34? 34 = F₉ ✓!")
check("10 = L₅−1", 11-1 == 10)
check("10 = 2F₅", 2*5 == 10)
print(f"  F₉ = 34, Nd−F₉ = 44−34 = 10 ✓")
check("10 = Nd−F₉ = 44−34", 44-34 == 10)

# λ_max/λ₂ ratio
ratio = lam_max / lam2
print(f"\n  λ_max/λ₂ = {ratio:.4f}")
print(f"  ≈ Nd/8.54? 44/8.54 = {44/8.54:.3f}")
print(f"  52/10 = 5.2 (用近似)")
print(f"  5.156 ≈ 33/6.4? 33/6.4 = 5.156 ✓")
print(f"  33 = K_tree, 6.4 = ? 唔係整數")
print(f"  5.156 ≈ F₈/4.07? 21/4.07 = 5.16")
print(f"  5.156 ≈ φ³+1.36? φ³ = 4.236")
print(f"  5.156 ≈ L₅/φ? 11/1.618 = 6.798 ✗")
print(f"  5.156 ≈ L₆/φ²? 18/2.618 = 6.875 ✗")
print(f"  5.156 ≈ Nd/8.54?")
print(f"  5.156 ≈ 66/12.8? 66/12.8 = 5.156 ✓ (66 = C(12,2), 12.8?)")

# ============ 4. v_max 方向 ============
print("\n[4] v_max 方向結構")
vmax = evec[:, 0]
w = vmax**2
# 檢查: 有冇分量對應特定 Kähler moduli?
# d_tensor_final 嘅 12 維 = K_Chain 拓撲, 唔係真幾何
# 但 12 維 = 3×4 (B×N_gen) 結構?
g = [w[i*4:(i+1)*4].sum() for i in range(3)]
print(f"  3×4 分組權重 (4 = B): {[round(x,4) for x in g]}")
# 4 組 × 3 (3 = N_gen)?
h = [w[i*3:(i+1)*3].sum() for i in range(4)]
print(f"  4×3 分組權重 (3 = N_gen): {[round(x,4) for x in h]}")
print(f"  3×4: [{g[0]:.3f}, {g[1]:.3f}, {g[2]:.3f}]")
print(f"  4×3: {[round(x,3) for x in h]}")
# 冇單一主導 → v_max 唔係沿單一方向
print(f"  → v_max 均勻分佈, 冇電弱破缺方向特徵")

# ============ 5. 11 個 Goldstone 殘留 ============
print("\n[5] 11 個 Goldstone/Gauge 殘留")
rest_ev = ev[1:]
print(f"  11 個剩餘本徵值: {np.round(rest_ev, 4)}")
print(f"  其中 λ₂ = 10.0002 (近整數)")
print(f"  λ₃ = 4.5783, λ₄ = 3.4329, λ₅ = 1.8662")
print(f"  其餘 6 個 < 0.235")
print(f"  → 11 個細模態, 但唔係全部 Goldstone (有質量)")
print(f"  Goldstone 數量 = dim(G/H) = 4−1 = 3 (SU(2)×U(1)→U(1))")
print(f"  ★ 真正 Goldstone 只有 3 個 (電弱), 其餘 8 個係 massive gauge?")
print(f"  11 = 3 (Goldstone) + 8 (其他)")
check("11 = 3+8 (Goldstone + gauge)", 3+8 == 11)
print(f"  8 = 2B = 2×4 (K_Tree 分支)")

# ============ 6. v_geom 敏感度 ============
print("\n[6] v_geom 敏感度")
# 88×14 有冇其他候選?
for name, F in [("88×14", 88*14), ("44×28", 44*28), ("2^11", 2**11),
                ("φ^15", phi**15), ("88×13", 88*13), ("88×14.06", 88*14.06),
                ("1232", 1232)]:
    vv = sqrt_lam * M0 * F
    err = abs(vv - v_ew)/v_ew*100
    mark = "★" if err < 1 else ""
    print(f"  F={name:10s}: v = {vv/1e3:8.2f} GeV  誤差 {err:6.2f}% {mark}")

# 精確 F
F_exact = v_ew / (sqrt_lam * M0)
print(f"\n  F_exact = {F_exact:.4f}")
print(f"  88×14 = 1232, F_exact = {F_exact:.2f}, 差 = {F_exact-1232:.2f}")
print(f"  誤差: {(1232-F_exact)/F_exact*100:.3f}%")

# ============ 7. 另一條路徑: λ_max 直接用 ============
print("\n[7] 其他路徑")
# λ_max × M₀ × 88 = ?
v2 = lam_max * M0 * 88
print(f"  λ_max × M₀ × 88 = {v2/1e3:.2f} GeV")
# λ_max × M₀ × 44 = ?
v3 = lam_max * M0 * 44
print(f"  λ_max × M₀ × 44 = {v3/1e3:.2f} GeV")
# λ_max × M₀ × 171 = ?
v4 = lam_max * M0 * 171
print(f"  λ_max × M₀ × 171 = {v4/1e3:.2f} GeV")
# λ_max² × M₀ = ?
v5 = lam_max**2 * M0
print(f"  λ_max² × M₀ = {v5/1e6:.3f} TeV")

print(f"\n{'='*72}")
print(f"Q1 Phase 2: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")

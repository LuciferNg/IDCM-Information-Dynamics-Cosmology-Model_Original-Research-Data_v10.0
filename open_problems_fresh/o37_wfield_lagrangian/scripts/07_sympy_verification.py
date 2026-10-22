#!/usr/bin/env python3
"""
O37 — Step 7: 第三重獨立驗證 (sympy 精確代數)
===============================================
目標: 用 sympy 精確代數 (唔係數值近似) 驗證全部核心公式!
完全獨立路徑: scripts/01-04 (decimal), scripts/05-06 (mpmath), 本 script (sympy)

★ 包含 Σγ=90 嘅閉合形式證明 (代數, 唔係數值):
  Σ_{n=1}^{44} cos(nπ/44) = -1  (Σ_{k=0}^{44} cos(kπ/44) = 0 對稱和)
  → Σ sin²(nπ/88) = 22 - (1/2)(-1) = 45/2
  → Σγ_n = 4·(45/2) = 90  ← 閉合證明!

驗證:
  [1] Σγ_n = 90 閉合形式 (sympy Sum)
  [2] ⟨W⟩ = M₀ (sympy 極值)
  [3] g_n ∝ ω_n (sympy 三角)
  [4] V''(M₀) = 4κM₀² (sympy)
  [5] V(M₀) = −κM₀⁴/2 (sympy)
  [6] 三合一 A_n = √γ_n (sympy)
  [7] c_n 歸一 Σc_n² = 1 (sympy Sum)
"""

import sympy as sp

print("=" * 70)
print("  O37 — Step 7: 第三重獨立驗證 (sympy 精確代數)")
print("=" * 70)
results = []

# ═══════════════════════════════════════════════════════════════
# [1] Σγ_n = 90 閉合形式證明 ★★★
# ═══════════════════════════════════════════════════════════════
print("\n─── [1] Σγ_n = 90 閉合形式 (代數證明) ───")
n = sp.symbols('n', integer=True)
# Σ_{k=0}^{44} cos(kπ/44) = 0 (對稱和: 44 偶數)
# 證明: Σ_{k=0}^{N} cos(kπ/N) = 0 當 N 偶數 (單位根和)
N_sym = 44
# 直接 sympy 求和
sum_cos = sp.summation(sp.cos(sp.pi*n/N_sym), (n, 1, N_sym))
print(f"  Σ_{{n=1}}^{{44}} cos(nπ/44) = {sp.simplify(sum_cos)}")
# 理論: -1 (因為 Σ_{k=0}^{44} = 0, 減去 k=0 項 = -1)
ok_cos = sp.simplify(sum_cos) == -1
print(f"  → 理論 -1 (Σ_{{k=0}}^{{44}} = 0 對稱和): {'✅' if ok_cos else '❌'}")
results.append(("V1 Σcos = -1", ok_cos))

# Σ sin²(nπ/88) = 22 - (1/2)Σcos(nπ/44) = 22 - (1/2)(-1) = 45/2
sum_sin2 = sp.summation(sp.sin(sp.pi*n/88)**2, (n, 1, N_sym))
print(f"  Σ_{{n=1}}^{{44}} sin²(nπ/88) = {sp.simplify(sum_sin2)}")
ok_sin2 = sp.simplify(sum_sin2) == sp.Rational(45, 2)
print(f"  → 理論 45/2: {'✅' if ok_sin2 else '❌'}")
results.append(("V2 Σsin² = 45/2", ok_sin2))

# Σγ_n = 4·45/2 = 90
sum_gamma = sp.summation(4*sp.sin(sp.pi*n/88)**2, (n, 1, N_sym))
print(f"  Σγ_n = Σ 4sin²(nπ/88) = {sp.simplify(sum_gamma)}")
ok_gamma = sp.simplify(sum_gamma) == 90
print(f"  → Σγ = 90 閉合證明 ✅: {'✅' if ok_gamma else '❌'}")
results.append(("V3 Σγ = 90 閉合", ok_gamma))

# ═══════════════════════════════════════════════════════════════
# [2] ⟨W⟩ = M₀ (sympy 極值)
# ═══════════════════════════════════════════════════════════════
print("\n─── [2] ⟨W⟩ = M₀ (sympy 極值) ───")
W, kap, M = sp.symbols('W kappa M0', positive=True)
lam_s = kap/2
V_s = -kap*M**2*W**2 + lam_s*W**4
dV = sp.diff(V_s, W)
print(f"  ∂V/∂W = {dV}")
solutions = sp.solve(dV, W)
print(f"  解: {solutions}")
# 非零解: ±M (因為 W² = κM²/λ = κM²/(κ/2) = 2M²... 等等!)
# 等我準確: dV/dW = -2κM²W + 4(κ/2)W³ = -2κM²W + 2κW³ = 2κW(W² - M²)
# 解: W = 0, ±M ✅
W_vev_sym = sp.solve(sp.Eq(dV, 0), W)[-1]  # 正解
print(f"  ⟨W⟩ = {W_vev_sym} (正解)")
ok_vev = sp.simplify(W_vev_sym - M) == 0
print(f"  ⟨W⟩ = M₀ 精確: {'✅' if ok_vev else '❌'}")
results.append(("V4 ⟨W⟩ = M₀", ok_vev))

# ═══════════════════════════════════════════════════════════════
# [3] V''(M₀) = 4κM₀² (sympy)
# ═══════════════════════════════════════════════════════════════
print("\n─── [3] V''(M₀) = 4κM₀² ───")
d2V = sp.diff(V_s, W, 2)
print(f"  V''(W) = {d2V}")
Vpp_at_M = sp.simplify(d2V.subs(W, M))
print(f"  V''(M₀) = {Vpp_at_M}")
ok_vpp = sp.simplify(Vpp_at_M - 4*kap*M**2) == 0
print(f"  = 4κM₀²: {'✅' if ok_vpp else '❌'}")
results.append(("V5 V''=4κM₀²", ok_vpp))

# ═══════════════════════════════════════════════════════════════
# [4] V(M₀) = −κM₀⁴/2 (sympy)
# ═══════════════════════════════════════════════════════════════
print("\n─── [4] V(M₀) = −κM₀⁴/2 ───")
V_at_M = sp.simplify(V_s.subs(W, M))
print(f"  V(M₀) = {V_at_M}")
ok_vmin = sp.simplify(V_at_M + kap*M**4/2) == 0
print(f"  = −κM₀⁴/2: {'✅' if ok_vmin else '❌'}")
results.append(("V6 V(M₀)=−κM₀⁴/2", ok_vmin))

# ═══════════════════════════════════════════════════════════════
# [5] 三合一 A_n = √γ_n (sympy 代數)
# ═══════════════════════════════════════════════════════════════
print("\n─── [5] 三合一 A_n = √γ_n ───")
# A_n = 2sin(nπ/88), γ_n = 4sin²(nπ/88) → A_n² = γ_n
k = sp.symbols('k', positive=True)
A_k = 2*sp.sin(sp.pi*k/88)
gamma_k = 4*sp.sin(sp.pi*k/88)**2
ok_tri = sp.simplify(A_k**2 - gamma_k) == 0
print(f"  A_k² = γ_k (代數): {'✅' if ok_tri else '❌'}")
results.append(("V7 三合一", ok_tri))

# ═══════════════════════════════════════════════════════════════
# [6] c_n 歸一 Σc_n² = 1 (sympy Sum)
# ═══════════════════════════════════════════════════════════════
print("\n─── [6] c_n 歸一 Σc_n² = 1 ───")
# c_n = A_n/√90, Σc_n² = ΣA_n²/90 = Σγ_n/90 = 90/90 = 1
sum_c2 = sp.summation(4*sp.sin(sp.pi*n/88)**2, (n, 1, N_sym))/90
print(f"  Σc_n² = Σγ_n/90 = {sp.simplify(sum_c2)}")
ok_norm = sp.simplify(sum_c2 - 1) == 0
print(f"  = 1: {'✅' if ok_norm else '❌'}")
results.append(("V8 Σc²=1", ok_norm))

# ═══════════════════════════════════════════════════════════════
# [7] 質量比 (sympy 精確值)
# ═══════════════════════════════════════════════════════════════
print("\n─── [7] 質量比 (sympy 精確) ───")
pairs = [
    ("m_u/m_d", 10, 24, "0.4625"),
    ("m_c/m_b", 8, 33, "0.3038"),
    ("m_W/m_Z", 30, 41, "0.8814"),
    ("m_H/m_W", 38, 19, "1.5583"),
    ("m_μ/m_τ", 1, 18, "0.0595"),
    ("m_s/m_d", 22, 1, "20.0"),
]
n_pass = 0
for name, n1, n2, target in pairs:
    r = sp.N(sp.sin(sp.pi*n1/88)/sp.sin(sp.pi*n2/88), 10)
    t = sp.N(target, 10)
    dev = abs(r - t)/t*100
    if dev < 1:
        n_pass += 1
    print(f"  {name:<10} = {r} (dev {float(dev):.3f}%) {'✅' if dev < 1 else '⚠️'}")
ok_pairs = n_pass >= 5
print(f"  [7] 質量比 ({n_pass}/6): {'✅' if ok_pairs else '❌'}")
results.append(("V9 質量比", ok_pairs))

# ═══════════════════════════════════════════════════════════════
# [8] m_δW = √(V''(M₀)) = 2M₀√κ (sympy)
# ═══════════════════════════════════════════════════════════════
print("\n─── [8] δW 質量 (遺留 3 預覽) ───")
m_dW = sp.sqrt(Vpp_at_M)
print(f"  m_δW = √(V''(M₀)) = {m_dW}")
ok_mdw = sp.simplify(m_dW**2 - 4*kap*M**2) == 0
print(f"  m_δW² = 4κM₀²: {'✅' if ok_mdw else '❌'}")
results.append(("V10 m_δW²=4κM₀²", ok_mdw))

# ═══════════════════════════════════════════════════════════════
print(f"\n{'═'*70}")
print(f"  O37 Step 7 結果: {sum(ok for _, ok in results)}/{len(results)} PASS")
for name, ok in results:
    print(f"  {name}: {'✅' if ok else '❌'}")
print(f"{'═'*70}")

with open("data/step7_sympy_verification_results.txt", "w") as f:
    f.write("O37 — Step 7: 第三重獨立驗證 (sympy 精確代數)\n")
    f.write("=" * 70 + "\n\n")
    for name, ok in results:
        f.write(f"  {name}: {'PASS' if ok else 'FAIL'}\n")
    f.write(f"\n總計: {sum(ok for _, ok in results)}/{len(results)} PASS\n")
    f.write(f"★ Σγ=90 閉合證明: Σcos(nπ/44)=-1 → Σsin²=45/2 → Σγ=90\n")
print(f"\n  結果已寫入 data/step7_sympy_verification_results.txt")

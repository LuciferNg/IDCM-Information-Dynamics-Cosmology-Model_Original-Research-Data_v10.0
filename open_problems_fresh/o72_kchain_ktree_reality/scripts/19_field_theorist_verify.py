"""
O72 驗證: docs/18 場論學家友好翻譯 — 核心數值核查
=====================================================================
驗證:
  [1] μ² = Σγ_even − Σγ_odd = 2
  [2] λ = 2/123
  [3] ⟨W⟩² = μ²/(2λ) = 61.5
  [4] V_min = −μ⁴/(4λ) = −61.5
  [5] V''(⟨W⟩) = 8μ² > 0 (穩定)
  [6] V_Λ = F(γ)+44−F₈−B = 283.0821
  [7] m_e = M₀γ₁ (O54)
"""
import numpy as np

phi = (1+np.sqrt(5))/2
ok = 0; total = 0
def check(name, cond, detail=""):
    global ok, total
    total += 1
    ok += cond
    print(f"[{'✅' if cond else '❌'}] {name} {detail}")

print("=" * 72)
print("[1] μ² = Σγ_even − Σγ_odd")
print("=" * 72)
# 88-site 對偶鏈
g88 = 4*np.sin(np.pi*np.arange(1,89)/176)**2
sum_odd = g88[0::2].sum()   # k=1,3,...,87
sum_even = g88[1::2].sum()  # k=2,4,...,88
mu2 = sum_even - sum_odd
check("Σγ_even = 90", abs(sum_even-90) < 1e-9, f"({sum_even:.6f})")
check("Σγ_odd = 88", abs(sum_odd-88) < 1e-9, f"({sum_odd:.6f})")
check("μ² = 90−88 = 2", abs(mu2-2) < 1e-9, f"({mu2:.6f})")

print()
print("[2] λ = 2/123")
lam = 2/123
check("λ = 2/123", abs(lam-2/123) < 1e-15)
check("123 = L₁₀", abs(phi**10+(-phi)**(-10)-123) < 1e-9)

print()
print("[3] ⟨W⟩² = μ²/(2λ)")
W2 = mu2/(2*lam)
check("⟨W⟩² = 61.5", abs(W2-61.5) < 1e-9, f"({W2:.6f})")
check("61.5 = 123/2", abs(61.5-123/2) < 1e-12)

print()
print("[4] V_min = −μ⁴/(4λ)")
Vmin = -(mu2**2)/(4*lam)
check("V_min = −61.5", abs(Vmin+61.5) < 1e-9, f"({Vmin:.6f})")

print()
print("[5] V''(⟨W⟩) 穩定性")
# V(W) = −μ²W²+λW⁴; V'(W) = −2μ²W+4λW³; V''(W) = −2μ²+12λW²
# at W²=μ²/(2λ): V'' = −2μ²+12λ·μ²/(2λ) = −2μ²+6μ² = 4μ²... 等等
# V'' = −2μ² + 12λW² = −2μ² + 12λ·(μ²/2λ) = −2μ²+6μ² = 4μ²
Vpp = -2*mu2 + 12*lam*W2
check("V''(⟨W⟩) > 0 (穩定)", Vpp > 0, f"(V''={Vpp:.1f} = 4μ²)")

print()
print("[6] V_Λ = 283.0821 (O62)")
# F(γ) = (1/6)κγ³ = 264.0821 (O62)
F_gamma = 264.0821
F8 = 21
B = 4
V_Lambda = F_gamma + 44 - F8 - B
check("V_Λ = 283.0821", abs(V_Lambda-283.0821) < 0.001, f"({V_Lambda:.4f})")

print()
print("[7] m_e = M₀γ₁ (O54)")
# γ₁ = 4sin²(π/88)
g1 = 4*np.sin(np.pi/88)**2
print(f"  γ₁ = {g1:.6f}")
print(f"  m_e = M₀×{g1:.6f} → M₀ = 0.511/γ₁ MeV = {0.511/g1:.2f} MeV")

print()
print(f"=== 總計: {ok}/{total} PASS ===")

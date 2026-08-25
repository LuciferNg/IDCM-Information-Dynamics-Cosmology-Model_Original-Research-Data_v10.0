"""
K_Tree 33 層詳細結構推導 — 每層模式、邊界、beat 耦合、層間連結
================================================================
基於已確立結構:
  • M = 33 = h¹¹−3 = (χ−2)/4 = ambient Picard rank
  • B = 4 = φ³−φ⁻³ (MERA branching)
  • μ_m = φ^(N_d·L − m), N_d·L = 583/2 = 291.5, m = 0..33
  • K = K_chain ⊗ K_tree: λ_{n,m} = γ_n × μ_m
  • Stair: k_u = 33β (UV pinned), k_d = 26β−φ⁻⁴ (Casimir), k_l = 19β (IR pinned)
  • ε = φ⁻¹/4, κ = 1/16 = 1/B²

推導目標:
  1. 每層嘅完整結構 (節點數、能量、時間、44-mode 投影)
  2. 邊界結構 (UV/IR pinned + Casimir)
  3. Beat 耦合 (層內 44-mode beat × μ_m, 跨層 φ 比例)
  4. 層間連結 (MERA isometry + disentangler 數學)
"""
import math
import sympy as sp

phi = (1 + sp.sqrt(5)) / 2
phii = phi - 1
eps = phii / 4
kappa = sp.Rational(1, 16)
B = sp.simplify(phi**3 - phi**(-3))
Nd = 44
L = sp.Rational(53, 8)
NdL = sp.simplify(Nd * L)   # 583/2
M = 33
beta = phii / 2
L5 = 11

print("=" * 76)
print("K_Tree 33 層完整結構推導")
print("=" * 76)
print(f"""
基礎常數:
  φ = {sp.N(phi, 12)}, φ⁻¹ = {sp.N(phii, 12)}
  B = φ³−φ⁻³ = {B} (MERA branching)
  ε = φ⁻¹/4 = {sp.N(eps, 12)}, κ = 1/B² = {kappa}
  N_d·L = 44×53/8 = {NdL} = 291.5
  M = 33, β = φ⁻¹/2 = {sp.N(beta, 12)}
""")

# ═══════════════════════════════════════════════════════════
# 1. 33 層總表
# ═══════════════════════════════════════════════════════════
print("=" * 76)
print("1. 33 層結構總表 (ℓ = 0..33)")
print("=" * 76)
print(f"{'ℓ':>3} | {'節點 4^ℓ':>12} | {'μ_ℓ = φ^(291.5−ℓ)':>22} | {'log₁₀ μ_ℓ':>9} | {'能量比 μ_ℓ/μ₃₃':>12} | {'時間 4^ℓ·t_site':>14}")
print("-" * 88)

t_site = 0.306  # Gyr
rows = []
for m in range(M + 1):
    nodes = 4**m
    mu = sp.N(phi**(NdL - m), 15)
    log10_mu = float(sp.N(sp.log(mu, 10), 10))
    ratio = sp.N(phi**(33 - m), 8)  # μ_m / μ_33 = φ^(33-m)
    t = nodes * t_site
    rows.append((m, nodes, mu, log10_mu, ratio, t))
    # 只印關鍵層 (0, 3, 7, 11, 19, 22, 26, 33) + 每 5 層
    if m in [0, 1, 3, 5, 7, 11, 15, 19, 22, 26, 29, 33]:
        print(f"{m:>3} | {nodes:>12,} | φ^({sp.nsimplify(NdL-m)}) = {sp.N(mu,6):>12} | {log10_mu:>9.2f} | {sp.N(ratio,6):>12} | {t:>14.4g}")

print(f"\n  33 層總節點: Σ4^ℓ = (4³⁴−1)/3 = {(4**34-1)//3:,}")
print(f"  能量跨度: μ₀/μ₃₃ = φ³³ = {sp.N(phi**33, 8):.4g} (33 個 φ 倍)")
print(f"  時間跨度: t(33)/t(0) = 4³³ = {4**33:.4g}")

# ═══════════════════════════════════════════════════════════
# 2. 每層嘅模式結構 — 44 個 chain mode 投影
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76)
print("2. 每層嘅模式結構 — 44 chain modes × μ_ℓ")
print("=" * 76)
print(f"""
  K = K_chain ⊗ K_tree ⇒ λ_{{n,m}} = γ_n × μ_m
  每層 ℓ 有 44 個 chain-mode 投影 (n=1..44):
    λ_{{n,ℓ}} = γ_n × μ_ℓ,  γ_n = 4sin²(πn/88)

  每層嘅完整模式譜 (以 ℓ=0 為例):
""")

def gamma(n):
    return 4 * math.sin(math.pi * n / 88)**2

# 每層嘅 mode 結構 — 展示 ℓ=0 同 ℓ=33 嘅譜
for m in [0, 11, 22, 33]:
    mu = float(sp.N(phi**(NdL - m), 15))
    g22 = gamma(22)  # = 2
    g44 = gamma(44)  # = 4
    lam22 = g22 * mu
    lam44 = g44 * mu
    lam1 = gamma(1) * mu
    print(f"  ℓ={m:>2}: μ_ℓ = {mu:.6e}")
    print(f"        λ(1,ℓ)  = γ₁·μ_ℓ = {gamma(1):.6f}×{mu:.3e} = {lam1:.6e}  (基模)")
    print(f"        λ(22,ℓ) = γ₂₂·μ_ℓ = 2×{mu:.3e}   = {lam22:.6e}  (光速 mode)")
    print(f"        λ(44,ℓ) = γ₄₄·μ_ℓ = 4×{mu:.3e}   = {lam44:.6e}  (駐波極限)")

# ═══════════════════════════════════════════════════════════
# 3. 邊界結構
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76)
print("3. 邊界結構 — UV/IR pinned + Casimir")
print("=" * 76)
print(f"""
  K_Tree 兩端固定:

  ┌─────────────────────────────────────────────────────────┐
  │  UV 邊界 (ℓ=0):  μ₀ = φ^291.5   ← 能量最大            │
  │     Up sector pinned: k_u = 33β = {sp.N(33*beta, 6)} (無 correction)  │
  │     (33 = M = 樹頂, UV pinned at M)                     │
  │                                                          │
  │  中間層 (ℓ=11): μ₁₁ = φ^280.5                           │
  │     Down sector: k_d = 26β − φ⁻⁴                        │
  │     = {sp.N(26*beta - phii**4, 8)} (Casimir 修正 φ⁻⁴ = {sp.N(phii**4, 8)})  │
  │     (26 = M − L₄ = 33−7, 中間未 pinned 層)              │
  │                                                          │
  │  IR 邊界 (ℓ=33): μ₃₃ = φ^258.5  ← 能量最小             │
  │     Lepton pinned: k_l = 19β = {sp.N(19*beta, 6)} (無 correction)          │
  │     (19 = M − 2L₄ = 33−14, IR pinned at L₅=11)          │
  └─────────────────────────────────────────────────────────┘

  Stair 結構: 33 → 26 → 19 (step = L₄ = 7 = B + L₂ = 4+3)
  只有 Down (中間層) 有 Casimir 修正 — 因為佢夾喺兩個 pinned 邊界之間
  φ⁻⁴ = 0.145898 係 L₄ = φ⁴+φ⁻⁴ = 7 嘅 evanescent tail
""")

# ═══════════════════════════════════════════════════════════
# 4. Beat 耦合結構
# ═══════════════════════════════════════════════════════════
print("=" * 76)
print("4. Beat 耦合結構 — 層內 + 跨層")
print("=" * 76)

# 4a. 層內 beat
print("\n  4a. 層內 beat (同一層 ℓ 嘅 44 個 mode 之間):")
print(f"""
  beat_ℓ(i,j) = |ω_{{i,ℓ}} − ω_{{j,ℓ}}| = μ_ℓ × |ω_i − ω_j|  (chain beat × tree scale)
  每層有 946 個 beat (44 choose 2), 全部同層縮放 μ_ℓ
  層內 beat 比例: beat_ℓ(i,j)/beat_ℓ(k,l) = beat₀(i,j)/beat₀(k,l)  (層內不變量!)
""")

# 驗證層內 beat 縮放
w = [2 * math.sin(math.pi * n / 88) for n in range(1, 45)]
def beat(i, j):
    return abs(w[i-1] - w[j-1])

# 展示幾個 beat 喺不同層嘅縮放
beats = [(5, 6), (19, 25), (13, 14), (22, 26)]
print(f"  {'beat':>10} | {'ℓ=0':>12} | {'ℓ=11':>12} | {'ℓ=22':>12} | {'ℓ=33':>12} | 跨層比例")
print("  " + "-" * 70)
for (i, j) in beats:
    b = beat(i, j)
    vals = []
    for m in [0, 11, 22, 33]:
        mu = float(sp.N(phi**(NdL - m), 15))
        vals.append(b * mu)
    # 跨層比例: μ_0/μ_33 = φ^33
    ratio = float(sp.N(phi**33, 8))
    print(f"  ({i:>2},{j:>2})    | {vals[0]:.4e} | {vals[1]:.4e} | {vals[2]:.4e} | {vals[3]:.4e} | ×{ratio:.4g}")

# 4b. 跨層 beat (不同層之間)
print("\n  4b. 跨層 beat (不同層嘅 mode 之間):")
print(f"""
  ω_{{n,ℓ}} = ω_n × μ_ℓ (chain freq × tree scale)
  跨層 beat: |ω_{{i,ℓ}} − ω_{{j,ℓ'}}| = |ω_i·μ_ℓ − ω_j·μ_ℓ'|
  特殊情況 ℓ' = ℓ±1:
    |ω_i·μ_ℓ − ω_j·μ_{{ℓ±1}}| = μ_ℓ·|ω_i − ω_j·φ^{{±1}}|
  跨層 coupling 嘅核心: μ_{{ℓ+1}}/μ_ℓ = φ⁻¹ (每層下降 φ 倍)

  MERA disentangler 耦合:
    同層相鄰:  |ω_i − ω_j| × μ_ℓ  (946 個層內 beat)
    跨層父子:  |ω_i − ω_j·φ⁻¹| × μ_ℓ  (4 個子節點耦合)
""")

# 4c. 層間 beat 嘅 φ 結構
print("  4c. 層間 φ 結構 — 樹嘅『音程』:")
intervals = [(0, "φ⁰ = 1 (同層)"), (1, "φ⁻¹ = 0.618 (父子)"),
             (2, "φ⁻² = 0.382 (祖孫)"), (3, "φ⁻³ = 0.236 (曾祖孫)")]
for k, desc in intervals:
    print(f"    μ_ℓ / μ_{{ℓ+{k}}} = φ^{k} = {sp.N(phi**k, 6):>8}  ← {desc}")

# ═══════════════════════════════════════════════════════════
# 5. 層間連結方式 — MERA isometry + disentangler
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76)
print("5. 層間連結方式 — MERA 幾何")
print("=" * 76)
print(f"""
  K_Tree 層間連結 = MERA (Multi-scale Entanglement Renormalization):

  ┌─────────────────────────────────────────────────────────┐
  │  ℓ=0:  ● (1 node)              ← UV (最大能量)          │
  │        │ isometry U† (4→1 粗粒化)                       │
  │  ℓ=1:  ● ● ● ● (4 nodes)                              │
  │        │ disentangler V (鄰居去纏結)                    │
  │  ℓ=2:  ●●●●●●●●●●●●●●●● (16 nodes)                   │
  │        │ ...                                            │
  │  ℓ=ℓ:  B^ℓ = 4^ℓ nodes                                 │
  │        │                                                │
  │  ℓ=33: 4³³ nodes (2^66)        ← IR (最小能量)          │
  └─────────────────────────────────────────────────────────┘

  每層兩類運算元:
""")

# isometry + disentangler 結構
print("  Isometry (粗粒化): 4 個子節點 → 1 個父節點")
print(f"    U: ℂ^(4^ℓ) → ℂ^(4^ℓ⁻¹)  (每層壓縮 4 倍)")
print(f"    U†U = I (等距), UU† = 投影 (非滿秩)")
print(f"    isometry 耦合強度: ε = φ⁻¹/4 = {sp.N(eps, 8)} (pipeline gap)")

print("\n  Disentangler (去纏結): 2 個相鄰節點 ↔ 2 個相鄰節點")
print(f"    V: ℂ² ⊗ ℂ² → ℂ² ⊗ ℂ²  (保距, 唔改變層)")
print(f"    V 移除層內短距纏結, 令粗粒化無損")
print(f"    disentangler 耦合: κ = 1/16 = 1/B² (最小作用單元)")

# 層間 Hamiltonian
print("\n  層間 Hamiltonian (離散作用量):")
print(f"""
  S_tree = Σ_{{n,ℓ}} B^{{−ℓ}}·(W_{{n,ℓ}} − U·W_{{n,ℓ−1}})²   (tree kinetic)
         + Σ_{{⟨n,m⟩}} g_sync·cos(θ_n − θ_m − 2π/88)          (sync coupling)

  每層嘅 kinetic 項以 B^{{−ℓ}} = 4^{{−ℓ}} 縮放
  → 深層 (大 ℓ) 嘅 fluctuation 被 4^{{−ℓ}} 壓低 — RG 階梯
  → 層間耦合強度: g_ℓ = B^{{−ℓ}} × g_sync
""")

# 計算層間耦合強度表
print("  層間耦合強度 g_ℓ = 4^{−ℓ}:")
for m in [0, 5, 11, 22, 33]:
    print(f"    g_{m:>2} = 4^{{-{m}}} = 4^{{-{m}}} = {4**(-m):.6e}")

# ═══════════════════════════════════════════════════════════
# 6. 層內 44-mode 投影嘅完整譜 (ℓ=0 詳細)
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76)
print("6. 每層嘅 44-mode 投影 — 譜結構 (ℓ=0)")
print("=" * 76)
print(f"{'n':>3} | {'γ_n':>10} | {'λ_{n,0} = γ_n·μ₀':>12} | {'v_g/c':>8} | {'mode 角色':>16}")
print("-" * 60)
mu0 = float(sp.N(phi**NdL, 15))
roles = {1: "基模 (SYNC)", 2: "SYNC 基模", 7: "DM mode", 22: "光速 mode ★",
         33: "Z₂ 對偶 γ₁₁", 44: "駐波極限", 6: "中微子 p6"}
for n in range(1, 45):
    g = gamma(n)
    vg = math.cos(math.pi * n / 88)
    role = roles.get(n, "")
    if n in [1, 2, 7, 22, 33, 44, 6] or n % 11 == 0:
        print(f"{n:>3} | {g:>10.6f} | {g*mu0:>12.6e} | {vg:>8.4f} | {role:>16}")

print(f"\n  每層 μ_ℓ 縮放全部 44 個 mode: λ_{{n,ℓ}} = γ_n × μ_ℓ")
print(f"  層間: λ_{{n,ℓ+1}}/λ_{{n,ℓ}} = φ⁻¹ (每層下降 φ 倍)")
print(f"  層內: λ_{{i,ℓ}}/λ_{{j,ℓ}} = γ_i/γ_j (層內比例不變)")

# ═══════════════════════════════════════════════════════════
# 7. 結構閉合 — 33 層嘅整體
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 76)
print("7. 結構閉合 — 33 層整體性質")
print("=" * 76)

# 光譜總數
total_eig = 44 * 34  # chain modes × tree levels
print(f"  光譜總數: 44 × 34 = {total_eig} 個 eigenvalue λ_{{n,m}}")
print(f"  (34 = M+1 = 33+1, 包括 ℓ=0..33)")

# 每層光譜間距
print(f"\n  層內光譜間距 (最小): γ₁ = 4sin²(π/88) = {gamma(1):.6f}")
print(f"  層間光譜間距: μ_ℓ/μ_{{ℓ+1}} = φ = {sp.N(phi, 8)}")

# MERA 深度
print(f"\n  MERA 深度: L = 53/8 = {sp.N(L, 6)} (非整數! 深度係『分數』)")
print(f"  N_d·L = 44 × 53/8 = 291.5 = 583/2")
print(f"  33 層 × 8.833... = 291.5 — 每層平均 8.83 個 φ-power 步")

# 數域橋樑
print(f"\n  數域結構:")
print(f"    每層 μ_ℓ = φ^(291.5−ℓ) ∈ Q(√5)  (φ 嘅家鄉)")
print(f"    γ_n ∈ Q(ζ_88)⁺  (chain 分圓域)")
print(f"    λ_{{n,ℓ}} ∈ Q(ζ_88)⁺ ⊗ Q(√5)  (複合域)")
print(f"    層間連結 = φ 冪次差 (μ_ℓ/μ_{{ℓ+k}} = φ^k)")

print("\n✅ K_Tree 33 層結構推導完成")

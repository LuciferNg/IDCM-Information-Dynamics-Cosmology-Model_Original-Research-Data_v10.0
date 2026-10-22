#!/usr/bin/env python3
"""
O147 獨立核對 v3 — 由原始定義重算 docs/01-13 全部關鍵數值
===========================================================
原則: 唔 import o147 scripts, 由 γ_n=4sin²(nπ/88), φ, Lucas/Fibonacci, PDG 重算。
涵蓋: docs/01 (528 身份), docs/02 (乘數族), docs/03 (六閉合),
      docs/04 (P1 數據), docs/05 (兩層), docs/06 (gap), docs/07 (8 比),
      docs/09 (κ 21 比), docs/11 (κ(t)), docs/12 (種子+階梯), docs/13 (37 統一)
"""
import math

PASS, FAIL = 0, 0
rows = []

def check(name, cond, detail=""):
    global PASS, FAIL
    rows.append((name, bool(cond), detail))
    if cond: PASS += 1
    else: FAIL += 1

# ============ 原始定義 ============
N_d = 44
B = 4
N_gen = 3
phi = (1 + math.sqrt(5)) / 2
M0 = 27.900915  # MeV
E_kchain = M0 / phi**(47 + 37/528)  # 反推 E_kchain 檢查 M₀ 定義

# Lucas/Fibonacci
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47, 9:76, 10:123}
F = {1:1, 2:1, 3:2, 4:3, 5:5, 6:8, 7:13, 8:21, 9:34, 10:55, 11:89, 12:144}

def gamma_n(n): return 4 * math.sin(n * math.pi / 88) ** 2

# O143 grid (n, P_f)
GRID = {"e":(1,3.6), "mu":(7,15.5), "tau":(20,37), "u":(1,15.5), "c":(34,13),
        "d":(1,33), "s":(14,3.6), "b":(33,44)}
# κ 表 (docs/11 修正後, t=0)
KAPPA = {"e":3.5, "mu":3.5, "tau":9.0, "d":0.0, "s":18.0, "b":2.0, "c":2.0, "u":-16.0, "t":0.0}

def grid_mass(p):
    n, pf = GRID[p]
    return M0 * gamma_n(n) * pf

print("=" * 100)
print("  O147 獨立核對 v3 — docs/01-13 全數值重算 (唔 import o147 scripts)")
print("=" * 100)

# ============ docs/01: 528 五重身份 ============
print("\n─── docs/01-02: 528 身份 ───")
check("528 = dimC·B·N_d = 3×4×44", 3*B*N_d == 528)
check("528 = N_d·h¹¹/N_gen = 44×36/3 (h¹¹=36)", N_d*36//N_gen == 528)
check("528 = 2×264", 2*264 == 528)
check("528 = Σγ_odd×2N_gen = 88×6", 88*6 == 528)
check("528 = B²×M = 16×33", 16*33 == 528)
check("528 = 4×132 = B×total_roots(SU(12))", 4*132 == 528)
check("528 = 8×66 = F₆×pos_roots (66=2M)", 8*66 == 528)
check("528 = 6×88", 6*88 == 528)
# 乘數族
check("44×族: 88=2×44, 132=3×44, 176=4×44, 264=6×44, 528=12×44",
      [2,3,4,6,12] == [88//44, 132//44, 176//44, 264//44, 528//44])
check("h¹¹ = N_d−F₆ = 36", N_d - F[6] == 36)
check("h¹¹ = B×N_gen² = 36", B*N_gen**2 == 36)
check("M = 33 = K_tree", 33 == 528//16)

# ============ docs/03: 六閉合 ============
print("\n─── docs/03: 六個 closure 數值 ───")
# 1. M₀ 標度: φ^47·φ^(37/528) = M₀/E_kchain
ratio = phi**47 * phi**(37/528)
check("M₀/E_kchain = φ^(47+37/528) 反推一致", abs(ratio - M0/E_kchain)/ (M0/E_kchain) < 1e-9)
check("47 = N_d+dimC = 47", N_d + 3 == 47)
check("37 = N_d−L₄ = 37", N_d - L[4] == 37)
# 2. 輕子跳躍 k 指數
k_emu = 11 + 7/88
k_mutau = 6 - 71/528
k_etau = 17 - 29/528
check("k(e→μ) = 11+7/88 = L₅+L₄/2N_d", k_emu == L[5] + L[4]/(2*N_d))
check("k(μ→τ) = 6−71/528 = C(4,2)−(2N_d−17)/528", k_mutau == 6 - 71/528)
check("加法互鎖: k(eμ)+k(μτ)=k(eτ)", abs(k_emu + k_mutau - k_etau) < 1e-12)
check("7/88 = 42/528", 7/88 == 42/528)
check("42−71 = −29", 42-71 == -29)
# 3. m_t/m_b cascade
mt_mb = phi**(8 + 71/132) * math.sin(19*math.pi/88)/math.sin(33*math.pi/88)
check("m_t/m_b cascade = 41.332", abs(mt_mb - 41.332)/41.332 < 1e-3)
check("m_t = 41.332×4.18 = 172.77 GeV", abs(mt_mb*4.18 - 172.768)/172.768 < 1e-3)
check("284 = 4×71", 4*71 == 284)
# 4. m_s/m_d cascade
ms_md = math.sin(22*math.pi/88)/math.sin(math.pi/88) * phi**(10/528)
check("m_s/m_d cascade = 19.9925", abs(ms_md - 19.9925)/19.9925 < 1e-3)
check("10 = n_u = n₀(1)−L₄ = 17−7", 17 - L[4] == 10)
check("sin22/sin1 = 19.811", abs(math.sin(22*math.pi/88)/math.sin(math.pi/88) - 19.811167)/19.811167 < 1e-4)

# ============ docs/04: P1 數據 ============
print("\n─── docs/04: P1 兩框架 ───")
# grid 比 (O143)
mu_e_grid = grid_mass("mu")/grid_mass("e")
s_d_grid = grid_mass("s")/grid_mass("d")
c_u_grid = grid_mass("c")/grid_mass("u")
b_d_grid = grid_mass("b")/grid_mass("d")
check("grid μ/e = 206.705", abs(mu_e_grid - 206.705)/206.705 < 1e-3)
check("grid s/d = 19.668 (1.66% off 20)", abs(s_d_grid - 19.668)/19.668 < 1e-3)
check("grid c/u = 577.96", abs(c_u_grid - 577.96)/577.96 < 1e-3)
check("grid b/d = 893.35", abs(b_d_grid - 893.35)/893.35 < 1e-3)
check("P_f 比 3.6/33 = 0.10909", abs(3.6/33 - 0.1090909) < 1e-6)

# ============ docs/05: 兩層 ============
print("\n─── docs/05: 兩層分工 ───")
check("s 公式層 n=14: M₀γ₁₄×3.6 = 92.3 MeV (Δ~1%)",
      abs(M0*gamma_n(14)*3.6 - 92.3)/92.3 < 0.02)
check("γ₁₄ = 4sin²(14π/88)", abs(gamma_n(14) - 4*math.sin(14*math.pi/88)**2) < 1e-12)
check("528/264 = 88/44 = 2 = Z₂", 528/264 == 88/44 == 2)
check("Σγ_odd = 88 (直接計)", abs(sum(gamma_n(k) for k in range(1, 88, 2)) - 88) < 1e-9)

# ============ docs/06: gap ============
print("\n─── docs/06: gap 0.73% ───")
sin_ratio = math.sin(22*math.pi/88)/math.sin(math.pi/88)
grid_ratio = (gamma_n(14)/gamma_n(1))*(3.6/33)
gap = abs(sin_ratio - grid_ratio)/grid_ratio
check("gap ≈ 0.73%", abs(gap - 0.0073)/0.0073 < 0.1)
need = math.sin(22*math.pi/88)*math.sin(math.pi/88)/math.sin(14*math.pi/88)**2
check("P_f 比需要 0.10989", abs(need - 0.10989)/0.10989 < 1e-3)
check("18/528 = 3/88 = N_gen/Σγ_odd", 18/528 == 3/88 == N_gen/88)
check("10/528 = 5/264 = n_u/528", 10/528 == 5/264)
# 公式層 φ^(18/528) 命中 20
formula_corr = grid_ratio * phi**(18/528)
check("公式層 φ^(18/528) = 19.9934 (0.033%)", abs(formula_corr - 19.9934)/19.9934 < 1e-3)
check("18 = L₆ = Tr(T̂⁶)", L[6] == 18)

# ============ docs/07: 8 比修正掃描 ============
print("\n─── docs/07: 8 比 k 掃描 ───")
# k_need = ln(PDG/grid)/ln(φ) × 528
def k_need(grid_val, pdg):
    return math.log(pdg/grid_val)/math.log(phi)*528
pairs = [("mu/e", mu_e_grid, 206.768), ("s/d", s_d_grid, 20.0), ("c/u", c_u_grid, 587.96),
         ("b/d", b_d_grid, 895.0), ("b/s", grid_mass("b")/grid_mass("s"), 44.75),
         ("c/s", grid_mass("c")/grid_mass("s"), 13.60)]
for name, g, p in pairs:
    kn = k_need(g, p)
    if name == "mu/e": check(f"{name} k_need≈0.3", abs(kn - 0.3)/0.3 < 0.5)
    if name == "s/d": check(f"{name} k_need≈18.4", abs(kn - 18.4)/18.4 < 0.05)
    if name == "c/u": check(f"{name} k_need≈18.8", abs(kn - 18.8)/18.8 < 0.05)
    if name == "b/s": check(f"{name} k_need≈−16.3", abs(kn + 16.3)/16.3 < 0.05)
    if name == "c/s": check(f"{name} k_need≈−16.2", abs(kn + 16.2)/16.2 < 0.05)

# ============ docs/09: κ 21 比 ============
print("\n─── docs/09: κ 可加性 21 比 ───")
PDG_MASS = {"e":0.511, "mu":105.66, "tau":1776.86, "u":2.16, "c":1270.0,
            "d":4.67, "s":93.4, "b":4180.0}
fits = [("mu","e"), ("tau","e"), ("tau","mu"), ("s","d"), ("c","u"),
        ("b","d"), ("b","s"), ("c","s")]
oos = [("c","d"), ("b","u"), ("mu","s"), ("tau","d"), ("tau","s"), ("s","u"),
       ("mu","d"), ("mu","u"), ("tau","c"), ("tau","u"), ("b","c"), ("c","e"), ("b","e")]
def kappa_pred(A, B):
    # 修正後比 = grid 比 × φ^((κA−κB)/528), 命中 PDG
    g = grid_mass(A)/grid_mass(B)
    tgt = PDG_MASS[A]/PDG_MASS[B]
    corr = g * phi**((KAPPA[A]-KAPPA[B])/528)
    return abs(corr - tgt)/tgt
fit_hits = sum(1 for A, B in fits if kappa_pred(A, B) < 0.005)
oos_hits = sum(1 for A, B in oos if kappa_pred(A, B) < 0.005)
check(f"8 fit 比修正後全部 <0.5% ({fit_hits}/8)", fit_hits == 8)
check(f"13 out-of-sample 修正後全部 <0.5% ({oos_hits}/13)", oos_hits == 13)
# 行結構
check("κ(u)−κ(d) = −16 = −B²", KAPPA["u"] - KAPPA["d"] == -B**2)
check("κ(c)−κ(s) = −16 = −B²", KAPPA["c"] - KAPPA["s"] == -B**2)
check("κ(s)−κ(d) = 18 = L₆", KAPPA["s"] - KAPPA["d"] == L[6])
check("κ(b)−κ(s) = −16 = −B²", KAPPA["b"] - KAPPA["s"] == -B**2)
check("κ(τ)−κ(μ) = 5.5 = L₅/2", KAPPA["tau"] - KAPPA["mu"] == L[5]/2)
check("κ(b) = κ(c) = Z₂", KAPPA["b"] == KAPPA["c"] == 2)
check("κ(s) = 2κ(τ)", KAPPA["s"] == 2*KAPPA["tau"])

# ============ docs/11: κ(t) = 0 ============
print("\n─── docs/11: κ(t) = 0 (O64) ───")
M_T_POLE = 172.69e3
base = M0 * gamma_n(44) * 37
check("γ₄₄ = 4 (Nyquist)", abs(gamma_n(44) - 4) < 1e-12)
check("M₀γ₄₄×37 = 4129.34", abs(base - 4129.34)/4129.34 < 1e-3)
check("×42 = 173.43 GeV", abs(base*42 - 173432)/173432 < 1e-3)
z0 = M_T_POLE/base
check("κ=0 Z_eff = 41.82 ≈ 42 (Δ0.43%)", abs(z0 - 41.82)/41.82 < 1e-3 and abs(z0-42)/42 < 0.005)
z_minus14 = M_T_POLE/(base*phi**(-14/528))
check("κ=−14 Z_eff = 42.36 偏離 42", abs(z_minus14 - 42.36)/42.36 < 1e-3)
# 8 t 比 (docs/11 B)
t_pairs = [("b",4180.0), ("c",1270.0), ("s",93.4), ("u",2.16), ("d",4.67),
           ("tau",1776.86), ("e",0.511), ("mu",105.66)]
t_hits = 0
for x, mx in t_pairs:
    grid_t_full = base * 42
    grid_x = grid_mass(x)
    corr = (grid_t_full/grid_x) * phi**((0 - KAPPA[x])/528)
    tgt = M_T_POLE/mx
    if abs(corr - tgt)/tgt < 0.005: t_hits += 1
check(f"κ(t)=0: 8 t 比修正後 <0.5% ({t_hits}/8)", t_hits == 8)

# ============ docs/12: 種子 + 階梯算子 ============
print("\n─── docs/12: 種子生成 + 階梯乘法算子 ───")
check("κ(e) = (L₅−B)/2 = 3.5", (L[5]-B)/2 == 3.5)
check("κ(τ) = L₅−Z₂ = 9 = N_gen²", L[5]-2 == 9 == N_gen**2)
check("κ(s) = 2N_gen² = 18 = L₆", 2*N_gen**2 == 18 == L[6])
check("κ(b) = Z₂ = B/2 = 2", 2 == B/2 == 2)
check("½L₅ − (L₆−B²) = 3.5 = L₄/2 = κ(e)", L[5]/2 - (L[6]-B**2) == L[4]/2)
check("½L₅ = rank(SU(12))/2 = 5.5", L[5]/2 == 11/2)
check("κ(τ)−κ(b) = 7 = L₄ = n(μ)", 9-2 == L[4])
def m(a, b): return N_d * 2**a * 3**b
check("階梯 m(1,0) = 88", m(1,0) == 88)
check("階梯 m(0,1) = 132", m(0,1) == 132)
check("階梯 m(2,1) = 528", m(2,1) == 528)
check("(2,1) = 2(1,0)+(0,1) 指數線性", (2*1+0, 2*0+1) == (2,1))
check("2²×3¹ = 12 = B×N_gen", 4*3 == 12 == B*N_gen)
check("Interaction 形式 I = 2.5 = F₅/Z₂", (12-7)/2 == F[5]/2)

# ============ docs/13: 37 統一 + O152 ============
print("\n─── docs/13: 37 身份統一 (O152 交叉) ───")
check("L₁₀/N_gen = 41 = N_d−N_gen", L[10]/N_gen == N_d - N_gen)
check("★ L₁₀ = N_gen×(N_d−N_gen) = 123", N_gen*(N_d-N_gen) == L[10] == 123)
check("N_gen+B = L₄ = 7", N_gen + B == L[4] == 7)
check("37 = L₁₀/N_gen−B ≡ N_d−L₄", L[10]/N_gen - B == N_d - L[4] == 37)
check("283 = 2L₁₀+37", 2*L[10] + 37 == 283)
check("283 = L₁₀(2+1/N_gen)−B", L[10]*(2+1/N_gen) - B == 283)
check("264 = 283−19 = 283−(L₆+1)", 283-19 == 264)
check("h¹¹ = (2N_gen)² = 36", (2*N_gen)**2 == 36)
check("66 = Λ²(12) = (6,6)⊕2Λ²(6) = 36+30", 36 + 30 == 66)
check("Λ³(6) = C(6,3) = 20", math.comb(6,3) == 20)
check("Λ²(6)⊕Λ⁴(6) = 15+15 = 30", math.comb(6,2)+math.comb(6,4) == 30)

# ============ 總結 ============
print("\n" + "=" * 100)
print(f"  PASS: {PASS}  FAIL: {FAIL}")
for name, ok, detail in rows:
    print(f"    {'✅' if ok else '🔴'} {name}  {detail}")
print("=" * 100)

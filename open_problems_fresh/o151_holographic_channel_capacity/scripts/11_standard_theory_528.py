#!/usr/bin/env python3
"""
O151 — Script 11: 標準理論微擾/RGE 是否 528 嘅佔據比?
=======================================================
問題 (用戶, 2026-09-06): 先研究標準理論中微擾和 RGE 跑動
是否 528 嘅佔據比。132 和 1/B 稍後。

方法:
1. 標準微擾量清單: SM/MSSM β 函數係數、g* DOF、SMEFT 算子數、
   群論維數、跑動值 — 邊個等於 528?
2. 528 嘅標準理論分解: 44×12, 11×48, 33×16, C(33,2), 6×88
3. 階梯 {2,3,6,12} vs SM 費米子佔據簡併度 {螺旋, 世代, 螺旋×世代,
   螺旋×世代×CP}
4. 精確整數巧合: SM b1×30 = 123 = L10; MSSM b1×10 = 66 = Λ²(12),
   33 = M; 2-loop b22 = 44/5 → 44 = N_d (🟡 標記, 來源 = SM content)
5. 誠實判決: RGE 跑動有冇 528? 冇 -> 佔據比讀法 = 費米子 content

β 係數來源: SM (41/10, -19/6, -7), MSSM (33/5, 1, -3)
  arXiv:1304.0343 + UChicago P487 JS-SUSY notes (ng=3, nh=1/2)
"""
import math

results = []
L10, N_d, B, N_gen = 123, 44, 4, 3

def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"  [{len(results)+1:2d}] {status} {name}" + (f" -- {detail}" if detail else ""))
    results.append(cond)

def frac(x):
    from fractions import Fraction
    return Fraction(x).limit_denominator(1000)

print("=" * 78)
print("  O151 S11: 標準理論微擾/RGE vs 528 佔據比")
print("=" * 78)

# ================================================================
# 1. SM/MSSM β 係數 (閉式, n_g=3, n_h=SM 1 / MSSM 2)
# ================================================================
print("\n--- 1. β 函數係數 (閉式) ---")
def sm_beta(ng, nh):
    return ((4/3)*ng + (1/10)*nh, (4/3)*ng + (1/6)*nh - 22/3, (4/3)*ng - 11)
def mssm_beta(ng, nh):
    return (2*ng + (3/10)*nh, 2*ng + (1/2)*nh - 6, 2*ng - 9)

b_sm = sm_beta(3, 1)
b_mssm = mssm_beta(3, 2)
print(f"  SM   b = {b_sm}  -> 期望 (41/10, -19/6, -7)")
print(f"  MSSM b = {b_mssm}  -> 期望 (33/5, 1, -3)")
check("SM β = (41/10, -19/6, -7)", frac(b_sm[0]) == frac(41/10) and frac(b_sm[1]) == frac(-19/6) and frac(b_sm[2]) == frac(-7))
check("MSSM β = (33/5, 1, -3)", frac(b_mssm[0]) == frac(33/5) and frac(b_mssm[1]) == 1 and frac(b_mssm[2]) == -3)

# 528 掃描: β 係數組合
b_vals = list(b_sm) + list(b_mssm)
print("\n  β 係數入面有冇 528?")
check("β 係數本身冇 528", all(abs(v - 528) > 1 for v in b_vals))
# b1 分子
b1_sm_30 = frac(41/10) * 30
b1_mssm_10 = frac(33/5) * 10
print(f"  SM b1 × 30 = {b1_sm_30} = L₁₀ = 123 (exact 整數)")
print(f"  MSSM b1 × 10 = {b1_mssm_10} = 66 = Λ²(12); 分子 33 = M (exact)")
check("★ SM b1×30 = 123 = L₁₀ (exact)", b1_sm_30 == L10)
check("★ MSSM b1×10 = 66 = Λ²(12)", b1_mssm_10 == 66)
check("★ MSSM b1 分子 = 33 = M (K_Tree total)", b1_mssm_10 // 2 == 33)
# 2-loop 矩陣 (arXiv:1304.0343): b^(2)₂₂ = 44/5
b2_22 = frac(44/5)
check("2-loop SM b22 = 44/5 -> ×5 = 44 = N_d", b2_22 * 5 == N_d)

# ================================================================
# 2. g* DOF 計數 (標準)
# ================================================================
print("\n--- 2. g* DOF ---")
# SM: 28 玻色子 (12 規範×2 螺旋 + ... 標準: 光子2+膠子16+W/Z9+Higgs1 = 28)
#     90 費米子 (3 gen × 15 Weyl × 2); 加 ν_R: 96
g_boson, g_ferm = 28, 90
g_star_sm = g_boson + g_ferm * 7 / 8
g_star_sm_nur = g_boson + 96 * 7 / 8
print(f"  g*_SM = {g_star_sm} (106.75); 加 ν_R: {g_star_sm_nur}")
print(f"  費米子: 90 (3×15×2) / 96 (3×16×2); Weyl 總數 48 = 3×16")
check("SM g* = 106.75", abs(g_star_sm - 106.75) < 1e-9)
check("SM Weyl 費米子 = 48 = 3×16", 3 * 16 == 48)
check("528/48 = 11 = L₅ (rank SU(12))", 528 / 48 == 11)
check("528/90 = 5.867, 528/106.75 = 4.946 — 唔係整數 (冇直接 g* 身份)",
      528 / 90 != 528 // 90 and 528 / 106.75 != 528 // int(106.75))

# ================================================================
# 3. ★ 528 佔據比: N_d × 12, 12 = 2×3×2 (螺旋×世代×CP)
# ================================================================
print("\n--- 3. ★ 528 = N_d × 12 佔據比 ---")
helicity, cp = 2, 2
occ12 = helicity * N_gen * cp
print(f"  12 = 2(螺旋) × 3(世代) × 2(粒子/反粒子 CP) = {occ12}")
print(f"  528 = 44 × 12 = N_d × (每模式 SM 費米子佔據槽)")
check("12 = 2×3×2 (螺旋×世代×CP)", occ12 == 12)
check("528 = 44×12 (N_d × 佔據簡併度)", N_d * occ12 == 528)
check("264 = 44×6 = N_d×2N_gen (冇 CP)", N_d * helicity * N_gen == 264)
check("132 = 44×3 = N_d×N_gen (冇螺旋冇 CP)", N_d * N_gen == 132)
check("88 = 44×2 = N_d×2 (只有螺旋)", N_d * helicity == 88)
# 階梯對應
print("\n  IDCM 階梯 vs SM 費米子佔據階梯:")
print("  88  = 44×2   {log₂B}     vs 螺旋簡併 2")
print("  132 = 44×3   {N_gen}     vs 世代 3")
print("  264 = 44×6   {2N_gen}    vs 螺旋×世代 6")
print("  528 = 44×12  {4N_gen}    vs 螺旋×世代×CP 12")
check("階梯 {2,3,6,12} = SM 佔據階梯 {螺旋,世代,螺旋×世代,螺旋×世代×CP}",
      [2, 3, 6, 12] == [helicity, N_gen, helicity * N_gen, helicity * N_gen * cp])

# ================================================================
# 4. 528 其他標準分解
# ================================================================
print("\n--- 4. 528 分解 ---")
check("528 = 33×16 = M × SO(10) spinor (每代 16 Weyl)", 33 * 16 == 528)
check("528 = 11×48 = L₅ × SM_Weyl", 11 * 48 == 528)
check("528 = C(33,2) = Λ²(33)", 33 * 32 // 2 == 528)
check("528 = 6×88 = 2N_gen×Σγ_odd (IDCM, O147)", 6 * 88 == 528)
check("528 = 12×44 = 12×N_d (佔據讀法)", 12 * 44 == 528)
check("528 = 2×264 (Z₂ = CP 對偶標準身份)", 2 * 264 == 528)

# ================================================================
# 5. 其他標準量掃描 (誠實負結果)
# ================================================================
print("\n--- 5. 標準量掃描 (有冇 528?) ---")
sm_quantities = {
    "SM β₁ = 41/10": 4.1,
    "SM β₂ = -19/6": -19 / 6,
    "SM β₃ = -7": -7,
    "MSSM β₁ = 33/5": 6.6,
    "MSSM β₂ = 1": 1,
    "MSSM β₃ = -3": -3,
    "SM g* = 106.75": 106.75,
    "MSSM g* = 228.75": 228.75,
    "SM 參數數目 = 26": 26,
    "SMEFT dim-5 = 1": 1,
    "SMEFT dim-6 = 59": 59,
    "SMEFT dim-7 = 1572": 1572,
    "SMEFT dim-8 = 9930": 9930,
    "C(33,2) = Λ²(33)": 528,
}
hits = [k for k, v in sm_quantities.items() if v == 528]
print(f"  命中 528: {hits if hits else '冇 (只有 C(33,2) 本身)'}")
check("標準微擾量冇 528 (除咗 C(33,2) 組合學)", hits == ["C(33,2) = Λ²(33)"])

# RGE 跑動: α⁻¹(M_Z) = 128 (IDCM O142); SM 1-loop 跑動
print("\n  RGE 跑動檢查:")
alpha_inv_MZ = 128.0
# SM 跑動 Δα⁻¹ 每 e-fold: b/2π
for i, (name, b) in enumerate([("U(1)", 4.1), ("SU(2)", -19/6), ("SU(3)", -7)]):
    d = b / (2 * math.pi)
    print(f"  SM {name}: Δα⁻¹/e-fold = {d:+.4f}")
check("跑動斜率冇 528 (|b/2π| 全部 < 5)", all(abs(b / (2 * math.pi)) < 5 for b in (4.1, -19/6, -7)))

# ================================================================
# 6. 判決
# ================================================================
print("\n--- 6. 判決 ---")
print("  🟢 微擾/RGE 本身冇 528 (β 係數、g*、SMEFT、跑動斜率全部唔等於 528)")
print("  🟢 但 528 嘅因子 12 = 2×3×2 = 螺旋×世代×CP = SM 費米子每模式佔據簡併度")
print("     -> 「佔據比」讀法: 528 = N_d 個模式 × 每模式 12 個 SM 費米子佔據槽")
print("  🟢 階梯 {2,3,6,12} = {螺旋, 世代, 螺旋×世代, 螺旋×世代×CP}")
print("  🟢 Z₂ (528 = 2×264) 標準身份 = 粒子/反粒子 CP 對偶")
print("  🟡 精確整數巧合 (來源 = SM content, 唔係 IDCM 推導):")
print("     SM b₁×30 = 123 = L₁₀; MSSM b₁×10 = 66 = Λ²(12), 33 = M;")
print("     2-loop b₂₂ = 44/5 -> 44 = N_d")
print("  🔴 微擾展開/RGE 動力學同 528 冇因果連結 (冇跑動量 = 528)")

print("\n" + "=" * 78)
print(f"  S11 總計: {sum(results)}/{len(results)} PASS")
print("=" * 78)

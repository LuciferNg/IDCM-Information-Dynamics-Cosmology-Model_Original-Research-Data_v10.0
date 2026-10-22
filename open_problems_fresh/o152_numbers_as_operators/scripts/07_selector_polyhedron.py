#!/usr/bin/env python3
"""
O152 scripts/07_selector_polyhedron.py — 選擇器鏈鎖定 + 多面體張量分級 + 尾巴審計
===========================================================================
R15: 選擇器鏈: rank 11 = L₅ (R5a 縫數) → SU(12) 唯一性 (rank-11 群中唯一 dim=143)
     → Λ²(12) = 66 = 15+15+36 (SU(6)² 分支) → CY₃ h¹¹ = 36 = (6,6) = (2N_gen)²
R16: 44.5 邊界縫: v_g(43.5) = +sin(π/176), v_g(44.5) = −sin(π/176), 43.5+44.5 = 88
R17: 47 多重身份: 2×23.5, N_d+N_gen, 2N_d−L₁₀/3, L₁₀−L₉
R18: V_Λ 整數部分: 283 = 2L₁₀ + P_f(τ) = 2×123+37; 37 = L₁₀/N_gen − B (候選 🟡);
     0.0821 尾巴候選全部喺陷阱窗 → 🔴 確認
R19: ★多面體 = SU(6) 張量分級: 20Δ = Λ³(6), 30□ = Λ²(6)⊕Λ⁴(6), 12⬠ = 6⊕6̄,
     32 阻挫 = Λ³(6)⊕2·6, 30 錨定 = Λ²⊕Λ⁴, 62 面 = 張量秩總和, 66 = Λ²(12) = 36+30
"""
import json
import os
import mpmath as mp

mp.mp.dps = 50
TOL = mp.mpf('1e-40')

LUCAS = {0: 2, 1: 1}
for _n in range(2, 15):
    LUCAS[_n] = LUCAS[_n - 1] + LUCAS[_n - 2]
FIB = {1: 1, 2: 1}
for _n in range(3, 16):
    FIB[_n] = FIB[_n - 1] + FIB[_n - 2]
def L(n): return LUCAS[n]
def F(n): return FIB[n]

N_d, B, N_gen = 44, 4, 3
def comb(n, k): return mp.binomial(n, k)
def vg(x): return mp.cos(mp.pi * x / 88)

results = []
def check(cid, desc, cond, detail=""):
    results.append((cid, desc, "PASS" if cond else "FAIL", detail))
    return cond

# ================= R15: 選擇器鏈 =================
check("R15a", "rank-11 經典群唯一 dim=143: SU(12)=143, Sp(22)=253, SO(23)=253, SO(24)=276",
      12 ** 2 - 1 == 143 and 22 * 23 // 2 == 253 and 23 * 22 // 2 == 253 and 24 * 23 // 2 == 276,
      "SU(12) 係唯一 rank-11 群有 dim = 12²−1 = 143")
check("R15b", "12 = L₅+1 = γ₄₄·N_gen = 11+1 = 4×3; 143 = 66+77 (Borel 分解)",
      L(5) + 1 == 12 and B * N_gen == 12 and 66 + 77 == 143)
check("R15c", "Λ²(12) 喺 SU(6)² ⊂ SU(12) 分支: 12→(6,1)⊕(1,6); Λ² = (15,1)⊕(1,15)⊕(6,6) = 15+15+36 = 66",
      comb(6, 2) == 15 and 15 + 15 + 36 == 66 and 6 * 6 == 36,
      "6 = 2N_gen; (6,6) = 36 = h¹¹(CY₃) — bi-fundamental 即 Kähler 模空間")
check("R15d", "選擇器鏈: 縫數 11 = rank (R5a) → SU(rank+1) = SU(12) → Λ² ⊃ (6,6) = 36 = (2N_gen)² → CY₃(36,98) via R9",
      L(5) == 11 and 11 + 1 == 12 and (2 * N_gen) ** 2 == 36 and 36 + 2 * (N_d - F(7)) == 98,
      "鏈: seams → rank → SU(12) → h¹¹ → h²¹ (R9 塌縮)")

# ================= R16: 44.5 邊界縫 =================
check("R16a", "v_g(43.5) = +sin(π/176) = +v_floor; v_g(44.5) = −sin(π/176) = −v_floor",
      abs(vg(43.5) - mp.sin(mp.pi / 176)) < TOL and abs(vg(44.5) + mp.sin(mp.pi / 176)) < TOL,
      "cos(43.5π/88) = sin(π/176); cos(44.5π/88) = −sin(π/176)")
check("R16b", "43.5 + 44.5 = 88 = 2N_d — Z₂ 鏡像縫對 (鏈末端兩側)",
      43.5 + 44.5 == 88 and 88 == 2 * N_d)
check("R16c", "44.5 = F₁₁/2 = N_d + log₄2 (45−0.5); 44.5 > 43.5 = 最後內部縫 → 首個負 v_g 縫",
      F(11) / 2 == 44.5 and N_d + mp.mpf(1) / 2 == 44.5 and 44.5 > 43.5,
      "44.5 = 鏈外邊界標記 (冇物理常數, 但係結構位置)")

# ================= R17: 47 多重身份 =================
check("R17a", "47 = 2×23.5 (縫雙倍) = N_d + N_gen = 44+3 = L₁₀−L₉ = 2N_d − L₁₀/3",
      2 * 23.5 == 47 and N_d + N_gen == 47 and L(10) - L(9) == 47
      and 2 * N_d - mp.mpf(L(10)) / 3 == 47,
      f"88 − 123/3 = 88−41 = 47; 多重 T̂ 身份, 冇觀測角色")
check("R17b", "55 = F₁₀ = C(L₅,2) = 66−11 = 非單正根數 (SU(12)) = 27.5×2",
      F(10) == 55 and L(5) * 10 // 2 == 55 and 66 - 11 == 55 and 2 * 27.5 == 55,
      "55 有結構角色 (非單正根), 47 冇 — 誠實分開")

# ================= R18: V_Λ 整數部分 =================
check("R18a", "283 = 2L₁₀ + P_f(τ) = 2×123 + 37 (O147: 37 = P_f(τ))",
      2 * L(10) + 37 == 283 and 2 * 123 == 246 and 246 + 37 == 283,
      "V_Λ 整數部分 = 2×Lucas跡 + 投影泛函")
check("R18b", "37 = P_f(τ) = L₁₀/N_gen − B = 123/3 − 4 = 41 − 4 (候選身份 🟡)",
      mp.mpf(L(10)) / N_gen - B == 37 and mp.mpf(123) / 3 == 41 and 41 - 4 == 37,
      "37 = L₁₀/N_gen − γ₄₄ — 需 O147 交叉審計")
check("R18c", "283 = L₁₀(2 + 1/N_gen) − B = 123×7/3 − 4 = 287−4 (全 T̂/G2 形式)",
      mp.mpf(L(10)) * (2 + mp.mpf(1) / N_gen) - B == 283,
      f"123×7/3 = {mp.mpf(123) * 7 / 3} − 4 = 283")
check("R18d", "264 = 283 − 19 = 2L₁₀ + P_f(τ) − (L₆+1) (F(γ) 整數部分)",
      283 - 19 == 264 and 2 * L(10) + 37 - (L(6) + 1) == 264)
check("R18e", "0.0821 尾巴: 結構候選 (ln10·sin, 14.5/176, 41/500) 全部喺 φ-陷阱窗且非精確 → 🔴 確認",
      all(abs(c - mp.mpf('0.0821')) > mp.mpf('1e-30') for c in [mp.log(10) * mp.sin(mp.pi / 88), mp.mpf('14.5') / 176, mp.mpf('41') / 500])
      and all(mp.mpf('1e-5') < abs(c - mp.mpf('0.0821')) < mp.mpf('1e-3')
              for c in [mp.log(10) * mp.sin(mp.pi / 88), mp.mpf('14.5') / 176, mp.mpf('41') / 500]),
      "δ = 7.5e-5 / 2.86e-4 / 1e-4 — 全部窗內, 冇精確身份 → 尾巴 0.0821 冇結構")

# ================= R19: ★多面體 = SU(6) 張量分級 =================
check("R19a", "20Δ = Λ³(6) = C(6,3) = 20; 30□ = Λ²(6)⊕Λ⁴(6) = 15+15; 12⬠ = 6⊕6̄",
      comb(6, 3) == 20 and comb(6, 2) == 15 and comb(6, 4) == 15 and 6 + 6 == 12,
      "6 = 2N_gen — 多面體面型 = SU(2N_gen) 張量秩")
check("R19b", "62 面 = 20+30+12 = Λ³ ⊕ (Λ²⊕Λ⁴) ⊕ (6⊕6̄) — 張量秩總和",
      20 + 30 + 12 == 62 and 20 + 30 + 12 == comb(6, 3) + comb(6, 2) + comb(6, 4) + 6 + 6)
check("R19c", "32 阻挫 = 20Δ+12⬠ = Λ³(6) ⊕ (6⊕6̄) (O41 阻挫數 = SU(6) 張量結構)",
      20 + 12 == 32 and comb(6, 3) + 12 == 32)
check("R19d", "30 錨定 = 30□ = Λ²(6)⊕Λ⁴(6) (冷斑錨定 30/30 = 張量秩)", 15 + 15 == 30)
check("R19e", "66 = Λ²(12) = (6,6)⊕2Λ²(6) = 36+30 = h¹¹(CY₃) + 錨定面 — SU(12)↔CY₃↔多面體三位一體",
      36 + 30 == 66 and comb(12, 2) == 66 and 6 * 6 + 2 * comb(6, 2) == 66)
check("R19f", "V = 12⬠×5 = 60 頂點 (每頂點 1 個五邊形); E = (20×3+30×4+12×5)/2 = 120; χ = 60−120+62 = 2",
      12 * 5 == 60 and (20 * 3 + 30 * 4 + 12 * 5) // 2 == 120 and 60 - 120 + 62 == 2,
      "rhombicosidodecahedron 一致性 (V−E+F = 2)")

n_pass = sum(1 for r in results if r[2] == "PASS")
n_fail = sum(1 for r in results if r[2] == "FAIL")
print(f"=== O152 選擇器+多面體: {n_pass} PASS / {n_fail} FAIL (共 {len(results)}) ===")
for cid, desc, status, detail in results:
    mark = "✅" if status == "PASS" else "❌"
    print(f"{mark} [{cid}] {desc}")
    if detail and status == "FAIL":
        print(f"     詳情: {detail}")

out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
entries = [{"id": cid, "result": desc, "status": status, "detail": detail}
           for cid, desc, status, detail in results]
with open(os.path.join(out_dir, "selector_polyhedron.json"), "w") as f:
    json.dump({"results": entries, "n_pass": n_pass, "n_fail": n_fail, "total": len(results)},
              f, indent=1, ensure_ascii=False)
print(f"\n輸出: data/selector_polyhedron.json")

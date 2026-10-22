#!/usr/bin/env python3
"""
O152 scripts/03_reducibility_epsilon.py — 數字可約化性 + ε/f_unproj 算子來源
============================================================================
① R6: G9/G10 (SU(12)/CY₃) 維數數字全部 = T̂/G2 多項式 (數字層約化; 結構獨立)
② R7: T̂-縫 (半整數) ↔ 結構 midpoints (O149 numerator duals, 分子 mean)
③ R8: ε_exact = (L₆+1)/L₁₀; f_unproj = L₁₀/(4(N_d+1)); E_min = L₁₀/(4N_d)
"""
import json
import os
import mpmath as mp

mp.mp.dps = 50
TOL = mp.mpf('1e-40')

def gamma44(n): return 4 * mp.sin(mp.pi * n / 88) ** 2

LUCAS = {0: 2, 1: 1}
for _n in range(2, 15):
    LUCAS[_n] = LUCAS[_n - 1] + LUCAS[_n - 2]
FIB = {1: 1, 2: 1}
for _n in range(3, 16):
    FIB[_n] = FIB[_n - 1] + FIB[_n - 2]
def L(n): return LUCAS[n]
def F(n): return FIB[n]

results = []
def check(cid, desc, op, func, cond, detail=""):
    results.append((cid, desc, op, func, "PASS" if cond else "FAIL", detail))
    return cond

N_d, B, N_gen = 44, 4, 3
g44 = 4.0  # γ₄₄ = B
g22 = 2.0  # γ₂₂ = log₂B

# ---------- ① R6: G9/G10 數字 = T̂/G2 多項式 ----------
checks6 = [
    ("12", 12 == B * N_gen, "γ₄₄×N_gen"),
    ("11", 11 == L(5), "L₅"),
    ("36", 36 == (2 * N_gen) ** 2, "[2N_gen]²"),
    ("98", 98 == 2 * L(4) ** 2, "2L₄²"),
    ("124", 124 == 2 * (98 - 36), "2(h²¹−h¹¹)"),
    ("60", 60 == F(5) * B * N_gen, "F₅·γ₄₄·N_gen"),
    ("66", 66 == 12 * 11 // 2, "dim·rank/2"),
    ("77", 77 == 66 + 11, "66+11"),
    ("132", 132 == 12 * 11, "dim·rank"),
    ("143", 143 == 12 ** 2 - 1, "dim²−1"),
    ("30", 30 == N_d - 2 * L(4), "N_d−2L₄"),
    ("32", 32 == B * F(5) + B * N_gen, "B(F₅+N_gen)"),
    ("84", 84 == F(8) * B, "F₈·γ₄₄"),
    ("192", 192 == B * (N_d + B), "γ₄₄(N_d+γ₄₄)"),
    ("137", 137 == N_gen * N_d + F(5), "N_gen·N_d+F₅"),
    ("264", 264 == N_d * 2 * N_gen, "N_d·2N_gen"),
    ("528", 528 == N_d * B * N_gen, "N_d·γ₄₄·N_gen"),
    ("24", 24 == B * 2 * N_gen, "γ₄₄·2N_gen"),
    ("46", 46 == N_d + g22, "N_d+γ₂₂"),
]
all6 = all(c for _, c, _ in checks6)
check("R6", f"G9/G10 維數數字全部 = T̂/G2 多項式 ({sum(1 for _,c,_ in checks6 if c)}/{len(checks6)})", "G1⊗G2", "F4 維數/多項式",
      all6, "; ".join(f"{n}={f}" for n, c, f in checks6 if c))

# ---------- ② R7: T̂-縫 ↔ 結構 midpoints ----------
# 1.5 = mid(F₂,F₃) = k=2 numerator dual (O149 §6.2: 分子 dual = (1,2))
# 2.5 = mid(F₃,F₄) = k=3 numerator dual (O149 §6.2: (2,3))
# 3.5 = mid(N_gen, B) = mid(3,4)
# 5.5 = mid(5,6) = O149 §7.1 分子 mean (5,6) → 5.5 ✓
# 23.5 = mid(F₈, 2F₇) = mid(21,26) [候選]
# 27.5 = mid(2F₇, L₇) = mid(26,29) [候選]
check("R7a", "1.5 = mid(F₂,F₃) = (1+2)/2 — k=2 numerator dual (O149 §6.2)", "G1⊗Z₂", "F11 縫/dual",
      (F(2) + F(3)) / 2 == 1.5, "k=2 numerator (42,43) 嘅 Z₂ dual = (1,2)")
check("R7b", "2.5 = mid(F₃,F₄) = (2+3)/2 — k=3 numerator dual (O149 §6.2)", "G1⊗Z₂", "F11 縫/dual",
      (F(3) + F(4)) / 2 == 2.5, "k=3 numerator (41,42) 嘅 Z₂ dual = (2,3)")
check("R7c", "3.5 = mid(N_gen, B) = (3+4)/2", "G2⊗G6", "F11 縫/世代-分支",
      (3 + 4) / 2 == 3.5, "世代 3 與分支 4 之間嘅縫")
check("R7d", "5.5 = mid(5,6) — O149 §7.1 分子 mean (5,6) = 5.5 (Δ=F₅=5, 0.5)", "G1⊗Z₂", "F11 縫/分子 mean",
      (5 + 6) / 2 == 5.5 and abs(5.5 - F(5)) == 0.5, "O149 家族結構表 (5,6) | 5.5 | F₅=5 | 0.5")
check("R7e", "23.5 = mid(F₈, 2F₇) = (21+26)/2 [候選]", "G1⊗Z₂", "F11 縫/候選",
      (F(8) + 2 * F(7)) / 2 == 23.5, "21 = F₈, 26 = 2F₇ — 縫 23.5")
check("R7f", "27.5 = mid(2F₇, L₇) = (26+29)/2 [候選]", "G1⊗Z₂", "F11 縫/候選",
      (2 * F(7) + L(7)) / 2 == 27.5, "26 = 2F₇, 29 = L₇ — 縫 27.5")

# ---------- ③ R8: ε 同 f_unproj 算子來源 ----------
check("R8a", "ε_exact = 19/123 = (L₆+1)/L₁₀", "G1 T̂", "F2 跡比率",
      mp.mpf(19) / 123 == mp.mpf(L(6) + 1) / L(10), "19 = L₆+1 (O151 S17 註冊), 123 = L₁₀")
check("R8b", "f_unproj = 41/60 = L₁₀/(4(N_d+1)) = 123/180", "G1⊗G2", "F7 比率",
      mp.mpf(41) / 60 == mp.mpf(L(10)) / (4 * (44 + 1)),
      "f_unproj = Tr(T̂¹⁰)/(4(N_d+1)) — 投影核心分數 = T̂ 跡 ÷ 世界符號位數×4")
check("R8c", "E_min = L₁₀/(4N_d); f_unproj/E_min = (N_d+1)/N_d 倒數 = 44/45", "G1⊗G2", "F7 比率",
      mp.mpf(123) / 176 == mp.mpf(L(10)) / (4 * 44)
      and mp.mpf(41) / 60 * mp.mpf(176) / 123 == mp.mpf(44) / 45,
      "O148 S4: f_unproj/E_min = N_d/(N_d+1) = 44/45")
check("R8d", "ε × E_min = 19/176 = (L₆+1)/(4N_d)", "G1⊗G2", "F7 比率",
      mp.mpf(19) / 123 * mp.mpf(123) / 176 == mp.mpf(19) / 176,
      "ε·E_min = (L₆+1)/(4N_d) — 兩個 Lucas 跡比率複合")
check("R8e", "ε = 4·41/123 − 4·f_unproj 關係: ε ≈ φ⁻¹/4 係 φ-近似 (δ₃)", "G1", "F7 比率/陷阱窗",
      abs(mp.mpf(19) / 123 - mp.mpf(1) / (4 * (1 + mp.sqrt(5)) / 2)) < mp.mpf('1e-3'),
      "φ⁻¹/4 = 0.154508 vs 19/123 = 0.154472 — 差 δ₃ = 0.023% (O148 判決: φ 形式係近似)")

# ---------- 統計 ----------
n_pass = sum(1 for r in results if r[4] == "PASS")
n_fail = sum(1 for r in results if r[4] == "FAIL")
print(f"=== O152 可約化性+ε: {n_pass} PASS / {n_fail} FAIL (共 {len(results)}) ===")
for cid, desc, op, func, status, detail in results:
    mark = "✅" if status == "PASS" else "❌"
    print(f"{mark} [{cid}] {desc}  | {op} {func}")
    if detail and status == "FAIL":
        print(f"     詳情: {detail}")

out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
entries = [{"id": cid, "result": desc, "operator": op, "function": func,
            "status": status, "detail": detail} for cid, desc, op, func, status, detail in results]
with open(os.path.join(out_dir, "reducibility_epsilon.json"), "w") as f:
    json.dump({"results": entries, "n_pass": n_pass, "n_fail": n_fail, "total": len(results)},
              f, indent=1, ensure_ascii=False)
print(f"\n輸出: data/reducibility_epsilon.json")

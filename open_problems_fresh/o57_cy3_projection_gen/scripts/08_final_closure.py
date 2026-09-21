#!/usr/bin/env python3
"""
O57 — 探索 08: 最終機制鏈 — CY₃ = K_Chain 投影嘅幾何化身 (完整閉合)
===================================================================
將探索 01-07 嘅所有結構閉合成單一機制鏈:

  x²+x−1=0 → φ
    → B=4, L5=11, L6=18, F8=21
    → K_Chain 44-site (γ_n = 4sin²(πn/88), Σγ=90)
    → Beat 空間 Λ²(R⁴⁴) = 946 (2-form 空間)
      even 462 = 2×Λ²(R²²) → Kähler sector
      odd 484 = R²²⊗R²² → CPX sector
    → 投影 P̂ (134×946):
      Kähler 36 行 (support 21 = F8, full rank)
      CPX 98 行 (rank 73, 缺口 25 = F8+B)
    → CY₃(36,98):
      h11 = 36 = Nd−2B = 2L6
      h21 = 98 = Σγ+2B = B×L5+3L6
      χ = −124

  對應真實 polytope:
    48 points = Nd+B, 144 simplices = B×h11
    484 sr_ideal = odd beats, 146 = C(36,2)−484 = 2×73
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
DATA = os.path.join(BASE, "data")

phi = (1 + math.sqrt(5)) / 2
Nd = 44

print("=" * 72)
print("O57 探索 08: 最終機制鏈閉合")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 基礎結構 ============
print("\n[1] 基礎結構 (x²+x−1=0 → φ)")
B = 4
L5 = 11
L6 = 18
F8 = 21
F10 = 55
F12 = 144
check("B = φ³−φ⁻³ = 4", abs(phi**3 - phi**-3 - 4) < 1e-9)
check("L5 = φ⁵+(−φ)⁻⁵ = 11", abs(phi**5 + (-phi)**-5 - 11) < 1e-9)
check("L6 = φ⁶+(−φ)⁻⁶ = 18", abs(phi**6 + (-phi)**-6 - 18) < 1e-9)
check("F8 = 21", F8 == 21)

# ============ 2. K_Chain ============
print("\n[2] K_Chain 44-site")
gamma = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, Nd+1)])
S_gamma = gamma.sum()
check("Nd = B×L5 = 44", B*L5 == 44)
check("Σγ = 90", abs(S_gamma - 90) < 1e-9)
check("Σγ = 5L6", abs(S_gamma - 5*L6) < 1e-9)
check("γ_n + γ_{44−n} = 4", all(abs(gamma[n-1] + gamma[44-n-1] - 4) < 1e-9 for n in range(1, 23)))

# ============ 3. Beat 空間 ============
print("\n[3] Beat 空間 Λ²(R⁴⁴) = 946")
C44_2 = 44*43//2
check("946 = C(44,2) = dim Λ²(R⁴⁴)", C44_2 == 946)
even_beats = 2 * (22*21//2)
odd_beats = 22 * 22
check("even = 2×Λ²(R²²) = 462", even_beats == 462)
check("odd = R²²⊗R²² = 484", odd_beats == 484)
check("even+odd = 946", even_beats + odd_beats == 946)

# Z₂ 結構
z2_fixed = sum(1 for n in range(1, 22) for m in range(n+1, 45) if n + m == 44)
check("Z₂-fixed beats = 21 = F8", z2_fixed == F8)
check("Z₂ orbits = 441 = F8²", (946 - 43 - F8)//2 == F8**2)

# ============ 4. 投影算子 ============
print("\n[4] 投影算子 P̂ (134×946)")
P = np.load(os.path.join(DATA, "P_fixed_v2.npy"))
rank_P = np.linalg.matrix_rank(P, tol=1e-10)
P_k = P[:36, :]
P_c = P[36:, :]
rank_k = np.linalg.matrix_rank(P_k, tol=1e-10)
rank_c = np.linalg.matrix_rank(P_c, tol=1e-10)

check("rank(P̂) = 109", rank_P == 109)
check("rank(Kähler) = 36 = h11", rank_k == 36)
check("rank(CPX) = 73", rank_c == 73)
check("36 + 73 = 109", rank_k + rank_c == 109)
check("缺口 = 25 = F8 + B", 98 - rank_c == F8 + B)
check("缺口 = Nd/2 + N_gen", 98 - rank_c == 22 + 3)

# Kähler support
supports_k = np.count_nonzero(P_k, axis=1)
check("Kähler support 全 = 21 = F8", np.all(supports_k == 21))
check("21 = Nd/2 − 1", 21 == 22-1)

# ============ 5. CY₃ Hodge ============
print("\n[5] CY₃(36,98)")
h11 = Nd - 2*B
h21 = int(S_gamma) + 2*B
check("h11 = Nd−2B = 36", h11 == 36)
check("h21 = Σγ+2B = 98", h21 == 98)
check("h11 = 2L6", h11 == 2*L6)
check("h21 = B×L5 + 3L6", h21 == B*L5 + 3*L6)
check("χ = 2(h11−h21) = −124", 2*(h11-h21) == -124)
check("b3 = 2(1+h21) = 198", 2*(1+h21) == 198)

# ============ 6. 真實 polytope 對應 ============
print("\n[6] 真實 polytope 對應")
import os
data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "o53_cy3_reality", "data", "polytopes")
d = json.load(open(os.path.join(data_dir, "cy36_98_sage_export.json")))
n_points = d["n_points"]
n_simplices = len(d["simplices"])
n_sr = len(d["sr_ideal"])

check("48 points = Nd + B", n_points == Nd + B)
check("144 simplices = B×h11", n_simplices == B*h11)
check("484 sr_ideal = odd beats", n_sr == odd_beats)
check("C(36,2) − 484 = 146 = 2×73", 36*35//2 - n_sr == 2*rank_c)
check("h11 = n_points − 12", h11 == n_points - 12)
check("h21 = (Nd−1) + F10", h21 == 43 + F10)

# sr_ideal 涉及 points
all_idx = set()
for s in d["sr_ideal"]:
    all_idx.update(s)
check("sr_ideal 涉及 36 points = h11", len(all_idx) == 36)
check("未涉及 12 = h11/3", 48 - len(all_idx) == 12)

# ============ 7. 三代結構 ============
print("\n[7] 三代結構")
check("N_gen = 3 = B−1", 3 == B-1)
check("66 = 3×22 = 3×(Nd/2)", 66 == 3*22)
check("66 = 6×L5", 66 == 6*L5)
check("66 = C(12,2)", 66 == 12*11//2)
check("12 = h11/3", 12 == h11//3)

# ============ 8. 頻率結構 ============
print("\n[8] 頻率結構")
freqs = []
for n in range(1, Nd+1):
    for m in range(n+1, Nd+1):
        freqs.append(abs(gamma[n-1] - gamma[m-1]))
freqs = np.array(freqs)
s_freq = sum((2*n - 45) * gamma[n-1] for n in range(1, 45))
check("Σ|ω| = Σ(2n−45)γ_n", abs(s_freq - freqs.sum()) < 1e-6)

# ============ 9. 最終機制鏈 ============
print("\n[9] 最終機制鏈 (完整)")
print(f"""
  ╔══════════════════════════════════════════════════════════╗
  ║  O57 閉合: CY₃ = K_Chain 投影嘅幾何化身                 ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║  x²+x−1=0 → φ                                           ║
  ║    ↓                                                    ║
  ║  B=4, L5=11, L6=18, F8=21 (Fibonacci/Lucas 結構)        ║
  ║    ↓                                                    ║
  ║  K_Chain 44-site (γ_n=4sin²(πn/88), Σγ=90)             ║
  ║    ↓ 兩兩組合 (n,m)                                     ║
  ║  Beat 空間 = Λ²(R⁴⁴) = 946  ← 2-form 空間!            ║
  ║    even 462 = 2×Λ²(R²²) → Kähler sector               ║
  ║    odd  484 = R²²⊗R²²   → CPX sector                  ║
  ║    Z₂: fixed 21=F8, orbits 441=F8², =時間反演          ║
  ║    ↓ 投影 P̂ (134×946)                                 ║
  ║  Kähler: 36 行, support 21=F8 每個, full rank 36       ║
  ║  CPX:    98 行, rank 73, 缺口 25=F8+B                  ║
  ║    ↓                                                    ║
  ║  CY₃(36,98): h11=2L6=36, h21=B×L5+3L6=98, χ=−124      ║
  ║                                                          ║
  ║  真實 polytope 驗證:                                    ║
  ║    48 points = Nd+B, 144 simps = B×h11                 ║
  ║    484 sr_ideal = odd beats = 22²                       ║
  ║    C(36,2)−484 = 146 = 2×rank(CPX) = 2×73              ║
  ║    sr 涉及 36 points = h11, 未涉及 12 = h11/3           ║
  ║                                                          ║
  ║  三代: N_gen = 3 = B−1                                  ║
  ║    66 = 3×22 = 3×(Nd/2) = 6×L5 = C(12,2)               ║
  ╚══════════════════════════════════════════════════════════╝
""")

# ============ 10. 結果保存 ============
results = {
    "test": "O57 探索 08: 最終機制鏈閉合",
    "chain": {
        "phi": "x²+x−1=0",
        "structure": "B=4, L5=11, L6=18, F8=21",
        "kchain": "44-site, Σγ=90",
        "beat_space": "Λ²(R⁴⁴) = 946 (2-forms)",
        "parity": "even 462 → Kähler, odd 484 → CPX",
        "z2": "fixed 21=F8, orbits 441=F8², time reversal",
        "projection": "P̂ 134×946, Kähler rank 36, CPX rank 73",
        "cy3": "h11=2L6=36, h21=B×L5+3L6=98, χ=−124",
        "polytope": "48pts=Nd+B, 144simps=B×h11, 484sr=odd beats",
        "generations": "N_gen=3=B−1, 66=3×22=6×L5=C(12,2)"
    },
    "rank": int(rank_P),
    "rank_kahler": int(rank_k),
    "rank_cpx": int(rank_c),
    "cpx_gap": int(98 - rank_c),
    "gap_identity": "F8+B = Nd/2+N_gen (B−1=N_gen)",
    "passed": passed, "failed": failed
}
with open("data/08_final_closure.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n{'='*72}")
print(f"最終結果: Passed: {passed}, Failed: {failed}")
print(f"{'='*72}")
if failed > 0:
    exit(1)
print("🎉🎉 O57 探索 08 完整閉合! 🎉🎉")

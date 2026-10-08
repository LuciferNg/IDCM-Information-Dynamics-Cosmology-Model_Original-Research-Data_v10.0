#!/usr/bin/env python3
"""
O84 — O240 交接判決獨立重驗 (2026-10-08)
==========================================
由原始輸入 (o53 κ tensor + γ_n = 4sin²(nπ/88) 定義 + Lucas/Fib 定義)
用 mpmath 高精度重算 O240 → O84 交回嘅全部判決數字:
  A.  Σκ = −8, Σκ_diag (k_iii) = −380 = −20×19   (O240 docs/08: 380/20 = 19)
  B.  F(γ) 高精度真值 + Δ = F(γ) − 264
      (O240 docs/09: 264.0821292325802448541101854337443526542058467...)
  C.  V_Λ 純κ譜形式 = F(γ) + |Σκ_diag|/(φ(88)/2) = 283.082129232580244854...
      vs O84 原式 F(γ) + 44 − 8 − 17
  D.  19 三讀收斂: 44−25 | |Σκ_diag|/20 | 44−(98−90+17)  (O240 docs/08 §4)
  E.  Q1: Δ ∈ ℚ(ζ₈₈)⁺ orbit 20 + Trace(Δ) ∉ ℤ ⟹ Δ 非代數整數
      (O240 docs/09 §1 — 用 20 個 σ_a 作用 mpmath 高精度重算)
  F.  41/60 vs 4/(φ⁴−1) dev = 5.176e-5  (O148 判決承接; O240 docs/04)
  G.  264 = 4⟨W⟩²+L₆ = 246+18;  283.0821 = B⟨W⟩²+L₆+L₅+F₆+Δ (O240 docs/03)
  H.  73 = Σγ_even − G_neg(17) = rank(CPX) 譜重建;  25 = 98−73

零 import 上游任何 script（只讀 o53 數據檔 + mpmath 由定義重算）。
執行: /usr/bin/python3 scripts/04_handover_ruling.py
"""
import json, os, sys, math
import mpmath as mp
mp.mp.dps = 80

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")

passed, failed = 0, 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ---------- 原始輸入 ----------
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa_raw = d["kappa"]            # 36×36×36 list
N = 36
# κ 非零項 (index, value)
nz = [(i, j, k, v) for i in range(N) for j in range(N) for k in range(N)
      for v in [kappa_raw[i][j][k]] if v != 0]

phi = (mp.mpf(1) + mp.sqrt(5)) / 2
L = [mp.mpf(2), mp.mpf(1)]
for i in range(2, 40):
    L.append(L[i-1] + L[i-2])
F_fib = [mp.mpf(0), mp.mpf(1)]
for i in range(2, 40):
    F_fib.append(F_fib[i-1] + F_fib[i-2])
# K_Tree branching = 4, N_d = 44, h21 = 98, rank(CPX) = 73 (O57)
B_kt, N_d, h21, rank_CPX = 4, 44, 98, 73

def gamma_n(n, N=88):
    """γ_n = 4 sin²(nπ/N) — 預設 88-site, O84 convention 176 用 γ(n,176)"""
    return 4 * mp.sin(n * mp.pi / N) ** 2

def F_gamma(gvec):
    """F(t) = (1/6) Σ κ_ijk t_i t_j t_k — 精確高精度 (只加非零項)"""
    s = mp.mpf(0)
    for (i, j, k, v) in nz:
        s += mp.mpf(v) * gvec[i] * gvec[j] * gvec[k]
    return s / 6

# ---------- A. κ 譜身份 ----------
print("=" * 72)
print("[A] κ 譜身份 (Σκ, Σκ_diag)")
S_kappa = sum(mp.mpf(v) for (_, _, _, v) in nz)
S_diag = sum(mp.mpf(kappa_raw[i][i][i]) for i in range(N))
print(f"  Σκ        = {S_kappa}")
print(f"  Σκ_diag   = {S_diag}   (期望 −380 = −20×19)")
check("Σκ = −8 = −2B", S_kappa == -8, f"(Σκ={S_kappa})")
check("Σκ_diag = −380 = −20×19", S_diag == -380)
check("Σκ_diag/(φ(88)/2) = 380/20 = 19", S_diag / 20 == -19,
      f"(φ(88)=40, /2=20)")

# ---------- B. F(γ) 高精度真值 + Δ ----------
print("=" * 72)
print("[B] F(γ) 高精度重算 (mpmath dps=80, 由 κ+γ 定義)")
g36 = [gamma_n(n) for n in range(1, 37)]
Fg = F_gamma(g36)
Delta = Fg - 264
print(f"  F(γ) = {mp.nstr(Fg, 60)}")
print(f"  Δ    = {mp.nstr(Delta, 60)}")
# O240 docs/09 真值 (含 ellipsis, 用 O62 rem_mp 完整 46 位)
F_expect = mp.mpf("264.0821292325802448541101854337443526542058")   # docs/09 寫 42 位
D_expect = mp.mpf("0.0821292325802448541101854337443526542058467051")  # O62 rem_mp
check("F(γ) 首 42 位 = 264.0821292325802448541101854337443526542058...",
      abs(Fg - F_expect) < mp.mpf("1e-38"),
      f"(diff {mp.nstr(abs(Fg-F_expect), 3)})")
check("Δ 首 46 位 = 0.0821292325802448541101854337443526542058467051 (O62 rem_mp)",
      abs(Delta - D_expect) < mp.mpf("1e-42"),
      f"(diff {mp.nstr(abs(Delta-D_expect), 3)})")
check("float64 舊值 264.082129232580257 同真值差 ~1.25e-14 (docs/09: 1.255e-14 約數)",
      abs(abs(mp.mpf("264.082129232580257") - Fg) - mp.mpf("1.25e-14")) < mp.mpf("1e-15"),
      f"(diff {mp.nstr(abs(mp.mpf('264.082129232580257')-Fg), 5)})")

# ---------- C. V_Λ 純κ譜形式 ----------
print("=" * 72)
print("[C] V_Λ = F(γ) + |Σκ_diag|/20 (純κ譜形式, O240 docs/08)")
V_lambda_kappa = Fg + abs(S_diag) / 20
V_lambda_o84 = Fg + (N_d - 8 - 17)     # O84 原式 F + N_d − F₈ − B (F₈=8, B=17)
print(f"  V_Λ(κ)   = {mp.nstr(V_lambda_kappa, 50)}")
print(f"  V_Λ(O84) = {mp.nstr(V_lambda_o84, 50)}")
check("V_Λ 純κ譜 = 283.08212923258024485411018543374435...",
      abs(V_lambda_kappa - mp.mpf("283.08212923258024485411018543374435")) < mp.mpf("1e-30"))
check("純κ譜形式 = O84 原式 (F + 44−8−17)", V_lambda_kappa == V_lambda_o84,
      "(380/20 = 19 = 44−8−17 EXACT)")

# ---------- D. 19 三讀收斂 ----------
print("=" * 72)
print("[D] 19 三讀收斂 (O240 docs/08 §4)")
# O84 scripts/01 convention: γ_88 = γ_n(176), even = n=2,4,...,88; odd = n=1,3,...,87
S_even = sum(gamma_n(n, 176) for n in range(2, 89, 2))
S_odd = sum(gamma_n(n, 176) for n in range(1, 88, 2))
G_neg = 17
print(f"  Σγ_even(176, n=2..88) = {mp.nstr(S_even, 20)} (90?)  Σγ_odd = {mp.nstr(S_odd, 20)} (88?)")
r_a = N_d - (h21 - rank_CPX)
r_b = abs(S_diag) / 20
r_c = N_d - (h21 - S_even + G_neg)
print(f"  讀法A: 44−(98−73)      = {int(r_a)}")
print(f"  讀法B: |Σκ_diag|/20     = {int(r_b)}")
print(f"  讀法C: 44−(98−90+17)    = {int(r_c)}")
check("三讀收斂 = 19 EXACT", r_a == 19 and r_b == 19 and r_c == 19)
check("Σγ_even=90, Σγ_odd=88 (O84 convention)",
      abs(S_even-90) < mp.mpf("1e-25") and abs(S_odd-88) < mp.mpf("1e-25"))

# ---------- E. Δ Galois orbit + Trace (Q1) ----------
print("=" * 72)
print("[E] Q1: Δ ∈ ℚ(ζ₈₈)⁺ — orbit=20, Trace ∉ ℤ (O240 docs/09)")
from math import gcd
units = [a for a in range(1, 88) if gcd(a, 88) == 1]
reps = sorted(set(min(a, 88-a) for a in units))       # 對合 {±1} 商
# ζ₈₈ σ_a: ζ → ζ^a, γ_n → 4sin²(anπ/88)
orbit = []
for a in reps:
    ga = [gamma_n((a*n) % 88 if (a*n) % 88 != 0 else 88) for n in range(1, 37)]
    orbit.append(F_gamma(ga) - 264)
Trace = sum(orbit)
print(f"  orbit size = {len(orbit)} (期望 20 = φ(88)/2)")
print(f"  Trace(Δ) = {mp.nstr(Trace, 50)}")
check("orbit = 20", len(orbit) == 20)
# 驗證 trace 有理值 −30050/3
tq = -mp.mpf(30050)/3
check("Trace(Δ) = −30050/3 EXACT", abs(Trace - tq) < mp.mpf("1e-40"),
      f"(diff {mp.nstr(abs(Trace-tq), 4)})")
check("Trace ∉ ℤ ⟹ Δ 非代數整數 (monic ℤ[x] 不存在)",
      mp.fmod(tq, 1) != 0)

k_frag = "+".join(f"σ_{reps[0]}={mp.nstr(orbit[0],12)}" for _ in [0])

# ---------- F. 41/60 vs 4/(φ⁴−1) ----------
print("=" * 72)
print("[F] 標籤審計: Ω_Λ = 61.5/90 = 41/60 (O148 判決承接)")
om1 = mp.mpf("61.5") / 90
om2 = mp.mpf(41) / 60
om_phi = 4 / (phi**4 - 1)
dev = abs(om2 - om_phi)
print(f"  61.5/90      = {mp.nstr(om1, 30)}")
print(f"  41/60        = {mp.nstr(om2, 30)}")
print(f"  4/(φ⁴−1)     = {mp.nstr(om_phi, 30)}  dev vs 41/60 = {mp.nstr(dev, 10)}")
check("61.5/90 ≡ 41/60 EXACT", om1 == om2)
check("dev(41/60, 4/(φ⁴−1)) = 5.176e-5 (O148)",
      abs(dev - mp.mpf("5.176e-5")) / mp.mpf("5.176e-5") < mp.mpf("1e-3"),
      f"(dev={mp.nstr(dev, 8)})")
check("4/(φ⁴−1) 唔係精確 — 只係 φ-代數近似", dev > mp.mpf("1e-10"))

# ---------- G. 264 = 4⟨W⟩² + L₆; 283 = B⟨W⟩²+L₆+L₅+F₆+Δ ----------
print("=" * 72)
print("[G] 五項分解 (O240 docs/03)")
W2 = mp.mpf(123)/2        # ⟨W⟩² = 61.5 = L₁₀/2
L5, L6, F6 = L[5], L[6], F_fib[6]     # L₅=11, L₆=18, F₆=8
g264 = 4*W2 + L6          # B⟨W⟩² + L₆ = 246 + 18 = 264
g283 = 4*W2 + L6 + L5 + F6 + Delta
print(f"  4⟨W⟩²+L₆   = {mp.nstr(g264, 25)} (264 EXACT?)")
print(f"  B⟨W⟩²+L₆+L₅+F₆+Δ = {mp.nstr(g283, 40)} (283.0821 EXACT?)")
check("264 = 4⟨W⟩² + L₆ = 246+18 EXACT (B=4=K_tree branching)",
      g264 == 264 and (4*W2) == 246 and L6 == 18)
check("283.0821... = 246+18+11+8+Δ EXACT",
      abs(g283 - V_lambda_kappa) < mp.mpf("1e-40"))
check("L₅=11, L₆=18, F₆=8 (Lucas/Fib 定義)", L5 == 11 and L6 == 18 and F6 == 8)

# ---------- H. 73 譜重建 ----------
print("=" * 72)
print("[H] 73 = Σγ_even − G_neg;  25 = 98 − 73")
r73 = S_even - G_neg
print(f"  90 − 17 = {mp.nstr(r73, 15)} (rank(CPX)=73 EXACT?)")
check("90−17 = 73 = rank(CPX)", r73 == 73)
check("25 = h²¹ − rank(CPX) = 98−73", h21 - rank_CPX == 25)

print("=" * 72)
print(f"RESULT: {passed}/{passed+failed} PASS")
sys.exit(0 if failed == 0 else 1)
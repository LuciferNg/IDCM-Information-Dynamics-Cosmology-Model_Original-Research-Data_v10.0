#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O244 — scripts/04: ζ_N 負矩家族 【代數推導】（替代 scripts/03 [F] 嘅純實證閉式）
=====================================================================================
目標: 將 ζ(2) = N⁴/90 + N²/36 + 17/720（scripts/03 實證）升級為【由首原理推導】,
      並一併推導 ζ(1), ζ(3), ζ(4)… 同正矩 ζ_N(−k) 閉式。

推導鏈 (全部 EXACT 有理算術, 唔係擬合):
  1. sin(2Nθ) = sin^{2N}(θ)·P(cotθ),   P(u) = Σ_{j=0}^{N−1} (−1)^{N−1−j} C(2N, 2j+1) u^{2j+1}
     ⟹ P 根 = {cot(πm/2N): m=1..2N−1} = {0, ±r_m}, r_m = cot(πm/2N), m=1..N−1
  2. Q(z) := P(u)/u|_{u²=z} = 2N·Π_{m=1}^{N−1} (z − r_m²)
     係數 [z^j]Q = (−1)^{N−1−j} C(2N, 2j+1)  (j=0..N−1)   ← 精確整數
  3. 正規化 q(z) = Q/2N = Π(z−r_m²) 全純 (monic) ⟹ Newton 恆等式:
     p_1 = −e_1,  p_k = −(e_1 p_{k−1} + e_2 p_{k−2} + … + e_{k−1} p_1 + k e_k)
     p_j := Σ_{m=1}^{N−1} cot^{2j}(πm/2N)  — EXACT Fraction
  4. csc²θ = 1 + cot²θ ⟹ Σ_{n=1}^N csc^{2k}(πn/2N) = Σ_{j=0}^{k} C(k,j) p_j   (p_0 := N)
  5. ζ_N(−k) = (1/4^k) Σ csc^{2k}(πn/2N)  —— 負矩閉式由係數表直接推出

判據:
  A 構造一致性: Q 領頭/常數係數 = 2N, (−1)^{N−1}2N; Π r_m² = 1 (正交性)
  B 直接數值核對: 推導出嘅 p_1..p_6, ζ(1..4), ζ_N(−1..−6)
     vs mpmath 60 位直接求和, 偏差 < 1e-45 (N ∈ {22,44,88,176,32,57,200})
  C 閉式識別: p_k(N), ζ(k)(N) 由 2k+1 個 N 值精確插值 (Vandermonde, Fraction)
     得有理多項式, 再喺樣本外 N 驗證 (唔係 fit, 係 Newton 推導 + 多項式閉式確認)
  D 正矩回復: ζ_N(−k) = N·C(2k,k) + 4^k/2 (scripts/03) 由本推導鏈統一導出

環境: /usr/bin/python3 (mpmath, 全有理算術 int/Fraction 優先)。
唯一輸入: 0,1 → φ → 結構數。零自由參數。
"""
import math
import itertools
import mpmath as mp
from fractions import Fraction

mp.mp.dps = 60

PASS = 0; FAIL = 0; TOTAL = 0
def check(name, cond, detail=""):
    global PASS, FAIL, TOTAL; TOTAL += 1
    if cond: PASS += 1; mark = "OK "
    else:    FAIL += 1; mark = "XX "
    print(f"  [{mark}] {name} {detail}")

# ── 1. Q 多項式係數 (sin(2Nθ) 展開) ──
def Q_coeffs(N):
    """Q(z) = Σ_j (−1)^{N−1−j} C(2N,2j+1) z^j, j=0..N−1 — 整數 array (升冪)"""
    return [(-1)**(N-1-j) * math.comb(2*N, 2*j+1) for j in range(N)]

# ── 3. Newton 恆等式 → p_k (Fraction, 對固定 N) ──
def power_sums(N, K):
    """返回 [p_0..p_K], p_j = Σ_{m=1}^{N−1} cot^{2j}(πm/2N) — Fraction 精確"""
    coeffs = Q_coeffs(N)                       # 升冪
    a = Fraction(coeffs[-1])                   # 領頭 = 2N
    c = [Fraction(x)/a for x in coeffs]        # monic q 嘅係數 (升冪)
    n = N - 1
    e = [0]*(n+1)                              # e_1..e_n (e[0] = 1)
    for k in range(1, n+1):
        e[k] = Fraction((-1)**k) * c[n-k]      # [z^{n−k}] q = (−1)^k e_k
    p = [Fraction(N)]                          # p_0 := N (j=0 項數)
    # Newton (monic q = Π(z−r_m): p_k = Σ_{j<k} (−1)^{j+1} e_j p_{k−j} + k(−1)^{k+1} e_k
    for k in range(1, K+1):
        s = sum(((-1)**(j+1))*e[j]*p[k-j] for j in range(1, k)) if k >= 2 else Fraction(0)
        s += Fraction(k)*((-1)**(k+1))*e[k]
        p.append(s)
    return p

# p_k 嘅小 N 直接核對 (mpmath)
def p_direct(N, k):
    return sum(mp.power(mp.cot(mp.pi*m/(2*N))**2, k) for m in range(1, N))

print("="*78)
print("  O244 scripts/04: ζ_N 負矩家族 — sin(2Nθ)→Q→Newton→p_k→ζ 代數推導")
print("  唯一輸入: 0,1 → φ → 結構數。零自由參數。")
print("="*78)

# ═══ A. 構造一致性 ═══
print("\n─── [A] Q 構造一致性 ───")
for N in [22, 44, 88]:
    qc = Q_coeffs(N)
    check(f"A1 Q 領頭 = 2N, 常數 = (−1)^(N−1)·2N (N={N})",
          qc[-1] == 2*N and qc[0] == (-1)**(N-1)*2*N,
          f"(領頭 {qc[-1]}, 常數 {qc[0]})")
    p = power_sums(N, 0)
    # Π r_m² = p 嘅極限: 用多項式常數/領頭: Q(0)/2N = (−1)^{N−1}·Πr_m² ⟹ Πr_m² = 1
    check(f"A2 Π_{{m=1}}^{{N−1}} cot²(πm/2N) = 1 (正交性, N={N})",
          qc[0] == (-1)**(N-1)*2*N, "(由 A1 直接: 常數 = (−1)^(N−1)·2N·Πr² ⟹ Πr² = 1)")

# ═══ B. p_k / ζ 直接數值核對 (推導 vs mpmath) ═══
print("\n─── [B] 推導值 vs mpmath 60 位直接求和 ───")
N_set = [22, 44, 88, 176, 32, 57, 200]
worstB = mp.mpf(0); total_checks = 0
for N in N_set:
    p = power_sums(N, 6)
    for k in range(1, 7):
        num = p_direct(N, k)
        d = abs(num - mp.mpf(p[k].numerator)/p[k].denominator)
        if d/max(mp.mpf(1), abs(num)) > worstB: worstB = d/max(mp.mpf(1), abs(num))
        if d > mp.mpf('1e-45')*max(1, abs(num)):
            check(f"B p_{k} (N={N})", False, f"(dev {mp.nstr(d,4)} > 1e-45)")
        total_checks += 1
    # ζ(1..4) = Σ csc^{2k}/4^k, csc^{2k} = Σ_j C(k,j) p_j
    for k in range(1, 5):
        S = sum(Fraction(math.comb(k, j)) * p[j] for j in range(k+1))
        z = S / Fraction(4**k)
        znum = sum(mp.power(4*mp.sin(mp.pi*n/(2*N))**2, -k) for n in range(1, N+1))
        d = abs(znum - mp.mpf(z.numerator)/z.denominator)
        if d/max(mp.mpf(1), abs(znum)) > worstB: worstB = d/max(mp.mpf(1), abs(znum))
        if d > mp.mpf('1e-45')*max(1, abs(znum)):
            check(f"B ζ({k}) (N={N})", False, "(dev > 1e-45)")
        total_checks += 1
check("B p1..p6 (7 N) + ζ(1..4) (7 N, 共 70 點) 全命中", worstB < mp.mpf('1e-45'),
      f"(total {total_checks} 點, worst rel dev {mp.nstr(worstB,4)})")

# ═══ C. 閉式識別: p_k(N), ζ(k)(N) 有理多項式 (Vandermonde 精確) ═══
print("\n─── [C] 閉式識別 (精確插值 + 樣本外驗證) ───")
def interpolate_poly(Ns, vals):
    """喺 Ns 上插值 (Fraction), 返回係數 list (升冪 N^{0..d})"""
    d = len(Ns) - 1
    M = [[Fraction(NV)**i for i in range(d+1)] for NV in Ns]
    b = [Fraction(v.numerator, v.denominator) if isinstance(v, Fraction) else Fraction(v) for v in vals]
    # 高斯消去 (Fraction)
    aug = [row + [b[i]] for i, row in enumerate(M)]
    for col in range(d+1):
        piv = next(r for r in range(col, d+1) if aug[r][col] != 0)
        aug[col], aug[piv] = aug[piv], aug[col]
        inv = Fraction(1)/aug[col][col]
        aug[col] = [x*inv for x in aug[col]]
        for r in range(d+1):
            if r != col and aug[r][col] != 0:
                f = aug[r][col]
                aug[r] = [x - f*y for x, y in zip(aug[r], aug[col])]
    return [aug[i][d+1] for i in range(d+1)]   # 升冪係數

fitN = [22, 32, 44, 57, 88, 100, 176, 200, 250]   # 9 點 → 八階多項式 (ζ(4) 用)
oosN = [11, 33, 55, 66, 300]                       # 樣本外
# p_k 閉式 (degree 2k): 用 2k+1 點
for k in range(1, 4):
    sub = fitN[:2*k+1]
    pvals = [power_sums(N, k)[k] for N in sub]
    poly = interpolate_poly(sub, pvals)
    pstr = " + ".join(f"{poly[i]}·N^{i}" for i in range(len(poly)) if poly[i] != 0)
    ok = all(power_sums(N, k)[k] == sum(poly[i]*Fraction(N)**i for i in range(len(poly)))
             for N in oosN + [44, 88])
    check(f"C1 p_{k}(N) 閉式 (degree {2*k}) 樣本外全命中", ok,
          f"(p_{k} = {pstr})")
# ζ(k) 閉式 (degree 2k): 同形轉換
for k in range(1, 5):
    sub = fitN[:2*k+1]
    def zvals(N):
        p = power_sums(N, k)
        S = sum(Fraction(math.comb(k, j))*p[j] for j in range(k+1))
        return S/Fraction(4**k)
    zv = [zvals(N) for N in sub]
    poly = interpolate_poly(sub, zv)
    zstr = " + ".join(f"{poly[i]}·N^{i}" for i in range(len(poly)) if poly[i] != 0)
    ok = all(zvals(N) == sum(poly[i]*Fraction(N)**i for i in range(len(poly)))
             for N in oosN + [44, 88])
    check(f"C2 ζ({k})(N) 閉式 (degree {2*k}) 樣本外全命中", ok,
          f"(ζ({k}) = {zstr})")

# ═══ D. 正矩 ζ_N(−k) 推導: 奇諧波幾何和 (sin^{2k} 展開鏈) ═══
print("\n─── [D] 正矩 ζ_N(−k) = N·C(2k,k) + 4^k/2 — 由奇諧波幾何和導出 ───")
# 幾何和: Σ_{n=1}^N e^{ijπn/N} = 2z/(1−z), z=e^{ijπ/N};  j 奇 ⟹ z^N = −1
#   = −1 + i·cot(jπ/2N)  EXACT (實部 −1, 虛部 cot(jπ/2N))
# ⟹ Σ cos(jπn/N) = −1 (j 奇);  sin^{2k}θ 展開 ⟹ sin^{2k}(πn/2N) = (1/4^k)Σ_j C(2k,j)(−1)^{...}
# 經 cos 和: Σ_n cos(2·(k−j)·θ_n) = Σ_n cos((k−j)πn/N) = −δ_{k−j 奇}
# ⟹ Σ sin^{2k} = [N·C(2k,k) + 2Σ_{j<k, (k−j) 奇} C(2k,j)]/4^k,  2Σ_{j<k,k−j奇}C(2k,j) = 4^k/2
okD = True; worstD = mp.mpf(0)
for N in N_set[:4]:
    wn = [mp.pi*n/N for n in range(1, N+1)]
    for k in range(1, 7):
        # 幾何和閉式 vs 直接求和 (j=1,3,5 奇)
        for j in [1, 3, 5]:
            S_closed = mp.mpf(-1) + 1j*mp.cot(mp.pi*j/(2*N))
            S_direct = sum(mp.e**(1j*j*w) for w in wn)
            d = abs(S_direct - S_closed)
            if d/max(mp.mpf(1), abs(S_direct)) > worstD: worstD = d/max(mp.mpf(1), abs(S_direct))
            if abs(S_direct.real + 1) > mp.mpf('1e-40') or abs(d) > mp.mpf('1e-40'):
                okD = False
        # Σ sin^{2k} = [N·C(2k,k) + 4^k/2]/4^k  → ζ(−k) = N·C(2k,k) + 4^k/2
        S_direct = sum(mp.power(mp.sin(mp.pi*n/(2*N)), 2*k) for n in range(1, N+1))
        S_closed = (mp.mpf(N)*math.comb(2*k, k) + mp.mpf(4)**k/2)/mp.mpf(4)**k
        d = abs(S_direct - S_closed)
        if d/max(mp.mpf(1), abs(S_direct)) > worstD: worstD = d/max(mp.mpf(1), abs(S_direct))
        if d > mp.mpf('1e-40')*max(1, abs(S_direct)):
            okD = False
check("D 正矩導出: 奇諧波幾何和 (−1+i·cot) + sin^{2k} 展開 ⟹ ζ_N(−k) = N·C(2k,k)+4^k/2 (24/24)",
      okD and worstD < mp.mpf('1e-40'),
      f"(worst rel dev {mp.nstr(worstD,4)}; 見 docs/04 推導梗概)")

# ═══ E. ζ_N(2) 具體數值 (N=44) 展示 ═══
print("\n─── [E] 展示: N=44 直接代入 ───")
p = power_sums(44, 2)
print(f"       p_1 = {p[1]}   (= (2N²−3N+1)/3 = {Fraction(2*44*44-3*44+1, 3)})")
S2 = p[0] + 2*p[1] + p[2]
print(f"       Σ csc⁴ = {S2}")
z2 = S2/Fraction(16)
print(f"       ζ(2) = {z2}  (閉式 44⁴/90 + 44²/36 + 17/720 = "
      f"{Fraction(44**4, 90) + Fraction(44**2, 36) + Fraction(17, 720)}) ⊗ 相等")
check("E N=44 ζ(2) 推導 = 閉式", z2 == Fraction(44**4,90)+Fraction(44**2,36)+Fraction(17,720),
      f"(ζ(2) = {z2.numerator}/{z2.denominator} = {mp.nstr(mp.mpf(z2.numerator)/z2.denominator, 12)})")

print(f"\n{'='*78}")
print(f"  RESULT: {PASS}/{TOTAL} PASS, {FAIL}/{TOTAL} FAIL")
print(f"{'='*78}")
import sys
sys.exit(0 if FAIL == 0 else 1)
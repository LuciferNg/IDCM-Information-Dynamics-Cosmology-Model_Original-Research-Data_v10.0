#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O210 scripts/04_escape_period_derivation.py
================================================================================
目的: 兩件事
  (A) 獨立重算 O88 逃生路線普查（唔靠 O88 自報）: Λ^k(12)/Sym^k(12) 含 ΔB=1 合格分量
      ⟺ k ≡ 2 (mod 4)（k ∈ {2,6,10}）。
  (B) ★ 結構推導: 證明呢個週期唔係「SU(4) 表示論嘅偶然指紋」，而係
      **k ≡ ±|B−L| (mod B)** 之結構定則，其中 B = 4 = IDCM 分支數（12 = B·N_gen）。
  (C) `66 = 2·K_tree` 之身份裁定（子群鏈分析）。

方法（全部真算，禁憑記憶寫分解）:
  SU(4) ⊃ SU(3)_c × U(1)_{B−L}:  4 = 3_{1/3} ⊕ 1_{−1}
  S_λ(C³ ⊕ C) = ⊕_{μ : λ/μ 為水平條} S_μ(C³) ⊗ (U(1))^{|λ|−|μ|}
  charge(S_μ) = |μ|/3 − (|λ|−|μ|) = (4|μ| − 3k)/3      (k = |λ|)  ← U(1) 與 SU(3) 對易 ⟹ 常數
  SU(3) irrep S_μ 為 (反)三重態 ⟺ Dynkin (p,q) = (μ₁−μ₂, μ₂−μ₃) ∈ {(1,0),(0,1)}
  合格 ΔB=1 ⟺ 存在 μ 使 (三重態) ∧ |charge| = 2/3
Cauchy（SU(12) ⊃ SU(4)×SU(3)_F, 12 = (4,3)）:
  Λ^k(12)   = ⊕_{λ⊢k} S_λ(4) ⊗ S_{λ'}(3)
  Sym^k(12) = ⊕_{λ⊢k} S_λ(4) ⊗ S_λ(3)
"""
from fractions import Fraction as F
from functools import lru_cache
import math

stats = {"PASS": 0, "FAIL": 0}

def chk(name, cond):
    stats["PASS" if cond else "FAIL"] += 1
    print(f"  {'PASS' if cond else 'FAIL'}  {name}")
    return cond

# ───────────────────────── 基本工具 ─────────────────────────
def partitions(n, max_rows):
    """n 之分割，最多 max_rows 行（遞減）"""
    if n == 0:
        yield ()
        return
    def rec(rem, mx, acc):
        if rem == 0:
            yield tuple(acc); return
        if len(acc) == max_rows:
            return
        for a in range(min(rem, mx), 0, -1):
            acc.append(a)
            yield from rec(rem - a, a, acc)
            acc.pop()
    yield from rec(n, n, [])

def conj(lam):
    if not lam: return ()
    return tuple(sum(1 for x in lam if x >= j) for j in range(1, lam[0] + 1))

def is_horizontal_strip(lam, mu):
    """λ/μ 為水平條 ⟺ μ ⊆ λ 且每列恰好多 0/1 格（等價：每列差 ≤1 且 μ₁ ≥ λ₂ 等）"""
    if len(mu) > len(lam): return False
    l = list(lam) + [0] * (len(mu) - len(lam))
    if any(l[i] < mu[i] for i in range(len(mu))): return False
    # 水平條: 每 row 差 ≤ 1
    return all(l[i] - mu[i] <= 1 for i in range(len(mu)))

def subdiagrams_hstrip(lam):
    """所有 μ : λ/μ 為水平條 ⟺ 交錯條件 λ₁ ≥ μ₁ ≥ λ₂ ≥ μ₂ ≥ λ₃ ≥ …
       （等價於每 column 恰移除 ≤1 格；μ 保持為 partition）"""
    n = len(lam)
    pad = list(lam) + [0] * (n + 1)
    out = []
    def rec(i, prev, acc):
        if i == n:
            out.append(tuple(acc)); return
        hi = min(pad[i], prev)
        lo = pad[i + 1]
        for v in range(lo, hi + 1):
            rec(i + 1, v, acc + [v])
    rec(0, 10 ** 9, [])
    return sorted({tuple(x for x in mu if x > 0) for mu in out})

def dynkin(lam, n=3):
    l = list(lam) + [0] * (n - len(lam))
    return tuple(l[i] - l[i + 1] for i in range(n - 1))

def is_triplet(mu):
    p, q = dynkin(mu, 3)
    return (p, q) in {(1, 0), (0, 1)}

def gl_dim(lam, n=4):
    """Weyl 維數公式 (GL(n) / SU(n) 同維, λ ≤ n 行)"""
    l = [lam[i] + (n - 1 - i) for i in range(len(lam))] + [n - 1 - i for i in range(len(lam), n)]
    num = 1
    for i in range(n):
        for j in range(i + 1, n):
            num *= (l[i] - l[j])
    den = 1
    for i in range(n):
        for j in range(i + 1, n):
            den *= (j - i)
    return num // den

def charge(mu, k):
    """U(1)_{B−L} 電荷 = (4|μ| − 3k)/3  (N_c=3, B=4)"""
    return F(4 * sum(mu) - 3 * k, 3)

# ─────────────── (A) 獨立重算 O88 普查 ───────────────
print("=" * 76)
print("(A) Λ^k(12) / Sym^k(12) 合格分量普查 — 獨立重算（判據: 三重態 ∧ |B−L|=2/3）")
print("=" * 76)

def qualifying_components(k, family):
    """回傳合格 (λ, S_λ(4) 維數, SU(3)_F 標籤, charge) 列表"""
    out = []
    if family == "L":
        lams = [lam for lam in partitions(k, 4) if len(conj(lam)) <= 3]   # λ' ≤ 3 行
    else:
        lams = [lam for lam in partitions(k, 3)]                          # Sym: λ ≤ 3 行 & ≤ 4 行
    for lam in lams:
        for mu in subdiagrams_hstrip(lam):
            if len(mu) > 3:
                continue            # ★ S_μ(C³) = 0（μ > 3 行）⟹ SU(3) 因子消失
            if not is_triplet(mu):
                continue
            if abs(charge(mu, k)) == F(2, 3):
                out.append((lam, gl_dim(lam, 4), mu, charge(mu, k)))
    return out

print("\n【維數守恆自檢】Σ_λ dim S_λ(4)·dim S_{λ'}(3) = C(12,k)")
for k in range(0, 13):
    totL = sum(gl_dim(l, 4) * gl_dim(conj(l), 3) for l in partitions(k, 4) if len(conj(l)) <= 3)
    totS = sum(gl_dim(l, 4) * gl_dim(l, 3) for l in partitions(k, 3))
    okL = (totL == math.comb(12, k))
    okS = (totS == math.comb(12 + k - 1, k))
    if not (okL and okS):
        print(f"  FAIL k={k} Λ:{totL} vs {math.comb(12,k)}; Sym:{totS} vs {math.comb(12+k-1,k)}")
chk("Λ 族維數守恆 k=0..12 全過", all(
    sum(gl_dim(l, 4) * gl_dim(conj(l), 3) for l in partitions(k, 4) if len(conj(l)) <= 3) == math.comb(12, k)
    for k in range(13)))
chk("Sym 族維數守恆 k=0..12 全過", all(
    sum(gl_dim(l, 4) * gl_dim(l, 3) for l in partitions(k, 3)) == math.comb(12 + k - 1, k)
    for k in range(13)))

print("\n【已知分解自檢】(對照 O88 docs/07 §5 判據表)")
d15 = [(mu, charge(mu, 4)) for lam in [(2, 1, 1)] for mu in subdiagrams_hstrip(lam) if not is_triplet(mu) or True]
l = (2, 1, 1)
content15 = sorted([(dynkin(mu, 3), gl_dim(mu, 3), charge(mu, 4)) for mu in subdiagrams_hstrip(l)],
                   key=lambda t: (t[2], -t[1]))
exp15 = [((1, 1), 8, F(0)), ((1, 0), 3, F(4, 3)), ((0, 1), 3, F(-4, 3)), ((0, 0), 1, F(0))]
chk(f"15 = Adj(4) 內容 = 8_0 ⊕ 3_(4/3) ⊕ 3̄_(−4/3) ⊕ 1_0（實得 {content15}）",
    content15 == sorted(exp15, key=lambda t: (t[2], -t[1])))
l = (1, 1)
c6 = sorted([(gl_dim(mu, 3), charge(mu, 2)) for mu in subdiagrams_hstrip(l)], key=lambda t: -t[1])
chk(f"6 = Λ²(4) 內容 = 3̄_(2/3) ⊕ 3_(−2/3)（實得 {c6}）", c6 == [(3, F(2, 3)), (3, F(-2, 3))])
l = (2,)
c10 = sorted([(gl_dim(mu, 3), charge(mu, 2)) for mu in subdiagrams_hstrip(l)], key=lambda t: -t[1])
chk(f"10 = Sym²(4) 內容 = 6_(2/3) ⊕ 3_(−2/3) ⊕ 1_(−2)（實得 {c10}）",
    c10 == [(6, F(2, 3)), (3, F(-2, 3)), (1, F(-2))])

print("\n【普查結果】")
print(f"{'族':<6}{'k':>3}{'合格分量數':>12}   合格分量 (SU(4)λ_dim ⊗ SU(3)_F dim @ B−L)")
qual = {}
for family, fname in (("L", "Λ^k"), ("S", "Sym^k")):
    for k in range(0, 13):
        qc = qualifying_components(k, family)
        qual[(family, k)] = qc
        if qc:
            desc = "; ".join(f"{lam}_{dim} ⊗ {gl_dim(mu,3)} @ {ch}" for lam, dim, mu, ch in qc)
            print(f"{fname:<6}{k:>3}{len(qc):>12}   {desc}")

qk = sorted({k for (f, k), v in qual.items() if v})
print(f"\n▶ 合格 k 集 = {qk}")
chk("★ 規格: 合格 ⟺ k ≡ 2 (mod 4), k ∈ {2,6,10}", qk == [2, 6, 10])
chk("k=3,4,5,7,8,9,11,12 零合格", all(not qual[(f, k)] for f in "LS" for k in [3,4,5,7,8,9,11,12]))
q_dims = sorted({dim for (f, k), v in qual.items() for (_, dim, _, _) in v})
print(f"▶ 合格 SU(4) irrep 維數集 = {q_dims}")
chk("★ 合格維數集 = {6,10,64,70,270,300}（O88 PD#4 判據）", q_dims == [6, 10, 64, 70, 270, 300])
cntL = [(k, len({lam for lam, _, _, _ in qual[("L", k)]})) for k in (2, 6, 10)]
cntS = [(k, len({lam for lam, _, _, _ in qual[("S", k)]})) for k in (2, 6, 10)]
print(f"▶ 合格 Cauchy 分量（distinct λ）: Λ 族 = {cntL}；Sym 族 = {cntS}")
chk("★ Λ 族 = (2,2),(6,4),(10,2)；Sym 族 = (2,2),(6,3),(10,3)（O88 §2 表）",
    cntL == [(2, 2), (6, 4), (10, 2)] and cntS == [(2, 2), (6, 3), (10, 3)])
chk("Λ²(12) = 66 含 2 個合格分量（O88 §2 首行）",
    len({lam for lam, _, _, _ in qual[("L", 2)]}) == 2 and math.comb(12, 2) == 66)

# ─────────────── (B) ★ 結構定則推導 ───────────────
print("\n" + "=" * 76)
print("(B) ★ 結構定則: k ≡ ±|B−L| (mod B)，B = 4 = IDCM 分支數")
print("=" * 76)
print("""
推導:
  12 = B · N_gen = 4 × 3      ⟹ SU(12) ⊃ SU(B) × SU(N_gen),  12 = (B, N_gen)
  SU(B) ⊃ SU(N_c) × U(1)_{B−L},  N_c = B − 1 = 3（12 = (B,3) 逼出）
  B = N_c + 1 係單位跡條件: N_c·(1/N_c) + 1·(−1) = 0
  權重盒數 (n₁,n₂,n₃ | n₄): B−L = (n₁+n₂+n₃)/N_c − n₄
  Cauchy 分解: S_λ 之分量 S_μ ⟹ n₄ = k − |μ| ⟹ B−L = |μ|/N_c − (k − |μ|) = (B|μ| − N_c·k)/N_c
  ⟹  N_c·|B−L| = B|μ| − N_c·k      [|B−L| = q]
  取 mod B（gcd(N_c,B) = gcd(3,4) = 1 可逆）:  N_c·k ≡ −N_c·q (mod B)
  N_c = B−1 ≡ −1 (mod B) ⟹ N_c⁻¹ ≡ −1 (mod B)
  ⟹  ★ k ≡ ±q (mod B)     即 k ≡ ±|B−L| (mod B)
""")
B, Nc = 4, 3
def rule_masks(q):
    """由定則 k ≡ ±q (mod B) 產生 k ≤ 12 之集合"""
    out = []
    for k in range(13):
        for s in (+1, -1):
            if (k - s * q.numerator * pow(q.denominator, -1, B)) % B == 0:
                out.append(k); break
    return sorted(set(out))
tests = [(F(1, 3), "夸克單體"), (F(2, 3), "qq pair (ΔB=1 通道)"), (F(1, 1), "B−L=1"),
         (F(4, 3), "gauge coset (PD#1)"), (F(5, 3), "Sym³(4) 之三重態")]
def empirical(q):
    """盲目真算: 存在 λ ⊆ 4 行, λ' ≤ 3 行, 含 triplet μ (≤3 行) 且 |charge| = q"""
    emp = []
    for k in range(13):
        for lam in partitions(k, 4):
            if len(conj(lam)) > 3:
                continue
            if any(len(mu) <= 3 and is_triplet(mu) and abs(charge(mu, k)) == q
                   for mu in subdiagrams_hstrip(lam)):
                emp.append(k); break
    return sorted(set(emp))

for q, lbl in tests:
    pred = rule_masks(q)
    e = empirical(q)
    print(f"  |B−L| = {str(q):<5} ({lbl:<18}) 定則預測 k ∈ {pred}")
    print(f"  {'':<28} 盲目真算 k ∈ {e}")
    chk(f"    ⟹ 必要性 真算 ⊆ 定則 ({str(q)})", set(e) <= set(pred))
    print(f"         （定則多出者 = 該 k 無 triplet 分量者，屬退化排除: {sorted(set(pred) - set(e))}）")
chk("★ ΔB=1 通道 (|B−L|=2/3): 定則與真算完全相等 = {2,6,10}",
    rule_masks(F(2, 3)) == empirical(F(2, 3)) == [2, 6, 10])
# ★ 盲測（O88 未算過之通道）: |B−L| = 4/3 ⟹ k ≡ 0 (mod 4)
pred43 = rule_masks(F(4, 3))
chk("★ 新預言: |B−L|=4/3 通道 ⟹ k ≡ 0 (mod 4)（= Λ⁴(12) 之 15 分量）", pred43[:4] == [0, 4, 8, 12])
chk("    Λ⁴(12) = 495 含 15 = Adj(4) 三重態 @ 4/3（真算 495 = C(12,4)）",
    math.comb(12, 4) == 495 and any(is_triplet(mu) and abs(charge(mu, 4)) == F(4, 3)
                                    for lam in partitions(4, 4) if len(conj(lam)) <= 3
                                    for mu in subdiagrams_hstrip(lam)))

# ─────────────── (C) 66 = 2·K_tree 身份裁定 ───────────────
print("\n" + "=" * 76)
print("(C) `66 = 2·K_tree` 之子群鏈分析")
print("=" * 76)
# 鏈 1: SU(4)×SU(3)_F
c = sum(gl_dim(l, 4) * gl_dim(conj(l), 3) for l in partitions(2, 4) if len(conj(l)) <= 3)
parts1 = [(l, gl_dim(l, 4), conj(l), gl_dim(conj(l), 3)) for l in partitions(2, 4) if len(conj(l)) <= 3]
# 鏈 2: SU(11)×U(1)  (12 = 1 ⊕ 11)
l2 = math.comb(11, 2) + 11
print(f"  鏈 1 [SU(4)×SU(3)_F]: Λ²(12) = " +
      " ⊕ ".join(f"S_{a}(4)_{d1} ⊗ S_{conj(a)}(3)_{d2}" for a, d1, _, d2 in parts1) + f" = {c}")
chk("鏈 1 維數 = 66", c == 66)
print(f"  鏈 2 [SU(11)×U(1)]: Λ²(12) = Λ²(1⊕11) = Λ²(11) ⊕ (1⊗11) = {math.comb(11,2)} ⊕ 11 = {l2}")
chk("鏈 2 維數 = 66（且 Λ²(11) = C(L₅,2) = 55 = F₁₀）", l2 == 66 and math.comb(11, 2) == 55)
print(f"  鏈 3 [樹譜]: K_tree 譜 λ_k = 4sin²(kπ/68), k=1..33, Σλ = 66 = 2·K_tree")
print(f"  K_tree = 33 = N_gen·L₅ = 3×11；樹譜固定點 λ₁₇ = 4sin²(π/4) = 2 = μ²")
import mpmath as mp
mp.mp.dps = 40
Sl = mp.fsum([4 * mp.sin(mp.pi * k / 68) ** 2 for k in range(1, 34)])
print(f"  數值: Σλ = {mp.nstr(Sl, 20)}")
chk("鏈 3 Σλ = 66（樹譜和）", abs(Sl - 66) < mp.mpf("1e-25"))
chk("樹譜固定點 λ₁₇ = μ² = 2", abs(4 * mp.sin(mp.pi * 17 / 68) ** 2 - 2) < mp.mpf("1e-30"))
print("""
  ⟹ 66 出現於三條互不相通之結構:
       (i)  SU(4)×SU(3)_F 鏈: 10⊗3̄ ⊕ 6⊗6 = 30+36 = 66   ← ΔB=1 判據所在鏈
       (ii) SU(11)×U(1) 鏈: 55 ⊕ 11 = 66                  ← K_tree 身份所在鏈
       (iii) 樹譜和 Σλ = 66                                ← 譜量（非維數）
  ⟹ 冇單一子群鏈同時承載 (i) 與 (ii) ⟹ 冇自然映射 Λ²(12) → K_tree ⊕ K_tree
  ⟹ ★ 裁定: `66 = 2·K_tree` = 跨鏈算術恆等式（🟡），**唔係** ΔB=1 通道之強逼機制。
     通道之真正強逼 = k = 2 = 對中 fundamentals 數目（qq pair）+ 模 B 定則。
""")

# ─────────────── (D) B-擾動測試（結構剛性, 4 Hard Tests #4） ───────────────
print("=" * 76)
print("(D) B-擾動測試: 樹譜結構 vs 2·K_tree 係「結構定則」定「單點巧合」？")
print("=" * 76)
print("""
  樹鏈結構（B-一般）:  鏈長 sites = 4(B²+1) = 68 ✓
                       λ_k = B·sin²(kπ/sites),  k = 1 .. sites/2−1 = 2B²+1 = K_tree ✓
  配對:                k ↔ sites/2−k = half−k  ⟹  λ_k + λ_{half−k} = B（振幅，恆等）
  配對數:              (2B²)/2 = B² = 16 ✓（固定點 k = half/2 = 17，λ = B/2 = μ² = 2）
  ⟹  Σλ = B²·B + B/2 = B³ + B/2
       B = 4:  Σλ = 64 + 2 = 66 ✓
""")
BB = 4
sites = 4 * (BB ** 2 + 1)          # 68
half = sites // 2                   # 34
modes = half - 1                    # 33 = 2B²+1
lamB = lambda k: BB * mp.sin(mp.pi * k / sites) ** 2
print(f"  B={BB}: 鏈長 sites = 4(B²+1) = {sites}; half = {half}; 模數 = half−1 = {modes} = 2B²+1 = K_tree ✓")
chk("樹鏈: sites = 4(B²+1) = 68, half = 34, 模數 = half−1 = 33 = 2B²+1 = K_tree",
    sites == 68 and half == 34 and modes == 33 == 2 * BB ** 2 + 1)
pairsum = all(abs(lamB(k) + lamB(half - k) - BB) < mp.mpf("1e-30") for k in range(1, half // 2))
chk("配對和 λ_k + λ_{half−k} = B（16 對全過，恆等）", pairsum)
chk("配對數 = B² = 16; 固定點 k = half/2 = 17, λ = B/2 = μ² = 2",
    (half // 2) == 17 and abs(lamB(half // 2) - 2) < mp.mpf("1e-30"))
chk("★ Σλ = B²·B + B/2 = B³ + B/2 = 66（結構式，只用 B）",
    BB ** 2 * BB + BB // 2 == 66 and BB ** 3 + BB // 2 == 66)
print("\n  【跨結構比較】R1 = 2·K_tree = 2·(B−1)·L₅（鏈, N_gen=B−1）vs R2 = Σλ = B³ + B/2（樹譜）")
rows = []
for b in range(2, 8):
    r1 = 2 * (b - 1) * 11
    r2 = b ** 3 + b / 2
    rows.append((b, r1, r2, r1 == r2))
    print(f"    B = {b}:  2·K_tree = {r1:>4}   Σλ = {r2:>7}   {'★ 相等' if r1 == r2 else ''}")
cross = [b for b, r1, r2, eq in rows if eq]
chk("★ B-一般性: 兩表達式只喺 B = 4 相交（無函數恆等 ⟹ 無結構機制）", cross == [4])
print("""
  ⟹ 兩個「66」係兩條獨立結構鏈之單點交會（B = 4），**冇** B-一般恆等 ⟹ 冇 map
  ⟹ 判定: `66 = 2·K_tree` = **單點算術巧合**（🔴 作為強逼機制）；但 66 本身作為
     Λ²(12) 仍係結構強逼（k = 2 = qq pair 之 fundamentals 數 + 模 B 定則）
  ⟹ O88 docs/07 §G#4 交接項 #4 結案: **非結構強逼**（附 B-擾動證）
""")

print("=" * 76)
print(f"O210 escape-period derivation — PASS {stats['PASS']} / FAIL {stats['FAIL']}")
print("=" * 76)
print("RESULT:", "FAIL" if stats["FAIL"] else "PASS")
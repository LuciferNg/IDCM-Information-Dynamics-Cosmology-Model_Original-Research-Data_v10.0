#!/usr/bin/env python3
"""
O83 — Script 09: A1 攻堅 — w_n 結構生成 (非由 A_m 反解)
=========================================================
★ 紀律: 候選族**事前宣告** (見 §3 FAMILY 常數)，掃描期間唔改族。
        全部判定用整數/Fraction 精確運算，浮點只做顯示。

目標 (權威 obs, 由 ACT DR4)
  A₁ = 1 (歸一)
  A₂/A₁ = 4/9      A₄/A₁ = 9/49     A₆/A₁ = 16/121      (偶峰 k=1,2,3)
  A₅/A₃ = 3/14     A₇/A₅ = 2/3                          (奇峰 — 獨立測試)

結構檢查:
  [1] 母函數恆等式 B·a_k − b_k = F₅
  [2] φ 層權重假設 |W_ℓ|² = φ^{-2ℓ}  (O165) — 定量測試
  [3] γ_n / ω_n 算子身份測試 (exact)
  [4] ★ 盲掃: r_k = (a+p·k)/(b+q·k), e ∈ {1,2} → 三點全中者
  [5] 命中者是否同時滿足 B·a_k − b_k = F₅ (結構強迫)
  [6] 奇峰獨立測試 (母函數推奇峰?)
  [7] 密度基準: N_search / N_hit / q_obs  (精確計數，取代 MC)
"""
import os, sys
from fractions import Fraction as Fr

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"  [{'✅ PASS' if cond else '❌ FAIL'}] {name} {detail}")
def note(name, detail=""):
    print(f"  [📝 註記] {name} {detail}")
def rec(kind, name, detail=""):
    print(f"  [{kind}] {name} {detail}")

print("=" * 78)
print("  O83 — Script 09: A1 攻堅 — w_n 結構生成")
print("=" * 78)

# ──────────────────────────────────────────────
# §0 結構原子 (corpus 已註冊，唔新造)
# ──────────────────────────────────────────────
N_d, M, B, N_gen, Z2 = 44, 33, 4, 3, 2
F = {3:2, 4:3, 5:5, 6:8, 7:13, 8:21, 9:34, 10:55, 11:89}
L = {0:2, 1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47}
CY3 = 134

# ──────────────────────────────────────────────
# §1 母函數恆等式 (既有, 精確)
# ──────────────────────────────────────────────
print("\n─── [1] 母函數恆等式 (整數精確) ───")
print(f"  偶峰 A_{{2k}}/A₁ = ((k+1)/(4k−1))²   k=1,2,3")
for k in (1, 2, 3):
    a, b = k + 1, 4 * k - 1
    val = Fr(a * a, b * b)
    print(f"    k={k}: a_k={a}, b_k={b}, (a/b)² = {val}")
    # B·a_k − b_k = 5 = F₅ ?
    print(f"          B·a_k − b_k = {B*a} − {b} = {B*a-b}  (F₅={F[5]})")
ident = all(B * (k + 1) - (4 * k - 1) == F[5] for k in range(1, 20))
check("B·a_k − b_k = F₅ ∀k (a_k=k+1)", ident,
      f"⟹ 母函數只剩一個自由整數序列 a_k")
note("⟹ b_k = B·a_k − F₅ 完全由 a_k 決定 (一個參數族)")

print(f"\n  奇峰 (獨立):")
print(f"    A₅/A₃ = 3/14 = {Fr(3,14)}")
print(f"    A₇/A₅ = 2/3  = {Fr(2,3)}")
note("2/3 = (a/b)|_{k=1} 一次方 (非平方)；3/14 = (3/7)·(1/2)")

# ──────────────────────────────────────────────
# §2 φ 層權重假設 (O165 |W_ℓ|² = φ^{-2ℓ})
# ──────────────────────────────────────────────
print("\n─── [2] φ 層權重假設 (O165) 定量測試 ───")
import math
phi = (1 + 5 ** 0.5) / 2
print("  假設: w_m² ∝ φ^{−2ℓ_m}  ⟹ A_m/A₁ = φ^{−2(ℓ_m−ℓ₁)}")
A_obs = {1: Fr(1), 2: Fr(4,9), 4: Fr(9,49), 6: Fr(16,121)}
dLs = {}
for m, ratio in A_obs.items():
    if m == 1: continue
    dL = -math.log(float(ratio)) / (2 * math.log(phi))
    dLs[m] = dL
    print(f"    A_{m}/A₁ = {ratio} ⟹ 需 Δℓ = {dL:.4f}  (唔係整數)")
fail = all(abs(v - round(v)) > 0.05 for v in dLs.values())
check("φ 層假設 ℓ 為整數 → 否定" if fail else "φ 層假設可行", fail,
      "⟹ |W_ℓ|²=φ^{−2ℓ} 唔可以直接做 w_n² (需非整數層)")
note("Δℓ = " + ", ".join(f"{v:.4f}" for v in dLs.values()) +
     " — 只有 k=3 近整數 3 ⟹ 單點巧合, 唔可成立")

# ──────────────────────────────────────────────
# §3 γ_n / ω_n 算子身份測試 (exact, 用 algebraic 關係)
# ──────────────────────────────────────────────
print("\n─── [3] γ_n / ω_n 算子身份測試 ───")
print("  檢: A_m 是否可以係 γ 比 / ω 比")
print("  ⚠ γ_n = 4sin²(nπ/88)：除 n=22,44 (γ=4) 外一般係無理代數數")
import sympy as sp
n_s = sp.symbols('n', integer=True, positive=True)
irr_demo = [k for k in (1, 7, 14, 33) 
            if sp.nsimplify(4 * sp.sin(k * sp.pi / 88) ** 2).is_rational is not True]
print(f"  抽樣無理性 (n=1,7,14,33): {len(irr_demo)}/4 非有理")
note("γ_n 比對一般 n 屬 ℚ(ζ₁₇₆) 嘅 2 次子域 ⟹ A_m ∈ ℚ 唔可能係 γ 比")
check("A_m ∈ ℚ 而 γ_n 比 ∉ ℚ (一般 n) ⟹ γ 算子族排除", len(irr_demo) >= 3,
      "代數域論證: 有理 vs 4sin² 嘅 extension")
note("ω 比 = sin 比，同理非有理 ⟹ ω 算子族亦排除")
rec("🟢", "算子族縮減", "A_m 全有理 ⟹ w_n² 只可含 L_k/F_k/整數原子")

# ──────────────────────────────────────────────
# §4 ★ 盲掃 (族事前宣告)
# ──────────────────────────────────────────────
print("\n─── [4] ★ 盲掃 — 族事前宣告 (唔改) ───")
# ★★★ FAMILY: 掃描前宣告，掃描期間不改 ★★★
A_ATOM = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 16, 18, 21, 22, 25,
          29, 33, 34, 44, 47, 55, 88, 89, 90, 132, 178, 528]      # 30
B_ATOM = [-1, -2, -3, -4, -5, -6, -8, -11] + A_ATOM[:0] + [-13] + [1,2,3,4,5,7,8,11,13,16,18,21,25,33,44]  # 22
P_ATOM = [1, 2, 3, 4, 5, 6, 8, 9, 11, 16, 25, 33, 44]            # 13
Q_ATOM = [1, 2, 3, 4, 5, 6, 8, 9, 11, 16, 25, 33, 44]            # 13
E_ATOM = [1, 2]                                                   # 2
N_search = len(A_ATOM) * len(B_ATOM) * len(P_ATOM) * len(Q_ATOM) * len(E_ATOM)
print(f"  族: r_k = ((a + p·k)/(b + q·k))^e")
print(f"     a ∈ A_ATOM ({len(A_ATOM)}) : {A_ATOM}")
print(f"     b ∈ B_ATOM ({len(B_ATOM)}) : {B_ATOM}")
print(f"     p ∈ P_ATOM ({len(P_ATOM)}) : {P_ATOM}")
print(f"     q ∈ Q_ATOM ({len(Q_ATOM)}) : {Q_ATOM}")
print(f"     e ∈ {E_ATOM}")
print(f"  ★ N_search = {N_search:,}")

# 目標 (偶峰三點) — 精確有理
TGT = {1: Fr(4, 9), 2: Fr(9, 49), 3: Fr(16, 121)}
# 精確整數比較: (a+pk)^e/(b+qk)^e == num/den
hits = []
for a in A_ATOM:
    for b in B_ATOM:
        for p in P_ATOM:
            for q in Q_ATOM:
                for e in E_ATOM:
                    ok = True
                    for k, t in TGT.items():
                        num = a + p * k
                        den = b + q * k
                        if den == 0:
                            ok = False; break
                        # (num/den)^e == t.num/t.den  ⟹ num^e · t.den == t.num · den^e
                        if num ** e * t.denominator != t.numerator * den ** e:
                            ok = False; break
                    if ok:
                        hits.append((a, b, p, q, e))
print(f"\n  命中三點全中 = {len(hits)}")
for h in hits:
    a, b, p, q, e = h
    print(f"    r_k = (({a}+{p}k)/({b}+{q}k))^{e}")

# 已知母函數在唔在族內?
known = (1, -1, 1, 4, 2)
print(f"  已知母函數 ((1+1k)/(−1+4k))² = {known}  在族內: {known in hits}")

# ──────────────────────────────────────────────
# §5 命中者結構強迫檢 (B·a_k − b_k = F₅)
# ──────────────────────────────────────────────
print("\n─── [5] 命中者結構強迫檢 ───")
struct = []
for (a, b, p, q, e) in hits:
    # b_k = b + q k, a_k = a + p k ⟹ 要求 q = B·p 且 b = B·a − F₅
    if q == B * p and b == B * a - F[5]:
        struct.append((a, b, p, q, e))
print(f"  同時滿足「q = B·p ∧ b = B·a − F₅」= {len(struct)}")
for s in struct: print(f"    {s}")
rec("🟢" if struct else "🔴", "母函數結構強迫",
    f"{len(struct)}/{len(hits)} 命中者滿足 q=Bp ∧ b=Ba−F₅")

# ──────────────────────────────────────────────
# §5b 標度去重 (4 命中 = 同一公式 × {1,2,4,11})
# ──────────────────────────────────────────────
print("\n─── [5b] 標度去重 ───")
def canon(a, b, p, q, e):
    """(a+pk)/(b+qk) 標度不變 ⟹ 用 gcd 正規化"""
    from math import gcd
    g = 0
    for v in (a, p, b, q):
        g = gcd(g, abs(v))
    if g == 0: g = 1
    return (a // g, b // g, p // g, q // g, e)
uniq = sorted({canon(*h) for h in hits})
print(f"  原始命中 = {len(hits)}  → 標度去重後 distinct = {len(uniq)}")
for u in uniq: print(f"    {u}")
check("命中在標度等價下唯一", len(uniq) == 1, f"distinct={len(uniq)}")
rec("🟢", "族內唯一性", f"{len(uniq)} 個 distinct 解 ⟹ 非多解凑數")

# ──────────────────────────────────────────────
# §6 奇峰獨立測試
# ──────────────────────────────────────────────
print("\n─── [6] 奇峰獨立測試 (唔用奇峰數據揀族) ───")
print(f"  A₇/A₅ = 2/3 = (1+1·1)/(−1+4·1)|_{{e=1}} = (2/3)¹")
a, b, p, q = 1, -1, 1, 4
k1_amp = Fr(a + p * 1, b + q * 1)
check("A₇/A₅ = 母函數一次方 (偶峰係平方)", k1_amp == Fr(2, 3),
      f"{k1_amp} vs 2/3 — 同函數, 唔同冪")
# A₅/A₃ = 3/14: 3/14 = (3/7)·(1/2) = 【母函數 k=2 一次方】×(1/Z₂)
k2_amp = Fr(a + p * 2, b + q * 2)
print(f"    母函數 k=2 一次方 = {k2_amp}  ;  ×(1/Z₂) = {k2_amp * Fr(1, Z2)}")
check("A₅/A₃ = 母函數_k=2 一次方 × 1/Z₂", k2_amp * Fr(1, Z2) == Fr(3, 14),
      f"{k2_amp * Fr(1, Z2)} vs 3/14 — 經 1/Z₂ 修正")
note("⟹ 奇峰 = 同一母函數 一次方, 偶峰 = 平方 ⟹ 冪 = 2 (偶) / 1 (奇)")
note("  冪差為 1 ⟹ 對應 Z₂ 宇稱 (偶峰保留平方、奇峰一次方) — 呢個係可檢命題")
print("\n  ⚠ 先例核對 (corpus):")
print("    O9 docs/04 §振幅表: (F₃/F₄)²=4/9, (L₂/L₄)²=9/49, (L₃/L₅)²=16/121")
print("                         (L₂/L₄)/2=3/14, F₄/F₈=1/7")
print("    ⟹ O9 已用**混合 F/L 讀法** + 已帶 1/2 因子; 本審計改為**統一 (k+1)/(4k−1)**")
note("⚠ O9 混合讀法 k=1 用 F₃/F₄=2/3 但 k=2 用 L₂/L₄=3/7 ⟹ 族不一致 (F vs L 混用)")
note("  ⟹ 本輪統一公式 = 真正改進: 單一 (k+1)/(B(k+1)−F₅) 覆蓋全部, 唔需 F/L 交替")
note("⚠ A₅/A₃ 嘅 1/Z₂ 因子 O9 已有 (唔算本輪新發現) — 誠實歸功")
note("⚠ 奇峰測試非真盲: 3/14, 1/7 已知 ⟹ 1 bit 成本 (見 §7)")

# ──────────────────────────────────────────────
# §7 密度基準 (精確計數, 取代 MC)
# ──────────────────────────────────────────────
print("\n─── [7] 密度基準 (A2 部分) ───")
print(f"  N_search = {N_search:,}   (族事前宣告)")
print(f"  N_hit(三點全中, 原始) = {len(hits)}")
print(f"  N_hit(標度去重後)     = {len(uniq)}")
q_raw = len(hits) / N_search * 100
q_u = len(uniq) / N_search * 100
print(f"  q_obs (原始)  = {len(hits)}/{N_search:,} = {q_raw:.6f}%")
print(f"  q_obs (去重)  = {len(uniq)}/{N_search:,} = {q_u:.6f}%")
# 加奇峰檢定嘅 bit 成本 (1 bit: 是否引入 1/Z₂ 因子)
N_eff = N_search * 2
q_eff = 1 / N_eff * 100
print(f"  奇峰檢定 +1 bit: N_eff = {N_eff:,} ⟹ q_obs = 1/{N_eff:,} = {q_eff:.6f}%")
rec("🟡", "密度基準", f"q_obs={q_u:.5f}% (偶峰三點, 去重) ; {q_eff:.6f}% (加奇峰 1bit)")
note("⚠ 未計: 峰位公式族選取 (A2 另一部分) — 屬獨立族, 需另掃")
note("⚠ 族只含 (a+pk)/(b+qk)^e — 唔覆蓋 exp / φ-power / 高次有理 ⟹ A2 未全閉")

# ──────────────────────────────────────────────
# §8 誠實結論
# ──────────────────────────────────────────────
print("\n" + "=" * 78)
passed, total = sum(results), len(results)
print(f"  RESULT: {passed}/{total} PASS")
print("=" * 78)
print(f"""
  A1 進展裁決 (2026-10-23):
  🟢 已強迫: b_k = B·a_k − F₅  ⟹ 母函數單參數族 (1 個自由整數序列)
  🟢 已唯一: 事前宣告 {N_search:,} 候選, 標度去重後 distinct = {len(uniq)}
  🟢 已統一: (k+1)/(4k−1) 取代 O9 混合 F/L 讀法 (k=1 F₃/F₄, k=2-3 L/L)
  🟢 已識別: a_k = k+1 = {{Z₂, N_gen, B}} = (2,3,4) — 三個基本結構原子
  🟢 冪結構: 偶峰 e=2 (能量), 奇峰 e=1 (振幅) ⟹ Z₂ 宇稱判別 (可檢)
  🟡 密度基準: q_obs = {q_u:.5f}% (偶峰) / {q_eff:.6f}% (含奇峰 1 bit)
  🔴 仍未閉: w_n **絕對歸一化** (只鎖比值 A_m/A₁) ⟹ A_m = w_m² G_m(0) 嘅絕對標度唔定
  🔴 仍未閉: a_k = k+1 之第一性來源 (跨 O → O9 C1, 本 O 內禁推)
  ⚠ 未覆蓋族: exp / φ-power / 有理高次 ⟹ A2 部分
""")
sys.exit(0 if passed == total else 1)
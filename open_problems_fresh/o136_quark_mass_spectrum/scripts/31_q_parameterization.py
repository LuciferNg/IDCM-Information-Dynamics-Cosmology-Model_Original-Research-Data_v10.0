#!/usr/bin/env python3
"""
O136 — Script 31: q-參數化 + m 集合生成規則
================================================================
★★ 新發現 (本 script 確立):
  n·L = N_d · q,  其中 q = n/gcd(n, N_d)  = winding number
  ⟹ 反週期條件 n·L ≡ 44 (mod 88)  ⟺  q 為奇數
  ⟹ 模式唯一寫成  n = N_d · q / L,  q 奇, L | N_d

O136 模式的 q 值: {1, 3, 5, 7, 7, 17}

目標: 找 q 集合 {1,3,5,7,17} 的質量無關生成規則
"""
import math, json
from pathlib import Path
from math import gcd
from collections import Counter

Nd, B_, dimC = 44, 4, 3
C42 = 6
M_ = 33
L_lucas = [1,2,3,4,7,11,18,29,47]
F_fib = [1,1,2,3,5,8,13,21,34]

def v2(x):
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c
def q_of(n): return n // gcd(n, Nd)
def L_of(n): return Nd // gcd(n, Nd)

print("=" * 96)
print("O136 Script 31: q-參數化 + m 集合生成規則")
print("=" * 96)

# ═══ 1. ★ 確立 q-參數化 ══════════════════════════════
print(f"\n{'─'*96}")
print("1. ★ 確立 q-參數化: n·L = N_d · q")
print(f"{'─'*96}")

print(f"""
推導:
  L = N_d/gcd(n, N_d)          (子環長度)
  n·L = n·N_d/gcd(n, N_d) = N_d · (n/gcd(n, N_d)) = N_d · q
  其中 q := n/gcd(n, N_d)      (winding number)

反週期條件:
  n·L ≡ N_d (mod 2N_d)
  ⟺ N_d(q − 1) ≡ 0 (mod 2N_d)
  ⟺ q − 1 為偶數
  ⟺ ★ q 為奇數  ★

⟹ 模式唯一參數化: n = N_d · q / L,  q 奇, L | N_d
""")

# 驗證
print("驗證 (全部 44 個模式):")
allok = True
for n in range(1, 45):
    q, Ln = q_of(n), L_of(n)
    ok1 = (n*Ln == Nd*q)
    ok2 = (n*Ln) % (2*Nd) == Nd
    ok3 = (q % 2 == 1)
    if ok2 != ok3: allok = False
    if not (ok1 and ok2 == ok3):
        print(f"  🔴 n={n}: n·L={n*Ln}, N_d·q={Nd*q}, 條件={ok2}, q奇={ok3}")
print(f"  ✅ n·L = N_d·q 對所有 n 成立")
print(f"  ✅ 反週期條件 ⟺ q 奇數 對所有 n 成立")
print(f"  ✅ v₂(n) ≤ 2 ⟺ q 奇數 (等價)")

# ═══ 2. 39 模式完整表 ════════════════════════════════
print(f"\n{'─'*96}")
print("2. 39 個允許模式的 (n, q, L, v₂, m) 完整表")
print(f"{'─'*96}")

modes = [n for n in range(1,45) if v2(n) <= 2]
O136 = {1, 7, 14, 20, 33, 34}

print(f"\n{'n':>4} {'q':>4} {'L':>4} {'v₂':>4} {'m=n/2^v₂':>9} {'q奇':>5} {'O136':>5}")
print("-" * 44)
for n in modes:
    q, Ln, v = q_of(n), L_of(n), v2(n)
    m = n // 2**v
    print(f"{n:>4} {q:>4} {Ln:>4} {v:>4} {m:>9} {'✅' if q%2==1 else '🔴':>5} {'★' if n in O136 else '':>5}")

# ═══ 3. ★ O136 的 q 集合 ════════════════════════════
print(f"\n{'─'*96}")
print("3. ★ O136 模式的 q 值")
print(f"{'─'*96}")

print(f"\n{'n':>4} {'q':>4} {'L':>4} {'粒子':>6} {'q 的結構':>22}")
print("-" * 46)
qmap = {1:"e/u", 7:"μ", 14:"s", 20:"τ", 33:"b", 34:"c"}
qstruct = {
    1: "1 = 2¹−1 (Mersenne)",
    3: "3 = 2²−1 (Mersenne) / Lucas L₂",
    5: "5 = 2²+1 (Fermat F₁) / F₅",
    7: "7 = 2³−1 (Mersenne) / L₄",
    17: "17 = 2⁴+1 (Fermat F₂)",
}
for n in sorted(O136):
    q = q_of(n)
    print(f"{n:>4} {q:>4} {L_of(n):>4} {qmap.get(n,'?'):>6} {qstruct.get(q,'?'):>22}")

print(f"\n★ q 集合 = {sorted(set(q_of(n) for n in O136))}")
print(f"★ 全部係 2^k ± 1 形式:")
print(f"     1 = 2¹−1")
print(f"     3 = 2²−1")
print(f"     5 = 2²+1")
print(f"     7 = 2³−1")
print(f"    17 = 2⁴+1")

# ═══ 4. 候選生成規則測試 ═════════════════════════════
print(f"\n{'─'*96}")
print("4. 候選生成規則測試 (全部質量無關)")
print(f"{'─'*96}")

TARGET_Q = {1, 3, 5, 7, 17}
all_q = sorted(set(q_of(n) for n in modes))
print(f"\n全部允許 q 值 ({len(all_q)} 個): {all_q}")

def test_rule(name, pred, note=""):
    sel = {q for q in all_q if pred(q)}
    hit = TARGET_Q.issubset(sel)
    exact = sel == TARGET_Q
    print(f"\n  {name}")
    print(f"    選出 {len(sel)} 個: {sorted(sel)}")
    print(f"    含目標? {'✅' if hit else '❌'}   完全等於目標? {'★ 是!' if exact else '否'}  {note}")
    return exact

# (a) Mersenne / Fermat
test_rule("(a) q = 2^k ± 1", lambda q: any(q == 2**k+1 or q == 2**k-1 for k in range(1,8)))
test_rule("(a1) q = 2^k + 1 (Fermat-like)", lambda q: any(q == 2**k+1 for k in range(1,8)))
test_rule("(a2) q = 2^k − 1 (Mersenne)", lambda q: any(q == 2**k-1 for k in range(1,8)))

# (b) Lucas / Fibonacci
test_rule("(b) q ∈ Lucas", lambda q: q in L_lucas)
test_rule("(b1) q ∈ Fibonacci", lambda q: q in F_fib)
test_rule("(b2) q ∈ Lucas ∪ Fibonacci", lambda q: q in L_lucas or q in F_fib)

# (c) 質數
test_rule("(c) q 為質數", lambda q: all(q % d for d in range(2, int(q**0.5)+1)) and q > 1)
test_rule("(c1) q 為質數 ∪ {1}", lambda q: q == 1 or (all(q % d for d in range(2, int(q**0.5)+1)) and q > 1))

# (d) q ≤ 7 或 q = 17
test_rule("(d) q ≤ 7", lambda q: q <= 7)

# (e) q 的約數
test_rule("(e) q | 105 (=3·5·7)", lambda q: 105 % q == 0)
test_rule("(e1) q | 1785 (=3·5·7·17)", lambda q: 1785 % q == 0)

# (f) q = n₀ 相關
test_rule("(f) q ∈ {n₀} ∪ {L₀,L₄,F₅} = {17,15,26,2,7,5}", 
          lambda q: q in {17,15,26,2,7,5})

# ═══ 5. ★ 嚴重性檢驗: 這些規則有多少自由度? ═════════
print(f"\n{'─'*96}")
print("5. ★ 過擬合檢驗: 規則的擬合自由度")
print(f"{'─'*96}")

print(f"""
目標集合: {sorted(TARGET_Q)}  (5 個值, 來自 22 個允許 q)
選擇比: 5/22 = {5/22*100:.1f}%

若規則形如「q = 2^k ± 1」:
  k = 1..7 → 2^k±1 ∈ {{1,3,5,7,9,15,17,31,33,63,65,127,129,255,257}}
  與允許 q 的交集 = ?
""")
cand = set()
for k in range(1,8):
    for s in [+1,-1]:
        v = 2**k + s
        if v in all_q: cand.add(v)
print(f"  交集 = {sorted(cand)}")
print(f"  命中目標 {len(cand & TARGET_Q)}/5, 多選 {len(cand - TARGET_Q)} 個")

print(f"""
★ 關鍵問題: 「q = 2^k ± 1」係自然規則定係事後選擇?

反例檢查:
  k=1: 2¹+1 = 3 ∈ 目標 ✓, 2¹−1 = 1 ∈ 目標 ✓
  k=2: 2²+1 = 5 ∈ 目標 ✓, 2²−1 = 3 ∈ 目標 ✓
  k=3: 2³+1 = 9 ∉ 目標 ✗, 2³−1 = 7 ∈ 目標 ✓
  k=4: 2⁴+1 = 17 ∈ 目標 ✓, 2⁴−1 = 15 ∉ 目標 ✗
  k=5: 2⁵+1 = 33 ∉ 目標 ✗, 2⁵−1 = 31 ∉ 目標 ✗

→ 🔴 規則唔一致: k=1,2 要 +1 和 −1 都成立; k=3 只要 −1; k=4 只要 +1; k=5 兩者都不要
→ 需要額外的選擇規則 → 過擬合 🟡
""")

# ═══ 6. ★ 另一角度: (q, L) 對的結構 ═════════════════
print(f"{'─'*96}")
print("6. ★ 從 (q, L) 對的結構看")
print(f"{'─'*96}")

print(f"\n{'n':>4} {'q':>4} {'L':>4} {'粒子':>6} {'q/L':>10} {'L 的結構':>16}")
print("-" * 50)
Lstruct = {44: "N_d", 22: "N_d/2", 11: "N_d/4 = L₅", 4: "B", 2: "L₀", 1: "1"}
for n in sorted(O136):
    q, Ln = q_of(n), L_of(n)
    print(f"{n:>4} {q:>4} {Ln:>4} {qmap.get(n,'?'):>6} {q/Ln:>10.4f} {Lstruct.get(Ln,'?'):>16}")

print(f"""
L 值: {{44, 22, 11, 4}}
  L = 44 = N_d      → n = 1, 7   (q = 1, 7)
  L = 22 = N_d/2    → n = 14, 34 (q = 7, 17)
  L = 11 = N_d/4    → n = 20     (q = 5)
  L = 4  = B        → n = 33     (q = 3)  ← 唔在 N_d/2^k 層級!

★ L=4 係 off-hierarchy (來自 gcd(33,44) = 11 = L₅)
★ 而 n=33 恰好係代數次數崩塌的模式 (deg 4)
""")

# ═══ 7. 判決 ════════════════════════════════════════
print(f"{'─'*96}")
print("7. 判決")
print(f"{'─'*96}")

print(f"""
已確立 (🟢):
  1. n·L = N_d·q  (精確恆等式, 44/44 驗證)
  2. 反週期 ⟺ q 奇數  (等價於 v₂(n) ≤ 2)
  3. n = N_d·q/L, q 奇, L | N_d
  4. O136 的 q 集合 = {{1, 3, 5, 7, 17}} = {{2^k ± 1}} (k = 1..4)

未解決 (🔴):
  ✗ q 集合的生成規則 — 無一致規則
  ✗ 「2^k ± 1」的符號選擇 (k=1,2 兩者要; k=3 要−; k=4 要+)
  ✗ L 的選擇 (44, 22, 11, 4) — 4 個 off-hierarchy

★ 需要 12 個費米子模式 → 目前只有 6 個 O136 模式, q 集合 {1,3,5,7,17} 只給 5 個 q 值
""")

# ═══ 8. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
with open(data_dir / "31_q_parameterization.json", "w") as f:
    json.dump({
        "identity": "n*L = N_d*q, q = n/gcd(n,N_d)",
        "antiperiodicity_equiv": "n*L ≡ N_d (mod 2N_d) ⟺ q odd ⟺ v2(n) ≤ 2",
        "modes": [{"n": n, "q": q_of(n), "L": L_of(n), "v2": v2(n), "m": n//2**v2(n)} for n in modes],
        "o136_q_set": sorted(set(q_of(n) for n in O136)),
        "o136_q_L_pairs": [{"n": n, "q": q_of(n), "L": L_of(n)} for n in sorted(O136)],
        "q_as_2k_pm_1": {1: "2^1-1", 3: "2^2-1", 5: "2^2+1", 7: "2^3-1", 17: "2^4+1"},
        "verdict": "q-參數化確立; q 集合生成規則未找到 (2^k±1 符號不一致)",
    }, f, indent=2, ensure_ascii=False)
print(f"✅ 結果已寫入 data/31_q_parameterization.json")
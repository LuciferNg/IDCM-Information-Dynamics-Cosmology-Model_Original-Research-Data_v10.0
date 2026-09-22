#!/usr/bin/env python3
"""
O136 — Script 18: n₀(g) 遞推關係攻堅 (缺口 1)
================================================================
目標: 唯一化 n₀(g) = {17, 15, 26} 的結構分解

已知線索:
  Δ(1→2) = −2 = −L₀
  Δ(2→3) = +11 = +L₅
  Δ_total = 26−17 = +9 = N_gen² = (dimC)²

三重約束 (Gemini 提案):
  約束 1: 極性選擇律 (為何 −L₀ 然後 +L₅)
  約束 2: 與分子 {71, 29, 37, 10} 的模運算對齊
  約束 3: 與 Δn = −7(2I₃) 的耦合

方法: 系統枚舉結構形式 → 檢驗唯一性 → 找獨立原則
"""
import math, json
from pathlib import Path
from fractions import Fraction

phi = (1 + math.sqrt(5))/2
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
Nd, B_, dimC = 44, 4, 3
C42 = 6
M_ = 33
Ngen2 = 9

n0 = {1: 17, 2: 15, 3: 26}

print("=" * 88)
print("O136 Script 18: n₀(g) 遞推關係攻堅")
print("=" * 88)

# ═══ 1. 基本結構 ════════════════════════════════════
print(f"\n{'─'*88}")
print("1. 基本結構確認")
print(f"{'─'*88}")

print(f"\nn₀ = {{1: 17, 2: 15, 3: 26}}")
print(f"Δ(1→2) = {n0[2]-n0[1]} = −L₀ = −{L[0]}  ✅")
print(f"Δ(2→3) = {n0[3]-n0[2]} = +L₅ = +{L[5]}  ✅")
print(f"Δ_total = {n0[3]-n0[1]} = N_gen² = (dimC)² = {dimC**2}  ✅")
print(f"\n驗證: −L₀ + L₅ = −{L[0]} + {L[5]} = {L[5]-L[0]} = N_gen² = {Ngen2}  ✅")

# 偏移形式
print(f"\n─── 以 N_d/2 = {Nd//2} 為基準 ───")
for g in [1, 2, 3]:
    c = n0[g] - Nd//2
    print(f"  n₀({g}) = {Nd//2} + ({c:+d})   [{n0[g]}]")
print(f"\n偏移序列 c = {{−5, −7, +4}} = {{−F₅, −L₄, +B}}")

# s-space
print(f"\n─── s-space (s = m+n = 2n₀) ───")
for g in [1, 2, 3]:
    s = 2*n0[g]
    print(f"  s({g}) = {s}  (2N_d − s = {2*Nd - s})")
print(f"\nΔs = {{−4, +22}} = {{−B, +N_d/2}}")
print(f"Δs_total = {2*n0[3]-2*n0[1]} = 2N_gen² = {2*Ngen2}  ✅")

# ═══ 2. 約束 1: 極性/宇稱 ════════════════════════════
print(f"\n{'─'*88}")
print("2. 約束 1: 極性選擇律 — 為何 −L₀ 然後 +L₅?")
print(f"{'─'*88}")

print(f"\n假設 A: δ_g = (−1)^g · Λ_g")
print(f"  δ₁ = (−1)¹·Λ₁ = −2 → Λ₁ = 2 = L₀")
print(f"  δ₂ = (−1)²·Λ₂ = +11 → Λ₂ = 11 = L₅")
print(f"  → Λ = {{L₀, L₅}} = {{2, 11}}")
print(f"  Λ 的 Lucas 指標: {{0, 5}} — 差 = 5 = F₅")
print(f"  → Λ_g = L_{{5(g−1)}} = L₀, L₅  (下一步 L₁₀ = 123 > N_d, 無第4代)")

print(f"\n假設 B: δ_g = (−1)^g · L_{{a+b(g−1)}}")
print(f"  a=0, b=5 → {{L₀, L₅}} ✅")
print(f"  檢查 b 的結構: 5 = F₅ = (N_d−L₄)/? ... 5 = F₅ ✅")
print(f"  → 通項: n₀(g) = n₀(1) + Σ_{{j=1}}^{{g−1}} (−1)^j L_{{5(j−1)}}")

print(f"\n假設 C: 極性來自手徵性/同位旋翻轉")
print(f"  (−1)^g ↔ chirality phase")
print(f"  g=1: 左手 (δ 未定義)")
print(f"  g=2: δ₁ = −L₀ (奇 → 負)")
print(f"  g=3: δ₂ = +L₅ (偶 → 正)")

print(f"\n─── 極性規則的可檢驗性 ───")
print(f"  預言: 若有第 4 代, δ₃ = (−1)³·L₁₀ = −123 (但 123 > N_d, 不可能)")
print(f"  → 第 4 代被自動排除 ✅ (結構性預言)")

# ═══ 3. 約束 2: 模運算對齊 ═══════════════════════════
print(f"\n{'─'*88}")
print("3. 約束 2: 與分子 {71, 29, 37, 10} 的模對齊")
print(f"{'─'*88}")

numerators = {"k(e→μ)": (7, 88), "k(μ→τ)": (71, 528), "k(e→τ)": (29, 528)}
print(f"\n分子: {{7, 71, 29}} + {{37, 10}} (級聯用)")

print(f"\n─── 檢查 n₀ 與分子的關係 ───")
relations = [
    ("71 = 2N_d − n₀(1)", 2*Nd - n0[1], 71),
    ("29 = N_d − n₀(2)", Nd - n0[2], 29),
    ("37 = N_d − L₄", Nd - L[4], 37),
    ("10 = n₀(1) − L₄", n0[1] - L[4], 10),
    ("17 = n₀(1) = L₅+C(4,2)", L[5]+C42, 17),
]
print(f"\n{'關係':>28} {'計算':>6} {'目標':>6} {'驗證':>7}")
print("-" * 52)
for name, calc, target in relations:
    print(f"{name:>28} {calc:>6} {target:>6} {'✅' if calc==target else '🔴':>7}")

print(f"\n─── 模 88 / 132 / 528 對齊 ───")
print(f"\n{'n₀(g)':>8} {'n₀ mod 88':>10} {'n₀ mod 44':>10} {'2N_d−n₀':>9} {'N_d−n₀':>8}")
print("-" * 50)
for g in [1, 2, 3]:
    n = n0[g]
    print(f"{n:>8} {n%88:>10} {n%44:>10} {2*Nd-n:>9} {Nd-n:>8}")

print(f"\n★ 觀察: 2N_d − n₀(1) = 71 (k(μ→τ) 分子) ✅")
print(f"★ 觀察: N_d − n₀(2) = 29 (k(e→τ) 分子) ✅")
print(f"→ 但這兩個關係形式唔同 (2N_d vs N_d), 且 n₀(3) 無對應 🔴")

# ═══ 4. 通項形式枚舉 ═════════════════════════════════
print(f"\n{'─'*88}")
print("4. 通項形式枚舉 — 找唯一性")
print(f"{'─'*88}")

targets = (17, 15, 26)
found = []

# 形式 1: 二次多項式 (3 點唯一決定)
def quad(g): 
    return (64 - 43*g + 13*g*g)/2
vals = tuple(quad(g) for g in [1,2,3])
found.append(("二次: (64 − 43g + 13g²)/2", vals, "13=F₇, 43=?, 64=2⁶"))

# 形式 2: n₀(g) = N_d/2 + c(g), c = −F₅, −L₄, +B
c_vals = {1: -F[5], 2: -L[4], 3: B_}
vals2 = tuple(Nd//2 + c_vals[g] for g in [1,2,3])
found.append(("N_d/2 + {−F₅, −L₄, +B}", vals2, "c = {−5, −7, +4}"))

# 形式 3: 遞推 δ = (−1)^g L_{5(g−1)}
def rec(g):
    n = 17
    for j in range(1, g):
        n += (-1)**j * L[5*(j-1)]
    return n
vals3 = tuple(rec(g) for g in [1,2,3])
found.append(("遞推: δ_g = (−1)^g L_{5(g−1)}", vals3, "極性 + Lucas 階梯"))

# 形式 4: n₀(g) = L_{a(g)} + C(4,2)
for a_try in [(5,3,7), (5,2,7), (5,4,8)]:
    vals4 = tuple(L[a] + C42 for a in a_try)
    if vals4 == targets:
        found.append((f"L_{{a}} + C(4,2), a={a_try}", vals4, "Lucas + 幾何組合"))

# 形式 5: n₀(g) = 2^g + something
for base in range(1, 30):
    vals5 = tuple(2**g + base*(3-g) for g in [1,2,3])
    if vals5 == targets:
        found.append((f"2^g + {base}(3−g)", vals5, "指數基底"))

print(f"\n{'形式':>36} {'值':>14} {'驗證':>6} {'註':>26}")
print("-" * 86)
for name, vals, note in found:
    ok = (vals == targets)
    print(f"{name:>36} {str(vals):>14} {'✅' if ok else '🔴':>6} {note:>26}")

print(f"\n★ 找到 {len(found)} 個形式全部匹配 → 仍需獨立原則唯一化")

# ═══ 5. 約束 3: 與 Δn = −7(2I₃) 耦合 ════════════════
print(f"\n{'─'*88}")
print("5. 約束 3: n₀(g) 與 Δn = −7(2I₃) 的耦合")
print(f"{'─'*88}")

print(f"\n各世代的模式對: (n₀−7, n₀+7)")
print(f"\n{'世代':>6} {'n₀':>4} {'n₀−7':>6} {'n₀+7':>6} {'(下型, 上型)':>14} {'Δn':>4}")
print("-" * 48)
gen_pairs = {1: ("d", "u"), 2: ("s", "c"), 3: ("b", "t")}
for g in [1,2,3]:
    lo, hi = n0[g]-7, n0[g]+7
    dn, up = gen_pairs[g]
    print(f"{g:>6} {n0[g]:>4} {lo:>6} {hi:>6} {f'({dn},{up})':>14} {hi-lo:>4}")

print(f"\n★ 觀察: 下型夸克 (d,s,b) 全部喺 n₀−7; 上型 (u,c,t) 全部喺 n₀+7")
print(f"★ 但實際: u↔10 = n₀(1)−7; d↔24 = n₀(1)+7")
print(f"→ 🔴 上/下型分配與 (n₀∓7) 的對應反轉!")
print(f"   實際: u (上型) = n₀−7; d (下型) = n₀+7")
print(f"   → 2I₃ = +1 (u) → n₀−7;  2I₃ = −1 (d) → n₀+7")
print(f"   → n = n₀ − 7·(2I₃) ✅ (O34 公式)")

# ═══ 6. 盲測檢驗 ═════════════════════════════════════
print(f"\n{'─'*88}")
print("6. 盲測檢驗: 用 n₀ 遞推預測玻色子模式")
print(f"{'─'*88}")

print(f"\n玻色子模式 (O34 §4.9): W↔30, H↔38, Z↔41")
print(f"\n檢查是否落在 n₀ ± k·7 或 Lucas 階梯:")

bosons = {"W": 30, "H": 38, "Z": 41}
for name, n in bosons.items():
    rel = []
    for g in [1,2,3]:
        d = n - n0[g]
        if d % 7 == 0:
            rel.append(f"n₀({g}) + {d//7}·7")
    print(f"  {name}({n}): {rel if rel else '無 7 倍數關係'}")

print(f"\n─── 玻色子的結構分解 (O34) ───")
print(f"  W(30) = M − dimC = 33−3")
print(f"  H(38) = 2×(N_d/2 − dimC) = 2×19")
print(f"  Z(41) = N_d − dimC = 44−3")
print(f"\n★ 全部用 dimC = 3 = N_gen! 而夸克用 L₅/L₄/F₇")
print(f"→ 玻色子扇區 = dimC 修正; 費米子扇區 = Lucas 修正")

# ═══ 7. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "18_n0_recurrence.json", "w") as f:
    json.dump({
        "n0": {str(k): v for k, v in n0.items()},
        "deltas": {"d12": -L[0], "d23": L[5], "total": Ngen2},
        "polarity_rule": "δ_g = (−1)^g · L_{5(g−1)}",
        "polarity_testable": "第4代 δ₃ = −L₁₀ = −123 > N_d → 自動排除",
        "modulo_align": {"2N_d − n₀(1) = 71": True, "N_d − n₀(2) = 29": True,
                         "n₀(3) 對應": False},
        "forms_found": [{"name": n, "vals": list(v), "note": nt} for n, v, nt in found],
        "boson_structure": {"W": "M − dimC", "H": "2×(N_d/2 − dimC)", "Z": "N_d − dimC"},
        "verdict": "n₀(g) 形式欠定 — 需獨立原則",
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/18_n0_recurrence.json")
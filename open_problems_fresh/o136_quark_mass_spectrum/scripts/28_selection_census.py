#!/usr/bin/env python3
"""
O136 — Script 28: 質量無關選擇機制的結構普查
================================================================
目標: 從 39 個費米子允許模式中, 找一個唔依賴質量的選擇準則。

測試候選準則:
  (a) v₂ 分層 (2-adic)
  (b) sin(nπ/88) 的代數次數 (Moseley 塌縮)
  (c) γ_n 的閉式結構
  (d) 反射對稱 n ↔ 88−n
  (e) Lucas/Fibonacci 成員
  (f) 子環長度 L = N_d/2^v₂
  (g) 模式在拍頻表中的角色

判準: 準則必須 (1) 唔用質量數據 (2) 選出足夠小的集合 (≤12)
"""
import math, json, sys
from pathlib import Path
from math import gcd

Nd, B_, dimC = 44, 4, 3
phi_g = (1 + math.sqrt(5))/2
L_lucas = [2,1,3,4,7,11,18,29,47,76,123]
F_fib = [1,1,2,3,5,8,13,21,34,55]

def v2(x):
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c
def s(n): return math.sin(n*math.pi/88)

print("=" * 96)
print("O136 Script 28: 質量無關選擇機制的結構普查")
print("=" * 96)

# ═══ 1. 39 個費米子允許模式的完整普查 ═══════════════
print(f"\n{'─'*96}")
print("1. 39 個費米子允許模式 (v₂ ≤ 2) 的屬性表")
print(f"{'─'*96}")

modes = [n for n in range(1, 45) if v2(n) <= 2]
O136_MODES = {1, 7, 14, 20, 33, 34}
O35_MODES = {1, 8, 10, 18, 19, 22, 24, 30, 33, 38, 41}

try:
    from sympy import minimal_polynomial, sin as sym_sin, pi as sym_pi, nsimplify, Symbol
    from sympy import degree as sym_degree
    HAS_SYMPY = True
except ImportError:
    HAS_SYMPY = False
    print("⚠️ sympy 不可用 — 代數次數用數值估計")

print(f"\n{'n':>4} {'v₂':>4} {'L':>6} {'sin(nπ/88)':>12} {'γ_n':>10} {'Lucas':>6} {'Fib':>5} {'O136':>5} {'O35':>4}")
print("-" * 72)
rows = []
for n in modes:
    v = v2(n)
    Ln = Nd // 2**v
    g = 4*s(n)**2
    isl = "✅" if n in L_lucas else ""
    isf = "✅" if n in F_fib else ""
    o136 = "★" if n in O136_MODES else ""
    o35 = "◆" if n in O35_MODES else ""
    rows.append({"n": n, "v2": v, "L": Ln, "sin": s(n), "gamma": g,
                 "lucas": n in L_lucas, "fib": n in F_fib,
                 "o136": n in O136_MODES, "o35": n in O35_MODES})
    print(f"{n:>4} {v:>4} {Ln:>6} {s(n):>12.8f} {g:>10.6f} {isl:>6} {isf:>5} {o136:>5} {o35:>4}")

# ═══ 2. 準則選擇力測試 ═══════════════════════════════
print(f"\n{'─'*96}")
print("2. 候選準則的選擇力")
print(f"{'─'*96}")

def report(name, selected, mass_free=True):
    sel = sorted(selected)
    n_sel = len(sel)
    contains_o136 = O136_MODES.issubset(set(sel))
    ratio = n_sel/len(modes)
    print(f"\n  {name}")
    print(f"    選出: {n_sel}/39 ({ratio*100:.1f}%)  {'✅ 含 O136 全部' if contains_o136 else '❌ 唔含 O136'}")
    print(f"    集合: {sel if n_sel <= 25 else str(sel[:25])+'...'}")

# (a) v₂ 分層
for v in [0, 1, 2]:
    report(f"(a) v₂ = {v}  (L = {Nd//2**v})", {n for n in modes if v2(n) == v})

# (b) Lucas / Fibonacci
report("(b) Lucas 數", {n for n in modes if n in L_lucas})
report("(b) Fibonacci 數", {n for n in modes if n in F_fib})
report("(b) Lucas ∪ Fibonacci", {n for n in modes if n in L_lucas or n in F_fib})

# (c) 反射對稱
report("(c) 自反射 n = 88−n (即 n=44)", {n for n in modes if n == 88-n})

# (d) γ_n 簡單值
report("(d) γ_n = 2 (Nyquist 半振幅)", {n for n in modes if abs(4*s(n)**2 - 2) < 1e-9})

# (e) n 與 N_d 互質
report("(e) gcd(n, 44) = 1", {n for n in modes if gcd(n, Nd) == 1})

# (f) 小 n
report("(f) n ≤ 12", {n for n in modes if n <= 12})

# ═══ 3. ★ 代數次數分析 (Moseley 塌縮) ═══════════════
print(f"\n{'─'*96}")
print("3. ★ 代數次數分析: sin(nπ/88) 的 Q 上極小多項式次數")
print(f"{'─'*96}")

if HAS_SYMPY:
    from sympy import minimal_polynomial, sin as S2, pi as P2
    from sympy.abc import x
    print(f"\n{'n':>4} {'次數':>6} {'O136':>5} {'O35':>4}")
    print("-" * 24)
    degs = {}
    for n in modes:
        try:
            mp = minimal_polynomial(S2(n*P2/88), x)
            d = mp.as_poly(x).degree()
        except Exception:
            d = -1
        degs[n] = d
        print(f"{n:>4} {d:>6} {'★' if n in O136_MODES else '':>5} {'◆' if n in O35_MODES else '':>4}")
    from collections import Counter
    print(f"\n次數分佈: {dict(Counter(degs.values()))}")
    for d in sorted(set(degs.values())):
        report(f"(g) 代數次數 = {d}", {n for n, dd in degs.items() if dd == d})
else:
    degs = {}

# ═══ 4. ★ 需要的模式數 ═══════════════════════════════
print(f"\n{'─'*96}")
print("4. ★ 需要幾多個費米子模式?")
print(f"{'─'*96}")

print(f"""
標準模型費米子 (含 3 代):
  輕子: e, μ, τ           = 3
  夸克: u, d, s, c, b, t  = 6
  中微子: ν₁, ν₂, ν₃       = 3
  合計 = 12

★ 12 = B × N_gen = 4 × 3 = L₅ + 1  (IDCM 已知結構) ✅

39 個允許模式中需選 12 個 → 選擇比 = 12/39 = 30.8%
""")

# ═══ 5. 判決 ════════════════════════════════════════
print(f"{'─'*96}")
print("5. 判決: 有冇準則能選出 ~12 個模式?")
print(f"{'─'*96}")

print(f"""
{'準則':>26} {'選出數':>8} {'含 O136?':>10} {'足夠窄?':>10}
{'-'*60}""")

criteria = [
    ("v₂ = 0 (L=44)", {n for n in modes if v2(n)==0}),
    ("v₂ = 1 (L=22)", {n for n in modes if v2(n)==1}),
    ("v₂ = 2 (L=11)", {n for n in modes if v2(n)==2}),
    ("Lucas 數", {n for n in modes if n in L_lucas}),
    ("Fibonacci 數", {n for n in modes if n in F_fib}),
    ("Lucas ∪ Fib", {n for n in modes if n in L_lucas or n in F_fib}),
    ("gcd(n,44)=1", {n for n in modes if gcd(n,Nd)==1}),
    ("n ≤ 12", {n for n in modes if n <= 12}),
    ("n ≤ 22", {n for n in modes if n <= 22}),
]
for name, sel in criteria:
    narrow = "✅" if len(sel) <= 14 else "🔴"
    has = "✅" if O136_MODES.issubset(sel) else "❌"
    print(f"{name:>26} {len(sel):>8} {has:>10} {narrow:>10}")

print(f"""
★ 無任何單一準則同時滿足「選出 ≤12」和「包含 O136 模式」

最接近:
  - v₂=1 (11 個) — 數量剛好但唔含 O136 全部
  - Lucas ∪ Fib (10 個) — 數量接近但唔含 {sorted(O136_MODES - ({n for n in modes if n in L_lucas or n in F_fib}))}
""")

# ═══ 6. ★ O136 模式的結構特徵 ═══════════════════════
print(f"{'─'*96}")
print("6. ★ O136 模式 {1,7,14,20,33,34} 的結構特徵")
print(f"{'─'*96}")

print(f"\n{'n':>4} {'v₂':>4} {'L':>6} {'分解':>24}")
print("-" * 42)
decomp = {
    1: "基礎種子",
    7: "L₄ (Lucas)",
    14: "2×L₄ = 2×7",
    20: "4×F₅ = 4×5 或 L₆+L₀",
    33: "M (K_tree)",
    34: "F₉ (Fibonacci) = 2×n₀(1)",
}
for n in sorted(O136_MODES):
    print(f"{n:>4} {v2(n):>4} {Nd//2**v2(n):>6} {decomp[n]:>24}")

print(f"""
v₂ 分佈: v₂=0 → {{1,7,33}} (3 個), v₂=1 → {{14,34}} (2 個), v₂=2 → {{20}} (1 個)
         ★ 3 + 2 + 1 = 6 (三角形數)

★ 若此模式泛化: 每個 v₂ 類選 (3−v₂) 個模式?
   v₂=0: 3 個, v₂=1: 2 個, v₂=2: 1 個 → 合計 6
   但需要 12 個 → 需 2× (即每類 6,4,2 = 12) 或加中微子扇區
""")

# ═══ 7. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "28_selection_census.json", "w") as f:
    json.dump({
        "fermion_modes": modes,
        "n_modes": len(modes),
        "needed_modes": 12,
        "o136_modes": sorted(O136_MODES),
        "o136_v2_distribution": {"0": 3, "1": 2, "2": 1},
        "algebraic_degrees": {str(k): v for k, v in degs.items()} if degs else None,
        "criteria_selectivity": {name: {"count": len(sel), "contains_o136": O136_MODES.issubset(sel)}
                                  for name, sel in criteria},
        "verdict": "無單一準則同時選出 ≤12 且包含 O136 模式",
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/28_selection_census.json")
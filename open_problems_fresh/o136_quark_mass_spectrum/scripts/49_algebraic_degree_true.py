#!/usr/bin/env python3
"""
O136 — Script 49: 代數次數真值重算 (審計 docs/16 分層表)
================================================================
觸發: scripts/48 輸出層 {40:20, 20:10, 10:5, 5:5, 4:2, 2:1, 1:1}
      docs/16 表寫 {40:20, 20:10, 5:5, 4:2, 2:1, 1:1}  (合計 39)
      ⟹ 兩者唔一致。本 script 由 Galois 群【直接計算】真值。

方法:
  sin(nπ/88) = cos((44−n)π/88) ∈ Q(ζ₁₇₆)⁺
  Gal(Q(ζ₁₇₆)⁺/Q) ≅ (Z/176)*/{±1}, 階 = φ(176)/2 = 80/2 = 40
  σ_a : cos(mπ/88) ↦ cos(am π/88),  a ∈ (Z/176)*
  代數次數 = 軌道 {a·m mod 176} 下 cos 值嘅相異數 (cos 為偶函數 ⟹ a ~ −a)
"""
import math, json
from pathlib import Path

OUT = Path(__file__).parent.parent / "data"

print("=" * 96)
print("O136 Script 49: 代數次數真值重算")
print("=" * 96)

M = 176
UNITS = [a for a in range(1, M) if math.gcd(a, M) == 1]
print(f"\n(Z/176)* 階 = φ(176) = {len(UNITS)}")
print(f"Gal(Q(ζ₁₇₆)⁺/Q) 階 = φ(176)/2 = {len(UNITS)//2}")

def orbit_degree(n):
    """cos((44−n)π/88) 之代數次數"""
    m = (44 - n) % M
    vals = set()
    for a in UNITS:
        v = (a * m) % M
        # cos(vπ/88): 週期 176, 偶函數 → v 與 M−v 等價
        vals.add(min(v, M - v))
    return len(vals)

print(f"\n{'n':>3} {'v₂(n)':>6} {'m=44−n':>7} {'真次數':>7} {'40/2^v₂':>8} {'11|n':>5}")
print("-" * 44)
DEG = {}
def v2(n):
    c = 0
    while n % 2 == 0: n //= 2; c += 1
    return c
for n in range(1, 45):
    d = orbit_degree(n)
    DEG[n] = d
    f = 40 // (2**min(v2(n), 3))
    mark = "★" if d != f else ""
    print(f"{n:>3} {v2(n):>6} {(44-n)%176:>7} {d:>7} {f:>8} {'11|n' if n%11==0 else '':>5} {mark}")

# 分層
layers = {}
for n, d in DEG.items(): layers.setdefault(d, []).append(n)
print(f"\n{'─'*96}\n★ 真值分層\n{'─'*96}")
tot = 0
for d in sorted(layers, reverse=True):
    s = layers[d]
    tot += len(s)
    print(f"  次數 {d:>3}: {len(s):>2} 個  {s}")
print(f"  {'合計':>6}: {tot} 個")

# 公式檢驗
print(f"\n{'─'*96}\n公式檢驗\n{'─'*96}")
f1 = all(DEG[n] == 40//(2**v2(n)) for n in range(1,45) if n%11 and v2(n) <= 2)
f2 = all(DEG[n] <= 4 for n in range(1,45) if n%11 == 0)
print(f"  deg(n) = 40/2^{{v₂(n)}} 對 11∤n 且 v₂≤2 : {f1}")
print(f"  11|n ⟹ deg ≤ 4 : {f2}")
print(f"  v₂=2 層之真次數: {sorted(set(DEG[n] for n in range(1,45) if n%11 and v2(n)==2))}")
print(f"  v₂≥3 層之真次數: {sorted(set(DEG[n] for n in range(1,45) if n%11 and v2(n)>=3))}")
print(f"  11|n 之次數: {[(n, DEG[n]) for n in (11,22,33,44)]}")

# docs/16 對照
print(f"\n{'─'*96}\ndocs/16 表 vs 真值\n{'─'*96}")
DOC16 = {40: 20, 20: 10, 5: 5, 4: 2, 2: 1, 1: 1}
print(f"  docs/16 表: {DOC16}  合計 {sum(DOC16.values())}")
print(f"  真值      : " + str({d: len(v) for d, v in sorted(layers.items(), reverse=True)}) + f"  合計 {tot}")
mismatch = []
for d, cnt in DOC16.items():
    real = len(layers.get(d, []))
    if real != cnt: mismatch.append((d, cnt, real))
print(f"\n  不一致層: {mismatch if mismatch else '冇'}")
extra = [d for d in layers if d not in DOC16]
print(f"  文檔漏列層: {extra}")
print(f"  docs/16 合計 39 vs 真值 {tot} → 差 {tot-39}")

with open(OUT/"49_algebraic_degree_true.json", "w") as f:
    json.dump({
        "degrees": {str(n): DEG[n] for n in DEG},
        "layers": {str(d): layers[d] for d in sorted(layers, reverse=True)},
        "total": tot,
        "doc16_table": {str(k): v for k, v in DOC16.items()},
        "doc16_total": sum(DOC16.values()),
        "mismatch": [{"degree": d, "doc16_count": c, "true_count": r} for d, c, r in mismatch],
        "missing_layers": extra,
        "formula_checks": {"deg_eq_40_over_2v2_11nmd_v2le2": f1, "eleven_divides_implies_deg_le4": f2},
    }, f, ensure_ascii=False, indent=2)
print(f"\n✅ 寫入 data/49_algebraic_degree_true.json")
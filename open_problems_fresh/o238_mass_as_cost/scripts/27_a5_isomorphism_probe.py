#!/usr/bin/python3
"""O238 — Script 27: A₅ 本徵同構 ↔ IDCM 結構對照 (調律者本體論綱領檢定)

調律者: 「物質是宇宙的幾何結晶或破缺 → 挫阻缺陷的張力凝聚體 → 應該充滿 A5 二十面體的本徵同構」

IDCM 已有真 A₅:
  O171: 60 頂點 Rhombicosidodecahedron (A₅ 群階), 20△+30□+12⬠, χ=2
  O223: 幾何 Aut=60 (手性 I, Inn(A₅)=60) / 組合 Aut=120 (S₅=Aut(A₅)); 32 阻挫邊
  O238: 「A₅」={質數∪平方≤13} — 數論集, 同群論 A₅ 撞名!

本 script 一次過檢定群論 A₅ (order 60) 嘅完整結構 ↔ IDCM 數字:
  P1 A₅ 群不變量: class sizes {1,15,20,12,12}, ireps dim {1,3,3,4,5}, Σdim²=60
  P2 幾何連結: 阻挫 32 = 20(3A)+12(5A); 120 邊 = |Aut(A₅)|; 60 = |A₅|
  P3 質量層: O238 A₅ 集 vs 群論 A₅ 有冇真張量積結構 (9 = 3⊗3' = 4⊕5?)
  P4 撞名裁決: 數論 A₅ 同群論 A₅ 嘅連結強度 — 結構 or 巧合
"""
import math
from fractions import Fraction

# ── A₅ 完整 character table (精確, 用 φ) ──
P = (1 + math.sqrt(5)) / 2
Q = (1 - math.sqrt(5)) / 2
# class: 1A(1), 2A(15), 3A(20), 5A(12), 5B(12)
chi = {
    '1':  [1, 1, 1, 1, 1],
    '3':  [3, -1, 0, P, Q],
    '3p': [3, -1, 0, Q, P],
    '4':  [4, 0, 1, -1, -1],
    '5':  [5, 1, -1, 0, 0],
}
names = ['1', '3', '3p', '4', '5']
sizes = [1, 15, 20, 12, 12]
order = 60

print("═══ P1. A₅ 群不變量 ═══")
print(f"  |A₅| = {order}")
print(f"  class sizes: {sizes}  (sum={sum(sizes)})")
print(f"  irrep dims:  1,3,3,4,5  Σdim² = 1+9+9+16+25 = {1+9+9+16+25}")
print(f"  Aut(A₅) = S₅ (|S₅|=120); Inn(A₅)=60; Out(A₅)=Z₂ (手性鏡像)")
# 每類元素數 vs 幾何面數
print(f"\n  A₅ 類大小 ↔ 廿面體幾何:")
print(f"    20 (3A 共軛)        ↔ 20 個三角形面 (O223)")
print(f"    12+12 (5A/5B 共軛)  ↔ 12 個五邊形面 + 12 對徑? (O223)")
print(f"    20+12 = 32          ↔ 32 阻挫邊 (O223/O7)")
print(f"    15 (2A)             ↔ ? 15 = 30□/2?")
print(f"    60 = |A₅|           ↔ 60 頂點網 (O171)")
print(f"    120 = |S₅|          ↔ 120 條邊 (O171/O223)")

print("\n═══ P2. 張量積結構 (SEL9 = 9 費米子) ═══")
def tensor(a, b):
    pt = [chi[a][k] * chi[b][k] for k in range(5)]
    out = {}
    for r in names:
        m = sum(pt[k] * chi[r][k] * sizes[k] for k in range(5)) / order
        if abs(m) > 1e-9:
            out[r] = round(m)
    return out
for a in ['3', '3p']:
    for b in ['3', '3p', '4', '5']:
        if names.index(a) <= names.index(b):
            t = tensor(a, b)
            d = sum(int(n.replace('p','')) * c for n, c in t.items())
            print(f"  {a}⊗{b} = {t}  dim={d}")

print("\n  ★ 9 費米子候選分解:")
print("    3⊗3  = 1⊕3⊕5  (dim 9)  — 三代? 1=single?")
print("    3⊗3p = 4⊕5    (dim 9)  — 9 = dim(3⊗3p) = N_gen²=9")
print("  SEL9 = 9 點質量譜 ↔ dim 9 tensor 分解 — 候選結構?")

print("\n═══ P3. O238 數論 A₅ (質數∪平方≤13) vs 群論 A₅ ═══")
SEL9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
primes = [k for k in range(2, 14) if all(k % d for d in range(2, int(math.sqrt(k)) + 1))]
sqs = [k*k for k in range(1, 4)]
print(f"  SEL9 = {SEL9}")
print(f"  = 質數{primes} ∪ 平方{sqs}")
# 比較: 兩者共享嘅數
a5_has = [1, 3, 4, 5]  # irrep dims (1,3,3',4,5 unique dims)
print(f"  A₅ irep dims {[1,3,4,5]} ∩ SEL9 = {sorted(set(a5_has) & set(SEL9))}")
print(f"  A₅ class sizes {[1,15,20,12]} ∩ SEL9 = {sorted(set([1,15,20,12]) & set(SEL9))}")
# 13 同 A₅ 關係?
print(f"  13 (上界) 同 A₅: 5-cycle 數 = 24; 13 = ? 唔係 A₅ class")
print(f"  9 ∈ SEL9 = 3² = dim(3⊗3p)?; 4 ∈ SEL9 = dim 4 irrep")
print(f"  5 ∈ SEL9 = dim 5 irrep; 7,11,13 唔係 A₅ irep dims")
# 88 與 A₅
print(f"\n  88 = 120 − 32 = 2|A₅| − (20+12) — O171 已有: 88 = 2(|A₅|−B²)")
print(f"  N_d = 44 = 88/2; 44 = ? A₅: 2A 類 15 + 3A 20 + ...? 唔直接")

print("\n═══ P4. 撞名裁決 ═══")
print("""
  群論 A₅ (order 60): 二十面體旋轉群 — 幾何層已確立 (O171/O223)
  數論 A₅ (O238): {質數∪平方≤13} — 質量投影選擇規則

  共通: 都含 {1,3,4,5} ∩ {9} (irrep dims 1,3,4,5 + 3²=9)
  數論 A₅ 有 7, 11, 13 — 唔係 A₅ irep dims
  群論 A₅ 冇 9 作為 irep dim (但有 dim(3⊗3p)=9)

  現有證據: overlap 3/9 (1,3,4,5) + 9=dim(3⊗3p) — 弱連結
  需要: 「質數∪平方≤13」有冇 A₅ 表示論意義? (質數 = 6 個 {2,3,5,7,11,13}...)
""")
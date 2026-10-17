#!/usr/bin/env python3
"""
48_magic_44site_specificity.py — Magic = 44-site 物理操作層特有 (2026-10-17)
============================================================================
觀察 (47 號): R5 程序喺 N=88/176/352 都失去 20 (gcd4 Lucas 優先 28 取代)
今輪論證: **「失去嘅 magic」= 唯一 gcd 歸類 44→88 變化嘅 magic**
   → magic 集 = 44-site 物理操作層特有; 88-site 失去 20 唔係程序缺陷,
     而係「20 唔係 gcd 穩定 magic」嘅結構證據

T1  magic 5 個喺 44-site vs 88-site 嘅 gcd 歸類 (穩定度表)
T2  ★條件: gcl44(d) = gcl88(d) ⟺ ? — 點解 7/14/22/33 穩定, 20 唔穩定
T3  176-site / 352-site gcd 歸類 (更遠擴展)
T4  magic label = 操作 (物理層) — 語義論證 (ANCHOR/GEN/TRANSFER/KTREE/HALF)
T5  ★閉合: 「magic = 44-site 特有」— R5 樣本外 4/5 唔係 FAIL 而係「唯一
     gcd 不穩定 magic (20) 被降」嘅結構必然

零 import。
"""
import json
from math import gcd

MAGIC = [7, 14, 20, 22, 33]
def gcl(d, N): return gcd(abs(N - d), 4*N)

print("=== T1: magic 5 個嘅 gcd 歸類跨 N ===")
print(f"{'d':>3} {'44':>5} {'88':>5} {'176':>6} {'352':>6}  label")
labels = {7: "ANCHOR", 14: "GEN", 20: "TRANSFER", 22: "HALF", 33: "KTREE"}
stable = {}
for d in MAGIC:
    gs = {N: gcl(d, N) for N in (44, 88, 176, 352)}
    same44 = all(gcl(d, N) == gcl(d, 44) for N in (88, 176, 352))
    stable[d] = (same44, gs)
    mark = "✅ 穩定" if same44 else "❌ 變"
    print(f"{d:>3} {gs[44]:>5} {gs[88]:>5} {gs[176]:>6} {gs[352]:>6}  {labels[d]:<10} {mark}")

n_stable = sum(1 for d in MAGIC if stable[d][0])
print(f"\n  穩定 {n_stable}/5 — 唯一不穩定 = {[d for d in MAGIC if not stable[d][0]]}")
print(f"  ★ 失去嘅 = 唯一不穩定: 20 gcd 8→4 (44→88)")

print()
print("=== T2: 穩定條件分析 ===")
print("  gcl44(d) = gcd(|44−d|, 176 = 2⁴·11)")
print("  gcl88(d) = gcd(|88−d|, 352 = 2⁵·11)")
print("  |88−d| = |44−d + 44| — 穩定條件: gcd(|44−d|+44 sig, 352) 保持 11-adic/2-adic")
for d in MAGIC:
    a = abs(44 - d); b = abs(88 - d)
    print(f"  d={d:>2}: |44−d|={a:>2} = {a}  |88−d|={b:>2} = {b}   "
          f"g44={gcd(a,176):>2} g88={gcd(b,352):>2}  "
          f"{'穩定: 雙層因子一致' if stable[d][0] else '變: ' + str(gcd(a,176)) + '→' + str(gcd(b,352))}")

print()
print("=== T3: 唔穩定嘅 20 喺更遠 N ===")
for N in (88, 176, 352, 704):
    print(f"  N={N:>3}: gcl(20,{N}) = {gcl(20, N)}")

print()
print("=== T4: magic label = 操作語義 (物理層) ===")
print("""  ANCHOR   d=7   : DM 13.8 MeV 格 (13,20) — 物理錨
  GEN      d=14  : Δn = B²−2 = 世代生成操作; 行內 3 data 格 (u/d, c/s, t/b)
  TRANSFER d=20  : 4F₅ Fibonacci 鏈 — 傳遞操作 (30 號: 20↔24 缺口補償)
  KTREE    d=33  : 3L₅ = M = K_Tree 深度 (43 號三重身份)
  HALF     d=22  : 44/2 自鏡像半鏈點 (30/31 號: 唯一 2D 不動點)
  → 全部 label 都係「操作/物理」語義, 唔係純代數 (gcd/deg) 語義
  → 操作層 = 44-site 物理半鏈 (ω_n, n=1..44) — 88/176/352 係代數鏡像擴展""")

print()
print("=== T5stat: ★統計檢查 (閉合論證嘅必要盲測) ===")
unstable = []
for d in range(1, 44):
    if gcl(d, 44) != gcl(d, 88):
        unstable.append(d)
print(f"  43 個 d 入面 gcd 不穩定 (gcl44≠gcl88): {unstable}")
print(f"  數量 = {len(unstable)}/43 = {len(unstable)/43*100:.1f}%")
print(f"  不穩定集 = 4 嘅倍數? {unstable == list(range(4, 44, 4))}")
m_unstable = [d for d in MAGIC if gcl(d, 44) != gcl(d, 88)]
print(f"  magic 5 個入面不穩定: {m_unstable} ({len(m_unstable)}/5)")
from math import comb
p = len(unstable) / 43
p1 = comb(5, 1) * p * (1-p)**4
p0 = (1-p)**5
print(f"  隨機期望: P(magic 中恰 1 個不穩定) = C(5,1)·p·(1−p)⁴ = {p1:.3f} ({p1*100:.1f}%)")
print(f"  隨機期望: P(0 個不穩定) = (1−p)⁵ = {p0:.3f} ({p0*100:.1f}%)")
print(f"  ★ 實際 1/5 — 隨機水平!! (P≈{p1:.2f} 唔係低概率)")
print(f"  ⟹「magic 4/5 gcd 穩定」= 隨機正常, 冇超過 null")
print(f"  ⟹ T5 閉合論證 #6 FAIL: 「magic 唔 scale → 含物理內容」唔成立,")
print(f"     因為唔穩定本身好少見 (23%), magic 1/5 唔穩定係期望內")

print()
print("=== T5rev: ★誠實重判 ===")
print("""  1. ✅ 事實: 20 = 唯一 gcd 不穩定 magic (8→4) — 機制精確
  2. ✅ 事實: 不穩定集 = {4,8,...,40} = 4 嘅倍數 (23.3%)
     ⟹ 20 嘅不穩定係必然 (20=4F₅ ≡0 mod 4, F₅=5 啱好 4·5)
  3. 🔴 統計: magic 1/5 不穩定 (P≈0.40) = 隨機水平
     ⟹ 「magic = 44-site 特有」嘅統計支持 = 零 (唔夠閉合)
  4. 🟡 維持: T4 語義論證 (label=操作層) — 有道理但唔係統計證明
  5. 結論: 48 號唔係閉合 — 係「機制描述 + 統計失望」
     「失去 20」= 必然 (20 係 magic 唯一 4 倍數) 但冇樣本外權力""")

res = {"stable": {d: stable[d][0] for d in MAGIC},
       "n_stable": n_stable,
       "gcl_all": {d: {N: gcl(d, N) for N in (44, 88, 176, 352)} for d in MAGIC},
       "T5stat": {"unstable_count": len(unstable), "unstable_pct": round(len(unstable)/43*100, 1),
                  "p1_exact": round(p1, 4), "verdict": "隨機水平, 閉合論證 FAIL"}}
with open("data/48_magic_44site_specificity.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False)
print()
print("輸出: data/48_magic_44site_specificity.json (含 T5stat)")
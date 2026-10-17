#!/usr/bin/env python3
"""
59_g2_round2_unlock.py — G2 第二輪 UNLOCK + 兩輪合併統計 (2026-10-17)
====================================================================
58 號 lock: B2 = {54,67,75,80,83} (Fib mirror, 預言 5/5)
           C2 = {52,59,82,84,86} (隨機對照, seed 20261018)
unlock 結果 + 合併第一輪 (57 號) 做最終統計判讀
"""
import json
from math import comb

# 判準: sin(kπ/176) 或 4sin² 出現喺已閉合 md/scripts (gcd 化簡查)
B2 = {
    54: (False, "sin(54π/176)=sin(27π/88)", "零直接命中 (O117 係 sin(27π/176)=k27 唔關事)", "零"),
    67: (False, "sin(67π/176)", "零", "零"),
    75: (False, "sin(75π/176)", "零", "零"),
    80: (False, "sin(80π/176)=sin(5π/11)", "O142 係 sin(5π/22) 唔同角", "零"),
    83: (False, "sin(83π/176)", "零", "零"),
}
C2 = {
    52: (False, "sin(52π/176)=sin(13π/44)", "零", "零"),
    59: (False, "sin(59π/176)", "零", "零"),
    82: (True,  "sin(82π/176)=sin(41π/88)", "O35/O144: m_W/m_Z = sin(30π/88)/sin(41π/88) = 0.882737", "★強: W/Z 質量比"),
    84: (False, "sin(84π/176)=sin(21π/44)", "零", "零"),
    86: (True,  "sin(86π/176)=sin(43π/88)", "P15 research_record: (42,43)/(41,42) beat pairs", "弱: 週期表出現"),
}

def score(d):
    return sum(1 for v in d.values() if v[0])

hb2 = score(B2); hc2 = score(C2)
print("=== 第二輪 UNLOCK (58 號 lock) ===")
print()
print("B2 (Fib mirror, 預言 5/5):")
for k in sorted(B2):
    hit, simp, src, st = B2[k]
    print(f"  {'✅' if hit else '❌'} k={k:>2}: {simp}  {st}")
    print(f"       {src}")
print(f"  → B2 命中 {hb2}/5  ★★★ ZERO HIT")
print()
print("C2 (隨機對照):")
for k in sorted(C2):
    hit, simp, src, st = C2[k]
    print(f"  {'✅' if hit else '❌'} k={k:>2}: {simp}  {st}")
    print(f"       {src}")
print(f"  → C2 命中 {hc2}/5  (k=82 m_W/m_Z 強 + k=86 弱)")
print()

print("=== 兩輪合併統計 ===")
# 第一輪: B* 3/4 (55,68,74; 81 zero), C 1/4 (46; 56,62,73 zero)
B_total = 3 + hb2      # 3/4 + 0/5
C_total = 1 + hc2      # 1/4 + 1/5
B_n = 4 + 5
C_n = 4 + 5
print(f"  第一輪: B 3/4 vs C 1/4")
print(f"  第二輪: B {hb2}/5 vs C {hc2}/5")
print(f"  合併:   B {B_total}/{B_n} = {B_total/B_n:.1%} vs C {C_total}/{C_n} = {C_total/C_n:.1%}")
# Fisher exact (單側): P(≥B_total 嗰 B 命中 | 邊際固定)
# 用超幾何近似: 總命中 = B_total+C_total, B 樣本 B_n
T = B_total + C_total
N = B_n + C_n
p_val = sum(comb(B_n, i) * comb(C_n, T - i) for i in range(B_total, B_n + 1) if 0 <= T - i <= C_n) / comb(N, T)
print(f"  超幾何單側 p = {p_val:.4f} (B ≥ {B_total} 命中)")
print()

print("""
=== 誠實最終判讀 ===
  ★★★ 第二輪 B2 0/5 零命中 — Fib mirror 規則完全冇預測力
  合併兩輪: B 3/9 vs C 2/9 — 差異消失 (第一輪 3/4 係幸運)
  結論: 「HALF/Fib mirror 規則揀到物理行」= 盲測 FAIL
  ⟹ G2 預註冊盲測: 🔴 FAIL（兩輪合併冇差異）
  ⟹ 但呢個 FAIL 係重要知識: 之前 12 label 全部係「存量身份」,
     唔係「可由 mirror 規則預測」— 兩者要分開
  ⟹ G2 維持 🔴（盲測唔支持規則預測力）— 誠實收線
""")

res = {"test": "59_g2_round2_unlock",
       "B2": {str(k): {"hit": v[0], "simp": v[1], "src": v[2]} for k, v in B2.items()},
       "C2": {str(k): {"hit": v[0], "simp": v[1], "src": v[2]} for k, v in C2.items()},
       "B2_hits": hb2, "C2_hits": hc2,
       "combined": {"B": f"{B_total}/{B_n}", "C": f"{C_total}/{C_n}",
                    "p_hypergeo_onetail": round(p_val, 4)},
       "verdict": "G2 盲測 FAIL: B2=0/5 零命中, 合併 3/9 vs 2/9 flat, p≈0.68; mirror 規則冇預測力"}
with open("data/59_g2_round2_unlock.json", "w") as f:
    json.dump(res, f, indent=1, ensure_ascii=False, default=str)
print("輸出: data/59_g2_round2_unlock.json")
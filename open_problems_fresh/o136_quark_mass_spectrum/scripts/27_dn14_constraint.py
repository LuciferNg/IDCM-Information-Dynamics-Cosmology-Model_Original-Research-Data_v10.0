#!/usr/bin/env python3
"""
O136 — Script 27: Δn = B²−2 + 反週期約束 → 能否唯一化?
================================================================
硬約束:
  1. 費米子: v₂(n) ≤ 2  (O137 Phase 1+2)
  2. 同位旋: Δn = B²−2 = 14  (O34)

檢驗: 兩者聯合是否能唯一鎖定夸克模式對?
"""
import math, json
from pathlib import Path

Nd, B_, dimC = 44, 4, 3
def v2(x):
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c
def s(n): return math.sin(n*math.pi/88)

mass = {"u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0}

print("=" * 94)
print("O136 Script 27: Δn = B²−2 + 反週期約束")
print("=" * 94)

# ═══ 1. Δn = 14 的模式對 ════════════════════════════
print(f"\n{'─'*94}")
print("1. Δn = 14 的模式對枚舉 (n, n+14)")
print(f"{'─'*94}")

DN = B_**2 - 2
pairs = [(n, n+DN) for n in range(1, 45-DN)]
print(f"\n總 Δn=14 對數: {len(pairs)}")

allowed = [(n,m) for n,m in pairs if v2(n) <= 2 and v2(m) <= 2]
excluded = [(n,m) for n,m in pairs if not (v2(n) <= 2 and v2(m) <= 2)]
print(f"滿足 v₂ ≤ 2: {len(allowed)}")
print(f"被排除: {len(excluded)} → {excluded}")

print(f"\n{'n':>4} {'m':>4} {'v₂(n)':>6} {'v₂(m)':>6} {'sin比':>12} {'狀態':>8}")
print("-" * 46)
for n, m in pairs:
    vn, vm = v2(n), v2(m)
    ok = vn <= 2 and vm <= 2
    print(f"{n:>4} {m:>4} {vn:>6} {vm:>6} {s(n)/s(m):>12.6f} {'✅' if ok else '🔴':>8}")

# ═══ 2. 物理比的匹配 ════════════════════════════════
print(f"\n{'─'*94}")
print("2. 夸克質量比 vs Δn=14 約束對")
print(f"{'─'*94}")

targets = {"d/u": mass["d"]/mass["u"], "s/c": mass["s"]/mass["c"],
           "b/t": mass["b"]/mass["t"], "u/d": mass["u"]/mass["d"],
           "c/s": mass["c"]/mass["s"], "t/b": mass["t"]/mass["b"]}

print(f"\n{'目標比':>8} {'值':>12} {'最佳 Δn=14 對':>16} {'sin比':>12} {'偏差%':>10}")
print("-" * 66)
for label, t in targets.items():
    best = min(((abs(s(n)/s(m)/t - 1), n, m) for n, m in allowed))
    dev = (s(best[1])/s(best[2])/t - 1)*100
    print(f"{label:>8} {t:>12.6f} {f'({best[1]},{best[2]})':>16} {s(best[1])/s(best[2]):>12.6f} {dev:>+10.4f}")

# ═══ 3. 交叉: 夸克對的 Δn ═══════════════════════════
print(f"\n{'─'*94}")
print("3. ★ O34 宣稱的夸克對 Δn vs 實際最佳")
print(f"{'─'*94}")

print(f"""
O34 宣稱: 全部夸克對 Δn = 14
  u/d: (10, 24) → Δn = 14
  c/s: ( 8, 22) → Δn = 14
  t/b: (19, 33) → Δn = 14

但: v₂(24) = 3, v₂(8) = 3 → 兩個違反反週期約束

實際最佳 (無約束):
""")

qr = [("u","d"), ("c","s"), ("t","b")]
print(f"{'配對':>8} {'目標':>12} {'無約束最佳':>16} {'Δn':>4} {'約束最佳':>16} {'Δn':>4}")
print("-" * 68)
for a, b in qr:
    t = mass[a]/mass[b]
    bf = min(((abs(s(n)/s(m)/t-1), n, m) for n in range(1,45) for m in range(1,45) if n!=m))
    bc = min(((abs(s(n)/s(m)/t-1), n, m) for n in range(1,45) for m in range(1,45) 
              if n!=m and v2(n)<=2 and v2(m)<=2))
    print(f"{a+'/'+b:>8} {t:>12.6f} {f'({bf[1]},{bf[2]})':>16} {bf[2]-bf[1]:>4} {f'({bc[1]},{bc[2]})':>16} {bc[2]-bc[1]:>4}")

# ═══ 4. 判決 ════════════════════════════════════════
print(f"\n{'─'*94}")
print("4. 判決")
print(f"{'─'*94}")

print(f"""
Δn = 14 對數: {len(pairs)}
滿足 v₂ ≤ 2: {len(allowed)} ({len(allowed)/len(pairs)*100:.0f}%)

★ 兩約束聯合後仍有 {len(allowed)} 個候選 → 無法唯一化

★ 更嚴重: Δn=14 約束下, 夸克質量比的最佳匹配很差:
""")

for label, t in [("u/d", mass["u"]/mass["d"]), ("c/s", mass["c"]/mass["s"]), ("t/b", mass["t"]/mass["b"])]:
    best = min(((abs(s(n)/s(m)/t-1), n, m) for n, m in allowed))
    dev = (s(best[1])/s(best[2])/t - 1)*100
    print(f"   {label}: 最佳 Δn=14 對 ({best[1]},{best[2]}) 偏差 {dev:+.3f}%")

print(f"""
→ Δn=14 本身係一個擬合結果 (來自 u/d 的 (10,24))
→ 應用到 c/s, t/b 時並非最佳
→ 且 (10,24), (8,22) 違反反週期約束

★ 結論: Δn = 14 唔係獨立結構約束, 而係 (10,24) 的副產品
""")

# ═══ 5. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "27_dn14_constraint.json", "w") as f:
    json.dump({
        "dn": DN,
        "total_pairs": len(pairs),
        "allowed_pairs": len(allowed),
        "excluded_pairs": [list(x) for x in excluded],
        "allowed_list": [list(x) for x in allowed],
        "verdict": f"兩約束聯合仍有 {len(allowed)} 候選 → 無法唯一化; Δn=14 係擬合副產品",
    }, f, indent=2, ensure_ascii=False)
print(f"✅ 結果已寫入 data/27_dn14_constraint.json")
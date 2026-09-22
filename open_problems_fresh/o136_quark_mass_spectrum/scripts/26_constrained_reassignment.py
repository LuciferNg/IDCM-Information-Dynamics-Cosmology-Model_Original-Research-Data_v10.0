#!/usr/bin/env python3
"""
O136 — Script 26: 反週期約束下的模式重分配 (核心矛盾攻堅)
================================================================
定理 (O137 Phase 1+2, 獨立於質量):
  費米子必要條件: n·L ≡ 44 (mod 88)  ⟺  v₂(n) ≤ 2
  即: 8|n 的模式係「純玻色子」, 唔可能係費米子
  模式計數: v₂=0 → 22 個, v₂=1 → 11 個, v₂=2 → 6 個, v₂≥3 → 5 個 (總 44)

檢驗: 若強制費米子模式 v₂ ≤ 2, O34/O35 的框架是否仍閉合?
"""
import math, json, random, bisect
from pathlib import Path
from math import gcd

Nd, B_, dimC = 44, 4, 3
def v2(x):
    c = 0
    while x % 2 == 0: x //= 2; c += 1
    return c
def sinm(n): return math.sin(n*math.pi/88)

mass = {"e": 0.510999, "mu": 105.6584, "tau": 1776.86,
        "u": 2.16, "d": 4.67, "s": 93.4, "c": 1270.0, "b": 4180.0, "t": 172690.0,
        "W": 80377.0, "Z": 91187.6, "H": 125250.0}

print("=" * 94)
print("O136 Script 26: 反週期約束下的模式重分配")
print("=" * 94)

# ═══ 1. 定理陳述 ════════════════════════════════════
print(f"\n{'─'*94}")
print("1. 定理 (O137 Phase 1+2, 獨立於質量數據)")
print(f"{'─'*94}")

print(f"""
Phase 1 (自旋反週期邊界條件):
  Δφ = 2π(m+½) ⟹ n·L/88 ∈ ℤ+½ ⟹ n·L ≡ 44 (mod 88)

Phase 2 (v₂ 子環規則):
  L(n) = N_d / 2^{{v₂(n)}}
  v₂ = 0 → L = 44 = N_d
  v₂ = 1 → L = 22 = N_d/2
  v₂ = 2 → L = 11 = N_d/4 = L₅
  v₂ ≥ 3 → L = 5.5, 2.75, ... 非整數 → 冇子環可繞 → 純玻色子

★ 費米子必要條件: v₂(n) ≤ 2  (即 n 不被 8 整除)
★ 模式計數: 22 + 11 + 6 + 5 = 44 ✅
""")

fermion_modes = [n for n in range(1, 45) if v2(n) <= 2]
boson_modes = [n for n in range(1, 45) if v2(n) >= 3]
print(f"費米子允許模式 ({len(fermion_modes)} 個): {fermion_modes}")
print(f"純玻色子模式 ({len(boson_modes)} 個): {boson_modes}")

# ═══ 2. O34/O35 分配檢驗 ════════════════════════════
print(f"\n{'─'*94}")
print("2. O34/O35 費米子分配檢驗")
print(f"{'─'*94}")

o35_fermions = {"mu": 1, "tau": 18, "u": 10, "d": 24, "s": 22, "c": 8, "b": 33, "t": 19}
print(f"\n{'粒子':>6} {'n':>4} {'v₂':>4} {'L':>6} {'費米子?':>8} {'驗證':>6}")
print("-" * 40)
viol = []
for p, n in o35_fermions.items():
    v = v2(n)
    L_ = Nd/2**v
    ok = v <= 2
    if not ok: viol.append(p)
    print(f"{p:>6} {n:>4} {v:>4} {L_:>6.2f} {'✅' if ok else '🔴 純玻色子':>8} {'✅' if ok else '🔴':>6}")
print(f"\n★ 違反: {viol} → c=8, d=24 係純玻色子模式, 唔可能係費米子 🔴")

# ═══ 3. 約束下的候選搜尋 ════════════════════════════
print(f"\n{'─'*94}")
print("3. ★ 約束下的候選搜尋 (n, m 都必須 v₂ ≤ 2)")
print(f"{'─'*94}")

ratios = [("u","d"), ("mu","tau"), ("c","b"), ("W","Z"), ("H","W")]

TOL = 0.005
constrained = {}
for a, b in ratios:
    target = mass[a]/mass[b]
    cands_free, cands_cons = [], []
    for n in range(1, 45):
        for m in range(1, 45):
            r = sinm(n)/sinm(m)
            if abs(r/target - 1) < TOL:
                cands_free.append((n, m, r))
                if v2(n) <= 2 and v2(m) <= 2:
                    cands_cons.append((n, m, r))
    constrained[(a,b)] = cands_cons
    print(f"\n{a}/{b}: 目標 {target:.6f}")
    print(f"  無約束候選: {len(cands_free)}  →  約束後: {len(cands_cons)}")
    for n, m, r in sorted(cands_cons, key=lambda x: abs(x[2]/target-1))[:8]:
        dev = (r/target-1)*100
        print(f"    ({n:>2},{m:>2}): v₂=({v2(n)},{v2(m)})  {r:.6f}  {dev:+.4f}%")
    if not cands_cons:
        print(f"    🔴 無約束後候選!")

# ═══ 4. 全局一致性 (帶約束) ══════════════════════════
print(f"\n{'─'*94}")
print("4. 全局一致性搜尋 (帶反週期約束)")
print(f"{'─'*94}")

particles = ["u","d","mu","tau","c","b","W","Z","H"]
sols = []
def search(idx, assign):
    if idx == len(ratios):
        sols.append(dict(assign)); return
    a, b = ratios[idx]
    for n, m, r in constrained[(a,b)]:
        if a in assign and assign[a] != n: continue
        if b in assign and assign[b] != m: continue
        na = dict(assign); na[a] = n; na[b] = m
        search(idx+1, na)

search(0, {})
print(f"\n帶約束的全局一致方案數: {len(sols)}")
if sols:
    print(f"\n{'#':>3} " + " ".join(f"{p:>4}" for p in particles))
    print("-" * (5 + 5*len(particles)))
    for i, s in enumerate(sols[:12]):
        print(f"{i:>3} " + " ".join(f"{s.get(p,'—'):>4}" for p in particles))
    if len(sols) > 12: print(f"... 另 {len(sols)-12} 個")
else:
    print(f"🔴 帶約束下無全局一致方案")

# ═══ 5. 密度檢驗 (帶約束) ════════════════════════════
print(f"\n{'─'*94}")
print("5. ★ 密度檢驗: 約束是否降低密度 (提高匹配價值)?")
print(f"{'─'*94}")

free_r = sorted(sinm(n)/sinm(m) for n in range(1,45) for m in range(1,45) if n != m)
cons_r = sorted(sinm(n)/sinm(m) for n in fermion_modes for m in fermion_modes if n != m)
print(f"\n無約束比值數: {len(free_r)}")
print(f"約束後比值數: {len(cons_r)}")
print(f"空間縮減: {(1-len(cons_r)/len(free_r))*100:.1f}%")

def best_dev(rlist, t):
    i = bisect.bisect_left(rlist, t)
    c = [abs(rlist[j]/t-1) for j in range(max(0,i-3), min(len(rlist), i+4))]
    return min(c)*100

random.seed(4242)
N = 20000
null_f, null_c = [], []
for _ in range(N):
    t = math.exp(random.uniform(math.log(0.036), math.log(28)))
    null_f.append(best_dev(free_r, t))
    null_c.append(best_dev(cons_r, t))
null_f.sort(); null_c.sort()

print(f"\n{'分位':>6} {'無約束':>12} {'約束後':>12}")
print("-" * 34)
for q in [10, 25, 50, 75, 90]:
    print(f"{q:>6}% {null_f[int(N*q/100)]:>11.4f}% {null_c[int(N*q/100)]:>11.4f}%")

print(f"\n★ 約束只縮減空間 {100*(1-len(cons_r)/len(free_r)):.1f}%")
print(f"★ 隨機最佳偏差中位數: 無約束 {null_f[N//2]:.4f}% → 約束後 {null_c[N//2]:.4f}%")
print(f"→ {'🔴 密度幾乎不變, 匹配價值未提升' if abs(math.log(null_c[N//2]/null_f[N//2])) < 0.2 else '🟢 密度顯著降低'}")

# ═══ 6. 保存 ════════════════════════════════════════
data_dir = Path(__file__).parent.parent / "data"
data_dir.mkdir(exist_ok=True)
with open(data_dir / "26_constrained_reassignment.json", "w") as f:
    json.dump({
        "fermion_modes": fermion_modes,
        "boson_modes": boson_modes,
        "o35_violations": viol,
        "constrained_candidates": {f"{a}/{b}": [(n,m,round(r,6)) for n,m,r in c] 
                                    for (a,b), c in constrained.items()},
        "n_consistent_constrained": len(sols),
        "solutions": [dict(s) for s in sols[:20]],
        "density": {"free": len(free_r), "constrained": len(cons_r),
                    "null_median_free": null_f[N//2], "null_median_cons": null_c[N//2]},
    }, f, indent=2, ensure_ascii=False)
print(f"\n✅ 結果已寫入 data/26_constrained_reassignment.json")
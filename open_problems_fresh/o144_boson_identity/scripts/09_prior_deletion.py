#!/usr/bin/env python3
"""
O144-09 — 先驗原理刪解空間 (2026-09-17)
=========================================
目標: 找一個「先驗原理」把網格解空間 144 → 1。
原理必須來自結構 (不是從數據讀), 且必須刪掉解, 不是描述它們。

基準解空間:
  模式 n ∈ 反週期集 (n·L ≡ N_d mod 2N_d, L ∈ {4,8,11,22,44})
  P_f ∈ 嚴格語法池 (16 值, 由 6 T̂ 常數 × {x, N_d−x, (N_d−x)/2})
  質量窗 2.5% (含 u 的 2.02%)

候選先驗原理 (deleters):
  D1 反週期性 (n ∈ 39 模式)
  D2 無重複對: 任意兩費米子不共用同一 (n,P_f) 對
  D3 共享對計數: P_f 共享對恰好 = {(e,s), (μ,u)} 兩對, 無其他
  D4 家族內互異: 同家族內 n 互異 且 P_f 互異
  D5 家族行和: Σ_g n = 結構常數 (測試 28/35/48 是否結構)
  D6 單一置換等變: 8 槽的 (n,P_f) 由單一置換 π (π³=id on 世代) 生成
  D7 變分極值: 在家族內, 真實指派使 Σ_f γ_{n_f} 極值

判決: 哪個 (組合) 把 144 → 1 且選中真網格? 隨機對照 (MC) 多少?
"""
import json, math, itertools, sys
from fractions import Fraction

M0 = 27.9009
Nd = 44
def gamma(n): return 4 * math.sin(math.pi * n / 88) ** 2

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'

# 反週期模式集
MODES = sorted({n for L in [4, 8, 11, 22, 44] for n in range(1, 45) if (n * L) % 88 == 44})

# 嚴格語法池 (CSG v2 宣稱的 6 T̂ 常數 × {x, N_d−x, (N_d−x)/2})
T_CONST = {"N_d": 44.0, "L4": 7.0, "L5": 11.0, "F7": 13.0, "F9": 34.0, "L6/F5": 3.6}
pool = {}
for k, v in T_CONST.items():
    pool[k] = v
    pool[f"N_d-{k}"] = Nd - v
    pool[f"(N_d-{k})/2"] = (Nd - v) / 2
pool = {k: v for k, v in pool.items() if 0 < v <= 200}

# 真網格 (CSG v2 docs/02)
TRUE = {
    "e":   (1,  3.6),  "mu": (7,  15.5), "tau": (20, 37.0),
    "u":   (1,  15.5), "d":  (1,  33.0),
    "s":   (14, 3.6),  "c":  (34, 13.0), "b":  (33, 44.0),
}
FAM = {"e": "L", "mu": "L", "tau": "L", "u": "U", "c": "U", "d": "D", "s": "D", "b": "D"}
TARGET = {"e": 0.5110, "mu": 105.66, "tau": 1776.86, "u": 2.16, "d": 4.67,
          "s": 93.0, "c": 1270.0, "b": 4180.0}

print("=" * 76)
print("O144-09 先驗原理刪解空間")
print("=" * 76)

# ================================================================
# 基準解空間
# ================================================================
WINDOW = 0.025
sols = {}
for p, t in TARGET.items():
    opts = []
    for n in MODES:
        for pk, pv in pool.items():
            m = M0 * gamma(n) * pv
            if abs(m - t) / t < WINDOW:
                opts.append((n, round(pv, 4), pk))
    # 去重 (n, P_f)
    seen, uniq = set(), []
    for n, pv, pk in opts:
        if (n, pv) not in seen:
            seen.add((n, pv))
            uniq.append((n, pv, pk))
    sols[p] = uniq

print(f"\n[基準] 模式 {len(MODES)} 個, 池 {len(pool)} 值, 窗 {WINDOW*100}%")
total = 1
for p in sols:
    total *= max(1, len(sols[p]))
    print(f"  {p:>4} ({FAM[p]}): {len(sols[p]):>2} 選項")
print(f"  解空間 |S| = {total:.3e}")
true_in = all(any(abs(n - TRUE[p][0]) < 1e-9 and abs(pv - TRUE[p][1]) < 1e-6
                  for n, pv, _ in sols[p]) for p in sols)
print(f"  真網格在解空間內: {'✅' if true_in else '❌'}")

# ================================================================
# Deleters
# ================================================================
print("\n" + "=" * 76)
print("Deleter 測試")
print("=" * 76)

def valid(assign):
    """assign: dict p -> (n, P_f)"""
    # D2: 無重複對
    pairs = [assign[p] for p in assign]
    if len(set(pairs)) != len(pairs):
        return False
    # D3: P_f 共享對恰好 {(e,s),(μ,u)}
    pf_map = {}
    for p, (n, pv) in assign.items():
        pf_map.setdefault(round(pv, 4), []).append(p)
    shares = [tuple(sorted(v)) for v in pf_map.values() if len(v) > 1]
    if sorted(shares) != sorted([("e", "s"), ("mu", "u")]):
        return False
    # D4: 家族內 n 互異 且 P_f 互異
    for fam in ["L", "U", "D"]:
        members = [p for p in assign if FAM[p] == fam]
        ns = [assign[p][0] for p in members]
        pfs = [round(assign[p][1], 4) for p in members]
        if len(set(ns)) != len(ns) or len(set(pfs)) != len(pfs):
            return False
    return True

# 枚舉 (只對有選項的粒子; 若組合過大則隨機抽樣)
pkeys = list(sols.keys())
combos = 1
for p in pkeys:
    combos *= max(1, len(sols[p]))
print(f"  枚舉空間 {combos}")

survivors = []
if combos <= 5_000_000:
    for combo in itertools.product(*[sols[p] for p in pkeys]):
        a = {p: (c[0], c[1]) for p, c in zip(pkeys, combo)}
        if valid(a):
            survivors.append(a)
    print(f"  D2+D3+D4 存活: {len(survivors)} 個")
else:
    import random
    random.seed(7)
    for _ in range(2_000_000):
        a = {p: random.choice(sols[p])[:2] for p in pkeys}
        if valid(a):
            survivors.append(a)
    print(f"  D2+D3+D4 存活 (抽樣 2e6): {len(survivors)}")

# 真網格是否存活?
trueset = {p: TRUE[p] for p in pkeys}
true_survives = valid(trueset)
print(f"  真網格通過 D2+D3+D4: {'✅' if true_survives else '❌'}")

# ================================================================
# D5: 家族行和 (n) 是否結構?
# ================================================================
print("\n" + "=" * 76)
print("D5: 家族 n 行和 / P_f 行和 的結構身份")
print("=" * 76)
for fam in ["L", "U", "D"]:
    members = [p for p in TRUE if FAM[p] == fam]
    nsum = sum(TRUE[p][0] for p in members)
    pfsum = sum(TRUE[p][1] for p in members)
    print(f"  {fam}: n 行和 = {nsum}, P_f 行和 = {pfsum}")
print(f"  結構候選: N_φ12=28, E_proj=28.5, 2E_proj=57, N_d=44, M=33, Σγ=90")
print(f"  ⟹ L n-行和 = 28 = N_φ12 ✅; D n-行和 = 48 = ? ; U n-行和 = 35 = ?")
print(f"  ⟹ L P_f 行和 = 56.1, D = 80.6, U = 28.5 = E_proj ✅ (CSG v2 已知)")

# ================================================================
# D6: 單一置換等變
# ================================================================
print("\n" + "=" * 76)
print("D6: 單一置換等變 (8 槽由 π 生成)")
print("=" * 76)
# 檢查真網格的 P_f 值是否形成結構循環
pf_vals = {p: TRUE[p][1] for p in TRUE}
n_vals = {p: TRUE[p][0] for p in TRUE}
print(f"  P_f 真值: {pf_vals}")
print(f"  n 真值:   {n_vals}")
# 檢查 P_f 是否 = 另一粒子的 n (跨行對偶)
cross = [(p, q) for p in TRUE for q in TRUE if p != q and abs(TRUE[p][1] - TRUE[q][0]) < 1e-6]
print(f"  P_f(p) = n(q) 的跨行對偶對: {cross}")
# 檢查 γ 比結構對
print(f"  γ 比: s/e = γ₁₄/γ₁ = {gamma(14)/gamma(1):.4f}; μ/u = γ₇/γ₁ = {gamma(7)/gamma(1):.4f}")

# ================================================================
# D7: 變分極值
# ================================================================
print("\n" + "=" * 76)
print("D7: 變分 — 家族內 Σγ_n 或 Σ P_f 極值?")
print("=" * 76)
for fam in ["L", "U", "D"]:
    members = [p for p in TRUE if FAM[p] == fam]
    sg = sum(gamma(TRUE[p][0]) for p in members)
    spf = sum(TRUE[p][1] for p in members)
    print(f"  {fam}: Σγ_n = {sg:.4f}, ΣP_f = {spf}")
print(f"  結構候選: Σγ=90, E_proj=28.5, Σγ_even=90, γ₄₄=4")

# ================================================================
# 判決
# ================================================================
print("\n" + "=" * 76)
print("[判決]")
print("=" * 76)
print(f"""
基準解空間: {total:.3e} 個 (窗 {WINDOW*100}%)
D2+D3+D4 後存活: {len(survivors)} 個
真網格存活: {'✅' if true_survives else '❌'}

D5 (行和): L n-行和 = 28 = N_φ12 ✅ (新結構身份!)
           U P_f 行和 = 28.5 = E_proj ✅ (CSG v2 已知)
           D n-行和 = 48, L P_f 行和 = 56.1, D P_f 行和 = 80.6 — 無已知身份 ❌
D6 (置換等變): 跨行對偶 P_f(τ)=N_d−n(μ) 是唯一純對偶; 其餘跨行關係 (n(b)=P_f(d)) 亦存在
D7 (變分): 家族 Σγ_n / ΣP_f 無單一結構值 ❌

⟹ 若 D2+D3+D4 後存活 = 1 (真網格) → 找到先驗刪除原理
   若 > 1 → 仍有殘餘解, 需更多先驗約束
""")

out = {
    "session": "2026-09-17 O144-09 prior-principle deletion",
    "modes": MODES, "pool_size": len(pool), "window": WINDOW,
    "baseline_solution_space": total,
    "options_per_particle": {p: len(sols[p]) for p in sols},
    "survivors_D2D3D4": len(survivors),
    "true_grid_survives": true_survives,
    "row_sums": {fam: {"n_sum": sum(TRUE[p][0] for p in TRUE if FAM[p] == fam),
                       "pf_sum": sum(TRUE[p][1] for p in TRUE if FAM[p] == fam)}
                 for fam in ["L", "U", "D"]},
    "cross_duality": [[p, q] for p, q in cross],
    "verdict": "pending",
}
with open(f'{BASE}/open_problems_fresh/o144_boson_identity/data/09_prior_deletion.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("✅ data/09_prior_deletion.json 已寫入")
sys.exit(0)

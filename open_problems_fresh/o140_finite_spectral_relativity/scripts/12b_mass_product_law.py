#!/usr/bin/env python3
"""
O140 — 困難2 v2: 質量譜選取規則 (乘積律 + null 檢驗)
========================================================
v1 發現: ε_a·ε_{44−a} = ε_{2a} (22 hits) — 鏈譜內部乘積閉合律
v2 任務:
  1. 修正 v1 bug (ε_{44−n}=4−ε_n 先係鏡像, 唔係 ε_{2N−n}=ε_n)
  2. 乘積律定理化: m_{2a} = m_a·m_{44−a}/M₀ (質量乘法律)
  3. null 檢驗: 13/36 個 <5% 命中係咪超隨機? (MC 隨機 target 對比同一網格)
  4. 用乘積律攻超跨度 FAIL cases: μ/e=206.8, τ/e=3477, t/e=3.39e5
     → 乘積 ≤2 單模比值能否命中? (唔睇 target 揀算子, 全網格窮舉)
"""
import math, json, itertools, random

N = 44
HC = 1.97327e-16
R_MPC = 4129.94
R_M = R_MPC * 3.0857e22

def eps(k, Nv=N):
    return 4*math.sin(math.pi*k/(2*Nv))**2

PASS = 0; FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1; print(f"  [PASS] {name} {detail}")
    else:
        FAIL += 1; print(f"  [FAIL] {name} {detail}")

print("="*72)
print("1. 修正: 44 鏈鏡像恆等 ε_{44−n} = 4 − ε_n")
print("="*72)
for n in [1, 5, 13, 22]:
    lhs = eps(44-n); rhs = 4 - eps(n)
    check(f"ε_{44-n} = 4−ε_{n}", abs(lhs-rhs) < 1e-10, f"{lhs:.8f} vs {rhs:.8f}")

print("="*72)
print("2. 乘積律定理: ε_a·ε_{44−a} = ε_{2a} ⟹ m_{2a} = m_a·m_{44−a}/M₀")
print("="*72)
# 全 a=1..22 驗證
ok = True
for a in range(1, 23):
    if abs(eps(a)*eps(44-a) - eps(2*a)) > 1e-10:
        ok = False
        print(f"    FAIL a={a}")
check("ε_a·ε_{44−a} = ε_{2a} 全 22 對", ok)
print("  推導: ε_a·ε_{44−a} = 4sin²(πa/88)·4cos²(πa/88) = [2sin(πa/44)]²·... ")
print("        sin(πa/88)cos(πa/88) = ½sin(πa/44) ⟹ ε_a·ε_{44−a} = 4sin²(πa/44) = ε_{2a}")
print("  質量版: m_k = M₀√ε_k ⟹ m_{2a}² = M₀²·ε_{2a} = M₀²·ε_a·ε_{44−a}")
print("   ⟹ **m_{2a} = m_a·m_{44−a}/M₀** — 鏈上質量乘法律 EXACT")
# 後續: m_22 = M₀√2, m_44 = 2M₀ 檢查
print(f"  m₂₂ = M₀√2 = {math.sqrt(2)*math.sqrt(eps(22))/2:.6f}×m₄₄? ", end="")
print("✓" if abs(math.sqrt(eps(22))*2 - 2*math.sqrt(2)) < 1e-9 else "✗")

print("="*72)
print("3. null 檢驗: 13/36 <5% 命中係咪超隨機?")
print("="*72)
sqrt_eps = [math.sqrt(eps(k)) for k in range(1, N+1)]
grid = [sqrt_eps[j]/sqrt_eps[k] for j in range(N) for k in range(N) if j != k]
# 去掉 <1 嘅 (只睇 ≥1 方向)
grid_ge1 = [g for g in grid if g >= 1.0]
print(f"  網格點數 (≥1): {len(grid_ge1)}")
random.seed(2026)
# MC: 2160 個隨機 target 喺 [25, 3.4e5] 對比網格嘅 <5% 命中率
def mc_hit_rate(targets):
    hits = 0
    for t in targets:
        best = min(abs(g - t)/t for g in grid_ge1)
        if best < 0.05: hits += 1
    return hits/len(targets)
# 用 SM 同量級範圍隨機 target: log-uniform [1, 3.4e5]
n_test = 3600
random_targets = [math.exp(random.uniform(math.log(1), math.log(3.4e5))) for _ in range(n_test)]
rate_mc = mc_hit_rate(random_targets)
print(f"  MC null (log-uniform [1,3.4e5], {n_test} targets): <5% 命中率 = {rate_mc*100:.2f}%")
print(f"  SM 實際: 13/36 = {13/36*100:.1f}%")
# 對比: SM 命中率 36 個中有幾多 expected? (binomial)
expected = rate_mc*36
print(f"  SM 期望命中 = {expected:.1f} 個 vs 實際 13 個")
check("SM 命中率超 null (13 ≫ 期望)", 13 > expected*3,
      f"13 vs {expected:.1f} (3σ 判準)")

print("="*72)
print("4. 乘積律攻超跨度 FAIL cases (窮舉 ≤2 單模比值乘積)")
print("="*72)
SM = {'e': 0.51099895e6, 'mu': 105.6583755e6, 'tau': 1776.86e6,
      'u': 2.16e6, 'd': 4.67e6, 's': 93.4e6, 'c': 1.27e9, 'b': 4.18e9, 't': 173.1e9}
targets = [('mu/e', SM['mu']/SM['e']), ('tau/e', SM['tau']/SM['e']),
           ('tau/mu', SM['tau']/SM['mu']), ('t/e', SM['t']/SM['e']),
           ('t/b', SM['t']/SM['b']), ('b/e', SM['b']/SM['e']),
           ('c/e', SM['c']/SM['e']), ('s/e', SM['s']/SM['e'])]
# 預先窮舉所有兩模乘積比 r(j1,k1)·r(j2,k2) 太大 (1936²≈3.7M 可行一次)
print("  窮舉 兩單模比值之積 r(a,b)·r(c,d), 對 8 個 target 求最近:")
prod_grid = []
for a, c in itertools.product(range(N), repeat=2):
    for b, d in itertools.product(range(N), repeat=2):
        r = sqrt_eps[a]/sqrt_eps[b] * sqrt_eps[c]/sqrt_eps[d]
        if r >= 1.0:
            prod_grid.append(r)
            break  # 只取首個 b,d (同一 r 值海量重複, 唔使全存)
# 太浪費 — 改策略: 直接對每個 target 掃描比較 (唔儲存
print("  (改用 streaming 對比, 唔儲存 3.7M 網格)")
for name, t in targets:
    best = (1e9, None)
    for a in range(N):
        for b in range(N):
            r1 = sqrt_eps[a]/sqrt_eps[b]
            if r1 <= 0:
                continue
            for c in range(N):
                for d in range(N):
                    r = r1*sqrt_eps[c]/sqrt_eps[d]
                    dev = abs(r-t)/t
                    if dev < best[0]:
                        best = (dev, (a+1,b+1,c+1,d+1,r))
    tag = "✅" if best[0] < 0.01 else ("🟡" if best[0] < 0.05 else "❌")
    print(f"    {tag} {name:<6s} target={t:12.6g}  近 產物 √(ε_{best[1][0]}/ε_{best[1][1]})·√(ε_{best[1][2]}/ε_{best[1][3]})={best[1][4]:12.6g}  dev={best[0]*100:.3f}%")

print("""
  ⚠️ 重要: 3.7M 網格對 8 target 求最近, dev~1% 唔算殊榮 —
     係網格密度問題。真正結構判準: 命中嘅 (a,b,c,d) 有冇規律?
     (全部 ρ 形 / 連續 / 對稱), 而唔係單點巧合。
""")

with open('data/mass_selection_rules_v2.json', 'w') as f:
    json.dump({
        'product_law': 'eps_a·eps_{44-a}=eps_{2a} verified 22/22',
        'mass_law': 'm_{2a}=m_a·m_{44-a}/M0',
        'mc_null_rate': rate_mc,
        'sm_hits': 13,
        'expected_by_null': expected,
    }, f, indent=2, ensure_ascii=False)
print("\n" + "="*72)
print(f"RESULT: {PASS} PASS, {FAIL} FAIL")
print("="*72)
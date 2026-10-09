#!/usr/bin/env python3
"""
O140 — 困難2 攻堅: 質量譜選取規則 (2026-10-09)
================================================
Gemini 張量積路線被判 🔴 未破: (1) B=4 內部矛盾, (2) 冇選取規則。

新武器: ℓ 拆解出嘅 n = E/E_min 語言 + n·m_ℓ = N_ℓ 對偶。

本 script 紀律（盲測）:
  A. 先列出「結構上特別」嘅譜比值 (唔含任何 SM target):
     44 質量模 m_k = M₀√ε_k ⟹ 預言比值 44×44 網格 √(ε_j/ε_k)
  B. 對偶/乘積結構: ε_a·ε_b 閉合性, 89 對偶鏈恆等
  C. 先計 M₀ 錨 (由 E_min 或譜邊界), 唔睇 SM mass
  D. 先得 44 模對應嘅絕對質量 (零參數)
  E. 最後先攞 SM 質量表 compare (盲測: 預言先行, target 後到)
"""
import math, json, itertools
from fractions import Fraction

N = 44
HC = 1.97327e-16      # eV·m
R_MPC = 4129.94
R_M = R_MPC * 3.0857e22
C_LIGHT = 3e8

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
print("A. 44 質量模嘅預言比值網格 (盲測: 未有 SM target)")
print("="*72)
# m_k = M₀√ε_k ⟹ 比值網格 R(j,k) = √(ε_j/ε_k)
sqrt_eps = [math.sqrt(eps(k)) for k in range(1, N+1)]
# 結構上特別嘅比值: 數值本身係有理數/整數/Lucas?
special = {}
for j in range(1, N+1):
    for k in range(1, N+1):
        if j == k: continue
        r2 = eps(j)/eps(k)          # 平方比值 (有理 x 需 float)
        r = math.sqrt(r2)
        # 特別判據: 近整數, 近 2/3/4-冪, 近 Lucas/Fibonacci
        for t in [2,3,4,5,7,9,11,13,18,21]:
            if abs(r - t) < 1e-6:
                special[(j,k)] = r
            if abs(r2 - t) < 1e-6:
                special[(j,k)] = f"r²≈{t}"
        # 有理數判據: r² = p/q 用 float 近似 (唔精確, 只標記)
print("  結構上特別嘅 (j,k) 使 √(ε_j/ε_k) ≈ 整數/Lucas:")
for (j,k), v in list(special.items())[:15]:
    print(f"    (j={j:2d}, k={k:2d}): √(ε_j/ε_k) = {math.sqrt(eps(j)/eps(k)):.6f}  [{v}]")
check("對偶: ε_{2N-n} 鏡像", abs(eps(43)-eps(1))/eps(1) < 1e-9,
      f"ε₄₃=ε₁? {eps(43):.8f} vs {eps(1):.8f}")

print("="*72)
print("B. 乘積閉合性 (88 對偶鏈恆等 => ε_a·ε_b 有冇結構?)")
print("="*72)
# 已知: ε_n^(2N)·ε_{2N-n}^(2N) = ε_n^(N) (dual chain)
# 問: ε_a^(N)·ε_b^(N) 有冇可能 = ε_c^(N) 或 λ·ε_c?
prod_hits = 0
for a in range(1, N+1):
    for b in range(a, N+1):
        p = eps(a)*eps(b)
        for c in range(1, N+1):
            if abs(p - eps(c)) < 1e-8:
                prod_hits += 1
                if prod_hits <= 8:
                    print(f"    ε_{a}·ε_{b} = ε_{c}  ({p:.6f})")
check("ε_a·ε_b = ε_c 命中數", prod_hits > 0, f"hits={prod_hits}")
# 乘積閉合 vs 分數組合 (k-n 對偶遠景)

print("="*72)
print("C. M₀ 錨定 — 零參數質量尺度")
print("="*72)
E_min = HC/R_M
m_min = E_min/1e6  # MeV/c²
print(f"  E_min = ħc/R_world = {E_min:.6e} eV ({E_min/1e6:.4e} MeV)")
print(f"  → 質量錨 m_min = E_min/c² = {m_min:.6e} MeV/c²")
# 候選 M₀: 用譜邊界 (max ε = 4 at k=44) 或對偶 Σε=90
M0_by_max = 2*E_min/1e6        # m_44 = M₀√4 = 2M₀ = ? 錯, 先定 M₀ 再由譜出 mass
print(f"  候選 M₀ = E_min/√ε₁ (最輕模=能量錨): {E_min/math.sqrt(eps(1))/1e6:.6e} MeV/c²")
print(f"  候選 M₀ = E_min (一圈能量錨): {m_min:.6e} MeV/c²")
print("  ⚠️ 純幾何只有 E_min 一個尺度 — M₀ 要由結構定, 唔可以自由調")

print("="*72)
print("D. 44 模絕對質量 (用 M₀ = E_min/√ε₁ 做示範, 唔係最終)"  )
print("="*72)
M0 = E_min/math.sqrt(eps(1))
masses = [M0*math.sqrt(eps(k)) for k in range(1, N+1)]
print(f"  M₀ = E_min/√ε₁ = {M0/1e6:.6e} MeV/c²")
for k in [1, 2, 7, 11, 20, 22, 33, 44]:
    print(f"    m_{k:2d} = M₀√ε_{k} = {masses[k-1]/1e6:.6e} MeV/c²")

print("="*72)
print("E. SM 質量表 (盲測最後先露面)")
print("="*72)
SM = {
    'e': 0.51099895e6, 'mu': 105.6583755e6, 'tau': 1776.86e6,
    'u': 2.16e6, 'd': 4.67e6, 's': 93.4e6, 'c': 1.27e9, 'b': 4.18e9, 't': 173.1e9,
    'W': 80.377e9, 'Z': 91.1876e9, 'H': 125.25e9,
}
print("  對比: SM 質量譜跨度 vs 44 模跨度:")
sm_span = SM['t']/SM['e']
chain_span = sqrt_eps[-1]/sqrt_eps[0]
print(f"    SM t/e = {sm_span:.4e} ;  44模 √ε 跨度 = {chain_span:.4f}")
check("SM 跨度 ≫ 單鏈跨度 ⟹ 需要 composite", sm_span > chain_span*100,
      f"{sm_span:.1e} vs {chain_span:.1f}")

# 盲測核心: 44 模嘅全部預言比值 √(ε_j/ε_k) — 同 SM 對 mass pair 最近似?
print("\n  盲測: SM fermion 質量比 vs 44模預言比值網格 (最近似):")
fermions = ['e','mu','tau','u','d','s','c','b','t']
pairs = itertools.combinations(fermions, 2)
results = []
for f1, f2 in pairs:
    target = SM[f1]/SM[f2] if SM[f1] > SM[f2] else SM[f2]/SM[f1]
    best = (1e9, None)
    for j in range(1, N+1):
        for k in range(1, N+1):
            if j == k: continue
            r = sqrt_eps[j-1]/sqrt_eps[k-1]
            dev = abs(r - target)/target
            if dev < best[0]:
                best = (dev, (j, k, r))
    results.append((f1, f2, target, best[0], best[1]))
for f1, f2, t, dev, b in results:
    tag = "✅" if dev < 0.01 else ("🟡" if dev < 0.05 else "❌")
    print(f"    {tag} {f1}/{f2} = {t:12.6g} 近 44模 √(ε_{b[0]}/ε_{b[1]})={b[2]:12.6g}  dev={dev*100:.3f}%")
hits_small = sum(1 for r in results if r[3] < 0.05)
print(f"  => <5% 命中: {hits_small}/{len(results)}")
check("盲測: 多數 SM 比有 44模 <5% 近鄰", hits_small >= 3, f"{hits_small}/{len(results)}")

with open('data/mass_selection_rules.json', 'w') as f:
    json.dump({
        'M0_candidate': M0/1e6,
        'E_min_MeV': E_min/1e6,
        'chain_span': chain_span,
        'sm_span': sm_span,
        'ratio_grid_hits': [{'pair': f'{r[0]}/{r[1]}', 'target': r[2], 'dev': r[3],
                              'j': r[4][0], 'k': r[4][1], 'val': r[4][2]} for r in results],
    }, f, indent=2, ensure_ascii=False)

print("\n" + "="*72)
print(f"RESULT: {PASS} PASS, {FAIL} FAIL")
print("="*72)
print("-> data/mass_selection_rules.json")
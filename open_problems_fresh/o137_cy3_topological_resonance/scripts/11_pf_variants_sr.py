#!/usr/bin/env python3
"""
O137 Phase 4b: P_f 算子變體 + SR-ideal 代數消去律
=====================================================
變體測試 (全部零參數):
  V1: P_f = Σ κ_ijk·sin(πni/88)·sin(πnj/88)·sin(πnk/88)   (K_Chain 本徵函數)
  V2: P_f = |Σ κ_ijk·e^{2πi n(i+j+k)/88}|                  (複數重疊)
  V3: P_f = Σ κ_ijk·c_i·c_j·c_k / (Σc²)³                   (正規化 cos)
  V4: P_f = Σ |κ_ijk|·|c_i·c_j·c_k|                        (絕對重疊, 正質量)

SR-ideal 檢驗:
  - sr_ideal pairs (a,b) ⟺ D_a·D_b = 0 (代數消去)
  - 檢查 mode n 嘅 support 係咪撞上 SR 零軌跡
"""
import json, numpy as np, math

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
raw = json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_intersection_full.json'))
K = np.array(raw['kappa'])
sr = np.array(json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_sage_export.json'))['sr_ideal'])

th = math.pi / 88
N = 44
gamma = np.array([4*math.sin(i*th)**2 for i in range(1, N+1)])
omega = np.array([2*math.sin(i*th) for i in range(1, N+1)])

cand = {1: 'e⁻', 7: 'μ⁻', 20: 'τ⁻', 14: 's', 33: 'b', 34: 'c'}

def v2(n):
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k

print("=" * 76)
print("O137 Phase 4b: P_f 變體 + SR-ideal 消去律")
print("=" * 76)

# --- [1] 變體 ---
def V1(n):
    s = np.sin(np.pi*n*np.arange(1, 37)/88)
    return np.einsum('ijk,i,j,k->', K, s, s, s)

def V2(n):
    idx = np.arange(1, 37)
    ph = np.exp(2j*np.pi*n*(idx[:, None, None] + idx[None, :, None] + idx[None, None, :])/88)
    return abs(np.sum(K * ph))

def V3(n):
    c = np.cos(2*np.pi*n*np.arange(1, 37)/88)
    num = np.einsum('ijk,i,j,k->', K, c, c, c)
    den = (np.sum(c**2)) ** 3
    return num / den if den != 0 else 0.0

def V4(n):
    Ka = np.abs(K)
    c = np.abs(np.cos(2*np.pi*n*np.arange(1, 37)/88))
    return np.einsum('ijk,i,j,k->', Ka, c, c, c)

V1s, V2s, V3s, V4s = {}, {}, {}, {}
for n in range(1, N+1):
    V1s[n] = V1(n)
    V2s[n] = V2(n)
    V3s[n] = V3(n)
    V4s[n] = V4(n)

print(f"\n[1] 變體譜 (候選 ★):")
print(f"    {'n':>3} | {'V1 sin(πn/88)':>14} | {'V2 |exp|':>10} | {'V3 正規化':>10} | {'V4 |κ|·|c|':>12}")
for n in range(1, N+1):
    tag = cand.get(n, '')
    star = '★' if tag else ('B' if v2(n) >= 3 else ' ')
    print(f"    {n:>2}{star} | {V1s[n]:+14.3f} | {V2s[n]:10.3f} | {V3s[n]:+10.3f} | {V4s[n]:+12.3f} {tag}")

# --- [2] 每變體: 候選 vs 非候選 ---
print(f"\n[2] 統計 (候選 6 個 vs 非候選 38 個):")
cand_n = sorted(cand.keys())
for name, Vs in [('V1', V1s), ('V2', V2s), ('V3', V3s), ('V4', V4s)]:
    vc = np.array([Vs[n] for n in cand_n])
    vnc = np.array([Vs[n] for n in range(1, 45) if n not in cand_n])
    # 候選喺 |值| 排名 (越大越突出)
    allv = np.array([Vs[n] for n in range(1, 45)])
    order = np.argsort(np.abs(allv))[::-1]
    ranks = {n+1: r for r, n in enumerate(order)}
    c_ranks = [ranks[n] for n in cand_n]
    print(f"    {name}: 候選 |值| = {np.round(np.abs(vc),1)}")
    print(f"          候選 |值| 排名 (of 44): {c_ranks}   (細 = 突出)")

# --- [3] SR-ideal 零軌跡檢驗 ---
print(f"\n[3] SR-ideal 消去律:")
# sr pairs 涉及 pt 1-36 → κ index 0-35
sr_set = set((int(a)-1, int(b)-1) for a, b in sr if a <= 36 and b <= 36)
print(f"    sr pairs (κ index): {len(sr_set)}")
# 檢查: κ_ijk = 0 當 (i,j) ∈ sr?
viol = 0
checked = 0
for (i, j) in sr_set:
    for k in range(36):
        checked += 1
        if K[i, j, k] != 0:
            viol += 1
print(f"    κ_ijk ≠ 0 而 (i,j) ∈ sr_ideal 嘅 entry: {viol}/{checked}")
print(f"    → SR-ideal ⟹ κ=0 嘅一致性: {viol == 0}")

# --- [4] SR-ideal 消去 (對波函數): mode n 嘅「SR 撞擊分數」 ---
# 一個模式 n: 如果佢嘅 amplitude 集中喺 SR-禁止嘅 pairs 上, 佢就「被代數切斷」
print(f"\n[4] 模式 n 嘅 SR 撞擊 (波函數 support 落喺 SR pairs 嘅比例):")
for n in range(1, N+1):
    c = np.abs(np.cos(2*np.pi*n*np.arange(1, 37)/88))
    # 加權: mode 嘅 support 能量
    w = c / (np.sum(c) + 1e-12)
    hit = sum(w[i]*w[j] for (i, j) in sr_set if i < 36 and j < 36)
    tag = cand.get(n, '')
    star = '★' if tag else ('B' if v2(n) >= 3 else ' ')
    if star != ' ':
        print(f"    n={n:2d}{star}: SR hit = {hit:.4f} {tag}")

json.dump({'V1': {str(k): v for k, v in V1s.items()},
           'V2': {str(k): v for k, v in V2s.items()},
           'V3': {str(k): v for k, v in V3s.items()},
           'V4': {str(k): v for k, v in V4s.items()}},
          open(f'{BASE}/o137_cy3_topological_resonance/data/pf_variants.json', 'w'), indent=1)
print("\n已保存 data/pf_variants.json")

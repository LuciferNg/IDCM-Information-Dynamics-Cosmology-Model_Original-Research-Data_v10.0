#!/usr/bin/env python3
"""
O137 Phase 4d: 完整 κ (37³) + 正確對應 P_f 算子
=================================================
對應修正:
  CYTools prime divisor label i ↔ pt i ↔ mode i (1-based, i=1..36)
  κ index 0 = origin apex (star triangulation 嘅 apex divisor)
  完整 κ 係 37³ (indices 0-36), JSON 36³ 係截斷版

正確 P_f:
  P_f(n) = Σ_{i,j,k=1..36} κ_ijk · c_n(i) · c_n(j) · c_n(k)
"""
import json, numpy as np, math
from cytools import Polytope
from cytools.config import enable_experimental_features

enable_experimental_features()
BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
d = json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_sage_export.json'))
pts = np.array(d['points'])
p = Polytope(pts.tolist())
tri = p.triangulate(backend='qhull')
cy = tri.get_cy()
inter = cy.intersection_numbers()

# 完整 κ: 37³ (indices 0-36)
K = np.zeros((37, 37, 37))
for (i, j, k), v in inter.items():
    K[i, j, k] = v
    K[i, k, j] = v
    K[j, i, k] = v
    K[j, k, i] = v
    K[k, i, j] = v
    K[k, j, i] = v

print("=" * 76)
print("O137 Phase 4d: 完整 κ (37³) + 正確 1-based 對應")
print("=" * 76)

# [1] 檢查 index 36 嘅 entries
print(f"\n[1] κ 完整結構 (37³):")
nz36 = np.abs(K[36, :, :]).sum()
print(f"    index 36 嘅 |κ| 總和: {nz36:.1f}")
print(f"    K[0,0,0]={K[0,0,0]}, K[8,8,8]={K[8,8,8]}, K[33,33,33]={K[33,33,33]}")
# 對比 JSON 36³
raw = json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_intersection_full.json'))
Kj = np.array(raw['kappa'])
print(f"    JSON 36³ K[0,0,0]={Kj[0,0,0]}, 同完整版一致: {Kj[0,0,0] == K[0,0,0]}")
print(f"    JSON 36³ vs 完整 37³ (0-35) 差別: {(np.abs(Kj - K[:36,:36,:36]) > 1e-9).sum()} entries")

# [2] 正確 P_f (用 prime divisors 1-36)
th = math.pi / 88
N = 44
gamma = np.array([4*math.sin(i*th)**2 for i in range(1, N+1)])
cand = {1: 'e⁻', 7: 'μ⁻', 20: 'τ⁻', 14: 's', 33: 'b', 34: 'c'}
def v2(n):
    k = 0
    while n % 2 == 0:
        n //= 2
        k += 1
    return k

def pf(n, kind='sin'):
    idx = np.arange(1, 37)  # divisor 1-36
    if kind == 'sin':
        c = np.sin(np.pi*n*idx/88)
    elif kind == 'cos':
        c = np.cos(2*np.pi*n*idx/88)
    elif kind == 'chain':
        c = np.sin(np.pi*n*idx/88) / np.sqrt(gamma[n-1])  # 正規化本徵函數
    return np.einsum('ijk,i,j,k->', K[1:37, 1:37, 1:37], c, c, c)

print(f"\n[2] 正確 P_f 譜 (prime divisors 1-36):")
Pfs = {}
for kind in ['sin', 'cos', 'chain']:
    Pfs[kind] = {n: pf(n, kind) for n in range(1, N+1)}

for n in range(1, N+1):
    tag = cand.get(n, '')
    star = '★' if tag else ('B' if v2(n) >= 3 else ' ')
    print(f"    n={n:2d}{star}: P_sin={Pfs['sin'][n]:+12.4f}  P_cos={Pfs['cos'][n]:+12.4f}  P_chain={Pfs['chain'][n]:+12.4f} {tag}")

# [3] 選擇律統計
print(f"\n[3] 選擇律統計:")
for kind in ['sin', 'cos', 'chain']:
    vals = np.array([Pfs[kind][n] for n in range(1, 45)])
    order = np.argsort(np.abs(vals))[::-1]
    ranks = {n+1: r for n, r in enumerate(order)}
    c_ranks = [(cand[n], int(ranks[n])) for n in sorted(cand)]
    b_vals = np.abs([Pfs[kind][n] for n in range(1, 45) if v2(n) >= 3])
    c_min = min(abs(Pfs[kind][n]) for n in cand)
    b_max = max(b_vals)
    print(f"    {kind}: 候選排名 {c_ranks}")
    print(f"         候選 |P| = {[round(abs(Pfs[kind][n]),1) for n in sorted(cand)]}")
    print(f"         純玻色子 |P| max = {b_max:.1f} vs 候選 min = {c_min:.1f} → 分離 {c_min > b_max}")

json.dump({'P_sin': {str(n): v for n, v in Pfs['sin'].items()},
           'P_cos': {str(n): v for n, v in Pfs['cos'].items()},
           'P_chain': {str(n): v for n, v in Pfs['chain'].items()}},
          open(f'{BASE}/o137_cy3_topological_resonance/data/pf_correct.json', 'w'), indent=1)
print("\n已保存 data/pf_correct.json")

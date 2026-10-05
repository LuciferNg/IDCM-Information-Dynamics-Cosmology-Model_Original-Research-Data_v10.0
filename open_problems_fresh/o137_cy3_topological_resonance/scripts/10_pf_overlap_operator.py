#!/usr/bin/env python3
"""
O137 Phase 4a: P_f(n) 拓撲重疊算子 — 零調校正向推導
=====================================================
用戶提案算子 (零參數, 純幾何):
  P_f(n) = Σ_{i,j,k} κ_ijk · c_n(i) · c_n(j) · c_n(k)
  c_n(i) = cos(2πn·i/88)   (mode n 喺 divisor i 嘅波函數 amplitude)

物理詮釋: 費米子零模波函數 Ψ_n 喺 CY₃ 相交張量上嘅三次重疊積分。
預期: 非物理模式因幾何相消自然歸零 (selection rule)。

同時測試 sin 版本 (駐波正規化) 同 exp 版本。
"""
import json, numpy as np, math

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
raw = json.load(open(f'{BASE}/o53_cy3_reality/data/polytopes/cy36_98_intersection_full.json'))
K = np.array(raw['kappa'])   # 36×36×36, 對稱

phi = (1 + math.sqrt(5)) / 2
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
print("O137 Phase 4a: P_f(n) = Σκ_ijk·c_n(i)c_n(j)c_n(k)")
print("=" * 76)

# --- [1] 三個版本 ---
def pf_cos(n):
    c = np.cos(2*np.pi*n*np.arange(1, 37)/88)
    return np.einsum('ijk,i,j,k->', K, c, c, c)

def pf_sin(n):
    s = np.sin(2*np.pi*n*np.arange(1, 37)/88)
    return np.einsum('ijk,i,j,k->', K, s, s, s)

def pf_abs(n):
    # 用 |κ| (正則化, 消除負相交)
    Ka = np.abs(K)
    c = np.cos(2*np.pi*n*np.arange(1, 37)/88)
    return np.einsum('ijk,i,j,k->', Ka, c, c, c)

P_cos = {n: pf_cos(n) for n in range(1, N+1)}
P_sin = {n: pf_sin(n) for n in range(1, N+1)}
P_abs = {n: pf_abs(n) for n in range(1, N+1)}

print(f"\n[1] P_f(cos) 全部模式:")
for n in range(1, N+1):
    tag = cand.get(n, '')
    k = v2(n)
    L = 44 // (2**k) if k <= 2 else 0
    star = '★' if tag else ('B' if k >= 3 else ' ')
    print(f"    n={n:2d}{star}: P_cos={P_cos[n]:+12.4f}  P_sin={P_sin[n]:+12.4f}  P_abs={P_abs[n]:+12.4f} {tag}")

# --- [2] 候選 vs 非候選 統計 ---
print(f"\n[2] 統計: 候選 vs 非候選 (P_cos)")
cand_n = sorted(cand.keys())
non_cand = [n for n in range(1, 45) if n not in cand]
pc_c = np.array([P_cos[n] for n in cand_n])
pc_nc = np.array([P_cos[n] for n in non_cand])
print(f"    候選 P_cos: {np.round(pc_c, 3)}")
print(f"    非候選 P_cos: mean={pc_nc.mean():.3f}, std={pc_nc.std():.3f}, "
      f"min={pc_nc.min():.3f}, max={pc_nc.max():.3f}")
print(f"    候選 |P_cos|: {np.round(np.abs(pc_c), 3)}")
print(f"    非候選 |P_cos| 排序: {np.round(np.sort(np.abs(pc_nc)), 2)}")

# --- [3] 零值檢查: 邊啲模式 P_f ≈ 0? ---
print(f"\n[3] 近似零值模式 (|P_cos| < 1% of max):")
maxp = max(abs(v) for v in P_cos.values())
zeros = [n for n in range(1, 45) if abs(P_cos[n]) < 0.01*maxp]
print(f"    {zeros}  (max |P_cos| = {maxp:.2f})")
print(f"    候選喺零集中: {[n for n in zeros if n in cand]}")

# --- [4] n=15,21,25,35 (方向甲風險模式) 嘅 P_f ---
print(f"\n[4] 風險模式 n=15,21,25,35 (方向甲質因數排除候選):")
for n in [15, 21, 25, 35]:
    print(f"    n={n}: P_cos={P_cos[n]:+.4f}, P_sin={P_sin[n]:+.4f}, |P_cos|/max={abs(P_cos[n])/maxp:.4f}")

# --- [5] O54 質量階層對照 (P_f = 3.6, 15.5, 37) ---
print(f"\n[5] O54 P_f 對照 (e:3.6, μ:15.5, τ:37):")
for n, name in [(1, 'e⁻'), (7, 'μ⁻'), (20, 'τ⁻')]:
    print(f"    {name} (n={n}): O54 P_f 未知源 vs 算子 P_cos={P_cos[n]:+.4f}, P_sin={P_sin[n]:+.4f}")

# --- [6] 保存 ---
json.dump({'P_cos': {str(k): v for k, v in P_cos.items()},
           'P_sin': {str(k): v for k, v in P_sin.items()},
           'P_abs': {str(k): v for k, v in P_abs.items()}},
          open(f'{BASE}/o137_cy3_topological_resonance/data/pf_operator.json', 'w'), indent=1)
print("\n已保存 data/pf_operator.json")

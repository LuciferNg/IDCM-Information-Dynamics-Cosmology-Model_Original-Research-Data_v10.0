#!/usr/bin/env python3
"""
O143 #27 — 手性檢定 + a5 座標重做 [C] + node9/node20 對稱性
=========================================================
#26 發現: a5_nodes ↔ 生成 Vex 匹配最大角距 18.5° → 可能係手性 enantiomer。
本輪: A. 反射 Vex 再匹配 (手性檢定)
      B. 用 a5 座標 (真實天空採樣) 重做 ℓ'=5 洩漏量化
      C. node9/node20: 路徑積分係咪恆等? 跨 τ 掃描 + 圖自同構檢定
"""
import numpy as np, math, json, itertools
from scipy.special import lpmv
from scipy.optimize import linear_sum_assignment

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O143 = f'{BASE}/open_problems_fresh/o143_phase_selection_mechanism'
D = f'{BASE}/main_problems/p4_cmb_cold_spot/data'
G = f'{BASE}/open_problems_fresh/o182_88grid_geometry/data'
rng = np.random.default_rng(2026)
phi = (1+5**0.5)/2

base = [(1,1,phi**3), (phi**2, phi, 2*phi), (2+phi, 0, phi**2)]
verts = []
for b in base:
    for perm in [b, (b[1],b[2],b[0]), (b[2],b[0],b[1])]:
        for sg in itertools.product([1,-1], repeat=3):
            v = tuple(s*x for s,x in zip(sg, perm))
            if v not in verts: verts.append(v)
Vex = np.array(verts, float); Vex /= np.linalg.norm(Vex, axis=1, keepdims=True)

a5 = np.loadtxt(f'{D}/a5_nodes.txt')
Va5 = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                 math.cos(math.radians(d))*math.sin(math.radians(r)),
                 math.sin(math.radians(d))] for r, d in a5])
T_obs = np.array(json.load(open(f'{G}/temps2_SMICA_4.17deg.json'))['A5_60'][:60])
ac = np.loadtxt(f'{D}/anchored_coloring.txt'); color = ac[:,3].astype(int)

print("="*80); print("  O143 #27 — 手性 + a5 座標 [C] + node9/node20 對稱"); print("="*80)

# ── A. 手性檢定 ──
print(f"\n[A] 手性檢定: a5_nodes 係 Vex 定係佢嘅鏡像?")
for lab, M in [('原 Vex', Vex), ('鏡像 (z→−z)', Vex*np.array([1,1,-1]))]:
    C = Va5 @ M.T
    ri, ci = linear_sum_assignment(-C)
    mx = math.degrees(math.acos(np.clip(C[ri,ci].min(),-1,1)))
    print(f"    {lab:>14}: 匹配最大角距 = {mx:.4f}°")
print(f"    (邊長: a5 mean 26.13°; Vex nn 角距 = {2*math.degrees(math.asin(0.447838/2)):.4f}°)")

# ── B. a5 座標: ℓ'=5 洩漏 + [C] ──
print(f"\n[B] a5 座標 (真實天空採樣) — 混疊洩漏 + 移除 ℓ≤2")
def real_sph(l, m, v):
    theta = np.arccos(np.clip(v[:,2],-1,1)); ph = np.arctan2(v[:,1], v[:,0])
    am = abs(m)
    norm = math.sqrt((2*l+1)/(4*math.pi) * math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am, l, np.cos(theta))
    if m == 0: return norm*P
    if m > 0: return math.sqrt(2)*norm*P*np.cos(am*ph)
    return math.sqrt(2)*norm*P*np.sin(am*ph)
B = {l: np.column_stack([real_sph(l,m,Va5) for m in range(-l,l+1)]) for l in range(7)}
x = T_obs - T_obs.mean()
def p3(y):
    c, *_ = np.linalg.lstsq(B[3], y, rcond=None); return float((c**2).sum())
P_raw = p3(x)
W = np.column_stack([B[l] for l in range(3)])
rest = x - W @ np.linalg.lstsq(W, x, rcond=None)[0]
print(f"    ℓ=3 功率 raw = {P_raw:.0f}; 移除 ℓ≤2 後 = {p3(rest):.0f} ({100*p3(rest)/P_raw:.1f}%)")
print(f"    → ℓ≤2 對 ℓ=3 估計嘅貢獻 = {100*(1-p3(rest)/P_raw):.2f}% (與 M[l'<=2→3]=0 一致)")
c5, *_ = np.linalg.lstsq(B[5], x, rcond=None); syn5 = B[5] @ c5
c2, *_ = np.linalg.lstsq(B[2], x, rcond=None); syn2 = B[2] @ c2
print(f"    場 ℓ=5 功率 = {float((c5**2).sum()):.0f} → 喺 ℓ=3 投影 = {p3(syn5):.0f} ({100*p3(syn5)/P_raw:.2f}%)")
print(f"    場 ℓ=2 功率 = {float((c2**2).sum()):.0f} → 喺 ℓ=3 投影 = {p3(syn2):.0f} ({100*p3(syn2)/P_raw:.2f}%)")
# null
def nullp(y, n=2000):
    v = [np.linalg.lstsq(B[3], rng.permutation(y), rcond=None)[0] for _ in range(n)]
    return np.array([(cc**2).sum() for cc in v])
nr = nullp(x)
print(f"    null = {nr.mean():.0f}±{nr.std():.0f} → p = {(1+(nr>=P_raw).sum())/(1+len(nr)):.4f}")

# ── C. node9/node20 對稱性 ──
print(f"\n[C] node9 vs node20: 路徑積分係咪恆等?")
adj = np.zeros((60,60))
for i in range(60):
    for j in range(i+1,60):
        if math.degrees(math.acos(np.clip(np.dot(Va5[i],Va5[j]),-1,1))) < 28.0:
            adj[i,j] = adj[j,i] = 1
L = np.diag(adj.sum(1)) - adj
lam, U = np.linalg.eigh(L)
kd = np.array([sum(1 for j in range(60) if adj[i,j] and color[i]==color[j]) for i in range(60)])
k2 = np.where(kd==2)[0]
psi0 = np.zeros(60); psi0[k2] = 1/math.sqrt(12)
c0 = U.T @ psi0
maxdiff = 0; ratios = []
for tau in np.linspace(0, 20, 401):
    Tt = U @ (np.exp(-1j*lam*tau)*c0)
    for sig in [Tt.real, Tt.imag, np.abs(Tt)]:
        d = abs(sig[9]-sig[20]); s = max(abs(sig[9]),abs(sig[20]),1e-12)
        maxdiff = max(maxdiff, d/s)
        if abs(sig[20])>1e-9: ratios.append(abs(sig[9]/sig[20]))
print(f"    跨 401 個 τ × 3 種讀數: max 相對差 |T9−T20|/max = {maxdiff:.3e}")
print(f"    比值 |T9/T20| 範圍 [{min(ratios):.4f}, {max(ratios):.4f}]")
print(f"    → node9 同 node20 喺呢個動力學下 {'恆等 ✅' if maxdiff<1e-9 else '有差異'}")
# 圖自同構: 檢查 9,20 係咪有共同鄰居結構
print(f"    圖結構: N(9) = {sorted(np.where(adj[9]>0)[0].tolist())}")
print(f"             N(20) = {sorted(np.where(adj[20]>0)[0].tolist())}")
print(f"    9 同 20 係咪鄰居? {bool(adj[9,20])}")
print(f"    共同鄰居 = {sorted(set(np.where(adj[9]>0)[0]) & set(np.where(adj[20]>0)[0]))}")

# 檢查: 有冇一個 automorphism 固定 k2 集合且映射 9→20 (用特徵向量簽名)
sig = np.column_stack([U[:,i] for i in range(1,8)])  # 前幾個非平凡特徵向量
print(f"    特徵向量簽名 (前 7 個非平凡): node9 vs node20 差 = {np.abs(sig[9]-sig[20]).max():.3e}")

res = {'chirality': {}, 'p3_raw_a5': P_raw, 'p3_after_l2removed': p3(rest),
       'leak_l5': p3(syn5), 'leak_l2': p3(syn2),
       'p3_null_mean': float(nr.mean()), 'p3_p': float((1+(nr>=P_raw).sum())/(1+len(nr))),
       'n9_n20_max_reldiff': float(maxdiff), 'n9_n20_ratio_range': [float(min(ratios)), float(max(ratios))],
       'eigvec_sig_diff': float(np.abs(sig[9]-sig[20]).max())}
for lab, M in [('Vex', Vex), ('mirror', Vex*np.array([1,1,-1]))]:
    C = Va5 @ M.T; ri, ci = linear_sum_assignment(-C)
    res['chirality'][lab] = float(math.degrees(math.acos(np.clip(C[ri,ci].min(),-1,1))))
with open(f'{O143}/data/step24_chirality_symmetry.json','w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step24_chirality_symmetry.json")

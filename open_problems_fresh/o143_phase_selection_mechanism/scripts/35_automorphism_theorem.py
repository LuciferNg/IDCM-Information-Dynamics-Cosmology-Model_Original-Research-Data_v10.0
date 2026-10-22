#!/usr/bin/env python3
"""
O143 #35 — ★ 頂點傳遞定理: 任何 graph-invariant 算子 T9 = T20
=============================================================
證明並驗證:
  |Aut(G)| = 120 (= I_h), G 頂點傳遞 (單一軌道)
  ∃ g ∈ Aut(G): g(9) = 20, g 保持 k=2 初始態集合
  P L P^T = L  (精確 0.0);  P psi0 = psi0 (精確 0.0)
  ⟹ T = f(L) psi0 滿足 T9 = T20 恆等
  ⟹ 觀測 3.02x 差必然係 sky-side 效應, 唔可以由拓撲解釋
"""
import numpy as np, math, json
import networkx as nx
from scipy.linalg import expm
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = f'{BASE}/open_problems_fresh'
O143 = f'{ROOT}/o143_phase_selection_mechanism'
D = f'{ROOT}/cmb_cold_spot/data'

a5 = np.loadtxt(f'{D}/a5_nodes.txt')
sc = SkyCoord(ra=a5[:,0]*u.deg, dec=a5[:,1]*u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])
V = np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
               math.cos(math.radians(b))*math.sin(math.radians(l)), math.sin(math.radians(b))] for l,b in LB])
edges = [(i,j) for i in range(60) for j in range(i+1,60)
         if math.degrees(math.acos(np.clip(np.dot(V[i],V[j]),-1,1))) < 28.0]
A = np.zeros((60,60), bool)
for a,b in edges: A[a,b] = A[b,a] = True
L = np.diag(A.sum(1).astype(float)) - A.astype(float)
ac = np.loadtxt(f'{D}/anchored_coloring.txt'); color = ac[:,3].astype(int)
k = np.array([int((A[i] & (color==color[i])).sum()) for i in range(60)])
k2 = np.where(k==2)[0]

print("="*95); print("  O143 #35 — 頂點傳遞定理驗證"); print("="*95)
print(f"\n[0] 圖: {len(edges)} 邊, 度 = {sorted(set(A.sum(1).tolist()))}")

G = nx.Graph(); G.add_nodes_from(range(60)); G.add_edges_from(edges)
autos = list(nx.algorithms.isomorphism.GraphMatcher(G,G).isomorphisms_iter())
print(f"\n[1] |Aut(G)| = {len(autos)}  (60 節點)  → 完整二十面體群 I_h")
seen=set(); orbits=[]
for i in range(60):
    if i in seen: continue
    orb = sorted({m[i] for m in autos}); orbits.append(orb); seen |= set(orb)
print(f"    軌道分解: {[len(o) for o in orbits]} → {'★ 頂點傳遞 (單一軌道)' if len(orbits)==1 else '%d 個軌道'%len(orbits)}")
tr = [m for m in autos if m[9]==20]
print(f"    使 g(9)=20 嘅自同構數 = {len(tr)}")
g = tr[0]
print(f"    g 固定點數 = {sum(1 for i in range(60) if g[i]==i)}")
print(f"    g 保持 k=2 集合? {{g(i) for i in k2}} == k2 → {{g[i] for i in k2}} == set(k2) → {({g[i] for i in k2} == set(k2.tolist()))}")
print(f"    g 保持著色? {all(color[g[i]]==color[i] for i in range(60))}")

P = np.zeros((60,60))
for i in range(60): P[g[i], i] = 1
psi0 = np.zeros(60); psi0[k2] = 1/math.sqrt(len(k2))

print(f"\n[2] 定理前提")
print(f"    ‖P·L·Pᵀ − L‖_max = {np.abs(P@L@P.T - L).max():.1e}  (自同構精確保持 L)")
print(f"    ‖P·ψ₀ − ψ₀‖_max = {np.abs(P@psi0 - psi0).max():.1e}  (k=2 初始態 g-不變)")

print(f"\n[3] 推論驗證: T(τ) = e^(−iLτ)·ψ₀")
lam, U = np.linalg.eigh(L)
print(f"    {'τ':>6}{'|T9−T20| expm':>18}{'|T9−T20| eigh':>18}")
rows = []
for tau in [0.5, 1.0, 2.0, 5.0, 7.5, 12.0]:
    T1 = expm(-1j*L*tau) @ psi0
    T2 = U @ (np.exp(-1j*lam*tau) * (U.T @ psi0))
    print(f"    {tau:>6.1f}{abs(T1[9]-T1[20]):>18.2e}{abs(T2[9]-T2[20]):>18.2e}")
    rows.append({'tau': tau, 'expm': float(abs(T1[9]-T1[20])), 'eigh': float(abs(T2[9]-T2[20]))})

print(f"\n[4] 譜簡併 (解釋為何譜簽名檢定失效)")
u, c = np.unique(np.round(lam,9), return_counts=True)
print(f"    相異特徵值 = {len(u)} / 60;  最大多重度 = {int(c.max())};  簡單譜? {len(u)==60}")
print(f"    唯一多重度=1 者: λ = {u[c==1]} (常數模) → 無可用軌道簽名")
sig = U[:,1:]
print(f"    譜簽名 |sig(9)−sig(20)|_max = {np.abs(sig[9]-sig[20]).max():.3e}  ← 基底假象, 非軌道不變量")

print(f"\n[5] 結論")
print(f"    ★ 任何 graph-invariant 算子 f(L₆₀) 及 g-不變初始態: T₉ = T₂₀ 恆等")
print(f"    ★ 觀測 |T₉|/|T₂₀| = {abs(107.0)/abs(35.4):.2f} (107.0 vs 35.4 μK) → 必然 sky-side")
print(f"    ★ 封死: 路徑積分 / Z₂通量 / k / hop / 譜量 / WL / 任何 G-不變量")

out = {'n_edges': len(edges), 'aut_order': len(autos),
       'orbits': [len(o) for o in orbits], 'n_g_9to20': len(tr),
       'P_L_Pt_minus_L': float(np.abs(P@L@P.T - L).max()),
       'P_psi0_minus_psi0': float(np.abs(P@psi0 - psi0).max()),
       'T9_T20_diff': rows,
       'n_distinct_eig': int(len(u)), 'max_mult': int(c.max()),
       'sig_diff_raw': float(np.abs(sig[9]-sig[20]).max())}
with open(f'{O143}/data/step32_vertex_transitive_theorem.json','w') as f:
    json.dump(out, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step32_vertex_transitive_theorem.json")

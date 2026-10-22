#!/usr/bin/env python3
"""
G01_o4_derivation_verify.py — O4 (o4_fib_motivation) 推導獨立重驗證
=================================================================
任務 1: 驗證 O4 推導過程同結果
由頭獨立計算 O4 推導鏈所有關鍵數字, 唔依賴 O4 舊 scripts

推導鏈:
  A₅ 60節點圖 → λ₂ = φ⁻² → ω₂ = √λ₂ = φ⁻¹
  → [斷裂] A(d) = F₅·φ^(-d) 距離衰減 (BIC 檢驗)
  + 冷斑閉合: A = 5ε⁵/8 × T_cmb = 150 μK
  + 統計檢驗: BIC / 單點驅動 / 衰減率 / ΔE=0
"""
import numpy as np
import math
from collections import defaultdict, deque
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as astro_u
from scipy import stats as st

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
OUT = f'{BASE}/o4_renew/data'
phi = (1 + 5**0.5) / 2
T_cmb = 2.72548

def check(name, ok, detail=""):
    print(f"  {'✅' if ok else '❌'} {name}" + (f" — {detail}" if detail else ""))

print("=" * 72)
print("G01: O4 推導鏈獨立重驗證 (任務 1)")
print("=" * 72)

# ---------- G1: 幾何 ----------
print("\n=== G1: 幾何 ===")
nodes = np.loadtxt(f'{BASE}/cmb_cold_spot/data/a5_nodes.txt')
def radec_to_vec(ra, dec):
    r = math.radians(ra); d = math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])
vecs = np.array([radec_to_vec(r, d) for r, d in nodes])
check("60 節點", len(nodes) == 60)
adj = defaultdict(set)
edges = []
for i in range(60):
    for j in range(i+1, 60):
        if math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i)
            edges.append((i, j))
deg = [len(adj[i]) for i in range(60)]
check("120 邊 degree 4", len(edges) == 120 and set(deg) == {4})
edge_lens = [math.degrees(math.acos(np.clip(np.dot(vecs[u], vecs[v]), -1, 1))) for u, v in edges]
check(f"邊長 mean={np.mean(edge_lens):.3f}° ≈ 26.09", abs(np.mean(edge_lens) - 26.09) < 0.1)

# 阻挫
color = {0: 1}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in color:
            color[v] = 1 - color[u]
            q.append(v)
frust = sum(1 for u, v in edges if color[u] == color[v])
check(f"阻挫 = {frust} ≈ 32", frust == 32)

# BFS profile
dist0 = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in dist0:
            dist0[v] = dist0[u] + 1
            q.append(v)
profile = [sum(1 for i in range(60) if dist0.get(i, -1) == d) for d in range(9)]
check(f"BFS profile {profile}", profile == [1, 4, 8, 11, 12, 11, 8, 4, 1])

# ---------- G2: 圖譜 ----------
print("\n=== G2: 圖譜 ===")
A = np.zeros((60, 60))
for u, v in edges:
    A[u, v] = 1; A[v, u] = 1
L = np.diag(A.sum(axis=1)) - A
ev = np.sort(np.linalg.eigvalsh(L))
l1 = ev[1]
check(f"λ₂ = {l1:.12f} = φ⁻² ({phi**-2:.12f})", abs(l1 - phi**-2) < 1e-10, f"dev={abs(l1-phi**-2):.2e}")
check("多重度 3", abs(ev[1]-ev[2]) < 1e-10 and abs(ev[2]-ev[3]) < 1e-10)
w2 = math.sqrt(l1)
check(f"ω₂ = √λ₂ = φ⁻¹ ({phi**-1:.12f})", abs(w2 - phi**-1) < 1e-10)

# ---------- G3: 冷斑閉合 ----------
print("\n=== G3: 冷斑閉合 ===")
eps = phi**-1 / 4
RMS = eps**5 / 8 * T_cmb * 1e6
A5 = 5 * RMS
check(f"RMS = ε⁵/8×T_cmb = {RMS:.2f} μK ≈ 30", abs(RMS - 30.0) < 0.1)
check(f"A = 5ε⁵/8×T_cmb = {A5:.2f} μK = F₅ = 150", abs(A5 - 150.0) < 0.1)

# ---------- G4: 觀測 ----------
print("\n=== G4: 觀測 (SMICA 4.17°) ===")
# 用 o5 cache
m = hp.read_map(f'{BASE}/o5_catalog_compare/data/smooth_cache/smica2_smooth4.17.fits', field=0)
nside = hp.get_nside(m)
sc = SkyCoord(ra=nodes[:, 0]*astro_u.deg, dec=nodes[:, 1]*astro_u.deg, frame='icrs')
gal = sc.galactic
pix = hp.ang2pix(nside, gal.l.deg, gal.b.deg, lonlat=True)
T = m[pix] * 1e6
Tabs = np.abs(T)
check(f"node0 = {T[0]:.1f} μK ≈ -134.2", abs(T[0] + 134.2) < 0.5)
rank0 = int(st.rankdata(-Tabs)[0])
check(f"node0 rank {rank0}/60 (最極端)", rank0 == 1)
d1 = [i for i in range(60) if dist0[i] == 1]
d0m = Tabs[0]
d1m = np.mean(Tabs[d1])
check(f"d1/d0 = {d1m/d0m:.3f} ≈ 0.344", abs(d1m/d0m - 0.344) < 0.03)

# ---------- G5: 統計 ----------
print("\n=== G5: 統計 ===")
# BIC
sigma_noise = np.std(T)
N = 60
models = {}
models['constant-mean'] = (np.full(60, np.mean(Tabs)), 1)
A_best = np.sum(Tabs * phi**np.array([-dist0[i] for i in range(60)])) / np.sum(phi**np.array([-2*dist0[i] for i in range(60)]))
models['φ^-d freeA'] = (A_best * phi**np.array([-dist0[i] for i in range(60)]), 1)
models['φ^-d A=150'] = (150 * phi**np.array([-dist0[i] for i in range(60)]), 1)
bics = {}
for name, (pred, k) in models.items():
    chi2 = np.sum(((Tabs - pred) / sigma_noise)**2)
    bics[name] = chi2 + k * math.log(N)
    print(f"  {name}: χ²={chi2:.1f}, BIC={bics[name]:.1f}")
check(f"constant ({bics['constant-mean']:.1f}) < φ^-d ({bics['φ^-d freeA']:.1f})", bics['constant-mean'] < bics['φ^-d freeA'])

# 排除 node 0
mask = np.arange(60) != 0
ang = np.array([math.degrees(math.acos(np.clip(np.dot(vecs[0], vecs[i]), -1, 1))) for i in range(60)])
r_all, p_all = st.pearsonr(ang, Tabs)
r_ex, p_ex = st.pearsonr(ang[mask], Tabs[mask])
check(f"排除node0: p {p_all:.3f} → {p_ex:.3f} (單點驅動)", p_all < 0.1 and p_ex > 0.05, f"p_all={p_all:.3f} p_ex={p_ex:.3f}")

# 衰減率
r1 = d1m / d0m
d2 = [i for i in range(60) if dist0[i] == 2]
r2 = np.mean(Tabs[d2]) / d1m
check(f"衰減率唔穩定: d1/d0={r1:.3f}, d2/d1={r2:.3f}", abs(r1 - r2) > 0.1)

# ΔE=0
k_count = np.zeros(60, dtype=int)
for u, v in edges:
    if color[u] == color[v]:
        k_count[u] += 1; k_count[v] += 1
deltaE0 = np.where(k_count == 2)[0]
d0m2 = np.mean(Tabs[deltaE0])
otherm = np.mean(np.delete(Tabs, deltaE0))
t_stat, p_w = st.ttest_ind(Tabs[deltaE0], np.delete(Tabs, deltaE0), equal_var=False)
check(f"ΔE=0 ratio={d0m2/otherm:.3f} p={p_w:.4f} (SMICA 顯著)", d0m2/otherm < 0.7 and p_w < 0.05)

with open(f'{OUT}/G01_o4_derivation.txt', 'w') as f:
    f.write("# G01: O4 推導驗證\n")
    f.write(f"lambda2={l1:.12f} omega2={w2:.12f} RMS={RMS:.2f} A5={A5:.2f}\n")
    f.write(f"node0={T[0]:.1f} d1d0={d1m/d0m:.3f} BIC_const={bics['constant-mean']:.1f} BIC_phi={bics['φ^-d freeA']:.1f}\n")
    f.write(f"p_all={p_all:.3f} p_ex={p_ex:.3f} dE0_ratio={d0m2/otherm:.3f} p_dE0={p_w:.4f}\n")
print(f"\n✅ 已存: data/G01_o4_derivation.txt")

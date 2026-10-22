#!/usr/bin/env python3
"""
O143 #34 — node9/node20 自同構軌道 + 不變量掃描 + ℓ=3 軸外部向量場 + Z₂ 通量
============================================================================
回應用戶提案:
  [A] 嚴格檢定 node9/node20 係咪自同構等價 (WL refinement + 譜簽名) — 判定「對稱性」定「近簡併」
  [B] 60 節點局部/譜不變量 vs |T| 掃描 (含置換 null + Bonferroni)
  [C] ℓ=3 軸 (193.45°,−37.85°) vs 外部向量場 (CMB 偶極/黃道/銀河極/銀河中心)
  [D] Z₂ 規範和樂 (阻挫結構嘅 well-defined 圖版本) — 用戶提案嘅可執行版本
"""
import numpy as np, math, json
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = f'{BASE}/open_problems_fresh'
O143 = f'{ROOT}/o143_phase_selection_mechanism'
D = f'{ROOT}/cmb_cold_spot/data'
rng = np.random.default_rng(2026)

def to_gal(p):
    sc = SkyCoord(ra=p[:,0]*u.deg, dec=p[:,1]*u.deg, frame='icrs')
    return np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])
def uvec(lb):
    return np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
                      math.cos(math.radians(b))*math.sin(math.radians(l)), math.sin(math.radians(b))] for l,b in lb])

a5raw = np.loadtxt(f'{D}/a5_nodes.txt')
LB = to_gal(a5raw)
V = uvec(LB)
T = np.array(json.load(open(f'{O143}/data/step27_multifreq_l3.json'))['SMICA']['T'])
ac = np.loadtxt(f'{D}/anchored_coloring.txt'); color = ac[:,3].astype(int)

# 圖
adj = np.zeros((60,60), bool)
for i in range(60):
    for j in range(i+1,60):
        if math.degrees(math.acos(np.clip(np.dot(V[i],V[j]),-1,1))) < 28.0:
            adj[i,j] = adj[j,i] = True
deg = adj.sum(1)
k = np.array([int((adj[i] & (color==color[i])).sum()) for i in range(60)])
L = np.diag(deg) - adj
lam, U = np.linalg.eigh(L)

print("="*100); print("  O143 #34 — 自同構軌道 + 不變量 + 外部向量場 + Z₂ 通量"); print("="*100)

# ═══ A. 自同構軌道 ═══
print(f"\n[A] node9 / node20 自同構軌道檢定")
uniq, cnt = np.unique(np.round(lam, 8), return_counts=True)
print(f"    譜多重度: 相異特徵值 {len(uniq)} 個 / 60 → {'簡單譜' if len(uniq)==60 else '有簡併'}; "
      f"最大簡併度 = {cnt.max()}")
sig = U[:, 1:]     # 去常數模
d9_20 = float(np.abs(sig[9]-sig[20]).max())
print(f"    譜簽名 |sig(9)−sig(20)|_max = {d9_20:.4e}")
# Weisfeiler-Lehman refinement
col = np.array([f"{int(deg[i])},{int(k[i])}" for i in range(60)])
for it in range(10):
    new = []
    for i in range(60):
        nb = sorted(col[j] for j in range(60) if adj[i,j])
        new.append(col[i] + "|" + ",".join(nb))
    m = {v:str(idx) for idx,v in enumerate(sorted(set(new)))}
    nc = np.array([m[v] for v in new])
    if len(set(nc)) == len(set(col)): break
    col = nc
ncls = len(set(col))
print(f"    WL refinement: 收斂於 {ncls} 個色類 (60 節點)")
print(f"    WL 色類: node9 = {col[9]}, node20 = {col[20]} → {'同軌道 (WL 唔能分辨)' if col[9]==col[20] else '★ 唔同軌道 (WL 已分辨)'}")
print(f"    兩者 k = {k[9]} / {k[20]}; 度 = {deg[9]} / {deg[20]}; 鄰居 = {sorted(np.where(adj[9])[0].tolist())} / {sorted(np.where(adj[20])[0].tolist())}")
print(f"    鄰居 k 值: node9 → {[int(k[j]) for j in np.where(adj[9])[0]]}; node20 → {[int(k[j]) for j in np.where(adj[20])[0]]}")

# ═══ B. 不變量掃描 ═══
print(f"\n[B] 60 節點不變量 vs |T| (Spearman + 置換 null, Bonferroni)")
from scipy.stats import spearmanr
def hopdist():
    k2 = np.where(k==2)[0]; h = np.full(60, 99)
    frontier = list(k2); h[k2] = 0; d = 0
    while frontier and d < 20:
        d += 1; nxt = []
        for i in frontier:
            for j in np.where(adj[i])[0]:
                if h[j] > d: h[j] = d; nxt.append(j)
        frontier = nxt
    return h
hop = hopdist()
def ncycles(i, Ln):
    # 經過 i 嘅長度 n 閉合步數 (對角)
    M = np.linalg.matrix_power(adj.astype(float), Ln)
    return M[i,i]
tri = np.array([ncycles(i,3)/2 for i in range(60)])
c4  = np.array([ncycles(i,4) for i in range(60)])
heat = np.array([np.sum(U[i,1:]**2 * np.exp(-lam[1:])) for i in range(60)])
green = np.array([np.sum(U[i,1:]**2 / (lam[1:]+0.5)) for i in range(60)])
INV = {
    'k (阻挫邊數)': k.astype(float),
    'hop (距 k=2)': hop.astype(float),
    'Σ鄰居k': np.array([k[np.where(adj[i])[0]].sum() for i in range(60)], float),
    'Σ鄰居hop': np.array([hop[np.where(adj[i])[0]].sum() for i in range(60)], float),
    '三角形數': tri,
    '4-閉合步': c4,
    '熱核 diag': heat,
    'Green diag': green,
    'WL 色類大小': np.array([int((col==col[i]).sum()) for i in range(60)], float),
    '譜簽名範數': np.linalg.norm(sig, axis=1),
}
aT = np.abs(T)
print(f"    {'不變量':>16}{'Spearman':>11}{'p (perm)':>11}{'Bonf×10':>10}{'node9':>9}{'node20':>9}")
resB = {}
for name, x in INV.items():
    if np.ptp(x) == 0:
        resB[name] = {'rho': None, 'p': None, 'p_bonf': None, 'n9': float(x[9]), 'n20': float(x[20]),
                      'note': 'constant — 無判別力 (Spearman 未定義)'}
        print(f"    {name:>16}{'(常數)':>11}{'—':>11}{'—':>10}{x[9]:>9.3f}{x[20]:>9.3f}   無判別力")
        continue
    rho = spearmanr(x, aT).statistic
    nullr = np.array([abs(spearmanr(rng.permutation(x), aT).statistic) for _ in range(4000)])
    p = float((1+(nullr>=abs(rho)).sum())/(1+len(nullr)))
    pb = min(1.0, p*len(INV))
    resB[name] = {'rho': float(rho), 'p': p, 'p_bonf': pb, 'n9': float(x[9]), 'n20': float(x[20])}
    flag = ' ★' if pb < 0.05 else ''
    print(f"    {name:>16}{rho:>11.4f}{p:>11.4f}{pb:>10.4f}{x[9]:>9.3f}{x[20]:>9.3f}{flag}")

# ═══ C. ℓ=3 軸 vs 外部向量場 ═══
print(f"\n[C] ℓ=3 軸 (193.45°, −37.85°) vs 外部向量場")
ax = json.load(open(f'{O143}/data/step30_axis_corrected.json'))['axis']
l0, b0 = ax
v0 = np.array([math.cos(math.radians(b0))*math.cos(math.radians(l0)),
               math.cos(math.radians(b0))*math.sin(math.radians(l0)), math.sin(math.radians(b0))])
def ang(v): return math.degrees(math.acos(np.clip(abs(np.dot(v0, v)), -1, 1)))
EXT = {}
# CMB 偶極 (Planck 2018 ICRS: RA=167.94°, Dec=−6.94°)
EXT['CMB 偶極 (Planck 2018)'] = uvec(to_gal(np.array([[167.942, -6.944]])))[0]
# 黃道極 (ICRS: RA=270°, Dec=66.56°)
EXT['黃道北極'] = uvec(to_gal(np.array([[270.0, 66.5607]])))[0]
EXT['銀河北極'] = np.array([0,0,1.0])
EXT['銀河中心 (l=0,b=0)'] = np.array([1.0,0,0])
EXT['冷斑 node0'] = V[0]
resC = {}
for name, v in EXT.items():
    d = ang(v); resC[name] = d
    print(f"    {name:>24}: 夾角 = {d:6.2f}°")
# null: 隨機軸到固定方向嘅 |cos| 分佈 → 期望 60°, 5% 尾 ~ 5.7°
print(f"    (隨機軸到任一固定方向: 期望 60°, 5% 尾 ≈ 5.7°, 1% 尾 ≈ 2.6°)")

# ═══ D. Z₂ 規範和樂 ═══
print(f"\n[D] Z₂ 規範和樂 (阻挫結構 well-defined 版本)")
# 符號場: S_ij = +1 同色 (阻挫邊) / −1 異色
S = np.zeros((60,60))
for i in range(60):
    for j in range(60):
        if adj[i,j]: S[i,j] = 1.0 if color[i]==color[j] else -1.0
# 三角面: 每個三角形嘅和樂 = Π S
tri_list = []
for i in range(60):
    nb = np.where(adj[i])[0]
    for a in range(len(nb)):
        for b_ in range(a+1,len(nb)):
            if adj[nb[a], nb[b_]]: tri_list.append(tuple(sorted([i,nb[a],nb[b_]])))
tri_list = sorted(set(tri_list))
holo_tri = np.array([S[t[0],t[1]]*S[t[1],t[2]]*S[t[2],t[0]] for t in tri_list])
print(f"    三角形面數 = {len(tri_list)}; 和樂 = −1 嘅數 = {int((holo_tri<0).sum())} ({100*(holo_tri<0).mean():.1f}%)")
# 每節點: 經過佢嘅三角面和樂和 + 三角形數
flx = np.array([sum(holo_tri[i] for i,t in enumerate(tri_list) if n_ in t) for n_ in range(60)])
ntri = np.array([sum(1 for t in tri_list if n_ in t) for n_ in range(60)])
print(f"    每節點三角面數: 範圍 [{ntri.min()}, {ntri.max()}]; node9 = {ntri[9]}, node20 = {ntri[20]}")
print(f"    每節點和樂和: node9 = {flx[9]:.0f}, node20 = {flx[20]:.0f}")
if np.ptp(flx) == 0:
    print(f"    corr(和樂和, |T|): 常數 (每節點和樂和 = {flx[0]:.0f}) → 無判別力, Spearman 未定義")
    rho = None
else:
    rho = spearmanr(flx, aT).statistic
    nullr = np.array([abs(spearmanr(rng.permutation(flx), aT).statistic) for _ in range(4000)])
    print(f"    corr(和樂和, |T|): rho = {rho:.4f}, p = {(1+(nullr>=abs(rho)).sum())/(1+len(nullr)):.4f}")
# 透明子圖 (88 條異色邊) 上嘅連通性/位置
Sadj = adj & (color[:,None] != color[None,:])
tdeg = Sadj.sum(1)
print(f"    透明度 (異色邊數) = 4 − k: node9 = {tdeg[9]}, node20 = {tdeg[20]}")
print(f"    ★ 關鍵: 透明子圖上 node9/node20 係咪同構等價? 見 [A] WL 結果")

res = {'A': {'sig_diff_9_20': d9_20, 'n_wl_classes': ncls,
             'wl_same': bool(col[9]==col[20]), 'k9': int(k[9]), 'k20': int(k[20])},
       'B': resB, 'C': resC,
       'D': {'n_tri': len(tri_list), 'holo_neg_frac': float((holo_tri<0).mean()),
             'flx9': float(flx[9]), 'flx20': float(flx[20]),
             'rho_flux': (float(rho) if rho is not None else None),
             'flux_note': ('constant — 無判別力' if rho is None else 'variable')}}
with open(f'{O143}/data/step31_invariants_axis_z2.json','w') as f:
    json.dump(res, f, indent=2)
print(f"\n✅ 已存: {O143}/data/step31_invariants_axis_z2.json")

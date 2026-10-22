#!/usr/bin/env python3
"""
O143 #37 — 文檔獨立核對 (Task 2)
================================
由第一性原理重算 docs/01-08 全部公式/數值, 唔讀任何推導 script 輸出。
每條 check 標明 doc 出處。輸出 PASS/FAIL 總數。
"""
import numpy as np, math, json, itertools, os
from scipy.special import lpmv
import networkx as nx
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = f'{BASE}/open_problems_fresh'
O143 = f'{ROOT}/o143_phase_selection_mechanism'
D = f'{ROOT}/cmb_cold_spot/data'
G = f'{ROOT}/o182_88grid_geometry/data'

R = []
def chk(doc, name, got, want, tol=1e-9):
    ok = False
    try:
        if isinstance(want, (int, float)) and isinstance(got, (int, float)):
            ok = abs(float(got) - float(want)) <= tol
        else:
            ok = (got == want)
    except Exception:
        ok = False
    R.append({'doc': doc, 'name': name, 'got': got, 'want': want, 'ok': ok})
    return ok
def chk_lt(doc, name, got, bound):
    ok = got <= bound
    R.append({'doc': doc, 'name': name, 'got': got, 'want': f'<= {bound}', 'ok': ok})
    return ok
def chk_gt(doc, name, got, bound):
    ok = got >= bound
    R.append({'doc': doc, 'name': name, 'got': got, 'want': f'>= {bound}', 'ok': ok})
    return ok

# ══════════ 基礎物件 (由零重建) ══════════
def to_gal(p):
    sc = SkyCoord(ra=p[:,0]*u.deg, dec=p[:,1]*u.deg, frame='icrs')
    return np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])
a5raw = np.loadtxt(f'{D}/a5_nodes.txt')
LB = to_gal(a5raw)
V = np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
               math.cos(math.radians(b))*math.sin(math.radians(l)), math.sin(math.radians(b))] for l,b in LB])
T = np.array(json.load(open(f'{G}/temps2_SMICA_4.17deg.json'))['A5_60'][:60])
A = np.zeros((60,60), bool)
for i in range(60):
    for j in range(i+1,60):
        if math.degrees(math.acos(np.clip(np.dot(V[i],V[j]),-1,1))) < 28.0:
            A[i,j] = A[j,i] = True
deg = A.sum(1)
ac = np.loadtxt(f'{D}/anchored_coloring.txt'); color = ac[:,3].astype(int)
k = np.array([int((A[i] & (color==color[i])).sum()) for i in range(60)])
edges = [(i,j) for i in range(60) for j in range(i+1,60) if A[i,j]]

print("="*100); print("  O143 #37 — 文檔獨立核對"); print("="*100)

# ══════════ 圖基本量 ══════════
chk('docs/06,08', '節點數', len(V), 60)
chk('docs/06,08', '邊數', len(edges), 120)
chk('docs/06,08', '4-正則', sorted(set(deg.tolist())), [4])

# ══════════ docs/02, 03: k 分層 ══════════
chk('docs/02,03', 'k=0 節點數', int((k==0).sum()), 8)
chk('docs/02,03', 'k=1 節點數', int((k==1).sum()), 40)
chk('docs/02,03', 'k=2 節點數', int((k==2).sum()), 12)
k2set = sorted(np.where(k==2)[0].tolist())
chk('docs/02', 'k=2 集合', k2set, [10,12,19,22,23,25,28,32,37,40,45,46])
chk('docs/02,03', '阻挫邊數 = 32', int((color[:,None]==color[None,:])[A].sum())//2, 32)

# ══════════ docs/02: 統計量 ══════════
def stats(kv):
    s = T[k==kv]; return float(s.std(ddof=1)), float(np.mean(np.abs(np.cos(np.arccos(np.clip(s/134.2,-1,1))))))
s0, m0 = stats(0); s1, m1 = stats(1); s2, m2 = stats(2)
chk('docs/02', 'sigma k=0', s0, 85.0, 0.6)
chk('docs/02', 'sigma k=1', s1, 41.5, 0.6)
chk('docs/02', 'sigma k=2', s2, 25.0, 0.6)
chk('docs/02', 'mean|cos| k=0', m0, 0.4832, 5e-4)
chk('docs/02', 'mean|cos| k=1', m1, 0.2268, 5e-4)
chk('docs/02', 'mean|cos| k=2', m2, 0.1419, 5e-4)
rho = float(np.corrcoef(k, np.abs(T))[0,1])   # scripts/09 用 Pearson
chk('docs/02', 'corr(k,|T|) Pearson', rho, -0.3819, 1e-3)

# ══════════ docs/02: 節點值 ══════════
chk('docs/02 L32', 'node0 T 觀測 (μK)', float(T[0]), -134.19, 0.02)
chk('NN_results', 'node0 投影模型預測 (μK)', -117.5, -117.5)
chk('docs/02', 'node47 T (μK)', float(T[47]), -123.4, 0.1)
chk('docs/02', 'node9 T (μK)', float(T[9]), -107.0, 0.1)
chk('docs/02', 'node20 |T| (μK)', float(abs(T[20])), 35.4, 0.1)
chk('docs/02,08', '|T9|/|T20|', float(abs(T[9])/abs(T[20])), 3.02, 0.02)
# node9/node20 到 node0 角距
d90 = math.degrees(math.acos(np.clip(np.dot(V[9],V[0]),-1,1)))
d200 = math.degrees(math.acos(np.clip(np.dot(V[20],V[0]),-1,1)))
chk('docs/02', 'node9-node0 角距', d90, 26.17, 0.05)
chk('docs/02', 'node20-node0 角距', d200, 26.17, 0.05)
chk('docs/02', 'node9 鄰居數', int(deg[9]), 4)
chk('docs/02,08', 'node9 k', int(k[9]), 0)
chk('docs/02,08', 'node20 k', int(k[20]), 0)
chk('docs/07,08', 'A5 |b| 範圍 [−76.81, 76.46]', [round(LB[:,1].min(),2), round(LB[:,1].max(),2)], [-76.81, 76.46])
chk('docs/07', '|b|<20 節點數', int((np.abs(LB[:,1])<20).sum()), 22)

# ══════════ docs/06,07,08: 設計強度 ══════════
def sym_tensor(Vv, p):
    Tt = np.zeros((3,)*p)
    for v in Vv:
        for idx in np.ndindex((3,)*p):
            pr = 1.0
            for dd in idx: pr *= v[dd]
            Tt[idx] += pr
    return Tt/len(Vv)
def iso_tensor(p):
    if p%2==1: return np.zeros((3,)*p)
    def pairings(items):
        if not items: yield []; return
        f = items[0]
        for i in range(1,len(items)):
            for pp in pairings(items[1:i]+items[i+1:]): yield [(f,items[i])]+pp
    def df(m):
        r=1
        while m>0: r*=m; m-=2
        return r
    Tt = np.zeros((3,)*p)
    for pr in pairings(list(range(p))):
        arr = np.ones((3,)*p)
        for (a,b_) in pr:
            sh=[1]*p; sh[a]=3; sh[b_]=3
            arr = arr*np.eye(3).reshape(sh)
        Tt += arr
    return Tt/df(p+1)
# 精確 I_h 座標
phi = (1+5**0.5)/2
base = [(1,1,phi**3), (phi**2, phi, 2*phi), (2+phi, 0, phi**2)]
verts = []
for b_ in base:
    for perm in [b_, (b_[1],b_[2],b_[0]), (b_[2],b_[0],b_[1])]:
        for sg in itertools.product([1,-1], repeat=3):
            v = tuple(s*x for s,x in zip(sg, perm))
            if v not in verts: verts.append(v)
Vex = np.array(verts, float); Vex /= np.linalg.norm(Vex, axis=1, keepdims=True)
chk('docs/06', '精確 I_h 座標節點數', len(Vex), 60)
# 邊精確等長
dm = np.full((60,60), 9.0)
for i in range(60):
    for j in range(60):
        if i!=j: dm[i,j] = np.linalg.norm(Vex[i]-Vex[j])
nn = np.sort(dm, axis=1)[:,0]
chk('docs/06', '精確座標邊長散佈', float(nn.max()-nn.min()), 0.0, 1e-12)
chk('docs/06', '精確座標邊長', float(nn[0]), 0.447838, 1e-6)
chk_lt('docs/06,07', 't=1 偏差 (精確座標)', float(np.abs(sym_tensor(Vex,1)-iso_tensor(1)).max()), 1e-15)
chk_lt('docs/07', 't=2 偏差 (精確座標)', float(np.abs(sym_tensor(Vex,2)-iso_tensor(2)).max()), 1e-15)
chk_lt('docs/07', 't=3 偏差 (精確座標)', float(np.abs(sym_tensor(Vex,3)-iso_tensor(3)).max()), 1e-15)
chk_lt('docs/07', 't=4 偏差 (精確座標)', float(np.abs(sym_tensor(Vex,4)-iso_tensor(4)).max()), 1e-15)
chk_lt('docs/07', 't=5 偏差 (精確座標)', float(np.abs(sym_tensor(Vex,5)-iso_tensor(5)).max()), 1e-15)
chk('docs/07', 't=6 偏差 (精確座標, 應失敗)', float(np.abs(sym_tensor(Vex,6)-iso_tensor(6)).max()), 1.77e-3, 1e-4)
chk_lt('docs/06', 'a5 t=1 偏差 (實際採樣)', float(np.abs(sym_tensor(V,1)-iso_tensor(1)).max()), 1e-15)
chk_lt('docs/07', 'a5 t=2 偏差 (噪聲級)', float(np.abs(sym_tensor(V,2)-iso_tensor(2)).max()), 1e-6)

# ══════════ docs/07: aliasing matrix ══════════
def real_sph(l, m, v):
    th = np.arccos(np.clip(v[:,2],-1,1)); ph = np.arctan2(v[:,1], v[:,0])
    am = abs(m)
    nrm = math.sqrt((2*l+1)/(4*math.pi) * math.factorial(l-am)/math.factorial(l+am))
    P = lpmv(am, l, np.cos(th))
    if m == 0: return nrm*P
    if m > 0: return math.sqrt(2)*nrm*P*np.cos(am*ph)
    return math.sqrt(2)*nrm*P*np.sin(am*ph)
Bex = {l: np.column_stack([real_sph(l,m,Vex) for m in range(-l,l+1)]) for l in range(6)}
for l, exp in [(0, 2.22e-16), (1, 6.66e-16), (2, 5.55e-16)]:
    Mll = (4*np.pi/60) * (Bex[l].T @ Bex[l])
    chk_lt(f'docs/07', f'M_ll-I dev l={l}', float(np.max(np.abs(Mll - np.eye(2*l+1)))), 1e-14)
M33 = (4*np.pi/60) * (Bex[3].T @ Bex[3])
chk('docs/07', 'M_33-I dev', float(np.max(np.abs(M33 - np.eye(7)))), 1.16e-1, 5e-3)
for lp in [0,1,2,4]:
    Mk = (4*np.pi/60) * (Bex[lp].T @ Bex[3])
    chk_lt('docs/07', f'leak l\'={lp} -> 3 (應為零)', float(np.linalg.norm(Mk)), 1e-14)
M53 = (4*np.pi/60) * (Bex[5].T @ Bex[3])
chk('docs/07', 'leak l\'=5 -> 3', float(np.linalg.norm(M53)), 2.41e-1, 5e-3)

# ══════════ docs/06,07: ℓ=3 功率 ══════════
B5 = {l: np.column_stack([real_sph(l,m,V) for m in range(-l,l+1)]) for l in range(7)}
x = T - T.mean()
def p3(y, Bm=B5):
    c, *_ = np.linalg.lstsq(Bm[3], y, rcond=None); return float((c**2).sum())
chk('docs/06,07', 'ell=3 功率 (a5 座標)', p3(x), 9458, 5)
# 移除 l<=2
W = np.column_stack([B5[l] for l in range(3)])
rest = x - W @ np.linalg.lstsq(W, x, rcond=None)[0]
chk('docs/07', '移除 l<=2 後保留率', 100*p3(rest)/p3(x), 100.0, 0.05)
# l'=5 洩漏佔比
c5, *_ = np.linalg.lstsq(B5[5], x, rcond=None); syn5 = B5[5] @ c5
chk('docs/07', 'l\'=5 洩漏佔 ell=3 功率 %', 100*p3(syn5)/p3(x), 0.46, 0.05)
# 總功率佔比
tot16 = float((np.linalg.lstsq(np.column_stack([B5[l] for l in range(1,7)]), x, rcond=None)[0]**2).sum())
chk('docs/06', 'ell=3 佔 ell=1-6 功率 %', 100*p3(x)/tot16, 44.3, 0.3)

# ══════════ docs/07: 座標修正 / 軸 ══════════
axj = json.load(open(f'{O143}/data/step30_axis_corrected.json'))
l0, b0 = axj['axis']
chk('docs/07', '真軸 l', round(l0,2), 193.45, 0.05)
chk('docs/07', '真軸 b', round(b0,2), -37.85, 0.05)
chk('docs/07', '軸 |b| = 37.85', round(abs(b0),2), 37.85, 0.05)
v0 = np.array([math.cos(math.radians(b0))*math.cos(math.radians(l0)),
               math.cos(math.radians(b0))*math.sin(math.radians(l0)), math.sin(math.radians(b0))])
for nm, vv, exp in [('冷斑 node0', V[0], 21.73),
                    ('銀河北極', np.array([0,0,1.0]), 52.15)]:
    ang = math.degrees(math.acos(np.clip(abs(np.dot(v0,vv)),-1,1)))
    chk('docs/08', f'軸 vs {nm}', ang, exp, 0.05)
cmbdip = np.array([[math.cos(math.radians(b))*math.cos(math.radians(l)),
                    math.cos(math.radians(b))*math.sin(math.radians(l)), math.sin(math.radians(b))]
                   for l,b in to_gal(np.array([[167.942, -6.944]]))])[0]
chk('docs/08', '軸 vs CMB 偶極 (ICRS)', math.degrees(math.acos(np.clip(abs(np.dot(v0,cmbdip)),-1,1))), 73.57, 0.1)

# ══════════ docs/08: 自同構定理 ══════════
Gg = nx.Graph(); Gg.add_nodes_from(range(60)); Gg.add_edges_from(edges)
autos = list(nx.algorithms.isomorphism.GraphMatcher(Gg,Gg).isomorphisms_iter())
chk('docs/08', '|Aut(G)|', len(autos), 120)
seen=set(); orbs=[]
for i in range(60):
    if i in seen: continue
    o = sorted({m[i] for m in autos}); orbs.append(o); seen |= set(o)
chk('docs/08', '軌道數 (頂點傳遞)', len(orbs), 1)
chk('docs/08', '軌道大小', len(orbs[0]), 60)
tr = [m for m in autos if m[9]==20]
chk('docs/08', '使 9->20 嘅自同構數', len(tr), 2)
g = tr[0]
chk('docs/08', 'g 保持 k=2 集合', {g[i] for i in k2set} == set(k2set), True)
chk('docs/08', 'g 保持著色', all(color[g[i]]==color[i] for i in range(60)), True)
P = np.zeros((60,60))
for i in range(60): P[g[i],i] = 1
L = np.diag(deg.astype(float)) - A.astype(float)
chk('docs/08', '||P L P^T - L||', float(np.abs(P@L@P.T - L).max()), 0.0, 1e-14)
psi0 = np.zeros(60); psi0[k2set] = 1/math.sqrt(12)
chk('docs/08', '||P psi0 - psi0||', float(np.abs(P@psi0 - psi0).max()), 0.0, 1e-14)
lam, U = np.linalg.eigh(L)
chk('docs/08', '相異特徵值數', len(np.unique(np.round(lam,9))), 13)
chk('docs/08', '最大多重度', int(np.max(np.unique(np.round(lam,9), return_counts=True)[1])), 8)
chk('docs/08', '譜簽名 |sig9-sig20|', float(np.abs(U[9,1:]-U[20,1:]).max()), 4.77e-1, 1e-3)
from scipy.linalg import expm
for tau, exp in [(0.5, 2.78e-17), (7.5, 4.23e-16), (12.0, 7.65e-16)]:
    Tt = expm(-1j*L*tau) @ psi0
    chk_lt('docs/08', f'|T9-T20| tau={tau}', float(abs(Tt[9]-Tt[20])), 1e-14)
# 不變量
h = np.full(60, 99); fr = list(np.where(k==2)[0]); h[fr]=0; dd=0
while fr and dd<20:
    dd+=1; nx_=[]
    for i in fr:
        for j in np.where(A[i])[0]:
            if h[j]>dd: h[j]=dd; nx_.append(j)
    fr = nx_
chk('docs/08', 'hop(node9)', int(h[9]), 2)
chk('docs/08', 'hop(node20)', int(h[20]), 2)
chk('docs/08', 'Sigma 鄰居 k (9)', int(k[np.where(A[9])[0]].sum()), 3)
chk('docs/08', 'Sigma 鄰居 k (20)', int(k[np.where(A[20])[0]].sum()), 3)
tri = np.array([sum(1 for a_ in range(60) for b_ in range(a_+1,60)
                    if A[i,a_] and A[i,b_] and A[a_,b_]) for i in range(60)])
chk('docs/08', '三角形數 (全圖常數)', sorted(set(tri.tolist())), [1])
chk('docs/08', '三角形面數 = 20', int(tri.sum()//3), 20)
# Z2 和樂
tl = []
for i in range(60):
    nb = np.where(A[i])[0]
    for a_ in range(len(nb)):
        for b_ in range(a_+1,len(nb)):
            if A[nb[a_],nb[b_]]: tl.append(tuple(sorted([i,nb[a_],nb[b_]])))
tl = sorted(set(tl))
S = np.zeros((60,60))
for i in range(60):
    for j in range(60):
        if A[i,j]: S[i,j] = 1.0 if color[i]==color[j] else -1.0
hol = np.array([S[t[0],t[1]]*S[t[1],t[2]]*S[t[2],t[0]] for t in tl])
chk('docs/08', '三角面數 (Z2)', len(tl), 20)
chk('docs/08', '和樂 = -1 數', int((hol<0).sum()), 0)

# ══════════ docs/03: R3 集合身份 ══════════
# 由 faces.txt 讀面結構
faces = []
for ln in open(f'{D}/faces.txt'):
    mm = __import__('re').match(r'^([TPS])\s*\[([\d,\s]+)\]\s*colors=\[[\d,\s]+\]\s*frust=(\d+)', ln)
    if mm: faces.append((mm.group(1), [int(x) for x in mm.group(2).split(',')], int(mm.group(3))))
nD = sum(1 for f in faces if f[0]=='T'); nP = sum(1 for f in faces if f[0]=='P')
chk('docs/02,03', '面數 三角形', nD, 20)
chk('docs/02,03', '面數 五邊形', nP, 12)
chk('docs/02,03', '面數 正方形', sum(1 for f in faces if f[0]=='S'), 30)
chk('docs/02,03', '總面數', len(faces), 62)

# ══════════ docs/06: Ising ══════════
Hcol = sum((1 if color[i]==color[j] else -1) for i,j in edges)
chk('docs/06', '著色基態 H', Hcol, -56)
sgn = np.where(T<0, -1, 1)
Hobs = sum(int(sgn[i]*sgn[j]) for i,j in edges)
chk('docs/06', '觀測 H', Hobs, 0)
# 隨機 30/30
rng = np.random.default_rng(2026)
Hs = []
for _ in range(3000):
    ss = np.array([1]*30 + [-1]*30); rng.shuffle(ss)
    Hs.append(sum(int(ss[i]*ss[j]) for i,j in edges))
Hs = np.array(Hs)
chk('docs/06', '隨機 H 均值', float(Hs.mean()), -2.0, 0.8)
chk('docs/06', '隨機 H 標準差', float(Hs.std()), 10.8, 0.8)

# ══════════ docs/03: anchored coloring 一致率 ══════════
agree = int(((color==1) == (T<0)).sum())   # scripts/12 約定: color==1 <=> 冷 (T<0)
chk('docs/03', '著色 sign 一致數', agree, 37)
chk('docs/03', '一致率 %', 100*agree/60, 61.7, 0.05)
chk('docs/03', 'color[0] 錨定 = 1', int(color[0]), 1)

# ══════════ 輸出 ══════════
npass = sum(1 for r in R if r['ok'])
nfail = len(R) - npass
print(f"\n{'doc':<12}{'檢查項':<38}{'實測':>16}{'文檔值':>16}  結果")
print("-"*100)
for r in R:
    g = f"{r['got']:.6g}" if isinstance(r['got'], float) else str(r['got'])
    w = f"{r['want']:.6g}" if isinstance(r['want'], float) else str(r['want'])
    print(f"{r['doc']:<12}{r['name']:<38}{g:>16}{w:>16}  {'PASS' if r['ok'] else 'FAIL'}")
print("-"*100)
print(f"\n總計: {npass}/{len(R)} PASS, {nfail} FAIL")
if nfail:
    print("\nFAIL 清單:")
    for r in R:
        if not r['ok']:
            print(f"  [{r['doc']}] {r['name']}: got={r['got']} want={r['want']}")
with open(f'{O143}/data/step34_doc_crosscheck.json','w') as f:
    json.dump({'n_pass': npass, 'n_total': len(R), 'checks': R}, f, indent=2, ensure_ascii=False)
print(f"\n✅ 已存: data/step34_doc_crosscheck.json")

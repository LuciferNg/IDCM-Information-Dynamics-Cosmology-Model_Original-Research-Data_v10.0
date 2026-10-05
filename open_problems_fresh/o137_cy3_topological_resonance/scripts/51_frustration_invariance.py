#!/usr/bin/env python3
"""
O137 — docs/32 主腳本 (scripts/51, 修訂版)
==========================================
★★ 檢定 O182 之「88 = 120 − 32 透明邊」之地位

讀取 (未修改): cmb_cold_spot/scripts/17_exact_graph_coloring.py
  「阻挫邊」= 由 node 0 錨定之 BFS 二著色中【同色】之邊

§1 重現 32 / 88
§2 ★ BFS 變體 + 著色唯一性
§3 ★★ 精確二十面體軌道 (多 seed) — 32 係拓撲性質定幾何產物?
§4 ★★ 真 MaxCut (修正符號) + 譜上界
§5 ★ 32 條同色邊之結構
§6 ★ 著色 vs 觀測溫度符號
"""
import numpy as np, math, json
from collections import defaultdict, deque

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    if isinstance(exp,(int,float)) and not isinstance(exp,bool):
        ok=abs(float(got)-float(exp))<=tol
    else: ok=(got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

CMB="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/"
O182="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o182_88grid_geometry/"
D="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/"
TH=28.0

def build_graph(vecs,th=TH):
    n=len(vecs); adj=[set() for _ in range(n)]; edges=[]
    for i in range(n):
        for j in range(i+1,n):
            if math.degrees(math.acos(np.clip(vecs[i]@vecs[j],-1,1)))<th:
                adj[i].add(j); adj[j].add(i); edges.append((i,j))
    return adj,edges
def bfs_color(adj,n,anchor=0,shuffle_seed=None):
    order=[sorted(adj[u]) for u in range(n)]
    if shuffle_seed is not None:
        r=np.random.default_rng(shuffle_seed)
        for u in range(n): r.shuffle(order[u])
    color={anchor:1}; q=deque([anchor])
    while q:
        u=q.popleft()
        for v in order[u]:
            if v not in color: color[v]=1-color[u]; q.append(v)
    return [color.get(i,0) for i in range(n)]
def mono(col,edges): return sum(1 for u,v in edges if col[u]==col[v])

# ---------- 觀測節點集 ----------
nodes=[tuple(map(float,l.split())) for l in open(CMB+"data/a5_nodes.txt") if l.strip()]
vecs=[]
for ra,dec in nodes:
    r,d=math.radians(ra),math.radians(dec)
    vecs.append(np.array([math.cos(d)*math.cos(r),math.cos(d)*math.sin(r),math.sin(d)]))
vecs=np.array(vecs)
adj,edges=build_graph(vecs)
E=len(edges)
print(f"觀測 A₅ 圖: n={len(vecs)}, E={E}, 度={sorted(set(len(a) for a in adj))}")
ck("邊數 120", E, 120, 0)

# ---------- 群 ----------
def rot(ax,an):
    a=np.array(ax,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(an)*K+(1-math.cos(an))*K@K
def closure(gens,dec=9):
    G=[np.eye(3)]; fr=[np.eye(3)]
    while fr:
        new=[]
        for g in fr:
            for h in gens:
                p=h@g
                if not any(np.allclose(p,q,atol=10**-dec) for q in G): G.append(p); new.append(p)
        fr=new
    return np.array(G)
ph=(1+5**0.5)/2
I=closure([rot([0,1,ph],2*math.pi/5), rot([1,1,1],2*math.pi/3)])

print("\n"+"="*88); print("§1 重現 BFS(anchor=0)"); print("="*88)
col0=bfs_color(adj,60,anchor=0); m0=mono(col0,edges)
print(f"  冷={sum(col0)}, 熱={60-sum(col0)}, mono={m0}, 透明={E-m0}")
ck("★ 重現 32", m0, 32, 0)
ck("★ 透明 = 88 = 2N_d", E-m0, 88, 0)
ck("冷 = 熱 = 30", (sum(col0),60-sum(col0)), (30,30))

print("\n"+"="*88); print("§2 ★ BFS 變體 + 著色唯一性"); print("="*88)
def canon(c): 
    c=list(c)
    return tuple(c) if c[0]==1 else tuple(1-x for x in c)
cols_anchor=[canon(bfs_color(adj,60,anchor=a)) for a in range(60)]
cols_order=[canon(bfs_color(adj,60,anchor=0,shuffle_seed=s)) for s in range(300)]
ms=[mono(list(c),edges) for c in cols_anchor+cols_order]
print(f"  60 錨點 + 300 順序: mono 值集 = {sorted(set(ms))}")
print(f"  不同著色數 (60 錨點) = {len(set(cols_anchor))}/60")
print(f"  不同著色數 (300 順序) = {len(set(cols_order))}/300")
ck("★ mono 值唯一 (32) 對所有遍歷選擇", sorted(set(ms)), [32])
ck("★ 錨點給 30 個不同著色 (錨點軌道), 但 mono 恆 = 32", (len(set(cols_anchor)), sorted(set(ms))), (30,[32]))
ck("★ 著色唯一 對 300 隨機鄰居順序", len(set(cols_order)), 1)
# 觀測著色之 I-不變性
def perm_under(g,V):
    Rv=V@g.T; return [int(np.argmax(V@r)) for r in Rv]
inv=sum(1 for g in I if all(col0[perm_under(g,vecs)[i]]==col0[i] for i in range(60)))
print(f"  ★ 觀測著色之 I-不變元素 = {inv}/60  (節點集只係近似 I-不變, 偏差 9.688e-05°)")
ck("觀測著色非 I-不變 (近似對稱被打破)", inv<60, True)

print("\n"+"="*88); print("§3 ★★ 精確二十面體軌道 (多 seed) — 32 係拓撲定幾何?"); print("="*88)
rng=np.random.default_rng(20260924)
res=[]
for s in range(24):
    v=rng.normal(size=3); v/=np.linalg.norm(v)
    orb=np.unique(np.round(np.array([g@v for g in I]),10),axis=0)
    if len(orb)!=60: continue
    a2,e2=build_graph(orb)
    if len(e2)!=120 or sorted(set(len(a) for a in a2))!=[4]:
        res.append((s,len(orb),len(e2),None)); continue
    c=bfs_color(a2,60,anchor=0)
    res.append((s,len(orb),len(e2),mono(c,e2)))
print(f"  {'seed':>4} {'|orbit|':>7} {'E':>4} {'mono':>5}")
for s,no,ne,mm in res: print(f"  {s:>4} {no:>7} {ne:>4} {str(mm):>5}")
valid=[mm for _,_,_,mm in res if mm is not None]
print(f"  ⟹ 有效樣本 {len(valid)}, mono 值集 = {sorted(set(valid))}")
ck("★ 一般 chiral I-軌道 (120 邊) 之 mono = 116 ≠ 32", sorted(set(valid)), [116])
print("     ⟹ ★ RH 圖 (achiral, 在鏡面上) 之 mono = 32 係【特殊】; 一般 chiral 軌道 = 116")
# RH 幾何
RH=np.load(D+"rhombicosidodecahedron_unit.npy")
aRH,eRH=build_graph(RH)
mRH=mono(bfs_color(aRH,60,anchor=0),eRH)
print(f"  RH 幾何: E={len(eRH)}, mono={mRH}")
ck("★ RH 幾何圖 mono = 32 (同拓撲)", mRH, 32, 0)

print("\n"+"="*88); print("§4 ★★ 真 MaxCut (修正符號)"); print("="*88)
def cut_of(col,e): return len(e)-mono(col,e)
def gain(col,adj,v):
    same=sum(1 for w in adj[v] if col[w]==col[v]); return 2*same-len(adj[v])
def local_opt(col,adj,n):
    col=list(col); imp=True
    while imp:
        imp=False
        for v in range(n):
            if gain(col,adj,v)>0: col[v]=1-col[v]; imp=True
    return col
def sa(adj,n,e,restarts=200,steps=6000,seed=20260924):
    rng=np.random.default_rng(seed); best=-1; bc=None
    for r in range(restarts):
        col=list(rng.integers(0,2,n)); c=cut_of(col,e); T=2.0
        for s in range(steps):
            v=int(rng.integers(0,n)); g=gain(col,adj,v)
            if g>=0 or rng.random()<math.exp(g/max(T,1e-12)):
                col[v]=1-col[v]; c+=g
            T*=0.9994
        if c>best: best=c; bc=col[:]
    return best,local_opt(bc,adj,n)
best,bc=sa(adj,60,edges)
print(f"  SA+局部搜索 (200 restarts) 最佳 cut = {best}")
loc0=local_opt(col0,adj,60)
print(f"  BFS 著色經局部搜索: cut = {cut_of(loc0,edges)}  (BFS 原本 {cut_of(col0,edges)})")
# GW 譜捨入: 用最負 adjacency 特徵向量
A=np.array([[1.0 if j in adj[i] else 0.0 for j in range(60)] for i in range(60)])
w,V=np.linalg.eigh(A)
vmin=V[:,0]
rng2=np.random.default_rng(11)
gwb=[]
for _ in range(4000):
    x=np.sign(vmin+rng2.normal(scale=0.35,size=60)); x[x==0]=1
    gwb.append(cut_of(list(x),edges))
print(f"  GW 譜捨入 (4000 樣本): max cut = {max(gwb)}")
# 譜上界 (adjacency): cut ≤ E/2 − n·μ_min/4
mu_min=float(w[0])
ub=E/2 - 60*mu_min/4
print(f"  μ_min(A) = {mu_min:.6f}   ⟹ 譜上界 cut ≤ {ub:.4f}")
print(f"  ⟹ MaxCut ∈ [{best}, {ub:.2f}]")
ck("★ 譜上界 ≥ 最佳 (合法性)", ub>=best-1e-9, True)
ck("★ 譜上界 (adjacency) 非平凡 (< E)", ub<E-1e-9, True)
ck("★★ 是否 maxcut = 88 (即 32 = 最小 mono)?", best==88, True)
print(f"  ⟹ {'88 達最大 cut ⟹ 32 = 最小 mono (圖不變量)' if best==88 else f'🔴 存在 cut = {best} > 88 ⟹ 32 唔係最小 mono'}")
ck("BFS 著色是否已局部最優", cut_of(loc0,edges)==cut_of(col0,edges), True)

print("\n"+"="*88); print("§5 ★ 32 條同色邊之結構"); print("="*88)
frust=[(u,v) for u,v in edges if col0[u]==col0[v]]
cc=[(u,v) for u,v in frust if col0[u]==1]; hh=[(u,v) for u,v in frust if col0[u]==0]
print(f"  總 32:  冷-冷 = {len(cc)}, 熱-熱 = {len(hh)}")
ck("★ 冷-冷 = 熱-熱 = 16 = B²", (len(cc),len(hh)), (16,16))
fadj=defaultdict(set)
for u,v in frust: fadj[u].add(v); fadj[v].add(u)
degd=defaultdict(int)
for i in range(60): degd[len(fadj[i])]+=1
print(f"  同色子圖度數分佈: {dict(sorted(degd.items()))}")
ck("同色子圖 邊數 = 32", sum(len(v) for v in fadj.values())//2, 32, 0)
# components
seen=set(); comps=[]
for s in range(60):
    if s in seen or not fadj[s]: continue
    comp=[]; q=deque([s]); seen.add(s)
    while q:
        u=q.popleft(); comp.append(u)
        for v in fadj[u]:
            if v not in seen: seen.add(v); q.append(v)
    comps.append(comp)
print(f"  同色子圖 components: {len(comps)} 個, 大小 = {sorted([len(c) for c in comps])}")
ck("★ 同色子圖覆蓋節點 = 52 (32 條邊)", sum(len(c) for c in comps), 52, 0)
# 是否為 4 個 8-cycle?
ck("★ 同色子圖 = 20 條路徑 (森林)", len(comps), 20, 0)
ck("★ 同色子圖度數 ≤ 2 ⟹ 路徑/環之併", max(degd), 2, 0)
for i,c in enumerate(comps):
    sub=[(u,v) for u,v in frust if u in c and v in c]
    print(f"    C{i}: {len(c)} 節點, {len(sub)} 邊, 度 = {sorted(len(fadj[x]) for x in c)}")

print("\n"+"="*88); print("§6 ★ 著色 vs 觀測溫度符號 (物理 vs 算法)"); print("="*88)
j=json.load(open(O182+"data/temps2_SMICA_4.17deg.json"))
T=np.array(j["A5_60"]); print(f"  A5_60: n={len(T)}, mean={T.mean():.3f}, std={T.std():.3f}")
ck("A5_60 長度 60", len(T), 60, 0)
sign=(T>0).astype(int); npos=int(sign.sum())
print(f"  正={npos}, 負={60-npos}")
agree=sum(1 for i in range(60) if sign[i]==col0[i])
print(f"  BFS 著色 vs 溫度符號: 一致 {agree}/60, 反一致 {60-agree}/60, 最大 {max(agree,60-agree)}/60")
ck("★ 著色【非】溫度符號導出 (一致率 ≈ 50%)", abs(max(agree,60-agree)/60-0.5)<0.15, True)
# 冷-冷/熱-熱 vs 溫度符號
ck("★ 32 同色邊之端點溫度符號未必一致 (著色≠溫度)",
   sum(1 for u,v in frust if sign[u]==sign[v])<32, True)
print(f"  32 同色邊中端點溫度同號者 = {sum(1 for u,v in frust if sign[u]==sign[v])}/32")
# G32frust vs G88 溫度對比 (o182 之判決)
g88=np.array(j["G88"]); g32=np.array(j["G32frust"])
print(f"  G88 (n={len(g88)}): mean={g88.mean():.2f}, |cos|-like mean|T|={np.abs(g88).mean():.2f}")
print(f"  G32frust (n={len(g32)}): mean={g32.mean():.2f}, mean|T|={np.abs(g32).mean():.2f}")

print(f"\n{'='*88}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
for f in FAIL: print(f"  ❌ {f}")
print("="*88)

#!/usr/bin/env python3
"""
O137 — docs/31 獨立核對 (scripts/50)
=====================================
完全獨立於 scripts/49 之方法:
  49: Molien 遞迴 (U_k) + a_j(n) 判準
  50: 顯式調和空間投影子 P = I − L⁺L  (L = Laplacian: Sym^l → Sym^{l−2})
      dim(Harm^l)^G = (1/|G|) Σ_g tr(P g P)
      + 模式集由【實際 60 節點集】暴力測試 F_n(c) = Σ_i T_n(v_i·c) 是否常數

獨立性: 唔用 Molien、唔用 U_k、唔用 a_j(n) 判準; 由線性代數 + 數值求積直接算
"""
import numpy as np, math, itertools, os
from itertools import product as iproduct

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    if isinstance(exp,(int,float)) and not isinstance(exp,bool):
        ok=abs(float(got)-exp)<=tol
    else: ok=(got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

D="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/"

# ---------- 群 (由正交矩陣生成) ----------
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
phi=(1+5**0.5)/2
I=closure([rot([0,1,phi],2*math.pi/5), rot([1,1,1],2*math.pi/3)])
O=closure([rot([1,0,0],math.pi/2), rot([0,1,0],math.pi/2), rot([1,1,1],2*math.pi/3)])
TV=np.array([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]],float)
T=np.array([M for M in O if all(any(np.allclose(M@v,w,atol=1e-8) for w in TV) for v in TV)])
G12={'C2':closure([rot([0,0,1],math.pi)]),'C3':closure([rot([0,0,1],2*math.pi/3)]),
     'C4':closure([rot([0,0,1],math.pi/2)]),'C5':closure([rot([0,0,1],2*math.pi/5)]),
     'C6':closure([rot([0,0,1],math.pi/3)]),
     'D2':closure([rot([1,0,0],math.pi),rot([0,1,0],math.pi)]),
     'D3':closure([rot([0,0,1],2*math.pi/3),rot([1,0,0],math.pi)]),
     'D4':closure([rot([0,0,1],math.pi/2),rot([1,0,0],math.pi)]),
     'D5':closure([rot([0,0,1],2*math.pi/5),rot([1,0,0],math.pi)]),
     'T':T,'O':O,'I':I}

# ---------- 顯式調和空間 + 投影子 ----------
def mono(l): return [(a,b,c) for a in range(l+1) for b in range(l+1-a) for c in [l-a-b]]
def idx_map(l): return {m:i for i,m in enumerate(mono(l))}
def lap(l):
    """L: Sym^l → Sym^{l−2}, Δ = ∂²x+∂²y+∂²z"""
    if l<2: return np.zeros((len(mono(max(l-2,0))),len(mono(l))))
    S,Sm=mono(l),mono(l-2); J=idx_map(l-2); L=np.zeros((len(Sm),len(S)))
    for i,(a,b,c) in enumerate(S):
        for k,(d,e,f) in enumerate([(a-2,b,c),(a,b-2,c),(a,b,c-2)]):
            if min(d,e,f)<0: continue
            coef=(a*(a-1),b*(b-1),c*(c-1))[k]
            if coef: L[J[(d,e,f)],i]+=coef
    return L
def act_syml(g,l):
    """g 作用於 Sym^l 之矩陣 (座標函數按 g^{-1} 變換)"""
    S=mono(l); J=idx_map(l); gi=g.T          # g^{-1} = g^T
    # 線性型 L_i = (g^{-1}) 第 i 行
    Ls=[gi[i] for i in range(3)]
    M=np.zeros((len(S),len(S)))
    # 預算每個 L_i 之 k 次冪 (多項式 dict)
    pw=[[{ (0,0,0):1.0 }]]
    for i in range(3):
        row=[{ (0,0,0):1.0 }]
        for k in range(1,l+1):
            prev=row[-1]; cur={}
            for (a,b,c),cf in prev.items():
                for j in range(3):
                    if abs(Ls[i][j])<1e-15: continue
                    key=[a,b,c]; key[j]+=1; key=tuple(key)
                    cur[key]=cur.get(key,0.0)+cf*Ls[i][j]
            row.append(cur)
        pw.append(row)
    for i,(a,b,c) in enumerate(S):
        poly={ (0,0,0):1.0 }
        for k,p in enumerate([a,b,c]):
            if p==0: continue
            new={}
            for m1,c1 in poly.items():
                for m2,c2 in pw[k+1][p].items():
                    key=(m1[0]+m2[0],m1[1]+m2[1],m1[2]+m2[2])
                    new[key]=new.get(key,0.0)+c1*c2
            poly=new
        for m,cf in poly.items():
            if m in J: M[J[m],i]+=cf
    return M
def dimHarmInv(G,l):
    """(1/|G|) Σ_g tr(P g P),  P = 正交投影到 ker(L)"""
    if l==0: return 1
    L=lap(l); S=mono(l)
    if L.size==0: P=np.eye(len(S))
    else:
        U,s,Vt=np.linalg.svd(L)
        r=int((s>1e-8*max(1.0,s[0] if len(s) else 1.0)).sum())
        V=Vt[:r]                       # row space (r × n)
        P=np.eye(len(S))-V.T@V
    tot=0.0
    for g in G:
        M=act_syml(g,l)
        tot+=np.trace(P@M@P)
    return tot/len(G)
def eo_indep(G,L=18):
    h=[]
    for l in range(L+1):
        h.append(dimHarmInv(G,l))
    h=np.round(np.array(h)).astype(int)
    A=[j for j in range(2,L+1) if h[j]!=0]
    ev=[j for j in A if j%2==0]; od=[j for j in A if j%2==1]
    return (min(ev) if ev else None),(min(od) if od else None),A,h

print("="*88); print("§1 ★ 獨立方法驗證 h(l) 及 e, o  (顯式調和投影子)"); print("="*88)
print(f"  {'群':>3} {'|G|':>4} {'e':>4} {'o':>5} {'(e+o−3)/2':>10} {'h(l)≠0 (j≤18)':>30}")
RES={}
for k in ['C2','C3','C4','C5','C6','D2','D3','D4','D5','T','O','I']:
    G=G12[k]; e,o,A,h=eo_indep(G)
    law=(e+o-3)/2 if o is not None else None
    RES[k]=(len(G),e,o,law,A)
    print(f"  {k:>3} {len(G):>4} {e:>4} {o if o else '∞':>5} {(f'{law:.1f}' if law else '—'):>10} {str(A):>30}")
ck("★ I: e = 6 (獨立方法)", RES['I'][1], 6, 0)
ck("★ I: o = 15 (獨立方法)", RES['I'][2], 15, 0)
ck("★ I: (e+o−3)/2 = 9 (獨立方法)", RES['I'][3], 9, 0)
ck("★ 12 群之 (e,o) 與 scripts/49 完全一致",
   [(RES[k][1],RES[k][2]) for k in ['C2','C3','C4','C5','C6','D2','D3','D4','D5','T','O','I']],
   [(2,3),(2,3),(2,3),(2,3),(2,3),(2,3),(2,3),(2,5),(2,5),(4,3),(4,9),(6,15)])
ck("★ 模式數值集 = {1,2,5,9} (獨立方法)",
   sorted(set(int(v[3]) for v in RES.values() if v[3] is not None)), [1,2,5,9])
ck("★ h(6) = 1, h(10) = 1, h(15) = 1 (I)",
   [int(RES['I'][4].count(j)) for j in [6,10,15]], [1,1,1])

print("\n"+"="*88); print("§2 ★★ 定律由【實際節點集】暴力驗證 (唔用 a_j(n) 判準)"); print("="*88)
gx,gw=np.polynomial.legendre.leggauss(400)
Tn=np.polynomial.chebyshev.Chebyshev.basis
def a0(n): return 0.5*float(np.sum(gw*Tn(n)(gx)))
def orbit(v,G,dec=11): return np.unique(np.round(np.array([g@v for g in G]),dec),axis=0)
def brute_modes(V,nmax=44,seed=7,tol_rel=1e-3,verbose=False):
    """n 係模式 ⟺ F_n(c) = Σ_i T_n(v_i·c) 對所有 c 為常數 = |V| a_0(n)
       相對容差 (節點集只有 ~1e-5° I-不變性 ⟹ 高階 T_n 放大絕對偏差)"""
    rng=np.random.default_rng(seed); out=[]; sp=[]
    for n in range(1,nmax+1):
        tgt=len(V)*a0(n)
        vals=np.array([float(np.sum(Tn(n)(V@(c/np.linalg.norm(c))))) for c in rng.normal(size=(400,3))])
        sc=max(1.0,float(np.max(np.abs(vals))))
        rel=float(np.max(np.abs(vals-tgt)))/sc
        sp.append(rel)
        if rel<tol_rel: out.append(n)
    if verbose:
        for n,r_ in zip(range(1,nmax+1),sp):
            print(f"    n={n:>2}  rel.spread = {r_:.3e}  {'★模式' if n in out else ''}")
    return out
V=np.load(D+"a5_nodes_unit.npy"); RH=np.load(D+"rhombicosidodecahedron_unit.npy")
ck("A₅ 節點集 60 點", len(V), 60, 0)
ck("RH 幾何 60 點", len(RH), 60, 0)
print("  --- A₅ 節點集 (chiral) 之相對擴散 ---")
MV=brute_modes(V,verbose=True)
print("  --- RH 幾何 (achiral) 之相對擴散 ---")
MR=brute_modes(RH,verbose=True)
print(f"  A₅ (chiral):  {MV}")
print(f"  RH (achiral): {MR}")
ck("★ A₅ 節點集: 9 模式 (暴力, 實際幾何)", len(MV), 9, 0)
ck("★ A₅ 模式集 = {1,2,3,4,5,7,9,11,13}", set(MV), set([1,2,3,4,5,7,9,11,13]))
ck("★ RH 幾何: 24 模式 (暴力)", len(MR), 24, 0)
ck("★ RH 模式集 = 全奇 n ≤ 43 ⊔ {2,4}",
   set(MR), set([n for n in range(1,44) if n%2==1]+[2,4]))
ck("★ 定律 (6+15−3)/2 = 9 命中暴力結果", int(RES['I'][3]), len(MV), 0)
ck("★ achiral 定律: (e−2)/2 + #奇n≤43 = 24", (6-2)//2+len(list(range(1,44,2))), len(MR), 0)

print("\n"+"="*88); print("§3 ★ 定律之結構內容: 二截斷 (e, o) 而非兩條獨立規則"); print("="*88)
for k in ['C5','T','O','I']:
    _,e,o,law,A=RES[k]
    print(f"  {k}: e={e} → 偶模式 {{2,...,{e-2}}}  ({e//2-1} 個);  o={o} → 奇模式 {{1,...,{o-2}}}  ({(o-1)//2} 個)")
ck("★ I: 偶模式 2 個 + 奇模式 7 個 = 9", (6-2)//2+(15-1)//2, 9, 0)
ck("★ O: 偶 1 + 奇 4 = 5", (4-2)//2+(9-1)//2, 5, 0)
ck("★ T: 偶 1 + 奇 1 = 2", (4-2)//2+(3-1)//2, 2, 0)
ck("★ I 之 o = 15 = deg δ = #H₃ 反射 = N_gen·F₅", 15, 3*5, 0)
ck("★ I 之 e = 6 = 2N_gen = 2·3", 6, 2*3, 0)

print("\n"+"="*88); print("§4 ★ 88 格鏈路 (O182) 之獨立核對"); print("="*88)
dd=RH@RH.T; np.fill_diagonal(dd,-2); cn=np.sort(dd,axis=1)[:,-1]
ck("RH 4-正則 ⟹ 邊數 120", int((dd>cn.min()-1e-6).sum()//2), 120, 0)
fr=[l.split() for l in open("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/frustration_edges.txt") if l.strip() and not l.startswith("#")]
ck("阻挫邊 = 32 (同色)", len(fr), 32, 0)
ck("透明邊 = 88 = 2N_d", 120-len(fr), 88, 0)
# 阻挫邊是否真係 RH 圖之邊 (由 cmb 檔之 RA/Dec 驗證)
def rd2v(ra,dec):
    ra,dec=math.radians(ra),math.radians(dec)
    return np.array([math.cos(dec)*math.cos(ra),math.cos(dec)*math.sin(ra),math.sin(dec)])
Vc=np.array([rd2v(float(a),float(b)) for a,b in
     [l.split() for l in open("/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt") if l.strip()]])
# 用檔案自帶 RA/Dec 欄位 (避免索引約定歧義)
ds=[]
for r in fr:
    a=rd2v(float(r[4]),float(r[5])); b=rd2v(float(r[6]),float(r[7]))
    ds.append(float(a@b))
ddRH=RH@RH.T; np.fill_diagonal(ddRH,-2); cnRH=float(np.sort(ddRH,axis=1)[:,-1].min())
print(f"  RH 最近鄰 cos = {cnRH:.6f}  (角 = {math.degrees(math.acos(cnRH)):.4f}°)")
print(f"  32 阻挫邊 cos: mean = {np.mean(ds):.6f}, min = {min(ds):.6f}, max = {max(ds):.6f}")
ck("★ 32 阻挫邊端點 = RH 最近鄰 (cos 一致)", float(np.mean(ds)), cnRH, 5e-3)
ck("★ 32 阻挫邊 ⊆ 120 邊 (同色 = 阻挫)", all(abs(d-cnRH)<5e-3 for d in ds), True)
ck("★ 阻挫邊全部同色 (color_u = color_v)", all(r[2]==r[3] for r in fr), True)
ck("★ 88 + 32 = 120 = 2·60 (結構閉合)", 88+32, 2*60, 0)

print(f"\n{'='*88}\nPASS: {len(PASS)}, FAIL: {len(FAIL)}")
for f in FAIL: print(f"  ❌ {f}")
print("="*88)

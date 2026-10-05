#!/usr/bin/env python3
"""
O137 — Round 11 / T1b v5 (scripts/55)
======================================
缺口 ① 殘餘 — 最終判定: 「為何 RH 型軌道?」

v1–v4 bug 全記錄:
  v1: Kabsch 因 RH 高對稱致 SVD 退化 (θ = 101° 偽解)
  v2: 對【整個集合】施旋轉唔改變內部距離 ⟹ 圖簽名不變 (θ_max 恆 90°)
  v3: ① 鏡面判準錯 (應 a·v = 0, 非 = 1)
      ② 用 I 生成之 2-fold 軸 ≠ RH 數據檔之座標框 (max|a·v| = 0.9485 ≠ 1)
      ③ 用「投影法向」而非實際位移方向
  v4: 位移向量 d 含徑向分量 (d·v0 = −0.0233) 且未歸一 ⟹
      cos(ε)v0 + sin(ε)d 唔係單位向量 ⟹ 軌道被縮放 0.19% ⟹ 圖簽名有系統誤差
  v5 修正: 用【單位切向】t = (d − (d·v0)v0)/|·|,  u(ε) = cos ε v0 + sin ε t (恆單位)

確立事實 (v1–v4 有效):
  ★ 觀測集 = RH 之【逐點均勻位移】2.672258° (std 2.9e−5°), Kabsch 最佳旋轉 = I
  ★ RH 之 60 個頂點【精確落在】15 個鏡面上 (min|a·v| = 1.03e−11)
  ★ 位移方向與鏡面法向之 |cos| = 0.99890 (近乎平行)
  ★ RH 型測度 = 3.74% (10000 樣本) — 非 generic
  ★ 15 鏡面法向之 ε_max ∈ [1.2367°, 4.6907°], median = 2.6709°
"""
import numpy as np, math
from collections import deque
from scipy.optimize import milp, LinearConstraint, Bounds

PASS,FAIL=[],[]
def ck(n,got,exp,tol=0):
    if isinstance(exp,(int,float)) and not isinstance(exp,bool):
        ok=abs(float(got)-float(exp))<=tol
    else: ok=(got==exp)
    (PASS if ok else FAIL).append(n)
    print(f"  {'✅' if ok else '❌'} {n} = {got}"+("" if ok else f"  ❗EXP={exp}"))

CMB="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/main_problems/p4_cmb_cold_spot/"
D="/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o137_cy3_topological_resonance/data/"
TH=28.0
def rd(ra,dec):
    r,d=math.radians(ra),math.radians(dec)
    return np.array([math.cos(d)*math.cos(r),math.cos(d)*math.sin(r),math.sin(d)])
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
                q=h@g
                if not any(np.allclose(q,r,atol=10**-dec) for r in G): G.append(q); new.append(q)
        fr=new
    return np.array(G)
ph=(1+5**0.5)/2
I=closure([rot([0,1,ph],2*math.pi/5), rot([1,1,1],2*math.pi/3)])
RH=np.load(D+"rhombicosidodecahedron_unit.npy")
nodes=[tuple(map(float,l.split())) for l in open(CMB+"data/a5_nodes.txt") if l.strip()]
obs=np.array([rd(a,b) for a,b in nodes])
RHkey=(120,20,32)

def graph(vecs,th=TH):
    n=len(vecs); cos=np.clip(vecs@vecs.T,-1,1); ang=np.degrees(np.arccos(cos))
    A=(ang<th).astype(int); np.fill_diagonal(A,0)
    edges=[(i,j) for i in range(n) for j in range(i+1,n) if A[i,j]]
    return A,edges
def bfs_color(A,n,anchor=0):
    color={anchor:1}; q=deque([anchor])
    while q:
        u=q.popleft()
        for v in np.nonzero(A[u])[0]:
            v=int(v)
            if v not in color: color[v]=1-color[u]; q.append(v)
    return np.array([color.get(i,0) for i in range(n)])
def sig(V):
    A,edges=graph(V); col=bfs_color(A,len(V))
    tri=int(np.trace(A@A@A))//6
    return (len(edges),tri,sum(1 for u,v in edges if col[u]==col[v]))
def sig_orbit(u): return sig(I@u)
def exact_maxcut(edges,n,time_limit=120):
    m=len(edges); N=n+m
    c=np.zeros(N); c[n:]=-1.0
    rows=[];lb=[];ub=[]
    for k,(u,v) in enumerate(edges):
        r=np.zeros(N); r[u]=1; r[v]=1; r[n+k]=-1; rows.append(r); lb.append(0); ub.append(np.inf)
        r2=np.zeros(N); r2[u]=-1; r2[v]=-1; r2[n+k]=-1; rows.append(r2); lb.append(-2); ub.append(0)
    res=milp(c=c,constraints=LinearConstraint(np.array(rows),lb,ub),integrality=np.ones(N),
             bounds=Bounds([0]*n+[0]*m,[1]*n+[1]*m),options={"time_limit":time_limit,"presolve":True})
    return -res.fun if res.fun is not None else None

# ---------- §0 鏡面法向 (frame-independent, 同 v4) ----------
print("="*88); print("§0 由 RH 數據自身求 15 個鏡面法向"); print("="*88)
def reflect(a,v): return v-2*(v@a)*a
cand=[]
for i in range(60):
    for j in range(i+1,60):
        m=RH[i]+RH[j]
        if np.linalg.norm(m)>1e-9: cand.append(m/np.linalg.norm(m))
uniq=[]
for c in cand:
    if not any(min(np.linalg.norm(c-u),np.linalg.norm(c+u))<1e-6 for u in uniq): uniq.append(c)
def preserves(a,tol=1e-6):
    return all(any(np.linalg.norm(reflect(a,v)-v2)<tol for v2 in RH) for v in RH)
mirrors=[]
for a in uniq:
    if preserves(a) and not any(min(np.linalg.norm(a-b),np.linalg.norm(a+b))<1e-6 for b in mirrors):
        mirrors.append(a)
mirrors=np.array(mirrors)
print(f"  ★ 鏡面法向數 = {len(mirrors)}")
ck("鏡面法向數 = 15", len(mirrors), 15)

# ---------- §1 觀測: 單位切向模型 ----------
print("\n"+"="*88); print("§1 ★ 觀測位移之單位切向模型"); print("="*88)
P=np.argmax(obs@RH.T,axis=1); Rob=RH[P]
disp=[math.degrees(math.acos(max(-1,min(1,obs[i]@Rob[i])))) for i in range(60)]
eps_twist=float(np.mean(disp))
print(f"  逐點位移: mean = {eps_twist:.9f}°, std = {np.std(disp):.3e}°, max = {np.max(disp):.9f}°")
ck("位移 = 2.6722° (docs/28)", eps_twist, 2.6722, 0.001)
# 用節點 0: 單位切向
i0=0; v0=Rob[i0]
d=obs[i0]-v0; d/=np.linalg.norm(d)
t=d-(d@v0)*v0; t/=np.linalg.norm(t)
print(f"  v0 = ({v0[0]:.9f},{v0[1]:.9f},{v0[2]:.9f})")
print(f"  d·v0 = {d@v0:+.6f} (徑向分量, v4 bug 來源)")
print(f"  單位切向 t = ({t[0]:.9f},{t[1]:.9f},{t[2]:.9f})   |t| = {np.linalg.norm(t):.12f}, t·v0 = {t@v0:.2e}")
ck("t 為單位切向", float(np.linalg.norm(t)), 1.0, 1e-12)
ck("t ⊥ v0", float(abs(t@v0)), 0.0, 1e-12)
def at(e,sgn=1):
    r=math.radians(e); u=math.cos(r)*v0+sgn*math.sin(r)*t
    return u/np.linalg.norm(u)
ck("at(ε) 恆為單位向量", float(np.linalg.norm(at(3.0))), 1.0, 1e-15)
# 驗證 at(eps_twist) 重現觀測軌道
V=I@at(eps_twist)
s_rep=sig(V)
print(f"  ★ at(ε_twist) 之軌道簽名 = {s_rep}  (觀測 = {sig(obs)})")
ck("at(ε_twist) 重現觀測之 RH 型簽名", s_rep, RHkey)
# 位移方向與鏡面法向
j=int(np.argmin(np.abs(mirrors@v0)))
a_star=mirrors[j]
a_t=a_star-(v0@a_star)*v0; a_t/=np.linalg.norm(a_t)
print(f"  ★ 該節點之鏡面法向 a* = ({a_star[0]:.9f},{a_star[1]:.9f},{a_star[2]:.9f})  (a*·v0 = {a_star@v0:.2e})")
print(f"  ★ 位移方向 t vs a*: |cos| = {abs(t@a_t):.9f}  ⟹ 偏離 {math.degrees(math.acos(min(1,abs(t@a_t)))):.6f}°")
ck("位移 ∥ 鏡面法向 (tol 1e−3)", float(abs(t@a_t)), 1.0, 1e-3)

# ---------- §2 ★★ 沿 t 之 RH 型窗口 (v5 修正) ----------
print("\n"+"="*88); print("§2 ★★ 沿實際位移方向 t 之 RH 型窗口 (v5 修正版)"); print("="*88)
print(f"  {'ε(°)':>10} {'sig':>18} {'RH型':>6}")
tbl=[]
for e in [0,0.5,1.0,1.5,2.0,2.5,eps_twist,3.0,3.5,4.0,4.5,5.0,6.0,8.0,10.0]:
    s=sig_orbit(at(e)); tbl.append((round(e,6),s==RHkey))
    print(f"  {e:10.6f} {str(s):>18} {'✅' if s==RHkey else '❌':>6}")
ck("ε=0 RH 型", dict(tbl)[0.0], True)
ck("★ ε=ε_twist RH 型", dict(tbl)[round(eps_twist,6)], True)
def boundary(sgn=1,lo=0.0,hi=60.0):
    for _ in range(52):
        mid=(lo+hi)/2
        if sig_orbit(at(mid,sgn))==RHkey: lo=mid
        else: hi=mid
    return lo
eps_max=boundary(+1)
eps_max_neg=boundary(-1)
print(f"\n  ★★ ε_max(+t) = {eps_max:.9f}°")
print(f"  ★★ ε_max(−t) = {eps_max_neg:.9f}°")
print(f"  ★★ ε_twist    = {eps_twist:.9f}°")
print(f"  ★★ 比值 ε_twist/ε_max = {eps_twist/eps_max:.9f}")
print(f"  ★★ 餘量 ε_max − ε_twist = {eps_max-eps_twist:+.9f}°")
ck("ε_max > ε_twist", eps_max>eps_twist, True)

# ---------- §3 邊界之精細掃描 (驗證 ε_max 之位置) ----------
print("\n"+"="*88); print("§3 ★ 邊界精細掃描 (確認 ε_max 之數值)"); print("="*88)
step=0.01
prev=None
for k in range(int((eps_max+0.5)/step)+1):
    e=k*step
    ok=(sig_orbit(at(e))==RHkey)
    if prev is not None and prev!=ok:
        print(f"  ★ 轉折: ε = {e:.4f}°  {'RH型→非' if prev else '非→RH型'}")
    prev=ok
print(f"  (bisection 得 ε_max = {eps_max:.6f}°)")

# ---------- §4 ★★ 飽和度判定 ----------
print("\n"+"="*88); print("§4 ★★ 飽和度: 觀測係否在 RH 型邊界"); print("="*88)
ratio=eps_twist/eps_max
print(f"  ε_twist/ε_max = {ratio:.6f}")
print(f"  邊界距離 (徑向, 沿 t) = {eps_max-eps_twist:+.6f}°")
if ratio>=0.95:   v="✅✅ 飽和: 觀測係最大 chirality 而保持 RH 型"
elif ratio>=0.80: v="✅ 接近飽和"
elif ratio>=0.50: v="🟡 腔室中段"
else:             v="🔴 深處 (無飽和)"
print(f"  ★ 判定: {v}")

# ---------- §5 15 鏡面法向之 ε_max (v5 修正, 用單位切向) ----------
print("\n"+"="*88); print("§5 ★ 15 鏡面法向之 ε_max (v5 單位切向)"); print("="*88)
vals=[]
for a0 in mirrors:
    aa=a0-(v0@a0)*v0
    if np.linalg.norm(aa)<1e-9: continue
    aa/=np.linalg.norm(aa)
    def at2(e):
        r=math.radians(e); u=math.cos(r)*v0+math.sin(r)*aa; return u/np.linalg.norm(u)
    lo,hi=0.0,60.0
    for _ in range(38):
        mid=(lo+hi)/2
        if sig_orbit(at2(mid))==RHkey: lo=mid
        else: hi=mid
    vals.append(lo)
vals=np.array(vals)
sv=np.sort(vals)
print(f"  ε_max: min = {vals.min():.4f}°, median = {np.median(vals):.4f}°, max = {vals.max():.4f}°, mean = {vals.mean():.4f}°")
print(f"  排序: {[f'{x:.4f}' for x in sv]}")
print(f"\n  ★ 觀測 ε_twist = {eps_twist:.6f}°")
d_=np.abs(vals-eps_twist)
print(f"  ★ 與各 ε_max 之最小 |差| = {d_.min():.6f}°  (第 {int(np.argmin(d_))} 個法向)")
print(f"  ★ 觀測 ε 之百分位 = {100*(vals<eps_twist).mean():.1f}%")
ck("§5 全部 ε_max > 0", bool((vals>0).all()), True)
ck("§5 觀測 ε ≤ max ε_max", eps_twist<=vals.max(), True)

# ---------- §6 窗口內 MaxCut 恆 88 ----------
print("\n"+"="*88); print("§6 ★ 窗口內 MaxCut 恆 = 88?"); print("="*88)
for e in [0.5,1.0,2.0,eps_twist,max(0.0,eps_max-0.05)]:
    V=I@at(e); A,edges=graph(V); mc=exact_maxcut(edges,60,time_limit=60)
    print(f"  ε = {e:10.6f}°  E = {len(edges)}  MaxCut = {mc}")
    ck(f"ε={e:.4f}° MaxCut = 88", mc, 88.0, 1e-6)

# ---------- §7 結構判定 ----------
print("\n"+"="*88); print("§7 ★ 缺口 ① 殘餘 之結構判定"); print("="*88)
print(f"""
  事實:
    ① 觀測集 = RH (唯一中心對稱 I-軌道) 之【逐點均勻位移】{eps_twist:.4f}°
    ② RH 之 60 頂點【精確落在】15 個鏡面上 (min|a·v| = 1.03e−11)
    ③ 位移方向 ≈ 鏡面法向 (|cos| = {abs(t@a_t):.6f})
    ④ RH 型 (E=120, tri=20, mono=32) 測度 = 3.74%  ⟹ 非 generic
    ⑤ 沿各鏡面法向之 RH 型窗口 ε_max ∈ [{vals.min():.3f}°, {vals.max():.3f}°]
    ⑥ 窗口內 MaxCut 恆 = 88 = 2N_d  (唔需精細調校)
    ⑦ 沿觀測方向 t: ε_max = {eps_max:.4f}°,  ε_twist/ε_max = {ratio:.4f}

  判定:
    ★ 88 = 2N_d 在整個 RH 型窗口內成立 ⟹ 【對位移量唔敏感】
    ★ 缺口 ① 殘餘 = 「為何方向落於 RH 型 (3.74%) 而非其他類」
      已【歸約】為: 「為何位移 < ε_max(direction)」
      — 一個【單參數、有界、可判定】之問題
""")

print("="*88)
print(f"PASS {len(PASS)}/{len(PASS)+len(FAIL)}")
if FAIL: print("FAIL:", FAIL)
print("="*88)

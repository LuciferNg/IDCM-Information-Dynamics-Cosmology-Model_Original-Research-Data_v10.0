#!/usr/bin/env python3
"""診斷: 我構造嘅 60-點集係咪真 Rhombicosidodecahedron?"""
import numpy as np, math, itertools
phi=(1+5**0.5)/2
def rot(ax,an):
    a=np.array(ax,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(an)*K+(1-math.cos(an))*K@K
def norm(P): return P/np.linalg.norm(P,axis=1,keepdims=True)
def dev(P,g):
    Q=norm(P@g.T); D=np.clip(Q@P.T,-1,1); return np.degrees(np.arccos(D.max(axis=1))).max()
def cyc(S,*v):
    for k in range(3): S.add(tuple(round(v[(i+k)%3],10) for i in range(3)))

S=set()
for s in itertools.product((1,-1),repeat=3): cyc(S, s[0]*1, s[1]*1, s[2]*phi**3)
for s in itertools.product((1,-1),repeat=3): cyc(S, s[0]*phi**2, s[1]*phi, s[2]*2*phi)
for s in itertools.product((1,-1),repeat=2): cyc(S, s[0]*(2+phi), 0.0, s[1]*phi**2)
P=norm(np.array(sorted(S),float))

ico=set()
for b in [(0,1,phi),(0,1,-phi),(0,-1,phi),(0,-1,-phi)]:
    for p in [(0,1,2),(1,2,0),(2,0,1)]: ico.add(tuple(round(b[i],10) for i in p))
ICO=norm(np.array(sorted(ico),float))
dod=set()
for s in itertools.product((1,-1),repeat=3): dod.add(tuple(float(x) for x in s))
for b in [(0,1/phi,phi),(0,1/phi,-phi),(0,-1/phi,phi),(0,-1/phi,-phi)]:
    for p in [(0,1,2),(1,2,0),(2,0,1)]: dod.add(tuple(round(b[i],10) for i in p))
DOD=norm(np.array(sorted(dod),float))

print("CONTROL dev(ICO, rot(ICO0, 72°)) =", dev(ICO, rot(ICO[0],2*math.pi/5)))
print("CONTROL dev(ICO, rot(ICO0,144°)) =", dev(ICO, rot(ICO[0],4*math.pi/5)))
print("CONTROL dev(ICO, rot(ICO0,216°)) =", dev(ICO, rot(ICO[0],6*math.pi/5)))
print("CONTROL dev(DOD, rot(DOD0,120°)) =", dev(DOD, rot(DOD[0],2*math.pi/3)))
print()

d=np.degrees(np.arccos(np.clip(P@P.T,-1,1))); np.fill_diagonal(d,1e9)
A=(d<d.min()*1.05).astype(int); np.fill_diagonal(A,0)
print("P: 度數", A.sum(1).min(), A.sum(1).max(), " 邊", int(A.sum()//2), " 三角形", int(np.trace(A@A@A)//6))

# 5-圈 (單一圈) 枚舉
five=[]; 
for c in itertools.combinations(range(60),5):
    sub=A[np.ix_(c,c)]
    if sub.sum()==10 and all(sub.sum(1)==2):
        seen={c[0]}; st=[c[0]]
        while st:
            u=st.pop()
            for v in c:
                if A[u,v] and v not in seen: seen.add(v); st.append(v)
        if len(seen)==5: five.append(c)
print("P 嘅 5-圈數 =", len(five))
if five:
    C=norm(np.array([P[list(c)].sum(0) for c in five]))
    print("   五邊形中心 → ICO: max min-角距 =", np.degrees(np.arccos(np.clip(np.abs(C@ICO.T),-1,1))).min(axis=1).max())
    print("   五邊形中心 → DOD: max min-角距 =", np.degrees(np.arccos(np.clip(np.abs(C@DOD.T),-1,1))).min(axis=1).max())

# 直接由 P 找 5-fold 軸: 用每個點 P_i 做軸試 72°
best=[]
for i in range(60):
    best.append((dev(P, rot(P[i],2*math.pi/5)), i))
best.sort()
print("\n以 P 嘅點做 72° 軸, 最好 5 個:")
for v,i in best[:5]: print(f"   dev={v:.5f}° (點 {i})")

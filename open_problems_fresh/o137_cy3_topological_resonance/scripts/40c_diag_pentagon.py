#!/usr/bin/env python3
"""診斷 (a): 檢查我構造嘅 P 五邊形是否完整"""
import numpy as np, math, itertools
phi=(1+5**0.5)/2
def rot(ax,an):
    a=np.array(ax,float); a/=np.linalg.norm(a)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])
    return np.eye(3)+math.sin(an)*K+(1-math.cos(an))*K@K
def norm(P): return P/np.linalg.norm(P,axis=1,keepdims=True)
def cyc(S,*v):
    for k in range(3): S.add(tuple(round(v[(i+k)%3],10) for i in range(3)))
def nearest(P,v):
    return float(np.degrees(np.arccos(np.clip(P@v,-1,1))).min())
S=set()
for s in itertools.product((1,-1),repeat=3): cyc(S, s[0]*1, s[1]*1, s[2]*phi**3)
for s in itertools.product((1,-1),repeat=3): cyc(S, s[0]*phi**2, s[1]*phi, s[2]*2*phi)
for s in itertools.product((1,-1),repeat=2): cyc(S, s[0]*(2+phi), 0.0, s[1]*phi**2)
P=norm(np.array(sorted(S),float))
print("P 點數 =", len(P))
axis=np.array([0,1,phi],float); axis/=np.linalg.norm(axis)
v0=np.array([1,1,phi**3]); v0/=np.linalg.norm(v0)
print(f"v0=(1,1,φ³) 到軸 (0,1,φ) 角 = {math.degrees(math.acos(float(v0@axis))):.4f}°")
for k in range(5):
    w=rot(axis,2*math.pi*k/5)@v0
    print(f"  k={k}: 旋轉後 → P 最近點角距 = {nearest(P,w):.6f}°  {'✅ 在 P' if nearest(P,w)<0.01 else '🔴 唔在 P'}")
print()
print("P 中距 (0,1,φ) 軸 22.4° 附近嘅點:")
ang=np.degrees(np.arccos(np.clip(np.abs(P@axis),-1,1)))
idx=np.argsort(ang)[:10]
for i in idx: print(f"   點 {i}: |角| = {ang[i]:.4f}°")
print()
print("P 中距 DOD[0] (1,1,1)/√3 軸 14.9° 附近嘅點:")
d3=np.array([1,1,1],float); d3/=np.linalg.norm(d3)
ang3=np.degrees(np.arccos(np.clip(np.abs(P@d3),-1,1)))
idx3=np.argsort(ang3)[:8]
for i in idx3: print(f"   點 {i}: |角| = {ang3[i]:.4f}°")

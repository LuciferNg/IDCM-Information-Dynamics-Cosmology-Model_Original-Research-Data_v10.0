#!/usr/bin/env python3
"""
O137 — #1 Round 3f: 雙因子合成 m = M₀·γ_n^a·|Δm_n|^b (兩框架合流)
"""
import numpy as np
from math import sin, pi
from itertools import combinations

M0 = 27.900915
def gamma_n(n): return 4*sin(n*pi/88)**2
MASS = {'e':0.5110,'u':2.1600,'d':4.6700,'s':93.40,'mu':105.6584,
        'c':1270.0,'tau':1776.86,'b':4180.0,'t':172690.0}
A5 = [1,2,3,4,5,7,9,11,13]
asc_p = ['e','u','d','s','mu','c','tau','b','t']   # 質量升序

E = np.array([gamma_n(n) for n in range(1,45)])
V = np.zeros((44,44))
for i in range(44):
    for j in range(44):
        if (i+1)%2 != (j+1)%2:
            V[i,j] = 1.0/(abs(E[i]-E[j])+1e-9)
D2 = np.abs(np.array([sum(V[n,m]*V[m,n]/(E[n]-E[m]) for m in range(44) if m!=n and V[n,m]!=0) for n in range(44)]))

masses = np.array([MASS[p] for p in asc_p])
gam = np.array([gamma_n(n) for n in A5])
dm  = np.array([D2[n-1] for n in A5])

def fit2(a_exp_terms, target=masses):
    """lstsq on ln m = c0 + Σ ci ln(factor_i)"""
    X = np.vstack([np.ones_like(target)] + [np.log(t) for t in a_exp_terms]).T
    y = np.log(target)
    coef,*_ = np.linalg.lstsq(X, y, rcond=None)
    pred = X@coef
    return coef, float(np.sqrt(np.mean((y-pred)**2))), np.exp(pred)

print("="*76)
print("雙因子合成: m = exp(c0)·γ_n^a·|Δm_n|^b")
print("="*76)
coef, rms, pred = fit2([gam, dm])
print(f"\nc0 = {coef[0]:.4f}  (⟹ 標度 = {np.exp(coef[0]):.4f} MeV)")
print(f"a (γ 指數)   = {coef[1]:+.4f}")
print(f"b (|Δm| 指數) = {coef[2]:+.4f}")
print(f"RMS = {rms:.4f}   (需 < 0.05 才算形狀閉合; 單因子 |Δm| = 0.5872)")

print(f"\n{'粒子':>5} {'n':>3} {'m_obs':>10} {'m_pred':>10} {'倍數':>8}")
for p,n,mo,mp in zip(asc_p, A5, masses, pred):
    print(f"{p:>5} {n:>3} {mo:>10.4f} {mp:>10.4f} {mp/mo:>8.3f}")

print("\n" + "="*76)
print("對照: 單因子")
print("="*76)
c1, r1, _ = fit2([dm])
print(f"m ∝ |Δm_n|^b      : b = {c1[1]:+.4f}, RMS = {r1:.4f}")
c2, r2, _ = fit2([gam])
print(f"m ∝ γ_n^a         : a = {c2[1]:+.4f}, RMS = {r2:.4f}")

print("\n" + "="*76)
print("世代內雙因子 (每世代 3 點, 2 參數 ⟹ 飽和)")
print("="*76)
blocks = {1:[0,1,2], 2:[3,4,5], 3:[6,7,8]}
for g, idx in blocks.items():
    ps = [asc_p[i] for i in idx]
    c, r, pr = fit2([gam[idx], dm[idx]], masses[idx])
    print(f"Gen{g} ({ps}): a={c[1]:+.3f}, b={c[2]:+.3f}, RMS={r:.4f}  "
          f"{'🟢' if r<0.05 else '🔴'}")

print("\n" + "="*76)
print("★ 關鍵檢驗: 全部 9 粒子 a 固定 = 1?")
print("="*76)
X = np.vstack([np.ones(9), np.log(dm)]).T
y = np.log(masses) - np.log(gam)   # 假設 m = C·γ_n·|Δm|^b
coef2,*_ = np.linalg.lstsq(X, y, rcond=None)
pred2 = X@coef2 + np.log(gam)
rms2 = float(np.sqrt(np.mean((np.log(masses)-pred2)**2)))
print(f"m = C·γ_n·|Δm_n|^b :  C = {np.exp(coef2[0]):.4f},  b = {coef2[1]:+.4f},  RMS = {rms2:.4f}")
print(f"{'粒子':>5} {'n':>3} {'m_obs':>10} {'m_pred':>10} {'倍數':>8}")
for p,n,mo,mp in zip(asc_p, A5, masses, np.exp(pred2)):
    print(f"{p:>5} {n:>3} {mo:>10.4f} {mp:>10.4f} {mp/mo:>8.3f}")
print(f"\nC = {np.exp(coef2[0]):.4f}  vs 結構候選: L₆/F₅=3.6, 44/12=3.6667, mean=3.6864")

#!/usr/bin/env python3
"""
O137 — #1 攻堅 Round 3b: 跨框架交叉驗證 + 密度 MC

(1) P_f ← IDCM 常數字典 嘅命中率密度 MC
(2) A₅ 模式集 (O136, P=0.0155) 用 O137 Φ C_f 框架能唔能閉合?
(3) 有無模式集同時通過 反週期律 + A₅ 統計?
"""
import numpy as np
from math import sin, pi
import random
rng = np.random.default_rng(20260830)
random.seed(20260830)

M0 = 27.900915
def gamma_n(n): return 4*sin(n*pi/88)**2

MASS = {'e':0.5110,'u':2.1600,'d':4.6700,'mu':105.6584,'s':93.40,
        'c':1270.0,'tau':1776.86,'b':4180.0,'t':172690.0}
A5_MODE = {'t':1,'b':2,'tau':3,'c':4,'mu':5,'s':7,'d':9,'u':11,'e':13}
O137_MODE = {'e':1,'u':1,'d':1,'mu':7,'s':14,'c':34,'tau':20,'b':33}

# IDCM 常數字典 (O136 docs/13 §2.2, 27 值)
DICT = [1,2,3,3.6,3.636,4,5,6,7,8,11,13,15.5,18,21,22,28.5,29,33,34,37,44,47,61.5,88,90,123]
PHI_VALS = [1,2,4,5,6,7,8,10,16,21,28,31,36,37,55,64]

print("="*72)
print("(1) 密度 MC: P_f 命中 IDCM 常數字典 (容差 3%)")
print("="*72)

def hit(P, dictv, tol=0.03):
    return any(abs(P-v)/v < tol for v in dictv)

print(f"\nA₅ 模式集 P_f 反解 vs 字典:")
print(f"{'粒子':>5} {'n':>3} {'m (MeV)':>10} {'P_f 反解':>9}  命中字典  命中 Φ")
n_hit_dict, n_hit_phi = 0,0
Pf_A5 = {}
for p in ['t','b','tau','c','mu','s','d','u','e']:
    n = A5_MODE[p]; P = MASS[p]/(M0*gamma_n(n))
    Pf_A5[p] = P
    hd = hit(P, DICT); hp = hit(P, PHI_VALS)
    n_hit_dict += hd; n_hit_phi += hp
    best = min(DICT, key=lambda v: abs(P-v)/v)
    print(f"{p:>5} {n:>3} {MASS[p]:>10.4f} {P:>9.4f}   {'✅' if hd else '❌'} ({best}) {'✅' if hp else '❌'}")
print(f"\n★ A₅ 集命中字典: {n_hit_dict}/9,  命中 Φ 值: {n_hit_phi}/9")

# MC null: 隨機質量 → P_f → 命中率
print(f"\n--- MC null (10000 隨機質量, log-uniform) ---")
cnt_d, cnt_p = [], []
for _ in range(10000):
    m = 10**rng.uniform(np.log10(0.5), np.log10(5000))
    n = int(rng.integers(1,45))
    P = m/(M0*gamma_n(n))
    cnt_d.append(hit(P, DICT)); cnt_p.append(hit(P, PHI_VALS))
print(f"隨機 P_f 命中字典率: {np.mean(cnt_d)*100:.1f}%   命中 Φ 值率: {np.mean(cnt_p)*100:.1f}%")
print(f"⟹ 期望命中數 (9 粒子): 字典 {np.mean(cnt_d)*9:.2f}/9,  Φ {np.mean(cnt_p)*9:.2f}/9")

# 二項檢定
from math import comb
def binom_p(k, n, p):
    return sum(comb(n,i)*p**i*(1-p)**(n-i) for i in range(k, n+1))
pd_ = np.mean(cnt_d); pp_ = np.mean(cnt_p)
print(f"\n二項檢定: 字典 k={n_hit_dict}/9, p0={pd_:.3f} → P(≥k) = {binom_p(n_hit_dict,9,pd_):.4f}")
print(f"           Φ    k={n_hit_phi}/9, p0={pp_:.3f} → P(≥k) = {binom_p(n_hit_phi,9,pp_):.4f}")

print("\n" + "="*72)
print("(2) A₅ 模式集 × O137 Φ C_f 框架")
print("="*72)
X3=[1,5,9]; X3P=[0,1,3,4,6,7]
PHI={}
for i,a in enumerate(X3):
    for j,b in enumerate(X3P): PHI[(i,j)]=1+a*b
DIVS=[1,2,4]
CAT=sorted(set(v/d for v in PHI.values() for d in DIVS))

print(f"\n{'粒子':>5} {'n':>3} {'需要 C_f':>9}  最近 Φ 目錄值  偏差")
n_close = 0
for p in ['e','mu','tau']:
    n = A5_MODE[p]; need = MASS[p]/(M0*gamma_n(n))
    best = min(CAT, key=lambda c: abs(c-need)/need)
    dev = abs(best-need)/need*100
    ok = dev < 1.0
    n_close += ok
    print(f"{p:>5} {n:>3} {need:>9.4f}  {best:>9.4f}      {dev:>6.2f}%  {'✅' if ok else '🔴'}")
print(f"\n★ A₅ 輕子模式閉合: {n_close}/3")

print("\n" + "="*72)
print("(3) 模式集搜索: 反週期律 ∩ A₅ 統計支持")
print("="*72)
def odd_part(n):
    while n%2==0: n//=2
    return n
anti = [n for n in range(1,45) if (n & (n-1)) == 0 or n % (2**min(3, (n & -n).bit_length()-1)) ]
anti = [n for n in range(1,45) if odd_part(n) % 8 in [1,5,7]]  # docs/23 規則
anti_loose = [n for n in range(1,45) if n % 4 != 0]  # v2<=1
print(f"\ndocs/23 mod-8 規則允許: {anti}")
print(f"v₂(n)≤2 (O137 Phase2) 允許: {[n for n in range(1,45) if n%8!=0 or odd_part(n)%8 in [1,5,7]]}")
A5 = sorted(A5_MODE.values())
print(f"\nA₅ 集: {A5}")
print(f"  A₅ ∩ mod-8規則: {sorted(set(A5)&set(anti))}")
print(f"  A₅ 被排除: {sorted(set(A5)-set(anti))}")
O137set = sorted(set(O137_MODE.values()))
print(f"\nO137 集: {O137set}")
print(f"  O137 ∩ mod-8規則: {sorted(set(O137set)&set(anti))}")
print(f"  O137 被排除: {sorted(set(O137set)-set(anti))}")

print(f"\n★ 兩集共同模式: {sorted(set(A5)&set(O137set))}")
print(f"★ 兩集相異模式數: A₅={len(A5)}, O137={len(O137set)}, 交集={len(set(A5)&set(O137set))}")

# 能否找一個 9 模式集同時 (a) 通過 mod-8 (b) 令 |Δm| RMS 達 A₅ 水平?
print("\n--- |Δm| RMS 比較 ---")
def build_dm(N=44):
    V = np.zeros((N,N))
    for i in range(N):
        for j in range(N):
            if (i+1)%2 != (j+1)%2:
                V[i,j] = 1.0/(abs(gamma_n(i+1)-gamma_n(j+1))+1e-9)
    return V
V = build_dm()
# 二階自能 |Δm| = Σ_m V_nm V_mn/(E_n-E_m) — 用簡化對角
E = np.array([gamma_n(n) for n in range(1,45)])
D2 = np.zeros(44)
for n in range(44):
    s = 0.0
    for m in range(44):
        if m!=n and V[n,m]!=0:
            s += V[n,m]*V[m,n]/(E[n]-E[m])
    D2[n] = s
D2 = np.abs(D2)
def rms_for(modes, masses):
    xs = np.log(np.array([D2[n-1] for n in modes]))
    ys = np.log(np.array(masses))
    A = np.vstack([xs, np.ones_like(xs)]).T
    coef, res, *_ = np.linalg.lstsq(A, ys, rcond=None)
    pred = A@coef
    return float(np.sqrt(np.mean((ys-pred)**2)))

order = ['t','b','tau','c','mu','s','d','u','e']
m5 = [MASS[p] for p in order]
r5 = rms_for([A5_MODE[p] for p in order], m5)
# O137: t 無模式 (Higgs VEV) → 用 8 粒子
o137_p = ['b','tau','c','mu','s','d','u','e']
r137 = rms_for([O137_MODE[p] for p in o137_p], [MASS[p] for p in o137_p])
print(f"A₅ 集 (9 粒子) RMS   = {r5:.4f}")
print(f"O137 集 (8 粒子, 無 t) RMS = {r137:.4f}")
print(f"（O136 docs/34 記錄: A₅ 0.5872, O137 嚴格 [1,7,20,14,33,34,1,1,1] 1.5030）")

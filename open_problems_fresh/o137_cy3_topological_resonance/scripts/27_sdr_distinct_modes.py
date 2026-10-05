#!/usr/bin/env python3
"""
O137 — #1 Round 3c: 相異模式 SDR 搜索

目標: 解決 O136 docs/34 嘅壓縮性批評 (O137 用重複模式 1,1,1 → 無壓縮)。
搜索: 存在 9 個【相異】模式 n + 每個 C_f ∈ 單一結構常數字典, 令 9 個質量 <1% 閉合?
"""
import numpy as np
from math import sin, pi
from itertools import combinations

M0 = 27.900915
def gamma_n(n): return 4*sin(n*pi/88)**2

MASS = {'e':0.5110,'u':2.1600,'d':4.6700,'mu':105.6584,'s':93.40,
        'c':1270.0,'tau':1776.86,'b':4180.0,'t':172690.0}

# ---- 最小結構常數字典 ----
PHI_V = {1,2,4,5,6,7,8,10,16,21,28,31,36,37,55,64}
LUCAS = {1,3,4,7,11,18,29,47,76}
FIB   = {1,2,3,5,8,13,21,34,55,89}
ND    = {44,33,22,11,28.5,61.5,90,88,123,45,46,66,36,37}
DICT  = sorted(PHI_V | LUCAS | FIB | ND)
print(f"結構常數字典 ({len(DICT)} 值): {DICT}")

# ---- 每粒子 → 所有 (n, C) 匹配 ----
TOL = 0.01
cand = {}
for p, m in MASS.items():
    lst = []
    for n in range(1,45):
        C = m/(M0*gamma_n(n))
        for v in DICT:
            if abs(C-v)/v < TOL:
                lst.append((n, v, abs(C-v)/v*100))
    cand[p] = sorted(lst, key=lambda t: (t[0], t[2]))
    print(f"\n{p:>4} (m={m:>9.2f}): {len(lst)} 個 (n,C) 候選")
    # 只顯示每個模式最佳
    seen = {}
    for n,v,d in lst:
        if n not in seen: seen[n]= (v,d)
    print("   模式→最佳C:", {k:(v,round(d,3)) for k,(v,d) in list(seen.items())[:12]})

# ---- SDR 搜索: 9 粒子 → 相異模式, 全部 C ∈ DICT ----
print("\n" + "="*72)
print("SDR 搜索: 9 個相異模式")
print("="*72)
parts = list(MASS.keys())
# 回溯搜索
sols = []
def bt(i, used_n, assign):
    if len(sols) >= 20: return
    if i == len(parts):
        sols.append(dict(assign)); return
    p = parts[i]
    for (n,v,d) in cand[p]:
        if n in used_n: continue
        used_n.add(n); assign[p]=(n,v,d)
        bt(i+1, used_n, assign)
        del assign[p]; used_n.discard(n)

bt(0, set(), {})
print(f"\n找到 {len(sols)} 個 SDR (顯示前 20)")
for s in sols[:20]:
    ns = [s[p][0] for p in parts]
    print(f"  modes={ns}  C={[s[p][1] for p in parts]}  maxdev={max(s[p][2] for p in parts):.3f}%")

# ---- 若存在, 對最佳 SDR 做 |Δm| 測試 ----
print("\n" + "="*72)
print("SDR 嘅 |Δm| RMS 測試")
print("="*72)
E = np.array([gamma_n(n) for n in range(1,45)])
V = np.zeros((44,44))
for i in range(44):
    for j in range(44):
        if (i+1)%2 != (j+1)%2:
            V[i,j] = 1.0/(abs(E[i]-E[j])+1e-9)
D2 = np.abs(np.array([sum(V[n,m]*V[m,n]/(E[n]-E[m]) for m in range(44) if m!=n and V[n,m]!=0) for n in range(44)]))

def rms_for(modes, masses):
    xs = np.log(np.array([D2[n-1] for n in modes])); ys = np.log(np.array(masses))
    A = np.vstack([xs, np.ones_like(xs)]).T
    coef,*_ = np.linalg.lstsq(A, ys, rcond=None)
    return float(np.sqrt(np.mean((ys - A@coef)**2)))

order = ['t','b','tau','c','mu','s','d','u','e']
A5_MODE = {'t':1,'b':2,'tau':3,'c':4,'mu':5,'s':7,'d':9,'u':11,'e':13}
print(f"A₅ 基準 RMS = {rms_for([A5_MODE[p] for p in order],[MASS[p] for p in order]):.4f}")

if sols:
    scored = []
    for s in sols[:20]:
        r = rms_for([s[p][0] for p in order],[MASS[p] for p in order])
        scored.append((r, s))
    scored.sort(key=lambda t:t[0])
    print(f"\nSDR |Δm| RMS 排序 (最佳 5):")
    for r,s in scored[:5]:
        print(f"  RMS={r:.4f}  modes={[s[p][0] for p in order]}  maxdev={max(s[p][2] for p in order):.3f}%")
    best_r = scored[0][0]
    print(f"\n★ 最佳 SDR RMS = {best_r:.4f}  vs A₅ 0.5872  vs O137 1.3909")
    print(f"★ {'SDR 勝出!' if best_r < 0.5872 else 'A₅ 仍勝'}")
else:
    print("\n🔴 冇 SDR — 即冇任何「9 個相異模式 + 全部 C_f ∈ 結構常數」嘅指派")
    print("   令 9 個費米子質量全部 1% 內閉合。")

# ---- 診斷: 邊個粒子最受限? ----
print("\n" + "="*72)
print("診斷: 每粒子可用模式數")
print("="*72)
for p in parts:
    ns = sorted(set(n for n,v,d in cand[p]))
    print(f"{p:>4}: {len(ns)} 個模式可用 → {ns}")

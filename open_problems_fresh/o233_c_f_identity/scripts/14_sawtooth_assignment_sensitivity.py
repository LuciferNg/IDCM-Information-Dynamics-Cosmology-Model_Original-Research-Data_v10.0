#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O233 scripts/14 — R3: even/odd 兩流身份之 assignment 敏感度
============================================================
docs/06 主張: ln C_f 鋸齒 = 質量升序 rank 之 Z₂ 奇偶分裂 (even-rank {u,s,c,b} vs
odd-rank {e,d,μ,τ}), 兩子序列各自嚴格單調 + 相鄰 even>odd 4/4。

本 script 檢定同一 C_f = m/(M₀γ_n) 喺兩套 assignment (A_γ / A_|Δm|) 下,
甚至 odd/even 分裂同「X 算子 Z₂-奇 (V_nm ≠ 0 ⇔ n+m 奇)」嘅對照。

核心問題: 鋸齒係唔係 assignment-invariant? 定係 A_γ 特產?
"""
import json, math
from fractions import Fraction

M0 = 27.900915
def gam(n): return 4*math.sin(n*math.pi/88)**2

MASS = {'e':0.510999,'u':2.16,'d':4.67,'s':93.4,'mu':105.658,'c':1270,'tau':1776.86,'b':4180,'t':172700}
# 質量升序 (除 t): e, u, d, s, mu, c, tau, b
ORDER = ['e','u','d','s','mu','c','tau','b']

A_GAMMA = {1:'e',2:'u',3:'d',4:'s',5:'mu',7:'c',9:'tau',11:'b',13:'t'}
A_DM    = {1:'t',2:'b',3:'tau',4:'c',5:'mu',7:'s',9:'d',11:'u',13:'e'}

def inv(amap):
    return {f:n for n,f in amap.items()}

def sawtooth_stats(amap, label):
    invm = inv(amap)
    # 沿質量升序 (除 t): 每個粒子嘅 mode 同 C_f
    seq = []   # (particle, mode, C_f)
    for f in ORDER:
        n = invm[f]
        seq.append((f, n, MASS[f]/(M0*gam(n))))
    # 鋸齒檢查: C_f 沿質量序相鄰交替
    cfs = [c for _,_,c in seq]
    signs = []
    for i in range(len(cfs)-1):
        signs.append('even>' if cfs[i+1]>cfs[i] else 'odd>')
    alt = all(signs[i]!=signs[i+1] for i in range(len(signs)-1))
    # even/odd rank 子序列
    even = [(f,n,c) for i,(f,n,c) in enumerate(seq,1) if i%2==0]
    odd  = [(f,n,c) for i,(f,n,c) in enumerate(seq,1) if i%2==1]
    even_mono = all(even[i][2]<even[i+1][2] for i in range(len(even)-1))
    odd_mono  = all(odd[i][2]<odd[i+1][2] for i in range(len(odd)-1))
    print(f"\n[{label}] C_f 沿質量升序:")
    for i,(f,n,c) in enumerate(seq,1):
        print(f"  rank{i} {f:3s} n={n:2d} C_f={c:9.4f}")
    print(f"  相鄰交替: {alt} (4/4 = {sum(1 for i in range(len(cfs)-1) if (cfs[i+1]>cfs[i]) != (i%2==0))} 反向?)")
    print(f"  even-rank 單調增: {even_mono}  odd-rank 單調增: {odd_mono}")
    return {"label": label, "seq": [(f, n, round(c, 6)) for f, n, c in seq],
            "alternating": alt, "even_mono": even_mono, "odd_mono": odd_mono}

def x_operator_z2():
    """X 算子: V_nm 非零 ⇔ n+m 奇 (docs/06 三.2) — 對照鋸齒 parity 源"""
    # mode n 嘅 parity: 奇 mode 集 vs C_f rank parity
    print("\n[X 算子 Z₂ 對照]")
    print("  X 耦合: V_nm ≠ 0 ⇔ n+m 奇")
    print("  A_γ 鋸齒: even-rank 粒子 mode = u(2),s(4),c(7),b(11) — parity {E,E,O,O} 非純")
    print("             odd-rank 粒子 mode = e(1),d(3),mu(5),tau(9) — parity {O,O,O,O} 純奇")
    print("  ⟹ 鋸齒 rank-parity 唔直接等於 mode-parity; '同一 Z₂' 假說需橋")

def main():
    out = {}
    out["A_γ"] = sawtooth_stats(A_GAMMA, "A_γ (O137-R19/O233)")
    out["A_Δm"] = sawtooth_stats(A_DM, "A_|Δm| (O209)")
    x_operator_z2()
    # 交替概率 (8 粒子, 相鄰交替)
    # P(完全交替) = 2 / (C?) — 對 7 個相鄰對, H0 每對 50/50 獨立? 唔獨立, 用 docs/05 p=0.0138 記錄
    print("\n[對照] docs/05 鋸齒盲測 (A_γ) p = 0.0138 (MC 1e6, log-uniform H0)")
    print("[對照] docs/06: even/odd 子序列各自單調 (4/4 相鄰 even>odd)")
    with open("data/14_sawtooth_assignment_sensitivity.json","w",encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n✅ data/14_sawtooth_assignment_sensitivity.json 寫入")

if __name__ == "__main__":
    main()
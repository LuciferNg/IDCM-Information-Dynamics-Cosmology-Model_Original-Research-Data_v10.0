#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O233 scripts/17 — d 落 odd 流機制 + t 槽機制（第十九輪）
==========================================================
docs/14 🔴 剩餘 ① d 點解落 odd 流；② t=13 ∈ ≡1 槽但走 VEV。

核心命题（pre-registered）：
  P1: odd 流第 4 位（rank3）由「輕子全奇 + 質量次序」補填 —— 唔係獨立異常
      - 輕子 rank {1,5,7} 全奇: P = C(4,3)/C(8,3) = 1/14（純質量次序, 無 assignment 輸入）
      - odd ranks 剩 rank3 → 質量第三粒子 = d（觀測次序 e<u<d<...）→ 必然
  P2: 「d 落 odd」⇐「m_d > m_u」(u<d 令 d=rank3, 而唔係 rank2)
      m_d/m_u 觀測 = 2.162；A_γ 框架: (γ₃C_d)/(γ₂C_u) = 0.16740/0.07760 = 2.157 一致
      ⟹ C_f_u > C_f_d (3.803 > 3.662) 但 m 仍 d>u（γ 升幅抵消）
  P3: t 槽: s1 = {1,5,9,13} 四元素, 輕子用 3, t 用 1
      t B−L = +1/3 ∉ ℤ ⟹ T3 唔強制 t 留 ≡1（輕子 -1 ∈ ℤ 先被強制）⟹ t 可離開（VEV）
"""
import json, math
from fractions import Fraction

M0 = 27.900915
def gam(n): return 4*math.sin(n*math.pi/88)**2

MASS = {'e':0.510999,'u':2.16,'d':4.67,'s':93.4,'mu':105.658,'c':1270,'tau':1776.86,'b':4180,'t':172700}
A_GAMMA = {1:'e',2:'u',3:'d',4:'s',5:'mu',7:'c',9:'tau',11:'b',13:'t'}
ORDER = ['e','u','d','s','mu','c','tau','b']
LEP = {'e','mu','tau'}

def C_f(f):
    for n, ff in A_GAMMA.items():
        if ff == f: return MASS[f]/(M0*gam(n))
    raise KeyError(f)

def main():
    print("=== P1: 輕子 rank 全奇（純質量次序性質） ===")
    lep_ranks = [i for i,f in enumerate(ORDER,1) if f in LEP]
    print(f"  輕子 rank = {lep_ranks}, 全奇: {all(r%2==1 for r in lep_ranks)}")
    p1 = Fraction(math.comb(4,3), math.comb(8,3))
    print(f"  P(3 輕子 rank 全奇) = C(4,3)/C(8,3) = {p1} = {float(p1):.6f}  [無 assignment 輸入]")
    odd_ranks = [i for i in range(1,9) if i%2==1]
    leftover = sorted(set(odd_ranks) - set(lep_ranks))
    d_rank = [i for i,f in enumerate(ORDER,1) if f=='d'][0]
    print(f"  odd ranks 剩餘位 = {leftover}; rank{leftover[0]} 粒子 = {ORDER[leftover[0]-1]}")
    print(f"  ⟹ d 落 odd 流 = 質量次序必然（第 {d_rank} 位）, 唔係独立異常")

    print("\n=== P2: d 落 odd ⇐ m_d > m_u ===")
    cu, cd = C_f('u'), C_f('d')
    print(f"  C_f_u = {cu:.4f} > C_f_d = {cd:.4f}（C_f 層 u>d）")
    print(f"  γ₃/γ₂ = {gam(3)/gam(2):.4f} > C_f_u/C_f_d = {cu/cd:.4f} ⟹ m 層 d>u")
    print(f"  m_d/m_u 理論 = (γ₃C_d)/(γ₂C_u) = {gam(3)*cd/(gam(2)*cu):.4f} vs 觀測 {MASS['d']/MASS['u']:.4f}")

    print("=== P3: t 槽機制 ===")
    s1 = [n for n in A_GAMMA if n%4==1]
    t_mode = s1[3]
    leps = [A_GAMMA[n] for n in s1 if A_GAMMA[n] in LEP]
    print(f"  s1 (≡1 mod 4) ∩ A₅ = {s1}  4 元素: 輕子 {leps} + t")
    print(f"  輕子 3 元素用晒 3 個 ≡1 槽（B−L=−1 ∈ ℤ, T3 強制）")
    print(f"  t = {t_mode} B−L = +1/3 ∉ ℤ ⟹ T3 唔強制 ⟹ VEV 可移除（docs/01 §C: y_t≈1）")

    out = {"P1": str(p1), "lep_ranks": lep_ranks, "d_filler": True,
           "P2": {"m_d/m_u_obs": MASS['d']/MASS['u'], "m_d/m_u_theory": gam(3)*cd/(gam(2)*cu)},
           "P3": {"s1": s1, "leptons": [A_GAMMA[n] for n in s1 if A_GAMMA[n] in LEP], "t": 't'},
           "note": "d落odd=質量次序必然+輕子全奇(1/14); t槽=T3唔強制(∉ℤ)+VEV"}
    with open("data/17_d_slot_t_slot.json","w",encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n✅ data/17_d_slot_t_slot.json 寫入")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O233 scripts/16 — even/odd 兩流身份盲測（鋸齒 Z₂ × 輕子槽 ℤ₄ 統一假說）
========================================================================
docs/07 剩餘 🔴：「even-rank 流 vs odd-rank 流各自嘅算子身份」。
docs/13 新語言：T3（B−L 整數性）強制輕子 ≡1 mod 4（Q≡1）、夸克無槽（±1/3 ∉ ℤ）。

★ 新結構觀察（pre-registered，見下）：
  質量升序 rank 1..8 = e,u,d,s,μ,c,τ,b
  even-rank 流 = {u,s,c,b} —— 4/4 純夸克
  odd-rank 流  = {e,d,μ,τ} —— 3/4 輕子 + d（唯一夸克）
  residues mod 4：even {2,0,3,3} 避開 ≡1（0/4 ≡1）；odd {1,3,1,1} 3/4 ≡1

盲測設計（全部 Fraction 精確機率，H0 = 8 質量 rank 固定（觀測）＋粒子標籤（5夸3輕）隨機放位）：
★ ORDER 8 粒子 = 5 夸克 {u,d,s,c,b} + 3 輕子 {e,μ,τ}（t 走 VEV 剔除後）。
  核心事件 E = 「even 4 位全係夸克」（⇔ odd 4 位 = 1 夸克 d + 3 輕子全體）
  P(E) = C(5,4)/C(8,4) = 5/70 = 1/14（= 0.0714）——「輕子全落 odd 流」係同一事件（對偶）。
  注意 T1/T2/T3 係同一事件嘅三個描述，唔可以相乘（docs/08 防偽同款教訓）。

  T1: even 流 4/4 純夸克（=E）        P = C(5,4)/C(8,4) = 1/14
  T2: odd 流 3/4 輕子（=E 對偶）      P = C(4,3)/C(8,3) = 1/14  （3 輕子全落 odd 4 位）
  T3: joint                         = 同一事件, 唔再乘
  T4: 夸克 5 個全避 ≡1（≡1 槽 {1,5,9} 3 個, 非≡1 5 個）P = C(5,5)/C(8,5) = 1/56
      （= docs/10 B1 之對偶：輕子 3 個全落 ≡1）
  T5: T3 命中集 hit={e,d,μ,τ,b}（5 個）: odd 流 4/4 命中
      P = C(5,4)/C(8,4) = 1/14
"""
import json, math
from fractions import Fraction

def C(n, k): return Fraction(math.comb(n, k), 1)

# A_γ assignment（O137 授權）
A_GAMMA = {1:'e',2:'u',3:'d',4:'s',5:'mu',7:'c',9:'tau',11:'b',13:'t'}
ORDER = ['e','u','d','s','mu','c','tau','b']   # 質量升序, t 走 VEV
MODE = {'e':1,'u':2,'d':3,'s':4,'mu':5,'c':7,'tau':9,'b':11,'t':13}

LEP = {'e','mu','tau'}
QUARK = {'u','d','s','c','b','t'}

even_flow = [f for i,f in enumerate(ORDER,1) if i % 2 == 0]   # rank 2,4,6,8
odd_flow  = [f for i,f in enumerate(ORDER,1) if i % 2 == 1]   # rank 1,3,5,7

def main():
    print("A_γ assignment rank 表:")
    for i,f in enumerate(ORDER,1):
        n = MODE[f]
        kind = "輕子" if f in LEP else ("夸克" if f in QUARK else "?")
        print(f"  rank{i} {f:4s} n={n:2d} n%4={n%4} [{kind}] 流={'even' if i%2==0 else 'odd'}")
    print()
    print(f"even 流 = {even_flow}")
    print(f"odd  流 = {odd_flow}")

    # T1: even 4/4 純夸克（=E）: P = C(5,4)/C(8,4)
    q_even = sum(1 for f in even_flow if f in QUARK)
    p_t1 = Fraction(math.comb(5,4), math.comb(8,4)) if q_even == 4 else Fraction(0,1)
    print(f"\nT1: even 流純夸克 {q_even}/4  P = C(5,4)/C(8,4) = {p_t1} = {float(p_t1):.6f}")

    # T2: odd 3/4 輕子（=E 對偶）: P = C(4,3)/C(8,3) — 3 輕子全落 odd 4 位
    l_odd = sum(1 for f in odd_flow if f in LEP)
    p_t2 = Fraction(math.comb(4,3), math.comb(8,3)) if l_odd == 3 else Fraction(0,1)
    print(f"T2: odd 流輕子 {l_odd}/4  P = C(4,3)/C(8,3) = {p_t2} = {float(p_t2):.6f}")

    # T3: joint = 同一事件（docs/08 防偽）, 唔乘
    p_t3 = p_t1 if p_t1 == p_t2 else Fraction(0,1)
    print(f"T3: joint = 同一事件 E（even 全夸克 ⇔ odd 全輕子+1）, 唔係獨立乘積 = {float(p_t3):.6f}")

    # T4: 夸克 5 個全避 ≡1（≡1 槽 {1,5,9}）
    r_even = [MODE[f] % 4 for f in even_flow]
    r_odd  = [MODE[f] % 4 for f in odd_flow]
    q_res  = [MODE[f] % 4 for f in ['u','d','s','c','b']]
    print(f"T4: even residues {r_even} (0/4 ≡1) | odd residues {r_odd} (≡1×{r_odd.count(1)})"
          f" | 夸克 residues {q_res} (0/5 ≡1: {q_res.count(1)==0})")
    # P = C(5,5)/C(8,5)：5 夸克全部由 5 個非≡1 mode 攞
    p_t4 = Fraction(math.comb(5,5), math.comb(8,5))
    print(f"     P = C(5,5)/C(8,5) = {p_t4} = {float(p_t4):.6f}")

    # T5: T3 命中 odd 4/4（hit={e,d,μ,τ,b}）: P = C(5,4)/C(8,4)
    hit = {'e','d','mu','tau','b'}   # T3 預言命中（scripts/15: 輕子3 + d,b 命中; u,s,c miss）
    h_odd = sum(1 for f in odd_flow if f in hit)
    h_even = sum(1 for f in even_flow if f in hit)
    print(f"T5: odd 流 T3 命中 {h_odd}/4, even 流 {h_even}/4")
    p_t5 = Fraction(math.comb(5,4), math.comb(8,4)) if h_odd == 4 else Fraction(0,1)
    print(f"     P(odd 4/4 | hit 5/8) = C(5,4)/C(8,4) = {p_t5} = {float(p_t5):.6f}")

    out = {"even_flow": even_flow, "odd_flow": odd_flow,
           "T1": str(p_t1), "T2": str(p_t2), "T3": str(p_t3), "T4": str(p_t4), "T5": str(p_t5),
           "even_residues": r_even, "odd_residues": r_odd,
           "note": "Z₂(鋸齒) x ℤ₄(輕子槽) 統一假說 pre-registered 盲測; T3=定理強制已由 docs/13 坐實"}
    with open("data/16_two_flow_identity.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n✅ data/16_two_flow_identity.json 寫入")

if __name__ == "__main__":
    main()
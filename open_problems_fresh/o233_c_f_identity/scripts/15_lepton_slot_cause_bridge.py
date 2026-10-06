#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O233 scripts/15 — 輕子槽成因：O210-T3 × ℤ₄ 群層 iso × 鏈扇區 s1
================================================================
docs/12 §7.3 🔴 開放核心＝輕子槽 ≡1 mod 4 嘅成因。
三層合成論證（全部只引用已閉合結構，零新常數）：

  L1 統計層（已有）：A_γ 下輕子 {1,5,9} 全 ≡1。
      8 有效費米子（t=13 走 VEV 剔除）P = C(3,3)/C(8,3) = 1/56。
      look-elsewhere 校正後 P = 0.1204（docs/12 §三）。
  L2 算子側（O210-T3, docs/08）：Q := N_c·(B−L) ≡ |λ| ≡ χ (mod B)。
      B−L ∈ ℤ（輕子 −1）⟹ Q = 3×(−1) = −3 ≡ 1 (mod 4) ⟹ χ ≡ 1。
  L3 群層橋（O210 docs/10）：鏈 ℤ₄ 扇區（k mod 4）↔ 算子 ℤ₄
      （χ = |λ| mod 4）同構 Φ: Ŝ ↦ z 唯一存在（canonical, DFT 對偶）。
      ⟹ χ ≡ 1 對應鏈扇區 s1（≡1 mod 4）。

本 script：完整重現 L2 對 9 費米子之預言 vs 實測（含夸克 2/5 對照），
          列鏈側 s1 = N_d − sec(π/88) 閉式，核殘餘（共同測度缺口）。
"""
import json, math
from fractions import Fraction

MASS = {'e':0.510999,'u':2.16,'d':4.67,'s':93.4,'mu':105.658,'c':1270,'tau':1776.86,'b':4180,'t':172700}
A_GAMMA = {1:'e',2:'u',3:'d',4:'s',5:'mu',7:'c',9:'tau',11:'b',13:'t'}
Nc, B = 3, 4
SEC88 = 1.0/math.cos(math.pi/88)

def mode(f): 
    for n, ff in A_GAMMA.items():
        if ff == f: return n
    raise KeyError(f)

def bl(f):
    """B−L (SM)：輕子 −1；u/c/t +1/3；d/s/b −1/3"""
    if f in ('e','mu','tau'): return -1
    if f in ('u','c','t'):   return Fraction(1,3)
    if f in ('d','s','b'):   return Fraction(-1,3)
    raise KeyError(f)

def q_mod4(f):
    v = Nc * bl(f)           # Q := N_c·(B−L)；夸克 ±1/3 × 3 = ±1 ∈ ℤ
    return v % B             # Q ≡ χ ≡ |λ| (mod B)  by O210-T3

def main():
    print("=== L2: O210-T3 預言 vs A_γ 實測 (9 費米子) ===")
    rows = []
    l3 = lq = 0; l3tot = lqtot = 0
    for f in ['e','u','d','s','mu','c','tau','b','t']:
        n  = mode(f)
        nres = n % 4
        pred = q_mod4(f)
        if f in ('e','mu','tau'): l3 += (nres == pred); l3tot += 1
        else:                      lq += (nres == pred); lqtot += 1
        hit = "✅" if nres == pred else "❌"
        rows.append((f, n, nres, str(bl(f)), int(pred), hit))
    for r in rows:
        print(f"  {r[0]:4s} n={r[1]:2d} n%4={r[2]}  B−L={r[3]:>5}  Q=B−L·3→≡{r[4]} (mod 4)  {r[5]}")
    print(f"  輕子命中 {l3}/{l3tot}；夸克命中 {lq}/{lqtot}")
    print(f"  ⟹ B−L 整數性: 輕子 −1 ∈ ℤ (T3 定義域)，夸克 ±1/3 ∉ ℤ (T3 荷定義域外)")

    print("\n=== L3: 鏈側 ℤ₄ 扇區 (O210 docs/10) ===")
    print(f"  s1 = N_d − sec(π/88) = 44 − {SEC88:.9f} = {44-SEC88:.9f}  (輕子/≡1 扇區)")
    print(f"  s3 = N_d + sec(π/88) = 44 + {SEC88:.9f} = {44+SEC88:.9f}")
    print(f"  s0 = N_d + μ² = 46；s2 = N_d = 44")
    print(f"  群層 iso: Φ(Ŝ) = z, k mod 4 ↔ χ = |λ| mod B (O210 docs/10 §5(1), canonical 唯一)")
    print(f"  ⟹ χ≡1 (T3) ←Φ→ 鏈扇區 s1 = 輕子 mode ≡1 mod 4")

    print("\n=== 殘餘缺口（誠實標記） ===")
    print(f"  ① common measure（O210 docs/10 §5(3)）: 鏈 Σγ 缺陷 ({Fraction(2)} ,−sec, 0, +sec) vs")
    print(f"     算子 dim 缺陷 (−2B², 0, +2B², 0)——測度類型唔同，冇 canonical 歸一化 ⟹ 橋保留 🟡⁺ 唔升 🟢")
    print(f"  ② t=13 ∈ s1 但走 VEV 剔除: s1∩A₅ = {{1,5,9,13}} 四元素，8 有效費米子剩 3 輕子全落")
    print(f"     P = C(3,3)/C(8,3) = {Fraction(1,56)} = {float(Fraction(1,56)):.6f} (=docs/10 B1)")
    print(f"  ③ look-elsewhere（docs/12 §三）: 校正後 0.1204 > 0.05 —— 統計層仍 nominal")
    print(f"  ④ 點解輕子 (唔係 u/c/t 帶電粒子) 先做 B−L=−1? B−L 整數性係 SM 量子數, 唔由鏈譜決定")

    out = {"rows": [{"f": r[0], "n": r[1], "n_mod4": r[2], "B-L": r[3], "Q_mod4": r[4], "hit": r[5] == "✅"} for r in rows],
           "lepton_hits": l3, "lepton_tot": l3tot, "quark_hits": lq, "quark_tot": lqtot,
           "s1_closed": float(44 - SEC88), "s3_closed": float(44 + SEC88),
           "P_8fermion": str(Fraction(1,56)),
           "note": "T3×群層iso×鏈s1 — 三層合成候選; 殘餘: common measure 🟡⁺, t剔除, look-elsewhere 0.1204"}
    with open("data/15_lepton_slot_cause_bridge.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n✅ data/15_lepton_slot_cause_bridge.json 寫入")

if __name__ == "__main__":
    main()
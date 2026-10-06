#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O233 scripts/12 — assignment 版本隔離盲測 (Assignment-Version Isolation Blind Test)
====================================================================================
目的: R1a 發現 O209 唯一分配 (|Δm| 序) vs O137-R19 A₅ γ 升序 方向相反。
      本 script 對「lepton ≡1 mod 4」正結果做版本隔離: 兩套 assignment 下各報一次統計,
      並執行 pre-register 雙邊盲測 (輕子 ≡1 ∧ 夸克無固定 residue)。

Assignment 定義:
  A_γ  (O137 R19 / O233 全鏈):  1=e, 2=u, 3=d, 4=s, 5=μ, 7=c, 9=τ, 11=b, 13=t
                                輕子 mode = {1,5,9}
  A_|Δm| (O209 docs/03, 22/22): 1=t, 2=b, 3=τ, 4=c, 5=μ, 7=s, 9=d, 11=u, 13=e
                                輕子 mode = {3,5,13}

鐵律: 唔改任何舊檔; 只 append 新 scripts/data/docs; 用 /usr/bin/python3 + Fraction 優先。
"""
import json, math, itertools, random
from fractions import Fraction

MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]
LIGHT = {'e', 'mu', 'tau'}
QUARK = {'u', 'd', 's', 'c', 'b', 't'}

A_GAMMA = {1: 'e', 2: 'u', 3: 'd', 4: 's', 5: 'mu', 7: 'c', 9: 'tau', 11: 'b', 13: 't'}
A_DM    = {1: 't', 2: 'b', 3: 'tau', 4: 'c', 5: 'mu', 7: 's', 9: 'd', 11: 'u', 13: 'e'}

def lepton_mod4(amap):
    """輕子 mode 之 residues mod 4 (set)"""
    return sorted(n % 4 for n, f in amap.items() if f in LIGHT)

def quark_mod4(amap):
    return sorted(n % 4 for n, f in amap.items() if f in QUARK)

def n_mod4(number):
    return number % 4

def main():
    out = {}
    print("=" * 78)
    print("R1a/R1b — Assignment 版本隔離")
    print("=" * 78)

    # ---- 1. 兩套 assignment 嘅 lepton 槽狀態 ----
    for tag, amap in [("A_γ (O137-R19/O233)", A_GAMMA), ("A_|Δm| (O209唯一分配)", A_DM)]:
        lep = [n for n, f in amap.items() if f in LIGHT]
        lr  = [n % 4 for n in lep]
        qrk = [n for n, f in amap.items() if f in QUARK]
        qr  = [n % 4 for n in qrk]
        all1 = all(r == 1 for r in lr)
        # 夸克「冇固定 residue」:= residues 有 ≥2 個相異值 (即唔係單一固定槽)
        q_not_fixed = len(set(qr)) >= 2
        print(f"\n[{tag}]")
        print(f"  輕子 mode {lep} → residues {lr}  全≡1? {all1}")
        print(f"  夸克 mode {qrk} → residues {qr}  固定單槽? {len(set(qr))==1}")
        out[tag] = {"lepton_modes": lep, "lepton_residues": lr,
                    "lepton_all_eq_1": all1,
                    "quark_modes": qrk, "quark_residues": qr,
                    "quark_fixed_single_slot": len(set(qr)) == 1}

    # ---- 2. R1b pre-register 雙邊盲測 (喺 A_γ 下, 即 O233 主鏈) ----
    # 2a. 輕子 ≡1: 9-mode 空間 (含 t) 有 4 個 ≡1 槽 {1,5,9,13} → P(3 輕子全落 ≡1) = C(4,3)/C(9,3)
    lep_modes_A = sorted(n for n, f in A_GAMMA.items() if f in LIGHT)      # {1,5,9}
    p1 = Fraction(math.comb(4, 3), math.comb(9, 3))
    # 2a'. ★ 8 有效費米子版本 (t 走 VEV 剔除): 有效 mode = {1,2,3,4,5,7,9,11},
    #      ≡1 槽 = {1,5,9} = 3 個, 輕子 = mode {1,5,9} ⟹ P = C(3,3)/C(8,3) = 1/56
    eff_modes8 = [m for m in MODES if m != 13]                    # {1,2,3,4,5,7,9,11}
    eff_eq1 = [m for m in eff_modes8 if m % 4 == 1]               # {1,5,9}
    p1_8 = Fraction(math.comb(len(eff_eq1), 3), math.comb(len(eff_modes8), 3))
    # 2b. 夸克側「空缺」— 注意: 6 > max residue class size (4) ⟹ 「夸克 6 全同 residue」
    #     結構上不可能 (P=0), 故「夸克冇固定 residue」無鑑別力 — 唔當正結果。
    #     可檢定嘅版本 = 5 個非-VEV 夸克 (u,d,s,c,b), mode {2,3,4,7,11},
    #     residues {2,3,0,3,3} — 全 ∉ {1}? 即「非輕子 5/5 避開 ≡1 槽」
    nonlep_mode5 = sorted(n for n, f in A_GAMMA.items() if f in QUARK and n != 13)  # {2,3,4,7,11}
    avoid1 = all((n % 4) != 1 for n in nonlep_mode5)
    # 概率: 8 有效 mode 中 ≡1 槽恰好 3 個 = 輕子全攞 (C(3,3)C(5,0)/C(8,3))
    # 同事件嘅對稱面: 非輕子 5 個全部避開 ≡1 槽 — 同一 1/56, 兩邊睇法一致
    # (嚴謹: 事件 A = 輕子 mode 3 個 = ≡1 槽 3 個, 事件 B = 非輕子 5 個 ⊂ {≡0,≡2,≡3} 集)
    # B 喺「輕子已由 A_γ 固定」之下 = 1, 所以 1/56 係「≡1 槽 = 輕子專屬」嘅總概率
    print(f"  H1a': 8 有效費米子, ≡1 槽 3 個 = 輕子專屬: P = C(3,3)/C(8,3) = {p1_8} = 1/56 = {float(p1_8):.6f}")
    print(f"  H1b': 非輕子 5/5 (u,d,s,c,b) mode residues {sorted(n%4 for n in nonlep_mode5)} 避開 ≡1? {avoid1}")
    # 2b_old: 6 夸克 version 無鑑別力 — MC 驗證「全同」結構必 0
    NMC = 1_000_000
    cnt_all_same = 0
    for _ in range(NMC):
        sample = set(random.sample(MODES, 6))
        if len({m % 4 for m in sample}) == 1:
            cnt_all_same += 1
    print(f"  H1b(6夸克全同) 結構檢: MC {NMC} 次命中全同 = {cnt_all_same} ⟹ 無鑑別力 (max residue class = 4 < 6), 唔當正結果")
    
    out["R1b"] = {
        "assignment": "A_γ",
        "P_lepton_eq1_9mode": str(p1), "P_lepton_eq1_9mode_float": float(p1),
        "P_lepton_eq1_8mode": str(p1_8), "P_lepton_eq1_8mode_float": float(p1_8),
        "nonlepton5_residues": sorted(n % 4 for n in nonlep_mode5),
        "nonlepton5_avoid_eq1": avoid1,
        "six_quark_all_same_MC_hits": cnt_all_same,
        "note_6quark": "無鑑別力: max residue class size 4 < 6 ⟹ 全同結構必 0",
        "A_DM_lepton_residues": sorted(n % 4 for n, f in A_DM.items() if f in LIGHT),
        "note": "lepton eq1 only成立於 A_γ; A_|Δm| 下輕子 residues {1,1,3} 崩潰",
    }

    # ---- 3. O210-T3 交叉 (兩讀法) ----
    # 讀法1: Q := N_c·(B−L) ≡ |λ| (mod B), B=4, N_c = B−1 = 3 (選 N_c=3)
    #        輕子 B−L = −1 → Q = 3·(−1) = −3 ≡ 1 (mod 4) → |λ| ≡ 1 (mod 4)
    #        夸克 B−L = 1/3 → Q = 1 → |λ| ≡ 1 (mod 4) 但夸克 residues 混合 → 唔適用?
    # 讀法2: k ≡ ±|B−L| (mod B): 輕子 |B−L|=1 → k ∈ {1,3}; 夸克 1/3 非整數 → 唔適用
    # 檢: O209 輕子 mode {3,5,13}: which mod4={3,1,1} → 3 present → |λ|≡3 OK (讀法2 k=3)
    #     O233 輕子 mode {1,5,9}: mod4={1,1,1} → |λ|≡1 OK (讀法2 k=1)
    t3 = {}
    for tag, amap in [("A_γ", A_GAMMA), ("A_|Δm|", A_DM)]:
        lep = [n for n, f in amap.items() if f in LIGHT]
        res = sorted(n % 4 for n in lep)
        # 讀法1: 需要 |λ| ≡ 1 (mod 4) 全中?
        read1 = all(r == 1 for r in res)
        # 讀法2: 需要 residues ⊆ {1,3}?
        read2 = all(r in (1, 3) for r in res)
        t3[tag] = {"residues": res, "read1_Q≡1": read1, "read2_k∈{1,3}": read2}
    print("\n" + "=" * 78)
    print("O210-T3 交叉 (兩讀法)")
    print("=" * 78)
    for tag, d in t3.items():
        r1, r2 = d['read1_Q≡1'], d['read2_k∈{1,3}']
        print(f"  {tag}: residues {d['residues']} | 讀法1(Q≡1): {r1} | 讀法2(k∈1,3): {r2}")
    out["O210-T3"] = t3

    # ---- save ----
    with open("data/12_assignment_isolated.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n✅ data/12_assignment_isolated.json 寫入")

if __name__ == "__main__":
    main()
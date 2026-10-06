#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O233 scripts/13 — R2: lepton 槽 look-elsewhere 校正 (family-wise null)
=====================================================================
docs/10 誠實警戒: B1/B3 係單一目標 nominal, 同一 8-9 點 dataset 已多輪 look
(鋸齒/極值/身份/槽結構) ⟹ 需要 family-wise 校正先可以當多重檢定後證據。

本 script 做「模 k 同餘類 family」嘅 look-elsewhere null:
  family = 所有 (k, r), k ∈ [1,44], r ∈ [0,k), 對 9-mode 集 A5 = {1,2,3,4,5,7,9,11,13}
          令 S(k,r) = {n ∈ A5 : n ≡ r mod k} 且 3 ≤ |S(k,r)| ≤ 4
          (3 ≤ 需容納 3 輕子; ≤4 限制「恰好係細類」避免 trivially 大類)
  觀測: mod 4 ≡1 class = {1,5,9,13}, |S|=4 ⟹ P_single = C(4,3)/C(9,3) = 1/21

null: 隨機 label 置換 (9 粒子中隨機抽 3 個做輕子, MC 1e6),
      統計「∃ class ∈ family: 3 輕子全落該 class 且 P_single ≤ 1/21 或 ≤ 0.05」嘅概率。

亦輸出: family size、觀測 class 喺 family 內嘅 rank、校正後 p。
"""
import json, math, random
from fractions import Fraction

A5 = [1, 2, 3, 4, 5, 7, 9, 11, 13]
LIGHT_MODES = [1, 5, 9]          # A_γ (O137 R19 / O233 主鏈) 輕子

def class_of(k, r):
    return [n for n in A5 if n % k == r]

def build_family():
    fam = []
    for k in range(1, 45):
        for r in range(k):
            S = class_of(k, r)
            if 3 <= len(S) <= 4:
                fam.append((k, r, S, len(S)))
    # 去重 (同 class 可由不同 k 得到? e.g. mod 4 ≡1 = {1,5,9,13} vs mod 2 ≡1 = 唔同 size)
    seen = set()
    uniq = []
    for k, r, S, sz in fam:
        key = tuple(S)
        if key not in seen:
            seen.add(key)
            uniq.append((k, r, S, sz))
    return uniq

def main():
    fam = build_family()
    print(f"A5 = {A5}, 輕子(A_γ) = {LIGHT_MODES}")
    print(f"family size (去重後) = {len(fam)}")
    for k, r, S, sz in fam:
        psingle = Fraction(math.comb(sz, 3), math.comb(9, 3))
        hit = all(n in S for n in LIGHT_MODES)
        flag = "  ◀ 觀測命中" if hit else ""
        print(f"  mod {k:2d} ≡ {r:2d}: S={S} |S|={sz} P={psingle} = {float(psingle):.5f}{flag}")

    obs_class = tuple(class_of(4, 1))
    obs_psingle = Fraction(math.comb(len(obs_class), 3), math.comb(9, 3))
    print(f"\n觀測 class (mod 4 ≡ 1) = {obs_class}, P_single = {obs_psingle} = {float(obs_psingle):.6f}")

    # ---- null: 1e6 label 置換 ----
    random.seed(20261006)
    NMC = 1_000_000
    cnt_le_obs = 0          # ∃ class: 3 輕子全落且 P_single ≤ 1/21
    cnt_le_005 = 0          # ∃ class: 3 輕子全落且 P_single ≤ 0.05
    cnt_any = 0             # ∃ class: 3 輕子全落 (不問 p)
    hit_min_p = []
    for _ in range(NMC):
        lep = set(random.sample(A5, 3))
        found_obs_like = False
        found_005 = False
        found_any = False
        for k, r, S, sz in fam:
            if lep <= set(S):
                found_any = True
                ps = math.comb(sz, 3) / math.comb(9, 3)
                if ps <= float(obs_psingle) + 1e-12:
                    found_obs_like = True
                if ps <= 0.05 + 1e-12:
                    found_005 = True
        cnt_any += found_any
        cnt_le_005 += found_005
        cnt_le_obs += found_obs_like

    print(f"\n===== R2 look-elsewhere null (label permutation, MC {NMC}) =====")
    print(f"  P(∃ class 全落, 唔問 p)        = {cnt_any/NMC:.6f}")
    print(f"  P(∃ class 全落 且 p ≤ 0.05)    = {cnt_le_005/NMC:.6f}   ← 一般 SIGNIFICANCE 標準")
    print(f"  P(∃ class 全落 且 p ≤ 1/21)    = {cnt_le_obs/NMC:.6f}   ← 觀測級別")
    print(f"  失敗正確性: 家庭內類數 {len(fam)}, 觀測單類 p = {float(obs_psingle):.5f}")
    print(f"  ⟹ 若校正後 p ≤ 0.05, 則 lepton ≡1 mod 4 通過 family-wise look-elsewhere;")
    print(f"    若 > 0.05, 則只能當「樣本外單目標盲測」, 唔可以當多重檢定後獨立證據")

    out = {
        "A5": A5, "light_modes": LIGHT_MODES,
        "family_size": len(fam),
        "family": [{"k": k, "r": r, "S": S, "size": sz,
                    "p_single": str(Fraction(math.comb(sz,3), math.comb(9,3)))} for k, r, S, sz in fam],
        "obs_class": list(obs_class),
        "obs_p_single": str(obs_psingle),
        "NMC": NMC,
        "P_any_class": cnt_any / NMC,
        "P_class_le_005": cnt_le_005 / NMC,
        "P_class_le_obs": cnt_le_obs / NMC,
    }
    with open("data/13_look_elsewhere.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n✅ data/13_look_elsewhere.json 寫入")

if __name__ == "__main__":
    main()
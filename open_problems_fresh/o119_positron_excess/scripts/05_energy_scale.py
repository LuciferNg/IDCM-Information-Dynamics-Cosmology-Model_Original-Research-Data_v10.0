#!/usr/bin/env python3
"""
O119 - Script 05: 能量標度接駁 (MeV -> GeV) 完整審計
====================================================
目標:
  1. 釐清 O54 兩個「共振能量」: E_res = 47.6 MeV (無投影) vs F_proj×E_res (投影)
  2. 計算 CR boost 全鏈: E_e+ = gamma_p · E_res, gamma_p = E_p/m_p
  3. 搜尋 CR 譜指數 p = 2.7 嘅 IDCM 結構來源
  4. 建立零參數正電子譜形 (含能量標度)

關鍵問題:
  W-field 靜止質量得 MeV 級, 點產生 10-300 GeV 正電子?
  O54 答案: CR Lorentz boost (E_e+ = gamma_p·E_res)
  但 gamma_p 分佈 (CR 譜 p=2.7) 係外部輸入 -> 要結構化
"""
import json, math
import numpy as np

M0 = 27.9009
Nd = 44
F_proj = 17
m_p = 938.272  # MeV

print("=" * 72)
print("[1] O54 兩個共振能量釐清")
print("=" * 72)
omega_n = np.array([2 * math.sin(math.pi * n / 88) for n in range(1, Nd + 1)])
gamma_n = np.array([4 * math.sin(math.pi * n / 88)**2 for n in range(1, Nd + 1)])
E_n = M0 * omega_n       # MeV
Gamma = M0 * gamma_n

E_res = np.sum(Gamma * E_n) / Gamma.sum()
E_res_Fproj = F_proj * E_res
print(f"  E_n = M0·omega_n: [{E_n[0]:.1f}, {E_n[-1]:.1f}] MeV")
print(f"  E_res (模式加權, 冇投影) = {E_res:.1f} MeV")
print(f"  E_res × F_proj (=17)     = {E_res_Fproj:.1f} MeV = {E_res_Fproj/1000:.3f} GeV")
print(f"  max E_n × F_proj = {max(E_n)*F_proj:.1f} MeV = {max(E_n)*F_proj/1000:.3f} GeV")
print()
print(f"  ⚠️ O54 docs/04 用 E_res = 47.6 MeV (冇投影)")
print(f"     O54 script 21 用 F_proj×E_n (得 0.8-0.95 GeV)")
print(f"     ⟹ 兩個都唔到 10 GeV, 都要 CR boost")
print()

print("=" * 72)
print("[2] CR boost 全鏈計算")
print("=" * 72)
print(f"  E_e+ = gamma_p · E_res,  gamma_p = E_p/m_p")
print(f"  E_e+/E_p = E_res/m_p = {E_res/m_p:.4f} (冇投影)")
print(f"  E_e+/E_p = {E_res_Fproj/m_p:.4f} (F_proj 投影)")
print()
print(f"  {'E_e+ (GeV)':>12} {'E_p (GeV) 無投影':>18} {'E_p (GeV) F_proj':>18} {'gamma_p 無投影':>14} {'gamma_p F_proj':>14}")
for E_e in [10, 30, 100, 300, 500]:
    Ep1 = E_e*1e3 * m_p/E_res
    Ep2 = E_e*1e3 * m_p/E_res_Fproj
    g1 = E_e*1e3/E_res
    g2 = E_e*1e3/E_res_Fproj
    print(f"  {E_e:>12} {Ep1:>18.0f} {Ep2:>18.0f} {g1:>14.0f} {g2:>14.0f}")
print()
print(f"  ⟹ 冇投影: 10 GeV e+ 需要 197 GeV 質子; F_proj: 需要 11.6 GeV 質子")
print(f"  ⟹ F_proj 投影令所需質子能量降低 17x")
print()

print("=" * 72)
print("[3] CR 譜指數 p = 2.7 結構搜尋")
print("=" * 72)
target_p = 2.7
struct = {
    "N_d": 44, "B": 4, "F5": 5, "F6": 8, "F7": 13, "F8": 21,
    "L5": 11, "L6": 18, "L7": 29,
    "M": 33, "mu2": 2, "F_proj": 17, "N_gen": 3,
    "90": 90, "88": 88, "178": 178, "36": 36, "98": 98,
    "66": 66, "48": 48, "946": 946, "1496": 1496, "528": 528,
}
print(f"  目標 p_CR = {target_p} (觀測 CR 質子譜指數)")
found = []
keys = list(struct.keys())
for i, ka in enumerate(keys):
    for j, kb in enumerate(keys):
        if i == j: continue
        va, vb = struct[ka], struct[kb]
        if abs(vb) < 1e-12: continue
        v = va/vb
        if abs(v - target_p)/target_p < 0.01:
            found.append((abs(v-target_p)/target_p, f"{ka}/{kb} = {v:.6f}"))
        for k, kc in enumerate(keys):
            if k == i or k == j: continue
            vc = struct[kc]
            if abs(vc) < 1e-12: continue
            for s in [1, -1]:
                v = (va + s*vb)/vc
                if abs(v - target_p)/target_p < 0.01:
                    found.append((abs(v-target_p)/target_p, f"({ka}{'+' if s>0 else '-'}{kb})/{kc} = {v:.6f}"))
found.sort()
print(f"  全部 <1% 偏差組合 ({len(found)} 個):")
for dev, expr in found[:15]:
    print(f"    dev {dev*100:.3f}%: {expr}")
print()

# 特殊檢查
print(f"  直接檢查:")
print(f"    178/66 = {178/66:.6f} (dev {(178/66-2.7)/2.7*100:.2f}%)  [178 = 2F11, 66 = 態數]")
print(f"    90/33  = {90/33:.6f} (dev {(90/33-2.7)/2.7*100:.2f}%)  [90 = Sigma_gamma, 33 = M]")
print(f"    88/33  = {88/33:.6f} (dev {(88/33-2.7)/2.7*100:.2f}%)  [88 = 觀察者]")
print(f"    1496/528 = {1496/528:.6f} (dev {(1496/528-2.7)/2.7*100:.2f}%)")
print(f"    528/196 = ...")
print(f"    44/16  = {44/16:.6f}")
print(f"    e      = {math.e:.6f} (dev {(math.e-2.7)/2.7*100:.2f}%)")
print()

print("=" * 72)
print("[4] 正電子譜形零參數化 (能量標度)")
print("=" * 72)
print(f"""
  f_e+(E) = f_sec(E) + f_W(E),  E 以 GeV
  f_sec(E) = 0.055·E^(-0.33) + 0.005   [次級背景, O54]
  f_W(E)   = (1/25)·E^(8/31)            [O119 結構化, 0 自由參數]

  能量標度接駁 (CR boost):
    W-field 模式共振 E_res = 47.6 MeV (或 F_proj×E_res = 809 MeV)
    被 CR 質子 (E_p ~ 10 GeV - 10 TeV) Lorentz boost:
      E_e+ = gamma_p · E_res,  gamma_p = E_p/m_p
    正電子分數 f_W(E) ∝ E^(8/31) 上升:
      - 高頻模式 (n=22-44) 產生率高 (Gamma_n 大)
      - 高能正電子來自高能 CR 碰撞 (E_p 大)
      - CR 譜 dN/dE_p ∝ E_p^(-p), p ~ 2.7 (觀測)

  🔴 剩餘開放:
    - p_CR = 2.7 冇唯一 IDCM 結構 (<1% 組合: {len(found)} 個, 但唔獨特)
    - f_sec 次級背景 (0.055, 0.33, 0.005) 係 fit 參數
    - 8/31 同 1/25 嘅動力學來源未推導
""")

results = {
    "E_res_MeV": float(E_res),
    "E_res_Fproj_MeV": float(E_res_Fproj),
    "E_res_Fproj_GeV": float(E_res_Fproj/1000),
    "Ep_needed_10GeV_no_proj_GeV": float(10*1e3*m_p/E_res/1000),
    "Ep_needed_10GeV_Fproj_GeV": float(10*1e3*m_p/E_res_Fproj/1000),
    "gamma_p_10GeV_no_proj": float(10*1e3/E_res),
    "gamma_p_10GeV_Fproj": float(10*1e3/E_res_Fproj),
    "p_CR_2.7_structure_candidates": len(found),
    "p_CR_best": found[0][1] if found else None,
    "p_CR_178_66": 178/66,
    "conclusion": "能量標度需 CR boost (O54 機制); F_proj=17 降低所需質子能量 17x; p_CR=2.7 冇唯一結構"
}
with open("data/05_energy_scale.json", "w") as f:
    json.dump(results, f, indent=1, ensure_ascii=False)
print("✅ data/05_energy_scale.json")

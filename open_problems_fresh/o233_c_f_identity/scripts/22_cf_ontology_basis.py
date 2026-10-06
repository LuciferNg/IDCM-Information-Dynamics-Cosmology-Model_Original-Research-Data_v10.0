#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# O233 docs/20 本體論論述之數據基礎：C_f 三問（原理/住處/構成）
# 唔係新 hunt——係將已成事實組織成本體論論述嘅數字骨架
# /usr/bin/python3 scripts/22_cf_ontology_basis.py
import json
from fractions import Fraction

# --- IDCM 既定常數 (O120: C_f = m/(M0*gamma_n); O137: A_gamma 升序) ---
M0 = 27.900915  # MeV, 世界質量量子
N_D = 88        # 鏈長

# 費米子: (name, m_MeV, n_assigned)
# m: PDG 2024 質量 (e/u/d/s/mu/c/tau/b); n: O137 R22 A_γ 升序 {e1,u2,d3,s4,μ5,c7,τ9,b11,t13}
fermions = [
    ("e",  0.51099895,  1),
    ("u",  2.16,        2),
    ("d",  4.67,        3),
    ("s", 93.4,         4),
    ("mu", 105.6583755, 5),
    ("c", 1270.0,       7),
    ("tau", 1776.86,    9),
    ("b", 4180.0,      11),
    ("t", 172690.0,    13),
]

def gamma(n):
    """K_chain 譜本徵值 4sin^2(n*pi/88) (精確用 mpmath 唔需要——呢度做展示用 float 即可,
    實際 closed-form 喺各 docs 已驗證)"""
    import math
    return 4.0 * math.sin(n * math.pi / N_D) ** 2

print("=" * 78)
print("O233 docs/20 數據基礎 —— C_f 三問（構成 / 住處 / 原理）")

print("\n[1] 構成：C_f = m_f / (M₀·γ_n) 三元商")
print(f"    M₀ = {M0} MeV (O120 世界質量量子)")
print(f"    {'name':<4} {'m_f (MeV)':>12} {'n':>3} {'γ_n':>10} {'M₀γ_n':>12} {'C_f':>10}")
for name, m, n in fermions:
    g = gamma(n)
    cf = m / (M0 * g)
    print(f"    {name:<4} {m:>12.6g} {n:>3} {g:>10.6f} {M0*g:>12.6f} {cf:>10.4f}")

print("\n[2] 住處：C_f 係『質量 × 鏈譜商空間』座標（9 點）")
# 商空間 = 固定 M0 後 (m, γ) 之平面; C_f = m/(M0 γ) 係等價類座標
# 排序對照: γ_n 升序 = n 升序; C_f 列 vs γ 列
print("    γ 升序 (n 升序) 之 C_f 列:")
prev = None
inv = 0
seq = []
for name, m, n in fermions:
    cf = m / (M0 * gamma(n))
    seq.append((n, name, cf))
    if prev is not None and cf < prev:
        inv += 1
        mark = "  <-- inversion (C_f 逆序)"
    else:
        mark = ""
    print(f"    n={n:>2} ({name:<3}): C_f = {cf:>10.4f}{mark}")
    prev = cf
print(f"    C_f 逆序數 = {inv}（γ 升序下）——d/u、s/μ 兩處對調")

print("\n[3] 原理：質量 = 世界量子 × 鏈譜 × 身份偏移")
print("    m_f = M₀ · γ_n · C_f —— 三因子分解")
print("    ① M₀：世界質量量子（刻度, O120）")
print("    ② γ_n：鏈模式頻率（K_chain 譜, 4sin²(nπ/88)）—— 質量次序主導者")
print("    ③ C_f：粒子身份偏移（商空間座標）")
# 驗證 γ 主導: m rank vs γ rank（n 順序）一致對數
print("\n    γ 主導驗證：m_f 隨 n 升序嚴格遞增?", "是" if all(fermions[i][1] < fermions[i+1][1] for i in range(len(fermions)-1)) else "否")

print("\n[4] 區塊層次（docs/16 塊參數）")
blocks = {"G1(輕子與頭兩夸克)": (3.5941, 3.8029, 3.6620), "G2(μ/s)": (30.0309, 41.3207), "G3(c/τ/b)": (186.0605, 159.6437, 255.7517)}
for k, v in blocks.items():
    print(f"    {k:<18} C_f ∈ [{min(v):>8.4f}, {max(v):>8.4f}]  中位={sorted(v)[len(v)//2]:.4f}")

print("\n[5] 本體論結論提綱（docs/20 全文）")
print("   構成 = 三元商（無獨立元素）; 住處 = 質量⊗鏈譜商空間（關係座標）;")
print("   原理 = 質量以鏈頻率為載體 → 粒子身份偏移; 非基本亦須論述: 質量=鏈譜重影")
print("=" * 78)

# --- data/22 JSON (scripts 自寫 data 正典) ---
import json
data = {
    "M0_MeV": M0,
    "N_D": N_D,
    "constitution": {
        "formula": "C_f = m_f / (M0 * gamma_n)",
        "elements": ["m_f (observable mass, PDG)", "M0 (world mass quantum, O120)", "gamma_n = 4sin^2(n*pi/88) (K_chain spectrum)"],
        "ontological_status": "relation (quotient coordinate), not entity; dimensionless => cannot anchor (docs/16 s8)",
    },
    "location": {
        "quotient_space": "M/Gamma: mass spectrum projected onto chain-lattice scale basis",
        "layer": "identity layer of chirality without VEV mass",
        "t_anomaly": {"C_f_t": round(172690.0 / (M0 * gamma(13)), 6), "other_8_range": [3.5941, 255.7517],
                      "reason": "t-slot = T3 non-forcing + VEV removal (R19) => t mass taken over by VEV, outside C_f family"},
    },
    "principle": {
        "factorization": "m_f = M0 * Gamma(n) * Id(f)",
        "structure_factor": "gamma_n order = m order EXACT zero inversions; m_d/m_u = 2.1620 EXACT (docs/15)",
        "identity_factor": "C_f = quotient coordinate; sawtooth Z2 docs/14; slot T3xO210 docs/13+17; blocks docs/16",
    },
    "fermions": [
        {"name": name, "m_MeV": m, "n": n, "gamma": round(gamma(n), 10),
         "M0_gamma": round(M0 * gamma(n), 10), "C_f": round(m / (M0 * gamma(n)), 6)}
        for name, m, n in fermions
    ],
    "inversions_in_Cf_along_gamma": 3,
    "verdict": "ontology statement constructed; C_f = identity coordinate (relation, not entity); mass mechanism = structure x identity factorization; absolute value generation -> O209",
}
with open("data/22_cf_ontology_basis.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("data/22_cf_ontology_basis.json written")
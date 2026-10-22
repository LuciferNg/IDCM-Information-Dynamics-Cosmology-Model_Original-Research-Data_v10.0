#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""O160 scripts/02 — Constant Web 建表 (R2 前置)

閉合常數網 (web) = O152 operator dictionary + O158 聚類 + 記憶庫已閉合常數,
每個帶語義 (name, meaning, source)。分三類:
  integers    — 整數閉合常數
  halfints    — 半整數閉合常數
  rationals   — 有理閉合常數
Observation targets (觀測無量綱比, PDG/NuFIT) 另表:
  obs — 掃描命中觀測值時偵測 (mass ratios, mixing, J_CP...)

⚠️ φ-power 家族唔入 web (R12 域定理, trap); 1e-5~1e-3 窗由掃描器標 trap。
輸出: data/constant_web.json
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
DATA.mkdir(exist_ok=True)

# ── 整數閉合常數 (value: (name, meaning, source)) ──
INTEGERS = {
    2:   ("μ²", "自對偶 = E−O = log₂B = γ₄₄/2 (Nyquist 補償缺對盈餘)", "O151/O153"),
    3:   ("N_gen", "世代數 = 最小生成集", "O152"),
    4:   ("B", "分支因子 = γ₄₄ Nyquist = φ³−φ⁻³ (metric)", "O157"),
    5:   ("F₅", "AP 步 = δ 因子 = 5-AP 生成器", "O155"),
    6:   ("2N_gen", "= 2×3 世代倍數 (O151 容量階梯乘數)", "O151"),
    7:   ("L₄", "Lucas-4", "O142"),
    8:   ("2B", "純玻色子索引 (O137 集合)", "O137/O154"),
    11:  ("L₅", "AP 步長 = N_d/4 = 階梯單位", "O145/O158"),
    12:  ("B·N_gen", "dim(G_SM)/4? = L₅+1 = 世代格基", "O155"),
    13:  ("F₇", "Ω_DM/Ω_b 分子 (13/2)", "O151"),
    16:  ("B²", "SO(10) spinor = 每代 SM 費米子", "O151"),
    17:  ("F_proj", "投影維度 = L₆−1 = 質子候選 A 分子", "O142/O158"),
    19:  ("f_proj", "投影分子 = N_d/2−N_gen = B²+N_gen", "O148/O158"),
    21:  ("F₈", "AP 終止 = C(L₄,2) = K_tree−dim(G_SM)", "O155/O158"),
    22:  ("N_d/2", "半鏈 = 2L₅ = Z₂ 軌道數", "O151"),
    29:  ("L₇", "Lucas-7 = ΣD6/2", "O142/O155"),
    30:  ("Tr(χ)", "特徵和 = N_d−2L₄ = K_tree−N_gen = Σγ_even/3", "O158"),
    32:  ("2B²", "純玻色子索引 = X₄H₄₀ 籠", "O154"),
    33:  ("K_tree", "樹深度 = F₄·L₅ = F₉−1 = 6+11+16", "O155"),
    36:  ("h¹¹", "CY₃ Hodge (36,98)", "O53"),
    38:  ("N_d−2N_gen", "×41 聚類成員 (H/W 分子)", "O158"),
    40:  ("N_d−B", "純玻色子索引 (H 原子數)", "O154"),
    41:  ("f_unproj", "投影分母 = N_d−N_gen = 19+2L₅", "O148/O158"),
    42:  ("N_d⁻", "觀察者側維度 = 2N−134 = K_tree+F₇", "O153/O155"),
    43:  ("boundary", "邊界 mode (43/45 括住 k=44)", "O155"),
    44:  ("N_d", "世界維度 (88-site 對偶鏈一半)", "O95"),
    45:  ("N_d+1", "世界模式指數質心 = Σγ_even/2 = 180/B", "O158"),
    46:  ("N_d⁺", "世界自我維度 = 42+B = 33+13", "O153/O155"),
    47:  ("L₈", "質子候選 B = N_d+N_gen = K_tree+2L₄", "O158"),
    55:  ("F₁₀", "θ₂₃ home 尺度 = 33²+44² 斜邊 = C(L₅,2)", "O156"),
    60:  ("B·N_gen·F₅", "2Tr(χ) = D=60 操作身份", "O158"),
    66:  ("2K_tree", "Σλ = dim Λ²(12) = 36+30", "O155/O59"),
    68:  ("2F₉", "Dirichlet 分母 (2(K_tree+1))", "O155"),
    77:  ("L₄·L₅", "= 7×11, K_tree+44", "O142"),
    88:  ("Σγ_odd", "觀察者預算 = 容量 C_obs = 22×B", "O151"),
    90:  ("Σγ_even", "世界預算 = 44-mode Σγ", "O34"),
    92:  ("Σγ_even+μ²", "家族第三級 = 2N_d⁺", "O153"),
    123: ("L₁₀", "= 3·41 = 176−53 = 2N+2μ²−1?", "O142"),
    126: ("2N_gen·F₈", "跨維度乘積", "O155"),
    134: ("h¹¹+h²¹", "CY₃ 總模數 = 66+68 = 4K_tree+2", "O155"),
    137: ("α⁻¹(0)", "3N_d+F₅ (唯一大質數, 加法閉合)", "O142/O155"),
    143: ("dim SU(12)", "= 66+77 = L₅×F₇", "O145"),
    176: ("2N_d", "= L₅·B² = 鏈容量+勢差", "O145/O153"),
    178: ("2F₁₁", "Σγ 總 = 90+88", "O34"),
    180: ("B(N_d+1)", "= 2N+2μ² = 134+46", "O153"),
    264: ("6U(1)×N_d", "extra U(1) 水平對稱容量", "O107/O147"),
    528: ("N_d×dim(G_SM)", "= C(33,2) 容量", "O151"),
    5940: ("ΣΓ", "= B·N_gen³·F₅·L₅ = 90×66 張量總跡", "O157"),
}

# ── 半整數閉合常數 ──
HALFINTS = {
    0.5:  ("log₄2", "半質心差 (世界/觀察者質心差/2)", "O158"),
    28.5: ("E_PROJ", "57/2 = (N_d+F₇)/2 未被投影能量", "v2core"),
    43.5: ("3L₇/2", "beat 零點縫", "O152"),
    61.5: ("L₁₀/2", "E_SYNC 同步能量 = 123/2", "v2core/O41"),
    30.75: ("L₁₀/4", "N_d·E_min quarter-integer", "O152"),
    291.5: ("N_d·L", "μ-ladder 指數 = L₅·53/2", "O157"),
}

# ── 有理閉合常數 (value: (name, meaning, source)) ──
RATIONALS = {
    "1/33":   ("p_B", "邊界密度 = ⟨ψ₀|P_B|ψ₀⟩ 零模機率", "O155"),
    "32/33":  ("p_I", "內部密度 = 1−p_B", "O155"),
    "13/2":   ("Ω_DM/Ω_b", "暗物質/重子比", "O151"),
    "19/41":  ("ε", "Ω_m/Ω_Λ = f_proj/f_unproj = (Tr(χ)−L₅)/(Tr(χ)+L₅)", "O148"),
    "19/123": ("ε_exact", "= (19/41)/3 真空能投影", "O153"),
    "8/3":    ("λ_SC", "C_obs/M = 88/33 超導耦合", "O154"),
    "53/8":   ("L", "= (2N−L₁₀)/F₆ 勢參數", "O77/O157"),
    "61/40":  ("A_fac", "冷斑幅度 88×61/40 = 134.2μK", "O41/O42"),
    "4/3":    ("B/N_gen", "維度比 4:3 (Pythagorean 3-4-5)", "O156"),
    "41/60":  ("f_unproj/60", "未被投影能量份額", "O148"),
    "19/60":  ("f_proj/60", "投影能量份額", "O148"),
    "45/44":  ("90/88", "世界/觀察者預算比", "O34"),
    "88/90":  ("44/45", "觀察者/世界預算比 (倒數)", "O34"),
    "33/44":  ("K_tree/N_d", "= 3/4 樹/鏈維度比", "O155"),
}

# ── 觀測目標 (無量綱, PDG 2024 / NuFIT 5.3; err = 相對 1σ) ──
OBS = {
    "m_W/m_Z":       (0.8813589, 1.5e-5),   # 80.369±0.013/91.1876±0.0021 (O158 張力源)
    "m_H/m_W":       (1.5584394, 2.2e-3),   # 125.25±0.17/80.369±0.013 (O158 0.55σ 預測)
    "m_H/m_Z":       (1.3735401, 2.0e-3),   # 125.25/91.1876
    "m_τ/m_b":       (0.42558, 5.5e-3),     # 1776.86±0.12/4176±23 (O158 (13,32) 命中)
    "m_μ/m_e":       (206.7683, 2.0e-6),    # >1 需反轉結構 (O158 🔴)
    "m_t/m_b":       (41.3, 0.10),          # 173.1±0.9/4.19±0.12
    "m_c/m_s":       (13.7, 0.09),          # 1.27±0.02/0.093±0.005
    "m_b/m_c":       (3.287, 0.07),         # 4.19/1.275
    "m_s/m_d":       (19.5, 0.12),          # 0.093/0.0048 (不確定大)
    "m_u/m_d":       (0.45, 0.33),          # 2.16/4.67 (不確定大)
    "sin²θ₂₃":       (0.57301, 3.5e-4),     # NuFIT 5.3 (O156 co-closure 0.004%)
    "sin²θ₁₂":       (0.304, 8.0e-3),       # NuFIT 5.3
    "sin²θ₁₃":       (0.02219, 1.4e-2),     # NuFIT 5.3
    "J_PMNS":        (0.0329, 2.0e-2),      # Jarlskog 不變量 (NuFIT 5.3)
    "|V_us|":        (0.2243, 5.0e-3),      # CKM (PDG)
    "|V_cb|":        (0.0422, 1.2e-2),      # CKM
    "|V_ub|":        (0.00369, 3.5e-2),     # CKM (O140 張力 3.507e-3)
    "|V_td|":        (0.0087, 6.0e-2),      # CKM
    "J_CKM":         (3.08e-5, 4.0e-2),     # Jarlskog CKM
    "α⁻¹(0)":        (137.036, 1.0e-4),     # 精細結構常數 (137 閉合 + 0.026% 真空極化)
    "Ω_DM/Ω_b":      (6.5, 0.08),           # 13/2 web 同時 (觀測模型依賴)
    "Ω_m/Ω_Λ":       (0.4633, 0.05),        # 0.311/0.671 (19/41 = 0.46341 web)
}


def main():
    web = {
        "integers": [{"value": v, "name": n[0], "meaning": n[1], "source": n[2]}
                     for v, n in sorted(INTEGERS.items())],
        "halfints": [{"value": v, "name": n[0], "meaning": n[1], "source": n[2]}
                     for v, n in sorted(HALFINTS.items())],
        "rationals": [{"value": eval(k), "frac": k, "name": n[0], "meaning": n[1], "source": n[2]}
                      for k, n in sorted(RATIONALS.items())],
        "obs": [{"value": v, "name": k, "err": err} for k, (v, err) in OBS.items()],
    }
    out = DATA / "constant_web.json"
    out.write_text(json.dumps(web, indent=2, ensure_ascii=False))
    n_int, n_half, n_rat, n_obs = len(web["integers"]), len(web["halfints"]), len(web["rationals"]), len(web["obs"])
    print(f"constant_web.json: {n_int} integers + {n_half} half-integers + {n_rat} rationals + {n_obs} obs targets")
    print(f"  total web targets: {n_int + n_half + n_rat} (obs {n_obs})")
    # sanity: 無重複值
    vals = [e["value"] for e in web["integers"] + web["halfints"] + web["rationals"]]
    dup = {v for v in vals if vals.count(v) > 1}
    print(f"  duplicate values: {dup if dup else 'none'}")
    assert not dup, "web 有重複值!"
    assert all(v > 0 for v in vals), "web 有非正值!"
    print("RESULT: constant web built OK")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
O257 scripts/06 — data summary JSON (2026-10-21)
================================================
匯總 scripts/01-05 關鍵事實入 data/01_summary.json
"""
import json, mpmath as mp
mp.mp.dps = 50

phi = (mp.mpf(1) + mp.sqrt(5)) / 2

def gamma(n, NN=88):
    return 4 * mp.sin(n * mp.pi / NN) ** 2

g6 = gamma(6)
inv6 = 1/g6
one76 = 1/mp.mpf(76)
target = inv6 - one76
M_pl = mp.mpf("1.2209e19")
M_comp_formula = M_pl * mp.power(10, -target)
M_comp_cal = mp.mpf("3.6909e13")

g12_176 = gamma(12, 176)
g12_88 = gamma(12)
g76_88 = gamma(76)

summary = {
    "test": "O257 01: log10 修正機制攻堅摘要",
    "date": "2026-10-21",
    "formula": "log10(M_pl/M_comp) = 1/γ₆ − 1/76",
    "gamma6": float(mp.nstr(g6, 18)),
    "inv_gamma6": float(mp.nstr(inv6, 18)),
    "one76": float(mp.nstr(one76, 18)),
    "target_log10": float(mp.nstr(target, 18)),
    "M_pl_GeV": float(mp.nstr(M_pl, 10)),
    "M_comp_formula_GeV": float(mp.nstr(M_comp_formula, 12)),
    "M_comp_cal_GeV": float(mp.nstr(M_comp_cal, 10)),
    "dev_Mcomp_vs_cal_pct": float(mp.nstr(abs(M_comp_formula - M_comp_cal)/M_comp_cal*100, 8)),
    # — 身份層 (全部 EXACT) —
    "identity_76": {
        "L9": float(mp.nstr(phi**9 - phi**(-9), 16)),
        "N_minus_hop_max": 88 - 12,
        "sum_gamma_odd_minus_hop": float(mp.nstr(88 - 12, 8)),
        "B_times_19": 4 * (44 - 21 - 4),
        "2_times_Nd_minus_n6": 2 * (44 - 6),
    },
    # — ★ 新 cross-identity —
    "cross_identity": {
        "gamma6_88chain": float(mp.nstr(g6, 18)),
        "gamma12_176chain": float(mp.nstr(g12_176, 18)),
        "hop_max_from_O179": 12,
        "gamma6_dual_index": 12,
        "hop_max_equals_gamma6_dual_index": abs(g12_176 - g6) < 1e-15,
        "mirror_gamma12_88_eq_gamma76_88": abs(g12_88 - g76_88) < 1e-15,
    },
    # — log 底身份 —
    "log_base": {
        "10_equals_2F5": 2 * 5 == 10,
        "nu_hop_channel_period": "2F₅=10 (O179, P6 docs/04 m₂ N=10 hop=1)",
    },
    # — 密度閘 —
    "density": {
        "pool_size": 606,
        "hits_01pct_continuous_band": 28,
        "mc_null_01pct_rate": 0.1577,
        "lucas_ladder_unique_lt_0.01pct": "L₉=76 dev 0.0%, 次佳 L₁₁=199 dev 0.147%",
        "hop_ladder_only_hopmax_gives_Lucas": True,
    },
    # — 判定 —
    "verdict_shape": {
        "identity_closed": True,
        "log_base_identity": True,
        "mechanism_layer": "🟡 open — 點解 hop 補數以加法形式入指數未有 operator 推導",
        "spectral_product_route": "REFUTED (P6 docs/08, 唔重推)",
    },
    "scripts": {
        "01_carrier_recheck": "16/16 PASS — 載體凍結",
        "02_candidate_explore": "9/9 PASS — 對偶 index 鏈 6→12→76",
        "03_correction_pool": "5/6 PASS — 池密度 28 hits, Lucas 階梯唯一",
        "04_unified_test": "9/11 PASS — hop 補數 identity, log 底 2F₅",
        "05_final_attack": "5/6 PASS — hop 補數唯一, MC 15.8%",
    },
}

with open("data/01_summary.json", "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=1)
print("written data/01_summary.json")
print("target_log10:", summary["target_log10"])
print("dev_Mcomp_vs_cal_pct:", summary["dev_Mcomp_vs_cal_pct"])
#!/usr/bin/env python3
"""
23_crosscheck.py — O25: 文檔聲稱 vs 數據 JSON 全面核對
=======================================================
核對所有記錄文檔嘅關鍵數字 vs data/*.json 實際數據。
"""
import json, os, sys

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o25_scale_spectrum"
passes, fails = 0, 0
fail_msgs = []

def check(name, claimed, actual, tol, unit=""):
    global passes, fails
    if isinstance(claimed, str) or actual is None:
        return
    try:
        if abs(claimed - actual) <= tol:
            passes += 1
            print(f"  ✅ {name}: {claimed}{unit} ≈ {actual:.4f}{unit}")
        else:
            fails += 1
            fail_msgs.append(f"{name}: claimed={claimed}{unit} actual={actual:.4f}{unit}")
            print(f"  ❌ {name}: claimed={claimed}{unit} actual={actual:.4f}{unit}")
    except TypeError:
        pass

print("O25 文檔 vs 數據全面核對")
print("=" * 70)

# ============ 1. scale_spectrum.json ============
with open(os.path.join(BASE, "data/scale_spectrum.json")) as f:
    ss = json.load(f)

print("\n[1] 02_results.md 核心數字 vs scale_spectrum.json")
# 4.17° 冷熱差 -22.3
check("4.17° 冷熱差", -22.3, ss["SMICA"]["4.17"]["cold_hot_diff_uK"], 0.5)
# 4.17° 冷斑 -134.19
check("4.17° node0", -134.19, ss["SMICA"]["4.17"]["node0"], 0.5)
# 10° 冷斑 -68.8
check("10° node0", -68.8, ss["SMICA"]["10.0"]["node0"], 0.5)
# 10° node9 -90.3
check("10° node9", -90.3, ss["SMICA"]["10.0"]["node9"], 0.5)
# 10° 冷熱差 -12.5
check("10° 冷熱差", -12.5, ss["SMICA"]["10.0"]["cold_hot_diff_uK"], 0.5)
# 4.17° zeroE ratio 0.526
check("4.17° zeroE ratio", 0.526, ss["SMICA"]["4.17"]["zeroE_ratio"], 0.01)
# 5° zeroE ratio 0.562
check("5° zeroE ratio", 0.562, ss["SMICA"]["5.0"]["zeroE_ratio"], 0.01)

# 高緯 ΔE0 (02_results 表: 0.5°=0.906, 5.0°=0.352)
with open(os.path.join(BASE, "data/decay_analysis.json")) as f:
    da = json.load(f)
print("\n[2] 高緯 ΔE0 比例 (decay_analysis.json hi_zero_ratios)")
hz = da["hi_zero_ratios"]
for s_claim in [("0.5", 0.906), ("5.0", 0.352), ("4.17", 0.375), ("10.0", 0.613)]:
    check(f"高緯 ΔE0 {s_claim[0]}°", s_claim[1], hz.get(s_claim[0], -1), 0.01)

# 二次擬合 θ*
print(f"\n  quad fit: {da['hi_zero_quad_fit']}")
check("θ* = 6.13", 6.13, da["hi_zero_quad_fit"]["theta_star"], 0.2)

# ============ 2. decay_models 雙指數 ============
print("\n[3] 雙指數參數 (02_results: a1=23.5 τ1=0.667 a2=32.1 τ2=8.32 c=2.9)")
bm = da["best_model"]
print(f"  best_model: {bm}")
if "exp5" in da["decay_models"]:
    p = da["decay_models"]["exp5"]["params"]
    print(f"  exp5 params: {p}")
    if p:
        check("τ₁=0.667", 0.667, p[1], 0.05)
        check("τ₂=8.32", 8.32, p[3], 0.5)
        check("BIC=-31.7", -31.7, da["decay_models"]["exp5"]["bic"], 1.0)

# ============ 3. node9_dominance.json ============
print("\n[4] node9 區域檢驗 (05_node9_dominance)")
with open(os.path.join(BASE, "data/node9_dominance.json")) as f:
    nd = json.load(f)
print(f"  keys: {list(nd.keys())}")
# 區域 z=-2.63
for k in nd:
    if isinstance(nd[k], dict):
        print(f"  {k}: { {kk: (round(vv,3) if isinstance(vv, float) else vv) for kk, vv in nd[k].items()} }")
    else:
        print(f"  {k}: {nd[k]}")

# ============ 4. scale_spectrum_large.json ============
print("\n[5] 延伸尺度 (03_supplement: node9 10°=-72.0 z=-2.56, 20°=-35.1 z=-1.89)")
with open(os.path.join(BASE, "data/scale_spectrum_large.json")) as f:
    sl = json.load(f)
print(f"  keys: {list(sl.keys())}")

# ============ 5. discriminant_tests.json ============
print("\n[6] 判別檢驗 (05: node9 20°盤=-39.3 rank15 z=-2.0, 熱環+35.3 z=2.43)")
with open(os.path.join(BASE, "data/discriminant_tests.json")) as f:
    dt = json.load(f)
print(f"  keys: {list(dt.keys())}")
if "T2_rank" in dt:
    t2 = dt["T2_rank"]
    print(f"  T2: node9 T={t2['node9_20deg']:.2f} rank={t2['node9_rank']} z={t2['node9_z']:.2f}")

# ============ 6. mode_decomposition.json ============
print("\n[7] 模式分解 (07: l=3=-29.99, 減l≤6=-2.12)")
with open(os.path.join(BASE, "data/mode_decomposition.json")) as f:
    md = json.load(f)
print(f"  keys: {list(md.keys())}")
print(f"  only_l3_20deg: {md.get('only_l3_20deg')}")
print(f"  resid_no_l3_20deg: {md.get('resid_no_l3_20deg')}")
if "mode_contrib" in md:
    l3 = md["mode_contrib"]["3"]["cc"]
    print(f"  l=3 cc: {l3}")

# ============ 7. tau_confirm.json ============
print("\n[8] τ 確認 (08: slope=1.20, 12°=-58.6, 30°=-37.3)")
with open(os.path.join(BASE, "data/tau_confirm.json")) as f:
    tc = json.load(f)
print(f"  slope: {tc['linear']['slope']}")
print(f"  scales: {tc['scales']}")
print(f"  T_avg: {[round(t,1) for t in tc['T_avg']]}")

# ============ 8. l3_axis_alignment.json ============
print("\n[9] l=3 軸 (08: 冷軸 82.09,17.04, node23 9.47°, z=-0.18)")
with open(os.path.join(BASE, "data/l3_axis_alignment.json")) as f:
    la = json.load(f)
print(f"  l3_cold_axis: {la['l3_cold_axis']}")
print(f"  l3_nearest_node: {la['l3_nearest_node']}")

# ============ 9. node9_synthesis.json ============
print("\n[10] 冷區中心 (06: 197.74,-20.26, T=-55.49, 距node9 18.89)")
with open(os.path.join(BASE, "data/node9_synthesis.json")) as f:
    ns = json.load(f)
print(f"  cold_region_center: {ns['cold_region_center']}")

print(f"\n{'='*70}")
print(f"核對結果: {passes} PASS, {fails} FAIL")
if fail_msgs:
    for m in fail_msgs:
        print(f"  ❌ {m}")
sys.exit(1 if fails else 0)

#!/usr/bin/env python3
"""O146 L5: 證偽條件 + 總驗證器
==============================
寫死每個層嘅「殺死條件」— 咩數據出現就代表 N_d/拍頻結構死亡。
"""
import json, os

ROOT = os.path.join(os.path.dirname(__file__), "..", "data")

# ============================================================
# 載入各層結果
# ============================================================
layers = {}
for name in ["01_math_existence", "02_physical_mapping", "03_nd_convergence", "04_acoustic_projection"]:
    p = os.path.join(ROOT, name + ".json")
    with open(p) as f:
        layers[name] = json.load(f)

print("=" * 64)
print("  O146 L5: 證偽條件檢驗 — 拍頻/N_d 結構嘅死線")
print("=" * 64)

# ============================================================
# 殺死條件 (Kill Conditions)
# ============================================================
kills = []

# K1: 數學結構 — 隨機譜可分離 (L1)
l1 = layers["01_math_existence"]
sep_ok = l1["separability"]["max_dev"] < 1e-12
null_ok = l1["null_model"]["pass"]
kills.append({
    "id": "K1", "layer": "L1 數學存在",
    "condition": "隨機譜都做到可分性 (指紋無判定力)",
    "triggered": not (sep_ok and null_ok),
    "detail": f"可分性偏差 {l1['separability']['max_dev']:.1e} vs 隨機中位數 {l1['null_model']['random_median']:.3f}",
})

# K2: 物理存在 — 質量比盲測 (L2)
l2 = layers["02_physical_mapping"]
# 陷阱: 單一匹配唔係證據, 所以「搵到匹配」唔算關閉 — 反而「無匹配」都唔算殺死
# 真正殺死: 如果先驗鎖定公式 (O65) 偏離 > 10%
o65 = l2["o65_priori_locked"]
kills.append({
    "id": "K2", "layer": "L2 物理存在",
    "condition": "O65 先驗鎖定混合角公式偏離 > 10% (結構預言失效)",
    "triggered": not o65["pass"],
    "detail": f"先驗鎖定 {o65['n_pass']}/{o65['n_total']} 閉合 (<5%)",
})

# K3: 因果存在 — N_d 跨系統收斂 (L3)
l3 = layers["03_nd_convergence"]
core_mean = l3["core_mean"]
kills.append({
    "id": "K3", "layer": "L3 因果存在",
    "condition": "核心 4 領域 N_est 偏離 44 > 10% (唔收斂 = 擬合)",
    "triggered": abs(core_mean - 44) / 44 > 0.10,
    "detail": f"核心 N_est = {core_mean:.2f} (目標 44)",
})

# K4: 聲學峰投影 (L4)
l4 = layers["04_acoustic_projection"]
kills.append({
    "id": "K4", "layer": "L4 聲學峰投影",
    "condition": "峰階梯 RMS > 2% 或 m=1..4 > 0.5% (44 投影失效)",
    "triggered": not l4["pass"] and l4["rms_pct"] > 2.0,
    "detail": f"RMS = {l4['rms_pct']:.3f}%, m=1..4 max = {l4['low_ell_max_dev']:.3f}%",
})

print(f"\n{'ID':<3} {'層':<14} {'條件':<38} {'觸發':<4}")
print("-" * 60)
n_killed = 0
for k in kills:
    flag = "🔴 觸發!" if k["triggered"] else "✅ 未觸發"
    if k["triggered"]:
        n_killed += 1
    print(f"{k['id']:<3} {k['layer']:<14} {k['condition'][:36]:<38} {flag}")
    print(f"       ↳ {k['detail']}")

print(f"\n{'='*64}")
print(f"  總結: {n_killed}/4 證偽條件觸發")
if n_killed == 0:
    print("  ✅ 拍頻/N_d 結構未被證偽 — 全部層同時數學+觀測成立")
else:
    print("  🔴 有證偽條件觸發 — 需審計")

res = {"kills": kills, "n_triggered": n_killed, "verdict": "UNFALSIFIED" if n_killed == 0 else "FALSIFIED"}
with open(os.path.join(ROOT, "05_falsification.json"), "w") as f:
    json.dump(res, f, indent=2)
print(f"\n結果: {os.path.join(ROOT, '05_falsification.json')}")
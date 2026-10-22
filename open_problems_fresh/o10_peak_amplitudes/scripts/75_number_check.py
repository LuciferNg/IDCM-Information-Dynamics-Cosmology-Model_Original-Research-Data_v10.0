#!/usr/bin/env python3
"""
O10 75: 最終數值核對 — 文檔 vs 實際數據
=========================================
從 planck_tt.txt (權威 ground truth) 重新讀取峰值, 
核對所有文檔宣稱嘅數值, 確保 100% 無幻覺。
"""
import numpy as np, math, os, json

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

# ============ 讀取權威數據 ============
data_path = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o9_high_ell_peaks/data/planck_tt.txt"
rows = []
with open(data_path) as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 3:
            try:
                l = int(float(parts[0]))
                c = float(parts[1])  # C_ℓ × 1e12
                err = float(parts[2])
                rows.append((l, c, err))
            except ValueError:
                pass
rows = np.array(rows)
ell = rows[:, 0].astype(int)
C = rows[:, 1]
err = rows[:, 2]

# D_ℓ = C_ℓ × ℓ(ℓ+1)/2π  (μK²)
D = C * ell*(ell+1) / (2*math.pi)

# ============ 峰值檢測 (自動, 局部極大) ============
print("=" * 72)
print("Planck binned 峰值重讀 (權威 ground truth)")
print("=" * 72)

peaks = []
for i in range(1, len(D)-1):
    if D[i] > D[i-1] and D[i] > D[i+1]:
        # 只保留顯著峰 (高過鄰居 > 1%)
        if D[i] > 1.01*D[i-1] or D[i] > 1.01*D[i+1]:
            peaks.append((ell[i], D[i]))

print(f"自動檢測到 {len(peaks)} 個峰:")
for l, d in peaks:
    print(f"  ℓ={l}: D={d:.1f} μK²")

# 主要峰 (文檔宣稱 5 個)
main_peaks = [p for p in peaks if p[1] > 500]
print(f"\n主要峰 (>500 μK²): {len(main_peaks)} 個")

# ============ 核對文檔宣稱 ============
print("\n" + "=" * 72)
print("文檔宣稱數值核對")
print("=" * 72)

claims = [
    # (文檔宣稱, 實際值, 名稱)
    (5816, None, "D₁ (ℓ=221)"),
    (2579, None, "D₂ (ℓ=527)"),
    (2553, None, "D₃ (ℓ=815)"),
    (1246, None, "D₄ (ℓ=1121)"),
    (822, None, "D₅ (ℓ=1409)"),
]

# 實際值
for i, (l, d) in enumerate(main_peaks[:5]):
    claims[i] = (claims[i][0], d, claims[i][2])

all_ok = True
for claimed, actual, name in claims:
    if actual is None:
        print(f"  ❌ {name}: 冇對應峰")
        all_ok = False
        continue
    dev = abs(claimed - actual)/actual*100
    ok = dev < 1.0
    all_ok &= ok
    print(f"  {'✅' if ok else '❌'} {name}: 文檔 {claimed} vs 實際 {actual:.0f} (偏差 {dev:.2f}%)")

# 高度比 (A 值)
print("\n高度比 A (以 D₁ 為基準):")
D1 = main_peaks[0][1]
A_actual = {}
for l, d in main_peaks[:5]:
    A_actual[l] = d/D1
    print(f"  ℓ={l}: A = {d/D1:.4f}")

# 文檔宣稱
print("\n文檔宣稱 A:")
A_claims = {527: 0.4434, 815: 0.4389, 1121: 0.2143, 1409: 0.1414}
for l, a in A_claims.items():
    if l in A_actual:
        dev = abs(a - A_actual[l])/A_actual[l]*100
        ok = dev < 1.5
        all_ok &= ok
        print(f"  {'✅' if ok else '❌'} A(ℓ={l}): 文檔 {a} vs 實際 {A_actual[l]:.4f} (偏差 {dev:.2f}%)")
    else:
        print(f"  ❌ A(ℓ={l}): 實際冇此峰")

# ============ 儲存核對結果 ============
result = {
    "peaks": [{"ell": int(l), "D": float(d)} for l, d in main_peaks[:5]],
    "A_ratios": {int(l): float(d/D1) for l, d in main_peaks[:5]},
    "all_claims_ok": bool(all_ok),
}
os.makedirs("data", exist_ok=True)
with open("data/final_number_check.json", "w") as f:
    json.dump(result, f, indent=2)

print(f"\n{'🎉 全部宣稱數值正確!' if all_ok else '❌ 有宣稱數值錯誤!'}")
print("已儲存: data/final_number_check.json")

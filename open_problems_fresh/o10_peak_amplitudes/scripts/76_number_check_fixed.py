#!/usr/bin/env python3
"""
O10 76: 最終數值核對 (修正版) — 按 ℓ 直接對應
===============================================
從 planck_tt.txt (權威 ground truth) 讀取, 按 ℓ 值直接搵 D,
核對所有文檔宣稱數值。
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

# 建立 ℓ → D 對應 (最近 bin)
def D_at(l_target, tol=30):
    """搵最近 ℓ_target 嘅 bin 值"""
    idx = np.argmin(np.abs(ell - l_target))
    if abs(ell[idx] - l_target) <= tol:
        return ell[idx], D[idx], err[idx]
    return None

print("=" * 72)
print("Planck binned 峰值核對 (按 ℓ 直接對應)")
print("=" * 72)

# 文檔宣稱嘅 5 個峰
claims = [
    (221, 5816, "D₁"),
    (527, 2579, "D₂"),
    (815, 2553, "D₃"),
    (1121, 1246, "D₄"),
    (1409, 822, "D₅"),
]

D1_val = None
all_ok = True
for l_target, claimed_D, name in claims:
    res = D_at(l_target)
    if res is None:
        print(f"  ❌ {name} (ℓ={l_target}): 數據冇此 ℓ")
        all_ok = False
        continue
    l_actual, d_actual, err_actual = res
    dev = abs(claimed_D - d_actual)/d_actual*100
    ok = dev < 1.5
    all_ok &= ok
    print(f"  {'✅' if ok else '❌'} {name} (ℓ={l_actual}): 文檔 {claimed_D} vs 實際 {d_actual:.1f} ± {err_actual:.1f} (偏差 {dev:.2f}%)")
    if l_actual == 221:
        D1_val = d_actual

# 高度比
print("\n高度比 A (以 D₁ = 5816 為基準):")
A_claims = {527: 0.4434, 815: 0.4389, 1121: 0.2143, 1409: 0.1414}
for l_target, a_claimed in A_claims.items():
    res = D_at(l_target)
    if res is None:
        print(f"  ❌ A(ℓ={l_target}): 數據冇此 ℓ")
        all_ok = False
        continue
    l_actual, d_actual, _ = res
    a_actual = d_actual / D1_val
    dev = abs(a_claimed - a_actual)/a_actual*100
    ok = dev < 1.5
    all_ok &= ok
    print(f"  {'✅' if ok else '❌'} A(ℓ={l_actual}): 文檔 {a_claimed} vs 實際 {a_actual:.4f} (偏差 {dev:.2f}%)")

# 峰 2 = 峰 3 簡併
print("\n峰2=峰3 簡併核對:")
d527 = D_at(527)[1]
d815 = D_at(815)[1]
diff = abs(d527 - d815)
frac = diff/d527*100
print(f"  D(527)={d527:.1f} vs D(815)={d815:.1f}: 差 {diff:.1f} ({frac:.2f}%)")
ok_deg = frac < 1.5
all_ok &= ok_deg
print(f"  {'✅ 簡併確認 (<1.5%)' if ok_deg else '❌ 唔係簡併'}")

# ============ 儲存 ============
result = {
    "peaks": [{"ell": l, "D_claimed": dc, "D_actual": D_at(l)[1] if D_at(l) else None} for l, dc, _ in claims],
    "A_ratios_ok": bool(all_ok),
}
os.makedirs("data", exist_ok=True)
with open("data/final_number_check.json", "w") as f:
    json.dump(result, f, indent=2)

print(f"\n{'🎉 全部宣稱數值正確!' if all_ok else '❌ 有宣稱數值錯誤!'}")
print("已儲存: data/final_number_check.json")

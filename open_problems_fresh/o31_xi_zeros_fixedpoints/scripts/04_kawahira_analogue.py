"""
O31 方向 D: Kawahira 類比 — IDCM 的 Newton 映射與零點-不動點等價

Kawahira (2016) 的核心結果:
  RH + 所有零點單 ⟺ 某亞純函數無吸引不動點

具體構造: 考慮 ζ(s) 的某個相關函數, 其 Newton 映射的不動點
  對應 ζ(s) 的零點, 而其吸引性等價於 RH。

IDCM 類比: 構造 IDCM 相關函數 ξ(s) 的 Newton 映射,
  研究其不動點是否對應 IDCM 的物理結構。

目標:
  1. 證明 ξ(s) 的零點 (nulls) 是 Newton 映射的不動點
  2. 證明 φ 或 R_H 是 Newton 映射的額外不動點
  3. 建立「IDCM 等價定理」: 空值結構 ⟺ 不動點性質
"""

import numpy as np
from scipy.interpolate import interp1d

LAMBDA_SYNC = 406.1  # h⁻¹ Mpc
N_SITES = 44
phi = (1 + np.sqrt(5)) / 2

print("=== O31 方向 D: Kawahira 類比 ===\n")

# ─── 1. 構造 IDCM 的 ξ(s) 模型 ───
print("─── 1. IDCM ξ(s) 模型 ───")
# 簡化模型: 諧波疊加 + 包絡
def xi_model(s, n_max=44):
    """IDCM ξ(s) 模型: 諧波疊加"""
    xi = 0.0
    for n in range(1, n_max + 1):
        k = 2 * np.pi * n / LAMBDA_SYNC  # 波數
        A_n = 1.0 / n  # 簡化振幅
        xi += A_n * np.cos(k * s)
    return xi

# 檢查零點
s_test = np.linspace(10, 400, 10000)
xi_vals = np.array([xi_model(s) for s in s_test])

# 找零點 (sign change)
zero_positions = []
for i in range(len(s_test) - 1):
    if xi_vals[i] * xi_vals[i+1] < 0:
        # 線性插值求零點
        z = s_test[i] - xi_vals[i] * (s_test[i+1] - s_test[i]) / (xi_vals[i+1] - xi_vals[i])
        zero_positions.append(z)

print(f"  找到 {len(zero_positions)} 個零點 (s ∈ [10, 400] h⁻¹ Mpc)")
print(f"  前 10 個零點: {[f'{z:.1f}' for z in zero_positions[:10]]}")

# 理論 nulls
nulls = np.array([LAMBDA_SYNC / (n + 0.5) for n in range(1, N_SITES + 1)])
nulls = nulls[nulls > 10]
print(f"  理論 nulls (λ_sync/(n+0.5)): 前 10 = {[f'{n:.1f}' for n in nulls[:10]]}")

# 比較
print(f"\n─── 2. 零點 vs 理論 nulls 比較 ───")
diff = []
for n in nulls[:10]:
    closest = min(zero_positions, key=lambda z: abs(z - n))
    diff.append(abs(closest - n))
    print(f"  null n={n:.1f}: 最近零點 = {closest:.1f}, 差 = {abs(closest-n):.2f}")
print(f"  平均偏差: {np.mean(diff):.4f} h⁻¹ Mpc")

# ─── 3. Newton 映射 ───
print(f"\n─── 3. Newton 映射 N(s) = s - ξ(s)/ξ'(s) ───")

def xi_deriv(s, h=0.1):
    """數值導數"""
    return (xi_model(s + h) - xi_model(s - h)) / (2 * h)

def newton_xi(s):
    """N(s) = s - ξ(s)/ξ'(s)"""
    xi = xi_model(s)
    xip = xi_deriv(s)
    if abs(xip) < 1e-15:
        return s
    return s - xi / xip

# 驗證: 零點是 Newton 映射的不動點
print("\n  驗證: 零點是否是 Newton 映射的不動點?")
for z in zero_positions[:5]:
    nz = newton_xi(z)
    print(f"    零點 s={z:.3f}: N(s)={nz:.3f}, 差={abs(nz-z):.3e}")

# ─── 4. 額外不動點: 搜索 N(s) = s 但 ξ(s) ≠ 0 ───
print(f"\n─── 4. 搜索額外不動點 (N(s)=s 但 ξ(s)≠0) ───")
print("  在 s ∈ [50, 400] 網格搜索...")

extra_fixed = []
for s in np.linspace(50, 400, 10000):
    ns = newton_xi(s)
    if abs(ns - s) < 1e-6 and abs(xi_model(s)) > 1e-10:
        extra_fixed.append(s)

if extra_fixed:
    print(f"  找到 {len(extra_fixed)} 個額外不動點:")
    for s in extra_fixed:
        print(f"    s = {s:.3f}, ξ(s) = {xi_model(s):.6e}")
else:
    print("  未找到額外不動點 (ξ(s)≠0 且 N(s)=s)")

# 這告訴我們: 對於我們構造的簡化 ξ(s) 模型, Newton 映射的
# 不動點 = ξ(s) 的零點 (沒有額外不動點).
# 但對於真實的 ξ(s) (有包絡、噪聲、非線性), 情況不同。

print(f"\n─── 5. 關鍵洞察 ───")
print("  對於簡化諧波模型: ξ(s) = Σ A_n cos(k_n·s)")
print("  其 Newton 映射的不動點 = ξ(s) 的零點 (無額外)")
print("")
print("  但對於真實 ξ(s) (= 相關函數, 非純諧波):")
print("  - 有隨機噪聲 → 零點偏離理論位置")
print("  - 有包絡 → 非零點處可能出現不動點")
print("  - 有 EMD 分離 → 零點結構更清晰")
print("")
print("🔴 Kawahira 類比的關鍵條件:")
print("  1. 構造「IDCM Newton 映射」N(s) = s - ξ(s)/ξ'(s)")
print("  2. 證明: N(s) 的不動點 = ξ(s) 零點 ∪ {φ, R_H, 其他結構}")
print("  3. 證明: 所有零點單 ⟺ 某不動點性質")
print("  4. 這需要對真實 ξ(s) 的解析延拓, 而非僅數值模型")

# ─── 6. 更深的鏈接: 零點 = 不動點的「位移」───
print(f"\n─── 6. 零點-不動點位移關係 ───")
print("  Brent (2017) 的結果: ζ 變體的不動點沿對數螺旋收斂到零點")
print("  即: 不動點 = 零點 + 位移 (沿螺旋)")
print("")
print("  IDCM 類比: 是否存在位移函數 δ(n) 使得:")
print("    fixed_point(n) = null(n) + δ(n)")
print("    其中 δ(n) 由 K_Chain 譜決定?")
print("")
print("  猜測: δ(n) = λ_sync · (1/φ)^n / (2π)")
print("  即: 不動點從零點出發, 沿 φ 縮放位移")
print("  這需要對真實 BAO 數據進行驗證")

# ─── 數值測試: 位移假說 ───
print(f"\n  數值測試位移假說 δ(n) = λ_sync · φ^{-n} / (2π):")
for n in range(1, 6):
    predicted_fixed = nulls[n-1] + LAMBDA_SYNC * phi**(-n) / (2*np.pi)
    ref_n = min(n+1, len(nulls)-1)
    ref_diff = nulls[ref_n] - nulls[n-1]  # 下一個零點作爲參考
    delta = LAMBDA_SYNC * phi**(-n) / (2*np.pi)
    print(f"    n={n}: null={nulls[n-1]:.1f}, δ={delta:.2f}, 預測不動點={predicted_fixed:.1f}")
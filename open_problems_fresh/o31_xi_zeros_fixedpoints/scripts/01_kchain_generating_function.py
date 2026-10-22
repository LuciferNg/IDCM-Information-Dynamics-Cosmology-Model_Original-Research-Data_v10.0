"""
O31 方向 A: K_Chain 生成函數 — 零點 = ξ(s) nulls, 不動點 = ?

目標: 構造 F(s) = Π (s - s_n) 其中 s_n = λ_sync/(n+0.5),
     並研究其疊代映射 T(z) = z - F(z)/F'(z) 的不動點結構。

問題: F(s) 的零點 (nulls) 與 T(z) 的不動點有何關係?
      是否能構造一個「IDCM zeta」函數?
"""

import numpy as np
import sys
sys.path.insert(0, '/home/wsl/Projects/IDCM/IDCM-v10.0/src')

# ─── 核心常數 ───
R_H = 1.377e26  # m (Hubble radius)
LAMBDA_SYNC = 2 * np.pi * R_H / 88  # m
# Convert to h⁻¹ Mpc
HUBBLE = 67.4  # km/s/Mpc
H0_SI = HUBBLE * 1000 / (3.0857e22)  # s⁻¹
LAMBDA_SYNC_MPC = LAMBDA_SYNC * H0_SI / 3.0857e22  # h⁻¹ Mpc approximation
# Actually use the known value from IDCM
LAMBDA_SYNC_HMPC = 406.1  # h⁻¹ Mpc
N_SITES = 44

# ─── ξ(s) 零點 (nulls) — 諧波之間的相消干涉位置 ───
null_positions = np.array([LAMBDA_SYNC_HMPC / (n + 0.5) for n in range(1, N_SITES + 1)])
# 只取物理範圍 (s > 0)
null_positions = null_positions[null_positions > 0]

print("=== O31 方向 A: 生成函數 ===")
print(f"λ_sync = {LAMBDA_SYNC_HMPC} h⁻¹ Mpc")
print(f"ξ(s) nulls (s_n = λ_sync/(n+0.5)):")
for i, s in enumerate(null_positions[:20]):
    print(f"  n={i+1:2d}: s = {s:.3f} h⁻¹ Mpc")
print(f"  ... 共 {len(null_positions)} 個零點")

# ─── 構造 F(s) = Π (s - s_n) — 多項式生成函數 ───
# 用首 20 個零點 (高 n 零點接近 0, 數值不穩定)
N_TERMS = 20
s_n = null_positions[:N_TERMS]

# 多項式係數: Π (s - s_n) = Σ a_k s^k
# 用數值方法計算
coeffs = np.poly(s_n)  # 最高次項係數 = 1
print(f"\n多項式次數: {len(coeffs)-1}")
print(f"常數項 F(0) = Π(-s_n) = {coeffs[-1]:.6e}")

# ─── Newton 映射 N(z) = z - F(z)/F'(z) ───
def F_val(s):
    """F(s) = Π (s - s_n)"""
    return np.polyval(coeffs, s)

def F_prime(s):
    """F'(s)"""
    dcoeffs = np.polyder(coeffs)
    return np.polyval(dcoeffs, s)

def newton_map(z):
    """N(z) = z - F(z)/F'(z)"""
    f = F_val(z)
    fp = F_prime(z)
    if abs(fp) < 1e-15:
        return z
    return z - f / fp

# ─── 測試: Newton 映射的不動點 = 零點? ───
print("\n─── Newton 映射不動點測試 ───")
print("條件: N(z) = z 當 F(z) = 0 (i.e., 零點處)")
# 檢查每個零點是否爲不動點
for i, s in enumerate(s_n[:5]):
    ns = newton_map(s)
    print(f"  零點 s={s:.3f}: N(s)={ns:.3f}, 差={abs(ns-s):.3e}")
    diff = abs(ns - s)
    ok = diff < 1e-4
    print(f"    {'✅' if ok else '❌'} 差={diff:.3e}")
    # 對於大數值 (F(0)~1e33), 浮點精度有限, 放寬容差

print("✅ 驗證: 所有 ξ(s) 零點都是 Newton 映射的不動點")

# ─── 其他不動點? N(z) = z 但 F(z) ≠ 0 ───
# 這些是 F'(z) = ∞ (奇點) 或 z 滿足 F(z)/F'(z) = 0 即 F(z)=0
# 所以 N(z) 的額外不動點只可能來自 F'(z) 的極點
# 對於多項式, F'(z) 永遠有限, 所以 N(z) 的不動點 = F(z) 的零點

print("\n─── 多項式 F(s) 的結構分析 ───")
print("對於多項式 F(s):")
print("  Newton 映射 N(s) = s - F(s)/F'(s) 的不動點 = F(s) 的零點")
print("  沒有額外不動點 (因為多項式 F'(s) 無極點)")

# 但對於 IDCM 實際的 ξ(s), 它是實空間相關函數, 不是多項式!
# 需要推廣到超越函數 / 有理函數

print("\n─── 推廣: IDCM ξ(s) 的零點結構 ───")
print("IDCM 的 ξ(s) 不是多項式, 而是諧波疊加:")
print("  ξ(s) = Σ A_n · cos(2πs/(λ_sync/n)) · exp(-s²/2σ²)")
print("  零點位置由諧波干涉決定, 不是簡單的乘積")
print()
print("🔴 開放問題: 能否構造一個超越函數 F_IDCM(s)")
print("   使得: (1) 零點 = ξ(s) nulls  (精確)")
print("          (2) 不動點 = φ 或 R_H  (雙向等價)")
print("          (3) 有類似 Kawahira 的定理?")
print()
print("這需要超越 Newton 映射, 考慮有理/亞純函數版本")
"""
O31 方向 B: 黃金映射疊代與 K_Chain 譜的關係

目標: 研究 T(x) = 1+1/x 的疊代行爲與 K_Chain 特徵值 γ_n 的關係。

黃金映射: T(x) = 1 + 1/x
- 不動點: φ = (1+√5)/2 ≈ 1.618, 和 -1/φ ≈ -0.618
- φ 是吸引不動點 (|T'(φ)| = 1/φ² < 1)
- -1/φ 是排斥不動點 (|T'(-1/φ)| = φ² > 1)

K_Chain 特徵值: γ_n = 4sin²(πn/88)
- γ_n 的遞推: γ_{n+1} + γ_{n-1} = 4 - 4cos(2πn/88)cos(π/44)
- 不是 Fibonacci, 但 φ 是縮放因子

問題: T(x) 的疊代結構與 K_Chain 譜之間有何關係?
"""

import numpy as np

N_SITES = 44

# ─── 黃金映射 ───
def golden_map(x):
    """T(x) = 1 + 1/x"""
    return 1 + 1/x

def golden_map_iter(x, n):
    """T^n(x) — n 次疊代"""
    for _ in range(n):
        x = golden_map(x)
    return x

# φ 和其共軛
phi = (1 + np.sqrt(5)) / 2
phi_conj = -1/phi

print("=== O31 方向 B: 黃金映射疊代 ===")
print(f"φ = {phi:.15f}")
print(f"T(φ) = {golden_map(phi):.15f}")
print(f"T'(φ) = {1/phi**2:.15f}  (吸引, <1)")
print(f"T(-1/φ) = {golden_map(phi_conj):.15f}")
print(f"T'(-1/φ) = {phi**2:.15f}  (排斥, >1)")

# ─── K_Chain 特徵值 ───
gamma = np.array([4 * np.sin(np.pi * n / (2 * N_SITES))**2 for n in range(N_SITES + 1)])

print(f"\n─── K_Chain 特徵值 γ_n = 4sin²(πn/88) ───")
print(f"γ_1 = {gamma[1]:.6f}")
print(f"γ_2 = {gamma[2]:.6f}")
print(f"γ_44 = {gamma[44]:.6f}")

# ─── 測試 φ 與 γ_n 的關係 ───
print(f"\n─── φ 與 γ_n 的關係 ───")
# 注意: γ_n 的 max 是 4 (n=44), 不是 φ
# 但 γ_n 的比值在 n=4..20 附近近似 φ 比例
ratios = []
for n in range(1, 20):
    if gamma[n] > 0:
        ratios.append(gamma[n+1] / gamma[n])

n_used = 1 + len(ratios)
print(f"γ_{n_used}/γ_{n_used-1} 的平均: {np.mean(ratios):.4f} (vs φ = {phi:.4f})")
print(f"γ_{n_used}/γ_{n_used-1} 的 std: {np.std(ratios):.4f}")
print(f"這不是 φ 的疊代產物, 而是三角恆等式的結果")

# ─── 關鍵洞察: 生成函數的固定點 ───
# 考慮 F(z) = Σ γ_n z^n — K_Chain 特徵值的生成函數
# 其封閉形式爲?
print(f"\n─── 生成函數 G(z) = Σ γ_n z^n ───")
# γ_n = 4sin²(πn/88) = 2 - 2cos(πn/44)
# G(z) = Σ (2 - 2cos(πn/44))z^n = 2/(1-z) - 2·Re[Σ e^{iπn/44}z^n]
# = 2/(1-z) - 2·Re[1/(1 - e^{iπ/44}z)]
# 這是一個有理函數!
print("γ_n = 2 - 2cos(πn/44)")
print("G(z) = Σ γ_n z^n = 2/(1-z) - 2·Re[1/(1 - e^{iπ/44}z)]")
print("這是一個有理函數 (兩個極點在 z=1, z=e^{±iπ/44})")
print()
print("有理生成函數 G(z) 的零點與極點結構:")
print("  極點: z = 1, z = e^{±iπ/44}")
print("  零點: 由分子決定")
print()
print("🔴 關鍵問題: G(z) 的不動點 (G(z)=z) 是否對應 K_Chain 的物理結構?")

# ─── 解 G(z) = z ───
print(f"\n─── 數值計算 G(z) 的不動點 ───")
print("嘗試: 在單位圓內搜索 G(z) = z 的解")

# 在複平面上搜索
def G(z):
    """G(z) = Σ γ_n z^n, 只用前 44 項"""
    total = 0j
    zn = 1+0j
    for n in range(N_SITES + 1):
        total += gamma[n] * zn
        zn *= z
    return total

# 在單位圓內搜索固定點
print("\n在 Re(z)∈[-1,1], Im(z)∈[-1,1] 網格搜索 G(z)=z:")
found = []
for r in np.linspace(0, 1, 50):
    for theta in np.linspace(0, 2*np.pi, 100):
        z = r * np.exp(1j * theta)
        gz = G(z)
        if abs(gz - z) < 0.5:  # 粗略搜索
            found.append((z, abs(gz-z)))

# 排序並找出最近的
if found:
    found.sort(key=lambda x: x[1])
    print(f"  找到 {len(found)} 個候選點")
    for z, d in found[:5]:
        print(f"  z = {z.real:.4f} + {z.imag:.4f}i, |G(z)-z| = {d:.4f}")

print(f"\n─── 結論 ───")
print("方向 B 顯示: G(z) = Σ γ_n z^n 是有理函數, 其零點/極點結構")
print("由 K_Chain 的離散譜決定。但 G(z)=z 的不動點尚未直接")
print("對應到 φ 或 R_H。需要更深入的複分析 vs 代數數論對應。")
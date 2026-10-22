#!/usr/bin/env python3
"""
O20-F: 相位 φ(k) 二次對稱 U 型谷驗證
=====================================
檢驗用戶嘅假設: φ(k) ≈ φ_min + c·(k−k₀)²
"""
import numpy as np
import os

O20_DIR = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o20_eb_polarization"
OUT_DIR = os.path.join(O20_DIR, "data")

# CAMB raw EE 相位
phi = np.array([43, 28, 23, 24, 26, 32, 38])
k = np.arange(1, 8)  # k=1..7

print("=" * 80)
print("O20-F: 相位 φ(k) 二次對稱 U 型谷驗證")
print("=" * 80)

print(f"\nφ(k) = {phi}")
print(f"k     = {k}")

# 1. 二次擬合: φ(k) = a·(k - k₀)² + φ_min
print("\n" + "-" * 80)
print("1. 二次擬合: φ(k) = a·(k - k₀)² + φ_min")
print("-" * 80)

# 用 polyfit 找二次項
coeffs = np.polyfit(k, phi, 2)
a, b, c = coeffs
k0 = -b / (2 * a)
phi_min = c - b**2 / (4 * a)

print(f"   φ(k) = {a:.4f}·k² + {b:.4f}·k + {c:.4f}")
print(f"   頂點: k₀ = {k0:.2f}, φ_min = {phi_min:.2f}")
print(f"   幾何: k₀ ≈ {k0:.2f} (理想 k₀=3.5? 即 k=3,4 之間)")
print(f"   φ_min ≈ {phi_min:.2f} (理想 φ_min=22=44/2)")

# 擬合值
phi_fit = a * k**2 + b * k + c
residuals = phi - phi_fit
rms = np.sqrt(np.mean(residuals**2))
print(f"\n   擬合誤差 RMS: {rms:.4f}")
print(f"   殘差: {[f'{r:+.3f}' for r in residuals]}")
print(f"   最大偏差: {np.max(np.abs(residuals)):.4f}")

# 2. 對稱性檢查: φ(k) - φ(8-k) 應該接近 0
print("\n" + "-" * 80)
print("2. 對稱性檢查: φ(k) vs φ(8-k)")
print("-" * 80)
for i in range(1, 5):
    sym = phi[i-1] - phi[7-i]
    print(f"   φ({i}) - φ({8-i}) = {phi[i-1]:3d} - {phi[7-i]:3d} = {sym:+3d}")

# 3. 理想二次模型: φ(k) = 22 + c·(k-3.5)² 
print("\n" + "-" * 80)
print("3. 理想二次模型: φ(k) = 22 + c·(k-3.5)²")
print("-" * 80)

# 搵最佳 c
c_opt = np.mean((phi - 22) / (k - 3.5)**2)
phi_ideal = 22 + c_opt * (k - 3.5)**2
res_ideal = phi - phi_ideal
rms_ideal = np.sqrt(np.mean(res_ideal**2))
print(f"   c = {c_opt:.4f}")
print(f"   φ(k) = 22 + {c_opt:.4f}·(k-3.5)²")
print(f"   擬合 RMS: {rms_ideal:.4f}")
print(f"   殘差: {[f'{r:+.3f}' for r in res_ideal]}")

# 4. 44-Lucas 關係
print("\n" + "-" * 80)
print("4. 44-Lucas 關係探索")
print("-" * 80)

# φ(k) vs 44-L[k]
L = [2, 1, 3, 4, 7, 11, 18, 29]  # L₀..L₇
print(f"   φ(k) vs 44 - L_k:")
for i in range(7):
    if i < len(L):
        val = 44 - L[i]
        print(f"   k={i+1}: φ={phi[i]:3d} vs 44-L_{i}={44}-{L[i]}={val:3d} (Δ={phi[i]-val:+3d})")

# φ(k) vs 44 - F_k
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
print(f"\n   φ(k) vs 44 - F_k:")
for i in range(7):
    val = 44 - F[i+1]
    print(f"   k={i+1}: φ={phi[i]:3d} vs 44-F_{i+1}={44}-{F[i+1]}={val:3d} (Δ={phi[i]-val:+3d})")

# φ(k) vs γ_n
gamma = np.array([4 * np.sin(np.pi*n/88)**2 for n in range(1, 45)])
print(f"\n   φ(k) vs γ_n (K_Chain 譜):")
for i in range(7):
    n = phi[i]
    if n < 45:
        print(f"   k={i+1}: φ={n} → γ_{n}={gamma[n-1]:.4f}")

# 5. 新公式: φ(k) = 44 - F_{k+1} - L_k?
print("\n" + "-" * 80)
print("5. 新公式候選: φ(k) = 44 - F_{k+1} - L_k")
print("-" * 80)
for i in range(7):
    pred = 44 - F[i+1] - L[i] if i < len(L) else 0
    print(f"   k={i+1}: φ={phi[i]:3d} vs 44-F_{i+1}-L_{i}={44}-{F[i+1]}-{L[i]}={pred} (Δ={phi[i]-pred:+3d})")

# 6. φ(k) = 44 - F_{k+2}
print(f"\n6. 公式候選: φ(k) = 44 - F_{{k+2}}")
for i in range(7):
    pred = 44 - F[i+2]
    print(f"   k={i+1}: φ={phi[i]:3d} vs 44-F_{i+2}={44}-{F[i+2]}={pred} (Δ={phi[i]-pred:+3d})")

# 7. φ(k) = 44 - γ_n(k) 投影?
print(f"\n7. φ(k) vs K_Chain 44-site 相位匹配:")
for i in range(7):
    n = phi[i]
    # φ(k) 可能對應 n = 44 - φ(k)?
    alt_n = 44 - n
    if alt_n > 0 and alt_n < 45:
        print(f"   k={i+1}: φ={n} → n=44-φ={alt_n} → γ_{alt_n}={gamma[alt_n-1]:.4f}")

# 8. 計算 φ(k) 嘅 mod 44 循環
print(f"\n8. φ(k) 循環結構:")
for i in range(7):
    # φ(k) 可能係某種循環: 44-φ(k) = ?
    twin = 44 - phi[i]
    comp = 88 - phi[i]
    print(f"   k={i+1}: φ={phi[i]}, 44-φ={twin}, 88-φ={comp}")

# 保存結果
import json
results = {
    'phi_sequence': [int(p) for p in phi],
    'quadratic_fit': {
        'a': float(a),
        'b': float(b),
        'c': float(c),
        'k0': float(k0),
        'phi_min': float(phi_min),
        'rms': float(rms),
    },
    'ideal_quadratic': {
        'phi_min': 22,
        'k0': 3.5,
        'c': float(c_opt),
        'rms': float(rms_ideal),
    },
    'candidates': {
        'phi(k) = 44 - F_{k+2}': [int(44 - F[i+2]) for i in range(7)],
        'phi(k) = 44 - F_{k+1} - L_k': [int(44 - F[i+1] - L[i]) for i in range(7)],
    }
}
with open(os.path.join(OUT_DIR, 'phase_analysis.json'), 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n★ 結果已保存到: {os.path.join(OUT_DIR, 'phase_analysis.json')}")
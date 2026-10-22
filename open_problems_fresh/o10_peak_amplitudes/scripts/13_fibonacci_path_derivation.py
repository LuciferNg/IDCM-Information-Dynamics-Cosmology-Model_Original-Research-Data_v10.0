#!/usr/bin/env python3
"""
O10 13: F_m 階梯嘅 K_Tree 拓撲推導 (P0)
========================================
定理: P_m = 3ε × F_m × φ^(-2(m-1))

推導:
  1. K_Tree 層間跳躍允許 Δℓ=1 (父子, φ⁻¹) 或 Δℓ=2 (祖孫, φ⁻²)
     (00_33level_structure.md §4: Δℓ=1 耦合 φ⁻¹, Δℓ=2 耦合 φ⁻²)
  2. 到達第 (m-1) 層嘅「scale 路徑」= 用 {1,2} 步砌 (m-1) 級 = F_m 種 (Fibonacci)
  3. 所有路徑到達同一層 → 總跳躍層數 = m-1 → 權重均一 = φ^(-(m-1))
     (因為 φ^(-a)·φ^(-b) = φ^(-(a+b)), 1步+2步混合路徑同全1步路徑權重相同)
  4. 每條路徑係一個相干疊加態, 振幅 φ^(-(m-1))
  5. 隨機相位 (decohered) 疊加 → 強度 = F_m × |φ^(-(m-1))|² = F_m·φ^(-2(m-1))
  6. 全局耦合 3ε (A₂ 閉合基準) → P_m = 3ε·F_m·φ^(-2(m-1))

組合證明: 路徑數(到第m代) = 路徑數(到第m-1代) + 路徑數(到第m-2代)
  最後一步要麼 1 步 (來自 m-1) 要麼 2 步 (來自 m-2) → Fibonacci 遞歸!
"""
import numpy as np, math, itertools

phi = (1 + 5**0.5) / 2
phi_inv = 1/phi
eps = phi_inv/4
F = [1, 1, 2, 3, 5, 8, 13, 21, 34]

print("=" * 72)
print("F_m 階梯嘅 K_Tree 拓撲推導")
print("=" * 72)

# ============ 1. 組合枚舉: 用 {1,2} 步砌 (m-1) 級 = F_m? ============
print("\n1. 組合枚舉驗證: 用 {1,2} 步砌 (m-1) 級嘅方法數 = F_m")
print("-" * 60)

def count_paths(n):
    """用 1 或 2 步砌 n 級樓梯嘅方法數 (Fibonacci)"""
    if n <= 1:
        return 1
    a, b = 1, 1
    for _ in range(2, n+1):
        a, b = b, a+b
    return b

def enumerate_paths(n):
    """列出所有 {1,2} 步組合砌 n 級"""
    paths = []
    for k in range(n//2 + 1):  # k 個 2 步
        ones = n - 2*k        # 剩餘 1 步
        total_steps = k + ones
        # 揀 k 個位置放 2 步
        for pos in itertools.combinations(range(total_steps), k):
            p = []
            idx = 0
            for s in range(total_steps):
                if idx < len(pos) and pos[idx] == s:
                    p.append(2)
                    idx += 1
                else:
                    p.append(1)
            paths.append(p)
    return paths

fib_check = True
for m in range(1, 9):
    n = m - 1  # 砌 (m-1) 級
    c = count_paths(n)
    expected = F[m-1]
    ok = (c == expected)
    fib_check &= ok
    print(f"  m={m}: 砌 {n} 級 = {c} 種 | F_{m} = {expected} {'✅' if ok else '❌'}")

print(f"\n  Fibonacci 樓梯驗證: {'8/8 ✅ 全部通過' if fib_check else '❌ 有錯'}")

# ============ 2. 權重均一性驗證 ============
print("\n2. 權重均一性: 所有到達第 (m-1) 層嘅路徑, 權重 = φ^(-(m-1))")
print("-" * 60)
weight_check = True
for m in range(2, 8):
    n = m - 1
    paths = enumerate_paths(n)
    weights = set()
    for p in paths:
        w = 1.0
        for step in p:
            w *= phi_inv**step  # 1步: φ⁻¹, 2步: φ⁻²
        weights.add(round(w, 12))
    expected = phi_inv**n
    uniform = (len(weights) == 1 and abs(list(weights)[0] - expected) < 1e-10)
    weight_check &= uniform
    print(f"  m={m}: {len(paths)} 條路徑, 權重集合 = {weights} | 期望 φ^(-{n}) = {expected:.6f} {'✅' if uniform else '❌'}")

print(f"\n  權重均一性: {'✅ 全部通過 (φ^(-a)·φ^(-b) = φ^(-(a+b)) 保證)' if weight_check else '❌'}")

# ============ 3. P_m 公式驗證 ============
print("\n3. 完整公式: P_m = 3ε × F_m × φ^(-2(m-1))")
print("-" * 60)
print(f"{'m':>2} | {'F_m':>3} | {'φ^(-2(m-1))':>12} | {'P_m 理論':>9} | {'P_m 觀測':>10} | {'偏差':>8}")
print("-" * 60)

# 觀測值 (Planck binned + CAMB unlensed)
obs = {
    1: 0.4412,   # Planck binned P₁
    2: 0.1778,   # Planck binned P₂
    3: 0.1359,   # CAMB unlensed P₃
    4: None,     # 未驗證 (預測)
}
for m in range(1, 5):
    P_th = 3*eps * F[m-1] * phi_inv**(2*(m-1))
    if obs[m]:
        dev = (obs[m]-P_th)/P_th*100
        print(f"{m:>2} | {F[m-1]:>3} | {phi_inv**(2*(m-1)):>12.5f} | {P_th:>9.5f} | {obs[m]:>10.4f} | {dev:>+7.2f}%")
    else:
        print(f"{m:>2} | {F[m-1]:>3} | {phi_inv**(2*(m-1)):>12.5f} | {P_th:>9.5f} | {'(預測)':>10} |")

print()
print("P₄ 預測 = 3ε·F₄·φ⁻⁶ = 3ε·3·φ⁻⁶ =", round(3*eps*3*phi_inv**6, 5))
print("用戶預期 P₄ ≈ 0.0775", "✅" if abs(3*eps*3*phi_inv**6 - 0.0775) < 0.001 else "❌")

# ============ 4. Fibonacci 遞歸嘅樹詮釋 ============
print("\n4. Fibonacci 遞歸嘅 K_Tree 詮釋")
print("-" * 60)
print("路徑數(到第 m 代) = 路徑數(到第 m-1 代, 最後1步) + 路徑數(到第 m-2 代, 最後2步)")
print("  F_{m+2} = F_{m+1} + F_m  ← 樹上嘅加法規則")
print()
print("最後一步 1 步 (Δℓ=1, 父子耦合 φ⁻¹) → 來自第 m-1 層")
print("最後一步 2 步 (Δℓ=2, 祖孫耦合 φ⁻²) → 來自第 m-2 層")
print("兩種最後一步嘅路徑數相加 = Fibonacci 重數")
print()
print("=> F_m 係 K_Tree 嘅 BRANCH MULTIPLICITY:")
print("   第 (m-1) 代嘅有效 scale 路徑數, 由 {1,2}-步跳躍枚舉")

# ============ 5. 34 = F₉ = M+1 連接 ============
print("\n5. 峰終止同 Fibonacci 連接")
print("-" * 60)
print(f"  M = 33 = F₉ - 1  (F₉ = 34)")
print(f"  峰 m 終止: m ≈ 8-9 (M=33 結構)")
print(f"  34 = F₉: 33 層樹 + 根 = 34 個 scale 層 = Fibonacci 第 9 項")
print(f"  => 峰數上限同 Fibonacci 9 直接連接 (觀察非推導)")

print("\n" + "=" * 72)
print("結論: F_m 階梯嘅 K_Tree 拓撲來源已推導")
print("P_m = 3ε × F_m × φ^(-2(m-1))")
print("  F_m = 到達第 (m-1) 層嘅 Fibonacci 路徑重數 (branch multiplicity)")
print("  φ^(-2(m-1)) = 單路徑強度 (振幅 φ^(-(m-1)) 平方, Born rule)")
print("  3ε = 全局耦合 (A₂ 閉合基準)")
print("=" * 72)

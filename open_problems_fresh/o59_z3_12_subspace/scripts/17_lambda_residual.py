#!/usr/bin/env python3
"""
O59 攻堅 17: λ_max 殘差修正驗證
================================
主張 (用戶):
  λ_max^(0) = Nd+2B = 52 = B×F₇
  Δλ = 52 − 51.5606 = -0.4394
  Δλ ≈ -B/L₅ = -4/11 = -0.3636 (一階)
  加二階幾何曲率項 → 殘差 < 0.01%

測試:
  1. -4/11 一階誤差 (vs 實際 Δλ)
  2. 系統搜尋 Δλ 嘅代數形式
  3. 搜尋「-4/11 + 二階項」組合 → <0.01%?
  4. λ_max 本身有冇更精確閉合?
"""
import os, math, itertools
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O59 攻堅 17: λ_max 殘差修正驗證")
print("=" * 72)

passed, failed = 0, 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. λ_max 精確值 ============
d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
v12 = phi ** (-np.arange(12)/12)
Y12 = np.einsum("ijk,k->ij", d12, v12)
Y12 = (Y12+Y12.T)/2
ev12 = np.linalg.eigvalsh(Y12)
lam_max = np.max(ev12)
print("\n[1] λ_max 精確值")
print(f"  λ_max = {lam_max:.10f}")
Delta = 52 - lam_max
print(f"  Δλ = 52 − λ_max = {Delta:.10f}")
print(f"  Δλ/λ_max = {Delta/lam_max*100:.4f}%")

# ============ 2. -4/11 一階測試 ============
print("\n[2] 主張: Δλ ≈ -B/L₅ = -4/11")
pred1 = -4/11
print(f"  -4/11 = {pred1:.6f}")
err1 = abs(pred1 - (-Delta))/Delta*100
print(f"  vs 實際 -Δλ = {-Delta:.6f}")
print(f"  誤差: {err1:.2f}%")
check("Δλ ≈ 4/11 (<5%)", err1 < 5, f"({err1:.1f}%)")

# ============ 3. Δλ 系統搜尋 ============
print("\n[3] Δλ = 0.43938856 代數形式搜尋")
target = Delta  # 0.43938856...
print(f"  目標: {target:.8f}")

# 簡單分數 a/b (b <= 100)
best_frac = []
for b in range(1, 101):
    a = round(target * b)
    if a <= 0:
        continue
    val = a / b
    err = abs(val - target)/target*100
    best_frac.append((err, f"{a}/{b}", val))
best_frac.sort()
print("  最佳分數:")
for err, name, val in best_frac[:8]:
    print(f"    {name:10s} = {val:.6f}  誤差 {err:.3f}%")

# φ 組合
print("\n  φ 組合:")
phi_cands = {
    "φ⁻²": phi**-2, "φ⁻³": phi**-3, "φ⁻⁴": phi**-4, "φ⁻⁵": phi**-5,
    "φ⁻²+φ⁻⁵": phi**-2+phi**-5, "φ⁻³+φ⁻⁵": phi**-3+phi**-5,
    "φ⁻¹−φ⁻³": phi**-1-phi**-3, "2φ⁻³": 2*phi**-3,
    "1−φ⁻²": 1-phi**-2, "1/φ+1/φ⁴": 1/phi+1/phi**4,
    "φ⁻²−φ⁻⁶": phi**-2-phi**-6, "φ⁻¹−φ⁻⁴": phi**-1-phi**-4,
}
for name, val in phi_cands.items():
    err = abs(val-target)/target*100
    mark = "★" if err < 2 else ""
    print(f"    {name:12s} = {val:.6f}  誤差 {err:6.2f}% {mark}")

# γ_n 組合
print("\n  K_Chain γ_n:")
g = {n: 4*math.sin(math.pi*n/88)**2 for n in range(1, 45)}
gamma_cands = {
    "γ₇": g[7], "γ₆": g[6], "γ₇/2": g[7]/2, "γ₆×2.4": g[6]*2.4,
    "γ₇×2": g[7]*2, "γ₆+γ₇": g[6]+g[7], "γ₈": g[8],
    "γ₇−γ₆": g[7]-g[6], "γ₇+γ₆": g[7]+g[6],
    "2γ₇−γ₆": 2*g[7]-g[6], "γ₇+γ₈": g[7]+g[8],
}
for name, val in gamma_cands.items():
    err = abs(val-target)/target*100
    mark = "★" if err < 2 else ""
    print(f"    {name:12s} = {val:.6f}  誤差 {err:6.2f}% {mark}")

# L_n / F_n 組合
print("\n  Lucas/Fibonacci 組合:")
L = {n: round((phi**n + (-1)**n * phi**(-n)) / 1) for n in range(1, 12)}
# 手動 Lucas: 1,3,4,7,11,18,29,47,76,123,199
L = {1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47, 9:76, 10:123, 11:199}
F = {n: round(phi**n/math.sqrt(5)) for n in range(1, 13)}
# 修正 F: 1,1,2,3,5,8,13,21,34,55,89,144
F = {1:1, 2:1, 3:2, 4:3, 5:5, 6:8, 7:13, 8:21, 9:34, 10:55, 11:89, 12:144}
LF_cands = {
    "L₄/16": L[4]/16, "L₅/25": L[5]/25, "L₆/41": L[6]/41,
    "F₆/18.2": F[6]/18.2, "L₄/F₉": L[4]/F[9], "F₇/29.6": F[7]/29.6,
    "L₄/B²": L[4]/16, "F₈/L₈": F[8]/L[8], "L₅−L₆/41": L[5]-L[6]/41,
    "F₈/47.8": F[8]/47.8, "L₇/F₁₀": L[7]/F[10], "F₇/2⁴": F[7]/16,
}
for name, val in LF_cands.items():
    err = abs(val-target)/target*100
    mark = "★" if err < 2 else ""
    print(f"    {name:12s} = {val:.6f}  誤差 {err:6.2f}% {mark}")

# ============ 4. 「-4/11 + 二階項」組合 ============
print("\n[4] 主張: -4/11 + 二階項 → <0.01%")
second_needed = Delta - 4/11
print(f"  需要二階項: Δλ − 4/11 = {second_needed:.8f}")
print(f"  = 0.07575187... ≈ ?")
# 候選二階項
second_cands = {
    "1/13": 1/13, "1/13.2": 1/13.2, "F₆/106": F[6]/106,
    "φ⁻⁵": phi**-5, "2φ⁻⁶": 2*phi**-6, "φ⁻⁷×3": 3*phi**-7,
    "L₄/92.4": L[4]/92.4, "γ₆/2.386": g[6]/2.386,
    "B/F₅₃": 4/53, "1/φ⁶−1/φ⁸": phi**-6-phi**-8,
    "1/(2L₅×2)": 1/44, "B/(N_dL₄)": 4/(44*7),
    "F₇/(2N_d)": F[7]/88, "L₆/F₁₀": L[6]/F[10],
    "φ⁻⁵−φ⁻⁸": phi**-5 - phi**-8, "2/(F₉−F₈)": 2/(F[9]-F[8]),
}
for name, val in second_cands.items():
    err = abs(val-second_needed)/second_needed*100
    mark = "★" if err < 5 else ""
    print(f"    {name:12s} = {val:.6f}  誤差 {err:6.2f}% {mark}")

# 總和測試: 4/11 + 最佳候選
total_cands = []
for name2, val2 in second_cands.items():
    tot = 4/11 + val2
    err = abs(tot - Delta)/Delta*100
    total_cands.append((err, name2, tot))
total_cands.sort()
print("\n  4/11 + 二階項 總和:")
for err, name2, tot in total_cands[:5]:
    mark = "★" if err < 0.01 else ""
    print(f"    4/11 + {name2:12s} = {tot:.8f}  誤差 {err:5.3f}% {mark}")

# ============ 5. 直接單項最優 ============
print("\n[5] 直接單項最優 (唔使一階+二階)")
all_cands = [(e, n, v) for e, n, v in best_frac[:10]]
for e, n, v in all_cands[:5]:
    print(f"    {n:10s} = {v:.6f}  誤差 {e:.3f}%")

print(f"\n{'='*72}")
print(f"攻堅 17: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")

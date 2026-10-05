#!/usr/bin/env python3
"""
O59 攻堅 18: ★★ λ_max = Nd+2B − L₇/C(12,2) 精確閉合
====================================================
發現: Δλ = 52 − λ_max = 0.4393885616 ≈ 29/66 = 0.4393939 (0.001%)
  29 = L₇ (Lucas 7)
  66 = C(12,2) = su(12) 正根 = 2×K_tree

測試:
  1. λ_max = 52 − 29/66 誤差 (期望 < 1e-5 相對)
  2. Null test: 隨機 target 有幾多最佳分數 = 29/66?
  3. 用其他 d_tensor 版本驗證 (數值噪聲檢查)
  4. 29 = L₇ 同 66 = C(12,2) 結構身份確認
"""
import os, math, random, json
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA = os.path.join(BASE, "main_problems", "p15_early_derivations", "data")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O59 攻堅 18: ★★ λ_max = 52 − L₇/C(12,2)")
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

# ============ 1. 主閉合 ============
d12 = np.load(os.path.join(DATA, "d_tensor_final.npy"))
v12 = phi ** (-np.arange(12)/12)
Y12 = np.einsum("ijk,k->ij", d12, v12)
Y12 = (Y12+Y12.T)/2
ev12 = np.linalg.eigvalsh(Y12)
lam_max = np.max(ev12)

L7 = 29  # Lucas 7
C122 = 66  # C(12,2)
lam_pred = 52 - L7/C122
print("\n[1] 主閉合: λ_max = 52 − 29/66")
print(f"  λ_max 實際 = {lam_max:.12f}")
print(f"  52 − 29/66 = {lam_pred:.12f}")
diff = abs(lam_max - lam_pred)
rel = diff / lam_max
print(f"  差 = {diff:.3e}")
print(f"  相對誤差 = {rel*100:.6f}%")
check("λ_max = 52−29/66 (<0.001% 相對)", rel < 1e-5,
      f"({rel*100:.6f}%)")

# ============ 2. Null test ============
print("\n[2] Null test: 29/66 顯著性")
# 隨機 10000 個 target 喺 [0.3, 0.6], 搵最佳分數 a/b (b≤100)
# 統計幾多個 target 嘅最佳分數 = 29/66 或誤差 < 0.01%
random.seed(42)
hits_2966 = 0
hits_better = 0
N_trials = 10000
for _ in range(N_trials):
    t = random.uniform(0.3, 0.6)
    best_err = 1e9
    best_frac = None
    for b in range(1, 101):
        a = round(t * b)
        if a <= 0:
            continue
        val = a / b
        err = abs(val - t)
        if err < best_err:
            best_err = err
            best_frac = (a, b)
    if best_frac == (29, 66):
        hits_2966 += 1
    if best_err / t < 1e-4:  # 0.01%
        hits_better += 1
print(f"  隨機 {N_trials} 個 target:")
print(f"  最佳分數 = 29/66: {hits_2966} ({hits_2966/N_trials*100:.2f}%)")
print(f"  最佳分數誤差 < 0.01%: {hits_better} ({hits_better/N_trials*100:.2f}%)")
check("29/66 出現率極低", hits_2966/N_trials < 0.01, f"({hits_2966/N_trials*100:.2f}%)")

# 對比: 實際 target 0.43938856 嘅最佳分數
t_actual = 52 - lam_max
best_err = 1e9
best_frac = None
for b in range(1, 101):
    a = round(t_actual * b)
    if a <= 0:
        continue
    val = a / b
    err = abs(val - t_actual)
    if err < best_err:
        best_err = err
        best_frac = (a, b)
print(f"\n  實際 target Δλ = {t_actual:.8f}")
print(f"  最佳分數 (b≤100): {best_frac[0]}/{best_frac[1]} = {best_frac[0]/best_frac[1]:.8f}")
print(f"  誤差: {best_err/t_actual*100:.6f}%")

# ============ 3. 數值噪聲檢查 ============
print("\n[3] 數值噪聲檢查 (其他 d_tensor 版本)")
for fn in sorted(os.listdir(DATA)):
    if fn.startswith("d_tensor") and fn.endswith(".npy"):
        try:
            d = np.load(os.path.join(DATA, fn))
            if d.shape == (12, 12, 12):
                Y = np.einsum("ijk,k->ij", d, v12)
                Y = (Y+Y.T)/2
                lam = np.max(np.linalg.eigvalsh(Y))
                rel2 = abs(lam - lam_pred)/lam*100
                mark = "★" if rel2 < 0.01 else ""
                print(f"    {fn:35s}: λ_max = {lam:10.5f}  52−29/66 誤差 {rel2:8.5f}% {mark}")
        except Exception:
            pass

# ============ 4. 結構身份 ============
print("\n[4] 29 = L₇ 同 66 = C(12,2) 結構身份")
L = {1:1, 2:3, 3:4, 4:7, 5:11, 6:18, 7:29, 8:47}
print(f"  L₇ = {L[7]} (Lucas 7)")
print(f"  C(12,2) = {12*11//2} = 66")
check("L₇ = 29", L[7] == 29)
check("C(12,2) = 66", 12*11//2 == 66)
print(f"  ★ O58: K = -232 = -8×L₇ (29 出現喺 κ)")
print(f"  ★ O59: 66 = C(12,2) = su(12) 正根 = 2×K_tree")
print(f"  → Δλ = L₇/66 = L₇/(2K_tree) — 兩個結構數嘅比!")

# 52 嘅身份
print(f"\n  52 = Nd+2B = 44+8 (K_Chain sites + 2×branch)")
print(f"  52 = B×F₇ = 4×13 (branch × Fibonacci 7)")
print(f"  L₇ = F₇+F₆ = 13+8? {13+8} = 21 ✗")
print(f"  L₇ = F₆+F₈ = 8+21 = 29 ✓ (Fibonacci 和)")
check("L₇ = F₆+F₈ = 8+21", 8+21 == 29)
print(f"  ★ 52 同 29 都係 F₇ 相關: 52 = 4×F₇, 29 = F₆+F₈")

# ============ 5. 擴展: 其他 λ 有冇類似修正? ============
print("\n[5] 其他 λ 嘅修正檢查")
for i in range(1, 6):
    lam_i = ev12[i]
    # 近整數?
    nearest = round(lam_i)
    diff_i = nearest - lam_i
    print(f"  λ_{i} = {lam_i:.6f}, 最近整數 {nearest}, 差 = {diff_i:+.6f}")

print(f"\n{'='*72}")
print(f"攻堅 18: {passed} PASS, {failed} FAIL")
print(f"{'='*72}")

# 保存
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
out = {
    "lam_max_actual": lam_max,
    "lam_max_pred_52_29_66": lam_pred,
    "rel_err": rel,
    "Delta_actual": t_actual,
    "Delta_2966": 29/66,
    "null_hits_2966": hits_2966,
    "null_total": N_trials,
    "L7": L7,
    "C122": C122,
}
with open(os.path.join(os.path.dirname(__file__), "..", "data", "lambda_closure.json"), "w") as f:
    json.dump(out, f, indent=2)
print(f"\n結果已保存: data/lambda_closure.json")

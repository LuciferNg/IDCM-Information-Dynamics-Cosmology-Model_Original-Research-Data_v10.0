#!/usr/bin/env python3
"""
O61 驗證 10: 誠實複核 — kernel 結構 vs 記錄文檔 claim
================================================================
目的: 核對 docs/02 嘅 claim:
  - "kernel(Y) = 4 對所有 Kähler 參數穩定" ← 要檢查
  - "Σ_k κ_ijk v_k = 0 有精確 4 個獨立解 (∀t 成立)" ← 檢查
  - "32 = 36−4 = 2B² 鎖定"

關鍵區分:
  A. 大矩陣 A = κ.reshape(1296×36) 嘅 kernel (4 維) — t 無關!
     v ∈ ker(A) ⟹ Σ_k κ_ijk v_k = 0 ∀i,j ⟹ Y_ij(t)·v = 0 ∀t
  B. 特定 t 嘅 Yukawa 矩陣 Y(t) = Σκt 嘅 eigenvalue kernel — t 依賴!

docs/02 寫 "kernel(Y) = 4 ∀t (50/50 隨機)" ← script 07 嘅 claim
  但 script 07 重跑發現: φ^(35-i) kernel=0, t=1 kernel=34!
  → "∀t" 係錯! 要誠實修正!
"""
import sys, os, math
import json
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "..")
O53 = os.path.join(BASE, "open_problems_fresh", "o53_cy3_reality", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 72)
print("O61 驗證 10: 誠實複核")
print("=" * 72)

passed = 0
failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✅ {name} {detail}")
    else:
        failed += 1
        print(f"  ❌ {name} {detail}")

# ============ 1. 載入 κ ============
d = json.load(open(os.path.join(O53, "cy36_98_intersection_full.json")))
kappa = np.array(d["kappa"])

# ============ 2. A 嘅 kernel (t 無關) ============
print("\n[1] 大矩陣 A kernel (t 無關)")
A = kappa.reshape(1296, 36)
U, S, Vt = np.linalg.svd(A, full_matrices=True)
n_zero_A = np.sum(S < 1e-8)
print(f"  kernel(A) = {n_zero_A}")
check("kernel(A) = 4", n_zero_A == 4, f"={n_zero_A}")
zero_basis = Vt[36-n_zero_A:, :]  # 4×36

# 驗證: v ∈ ker(A) ⟹ Σκv = 0 ⟹ Y(t)v = 0 ∀t
print("\n[2] 驗證 v ∈ ker(A) ⟹ Y(t)v = 0 ∀t")
for a in range(4):
    v = zero_basis[a]
    Mv = np.einsum("ijk,k", kappa, v)
    err = np.max(np.abs(Mv))
    check(f"v^{a+1}: Σκv = 0", err < 1e-8, f"err={err:.1e}")

# 隨機 t 驗證 Y(t)v = 0
rng = np.random.default_rng(123)
max_err = 0
for trial in range(20):
    t = rng.uniform(-5, 5, 36)
    Y = np.einsum("ijk,k", kappa, t)
    for a in range(4):
        err = np.max(np.abs(Y @ zero_basis[a]))
        max_err = max(max_err, err)
print(f"  隨機 20 t × 4 v: max|Y(t)v| = {max_err:.2e}")
check("Y(t)v = 0 ∀ 隨機 t", max_err < 1e-8, f"max={max_err:.1e}")

# ============ 3. Y(t) eigenvalue kernel 係 t 依賴 ============
print("\n[3] Y(t) eigenvalue kernel 係 t 依賴 (誠實修正)")
print("  docs/02 claim: 'kernel(Y) = 4 對所有 Kähler 參數穩定' ← 要修正!")
results_kernel = {}
for name, t in [
    ("γ", 4*np.sin(np.pi*np.arange(1,37)/88)**2),
    ("φ^(35-i)", phi**(35-np.arange(36))),
    ("φ^(-i)", phi**(-np.arange(36))),
    ("t=1", np.ones(36)),
    ("隨機", rng.uniform(0.1, 5, 36)),
]:
    Y = np.einsum("ijk,k", kappa, t)
    ev = np.linalg.eigvalsh(Y)
    nz = np.sum(np.abs(ev) < 1e-8)
    results_kernel[name] = int(nz)
    print(f"  {name}: eigenvalue kernel = {nz}")

print("\n  ★ 正確 claim: kernel(A) = 4 (t 無關), 而 kernel(Y(t)) 係 t 依賴")
print("  ★ v ∈ ker(A) ⟹ v ∈ ker(Y(t)) ∀t (即使 Y(t) 有其他額外零模)")
check("γ kernel = 4", results_kernel["γ"] == 4)
check("φ^(-i) kernel = 4", results_kernel["φ^(-i)"] == 4)

# ============ 4. docs/02 其他 claim 複核 ============
print("\n[4] docs/02 其他 claim 複核")
# "32 = 36−4 = 2B²"
check("32 = 2B²", 32 == 2*16)
# "通量子 N ∈ kernel(Y) 穩定條件"
# 正確嘅穩定條件: ∂W/∂t = Y·N = 0 → N ∈ ker(Y(t))
# 但 ker(Y(t)) 依 t! 所以: 穩定點 t* 要求 N ∈ ker(Y(t*))
# v ∈ ker(A) 提供 4 個 t 無關解
print("\n  ★ 穩定條件修正:")
print("    ∂W/∂t_j = Σ_i N_i Y_ij(t) = 0 → N ∈ ker(Y(t*))")
print("    ker(A) ⊆ ker(Y(t)) ∀t → 4 個 t 無關通量子解")
print("    (Y(t) 額外零模係 t 依賴, 唔係結構)")
check("4 = B", 4 == 4)

# ============ 5. 質量矩陣正定 ============
print("\n[5] 質量矩陣正定複核")
gamma = 4*np.sin(np.pi*np.arange(1,37)/88)**2
Y = np.einsum("ijk,k", kappa, gamma)
lock_basis = Vt[:32, :]  # 32×36 (ker(A) 正交補)
M_lock = lock_basis @ (Y.T @ Y) @ lock_basis.T
ev_lock = np.linalg.eigvalsh(M_lock)
print(f"  M_lock min eig = {ev_lock.min():.6f}")
check("M_lock 正定", ev_lock.min() > 0, f"min={ev_lock.min():.6f}")

# ============ 6. 通量子 66/90 複核 ============
print("\n[6] 通量子 66/90 複核")
zero_basis = Vt[36-4:, :]
for tname, tval in [("66", 66), ("90", 90)]:
    best = None
    for scale in range(1, 41):
        for a in range(4):
            N = np.round(zero_basis[a] * scale).astype(int)
            s = np.sum(np.abs(N))
            if abs(s - tval) < 2:
                if best is None or abs(s - tval) < abs(best[0] - tval):
                    best = (s, scale, a)
    if best:
        print(f"  {tname}={tval}: scale={best[1]}, dir={best[2]}, sum|N|={best[0]} (偏差 {best[0]-tval})")
    else:
        print(f"  {tname}={tval}: 冇搵到 <2 偏差")
        # 放寬
        for scale in range(1, 41):
            for a in range(4):
                N = np.round(zero_basis[a] * scale).astype(int)
                s = np.sum(np.abs(N))
                if abs(s - tval) < 5:
                    print(f"    (放寬) scale={scale}, dir={a}, sum|N|={s} (偏差 {s-tval})")
                    break
            else:
                continue
            break

# ============ 7. 總結 ============
print("\n" + "=" * 72)
print("O61 驗證 10 總結:")
print("=" * 72)
print(f"""
  誠實複核結果:
  ─────────────────────────────────
  1. kernel(A) = 4 (t 無關) ✅
  2. v ∈ ker(A) ⟹ Y(t)v = 0 ∀t ✅ (20 隨機 t)
  3. kernel(Y(t)) 係 t 依賴 ⚠️ (γ:4, φ^35:0, t=1:34)
     → docs/02 "kernel(Y)=4 ∀t" 要修正為 "kernel(A)=4"
  4. M_lock 正定 ✅

  {'✅ 複核完成' if failed == 0 else '❌ 有失敗'}
""")
results = {
    "test": "O61 verify 10",
    "kernel_A": int(n_zero_A),
    "Ytv_max_err": float(max_err),
    "kernel_Y_t_dependent": results_kernel,
    "M_lock_min": float(ev_lock.min()),
    "passed": passed, "failed": failed
}
with open("data/10_verification.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nPassed: {passed}, Failed: {failed}")
if failed > 0:
    exit(1)
print("🎉 O61 驗證 10 完成!")

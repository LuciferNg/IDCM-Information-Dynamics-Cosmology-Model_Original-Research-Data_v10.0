#!/usr/bin/env python3
"""
O53 開放 1 閉合: λ₁ 規範 + tr(Y²) = 5 嘅精確檢驗
===================================================
發現:
  - J0 scale 由 λ₁ = φ^(1/3) 閉合決定 (誤差 0.004%)
  - 檔案 Vol = 2^(-12) 係 polytope 尺度, 唔係 κ 幾何規範
  - tr(Y²) = 4.947 (誤差 1.05%) — 需要解釋

分析:
  1. λ₁ 規範下, tr(Y²) = 5 有冇精確來源?
  2. tr(Y²)/λ₁² = 3.59 ≈ ?
  3. Σλ_i² (全部 32 個非零) = ?
  4. 有冇「主本徵值 + 次結構」分解?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53 開放 1: λ₁ 規範 + tr(Y²) 分解")
print("=" * 70)

with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)

K = np.zeros(tuple(kappa['shape']))
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val
    K[i, k, j] = val
    K[j, i, k] = val
    K[j, k, i] = val
    K[k, i, j] = val
    K[k, j, i] = val

J0 = np.array(jstar['Jstar_36D'])

def yspec(J):
    Y = np.einsum('ijk,k->ij', K, J)
    Y = (Y + Y.T) / 2
    return np.linalg.eigvalsh(Y)

# --- [1] λ₁ 規範 ---
print("\n[1] λ₁ = φ^(1/3) 規範:")
s = phi**(-1/3) / (1/max(yspec(J0)))
J_norm = s * J0
ev = yspec(J_norm)
l1 = max(ev)
print(f"    s = {s:.6f} (J* scale 修正)")
print(f"    λ₁ = {l1:.8f}, 1/λ₁ = {1/l1:.8f}")
print(f"    φ^(-1/3) = {phi**(-1/3):.8f}")
print(f"    誤差: {abs(1/l1 - phi**(-1/3))/phi**(-1/3)*100:.5f}%")

# --- [2] tr(Y²) 分解 ---
print("\n[2] tr(Y²) 分解 (λ₁ 規範):")
tr2 = np.sum(ev**2)
print(f"    tr(Y²) = Σλ² = {tr2:.8f}")
print(f"    λ₁² = {l1**2:.8f}")
print(f"    tr(Y²) − λ₁² = {tr2 - l1**2:.8f}")
print(f"    λ₁²/tr(Y²) = {l1**2/tr2:.4f}")
print(f"    5 = F₅: 誤差 {abs(tr2-5)/5*100:.3f}%")

# 次結構: 第二組本徵值
ev_sorted = np.sort(ev)[::-1]
print(f"\n    前 12 個 |λ| (λ₁ 規範):")
for i in range(12):
    print(f"      λ_{i+1:2d} = {ev_sorted[i]:10.6f}  (1/|λ| = {1/abs(ev_sorted[i]):8.4f}, φ^({math.log(1/abs(ev_sorted[i]))/math.log(phi):+6.3f}))")

# --- [3] tr(Y²) = 5 嘅候選結構 ---
print("\n[3] tr(Y²) = 5 結構:")
print(f"    5 = F₅ (Fibonacci)")
print(f"    5 = 1 + 4 = φ⁰ + B")
print(f"    5 = φ² + φ⁻² = 2.618+0.382 = 3.0? 唔啱")
print(f"    5 = 2φ+1? {2*phi+1:.4f}")
print(f"    5 = φ³−φ⁻³+1 = {phi**3-phi**-3+1:.4f} = B+1")
print(f"    5 = L₅ = 11? 唔啱")

# tr(Y²) 嘅 λ₁ 分解: λ₁² + Σ_{i>1} λ_i²
rest = tr2 - l1**2
print(f"\n    Σ_{i>1} λ_i² = {rest:.6f}")
print(f"    rest/λ₁² = {rest/l1**2:.4f}")
print(f"    4/φ^(2/3) = {4/phi**(2/3):.4f}")
print(f"    5−φ^(2/3) = {5-phi**(2/3):.4f}")
print(f"    → tr(Y²) = 5 ⟺ λ₁² + rest = 5")
print(f"    → φ^(2/3) + rest = 5 → rest = {5-phi**(2/3):.4f}")

# --- [4] 有冇「λ₁ 單極」近似? ---
print("\n[4] 單極近似:")
print(f"    tr(Y²)/λ₁² = {tr2/l1**2:.4f}")
print(f"    → 譜有 {tr2/l1**2:.2f} 個「有效 λ₁ 等價」")
print(f"    5/φ^(2/3) = {5/phi**(2/3):.4f} ← 如果 tr(Y²)=5 且 λ₁²=φ^(2/3)")
print(f"    → 5 = φ^(2/3) × 3.63")
print(f"    3.63 ≈ φ+2 = {phi+2:.4f}? 3.63 ≈ 3.5?")

# --- [5] 直接數值: tr(Y²) 喺 λ₁ 規範 ---
print("\n[5] 最終狀態:")
print(f"    λ₁ = φ^(1/3): 誤差 {abs(1/l1-phi**(-1/3))/phi**(-1/3)*100:.4f}%")
print(f"    tr(Y²) = {tr2:.4f} vs 5: 誤差 {abs(tr2-5)/5*100:.2f}%")
check("λ₁ = φ^(1/3) 精確", abs(1/l1-phi**(-1/3))/phi**(-1/3)*100 < 0.01, 
      f"({abs(1/l1-phi**(-1/3))/phi**(-1/3)*100:.4f}%)")
check("tr(Y²) ≈ 5 (誤差 <5%)", abs(tr2-5)/5 < 0.05, f"({abs(tr2-5)/5*100:.2f}%)")

# tr(Y²) 嘅「5」係咪 J 嘅 5 次齊次? 唔係 — 二次
# 試: tr(Y²) = 5 需要 J 縮 s = sqrt(5/4.947) = 1.0053
# 但 λ₁ 需要 s = 1.0008 → 0.45% 差 = 「兩閉合張力」
print("\n[6] 兩閉合張力 (0.45%):")
s_tr = math.sqrt(5/np.sum(yspec(J0)**2))
s_l1 = phi**(-1/3)*max(yspec(J0))
print(f"    s(tr) = {s_tr:.6f}, s(λ₁) = {s_l1:.6f}")
print(f"    張力 = {abs(s_tr-s_l1)/s_l1*100:.3f}%")
print(f"    → 0.45% 張力 = 需要 instanton/非微擾修正?")
print(f"    → 或 tr(Y²) ≈ 5 只係近似巧合 (1% 級)")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)

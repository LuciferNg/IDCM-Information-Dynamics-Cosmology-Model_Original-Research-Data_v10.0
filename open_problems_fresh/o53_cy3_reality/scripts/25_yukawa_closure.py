#!/usr/bin/env python3
"""
O53 Q4: 真實 Y 譜結構閉合
============================
發現: 真實 Y (κ_ijk J*^k) 有 32 非零 + 4 零本徵值
      λ₁ = 1.174 (主本徵值)
      tr(Y²) = 4.947

分析:
  1. 32 = ? 4 = ? (身份搜索)
  2. 主本徵值 λ₁ = 1.174 ≈ φ^(-1/3)? φ^(-1/4)?
  3. 質量譜 (Y 本徵值 → 質量) 有冇 SM 結構?
  4. tr(Y) = -1.485 vs 66 — 需要新閉合
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
print("O53 Q4: 真實 Y 譜閉合")
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

J = np.array(jstar['Jstar_36D'])
Y = np.einsum('ijk,k->ij', K, J)
Y = (Y + Y.T) / 2
evals = np.linalg.eigvalsh(Y)
n_nz = np.sum(np.abs(evals) > 1e-10)

# --- [1] 32/4 身份 ---
print("\n[1] 32 同 4 嘅身份:")
print(f"    32 = GLSM rows (32×37)")
print(f"    32 = 36−4 (h11 − dim)")
print(f"    32 = 2⁵")
print(f"    32 = 44−12 (Nd − 12)")
print(f"    4 = dim (CY₃ 複維度)")
print(f"    4 = B (K_Chain)")
print(f"    4 = 36−32")
check("32 = h11 − dim", n_nz == 36 - 4, f"({n_nz} = 36−4)")

# --- [2] λ₁ 身份 ---
print("\n[2] 主本徵值 λ₁ = 1.174:")
l1 = max(evals)
print(f"    λ₁ = {l1:.6f}")
print(f"    φ⁻¹ = {phi**-1:.4f}")
print(f"    φ^(−1/3) = {phi**(-1/3):.4f}")
print(f"    φ^(−1/4) = {phi**(-1/4):.4f}")
print(f"    √φ−1 = {math.sqrt(phi)-1:.4f}")
print(f"    1/λ₁ = {1/l1:.4f}")
check("λ₁ ≈ 1", abs(l1 - 1) < 0.3, f"({l1:.4f})")

# --- [3] 質量譜 ---
print("\n[3] 質量譜 (M_Pl × λ):")
masses = np.sort(np.abs(evals))[::-1]
print(f"    最大 12 個 |λ|:")
for i in range(12):
    print(f"      m_{i+1:2d} = {masses[i]:.6f}")

# SM 質量比 (top:bottom:tau:mu:e = 172:4.18:1.777:0.105:0.0005)
print(f"\n    SM 質量比 (誇克+輕子):")
print(f"      t/b/τ/μ/e = 172/4.18/1.777/0.1057/0.000511 GeV")
print(f"      t/b = {172/4.18:.1f}, t/τ = {172/1.777:.1f}, t/μ = {172/0.1057:.1e}")

# --- [4] 有冇 3×11 或 3 代結構? ---
print("\n[4] 3 代結構 (Y 本徵值分組):")
ev_nz = np.sort(evals)[::-1][:n_nz]
print(f"    32 個非零本徵值分 3 組 (每 10-11 個):")
for g in range(3):
    group = ev_nz[g*11:(g+1)*11] if g < 2 else ev_nz[22:]
    print(f"      Gen{g+1}: mean={np.abs(group).mean():.4f}, 範圍 [{np.abs(group).min():.2e}, {np.abs(group).max():.2e}]")

# --- [5] tr(Y²) 身份 ---
print("\n[5] tr(Y²) = 4.947:")
trY2 = np.trace(Y @ Y)
print(f"    tr(Y²) = {trY2:.4f}")
print(f"    φ⁴ = {phi**4:.4f}, φ⁵ = {phi**5:.4f}")
print(f"    5 = F₅, φ⁴ = 6.854")
print(f"    tr(Y²) ≈ 5? {'✅' if abs(trY2-5) < 0.2 else '❌'} ({trY2:.4f})")
print(f"    tr(Y²) ≈ φ⁴−2 = {phi**4-2:.4f}?")

# --- [6] 用 real J* 嘅 κ 縮放 ---
print("\n[6] 縮放關係:")
print(f"    J* 總和 = {J.sum():.6f}")
print(f"    Vol = κ_ijk J*^i J*^j J*^k = {np.einsum('ijk,i,j,k->', K, J, J, J):.6f}")
print(f"    1/Vol = {1/np.einsum('ijk,i,j,k->', K, J, J, J):.6f}" if np.einsum('ijk,i,j,k->', K, J, J, J) != 0 else "    Vol = 0")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)

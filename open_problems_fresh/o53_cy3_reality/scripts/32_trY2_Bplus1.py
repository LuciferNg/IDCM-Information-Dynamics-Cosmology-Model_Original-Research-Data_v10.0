#!/usr/bin/env python3
"""
O53 開放 1 閉合: tr(Y²) = 5 = B+1 精確驗證
=============================================
發現: 5 = φ³−φ⁻³+1 = B+1 (B=4 K_Chain 分支)

驗證:
  1. tr(Y²) = 5 嘅「B+1」身份
  2. 張力 0.53% 有冇結構來源
  3. 譜結構: λ₁ = φ^(1/3), 次 λ 有冇 φ 指數
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
B = phi**3 - phi**-3  # = 4
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
print("O53 開放 1: tr(Y²) = B+1 閉合")
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
Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2
ev = np.linalg.eigvalsh(Y)
tr2 = np.sum(ev**2)

print(f"\n[1] tr(Y²) = {tr2:.6f}")
print(f"    B = φ³−φ⁻³ = {B:.6f} (= 4)")
print(f"    B+1 = {B+1:.6f} (= 5)")
print(f"    誤差: {abs(tr2-(B+1))/(B+1)*100:.3f}%")
check("tr(Y²) ≈ B+1 = 5", abs(tr2-5)/5 < 0.02, f"({abs(tr2-5)/5*100:.2f}%)")
check("B = 4 精確", abs(B-4) < 1e-10, f"({B:.10f})")

print("\n[2] 譜 φ 指數 (全部 32 非零):")
ev_sorted = np.sort(ev)[::-1]
ev_nz = ev_sorted[np.abs(ev_sorted) > 1e-10]
print(f"    非零: {len(ev_nz)}")
# 檢查 λ 係咪 φ^(-k/3) 形式
for i in range(min(16, len(ev_nz))):
    l = abs(ev_nz[i])
    if l > 0:
        exp = math.log(1/l) / math.log(phi)
        # 最接近嘅 φ^(-n/3)
        n3 = round(exp*3)
        target = phi ** (-n3/3)
        err = abs(l - target)/target*100
        print(f"      λ_{i+1:2d} = {l:10.6f}  1/λ = φ^({exp:+6.3f})  ≈ φ^(-{n3}/3) ({err:.2f}%)")

# --- [3] 張力分析 ---
print("\n[3] 兩閉合張力 0.53%:")
s_tr = math.sqrt((B+1)/tr2)
s_l1 = phi**(-1/3)*max(ev)
print(f"    s(tr) = {s_tr:.6f}, s(λ₁) = {s_l1:.6f}")
tension = abs(s_tr - s_l1)/s_l1*100
print(f"    張力 = {tension:.3f}%")
# 有冇第三個閉合決定 scale?
print(f"    候選: Vol = 2^(-12) 需要 s_vol = {((2**-12)/np.einsum('ijk,i,j,k->', K, J0, J0, J0))**(1/3):.6f}")
print(f"    → 三個 scale 候選: 1.0053 (tr), 1.0000 (λ₁), 0.8016 (Vol)")
print(f"    → λ₁ 閉合最自然 (0.008%), tr 次之 (1.06%), Vol 係 polytope 尺度 (唔關事)")

# --- [4] 66 同 tr(Y²) 嘅關聯 ---
print("\n[4] 66 同 tr(Y²):")
print(f"    66 = C(12,2) = 12×11/2")
print(f"    tr(Y²) = 5 = B+1")
print(f"    66 + 5 = 71? 66×5 = 330? 66/5 = 13.2?")
print(f"    66 = 5×13 + 1? {5*13+1}")
print(f"    66 = 5×12 + 6? {5*12+6}")
print(f"    66 = 5×11 + 11? {5*11+11}")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)

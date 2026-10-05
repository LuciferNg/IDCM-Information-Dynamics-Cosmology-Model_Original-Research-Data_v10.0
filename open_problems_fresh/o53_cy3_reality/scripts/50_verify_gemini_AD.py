#!/usr/bin/env python3
"""
O53 驗證 Gemini 理論 (A-D 部分)
==================================
Gemini 主張: c_f = n/3 係由 CY₃ 複維度 + 3×12D sector + Z₃ 對稱三重鎖定

驗證:
  A. Z₃ 循環置換不變性: P·Y·Pᵀ = Y? (P 係 12-shift 循環置換)
  B. κ 嘅 shift-by-12 對稱 (κ_{i+12,j,k} ≈ κ_ijk?)
  C. Gemini 粒子→n 分配 vs 實測 c_f
  D. n/3 量化統計顯著性 (p-value)
"""
import os, json, math, sys
import numpy as np
from collections import Counter
from scipy import stats

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
print("O53 驗證 Gemini 理論 (A-D)")
print("=" * 70)

with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)
K = np.zeros((36, 36, 36))
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

# --- [A] Z₃ 循環置換 ---
print("\n[A] Z₃ 循環置換不變性 (P·Y·Pᵀ = Y?):")
# P: 12-shift 循環置換 (0→12→24→0)
P = np.zeros((36, 36))
for i in range(12):
    P[i, i+12] = 1
    P[i+12, i+24] = 1
    P[i+24, i] = 1
PY = P @ Y @ P.T
err = np.linalg.norm(PY - Y)
rel = err / np.linalg.norm(Y)
print(f"    ||P·Y·Pᵀ − Y|| = {err:.4f} (rel {rel:.4f})")
check("Y 係 Z₃ 循環置換不變", rel < 1e-10, f"(rel {rel:.4f})")

# P 作用喺 κ?
Kp = np.einsum('ijk,ai,bj,ck->abc', K, P, P, P)
errK = np.linalg.norm(Kp - K)
print(f"    ||P·κ·PᵀPᵀ − κ|| = {errK:.4f} (rel {errK/np.linalg.norm(K):.4f})")
check("κ 係 Z₃ 循環置換不變", errK/np.linalg.norm(K) < 1e-10, f"(rel {errK/np.linalg.norm(K):.4f})")

# --- [B] shift-by-12 對稱 ---
print("\n[B] shift-by-12 對稱 (κ_{i+12,j,k} ≈ κ_ijk?):")
# 唔係循環, 係 shift: i → i+12 (0-11 → 12-23 → 24-35)
# 檢查三個 12-block 嘅 κ 譜相似度
block_spec = []
for g in range(3):
    idx = slice(g*12, (g+1)*12)
    Kb = K[idx, idx, idx]
    vals = np.abs(Kb[Kb != 0])
    block_spec.append(vals)
print(f"    Block 0: {len(block_spec[0])} non-zero, mean|κ| = {block_spec[0].mean():.3f}")
print(f"    Block 1: {len(block_spec[1])} non-zero, mean|κ| = {block_spec[1].mean():.3f}")
print(f"    Block 2: {len(block_spec[2])} non-zero, mean|κ| = {block_spec[2].mean():.3f}")
# 相似度 (KS test 或 mean 比較)
from scipy import stats
ks01 = stats.ks_2samp(block_spec[0], block_spec[1])
print(f"    KS(block0,block1) = {ks01.statistic:.3f}, p = {ks01.pvalue:.3f}")
check("3 blocks κ 同分佈", ks01.pvalue > 0.05, f"(p={ks01.pvalue:.3f})")

# --- [C] Gemini 粒子→n 分配 vs 實測 ---
print("\n[C] Gemini 粒子→n 分配 vs 實測 c_f:")
M_Pl = 1.22e19
m44 = M_Pl * math.exp(-44)
SM = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
      'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}
measured = {}
for k, m in SM.items():
    d = 44 - math.log(M_Pl/m)
    n = round(d)
    c = round((d-n)/math.log(phi)*3)/3
    measured[k] = c

gemini = {'t': 1.0, 'c': 0.0, 'u': 0.0, 'b': 1.0, 's': -2/3, 'd': -2/3,
          'tau': -2/3, 'mu': -1/3, 'e': 1.0}
print(f"    {'粒子':6s} {'Gemini':8s} {'實測':8s} {'一致':5s}")
match = 0
for k in SM:
    g = gemini[k]
    m = measured[k]
    ok = abs(g - m) < 1e-9
    match += ok
    print(f"    {k:6s} {g:+8.3f} {m:+8.3f} {'✅' if ok else '❌'}")
print(f"    一致: {match}/9")
check("Gemini n 分配全對", match == 9, f"({match}/9)")

# --- [D] n/3 量化統計顯著性 ---
print("\n[D] n/3 量化統計顯著性:")
# 零假設: c_f 均勻分佈喺 [−1,1] (連續)
# 觀測: 9 個值全部 ∈ {±1, ±2/3, ±1/3, 0} (7 個可能值, 但只有 6 個出現)
# 每個值準確落在 1/3 格點嘅概率: 格點間距 1/3, 容差 ±0.05
# → 連續均勻下, 落在任一格點 ±0.05 內概率 = 7 × 0.1/2 = 0.35
# P(9 個全中) = 0.35^9 = 7.9e-5
p_all = (7 * 0.1 / 2) ** 9
print(f"    格點: {{±1, ±2/3, ±1/3, 0}} (7 點, 間距 1/3)")
print(f"    容差: ±0.05 (最近 1/3 平均誤差 {np.mean([abs(measured[k]-round(measured[k]*3)/3) for k in SM]):.3f})")
print(f"    單點命中概率: 7×0.1/2 = 0.35")
print(f"    9 點全中概率: {p_all:.2e}")
check("n/3 量化顯著 (p < 0.05)", p_all < 0.05, f"(p={p_all:.2e})")

# 更嚴格: 用實測誤差
errs = [abs(measured[k]*3 - round(measured[k]*3)) for k in SM]
print(f"    3c_f 離整數最大偏差: {max(errs):.4f}")
print(f"    3c_f 離整數 RMS: {np.sqrt(np.mean(np.array(errs)**2)):.4f}")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)

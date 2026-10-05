#!/usr/bin/env python3
"""
O53 路徑二 (驗證): k 值 3-cluster 顯著性
============================================
發現: k = -ln(J*)/ln(φ) 3 等分 → G1/G2/G3 = 12/12/12, mean 7.59/9.51/12.52

驗證:
  1. 3-cluster 顯著性 (vs 均勻/隨機)
  2. 12/12/12 分組係咪巧合?
  3. cluster 間距有冇 φ/44 結構?
  4. 同 3×12D sector 排列對應
"""
import os, json, math, sys
import numpy as np
from scipy import stats

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
lnphi = math.log(phi)
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
print("O53 路徑二驗證: k 3-cluster")
print("=" * 70)

with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
k = -np.log(J0)/lnphi

# --- [1] 3 等分 ---
print("\n[1] k 3 等分:")
k_sorted = np.sort(k)
g1 = k_sorted[:12]
g2 = k_sorted[12:24]
g3 = k_sorted[24:36]
print(f"    G1: {np.array2string(g1, precision=2)}, mean = {g1.mean():.2f}")
print(f"    G2: {np.array2string(g2, precision=2)}, mean = {g2.mean():.2f}")
print(f"    G3: {np.array2string(g3, precision=2)}, mean = {g3.mean():.2f}")

# --- [2] 顯著性: 3 組 mean 差距 ---
print("\n[2] 組間分離:")
print(f"    G3−G2 = {g3.mean()-g2.mean():.2f}")
print(f"    G2−G1 = {g2.mean()-g1.mean():.2f}")
print(f"    G3−G1 = {g3.mean()-g1.mean():.2f}")
print(f"    G1 內 std = {g1.std():.2f}")
print(f"    G2 內 std = {g2.std():.2f}")
print(f"    G3 內 std = {g3.std():.2f}")
print(f"    → 組間 gap vs 組內 std:")
print(f"    (G2−G1)/std = {(g2.mean()-g1.mean())/g1.std():.1f}")
print(f"    (G3−G2)/std = {(g3.mean()-g2.mean())/g2.std():.1f}")

# --- [3] 隨機對照 ---
print("\n[3] 隨機對照 (36 個均勻 [6.77, 13.99]):")
rng = np.random.default_rng(42)
gaps = []
for _ in range(1000):
    rk = np.sort(rng.uniform(6.77, 13.99, 36))
    rg1, rg2, rg3 = rk[:12], rk[12:24], rk[24:36]
    gap = (rg3.mean() - rg1.mean()) / (rg1.std() + 1e-9)
    gaps.append(gap)
obs_gap = (g3.mean() - g1.mean()) / (g1.std() + 1e-9)
p_val = np.mean(np.array(gaps) > obs_gap)
print(f"    觀測 gap/σ = {obs_gap:.2f}")
print(f"    隨機 mean gap/σ = {np.mean(gaps):.2f}")
print(f"    隨機 std = {np.std(gaps):.2f}")
print(f"    p(隨機 ≥ 觀測) = {p_val:.4f}")
check("k 3-cluster 顯著 (p<0.05)", p_val < 0.05, f"(p={p_val:.4f})")

# --- [4] cluster 間距結構 ---
print("\n[4] 組 mean 結構:")
m1, m2, m3 = g1.mean(), g2.mean(), g3.mean()
print(f"    mean: {m1:.2f}, {m2:.2f}, {m3:.2f}")
print(f"    間距: {m2-m1:.2f}, {m3-m2:.2f}")
print(f"    比: {(m2-m1)/(m3-m2):.3f}")
print(f"    lnφ×4 = {lnphi*4:.2f}")
print(f"    lnφ×5 = {lnphi*5:.2f}")
print(f"    lnφ×6 = {lnphi*6:.2f}")
print(f"    → 間距 ≈ {((m2-m1)+(m3-m2))/2:.2f} ≈ ?")

# --- [5] 12/12/12 巧合檢驗 ---
print("\n[5] 12/12/12 分組:")
print(f"    36 個 k 值 3 等分 = 12/12/12 (強制)")
print(f"    → 12/12/12 係「定義」唔係發現")
print(f"    → 真正發現係: 3 組 mean 分離 (7.59/9.51/12.52)")
print(f"    → 但 k 連續均勻下 3 等分都自然有 3 組 mean")
print(f"    → 關鍵: gap 有冇大過隨機?")

# --- [6] 結論 ---
print("\n[6] 結論:")
print(f"    k 值 3 等分 → 3 組 mean (7.59/9.51/12.52)")
print(f"    p(隨機 ≥ 觀測 gap) = {p_val:.4f}")
if p_val < 0.05:
    print(f"    → ✅ k 值有真實 3-cluster 結構")
else:
    print(f"    → ❌ k 3-cluster 唔顯著 (均勻分佈自然結果)")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)

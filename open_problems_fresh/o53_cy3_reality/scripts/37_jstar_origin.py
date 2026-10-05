#!/usr/bin/env python3
"""
O53 開放問題 2: J* 物理來源 — 由 IDCM 結構生成?
==================================================
J* (36 維 Kähler 參數) 係舊 session 優化嘅產物。
問題: J* 有冇由 K_Chain/φ 結構自然生成?

分析:
  1. J* 值有冇 φ 指數結構?
  2. J* 排序 vs K_Chain mode 數有冇對應?
  3. J* 有冇「生成公式」: J*_i = f(γ_i)?
  4. 對比: J* vs φ^(-k/12), φ^(-k/36), γ_k
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
print("O53 開放 2: J* 物理來源")
print("=" * 70)

with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)
J = np.array(jstar['Jstar_36D'])

print(f"\n[1] J* (36 維):")
print(f"    範圍: [{J.min():.6f}, {J.max():.6f}]")
print(f"    mean: {J.mean():.6f}, std: {J.std():.6f}")

# 排序
J_sort = np.sort(J)
print(f"    排序後: {np.array2string(J_sort, precision=4)}")

# --- [1] φ 指數 ---
print("\n[2] J* 嘅 φ 指數 (ln(1/J)/lnφ):")
exps = np.log(1/J) / math.log(phi)
print(f"    φ 指數範圍: [{exps.min():.3f}, {exps.max():.3f}]")
# 有冇近整數?
near_int = np.sum(np.abs(exps - np.round(exps)) < 0.3)
print(f"    近整數 φ 指數: {near_int}/36")
print(f"    前 12 個指數: {np.array2string(exps[:12], precision=2)}")

# --- [2] J* vs γ 譜 ---
print("\n[3] J* vs K_Chain γ:")
gammas = np.array([4*math.sin(math.pi*n/88)**2 for n in range(1, 45)])
gamma_low = np.sort(gammas)[:36]  # 36 個最低
print(f"    γ 前 36: [{gamma_low.min():.3f}, {gamma_low.max():.3f}]")

# J* 同 γ 有冇相關? (J* 係 Kähler 參數, 唔一定同 γ 直接相關)
# 但試: J*_i 同 γ_i 有冇單調關係?
corr = np.corrcoef(J, gamma_low)[0, 1]
print(f"    corr(J, γ_low) = {corr:.4f}")
check("J 同 γ 冇強相關 (獨立參數)", abs(corr) < 0.5, f"({corr:.3f})")

# --- [3] J* 生成公式候選 ---
print("\n[4] J* 生成公式:")
# 候選 1: J*_i ∝ φ^(-k/36)
k = np.arange(36)
cand1 = phi ** (-k/36)
cand1 = cand1 / cand1.sum() * J.sum()
# 候選 2: J*_i ∝ φ^(-k/12)
cand2 = phi ** (-k/12)
cand2 = cand2 / cand2.sum() * J.sum()
# 候選 3: J*_i ∝ 1/γ_i
cand3 = 1/gamma_low
cand3 = cand3 / cand3.sum() * J.sum()

J_sorted = np.sort(J)[::-1]
for name, cand in [("φ^(-k/36)", cand1), ("φ^(-k/12)", cand2), ("1/γ", cand3)]:
    # 排序後比較
    c_sorted = np.sort(cand)[::-1]
    c = np.corrcoef(J_sorted, c_sorted)[0, 1]
    print(f"    {name}: corr(J_sorted, cand) = {c:.4f}")

# --- [4] J* 有冇 log 結構? ---
print("\n[5] J* 嘅 log 結構:")
logJ = np.log(J)
print(f"    ln(J) 範圍: [{logJ.min():.3f}, {logJ.max():.3f}]")
print(f"    ln(J) 分佈: mean={logJ.mean():.3f}, std={logJ.std():.3f}")
# ln(J) 有冇近整數?
n_int = np.sum(np.abs(logJ - np.round(logJ)) < 0.3)
print(f"    ln(J) 近整數: {n_int}/36")

# --- [5] J* 同 44 結構 ---
print("\n[6] J* 同 44:")
print(f"    1/J 範圍: [{1/J.max():.3f}, {1/J.min():.3f}]")
print(f"    1/J mean: {np.mean(1/J):.3f}")
print(f"    44 相關: J·44 = {J.sum()*44:.4f}")
print(f"    J sum = {J.sum():.6f}")
print(f"    1/(J·44) = {1/(J.sum()*44):.4f}")
print(f"    44×mean(J) = {44*J.mean():.4f}")

# --- [6] J* 係咪「volume 均衡」? ---
print("\n[7] J* 結構檢查:")
# 每個 divisor 嘅 volume: Vol_i = κ_ijk J^j J^k
Vol_i = np.einsum('ijk,j,k->i', np.zeros((36,36,36)), J, J)  # placeholder
K = np.zeros((36,36,36))
with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val
    K[i, k, j] = val
    K[j, i, k] = val
    K[j, k, i] = val
    K[k, i, j] = val
    K[k, j, i] = val
Vol_i = np.einsum('ijk,j,k->i', K, J, J)
print(f"    Vol_i 範圍: [{Vol_i.min():.4f}, {Vol_i.max():.4f}]")
print(f"    Vol_i mean: {Vol_i.mean():.4f}")
print(f"    Vol_i std/mean: {Vol_i.std()/Vol_i.mean():.3f}")
check("Vol_i 均勻 (Kähler 均衡)", Vol_i.std()/Vol_i.mean() < 1.0, f"({Vol_i.std()/Vol_i.mean():.3f})")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)

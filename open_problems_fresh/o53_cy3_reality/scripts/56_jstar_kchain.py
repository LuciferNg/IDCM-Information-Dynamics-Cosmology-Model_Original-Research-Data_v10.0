#!/usr/bin/env python3
"""
O53 A2: J* 物理來源 — K_Chain 生成測試
===========================================
J* (36 維 Kähler 參數) 係舊 session 優化產物。
問題: J* 可唔可以由 K_Chain 結構生成?

測試:
  1. J* vs K_Chain γ 譜 (44-site, γ_n = 4sin²(nπ/88))
  2. J* vs φ^(-k/12) 排序
  3. J* 嘅 rank/結構
  4. J* 值嘅對數有冇 K_Chain 節點數結構?
"""
import os, json, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53 A2: J* K_Chain 生成測試")
print("=" * 70)

with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
print(f"\n[1] J* 基本:")
print(f"    shape: {J0.shape}")
print(f"    min/max: {J0.min():.4f} / {J0.max():.4f}")
print(f"    mean: {J0.mean():.6f}")
print(f"    ㅤ")
print(f"    J* 值 (36 個):")
for i in range(0, 36, 6):
    print(f"    {i:2d}-{i+5:2d}: " + " ".join(f"{v:8.4f}" for v in J0[i:i+6]))

# --- [1] J* 排序 vs K_Chain γ ---
print("\n[2] J* 排序 vs φ^(-k/12):")
J_sorted = np.sort(J0)[::-1]
for k in range(10):
    target = phi ** (-k/12)
    print(f"    J[{k}] = {J_sorted[k]:.4f}  φ^(-{k}/12) = {target:.4f}  比 = {J_sorted[k]/target:.3f}")

# --- [2] J* 對數結構 ---
print("\n[3] ln(J*) 結構:")
lnJ = np.log(J0)
print(f"    ln(J*) min/max: {lnJ.min():.2f} / {lnJ.max():.2f}")
print(f"    ln(J*) 排序後:")
lnJ_sorted = np.sort(lnJ)[::-1]
print(f"    " + " ".join(f"{v:.2f}" for v in lnJ_sorted))
# 間距
diffs = np.diff(lnJ_sorted)
print(f"    ln 間距: " + " ".join(f"{d:.2f}" for d in diffs[:12]))

# --- [3] ln(J*) 係咪等距 (指數譜)? ---
print("\n[4] ln(J*) 等距檢驗:")
print(f"    mean|Δln| = {np.abs(diffs).mean():.4f}")
print(f"    std|Δln| = {np.abs(diffs).std():.4f}")
print(f"    ln(φ)/3 = {math.log(phi)/3:.4f}")
print(f"    ln(φ)/6 = {math.log(phi)/6:.4f}")
print(f"    ln(2)/12 = {math.log(2)/12:.4f}")
print(f"    → J* 係咪 e^(-k·step)? step = ?")

# --- [4] J* vs 44-site γ 譜 ---
print("\n[5] K_Chain γ 譜 (γ_n = 4sin²(nπ/88)):")
N = 44
gammas = [4*math.sin(n*math.pi/88)**2 for n in range(1, N+1)]
gamma_sorted = np.sort(gammas)[::-1]
print(f"    γ 範圍: {gamma_sorted.min():.4f} - {gamma_sorted.max():.4f}")
# J* 對數值 vs γ 對數值
print(f"    ln(γ) 範圍: {math.log(gamma_sorted.min()):.2f} - {math.log(gamma_sorted.max()):.2f}")
print(f"    ln(J*) 範圍: {lnJ.min():.2f} - {lnJ.max():.2f}")
print(f"    → J* 同 γ 都係遞減譜, 但 scale 差好多")

# --- [5] J* 生成候選: J_i = γ_perm(i)? ---
print("\n[6] J* = γ 子集?")
gamma36 = gamma_sorted[:36]
ratio = J_sorted / gamma36
print(f"    J*/γ (前 36): {np.array2string(ratio[:8], precision=3)}")
print(f"    ratio std: {ratio.std():.3f}")
print(f"    → 唔係簡單 γ 子集 (ratio 唔常數)")

# --- [6] J* 嘅 φ 指數 ---
print("\n[7] J* φ 指數 (ln(J*)/ln(φ)):")
exps = np.log(J0)/math.log(phi)
print(f"    範圍: {exps.min():.2f} 至 {exps.max():.2f}")
# 近整數?
near_int = np.abs(exps - np.round(exps)) < 0.2
print(f"    近整數: {near_int.sum()}/36")
exps_sorted = np.sort(exps)
print(f"    排序: " + " ".join(f"{v:.2f}" for v in exps_sorted))

print("\n" + "=" * 70)
print("測試完成")
print("=" * 70)

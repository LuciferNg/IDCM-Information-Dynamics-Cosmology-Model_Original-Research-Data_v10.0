#!/usr/bin/env python3
"""
O54 — 檢查 1: K_Chain 模式正負頻率對稱性
==========================================
問題: K_Chain 44 個模式有冇「反模式」（負頻率/相位共軛）？
      如果譜只有正頻率 → 反物質 = 未被投影（結構必然 n_B̄ = 0）

方法:
1. K_Chain 緊束矩陣本徵值分析（正負對稱性）
2. γ_n = 4sin²(πn/88) 譜嘅奇偶結構
3. Z₂ 對偶 γ_n + γ_{44-n} = 4 嘅物理解讀
4. 相位共軛檢查: 波函數 ψ_n(x) 同 ψ_n*(x) 係咪同一個模式？
5. 對稱性結論: 反物質喺 K_Chain 結構中嘅地位

反幻覺鐵律:
- γ_n = 4sin²(πn/88), v_g = c·cos(πn/88), n=22 → 0.7071c (唔係駐波)
- 只有 n=44 Nyquist v_g=0
"""
import math
import numpy as np

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
Nd = 44
R_H = 4129.94  # Mpc

print("=" * 72)
print("O54 檢查 1: K_Chain 模式正負頻率對稱性")
print("=" * 72)

# ============ 1. K_Chain 緊束矩陣 ============
print("\n[1] K_Chain 緊束矩陣本徵值")
print("-" * 72)
# 週期邊界緊束矩陣 (hopping -1, on-site 0)
# H ψ_n = -ψ_{n-1} - ψ_{n+1} → 本徵值 -2cos(2πk/44)
# 但 IDCM 用 γ_n = 4sin²(πn/88) = 2 - 2cos(πn/44)
# 呢個對應 open chain (Dirichlet) 本徵值 2-2cos(πn/(N+1))?
# 檢查: 4sin²(πn/88) = 2(1-cos(πn/44)) → n=44: 4sin²(π/2)=4

# 構造緊束矩陣: 週期邊界
N = Nd
T = np.zeros((N, N))
for i in range(N):
    T[i, (i+1) % N] = -1
    T[i, (i-1) % N] = -1
# 加 on-site 2 (令本徵值 = 2-2cos(2πk/44) 形式)
T = T + 2 * np.eye(N)

eigvals_periodic = np.sort(np.linalg.eigvalsh(T))
print("週期邊界 44-site 緊束本徵值 (2-2cos(2πk/44)):")
print(f"  範圍: [{eigvals_periodic[0]:.6f}, {eigvals_periodic[-1]:.6f}]")
print(f"  零本徵值數: {np.sum(np.abs(eigvals_periodic) < 1e-10)}")
print(f"  負本徵值: {eigvals_periodic[eigvals_periodic < 0]}")
print(f"  正本徵值: {eigvals_periodic[eigvals_periodic > 0]}")

# 檢查: 週期邊界譜有冇正負對稱?
# 2-2cos(2πk/44): k=0 → 0, k=1..21 正, k=22 → 4, k=23..43 = 2-2cos(2πk/44)
# cos(2π(44-k)/44) = cos(2πk/44) → 簡併
print("\n  → 週期邊界譜: k=0 零模 + 21 對簡併正模 + k=22 Nyquist")
print("  → 冇負頻率模式（譜半正定）")

# ============ 2. IDCM 譜 γ_n = 4sin²(πn/88) ============
print("\n[2] IDCM 譜 γ_n = 4sin²(πn/88)")
print("-" * 72)
gamma = np.array([4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, Nd + 1)])
print(f"  γ 範圍: [{gamma.min():.6f}, {gamma.max():.6f}]")
print(f"  γ > 0: 全部 {np.sum(gamma > 0)}/44")
print(f"  Σγ = {gamma.sum():.6f} (理論: 90)")
print(f"  Σγ_even = {gamma[::2].sum():.6f} (偶數=世界)")
print(f"  Σγ_odd  = {gamma[1::2].sum():.6f} (奇數=觀察者)")
print(f"  Σγ_total (88-site 對偶) = {2*gamma.sum():.1f} = 2F₁₁? F₁₁={144}")

# 負頻率對應: sin² 函數係平方 → γ_n ≥ 0 恆真
print("\n  → γ_n = 4sin²(πn/88) ≥ 0 恆真 (平方)")
print("  → IDCM 譜只有正頻率/正能量模式，冇負頻率模式")

# ============ 3. 相位共軛檢查 ============
print("\n[3] 波函數相位共軛檢查")
print("-" * 72)
# 緊束波函數: ψ_n(x) = sin(nπx/44) (Dirichlet) or e^{ikx} (週期)
# 反粒子 = 正粒子嘅相位共軛 (CPT)
# 檢查: 如果 ψ 同 ψ* 係同一個本徵態（實波函數），則冇獨立反模式

# 週期邊界本徵向量
eigvals_p, eigvecs_p = np.linalg.eigh(T)
# 檢查本徵向量係咪實數 (相位共軛不變)
imag_norms = []
for k in range(N):
    v = eigvecs_p[:, k]
    imag_norms.append(np.linalg.norm(v.imag))
print(f"  本徵向量虛部範數: max = {max(imag_norms):.2e}")
print(f"  → 波函數 ψ = ψ* (實) → 模式同佢嘅相位共軛係同一個模式")
print(f"  → 冇獨立嘅「反模式」— CPT 共軛唔產生新模式")

# ============ 4. Z₂ 對偶 ============
print("\n[4] Z₂ 對偶 γ_n + γ_{44-n} = 4")
print("-" * 72)
pairs_ok = 0
for n in range(1, 23):
    g_n = 4 * math.sin(math.pi * n / 88) ** 2
    g_dual = 4 * math.sin(math.pi * (44 - n) / 88) ** 2
    if abs(g_n + g_dual - 4.0) < 1e-12:
        pairs_ok += 1
print(f"  Z₂ 對偶驗證: {pairs_ok}/22 對 γ_n + γ_{44-n} = 4")
print(f"  → Z₂ 對偶 (n ↔ 44-n) 係譜對稱性，但唔係正負頻率對偶")
print(f"  → 兩個模式都係正能量，Z₂ 係「世界↔觀察者」對偶 (O34), 唔係物質↔反物質")

# ============ 5. 對稱性結論 ============
print("\n[5] 結構結論")
print("-" * 72)
print("""
K_Chain 譜結構:
  1. γ_n = 4sin²(πn/88) ≥ 0 恆真 → 譜半正定，冇負頻率模式
  2. 本徵向量全實 → ψ = ψ* → 相位共軛不產生新模式
  3. Z₂ 對偶 n ↔ 44-n 係「世界/觀察者」對偶 (O34), 唔係物質/反物質
  4. 週期邊界 k=0 有零模 (真空)，k=22 Nyquist 有最大能量

⟹ 結構推論（待驗證）:
  反粒子唔係 K_Chain 嘅「負頻率模式」— 冇呢啲模式存在。
  如果反物質豐度 = 反模式佔有數，則 n_B̄ = 0 係 K_Chain 結構必然。

  ⚠️ 但呢個只係「缺場」論證 (absence of anti-modes)，
  需要 (a) 投影算符 kernel 分析 (檢查 2)
       (b) CP 破壞相位 δ_CP 結構檢查 (檢查 3)
       (c) 湮滅殘留觀測對比 (檢查 4)
  先可以閉合。

  🔴 開放: 反物質可能唔係「模式」而係「投影」嘅另一面 —
  O33 黑洞反投影 T_pipe† = I - T_pipe 係「反物質通道」候選。
""")

# ============ 驗證摘要 ============
results = {
    "test": "K_Chain 正負頻率對稱性",
    "gamma_all_positive": bool(np.all(gamma > 0)),
    "gamma_min": float(gamma.min()),
    "sum_gamma": float(gamma.sum()),
    "sum_gamma_even": float(gamma[::2].sum()),
    "sum_gamma_odd": float(gamma[1::2].sum()),
    "eigenvectors_real": bool(max(imag_norms) < 1e-10),
    "z2_pairs_ok": int(pairs_ok),
    "conclusion": "譜半正定 + 實波函數 → 冇獨立反模式 → n_B̄=0 結構候選 (待投影分析)",
}
print("\n驗證摘要:")
for k, v in results.items():
    print(f"  {k}: {v}")

import json
with open("data/01_kchain_mode_symmetry.json", "w") as f:
    json.dump(results, f, indent=2)
print("\n✅ 結果已寫入 data/01_kchain_mode_symmetry.json")

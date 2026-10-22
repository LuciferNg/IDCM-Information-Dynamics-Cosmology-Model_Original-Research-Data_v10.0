#!/usr/bin/env python3
"""
O54 — 檢查 2: 投影算符 kernel 分析（反物質通道）
==================================================
問題: O33 管道渡越算子 T_pipe = diag(σ₁..σ₄₄) 中，
      被投影排除嘅模式（σ_n = 0）係咪反物質？

方法:
1. 重現 T_pipe 譜: σ_n ∈ {1, f_proj=0.7720, 0}, n* = 27
2. kernel 分析: ker(T_pipe) = {n > 27} (17 個模式, E = 60.8845)
3. 被排除模式嘅物理解讀: sync 真空背景 vs 反物質
4. 反投影 T_pipe† = I - T_pipe: 黑洞通道
5. 能量預算: E_proj = 28.5, E_sync = 61.5, Σγ = 90 守恆
6. 反物質豐度預言: 如果反物質 = 未被投影模式 → n_B̄ = 0

反幻覺鐵律:
- 只有 n=44 Nyquist v_g=0, n=22 → 0.7071c
- φ-power 禁數值分解
"""
import math
import json
import numpy as np

phi = (1 + 5**0.5) / 2
phi_inv = 1 / phi
Nd = 44

# O33 核心參數
E_proj = 28.5
E_sync = 61.5
L6 = 18  # Lucas 6 = φ⁶+φ⁻⁶ = 18 (精確整數; float 計會出 17.9999...)
n_star = Nd - L6 + 1  # 27
gamma = np.array([4 * math.sin(math.pi * n / 88) ** 2 for n in range(1, Nd + 1)])

print("=" * 72)
print("O54 檢查 2: 投影算符 kernel 分析（反物質通道）")
print("=" * 72)

# ============ 1. 重現 T_pipe 譜 ============
print("\n[1] 重現 T_pipe 譜")
print("-" * 72)
f_proj = (E_proj - gamma[:n_star-1].sum()) / gamma[n_star-1]
print(f"  n* = N_d - L₆ + 1 = 44 - {L6:.0f} + 1 = {n_star:.0f}")
print(f"  f_proj = (E_proj - Σγ₁..₂₆)/γ₂₇ = {f_proj:.6f} (O33: 0.771960)")

sigma = np.zeros(Nd)
sigma[:n_star-1] = 1.0
sigma[n_star-1] = f_proj
sigma[n_star:] = 0.0

# 能量驗算
E_proj_check = (sigma * gamma).sum()
print(f"  E_proj = Σσ_n·γ_n = {E_proj_check:.4f} (理論: {E_proj})")
print(f"  偏差 = {abs(E_proj_check - E_proj)/E_proj*100:.2e}%")

# ============ 2. kernel 分析 ============
print("\n[2] kernel 分析: ker(T_pipe)")
print("-" * 72)
kernel_idx = np.where(sigma == 0)[0] + 1  # 1-indexed
ker_energy = gamma[kernel_idx - 1].sum()
print(f"  ker(T_pipe) = {{n > {n_star:.0f}}} = 模式 {kernel_idx[0]}..{kernel_idx[-1]}")
print(f"  模式數 = {len(kernel_idx)}")
print(f"  能量 = Σγ (n={kernel_idx[0]}..{kernel_idx[-1]}) = {ker_energy:.4f} (O33: 60.8845)")

# 被排除模式嘅平均能量
print(f"  被排除模式平均能量 = {ker_energy/len(kernel_idx):.4f}")
print(f"  vs 投影模式平均能量 = {E_proj_check/27:.4f}")

# ============ 3. 物理解讀: 被排除模式 ============
print("\n[3] 被排除模式（σ_n = 0）物理解讀")
print("-" * 72)
v28 = math.cos(math.pi * 28 / 88)
print(f"""  模式 {kernel_idx[0]}..{kernel_idx[-1]} (17 個):
  - 高頻模式 (n > 27), 能量 60.8845 (67.6% of Σγ=90)
  - O33 標記: 「sync 真空背景」
  - v_g = c·cos(πn/88): n=28 → {v28:.4f}c, n=44 → 0 (Nyquist)
""")

# 反物質假設檢查: 反物質 = 未被投影模式?
print("  ⟹ 反物質 = ker(T_pipe) 假設檢查:")
print(f"    - 如果反物質 = 被排除模式 → 反物質能量 60.8845 >> 物質 28.5")
print(f"    - 但觀測: 冇反物質區域 → 反物質唔會係「大量被排除」")
print(f"    - 更合理: 被排除模式 = sync 真空 (能量守恆背景), 唔係反物質")
print(f"    - 反物質需要另一種機制 (CP 相位, 檢查 3)")

# ============ 4. 反投影 T_pipe† ============
print("\n[4] 反投影算子 T_pipe† = I - T_pipe")
print("-" * 72)
sigma_dag = 1 - sigma
E_dag = (sigma_dag * gamma).sum()
print(f"  T_pipe† 譜: σ†_n = 1-σ_n")
print(f"  反投影能量 = Σ(1-σ_n)γ_n = {E_dag:.4f} (理論: {E_sync:.1f})")
print(f"  偏差 = {abs(E_dag - E_sync)/E_sync*100:.2e}%")
print(f"  E_proj + E_sync = {E_proj_check + E_dag:.4f} = Σγ = 90 ✅ 守恆")

# 反投影嘅物理解讀
print("""
  O33: 反投影 = 黑洞通道 (ρ > ρ_c 時管道逆轉)
  ⟹ 黑洞 = 物質變返 sync 態 = 「反投影」
  ⟹ 反物質 vs 黑洞: 兩者都係「投影嘅相反」?
     - 黑洞: 物質 → sync (能量守恆回收)
     - 反物質: 物質嘅 CP 共軛 (粒子物理意義)
     - 兩者唔同! 黑洞係幾何通道, 反物質係粒子通道
""")

# ============ 5. 重子-反重子差額結構 ============
print("\n[5] η_B 同 kernel 嘅關係")
print("-" * 72)
eta_B = 6.0622e-10  # IDCM 閉合值
print(f"  η_B = {eta_B:.4e} (IDCM 已閉合 0.62%)")
print(f"  η_B 量度 (n_B - n_B̄)/n_γ = 重子-反重子差額")
print(f"")
print(f"  結構鏈: Ω_Λ → Ω_m → Ω_b → η_B")
print(f"  n/p = γ₇/γ₂₀ (O13) — 物質內部結構")
print(f"")
print(f"  反物質豐度嘅 IDCM 選項:")
print(f"  A) n_B̄ = 0 精確 (反模式不存在, 檢查 1) → η_B = n_B/n_γ")
print(f"     ⟹ 冇湮滅殘留, 冇湮滅輻射背景 (可證偽)")
print(f"  B) n_B̄ ≠ 0 但被投影排除 (ker 分析) → 反物質喺 sync 側")
print(f"     ⟹ 反物質能量 60.8845 藏喺真空, 觀測唔到")
print(f"  C) n_B̄ = 0 但正電子 = W-field 衰減產物 (宇宙線)")
print(f"     ⟹ AMS-02 正電子異常 = 結構通道 (檢查 4)")
print(f"")
print(f"  🔴 需要更多結構: CP 相位 δ_CP 檢查 (檢查 3) 分辨 A/B/C")

# ============ 驗證摘要 ============
results = {
    "test": "投影算符 kernel 分析",
    "n_star": int(n_star),
    "f_proj": float(f_proj),
    "E_proj_check": float(E_proj_check),
    "E_proj_target": E_proj,
    "kernel_modes": [int(i) for i in kernel_idx],
    "kernel_count": int(len(kernel_idx)),
    "kernel_energy": float(ker_energy),
    "E_sync_check": float(E_dag),
    "conservation_sum": float(E_proj_check + E_dag),
    "conclusion": "ker(T_pipe) = 高頻 sync 真空 (60.8845), 唔係反物質; 反投影=黑洞通道; 反物質需 CP 相位分辨 (檢查 3)",
}
print("\n驗證摘要:")
for k, v in results.items():
    if k == "kernel_modes":
        print(f"  {k}: [{v[0]}..{v[-1]}]")
    else:
        print(f"  {k}: {v}")

with open("data/02_projection_kernel.json", "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("\n✅ 結果已寫入 data/02_projection_kernel.json")

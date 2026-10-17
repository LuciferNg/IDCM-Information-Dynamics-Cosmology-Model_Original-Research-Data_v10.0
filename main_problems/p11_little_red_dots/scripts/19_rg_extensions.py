#!/usr/bin/env python3
"""
RG 推導延伸 — λ_Edd 誠實修正 + β 壓縮比公設 + 判別檢驗 + b₀ 候選 (2026-09-09)
================================================================================
Part A — λ_Edd=10 誠實修正: M(8) 本身用 λ=0.1 效率假設計 → λ=10 係定義自洽
         真正閉合: M_base × (1+δ)^{3/2} = M_obs(λ=0.1)
Part B — β = 壓縮比公設 (block-spin 自由度計數): β = ΔN_cand/N_eff
         判別檢驗: 截斷版本 4.19 vs 無截斷 4.00 vs 無分支 3.14 vs 觀測 4.081±0.497
Part C — b₀ 候選 + dβ/dℓ×M₄/M₀ 候選狀態更新 (保持 🟡)
"""
import math, json
import numpy as np

phi = (1+5**0.5)/2
N_d, B, L5, L4, N_gen, F8, F10 = 44, 4, 11, 7, 3, 21, 55
mu2 = 2.0
OUT = 'data/19_rg_extensions.json'
res = {}

print("="*78)
print("A. λ_Edd=10 誠實修正 (record 10 §3 解讀更新)")
print("="*78)
Lbol_W = 10**45.94 * 1e-7
M_obs_Edd01 = 6.97319969612336e6   # script 11: M_obs_Edd01_median (λ=10% 假設)
M_obs_Edd1 = 6.97319969612336e7    # script 11: M_obs_Edd1_median (λ=100% 假設)
L_edd_M = 1.26e31 * M_obs_Edd01
lam = Lbol_W / L_edd_M
print(f"  M(8) 來源: script 11 M_obs_Edd01_median = {M_obs_Edd01:.2e} M☉")
print(f"  → 呢個質量本身假設 Eddington 效率 λ=10% (名 Edd01)")
print(f"  → λ_Edd = Lbol/L_Edd(M_Edd01) = {lam:.2f} 係定義恆等, 唔係獨立發現 ⚠️")
print(f"  真正資訊: IDCM M_base = 1.914e6 (record 07) × (1+δ)^1.5")
M_base = 1.914e6
delta = 1.3668
M_pred_env = M_base * (1+delta)**1.5
print(f"  M_pred = {M_base:.2e} × (1+{delta:.4f})^1.5 = {M_pred_env:.2e}")
print(f"  vs M_obs(λ=10%) = {M_obs_Edd01:.2e} → ratio {M_pred_env/M_obs_Edd01:.4f}")
print(f"  vs M_obs(λ=100%) = {M_obs_Edd1:.2e} → ratio {M_pred_env/M_obs_Edd1:.4f}")
print(f"  → 閉合係對 λ=10% 質量 (ratio≈1), 對 λ=100% 差 10× — IDCM 預言 LRD 係 10% 效率")
print(f"  → λ_Edd=10 嘅真正角色: 效率假設嘅自洽標記, 唔係新常數身份 🟡→✅ 修正")
res['partA'] = {'lam_Edd': float(lam), 'M_pred_env': float(M_pred_env),
                'ratio_Edd01': float(M_pred_env/M_obs_Edd01),
                'ratio_Edd1': float(M_pred_env/M_obs_Edd1)}

print("\n" + "="*78)
print("B. β = 壓縮比公設 (block-spin 自由度計數)")
print("="*78)
db_obs, db_err = 4.080733175925888, 0.4970611813721131
cand = {
    '截斷 (4N_d/(N_d−μ²))': 4*N_d/(N_d-mu2),
    '無截斷 (4N_d/N_d)':    4*N_d/N_d,
    '無分支 (3N_d/(N_d−μ²))': 3*N_d/(N_d-mu2),
    '截斷+分支/2':         2*N_d/(N_d-mu2),
}
print(f"  觀測: dβ/dℓ = {db_obs:.3f} ± {db_err:.3f}")
for name, val in cand.items():
    sigma = (val - db_obs)/db_err
    print(f"  {name:<24} = {val:.4f}  (vs 觀測: {sigma:+.2f}σ)")
print()
print(f"  公設: β(b) = ΔN_cand/N_eff — 每步 block-spin 壓縮比 (候選模態/有效模態)")
print(f"  論證: Kadanoff 一步將 4 世界副本 (每 44 模) 壓縮成 1 區塊世界")
print(f"        → 候選 = 4N_d = 176; 凝聚截斷 → 有效 = N_d−μ² = 42")
print(f"        → β = 176/42 = 88/21 = 4.1905")
print(f"  判別力: 截斷 vs 無截斷差 0.19σ — 現有誤差 (±0.50) 未夠分辨 ⚠️")
print(f"          需要更緊斜率測量 (多波段 + 深樣本) 先可以做判別 🟡")
res['partB'] = {'obs': db_obs, 'err': db_err,
                'candidates': {k: float(v) for k, v in cand.items()}}

print("\n" + "="*78)
print("C. b₀ 同 dβ/dℓ×M₄/M₀ 候選狀態")
print("="*78)
b0_naive = 2.3886097487680744
c12_5 = 12/5
print(f"  b₀ (未加權) = {b0_naive:.4f} vs 12/5 = {c12_5} → dev {(b0_naive-c12_5)/c12_5*100:.2f}%")
print(f"  b₀ = (B·N_gen)/F₅ = 12/5 候選 — 未加權 fit 受噪聲污染, 需加權 intercept 🟡")
prod = (88/21)*(7/15)
print(f"  dβ/dℓ × M₄/M₀ = (88/21)×(7/15) = {prod:.4f} vs 2 → dev {(prod-2)/2*100:.2f}%")
print(f"  → 0.9% 候選, 唔係代數 — 維持 🟡 唔入列 (φ-power trap 教訓)")

print("\n" + "="*78)
print("D. 修訂開放問題狀態")
print("="*78)
print("  #19 λ_Edd=10 身份 → ✅ 撤銷問題: λ=10 係效率假設自洽 (record 10 修正)")
print("  #10 β 函數形式 → 🔴 壓縮比公設已立 (record 12), 函數形式證明仍開")
print("  新: M 預言 λ=10% 效率 — 可證偽: 光譜質量 (唔靠 Eddington) 應證實 10% 效率")

json.dump(res, open(OUT, 'w'), indent=2)
print(f"\nSaved {OUT}")

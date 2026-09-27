# O130 — 小波工具箱宇宙學應用 (v9.0→v10.0 遷移)

## 狀態: 🟡 遷移判決完成 (32/32 PASS + 14 結構聲稱)

## 結論

v9.0 `wavelet_toolbox/` 只有**方法層 + 純結構骨架**遷移 (P: γ_n=4sin²(πn/88) 88 環精確譜 /
λ_sync=2πR_H/88≡πR_world/44 / v_g=cos(πn/88) / B=4,z=4^ℓ−1 / 小波+EMD 工具)；所有**定量偵測聲稱**
失效 (R: φ-ratio 已證偽, 17/19 諧波 = 單調斜坡偽影 + sub-bin aliasing; X: H(z) ζ 模型, sync dip z_c=0.6)。
BOSS DR12 (5 h⁻¹Mpc bins) 對 K_Chain 階梯嘅解析度只到 n_max = 8.53。

## 關鍵公式

- **P 遷移**: `γ_n = 4 sin²(πn/88)` (88-site 環 Laplacian 精確譜, Σγ=176=4N_d, γ_n+γ_{44−n}=4)
- **P 遷移**: `λ_sync = 2πR_H/88 ≡ πR_world/44 = 294.877 Mpc` (v9≡v10, dev=0)
- **P 遷移**: `v_g = cos(πn/88)` (O99)；`B = L₃ = 4`，`z = 4^ℓ − 1` (O76)
- **A→🔴**: 阻抗 `Z_n = γ_n/|v_g,n|`，反射 `R_n = (Z_n−Z_{n−1})/(Z_n+Z_{n−1})`，`s_ref = λ_sync/(2n|R_n|)`
  — 部件結構，但模型無 v10.0 擁有者 + **O118 裁定唔做**（同 O131 一致；階梯 169–190 h⁻¹Mpc）
- **k-space**: `k_n = n·(2π/λ_sync) = 88n/R_world` (sync = 88 環諧和, m=88 精確; 44-鏈諧和 = 44/π 非整數)
- **解析度極限**: `Δs_n = λ_sync/[n(n+1)] ≥ Δs_bin(=5)` ⟹ `n_max = 8.53`
- **R 🔴**: φ-ratio `A_n ∝ φ^n` 證偽 (log-slope 0.2937 vs log φ 0.4812, 39%; γ_n 模型 RMS 0.3115 < φ^n 0.6064)
- **斜坡偽影**: EMD residual S/N 對 n 單調 (Spearman ρ=0.9979, 1 IMF) ⟹ 「17/18」非 17 諧波
- **X 🔴**: `H(z)=H₀(1+z)^α` with ζ(z) (05)；sync dip `z_c = 3/5` (O126 撤回)

## 依賴

v9.0 `wavelet_toolbox/` → O130；交叉 O133 (k-space) / O129 (λ_sync) / O126 (ζ 撤回) /
O138 (z=17=F_proj) / O76 (離散 z) / O99 (色散) / O135 (P/R/A/X 分類法) / O131 (同批 stacking 遷移) /
O118 (裁定唔做阻抗模型)

## 驗證統計

| Script | PASS | 內容 |
|:-------|:----:|:-----|
| `scripts/01_migration_inventory.py` | 18/18 | λ_sync 幾何 / γ_n 精確譜 / 阻抗階梯 / H(z) ζ / z=17 / φ-ratio / P-R-A-X |
| `scripts/02_wavelet_emd_rerun.py` | 9/9 | 實數據 DWT+EMD 重跑 + 諧波掃描 + 反射階梯 + k-space 對照 |
| `scripts/03_significance_null.py` | 5/5 | φ-ratio 不可辨識 / 斜坡診斷 / BOSS 解析度極限 |
| **合計** | **32/32** | + 14 結構聲稱 |

## 密度基準

- 本 O 係**遷移分類 + null 檢定**，非數值閉合聲稱；無結構常數匹配 → 不適用 O208 分位數門檻。
- 相關 null: φ-ratio 檢定 (斜率 39% 偏離 log φ)；斜坡診斷 (Spearman ρ=0.9979, p=1.65e-20)；
  解析度 (n_max=8.53, 客觀由 λ_sync 同 bin 間距決定)。

## 開放

- eBOSS 反射尺度獨立檢驗 🟡 / DESI DR2 細 bin 重跑諧波階梯 🟡 / aliasing 機制重新形式化或併入 O76 🔴 /
  v10.0 native 阻抗算子 🟡
- 目錄處置 (保留 / 併入 O133) 待調律者裁定

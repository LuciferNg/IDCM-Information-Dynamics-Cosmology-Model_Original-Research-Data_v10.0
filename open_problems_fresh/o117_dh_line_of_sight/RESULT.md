# O117 — DH/rd 視線投影 (Line-of-Sight)

## 狀態: 🟢 已閉合（診斷性）— 2026-09-26
> 憑證: `scripts/12_closure_adjudication.py` (4/4 PASS) + `docs/05_closure_verdict.md`

## 結論
DM 與 DH 係 IDCM 中兩個獨立投影 —— `D_H = dD_A/dz` 係 Friedmann 方程嘅推論，IDCM 冇 Friedmann 方程，故此關係唔成立。此**結構診斷**為本 O 唯一存活結果。本 O 全部**數值**內容已作廢；現行徑向律由 **O170 arch 核**提供。

## 關鍵公式
- ✅ ★ **`D_H ≠ dD_A/dz`**（唯一存活；O169 + O170 雙重確認）
- ✅ 取代者（O170）：`M(ℓ) = sec(π·n_c/88)`，`n_c = N_d/2 + B·sin(πℓ) | N_d/2`，χ²(D_H) = 3.4712/6
- 🔴 作廢：DH 全式、`C_DM`、`C_DH`、`4/3`、`δ_k0` Gaussian、**AP χ² = 4.65/5**、**盲測 Σm_ν = 0.08711 eV**、`T̂⁵`

## 依賴
O76 → O51 → O117（診斷）→ O170（徑向律取代）→ O118（已閉合：前提作廢）

## 密度基準
- `N_search = N/A` — 存活聲稱係**結構/no-go 陳述**，非數值匹配（O208 §二豁免）
- `q_obs = N/A` — 全部數值聲稱已作廢，無候選可定義

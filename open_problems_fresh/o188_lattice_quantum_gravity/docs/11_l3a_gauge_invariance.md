# O188 docs/11 — R3 L3a：γ 係 area gauge（不變量驗證）

**日期**: 2026-10-04（Route L3 第三輪）
**腳本**: `scripts/11_l3a_gauge_invariance.py` — **4/4 PASS**（logs/11.txt）
**對象**: L3 殘留「γ 唔係 IDCM 內生」之詮釋

---

## 〇、一句話

測試「IDCM 物理可觀測量係咪對 area-rescaling s（γ 類自由度）不變」。
結果：**7 個 ratio-type 可觀測量全部 s-invariant；只有絕對面積類（A_h、R_world、a_ℓ）隨 s 變** ⟹ 「IDCM 冇 γ」係**結構必然（gauge）**，唔係缺陷。

## 一、精確結果

| 檢查 | 內容 | 結果 |
|:-----|:-----|:-----|
| M1 | 量分類：7 ratio-type（dimensionless）vs 3 absolute-area | ✅ |
| M2 | γ₂₂/γ₁₁ = 3.8478… 對 s=3.7 rescale 不變（dev 0.0） | ✅ |
| M3 | 絕對面積 ∝ γ（同一個 slot） | ✅ |
| M4 | 所有 7 個物理量 s-invariant ⟹ gauge area-scale | ✅ |

## 二、結構意義

- **LQG**：面積 = 8πγℓ_P²·√(j(j+1)) —— γ 固定**絕對面積標定**（Planck area ↔ graph area 單位換算）。
- **IDCM**：所有物理預測（c、色散 sin(x)/x、譜比、parity 計數、sign_rank、二面角、graviton DoF）皆**無面積絕對標定** —— 只有面積比有物理意義。
- ⟹ **IDCM 嘅 cell area a_ℓ² 同 LQG 嘅 8πγℓ_P² 佔同一個 slot**：一個整體 area unit。γ 嘅「值」在此框架下係 gauge。

## 三、判決

- **L3 缺口詮釋升級**：由「γ 唔係 IDCM 內生（缺失）」→「**γ 係 IDCM 內在 gauge，冇內生值係必然**」。
- **與 docs/12 合併睇**：gauge 唔等於冇意義 —— γ 嘅**值**可由 counting 結構固定（docs/12），只係冇獨立物理自由度。

## 四、對照
- R2 docs/07：40 數掃描零命中（γ 唔係結構有理數）。
- R3 docs/11：γ 佔 area-gauge slot（**值本身唔係物理參數**）—— 兩者一致，且將「缺失」重新詮釋為「必然」。
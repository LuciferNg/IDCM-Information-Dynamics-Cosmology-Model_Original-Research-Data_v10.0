# O53 決定性誠實報告 — λ₁/tr(Y²) 閉合撤銷

> **日期**: 2026-08-22
> **狀態**: 🔴 **兩個核心閉合正式撤銷（建基於錯誤數據）**
> **腳本**: scripts/71-79

---

## 一、事件時間線

1. 用戶下載 HuggingFace `polytopes-4d` 完整數據集（30GB, 473M polytopes）
2. 提取 (36,98) polytope（20 vertices normal form）+ 對照 (36,94)
3. CYTools 由真實 polytope（Sage export 48 points）成功計算：
   - h11=36, h12=98, χ=-124 ✅
   - **完整 intersection numbers（36³, 1341 nnz, triangulation 獨立）**
4. 對比發現 `kappa_36d_raw.json` 唔係真 intersection numbers：
   - CYTools 1341 entries vs 舊 1122 entries
   - 只有 201 個共同 entries（67 個完全一樣）
5. 用 CYTools 真 κ 重新分析：
   - **λ₁ = 3.697 ≠ φ^(1/3) = 1.174（誤差 215%）**
   - **tr(Y²) = 16.14 ≠ 5（誤差 223%）**
6. J* 合法性檢查：
   - **J*[:32] 唔喺 Kähler cone（contains = False）**
   - J* 係「優化擬合向量」，唔係真正 Kähler form

## 二、撤銷聲明

| 之前閉合 | 狀態 | 原因 |
|:---------|:----:|:-----|
| **λ₁ = φ^(1/3)（0.004%）** | 🔴 **撤銷** | 舊 κ 數據錯誤 + J* 唔喺 Kähler cone |
| **tr(Y²) ≈ 5 = B+1（1.05%）** | 🔴 **撤銷** | 同上 |
| **J* ≈ φ^(-n)（10.1%）** | 🔴 **撤銷** | J* 唔係合法 Kähler 參數 |
| **3×12D block-triangular** | ✅ **成立** | CYTools κ 都確認（Schur 下三角 = 0）|
| **n/3 量化（c_f）** | ✅ **獨立成立** | 唔依賴 κ（只依賴 SM 質量）|
| **Δδ = c_f·ln(φ)（2.8%）** | ✅ **獨立成立** | 同上 |
| **Vtd = φ^(-10) 等 CKM** | ✅ **獨立成立** | 同上 |

## 三、教訓

1. **`kappa_36d_raw.json` 來源不明** — 同 CYTools 真 intersection numbers 大相徑庭，之前所有基於佢嘅閉合需要撤銷
2. **J* 唔係 Kähler form** — 之前「Attractor gauge 鎖定 J*」嘅講法冇幾何根據；J* 只係數值優化產物
3. **3×12 block-triangular 係唯一 survive 嘅幾何閉合** — 因為佢係 κ 本身嘅性質（唔依賴 J 嘅選擇）

## 四、仍然有效嘅閉合（唔依賴 κ 數據）

- 3×12D block-triangular 結構（Schur 分解）
- SM 質量 Δδ = c_f·ln(φ)，c_f ∈ n/3（p=7.9e-5）
- CKM φ 指數（Vtd=φ^(-10) 等）
- 12 = (Nd−2B)/3 = (44−8)/3（K_Chain 結構）

## 五、新方向

1. 🔴 **用 CYTools 真 κ 重新搜尋 λ₁** — 搵一個合法 J ∈ Kähler cone 令 λ₁ = φ^(1/3)
2. 🔴 **3×12 block 結構嘅 su(12) 解讀** — 用真 κ 驗證
3. 🟡 檢查 `kappa_36d_raw.json` 究竟係乜（可能係唔同 polytope 或者唔同 basis）

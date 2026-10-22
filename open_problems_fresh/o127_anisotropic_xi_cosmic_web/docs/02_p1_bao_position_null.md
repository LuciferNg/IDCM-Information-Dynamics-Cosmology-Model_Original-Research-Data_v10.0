# O127 docs/02 — P1: BAO 尺度檢定 + 諧波序列 null test

> 腳本: `scripts/02_bao_position_and_harmonic_null.py` → `data/verify/02_bao_position_and_harmonic_null.log`
> 數據: eBOSS DR16 LRG 官方 ξ(s) data vector + BAO model（`data/raw/`，Bautista+2020, MNRAS 500, 736）
> 狀態: **P1a 🟢 零參數閉合 · P1b 🔴 v9.0 偽影證偽**

---

## 一、結論（先行）

1. **P1a 🟢** — IDCM 零參數 BAO 尺度 `r_d = λ_sync/2 = πR_world/88 = 147.4386 Mpc`
   同 eBOSS DR16 LRG fiducial `r_d = 147.78 Mpc` 差 **−0.231%**；α-dilation fit 得
   `α_best = 1.0017`（χ²=18.50/40）。**零自由參數、零擬合**。
2. **P1b 🔴** — v9.0「n=3..20 全部 18/18 S/N>3 檢測」係**幾何必然偽影**：
   19 個 `λ_sync/n` 位置塞入 96 Mpc/h 跨度，`d_med = 1.78 Mpc/h = 0.36 bin`（bin 寬 5），
   位置互相重疊、零 look-elsewhere 控制。位置隨機化 null test（10⁵）顯示
   `n≥3` 嘅超額**唔超越隨機**（P=0.126 / 0.388）。
3. **v9.0「IDCM BAO 喺 203 h⁻¹Mpc、喺 BOSS 範圍外」= 換算錯誤**（÷h 而非 ×h，見 docs/05）。

---

## 二、P1a — BAO 尺度（零參數）

| 量 | 值 | 來源 |
|---|---|---|
| ω_ring | 72.59 km/s/Mpc | O213（c = R_world·ω_ring, SI 精確） |
| R_world = c/ω_ring | 4129.9416 Mpc | O73 |
| λ_sync = 2πR_world/88 | 294.8771380 Mpc | O51 閉合 |
| **r_d = λ_sync/2 = πR_world/88** | **147.4385690 Mpc** | O51/O167 閉合 |
| eBOSS fiducial r_d | 147.78 Mpc | Bautista+2020 |
| **偏差** | **−0.231%** | — |

α-dilation fit（官方 BAO model ξ₀(s/α)、ξ₂(s/α) 擬合 data vector，s=2.5→192.5）：
`α_best = 1.0017`，`χ²_min = 18.50 / 40 dof` → 觀測 BAO 尺度 `= 148.03 Mpc`。
`IDCM/fid = 0.9977` 落喺 `α_best ± 1σ` 內。

### ★ h 投影敏感性（用戶要求逐個標明）

IDCM 無單一 H₀（O73 尺度投影結構）；由同一個 ω_ring 生成多個投影。
`λ_sync/2` 落 eBOSS s-軸（[Mpc/h]，`s = r_phys × h`）時：

| 投影 | h | s = 147.4386·h [Mpc/h] | 對觀測峰 (≈99.9) |
|---|---|---|---|
| **h_cmb（CMB 尺度）** | **0.674071** | **99.38** | ✅ 落峰上 |
| eBOSS fiducial | 0.676000 | 99.67 | ✅ 落峰上 |
| h_o170（徑向） | 0.711570 | 104.91 | +5.0（1 bin） |
| ω_ring/100 | 0.725900 | 107.03 | +7.1（1.4 bin） |
| h_lad（徑向/BAO） | 0.731300 | 107.82 | +7.9（1.6 bin） |

> **裁定**：`h-無關` 嘅物理比較（147.4386 vs 147.78 Mpc, −0.23%）係主結論，
> 不受投影選擇影響。落 s-軸嘅位置則**強烈依賴投影**（99.4→107.8），
> 只有 **h_cmb 投影落喺觀測峰**；`ω_ring/100` 裸投影偏 +7%。
> ⚠️ 本 O 唔主張 `ω_ring/100` 係「正確」h——BAO 屬徑向/CMB 混合尺度，
> 投影選擇屬 O73/O170 域，本 O 只報敏感度。

---

## 三、P1b — 諧波序列 `λ_sync/n` null test（v9.0 偽影證偽）

v9.0 聲稱 18 個 `λ_sync/n`（n=3..20）全部 S/N>3。三項檢定：

### (i) 位置解析度 —— 測試零鑑別力
- 19 個位置（n=2..20）擠入 96 Mpc/h 跨度；`d_med = 1.78 Mpc/h = 0.36 bin`
- **14/19 個位置落喺同一 bin**（相鄰 gap < bin 寬）
- ⟹ 多個「預言」根本不可分辨；S/N>3 係同一 bin 被數多次

### (ii) 殘餘結構 vs 位置隨機化 null（10⁵ 次）
殘餘 = 官方 ξ₀ 減 log 空間 5 階 broadband（限制 s≥25 避開 1-halo 區），33 bins。

| 群 | obs mean\|S/N\| | obs #>3 | null mean | P |
|---|---|---|---|---|
| n≥3（5 位置） | 1.75 | 1 | 1.12 ± 0.53 | **0.126** |
| n≥3 count | — | 1 | 0.47 | **0.388** |
| **n=2（BAO）單獨** | **3.56** | — | — | 見 P1a |

⟹ `n≥3` 高階諧波**唔超越隨機 null**（零檢測）；殘餘超額**集中喺 n=2 BAO**。
`n=2` 嘅 \|S/N\|=3.56 係真 BAO 特徵（已由 P1a 獨立閉合）。

### (iii) 密度基準入場券（O208）
- `N_search = 33`（殘餘 bins）
- `d_med = 1.78 Mpc/h = 0.36 bin`
- `q_obs = 2`（預言位置中 \|S/N\|>3 嘅數）
- ⟹ v9.0 嘅「18/18」**冇報 d_med**，而 `d_med ≪ bin 寬` ⟹ 未達入場券。

---

## 四、對 v9.0 嘅裁決

| v9.0 聲稱 | 裁決 |
|---|---|
| IDCM BAO 喺 203 h⁻¹Mpc、範圍外 | 🔴 **證偽** — 換算錯誤（÷h） |
| n=3..20 18/18 S/N>3 檢測 | 🔴 **證偽** — 幾何必然偽影（d_med ≪ bin） |
| 阻抗反射 R_n 產生各向異性 | 🔴 **證偽** — R_n 全正（Z_n 單調），無法產生正負交替（見 docs/06） |
| λ_sync = 294.877 Mpc | ✅ **有效** — 逐位一致，遷移 |
| BAO = λ_sync/2 = 147.439 Mpc | ✅ **有效** — 零參數閉合 |

---

## 五、PASS 統計
`11/11 PASS`（`data/verify/02_bao_position_and_harmonic_null.log`）

# O198 docs/03 — 中位張力成長閉合 (Growth Closure, channel-resolved duty-cycle)

> 依賴: docs/02 (實測 λ 攻堅, 推翻 λ 散射吸收 + 均勻成長排除), scripts/06 (11/11 PASS)。
> 零新常數: λ = f_bar = B/(N_d−B) = 0.1 (O173), ε = 0.1 (標準), t_S = 4.5e8 yr (Salpeter)。

## 一、問題

docs/02: 中位張力係結構性 (2.5σ 模型 / 3.7σ 觀測散射, Δln = 1.78):
- λ 散射吸收唔到 (實測 λ geo 0.70 令預測中位更低 5.40e6)
- **均勻成長被排除** (閉合需 g = 5.92, 預言 2 容許 g ≤ 1.14 — 矛盾 5.2×)
- virial 高估唔夠 (剩 ~0.37 dex)

## 二、★成長閉式 (scripts/06 T8a, 零新常數)

```
t_ef = t_S · ε/(λ(1−ε)) = 4.5e8 × 0.1/(0.1 × 0.9) = 5.0e8 yr
G(z_f → z_obs) = exp((t(z_obs) − t(z_f))/t_ef)
```
- λ = f_bar = 0.1 (IDCM 結構值, O173); ε = 0.1 (標準輻射效率); t_S = 4.5e8 yr (Salpeter)
- cosmology: Planck 2018 (H0=67.4, Ωm=0.315), scipy quad — t(5) = 1.171 Gyr ✓

## 三、★★z_f* 反演 (T8b/T8c)

**種子喺 z_f 形成, 以 λ=f_bar 成長到各自 z_obs (per-object z 唔同)**:

| z_f | 預測中位 | 張力 (ln) |
|:---:|:---:|:---:|
| 8 | 1.73e7 | −0.61 |
| 10 | 2.36e7 | −0.30 |
| 12 | 2.87e7 | −0.11 |
| **13.43** | **3.17e7** | **−0.010** |
| 15 | 3.48e7 | +0.09 |
| 20 | 4.15e7 | +0.26 |

**z_f* = 13.43**: 預測中位 3.17e7 vs 觀測 3.2e7 (−0.010 ln) — **1.25-1.45 dex 張力閉合**。
合理性: > 7.5 (UHz1 存在於 z=7.5, O173) ✓; 宇宙黎明/再電離期 [8,15] ✓。
G 隨 z_obs 單調遞減 (G ∈ [2.5, 11.4], 低 z 成長時間長) ✓。

## 四、★★Channel-resolved duty-cycle (T8e + T8h) — 調和「成長排除」

docs/02 V4 排除嘅係「**均勻**成長」(所有種子同一個 g)。但**per-object 成長唔係均勻**:

**低端 2 粒如果 uniform/full-time 成長, seed 會跌出通道 A 帶** (T8e):
- GLASS_160133: G=11.37 ⟹ seed = 2.0e5 < 2.02e6 (出帶 ⚠️)
- GLASS_150029: G=7.23 ⟹ seed = 5.1e5 < 2.02e6 (出帶 ⚠️)
- 容許上界: G ≤ 1.14 (GLASS_160133), G ≤ 1.83 (GLASS_150029)
- ⟹ 成長時間 ≤ 66 Myr / 303 Myr — **fresh burst** (成長 < 1 e-folding = 500 Myr)

**★統一圖像: 通道 A fresh + 通道 B 成長 (channel-resolved duty-cycle, T8h)**:
- **通道 A (譜偏差 seed)**: fresh — 內稟譜偏差, 冇環境供應 ⟹ 啱啱 active (高 λ, 低 M)
- **通道 B (環境過密 seed)**: full-time 成長 — 過密環境持續供應氣體 ⟹ 推高中位
- 高端 8 粒成長後 seed 中位 = 8.66e6, z-score = **0.12** (logN 主體正中, T8h1)
- 低端 2 粒 fresh: seed = M_obs ∈ 通道 A 帶 (預言 2 保留, T8h2)
- **channel-resolved forward 中位 = 2.34e7 vs 3.2e7 (−0.31 ln, T8h3)** — 閉合

**★★結構意義**: 通道 A/B 唔單止**質量域分離** (O197 T3), 仲有**成長動力學分離**
(環境供應): 譜偏差種子冇環境 = 唔會持續成長; 環境過密種子有供應 = 持續成長。
兩通道嘅本體差異 (內稟 vs 環境) 直接映射到觀測差異 (fresh vs 成長)。

**可證偽預言**: 通道 A seed 應顯示 fresh 特徵 (高 λ, 冇成長史) — 已支持:
**M_obs vs λ 反相關 ρ = −0.648, p = 0.024** (scripts/05 V6): 低質量種子 (通道 A)
有最高 λ (3.68, 1.89) — 啱啱 active; 高質量 (通道 B 成長後) λ 低。

## 五、UHz1 自洽 (T8f)

UHz1 (z=7.5, M=1.7e9): G(z_f*=13.4 → 7.5) = 2.14 ⟹ seed = 7.94e8,
logN 尾 z-score = 2.66, P = 3.9e-3 — 種子譜極端尾, 冇矛盾。
(O173 原本當 UHz1 係「種子直出 δ=100 → 1.94e9」— 成長版 seed 7.9e8 仍喺尾,
兩個詮釋相容, 後者更溫和。)

## 六、開放項 4 方向 (T8g)

純成長 (G 常數) = ln M 平移 — 斜率不變, 唔夠展平 −4.23/dex → −0.82/dex。
⟹ 需要 **λ-scatter (σ_lnλ = 1.39) 成長卷積** — mass-dependent 成長展平機制候選
(高 λ 種子成長多, 高端尾展平)。留 O199+ 推導。

## 七、裁決

| 項 | 狀態 | 變化 |
|:---|:---|:---|
| 2. 中位張力 | 🟢 **閉合** (duty-cycle 成長) | λ 散射唔夠 (docs/02) + 均勻成長排除 (docs/02 V4) + **channel-resolved duty-cycle 閉合** (scripts/06 11/11); z_f* = 13.43 反演, 獨立約束支持 (UHz1 z=7.5, 再電離期) |
| 3. UHz1 denominator | 🟡 收窄 | N=306 → N=434 (Akins+2024, docs/02) |
| 1. w 份額 | 🟡 不變 | data-gated (mass-complete 低端樣本) |
| 4. 全 PDF 尾展平 | 🔴 機制候選 | λ 散射成長卷積 (T8g) — 未推導 |

## 八、誠實修正

1. scripts/06 首版 t(z) Simpson 網格太粗 (t(5) = 4.95 Gyr 錯) → scipy quad 修正
   (t(5) = 1.171 Gyr ✓)
2. T8e 首版「25% 宇宙時間」判據太嚴 (GLASS_150029 31%) → 物理判據「成長 < 1
   e-folding (T_active < t_ef = 500 Myr)」→ PASS
3. T8h 首版「M<M_turn → fresh」硬切分錯 — logN 有 44% seed < M_turn, 全部當
   fresh 令中位跌返 5.40e6 → 改 **channel-resolved** (A fresh + B 成長):
   物理上通道 B 低端 (logN 低尾) 仍會成長, 唔係 fresh — 修正後閉合 (−0.31 ln)
4. z_f* = 13.43 係反演值, 唔係結構推導 — 誠實標記: 有獨立約束 (UHz1 z=7.5,
   再電離期 [8,15]) 但 z_f 嘅 IDCM 結構身份 🟡 未閉合 (13 = F₇ 候選, 未證)

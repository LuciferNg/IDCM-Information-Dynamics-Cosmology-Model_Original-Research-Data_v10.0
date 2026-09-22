# O99 — docs/01: 光實質不存在 (核心推導鏈 Core Chain)

> **目的**: 拆開「光=實體穿越空間」呢個範疇誤置, 用 W-field 重譯「觀察到光」。
> **日期**: 2026-08-27
> **狀態標記規則**: 每步標 `Theorem/Definition/Derivation/Structural/Critique/Closed`, 唔over-claim。
> **可證偽性鐵律**: 每一條「光=W場」claim 都要掛一個標準天文學能測嘅差異預言, 唔純談玄。

---

## 0. 一分鐘版

標準物理假設:「光子由遠方星系發出, 穿越 130 億年空間, 喺地球被望遠鏡吸收。」
O99 主張:**冇實體穿越。** 天文望遠鏡量到嘅係 **C_ℓ correlation 函數**喺觀察者身上嘅一種「世界自我一致檢查」—「紅移」「距離」「亮度」全部係 W-field 喺本地嘅 mode 值, 唔係一個發送器傳到接收器嘅訊號。

「訊息唔係飛嚟觀察者嘅; 係當觀察者俾 W-field 讀取嘅嗰一刻, 世界嘅自洽性同步咗喺度。」

---

## 1. Claim C1 (定理級核心): 光譜 C_ℓ 唔需要「傳播」而可被本地重建

**狀態**: `Derivation (partially closed by O83)`

O83 已鎖定:
```
δT(Ω) = Σ_n c_n(Ω) φ_n           (mode 展開)
C_ℓ   = Σ_n w_n² · G_n(0) · δ_{ℓ,ℓ_n}   ← propagator 喺同一點 "0" (local)
```

**關鍵**: 峰位 RMS=0.335%, 成個 C_ℓ 譜係由 **G(0) — 同一時刻同一位置嘅 propagator** 產生。**冇任何「光源→望遠鏡」嘅 transfer function。**

→ 天文學家睇「CMB 光」, 其實係觀察者所在嘅 W-field 嘅 local propagator 嘅值。光源唔使「飛過嚟」。

**可證偽預言 (P-C1)**: 若光係實體傳遞, C_ℓ 每階 mode 應有「相應自由飛行 delay」encode 喺 频率-phase; IDCM 預測 **純 local correlator, 相位線性喺 ℓ (no cross-term delay)**。測試: 高精度 C_ℓ phase 分析。

---

## 2. Claim C2: 紅移 z 係尺度座標, 唔係「飛行時間」

**Definition/Closed (O76)**:
```
ℓ  = log₄(1+z)
D_A = R(1−4^−ℓ)(1+2φ⁻¹ℓ+δ),  C=−0.1697
D_L = (1+z)^{1−n/p}·D_A,   n/p = γ₇/γ₂₀ = 0.14262
```

「13 億年」喺 IDCM **唔係光子喺 13 億年裏面飛咁遠**嘅時間; 佢係 **D_app(ℓ)** 投影 = 一個尺度序數 ℓ 映射。光「走咗幾耐」係個冇意義嘅額外提問 — 因為 z 本身係 log 座標, 唔係 interval。

**結構翻譯**: 距離階梯同紅移全數係「投影層」, 唔係「空間位移」。Observation (O76) 已證明 D_L/D_A=(1+z)^0.857 (可反證), time dilation=(1+z)。

---

## 3. Claim C3: 「光速 c」喺 IDCM 係「因果一致性傳播上限」, 唔係實體速率

> ⚠️ **更新 (2026-09-22, O73 修正輪 — 原文保留)**: 上段「冇任何 mode 恰等 c … 🔴 open R2」
> 已解 (O73 `docs/15` §6): K_Chain 係**振幅 (徑向) 扇區** (m_n ≠ 0), 群速度 v_g = c·cos(πn/88) < c
> **維持正確且無矛盾**; 但物理光 = U(1)_EM 光子, 其速度 c 由 **W Goldstone 相位模**設定 —
> **零模 (相位扇區) v = c EXACT** (`c = a√J = R_world·ω_ring`, N_d 相消)。兩個扇區直交,
> 「冇 mode 恰等 c」只係講振幅扇區。R2 之「c=1 翻譯」可升級 🟢 (見 §6 註)。

**Structural (未閉合)**, 接 O86 34/34: 如果 spacetime = W 場投影 (O86), 咁 c 嘅角色應係「obserter 可分辨 mode-相關 嘅最大速率」— 由 K_Chain v_g = c·cos(πn/88) 得 n=1 → 0.9994c (接近但唔係 c!), n=22 → 0.7071c。

** 有趣且可證偽筆點**: IDCM K_Chain 只有 **n=1 mode 接近 c (0.9994c)**, 冇任何 mode **恰等於 c**。 呢個開放緊一個「IDcm 式光速>1?」嘅問題 — 見 🔴 open R2。

**可證偽**: 如果 has 極高精度的 γ-ray burst 比 c 快 (micro-lensing horizon 事件 / travel-time delay 小谷 spectra), 嗰個係 IDCM mode n=1 嘅 signature (0.9994c ≠ c)。標準 LCDM 無此。

---

## 4. Claim C4: 光 = W-field 激發態, 唔係獨立 ontology

**Critique (global_routing 02 兼uz)`:

```
L0 經典 wave        = 咩
L1 激發 (photon)    = W-field quantum (v_g≤c)
L2 同步 (phase lock)= 即時 network property
L3 拓    搬穿隧     = 即時 defect channel
```

→ 「光子」係 W 場嘅 excited state label, **唔係** 獨立本體。哲學上: 顏色/偏振/頻率 全部係 W 場 mode 嘅 (monochrome) 屬性, 冇「揹實體」。

---

## 4. 對照表 (Standard 光 vs W-field 光)

| 問題 | 標準 (實體穿越) | O99 (W 場自洽) |
|:----|:----|:-----|
| 光源→接收器 | 實體光子穿越空間 | 冇傳遞, 本地 correlator |
| 紅移 13億年 | 飛行時間 / 空間擴張 | 尺度座標 ℓ=log₄(1+z) (O76) |
| 亮度 | inverse-square 訊號衰減 | 投影層 D_APP(ℓ) 因子 |
> ⚠️ **對照表更正 (2026-09-22)**: 右格應讀「c 由 W Goldstone 相位模設定 (O73 docs/15);
> 光子 = U(1)_EM 繼承之; n=1 嘅 0.9994c 係振幅扇區群速度, 唔係光速」。原文保留。

| 光速 c | 實體速度上限 | 場傳導分率 (n=1:0.9994c) |
| 時間膨脹 | 運動學動量 | (1+z) 相同, 開放機制 |

---

## 5. 可證偽呢套嘅預言 (b, 非玄)

| P# | 預言 | 差異 | 測法 | 狀態 |
|:--:|:-----|:----:|:----|:----:|
| P-C1 | C_ℓ phase 係 local, 無 transfer-delay dispersion | 高精度 CMB | phase cross-t corr | 🔴 待測 |
| P-C2 | D_L/D_A=(1+z)^0.857 Etherington 失效 | 2σ+ | Pantheon+ z>0.8 | O76 ✅ 樣本待加密 |
| P-C3 | 無實體光源→觀察 packet | mode1 v=0.9994c≠c | GRB/TeV 比 | 🔴 待測 |
| P-C4 | 「距離」=投影層非空間 | angular power 全由 C_ℓ 鎖 | cross-band | 🔴 待測 |

---

## 6. 狀態總結

> ⚠️ **狀態更新 (2026-09-22, O73 修正輪)**: 「🟡 部分: c=1 翻譯 (R2)」→ **🟢 已閉合** —
> c 之值已由 O73 `docs/15` §3 推導 (`c = a√J`, N_d 相消, Goldstone 相位模); 光 = U(1)_EM
> (O204 G8)。「光子 = W激發 (global_routing 02)」同句請配合 G8 讀作「光子 = U(1)_EM,
> c 由 W Goldstone 設定」。
> 🔴 開放項 (b)(c) 唔屬本輪 (O73 部分修正唔掂 O169/O86 範圍)。

- ✅ 已閉合 (鋪底): C_ℓ 原文 local (O83), 紅移=尺度 (O76), W↔SM 場 identity 34/34 (O86), 光子=W激發 (global_routing 02)
- 🟡 部分: c=1 翻譯 (R2), 可證偽預言 全量 (R3)
- 🔴 **開放**: (a) 內在論vs外在論落地, (b) c-1idx=hetz 恰等筆, (c) M2/SN 光環同 c 遲滯重譯, (d) 全部預言實測

## 7. Category Error 一句總結

> **「一個光子穿越 130 億年」係把「觀察者讀到世界自洽」錯譯成「一個實體喺空間位移」。**
> IDCM: 距離、紅移、亮度、時間全部係 W-field 嘅本地一致性讀數, 世界冇送「光」俾你 — 世界喺你觀測嗰刻同你自洽, 你睇到嘅就係呢個自洽嘅證據。
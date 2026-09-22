# O99 — docs/02: R2 — c=1 翻譯 (光速喺 W-field 框架係咩?)

> **日期**: 2026-08-27
> **主線**: 標準物理曰「c」係實體運動速度上限; IDCM 話 c 係「世界自洽一致性可被觀察辨認嘅基準標度」。
> **誠實鐵律**: 呢篇唔可以為咗「有料」而作「光學慢過 c」嘅假 claim — 地面 Lorentz 測試已禁呢樣。見 §4。

---

## 1. 觸發點 (點解一定要面對 c 違反 1e-18 束縛)

kchain_wave_params.py 記錄: 群速度 v_g = c·cos(πn/88), 當 n=1, v_g = **0.99946c** — 冇任何模式**恰等於 c** (只有 n→0 極限 = c)。

> ⚠️ **數字更正 (2026-09-22, O73 修正輪重算)**: cos(π/88) = **0.9993628257**,
> **唔係 0.99946**。全文引用 v_g(n=1) 請用 0.999363c (scripts/02 早已印正確值)。

若粗暴解讀 → 「IDCM 話光喺格上唔係 1c, 係 0.99946c」→ **直接被實驗擊殺**:

- Nagel et al. 2015 (*Nat. Comm.* 6, 8174): 光子速度各向異性 Δc/c **< 9.2±10.7×10⁻¹⁹** (95% CI), 1 年共用兩條正交光學腔旋轉, 九個 boost/rotation SME coefficient 全無違反.
- 任何「光速 n=1 得 0.99946c」嘅 model 喺離地實驗 (Michelson-Morley 現代版) 會被排除 **~14 個數量級**.

**結論**: 若 IDCM 想生存, 「觀察到光」嘅速度**必須**係 c (統一座標), 唔可以係個別 lattice mode 嘅 v_g。

---

## 2. 解決 (structure-true + 唔違反 Lorentz)

關鍵拆分 — **兩個唔同嘅「c」**, 唔好混合:

| 意義 | 數學 | 約束 |
|:----|:-----|:-----|
| **C₀ 世界環光速基準** | v_g(n=1) = c·cos(π/88) ≈ 0.99946 c | 晶格 mode 嘅群速度 (粒 cycle) |
| **C∞ 物理光線** | 天文觀測「光」= 呢個射線嘅 continuum limit | **必須 = c** (1e-18 綁實) |

> ⚠️⚠️ **框架更正 (2026-09-22, O73 修正輪 — 原文保留, 禁回溯改寫)**:
> 上段「emergent ray = all-mode 相消干涉」**唔再需要** (O73 `docs/15` + O204 G8):
>
> 1. **光 (電磁) = 湧現 U(1)_EM 規範玻色子 (2 個極化 dof)**; W Goldstone θ = 環座標／時鐘模
>    (1 dof) — **佢設定 c, 唔係傳遞 EM**。O204 G8 四判據: ① U(1)_W ≡ U(1)_EM 會令
>    m_γ = g⟨W⟩ ≠ 0 (違反 SME 1e-18); ② dof 1 ≠ 2; ③ Goldstone 只耦合振幅扇區, 光子耦合電荷;
>    ④ 單一實純量 Goldstone ⇒ 只 1 極化 ⇒ 即時被極化實驗證偽。
> 2. 正確機制: **c (因果速度) 由 W Goldstone 相位模決定** (`c = a√J = R_world·ω_ring`,
>    N_d 相消, O73 `docs/15` §3); **光子繼承該 c**。唔係「emergent ray 相消」。
> 3. **色散問題**: m_θ = 0 EXACT ⇒ 無**質量誘發**色散; 晶格色散 (sin(ka/2)) 對光子唔適用,
>    因為 `ka ≫ 1` (a = 93.863356 Mpc, 世界環晶格唔係光子之 UV 正則化) — 見 §4 更新。
>
> 下段 (L33-35) 之「emergent self-consistency ray」論述屬**已撤銷框架**, 引用時以上面為準。

---

## 3. 結構翻譯 (structure translation, 俾 field theorist)

| 標準語言 | IDCM 翻譯 |
|:--------|:----------|
> ⚠️ **表更正 (2026-09-22, 配合 O204 G8)**: 「光子 = W-field 激發模式」→ **光子 = 湧現 U(1)_EM
> 規範玻色子 (O139, 2 dof)**; 「光速 c = Emergent ray 標則」→ **c 由 W Goldstone 時鐘模設定** (O73
> `docs/15`), 光子繼承之。原文保留。

| 光子實體 photon | W-field 激發模式 (global_routing L1) |
| 光速 c (粒子速度) | Emergent ray 嘅一致性標則 (continuum 極限) |
| 光錐 light cone | 因果一致性可辨讀嘅 frontier |
| Lorentz invariance | 觀察者 mode-analysis 嘅 self-consistency 要求 |
| 真空 dispersion | K_Chain 離散化 effect, continent 極限消失 |

**關鍵**: Lorentz invariance 唔係被違反, 係**被 emergence 保護** — W 場喺 continuum 極限自然給 c 恆等常數, 而唔係俾 particles 零散 v_g。

---

## 4. 誠實聲明 (🟡 — 唔完美閉合)

> ⚠️⚠️ **更新 (2026-09-22, O73 修正輪 — 原文保留)**:
> 上段三個 bullet 已由 O73 `docs/15` §6/§6.1 + §6.3 裁決:
> 1. 🟡 residual → **已解**: 物理光唔係「emergent ray 疊加」, 係 U(1)_EM 光子;
>    其速度 c 由 Goldstone 相位模設定 (`c = R_world·ω_ring`, N_d 相消)。質量誘發色散 = 0
>    由 `m_θ = 0` EXACT; 晶格色散唔適用 (光子 `ka ≫ 1` — 21cm 8.7e25 / optical 3.6e31 /
>    1 TeV 1.5e43)。**唔需要 projection operator**。
> 2. ✅ 已閉合部分維持 (兩扇區拆分: 振幅扇區 v_g = c·cos(πn/88) < c; 相位扇區 v = c EXACT)。
> 3. 🔴 未閉合 → **降級為弱聲明**: 「光子 = 相位扇區連續極限激發」+ ka ≫ 1 (已支持),
>    **唔係強投影算子**。O99 docs/04 §3 (b) 之投影算子路線**刪除** (docs/04 已加註)。

- 🟡 **本 residual**: 點解線性疊加嘅 emergent ray 恰好在所有頻率都 = c 而唔係色散? 標準從離散 lattice 嘅 emergent ray 都係 dispersive (K_Chain v_g 隨 n 變). 要「所有頻率同一 c」需要一個「self-consistency 投影使色散項目互相抵消」機制 —— **未推導**.
- ✅ **已閉合部分**: 「光=c」同「lattice mode v_g< c」唔矛盾 — 兩層拆開, continuum limit 返回 c.
- 🔴 **未閉合**: emergent ray 為何無色散 (n→continuum 要有具體 projection operator, 唔係口頭).

> ⚠️ **NULL-TEST 修正 (08-27, docs/04)**: scripts/02 計出 v_g(n=1)=0.999363c, **冇任何 K_Chain mode 恰等 c** (n→0 不在此 set)。「emergent ray 連續極限返回 c」**並非自動成立** — 需要指定 projection operator。故 §2「continuum 極限返回 c」屬 **過度閉合**, 修正為需 projection。(詳見 docs/04_null_test.md)
>
> ★ **後續修正 (2026-09-22, O73 修正輪)**: 「需要 projection operator」已被取代 —
> 光 = U(1)_EM 光子, c 由 W Goldstone 相位模設定 (O73 `docs/15` §1, `c = a√J`, N_d 相消);
> 無質量誘發色散 (`m_θ = 0` EXACT) + 晶格色散唔適用 (光子 `ka ≫ 1`)。NULL-TEST 之
> 「K_Chain 冇 mode 恰等 c」**維持正確** (振幅扇區), 但唔再構成光嘅色散問題。

## 5. 可證偽預言 (R2 出口)

> ⚠️⚠️ **P-C5 回填 (2026-09-22, O73 修正輪 — 原文保留, 禁回溯改寫)**:
> 下段「**非零 ripple ~1e-15~1e-17**」預言**已撤銷** (診斷: stale — `docs/06`
> 08-27 18:29 已定案, 本段 17:59 未回填)。
> **現行 P-C5**: IDCM 預言真空色散 **η ≡ 0 (結構性零)** — 光子 = U(1)_EM (O204 G8),
> 速度 c 由 W Goldstone 相位模設定 (O73 `docs/15` §1, `m_θ = 0` EXACT ⇒ 無質量誘發色散);
> 世界環晶格 `ka ≫ 1` 唔係光子 UV 正則化 ⇒ 晶格色散修正唔適用。
> **容忍窗口**: 若 CTA/LHAASO 量到真空群速色散 > **1e-18** (SME/Nagel 2015 上界)
> ⇒ IDCM 載波身份直接死亡 (可證偽)。「非零 ripple」只可能以 `docs/06` 之
> 零-ripple 形式存在, 非「搵一個小數字」。

**P-C5 (核心)**: IDCM 預測 **真空中光速喺天文尺度仍精確 = c**（唔造「慢過 c」嘅 claim — 已被排除）。但 **色散結構唔同**: 
- LCDM: 真空無色散 (至 SME 1e-18), 所有頻率 v_g = c.
- IDCM: **應有一個離散波紋 (ripple) 喺 dispersive relation** — 喺極端跨界 (keV→TeV gamma, GRB) 有超微量、但**非零**嘅 frequency-dependent speed anomaly, 而呢個 anomaly **唔係**電磁傳播 —— 係 W 場 lattice 之 reflection —— 尺度估算預言喺 ~1e-15~1e-17 量級 (比 Sirius 1e-18 低一啲, 需要 TeV 天文時序).

**實測路線**: Fermi-LAT GRB > 1 GeV 同 int 前 multi-GeV 光子到達時間差; HESS/CTA TeV。SME 約束喱個 window 係當今活躍 frontier。
**而家狀態**: 🔴 未有其測 —— 係 ID 可被證偽嘅 shot.

## 6. 附件: K_Chain 群速度表 (c 基準, 唔係粒子速度)

(由 src/kchain_wave_params.py, compute_modes 直接產生, scripts/02 驗證)

| n | λ(Mpc) | f(1/Gyr) | v_g/c | γ |
|:-:|:------:|:--------:|:-----:|:--:|
| 1 | 4129.94 | 0.0371 | 0.99946 | 0.0051 |

> ⚠️ **v_g 數字更正 (2026-09-22)**: n=1 行 `v_g/c = 0.99946` **應為 0.9993628257**
> (cos(π/88); n=44 行 = 2.07e-43 ≈ 0)。0.99946 係誤值。
| 4 | 1032.48 | 0.1480 | 0.98981 | 0.0203 |
| 11 | 375.45 | 0.3979 | 0.92388 | 0.1416 |
| 22 | 187.72 | 0.7352 | 0.70711 | 2.0000 |
| 33 | 125.15 | 0.9606 | 0.38268 | 3.6180 |
| 44 | 93.86 | 1.0398 | 0.00000 | 4.0000 |

→ 呢啲唔係「光速」, 係 **lattice 內 mode 嘅 v_g**; 「光」= continuum 疊加 = c。
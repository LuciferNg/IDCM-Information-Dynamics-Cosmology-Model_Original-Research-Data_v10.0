# O99 — SESSION START

> **Session**: 2026-08-27 (新開)
> **狀態**: 🔴 已註冊 — 侍攻堅
> **鏈接**: physics-foundations-critique-paper skill

---

## 定位

批判並證明「光」實質不存在 — 冇 photon/EM 實體穿越 130 億年; 只有 W-field 因果互證 + 自洽性檢查。

## 待攻堅 (本 session 開始)

- docs/01_core_chain.md — 把本體論型當口述問題寫成 status-marked 推導鏈 + 對照表
- scripts/01_lightcone_translate.py — 用 O83 correlator 證明 C_ℓ 唔需要 transport (局部讀場
- 之後: R2 光速上限翻譯, R3 可證偽預言, R5 觀察者讀取

## 相關資源

```
- physics-foundations-critique-paper (skill)
- o76_z_redshift_translation (z=log₄ℓ 距離)
- o83_correlator_cmb (C_ℓ = 遙centre local state)
- o86_sm_gr_coupling (W↔spacetime)
- global_routing_table/docs/02 (photon = W 激發)
```

## 簡單限制

- 「光不存在」必須破 O「形而上學」批判: 每個分點都要有「可證偽對應預言」, 唔純談玄。
- 唔好過度聲稱 (無「已證」): 按 skill 用 Definition/Derivation/Structural/Critique 標記。

---

## ⚠️ O169 修正點 (2026-09-15) — 待本 O 重驗

**修正點** (上游 O169):

- 伸長定律 `E = 1 + 2φ⁻¹ℓ` **已證偽** (DESI DR2 D_M×6 排除 4.88σ) → `E(ℓ) = ℓ + 1.11911398` (= ⟨γ⟩_odd/2·ℓ + 1/⟨v_g⟩_{1..22}); `δ(ℓ) = −φ⁻³(ℓ−1/2)`, `C = 1−2φ⁻¹ = −(√5−2)`

**問題** (本 O 受影響點):

- `docs/01_core_chain.md:42`, `docs/07_r4_projection_layer.md:19`
- `scripts/05_r4_projection_layer.py:22,31,57`, `scripts/06_falsification.py:24`, `scripts/09_layer_lensing.py:29`
- ★ `scripts/05:57` 嘅 check「D_app 含投影伸長 (1+2φ⁻¹ℓ) — 結構定義, 唔係 bug」 — 呢個 check 會鎖死已證偽公式 → 必須更新, 否則 falsification 測試會保護錯嘅公式

- **狀態**: [ ] 未重驗
> 只加註, 未改本 O 結論檔 (01_problem_record.md / docs/ / final_result.md); 重驗後由本 O 自行寫入。

---

## ★★ 上游 O73 §10 修正點 (2026-09-18) — 待本 O 修改

> **來源**: O73 `docs/15_c_first_principles.md` + `scripts/24_c_first_principles.py` (commit `033f105`)
> **用戶指示**: O73 側**未改動 O99 任何檔案** (依「無指示下禁寫入本條目以外」紀律);
> 現由本節列明**問題 + 修正點**, 要求 O99 session 自行執行修改。
> **狀態**: [ ] 未修改

### 〇. 一句話

O73 §10 由 **W-field SSB 第一性原理**導出: **光 = W-field 相位 (Goldstone) 模**,
`m_θ = 0 EXACT`; 並導出 `c = a·√J` 而 `a = R_world/N_d`, `√J = N_d·ω_ring`
⇒ **N_d 精確相消** ⇒ `c = R_world·ω_ring = 2πR_world/T_ring = L_ring/T_ring` EXACT (零自由參數)。

⇒ 本 O 之「載波 (carrier)」postulate 現有**推導來源**; 本 O 遺留之 🔴「emergent ray 為何無色散」
需求**由強降為弱** (見 §三)。但同時暴露本 O **一處內部矛盾** (見 §二, ★ 需裁決)。

---

### 一. 需要修正嘅檔案 (逐項)

#### A. `docs/02_c_identity.md`

| 行 | 現狀 | 修正方向 |
|:--|:-----|:---------|
| L31, L35 | 「emergent ray = **all-mode 相消干涉** 嘅疊加」為光之機制 | ★ **框架應換**: 光 = W-field SSB 之**相位 (Goldstone) 扇區**, 唔係振幅模之相消疊加。相消論證 (需指定投影算子令色散 cancel) 唔再需要 — 兩個扇區直交 |
| L55 | 🟡 residual: 「點解線性疊加嘅 emergent ray 恰在所有頻率 = c 而唔係色散? … **未推導**」 | 更新: ① **質量誘發色散 = 0** 由 `m_θ = 0` EXACT (Goldstone) ✓; ② 晶格色散**唔適用** (光子 `ka >> 1`, 見 §三) |
| L57 | 🔴 「未閉合: emergent ray 為何無色散 (**n→continuum 要有具體 projection operator**)」 | ★ **降級**: 唔需要 projection operator。改為需「光子 = 相位扇區之連續極限激發」之聲明 (弱, 且 `ka >> 1` 已支持) |
| L59 | NULL-TEST 修正註 (保留) | 保留原文 + 加指向 O73 `docs/15` §6/§6.1 之註 |
| L63–68 | ★★ **P-C5**: 「IDCM 應有一個離散波紋 (ripple) … ~1e-15~1e-17 量級」 | ★ **需重審 — 見 §二 內部矛盾** |
| L68 | 「而家狀態: 🔴 未有其測」 | 與 `01_problem_record.md`「P-C5 … LHAASO 100% 契合 🟢」矛盾 → 需統一 |

#### B. `docs/04_null_test.md`

| 節 | 現狀 | 修正方向 |
|:--|:-----|:---------|
| §3 (a)(b)(c) | 三選一「**尚未定**」 | ★ **現可定**: 主體係 (c) 之精確版 — `v_g = c·cos(πn/88)` 係**振幅 (徑向) 扇區**之群速度, 物理光喺**相位扇區**。但唔係「數學數值 vs 物理」之模糊講法, 而係兩個 sector |
| §3 (b) | 「需一個具體 W-field projection operator, **令色散喺所有頻率 cancel**」 | ★ **呢條路係錯嘅** — 唔需要 cancel。應改為「光子 = 相位扇區連續極限激發」 |
| §4 ⚠️ | 「實情係『光=c』仲係要 **axiom** (冇 projected operator 會導致色散), 唔係 derive」 | 更新: `c` 之**值**已由 O73 `docs/15` §3 推導 (N_d 相消); `m_γ = 0` EXACT; 「零色散」仍需**弱聲明** (唔係全盤 axiom) |
| §6 金句 | 「要真 c, 要推 **W-projector**, 唔係口吟」 | ★ 已達成, **但唔係靠 projector** — 靠 Goldstone 扇區 + 連續極限。金句需修 |

#### C. `docs/05_oa_carrier_projection.md`

| 節 | 現狀 | 修正方向 |
|:--|:-----|:---------|
| §2 | `c_phase(ring) = 2πR_world/T_ring = ω_ring × R_world = c` (恆等) | 呢個係 **identity**, 唔係推導。現由 O73 `docs/15` §1–3 由 W-field SSB **導出** ⇒ 由 postulate 升級為 derivation, 應更新引用 |
| §3 | `H_carrier: 世界環 translational mode (n=0, ω=0, 相速度=c)` — ★ 呢個係 **postulate** | ★ 現可**識別**為 **W-field Goldstone 相位模** (SSB 之後果), 唔需另立載波 sector。`P̂` 之必要性下降 |
| §5 Status | 「🔴 剩: **P-C5 ripple 之數量級未閉合 (需投影權重)**」 | ★ 需重審 — 見 §二 矛盾; O73 立場: 若光 = 無質量 Goldstone, 真空色散 = 0, **ripple 唔應該存在** |
| §5 | ★ **標題重複** (`## 5. Status` 之後又一個 `## 5. 一致性`) | 格式 bug — 後者應為 `## 6.` |

#### C2. `docs/06_pc5_tev_ripple.md` (★ 已有正確版本, 作為回填之基準)

| 節 | 現狀 | 修正方向 |
|:--|:-----|:---------|
| §1 | 「光子 = 世界環**載波** (carrier), 相速度 v_ph = c (dev=0, **構造身份**)」 | ★ 「構造身份 (postulate)」現有推導來源: 由 O73 `docs/15` §1 導出為 W-field **Goldstone 相位模** ⇒ 引用更新 |
| §5 | 「🔴 若 future 發現真空色散 >1e-18 → 唔一定殺 O99 (可以 carrier 有微 ripple)」 | 可收緊: 若光 = 無質量 Goldstone, 真空色散應為**結構性零** (非「可容微 ripple」) |
| §2/§3/§6 | 零-ripple 預言 + 容忍窗口 1e-18 | ✅ **正確, 保留** — 此為 `docs/02` §5 / `docs/03` P-C5 應回填之目標形式 |

#### D. `docs/01_core_chain.md`

| 行 | 現狀 | 修正方向 |
|:--|:-----|:---------|
| L56 | 「K_Chain 只有 n=1 mode 接近 c (0.9994c), 冇任何 mode 恰等於 c … 見 🔴 open R2」 | 更新: **零模 = 相位 (Goldstone) 模**, `v = c` EXACT (O73 `docs/15`); 振幅模 `v_g < c` 係正確且**無矛盾** (兩個扇區) |
| L103 | 「🟡 部分: c=1 翻譯 (R2)」 | 可升級 (c 之值已推導) |
| L93–96 | P-C1/C3/C4 標 🔴 待測 | 保留 (預言待測, 與本修正無關) |

#### E. `01_problem_record.md`

| 項 | 現狀 | 修正方向 |
|:--|:-----|:---------|
| 狀態行 | 「🟢 ★★★ 全鏈閉合 — 6 項剩餘問題全部解決」 | ★ **與內文不一致** (同 §二 之 stale 診斷): `docs/02` §4 (🟡+🔴)、`docs/04` §3 (「尚未定」)、`docs/05` §5 (🔴) 仍載**舊開放標記**未回填 ⇒ 應收斂為 🟢 並補推導引用 (O73 `docs/15`), 非裁決 |
| 表 #5 | 「P-C5 (LHAASO 零色散) … d v_g/dE ≡ 0 … **100% 契合** 🟢」 | 結論方向正確, 但**機制陳述**為 postulate; 現可引 O73 `docs/15` |
| 速查表 | 「✅ 光=c = 世界環載波相速度 (H=H_carrier⊕H_mod) 🟢」 | ★ 實為 **postulate**, 現由 O73 `docs/15` 提供 derivation ⇒ 引用更新 |
| 速查表 | 「✅ 載波 ripple ≡ 0 (零色散, LHAASO 確認) 🟢」 | ★ **與 `docs/02` §5 P-C5「應有 1e-15~1e-17 ripple」直接矛盾** → 見 §二 |

#### F. `scripts/`

| 檔案 | 現狀 | 修正方向 |
|:-----|:-----|:---------|
| `02_R2_R3_check.py` | 結論「需 projection operator; 預測存在性唔係值」 | 更新結論 (唔需 projection operator) |
| `03_emergent_c_projection.py` | `P̂` 定義: `H_carrier` 為 postulate | 對應更新 (識別為 Goldstone 相位模) |
| `03_emergent_c_projection.py:89` | ★ **hardcoded 舊 repo 路徑** `/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o99_light_ontology/data/...` | ★ **獨立 bug** — repo 已搬遷至 `~/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/`。會寫錯位置或 crash。建議改用 `os.path.dirname(os.path.abspath(__file__))` 相對路徑 |

---

### 二. ★★ P-C5 陳述分歧 — 診斷為「stale 未同步」(唔係真矛盾)

**三份文檔對 P-C5 之陳述**:

```
docs/02_c_identity.md §5 (L63-68)     : P-C5 = IDCM「應有」離散 ripple ~1e-15~1e-17 (非零 freq-dep)
docs/03_falsifiable_predictions.md L17 : P-C5 = 「離散 dispersive ripple 1e-15~1e-17」 🔴 待測
docs/06_pc5_tev_ripple.md (08-27 18:29): P-C5 = **「零 ripple (η ≡ 0)」+ 容忍窗口 1e-18** 🟢
01_problem_record.md 表 #5 + 速查表      : 「ripple ≡ 0 … LHAASO 100% 契合」🟢
```

**★ 診斷 (O73 側觀察)**: 呢個唔係未裁決之矛盾, 而係 **stale 未同步**:

- `docs/06` (時間戳 08-27 **18:29**, 最晚) 已**明確推翻** docs/02 §5 之「非零 ripple」假設, 原文:
  > 「原本 P-C5 假設: 光喺 K_Chain lattice 上行有個 ~1e-3 數量級嘅 dispersive ripple … → 呢個係 naive lattice 色散聲稱, 已被 docs/04 null 拒 … **O99-A 閉合後, P-C5 嘅正確形式變咗: 光子 = 世界環載波, 相速度 v_ph = c (dev=0)。載波自身嘅 dispersive ripple ≡ 0。**」
- 但 `docs/02` (08-27 **17:59**) 同 `docs/03` (08-27 **17:57**) **早於** docs/06 且**從未回填** ⇒ 兩份仍載舊「非零 ripple」陳述。
- `01_problem_record.md` (08-29) 及 `docs/06` 之結論 (**ripple ≡ 0**) 一致。

**⇒ 修正方向明確 (唔需裁決)**: 把 `docs/02` §5 + `docs/03` P-C5 **回填至 docs/06 之「零 ripple」形式**
(加日期註記, 保留原文, 依禁回溯紀律)。O73 `docs/15` §1 現提供該形式之**推導來源**
(`m_γ = 0` EXACT, Goldstone), 取代 docs/06 §1 之「構造身份 (postulate)」。

**O73 側之技術輸入 (支持 ripple ≡ 0, 非裁決本身)**:

```
(1) 若光 = 無質量 Goldstone 相位模 (O73 docs/15 §1):
      m_γ = 0 EXACT  =>  真空無「質量誘發色散」  =>  ripple 應為 0
    => 支持 01_problem_record 之結論 (ripple ≡ 0)
    => docs/02 §5 + docs/03 P-C5 之「非零 ripple」預言 應撤銷或重寫

(2) 但「零色散」仍需「光子 = 相位扇區連續極限」之聲明 (O73 docs/15 §6.1):
      世界環晶格 a = 93.863356 Mpc; 光子 ka >> 1 (21cm: 8.7e25; optical: 3.6e31; 1TeV: 1.5e40)
      => 世界環晶格完全唔係光子之 UV 正則化 => 晶格色散修正唔適用 (唔係「小量」)
    => 呢個係 O73 提供之**新技術支撐** (支持 ripple = 0), 但唔構成完整證明

(3) 舊 docs/02 §5 之 ripple 量級 1e-15~1e-17 源自 K_chain 振幅模 v_g 隨 n 變
    — 但振幅模唔係光 (唔同扇區) => 該估算之物理對象錯
```

**⇒ 建議裁決方向 (待 O99 自行決定)**: 撤銷「非零 ripple」預言, 統一為
「**真空色散 = 0 (結構性)**, 檢定 = SME/LHAASO 上界」; `docs/02` §5 與 `docs/03` P-C5 需重寫,
`01_problem_record` 之 🟢 保留但補上推導引用 (O73 `docs/15`)。

---

### 三. O73 側之精確貢獻與界限 (誠實邊界)

**✅ 提供 (可引用)**:

| 項 | 內容 | 位置 |
|:---|:-----|:-----|
| c 之值 | `c = R_world·ω_ring` (N_d 相消, 零自由參數) | O73 `docs/15` §3 |
| 光之本體論身份 | W-field **Goldstone 相位模** (SSB 後果, 非 postulate) | O73 `docs/15` §1 |
| 質量 | `m_γ = 0` **EXACT** | O73 `docs/15` §1 |
| 扇區拆分 | 相位 (m=0, v=c) vs 振幅 (m_n = M₀√γ_n, v_g = c·cos(πn/88) < c) | O73 `docs/15` §6 |
| 細化不變 | `c_ℓ = c ∀ℓ` (Z_(88·4^ℓ)) | O73 `docs/15` §5 |
| 晶格色散唔適用 | 光子 `ka >> 1` (a = 93.863356 Mpc) | O73 `docs/15` §6.1 |
| 新常數 | `τ_hop = 1/(N_d·ω_ring) = 0.30554861 Gyr` | O73 `docs/15` §3.1 |

**🔴 唔提供 (唔可宣稱)**:

1. 「所有頻率零色散」**唔係**由 Goldstone 條件單獨導出 —— 晶格 Goldstone 模仍有 `ω = 2√J|sin(ka/2)|`;
   需要「光子 = 相位扇區**連續極限**激發」之聲明 (弱需求, 非強投影算子)。
2. `c` 之**絕對值**仍需 **1 個有量綱錨** (維度定理: `D(c) ≠ 0`, 結構常數全無量綱);
   世界環 sector dof = 4 − 3 = 1。主導不確定度 = `ω_ring` 之 0.19% (BBN), 非結構。
3. O73 **未改動 O99 任何檔案** — 本節僅列問題與修正點。

---

### 四. 建議執行順序 (供 O99 session 參考)

```
1. ★ 依 §二 診斷: P-C5 唔需裁決 — 直接以 `docs/06` (零 ripple, 08-27 18:29 已定) 為基準回填 docs/02 §5 + docs/03
2. docs/02 §4/§5 重寫 (emergent-ray → Goldstone 扇區; P-C5 依裁決)
3. docs/04 §3 定案 (a/b/c 三選一 → (c) 之精確版; 刪 (b) 之投影算子路線) + §6 金句修
4. docs/05 §2/§3/§5 更新 (postulate → derivation; P̂ 必要性下降) + §5 標題重複修正
5. docs/01 L56/L103 更新
6. 01_problem_record 狀態行 + 速查表 + 表 #5 補引用 (解內部不一致)
7. scripts/02 結論更新; scripts/03 P̂ 更新; ★ scripts/03:89 舊路徑 bug 修正
8. 全部重跑 + 記錄時序 (禁回溯改寫; 加日期註記)
```

---

### 五. 上游 O169 修正點 (2026-09-15) — 仍待本 O 重驗

（見本檔上方 §「⚠️ O169 修正點 (2026-09-15)」— 狀態 [ ] 未重驗, 內容不變）



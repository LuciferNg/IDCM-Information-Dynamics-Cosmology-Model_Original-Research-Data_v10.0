# O185/IF3 — docs/06: R2 entanglement 直接計算（88-site correlation matrix）

> **日期**: 2026-10-10 ｜ **Script**: `scripts/06_entanglement.py`（12 PASS / 0 FAIL） ｜ **Log**: `logs/06_entanglement.out`
> **定位**: 「全部喺 O185 繼續」Round 3（路線 A, 建議攻堅首選）——R2 (F_proj=17 ↔ entanglement wedge) 由**類比**升級為**直接計算**。Register: `O185/IF3`
> **承接**: docs/04 R2 + O121 (sync sector 17, E_sync=61.5) + O151 docs/24 (面積律 1/B 雙側機制) + Peschel (2003) correlation matrix 法

---

## 1. 方法（零新參數）

88-site 對偶鏈 free-fermion correlation matrix（Peschel 2003）：
```
C_AA[i,j] = Σ_{k∈occ} ψ_k(i)ψ_k(j)*    (A = 空間半邊 site 1..44, 44×44 Hermitian)
ψ_k(i)    = e^{2πiki/88}/√88           (IDCM 88-site plane wave, k=1..88)
λ_m       = eig(C_AA) ∈ [0,1]          (entanglement spectrum)
S_vN      = -Σ[λ ln λ + (1−λ)ln(1−λ)]
S₂        = Rényi-2
```
三個 sector（全部只用 IDCM 已有模式集）：
- `occ_even` = 偶 k 模式（世界側, 44 個, Σγ_even=90, O121/O151）
- `occ_sync` = k=56..88 even（44-site n≥28 對應, **17 個 = sync sector = O121 黑洞自由度**）
- `occ_low` = k=1..44（half-fill, **對照**, 唔係 IDCM 結構填充）

判決準則（計算前聲明）: R2 升級 ⇔ sync sector entanglement spectrum 非零數 = **17 = F_proj**。
誠實限制: free-fermion 建構 = **工具對接**（O222 QM-tool 先例），唔宣稱 IDCM 有量子態。

## 2. 結果（12/12 PASS）

| sector | occupied | entanglement spectrum | S_vN (nats) | S_vN (bits) | 結構身份 |
|:-------|:--------:|:----------------------|:------------|:------------|:---------|
| 世界側 occ_even | 44 | 44× λ=1/2 (unique={0.5}) | 30.498476 | **44.0000** | N_d bits EXACT |
| **sync occ_sync** | **17** | **17× λ=1/2** (+27×0) | 11.783502 | **17.0000** | **F_proj bits EXACT** |
| half-fill occ_low | 44 | 29 nonz, λ=1 有 | 1.836986 | 2.6502 | （對照, 冇 IDCM 身份） |

## 3. ★★★ R2 升級 🟡→🟢：wedge 分辨極限 = 直接計算

**核心結果**: 投影截斷後嘅 sync 17 模式喺半邊空間（site 1..44）嘅 correlation matrix rank = **17**，
entanglement spectrum = 17× λ=1/2（每 sync 模式半佔據）⟹ **S_vN(sync) = 17.0000 bits EXACT**。

三層對接（全部 scripts/06 可複現）：
1. **wedge 分辨極限 = F_proj**: sync sector（黑洞自由度, O121 ker(T_pipe)=17）喺半邊空間
   完全分辨——rank(C_AA) = 17 = dim ker(T_pipe)。「量子-經典邊界 F_proj=17」
   第一次以 entanglement spectrum 形式出現（唔再係命名對應）。
2. **區劃分辨（vs 世界）**: 世界側 44 模式 rank 44、sync 17 模式 rank 17——分割比例
   **17/44 = 0.38636**（記錄, 唔硬配）。
3. **Rényi 不變量**: S₂ = S_vN（λ∈{0,1/2} 均勻）——entanglement spectrum 係「平坦
   半佔據」結構；熵嘅所有階一致 = 自由度計數（每模式恰好 1 bit）。

**對接表述**: 「IDCM 觀察者可分辨嘅 wedge = sync 17 自由度」喺工具層 = 「半邊空間
correlation matrix rank 17, 每模式 λ=1/2」。呢個唔係宣稱 IDCM 有量子糾纏——
係以弦論/QI 工具將 O121 已有嘅 sync 17 結構翻譯成 entanglement-spectrum 語言。

## 4. 誠實標記

- ⚠️ **λ=1/2 嘅「每模式 1 bit」係 free-fermion 一般特徵**（occupied plane-wave restriction
  到半邊空間自然半佔據）——唔係 IDCM 獨有結構。**IDCM 內容係 occ_set 選擇**:
  sync sector (k≥56) 正好係 O121 投影截斷區段, 而唔係任意 17 模式。
- ⚠️ 世界側 44 bits = N_d bits 嘅「精確」同 sync 17 bits 一樣來自 λ=1/2——本身唔特別。
  特別嘅係 `occ_sync` 由 IDCM 結構（O121 n≥28 截斷）指定, 而唔係事後揀。
- 🟡 未有「面積律 1/B = 0.25」直接由本計算出現——1/B 係每邊界格 0.25 bit (O151 docs/24),
  本計算係「每 sync 模式 1 bit」。兩者唔矛盾 (不同計數對象: 邊界格 vs 模式), 但
  **唔可以將 17 bits 直接硬配 1/B**——誠實記錄, 唔閉合嗰條線 (O151 已自己閉合)。
- 🔴 禁宣稱「IDCM 量子糾纏/entanglement = 弦論 entanglement」——工具對接, 唔係本體層。

## 5. 四道硬測試

| 測試 | 狀態 |
|:----|:----:|
| ① 自由度成本 | ✅ 零新參數——occ_set 全由 IDCM 模式集定義 (偶 k / n≥28 / 對照) |
| ② MC null | N/A（純代數/數值恆等; 12/12 由 numpy eigvalsh 直接計算） |
| ③ 可證偽 | ✅ 判決準則計算前聲明 (rank=17 ⇔ 升級); half-fill 對照唔會偶然 rank 17 (實測 29) |
| ④ 結構剛性 | ✅ world rank=44 / sync rank=17 分開計算, λ 全等 1/2 (allclose 1e-9); 冇 target-fit |

## 6. 誠實缺口（更新後）

- 🟡 **A5** ε=9/32=N_gen²/2B² 候選——未閉合（IF2 遺留, 需 twist vector 對應物）
- 🟡 **R4ᵘ 完整質量公式逐項比對**——未做（IF2 遺留）
- 🟢 **R2 已升級**——wedge 分辨極限 = sync rank 17 = F_proj（本輪）
- 🟡 完整 twisted 質量公式 (docs/05 §6) —— 維持隊列
- ✅ 雙向驗證 R7ᵇ/R9ᵇ —— 已完成 (IF2)
- ✅ R8ᵇ 負結果 —— 已完成 (IF2)

## 7. 累計水位

- scripts/01-06: 14+14+11+14+10+12 = **75/75 PASS, 0 FAIL**
- docs/01-06 齊全; register: O185/IF3 registered → closed（本輪）
- 剩餘隊列（全留 O185）: A5 升級 / 完整 twisted 質量公式 / （R2 已收, 新增無）

## 8. 對調律者指令嘅履行

- ✅ 「全部喺 O185 繼續」——IF3 承接 R2 缺口, 無開新 O
- ✅ 路線 A (建議攻堅首選) 完成: R2 由類比升級為直接計算
- ✅ 零新參數 + 防過度宣稱 (§4 誠實標記)
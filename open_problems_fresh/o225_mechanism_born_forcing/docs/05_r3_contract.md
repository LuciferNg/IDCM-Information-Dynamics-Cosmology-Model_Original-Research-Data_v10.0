# O225 docs/05 — R3 合約：中心不變定理（G1 語義之機制）`r3-centre-v1`

> 2026-10-01｜**預註冊**：本檔案先寫定、先註冊，之後才寫機器／才首次執行（register `O225/R3`）。
> 承接：R2 實測唯一結構律 = 中心不變 `overrides(s) = overrides(−s)`（`docs/04` §2.4），R3 給其**機制**並判定理之**充要性**。

## §1 待證定理（精確陳述）
設重播協定（凍結，逐字沿用 O222 `scripts/30.ledger_replay`）由狀態變數驅動，`s` 取值於有限群 `G`（此處 `G = 2I`，|G| = 120），並滿足：
```
(i)  等變更新：狀態推進 = 以固定群元素右乘（或左乘）：s ↦ MUL[s][h(ctx)]
(ii) 讀出表中心不變：K[−s][a] = K[s][a]  ∀ s ∈ G, ∀ a ∈ ctx（−s := s·z，z = 中心元素 −1）
```
則對所有 `s0`：由 `s0` 與由 `−s0` 啟動之重播，其 **G1 計數器完全相同**：
```
hits(s0) = hits(−s0)   stale = stale   agree = agree   stale_agree = stale_agree
overrides(s0) = overrides(−s0)        ← 即 R2 實測之唯一結構律
```
並且所有伴隨量亦相同：`ledger_len`、`#visited`、`#(s,ctx)`、`miss` 直方圖、`top` 分布、`entries_per_ctx`。

### §1.1 推導（三步，本次 R3 之核心）
```
步 1（軌跡等變）：−1 為中心元素 ⟹ (−g)·h = −(g·h) 且（左乘亦然）⟹ 歸納得
                   s_t(−s0) = −s_t(s0)  對所有 t（含 pop 回溯所致之狀態復原）
                   註：讀取「模式」（邊個 ctx 命中／push／pop）只由 ctx 序列與 ledger 結構決定，與值無關
                   ⟹ 兩條軌跡之讀取模式逐位相同
步 2（值等變）：由 (ii)，兩條軌跡上所有 K 讀值逐位相同：K[−s_t][a] = K[s_t][a]
步 3（比較同結果）：協定之比較只有兩類 ——
                   (a) 值比較（override：stored_v ≠ now；agree：stored_v = now 且 s = stored_s）
                       ⟹ 兩軌跡之 (stored_v, now) 逐位相同 ⟹ 結果相同
                   (b) 索引比較（stale：s ≠ stored_s）⟹ 兩邊同時取負 ⟹ 不等號保持
                   ⟹ 全部計數器相同  ∎
```
### §1.2 尖銳性（判準 = 逐欄比率；【首次執行前修訂】）
原寫法「破 (ii) 必失效」**過寬**：比較之結果只由 `(stored_v, now)` 之「相等／唔等」決定，而等號在兩邊同乘非零常數下不變。
故真正之充分條件係
```
(ii') 逐欄比率恆定：K[-s][a] · K[s][a] = λ_a ∈ {±1}，且 λ_a 唔依賴 s（可逐欄不同）
```
- **(ii) 係 λ_a ≡ +1 之特例** —— 故 (ii) 仍充分，但**唔必要**。
- 反例（本輪刀刃對照 1）：中心奇縮放 `K' = σ·K`（`σ(-s) = -σ(s)`）破壞 (ii)，但給出 `λ_a ≡ -1` 恆定
  ⟹ 依 (ii') 預測**不變仍成立** ⟹ 原「破 (ii) 必失效」之寫法被證偽，本輪以 (ii') 取代。
- **必要性（刀刃）**：若某欄之比率 `K[-s][a]·K[s][a]` 隨 `s` 變化 ⟹ 必須出現中心不變失效（T-翻轉反事實）。

### §1.3 普適性（唔係 2I 特例）
同一結構對合成群機器 `Z_n`（n = 8, 12, 16；交換 ⟹ 全體中心）成立：滿足 (ii') 則不變；若比率隨 `s` 變化則失效。

### §1.4 商結構（本輪之結構結論）
`2I / {±1} ≅ A₅`（階 60）。定理 ⟹ G1 語義**透過 A₅ 商分解**：`overrides` 係 `A₅` 上之函數（60 元素 → 26 個值）。
附帶判準：`overrides` **唔**由 `A₅` 之共軛類決定（5 類：1＋12＋12＋15＋20）。

## §2 預註冊判定項（R3-P1 … R3-P8；標籤固定，逐一列於 `register`）
```
R3-P1 前置 (ii) 機械檢定：K[s][a] = K[MUL[s][zc]][a] 對全部 120×62 = 7440 對（zc = 中心索引，預期 0；恆等元索引預期 75）
R3-P2 前置 (i) 機械檢定：MUL[s][zc] = MUL[zc][s]（中心性）∀s；且 MUL[MUL[s][h]][zc] = MUL[MUL[s][zc]][h] ∀s,h（等變）
R3-P3 軌跡等變（實測）：對全部 120 s0，記錄兩條軌跡之完整狀態序列，檢 s_t(−s0) = MUL[s_t(s0)][zc] 逐位成立（0 dev）
R3-P4 定理後果（實測）：hits／stale／agree／stale_agree／overrides 五量全 120 態中心不變（120/120）
R3-P5 伴隨量後果（實測）：ledger_len／#visited／#(s,ctx)／miss 直方圖／top 分布／entries_per_ctx 中心不變（120/120）
R3-P6a 凍結 K 之逐欄比率 λ_a = K[-s][a]·K[s][a] 與 s 無關（(ii') 成立），且 λ_a ≡ +1（即 (ii) 恰成立）
R3-P6b 刀刃對照 1：σ·K（中心奇縮放；破 (ii) 但 λ_a ≡ -1 恆定）⟹ 依 (ii') 預測不變**仍成立**；原「破 (ii) 必失效」在此被偽證
R3-P6c 刀刃對照 2：T-翻轉（30 個中心類各翻一元素 ⟹ 比率隨 s 變化）⟹ overrides 之中心不變必須**失效**（失效態數 > 0）
R3-P7 刀刃對照 3（破 (i)）：非等變更新（奇索引再推一步）⟹ 不變必須**失效**；並檢軌跡等變已被破壞
R3-P8a 普適性：Z_8／Z_12／Z_16 合成機器 —— 滿足 (ii) 時不變成立、破 (ii)（σ 型）時依 (ii') 仍成立
R3-P8b 商結構：2I/{±1} 階 60、共軛類大小多重集 = [1,12,12,15,20]（A₅ 簽名）；overrides 係商上之函數（26 值）但唔由商共軛類決定
```
## §3 判準（沿用 O222／O225 全套）
精確算術（int／`Fraction`）｜零浮點｜零擬合參數｜禁字集（`math` `random` `numpy` `scipy` `statistics` `cmath` `secrets` `decimal`）｜上游 O222 **唯讀**（唔寫任何 O222 檔）｜預註冊先於運算｜「無效才是正確」（刀刃測試若唔失效，即定理過寬，必須修正定理而非放寬判準）。
## §4 交付
```
docs/05_r3_contract.md（本文，凍結）｜docs/06_r3_results.md
scripts/14_r3_contract.py（enforcer）｜scripts/15_r3_centre_theorem.py（機器）｜scripts/16_r3_audit.py（獨立審計）
data/14_r3_freeze.json｜data/15_r3_centre.json｜data/16_r3_audit.json
logs/14..16｜data/MANIFEST.json（升 v3）｜01_problem_record.md §十｜register O225/R3
```

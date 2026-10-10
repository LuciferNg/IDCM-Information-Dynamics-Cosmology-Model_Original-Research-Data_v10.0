# O246 — tan 家族開譜掃描：sin/cos → tan²(nπ/88) 全開放問題探針

<!-- registry
pid:     O246
title:   tan 家族開譜掃描：sin/cos → tan²(nπ/88) 全開放問題探針
state:   registered
verdict: -
flags:   -
owner:   O246
created: 2026-10-10
updated: 2026-10-10
prereq:  -
source:  調律者 2026-10-10: 開新O掃全部開放問題; tan 分析示範
-->

> **狀態**: 📄 **已註冊 — 未開始（開完不推）**
> **建立**: 2026-10-10
> **前置**: -
> **位置**: `open_problems_fresh/o246_tan_sin_cos_tan_n_88/`

---

## 一、問題陳述

調律者觀察 (2026-10-10)：IDCM 公式「好像只用到 sin 和 cos」。提出假設：**如果換上 tan²(nπ/88) 會怎樣？** 並追問：「tanθ 本質就係一個三角波，對某些仍未解的問題有無幫助？」

本 O 任務（調律者指示）：**把所有開放問題掃一遍**（130 主 O + 157 子問題），以**tan 家族開譜掃描**做統一探針，評估 tan²(nπ/88)／三角波身份對各開放問題嘅適用性。**本次 tan 分析 = 示範**：記錄完整分析結果 → 驗證 → 逐項交接去歸屬 O。**開完不推**（唔做後續推導，只掃描＋記錄＋交接）。

## 二、已確立嘅結構

```
🟢 sin/cos 係 88-site 鏈 Dirichlet BVP 正交完備基底（實測：Σsin²(πn/88)=44=N/2 Parseval）
🟢 IDCM 已用全三角家族：sin（色散 ω_n=2sin(πn/88)）、cos（O180 v_k=c·cosθ_k）、sec（O117）、csc（O140 FSR γ_n=csc(πn/2N)）、atan（O123 δ_PMNS=π+atan(β)）
🟢 tan²(nπ/88) 喺 n=44 有 pole（tan²(π/2)=∞）⟹ 唔可以替換 sin/cos 做譜加權（Σtan² 發散；唔係完備基底）
🟢 arctan∘tan = 三角波摺疊（fold，全 88 格 ✓）⟹ tan 本質係「二元/位元結構 → 連續量」嘅積分橋（用戶直覺成立）
🟢 88=8×11 因子結構：tan 喺 n=11k 取八角分圓值（√2−1, 1, √2+1, pole, −√2−1, −1, 1−√2）—— 88 格內建八角子格
🟢 新發現 Σ_{n=1}^{43} tan²(nπ/88) = 1247 EXACT（閉式 (N−1)(N−2)/6 = C(87,2)/3 = 29×43；digamma/csc² 家族同源；RAG 查無先例）
🔴 tan²(nπ/88) 對 φ/β/φ²/√φ 精確命中：0 個（n=1..87, n≠44 盲測）⟹ 唔係 φ 家族自然語言
🔴 O221 相位差 0.2457 對 88 格/176 格：n*=6.88/13.76 皆非整數 ⟹ tan²(nπ/88) 唔可以直接閉合 O221 殘餘
```

## 三、未確立（🔴 開放問題）

```
🔴 130 個主 O + 157 子問題嘅系統性掃描未做（本 O 主任務，開完不推）
🔴 「tan 三角波 → 位元/相位層」對邊啲 O 有實際幫助——未驗證（潛在候選：O7 相位滑移、O221 摺疊、O189 CA、O222 位元、O225 對合、O35 拍頻）
🔴 Σtan²=1247 有冇物理歸屬——未查（1247 mod 88 = 15；1247/55 = 22.67 唔特；RAG 無命中）
```

## 四、攻擊路線

```
1. 全開放問題掃描（130 主 O + 157 子問題）→ 歸屬分類表（tan 適用/唔適用/需進一步測試）→ 成本：低（讀 register + README + 關鍵 docs）
2. tan 示範分析驗證（scripts/01）→ 10 個檢查 PASS（既有實測數據固化）→ 已做，見 scripts/01
3. 交接：tan 示範結果 → 逐項 handoff 去歸屬 O（O140/O117/O123/O7/O221/O35）+ register note → 成本：低
4. 🔴 唔推：唔寫新推導、唔開新 docs 推導、唔 gerrymander 任何 O
```

## 五、驗證標準

```
✅ scripts/01_tan_spectral_sweep.py 全 PASS（已跑：10/10）
✅ 開放問題掃描分類表完成（130 主 O + 157 子問題 → 分類）
✅ 交接完成（register handoff 去歸屬 O；跨 O 零檔案寫入）
✅ register check 回落基線（無新 HARD DRIFT）
✅ 開完不推：scripts/ 只保留掃描+驗證，無後續推導 round
```

**四道硬測試**（閉合宣稱必過）：
① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）
③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-10-10 | 註冊 O246（調律者指示：掃全部開放問題 + tan 示範 + 交接 + 不推） | scaffold |
| 2 | 2026-10-10 | tan 示範分析完成（scripts/01 10/10 PASS）：pole/FOLD/Parseval/八角/1247/φ盲測/O221對格 | docs/02 + scripts/01 |
| 3 | 2026-10-11 | 全開放問題掃描分類完成：主 O 131（A=14/B=55/C=62）+ 子問題 157（A=18/B=77/C=62）；1247 repo 查重（無 Σtan² 先例 ⟹ 新產物確認）；6 項 register handoff（O221/O140/O117/O123/O7/O35)；README 行 + handoff 記錄 | docs/03 + scripts/02 + register |

## 七、相關文件

```
- o140_finite_spectral_relativity/ — FSR γ_n=csc(πn/2N)（tan 家族同源）
- o117_dh_line_of_sight/ — w_n=sec(πn/88)（tan 家族同源）
- o123_neutrino_delta_cp/ — δ_PMNS=π+atan(β)（tan 角度身份）
- o35_beats_mass_linkup/ — sin_ratio 系列（拍頻→三角質量公式）
- o221_continuum_low_energy/ — 相位差 0.2457 殘餘（tan 盲測對照）
- o7_frustration_distribution/ — 相位滑移 π（tan pole 結構同源）
- scripts/01_tan_spectral_sweep.py — 驗證 script（10/10 PASS）
```
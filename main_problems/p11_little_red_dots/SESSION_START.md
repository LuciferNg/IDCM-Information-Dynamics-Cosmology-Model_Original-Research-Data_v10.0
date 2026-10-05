# little_red_dots — Session Handoff (下一 session 交接)

> **交接日期**: 2026-09-13（獨立化）
> **狀態**: 🟢 核心閉合（質量/紅化/環境/投影/RG 流）— 45/45 + 50/50 全綠
> 剩 🔴 等數據 + 微觀機制（O179 開題）

## 已完成 (本項目)

1. **質量閉合鏈** — M = E_strain·η·S·f·(1+δ)^{3/2}, ratio 0.9994 (λ=10% Edd)
2. **E_strain 全譜量化** — (π²/(L₄L₅−μ²))·M_Pl·(R_H/L_P)·N_d^{−2N_gen} (75 = L₄L₅−μ²)
3. **結構紅化定律** — dβ/dℓ = 88/21 = 176/42 = 4N_d/(N_d−μ²) (0.22σ)
4. **RG 流推導** — β-function = ΔN_cand/N_eff (模態計數); 不變量 21×176/42 = 88
5. **投影審計** — 22 操作 13/13; C=B/L₅, M₄/M₀=L₄/(L₅+B); D_app/N(z) 互補
6. **環境** — δ∈[0.32,3.34] 中位 1.37; δ 解釋 53% scatter
7. **誠實修正** — λ_Edd=10 係效率假設自洽 (預言 LRD = 10% Edd);
   凝聚時標 3.2e7→4.54e6 yr; dβ/dℓ×M₄/M₀ dev 2.2% (原 0.9% 錯)
8. **本體論** — LRD = 真實天體 (凝聚核心充當星系核); 連續製造支持
9. **驗證** — master 45/45 (T1-T45) + 獨立核對 61/61 (records 02-14)
10. **巴爾末雙峰 (2026-09-13)** — 共軛模態對定理: θ_{176−k} = π − θ_k ⟹ 同半徑、反號速度
    ⟹ 對稱雙峰係結構必然 (唔需散射/雙錐); Δv = 2√(a₀r); 中心模態 → 三峰預言;
    ℓ=3 量子 167.23 km/s; 平軌上限 2V_max = 819.56 km/s; script 21 = 9/9 PASS

## 未完成 / 移交 (下一 session)

- [ ] **🔴 T1 判別 (最sharp)**: 雙峰 Hβ 且 Δv(Hβ) = Δv(Hα) → 殺死共振散射
      (Chang & Gronke 2026: BR3 = 0.261 令 Hβ 冇雙峰), 支持運動學/IDCM。
      等 NIRSpec R≳2700 高解像雙峰樣本 (record 14 §5)
- [ ] **🔴 raw FWHM 張力**: 觀測 raw FWHM 1000–1500 km/s > 平軌上限 2V_max = 819.6 km/s
      — 需分離運動學 vs 散射成分 (Rusakov 本徵 ~300 km/s)
- [ ] **等數據監測**: #21 λ=10% Edd (光譜質量) / #22 β 判別 (±0.15 斜率) /
      #25 scatter 分解 / Q3 宿主星系 M_host = M_BH×306 (JWST) /
      P13 (Euclid DR1 2026尾) / P15 (Gaia DR4) / P9′ (AugerPrime 2035)
- [ ] **🔴 結構側**: #10 β 函數形式證明 / #24 E_strain π² 來源
- [ ] **O173 體系**（應變能循環，已閉合）: 池再生六機制 / 轉化器 / 殘骸固定點 /
      熵定理 (O175) / 觀測裁決 (O176) / 364 身份 (O177)
- [ ] **O179 開題**（新節點出現機制）: 4^{−ℓ} 層級點樣產生新星系位置 —
      `open_problems_fresh/o179_new_node_mechanism/`

## 工作目錄

`main_problems/p11_little_red_dots/` — records/ (01-13) + scripts/ (01-20) +
data/ (11-20 JSON + COSMOS-Web_LRDs.dat + a5 routing)

## 判準提醒

- 零新常數 / 結構強逼唯一解 / 沙漠審計 (O166 四步法)
- 反秘數 (O165): 唔可以 φ-power 湊數 (φ-power trap 教訓)
- 時序潔癖: 新發現 append, 唔改舊結論 (02 §8-§19 延伸鏈)
- 無指示禁寫入 crystal_stress（已分家，唔再合併）

---

## ⚠️ O169 修正點 (2026-09-15) — 待本 O 重驗

**修正點** (上游 O169):

- 伸長定律 `E = 1 + 2φ⁻¹ℓ` **已證偽** (DESI DR2 D_M×6 排除 4.88σ) → `E(ℓ) = ℓ + 1.11911398` (= ⟨γ⟩_odd/2·ℓ + 1/⟨v_g⟩_{1..22}); `δ(ℓ) = −φ⁻³(ℓ−1/2)`, `C = 1−2φ⁻¹ = −(√5−2)`

**問題** (本 O 受影響點):

- `records/09_projection_audit.md:83` — #17 D_app 同 N(z) = 4^{−ℓ} 嘅投影關係
- `records/10_projection_extensions.md:11-16` — ★ `D_app/R_H + 4^{−ℓ} = 1 + 2φ⁻¹ℓ(1−4^{−ℓ})`
- `records/02_lrd_record.md:346` — #17 D_app/N(z) 互補 🟢
- `scripts/17_audit_crosscheck.py:87` — check「1 + 2φ⁻¹·(1−4⁻¹)」
- ★ **#17「D_app/N(z) 互補」重推**: `D_app/R_H + 4^{−ℓ} = 1 + 2φ⁻¹ℓ(1−4^{−ℓ})` 直接依賴舊伸長 → 用新 `E(ℓ) = ℓ + √5/2` 重算呢個互補關係 (可能形式變, 甚至唔再成立)

**狀態**: [ ] 未重驗
> 只加註, 未改本 O 結論檔 (01_problem_record.md / docs/ / final_result.md); 重驗後由本 O 自行寫入。


---

## ★ 全樹路徑衛生審計註記（2026-10-02，append-only）

> 由 skill `script-chain-reproducibility` 全鏈核對器（`path_hygiene_scan.py`）全樹掃描建立——
> **2026-10-02 首次**。**本節唔改動上方任何內容。**
>
> ⚠️ 本節係**工具層審計**（產物路徑衛生），**唔屬本 O 推導**；亦冇對本 O 任何結論作出判定。
> 完整報告：`path_hygiene_audit_20261002/REPORT.md`

### 〇. 一句話

本目錄命中 **5 個 ghost-tree call site**。

### 一. 命中清單

#### ⚠️ ghost tree 依赖

| # | 檔案:行 | 讀取目標（ghost tree 內）|
|:--|:--|:--|
| 1 | `little_red_dots/scripts/03_lrd_node_crosscheck.py:67` | `main_problems/p4_cmb_cold_spot/data/a5_nodes.txt` |
| 2 | `little_red_dots/scripts/03_lrd_node_crosscheck.py:78` | `main_problems/p4_cmb_cold_spot/data/frustration_edges.txt` |
| 3 | `little_red_dots/scripts/06_a5_routing_analysis.py:202` | `main_problems/p5_crystal_stress/little_red_dots/data` |
| 4 | `little_red_dots/scripts/07_a5_routing_weighted.py:197` | `main_problems/p5_crystal_stress/little_red_dots/data` |
| 5 | `little_red_dots/scripts/08_kchain_modes.py:171` | `main_problems/p5_crystal_stress/little_red_dots/data` |

### 二. 處置（別 O 執行；本節只記移交）

```
⚠️ ghost tree 依赖：5 個 call site 讀 `/home/wsl/Projects/IDCM/IDCM-v10.0/`。
   ① 把所需檔搬入本 O `data/`（或記明「唯讀外部輸入」）
   ② `BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` ＋ 相對路徑
   ③ 風險（已量化）：ghost tree 係 2026-09-08 副本（全樹 288K）。全樹 301 個 call site 分類：
      ① 69 個目標仍存在（讀嘅係**陳舊副本**）；② 231 個目標已失踪但同相對路徑在 repo 存在
      （⟹ **改一行即可，零資料損失**）；③ 1 個 repo 內完全冇。逐 O 對照表 → 同報告目錄 `ghost_dispatch.md`
```

> ⚠️ 依據 `idcm-closeout` §8.1：跨 O 問題**只登記移交，唔准就地修**。本節由**外部審計**寫入，
> 本 O 之 session **有權刪去或改寫本節**（上方內容不受影響）——但如果決定保留，
> 請在 GATE / 下輪 round doc 裏明文記下「已接納 / 已處理」。

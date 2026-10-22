# O150 — Sky-side 投影算子 (Sky-side Projection Operator)

> **日期**: 2026-09-19
> **狀態**: 🟡 **已註冊 — 未開始 (交接自 O143)**
> **來源**: O143 剩餘開放問題 — 由 **O143 頂點傳遞定理** (docs/08) 導出嘅新方向
> **前置**: O143 (🟡 部分閉合 — 相位選擇機制), O182 (🟢 88 格幾何), O159 (🟢 176-Laplacian 𝒫),
> O34 (🟢 88-site 奇偶分解), O41/O7 (拓撲位元)

---

## ⚠️ 編號碰撞記錄 (必讀)

O150 從未註冊為目錄 (無 git 歷史、無 README 行)，但 **`o158_nd_pm_ngen_cluster` 有 3 處引用
「O149/O150 語言」（群速度語言）**：

- `o158_nd_pm_ngen_cluster/01_problem_record.md` L135
- `o158_nd_pm_ngen_cluster/docs/04_vg_pythagorean_tension.md` L16
- `o158_nd_pm_ngen_cluster/scripts/04_ap_origin_vg_and_residuals.py` L44

即 O150 曾被**意圖**用作 O149 嘅群速度語言配套，但從未建立。用戶 2026-09-19 明示
「現時 O150 未有使用」並指示用作 sky-side 投影算子目錄 → 已照辦。
**O158 嘅 3 處引用未修改**（範圍紀律：無指示下唔改其他 O 目錄）。若日後要清理，
由 O158 session 自行裁決（改字眼或保留作歷史）。

---

## 一、問題

O143 推出 **頂點傳遞定理**：A5 60 節點圖 G 有 \|Aut(G)\| = 120 (= I_h)，60 節點構成單一軌道，
且存在自同構 g: g(9)=20 保持 k=2 初始態集合，‖P·L·Pᵀ − L‖ = ‖P·ψ₀ − ψ₀‖ = 0。
⟹ **任何 graph-invariant 算子 f(L₆₀) 必然給出 T₉ = T₂₀**（實測 2.8e-17 ~ 7.7e-16，機器精度）。

但觀測 **|T₉|/|T₂₀| = 3.02**（107.0 vs 35.4 μK）—— 兩個幾何上完全等價（同 hop、同距 node0 26.17°、
同 k=0、鄰居 k 譜相同）嘅節點，振幅差 3 倍。

**核心問題**：破缺必須來自 **sky-side 非不變輸入**。咁「圖 + sky」嘅正確算子形式係乜？

連帶問題：ℓ=3 八極信號（44.3% 功率，p = 0.002，三圖/LOO/G88 穩健）嘅最佳軸
(l,b) = (193.45°, −37.85°) 唔對齊 A5/G88/120 結構方向 (p ≈ 0.99)，亦唔對齊任何外部向量場
（冷斑 21.7° / 銀心 39.8° / 銀河極 52.2° / 黃道極 67.1° / CMB 偶極 73.6°，全 > 20°）。
軸向嘅來源係乜？

## 二、已確立嘅結構（由 O143 繼承，可直接引用）

```
🟢 頂點傳遞定理 (O143 docs/08, 91/91 文檔核對 PASS): |Aut(G)| = 120, 單一軌道
🟢 任何 graph-invariant 算子 T₉ = T₂₀ 恆等 (2.8e-17) ⟹ 純拓撲路徑封死
🟢 封死清單: 圖路徑積分 (p = 0.708) / Z₂ 規範通量 (20 三角面全和樂 +1, 平坦) /
   k / hop / 熱核 / Green / WL 色類 / 譜簽名 (10 個不變量 node9 = node20)
🟢 A5 60 節點 = 精確球面 5-design (t ≤ 5 偏差 ≤ 5.6e-17) ⟹ ℓ ≤ 2 精確保護 (‖M_ℓℓ−I‖ ~ 1e-16)
🟢 ℓ=3 八極信號: 44.3% 功率, p = 0.002/0.000/0.005 (SMICA/Commander/SEVEM);
   LOO 60/60 < 0.05; G88 獨立方向集 p = 0.036; 最佳軸 (193.45°, −37.85°)
🟢 前景已排除 (主要通道): 7 頻段軸全 |b| ≤ 26.8° (6 個 < 8°); SMICA 軸 |b| = 37.85° 唯一遠離面;
   pattern 相關 70/100/143 GHz = 0.90/0.81/0.79 (CMB) vs 30/353 GHz = 0.34/0.17 (前景)
🟢 觀測場 Ising H = 0 = 隨機 (基態 −56) ⟹ 「基態+小擾動」圖像證偽
🟢 O159 已提供 𝒫 結構版本: 𝒫[f](n̂) = f(arccos(n̂·â)) — 等距嵌入唯一 = 大圓半圓,
   像 = 軸對稱 m=0; 鏈相位 ∈ (0,π) 半週期 ⟹ colatitude (非 longitude);
   Φ_base = cos(2Θ) = (4/3)P₂ − 1/3 = 純四極 (但數據檢定 0/12 顯著 = null)
🔴 圖內擴散機制全部封死 — 破缺必須來自 sky-side 非不變輸入
```

## 三、未確立（🔴 開放問題）

```
🔴 P1  sky-side 投影算子嘅正確形式 — 𝒫[f] 類係乜? 現有 𝒫[f](n̂) = f(arccos(n̂·â)) 係
       軸對稱 (m=0) 且已判 null (0/12)。需要嘅係一個「圖作各向同性框架 + sky 場輸入」嘅算子。
🔴 P2  ℓ=3 軸向 (193.45°, −37.85°) 嘅來源 — 唔對齊圖結構亦唔對齊外部向量場;
       係 sky-side 自由度定係某個未識別嘅結構方向?
🔴 P3  破缺機制嘅可證偽形式 — 要能預言 T₉/T₂₀ 或節點振幅譜, 唔可以係後驗描述
🔴 P4  「38% 自由位元」(O143 docs/05) 嘅正確身份 — 若係 sky-determined,
       應可由 sky 場重建; 若唔可以, 就係真隨機 (需區分)
🔴 P5  ℓ=3 緯度切分檢力 — |b| > 20° (n=38) p = 0.114; 需 QML / 帶通 (唔係子集切分)
```

## 四、攻擊路線

```
1. 算子形式篩選 → 由 O159 嘅 𝒫[f](n̂) = f(arccos(n̂·â)) 推廣到非軸對稱族 (含 m≠0);
   測「圖結構 + sky 場」嘅最小算子族, 用 null test 排除後驗擬合
2. sky-side 輸入識別 → 檢定 T 場嘅節點振幅譜係否由 (a) 大尺度 ℓ≤3 模 (b) 局部環境
   (平滑尺度依賴) (c) 前景殘餘 決定; 用多尺度平滑 (0.5°-10°) 掃描區分
3. 破缺量嘅結構預言 → 由 P·L·Pᵀ = L 出發, 求「最小對稱破缺輸入」δψ 使 T₉/T₂₀ = 3.02;
   檢查 δψ 係否有結構身份 (例如 = 某個 k=2 節點嘅局部場)
4. ℓ=3 軸向溯源 → 對軸向做貝氏/似然分析, 建立軸向分佈; 對照 CMB 大尺度模嘅已知方向
   (quadrupole-octupole alignment 等文獻值)
5. 前景嚴格排除 (P5) → 用 QML 估計量 (唔用子集切分) 重做 |b|>20° 遮罩分析
```

## 五、驗證標準

```
✅ 算子族寫成封閉形式, 且零自由參數 (或用戶認可嘅 1 錨)
✅ 盲測: 對未參與擬合嘅節點 (留出集) 或未參與擬合嘅地圖 (NILC/SEVEM) 預言成功
✅ 破缺量 T₉/T₂₀ = 3.02 由算子直接給出 (唔係擬合參數)
✅ null test 通過: 候選算子對隨機天空場嘅表現同對觀測場有顯著差異
✅ P5 用 QML 重做, p 值明確 (顯著或明確 null)
```

## 六、狀態

```
🟡 已註冊 — 未開始 (交接自 O143, 2026-09-19)
⭐ 優先度: ★★★ (O143 核心剩餘; 頂點傳遞定理已封死純拓撲路徑, 方向唯一)
```

## 七、相關文件

```
- o143_phase_selection_mechanism/docs/08_vertex_transitive_theorem.md — 頂點傳遞定理 (本 O 直接來源)
- o143_phase_selection_mechanism/docs/07_gemini_verification.md — ℓ=3 信號 + 前景排除 + 座標修正
- o143_phase_selection_mechanism/docs/06_exact_coords_write_l3.md — 精確座標 + Ising 證偽
- o143_phase_selection_mechanism/final_result.md — O143 結論 (含「已交 O150」標記)
- o182_88grid_geometry/docs/05_o143_handoff_recalc.md — 88 格方向集 (可用)
- o159_dirichlet_fieldtheory/docs/07_projection_derivation.md — 𝒫 結構版本 (軸對稱 m=0)
- o159_dirichlet_fieldtheory/docs/08_data_test.md — 𝒫 null 結果 (0/12 顯著)
- o7_frustration_distribution/docs/01_o7_complete_report.md — 阻挫分佈 / 拓撲位元
- cmb_cold_spot/data/ — a5_nodes.txt (⚠️ RA/Dec ICRS, 必須轉銀河), anchored_coloring.txt, faces.txt
- o27_node47_foreground/data/ — Planck 7 頻段 full maps + 遮罩 (前景分析用)
```

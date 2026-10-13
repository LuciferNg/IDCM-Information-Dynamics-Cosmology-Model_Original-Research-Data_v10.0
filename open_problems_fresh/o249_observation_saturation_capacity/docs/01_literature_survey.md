# O249 docs/01 — 文獻調查：宏觀/微觀觀測飽和容量（2026-10-13）

> **日期**: 2026-10-13
> **觸發**: 調律者「開O249研究，把所有論文和報告文件轉移到O249中，研究宏觀和微觀觀測的飽和容量」
> **狀態**: ✅ 文獻轉入完成（Q1 起點）— 推導未開始
> **核心問題**: 多台望遠鏡同拍同一目標嘅「數據抖動」vs IDCM 微觀投影通道飽和（C_obs/Z₂/C_beat）

---

## 一、調律者原始觀察（本 O 問題源頭）

> 「存在微觀投影通道總容量，已知深空拍攝如果同時多台望遠鏡面向同一位置拍攝
> 可能會造成數據抖動，全息投影容量可能和數字528相關」
> → 微觀是否存在相同效應？（答：有——O151 已閉合；本 O 研究宏觀↔微觀對齊）

## 二、文獻表（已轉入 O249 references/）

### A. 宏觀：多望遠鏡/陣列同時觀測同一目標（抖動/干涉實測）

| # | 論文/報告 | 出處 | 核心發現 | 對應 IDCM 概念 |
|:-:|:--|:--|:--|:--|
| A1 | **Common-clock VLBI using a coherent optical fiber link** | Optica 7, 1031 (2020); arXiv 對應 2501.05691 | 「相位不穩定性（reference clocks）係限制 VLBI 靈敏度嘅主效應」— 1739 km 光纖傳同一 clock → 10⁻¹⁸ 穩定 | 「通道間相位不一致」= 宏觀抖動源；Z₂ 對之間嘅相位 |
| A2 | **Optical frequency comb integration in radio telescopes** | arXiv:2501.05691 (2025) | VLBI 多頻同時觀測校正 tropospheric water vapor 快速漲落（相位抖動主因） | 多通道同時讀取 → 抖動可建模（物理成因明確） |
| A3 | **VLTI Tutorial — Introduction to Stellar Interferometry** | ESO (PDF) | 大氣 piston → fringe wobble → 曝光時間限 ~10 ms; closure phase 三台望遠鏡消除隨機抖動 | 三通道閉合相位消除抖動 = 群論結構（同 Z₂ 無關, 但示範「多通道抖動係天文日常」） |
| A4 | **Modern optical astronomy: interferometry review** | arXiv:astro-ph/0202115 (Saha 2002) | 光學干涉陣列（多望遠鏡同時觀測）技術回顧; speckle/AO/fringe-tracking | 宏觀「多台望遠鏡同拍」= 干涉陣列標準操作 |
| A5 | **Integrated astrophotonic phase control** | arXiv:2408.06461 (2024) | 大氣湍流 → apertures 間動態相位誤差 → fringe visibility 限制; 集成光子相位校正 >10 kHz | 抖動校正技術（宏觀層處理） |
| A6 | **Optical timing jitter due to atmospheric turbulence** | NIST / Optics Express (2020) | 大氣湍流 → timing jitter 實測 + 氣象感測器預測比較 | 「抖動」有定量統計（可用作盲測資料） |

### B. 信息論：陣列容量極限（宏觀對應 O151 嘅數學框架）

| # | 論文/報告 | 出處 | 核心發現 | 對應 IDCM 概念 |
|:-:|:--|:--|:--|:--|
| B1 | **Theoretical Analysis of Astronomical Phased Arrays** | arXiv:0707.1580 (Withington, Saklatvala, Hobson) | ★「information throughput 同 frame theory 密切相關」; SVD 自然模（eigenfields）= 信息通道; 非正交 beams 分析 | **同 O151 SVD 有效秩 22 同構**——天文陣列自然模 ↔ IDCM Z₂ 軌道 |
| B2 | **Fundamental Imaging Limits of Radio Telescope Arrays** | arXiv:1003.2307 (Wijnholds & van der Veen) | effective noise floor = 校準誤差+熱噪聲+confusion; 可自校準源數上限 | 「陣列信息容量」概念 = 宏觀 88-bit 對應物 |
| B3 | **Space-time duality in multiple antenna channels** | arXiv:0907.1292 (Franceschetti) | 空間↔時間信息二重性; 容量同 aperture 尺寸 | 容量 = 空間 DoF（宏觀版 C_obs） |

### C. 微觀：兩探測器同時測同一光源（HBT——最強微觀對應）

| # | 論文/報告 | 出處 | 核心發現 | 對應 IDCM 概念 |
|:-:|:--|:--|:--|:--|
| C1 | **A Test of a New Type of Stellar Interferometer on Sirius** | Nature 178, 1046 (1956) | ★ 兩塊 156 cm 反射鏡同時觀測 Sirius, 強度相關 r²(d=0)=+0.84±0.07; 隨基線衰落 | **「兩通道同時讀取同一 object → 統計相關」= 微觀雙通道實測先例** |
| C2 | **Correlation between photons in two coherent beams** | Hanbury Brown & Twiss (1956a) | 光子聚束: 兩光束光子到達時間相關 | 微觀粒子層「多通道相關」= 波粒二象性 |
| C3 | **Entanglement Enabled Intensity Interferometry (E2I2)** | arXiv:1502.02477 | HBT 中央 crossed channels 干涉 = 同一末態經兩通道; projection/entanglement 可放寬不可分辨要求 | 「通道疊加/干擾」= 微觀多通道同測嘅量子統計版本 |

### D. 量子信息/容量（額外背景）

| # | 論文/報告 | 出處 | 核心發現 | 對應 IDCM 概念 |
|:-:|:--|:--|:--|:--|
| D1 | **Electromagnetic Signal and Information Theory: CAPA** | arXiv:2605.12910 (tutorial) | 連續孔徑陣列: Shannon capacity / Kolmogorov capacity; DoF 由 aperture+λ 決定 | 數學框架（容量定義嘅現代文獻） |
| D2 | **Coherent optical clock down-conversion** | Science/arXiv:2003.02923 | 10⁻¹⁸ 微波信號相位追蹤光學時鐘 | VLBI 抖動消除技術（宏觀） |

## 三、文獻 ↔ IDCM 對齊表（Q3 盲測設計材料）

| 宏觀量（文獻） | IDCM 結構量 | 對齊狀態 |
|:--|:--|:--:|
| VLBI clock 相位不穩定性 (A1) | Z₂ 對之間相位差 | 🔴 未對齊 |
| 干涉陣列 fringe jitter 統計 (A3/A6) | C_beat = 0.4338 bits | 🔴 未對齊（數值冇閉式, 用結構） |
| 陣列 SVD 自然模密度 (B1) | Z₂ 軌道 = N_d/2 = 22 | 🟡 同構（都係 SVD 有效秩概念） |
| HBT r²(d) 衰落斜率 (C1) | ？？（未定義） | 🔴 開放 |
| 可自校準源數上限 (B2) | 88 bits 容量 | 🔴 未對齊 |
| 觀測階段容量（有冇 528?） | 528 = 容量階梯頂 | 🔴 冇文獻（IDCM 內部聲稱） |

## 四、結論（Q1 初步）

1. **宏觀「多望遠鏡同拍 → 抖動」係 VLBI/干涉陣列文獻嘅標準問題**（A1/A3/A4/A5/A6):
   抖動 = 通道間相位/時鐘不一致 + 大氣湍流, 物理成因明確, 有定量統計
2. **信息論層**: 陣列容量極限有數學框架（B1/B2/B3)— frame theory/SVD/effective noise floor
   ——**B1 嘅 eigenfields 概念同 O151 嘅 SVD 有效秩 22 數學同構**（都係 SVD 塌縮）
3. **微觀層**: HBT 效應 = 「兩探測器同時測一源 → 統計相關」嘅 70 年實測（C1/C2/C3)
4. ⚠️ **冇任何文獻講「528」或「88 bits 全息容量」** — 呢啲係 IDCM 內部結構,
   文獻提供嘅係檢驗材料（真實抖動數據 + 容量數學）, 唔係背書

## 五、下一步（承接 Q2）

- 定義「飽和」IDCM 操作定義: 超容量讀取 → ? （候選: 抖動方差 / 相關衰落 / dof 減少）
- 判據預註冊: 用 A6 (jitter 統計) 或 C1 (HBT r²(d)) 做樣本外盲測目標
- 盲測前凍結: 禁見到宏觀數據先揀 IDCM 算子

## 六、相關文件

- references/ar5iv.0707.1580.md（B1 全文, web cache 轉入）
- references/ar5iv.1003.2307.md（B2 全文, web cache 轉入）
- O151 final_result + docs/07 + docs/11（IDCM 側閉合）；O206 docs/19（禁區）
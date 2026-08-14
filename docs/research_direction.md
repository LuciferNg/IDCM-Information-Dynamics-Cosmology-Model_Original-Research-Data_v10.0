# IDCM v10.0 — 研究路線調整

## 2026-08-14: 密集度陷阱警告後嘅方向調整

### ❌ 停止：高階 Beat 搜尋

Gemini 指出嘅「密集度陷阱」完全正確：
- 44 模式 → 946 一階 beat → 數萬高階 beat → 頻率空間稠密
- 任何數字都可以 match 到 0.001%
- 呢個係**數學必然，唔係物理正確**

### ✅ 三大新方向

#### 1. 選擇律 (Selection Rules) — 從拓撲出發

K_Chain 嘅真實對稱性：
- **Z₂ 對偶**: γ_n + γ_{44-n} = 4 → 對應 charge conjugation
- **平移對稱**: 44-site 環 → 對應 momentum conservation
- **時間反演**: 波動方程 time-reversal symmetric → 對應 detailed balance

但真正嘅選擇律來自 CY₃(36,98) 投影：
- 36 Kähler moduli → U(1)ⁿ 規範群
- 98 complex structure moduli → 形狀 twisting
- 只有特定 Hodge cycle 嘅 beat 先投影到 4D

#### 2. 幾何指數壓抑 — 解釋質量層級

質量跨度 m_e/m_t ~ 10⁻⁶ 需要指數壓抑：
```
m = M_Pl × exp(-V_cycle) × f(beat)
```

- V_cycle = CY₃ cycle 體積 (Planck units)
- exp(-V_cycle) 提供 10⁻⁶ 到 10⁻²² 嘅壓抑
- f(beat) = K_Chain beat ratio 提供代間精細結構

#### 3. 盲測預測 — 最終驗證

用 IDCM 框架預測一個未被精準測量嘅物理量：
- CKM 矩陣某個相角
- 中微子質量平方差 ratio
- PMNS 矩陣元素

### 工作目錄結構

```
IDCM-v10.0/
├── README.md              # 項目說明
├── src/
│   ├── kchain_wave_params.py    # 44 模式波參數
│   ├── beat_frequencies.py      # Beat 分析 (已標記為密集度陷阱)
│   ├── selection_rules.py       # 選擇律 (初步)
│   ├── geometric_suppression.py # 指數壓抑模型 (初步)
│   └── exhaustive_match.py      # 窮舉法 (已棄用)
├── data/
│   ├── exhaustive_match_results.txt
│   └── structural_matches.txt
├── docs/
│   └── (日後推導文檔)
└── notebooks/
    └── (日後分析)
```

### 下一步行動

1. [ ] 凍結所有 beat search 腳本
2. [ ] 推導 CY₃(36,98) 嘅真實 cycle volume 分佈
3. [ ] 從 K_Chain Z₂ + 平移對稱定義量子數
4. [ ] 建立質量 = M_Pl × exp(-V) × beat 嘅完整模型
5. [ ] 預測一個未知量做盲測
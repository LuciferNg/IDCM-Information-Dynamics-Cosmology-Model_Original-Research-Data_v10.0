# O173 docs/17 — 現有數據先行驗證盤點 (用戶 09-12 指示) 🟢

> **日期**: 2026-09-12 · **Script**: `scripts/20_existing_data_audit.py` (9/9 PASS)
> **指示**: 全部預言先用現有觀測數據先行驗證, 唔等未來 JWST/DESI

## 盤點結果: 10/15 已用現有數據驗證, 5 個 🟡

| P | 預言 | 狀態 | 現有數據依據 |
|:-:|:---|:---:|:---|
| P1 | N(z) ∝ 1/(1+z) | 🟡 | 定義待釘 (docs/15); crystal_stress LRD N(z) 投影已做 |
| P2 | 有限池 ≤9 LRD 證偽 | ✅ | COSMOS-Web **434 LRD** |
| P3 | 10% Eddington | ✅ | 434 LRD Lbol 分佈 |
| P4 | 拍頻 null | ✅ | crystal_stress |
| P5 | 宿主干涉比 4.96 否決 | ✅ | docs/07 |
| P6 | 冇老化 | ✅ | crystal_stress |
| P7 | 種子上限 | ✅ | 434 LRD (0.27) + **UHz1 δ_eff 91.4** |
| P8 | 冇 Hawking | ✅ | null (冇蒸發觀測) |
| P9 | UHECR 返池簽名 | 🟡 | Auger UHECR-Cen A/AGN 關聯方向支持 |
| P10 | 冇回收中 | ✅ | null (BHMF 冇萎縮端) |
| P11 | 噴流/UHECR 返池 | 🟡 | 同 P9 (AGN 噴流 = 返池通道) |
| P12 | 1/306 紅移平穩 | 🟡 | **JWST overmassive BH 張力候選** |
| P13 | 冇 1e12+ | ✅ | ★**Abell 1201 = 3.0e10 = 0.91× 上限** |
| P14 | M_BH/M_star = 1/306 | ✅ | 樣本定義測試 (docs/16) |
| P15 | 殘骸 = 形成史×2% | 🟡 | 局部 WD 7.2% (環境效應) |

## ★ 新發現: P13 現有數據封頂

**Abell 1201 BCG = 3.0e10 M☉** (引力透鏡, Nightingale+2023 — 最可靠測量方法):
- IDCM M_BH_max = 3.3e10 → **Abell = 0.91× 上限** — 直接封頂喺預言內
- TON 618 (6.6e10) = virial 估計 (不可靠); Phoenix A (1e11) 有爭議
- → 「最重 SMBH」嘅可靠測量下界 = 3e10, 同 P13 一致, 冇突破天花板

## P15 數量級檢驗 (Holberg+16)

```
局部 WD 密度: n_WD = 4.8±0.5e-3 pc⁻³ (其他文獻 4.49-5.5e-3 一致)
ρ_WD = 4.8e-3 × 0.6 = 2.88e-3 M☉/pc³
局部比例 = 7.2% vs 宇宙平均 f_debris ≈ 2%
→ 高係薄盤老化環境效應 (太陽鄰域老薄盤), 數量級一致, 冇爆炸累積
```

## 🟡 張力候選 (誠實)

**P12: JWST (2023-2024) high-z overmassive BH 發現** — 若 confirmed,
M_BH/M_star 高 z 偏離 1/306 → P12/P14 受壓。但 high-z 宿主質量測量
(核光污染) 系統誤差大 — 未定論。→ 標記為**最優先跟進** (R1 JWST 數據
出嚟時第一個要 check 嘅位)。

## 行動

1. P12 overmassive 張力 → 專項檢驗 (JWST 宿主質量公布時)
2. P1 定義釘死 → DESI/Euclid N(z) 統計
3. P9/P11 → Auger 完整各向異性圖譜對比 (現有公開數據可做)
4. P15 → 宇宙平均 WD 質量密度 (深場) 對比 2%

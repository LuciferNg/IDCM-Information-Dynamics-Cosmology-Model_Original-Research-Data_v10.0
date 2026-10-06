# O234 docs/03 — Round 3: freeze v2（RGI_b 入層 + scheme 更正 + redundancy 閉環 + 預言 register）

> **日期**: 2026-10-07（第三輪，完整讀 FLAG 2024 §4.3）
> **Scripts**: `scripts/05_freeze_v2_prediction_register.py`（4 PASS / 0 FAIL）
> **凍結層**: v2（v1.1 + 本輪新增量; data/05_freeze_v2_prediction_register.json）
> **來源**: FLAG Review 2024 §4.3 (Eqs.61–64, Tab.15) + §4.1 (Eqs.35,44) + 前輪凍結值

---

## 一、freeze v2 新增量（全部 FLAG 2024 §4，scheme 註冊）

| 量 | 值 | 誤差 | 出處 |
|:--|:--|:--|:--|
| Mᵇ_RGI (Nf=2+1+1) | **6.938(23)(45) GeV** | 0.73% | Eq.(64), Refs[42,89–92] |
| m_b/m_c @μ=3GeV (MS, Nf=4) | **4.586(12)** | 0.26% | HPQCD 21 (Tab.15, QED 已含) |
| m_b/m_c cross | 4.578(7) | 0.15% | FNAL/MILC/TUM 18 |
| Mᵤ_RGI | 2.97(11)(3) MeV | 3.8% | Eq.(44), Refs[42,63] |
| M_d_RGI | 6.53(7)(8) MeV | 1.6% | Eq.(44) |
| m_c/m_s Nf=4 | 11.652(65) — 維持主值 | 0.56% | round-2 決策: Nf=4 主, HPQCD 11.85(16) 交叉 |

另: m_b(m_b) = 4.200(14) GeV (Nf=2+1+1, Eq.63) 有錄, 但唔用 —— 混標度（mb(mb)/mc(mc)）唔入層,
一律用同 scheme/同標度比或 RGI。

## 二、★ 重大更正: b/c「near-hit」係混標度偽影

round-1 S1a 用 PDG mb(mb)/mc(mc) = 4.18/1.27 = 3.291（兩個唔同 scheme 標度相除）:

- 混標度 → 所需 C_b/C_c = 1.3746 → 對 44/33 = 1.3333 **dev 3.0% (nominal near-hit)**
- **scheme 正確（HPQCD 21 @3GeV）→ C_b/C_c = 1.9153 → dev 43.6% —— 死實**

⟹ **「44/33 近命中」係偽影**; 更正後池無命中。混標度誤導性正式坐實:
任何「C_f 池匹配」分析必須先用同 scheme 比（凍結層 v2 規則）。

## 三、★ redundancy 0 → 1: 凍結層內部閉環（b/s 兩通道）

```
通道 A: (b/c @3GeV) × (c/s Nf=4)  = 4.586 × 11.652 = 53.436 ± 0.329
通道 B: M^RGI_b / M^RGI_s        = 6938/130.0    = 53.369 ± 0.737
dev = 0.13%    z = +0.08   ⟹ 閉環 PASS
```

- 呢個係**觀測層自身一致性審計**（FLAG 內部），唔係 IDCM 測試；
- 但佢令凍結層 quark 約束由 4+2 變 5 個互相獨立可查嘅比（d/u, s/u, c/s, b/c, b/s），
  redundancy = 1（之前 0）⟹ 任何一個量新值，可以由餘者交叉預言（LOOCV 有嘢做喇）。

## 四、純 γ u/d 雙通道（鏈譜唯一可檢驗點，而家有兩把尺）

| 通道 | d/u 觀測 | 純γ γ3/γ2 = 2.2452 | z |
|:--|:--|:--|:--|
| MS @2GeV (round 1) | 2.1505 ± 0.111 | 差 +4.4% | +0.85 |
| RGI (round 3) | 2.1987 ± 0.092 | 差 +2.1% | +0.51 |

**兩通道獨立地過**（RGI 框架嚟自 Eqs.44 嘅 M_u/M_d, 同 MS 通道數據重疊有限）——
純 γ 層最穩陣嘅現存測試, 而家係「雙尺通過」。

## 五、C-shape v2（scheme 更正完成）

```
夸克: u=1.000  d=0.958  s=10.777  c=41.585  b=79.645
輕子: e=1.000  μ=8.356  τ=44.418
```
- b 由 round-2 嘅 57.16 升至 79.65（scheme 更正 39%）；其餘不变
- 自洽: C_b/C_s 經 RGI = 7.381 vs 經 b/c×c/s = 7.390 → dev 0.13%

## 六、★★ pre-registered 預言 register（可證偽預言清單）

凍結層 v2 規則: **未來任何新量度，先對表，唔准事後選 scheme**。每行 = 預言 + 觸發條件 + 判決機制:

| 預言 | 值 ± 誤差 | 觸發（新量度） | 判決 |
|:--|:--|:--|:--|
| md/mu (MS) | 2.1505 ± 0.111 | lattice 1–2% mu/md | 純γ 2.2452 vs shape 2.1505 相隔 4.4% → 1–2% 精度即裁決純γ vs C-shape |
| **ms/mu（killer）** | **42.89 ± 1.52** | lattice 直量 1% | 唯一非 assignment 內含; 1% ≪ 3.5% 誤差 → 一擊即決 |
| ms/md | 19.944 ± 0.332 | lattice 直量 | 同上架構 |
| mc/mu | 499.75 ± 17.89 | lattice 直量 mc/mu | |
| mc/md | 232.39 ± 14.60 | lattice 直量 | |
| mb/ms (RGI) | 53.369 ± 0.737 | RGI 第二通道 | 已閉環 z=+0.08（現存） |
| mb/mc (3GeV) | 4.586 ± 0.012 | 已凍結 | scheme 正確; C_b/C_c=1.916 池無命中 |
| RGI d/u | 2.1987 ± 0.092 | 已凍結 | 純γ z=+0.51 |

**預言行嘅結構地位**: C-shape 已被凍結層釘死（shape DOF=0, round-2）⟹
任何新比嘅預言值**冇自由參數**（全部由凍結量決定）⟹ 每個未來量度都係完整 out-of-sample 測試。

## 七、開放問題（round-3 之後）

```
✅ 三條待辦全部完成（RGI_b 入層 / mc-ms 決策 / 1% ms/mu 預研→預言 register）
🟡 freeze v2 生效; 舊 data/01 保留(v1) 唔改（append-only）; 新量度一律入 v2 對表
🔴 O233 C 池匹配分析（若重啟）必須用 freeze v2 同 scheme 比（b/c 43.6% 反例）
🔴 IDCM 側冇新增: 質量公式仍然只有一個可證偽內容（純γ u/d 雙尺）; C 生成器仍缺（O233 負）
```
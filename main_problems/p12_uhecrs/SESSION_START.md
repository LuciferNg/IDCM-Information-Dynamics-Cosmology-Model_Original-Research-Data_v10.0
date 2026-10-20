# P12 SESSION_START — UHECR 超高能宇宙射線（晶體應力釋放詳情）

<!-- registry
pid:     uhecrs
title:   UHECR 超高能宇宙射線（晶體應力釋放詳情）
state:   open
verdict: -
flags:   -
owner:   uhecrs
created: 2026-10-05
updated: 2026-10-20
prereq:  O7, O110, O121, O173
source:  遷移自 open_problems_fresh/crystal_stress/uhecrs（2026-09-27 分拆；register 2026-10-05）
-->

> **Session**: 2026-10-18（結構重整 session——非研究攻堅）
> **狀態**: 🔴 開放（register 權威；主體閉合屬 P5）｜**階段閉合 2026-10-20**（內部推項清零，剩等數據）
> **來源**: P5 crystal_stress SESSION_START（2026-10-17）交接建議 → 本 session
> **前置**: O7, O110, O121, O173
> **位置**: `main_problems/p12_uhecrs/`

---

## 一、接手起點

P12 = UHECR 詳情目錄（2026-09-27 由 P5 分拆）。之前未入 git（untracked），結構唔合慣例（得 records/，冇 root 四檔）。
本 session（2026-10-18）已完成：records/→docs/、root 建 README / 01_problem_record / SESSION_START / final_result、
register 同步（O7/O110/O121/O173 交接 + P12_REF_FIX 翻譯層）、git 提交。研究內容本身未開工。

P5 交接建議（2026-10-17, docs/08）：**CluMPR 3.0° p 改 Gaussian 估計 + 更密 inner grid** 係「確認性」工作，
已 clamp 保守報導，唔影響 4.69σ 結論——屬可選，非緊急。

## 二、先做嘅第一步

```
1. 已讀 docs/03_uhecrs_record.md（主記錄）+ docs/05_psz1_vacuum_result.md（真空 3.43σ）——結論齊
2. 若開研究攻堅：先讀 P5 docs/08_routes_2_3_execution.md + scripts/17-19（路線 2+3 執行記錄），
   再做 CluMPR 3.0° Gaussian p 重估（scripts/17 同款管線）
3. register 狀態以 problem_register 為準；docs 改動後跑 idcm_problem_find reindex
```

## 三、已知陷阱

```
⚠️ 結構已變（2026-10-18）：records/ 已搬去 docs/；舊 ref 指向 records/ 由 P12_REF_FIX 翻譯層承接，
   唔好再開 records/（會製造新 REF-MISSING）
⚠️ data/ 同 stdout 一致性：任何重跑後 json 數字對唔上要修正（唔准留矛盾）
⚠️ 跨 O 引用數字核歸一化：本目錄結論（2.18% / 1.08% / 3.43σ / 3.99σ / 4.69σ）以 P5 docs/08 為最新權威
⚠️ 時序潔癖：新發現只可 append，唔准改 docs/03/05 舊結論
⚠️ 全譜缺口屬 O110，唔好喺 P12 內扮閉合低能段
```

## 四、關鍵數字

| 量 | 值 | 出處 |
|:---|:---|:-----|
| λ_min（晶格承載極限） | L_P·φ⁴⁴ = 2.535×10⁻²⁶ m | docs/03 §2.1 |
| E_GZK = hc/λ_min | 4.891×10¹⁹ eV（GZK 偏差 2.18%） | docs/03 §2.2 |
| E_max = 4φ·E_GZK | 3.166×10²⁰ eV（OMG 上限 1.08%） | docs/03 §2.3 |
| 證偽線 | >316.6 EeV 確認事件 → IDCM 錯 | docs/03 §3 |
| Auger 各向異性（109 events） | Fisher 2.66σ / 能量加權 3.99σ | docs/03 §4.3 |
| 節點核心真空（4 目錄） | Fisher4 p=0.0003 = 3.43σ | docs/05 |
| DESI 第 5 重（P5, 10-17） | Fisher5 = 4.69σ；2.0° z=7.72σ | P5 docs/08 |
| 盲測功效 | N_for_5σ = 53（雙比例） | P5 docs/08 |
| A₅ 節點 | 60 個（±8°）｜阻挫邊：32 條（±5°） | docs/03 §4.1 |

## 五、交接 / 依賴

```
- 前置: O7（阻挫邊重聯機制）→ O173（應變能池）→ O121（返池 f_UHECR=0.8028）→ O110（全譜缺口）
- 移交出: P5（主體閉合 45/45 + 路線 1/4 預註冊）；P14（相位滑移 = 寫入端）
- 範圍警告: LRD → P11；低能段全譜 → O110；偏振 mask 技術規格 → P5（10-17 已凍結）
```

---

> ⚠️ **本檔係起手式快照，唔係狀態權威。**
> 當前狀態以 register 為準；生命週期事件以 `problem_register/` 為準。

---

## 2026-10-18 — 路線 2 精化攻堅（本 session）

**任務**: P5 交接建議 — CluMPR 3.0° p 改 Gaussian 估計 + 更密 inner grid。**已執行**。

- `scripts/22_desi_inner_grid_gaussian.py`（N_MC=6000, 352s）：radii 1.0–3.5 step 0.25 +
  4.0/4.5/5.0 對照；Gaussianity KS 全過（p∈[0.28,0.80]）；真空核氹 1.0°→2.0° 升
  （z 4.18→7.61）、2.0°→5.0° 降（7.61→4.57）；**Z最深 r=2.0°**（探索性）
- `scripts/23_desi_exact_binomial_validation.py`：exact Binomial CDF 做 Gold Standard —
  與 Gaussian 尾互證（3.0°: 1.242e-5 vs 1.25e-5；2.0°: 9.2e-15 vs 1.39e-14）→ 唔係 method artifact
- **Fisher5 更新**: clamp 2e-4（4.694σ）→ **exact@3.0° 指定點 = 1.242e-5 ⟹ 5.153σ**
  （3.0° 係 P5 交接事前指定嘅報告點 → 冇 look-elsewhere 懲罰；clamp 低估咗 0.46σ）
- 記錄: `docs/06_desi_inner_grid_gaussian.md`；輸出: `data/reverify_desi_inner_grid.json` +
  `data/reverify_desi_exact_p.json`

**剩餘（等數據，無內部可推）**: AugerPrime 盲測（N_for_5σ=53）；CMB-S4/SO 偏振（mask 已凍結）；
Euclid DR1（2026-11-12）；O110 全譜缺口。

---

## 2026-10-18 — 路線 3 補完（同 session 續段）

> 附註：本檔 §一 header 早段寫「結構重整 session——非研究攻堅」；同日續段已做路線 2 同路線 3，
> 實際係研究 session。原句保留（append-only）。

**任務**: docs/03 §4.1 第二個幾何預言（**32 阻挫邊 ±5°**）從未做過正式統計檢驗（舊 script 07 只有
描述性 d_edge + 硬編碼失效路徑）；docs/03 §4.3 低能段避開節點亦未正式化。

- `scripts/24_edge_auger_formal_test.py`（修正幾何後重跑 ✅）: 全樣本 + 4 能量層（46/100/130/150）
  邊距離 MC null（scramble RA keep dec, seed 42, N_MC=5000）→ **冇任何層顯著**（全部 p>0.09）
- `scripts/25_frustration_edge_verdict.py`（條件化判決 ✅）: 條件化 edge-only 19/68 = 27.9%
  vs 條件化 MC 25.8%±5.0%（p_excess=0.325）；三分區分解：節點帶 +1.40σ / 邊中段 −0.07σ /
  其餘 −1.24σ，聯合 χ²=2.10 (df=2) p=0.350
- ⚠️ **首輪兩個方法 bug 已修正重跑**（① 球面弧內容判定寫錯 → 邊帶誤縮成節點帶；② 條件化不對等
  → 假 deficit）。詳見 `docs/07` §三。舊讀數「edge-only 0/68、p=4.8e-10」**已撤銷，不得引用**。
- 低能段 46-80 EeV: 0/14 vs MC 4.0±1.7 → 單尾 **p=0.0090**；80+ EeV 段 43.2%
- `scripts/26_lee_correction.py`（LEE 校正 ✅）: family-wise max-statistic null（4 層 × 2 窗, |F|=8）
  → 節點側最強點（80-100 EeV <8°, z=+2.37）naive 0.0160 → **校正 0.0848（唔顯著）**；
  低能避開（−z=2.38）naive 0.0070 → **校正 0.0080（仍顯著）** ⟹ 唯一過校正嘅訊號 = 低能避開
- 記錄: `docs/07`（§4 + §4.5 + §六局限）；輸出: `data/lee_correction.json`
- `scripts/27_ra_exposure_null.py`（RA 曝光硬化 ✅）: RA 邊緣平坦度三重檢驗全過（Rayleigh p=0.964 /
  χ² p=0.980 / KS p=0.959）；實證-RA null（從觀測邊緣抽樣 keep-dec, seed 44）對照 uniform-RA（seed 43）：
  節點帶 0.093/0.172、邊帶 0.091/0.181（兩空都唔顯著）、低能避開 0.0060/0.0094（**兩空都顯著**）、
  family LEE 0.070/0.135（都唔過）⟹ 結論對 RA 曝光假設穩健
- 記錄: `docs/07` §4.6 + §六局限(3) 已標記硬化；輸出: `data/ra_exposure_null.json`
- **判決**: 🔴 32 阻挫邊方向預言 **否證**（四個獨立角度全部落 null）；🟡 60 節點 ±8° 邊際支持（+1.40σ）
- 記錄: `docs/07_frustration_edge_and_lowenergy.md`；輸出: `data/edge_auger_and_lowenergy.json`,
  `data/frustration_edge_verdict.json`
- 副作用發現（integrity）: **12/25 本目錄歷史 scripts 含失效硬編碼路徑**（`~/Projects/IDCM/IDCM-v10.0/`
  只剩 Sep-8 殘殼）→ 不可直接重跑；依時序潔癖**不修改歷史 scripts**，重驗走 P5 scripts/10-16 或本目錄 22-25

**剩餘（等數據，無內部可推）**: AugerPrime 盲測（N_for_5σ=53）；CMB-S4/SO 偏振；Euclid DR1（2026-11-12）；
O110 全譜缺口；look-elsewhere 校正 / RA 曝光非均勻 null（方法論，非數據）。
> ⚠️ 更正附註（2026-10-20, append-only）：**look-elsewhere 校正已收口**（script 26 → docs/07 §4.5）；
> 剩餘方法論項只剩 RA 曝光非均勻 null。
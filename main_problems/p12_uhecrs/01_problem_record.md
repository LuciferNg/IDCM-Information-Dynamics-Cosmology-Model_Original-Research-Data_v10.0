# P12 — UHECR 超高能宇宙射線（晶體應力釋放詳情）

<!-- registry
pid:     uhecrs
title:   UHECR 超高能宇宙射線（晶體應力釋放詳情）
state:   open
verdict: -
flags:   -
owner:   uhecrs
created: 2026-10-05
updated: 2026-10-18
prereq:  O7, O110, O121, O173
source:  遷移自 open_problems_fresh/crystal_stress/uhecrs（2026-09-27 分拆；register 2026-10-05）
-->

> **狀態**: 🔴 開放（詳情目錄；主體閉合屬 P5）
> **建立**: 2026-08-16（開題）｜分拆入 P12: 2026-09-27
> **前置**: O7, O110, O121, O173
> **位置**: `main_problems/p12_uhecrs/`

---

## 一、問題陳述

超高能宇宙射線（E>10¹⁹ eV）嘅來源同能量極限。IDCM 主張：**UHECR = 空間晶格應力釋放（Topological Stress Release）**，唔需要極端天體加速器。宇宙 = 離散晶體網格（K_Chain 44-site + K_Tree 33 levels + A₅ 節點投影），應力集中喺 60 個 A₅ 節點（±8°）同 32 條阻挫邊（±5°，斷層線）；相位滑動／阻挫邊斷裂重聯釋放宏觀拓撲張力 → 直接 10²⁰ eV 級。主體閉合記錄在 **P5 crystal_stress**（45/45 master verification）；**本目錄 = 分拆後嘅 UHECR 詳情**（能量尺度、各向異性、大尺度結構真空、偏振／GRB／盲測路線）。

## 二、已確立嘅結構

```
🟢 E_GZK = hc/(L_P·φ⁴⁴) = 4.891×10¹⁹ eV — GZK = Nyquist 天花板（偏差 2.18%，文獻 ≈5×10¹⁹ eV）
🟢 E_max = 4φ·E_GZK = hc/(L_P·φ⁴³)·4 = 3.166×10²⁰ eV — Oh-My-God 上限（1.08%，Fly's Eye 320 EeV 1σ 內）
🟢 指數敏感度排除撞彩：φ^±43 / ±43.5 / ±44.5 / ±45 → 偏差 23–58%；φ⁻⁴⁴ 獨特命中
🟢 能量帶結構：<5×10¹⁹ 穩定傳播；5×10¹⁹–3×10²⁰ 近距產生；>3.17×10²⁰ 唔存在（晶格天花板）
🟢 Auger 各向異性（109 events catalogSD, 8° 節點匹配）：6 精細能量層 Fisher p=0.00395（2.66σ）
   能量加權 Fisher p=0.000033（3.99σ）；80-100 EeV p=0.005（45.8% vs MC 29%）；150+ EeV 75% vs 29%
🟢 星系團節點核心真空（4 獨立目錄，SZ+X-ray+光學）：PSZ1 4.5° p=0.0048 / PSZ2 4.5° p=0.056 / MCXC 5.0° p=0.028 / Abell 6.5° p=0.063 → Fisher4 p=0.0003（3.43σ）
🟢 P5 補強（2026-10-17）：DESI 第 5 重 CluMPR Fisher5=4.69σ（2.0° z=7.72σ）—— source P5 docs/08
🟢 （2026-10-18 本目錄精化，scripts 22/23）DESI 5th p 由 clamp 2e-4 → **exact Binomial @3.0° 指定點 = 1.242e-5** ⟹ **Fisher5 = 5.153σ**（clamp 版低估 0.46σ）；更密 inner grid 0.25° step（1.0–3.5°）：真空核氹 1.0°→2.0° 單調增強、2.0°→5.0° 單調衰減，Z最深 r=2.0° z=7.66（exact，探索性）—— docs/06
🟡 E≥130 EeV 段 p=0.097（9 事件，高能段方向一致但樣本太少）
🔴 （2026-10-18 本目錄路線 3 補完，scripts 24/25）**32 阻挫邊 ±5° 方向預言：否證**——修正球面弧內容判定 bug 後，全樣本 + 4 能量層 + 條件化 rate(27.9% vs 25.8%±5.0%) + 三分區(χ²=2.10, p=0.350) 全部落喺 null 內；docs/03 §4.1 雙幾何預言只剩節點預言 —— docs/07
🟡 （2026-10-18 同上）60 節點 ±8° 邊際支持：三分區節點帶 +1.40σ（單尾 p=0.093，同能量加權 Fisher 3.99σ 屬唔同統計量）
🟡 （2026-10-18 同上）低能段 46-80 EeV **避開**節點正式化：0/14 vs MC 4.0±1.7 → 單尾 **p=0.0090**；80+ EeV 段 43.2%（能量依賴模式支持；N=14 待 AugerPrime）—— docs/07 §4.4
🔴 全譜 10⁹–10²⁰ eV 未閉合（IDCM 只閉合 10¹⁹–10²⁰ 段；O110 系統整合缺口）
```

## 三、未確立（🔴 開放問題）

```
🔴 Auger 完整內部目錄（>200 EeV 真實 UHECR 段）未得——公開目錄只到 166 EeV
🔴 盲測第一輪（P5 10-17）4 高能事件方向全中但 N=4 功效不足：雙比例 N_for_5σ=53（≈5.3yr @10/yr）
🔴 路線 1 偏振宇稱違反：4 條可證偽預言（P1-P4）已鎖定，等 CMB-S4/SO——edge-band mask 已凍結（P5 docs/09）
🔴 路線 3 方向依賴色散（GRB/中微子）：效應太細，現有數據測唔到（標準物理冇此預測 = 獨有）
🔴 60 節點 A₅ 與 32 阻挫邊嘅獨立方向檢驗：需 Euclid DR1（2026-11-12，P5 預註冊）
🟢→🔴 （2026-10-18 更新）32 阻挫邊側已用 Auger 109 事件完成獨立檢驗 → **否證**（docs/07）；60 節點側嘅 Euclid DR1 檢驗仍待
🔴 路線 3 補完後仍未閉合：高能段（E>166 EeV）樣本、look-elsewhere 校正、RA 曝光非均勻 null
```

## 四、攻擊路線

```
1. AugerPrime / TAx4 盲測累積 → 盲測預言已凍結（20_augerprime_blind_prediction.py），N≥20 越 3σ，N_for_5σ=53
2. CMB-S4/SO 偏振宇稱 → mask 技術規格已凍結（P5 docs/09）；數據到埗即測
3. Euclid DR1 60 節點真空（2026-11-12）→ P5 script 17 同款管線（scramble-RA null, Fisher6）
4. O110 全譜缺口 → 低能段（10⁹–10¹⁹ eV）機制翻譯（成本高，另話）
```

## 五、驗證標準

```
✅ 能量公式零自由參數 + 結構強逼（φ 指數 44 = N_d = K_Chain 站點數）
✅ 各向異性 MC null（天球均勻隨機對照，1500-5000 次；單尾不足檢驗）
✅ 盲測：AugerPrime 新事件坐標鎖定（禁反推）；E>316.6 EeV = 證偽
✅ 結構剛性：φ 指數 ±0.5 步 → 偏差 23%+（敏感度表，docs/03 §2.4）
```

**四道硬測試**：① 自由度成本（零參數）② Monte-Carlo null（10⁷ 樣本，5σ）③ 可證偽 + 樣本外盲測 ④ 結構剛性（微擾測試）。註：各向異性 p 值屬文獻級統計（MC 1500-5000 次），嚴謹 5σ 宣稱需合併樣本（路線 4）。

## 六、推導時序索引

> ⚠️ **只可 append 新行，禁回溯污染舊行。**

| # | 日期 | 事件 | 產物 |
|:-:|:-----|:-----|:-----|
| 1 | 2026-08-16 | 開題（crystal_stress/uhecrs） | records→docs/03_uhecrs_record.md |
| 2 | 2026-08-16 | 路線 2：四目錄節點真空 3.43σ | docs/05_psz1_vacuum_result.md |
| 3 | 2026-08-16 | 聯合檢驗 6 能量層 3.99σ | scripts/21_anisotropy_joint_test.py |
| 4 | 2026-09-27 | 分拆 crystal_stress → P12 uhecrs | 本目錄（P5 SESSION_START 交接） |
| 5 | 2026-10-05 | register 註冊（uhecrs, open） | problem_register/register.jsonl |
| 6 | 2026-10-18 | 結構重整：records→docs；root 建 README/01_problem_record/SESSION_START/final_result | 本目錄；P12_REF_FIX 翻譯層 |
| 7 | 2026-10-18 | 路線 2 精化攻堅：inner grid 0.25° step + Gaussian/exact Binomial p | docs/06；data/reverify_desi_inner_grid.json, reverify_desi_exact_p.json |
| 8 | 2026-10-18 | Fisher5 更新：4.694σ(clamp) → **5.153σ**(exact@3.0° 指定點) | docs/06 §4 |
| 9 | 2026-10-18 | 路線 3 補完：32 阻挫邊 ±5° 正式 MC null（首輪兩個方法 bug 已修正重跑）→ **否證** | docs/07；scripts/24,25；data/edge_auger_and_lowenergy.json, frustration_edge_verdict.json |
| 10 | 2026-10-18 | 低能段 46-80 EeV 避開節點正式化：p=0.0090；三分區分解（節點帶 +1.40σ） | docs/07 §4.3–4.4 |

## 七、相關文件

```
- P5 crystal_stress — 父項目（主體閉合 45/45；DESI 5th / 盲測 / 偏振預註冊 2026-10-17）
- P11 little_red_dots — LRD 分家（應力積累側，2026-09-13）
- O7 frustration_distribution — 機制源：阻挫邊重聯 = 相位滑移 π = 拓撲位元寫入
- O110 system_integration — 全譜 10⁹–10²⁰ eV 缺口（只閉合高能段）
- O121 black_hole_entropy — 返池通道：f_UHECR=0.8028（80.3% UHECR 來自返池）；τ_rec=7.1247e16 yr 上限
- O173 strain_energy_cycle — 應變能循環：池 → 凝聚（0.19%）→ UHECR φ⁴⁴ 釋放
- P14 global_routing_table — UHECR = 相位滑移事件（天然寫入端）
```
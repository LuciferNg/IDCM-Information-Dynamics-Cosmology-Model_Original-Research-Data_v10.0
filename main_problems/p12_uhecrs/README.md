# P12 — uhecrs（UHECR 超高能宇宙射線）

## 狀態: 🟢 主體已閉合（P5 45/45）/ 🟡 詳情等數據（AugerPrime / CMB-S4/SO / Euclid DR1）

**UHECR = 空間晶格應力釋放**（Topological Stress Release）：宇宙 = 88-site 對偶鏈晶格（K_chain ⊗ K_tree），
60 個 A₅ 節點 + 32 條阻挫邊係應力集中點；相位滑動／阻挫邊重聯一次性釋放 10²⁰ eV 級，唔使逐次加速。
GZK = Nyquist 天花板（2.18%）、Oh-My-God 上限（1.08%）、Auger 各向異性（3.99σ）、星系團節點真空（3.43σ）——全部零自由參數。
主體閉合屬 **P5**；本目錄 = 分拆後嘅詳情（能量尺度敏感度、各向異性掃描、LSS 真空、偏振／GRB／盲測路線）。

## 檔案

| 檔案 | 描述 | 狀態 |
|:----|:-----|:----:|
| `01_problem_record.md` | 問題陳述 + 已確立結構 + 開放問題 + 攻堅路線 | 🟢 |
| `docs/03_uhecrs_record.md` | 主記錄：能量尺度 + 各向異性 + 可證偽預言 | 🟢 |
| `docs/05_psz1_vacuum_result.md` | 路線 2：四目錄節點核心真空 3.43σ | 🟢 |
| `SESSION_START.md` | 起手式 + 交接（下一 session 起點） | 🟢 |
| `final_result.md` | 結論摘要（RESULT_TEMPLATE 格式） | 🟢 |
| `scripts/01-21` | 能量尺度 / GZK / 各向異性 / LSS / 偏振 / 盲測 21 支 | 🟢（歷史，重驗見 P5 scripts/10-16） |
| `data/` | Auger 目錄 + 掃描輸出（19 份 json/csv） | 🟢 |

## 依賴

IDCM-v10.0（K_chain ⊗ K_tree）→ O140 FSR → **P5 crystal_stress** → **P12 uhecrs**（UHECR 詳情，2026-09-27 分拆）＋ P11 little_red_dots（LRD，2026-09-13 分家）
O-series 同步：O7（阻挫邊重聯機制）· O110（全譜缺口）· O121（返池 f_UHECR=0.8028）· O173（應變能循環 φ⁴⁴ 釋放）→ 已 register handoff 入本問題（2026-10-18）

## 來源

- 原 `open_problems_fresh/crystal_stress/uhecrs/`（2026-08-16 開題）；2026-09-27 分拆 → `main_problems/p12_uhecrs/`；`records/` → `docs/`（2026-10-18）
- 重驗：P5 `scripts/00_master_verification.py` 45/45 + scripts/10-16（2026-09-27）；DESI 第 5 重 F5=4.69σ（2026-10-17, P5 docs/08）
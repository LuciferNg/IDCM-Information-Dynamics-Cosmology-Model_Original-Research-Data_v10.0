# P5 — crystal_stress（晶體應力：UHECR + 小紅點）

## 狀態: 已閉合（核心 UHECR）/ 部分閉合（環境/微觀）/ 等數據

**IDCM v10.0「宇宙晶體」應力釋放問題**：宇宙 = 88-site 對偶鏈晶格
（K_chain ⊗ K_tree），晶格應力集中喺 60 個 A₅ 節點 + 32 條阻挫邊。
**應力釋放 = UHECR**（GZK = Nyquist 天花板 2.18%；Oh-My-God 上限 1.08%；
Auger 各向異性 3.99σ；星系團節點核心真空 3.43σ）；**應力積累 = 小紅點**（已分家 → P11）。

主體 UHECR 已閉合：`scripts/00_master_verification.py` **45/45 PASS**，
2026-09-27 全量重驗（scripts/10-16）。剩餘路線（2026-10-17 執行後）：
**① CMB 偏振宇稱違反 ✅已預註冊**（32 阻挫邊 edge-band mask 凍結, docs/09；等 CMB-S4/SO 數據）、
**② DESI 第 5 重 ✅ 已執行**
（CluMPR 2024 光度團, 非 DESI DR2 光譜——見 docs/08；**Fisher5=4.69σ, 2.0° z=7.72σ**）、
**③ 盲測第一輪 ✅**
（4 事件方向全中但 N<20 未達否證門檻，功效表已修正）、**④ Euclid ✅已預註冊**
（歸屬 P5；等 DR1 2026-11-12——docs/09）。**P9′** 等 AugerPrime (2035)。

## 檔案

| 檔案 | 描述 | 狀態 |
|:----|:-----|:----:|
| `01_problem_record.md` | 問題陳述 + 已確立結構 + 開放問題 + 攻堅路線 | 🟢 |
| `docs/04_master_summary.md` | 主體推導總結（45/45 全量重驗） | 🟢 |
| `docs/06_gemini_insight_analysis.md` | Gemini 洞察分析（洞察 4 已由 LRD 八輪閉合） | 🟡 |
| `docs/07_o169_correction_reverify.md` | O169 伸長律修正重驗（`E(ℓ)=ℓ+1.11911398`） | ✅ |
| `docs/08_routes_2_3_execution.md` | 路線 2+3 執行記錄（DESI 第 5 重 + 盲測 + 功效修正） | ✅ |
| `SESSION_START.md` | 起手式 + 交接（下一 session 起點） | 🟢 |
| `final_result.md` | 結論摘要（RESULT_TEMPLATE 格式 + 重驗註記） | 🟢 |
| `scripts/00,01` | 歷史綜合驗證（不修改，保留） | 🟢 |
| `scripts/02,10-16` | O169 修正 + 全量重驗劇本（2026-09-27） | ✅ |
| `scripts/17,18` | 路線 2+3 執行劇本（DESI 第 5 重 / 盲測 + 功效修正, 2026-10-17） | ✅ |
| `data/` | 4 星系團目錄 .npz + CluMPR 2024 fits + 8 份 reverify_*.json 輸出 | ✅ |

## 依賴

IDCM-v10.0（K_chain ⊗ K_tree）→ O140 FSR → **P5 crystal_stress**
→ P11 little_red_dots（LRD，2026-09-13 分家）→ P12 uhecrs（UHECR 詳細，2026-09-27 分拆）

## 來源

- 原 `open_problems_fresh/crystal_stress/`（2026-08-16 開題）；git mv → `main_problems/p5_crystal_stress/`；`records/` → `docs/`（2026-09-27）
- LRD 詳情：`main_problems/p11_little_red_dots/`；UHECR 詳情：`main_problems/p12_uhecrs/`
# O120 — Closeout Record（收尾 + 交接處理）

> **日期**: 2026-10-06（HKT）
> **狀態**: 🟢 **診斷性閉合（Diagnostic Closure）**
> **驗證**: `scripts/01_verify_all.py` **35/35**（logs/01_verify_all.out）· `scripts/02_audit_independent.py` **78/78**（logs/02_audit_independent.out）
> **性質**: 本檔為新增記錄（docs/01-03 原檔零改動；`docs/01_problem_record.md` 只作路徑指標）
> **範圍**: 只寫入 `o120_light_quark_masses/` + `open_problems_fresh/README.md` 本 O 行 + `problem_register/`（交接，SS8）

---

## 1. Verdict — 為何係「診斷性閉合」而唔係 🟡 / 🔀

依 skill `idcm-closeout` §6.2.8，只有診斷存活時 close 為 DIAGNOSTIC closure。三個存活診斷：

1. **u/d 質量數值閉合成立**（三框架，全部 <2.05%）—— 由第一性原理重算確認（§3）；
2. **原問題「n=1 三態 (e,u,d) 靠 P_f={3.6, 15.5, 33} 分化」有確定答案** —— P_f 係 zombie：
   O136 方向二 search 產物 + O136 自身 docs/34 已判其模式分配 P=0.8525（比隨機更差）、
   A₅ 集 P=0.0155 為唯一統計支持；本輪另由兩條獨立判準（全息保護 + O209 閾值定理）
   交叉確認合法模式集 = {1,2,3,4,5,7,9,11,13}，而 O136/O120 指派之 s/c/b 模式
   {14,33,34} **全部超出**（§4）；
3. **新結構訊號（密度控制）**：A₅ 質量升序指派下，第一代 C_f 跨度 = **1.058**，
   係全部 C(9,3)=84 個三子集嘅**唯一最小值**（rank 1/84, p=0.0119, 多 seed MC 確認）
   ——「第一代坐純 γ-階梯」係真實 (~2.5σ) 結構事實（§5），O120 之前冇記錄過。

**為何唔 🟡**：O 嘅問題陳述已有確定裁決（P_f 被取代／排除），冇屬於本 O 之未決項；
真正殘餘（C_f 生成器，2149× 跨度）已由 O137 docs/37 裁決歸 **O206**（O221→O206 併入），
留 O120 🟡 = 重複 O206 已註冊開放項。
**為何唔 🔀 併 O136**：O136 自身係 🔴 審計後（方向二證偽），且其模式指派 {14,33,34} 同被排除；
殘餘歸屬 O206 先於一切（O137 docs/37 §十二）。

---

## 2. 檔案閉合水位（T0）

| # | 檔案 | 上次檔案更新 (mtime) | 上次 closed-out | 已驗範圍 | 狀態 |
|:-:|:-----|:---------------------|:----------------|:---------|:-----|
| 1 | SESSION_START.md | 2026-09-03 14:53 | —（首次） | 全文 | ✅ 已驗（append closeout 節） |
| 2 | docs/01_problem_record.md | 2026-09-20 01:38 | —（首次） | 全文；已搬 root（byte-identical） | ✅ 已驗 |
| 3 | docs/02_findings.md | 2026-09-03 14:55 | —（首次） | 全文 | ✅ 已驗 |
| 4 | docs/03_verification_trail.md | 2026-09-20 01:38 | —（首次） | 全文 | ✅ 已驗 |
| 5 | final_result.md | 2026-09-20 01:40 | —（首次） | 全文；重寫至最終狀態 | ✅ 已驗 |
| 6 | scripts/01_verify_all.py | 2026-09-20 01:31 | —（首次） | 全文；重跑 35/35 | ✅ 已驗 |
| 7 | scripts/02_audit_independent.py | 2026-10-06（新） | — | 新建 78/78 | ✅ 已驗 |
| 8 | data/ | 2026-08-29 07:08 | — | 空目錄（無產物） | ✅ 不適用 |

> mtime 全數 ≤ 2026-09-20（本輪新增除外）；git 未追蹤（首次 commit = 本輪）。無跨 session 寫入跡象。

## 3. 三框架數值重驗（T1/T2，零 import 重算）

| 框架 | m_u | m_d | 出處 |
|:--|:--:|:--:|:--|
| A. v9.0 第一代 Fₙ/CY₃ˢ | 2.1711 MeV (0.5125%) | 4.6511 MeV (0.4043%) | docs/02 §1.1 |
| B. O136 M₀γ_nP_f | 2.203738 MeV (2.0249%) | 4.691830 MeV (0.4675%) | JSON 對照一致 |
| C. up_quark_correction | 2.1702 MeV (0.4720%) | 4.6586 MeV (0.2443%) | docs/03 §1.4 |
| m_u/m_d = 15.5/33 | 0.469697 vs 0.462527 | Δ **1.5502%** | docs/02 Q4 |

O54 交叉：m_μ = M₀γ₇×15.5 → 0.1315%；m_e = M₀γ₁×3.6 → 0.1638%。O136 JSON 9 費米子
指派（u n=1 P=15.5 / d n=1 P=33 / e n=1 P=3.6 / μ n=7 P=15.5 / τ n=20 P=37 / s n=14 P=3.6
/ c n=34 P=13 / b n=33 P=44）全部一致。費米子反週期 nL≡44 (mod 88) 6/6。

## 4. ★★ 模式集 / P_f 基礎裁決（新檢定）

```
判準① 全息保護 (H_NZ 判準)      = {1,2,3,4,5,7,9,11,13}
判準② O209 閾值定理 Sel(S)      = {1,2,3,4,5,7,9,11,13}   （兩判準逐元素一致）
O136/O120 之 s n=14, c n=34, b n=33 → 全部 NOT protected  （u/d n=1 合法）
O136 docs/34 統計裁決            : O120/O137 反週期集 P = 0.8525 🔴 / A₅ 集 P = 0.0155 ✅
密度基準 (O208)                   : 目錄 1..176 有 87 結構數 (49.4%)；整數 12..20 全在目錄
                                   ⟹ P_f={3.6,15.5,33} 之「目錄身份」零證據力
```

**裁決**: O120 嘅 P_f 三數目（3.6/15.5/33）係 O136 search 產物 + 高密度巧合；
「u,d 必須落 n=1 靠 P_f 分化」**被取代**（A₅ 指派 e,u,d → n=1,2,3 全合法，見 §5）。

## 5. ★★ 新結構訊號 — 第一代 γ-階梯（密度控制 null）

A₅ 質量升序指派（O137 R19 框架）之 C_f = m/(M₀γ_n)：

```
e n=1 → 3.5941   |  s n=4 → 41.3207  |  τ n=9  → 159.6437
u n=2 → 3.8029   | μ n=5 → 30.0309   |  b n=11 → 255.7517
d n=3 → 3.6620   |  c n=7 → 186.0605 |  t n=13 → 7722.8073
塊內跨度: gen1 = 1.058 · gen2 = 6.196 · gen3 = 48.375 · 全譜 = 2149×
```

**null（精確枚舉 + 多 seed MC）**：統計量 S = 塊內 C_f max/min；null = 9 質量隨機抽 3、
升序貼上該塊模式：
- gen1 S=1.0583 → **rank 1/84（p = 0.0119）**；MC seed {7,123,20260926} → p = 0.0119/0.0122/0.0126
- gen2 rank 3/84 (p=0.0357) · gen3 rank 16/84 (p=0.1905)

**預言測試**：若整代 C_f ≡ L₆/F₅ = 3.6 → m_e 0.164% ✅ / m_d 1.69% 🟡 / **m_u 5.34% 🔴**
（m_u 係殘餘：需 C_u/C_d = 1.038476 先令 m_u/m_d 精確閉合；純 γ₂/γ₃ 本身 3.705% off）。

## 6. 交接處理 — 其他 O 系列 → O120（incoming handoff receipt)

| 來源 | 交接項 | 原文位置 | 裁決 | 去向 |
|:--|:--|:--|:--|:--|
| **O86** | N4 夸克質量譜 (s,c,b,t)+d 列 🔴 | O86 `docs/04_open_problem_closure.md` L22 | 數值閉合成立：O136-08 s 0.78/c 0.29/b 0.27/t 0.68%/u 2.02🟡 d 0.47% 全 <5%；18-50% 聲稱已過時（O115 同判） | 已裁決（本輪） |
| **O134** | §5 第一代 F_n/CY₃ˢ → O120 擁有者 | O134 `docs/03_cross_o_coverage.md` L25 | O120 判「✅ 兼容 v10.0」核實（u 0.5125%/d 0.4043%）；三框架並存係重現非預言 — 加注成立 | 已裁決（本輪） |
| **O144** | QCD 質量預算：夸克質量未閉合 🔴 | O144 `docs/01_qcd_mass_budget.md` L35 | 同 O86 裁決；結構殘餘（C_f 生成器）→ O206 | 已裁決 + handoff → O206 |
| **O115** | README O120 行過時（🔴未開始 + 18-50%） | O115 `docs/01_open_series_audit.md` L79 | 本輪已更新 README 行 → 🟢 診斷性閉合 | 已處理 |
| **O136** | docs/34 交叉檢驗（第一代閉合 ✅ / 模式分配 P=0.8525 🔴 / P_f 框架無壓縮性 🔴） | O136 `docs/34_two_modesets_crosscheck.md` | 全部收錄：數值閉合確認 ✅；P_f 統計否定 → 反映於 verdict | 已收錄 |
| **O208** | 三源報告：A_SESSION_START 🟡 vs B_README 🔴 DIFF | O208 `data/03_three_source_report.json` L1680-84 | 已處理（README 行更新後三源一致） | 已處理 |
| **O219** | pt↔mode 審計掃描提及（非交接項） | O219 `data/02_scan.json` | 只係語料掃描，無 handoff；docs 0 命中 | 不適用 |

## 7. 殘餘 / 新問題（全部經 register，唔寫源 O 檔案）

1. **🔴 C_f 生成器**（供給 2149× 跨度）→ `register.py handoff O120 → O206`（O206 開放項 2，O221 已併入）
2. **🟡 第一代 γ-階梯定理**（C_f(gen1) ≡ L₆/F₅ 嘅機制；u 5.34% 殘餘）→ 同一 handoff 註明
   （O206 之「C_f 池 label 機制」範圍，唔開新 O）
3. **🚫 禁區**：P_f 路徑（lookup 表 3.6/15.5/33 式）禁止重推 —— O136 審計判過擬合 +
   O136 docs/34 P=0.8525 + 本輪密度 49.4% 三層否證。v7 α 式同屬禁區（見 MEMORY）。

## 8. 範圍核實（本次寫入清單）

```
o120_light_quark_masses/01_problem_record.md        （由 docs 搬遷 + append closeout 節）
o120_light_quark_masses/SESSION_START.md            （append closeout 狀態節，舊 32 行 byte-identical）
o120_light_quark_masses/final_result.md             （重寫至最終狀態，活摘要）
o120_light_quark_masses/docs/01_problem_record.md   （路徑指標，E7）
o120_light_quark_masses/docs/04_closeout_record.md  （本檔）
o120_light_quark_masses/scripts/02_audit_independent.py（新建）
o120_light_quark_masses/logs/01_verify_all.out      （重跑 log）
o120_light_quark_masses/logs/02_audit_independent.out（重跑 log）
open_problems_fresh/README.md                       （O120 單行更新 — 用戶明示處理交接）
problem_register/register.jsonl (+REGISTER.md)      （handoff/close 事件 — 交接管道）
```

**未觸碰**: o86/o134/o144/o115/o136/o137/o208/o219 任何檔案；docs/02、docs/03 零改動；
O136 `data/08_final_closure.json` 唯讀。

## 9. 時序完整性

- 全部既有檔 mtime ≤ 2026-09-20；本輪產物 2026-10-06。
- docs/02、docs/03 未含本輪關鍵詞（「診斷性閉合 / C_f 生成器 / A₅ 指派」回溯污染 grep = 0）。
- 開放問題結案表（原 problem_record「未閉合開放問題」L44-49 加注）見 root `01_problem_record.md`。
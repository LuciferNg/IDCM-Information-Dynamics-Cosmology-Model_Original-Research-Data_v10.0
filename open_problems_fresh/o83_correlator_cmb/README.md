# O83 — Correlator ⟨φφ⟩ ↔ C_ℓ

## 狀態: 🟡 部分閉合（2026-10-23 審計降級，原聲稱 🟢 58/58）

**IDCM v10.0 由 W-field propagator 推導 CMB 角功率譜嘅橋接層**：mode expansion
δT(Ω)=Σ c_n φ_n → C_ℓ = Σ w_n² G_n(0) δ_{ℓ,ℓ_n} → 峰位 ℓ_m = 44(M−C(9−m,2)) + 相位_m。
**形式成立、數值可重現，但內容（峰位/振幅）係 P3/O9 後驗值之代數重讀 — 唔係 O83 結構推導。**

**🟢 保留（真）**：G_n(0)=1/(2ω_n)≡1/(4sin(nπ/88)) 代數恆等；Σγ 精確和
（44-site=90；88-site 偶90/奇88/總178=2F₁₁，sympy）；橋接與熱態形式（Z_0(β)、E_0=45）。

**🟡 降級（審計 10-23）**：
- 「零自由參數 142/142」→ **實質 129 check**（11 個 `check(...,True)` 恆真項已改 📝 註記）
- 峰位 RMS 0.335% → **權威 0.84%**（O9 最終閉合矩陣 obs；0.34% 只屬 P3 舊 obs）
- 「ℓ_sync = 44 = 2N_d 結構恆等」→ **定義恆等**（λ_sync ≡ L_ring/88 = πR_world/44 = 294.8770）
- 「振幅由 propagator 推導」→ w_m ≡ √(A_m/G_m(0)) **反解**（A_m 係輸入，O9 自認事後揀最靚）
- m=5 `F₆=8/F₈=21` **硬寫後驗**

**驗證（2026-10-23 全量重跑）**：scripts/01–07 exit 0；`07_file_verifier.py` **77/77 PASS**；
`08_audit.py` 審計 **20 項：🟢13 / 🔴7**。詳細：`docs/03_audit_report.md`。

## 檔案
```
01_problem_record.md     問題記錄 (10-15 骨架 + 08-25 原文重建 §2026-10-23)
final_result.md          結論摘要 (🟡 partial)
SESSION_START.md         session 錨點 (含 10-02 外部審計 + 10-23 裁決)
docs/01_problem_record.md  10-15 覆蓋事件物證 (811 bytes, 唔改)
docs/02_derivation_record.md  08-25 推導記錄 + 10-23 更正附註
docs/03_audit_report.md   ★ 全量審計報告 (20 項, 證據齊)
scripts/01–06            推導腳本 (129 實質 check)
scripts/07_file_verifier.py  文檔完整性 verifier (77/77)
scripts/08_audit.py      審計腳本 (獨立重算 + AST 空洞掃描)
```

## 路徑
```
/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o83_correlator_cmb
（舊址 /home/wsl/Projects/IDCM/IDCM-v10.0/... 已冇 o83 ⟹ scripts 已全改相對路徑）
```

## 未閉合（跨 O 移交）
🟡 母函數生成規則 → O9/O48　🟡 m=5 F₆/F₈ → O9　🟡 m=2 obs 527 vs 537 → O9　🟡 w_n 獨立生成 → 新問題
📤 P3 標籤錯：`ℓ_sync = 2N_d`（N_d=44 ⟹ 2N_d=88）、`T_CMB (0.01%)`（實 0.104%）— register handoff 已立

## 缺口清單
**`docs/04_current_gaps.md`** — A 本 O 內 4（A1 `w_n` 無獨立生成★ / A2 密度基準未建 / A3 88-site 未接入 / A4 熱態未接振幅）／B 已發還 P3 ×2／C 跨 O 5（已 handoff O9 ×2）／D 非缺口 5。
register: **state=partial, verdict=partial**（2026-10-23）。

## 攻堅進展（2026-10-23）
**`docs/05_w_n_and_thermal_derivation.md`**
```
A1 🔴→🟡  b_k = B·a_k − F₅ (單參數族); a_k = {Z₂,N_gen,B}; 族 243,360 → distinct 1
A2 🔴→🟡  q_obs = 0.00041% (振幅族); 峯位族未掃
A4 🔴→🟢  熱佔據 < 10^(−3.7×10⁹) ⟹ C_ℓ 振幅 ≡ 真空 propagator
A5 🔴新   w_n 絕對歸一化 ((δT/T)² 結構式) — φ-power 陷阱 ⟹ 只登記未掃
```
`scripts/09_w_n_structural.py` 6/6 ／ `scripts/10_thermal_amplitude.py` 4/4 ／ `07_file_verifier` **83/83**

## 第二輪攻堅（2026-10-23）
**`docs/06_a3_a5_a6_attack.md`** — 真 Planck PR3 譜實讀，腳本 `11`(5/5) + `12`(6/6)
```
A3 🔴→🟢  λ_sync=L_ring/88 已接入定義層; W_A=W_B=22 恆1/2 (87/87) ⟹ 唔提供振幅自由度
A6 🟡新    級聯吻合 D_ℓ binned 比 (1.85%), C_ℓ 比差 7.17× ⟹ A_m ≡ D_ℓ 比, 度量因子結構未推
A5 🔴      ε⁵/8 需 14.57° 平滑 (非結構角); 7峰+γ49.5 方差不足 ⟹ 需全ℓ包絡
A3′🟡新    44 奇模 (observer sector) 觀測通道
🟢 定理    Niven ⟹ γ/ω/sin/cos 算子族永久排除; w_n² 只可由計數原子構成
```
`07_file_verifier` **87/87 PASS**（含 11/12）

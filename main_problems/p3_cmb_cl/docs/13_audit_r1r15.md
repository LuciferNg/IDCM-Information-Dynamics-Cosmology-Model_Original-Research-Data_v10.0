# P3 / AUDIT — 未審計產物全量審計（R1-R15，2026-10-22）

> **狀態**: ✅ 審計完成；🔴 **3 項記錄層錯誤已定讞**（R4 方法 artifact / R13 ghost claim / R15 誤讀）
> **範圍**: `scripts/09-23`（15 支，此前從未獨立審計）+ `docs/09-12`（4 份）+ `logs/09-23`
> **審計器**: `scripts/AUDIT_A_r1r12.py`、`AUDIT_B_r13r15.py`、`AUDIT_C_docs_register.py`（零 import 原推導 script）
> **判決總計**: A **32 PASS / 7 FAIL / 39**　B **19 PASS / 2 FAIL / 21**　C **28 PASS / 0 FAIL / 28**

---

## 0. T0 水位掃描（審計前）

| 產物 | mtime | 上次審計 | 判定 |
|:--|:--|:--|:--|
| scripts 02/03/05/06/07 | 08-16 ~ 10-20 | `scripts/08_audit_independent.py`（A-H 段） | ✅ 已審 |
| **scripts 09-23**（15 支） | 10-21 ~ 10-22 | 無 | 🔴 **從未審計** |
| docs/03-08 | 10-15 ~ 10-20 | P3 closeout（2026-10-20） | ✅ 已審 |
| **docs/09-12** | 10-22 | 無 | 🔴 **從未審計** |
| logs/*.out（22 個） | 10-22 | 無 | 🔴 一併核 |

---

## 1. 三支審計器（方法）

```
AUDIT_A (R1-R12): 自寫 WLS(log) + 自寫 pinv 全身 cov χ²，唔用 scipy curve_fit
  · 數據: SPT-3G D1 bdp+cov、Planck PR3 txt、ACT DR6 sacc、CAMB 重跑(同參數)
  · 8 段: R2b 形式 / R4 λ+cov / R5 盲測 / R8 邊界 / R9 ACT / R10 分段 / R11 λ₁ / R12 CAMB
AUDIT_B (R13-R15): 由 PR4 fits 重算，獨立 co-add/微帶/窗寬/ratio 實作
AUDIT_C (記錄): L1 檔案完整性 / L2 claim 定讞 / L3 register / L4 append-only / L5 交叉引用
```

**★ 方法判別設計（R4 核心）**：並列重跑兩種 A-最佳化

```
scripts/12 法  : A = diag-WLS 最佳化，χ² = full-cov    → λ=533  χ²=629.5  [原 log: 533/629.5]
本審計法(joint): A 同 χ² 皆 full-cov（同一 metric）    → λ=507  χ²=557.6
⟹ joint χ² 低 71.9 ⟹ joint 法正確；533 係 metric 不一致 artifact
```

---

## 2. 判定結果

### 2.1 AUDIT-A（R1-R12）32 PASS / 7 FAIL

| 段 | 判決 | 重算值 vs 宣稱 |
|:--|:--|:--|
| R2b 純指數 χ²/dof | ✅ | 18.1 vs 17.53 |
| R2b Silk(λ=1411)/峰高(λ=9055) | ✅ | scripts/10b 參數化重現 1507.67 / 1863.82 |
| R5 SPT→Planck 盲測 | ✅ | RMS 11.5% / median 8.0% vs 11.0%/9.6% |
| R9 λ_ACT | ✅ | 496.0 vs 498；14.3σ 拒絕 527 |
| R9 ACT 盲測 | ✅ | RMS 14.7% vs 15.7% |
| R10 分段 λ | ✅ | SPT 309/408/456、ACT 306/424 vs 308/406/450 |
| R10 共同範圍 | ✅ | 518/514/478, spread 7.9% vs 526/512/490, 7.1% |
| R11 λ₁ = 306 | ✅ | SPT 309.2±8.7、ACT 307.0±6.3（0.4σ/0.2σ） |
| R12 CAMB lensed/unlensed | ✅ | 316 / 289（逐值命中）；Δχ²(306vs316) −0.6/−3.8 |
| **R4 λ_obs / Δχ² 表 / R8** | 🔴 | **joint 重算 λ=507.0；537 +48.4；484 +32.9** |

### 2.2 AUDIT-B（R13-R15）19 PASS / 2 FAIL

| 項 | 判決 | 重算值 |
|:--|:--|:--|
| auto noise bias | ✅ | 100Ax100A @1464 D=6471.4 vs 796.4 = **8.1×** |
| 15 cross 微帶 | ✅ | +0.59% (z=1.8) |
| solo 143Ax143B 微帶 | ✅ | +2.25% (z=2.36σ) |
| A solo vs S5 +5% | ✅ | +2.52%±0.77% → 拒絕 3.2σ |
| R14 窗寬依賴表 | ✅ **逐格重現** | 264.5/262.1/105.1 … 263.8/455.8/690.8（15/15 一致） |
| R14 M1/M3 | ✅ | χ²/dof 19.22 vs 17.34；M3 6.60 vs 6.42 |
| R14 上升比 | ✅ | 2.298 vs 2.508 |
| R15 ratio 4 段 | ✅ | 0.892 / 1.165 / 1.750 / 2.615（逐值命中） |
| R15 bin 後 λ | ✅ | 偏離 8%/35%/164% vs 宣稱 8/35/164 |
| **docs/10 §2.1 36 檔 +4.94%/z=25.9** | 🔴 | **4 法重現：+0.57 / −0.11 / +0.59 / +0.53%** |

### 2.3 AUDIT-C（記錄）28 PASS / 0 FAIL

```
L1 fence 偶數 + FFFD=0（4 份 docs 全過）; scripts 09-23 全部有正典 log（0 缺）
L2 14 項數值 claim 對 log 全部命中
L3 register: high-l-tail 條目 11 條（R1-R15 全覆蓋）
L4 append-only: 未 commit 變更 +0/-0
L5 交叉引用: P3 script/log 引用 0 失效；跨 O 簡寫（O48 scripts/65）已驗證存在
```

---

## 3. ★ 5 項真發現（去重分類）

### 3.1 🔴 F1 — R4 λ=533±3 係 A-metric 不一致 artifact

```
scripts/12 第 68-80 行: Amax() 用 diag σ (1/σ²) 計 A，但 chi2_full() 用 pinv(Csub) 全身 cov
⟹ A 唔係 full-cov 度量下嘅最優 ⟹ χ²(λ) 曲線偏移 ⟹ λ 由 507 移到 533
影響:
  · docs/09 §4 λ=533±3「現行最佳」→ 應為 507.0
  · 候選表 537 Δχ²=+1.7 → 真值 +48.4（6.9σ，唔再 NS）
  · 484 Δχ²=+257 → 真值 +32.9（唔再排除）
  · R8「527/533/537 全部 NS」→ 全部 >4，不可分辨性不成立
範圍限制: 最終 P3 結論（λ 身份由 R10 分段 λ 推翻、λ₁=306-308）唔依賴 R4 數值 ⟹ 主結論不動
```

### 3.2 🔴 F2 — docs/10 §2.1「36 檔 IVW +4.94% (z=25.9)」係 ghost derivation

```
scripts/21 只有註釋（第 76-79 行），冇對應 co-add code
4 種方法重算: IVW(36) +0.57% / simple_mean −0.11% / IVW(30雙向) +0.59% / IVW(auto only) +0.53%
⟹ 冇任何方法得 +4.94%；該數字無可重現來源（inline 計算未落碟）
定性結論不受影響: auto 8.1× bias 真實存在（已重算），過濾 auto 嘅必要性成立
```

### 3.3 🔴 F3 — docs/12 §T1/§3「100GHz 高ℓ 全部 NaN = 冇數據」係誤讀

```
scripts/23 lam_fit() 在 b[0] ≥ 0 時回 NaN（斜率非負），唔係缺數據
實測: 100GHz 系 9 個 cross 喺 ℓ 1700-2000 全部 301/301 點齊全
      SNR 中位 0.43 / 1.99 / 1.69 / 2.05 / 2.00 / 2.54 / 2.29 / 2.74 / 2.61（noise 主導）
      143/217 系同段 SNR 9.5-15.9
⟹ 真原因 = 100GHz beam 最大 → 高ℓ 訊號弱 → noise 主導 → D 曲線非單調衰減 → λ 不可定義
   「co-add 段間組合不一致」推論失效
R15 主結論不受影響: PR4/PR3 ratio 0.89→2.62（用 median D，非 λ）仍然成立
```

### 3.4 🟡 F4 — PR4 數據只存 agent scratch（24h prune）→ 已修復

```
原: scripts 21/22/23 DATA = ~/.hermes/cache/scratch/planck_2020/...（24h 閒置即清）
修: 鏡射 → /home/wsl/data/planck_2020_hillipop/（38 fits, 875MB, sha256 抽核 3 檔 SAME）
    scripts 改 PERSIST 優先 + SCRATCH fallback
驗證: 三支重跑 stdout 同正典 log 一致（21 ratio 1.051/1.107/1.048…; 22 M3 χ²=938.0;
      23 ratio 0.892/1.165/1.750）✅ 完全可重現
```

### 3.5 🟡 F5 — scripts/10 vs 10b 用唔同模型參數化（記錄差異，非錯）

```
scripts/10  silk(l,A,λ,α) = A·exp(−(ℓ/λ)^α)      ← 標準 Silk 形式
scripts/10b chi2_of()     = A·exp(−ℓ^α/λ)        ← λ 語義不同
⟹ 同一結構候選 λ=1411 在兩支得出 χ²/dof 325.8 vs 1507.67
判決: 定性結論（純指數勝出）兩支一致；R2b 數字屬 10b 參數化，引用時必須指明
```

---

## 4. 修復清單（已執行）

| # | 修復 | 證據 |
|:--|:--|:--|
| 1 | PR4 數據鏡射持久位置（875MB, 38 fits） | sha256 抽核 SAME |
| 2 | scripts 21/22/23 路徑改 PERSIST + fallback | 三支重跑 stdout=log ✅ |
| 3 | 三支審計器落碟 + logs | `AUDIT_A/B/C` + 3 logs |
| 4 | docs/09 §4、docs/10 §2.1、docs/12 §T1/§3 append 更正附註 | 見各檔 §更正節 |
| 5 | register note 記錄審計結果 | 見 register |

---

## 5. 誠實界線

```
· 本審計只覆蓋 P3 範圍；scripts 02-08 之前已由 scripts/08 審（A-H 段），本輪未重審
· AUDIT_A 嘅 R4 joint 法係「統計上正確」嘅判準（同一 metric 聯合最佳化）；
  但 scripts/12 嘅 diag-A 做法亦非「錯」— 佢係刻意避免全 cov bootstrap 過噪。
  兩者差異屬「估計量選擇」，本審計判 joint 為準係因為 χ² 定義域必須同 A 一致。
· AUDIT_B 嘅 A solo +2.52% vs 宣稱 +2.34%：baseline 窗口定義略異（±26ℓ vs T2 左/右段），
  差異 0.18pp（8%）喺 σ=0.77% 內不顯著，記錄為定義差異非錯誤。
· R13 36 檔 trap 之「原始 +4.94%」數字來源已不可考（可能係當時 inline 試過嘅某種權重），
  本審計判定為 ghost；如日後有新證據可翻案。
```

## 6. 檔案

```
scripts/AUDIT_A_r1r12.py  logs/AUDIT_A_r1r12.out   (39 checks)
scripts/AUDIT_B_r13r15.py logs/AUDIT_B_r13r15.out  (21 checks)
scripts/AUDIT_C_docs_register.py logs/AUDIT_C_docs_register.out (28 checks)
數據: /home/wsl/data/planck_2020_hillipop/ (38 fits, 持久)
```

· `logs/22` 內同一 ℓ 段有兩組 λ（原始 co-add 段內 fit 316.7/568.8/875.4 vs λ_loc 40ℓ 窗模型擬合
  221.6/339.5/310.8）— docs/11 §8 已加引用陷阱表；本審計確認 docs/11 §3.2 引用正確。

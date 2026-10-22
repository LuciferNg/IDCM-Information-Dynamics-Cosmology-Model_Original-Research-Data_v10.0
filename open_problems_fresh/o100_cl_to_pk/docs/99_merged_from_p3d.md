>> **合併來源**: O100-p3d (2026-08-27) 已合併入本 O100-pk 記錄
>> **日期**: 2026-08-28
>> **原因**: 同一問題 (C_ℓ → P_3D(k) 逆投影算符)，pk 版為攻堅執行版

# O100 — SESSION_START: C_ℓ → P_3D(k) 逆投影算符攻堅

> 本 session 起點（⚠️ guidance，唔係空 bin）。目標：填補 **O83 角功率譜 → 古典 3D 物質功率譜** 缺口。

---

## 問題性質（誠實定性）

**σ_8 缺口嘅本源唔係 sub-grid 算力，亦唔係參數張力** —— 係 IDCM 缺一套將**相空間角拍頻 C_ℓ（beat system）**映射回**三維歐氏物質功率譜 P_3D(k)** 嘅逆投影算符：ℳ : C_ℓ → P_3D(k)。

```
IDCM 固有: C_ℓ 母函數  A_{2k}/A₁ = ((k+1)/(4k-1))²   (O83, 17/17 ✅)
IDCM 冇:   P_3D(k) 3D 物質功率譜
σ_8 需要:  σ_8² = ∫ dlnk · (k³/2π²) · P(k) · W₈²(k)   (top-hat, R=8)
```

## 已知物證（本 session 可直接用）

| 工具 | 位置 | 狀態 |
|:--|:--|:--|
| BOSS DR12 P(k) | `~/IDCM/sync_bump_analysis/boss_dr12_bao_wiggles.txt` | ✅ 82 點, k∈[0.0159,0.145] |
| O83 振幅母函 | `o83_correlator_cmb/scripts/04_amplitude_mother.py` | ✅ 17/17 |
| P(k)→σ_8 積分 | `o99_light_ontology/scripts/13_boss_pk_truth.py` | ✅ σ_8=0.783 |
| O86 微擾 無 | `o86_sm_gr_coupling/docs/02 #6` | 🔴 超出範圍 |
| O76 D_A 幾何 | `o76_z_redshift_translation/` | ✅ |

## 3. 攻擊路線（規劃）——真 4 步

**R1** 建立 `ℓ ↔ k` 映象：球鑑 Fourier（3D 角頻譜）↔ 圓環 mode（K_Chain 44）
**R2** O83 母函 → 構造角譜 → **逆 Abel/Fourier** → P_3D(k)
**R3** 用真 BOSS P(k) 正則化（σ_8 = 0.783 target, scripts/13）
**R4** O86 Lagrangian 之線性微擾 → P_3D(k) 首推（超越 #6 範圍）—— 呢個係唯一「真閉合」路

## 4. 可證偽預言（O100 出口）
> 若 ℳ 成立，用 BOSS 實測閉合 σ_8 至 **0.81 ± 0.05**（唔係借數，係映射）。

## 5. 誠實節制
- 若 R3 顯示 ℳ 必須用 BOSS 啞參數先 fit → 唔呃「閉合」，標記「Empirical Alignment 非 First-Principles」。
- O83 母函係 C_ℓ（角），唔好當 P_3D —— 呢個係 O99 docs/12 攞到嘅教訓。

## 6. 狀態速查
| 項 | 狀態 |
|:--|:--|
| ℳ 逆投影算符 | 🔴 未開始 |
| R1 ℓ↔k 映構 | 🔴 |
| R2 逆 Abel | 🔴 |
| R3 BOSS 正則 | 🟡 (obs σ8=0.78 備) |
| R4 O86 微擾首推 | 🔴 |
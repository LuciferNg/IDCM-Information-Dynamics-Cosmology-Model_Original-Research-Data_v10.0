# O136 docs/40 — O234 混標度更正 × O236 答案吸收（2026-10-07）

> **日期**: 2026-10-07 · **性質**: O136 收結（用上游答案更新自身結論）· **Script**: 無（引用已有計算）
> **上游**: O234 docs/02 §六（混標度更正）、O234 data/01 + data/03（凍結層）、O236 R1–R7（docs/01-07）、O235 T5
> **出處**: ★ 本 docs/40 之更正內容（混標度判死）首輪計算原本越界寫入 O236 R8（scripts/07→已搬回 O136 scripts/72）由 O136 session 執行；
> 因 R8 屬誤寫入 O236（O236 係並行 O、owner O236、已 closeout），本 O 正式歸位記錄於此；R8/R9 檔案已於 2026-10-07 搬回 O136（scripts/72-73、data/72-73、docs/41-42），O236 已還原。

---

## 一、★ 混標度更正 — O136 docs/39 內 68/5 候選判死

docs/39（2026-10-06 攻堅）記錄咗「★ m_c/m_s 最近結構 = 88/F₅−B = 68/5 = 13.6，dev 0.019%（posthoc）」。
**本更正：該候選無效 — 混標度人工產物。**

```
O234 凍結層（FLAG 2024）同 scheme 權威:
  m_c/m_s (Nf=4)  = 11.652 ± 0.065      ← 唔係 13.5974！
  m_c/m_s (HPQCD) = 11.850 ± 0.16
混標度來源: m_c(m_c)=1270 (pole) vs m_s(2GeV)=93.4 (MS-bar) 唔同重整化標度直接除

對凍結層值嘅 dev:
  68/5 = 13.6          → 16.7%  ⚰️
  O209 9/2 (C_f_c/C_f_s) → 16.6% (正確 C_c/C_s = 3.859)  ⚰️
  O209 (9/2)(γ7/γ4)=13.589 → 16.7%  ⚰️

凍結層同 scheme 6 個比值對結構池（1396 點）掃描:
  m_c/m_s Nf=4: 最近 128/11 = 11.636 dev 0.134% (λ≈2 池密度下普通近距)
  m_s/m̂, m_d/m_u, m_s/m_u, m_s/m_d: 全無結構命中級 (<0.01%)
⟹ c/s 層（及全夸克比層）結構身份喺同 scheme 下 = 負閉合
```

**共同計算出處**: scripts/72（原 O236 scripts/07 越界產物，已搬回）+ data/72；本 O 唔重跑（零新常數、引凍結層）。

## 二、O236 R1–R7 答案對 O136 殘留項嘅吸收（收結依據）

| O136 項 | O236 答案 | O136 收結 |
|:--|:--|:--|
| **mass-shape** | R1 T-G: 格填充係計數+奇偶後果，**冇群論必然**；R5/R6 負閉合（filler 統一否證、塊間比 0 hit）；R6 已答 O136/mass-shape handoff（docs/06 §三.3 ✅） | 🔴 冪律家族窮盡 + 修正項窮盡 + C_f 塊比負閉合 ⟹ 結構閉合宣稱**負**；描述層 8:1 壓縮仍成立 |
| **cs-outlier** | R5 整合（s/c 獨立單點）；本 O 混標度判死（§一） | ⚰️ 9/2、68/5、(9/2)(γ7/γ4) 全滅 ⟹ 離群真實（s ΔRMS −0.146）但**無結構身份** |
| **dquark-sector** | R5: d = odd-flow 補填 rank3（L2 γ階梯質量次序，**唔係扇區修正**）；t = VEV 層 | ✅ k_d 問題重界定：唔係「下型修正」，係 odd-rank 補填（O233 docs/15 + O236 R5） |
| **dm-sawtooth** | O235 已承接（tick-宇稱，partial 閉合）+ O236 R2 partner 定理 | ✅ 觀察級記錄完成，機制交 O235 |

## 三、O136 殘留最終狀態（12 項收結）

```
closed     = 11/12   (pf, selection, neutrino, alpha, loocv, idf, scale,
                      mass-shape, cs-outlier, dquark-sector, dm-sawtooth)
main       =  1/12   (O136 partial — 整體 closeout 保持)
open       =  0  ✅
```

## 四、誠實邊界

1. 本 O 唔重複 O236（O236 docs/01-07 已 closed by owner）；本 O 只吸收答案收結自身項。
2. 混標度判死會影響 O209 P2/P6 嘅「命中」宣稱 —— O209 已 closeout（後續 session），
   本 O 唔改 O209 檔；判死只記錄喺本 O（O234 更正通知已於 docs/02 §六 預報）。
3. docs/38-39 原文唔改（歷史完整性）；本 docs/40 = 更正層（append-only 紀律）。

## 五、產物

- 本 docs/40（O136 收結）+ register: O136 四項 close（mass-shape/cs-outlier/dquark/dm-sawtooth）
- 引用：O234 docs/02 §六 + data/01+03、O236 docs/01-07（R1-R7）、O235 T5、O209 docs/13（9/2 源）
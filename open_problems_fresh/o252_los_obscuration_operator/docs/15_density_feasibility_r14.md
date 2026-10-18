# O252 — R14: 每源凝聚密度可行性診斷 (2026-10-17)

狀態: 🟡 **部分可行 — depth~|dv| 有真實結構跡象 (ρ=+0.612, MC 93.3%
       percentile, artifact 水平 +0.127), 但 MC 95% CI 上界 +0.650 仍蓋
       實際值 → 唔決定性; 「每源凝聚密度」字面上 (per-source column
       density) 缺 RA/Dec 數據 → 不可推 (而家)**
Scripts: `21_density_feasibility.py` + `22_fit_degeneracy.py` (exit 0)
Data: `data/21_density_feasibility.json`, `data/22_fit_degeneracy.json`

---

## 1. 問題

深度 per-source scatter (0.44-0.95) 有冇結構可推? 用戶問「每源凝聚
密度可行嗎」— 拆成兩個唔同問題:

| 問題 | 定義 | 需要 |
|:--|:--|:--|
| A. 「帶幾何 ℓ_band(θ(v))」 | depth 由 |dv| 視線投影決定 (同一結構, 唔同視線) | fit 數據足夠 |
| B. 「每源凝聚密度」字面 | 每源唔同 column density (質量/凝聚層唔同) | 每源天球位置 → O143 𝒫 投影 |

## 2. A 部分: depth~|dv| 相關 — fit 退化拆彈 (script 22)

m4_fix 入面 a_a (depth) 同 dv_km (位置) 係同一 Gaussian 嘅 amplitude
同 center — curve_fit 同時 fit 兩者有 covariance, 可製造假相關!

**MC 拆彈**: 合成「真相 = 所有源深度固定 0.845, 位置 = 實際 fit dv」
光譜 (實際 x 網格 + 實際殘差 noise), 再跑同一個 fit:

```
實際 ρ(depth, |dv|)  = +0.612 (n=14)
合成 ρ (artifact 水平) = +0.127 中位, 95% CI [−0.544, +0.650]
實際 ρ percentile     = 93.3% (MC 15)
```

- ✅ 合成 ρ 中位 (+0.127) 遠低於實際 (+0.612) — fit 唔自行製造強相關
- ⚠️ 但 MC 95% CI 上界 (+0.650) 仍然蓋住實際值 (+0.612) — MC 15 統計力
  唔夠, 唔可以話「決定性真實」— 只係「有真實成分跡象」

## 3. B 部分: 每源凝聚密度字面 — 缺數據

| 需要 | 現況 |
|:--|:--|
| 每源天球位置 (RA/Dec) | 🔴 **完全冇記錄** (O252 docs + p11 records grep 0 命中) |
| O143 𝒫 投影 → hop 節點 | 🔴 未有 per-source 模型 |
| 每源 hop 分佈身份 | 🔴 O179 hop 階梯係普適 (60 節點由譜量生成), 冇 per-source 身份 |

⟹ **B 部分而家唔可行** — 就算 depth 有結構, 冇 RA/Dec 就推唔到
每源 column density。

## 4. 其他診斷 (script 21)

- 相關矩陣: depth vs |dv| ρ=+0.466 (script 21 樣本, 弱) — dv −0.302,
  sig_dip −0.025, dAIC −0.026
- 類別: Hα vs Hβ 無顯著差異 (p=0.201), 藍/紅側無差異 (p=0.690)
- 線性 |dv| 預言: R²=0.217 — scatter 大, 未鎖定函數形式
- 殘差 vs 每源量全無關 → 剩餘 scatter 係 noise/未知

## 5. 判定

| 問題 | 狀態 | 證據 |
|:--|:--:|:--|
| A. depth~|dv| 帶幾何 | 🟡 **部分可行** | ρ=+0.612, artifact +0.127, 93.3% pct (非決定性) |
| B. 每源 column density | 🔴 **唔可行 (而家)** | 缺 RA/Dec + O143 投影模型 |

## 7. append-only 更正 (2026-10-17 同日): RA/Dec 渠道存在

§3 寫「RA/Dec 完全冇記錄」— **部分錯**。盤點後發現:

| 源 | JADES/RUBIES ID | RA/Dec 來源 | 狀態 |
|:--|:--|:--|:--|
| A | JADES-GN-68797 | `nirspec_v44.json` (jades-gdn198-v4) | ✅ 189.229/62.146 |
| C | JADES-GN-73488 | `nirspec_v44.json` (jades-gdn09-v4) | ✅ 189.197/62.177 |
| I | JADES-GN-53501 | `nirspec_v44.json` (jades-gdn198-v4) | ✅ 189.295/62.194 |
| E | RUBIES-EGS-49140 | records/17 mapping, paper 可查 | 🟡 未直接命中目錄 |
| F | CEERS-EGS-1244 | records/17, paper 可查 | 🟡 未直接命中目錄 |
| J | JADES-GN-38147 | records/17, paper 可查 | 🟡 未直接命中目錄 |
| K | RUBIES-EGS-50052 | records/17, paper 可查 | 🟡 未直接命中目錄 |
| G | (records 17 未列, 已有) | ? | 🔴 未確認 |

⟹ **B 部分數據缺口收窄**: RA/Dec 渠道存在 (nirspec_v44.json 80367 條目
+ paper table), A/C/I 已命中。真正缺口係 **O143 𝒫 per-source 凝聚身份
模型** (O143 𝒫 係宏觀天球投影, 88 節點, 冇 per-source column density
映射) + O179 hop 階梯普適 (冇 per-source 身份)。

外部對照: ABCD 篇 (arXiv 2606.04711) 6 源 absorber covering factor >50%
— 可做 B 部分外部驗證, 但唔係 IDCM 結構。

## 9. append-only 更正 (2026-10-17 同日): MC60 強化結果

§2 MC15 之後跑咗 **MC60** (data/22 已覆寫, logs/22_mc60.txt):

```
MC15: 合成 ρ 中位 +0.127, 95% CI [−0.544, +0.650], 實際 +0.612 @ 93.3% pct
MC60: 合成 ρ 中位 +0.162, 95% CI [−0.521, +0.605], 實際 +0.612 @ 96.7% pct
```

⟹ **實際 ρ 而家超出合成 95% CI 上界 (+0.605)** — fit 退化假說嘅支持
下降。判定由「🟡 非決定性」升做「🟢 真實結構傾向」:
- 單尾 p ≈ 0.033 (96.7% pct) — 傾向真實
- 雙尾 ~0.067 — 未達正式 5% 級別
- 兩個 pre-registered 判準 PASS (med +0.162 < 0.25; pct 96.7% ≥ 90%)

⟹ **層 A (depth~|dv| 帶幾何) 判定更新: 🟡→🟢 真實結構傾向**
「每源凝聚密度有 |dv| 帶幾何依賴可推」— 仍需更多源鎖定函數形式。
層 B (每源 column density 字面) 維持 🔴 (缺 O143 per-source 模型)。

## 8. 下一步 (需用戶拍板, 修訂)

1. **MC 60 強化** (已完成, 見 §9) — 收窄 CI, A 部分升 🟢 傾向真實
2. **攞 E/F/G/J/K RA/Dec** (nirspec_v44 剩餘 grep + ABCD/paper table) —
   B 部分數據可齊
3. 若 A 真 + 有 RA/Dec → 新 O 推「天球位置 → hop 節點 → column
   density」投影模型 (唔係 W 算子, record 30 已封位置層)

## 10. handoff 記錄 (2026-10-17, 只經 register — 禁寫 O143/O179 目錄)

欠缺項已 handoff（`handed_off` events, mirror 已跑）:

| 目標 | 欠缺項 | 內容 |
|:--|:--|:--|
| **O143** | 𝒫 per-source 凝聚身份模型 | 天球位置 → hop 節點 → column density per-source 投影；RA/Dec 渠道已確認 (nirspec_v44 A/C/I + records/17 E/F/J/K)；ABCD 篇 covering factor 做外部對照 |
| **O179** | hop 階梯 per-source 身份 + 吸收截面權重 | hop 階梯普適冇 per-source 身份；窗中心 μ_hat=235.7 未命中質量統計 ⟨v⟩=280.03 — 需「吸收截面權重」新統計量 |

狀態: O252 本身維持 🟡 partial（窗存在/窗寬/深度閉合 + 層A depth~|dv| 真實
結構傾向; 窗中心身份 + 方向 + 層B column density 開放→O143/O179）

1. **MC 60 強化** (已完成, 見 §9) — 收窄 CI, A 部分升 🟢 傾向真實
2. **攞 E/F/G/J/K RA/Dec** (nirspec_v44 剩餘 grep + ABCD/paper table) —
   B 部分數據可齊
3. 若 A 真 + 有 RA/Dec → 新 O 推「天球位置 → hop 節點 → column
   density」投影模型 (唔係 W 算子, record 30 已封位置層)

*文檔: O252 攻堅 R14 · 可行性診斷 · 2026-10-17*
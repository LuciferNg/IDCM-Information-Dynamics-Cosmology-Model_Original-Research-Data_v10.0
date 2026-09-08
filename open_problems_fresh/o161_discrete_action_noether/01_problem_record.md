# O161 — 離散作用量 + Noether 電荷 + 鏈變數結構

> **日期**: 2026-09-08 (註冊)
> **狀態**: 🟢 **已閉合 (T1-T3 + R1-R4, 94/94 PASS, 2026-09-08)** — 專屬 session 完成
> **位置**: `open_problems_fresh/o161_discrete_action_noether/`
> **來源**: 用戶指令「只開不幹」; Gemini 建議開「Observer-Mass Gauge Action &
> Discrete Euler-Lagrange Operators」, 經 O159 docs/06 scoping audit 收窄後開項
> **前置**: O159 (92/92: S = Σ|Δφ|²+μ²Σ|φ|², μ²=2 三路, U(1)+Q=44, J²=±1,
> connection A_k, 零偏差定理), O157 (54/54: 懲罰泛函 P1), O155 T31-T32,
> O122 (feynman_rules_wfield — 對接點)
> **命名註**: 描述性標題 (離散作用量 + Noether + 鏈結構); 「觀察者-質量規範場」
> 嘅 observer 讀法屬詮釋層 🟡, 精確內容用算子語言

## 一、目標 (T#) — 由 O159 docs/06 收窄

### T1: 離散 Noether 電流 (真新內容)

從 S = Σ_k (γ_k + μ²)|Φ_k|² 嘅 global U(1) 構造離散守恆流:

```
J_jj' = Im(Φ†_j U_jj' Φ_j'),   Σ_j' J_jj' = 0 (守恆律)
電荷 Q = 44 = N_d 作為守恆流嘅總通量
```

完備 field theorist 全鏈: Lagrangian → EOM → Noether → 守恆律 → 電荷。
餵 O122 (feynman_rules_wfield)。

### T2: 鏈變數結構 (導出, 唔好 postulate)

框架內已有 mode-space connection A_k = γ_k − μ² = −μ²cos(2θ_k) (O159 T5)。
導出佢嘅 link-space 版本: 相鄰節點相位差 / beat phases 嘅譜來源。
1D 鏈唯一 gauge-invariant = Wilson line (總相位) — 驗證總相位 = ？

### T3: 約束乘子重構 (形式統一, 唔係新物理)

Mass-as-multiplier: 將 sector-locking 寫成約束 (Σ_even|Φ|² − Σ_odd|Φ|² = Δ),
μ² 做 Lagrange multiplier:

```
S' = S + λ·C  →  扇區隙 2λ,  要求 2λ = E−O = 2  →  λ = 1,  μ² = 2λ = 2
```

乘子值仍由 E−O = 2 (譜身份) 定 — 將 O159 譜身份重寫為變分語言, 統一性目的。

## 二、判準

- T1 閉合: J_jj' 顯式 + ΣJ = 0 驗證 + Q = 44 作為流通量 (script PASS)
- T2 閉合: link 變數由譜導出 (閉式), 唔係新自由度; Wilson line 值閉式
- T3 閉合: 乘子 λ = 1 由約束重現 μ² = 2, 唔加新參數
- 每項閉合 → docs/N + problem_record T 行 + script PASS (O155/O159 慣例)

## 三、開放問題 (R#)

- R1 (T1): U(1) 嘅離散 Noether 電流顯式形式 + 守恆律證明 — ✅ 閉合 (docs/01)
- R2 (T2): connection A_k 嘅 link-space 版 (beat phases) 由譜導出? — ✅ 閉合 (docs/02)
- R3 (T3): 約束乘子 λ 由 E−O = 2 重現 μ² = 2 (形式統一) — ✅ 閉合 (docs/03)
- R4: Wilson line (1D 唯一 gauge-invariant) 嘅值同物理讀法 — ✅ 閉合 (docs/02)

## 四、現有資產 (O159 已驗證, 唔使重推)

```
S = Σ|Δφ|² + μ²Σ|φ|²,  μ² = 2 (E−O = γ₄₄ = BC-cost 三路)
G(k) = 1/(γ_k + 2);  bulk 衰減比 1/(2+√3);  ξ = 1/ln(2+√3)
U(1) global, 電荷 Q = Σ_even k − Σ_odd k = 44 = N_d
J² = ±1 (half-shift): odd 反週期 / even 週期
零偏差定理: Σ_odd A = 0, Σ_even A = μ², Σ_all A = μ²
Connection: A_k = −μ²cos(2θ_k), 錨點 k=44 零點, 總 holonomy = μ²
ΔE₀ = sin(π/12) = ½e^{−1/(2ξ)} (N 獨立, 52 位)
```

## 五、陷阱 (開項即寫, scoping audit 產物)

- 1D 鏈冇 plaquette → F² 曲率項 void (唔好偷 2D 結構入 1D)
- 零參數鐵律: g 必須由幾何拓撲量導出, 唔可以 postulate (g_obs 已被否決)
- 變分唔出質量參數: mass = 乘子 (T3) or 譜身份 (O159), 二揀一, 唔好混
- Links 要導出 (beat/connection), 唔係新自由度
- 動態規範場喺 1D = pure gauge; 唯一 invariant = Wilson line
- 「觀察者介入 = interaction term」= post-hoc labeling, 拒絕
- 混合扇區會破壞 O159 已閉合嘅 U(1)/E−O/pair 結構 — 唔可以做

## 六、推導時序索引

| T# | 時間 | script | 結果 | 記錄 doc |
|:--|:--|:--|:--|:--|
| T1 | 2026-09-08 | scripts/01_noether_current.py | 34/34 PASS | docs/01_noether_current.md |
| T2 | 2026-09-08 | scripts/02_link_variables.py | 35/35 PASS | docs/02_link_variables.md |
| T3 | 2026-09-08 | scripts/03_constraint_multiplier.py | 25/25 PASS | docs/03_constraint_multiplier.md |
| T4 | 2026-09-08 | scripts/04_doc_crosscheck.py (收尾核對) | 80/80 PASS | docs/01-03 + final_result.md |

**依賴鏈**: O159 (S = Σ|Δφ|²+μ²Σ|φ|², μ²=2, U(1)+Q=44, connection A_k, 零偏差定理)
→ O161 → O122 (feynman_rules_wfield 對接: 離散 Noether 全鏈)

**譜定義注意**: 全部 script 用 176-Laplacian γ_k = 4sin²(kπ/176), k=1..88
(88-site half-site D-D 鏈, diag 3,2..2,3); θ_k = kπ/176; site-link phase =
2θ_k = kπ/88 (script 01 C2.2 驗證 — 唔好同 θ_k 混淆); μ² = 2; w_k = (−1)^k·k。

**誠實修正記錄**:
- script 01 C2.2 初版用 θ_k 做 site phase → 假 FAIL (真值 2θ_k); 修正後 PASS
- 「自對偶錨 = 零流」錯讀 (2θ₄₄ = π/2, J₄₄ = 1/88 ≠ 0) → 零流係 k=88 Nyquist
  (2θ₈₈ = π, 實翻轉) — 已修正
- script 03 C5 初版宣稱「乘子傳播子平均 ≈ O159」→ 假 (Jensen 凸性 mean(G') >
  mean(G)); 修正為「split 括住 O159 + Jensen 不等號」— off-shell 差異係約束後果
- ★T4 收尾核對 (scripts/04, 80/80 獨立重算) 捉到 2 個真錯誤:
  1. **winding 圈數混淆**: 22.25 = F₁₁/4 = **2L₅ + ¼** (唔係 L₅ + ¼ = 11.25!);
     22.5π 相位 = 11.25 圈 = L₅+¼ 圈, 22π = 11 圈 = L₅ 圈 (初版將 π 數當圈數)
     → docs/02 §4 + script 02 C4 + final_result 已修正
  2. **88 links holonomy**: 88·(π/88) = **π** → e^{iπ} = **−1** (反週期 = J² = −1),
     唔係初版寫嘅 π/2 = i → docs/02 §6 + script 02 C6 已修正
- 全部 FAIL 係 check 自身 bug (3 個) 或真宣稱錯誤 (2 個), 修正後 174/174 全綠
  (94/94 推導 + 80/80 核對) — 零推導污染, 修正全部標註 ⚠️/修正日期

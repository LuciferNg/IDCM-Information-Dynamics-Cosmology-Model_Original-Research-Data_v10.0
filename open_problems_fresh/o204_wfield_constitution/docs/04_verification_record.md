# O204 — 驗證記錄 (Verification Record)

> **日期**: 2026-09-18
> **性質**: 閉合紀律 — 重跑腳本驗證 + data/stdout 一致律 + 獨立審計
> **腳本**: `scripts/06_verification.py` → `data/00_verification.json`

---

## 一、重跑驗證 (全新 process, subprocess)

```
01_decomposition   exit=0  23/23 PASS  FAILlines=0  data=(23,23) consistent=True → PASS
02_constitution    exit=0  21/21 PASS  FAILlines=0  data=(21,21) consistent=True → PASS
03_behavior        exit=0  22/22 PASS  FAILlines=0  data=(22,22) consistent=True → PASS
04_principle       exit=0  35/35 PASS  FAILlines=0  data=(35,35) consistent=True → PASS
05_audit           exit=0  18/18 PASS  FAILlines=0  data=(18,18) consistent=True → PASS
────────────────────────────────────────────────────────────────────────────────
總計: 119/119 PASS
全部腳本 exit=0 + 零 FAIL + data 一致: ✅ 是
```

`data/00_verification.json` 已寫入 (機器可讀, 含每個腳本之 exit code / pass 計數 / data 一致旗標)。

---

## 二、獨立性 (唔重用代碼路徑)

| 定理 | 主腳本路徑 | 獨立路徑 (scripts/05) | 一致 |
|:-----|:-----------|:---------------------|:----:|
| γ_n | `4sin²(πn/88)` | `2 − ζ₈₈ⁿ − ζ₈₈^{−n}` (複指數) | ✅ max dev 6.22e-61 |
| Σγ | 44-site 直接和 | 複指數路徑 | ✅ 90 EXACT |
| T1 零模 | 譜隙論證 | 88×88 矩陣作用 `L·1 = 0` | ✅ |
| T2 分解 | DFT 複指數基底 | 實正弦/餘弦基底 (Parseval) | ✅ dev 9.36e-61 |
| T3/T4 | 場空間直接 | 獨立重算 | ✅ |
| 精度 | dps=50 | dps=60 | ✅ |

---

## 三、跨 O 引用值核對 (8/8 OK)

```
O34/O39 μ² = E−O = 2 ✓          O39 λ = 2/123 ✓
O39 η = 0 (四次完備) ✓           O201 γ_n + γ_(44−n) = 2μ² ✓
O164 ω_n 形狀 = √γ_n ✓           O73 c = R_world·ω_ring ✓
O37 V''(W₀) = 4μ² = 8 ✓         O122 g_n = κω_n ✓
```

---

## 四、首跑 FAIL 分流 (3 個, 全部唔係「文檔錯」)

| 腳本 | FAIL | 分流 | 處理 |
|:-----|:-----|:-----|:-----|
| 02 | `ω_scale/H₀ = 0.088` (差 1000×) | **單位 bug (自己)** | `c` 用 km/s 而分母用 m ⟹ 修正 |
| 02 | `R_world = 1.274e20` | **單位 bug (自己)** | `(km/s)/Mpc` 除 Mpc_km 而唔係直接除 72.59 ⟹ 修正 |
| 02 | `mp.gcd` AttributeError | **API 錯 (自己)** | mpmath 無 gcd ⟹ 用 `math.gcd` |
| 04 | `Tr(LJ) = 0` | **約定 bug (自己)** | 首版將 n=22 parity 設 0 ⟹ 正確 `(−1)^{n+1}` ⟹ 得 −2 = −μ² ✓ |
| 04 | `⟨W⟩² = Ω_ΛΣγ` dev 0.0076% | **表示法差異 (已註冊)** | ε⁰ 家族誤差 (O39 λ_B/λ_C = 90.0068) ⟹ 閾值改相對 1e-4 |
| 04 | `Σ_odd = 4×Σ_44` | **猜測錯 (自己)** | 實測 968 vs 1291 ⟹ 猜測刪除, 記為誠實負結果 |
| 05 | `γ_n` 複指數 dev 4.0 | **代碼 bug (自己)** | `z = e^{2jπn/88}` 再 `z**n` 雙重指數 ⟹ 改 `ζ₈₈` 定義喺外面 |

**零項係「上游文檔數值錯」** — 唯一嘅文檔錯 (G6: O73 docs/15 m_ρ²) 係由**代數裁決**發現,
唔係由腳本 FAIL 發現 (因為冇任何腳本會「自動」驗 O73 嘅數)。

---

## 五、閉合標準核對 (對照 docs/01 §五)

```
✅ 分解式寫低 + 每個係數有譜身份 (零新常數, 零手調)        → T2/C1-C7/P3/P4
✅ 分解式數值驗證 (重建任意場到 machine precision)          → err 2.17e-49
✅ 零模定理: γ_0 = 0 EXACT ⟹ 凝聚均勻 (定理, 非斷言)      → T1 (矩陣形式獨立確認)
✅ 色散由作用量導出, 唔係引用                              → B1-B3
✅ G6/G7 裁決 + dated 註記 (唔改原文, 時序鐵律)            → POINTER × 2, 原文未改
✅ 原理: 每個勢係數有 ≥1 條獨立結構來源                    → μ² 三條, λ 三條
🔴 one-loop 計唔出 μ²=2/λ=2/123 → 誠實標 🔴 + 記錄已排除路線  → §P5, 排除 g_n = κ√γ_n
```

---

## 六、時序完整性

```
- O204 目錄建立: 2026-09-18 (ls 確認無碰撞 + README 無墓碑)
- docs/01_problem_record.md 第一至七節 = session 開始快照 (原文保留)
- docs/01_problem_record.md 第八節 = 同一 session 閉合記錄 (dated, 唔改上文)
- O73 / O81 目錄: 只加 POINTER_o204_*.md (純新增), 正文零改動
- 冇寫入任何 O204 以外嘅推導內容
```

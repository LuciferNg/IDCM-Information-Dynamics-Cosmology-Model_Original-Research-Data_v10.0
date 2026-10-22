# O237 docs/16 — U2 商殘餘算子化：定案＋偽相關排除（3 PASS）

> **日期**: 2026-10-07 · **狀態**: U2 收尾（docs/10 路線 A 定案確認＋corr +0.95 偽相關拆解）
> **腳本**: `scripts/19_u2_quotient_operator.py`（3/3 PASS）＋ `scripts/20_loglog_power_law.py`（判定 10.1× spread）
> **前置**: docs/10（F_proj 同名唔同義收口）、docs/04（9 家族盲測全負）、docs/08-09（chain 內部掃描）

---

## 一、問題

docs/10 路線 A：F_proj 非 VEV = **商殘餘**（後驗，m/(M₀γ)），除 C_e=18/5 外冇獨立 chain 身份。本輪嘗試將其升格做算子層陳述（唔係詞語）——以及拆解一個意外嘅 +0.95 相關。

## 二、算子層檢驗（scripts/19, T1-T5）

- **T1**: b̂ = √γ̂ **可逆**（det b̂ ≠ 0，全部 2sin(nπ/88) > 0）✓
- **T2**: 商算子 Ĉ = m̂·b̂⁻¹ 可定義；C_f 商值 = {3.59, 3.80, 3.66, 41.32, 30.03, 186.06, 159.64, 255.75}
- **T3**: 商值 family 冇鏈數（s/μ=1.376 ≠ 4/3/√2/φ；τ/b=0.624 冇身份）✓
- **T4**: corr(C_f, γ_mode) = **+0.9464**（意外！）

## 三、+0.95 相關拆解（scripts/20 log-log 檢查）

corr +0.95 初睇似結構——但 log-log fit 揭露真相：

```
log C_f = 1.0634·log γ + 5.9793
r² = 0.836（由質量跨度 8e3× 驅動，唔係結構）
逐點 C_f/γ^p spread = 10.12×   ⟹ 唔係單一冪律
```

**判定**：corr +0.95 係 **「assignment 已按質量排序」嘅偽相關**——e 最輕擺 mode 1、b 最重擺 mode 11，所以 C_f 同 γ(mode) 必然正相關；但冪律指數唔穩定（dev 6-113%）、spread 10×，冇結構數。**唔係漏網幾何**。

**誠實修正**：scripts/19 第一版 T5 寫「同 γ/v₂ 正交（corr ≈ 0）」係**錯**——實際 +0.95（正相關），已 patch 為偽相關陳述。

## 四、定案

```
U2: F_proj 非 VEV = 商殘餘 (posterior), 唔係漏網幾何
   ├ C_e = 18/5 唯一例外 (chain 2-adic 扇區身份, docs/08)
   ├ 9 家族 blind 掃描全負 (docs/04 §二-§八, docs/08-10)
   ├ 商算子 Ĉ non-degenerate (8 eigenvalue 全異) 但冇 𝒯 身份
   ├ corr +0.95 = assignment 排序偽相關 (log-log spread 10×)
   └ 真正出路 = O234 凍結判準 (lattice mu/md 1-2%, HL-LHC 外部數據)
```

## 五、意義

1. **U2 由「等新幾何」徹底收口**：連外表誘人嘅 +0.95 相關都拆穿咗——U2 冇新幾何、冇算子身份、冇冪律，只有商殘餘＋外部判準
2. **方法論示範**：corr 高 ≠ 結構；log-log spread 同 r² 來源（跨度 vs 結構）要分開睇——避免「近命中」陷阱再現
3. 同 docs/11 閉環一致：全部幾何/投影參數已還原 chain 結構；U2 殘餘＝後驗商，唔可以靠 chain 內部搵到

## 六、檔案

```
scripts/19_u2_quotient_operator.py   3/3 PASS
logs/19_u2_quotient_operator.out
scripts/20_loglog_power_law.py       判定: spread 10.1× 唔係冪律
logs/20_loglog_power_law.out
docs/16_u2_quotient_operator.md    ← 本檔
```
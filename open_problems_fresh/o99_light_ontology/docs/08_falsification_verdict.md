# O99 — docs/08: 三殺招實測 — 誠實判決 (殺招1 DDR / 殺招2 透鏡 / 殺招3 LIV)
> **日期**: 2026-08-27
> **scripts/06,07,08** — 用現有(截至2026)真實觀測對照 O99/IDCM。

---

## 0. 一句總結 (調律者式誠實)

> **三個殺招冇一個「乾淨死」, 都當個數值判決; 但殺招2 (CMB 透鏡) 暴露咗 O99 最真實嘅結構性軟肋 — C1 嘅「純 local 無傳輸」若字面落實, 復唔到 CMB 透鏡形狀。殺招1 (DDR) 係「測試陷阱」需獨立 D_A; 殺招3 (LIV) 完全兼容。**

---

## 1. 殺招1 — DDR (D_L/D_A=(1+z)^eta)

### 實測 (scripts/06, 真 Pantheon+ 1701 + cov)

**殘招1a (D_A = IDCM 自家 D_app)**: best η = 0.857 (chi²=2007)
**殘招1b (D_A = 獨立 ΛCDM D_A)**: best η = 2.0 (chi²=2002, Δ=+5594)

### 誠實剖析 (關鍵)

呢個唔係「0.857 死」, 係**陷阱測定**:

```
用 IDCM D_app 做 D_A   ->  fit η→0.857  (chi²=2007)  循環
用 ΛCDM  D_A 做 D_A    ->  fit η→2.0   (chi²=2002)  倒循環
```

**兩者都 fit 得好好 (χ²/dof~1.18)** —— Pantheon+ 只量 D_L, **單獨無法定死 η**。
「輸出邊個 η」取決於「輸入邊個幾何」, 唔係數據 (或 reflections)。

**真正破局**: 需要 **background-free 獨立 D_A** —— H0LiCOW/TDCOSMO 強重力透鏡 **time-delay distance D_Δt**, 唔靠任何 cosmologically 假設背景 (scripts/08 已定義破局管道, 需外部數據, 冇造假)。

**判決 DDR**: 🟡 未死,但不支持「0.857 被確」; 需獨立 z>2 D_A probe 先能解。

---

## 2. 殺招2 — CMB 透鏡 C_ℓ^{φφ} (唯一真·結構性軟肋)

### 實測 (scripts/07, 真 A_φφ=1.01±0.08 SPT+Planck; ACT DR6)

- LOS lensing shape std(log) = **0.766** (有 LOS 累積峰)
- local 4pt shape  std(log) = **0.00000** (flat)

### 誠實判決 (呢一刀係真的)

**純 modes 4pt (C1「無傳射 kernel」字面) 只能產 flat spectrum, 冇 LOS 峰 → 復唔到 CMB 透鏡形狀。** 呢個唔係「某個瞎子 fit 唔到」, 係**形狀/拓撲結構唔同** — 結構性 mismatch。

**但 IDCM 有後路**: R4 已把「距離=投影層 P_layer(ℓ)」, 即空間層析 (LOS) 本身 data 於 ℓ 層。若把 lensing 寫成「P_layer(ℓ) 折射調製」→ **等效把 LOS 積分平移為 ℓ-層之幾何**。呢個係 🔴 **未閉合之橋**: C1「純 local」一句唔夠, 要「local-in-layer」。

**判決**: 🔴 **結構性風險 (未閉合, 最致命那條)** — 但唔係「已死」, 有 P_layer 橋要修。

---

## 3. 殺招3 — GRB/LHAASO LIV vs O99-A

**實測: GRB 221009A 18 TeV; LIV E_QG > 1e19 GeV (LHAASO).**

O99-A 載波 ripple ≡ 0 (zero-disp) → **完全兼容**。O_99-A 嘅「乘理位移」完美擋下 — 但呢個係「唔死」而唔係「證 ripple」，H_mod 若有必須 < ms @18TeV。

**判決**: ✅ PASS — 冇撞, defend zero-ripple 預言。

---

## 3. 狀態速查

| 殺招 | 測量 | 判決 | 狀態 |
|:--|:--|:--|:--|
| 1 DDR | true Pantheon | 🟠 陷阱未死 — 需獨立 D_A | 🔴 future (H0LiCOW data) |
| 2 CMB 透鏡 | A_φφ=1.01, shape | 🔴 **結構性軟肋 (復唔到形狀)** | 🔴 -> P_layer bridge |
| 3 LIV | LHAASO 18TeV | ✅ PASS (零色散) | 🟢 |

---

## 4. 後續兩途
- **dắt** 殺2: 構「P_layer(ℓ) 折射調製」local-in-layer — 而家最重要嘅防線。
- 殺 1: 抓 H0LiCOW/TDCOSMO D_Δt 數據 (背景-free) 去決 0.857 vs 2.0.